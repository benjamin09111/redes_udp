"""Carga amenazas/opensky_aeronaves.geojson en threat_event (event_type = 'aeronave')."""
from bd.conexion import ejecutar, insertar_amenazas

ARCHIVO = "amenazas/opensky_aeronaves.geojson"

if __name__ == "__main__":
    ejecutar("threat_event (aeronave)", lambda cur: insertar_amenazas(cur, ARCHIVO, "opensky_aeronaves"))
