"""Carga infraestructura/zonas_urbanas.geojson en la tabla urban_zone (polígonos)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "infraestructura/zonas_urbanas.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    registrar_fuente(cur, "zonas_urbanas", "infraestructura", "dataset", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO urban_zone (code, name, city, area_km2, geom)
            VALUES (%s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (p["code"], p["name"], p["city"], p["area_km2"], json.dumps(f["geometry"])),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("urban_zone", cargar)
