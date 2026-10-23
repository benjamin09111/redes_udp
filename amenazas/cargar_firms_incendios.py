"""Carga amenazas/firms_incendios.geojson en threat_event (event_type = 'incendio') e inserta foco simulado."""
import json
from datetime import datetime, timezone
from bd.conexion import RAIZ, ejecutar, insertar_amenazas

ARCHIVO = "amenazas/firms_incendios.geojson"
CONFIG_PATH = RAIZ / "config" / "parametros.json"


def cargar_con_foco_simulado(cur):
    n = insertar_amenazas(cur, ARCHIVO, "firms_incendios")
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        foco = cfg.get("contingencia", {})
        if foco:
            cur.execute("""
            INSERT INTO threat_event (source_id, external_id, event_type, value, unit, threshold,
                                      exceeds, simulated, observed_at, properties,
                                      point_geom, geom)
            SELECT ds.id, 'sim_asfaltos_quintero', 'incendio', 850.0, 'K', 320.0,
                   true, true, NOW(), %s::jsonb,
                   ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                   ST_Buffer(ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, %s)::geometry
            FROM data_source ds WHERE ds.code = 'firms_incendios'
            ON CONFLICT (source_id, external_id) DO UPDATE
                SET exceeds = EXCLUDED.exceeds, simulated = EXCLUDED.simulated, geom = EXCLUDED.geom
            """, (
                json.dumps({"nombre": foco.get("nombre"), "descripcion": foco.get("descripcion")}, ensure_ascii=False),
                foco["lon"], foco["lat"],
                foco["lon"], foco["lat"],
                foco.get("radio_m", 180.0)
            ))
            n += 1
    return n


if __name__ == "__main__":
    ejecutar("threat_event (incendios)", cargar_con_foco_simulado)
