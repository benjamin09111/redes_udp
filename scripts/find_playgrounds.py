import urllib.request
import urllib.parse
import json

q = """[out:json][timeout:25];
(
  node["leisure"="playground"](-32.84,-71.56,-32.68,-71.36);
  way["leisure"="playground"](-32.84,-71.56,-32.68,-71.36);
);
out center tags;"""

url = 'https://lz4.overpass-api.de/api/interpreter'
data = urllib.parse.urlencode({'data': q}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'User-Agent': 'UAV-Playground/1.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read())
        elems = res.get('elements', [])
        print(f"Playgrounds en OSM: {len(elems)}")
        for el in elems:
            tags = el.get('tags', {})
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            print(f"  {tags.get('name', 'Parque Infantil / Juegos')} ({lat}, {lon})")
except Exception as e:
    print('Error:', e)
