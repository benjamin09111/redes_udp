import urllib.request
import urllib.parse
import json

# Buscar zonas residenciales / urbanas de Quintero, Ventanas y Puchuncaví en OSM
query = """
[out:json][timeout:25];
(
  relation["boundary"="administrative"]["name"="Quintero"](-32.85,-71.58,-32.68,-71.35);
  relation["boundary"="administrative"]["name"="Puchuncaví"](-32.85,-71.58,-32.68,-71.35);
  way["landuse"="residential"](-32.82,-71.55,-32.77,-71.49); // Quintero
  way["landuse"="residential"](-32.76,-71.50,-32.73,-71.46); // Ventanas
  way["landuse"="residential"](-32.74,-71.43,-32.71,-71.40); // Puchuncaví
);
out geom;
"""

url = "https://overpass-api.de/api/interpreter"
data = urllib.parse.urlencode({'data': query}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'User-Agent': 'UAV-Research/1.0'})

try:
    with urllib.request.urlopen(req, timeout=25) as r:
        res = json.loads(r.read())
        elements = res.get('elements', [])
        print(f"Total elementos encontrados: {len(elements)}")
        with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\urban_geom.json', 'w', encoding='utf-8') as f:
            json.dump(elements, f)
except Exception as e:
    print(f"Error: {e}")
