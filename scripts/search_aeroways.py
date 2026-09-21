import urllib.request
import urllib.parse
import json

query_aeroway = """[out:json][timeout:25];
(
  node["aeroway"](-32.85,-71.56,-32.65,-71.30);
  way["aeroway"](-32.85,-71.56,-32.65,-71.30);
  relation["aeroway"](-32.85,-71.56,-32.65,-71.30);
  node["emergency"="landing_site"](-32.85,-71.56,-32.65,-71.30);
  way["emergency"="landing_site"](-32.85,-71.56,-32.65,-71.30);
);
out center tags;
"""

url = "https://lz4.overpass-api.de/api/interpreter"
req = urllib.request.Request(url, data=urllib.parse.urlencode({'data': query_aeroway}).encode('utf-8'), headers={'User-Agent': 'UAV-Aero-Audit/1.0'})
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        elems = data.get('elements', [])
        print(f"Total aeroway elements found: {len(elems)}")
        for el in elems:
            tags = el.get('tags', {})
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            print(f"- {tags.get('name') or tags.get('aeroway')} | type={tags.get('aeroway')} | coords=[{lon}, {lat}] | tags={tags}")
except Exception as e:
    print(f"Error querying aeroways: {e}")
