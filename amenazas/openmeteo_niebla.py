"""
Amenaza 3 - Open-Meteo: niebla costera y visibilidad reducida sobre una grilla del área de estudio.

La niebla costera (camanchaca) ingresa desde el mar hacia el litoral de Quintero y Puchuncaví,
saturando la humedad al 100 % y reduciendo la visibilidad a menos de 1000 m.
Justificación operacional:
  - Inhabilita el vuelo visual VLOS (Visual Line of Sight) exigido por la norma DAN 151 (DGAC).
  - Degrada las cámaras de navegación y altera la calibración de sensores electroquímicos de gases.
  - La condensación sobre la estructura compromete la aviónica.

Extrae: https://api.open-meteo.com/v1/forecast (condiciones actuales de visibilidad, humedad y nubosidad baja)
Transforma:
  - divide el área de estudio en una grilla GRID x GRID (16 celdas poligonales),
  - consulta en el centro de cada celda: visibilidad (m), humedad relativa (%) y nubosidad baja (%),
  - marca `exceeds = true` si la visibilidad es inferior a 1000 m o la humedad >= 95 % con nubosidad baja >= 80 %.

Salida: amenazas/openmeteo_niebla.geojson (estructura en openmeteo_niebla.md)
Uso:    python amenazas/openmeteo_niebla.py
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
VISIBILITY_THRESHOLD_M = 1000.0         # Límite VLOS DAN 151: niebla densa si visibilidad < 1000 m
VARS = "visibility,relative_humidity_2m,cloud_cover_low,weather_code"
OUT = Path(__file__).resolve().parent / "openmeteo_niebla.geojson"


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
        "timezone": "UTC",
    })
    results = data if isinstance(data, list) else [data]

    features = []
    for (cell_id, ring, (lon, lat)), res in zip(cells, results):
        cur = res.get("current", {})
        vis = cur.get("visibility", 10000.0)
        rh = cur.get("relative_humidity_2m", 50)
        c_low = cur.get("cloud_cover_low", 0)
        w_code = cur.get("weather_code", 0)

        # Condición de niebla costera: visibilidad < 1000m o saturación marina (HR >= 95% con nubes bajas)
        is_fog = (vis < VISIBILITY_THRESHOLD_M) or (rh >= 95 and c_low >= 80) or (w_code in (45, 48))

        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "external_id": f"niebla_{cell_id}_{cur.get('time', 'now')}",
                "event_type": "niebla",
                "value": round(float(vis), 1),
                "unit": "m (visibilidad)",
                "threshold": VISIBILITY_THRESHOLD_M,
                "exceeds": bool(is_fog),
                "observed_at": f"{cur.get('time', '2026-10-18T22:00')}:00+00:00" if ":" in cur.get("time", "") else datetime.now(timezone.utc).isoformat(),
                "lon": round(lon, 5),
                "lat": round(lat, 5),
                "cell": cell_id,
                "relative_humidity": rh,
                "cloud_cover_low": c_low,
                "weather_code": w_code,
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "Open-Meteo Forecast API (niebla y visibilidad en superficie)",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"aoi": AOI, "grilla": f"{GRID}x{GRID}", "umbral_visibilidad_m": VISIBILITY_THRESHOLD_M},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    bad = sum(1 for ft in features if ft["properties"]["exceeds"])
    print(f"{len(features)} celdas de visibilidad/niebla ({bad} con niebla activa) -> {OUT.name}")


if __name__ == "__main__":
    main()
