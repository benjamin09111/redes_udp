"""Carga amenazas/openmeteo_viento.geojson en threat_event (event_type = 'viento')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/openmeteo_viento.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (viento)", lambda cur: insertar_amenazas(cur, ARCHIVO, "openmeteo_viento"))
