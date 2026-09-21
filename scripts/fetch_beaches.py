import urllib.request
import urllib.parse
import json

BBOX = "-32.84,-71.56,-32.68,-71.38"

q = f"""[out:json][timeout:25];
(
  node["natural"="beach"]({BBOX});
  way["natural"="beach"]({BBOX});
  relation["natural"="beach"]({BBOX});
  node["leisure"="beach_resort"]({BBOX});
  way["leisure"="beach_resort"]({BBOX});
);
out center tags;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

data = urllib.parse.urlencode({'data': q}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Probando {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Beach-Search/1.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elementos playa encontrados: {len(elems)}")
            beaches = []
            for el in elems:
                tags = el.get('tags', {})
                lat = el.get('lat') or el.get('center', {}).get('lat')
                lon = el.get('lon') or el.get('center', {}).get('lon')
                name = tags.get('name', 'Playa sin nombre')
                beaches.append({
                    "id": el.get('id'),
                    "name": name,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "tags": tags
                })
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_beaches.json', 'w', encoding='utf-8') as f:
                json.dump(beaches, f, indent=2, ensure_ascii=False)
            
            for b in beaches:
                print(f"  - {b['name']} ({b['lat']}, {b['lon']})")
            break
    except Exception as e:
        print(f"Fallo con {m}: {e}")
