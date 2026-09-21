import urllib.request
import urllib.parse
import json
import time

BBOX = "-32.84,-71.56,-32.68,-71.38"

MIRRORS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

def query_overpass(query_str):
    full_query = f"""[out:json][timeout:35];
(
{query_str}
);
out center;
"""
    data = urllib.parse.urlencode({'data': full_query}).encode('utf-8')
    for m in MIRRORS:
        try:
            print(f"Probando {m}...")
            req = urllib.request.Request(m, data=data, headers={'User-Agent': 'UAV-Research-Crowd-Nodes/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read().decode('utf-8'))
                elems = res.get('elements', [])
                print(f"Éxito con {m}: {len(elems)} elementos")
                return elems
        except Exception as e:
            print(f"Fallo en {m}: {e}")
            time.sleep(1)
    return []

# 1. Universidades, CFT, Institutos de Investigación y Educación Superior
print("\n=== Consultando Universidades / Educación Superior / Investigación ===")
q_higher_ed = f"""
node["amenity"~"university|college|research_institute"]({BBOX});
way["amenity"~"university|college|research_institute"]({BBOX});
"""
elems_higher_ed = query_overpass(q_higher_ed)

# 2. Centros Comerciales, Supermercados, Mercados y Ferias
print("\n=== Consultando Comercio y Supermercados / Mercados ===")
q_commerce = f"""
node["shop"~"supermarket|mall|department_store"]({BBOX});
way["shop"~"supermarket|mall|department_store"]({BBOX});
node["amenity"~"marketplace"]({BBOX});
way["amenity"~"marketplace"]({BBOX});
"""
elems_commerce = query_overpass(q_commerce)

# 3. Lugares de Gran Aglomeración / Concurrencia (Plazas, Terminales, Estadios, Deporte, Cívicos)
print("\n=== Consultando Lugares de Gran Concurrencia (Plazas, Terminales, Estadios, Cívicos) ===")
q_crowd = f"""
node["amenity"~"bus_station|townhall|community_centre|police|fire_station|place_of_worship"]({BBOX});
way["amenity"~"bus_station|townhall|community_centre|police|fire_station|place_of_worship"]({BBOX});
node["leisure"~"stadium|sports_centre"]({BBOX});
way["leisure"~"stadium|sports_centre"]({BBOX});
"""
elems_crowd = query_overpass(q_crowd)

# 4. Salud adicional (Farmacias grandes, centros médicos, clínicas)
print("\n=== Consultando Salud Adicional ===")
q_health = f"""
node["amenity"~"pharmacy|dentist|doctors|social_facility"]({BBOX});
way["amenity"~"pharmacy|dentist|doctors|social_facility"]({BBOX});
"""
elems_health = query_overpass(q_health)

# 5. Educación adicional (todos los colegios y jardines)
print("\n=== Consultando Educación Adicional ===")
q_edu = f"""
node["amenity"~"school|kindergarten|childcare"]({BBOX});
way["amenity"~"school|kindergarten|childcare"]({BBOX});
"""
elems_edu = query_overpass(q_edu)

def extract_items(elements, group_name):
    extracted = []
    seen = set()
    for el in elements:
        tags = el.get('tags', {})
        lat = el.get('lat') or (el.get('center', {}).get('lat'))
        lon = el.get('lon') or (el.get('center', {}).get('lon'))
        if not lat or not lon:
            continue
        name = tags.get('name') or tags.get('operator') or tags.get('brand')
        amenity = tags.get('amenity') or tags.get('shop') or tags.get('leisure')
        
        # Deduplicar coordenadas muy cercanas
        coord_key = (round(lon, 4), round(lat, 4))
        if coord_key in seen:
            continue
        seen.add(coord_key)
        
        extracted.append({
            "osm_id": el.get('id'),
            "osm_type": el.get('type'),
            "name": name or f"{group_name} ({amenity})",
            "has_proper_name": bool(name),
            "group": group_name,
            "category_tag": amenity,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "tags": tags
        })
    return extracted

data_summary = {
    "higher_education": extract_items(elems_higher_ed, "higher_education"),
    "commercial_supermarkets": extract_items(elems_commerce, "commercial"),
    "crowded_places": extract_items(elems_crowd, "crowded_places"),
    "health_additional": extract_items(elems_health, "health"),
    "education_all": extract_items(elems_edu, "education")
}

output_path = r"c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_raw_extracted.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data_summary, f, indent=2, ensure_ascii=False)

print("\n=== RESUMEN EXTRACCIÓN ===")
for k, v in data_summary.items():
    print(f"{k}: {len(v)} elementos únicos")
    for item in v[:5]:
        print(f"   - {item['name']} ({item['lat']}, {item['lon']}) [{item.get('category_tag')}]")
