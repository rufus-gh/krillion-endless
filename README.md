# Krillion Endless (clone)

An unlimited version of Krillion's classic mode. Each dive has 7 prompts, with 25 seconds and one answer per prompt. If a guess isn't on the list, you can keep trying until time runs out. Rarer answers score more, and every point sinks you 10 m. A perfect dive (700 pts) reaches the trench floor at 7,000 m. There's no daily limit.

## Dig to China

**Dig to China** is a separate game, reached from the **DIG TO CHINA** button on the title screen. It has its own title screen (**DIGGER**), its own stats and earth-and-lava colours. You start in a backyard with a shovel and dig straight down through the soil, the crust, the mantle, the outer core and the inner core, then come out the other side in the Indian Ocean (the real antipode of most of the US). Your tunnel carries over from one dig to the next. The whole trip is 5,000 points, about 20 digs. Your progress is saved in the browser, and "fill in the tunnel" starts you over.

The rules are the same as the endless dive, with dig wording: **Deep Dig** (85 pts) replaces Deep Cut, **Almost Chinese** (100 pts) replaces One in a Krillion, and running out of time is **Stuck in the Mud**. The result screen shows a little drill rig juddering straight down instead of the krill swaying as it sinks.

The route (layer sizes and point budgets) is `ROUTE` at the top of `scene.js`. The `.dig-bar` gradient in `styles.css` mirrors it. The dig colours are the `body.dig` variables in `styles.css`. Tunnels saved before the dig started on land are converted to the same layer automatically.

## Graphics

The backdrop is one pixel-art `<canvas>` drawn by `scene.js`. For the endless dive it covers the sky, waves and boat, and the sea life for each zone (fish, jellies, a sperm whale, a giant squid, anglerfish, the Titanic, the trench walls). For Dig to China it covers the backyard, every layer of the Earth (worms, fossils, diamonds, magma, liquid iron, crystals) and the Indian Ocean on the far side. Everything is positioned in points, the same unit as the score, and a single camera moves the scene, the depth ruler and the fun facts together.

## Run

It's a static site with no build step. Open `index.html` directly, or serve the folder:

```bash
python3 -m http.server 5173
```

## Deploying

The GitHub repo is connected to the Vercel project `krillion-endless`. A push to `main` deploys to https://krillion-endless.vercel.app, and pushes to other branches get their own preview URLs.

## Prompts

The bank holds 1,680 prompts and about 337,000 accepted answers. They were generated from [Wikidata](https://www.wikidata.org) (CC0): for each prompt, every valid answer is ranked by how many Wikipedia language editions cover it. The well-known answers land in the low tiers and the obscure ones sink deeper. Aliases (alternative names, surnames for people, short titles) are accepted too.

`questions.js` lists the prompts. Each prompt's answers live in `questions/<index>.js` and are loaded only when that prompt is dealt, so the page doesn't download all 300k+ answers up front. The generator lives in [`tools/question-bank`](tools/question-bank).

To add a prompt by hand, append `{ prompt: "Name a ...", gem: "..." }` to the end of `questions.js`, then create `questions/<its index>.js`:

```js
KRILLION_ANSWERS(1680, {
  plankton:  [...], // 10 pts: the obvious answers
  tooClever: [...], // 15 pts: the "obscure" pick everyone thinks of
  schooler:  [...], // 30 pts
  rare:      [...], // 60 pts
  deepCut:   [...], // 85 pts
  gem:       ["..."], // 100 pts: exactly one hidden gem (the same as `gem` in questions.js)
});
```

- Use `"Display name|alias|other alias"` to accept several spellings. The first one is the name players see.
- Matching ignores case, accents, punctuation, spaces, a leading "the", and simple plurals.
- **Near misses get a "Did you mean …?"** instead of a rejection. This covers typos, a surname or one word of a longer title, and the start of a long name. Press Enter again, or click the suggestion, to submit it as that answer. Typing anything else dismisses it.
- If an answer appears in two tiers, the lower tier wins and a warning is printed in the browser console.
- Prompts are dealt from a shuffle bag, so you see every prompt before any of them repeats.
- Multiplayer rooms refer to prompts by their position in the array, so add new prompts at the end.

## Multiplayer

Click **Multiplayer** on the title screen. No account is needed; you just pick a name.

- **Create a room.** The room name is optional. Adding a password makes the room private: it still shows in the room browser, but joining asks for the password.
- **Invite people** with the share link (`?room=CODE`, plus `&pw=…` for private rooms so link-joiners skip the password), with the 5-letter code, or through the room browser.
- **Only the host can start a dive.** If the host leaves, the player who's been in the room longest takes over.
- **Each prompt lasts 25 seconds.** It ends early once everyone has answered.
- **The scoreboard after each prompt** shows every player's answer, best tier first. It moves on when the host clicks Next, or by itself after 20 seconds.
- **Shared answers get half points**, like in Stop. When two or more players give the same answer to a prompt, each of them gets half that answer's points (rounded up). The database stores full points; each client applies the halving once the prompt is revealed.
- **Other divers appear on the depth ruler** beside you, with their name and total depth. During a prompt they stay at their previous depth so answers aren't given away early.

### Dig to China race

In the lobby, or between dives, the host can switch the room from **Classic** to **Dig to China**. A dig room uses the Dig to China route, colours and tier names. In a dig room:

- **Tunnels carry over between dives in that room.** At the start of each dive the server banks everyone's points from the last dive (after halving shared answers) into their tunnel (`players.tunnel_pts`). This is separate from your solo tunnel, which stays in your browser.
- **Everyone's drill shows on the canvas**, each in its own tunnel beside yours, and on the depth ruler.
- **The first player to reach the far surface (5,000 pts) wins.** The dive ends at the scoreboard where someone breaks through, even mid-dive, and everyone gets the breakthrough screen. If two players break through on the same prompt, the higher total wins, then whoever answered first.
- **The next dive starts a new race**, with every tunnel filled in. Switching modes also fills in every tunnel.
- If you leave and join again as a new player, you start from the surface. Refreshing the page keeps your tunnel.

The goal is set in `_dig_goal()` in the migration and must match `Scene.END` in `scene.js`. The server also applies the half-points rule (in `_dive_pts()`) when it banks tunnels and decides the winner, so if you change that rule, change it in both `mp.js` `applyShared()` and the SQL.

The backend is a Supabase project (`krillion-multiplayer`). Its URL and public anon key are in `config.js`. The database is `supabase/schema.sql` plus the files in `supabase/migrations/`, applied in order. To change the live database, run a migration in the project's SQL editor **before** pushing client code that depends on it. Clients can only read room state; every change goes through database functions that check each player's secret token. Answers are matched in the browser against `questions.js`, so this is built for friendly games, not tournaments.
