"""Carga amenazas/metno_lluvia.geojson en threat_event (event_type = 'lluvia')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/metno_lluvia.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (lluvia)", lambda cur: insertar_amenazas(cur, ARCHIVO, "metno_lluvia"))
