"""
Infraestructura: extracción y transformación de la red (nodos, aristas y zonas urbanas).

Fuente: dataset maestro del proyecto (public/data/), construido en la fase 1 a partir de
Overpass/OSM, SINCA, BCN y Open-Elevation (ver scripts/) y curado manualmente.
  1. Nodos: nodes.geojson -> se normalizan y reciben un id entero (requerido por pgRouting).
  2. Aristas: cada nodo se une a sus K vecinos más cercanos; si quedan componentes
     desconectados se unen por su par de nodos más cercano (grafo conexo).
     Costo de cada arista = longitud en metros (haversine).
  3. Zonas urbanas (polígonos): urban_zones.geojson -> MultiPolygon + área en km².

Salida (infraestructura/): nodos.geojson, aristas.geojson, zonas_urbanas.geojson
Estructura de cada archivo: ver el .md del mismo nombre.
Uso: python infraestructura/extraer_infraestructura.py [K]
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(__file__).resolve().parent
NODES_SRC = ROOT / "public" / "data" / "nodes.geojson"
ZONES_SRC = ROOT / "public" / "data" / "urban_zones.geojson"
K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
R_EARTH = 6371000.0


def haversine_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(a))


def ring_area_m2(ring):
    """Área firmada de un anillo [[lon, lat], ...] en m² (> 0 antihorario). Proyección equirectangular local."""
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    xy = [(math.radians(lon) * R_EARTH * math.cos(lat0), math.radians(lat) * R_EARTH) for lon, lat, *_ in ring]
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1])) / 2


def orientar(poly):
    """RFC 7946: anillo exterior antihorario y huecos horarios."""
    exterior, *huecos = poly
    if ring_area_m2(exterior) < 0:
        exterior = exterior[::-1]
    huecos = [h[::-1] if ring_area_m2(h) > 0 else h for h in huecos]
    return [exterior, *huecos]


def feature_collection(features, source, params=None):
    return {
        "type": "FeatureCollection",
        "etl": {
            "fuente": source,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": params or {},
            "total": len(features),
        },
        "features": features,
    }


def write(name, fc):
    path = OUT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    print(f"  {name}: {fc['etl']['total']} features")


def parse_pollutants(value):
    """En el dataset maestro viene como lista, como texto separado por comas o null -> siempre lista."""
    if not value:
        return []
    if isinstance(value, str):
        return [] if value.startswith("Ninguno") else [s.strip() for s in value.split(",") if s.strip()]
    return value


def build_nodes():
    with open(NODES_SRC, encoding="utf-8") as f:
        feats = json.load(f)["features"]
    nodes = []
    for i, feat in enumerate(feats, start=1):
        p = feat["properties"]
        lon, lat, *rest = feat["geometry"]["coordinates"]
        nodes.append({
            "id": i,
            "code": p["id"],
            "name": p["name"],
            "category": p["category"],
            "type": p.get("type"),
            "role": p.get("role"),
            "priority": p.get("priority"),
            "city": p.get("city"),
            "elevation_msnm": p.get("elevation_msnm", rest[0] if rest else None),
            "pollutants": parse_pollutants(p.get("pollutants")),
            "lon": round(lon, 6),
            "lat": round(lat, 6),
        })
    return nodes


def build_edges(nodes):
    n = len(nodes)

    def dist(a, b):
        return haversine_m(nodes[a]["lon"], nodes[a]["lat"], nodes[b]["lon"], nodes[b]["lat"])

    pairs = set()
    for a in range(n):
        near = sorted((b for b in range(n) if b != a), key=lambda b: dist(a, b))[:K]
        pairs.update((min(a, b), max(a, b)) for b in near)

    # Conectividad: unir componentes por el par de nodos más cercano (union-find)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
    bridges = 0
    while len({find(x) for x in range(n)}) > 1:
        _, a, b = min((dist(a, b), a, b) for a in range(n) for b in range(a + 1, n) if find(a) != find(b))
        pairs.add((a, b))
        parent[find(a)] = find(b)
        bridges += 1

    edges = []
    for eid, (a, b) in enumerate(sorted(pairs), start=1):
        na, nb = nodes[a], nodes[b]
        length = round(dist(a, b), 2)
        edges.append({
            "id": eid,
            "source": na["id"],
            "target": nb["id"],
            "source_code": na["code"],
            "target_code": nb["code"],
            "length_m": length,
            "cost": length,
            "reverse_cost": length,
            "coords": [[na["lon"], na["lat"]], [nb["lon"], nb["lat"]]],
        })
    return edges, bridges


def build_zones():
    with open(ZONES_SRC, encoding="utf-8") as f:
        feats = json.load(f)["features"]
    zones = []
    for feat in feats:
        p, g = feat["properties"], feat["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        polys = [[[[round(lon, 6), round(lat, 6)] for lon, lat, *_ in ring] for ring in poly] for poly in polys]
        polys = [orientar(poly) for poly in polys]
        area = sum(abs(ring_area_m2(poly[0])) - sum(abs(ring_area_m2(h)) for h in poly[1:]) for poly in polys)
        zones.append({
            "type": "Feature",
            "geometry": {"type": "MultiPolygon", "coordinates": polys},
            "properties": {
                "code": p["id"],
                "name": p["name"],
                "city": p.get("city"),
                "area_km2": round(area / 1e6, 4),
            },
        })
    return zones


def main():
    nodes = build_nodes()
    edges, bridges = build_edges(nodes)
    zones = build_zones()
    src = "public/data (dataset maestro fase 1: OSM/Overpass, SINCA, BCN, Open-Elevation)"

    node_feats = [{
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [n["lon"], n["lat"]]},
        "properties": {k: v for k, v in n.items() if k not in ("lon", "lat")},
    } for n in nodes]
    edge_feats = [{
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": e["coords"]},
        "properties": {k: v for k, v in e.items() if k != "coords"},
    } for e in edges]

    write("nodos.geojson", feature_collection(node_feats, src))
    write("aristas.geojson", feature_collection(edge_feats, src, {"k_vecinos": K, "aristas_puente": bridges}))
    write("zonas_urbanas.geojson", feature_collection(zones, src))
    lens = [e["length_m"] for e in edges]
    print(f"{len(nodes)} nodos, {len(edges)} aristas (K={K}, {bridges} puentes de conectividad)")
    print(f"largo aristas: min {min(lens):.0f} m, prom {sum(lens) / len(lens):.0f} m, max {max(lens):.0f} m")


if __name__ == "__main__":
    main()
