"""
Amenaza 1 - NASA FIRMS: focos de incendio activos detectados por satélite (últimos 7 días).

Extrae: archivos públicos NRT de FIRMS para Sudamérica (VIIRS S-NPP, VIIRS NOAA-20 y MODIS)
        https://firms.modaps.eosdis.nasa.gov/data/active_fire/
Transforma:
  - filtra los focos dentro del área de estudio ampliada (REGION_MARGIN_DEG),
  - genera un polígono de exclusión circular de EXCLUSION_RADIUS_M (humo, calor y turbulencia térmica),
  - marca `exceeds = true` si la confianza de detección es nominal/alta: la zona queda activa
    (la fase 3 decide qué nodos y aristas bloquea).

Salida: amenazas/firms_incendios.geojson  (estructura en firms_incendios.md)
Uso:    python amenazas/firms_incendios.py
"""
import csv
import io
import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://firms.modaps.eosdis.nasa.gov/data/active_fire"
FILES = {
    "VIIRS_SNPP": f"{BASE}/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_America_7d.csv",
    "VIIRS_NOAA20": f"{BASE}/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_America_7d.csv",
    "MODIS": f"{BASE}/modis-c6.1/csv/MODIS_C6_1_South_America_7d.csv",
}
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
REGION_MARGIN_DEG = 0.30                 # ~30 km alrededor del área de estudio
EXCLUSION_RADIUS_M = 2000                # supuesto: radio de humo/turbulencia que inhabilita el vuelo
OUT = Path(__file__).resolve().parent / "firms_incendios.geojson"


def get_text(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def circle(lon, lat, radius_m, n=32):
    dlat = radius_m / 111320.0
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    ring = [[round(lon + dlon * math.cos(2 * math.pi * i / n), 6),
             round(lat + dlat * math.sin(2 * math.pi * i / n), 6)] for i in range(n)]
    return ring + [ring[0]]


def reliable(instrument, confidence):
    # VIIRS: low / nominal / high (o l / n / h); MODIS: 0-100
    if instrument == "MODIS":
        return float(confidence) >= 50
    return confidence in ("n", "h", "nominal", "high")


def main():
    w, s = AOI[0] - REGION_MARGIN_DEG, AOI[1] - REGION_MARGIN_DEG
    e, n = AOI[2] + REGION_MARGIN_DEG, AOI[3] + REGION_MARGIN_DEG
    features = []
    for instrument, url in FILES.items():
        rows = list(csv.DictReader(io.StringIO(get_text(url))))
        kept = 0
        for r in rows:
            lon, lat = float(r["longitude"]), float(r["latitude"])
            if not (w <= lon <= e and s <= lat <= n):
                continue
            hhmm = r["acq_time"].zfill(4)
            observed = f"{r['acq_date']}T{hhmm[:2]}:{hhmm[2:]}:00+00:00"
            kind = "MODIS" if instrument == "MODIS" else "VIIRS"
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [circle(lon, lat, EXCLUSION_RADIUS_M)]},
                "properties": {
                    "external_id": f"{instrument}_{r['acq_date']}_{hhmm}_{lat:.4f}_{lon:.4f}",
                    "event_type": "incendio",
                    "value": float(r["frp"]),
                    "unit": "MW (FRP)",
                    "threshold": None,
                    "exceeds": reliable(kind, r["confidence"]),
                    "observed_at": observed,
                    "lon": round(lon, 5),
                    "lat": round(lat, 5),
                    "radius_m": EXCLUSION_RADIUS_M,
                    "instrument": instrument,
                    "satellite": r.get("satellite"),
                    "confidence": r["confidence"],
                    "brightness_k": float(r.get("bright_ti4") or r.get("brightness") or 0),
                    "daynight": r.get("daynight"),
                },
            })
            kept += 1
        print(f"  {instrument}: {len(rows)} focos en Sudamérica, {kept} en la región")

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "NASA FIRMS (VIIRS S-NPP, VIIRS NOAA-20, MODIS) - NRT 7 días",
            "url": BASE,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"bbox_region": [w, s, e, n], "radio_exclusion_m": EXCLUSION_RADIUS_M},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    print(f"{len(features)} focos de incendio -> {OUT.name}")


if __name__ == "__main__":
    main()
