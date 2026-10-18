"""Carga metadata/osm_antenas.geojson en meta_telecom_antenna (ubicación + cobertura)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "metadata/osm_antenas.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    source_id = registrar_fuente(cur, "osm_antenas", "metadata", "api", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO meta_telecom_antenna (source_id, osm_id, name, operator, structure,
                mobile_phone, height_m, coverage_radius_m, geom, coverage_geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (source_id, p["osm_id"], p["name"], p["operator"], p["structure"], p["mobile_phone"],
             p["height_m"], p["coverage_radius_m"], p["lon"], p["lat"],
             json.dumps(f["geometry"])),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("meta_telecom_antenna", cargar)
