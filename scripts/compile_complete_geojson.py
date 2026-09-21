import json

# Cargar archivos base
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_beaches.json', 'r', encoding='utf-8') as f:
    beaches_raw = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    pois_raw = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    current_geojson = json.load(f)

# Guardar nodos existentes como lista base
all_nodes = []
seen_ids = set()
seen_coords = set()

for feat in current_geojson['features']:
    props = feat['properties']
    coords = feat['geometry']['coordinates']
    all_nodes.append({
        "id": props['id'],
        "name": props['name'],
        "category": props['category'],
        "type": props['type'],
        "role": props['role'],
        "icon": props['icon'],
        "color": props['color'],
        "priority": props.get('priority', 3),
        "coords": coords,
        "pollutants": props.get('pollutants', [])
    })
    seen_ids.add(props['id'])
    seen_coords.add((round(coords[0], 4), round(coords[1], 4)))

print(f"Base de partida: {len(all_nodes)} nodos existentes.")

# 1. PLAYAS (28)
clean_beach_names = {
    "Playa Los Enamorados": [-71.529716, -32.76978, 2],
    "Playa Las Conchitas": [-71.527321, -32.771316, 2],
    "Playa El Durazno": [-71.526717, -32.775683, 2],
    "Playa El Caleuche": [-71.52666, -32.77367, 2],
    "Playa Waikiki": [-71.527142, -32.774595, 2],
    "Playa El Papagayo": [-71.533915, -32.780007, 2],
    "Playa El Libro": [-71.537605, -32.775621, 2],
    "Playa La Tortuga": [-71.534502, -32.778263, 2],
    "Playa Las Cañitas": [-71.537937, -32.784669, 2],
    "Playa La Caleta": [-71.53731, -32.784541, 2],
    "Playa El Manzano": [-71.526778, -32.781522, 2],
    "Playa Albatros": [-71.5253, -32.782378, 2],
    "Playa El Burrito": [-71.535147, -32.783419, 2],
    "Playa Giligan": [-71.535015, -32.777449, 2],
    "Playa Los Bolones": [-71.530437, -32.769104, 2],
    "Playa El Coronel": [-71.52849, -32.769572, 2],
    "Playa Loncura": [-71.509192, -32.779644, 2],
    "Playa Ventanas": [-71.488208, -32.744452, 2],
    "Playa El Clarón": [-71.487815, -32.71079, 2],
    "Playa Cau-Cau": [-71.496475, -32.709927, 2],
    "Playa de Horcón": [-71.49099, -32.709093, 2],
    "Playa Larga de Horcón": [-71.473653, -32.710284, 2],
    "Playa El Tebo": [-71.502999, -32.725604, 2],
    "Playa Quirilluca": [-71.458373, -32.697404, 2],
    "Playa Luna": [-71.462585, -32.702783, 2],
    "Playa El Barco": [-71.452461, -32.690244, 2],
    "Playa Corral de los Perros": [-71.454207, -32.692525, 2],
    "Playa Las Ágatas": [-71.456398, -32.694496, 2]
}

for name, coords in clean_beach_names.items():
    key = (round(coords[0], 4), round(coords[1], 4))
    if key in seen_coords:
        continue
    node_id = f"beach_{name.lower().replace(' ', '_').replace('-', '_')}"
    seen_coords.add(key)
    all_nodes.append({
        "id": node_id,
        "name": name,
        "category": "beach",
        "type": "beach",
        "role": f"Balneario y Franja Costera: {name} (Aglomeración de Bañistas)",
        "icon": "🏖",
        "color": "#06b6d4", # Cyan
        "priority": 4,
        "coords": coords
    })

# 2. HOTELES, CABAÑAS Y HOSPEDAJES
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    tourism = p.get('tourism', '')
    
    is_lodging = (tourism in ['hotel', 'motel', 'hostel', 'guest_house', 'chalet', 'camp_site'] or 
                  any(k in name_l for k in ['hotel', 'hostal', 'cabaña', 'cabañas', 'resort', 'camping', 'posada', 'hostería']))
    
    if is_lodging:
        key = (round(lon, 4), round(lat, 4))
        if key in seen_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_coords.add(key)
        node_id = f"hotel_{p['id']}"
        all_nodes.append({
            "id": node_id,
            "name": name,
            "category": "hospitality",
            "type": "hospitality",
            "role": f"Hospedaje Turístico: {name} (Población Flotante y Descanso)",
            "icon": "🏨",
            "color": "#8b5cf6", # Purple / Indigo
            "priority": 3,
            "coords": [lon, lat, 16]
        })

