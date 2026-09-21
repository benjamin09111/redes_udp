import urllib.request
import urllib.parse
import json
import time

# 1. Test higher ed & university search in Nominatim
queries_higher_ed = [
    "Universidad Quintero",
    "Universidad Puchuncaví",
    "CFT Quintero",
    "Centro de Formacion Tecnica Quintero",
    "Estacion Costera Quintero",
    "Estacion Biologia Marina Montemar",
    "Sede Universitaria Quintero",
    "Instituto Quintero",
    "CFT Estatal Puchuncaví",
    "CEIA Quintero"
]

results_hed = []
for q in queries_higher_ed:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=2&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Thesis-Search/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                print(f"[FOUND] {q} -> {data[0].get('display_name')}")
                results_hed.append({"query": q, "res": data[0]})
            else:
                print(f"[NO] {q}")
    except Exception as e:
        print(f"[ERR] {q}: {e}")
    time.sleep(1)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\higher_ed_search.json', 'w', encoding='utf-8') as f:
    json.dump(results_hed, f, indent=2, ensure_ascii=False)
