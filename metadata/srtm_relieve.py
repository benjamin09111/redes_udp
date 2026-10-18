"""
Metadata 2 - SRTM 30 m (NASA) vía OpenTopoData: perfil de relieve de cada arista.

Extrae: https://api.opentopodata.org/v1/srtm30m  (API pública, máx. 100 puntos/consulta, 1 consulta/s)
Transforma:
  - muestrea cada arista de infraestructura/aristas.geojson cada SPACING_M metros,
  - consulta la elevación del terreno (m s.n.m.) en cada muestra,
  - resume por arista: terreno mín/máx/medio, desnivel, ascenso y descenso acumulados
    (sentido source -> target). Insumo para la altitud segura (DAN 151: <= 120 m AGL) y la EEE.
  Puntos sobre el mar (SRTM sin dato) se toman como 0 m.

Requiere: haber ejecutado infraestructura/extraer_infraestructura.py
Salida:   metadata/srtm_relieve.geojson  (estructura en srtm_relieve.md)
Uso:      python metadata/srtm_relieve.py
"""
import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://api.opentopodata.org/v1/srtm30m"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
SPACING_M = 100
BATCH = 100
ROOT = Path(__file__).resolve().parent.parent
EDGES = ROOT / "infraestructura" / "aristas.geojson"
OUT = Path(__file__).resolve().parent / "srtm_relieve.geojson"


def get_json(url, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def sample(coords, length_m):
    (lon1, lat1), (lon2, lat2) = coords[0], coords[-1]
    n = max(1, math.ceil(length_m / SPACING_M))
    return [(round(lon1 + (lon2 - lon1) * i / n, 5), round(lat1 + (lat2 - lat1) * i / n, 5)) for i in range(n + 1)]


def main():
    with open(EDGES, encoding="utf-8") as f:
        edges = json.load(f)["features"]

    profiles = {e["properties"]["id"]: sample(e["geometry"]["coordinates"], e["properties"]["length_m"]) for e in edges}
    points = sorted({p for prof in profiles.values() for p in prof})
    print(f"{len(edges)} aristas -> {len(points)} puntos únicos ({math.ceil(len(points) / BATCH)} consultas)")

    elevation = {}
    for i in range(0, len(points), BATCH):
        chunk = points[i:i + BATCH]
        locs = "|".join(f"{lat},{lon}" for lon, lat in chunk)
        data = get_json(f"{URL}?locations={locs}")
        for (lon, lat), res in zip(chunk, data["results"]):
            elevation[(lon, lat)] = res["elevation"] if res["elevation"] is not None else 0.0
        time.sleep(1.1)  # límite de la API pública: 1 consulta por segundo

    features = []
    for e in edges:
        p = e["properties"]
        z = [elevation[pt] for pt in profiles[p["id"]]]
        steps = [b - a for a, b in zip(z, z[1:])]
        features.append({
            "type": "Feature",
            "geometry": e["geometry"],
            "properties": {
                "edge_id": p["id"],
                "source_code": p["source_code"],
                "target_code": p["target_code"],
                "samples": len(z),
                "terrain_min_m": round(min(z), 1),
                "terrain_max_m": round(max(z), 1),
                "terrain_mean_m": round(sum(z) / len(z), 1),
                "relief_m": round(max(z) - min(z), 1),
                "ascent_m": round(sum(s for s in steps if s > 0), 1),
                "descent_m": round(-sum(s for s in steps if s < 0), 1),
                "profile_m": [round(v, 1) for v in z],
            },
        })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "NASA SRTM GL1 (30 m) vía OpenTopoData",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"espaciado_muestras_m": SPACING_M, "puntos_consultados": len(points)},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=1)
    print(f"{len(features)} perfiles de arista -> {OUT.name}")


if __name__ == "__main__":
    main()
