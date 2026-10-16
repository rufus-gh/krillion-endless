# Question bank generator

Rebuilds `questions.js` and `questions/` from Wikidata.

```bash
python3 tools/question-bank/run.py      # query Wikidata (about 2 hours cold; cached in cache/)
python3 tools/question-bank/emit.py .   # write questions.js and questions/<n>.js
```

- `specs.py` lists the prompt templates, each a SPARQL pattern that binds `?item`.
- `fixes.py` corrects or drops specs whose class IDs turned out wrong, and renames a few.
- `core.py` fetches items, ranks them by sitelink count, builds aliases, and splits them into tiers.
- `curate.py` decides which prompts make the cut: broad questions only, so it drops things like "Name a Swiss canton" or songs by niche artists.
- `EXTRA` in `fixes.py` holds hand-added answers (and aliases) for things Wikidata files under a generic class, such as Tooheys, which it only knows as "a drink". Add to it when players report a valid answer that's missing.
- `extra.json`, if present, holds hand-written prompts in the same `{prompt, answers}` shape; `emit.py` merges them in.

Re-emitting reorders prompts, which changes their indexes. Don't deploy that while multiplayer rooms are mid-game.
