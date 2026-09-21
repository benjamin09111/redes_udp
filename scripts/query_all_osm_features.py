import urllib.request
import urllib.parse
import json

BBOX = "-32.84,-71.56,-32.68,-71.36"

# Consulta exhaustiva a Overpass para encontrar TODO elemento con tag significativo
query = f"""[out:json][timeout:35];
(
  node["amenity"]({BBOX});
  way["amenity"]({BBOX});
  node["tourism"]({BBOX});
  way["tourism"]({BBOX});
  node["leisure"]({BBOX});
  way["leisure"]({BBOX});
  node["shop"]({BBOX});
  way["shop"]({BBOX});
  node["office"]({BBOX});
  way["office"]({BBOX});
  node["historic"]({BBOX});
  way["historic"]({BBOX});
);
out center tags;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter"
]

data = urllib.parse.urlencode({'data': query}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Consultando Overpass API en {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-OSM-Complete-Harvest/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elementos con tags en OSM: {len(elems)}")
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_full_amenities_all.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            
            print("Guardado en osm_full_amenities_all.json")
            break
    except Exception as e:
        print(f"Fallo en {m}: {e}")
