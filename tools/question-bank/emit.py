import json, sys, os
here = os.path.dirname(__file__)
data = json.load(open(os.path.join(here, "cache", "prompts.json")))
extra = os.path.join(here, "extra.json")
if os.path.exists(extra): data += json.load(open(extra))
import re
for p in data:
    m = re.match(r"^Name a club that has played in (?:the )?(.+)$", p["prompt"])
    if m: p["prompt"] = f"Name a club in {m.group(1)}" if m.group(1).startswith("the") else f"Name {'an' if m.group(1)[0] in 'AEIO' else 'a'} {m.group(1)} club"
seen, out = set(), []
for p in data:
    if p["prompt"] in seen: continue
    seen.add(p["prompt"]); out.append(p)
out.sort(key=lambda p: p["prompt"].lower())
TIERS = ["plankton", "tooClever", "schooler", "rare", "deepCut", "gem"]
root = sys.argv[1]
qdir = os.path.join(root, "questions")
os.makedirs(qdir, exist_ok=True)
for f in os.listdir(qdir):
    if f.endswith(".js"): os.remove(os.path.join(qdir, f))
index = []
for i, p in enumerate(out):
    ans = {t: p["answers"][t] for t in TIERS}
    open(os.path.join(qdir, f"{i}.js"), "w").write(f"KRILLION_ANSWERS({i},{json.dumps(ans, ensure_ascii=False, separators=(',', ':'))});\n")
    gem = p["answers"]["gem"][0].split("|")[0]
    index.append(f"  {{ prompt: {json.dumps(p['prompt'], ensure_ascii=False)}, gem: {json.dumps(gem, ensure_ascii=False)} }}")
n_ans = sum(len(v) for p in out for v in p["answers"].values())
header = f"""// Prompt bank: {len(out)} prompts, {n_ans:,} accepted answers. Each dive picks 7 of these at random.
//
// Generated from Wikidata (CC0). For each prompt, every valid answer is ranked by how widely known it is
// (how many Wikipedia language editions cover it), so the obvious picks land in the low tiers and obscure
// ones sink deeper. This file lists the prompts; each prompt's answers live in questions/<index>.js and
// are loaded when the prompt is dealt, so the page doesn't download every answer up front.
//
// An answers file calls KRILLION_ANSWERS(index, {{ plankton: [...], tooClever: [...], schooler: [...],
// rare: [...], deepCut: [...], gem: ["..."] }}). Each answer string lists aliases separated by "|"; the
// first one is shown to the player.
//
// Tiers (points): plankton 10 · tooClever 15 · schooler 30 · rare 60 · deepCut 85 · gem 100
// `gem` holds exactly one answer: the hidden "one in a krillion". It's repeated here so end-of-dive
// screens can show it without loading the answers.
//
// Multiplayer rooms refer to prompts by their index, so add new prompts at the end of the list.

window.KRILLION_PROMPTS = [
"""
open(os.path.join(root, "questions.js"), "w").write(header + ",\n".join(index) + ",\n];\n")
print(len(out), "prompts", n_ans, "answers")
