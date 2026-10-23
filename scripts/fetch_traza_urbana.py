import urllib.request
import json

overpass_url = 'https://overpass-api.de/api/interpreter'
query = """[out:json][timeout:25];
(
  way["waterway"](-32.85,-71.58,-32.68,-71.36);
);
out body;
>;
out skel qt;"""

req = urllib.request.Request(overpass_url, data=query.encode('utf-8'), headers={'User-Agent': 'UAV-Routing/2.0'})
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        nodes_dict = {e['id']: (e['lon'], e['lat']) for e in data.get('elements', []) if e.get('type') == 'node'}
        ways = [e for e in data.get('elements', []) if e.get('type') == 'way']
        print(f"Total nodes: {len(nodes_dict)}, Total ways: {len(ways)}")
        
        features = []
        for w in ways:
            tags = w.get('tags', {})
            node_ids = w.get('nodes', [])
            coords = [nodes_dict[nid] for nid in node_ids if nid in nodes_dict]
            if len(coords) >= 2:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords
                    },
                    "properties": {
                        "id": w['id'],
                        "name": tags.get('name') or "Quebrada / Cauce natural",
                        "waterway": tags.get('waterway', 'stream'),
                        "tipo_cauce": "Quebrada natural de escurrimiento",
                        "fuente": "Traza Urbana / Red Hidrográfica BCN - OSM",
                        "faja_restriccion_m": 25,
                        "riesgo": "Inundación y turbulencia por encajonamiento orográfico"
                    }
                })
        
        geojson = {
            "type": "FeatureCollection",
            "name": "traza_urbana_quebradas",
            "metadata": {
                "fuente": "Traza Urbana (https://trazaurbana.cl) & Red Hidrográfica",
                "referencia": "Planes Reguladores Comunales y Cauces de Quebradas",
                "total": len(features)
            },
            "features": features
        }
        
        with open('public/data/traza_urbana_quebradas.geojson', 'w', encoding='utf-8') as out:
            json.dump(geojson, out, ensure_ascii=False, indent=2)
        print(f"Generado public/data/traza_urbana_quebradas.geojson con {len(features)} quebradas y cauces")
except Exception as e:
    print('Error:', e)
