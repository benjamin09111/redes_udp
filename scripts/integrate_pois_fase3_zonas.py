"""Integra POIs nuevos al dataset maestro para rellenar tres zonas con baja densidad de nodos:

  1. Zona Urbana Caleta Horcon        (urban_horcon)
  2. Localidad de La Chocota          (urban_chocota)
  3. Corredor Campiche - Puchuncavi   (urban_salinas_campiche <-> urban_puchuncavi)

Fuente: OpenStreetMap via Overpass (cosecha en scripts/pois_fase3_zonas.json).
Todos los nodos usan EXCLUSIVAMENTE las categorias ya definidas en src/config/categories.js.

Solo escribe en public/data/nodes.geojson. No toca aristas, BD ni configuracion.
Es idempotente: re-ejecutarlo no duplica nada (dedup por id y por cercania < 60 m).

Uso:
    python3 scripts/integrate_pois_fase3_zonas.py            # integra
    python3 scripts/integrate_pois_fase3_zonas.py --dry-run  # solo reporta
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "public" / "data" / "nodes.geojson"
POIS = Path(__file__).resolve().parent / "pois_fase3_zonas.json"

R_EARTH = 6371000.0
UMBRAL_DUPLICADO_M = 60.0


def haversine_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(a))


def main():
    dry = "--dry-run" in sys.argv

    with open(MASTER, encoding="utf-8") as f:
        data = json.load(f)
    with open(POIS, encoding="utf-8") as f:
        pois = json.load(f)

    ids_exist = {feat["properties"]["id"] for feat in data["features"]}
    coords_exist = [(feat["geometry"]["coordinates"][0], feat["geometry"]["coordinates"][1])
                    for feat in data["features"]]

    print(f"Nodos iniciales: {len(data['features'])}")
    print(f"POIs candidatos: {len(pois)}\n")

    agregados, omitidos = [], []
    for poi in pois:
        if poi["id"] in ids_exist:
            omitidos.append((poi["name"], "id ya existe"))
            continue
        cerca = [d for d in (haversine_m(poi["lon"], poi["lat"], x, y) for x, y in coords_exist)
                 if d < UMBRAL_DUPLICADO_M]
        if cerca:
            omitidos.append((poi["name"], f"nodo existente a {min(cerca):.0f} m"))
            continue

        feat = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [poi["lon"], poi["lat"]]},
            "properties": {
                "id": poi["id"],
                "name": poi["name"],
                "category": poi["category"],
                "type": poi["type"],
                "role": poi["role"],
                "icon": poi["icon"],
                "color": poi["color"],
                "priority": poi["priority"],
                "elevation_msnm": poi["elevation_msnm"],
                "pollutants": poi["pollutants"],
                "city": poi["city"],
            },
        }
        data["features"].append(feat)
        ids_exist.add(poi["id"])
        coords_exist.append((poi["lon"], poi["lat"]))
        agregados.append(poi)

    por_zona = {}
    for p in agregados:
        por_zona.setdefault(p.get("zona", "?"), []).append(p)
    for z in sorted(por_zona):
        print(f"--- {z}: {len(por_zona[z])} nodos ---")
        for p in sorted(por_zona[z], key=lambda x: x["category"]):
            print(f"    {p['icon']} {p['category']:14s} {p['name'][:44]:46s} {p['lon']:.5f},{p['lat']:.5f}")
        print()

    if omitidos:
        print(f"Omitidos ({len(omitidos)}):")
        for n, r in omitidos[:15]:
            print(f"    {n[:48]:50s} {r}")
        if len(omitidos) > 15:
            print(f"    ... y {len(omitidos) - 15} mas")
        print()

    print(f"Agregados: {len(agregados)}   Total final: {len(data['features'])}")

    if dry:
        print("\n[--dry-run] no se escribio nada.")
        return

    with open(MASTER, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nGuardado en {MASTER.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
