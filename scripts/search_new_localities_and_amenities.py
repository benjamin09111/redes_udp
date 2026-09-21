import urllib.request
import urllib.parse
import json
import time

# 1. First find Los Tomes specifically via Nominatim and Overpass
search_queries = [
    "Los Tomes, Puchuncaví",
    "Los Tomes, Valparaíso",
    "Los Tomes, Chile",
    "Tomes, Puchuncaví"
]

print("Searching for Los Tomes in Nominatim...")
found_tomes = []
for q in search_queries:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&addressdetails=1&limit=5"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Research-Puchuncavi/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for item in data:
                lat = float(item['lat'])
                lon = float(item['lon'])
                print(f"Match: {item.get('display_name')} -> [{lon}, {lat}]")
                found_tomes.append(item)
    except Exception as e:
        print(f"Error searching {q}: {e}")
    time.sleep(1.2)

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\search_tomes_result.json', 'w', encoding='utf-8') as f:
    json.dump(found_tomes, f, indent=2, ensure_ascii=False)

# 2. Overpass query for named nodes / ways matching Tomes or located in the interior
query_tomes_osm = """[out:json][timeout:25];
(
  node["name"~"Tome|Tomes",i](-32.85,-71.56,-32.65,-71.30);
  way["name"~"Tome|Tomes",i](-32.85,-71.56,-32.65,-71.30);
  relation["name"~"Tome|Tomes",i](-32.85,-71.56,-32.65,-71.30);
);
out center tags;
"""

overpass_url = "https://lz4.overpass-api.de/api/interpreter"
req = urllib.request.Request(overpass_url, data=urllib.parse.urlencode({'data': query_tomes_osm}).encode('utf-8'), headers={'User-Agent': 'UAV-Research-Puchuncavi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        osm_tomes = json.loads(resp.read().decode('utf-8'))
        print(f"Overpass matches for Tomes: {len(osm_tomes.get('elements', []))}")
        with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\osm_tomes.json', 'w', encoding='utf-8') as f:
            json.dump(osm_tomes.get('elements', []), f, indent=2, ensure_ascii=False)
except Exception as e:
    print(f"Error querying Overpass for Tomes: {e}")

print("Done searching for Tomes.")
