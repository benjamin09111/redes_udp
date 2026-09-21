import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    fc = json.load(f)

print(f"Total current nodes in nodes.geojson: {len(fc['features'])}")
categories = {}
cities = {}
for feat in fc['features']:
    props = feat['properties']
    cat = props.get('category', 'unknown')
    city = props.get('city', 'unknown')
    categories[cat] = categories.get(cat, 0) + 1
    cities[city] = cities.get(city, 0) + 1

print("\nCurrent category counts:")
for k, v in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"- {k}: {v}")

print("\nCurrent city counts:")
for k, v in sorted(cities.items(), key=lambda x: -x[1]):
    print(f"- {k}: {v}")