# 3. GASTRONOMÍA Y RESTAURANTES DE CALETA / TURISMO
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    amenity = p.get('amenity', '')
    
    is_resto = (amenity in ['restaurant', 'cafe', 'fast_food', 'bar'] or 'restaurant' in name_l or 'picá' in name_l)
    if is_resto:
        key = (round(lon, 4), round(lat, 4))
        if key in seen_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_coords.add(key)
        node_id = f"resto_{p['id']}"
        all_nodes.append({
            "id": node_id,
            "name": name,
            "category": "restaurant",
            "type": "restaurant",
            "role": f"Gastronomía y Polo Turístico: {name} (Concurrencia en Horas Pico)",
            "icon": "🍽",
            "color": "#f59e0b", # Amber
            "priority": 3,
            "coords": [lon, lat, 15]
        })

# 4. MIRADORES, PARQUES DE VISITA Y ATRACCIONES
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    tourism = p.get('tourism', '')
    leisure = p.get('leisure', '')
    
    is_attr = (tourism in ['viewpoint', 'attraction', 'artwork', 'museum'] or 
               leisure in ['park', 'garden'] or 
               any(k in name_l for k in ['mirador', 'cueva', 'puntilla', 'geositio', 'museo', 'monumento']))
    
    if is_attr:
        key = (round(lon, 4), round(lat, 4))
        if key in seen_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_coords.add(key)
        node_id = f"attr_{p['id']}"
        all_nodes.append({
            "id": node_id,
            "name": name,
            "category": "attraction",
            "type": "attraction",
            "role": f"Atractivo Turístico y Mirador: {name} (Afluencia Visitantes)",
            "icon": "📸",
            "color": "#ec4899", # Pink
            "priority": 3,
            "coords": [lon, lat, 22]
        })

# 5. IGLESIAS / CENTROS DE CULTO ADICIONALES
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    amenity = p.get('amenity', '')
    
    if amenity == 'place_of_worship' or any(k in name_l for k in ['iglesia', 'capilla', 'parroquia', 'templo']):
        key = (round(lon, 4), round(lat, 4))
        if key in seen_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_coords.add(key)
        node_id = f"church_{p['id']}"
        all_nodes.append({
            "id": node_id,
            "name": name,
            "category": "crowded_area",
            "type": "crowd",
            "role": f"Centro de Culto Religioso: {name} (Congregación Masiva)",
            "icon": "⛪",
            "color": "#ec4899",
            "priority": 4,
            "coords": [lon, lat, 20]
        })

print(f"\nTOTAL NODOS CONSOLIDADOS: {len(all_nodes)}")

# Generar GeoJSON
features = []
for n in all_nodes:
    features.append({
        "type": "Feature",
        "properties": {
            "id": n["id"],
            "name": n["name"],
            "category": n["category"],
            "type": n["type"],
            "role": n["role"],
            "icon": n["icon"],
            "color": n["color"],
            "priority": n.get("priority", 3),
            "elevation_msnm": n["coords"][2] if len(n["coords"]) > 2 else 15,
            "pollutants": n.get("pollutants", [])
        },
        "geometry": {
            "type": "Point",
            "coordinates": n["coords"]
        }
    })

geojson_obj = {
    "type": "FeatureCollection",
    "name": "Red_Resiliente_Quintero_Puchuncavi_Alta_Resolucion",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": features
}

output_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_obj, f, indent=2, ensure_ascii=False)

print(f"Archivo guardado exitosamente en: {output_path}")

# Breakdown por categoria
counts = {}
for n in all_nodes:
    c = n['category']
    counts[c] = counts.get(c, 0) + 1

print("\n--- RESUMEN POR CATEGORIA ---")
for cat, cnt in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {cnt} nodos")
