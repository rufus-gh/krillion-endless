import sys, json, os, re
sys.path.insert(0, os.path.dirname(__file__))
from concurrent.futures import ThreadPoolExecutor
from core import resolve2 as resolve, build_all
import specs
S = specs.S
from fixes import FIX, WHERE, RENAME, DESC
FIXIDS = json.load(open(os.path.join(os.path.dirname(__file__), "fix_ids.json")))
# de-dupe by prompt text, apply class-ID corrections
seen, todo = set(), []
for s in S:
    if s["prompt"] in seen: continue
    if s["prompt"] in FIX:
        if FIX[s["prompt"]] is None: continue
        s = dict(s)
        for old, label in FIX[s["prompt"]].items():
            if label not in FIXIDS: s = None; break
            s["where"] = s["where"].replace("wd:" + old + " ", "wd:" + FIXIDS[label] + " ").replace("wd:" + old + ".", "wd:" + FIXIDS[label] + ".").replace("wd:" + old + "}", "wd:" + FIXIDS[label] + "}")
        if s is None: continue
    if s["prompt"] in WHERE: s = dict(s); s["where"] = WHERE[s["prompt"]]
    if s["prompt"].startswith("Name a club that has played in"):
        s = dict(s); s["where"] += " ?item wdt:P31/wdt:P279* wd:Q476028."
    TYPE_FILTER = {"Name a soap opera": "Q15416", "Name a talk show": "Q15416", "Name a Christmas film": "Q11424", "Name a Christmas song": "Q2188189"}
    if s["prompt"] in TYPE_FILTER:
        s = dict(s); s["where"] += f" ?item wdt:P31/wdt:P279* wd:{TYPE_FILTER[s['prompt']]}."
    if s["prompt"].endswith("car model"):
        s = dict(s); s["prompt"] = s["prompt"].replace("Saabmobile", "Saab")
        s["prompt"] = re.sub(r"^Name a (?=[AEIOU])", "Name an ", s["prompt"])
    if re.match(r"^Name a (?=[AEIO])(?!Eu|One)", s["prompt"]):
        s = dict(s); s["prompt"] = "Name an " + s["prompt"][7:]
    if s["prompt"] in RENAME:
        s = dict(s); s["prompt"] = RENAME[s["prompt"]]; s["desc"] = DESC.get(s["prompt"], s.get("desc"))
    seen.add(s["prompt"]); todo.append(s)
need = {}
for s in todo:
    for k, (name, types) in s.get("resolve", {}).items():
        need[(name, tuple(types))] = None
OVERRIDE = {"Beyoncé": "Q36153", "50 Cent": "Q6060"}
keys = [k for k in need if k[0] not in OVERRIDE]
for k in need:
    if k[0] in OVERRIDE: need[k] = OVERRIDE[k[0]]
with ThreadPoolExecutor(3) as ex:
    for k, q in zip(keys, ex.map(lambda k: resolve(k[0], list(k[1])), keys)):
        need[k] = q
        if not q: print("unresolved:", k[0], file=sys.stderr)
ready = []
for s in todo:
    ok = True
    w = s["where"]
    for k, (name, types) in s.get("resolve", {}).items():
        q = need[(name, tuple(types))]
        if not q: ok = False; break
        w = w.replace("{" + k + "}", q)
    if ok:
        s = dict(s); s["where"] = w; ready.append(s)
print(f"{len(ready)} specs ready", file=sys.stderr)
out = build_all(ready, workers=5)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "cache", "prompts.json"), "w"), ensure_ascii=False)
print(f"DONE {len(out)} prompts", file=sys.stderr)
