import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_schools_raw.json', 'r', encoding='utf-8') as f:
    osm_schools = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    current_geojson = json.load(f)

current_edu = [f for f in current_geojson['features'] if f['properties']['category'] == 'education']
current_coords = [(f['geometry']['coordinates'][0], f['geometry']['coordinates'][1]) for f in current_edu]

print(f"Colegios actualmente en nodes.geojson: {len(current_edu)}")
print(f"Elementos educativos encontrados en OSM: {len(osm_schools)}\n")

osm_items = []
for el in osm_schools:
    tags = el.get('tags', {})
    lat = el.get('lat') or el.get('center', {}).get('lat')
    lon = el.get('lon') or el.get('center', {}).get('lon')
    name = tags.get('name') or tags.get('operator') or tags.get('official_name')
    amenity = tags.get('amenity') or tags.get('building') or tags.get('landuse')
    
    osm_items.append({
        "id": el.get('id'),
        "type": el.get('type'),
        "name": name,
        "amenity": amenity,
        "lat": round(lat, 6) if lat else None,
        "lon": round(lon, 6) if lon else None,
        "tags": tags
    })

print("=== LISTA DE ELEMENTOS EN OPENSTREETMAP ===")
for idx, it in enumerate(osm_items):
    matched = False
    for cx, cy in current_coords:
        if it['lon'] and it['lat']:
            dist = ((it['lon'] - cx)**2 + (it['lat'] - cy)**2)**0.5
            if dist < 0.002: # ~200 metros
                matched = True
                break
    status = "[YA EN GEOJSON]" if matched else "[NUEVO DETECTADO]"
    print(f"{idx+1}. {status} {it['name']} ({it['amenity']}) -> [{it['lat']}, {it['lon']}]")
