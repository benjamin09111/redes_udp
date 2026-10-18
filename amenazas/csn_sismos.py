"""
Amenaza 2 - Sismos (CSN Chile vía EMSC FDSN): eventos sísmicos recientes cerca del área de estudio.

El CSN (Universidad de Chile) no publica una API JSON oficial; sus eventos se distribuyen por el
servicio FDSN del EMSC (campo `auth` = "CSN" cuando el CSN es la agencia autora).
Extrae: https://www.seismicportal.eu/fdsnws/event/1/query  (últimos DAYS días, radio MAX_RADIUS_DEG)
Transforma:
  - calcula la distancia del epicentro a la base (Aeródromo de Quintero),
  - estima un radio de afectación R_km = 10^(0.5*M - 1.8) (heurística de intensidad >= VI) y
    genera su polígono circular,
  - marca `exceeds = true` si M >= MAG_THRESHOLD (zona activa). Indica además `base_dentro_radio`:
    la fase 3 aplica la regla del informe (un nodo base dentro del radio queda sin energía de recarga).

Salida: amenazas/csn_sismos.geojson  (estructura en csn_sismos.md)
Uso:    python amenazas/csn_sismos.py
"""
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL = "https://www.seismicportal.eu/fdsnws/event/1/query"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
BASE_LON, BASE_LAT = -71.5173, -32.7842  # Aeródromo de Quintero (SCER)
DAYS = 30
MAX_RADIUS_DEG = 3.0   # ~330 km
MIN_MAG = 3.0
MAG_THRESHOLD = 5.0
OUT = Path(__file__).resolve().parent / "csn_sismos.geojson"


def get_json(url, params, retries=3):
    full = f"{url}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r) if r.status == 200 else {"features": []}  # 204 = sin eventos
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def haversine_km(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(a))


def circle(lon, lat, radius_m, n=48):
    dlat = radius_m / 111320.0
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    ring = [[round(lon + dlon * math.cos(2 * math.pi * i / n), 5),
             round(lat + dlat * math.sin(2 * math.pi * i / n), 5)] for i in range(n)]
    return ring + [ring[0]]


def main():
    start = (datetime.now(timezone.utc) - timedelta(days=DAYS)).strftime("%Y-%m-%dT%H:%M:%S")
    data = get_json(URL, {
        "format": "json",
        "lat": BASE_LAT,
        "lon": BASE_LON,
        "maxradius": MAX_RADIUS_DEG,
        "minmag": MIN_MAG,
        "start": start,
        "orderby": "time",
        "limit": 1000,
    })

    features = []
    for ev in data.get("features", []):
        p = ev["properties"]
        lon, lat, mag = p["lon"], p["lat"], p["mag"]
        radius_km = 10 ** (0.5 * mag - 1.8)
        dist_km = haversine_km(BASE_LON, BASE_LAT, lon, lat)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [circle(lon, lat, radius_km * 1000)]},
            "properties": {
                "external_id": p["unid"],
                "event_type": "sismo",
                "value": mag,
                "unit": f"magnitud ({p.get('magtype')})",
                "threshold": MAG_THRESHOLD,
                "exceeds": mag >= MAG_THRESHOLD,
                "observed_at": p["time"].replace("Z", "+00:00"),
                "lon": lon,
                "lat": lat,
                "depth_km": p.get("depth"),
                "region": p.get("flynn_region"),
                "authority": p.get("auth"),
                "affect_radius_km": round(radius_km, 2),
                "distance_to_base_km": round(dist_km, 1),
                "base_dentro_radio": dist_km <= radius_km,
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "EMSC FDSN Event Service (incluye eventos autoría CSN Chile)",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"dias": DAYS, "radio_busqueda_grados": MAX_RADIUS_DEG,
                           "magnitud_min": MIN_MAG, "umbral_magnitud": MAG_THRESHOLD},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    csn = sum(1 for ft in features if ft["properties"]["authority"] == "CSN")
    print(f"{len(features)} sismos ({csn} autoría CSN) -> {OUT.name}")


if __name__ == "__main__":
    main()
