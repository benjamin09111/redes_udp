import json

# 1. Cargar playas
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_beaches.json', 'r', encoding='utf-8') as f:
    beaches_raw = json.load(f)

# 2. Cargar POIs nombrados de OSM
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    pois_raw = json.load(f)

# 3. Cargar nodos existentes ya validados
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    current_geojson = json.load(f)

current_features = current_geojson['features']
existing_coords = set()
for feat in current_features:
    coords = feat['geometry']['coordinates']
    existing_coords.add((round(coords[0], 4), round(coords[1], 4)))

print(f"Nodos existentes actuales: {len(current_features)}")

# --- A. Procesar Playas ---
clean_beaches = []
seen_beach_names = set()
for b in beaches_raw:
    name = b['name']
    lat = b['lat']
    lon = b['lon']
    if 'sin nombre' in name.lower() or name in seen_beach_names:
        continue
    # Limitar estrictamente al área de estudio: lat [-32.84, -32.68], lon [-71.56, -71.38]
    if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
        continue
    coord_key = (round(lon, 4), round(lat, 4))
    if coord_key in existing_coords:
        continue
    seen_beach_names.add(name)
    clean_beaches.append({
        "id": f"beach_{b['id']}",
        "name": name,
        "category": "beach",
        "type": "beach",
        "role": f"Balneario y Franja Costera: {name} (Aglomeración Estival / Borde Marítimo)",
        "icon": "🏖",
        "color": "#0ea5e9", # Cyan-Blue
        "priority": 4,
        "coords": [lon, lat, 2] # nivel del mar
    })

print(f"Nuevas playas filtradas: {len(clean_beaches)}")
for cb in clean_beaches:
    print(f"  - {cb['name']} ({cb['coords']})")

# --- B. Procesar Hoteles, Hostales y Cabañas ---
clean_lodging = []
seen_lodging = set()
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    tourism = p.get('tourism', '')
    
    is_lodging = (tourism in ['hotel', 'motel', 'hostel', 'guest_house', 'chalet', 'camp_site'] or 
                  any(k in name_l for k in ['hotel', 'hostal', 'cabaña', 'cabañas', 'resort', 'camping', 'posada']))
    
    if is_lodging and name not in seen_lodging:
        coord_key = (round(lon, 4), round(lat, 4))
        if coord_key in existing_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_lodging.add(name)
        clean_lodging.append({
            "id": f"hotel_{p['id']}",
            "name": name,
            "category": "tourism_hospitality",
            "type": "hospitality",
            "role": f"Hospedaje Turístico: {name} (Concentración de Visitantes y Residentes Temporales)",
            "icon": "🏨",
            "color": "#8b5cf6", # Indigo / Violet
            "priority": 3,
            "coords": [lon, lat, 15]
        })

print(f"\nNuevos alojamientos (hoteles/cabañas/hostales): {len(clean_lodging)}")
for cl in clean_lodging:
    print(f"  - {cl['name']} ({cl['coords']})")

# --- C. Procesar Restaurantes y Gastronomía ---
clean_resto = []
seen_resto = set()
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    amenity = p.get('amenity', '')
    
    is_resto = (amenity in ['restaurant', 'cafe', 'fast_food', 'bar'] or 'restaurant' in name_l)
    if is_resto and name not in seen_resto and name not in seen_lodging:
        coord_key = (round(lon, 4), round(lat, 4))
        if coord_key in existing_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_resto.add(name)
        clean_resto.append({
            "id": f"resto_{p['id']}",
            "name": name,
            "category": "tourism_hospitality",
            "type": "restaurant",
            "role": f"Gastronomía y Concurrencia: {name}",
            "icon": "🍽",
            "color": "#8b5cf6",
            "priority": 3,
            "coords": [lon, lat, 15]
        })

print(f"\nNuevos restaurantes / gastronomía: {len(clean_resto)}")
for cr in clean_resto:
    print(f"  - {cr['name']} ({cr['coords']})")

# --- D. Procesar Miradores, Atracciones y Parques ---
clean_attractions = []
seen_attractions = set()
for p in pois_raw:
    name = p['name']
    name_l = name.lower()
    lat = p['lat']
    lon = p['lon']
    tourism = p.get('tourism', '')
    leisure = p.get('leisure', '')
    
    is_attr = (tourism in ['viewpoint', 'attraction', 'artwork', 'museum'] or 
               leisure in ['park', 'garden'] or 
               any(k in name_l for k in ['mirador', 'cueva', 'puntilla', 'parque', 'geositio', 'museo']))
    
    if is_attr and name not in seen_attractions and name not in seen_lodging and name not in seen_resto:
        coord_key = (round(lon, 4), round(lat, 4))
        if coord_key in existing_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_attractions.add(name)
        clean_attractions.append({
            "id": f"attr_{p['id']}",
            "name": name,
            "category": "tourism_hospitality",
            "type": "attraction",
            "role": f"Punto Turístico y Mirador: {name} (Afluencia de Público)",
            "icon": "📸",
            "color": "#8b5cf6",
            "priority": 4,
            "coords": [lon, lat, 20]
        })

print(f"\nNuevas atracciones / miradores / parques de visita: {len(clean_attractions)}")
for ca in clean_attractions:
    print(f"  - {ca['name']} ({ca['coords']})")

# --- E. Procesar Iglesias y Templos adicionales ---
clean_churches = []
seen_churches = set()
for p in pois_raw:
    name = p['name']
    lat = p['lat']
    lon = p['lon']
    amenity = p.get('amenity', '')
    
    if (amenity == 'place_of_worship' or any(k in name.lower() for k in ['iglesia', 'capilla', 'parroquia', 'templo'])) and name not in seen_churches:
        coord_key = (round(lon, 4), round(lat, 4))
        if coord_key in existing_coords:
            continue
        if not (-32.835 <= lat <= -32.685 and -71.565 <= lon <= -71.38):
            continue
        seen_churches.add(name)
        clean_churches.append({
            "id": f"church_{p['id']}",
            "name": name,
            "category": "crowded_area",
            "type": "crowd",
            "role": f"Centro de Culto Religioso: {name} (Aglomeración en Días Festivos)",
            "icon": "⛪",
            "color": "#ec4899",
            "priority": 4,
            "coords": [lon, lat, 20]
        })

print(f"\nNuevas iglesias / capillas: {len(clean_churches)}")
for cc in clean_churches:
    print(f"  - {cc['name']} ({cc['coords']})")
