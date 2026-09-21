import urllib.request
import urllib.parse
import json

# Fetch residential/highway geometry for the new sectors to form precise urban zone polygons
query_roads = """[out:json][timeout:30];
(
  way["highway"~"residential|unclassified|tertiary|living_street"](-32.76,-71.46,-32.68,-71.35);
  way["landuse"~"residential"](-32.76,-71.46,-32.68,-71.35);
  way["place"~"hamlet|village|isolated_dwelling"](-32.76,-71.46,-32.68,-71.35);
);
out geom;
"""

mirrors = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

data = urllib.parse.urlencode({'data': query_roads}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Fetching road geometry for new sectors from {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Urban-Analysis/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elements retrieved: {len(elems)}")
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\new_sectors_geom.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            break
    except Exception as e:
        print(f"Error on {m}: {e}")
