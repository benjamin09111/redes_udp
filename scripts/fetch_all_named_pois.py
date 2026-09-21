import urllib.request
import urllib.parse
import json
import time

BBOX = "-32.83,-71.56,-32.70,-71.38"

# Consulta limpia para traer TODO elemento con nombre en la zona
q = f"""[out:json][timeout:35];
(
  node["name"]({BBOX});
  way["name"]({BBOX});
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
        print(f"Probando mirror: {m}...")
        req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Complete-Audit/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            elems = res.get('elements', [])
            print(f"Éxito con {m}! Total elementos con nombre encontrados: {len(elems)}")
            
            classified = []
            for el in elems:
                tags = el.get('tags', {})
                name = tags.get('name')
                lat = el.get('lat') or (el.get('center', {}).get('lat'))
                lon = el.get('lon') or (el.get('center', {}).get('lon'))
                if not name or not lat or not lon:
                    continue
                
                # Clasificar según tags relevantes
                amenity = tags.get('amenity', '')
                shop = tags.get('shop', '')
                leisure = tags.get('leisure', '')
                tourism = tags.get('tourism', '')
                building = tags.get('building', '')
                highway = tags.get('highway', '')
                natural = tags.get('natural', '')
                
                # Excluir calles ordinarias o casas sin interés
                if highway and not (amenity or shop or leisure or tourism):
                    continue
                
                classified.append({
                    "id": el.get('id'),
                    "type": el.get('type'),
                    "name": name,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "amenity": amenity,
                    "shop": shop,
                    "leisure": leisure,
                    "tourism": tourism,
                    "building": building,
                    "all_tags": tags
                })
            
            with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'w', encoding='utf-8') as f:
                json.dump(classified, f, indent=2, ensure_ascii=False)
            
            print(f"Total POIs clasificados con nombre: {len(classified)}")
            break
    except Exception as e:
        print(f"Fallo en {m}: {e}")
        time.sleep(1)
