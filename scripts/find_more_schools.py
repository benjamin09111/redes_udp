import urllib.request
import urllib.parse
import json

# Buscar en una bounding box aún más generosa para capturar cualquier recinto educativo
BBOX = "-32.86,-71.57,-32.66,-71.34"

query = f"""[out:json][timeout:35];
(
  node[~"amenity|name|building"~"school|colegio|liceo|escuela|jardin|kinder|educa",i]({BBOX});
  way[~"amenity|name|building"~"school|colegio|liceo|escuela|jardin|kinder|educa",i]({BBOX});
  relation[~"amenity|name|building"~"school|colegio|liceo|escuela|jardin|kinder|educa",i]({BBOX});
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
        print(f"Probando {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Broad-Education/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Total elementos encontrados con regex educativo: {len(elems)}")
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_broad_education.json', 'w', encoding='utf-8') as f:
                json.dump(elems, f, indent=2, ensure_ascii=False)
            
            for el in elems:
                tags = el.get('tags', {})
                name = tags.get('name')
                lat = el.get('lat') or el.get('center', {}).get('lat')
                lon = el.get('lon') or el.get('center', {}).get('lon')
                amenity = tags.get('amenity')
                print(f"  [{amenity}] {name} ({lat}, {lon})")
            break
    except Exception as e:
        print(f"Error con {m}: {e}")
