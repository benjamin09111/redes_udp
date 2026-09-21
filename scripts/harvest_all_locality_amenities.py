import urllib.request
import urllib.parse
import json

# Query specifically targeting the sectors:
# El Alto (Puchuncaví [-32.72, -71.44]), El Alto (Quintero [-32.785, -71.50])
# Los Tomes ([-32.72, -71.45])
# Comunidad La Estancilla ([-32.745, -71.39])
# El Rincón ([-32.725, -71.37])
# El Rungue / Rungue ([-32.698, -71.41])

# We can query a bounding box covering the entire region:
# south: -32.85, west: -71.56, north: -32.65, east: -71.32
# and request ALL amenities, leisure, tourism, shop, healthcare, historic, place, office, emergency
query_amenities = """[out:json][timeout:35];
(
  node["amenity"](-32.85,-71.56,-32.65,-71.32);
  way["amenity"](-32.85,-71.56,-32.65,-71.32);
  node["leisure"](-32.85,-71.56,-32.65,-71.32);
  way["leisure"](-32.85,-71.56,-32.65,-71.32);
  node["tourism"](-32.85,-71.56,-32.65,-71.32);
  way["tourism"](-32.85,-71.56,-32.65,-71.32);
  node["shop"](-32.85,-71.56,-32.65,-71.32);
  way["shop"](-32.85,-71.56,-32.65,-71.32);
  node["healthcare"](-32.85,-71.56,-32.65,-71.32);
  way["healthcare"](-32.85,-71.56,-32.65,-71.32);
  node["place"~"village|hamlet|isolated_dwelling|suburb|neighbourhood"](-32.85,-71.56,-32.65,-71.32);
);
out center tags;
"""

mirrors = [
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

data = urllib.parse.urlencode({'data': query_amenities}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Querying all amenities across region in {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Comprehensive-Audit/1.0'})
        with urllib.request.urlopen(req, timeout=35) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total amenities and places found: {len(elems)}")
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_amenities_broad.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            break
    except Exception as e:
        print(f"Mirror {m} error: {e}")
