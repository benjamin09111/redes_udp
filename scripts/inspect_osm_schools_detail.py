import json
import urllib.request
import urllib.parse
import time

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_schools_raw.json', 'r', encoding='utf-8') as f:
    osm_schools = json.load(f)

# Ver el item 31
for el in osm_schools:
    lat = el.get('lat') or el.get('center', {}).get('lat')
    if lat and abs(lat - (-32.740037)) < 0.001:
        print("Item 31 en OSM:")
        print(json.dumps(el, indent=2, ensure_ascii=False))

# Consultar escuelas rurales y jardines de Quintero y Puchuncaví en Nominatim
targets = [
    "Escuela El Rincón Puchuncaví",
    "Escuela La Laguna Puchuncaví",
    "Escuela Pucalán Puchuncaví",
    "Escuela San Antonio Puchuncaví",
    "Jardín Infantil Las Ventanas",
    "Jardín Infantil Los Pinitos Horcón",
    "Jardín Infantil Mar y Cielo Quintero",
    "Jardín Infantil Rayito de Sol Quintero",
    "Colegio Pioneros Costa Puchuncaví",
    "Sala Cuna Quintero"
]

results = []
for t in targets:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(t)}&format=json&limit=1&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-School-Mineduc/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if data:
                res = data[0]
                lat = float(res['lat'])
                lon = float(res['lon'])
                print(f"[OK] {t} -> [{lat:.5f}, {lon:.5f}] ({res.get('display_name')})")
                results.append({"name": t, "lat": lat, "lon": lon, "display": res.get('display_name')})
            else:
                print(f"[NONE] {t}")
    except Exception as e:
        print(f"[ERR] {t}: {e}")
    time.sleep(1)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\additional_schools_mineduc.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
