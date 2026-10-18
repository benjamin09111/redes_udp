"""
Metadata 1 - SINCA (MMA): calidad del aire en tiempo real por estación de monitoreo.

Extrae: https://sinca.mma.gob.cl/index.php/json/listadomapa2k19/  (JSON público del mapa SINCA)
Transforma:
  - filtra las estaciones dentro del área de estudio (Quintero / Ventanas / Puchuncaví),
  - normaliza contaminantes (SO2, NO2, CO, O3, PM10, PM2.5), unidades y fechas (ISO 8601),
  - asocia cada estación al nodo `sinca` más cercano de la infraestructura (<= 500 m),
  - calcula el peor estado ICA de la estación (prioridad de muestreo para el GPP).

Salida: metadata/sinca_calidad_aire.geojson  (estructura en sinca_calidad_aire.md)
Uso:    python metadata/sinca_calidad_aire.py
"""
import html
import json
import math
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://sinca.mma.gob.cl/index.php/json/listadomapa2k19/"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
MATCH_RADIUS_M = 500
ROOT = Path(__file__).resolve().parent.parent
NODES = ROOT / "infraestructura" / "nodos.geojson"
OUT = Path(__file__).resolve().parent / "sinca_calidad_aire.geojson"

POLLUTANTS = {"0001": "SO2", "0003": "NO2", "0004": "CO", "0008": "O3", "PM10": "PM10", "PM25": "PM2.5"}


def get_json(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def haversine_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371000.0 * math.asin(math.sqrt(a))


def clean(text):
    """'&micro;g&#8725;m<sup>3</sup>N' -> 'µg/m3N'"""
    if text is None:
        return None
    text = re.sub(r"<[^>]+>", "", html.unescape(text))
    return text.replace("∕", "/").replace("⁄", "/").strip()


def to_iso(local_dt, header_dt):
    """'2026-10-18 16:00' + '... hrs. UTC-04' -> '2026-10-18T16:00:00-04:00'"""
    m = re.search(r"UTC([+-]\d{2})", header_dt or "")
    offset = f"{m.group(1)}:00" if m else "-04:00"
    return f"{local_dt.replace(' ', 'T')}:00{offset}"


def main():
    with open(NODES, encoding="utf-8") as f:
        sinca_nodes = [n for n in json.load(f)["features"] if n["properties"]["category"] == "sinca"]

    stations = get_json(URL)
    features = []
    for s in stations:
        lon, lat = float(s["longitud"]), float(s["latitud"])
        if not (AOI[0] <= lon <= AOI[2] and AOI[1] <= lat <= AOI[3]):
            continue

        measurements = []
        for p in s.get("realtime") or []:
            row = p.get("tableRow") or {}
            if row.get("value") is None:
                continue
            measurements.append({
                "pollutant": POLLUTANTS.get(p["code"], clean(p["name"])),
                "value": row["value"],
                "unit": clean(row.get("unit")),
                "averaging": clean(row.get("movil")),
                "status": row.get("status"),
                "status_code": row.get("statuscode"),
                "icap": row.get("icap"),
                "observed_at": to_iso(row["datetime"], p.get("datetime")),
            })

        dist, node = min(
            ((haversine_m(lon, lat, *n["geometry"]["coordinates"][:2]), n) for n in sinca_nodes),
            key=lambda t: t[0],
        )
        worst = max(measurements, key=lambda m: m["status_code"] or 0, default=None)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {
                "station_key": s["key"],
                "station_name": s["nombre"],
                "commune": s.get("comuna"),
                "network": s.get("red"),
                "operator": s.get("empresa"),
                "ownership": s.get("calificacion"),
                "node_code": node["properties"]["code"] if dist <= MATCH_RADIUS_M else None,
                "node_distance_m": round(dist, 1),
                "worst_status": worst["status"] if worst else None,
                "worst_status_code": worst["status_code"] if worst else None,
                "measurements": measurements,
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "SINCA - Ministerio del Medio Ambiente",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"aoi": AOI, "radio_asociacion_nodo_m": MATCH_RADIUS_M},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    matched = sum(1 for ft in features if ft["properties"]["node_code"])
    print(f"{len(features)} estaciones SINCA ({matched} asociadas a nodos) -> {OUT.name}")


if __name__ == "__main__":
    main()
