import json
import math

# =============================================================================
# 1. CARGAR PUNTOS RESIDENCIALES DE LAS DISTINTAS FUENTES
# =============================================================================
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\urban_geom.json', 'r', encoding='utf-8') as f:
    urban_elements = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\campiche_salinas_geom.json', 'r', encoding='utf-8') as f:
    campiche_elements = json.load(f)

all_points = []
for el in urban_elements + campiche_elements:
    if el.get('type') == 'way':
        for pt in el.get('geometry', []):
            all_points.append((pt['lon'], pt['lat']))

print(f"Total puntos acumulados: {len(all_points)}")

# Algoritmo Convex Hull (Monotone Chain)
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

def expand_polygon(poly, margin=0.002):
    if len(poly) < 3:
        return poly
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

# =============================================================================
# 2. DEFINIR ZONAS URBANAS SOLICITADAS POR EL USUARIO
# =============================================================================
# 1. Quintero Centro/Península
pts_quintero = [p for p in all_points if p[0] < -71.515 and p[1] < -32.765]
# 2. Loncura
pts_loncura = [p for p in all_points if -71.515 <= p[0] <= -71.490 and -32.802 <= p[1] <= -32.778]
# 3. Las Ventanas
pts_ventanas = [p for p in all_points if -71.495 <= p[0] <= -71.478 and -32.756 <= p[1] <= -32.738]
# 4. La Chocota
pts_chocota = [p for p in all_points if -71.495 <= p[0] <= -71.475 and -32.738 < p[1] <= -32.720]
# 5. La Greda
pts_greda = [p for p in all_points if -71.478 < p[0] <= -71.458 and -32.755 <= p[1] <= -32.738]
# 6. Las Salinas / Campiche
pts_salinas_campiche = [p for p in all_points if -71.465 <= p[0] <= -71.435 and -32.748 <= p[1] <= -32.725]
# 7. Horcón
pts_horcon = [p for p in all_points if -71.512 <= p[0] <= -71.482 and -32.718 <= p[1] <= -32.705]
# 8. Puchuncaví Centro
pts_puchuncavi = [p for p in all_points if p[0] > -71.430 and -32.740 <= p[1] <= -32.710]

zones_config = [
    {
        "id": "urban_quintero",
        "name": "Zona Urbana Quintero",
        "city": "Quintero",
        "pts": pts_quintero,
        "color": "#38bdf8", # Sky Blue / Cyan
        "fillColor": "#0284c7",
        "margin": 0.0025
    },
    {
        "id": "urban_loncura",
        "name": "Localidad Urbana de Loncura",
        "city": "Loncura",
        "pts": pts_loncura,
        "color": "#f59e0b", # Amber / Gold
        "fillColor": "#d97706",
        "margin": 0.002
    },
    {
        "id": "urban_ventanas",
        "name": "Zona Urbana Las Ventanas",
        "city": "Las Ventanas",
        "pts": pts_ventanas,
        "color": "#a855f7", # Purple
        "fillColor": "#9333ea",
        "margin": 0.002
    },
    {
        "id": "urban_chocota",
        "name": "Localidad de La Chocota",
        "city": "La Chocota",
        "pts": pts_chocota,
        "color": "#ec4899", # Pink
        "fillColor": "#db2777",
        "margin": 0.002
    },
    {
        "id": "urban_greda",
        "name": "Sector Urbano-Rural La Greda",
        "city": "La Greda",
        "pts": pts_greda,
        "color": "#ef4444", # Red
        "fillColor": "#dc2626",
        "margin": 0.002
    },
    {
        "id": "urban_salinas_campiche",
        "name": "Sector Las Salinas y Campiche",
        "city": "Las Salinas / Campiche",
        "pts": pts_salinas_campiche,
        "color": "#06b6d4", # Cyan / Teal
        "fillColor": "#0891b2",
        "margin": 0.002
    },
    {
        "id": "urban_horcon",
        "name": "Zona Urbana Caleta Horcón",
        "city": "Horcón",
        "pts": pts_horcon,
        "color": "#8b5cf6", # Violet
        "fillColor": "#7c3aed",
        "margin": 0.002
    },
    {
        "id": "urban_puchuncavi",
        "name": "Zona Urbana Puchuncaví Centro",
        "city": "Puchuncaví",
        "pts": pts_puchuncavi,
        "color": "#10b981", # Emerald
        "fillColor": "#059669",
        "margin": 0.0025
    }
]

