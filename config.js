// Supabase project that powers multiplayer rooms. The anon key is public by design;
// all writes go through database functions that check each player's secret token.
window.KRILLION_CONFIG = {
  supabaseUrl: "https://hltgtwymcdlhsrdffgql.supabase.co",
  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhsdGd0d3ltY2RsaHNyZGZmZ3FsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTIxMDE3ODQsImV4cCI6MjEwNzY3Nzc4NH0.udqIZ4_SYd69h86LPNzfkFMZLg0wUP9SWbwzND_MT2o",
};
