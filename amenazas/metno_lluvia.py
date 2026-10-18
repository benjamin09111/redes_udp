"""
Amenaza 4 - MET Norway Locationforecast: precipitación de la próxima hora sobre una grilla del área.

Reemplaza a JAXA GSMaP / RainViewer: GSMaP exige cuenta FTP y RainViewer solo entrega imágenes de
radar (teselas PNG), sin valores numéricos de lluvia.
Extrae: https://api.met.no/weatherapi/locationforecast/2.0/compact  (una consulta por celda)
Transforma:
  - misma grilla GRID x GRID que el viento; cada celda es un polígono,
  - toma la precipitación prevista para la próxima hora (mm) en el centro de cada celda,
  - marca `exceeds = true` si supera RAIN_THRESHOLD_MM_H: las aristas de esa celda se inhabilitan
    y el dron activa el retorno de emergencia (LPP).

Salida: amenazas/metno_lluvia.geojson  (estructura en metno_lluvia.md)
Uso:    python amenazas/metno_lluvia.py
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"  # MET Norway exige User-Agent identificable
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
GRID = 4
RAIN_THRESHOLD_MM_H = 2.0                # .agents/rules/geo_and_apis.md: No-Go si precipitación > 2 mm/h
OUT = Path(__file__).resolve().parent / "metno_lluvia.geojson"


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
    features = []
    for cell_id, ring, (lon, lat) in grid_cells():
        data = get_json(URL, {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}"})  # la API admite máx. 4 decimales
        step = data["properties"]["timeseries"][0]
        next_1h = step["data"].get("next_1_hours", {})
        rain = next_1h.get("details", {}).get("precipitation_amount", 0.0)
        start = datetime.fromisoformat(step["time"].replace("Z", "+00:00"))
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "external_id": f"{cell_id}_{step['time']}",
                "event_type": "lluvia",
                "value": rain,
                "unit": "mm/h",
                "threshold": RAIN_THRESHOLD_MM_H,
                "exceeds": rain > RAIN_THRESHOLD_MM_H,
                "observed_at": start.isoformat(),
                "valid_until": (start + timedelta(hours=1)).isoformat(),
                "lon": round(lon, 5),
                "lat": round(lat, 5),
                "cell": cell_id,
                "symbol_code": next_1h.get("summary", {}).get("symbol_code"),
                "model_updated_at": data["properties"]["meta"]["updated_at"],
            },
        })
        time.sleep(0.2)

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "MET Norway Locationforecast 2.0",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"aoi": AOI, "grilla": f"{GRID}x{GRID}", "umbral_mm_h": RAIN_THRESHOLD_MM_H},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    bad = sum(1 for ft in features if ft["properties"]["exceeds"])
    print(f"{len(features)} celdas de lluvia ({bad} sobre umbral) -> {OUT.name}")


if __name__ == "__main__":
    main()
