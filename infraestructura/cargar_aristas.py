"""Carga infraestructura/aristas.geojson en la tabla infra_edge (requiere nodos cargados)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "infraestructura/aristas.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    registrar_fuente(cur, "aristas", "infraestructura", "dataset", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO infra_edge (id, source, target, length_m, cost, reverse_cost, geom)
            VALUES (%s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (p["id"], p["source"], p["target"], p["length_m"], p["cost"], p["reverse_cost"],
             json.dumps(f["geometry"])),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("infra_edge", cargar)
