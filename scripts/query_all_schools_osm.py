import urllib.request
import urllib.parse
import json

# Bounding box amplio de toda la zona metropolitana y rural de Quintero y Puchuncaví
BBOX = "-32.85,-71.56,-32.67,-71.36"

query = f"""[out:json][timeout:35];
(
  node["amenity"~"school|kindergarten|childcare|college|university|language_school|prep_school"]({BBOX});
  way["amenity"~"school|kindergarten|childcare|college|university|language_school|prep_school"]({BBOX});
  relation["amenity"~"school|kindergarten|childcare|college|university|language_school|prep_school"]({BBOX});
  node["building"~"school|kindergarten|college|university"]({BBOX});
  way["building"~"school|kindergarten|college|university"]({BBOX});
  node["landuse"="education"]({BBOX});
  way["landuse"="education"]({BBOX});
);
out center tags;
"""

mirrors = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

data = urllib.parse.urlencode({'data': query}).encode('utf-8')

for m in mirrors:
    try:
        print(f"Consultando Overpass API en {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-School-Auditor/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elementos educativos encontrados en OSM: {len(elems)}")
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_schools_raw.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            
            print(f"Guardado en osm_all_schools_raw.json")
            break
    except Exception as e:
        print(f"Error con {m}: {e}")
