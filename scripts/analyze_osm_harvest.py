import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_full_amenities_all.json', 'r', encoding='utf-8') as f:
    elements = json.load(f)

# Cargar nodos existentes en GeoJSON
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    current_geojson = json.load(f)

existing_coords = []
for feat in current_geojson['features']:
    c = feat['geometry']['coordinates']
    existing_coords.append((c[0], c[1]))

print(f"Total elementos en extracción OSM: {len(elements)}")
print(f"Total nodos actuales en GeoJSON: {len(current_geojson['features'])}\n")

schools = []
other_new = []

for el in elements:
    tags = el.get('tags', {})
    lat = el.get('lat') or el.get('center', {}).get('lat')
    lon = el.get('lon') or el.get('center', {}).get('lon')
    if not lat or not lon:
        continue
    
    name = tags.get('name') or tags.get('operator') or tags.get('description')
    amenity = tags.get('amenity')
    tourism = tags.get('tourism')
    leisure = tags.get('leisure')
    shop = tags.get('shop')
    office = tags.get('office')
    historic = tags.get('historic')
    
    # Comprobar si ya existe en coordenadas cercanas (< 150m)
    is_existing = any(((lon - ex[0])**2 + (lat - ex[1])**2)**0.5 < 0.0015 for ex in existing_coords)
    
    if amenity in ['school', 'kindergarten', 'childcare', 'college', 'university', 'language_school']:
        schools.append({
            "id": el.get('id'),
            "name": name or f"Colegio/Jardín ({amenity})",
            "has_name": bool(name),
            "amenity": amenity,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "is_existing": is_existing,
            "tags": tags
        })
    elif not is_existing and name:
        other_new.append({
            "id": el.get('id'),
            "name": name,
            "type": amenity or tourism or leisure or shop or office or historic,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "tags": tags
        })

print(f"=== COLEGIOS / JARDINES ENCONTRADOS EN OSM: {len(schools)} ===")
for s in schools:
    st = "[YA EN RED]" if s['is_existing'] else "[NUEVO A AGREGAR]"
    print(f"  {st} {s['name']} ({s['amenity']}) -> [{s['lat']}, {s['lon']}]")

print(f"\n=== OTROS ELEMENTOS RELEVANTES CON NOMBRE NO INCLUIDOS: {len(other_new)} ===")
for o in other_new[:25]:
    print(f"  - {o['name']} ({o['type']}) -> [{o['lat']}, {o['lon']}]")
