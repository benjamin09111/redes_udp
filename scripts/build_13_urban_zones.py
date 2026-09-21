import json
import math

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\urban_geom.json', 'r', encoding='utf-8') as f:
    urban_elements = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\campiche_salinas_geom.json', 'r', encoding='utf-8') as f:
    campiche_elements = json.load(f)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_amenities_broad.json', 'r', encoding='utf-8') as f:
    amenities = json.load(f)

all_points = []
for el in urban_elements + campiche_elements:
    if el.get('type') == 'way':
        for pt in el.get('geometry', []):
            all_points.append((pt['lon'], pt['lat']))

for a in amenities:
    lat = a.get('lat') or (a.get('center', {}).get('lat') if 'center' in a else None)
    lon = a.get('lon') or (a.get('center', {}).get('lon') if 'center' in a else None)
    if lat and lon:
        all_points.append((lon, lat))

print(f"Total accumulated reference points: {len(all_points)}")

# Convex Hull algorithm
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

def create_circular_hull(center_lon, center_lat, radius_deg, num_pts=16):
    pts = []
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        # adjust for latitude distortion
        dx = radius_deg * math.cos(angle) / math.cos(math.radians(center_lat))
        dy = radius_deg * math.sin(angle)
        pts.append([round(center_lon + dx, 5), round(center_lat + dy, 5)])
    pts.append(pts[0])
    return pts

# Filter points for existing and new zones:
# 1. Quintero
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
pts_salinas_campiche = [p for p in all_points if -71.465 <= p[0] <= -71.438 and -32.748 <= p[1] <= -32.725]
# 7. Horcón
pts_horcon = [p for p in all_points if -71.512 <= p[0] <= -71.482 and -32.718 <= p[1] <= -32.705]
# 8. Puchuncaví Centro
pts_puchuncavi = [p for p in all_points if -71.425 <= p[0] <= -71.400 and -32.738 <= p[1] <= -32.718]

# 9. El Alto (Puchuncaví)
pts_el_alto = [p for p in all_points if -71.438 <= p[0] <= -71.418 and -32.722 <= p[1] <= -32.705]
# 10. Los Tomes
pts_los_tomes = [p for p in all_points if -71.462 <= p[0] <= -71.442 and -32.725 <= p[1] <= -32.708]
# 11. Comunidad La Estancilla
pts_estancilla = [p for p in all_points if -71.402 <= p[0] <= -71.378 and -32.755 <= p[1] <= -32.735]
# 12. El Rincón
pts_el_rincon = [p for p in all_points if -71.395 <= p[0] <= -71.360 and -32.732 <= p[1] <= -32.715]
# 13. El Rungue
pts_el_rungue = [p for p in all_points if -71.418 <= p[0] <= -71.395 and -32.708 <= p[1] <= -32.685]

