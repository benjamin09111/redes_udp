import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

restaurants = []
hotels = []
attractions = []
parks = []
churches = []

for d in data:
    name_l = d['name'].lower()
    amenity = d.get('amenity', '')
    tourism = d.get('tourism', '')
    leisure = d.get('leisure', '')
    
    # Restaurantes / Gastronomia
    if amenity in ['restaurant', 'cafe', 'fast_food', 'bar'] or 'restaurant' in name_l:
        restaurants.append(d)
        
    # Hoteles / Hostales / Cabañas
    if tourism in ['hotel', 'motel', 'hostel', 'guest_house', 'chalet', 'camp_site'] or any(k in name_l for k in ['hotel', 'hostal', 'cabaña', 'cabana', 'resort', 'lodge']):
        hotels.append(d)
        
    # Atracciones / Miradores / Visitas
    if tourism in ['viewpoint', 'attraction', 'artwork', 'museum'] or 'mirador' in name_l:
        attractions.append(d)
        
    # Parques / Plazas
    if leisure in ['park', 'square', 'garden'] or 'plaza' in name_l:
        parks.append(d)
        
    # Iglesias / Culto
    if amenity in ['place_of_worship'] or any(k in name_l for k in ['iglesia', 'capilla', 'parroquia', 'templo']):
        churches.append(d)

print(f"Total Restaurantes: {len(restaurants)}")
for r in restaurants[:10]:
    print(f"  - {r['name']} ({r['lat']}, {r['lon']})")

print(f"\nTotal Hoteles/Hostales/Cabañas: {len(hotels)}")
for h in hotels[:10]:
    print(f"  - {h['name']} ({h['lat']}, {h['lon']})")

print(f"\nTotal Atracciones/Miradores: {len(attractions)}")
for a in attractions[:10]:
    print(f"  - {a['name']} ({a['lat']}, {a['lon']})")

print(f"\nTotal Plazas/Parques: {len(parks)}")
for p in parks[:10]:
    print(f"  - {p['name']} ({p['lat']}, {p['lon']})")

print(f"\nTotal Iglesias/Culto: {len(churches)}")
for c in churches[:10]:
    print(f"  - {c['name']} ({c['lat']}, {c['lon']})")
