"""Ruta base -> cada estación SINCA con pgr_dijkstra (k >= 2), usando la longitud como costo.

Es la ruta de referencia (peor caso) de la fase 2: NO considera metadata ni amenazas.
Genera k=1 y k=2 mediante pgr_dijkstra en la base de datos PostgreSQL (pgRouting),
penalizando las aristas de k=1 para encontrar la alternativa más corta disimilar.

Lee la red desde la BD (infra_edge) y escribe el resultado para el sitio web:
    sitio_web/data/ruta_dijkstra.geojson
"""
import json
from datetime import datetime, timezone

from bd.conexion import RAIZ, conectar

# Cargar parámetros unificados
CONFIG_PATH = RAIZ / "config" / "parametros.json"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _cfg = json.load(f)
    ORIGEN = _cfg.get("algoritmo", {}).get("origen_default", "base_scer")
    FACTOR_P = float(_cfg.get("algoritmo", {}).get("factor_penalizacion_p", 4.0))
else:
    ORIGEN = "base_scer"
    FACTOR_P = 4.0

SALIDA = RAIZ / "sitio_web" / "data" / "ruta_dijkstra.geojson"

SQL_DESTINOS = """
SELECT id, code, name FROM infra_node WHERE category = 'sinca' ORDER BY name
"""

SQL_RUTA_K1 = """
SELECT count(*) FILTER (WHERE d.edge <> -1)                AS tramos,
       COALESCE(SUM(e.length_m), 0)                        AS longitud_m,
       MAX(d.agg_cost)                                     AS costo,
       COUNT(DISTINCT d.node)                              AS nodos,
       ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq))    AS linea
FROM pgr_dijkstra(
       'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
       (SELECT id FROM infra_node WHERE code = %s),
       %s,
       directed := false) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
JOIN infra_node n ON n.id = d.node
"""

SQL_ARISTAS_K1 = """
SELECT d.edge
FROM pgr_dijkstra(
       'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
       (SELECT id FROM infra_node WHERE code = %s),
       %s,
       directed := false) AS d
WHERE d.edge <> -1
ORDER BY d.seq
"""


def calcular_k2(cur, destino_id, aristas_k1, factor_p=4.0):
    if not aristas_k1:
        return 0, 0.0, 0.0, 0, None, []

    ids_str = ",".join(str(int(x)) for x in aristas_k1)
    sql_grafo_k2 = (
        "SELECT id, source, target, "
        f"CASE WHEN id IN ({ids_str}) THEN length_m * {factor_p} ELSE length_m END AS cost, "
        f"CASE WHEN id IN ({ids_str}) THEN length_m * {factor_p} ELSE length_m END AS reverse_cost "
        "FROM infra_edge"
    )
    sql_k2 = f"""
    SELECT count(*) FILTER (WHERE d.edge <> -1)                AS tramos,
           COALESCE(SUM(e.length_m), 0)                        AS longitud_m,
           MAX(d.agg_cost)                                     AS costo,
           COUNT(DISTINCT d.node)                              AS nodos,
           ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq))    AS linea
    FROM pgr_dijkstra(
           '{sql_grafo_k2}',
           (SELECT id FROM infra_node WHERE code = %s),
           %s,
           directed := false) AS d
    LEFT JOIN infra_edge e ON e.id = d.edge
    JOIN infra_node n ON n.id = d.node
    """
    cur.execute(sql_k2, (ORIGEN, destino_id))
    tramos, long_m, costo, nodos, linea = cur.fetchone()

    # Obtener aristas de k=2
    sql_aristas_k2 = f"""
    SELECT d.edge
    FROM pgr_dijkstra(
           '{sql_grafo_k2}',
           (SELECT id FROM infra_node WHERE code = %s),
           %s,
           directed := false) AS d
    WHERE d.edge <> -1
    ORDER BY d.seq
    """
    cur.execute(sql_aristas_k2, (ORIGEN, destino_id))
    aristas_k2 = [r[0] for r in cur.fetchall()]
    return tramos, long_m, costo, nodos, linea, aristas_k2


def calcular(cur):
    cur.execute(SQL_DESTINOS)
    destinos = cur.fetchall()
    features = []
    for destino_id, code, nombre in destinos:
        # 1. Ruta k=1 con pgr_dijkstra
        cur.execute(SQL_RUTA_K1, (ORIGEN, destino_id))
        tramos_k1, longitud_k1, costo_k1, nodos_k1, linea_k1 = cur.fetchone()

        # 2. Aristas de k=1 para penalización
        cur.execute(SQL_ARISTAS_K1, (ORIGEN, destino_id))
        aristas_k1 = [row[0] for row in cur.fetchall()]

        # 3. Ruta k=2 con pgr_dijkstra penalizando aristas de k=1 (factor_p)
        tramos_k2, longitud_k2, costo_k2, nodos_k2, linea_k2, aristas_k2 = calcular_k2(cur, destino_id, aristas_k1, FACTOR_P)

        # Feature k=1
        features.append({
            "type": "Feature",
            "geometry": json.loads(linea_k1),
            "properties": {
                "origen": ORIGEN,
                "destino": code,
                "destino_nombre": nombre,
                "tramos": tramos_k1,
                "nodos": nodos_k1,
                "longitud_m": round(longitud_k1, 1),
                "costo": round(costo_k1, 1),
                "k": 1,
                "aristas": aristas_k1,
            },
        })

        # Feature k=2 (si existe ruta alternativa)
        if linea_k2 and longitud_k2:
            features.append({
                "type": "Feature",
                "geometry": json.loads(linea_k2),
                "properties": {
                    "origen": ORIGEN,
                    "destino": code,
                    "destino_nombre": f"{nombre} (k=2)",
                    "tramos": tramos_k2,
                    "nodos": nodos_k2,
                    "longitud_m": round(longitud_k2, 1),
                    "costo": round(costo_k2, 1),
                    "k": 2,
                    "aristas": aristas_k2,
                },
            })
    return features


def main():
    with conectar() as conn, conn.cursor() as cur:
        features = calcular(cur)

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "pgRouting pgr_dijkstra sobre infra_edge (k=1 y k=2 con costo = length_m)",
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {
                "origen": ORIGEN,
                "costo": "length_m",
                "k_rutas": 2,
                "factor_penalizacion_k2": FACTOR_P,
                "considera_metadata_y_amenazas": False,
            },
            "total": len(features),
        },
        "features": features,
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)

    print(f"  rutas k=1 y k=2 desde {ORIGEN} a {len(features)//2} estaciones SINCA ({len(features)} features) -> {SALIDA.name}")
    for ft in sorted(features, key=lambda x: (x["properties"]["destino"], x["properties"]["k"])):
        p = ft["properties"]
        print(f"    {p['destino_nombre']:<35} (k={p['k']}): {p['longitud_m']/1000:6.2f} km | costo: {p['costo']:6.1f}")


if __name__ == "__main__":
    main()
