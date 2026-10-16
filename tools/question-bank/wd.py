import json, sys, time, urllib.request, urllib.parse, hashlib, os
UA = "krillion-clone-builder/1.0 (rufus.gordonheywood@gmail.com)"
CACHE = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE, exist_ok=True)
def sparql(q, tries=4):
    h = hashlib.sha1(q.encode()).hexdigest()
    p = os.path.join(CACHE, h + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    for t in range(tries):
        try:
            req = urllib.request.Request("https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"}), headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=62) as r:
                data = json.load(r)["results"]["bindings"]
            json.dump(data, open(p, "w"))
            return data
        except Exception as e:
            msg = str(e)
            last = msg
            if "429" in msg: time.sleep(20); continue
            if "timed out" in msg or "504" in msg or "500" in msg: break  # server-side timeout: retrying won't help
            time.sleep(3 + 5 * t)
            last = msg
    print("  !! query failed:", last, file=sys.stderr)
    return None
if __name__ == "__main__":
    print(json.dumps(sparql(sys.argv[1]), indent=1)[:3000])
