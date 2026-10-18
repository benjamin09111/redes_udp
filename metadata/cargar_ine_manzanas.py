"""Carga metadata/ine_manzanas.geojson en meta_census_block (polígonos de manzanas)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "metadata/ine_manzanas.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    source_id = registrar_fuente(cur, "ine_manzanas", "metadata", "bd_geoespacial", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO meta_census_block (source_id, manzent, cut, commune, district, persons,
                dwellings, area_m2, density_hab_km2, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (source_id, p["manzent"], p["cut"], p["commune"], p["district"], p["persons"],
             p["dwellings"], p["area_m2"], p["density_hab_km2"], json.dumps(f["geometry"])),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("meta_census_block", cargar)
