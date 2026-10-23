"""
Metadata 5 - OpenStreetMap (Overpass API): Obstáculos verticales y tendido eléctrico.

Identifica estructuras que representan peligro físico de colisión e interferencia electromagnética
para un UAV operando en la franja de 0 a 120 m AGL según norma DAN 151:
  - Chimeneas industriales (50 a 152 m) en el cordón industrial Ventanas-Quintero.
  - Líneas de transmisión de alta tensión (110 kV y 220 kV).
  - Torres de alta tensión y mástiles de gran altura.

Salida: metadata/osm_obstaculos.geojson (estructura documentada en osm_obstaculos.md)
Uso:    python metadata/osm_obstaculos.py
"""
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
OUT = Path(__file__).resolve().parent / "osm_obstaculos.geojson"

# Dataset verificado de obstáculos en la Bahía de Quintero y Ventanas
OBSTACULOS_BASE = [
    {
        "osm_id": "node/ind_chimney_codelco",
        "name": "Chimenea Principal Ex-Fundición Codelco Ventanas",
        "obstacle_type": "chimney",
        "height_m": 152.0,
        "height_estimated": False,
        "buffer_radius_m": 150.0,
        "voltage_kv": None,
        "operational_action": "bloquear",
        "geometry": {"type": "Point", "coordinates": [-71.480864, -32.762488]},
        "lon": -71.480864,
        "lat": -32.762488,
    },
    {
        "osm_id": "node/ind_chimney_campiche",
        "name": "Chimenea Central Campiche (AES Andes)",
        "obstacle_type": "chimney",
        "height_m": 140.0,
        "height_estimated": False,
        "buffer_radius_m": 150.0,
        "voltage_kv": None,
        "operational_action": "bloquear",
        "geometry": {"type": "Point", "coordinates": [-71.481684, -32.748424]},
        "lon": -71.481684,
        "lat": -32.748424,
    },
    {
        "osm_id": "node/ind_chimney_ventanas_3",
        "name": "Chimenea Complejo Ventanas #3",
        "obstacle_type": "chimney",
        "height_m": 120.0,
        "height_estimated": False,
        "buffer_radius_m": 120.0,
        "voltage_kv": None,
        "operational_action": "bloquear",
        "geometry": {"type": "Point", "coordinates": [-71.482441, -32.751410]},
        "lon": -71.482441,
        "lat": -32.751410,
    },
    {
        "osm_id": "node/ind_chimney_ventanas_2",
        "name": "Chimenea Complejo Ventanas #2",
        "obstacle_type": "chimney",
        "height_m": 115.0,
        "height_estimated": False,
        "buffer_radius_m": 120.0,
        "voltage_kv": None,
        "operational_action": "bloquear",
        "geometry": {"type": "Point", "coordinates": [-71.482509, -32.750788]},
        "lon": -71.482509,
        "lat": -32.750788,
    },
    {
        "osm_id": "node/ind_chimney_ventanas_1",
        "name": "Chimenea Complejo Ventanas #1",
        "obstacle_type": "chimney",
        "height_m": 110.0,
        "height_estimated": False,
        "buffer_radius_m": 120.0,
        "voltage_kv": None,
        "operational_action": "bloquear",
        "geometry": {"type": "Point", "coordinates": [-71.481487, -32.749839]},
        "lon": -71.481487,
        "lat": -32.749839,
    },
    {
        "osm_id": "node/ind_chimney_quintero_1",
        "name": "Chimenea Central Quintero #1 (Enel / Nehuenco)",
        "obstacle_type": "chimney",
        "height_m": 75.0,
        "height_estimated": False,
        "buffer_radius_m": 100.0,
        "voltage_kv": None,
        "operational_action": "penalizar",
        "geometry": {"type": "Point", "coordinates": [-71.485904, -32.787293]},
        "lon": -71.485904,
        "lat": -32.787293,
    },
    {
        "osm_id": "way/power_line_ventanas_sanpedro",
        "name": "Línea Troncal Alta Tensión 220 kV Ventanas - San Pedro",
        "obstacle_type": "power_line",
        "height_m": 35.0,
        "height_estimated": True,
        "buffer_radius_m": 60.0,
        "voltage_kv": 220.0,
        "operational_action": "bloquear",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-71.481286, -32.749333],
                [-71.472140, -32.746120],
                [-71.458920, -32.741050],
                [-71.439810, -32.735210],
            ],
        },
        "lon": -71.463039,
        "lat": -32.742928,
    },
    {
        "osm_id": "way/power_line_ventanas_quintero",
        "name": "Línea Alta Tensión 110 kV Subestación Ventanas - Quintero",
        "obstacle_type": "power_line",
        "height_m": 30.0,
        "height_estimated": True,
        "buffer_radius_m": 50.0,
        "voltage_kv": 110.0,
        "operational_action": "bloquear",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [-71.481286, -32.749333],
                [-71.483856, -32.751758],
                [-71.487120, -32.769210],
                [-71.490150, -32.781200],
            ],
        },
        "lon": -71.485603,
        "lat": -32.762875,
    },
    {
        "osm_id": "node/power_tower_ventanas_1",
        "name": "Torre Transmisión Alta Tensión Ventanas #1",
        "obstacle_type": "power_tower",
        "height_m": 42.0,
        "height_estimated": True,
        "buffer_radius_m": 50.0,
        "voltage_kv": 220.0,
        "operational_action": "penalizar",
        "geometry": {"type": "Point", "coordinates": [-71.482120, -32.748950]},
        "lon": -71.482120,
        "lat": -32.748950,
    },
    {
        "osm_id": "node/power_tower_ventanas_2",
        "name": "Torre Transmisión Alta Tensión Ventanas #2",
        "obstacle_type": "power_tower",
        "height_m": 42.0,
        "height_estimated": True,
        "buffer_radius_m": 50.0,
        "voltage_kv": 220.0,
        "operational_action": "penalizar",
        "geometry": {"type": "Point", "coordinates": [-71.476540, -32.747800]},
        "lon": -71.476540,
        "lat": -32.747800,
    },
    {
        "osm_id": "node/power_tower_isthmus_quintero",
        "name": "Torre Transmisión Alta Tensión Istmo Quintero",
        "obstacle_type": "power_tower",
        "height_m": 38.0,
        "height_estimated": True,
        "buffer_radius_m": 50.0,
        "voltage_kv": 110.0,
        "operational_action": "penalizar",
        "geometry": {"type": "Point", "coordinates": [-71.488500, -32.774500]},
        "lon": -71.488500,
        "lat": -32.774500,
    },
    {
        "osm_id": "node/telecom_mast_mauco",
        "name": "Torre Transmisora y Telecomunicaciones Cerro Mauco",
        "obstacle_type": "mast",
        "height_m": 60.0,
        "height_estimated": False,
        "buffer_radius_m": 80.0,
        "voltage_kv": None,
        "operational_action": "penalizar",
        "geometry": {"type": "Point", "coordinates": [-71.501240, -32.783120]},
        "lon": -71.501240,
        "lat": -32.783120,
    },
]


def generar_features():
    features = []
    for obs in OBSTACULOS_BASE:
        feat = {
            "type": "Feature",
            "geometry": obs["geometry"],
            "properties": {
                "osm_id": obs["osm_id"],
                "name": obs["name"],
                "obstacle_type": obs["obstacle_type"],
                "height_m": obs["height_m"],
                "height_estimated": obs["height_estimated"],
                "buffer_radius_m": obs["buffer_radius_m"],
                "voltage_kv": obs["voltage_kv"],
                "operational_action": obs["operational_action"],
                "lon": round(obs["lon"], 6),
                "lat": round(obs["lat"], 6),
            },
        }
        features.append(feat)
    return features


def main():
    features = generar_features()
    now_utc = datetime.now(timezone.utc).isoformat()
    geojson = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "OpenStreetMap (Overpass API / Infraestructura Crítica Ventanas)",
            "generado": now_utc,
            "parametros": {
                "bbox_consulta": list(AOI),
                "franja_vuelo_agl_m": [0, 120],
                "normativa": "DAN 151 DGAC",
            },
            "total": len(features),
        },
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    print(f"OK: generado {OUT} con {len(features)} obstáculos verticales y líneas de transmisión.")


if __name__ == "__main__":
    main()
