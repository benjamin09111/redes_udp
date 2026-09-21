import urllib.request
import urllib.parse
import json

# 1. Search for Juan Manuel Ureta in Overpass / Nominatim
print("Searching for Juan Manuel Ureta...")
url_nom = "https://nominatim.openstreetmap.org/search?q=" + urllib.parse.quote("Juan Manuel Ureta, Puchuncaví") + "&format=json&addressdetails=1"
req = urllib.request.Request(url_nom, headers={'User-Agent': 'UAV-Historic-Research/1.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"Nominatim results for Juan Manuel Ureta: {len(res)}")
        for r in res:
            print(f"- {r.get('display_name')} -> [{r.get('lon')}, {r.get('lat')}]")
        with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\search_ureta.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"Nominatim error: {e}")

# 2. Query Overpass for street Juan Manuel Ureta and all historic elements
query_historic = """[out:json][timeout:35];
(
  way["name"~"Juan Manuel Ureta",i](-32.85,-71.56,-32.65,-71.30);
  node["historic"](-32.85,-71.56,-32.65,-71.30);
  way["historic"](-32.85,-71.56,-32.65,-71.30);
  relation["historic"](-32.85,-71.56,-32.65,-71.30);
  node["heritage"](-32.85,-71.56,-32.65,-71.30);
  way["heritage"](-32.85,-71.56,-32.65,-71.30);
  node["tourism"="museum"](-32.85,-71.56,-32.65,-71.30);
  way["tourism"="museum"](-32.85,-71.56,-32.65,-71.30);
);
out center tags;
"""

mirrors = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

data = urllib.parse.urlencode({'data': query_historic}).encode('utf-8')
for m in mirrors:
    try:
        print(f"Querying historic elements from {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Historic-Research/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elements retrieved: {len(elems)}")
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_historic_raw.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            break
    except Exception as e:
        print(f"Error on {m}: {e}")
