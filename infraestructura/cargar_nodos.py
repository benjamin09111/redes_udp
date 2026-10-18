"""Carga infraestructura/nodos.geojson en la tabla infra_node."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "infraestructura/nodos.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    registrar_fuente(cur, "nodos", "infraestructura", "dataset", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO infra_node (id, code, name, category, type, role, priority, city,
                                    elevation_msnm, pollutants, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (p["id"], p["code"], p["name"], p["category"], p["type"], p["role"], p["priority"],
             p["city"], p["elevation_msnm"], p["pollutants"], json.dumps(f["geometry"])),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("infra_node", cargar)
