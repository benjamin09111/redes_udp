import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\urban_geom.json', 'r', encoding='utf-8') as f:
    elements = json.load(f)

print(f"Total elementos en urban_geom: {len(elements)}")

# Analizar la distribución de coordenadas
all_points = []
for el in elements:
    if el.get('type') == 'way':
        for pt in el.get('geometry', []):
            all_points.append((pt['lon'], pt['lat']))

print(f"Total puntos residenciales/urbanos en urban_geom: {len(all_points)}")

# Probar filtros espaciales para las zonas solicitadas por el usuario:
# 1. Loncura: lon [-71.515, -71.490], lat [-32.802, -32.778]
loncura_pts = [p for p in all_points if -71.515 <= p[0] <= -71.490 and -32.802 <= p[1] <= -32.778]
# 2. La Chocota: lon [-71.495, -71.475], lat [-32.738, -32.722]
chocota_pts = [p for p in all_points if -71.495 <= p[0] <= -71.475 and -32.738 <= p[1] <= -32.722]
# 3. La Greda: lon [-71.478, -71.455], lat [-32.755, -32.742]
greda_pts = [p for p in all_points if -71.478 <= p[0] <= -71.455 and -32.755 <= p[1] <= -32.742]
# 4. Las Salinas / Campiche: lon [-71.460, -71.435], lat [-32.748, -32.725]
salinas_pts = [p for p in all_points if -71.460 <= p[0] <= -71.435 and -32.748 <= p[1] <= -32.725]
# 5. Horcón: lon [-71.512, -71.482], lat [-32.718, -32.705]
horcon_pts = [p for p in all_points if -71.512 <= p[0] <= -71.482 and -32.718 <= p[1] <= -32.705]

print(f"Puntos Loncura: {len(loncura_pts)}")
print(f"Puntos La Chocota: {len(chocota_pts)}")
print(f"Puntos La Greda: {len(greda_pts)}")
print(f"Puntos Las Salinas / Campiche: {len(salinas_pts)}")
print(f"Puntos Horcón: {len(horcon_pts)}")
