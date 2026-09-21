import urllib.request
import urllib.parse
import json
import time

queries = [
    "Pista Escuadrón 4WD Quintero",
    "Pista 4WD Quintero",
    "Escuadron 4WD Quintero",
    "F-210, Quintero, Valparaíso",
    "Ruta F-210 Quintero",
    "Parque infantil Quintero",
    "Plaza de Juegos Quintero",
    "Plaza Infantil Quintero",
    "Loncura, Quintero",
    "La Chocota, Puchuncaví",
    "La Greda, Puchuncaví",
    "Las Salinas, Puchuncaví",
    "Campiche, Puchuncaví"
]

results = []
for q in queries:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Urban-Expansion/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if data:
                res = data[0]
                lat = float(res['lat'])
                lon = float(res['lon'])
                print(f"[OK] {q} -> [{lat:.5f}, {lon:.5f}] | {res.get('display_name')}")
                results.append({"q": q, "lat": lat, "lon": lon, "display": res.get('display_name')})
            else:
                print(f"[NONE] {q}")
    except Exception as e:
        print(f"[ERR] {q}: {e}")
    time.sleep(1)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\search_user_requests.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
