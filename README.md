# Krillion Endless (clone)

An unlimited version of Krillion's classic mode. Each dive has 7 prompts, with 25 seconds and one answer per prompt. If a guess isn't on the list, you can keep trying until time runs out. Rarer answers score more, and every point sinks you 10 m. A perfect dive (700 pts) reaches the trench floor at 7,000 m. There's no daily limit.

## Run

It's a static site with no build step. Open `index.html` directly, or serve the folder:

```bash
python3 -m http.server 5173
```

## Deploying

The GitHub repo is connected to the Vercel project `krillion-endless`. A push to `main` deploys to https://krillion-endless.vercel.app, and pushes to other branches get their own preview URLs.

## Adding prompts

Edit `questions.js` and add an object to the array:

```js
{
  prompt: "Name a ...",
  answers: {
    plankton:  [...], // 10 pts: the obvious answers
    tooClever: [...], // 15 pts: the "obscure" pick everyone thinks of
    schooler:  [...], // 30 pts
    rare:      [...], // 60 pts
    deepCut:   [...], // 85 pts
    gem:       ["..."], // 100 pts: exactly one hidden gem
  },
}
```

- Use `"Display name|alias|other alias"` to accept several spellings. The first one is the name players see.
- Matching already ignores case, accents, punctuation, spaces, a leading "the", and simple plurals, and it forgives small typos (1 letter for 5–8 character answers, 2 letters for longer ones).
- If an answer appears in two tiers, the lower tier wins and a warning is printed in the browser console.
- Prompts are dealt from a shuffle bag, so you see every prompt before any of them repeats.

## Multiplayer

Click **Multiplayer** on the title screen. No account is needed; you just pick a name.

- **Create a room.** The room name is optional. Adding a password makes the room private: it still shows in the room browser, but joining asks for the password.
- **Invite people** with the share link (`?room=CODE`, plus `&pw=…` for private rooms so link-joiners skip the password), with the 5-letter code, or through the room browser.
- **Only the host can start a dive.** If the host leaves, the player who's been in the room longest takes over.
- **Each prompt lasts 25 seconds.** It ends early once everyone has answered.
- **The scoreboard after each prompt** shows every player's answer, best tier first. It moves on when the host clicks Next, or by itself after 20 seconds.
- **Other divers appear on the depth ruler** beside you, with their name and total depth. During a prompt they stay at their previous depth so answers aren't given away early.

The backend is a Supabase project (`krillion-multiplayer`). Its URL and public anon key are in `config.js`, and the full database schema is in `supabase/schema.sql`. Clients can only read room state; every change goes through database functions that check each player's secret token. Answers are matched in the browser against `questions.js`, so this is built for friendly games, not tournaments.
