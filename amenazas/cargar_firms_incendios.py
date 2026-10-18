"""Carga amenazas/firms_incendios.geojson en threat_event (event_type = 'incendio')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/firms_incendios.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (incendios)", lambda cur: insertar_amenazas(cur, ARCHIVO, "firms_incendios"))
