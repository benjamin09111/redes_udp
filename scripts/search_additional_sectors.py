import urllib.request
import urllib.parse
import json
import time

sectors = [
    "El Alto Quintero",
    "El Alto Puchuncaví",
    "Los Tomes Puchuncaví",
    "Los Tomes Quintero",
    "La Estancilla Puchuncaví",
    "Comunidad La Estancilla Puchuncaví",
    "El Rincón Puchuncaví",
    "El Rungue Puchuncaví",
    "Rungue Puchuncaví"
]

results = []
for s in sectors:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(s)}&format=json&limit=2&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-New-Sectors/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read())
            if data:
                res = data[0]
                lat = float(res['lat'])
                lon = float(res['lon'])
                print(f"[OK] {s} -> [{lat:.5f}, {lon:.5f}] | {res.get('display_name')}")
                results.append({"sector": s, "lat": lat, "lon": lon, "display": res.get('display_name')})
            else:
                print(f"[NONE] {s}")
    except Exception as e:
        print(f"[ERR] {s}: {e}")
    time.sleep(1)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\search_additional_sectors.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
