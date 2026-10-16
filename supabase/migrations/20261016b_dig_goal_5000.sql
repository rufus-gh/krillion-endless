-- Dig to China now starts on land, so the trip through the Earth is 5,000 pts (was 5,500).
-- Run once on "krillion-multiplayer" if 20261016_dig_race.sql was applied while it still said 5500.
-- Harmless to run again. Must match Scene.END in scene.js.
create or replace function public._dig_goal() returns int
language sql immutable set search_path = '' as $$ select 5000 $$;
