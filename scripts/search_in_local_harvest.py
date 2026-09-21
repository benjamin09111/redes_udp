import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

print(f"Total places in osm_all_named_places.json: {len(places)}")

keywords = ["alto", "tome", "estancilla", "rincon", "rincón", "rungue", "maitenes", "puchuncavi", "quintero"]

matches = []
for p in places:
    tags = p.get('tags', {})
    name = tags.get('name', '').lower()
    place_type = tags.get('place', '')
    amenity = tags.get('amenity', '')
    
    matched_kw = [kw for kw in keywords if kw in name]
    if matched_kw or place_type:
        lat = p.get('lat') or p.get('center', {}).get('lat')
        lon = p.get('lon') or p.get('center', {}).get('lon')
        matches.append({
            'name': tags.get('name'),
            'tags': tags,
            'coords': [lon, lat],
            'matched': matched_kw
        })

print(f"Found {len(matches)} matching places/amenities in existing harvest:")
for m in matches[:40]:
    print(f"- {m['name']} | tags={m['tags'].get('place') or m['tags'].get('amenity')} | coords={m['coords']}")
