import json
import urllib.request

CANDIDATES = [
    "www.allbirds.com",
    "www.gymshark.com",
    "www.fashionnova.com",
    "www.colourpop.com",
    "boat-lifestyle.com",
    "mamaearth.in",
]

for domain in CANDIDATES:
    url = f"https://{domain}/products.json?limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "PriceWatch/1.0 (learning project)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            n = len(data.get("products", []))
            print(f"OK    {domain}  (products feed works, got {n})")
    except Exception as e:
        print(f"FAIL  {domain}  ({type(e).__name__})")