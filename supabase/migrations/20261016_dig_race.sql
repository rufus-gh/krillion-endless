-- Dig to China race for multiplayer rooms.
-- NOT YET APPLIED to the live Supabase project "krillion-multiplayer". Run this once in the
-- SQL editor (after schema.sql) BEFORE deploying the matching client, which reads the new columns.
-- Existing clients keep working after it's applied: every new column has a default.
--
-- A room is either 'classic' (every dive starts at the surface) or 'dig' (a race through the Earth).
-- In a dig room each player's tunnel carries over between dives, and the first player whose tunnel
-- plus current dive reaches the far surface wins.

alter table public.rooms
  add column mode text not null default 'classic' check (mode in ('classic', 'dig')),
  add column winner_id uuid;                   -- dig rooms: who broke through first (null = race on)

alter table public.players
  add column tunnel_pts int not null default 0; -- dig rooms: points banked from earlier dives in this room

-- Points to the far surface. Must match Scene.END in scene.js.
create or replace function public._dig_goal() returns int
language sql immutable set search_path = '' as $$ select 5500 $$;

-- Each player's points in the current dive, with the half-points-for-shared-answers rule
-- (the same rule mp.js applyShared() applies in the browser): when two or more players give
-- the same answer to a prompt, each gets half its points, rounded up.
create or replace function public._dive_pts(p_code text, p_upto int default null)
returns table (player_id uuid, pts int)
language sql stable set search_path = '' as $$
  with a as (
    select a.player_id, a.pts, a.tier, a.answer,
           count(*) filter (where a.tier is not null and a.answer is not null)
             over (partition by a.round, lower(a.answer)) as same
      from public.answers a
     where a.room_code = p_code and (p_upto is null or a.round <= p_upto)
  )
  select a.player_id,
         sum(case when a.tier is not null and a.answer is not null and a.same > 1 then ceil(a.pts / 2.0)::int else a.pts end)::int
    from a group by a.player_id
$$;

-- Leaving a scoreboard: in a dig room, end the dive as soon as someone has broken through.
-- Highest total wins; a tie goes to whoever answered that prompt first.
create or replace function public._next_round(p_code text) returns void
language plpgsql security definer set search_path = '' as $$
declare r public.rooms; v_winner uuid;
begin
  select * into r from public.rooms where code = p_code;
  if r.mode = 'dig' and r.winner_id is null then
    select t.id into v_winner from (
      select pl.id, pl.tunnel_pts + coalesce(d.pts, 0) as total,
             (select a.submitted_at from public.answers a
               where a.room_code = p_code and a.round = r.round and a.player_id = pl.id) as answered_at
        from public.players pl
        left join public._dive_pts(p_code, r.round) d on d.player_id = pl.id
       where pl.room_code = p_code
    ) t
     where t.total >= public._dig_goal()
     order by t.total desc, t.answered_at nulls last
     limit 1;
  end if;
  if v_winner is not null then
    update public.rooms set status = 'finished', winner_id = v_winner, phase_ends_at = null, updated_at = now() where code = p_code;
  elsif r.round + 1 >= coalesce(array_length(r.prompt_ids, 1), 0) then
    update public.rooms set status = 'finished', phase_ends_at = null, updated_at = now() where code = p_code;
  else
    update public.rooms set status = 'playing', round = r.round + 1, round_started_at = now(),
           phase_ends_at = now() + interval '25.5 seconds', updated_at = now()
     where code = p_code;
  end if;
end $$;

-- Starting a dive in a dig room banks the last dive's points into everyone's tunnel
-- (or fills every tunnel in, if the last dive had a winner) before the answers are cleared.
create or replace function public.start_game(p_player_id uuid, p_token uuid, p_prompt_ids int[]) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players; r public.rooms;
begin
  p := public._auth(p_player_id, p_token);
  select * into r from public.rooms where code = p.room_code for update;
  if r.host_id <> p.id then raise exception 'host_only' using errcode = 'P0001'; end if;
  if r.status not in ('lobby', 'finished') then raise exception 'already_playing' using errcode = 'P0001'; end if;
  if coalesce(array_length(p_prompt_ids, 1), 0) not between 1 and 20 then raise exception 'bad_prompts' using errcode = 'P0001'; end if;
  if r.mode = 'dig' then
    if r.winner_id is not null then
      update public.players set tunnel_pts = 0 where room_code = r.code;
    else
      update public.players pl set tunnel_pts = pl.tunnel_pts + d.pts
        from public._dive_pts(r.code) d where d.player_id = pl.id and pl.room_code = r.code;
    end if;
  end if;
  delete from public.answers where room_code = r.code;
  update public.players set score = 0 where room_code = r.code;
  update public.rooms set status = 'playing', prompt_ids = p_prompt_ids, round = 0, round_started_at = now(),
         phase_ends_at = now() + interval '25.5 seconds', winner_id = null, updated_at = now()
   where code = r.code;
end $$;

-- Host picks Classic or Dig to China between dives. Switching fills in every tunnel.
create or replace function public.set_room_mode(p_player_id uuid, p_token uuid, p_mode text) returns void
language plpgsql security definer set search_path = '' as $$
declare p public.players; r public.rooms;
begin
  p := public._auth(p_player_id, p_token);
  select * into r from public.rooms where code = p.room_code for update;
  if r.host_id <> p.id then raise exception 'host_only' using errcode = 'P0001'; end if;
  if r.status not in ('lobby', 'finished') then raise exception 'already_playing' using errcode = 'P0001'; end if;
  if p_mode not in ('classic', 'dig') then raise exception 'bad_mode' using errcode = 'P0001'; end if;
  if p_mode = r.mode then return; end if;
  update public.players set tunnel_pts = 0 where room_code = r.code;
  update public.rooms set mode = p_mode, winner_id = null, updated_at = now() where code = r.code;
end $$;

-- The room browser also shows each room's mode.
drop function public.list_rooms();
create function public.list_rooms() returns table (
  code text, name text, locked boolean, status text, players int, host_name text, round int, total_rounds int, created_at timestamptz, mode text
)
language sql stable security definer set search_path = '' as $$
  select r.code, r.name, r.locked, r.status,
         (select count(*)::int from public.players pl where pl.room_code = r.code and public._is_active(pl)),
         (select h.name from public.players h where h.id = r.host_id),
         r.round, coalesce(array_length(r.prompt_ids, 1), 0), r.created_at, r.mode
    from public.rooms r
   where exists (select 1 from public.players pl where pl.room_code = r.code and public._is_active(pl))
   order by r.created_at desc
   limit 50
$$;

revoke execute on function public._dig_goal(), public._dive_pts(text, int), public.set_room_mode(uuid, uuid, text),
  public.list_rooms() from public, anon, authenticated;
grant execute on function public.set_room_mode(uuid, uuid, text), public.list_rooms() to anon, authenticated;
