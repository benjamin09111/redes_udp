"""Carga amenazas/csn_sismos.geojson en threat_event (event_type = 'sismo')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/csn_sismos.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (sismos)", lambda cur: insertar_amenazas(cur, ARCHIVO, "csn_sismos"))
