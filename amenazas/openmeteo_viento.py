"""
Amenaza 3 - Open-Meteo: viento y ráfagas actuales sobre una grilla del área de estudio.

Reemplaza a DMC/Windy: la API de la DMC exige registro/token y la de Windy es de pago.
Extrae: https://api.open-meteo.com/v1/forecast  (condiciones actuales, una consulta para toda la grilla)
Transforma:
  - divide el área de estudio en una grilla GRID x GRID; cada celda es un polígono,
  - consulta en el centro de cada celda: viento a 10 m, ráfagas a 10 m, viento a 80 y 120 m (techo DAN 151),
  - marca `exceeds = true` si las ráfagas o el viento a 120 m superan GUST_THRESHOLD_MS:
    las aristas que cruzan esa celda se inhabilitan para el ruteo.

Salida: amenazas/openmeteo_viento.geojson  (estructura en openmeteo_viento.md)
Uso:    python amenazas/openmeteo_viento.py
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://api.open-meteo.com/v1/forecast"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
GRID = 4
GUST_THRESHOLD_MS = 12.0                 # Límite operacional DJI Matrice 350 RTK (12 m/s a 120 m AGL)
VARS = "wind_speed_10m,wind_gusts_10m,wind_direction_10m,wind_speed_80m,wind_speed_120m,wind_direction_120m"
OUT = Path(__file__).resolve().parent / "openmeteo_viento.geojson"


def get_json(url, params, retries=3):
    full = f"{url}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def grid_cells():
    dx, dy = (AOI[2] - AOI[0]) / GRID, (AOI[3] - AOI[1]) / GRID
    for row in range(GRID):
        for col in range(GRID):
            x0, y0 = AOI[0] + col * dx, AOI[1] + row * dy
            ring = [[x0, y0], [x0 + dx, y0], [x0 + dx, y0 + dy], [x0, y0 + dy], [x0, y0]]
            yield f"r{row}c{col}", [[round(x, 5), round(y, 5)] for x, y in ring], (x0 + dx / 2, y0 + dy / 2)


def main():
    cells = list(grid_cells())
    data = get_json(URL, {
        "latitude": ",".join(f"{c[1]:.4f}" for _, _, c in cells),
        "longitude": ",".join(f"{c[0]:.4f}" for _, _, c in cells),
        "current": VARS,
        "wind_speed_unit": "ms",
        "timezone": "UTC",
    })
    results = data if isinstance(data, list) else [data]

    features = []
    for (cell_id, ring, (lon, lat)), res in zip(cells, results):
        cur = res["current"]
        gust, w120 = cur["wind_gusts_10m"], cur["wind_speed_120m"]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "external_id": f"{cell_id}_{cur['time']}",
                "event_type": "viento",
                "value": gust,
                "unit": "m/s (ráfaga 10 m)",
                "threshold": GUST_THRESHOLD_MS,
                "exceeds": max(gust, w120) > GUST_THRESHOLD_MS,
                "observed_at": f"{cur['time']}:00+00:00",
                "lon": round(lon, 5),
                "lat": round(lat, 5),
                "cell": cell_id,
                "wind_speed_10m": cur["wind_speed_10m"],
                "wind_direction_10m": cur["wind_direction_10m"],
                "wind_speed_80m": cur["wind_speed_80m"],
                "wind_speed_120m": w120,
                "wind_direction_120m": cur["wind_direction_120m"],
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "Open-Meteo Forecast API (condiciones actuales)",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"aoi": AOI, "grilla": f"{GRID}x{GRID}", "umbral_rafaga_ms": GUST_THRESHOLD_MS},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    bad = sum(1 for ft in features if ft["properties"]["exceeds"])
    print(f"{len(features)} celdas de viento ({bad} sobre umbral) -> {OUT.name}")


if __name__ == "__main__":
    main()
