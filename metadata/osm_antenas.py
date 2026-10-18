"""
Metadata 4 - OpenStreetMap (Overpass API): antenas de telecomunicaciones y cobertura estimada.

Reemplaza a Subtel RNC, cuyo visor está protegido por reCAPTCHA y no expone una API automatizable.
Extrae: https://overpass-api.de/api/interpreter  (torres/mástiles de comunicación en el área + margen)
Transforma:
  - filtra elementos de telecomunicaciones (descarta sirenas, faros, etc.),
  - genera un polígono de cobertura circular de COVERAGE_RADIUS_M alrededor de cada antena.
  Las aristas fuera de toda cobertura son "sombras de telemetría" (riesgo de pérdida de enlace GCS).

Salida: metadata/osm_antenas.geojson  (estructura en osm_antenas.md)
Uso:    python metadata/osm_antenas.py
"""
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"]
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
MARGIN_DEG = 0.08                        # ~8 km: antenas fuera del área también la cubren
COVERAGE_RADIUS_M = 3000                 # supuesto: celda macro LTE suburbana (1-5 km)
OUT = Path(__file__).resolve().parent / "osm_antenas.geojson"


def overpass(query):
    body = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for url in MIRRORS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, data=body, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.load(r), url
            except Exception as e:
                last = e
                print(f"  {url} falló ({e}), reintentando...")
                time.sleep(5)
    raise RuntimeError(f"Overpass no disponible: {last}")


def circle(lon, lat, radius_m, n=32):
    dlat = radius_m / 111320.0
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    ring = [[round(lon + dlon * math.cos(2 * math.pi * i / n), 6),
             round(lat + dlat * math.sin(2 * math.pi * i / n), 6)] for i in range(n)]
    return ring + [ring[0]]


def is_telecom(tags):
    return (tags.get("tower:type") == "communication"
            or tags.get("communication:mobile_phone") == "yes"
            or any(k.startswith("communication:") for k in tags))


def to_float(value):
    try:
        return float(str(value).replace("m", "").strip())
    except (TypeError, ValueError):
        return None


def main():
    s, w, n, e = AOI[1] - MARGIN_DEG, AOI[0] - MARGIN_DEG, AOI[3] + MARGIN_DEG, AOI[2] + MARGIN_DEG
    bbox = f"{s},{w},{n},{e}"
    query = f"""[out:json][timeout:90];
(
  nwr["tower:type"="communication"]({bbox});
  nwr["man_made"~"^(mast|tower|antenna)$"]["communication:mobile_phone"]({bbox});
  nwr["communication:mobile_phone"="yes"]({bbox});
);
out center tags;"""
    data, used = overpass(query)

    features = []
    for el in data["elements"]:
        tags = el.get("tags", {})
        if not is_telecom(tags):
            continue
        lon = el.get("lon", el.get("center", {}).get("lon"))
        lat = el.get("lat", el.get("center", {}).get("lat"))
        if lon is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [circle(lon, lat, COVERAGE_RADIUS_M)]},
            "properties": {
                "osm_id": f"{el['type']}/{el['id']}",
                "name": tags.get("name"),
                "operator": tags.get("operator"),
                "structure": tags.get("man_made"),
                "mobile_phone": tags.get("communication:mobile_phone") == "yes",
                "height_m": to_float(tags.get("height")),
                "coverage_radius_m": COVERAGE_RADIUS_M,
                "lon": round(lon, 6),
                "lat": round(lat, 6),
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "OpenStreetMap vía Overpass API",
            "url": used,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"bbox_consulta": [w, s, e, n], "radio_cobertura_m": COVERAGE_RADIUS_M},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    print(f"{len(features)} antenas de telecomunicaciones -> {OUT.name}")


if __name__ == "__main__":
    main()
