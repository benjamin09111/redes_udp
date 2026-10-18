"""Carga metadata/srtm_relieve.geojson en meta_edge_terrain (una fila por arista)."""
from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "metadata/srtm_relieve.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    source_id = registrar_fuente(cur, "srtm_relieve", "metadata", "api", fc)
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO meta_edge_terrain (edge_id, source_id, samples, terrain_min_m,
                terrain_max_m, terrain_mean_m, relief_m, ascent_m, descent_m, profile_m)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (p["edge_id"], source_id, p["samples"], p["terrain_min_m"], p["terrain_max_m"],
             p["terrain_mean_m"], p["relief_m"], p["ascent_m"], p["descent_m"], p["profile_m"]),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("meta_edge_terrain", cargar)
