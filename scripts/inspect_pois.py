import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== SUPERMARKETS / COMMERCIAL ===')
for d in data:
    if d['shop'] in ['supermarket', 'mall', 'department_store'] or d['amenity'] == 'marketplace':
        tag = d['shop'] or d['amenity']
        print(f"[{tag}] {d['name']} ({d['lat']}, {d['lon']})")

print('\n=== CROWD / CIVIC / LEISURE ===')
for d in data:
    if d['amenity'] in ['police', 'community_centre', 'place_of_worship', 'bank', 'townhall', 'courthouse', 'bus_station'] or d['leisure'] in ['stadium', 'sports_centre', 'park'] or d['tourism'] in ['attraction', 'museum']:
        tag = d['amenity'] or d['leisure'] or d['tourism']
        print(f"[{tag}] {d['name']} ({d['lat']}, {d['lon']})")

print('\n=== HEALTH / CLINICS / PHARMACIES ===')
for d in data:
    if d['amenity'] in ['hospital', 'clinic', 'doctors', 'pharmacy']:
        print(f"[{d['amenity']}] {d['name']} ({d['lat']}, {d['lon']})")

print('\n=== EDUCATION ===')
for d in data:
    if d['amenity'] in ['school', 'kindergarten', 'college', 'university']:
        print(f"[{d['amenity']}] {d['name']} ({d['lat']}, {d['lon']})")
