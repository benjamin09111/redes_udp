import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_industries_raw.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

unnamed_by_type = {}
for it in items:
    tags = it.get('tags', {})
    if not tags.get('name') and not tags.get('operator'):
        mm = tags.get('man_made') or tags.get('power') or tags.get('landuse') or 'other'
        unnamed_by_type.setdefault(mm, []).append(it)

print("Summary of unnamed industrial structures:")
for k, v in unnamed_by_type.items():
    print(f"- {k}: {len(v)}")

# Chimneys:
chimneys = unnamed_by_type.get('chimney', [])
print(f"\nDetailed Chimneys ({len(chimneys)}):")
for ch in chimneys:
    lat = ch.get('lat') or (ch.get('center', {}).get('lat') if 'center' in ch else None)
    lon = ch.get('lon') or (ch.get('center', {}).get('lon') if 'center' in ch else None)
    tags = ch.get('tags', {})
    print(f"Chimney ID={ch['id']} at [{lon}, {lat}] tags={tags}")
