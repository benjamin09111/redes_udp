"""Carga amenazas/openmeteo_niebla.geojson en threat_event (event_type = 'niebla')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/openmeteo_niebla.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (niebla)", lambda cur: insertar_amenazas(cur, ARCHIVO, "openmeteo_niebla"))
