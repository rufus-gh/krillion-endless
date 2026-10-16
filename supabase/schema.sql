-- Krillion multiplayer backend (Supabase project "krillion-multiplayer").
-- Already applied to the live project; kept here so it can be recreated from scratch.
-- Later changes live in supabase/migrations/ (apply them in order after this file).
--
-- Model: clients can READ rooms/players/answers (and get realtime updates), but every
-- WRITE goes through the functions below, which check a per-player secret token.
-- Room passwords and player tokens live in tables clients can't read at all.

create extension if not exists pgcrypto with schema extensions;

-- ---------- Tables ----------
create table public.rooms (
  code text primary key,
  name text not null check (char_length(name) between 1 and 40),
  host_id uuid,
  locked boolean not null default false,
  status text not null default 'lobby' check (status in ('lobby','playing','reveal','finished')),
  prompt_ids int[] not null default '{}',      -- indexes into questions.js
  round int not null default 0,
  round_started_at timestamptz,
  phase_ends_at timestamptz,                   -- end of the answer window, or of the scoreboard
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.room_secrets (
  code text primary key references public.rooms(code) on delete cascade,
  passcode text not null
);

create table public.players (
  id uuid primary key default gen_random_uuid(),
  room_code text not null references public.rooms(code) on delete cascade,
  name text not null check (char_length(name) between 1 and 20),
  score int not null default 0,
  joined_at timestamptz not null default now(),
  last_seen timestamptz not null default now(),
  left_at timestamptz
);
create index players_room_idx on public.players(room_code);

create table public.player_secrets (
  player_id uuid primary key references public.players(id) on delete cascade,
  token uuid not null default gen_random_uuid()
);

create table public.answers (
  room_code text not null references public.rooms(code) on delete cascade,
  round int not null,
  player_id uuid not null references public.players(id) on delete cascade,
  answer text check (answer is null or char_length(answer) <= 80),
  tier text check (tier is null or tier in ('plankton','tooClever','schooler','rare','deepCut','gem')),
  pts int not null default 0,
  submitted_at timestamptz not null default now(),
  primary key (room_code, round, player_id)
);
create index answers_player_idx on public.answers(player_id);

-- ---------- Access ----------
alter table public.rooms enable row level security;
alter table public.room_secrets enable row level security;
alter table public.players enable row level security;
alter table public.player_secrets enable row level security;
alter table public.answers enable row level security;

create policy "rooms are public" on public.rooms for select to anon, authenticated using (true);
create policy "players are public" on public.players for select to anon, authenticated using (true);
create policy "answers are public" on public.answers for select to anon, authenticated using (true);

revoke insert, update, delete, truncate on public.rooms, public.players, public.answers from anon, authenticated;
revoke all on public.room_secrets, public.player_secrets from anon, authenticated;

alter publication supabase_realtime add table public.rooms, public.players, public.answers;

-- ---------- Helpers (not callable by clients) ----------
create or replace function public._tier_pts(p_tier text) returns int
language sql immutable set search_path = '' as $$
  select case p_tier
    when 'plankton' then 10 when 'tooClever' then 15 when 'schooler' then 30
    when 'rare' then 60 when 'deepCut' then 85 when 'gem' then 100 else 0 end
$$;

-- A player counts as present if they haven't left and sent a heartbeat in the last 25s.
create or replace function public._is_active(p public.players) returns boolean
language sql stable set search_path = '' as $$
  select p.left_at is null and p.last_seen > now() - interval '25 seconds'
$$;

create or replace function public._auth(p_player_id uuid, p_token uuid) returns public.players
language plpgsql security definer set search_path = '' as $$
declare v public.players;
begin
  select pl.* into v from public.players pl
    join public.player_secrets s on s.player_id = pl.id
   where pl.id = p_player_id and s.token = p_token;
  if not found then raise exception 'not_in_room' using errcode = 'P0001'; end if;
  return v;
end $$;

create or replace function public._clean_name(p_name text) returns text
language sql immutable set search_path = '' as $$
  select left(regexp_replace(btrim(coalesce(p_name, '')), '\s+', ' ', 'g'), 20)
$$;

-- Picks a name not already used by a present player in the room ("Sam", "Sam 2", ...).
create or replace function public._unique_name(p_code text, p_name text, p_except uuid default null) returns text
language plpgsql security definer set search_path = '' as $$
declare v text := p_name; n int := 1;
begin
  while exists (select 1 from public.players pl where pl.room_code = p_code and lower(pl.name) = lower(v)
                and pl.left_at is null and pl.id is distinct from p_except) loop
    n := n + 1; v := left(p_name, 17) || ' ' || n;
  end loop;
  return v;
end $$;

-- Advances timed phases and keeps a live host. Safe to call from any client, any time.
create or replace function public._advance(p_code text) returns void
language plpgsql security definer set search_path = '' as $$
declare r public.rooms; waiting int; new_host uuid;
begin
  select * into r from public.rooms where code = p_code for update;
  if not found then return; end if;

  -- Host failover: the longest-present player takes over.
  if not exists (select 1 from public.players pl where pl.id = r.host_id and public._is_active(pl)) then
    select pl.id into new_host from public.players pl
     where pl.room_code = p_code and public._is_active(pl) order by pl.joined_at limit 1;
    if new_host is not null and new_host is distinct from r.host_id then
      update public.rooms set host_id = new_host, updated_at = now() where code = p_code;
      r.host_id := new_host;
    end if;
  end if;

  if r.status = 'playing' then
    select count(*) into waiting from public.players pl
     where pl.room_code = p_code and public._is_active(pl)
       and not exists (select 1 from public.answers a where a.room_code = p_code and a.round = r.round and a.player_id = pl.id);
    if now() >= r.phase_ends_at or waiting = 0 then
      update public.rooms set status = 'reveal', phase_ends_at = now() + interval '20 seconds', updated_at = now()
       where code = p_code;
    end if;
  elsif r.status = 'reveal' and now() >= r.phase_ends_at then
    perform public._next_round(p_code);
  end if;
end $$;

create or replace function public._next_round(p_code text) returns void
language plpgsql security definer set search_path = '' as $$
declare r public.rooms;
begin
  select * into r from public.rooms where code = p_code;
  if r.round + 1 >= coalesce(array_length(r.prompt_ids, 1), 0) then
    update public.rooms set status = 'finished', phase_ends_at = null, updated_at = now() where code = p_code;
  else
    update public.rooms set status = 'playing', round = r.round + 1, round_started_at = now(),
           phase_ends_at = now() + interval '25.5 seconds', updated_at = now()
     where code = p_code;
  end if;
end $$;

-- Rooms nobody has touched for 6 hours are deleted whenever a new room is created.
create or replace function public._cleanup_rooms() returns void
language sql security definer set search_path = '' as $$
  delete from public.rooms r
   where r.updated_at < now() - interval '6 hours'
     and not exists (select 1 from public.players pl where pl.room_code = r.code and pl.last_seen > now() - interval '6 hours');
$$;

-- ---------- Public API ----------
create or replace function public.server_now() returns timestamptz
language sql stable set search_path = '' as $$ select now() $$;

create or replace function public.create_room(p_room_name text, p_passcode text, p_player_name text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  v_code text; v_player uuid; v_token uuid;
  v_name text := public._clean_name(p_player_name);
  v_room text := left(btrim(coalesce(p_room_name, '')), 40);
  v_pass text := nullif(btrim(coalesce(p_passcode, '')), '');
  alphabet text := 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
begin
  if v_name = '' then raise exception 'name_required' using errcode = 'P0001'; end if;
  if v_room = '' then v_room := v_name || '''s room'; end if;
  if v_pass is not null and char_length(v_pass) > 32 then raise exception 'passcode_too_long' using errcode = 'P0001'; end if;
  perform public._cleanup_rooms();
  loop
    v_code := (select string_agg(substr(alphabet, 1 + floor(random() * length(alphabet))::int, 1), '') from generate_series(1, 5));
    exit when not exists (select 1 from public.rooms where code = v_code);
  end loop;
  insert into public.rooms(code, name, locked) values (v_code, v_room, v_pass is not null);
  if v_pass is not null then insert into public.room_secrets(code, passcode) values (v_code, v_pass); end if;
  insert into public.players(room_code, name) values (v_code, v_name) returning id into v_player;
  insert into public.player_secrets(player_id) values (v_player) returning token into v_token;
  update public.rooms set host_id = v_player where code = v_code;
  return json_build_object('code', v_code, 'player_id', v_player, 'token', v_token);
end $$;

create or replace function public.join_room(p_code text, p_passcode text, p_player_name text) returns json
language plpgsql security definer set search_path = '' as $$
declare
  r public.rooms; v_player uuid; v_token uuid; v_name text := public._clean_name(p_player_name);
  v_code text := upper(btrim(coalesce(p_code, '')));
begin
  if v_name = '' then raise exception 'name_required' using errcode = 'P0001'; end if;
  select * into r from public.rooms where code = v_code;
  if not found then raise exception 'room_not_found' using errcode = 'P0001'; end if;
  if r.locked and not exists (select 1 from public.room_secrets s where s.code = v_code and s.passcode = btrim(coalesce(p_passcode, ''))) then
    raise exception 'wrong_passcode' using errcode = 'P0001';
  end if;
  if (select count(*) from public.players pl where pl.room_code = v_code and public._is_active(pl)) >= 16 then
    raise exception 'room_full' using errcode = 'P0001';
  end if;
  insert into public.players(room_code, name) values (v_code, public._unique_name(v_code, v_name)) returning id into v_player;
  insert into public.player_secrets(player_id) values (v_player) returning token into v_token;
  update public.rooms set updated_at = now() where code = v_code;
  perform public._advance(v_code);
  return json_build_object('code', v_code, 'player_id', v_player, 'token', v_token);
end $$;

-- Heartbeat: marks you present (also rejoins after a refresh) and nudges the room's clock.
create or replace function public.heartbeat(p_player_id uuid, p_token uuid) returns timestamptz
language plpgsql security definer set search_path = '' as $$
declare p public.players;
begin
  p := public._auth(p_player_id, p_token);
  update public.players set last_seen = now(), left_at = null where id = p.id;
  perform public._advance(p.room_code);
  return now();
end $$;

create or replace function public.leave_room(p_player_id uuid, p_token uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players;
begin
  p := public._auth(p_player_id, p_token);
  update public.players set left_at = now() where id = p.id;
  perform public._advance(p.room_code);
end $$;

create or replace function public.start_game(p_player_id uuid, p_token uuid, p_prompt_ids int[]) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players; r public.rooms;
begin
  p := public._auth(p_player_id, p_token);
  select * into r from public.rooms where code = p.room_code for update;
  if r.host_id <> p.id then raise exception 'host_only' using errcode = 'P0001'; end if;
  if r.status not in ('lobby', 'finished') then raise exception 'already_playing' using errcode = 'P0001'; end if;
  if coalesce(array_length(p_prompt_ids, 1), 0) not between 1 and 20 then raise exception 'bad_prompts' using errcode = 'P0001'; end if;
  delete from public.answers where room_code = r.code;
  update public.players set score = 0 where room_code = r.code;
  update public.rooms set status = 'playing', prompt_ids = p_prompt_ids, round = 0, round_started_at = now(),
         phase_ends_at = now() + interval '25.5 seconds', updated_at = now()
   where code = r.code;
end $$;

-- The client matches answers against questions.js and reports the tier; points are set here.
create or replace function public.submit_answer(p_player_id uuid, p_token uuid, p_round int, p_answer text, p_tier text) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players; r public.rooms; v_pts int := public._tier_pts(p_tier);
begin
  p := public._auth(p_player_id, p_token);
  select * into r from public.rooms where code = p.room_code;
  if r.status <> 'playing' or r.round <> p_round or now() > r.phase_ends_at + interval '2 seconds' then
    raise exception 'round_closed' using errcode = 'P0001';
  end if;
  insert into public.answers(room_code, round, player_id, answer, tier, pts)
  values (r.code, p_round, p.id, left(p_answer, 80), p_tier, v_pts)
  on conflict do nothing;
  if found then update public.players set score = score + v_pts, last_seen = now() where id = p.id; end if;
  perform public._advance(r.code);
end $$;

create or replace function public.next_round(p_player_id uuid, p_token uuid, p_round int) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players; r public.rooms;
begin
  p := public._auth(p_player_id, p_token);
  select * into r from public.rooms where code = p.room_code for update;
  if r.host_id <> p.id then raise exception 'host_only' using errcode = 'P0001'; end if;
  if r.status = 'reveal' and r.round = p_round then perform public._next_round(r.code); end if;
end $$;

create or replace function public.list_rooms() returns table (
  code text, name text, locked boolean, status text, players int, host_name text, round int, total_rounds int, created_at timestamptz
)
language sql stable security definer set search_path = '' as $$
  select r.code, r.name, r.locked, r.status,
         (select count(*)::int from public.players pl where pl.room_code = r.code and public._is_active(pl)),
         (select h.name from public.players h where h.id = r.host_id),
         r.round, coalesce(array_length(r.prompt_ids, 1), 0), r.created_at
    from public.rooms r
   where exists (select 1 from public.players pl where pl.room_code = r.code and public._is_active(pl))
   order by r.created_at desc
   limit 50
$$;

-- Only the public API is callable by clients.
revoke execute on all functions in schema public from public, anon, authenticated;
grant execute on function public.server_now(), public.create_room(text, text, text), public.join_room(text, text, text),
  public.heartbeat(uuid, uuid), public.leave_room(uuid, uuid), public.start_game(uuid, uuid, int[]),
  public.submit_answer(uuid, uuid, int, text, text), public.next_round(uuid, uuid, int), public.list_rooms()
  to anon, authenticated;
