import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_full_amenities_all.json', 'r', encoding='utf-8') as f:
    elements = json.load(f)

print(f"Total elementos en archivo: {len(elements)}")
for el in elements:
    tags = el.get('tags', {})
    name = tags.get('name', '')
    leisure = tags.get('leisure', '')
    amenity = tags.get('amenity', '')
    lat = el.get('lat') or el.get('center', {}).get('lat')
    lon = el.get('lon') or el.get('center', {}).get('lon')
    
    if leisure == 'playground' or 'infantil' in name.lower() or 'juego' in name.lower() or 'pista' in name.lower() or 'escuadron' in name.lower() or '4wd' in name.lower():
        print(f"MATCH: {name} | leisure={leisure} | amenity={amenity} -> [{lat}, {lon}] tags={tags}")
