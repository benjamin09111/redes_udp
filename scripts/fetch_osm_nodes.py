import urllib.request
import urllib.parse
import json
import time
import os

BBOX = "-32.83,-71.56,-32.70,-71.38"

MIRRORS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

def query_osm(subquery):
    full_query = f"""[out:json][timeout:25];
(
  {subquery}
);
out center;
"""
    data = urllib.parse.urlencode({'data': full_query}).encode('utf-8')
    for mirror in MIRRORS:
        try:
            print(f"Probando mirror: {mirror} ...")
            req = urllib.request.Request(mirror, data=data, headers={'User-Agent': 'UAV-Resilience-Research/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                print(f"Éxito con {mirror}: {len(res.get('elements', []))} elementos.")
                return res.get('elements', [])
        except Exception as e:
            print(f"Fallo en {mirror}: {e}")
            time.sleep(1)
    return []

# 1. NIVEL 1: Industrial y Emisión
print("\n--- Consultando Nivel 1: Industrial / Emisión ---")
q1 = f"""
node["man_made"="chimney"]({BBOX});
way["man_made"="chimney"]({BBOX});
way["power"="plant"]({BBOX});
way["landuse"="industrial"]({BBOX});
"""
elements_l1 = query_osm(q1)

# 2. NIVEL 2: Receptores Sensibles (Educación y Salud)
print("\n--- Consultando Nivel 2: Receptores Sensibles (Salud/Colegios) ---")
q2 = f"""
node["amenity"~"school|hospital|clinic|kindergarten"]({BBOX});
way["amenity"~"school|hospital|clinic|kindergarten"]({BBOX});
"""
elements_l2 = query_osm(q2)

# 3. NIVEL 3: Zonas Despejadas / Aterrizaje Emergencia
print("\n--- Consultando Nivel 3: Zonas Despejadas / Aterrizaje ---")
q3 = f"""
node["natural"~"beach|sand"]({BBOX});
way["natural"~"beach|sand"]({BBOX});
"""
elements_l3 = query_osm(q3)

# Procesar y estructurar
def parse_elements(elements, cat_type):
    parsed = []
    seen_names = set()
    for el in elements:
        tags = el.get('tags', {})
        lat = el.get('lat') or (el.get('center', {}).get('lat'))
        lon = el.get('lon') or (el.get('center', {}).get('lon'))
        if not lat or not lon:
            continue
        
        name = tags.get('name') or tags.get('operator') or tags.get('description')
        if not name:
            # Asignar nombre descriptivo si no tiene
            sub = tags.get('amenity') or tags.get('industrial') or tags.get('power') or tags.get('natural') or tags.get('man_made')
            name = f"{cat_type.replace('_', ' ').title()} ({sub})"
        
        key = (round(lon, 4), round(lat, 4))
        if key in seen_names:
            continue
        seen_names.add(key)
        
        parsed.append({
            "id": f"{cat_type}_{el.get('id')}",
            "name": name,
            "category": cat_type,
            "coords": [round(lon, 6), round(lat, 6)],
            "tags": {k: v for k, v in tags.items() if k in ['name', 'amenity', 'power', 'industrial', 'natural', 'man_made', 'operator']}
        })
    return parsed

l1_parsed = parse_elements(elements_l1, "emission_source")
l2_parsed = parse_elements(elements_l2, "sensitive_receptor")
l3_parsed = parse_elements(elements_l3, "safe_landing")

result_all = {
    "summary": {
        "level1_industrial": len(l1_parsed),
        "level2_sensitive": len(l2_parsed),
        "level3_emergency": len(l3_parsed)
    },
    "level1": l1_parsed,
    "level2": l2_parsed,
    "level3": l3_parsed
}

output_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_parsed_nodes.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(result_all, f, indent=2, ensure_ascii=False)

print("\n=== EXTRACCIÓN COMPLETADA ===")
print(f"Nivel 1 (Industrial/Emisión): {len(l1_parsed)} nodos")
print(f"Nivel 2 (Receptores Sensibles): {len(l2_parsed)} nodos")
print(f"Nivel 3 (Playas/Dunas/Aterrizaje): {len(l3_parsed)} nodos")
print(f"Archivo guardado en: {output_path}")