features = []
for z in zones_config:
    pts = z["pts"]
    print(f"Zona {z['name']}: {len(pts)} puntos")
    if len(pts) < 3:
        print(f"  Advertencia: insuficientes puntos para {z['name']}")
        continue
    hull = convex_hull(pts)
    poly = expand_polygon(hull, margin=z["margin"])
    
    features.append({
        "type": "Feature",
        "properties": {
            "id": z["id"],
            "name": z["name"],
            "city": z["city"],
            "color": z["color"],
            "fillColor": z["fillColor"]
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [poly]
        }
    })

urban_geojson = {
    "type": "FeatureCollection",
    "name": "Zonas_Urbanas_Bahia_Quintero_Multicolor",
    "features": features
}

out_urban = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\urban_zones.geojson'
with open(out_urban, 'w', encoding='utf-8') as f:
    json.dump(urban_geojson, f, indent=2, ensure_ascii=False)

print(f"\nPolígonos urbanos multicolor guardados con éxito en:\n  {out_urban}")

# =============================================================================
# 3. AGREGAR LOS NUEVOS NODOS SOLICITADOS A NODOS.GEOJSON
# =============================================================================
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    nodes_geojson = json.load(f)

existing_ids = {feat['properties']['id'] for feat in nodes_geojson['features']}

nodes_to_append = [
    {
        "id": "infra_ruta_f210_quintero",
        "name": "Eje Vial Ruta F-210 (Acceso Quintero - Loncura)",
        "category": "crowded_area",
        "type": "transport",
        "role": "Nodo de Tránsito y Acceso Vial Principal F-210 (Quintero / Loncura)",
        "icon": "🛣",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.508960, -32.799020, 18]
    },
    {
        "id": "attr_pista_4wd_quintero",
        "name": "Pista Escuadrón 4WD Quintero (Off-Road Ritoque)",
        "category": "attraction",
        "type": "attraction",
        "role": "Recinto Deportivo Motor Off-Road 4x4 / Dunas de Ritoque",
        "icon": "🚙",
        "color": "#d946ef",
        "priority": 3,
        "coords": [-71.528300, -32.825000, 15]
    },
    {
        "id": "crowd_parque_infantil_quintero",
        "name": "Parque Infantil de Juegos (Quintero Centro)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Zona de Juegos Infantiles y Concurrencia Familiar",
        "icon": "🎠",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.528533, -32.784815, 23]
    },
    {
        "id": "crowd_plaza_la_greda",
        "name": "Plaza y Centro Comunitario La Greda",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Espacio Público Central y Concurrencia Sector La Greda",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.475610, -32.744520, 32]
    },
    {
        "id": "crowd_plaza_las_salinas",
        "name": "Punto Comunitario Las Salinas (Puchuncaví)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Punto de Reunión y Conectividad Sector Las Salinas",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.472770, -32.745180, 25]
    }
]

added_nodes = 0
for n in nodes_to_append:
    if n["id"] not in existing_ids:
        nodes_geojson["features"].append({
            "type": "Feature",
            "properties": {
                "id": n["id"],
                "name": n["name"],
                "category": n["category"],
                "type": n["type"],
                "role": n["role"],
                "icon": n["icon"],
                "color": n["color"],
                "priority": n["priority"],
                "elevation_msnm": n["coords"][2],
                "pollutants": []
            },
            "geometry": {
                "type": "Point",
                "coordinates": n["coords"]
            }
        })
        existing_ids.add(n["id"])
        added_nodes += 1
        print(f"Nodo agregado: {n['name']}")

out_nodes = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(out_nodes, 'w', encoding='utf-8') as f:
    json.dump(nodes_geojson, f, indent=2, ensure_ascii=False)

print(f"\nNodos guardados exitosamente. Agregados: {added_nodes}. Total: {len(nodes_geojson['features'])}")
