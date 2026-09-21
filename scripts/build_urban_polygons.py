import json
import math

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\urban_geom.json', 'r', encoding='utf-8') as f:
    elements = json.load(f)

# Agrupar puntos residenciales por zona
quintero_pts = []
ventanas_pts = []
puchuncavi_pts = []

for el in elements:
    if el.get('type') == 'way':
        geom = el.get('geometry', [])
        for pt in geom:
            lat = pt['lat']
            lon = pt['lon']
            # Quintero: lon < -71.49, lat < -32.76
            if lon < -71.49 and lat < -32.76:
                quintero_pts.append((lon, lat))
            # Ventanas: lon between -71.50 and -71.46, lat between -32.76 and -32.73
            elif -71.50 <= lon <= -71.46 and -32.76 <= lat <= -32.73:
                ventanas_pts.append((lon, lat))
            # Puchuncavi: lon > -71.43, lat between -32.74 and -32.71
            elif lon > -71.43 and -32.74 <= lat <= -32.71:
                puchuncavi_pts.append((lon, lat))

print(f"Puntos Quintero: {len(quintero_pts)}, Ventanas: {len(ventanas_pts)}, Puchuncaví: {len(puchuncavi_pts)}")

def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points
    
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
        
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
        
    return lower[:-1] + upper[:-1]

# Buffer un poco el casco para que se vea como una zona suave
def expand_polygon(poly, margin=0.003):
    # centroide
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    expanded = []
    for x, y in poly:
        dx = x - cx
        dy = y - cy
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            nx = x + (dx / dist) * margin
            ny = y + (dy / dist) * margin
            expanded.append([round(nx, 5), round(ny, 5)])
        else:
            expanded.append([round(x, 5), round(y, 5)])
    if expanded and expanded[0] != expanded[-1]:
        expanded.append(expanded[0])
    return expanded

h_quintero = expand_polygon(convex_hull(quintero_pts), margin=0.0025)
h_ventanas = expand_polygon(convex_hull(ventanas_pts), margin=0.002)
h_puchuncavi = expand_polygon(convex_hull(puchuncavi_pts), margin=0.002)

city_polygons = {
    "type": "FeatureCollection",
    "name": "Zonas_Urbanas_Contornos",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": "urban_quintero",
                "name": "Zona Urbana Quintero",
                "city": "Quintero",
                "color": "#38bdf8", # Cyan
                "fillColor": "#0284c7"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [h_quintero]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "urban_ventanas",
                "name": "Zona Urbana Las Ventanas",
                "city": "Ventanas",
                "color": "#a855f7", # Purple
                "fillColor": "#9333ea"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [h_ventanas]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "id": "urban_puchuncavi",
                "name": "Zona Urbana Puchuncaví",
                "city": "Puchuncaví",
                "color": "#10b981", # Emerald
                "fillColor": "#059669"
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [h_puchuncavi]
            }
        }
    ]
}

out_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\urban_zones.geojson'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(city_polygons, f, indent=2, ensure_ascii=False)

print(f"Polígonos guardados con éxito en {out_path}")
print("Vértices Quintero:", len(h_quintero))
print("Vértices Ventanas:", len(h_ventanas))
print("Vértices Puchuncaví:", len(h_puchuncavi))
