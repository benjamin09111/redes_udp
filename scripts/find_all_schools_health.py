import urllib.request
import urllib.parse
import json

query = """
[out:json][timeout:25];
(
  node["amenity"~"school|kindergarten|hospital|clinic|doctors"](-32.84, -71.56, -32.68, -71.38);
  way["amenity"~"school|kindergarten|hospital|clinic|doctors"](-32.84, -71.56, -32.68, -71.38);
);
out center;
"""

mirrors = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

data = urllib.parse.urlencode({'data': query}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Probando {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Research-Chile/1.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            res = json.loads(r.read())
            elements = res.get('elements', [])
            print(f"Total elementos encontrados: {len(elements)}")
            items = []
            for el in elements:
                tags = el.get('tags', {})
                lat = el.get('lat') or (el.get('center', {}).get('lat'))
                lon = el.get('lon') or (el.get('center', {}).get('lon'))
                name = tags.get('name')
                amenity = tags.get('amenity')
                if not lat or not lon:
                    continue
                items.append({
                    "id": el.get('id'),
                    "name": name or f"{amenity.capitalize()} sin nombre",
                    "amenity": amenity,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "tags": tags
                })
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_schools_health.json', 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            
            for it in items:
                print(f"[{it['amenity']}] {it['name']} -> ({it['lat']}, {it['lon']})")
            break
    except Exception as e:
        print(f"Error con {m}: {e}")
