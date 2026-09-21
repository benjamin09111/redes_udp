import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_named_places.json', 'r', encoding='utf-8') as f:
    places = json.load(f)

print(f"Total places in osm_all_named_places.json: {len(places)}")

keywords = ["alto", "tome", "estancilla", "rincon", "rincón", "rungue", "maitenes", "campiche", "greda", "chocota", "ventanas", "loncura", "quintero", "puchuncaví", "puchuncavi", "horcon", "horcón"]

matches = []
for p in places:
    name = (p.get('name') or '').lower()
    tags = p.get('all_tags', {})
    place_tag = tags.get('place', '')
    
    matched_kw = [kw for kw in ["alto", "tome", "estancilla", "rincon", "rincón", "rungue"] if kw in name]
    if matched_kw or place_tag:
        lat = p.get('lat')
        lon = p.get('lon')
        matches.append({
            'name': p.get('name'),
            'amenity': p.get('amenity'),
            'shop': p.get('shop'),
            'place': place_tag,
            'coords': [lon, lat],
            'tags': tags
        })

print(f"Total matching elements: {len(matches)}")
for m in matches:
    print(f"- {m['name']} | place={m['place']} | amenity={m['amenity']} | coords={m['coords']}")
