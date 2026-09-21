import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_historic_raw.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total raw historic elements from Overpass: {len(items)}")

for it in items:
    tags = it.get('tags', {})
    lat = it.get('lat') or (it.get('center', {}).get('lat') if 'center' in it else None)
    lon = it.get('lon') or (it.get('center', {}).get('lon') if 'center' in it else None)
    name = tags.get('name') or tags.get('historic') or tags.get('tourism') or tags.get('heritage')
    print(f"- {name} | type={it.get('type')} | tags={tags} | coords=[{lon}, {lat}]")
