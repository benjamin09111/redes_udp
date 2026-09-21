import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_all_amenities_broad.json', 'r', encoding='utf-8') as f:
    amenities = json.load(f)

print(f"Total elements in osm_all_amenities_broad.json: {len(amenities)}")

# Group by category
categorized = {
    'schools': [],
    'health': [],
    'civic_crowd': [],
    'commerce': [],
    'plazas_leisure': [],
    'tourism_hospitality': [],
    'food_restaurant': [],
    'industry_craft': [],
    'other': []
}

for a in amenities:
    tags = a.get('tags', {})
    name = tags.get('name')
    amenity = tags.get('amenity', '')
    leisure = tags.get('leisure', '')
    tourism = tags.get('tourism', '')
    shop = tags.get('shop', '')
    healthcare = tags.get('healthcare', '')
    place = tags.get('place', '')
    
    lat = a.get('lat') or (a.get('center', {}).get('lat') if 'center' in a else None)
    lon = a.get('lon') or (a.get('center', {}).get('lon') if 'center' in a else None)
    
    if not lat or not lon:
        continue
        
    elem_info = {
        'id': a.get('id'),
        'name': name or f"{amenity or leisure or shop or place}_{a.get('id')}",
        'has_real_name': bool(name),
        'amenity': amenity,
        'leisure': leisure,
        'tourism': tourism,
        'shop': shop,
        'healthcare': healthcare,
        'place': place,
        'tags': tags,
        'lat': lat,
        'lon': lon
    }
    
    if amenity in ['school', 'kindergarten', 'college', 'university']:
        categorized['schools'].append(elem_info)
    elif amenity in ['hospital', 'clinic', 'doctors', 'pharmacy'] or healthcare:
        categorized['health'].append(elem_info)
    elif amenity in ['townhall', 'community_centre', 'place_of_worship', 'police', 'fire_station', 'post_office', 'bank']:
        categorized['civic_crowd'].append(elem_info)
    elif shop or amenity in ['marketplace', 'fuel']:
        categorized['commerce'].append(elem_info)
    elif leisure in ['park', 'pitch', 'sports_centre', 'playground', 'stadium', 'track'] or place == 'square':
        categorized['plazas_leisure'].append(elem_info)
    elif tourism in ['hotel', 'hostel', 'guest_house', 'motel', 'camp_site', 'viewpoint', 'attraction']:
        categorized['tourism_hospitality'].append(elem_info)
    elif amenity in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'ice_cream']:
        categorized['food_restaurant'].append(elem_info)
    else:
        categorized['other'].append(elem_info)

print("Categorization summary:")
for k, v in categorized.items():
    named_count = sum(1 for x in v if x['has_real_name'])
    print(f"- {k}: {len(v)} total ({named_count} with explicit name)")

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\categorized_broad_amenities.json', 'w', encoding='utf-8') as f:
    json.dump(categorized, f, indent=2, ensure_ascii=False)
