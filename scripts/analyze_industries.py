import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_industries_raw.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total raw industrial items: {len(items)}")

categories = {}
named_industries = []
unnamed_industries = []

for it in items:
    tags = it.get('tags', {})
    name = tags.get('name')
    operator = tags.get('operator')
    man_made = tags.get('man_made')
    power = tags.get('power')
    industrial = tags.get('industrial')
    landuse = tags.get('landuse')
    
    lat = it.get('lat') or (it.get('center', {}).get('lat') if 'center' in it else None)
    lon = it.get('lon') or (it.get('center', {}).get('lon') if 'center' in it else None)
    
    item_info = {
        'id': it.get('id'),
        'type': it.get('type'),
        'name': name,
        'operator': operator,
        'man_made': man_made,
        'power': power,
        'industrial': industrial,
        'landuse': landuse,
        'tags': tags,
        'lat': lat,
        'lon': lon
    }
    
    if name or operator:
        named_industries.append(item_info)
    else:
        unnamed_industries.append(item_info)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\analyzed_industries.json', 'w', encoding='utf-8') as f:
    json.dump({'named': named_industries, 'unnamed_count': len(unnamed_industries), 'named_count': len(named_industries)}, f, indent=2, ensure_ascii=False)

print(f"Named/Operated industrial facilities: {len(named_industries)}")
print(f"Unnamed industrial structures (chimneys, tanks, etc.): {len(unnamed_industries)}")

# Sample print some of the named facilities
print("\n--- Top Named Industrial Facilities ---")
for fac in named_industries[:30]:
    title = fac['name'] or fac['operator']
    mm = fac['man_made'] or fac['industrial'] or fac['power'] or fac['landuse']
    print(f"- {title} | type={mm} | coords=[{fac['lon']}, {fac['lat']}]")
