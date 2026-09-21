import json
import math

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_amenities_broad.json', 'r', encoding='utf-8') as f:
    all_amenities = json.load(f)

# Coordinates of the centers of the 5 localities:
localities = {
    "El Alto (Puchuncaví)": (-71.43063, -32.715738),
    "El Alto (Quintero)": (-71.498426, -32.782897),
    "Los Tomes": (-71.45000, -32.71670),
    "Comunidad La Estancilla": (-71.389997, -32.743157),
    "El Rincón": (-71.369826, -32.724445),
    "Rungue / El Rungue": (-71.406327, -32.696091)
}

def dist_m(lon1, lat1, lon2, lat2):
    # approximate haversine
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

results_by_loc = {loc: [] for loc in localities}

for item in all_amenities:
    lat = item.get('lat') or (item.get('center', {}).get('lat') if 'center' in item else None)
    lon = item.get('lon') or (item.get('center', {}).get('lon') if 'center' in item else None)
    if not lat or not lon:
        continue
    
    tags = item.get('tags', {})
    name = tags.get('name') or tags.get('amenity') or tags.get('leisure') or tags.get('shop') or tags.get('place')
    
    for loc_name, (clon, clat) in localities.items():
        d = dist_m(lon, lat, clon, clat)
        radius = 2200 # 2.2 km radius around locality center
        if d <= radius:
            results_by_loc[loc_name].append({
                'name': name,
                'dist_m': round(d, 1),
                'coords': [lon, lat],
                'tags': tags
            })

for loc_name, items in results_by_loc.items():
    print(f"\n============================\nLocalidad: {loc_name} (Total encontrados: {len(items)})")
    items.sort(key=lambda x: x['dist_m'])
    for it in items[:15]:
        print(f"- {it['name']} ({it['dist_m']}m) | tags={list(it['tags'].keys())} coords={it['coords']}")

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\amenities_by_new_localities.json', 'w', encoding='utf-8') as f:
    json.dump(results_by_loc, f, indent=2, ensure_ascii=False)