zones_specs = [
    {
        "id": "urban_quintero",
        "name": "Zona Urbana Quintero",
        "city": "Quintero",
        "pts": pts_quintero,
        "default_center": (-71.53, -32.785),
        "radius": 0.015,
        "color": "#38bdf8", # Sky Blue
        "fillColor": "#0284c7",
        "margin": 0.0025
    },
    {
        "id": "urban_loncura",
        "name": "Localidad Urbana de Loncura",
        "city": "Loncura",
        "pts": pts_loncura,
        "default_center": (-71.503, -32.788),
        "radius": 0.010,
        "color": "#f59e0b", # Amber
        "fillColor": "#d97706",
        "margin": 0.002
    },
    {
        "id": "urban_ventanas",
        "name": "Zona Urbana Las Ventanas",
        "city": "Las Ventanas",
        "pts": pts_ventanas,
        "default_center": (-71.485, -32.746),
        "radius": 0.009,
        "color": "#a855f7", # Purple
        "fillColor": "#9333ea",
        "margin": 0.002
    },
    {
        "id": "urban_chocota",
        "name": "Localidad de La Chocota",
        "city": "La Chocota",
        "pts": pts_chocota,
        "default_center": (-71.487, -32.730),
        "radius": 0.008,
        "color": "#ec4899", # Pink
        "fillColor": "#db2777",
        "margin": 0.002
    },
    {
        "id": "urban_greda",
        "name": "Sector Urbano-Rural La Greda",
        "city": "La Greda",
        "pts": pts_greda,
        "default_center": (-71.472, -32.745),
        "radius": 0.008,
        "color": "#ef4444", # Red
        "fillColor": "#dc2626",
        "margin": 0.002
    },
    {
        "id": "urban_salinas_campiche",
        "name": "Sector Las Salinas y Campiche",
        "city": "Las Salinas / Campiche",
        "pts": pts_salinas_campiche,
        "default_center": (-71.450, -32.735),
        "radius": 0.010,
        "color": "#06b6d4", # Cyan / Teal
        "fillColor": "#0891b2",
        "margin": 0.002
    },
    {
        "id": "urban_horcon",
        "name": "Zona Urbana Caleta Horcón",
        "city": "Horcón",
        "pts": pts_horcon,
        "default_center": (-71.492, -32.712),
        "radius": 0.010,
        "color": "#8b5cf6", # Violet
        "fillColor": "#7c3aed",
        "margin": 0.002
    },
    {
        "id": "urban_puchuncavi",
        "name": "Zona Urbana Puchuncaví Centro",
        "city": "Puchuncaví Centro",
        "pts": pts_puchuncavi,
        "default_center": (-71.415, -32.726),
        "radius": 0.012,
        "color": "#10b981", # Emerald
        "fillColor": "#059669",
        "margin": 0.0025
    },
    # --- NUEVAS 5 CIUDADES / LOCALIDADES ---
    {
        "id": "urban_el_alto",
        "name": "Sector Rural El Alto (Puchuncaví)",
        "city": "El Alto",
        "pts": pts_el_alto,
        "default_center": (-71.43063, -32.71574),
        "radius": 0.007,
        "color": "#14b8a6", # Teal
        "fillColor": "#0d9488",
        "margin": 0.002
    },
    {
        "id": "urban_los_tomes",
        "name": "Localidad Rural Los Tomes",
        "city": "Los Tomes",
        "pts": pts_los_tomes,
        "default_center": (-71.45000, -32.71670),
        "radius": 0.007,
        "color": "#84cc16", # Lime
        "fillColor": "#65a30d",
        "margin": 0.002
    },
    {
        "id": "urban_estancilla",
        "name": "Comunidad La Estancilla",
        "city": "Comunidad La Estancilla",
        "pts": pts_estancilla,
        "default_center": (-71.389997, -32.743157),
        "radius": 0.0075,
        "color": "#f97316", # Orange
        "fillColor": "#ea580c",
        "margin": 0.002
    },
    {
        "id": "urban_el_rincon",
        "name": "Sector Rural El Rincón",
        "city": "El Rincón",
        "pts": pts_el_rincon,
        "default_center": (-71.369826, -32.724445),
        "radius": 0.008,
        "color": "#e11d48", # Rose
        "fillColor": "#be123c",
        "margin": 0.002
    },
    {
        "id": "urban_rungue",
        "name": "Localidad de El Rungue",
        "city": "El Rungue",
        "pts": pts_el_rungue,
        "default_center": (-71.406327, -32.696091),
        "radius": 0.008,
        "color": "#6366f1", # Indigo
        "fillColor": "#4f46e5",
        "margin": 0.002
    }
]

features = []
for z in zones_specs:
    pts = z["pts"]
    print(f"Zona {z['name']}: {len(pts)} puntos encontrados")
    if len(pts) >= 4:
        hull = convex_hull(pts)
        poly = expand_polygon(hull, margin=z["margin"])
    else:
        # Fallback circle hull
        clon, clat = z["default_center"]
        poly = create_circular_hull(clon, clat, z["radius"])
    
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

print(f"\n[OK] 13 Zonas Urbanas guardadas exitosamente en:\n  {out_urban}")
