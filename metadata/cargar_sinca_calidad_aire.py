"""Carga metadata/sinca_calidad_aire.geojson en meta_air_quality (una fila por medición)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "metadata/sinca_calidad_aire.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    source_id = registrar_fuente(cur, "sinca_calidad_aire", "metadata", "api", fc)
    filas = 0
    for f in fc["features"]:
        p = f["properties"]
        geo = json.dumps(f["geometry"])
        for m in p["measurements"]:
            cur.execute(
                """
                INSERT INTO meta_air_quality (source_id, station_key, station_name, commune,
                    network, operator, node_id, pollutant, value, unit, averaging, status,
                    status_code, icap, observed_at, geom)
                VALUES (%s, %s, %s, %s, %s, %s,
                    (SELECT id FROM infra_node WHERE code = %s),
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                """,
                (source_id, p["station_key"], p["station_name"], p["commune"], p["network"],
                 p["operator"], p["node_code"], m["pollutant"], m["value"], m["unit"],
                 m["averaging"], m["status"], m["status_code"], m["icap"], m["observed_at"], geo),
            )
            filas += 1
    return filas


if __name__ == "__main__":
    ejecutar("meta_air_quality", cargar)
