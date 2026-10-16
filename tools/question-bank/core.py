import re, unicodedata, hashlib, sys, os
from wd import CACHE
from concurrent.futures import ThreadPoolExecutor
from wd import sparql

def normalize(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    s = s.replace("&", " and ")
    s = re.sub(r"['’`.!?]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"^(the|a|an) ", "", s)
    return "".join(w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w for w in s.split(" "))

def items_query(where, limit, minsl):
    return f"""SELECT ?item ?sl (SAMPLE(?l) AS ?label) (GROUP_CONCAT(DISTINCT ?alt; separator="␟") AS ?alts) WHERE {{
  {{ SELECT DISTINCT ?item ?sl WHERE {{ {where} ?item wikibase:sitelinks ?sl. FILTER(?sl >= {minsl}) }} ORDER BY DESC(?sl) LIMIT {limit} }}
  ?item rdfs:label ?l. FILTER(lang(?l)="en")
  OPTIONAL {{ ?item skos:altLabel ?alt. FILTER(lang(?alt)="en") }}
}} GROUP BY ?item ?sl"""

def resolve(name, types):
    """Find the best-known item with this English label (or alias) and one of the given types (P31/P279*)."""
    vals = " ".join("wd:" + t for t in types)
    esc = name.replace('"', '\\"')
    q = f"""SELECT DISTINCT ?x ?sl WHERE {{ VALUES ?t {{ {vals} }} {{ ?x rdfs:label "{esc}"@en }} UNION {{ ?x skos:altLabel "{esc}"@en }}
      ?x wdt:P31/wdt:P279? ?t; wikibase:sitelinks ?sl }} ORDER BY DESC(?sl) LIMIT 1"""
    r = sparql(q)
    if not r: return None
    return r[0]["x"]["value"].rsplit("/", 1)[1]

PAREN = re.compile(r"\s*\([^)]*\)\s*$")
CODEY = re.compile(r"^[A-Z0-9\-]{1,3}$")

COMPANY = re.compile(r" (Brewery|Breweries|Brewing Company|Brewing Co\.?|Group|International|Holdings|Limited|Ltd\.?|Inc\.?|plc|AG|S\.A\.|N\.V\.)$", re.I)
def clean_label(l):
    l = NOISE.sub("", PAREN.sub("", l).strip())
    short = COMPANY.sub("", l).strip()
    if short != l and len(short) >= 2: l = short
    if l and l[0].islower(): l = l[0].upper() + l[1:]
    return l

NOISE = re.compile(r"\s+(PDO|PGI|DOP|AOC|TSG)$")
LATIN = re.compile(r"^[A-Z][a-z]+ [a-z]+$")
LATIN_END = re.compile(r"(um|us|a|is|ae|ii|ensis|ia|es|e|ax|ix|ii|i)$")
def is_latin(l):
    return bool(LATIN.match(l)) and all(LATIN_END.search(w) for w in l.lower().split())
GEN_PRE = re.compile(r"^(County|Province of|Region of|State of|City of|Municipality of|Lake|Mount|Mt\.?|Isle of|Gulf of|Bay of|Sea of|Strait of|Cape|Saint|St\.?) ", re.I)
GEN_SUF = re.compile(r" (Group|International|Brewery|Breweries|Brewing Company|Brewing Co\.|Brewing|Beer|Distillery|Province|Prefecture|County|Municipality|Region|Oblast|Governorate|District|Department|Island|Islands|Airport|International Airport|Castle|Palace|Bridge|Cathedral|Zoo|Museum|River|Lake|Mountain|Mountains|Range|Desert|Sea|Ocean|Falls|Waterfall|Glacier|Canyon|Volcano|Peninsula|Strait|Bay|Gulf|Stadium|Arena|Park|National Park|Tower|Temple|Mosque|Abbey|Church|station|Station|Line|F\.C\.|FC|A\.F\.C\.|AFC|S\.C\.|SC|CF|C\.F\.|Football Club)$", re.I)
def variants_for(label, alts, kind, noun=None):
    label = NOISE.sub("", label)
    base = PAREN.sub("", label).strip()
    strong = [label, base]
    for rx in (GEN_PRE, GEN_SUF):
        short = rx.sub("", base).strip()
        if short != base and len(short) >= 3 and short[:1].isupper():
            strong.append(short)
    if noun:
        ws = base.split()
        if len(ws) >= 2 and ws[-1].lower().rstrip("s") == noun and ws[0][:1].isupper():
            strong.append(" ".join(ws[:-1]))
    for sep in (": ", " – ", " - "):
        if sep in base:
            tail = base.split(sep, 1)[1].strip()
            if len(tail) >= 4: strong.append(tail)
    if kind == "person":
        toks = re.sub(r",.*$", "", base).split()
        if len(toks) >= 2:
            last = toks[-1]
            if last.lower().rstrip(".") in ("jr", "sr", "ii", "iii") and len(toks) >= 3: last = toks[-2]
            if len(last) >= 4: strong.append(last)
            for i, t in enumerate(toks[1:-1], 1):
                if t.lower() in ("van", "von", "de", "da", "di", "del", "la", "le", "du", "der", "den", "dos", "al"):
                    strong.append(" ".join(toks[i:])); break
    weak = []
    for a in alts:
        a = a.strip()
        if not a or len(a) > 50 or ":" in a[:12]: continue
        if CODEY.match(a) and kind not in ("country", "element", "state"): continue
        if re.search(r"\d{4,}", a) and not re.search(r"\d{4,}", base): continue
        if any(unicodedata.category(c) == "Mn" for c in unicodedata.normalize("NFC", a)): continue
        weak.append(PAREN.sub("", a).strip())
    seen, res = set(), []
    for v in strong + weak:
        if v and v not in seen: seen.add(v); res.append(v)
    return res[:9]

BAD_LABEL = re.compile(r"^Q\d+$|^Category:|^List of|^Template:|\bseason \d|, season\b|\bepisode \d", re.I)

def fetch(spec):
    rows = sparql(f"SELECT DISTINCT ?item ?sl WHERE {{ {spec['where']} ?item wikibase:sitelinks ?sl. FILTER(?sl >= {spec.get('minsl', 3)}) }}", tries=2)
    if rows is None: return None
    best = {}
    for r in rows:
        q = r["item"]["value"].rsplit("/", 1)[1]
        best[q] = max(best.get(q, 0), int(r["sl"]["value"]))
    top = sorted(best, key=lambda q: -best[q])[: spec.get("limit", 500) * (2 if spec.get("desc") else 1)]
    items = []
    for i in range(0, len(top), 400):
        chunk = top[i:i + 400]
        vals = " ".join("wd:" + q for q in chunk)
        lr = sparql(f"""SELECT ?item (SAMPLE(?l) AS ?label) (GROUP_CONCAT(DISTINCT ?alt; separator="\u241f") AS ?alts) (SAMPLE(?d) AS ?desc) WHERE {{
          VALUES ?item {{ {vals} }} ?item rdfs:label ?l. FILTER(lang(?l)="en")
          OPTIONAL {{ ?item schema:description ?d. FILTER(lang(?d)="en") }}
          OPTIONAL {{ ?item skos:altLabel ?alt. FILTER(lang(?alt)="en") }} }} GROUP BY ?item""", tries=3)
        if lr is None: return None
        for r in lr:
            lab = r.get("label", {}).get("value")
            if not lab or BAD_LABEL.search(lab): continue
            q = r["item"]["value"].rsplit("/", 1)[1]
            alts = [a for a in r.get("alts", {}).get("value", "").split("\u241f") if a]
            sl = best[q]
            if spec.get("desc") and not re.search(spec["desc"], r.get("desc", {}).get("value", ""), re.I):
                sl = sl / 20  # famous for something else (e.g. a president who also paints): still accepted, but rarer
            items.append({"qid": q, "sl": sl, "label": lab, "alts": alts})
    items.sort(key=lambda x: (-x["sl"], x["label"]))
    return items[: spec.get("limit", 500)]

def clamp(v, lo, hi): return max(lo, min(hi, v))

def tierize(spec, items):
    kind = spec.get("kind", "thing")
    drop = {normalize(x) for x in spec.get("exclude", [])}
    # Build entries: display + variants; resolve key collisions (labels beat aliases, popular beats obscure).
    noun = re.sub(r"\s*\(.*\)", "", spec["prompt"]).split()[-1].lower().rstrip("s")
    pwords = set(normalize(w) for w in spec["prompt"].split())
    entries, labelkeys = [], {}
    for it in items:
        if is_latin(clean_label(it["label"])):
            common = [a for a in it["alts"] if not is_latin(a) and len(a) >= 3 and not re.search(r"\d", a)]
            if common:
                it = dict(it, label=common[0][:1].upper() + common[0][1:], alts=[it["label"]] + [a for a in it["alts"] if a != common[0]])
        disp = clean_label(it["label"])
        k = normalize(disp)
        if not k or k in drop: continue
        if k in labelkeys: continue  # duplicate display (e.g. two songs with same title): keep the popular one
        labelkeys[k] = len(entries)
        vs = variants_for(it["label"], it["alts"], kind, noun)
        ws = disp.split()
        for n in (1, 2):  # "Ford Model T" -> "Model T" when the prompt already names Ford
            if len(ws) > n and all(normalize(w) in pwords for w in ws[:n]) and len(" ".join(ws[n:])) >= 2:
                vs.append(" ".join(ws[n:]))
        entries.append({"disp": disp, "sl": it["sl"], "proper": it["label"][:1].isupper(), "vars": vs})
    owner = {}
    for i, e in enumerate(entries):
        for v in e["vars"]:
            k = normalize(v)
            if not k: continue
            owner.setdefault(k, set()).add(i)
    final = []
    for i, e in enumerate(entries):
        vs, seen = [e["disp"]], {normalize(e["disp"])}
        for v in e["vars"]:
            k = normalize(v)
            if not k or k in seen: continue
            if k in labelkeys and labelkeys[k] != i: continue   # alias equals another answer's name
            if min(owner.get(k, {i})) != i: continue             # shared alias: the best-known owner keeps it
            if len(k) < 2: continue
            seen.add(k); vs.append(v.replace("|", "/"))
        final.append("|".join(vs))
        e["str"] = final[-1]
    n = len(final)
    if n < spec.get("min", 12): return None
    if n >= 40:
        sizes = [clamp(round(n * 0.06), 4, 12), clamp(round(n * 0.04), 2, 8), clamp(round(n * 0.18), 6, 60), clamp(round(n * 0.25), 6, 150)]
    else:  # short closed lists (South American countries, Australian states): scale every tier down
        sizes = [max(1, round(n * 0.3)), max(1, round(n * 0.1)), max(1, round(n * 0.25)), max(1, round(n * 0.15))]
        while n - sum(sizes) < 2 and max(sizes) > 1:
            sizes[sizes.index(max(sizes[2:]) if max(sizes[2:]) > 1 else max(sizes))] -= 1
    a, b, c, d = sizes
    tiers = {"plankton": final[:a], "tooClever": final[a:a+b], "schooler": final[a+b:a+b+c], "rare": final[a+b+c:a+b+c+d], "deepCut": final[a+b+c+d:]}
    dc = tiers["deepCut"]
    if not dc: return None
    proper = {e["str"] for e in entries if e["proper"] and noun not in e["disp"].lower()}
    pool = dc[: max(1, len(dc) // 3)]
    pool = [x for x in pool if x in proper] or pool
    gi = int(hashlib.md5(spec["prompt"].encode()).hexdigest(), 16) % len(pool)
    gem = pool[gi]
    tiers["deepCut"] = [x for x in dc if x is not gem]
    tiers["gem"] = [gem]
    return tiers

def build_all(specs, workers=2):
    out = [None] * len(specs)
    def run(i):
        try:
            r = run1(i)
            if r[1] is None and specs[i].get("fallback"):  # broadened query failed: use the original one
                fb = dict(specs[i]["fallback"]); specs[i] = fb
                r = run1(i)
            return r
        except Exception as e: return i, None, f"error {e!r}"
    def run1(i):
        s = specs[i]
        items = fetch(s)
        if items is None: return i, None, "failed"
        t = tierize(s, items)
        return i, t, len(items)
    with ThreadPoolExecutor(workers) as ex:
        for i, t, info in ex.map(run, range(len(specs))):
            s = specs[i]
            if t: out[i] = {"prompt": s["prompt"], "answers": t}
            top = ", ".join(x.split("|")[0] for x in (t["plankton"][:4] if t else []))
            print(f"{'OK ' if t else '-- '}{i:4d} {s['prompt'][:50]:50s} {info} | {top}", file=sys.stderr, flush=True)
    return [o for o in out if o]

import json as _json, urllib.request as _ur, urllib.parse as _up, os as _os
from wd import UA, CACHE
def search_ids(name):
    p = _os.path.join(CACHE, "s_" + hashlib.sha1(name.encode()).hexdigest() + ".json")
    if _os.path.exists(p): return _json.load(open(p))
    url = "https://www.wikidata.org/w/api.php?" + _up.urlencode({"action": "wbsearchentities", "search": name, "language": "en", "limit": 10, "format": "json", "type": "item"})
    with _ur.urlopen(_ur.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        ids = [[x["id"], x.get("label", "")] for x in _json.load(r).get("search", [])]
    _json.dump(ids, open(p, "w"))
    return ids

def resolve2(name, types):
    vals_t = " ".join("wd:" + t for t in types)
    esc = name.replace('"', '\\"')
    cached = os.path.join(CACHE, hashlib.sha1(f"""SELECT DISTINCT ?x ?sl WHERE {{ VALUES ?t {{ {vals_t} }} {{ ?x rdfs:label "{esc}"@en }} UNION {{ ?x skos:altLabel "{esc}"@en }}
      ?x wdt:P31/wdt:P279? ?t; wikibase:sitelinks ?sl }} ORDER BY DESC(?sl) LIMIT 1""".encode()).hexdigest() + ".json")
    if os.path.exists(cached):
        q = resolve(name, types)
        if q: return q
    ids = search_ids(name)
    if not ids: return None
    labels = dict(ids); ids = [i for i, _ in ids]
    vals = " ".join("wd:" + i for i in ids)
    tv = " ".join("wd:" + t for t in types)
    r = sparql(f"SELECT DISTINCT ?x WHERE {{ VALUES ?x {{ {vals} }} VALUES ?t {{ {tv} }} ?x wdt:P31/wdt:P279* ?t }}")
    ok = {row["x"]["value"].rsplit("/", 1)[1] for row in (r or [])}
    for i in ids:
        if i in ok and labels.get(i, "").lower() == name.lower(): return i
    for i in ids:
        if i in ok: return i
    return None
