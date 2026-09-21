import urllib.request
import urllib.parse
import json
import time

test_queries = [
    # Quintero
    ("Plaza Quintero", "crowded_area", "Plaza de Armas / Plaza Ignacio Carrera Pinto"),
    ("Plaza Los Deportistas Quintero", "crowded_area", "Plaza Los Deportistas"),
    ("Caleta El Manzano", "crowded_area", "Caleta El Manzano"),
    ("Carabineros Subcomisaría Quintero", "crowded_area", "Subcomisaría Carabineros Quintero"),
    ("Santa Isabel, Quintero", "commercial", "Supermercado Santa Isabel Quintero"),
    ("Feria Quintero", "commercial", "Feria y Comercio Ambulante Quintero"),
    
    # Puchuncaví
    ("Plaza Puchuncaví", "crowded_area", "Plaza de Armas de Puchuncaví"),
    ("Parroquia Puchuncaví", "crowded_area", "Parroquia Nuestra Señora del Rosario Puchuncaví"),
    ("Bomberos Puchuncaví", "crowded_area", "Cuerpo de Bomberos Puchuncaví"),
    ("Bomberos Ventanas", "crowded_area", "Cuerpo de Bomberos Las Ventanas"),
    ("Escuela Los Maitenes", "education", "Escuela Básica Los Maitenes"),
    ("Posta Los Maitenes", "health", "Posta de Salud Rural Los Maitenes"),
    ("Posta Campiche", "health", "Posta de Salud Rural Campiche"),
    ("CESFAM Puchuncaví", "health", "CESFAM Puchuncaví"),
    
    # Loncura / Ventanas
    ("Plaza Loncura", "crowded_area", "Plaza Loncura"),
    ("Plaza Las Ventanas", "crowded_area", "Plaza Las Ventanas")
]

results = []
for q, cat, label in test_queries:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Test-2/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"[FOUND] {label} ({q}) -> [{lat:.5f}, {lon:.5f}]")
                results.append({"name": label, "cat": cat, "lat": lat, "lon": lon, "display": data[0].get('display_name')})
            else:
                print(f"[NONE] {label} ({q})")
    except Exception as e:
        print(f"[ERR] {label}: {e}")
    time.sleep(1)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\second_batch.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
