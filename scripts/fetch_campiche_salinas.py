import urllib.request
import urllib.parse
import json

q = """[out:json][timeout:25];
(
  way["highway"~"residential|unclassified"](-32.755, -71.475, -32.725, -71.440);
  way["landuse"="residential"](-32.755, -71.475, -32.725, -71.440);
);
out geom;"""

url = 'https://overpass-api.de/api/interpreter'
data = urllib.parse.urlencode({'data': q}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'User-Agent': 'UAV-Campiche-Salinas/1.0'})
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        res = json.loads(r.read())
        elems = res.get('elements', [])
        print(f"Elementos residenciales en Campiche/Salinas: {len(elems)}")
        with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\campiche_salinas_geom.json', 'w', encoding='utf-8') as f:
            json.dump(elems, f, indent=2)
except Exception as e:
    print('Error:', e)
