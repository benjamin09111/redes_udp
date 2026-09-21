import json
import math

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    fc = json.load(f)

nodes = fc['features']
print(f"Total current nodes: {len(nodes)}")

# Check for any historical keywords or close coordinates
keywords = ["ureta", "melinka", "cochrane", "downey", "museo", "petras", "conchal", "piedra", "patrimonio", "histórico", "historico"]

found = []
for n in nodes:
    name = n['properties'].get('name', '').lower()
    role = n['properties'].get('role', '').lower()
    coords = n['geometry']['coordinates']
    for kw in keywords:
        if kw in name or kw in role:
            found.append({
                'id': n['properties']['id'],
                'name': n['properties']['name'],
                'category': n['properties']['category'],
                'coords': coords
            })
            break

print(f"Nodes matching historical keywords: {len(found)}")
for f in found:
    print(f"- {f['id']} | {f['name']} ({f['category']}) | coords={f['coords']}")
