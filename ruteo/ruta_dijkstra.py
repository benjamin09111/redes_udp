"""Ruta base -> cada estación SINCA con pgr_dijkstra, usando la longitud de la arista como costo.

Es la ruta de "peor caso" de la fase 2: NO considera metadata ni amenazas (eso es la fase 3).
Lee la red desde la BD (infra_edge) y escribe el resultado para el sitio web:
    sitio_web/data/ruta_dijkstra.geojson
"""
import json
from datetime import datetime, timezone

from bd.conexion import RAIZ, conectar

ORIGEN = "base_scer"  # Aeródromo de Quintero (base de despacho y RTH)
SALIDA = RAIZ / "sitio_web" / "data" / "ruta_dijkstra.geojson"

SQL_DESTINOS = """
SELECT id, code, name FROM infra_node WHERE category = 'sinca' ORDER BY name
"""

SQL_RUTA = """
SELECT count(*) FILTER (WHERE d.edge <> -1)                AS tramos,
       COALESCE(SUM(e.length_m), 0)                        AS longitud_m,
       MAX(d.agg_cost)                                     AS costo,
       COUNT(DISTINCT d.node)                              AS nodos,
       ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq))    AS linea
FROM pgr_dijkstra(
       'SELECT id, source, target, cost, reverse_cost FROM infra_edge',
       (SELECT id FROM infra_node WHERE code = %s),
       %s,
       directed := true) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
JOIN infra_node n ON n.id = d.node
"""


def calcular(cur):
    cur.execute(SQL_DESTINOS)
    destinos = cur.fetchall()
    features = []
    for destino_id, code, nombre in destinos:
        cur.execute(SQL_RUTA, (ORIGEN, destino_id))
        tramos, longitud, costo, nodos, linea = cur.fetchone()
        features.append({
            "type": "Feature",
            "geometry": json.loads(linea),
            "properties": {
                "origen": ORIGEN,
                "destino": code,
                "destino_nombre": nombre,
                "tramos": tramos,
                "nodos": nodos,
                "longitud_m": round(longitud, 1),
                "costo": round(costo, 1),
            },
        })
    return features


def main():
    with conectar() as conn, conn.cursor() as cur:
        features = calcular(cur)

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "pgRouting pgr_dijkstra sobre infra_edge (costo = length_m)",
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"origen": ORIGEN, "costo": "length_m",
                           "considera_metadata_y_amenazas": False},
            "total": len(features),
        },
        "features": features,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)

    print(f"  rutas desde {ORIGEN} a {len(features)} estaciones SINCA -> {SALIDA.name}")
    for ft in sorted(features, key=lambda x: x["properties"]["longitud_m"]):
        p = ft["properties"]
        print(f"    {p['destino_nombre']:<28} {p['longitud_m'] / 1000:6.2f} km  {p['tramos']:>3} tramos")


if __name__ == "__main__":
    main()
