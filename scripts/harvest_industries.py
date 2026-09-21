import urllib.request
import urllib.parse
import json
import time

BBOX = "-32.85,-71.56,-32.67,-71.34"

# 1. Consulta exhaustiva de todas las industrias, fábricas, chimeneas, estanques y fuentes de emisión
query_industries = f"""[out:json][timeout:35];
(
  node["man_made"~"chimney|storage_tank|works|wastewater_plant"]({BBOX});
  way["man_made"~"chimney|storage_tank|works|wastewater_plant"]({BBOX});
  node["industrial"]({BBOX});
  way["industrial"]({BBOX});
  node["landuse"="industrial"]({BBOX});
  way["landuse"="industrial"]({BBOX});
  node["power"~"plant|substation|generator"]({BBOX});
  way["power"~"plant|substation|generator"]({BBOX});
);
out center tags;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

data = urllib.parse.urlencode({'data': query_industries}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Consultando fuentes industriales en {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Industrial-Audit/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elementos industriales encontrados: {len(elems)}")
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_industries_raw.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            break
    except Exception as e:
        print(f"Fallo en {m}: {e}")
