"""
Metadata 3 - INE Censo 2017: población por manzana censal (polígonos) para riesgo poblacional.

Extrae: IDE de la Superintendencia del Medio Ambiente (ArcGIS REST, capa "Manzanas censales - INE")
        https://ideserver.sma.gob.cl/arcgis/rest/services/IDE/Infraestructura_rural_urbana/MapServer/11
Transforma:
  - consulta por lotes de ids de las manzanas que intersectan el área de estudio,
  - convierte la geometría Esri JSON (rings) a GeoJSON MultiPolygon (RFC 7946, anillo exterior antihorario),
  - calcula área (m²) y densidad (hab/km²): a mayor densidad, mayor costo de sobrevuelo (riesgo de caída).

Salida: metadata/ine_manzanas.geojson  (estructura en ine_manzanas.md)
Uso:    python metadata/ine_manzanas.py
"""
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://ideserver.sma.gob.cl/arcgis/rest/services/IDE/Infraestructura_rural_urbana/MapServer/11/query"
UA = "redes_udp-uav-sim/1.0 (+https://giteit.udp.cl)"
AOI = (-71.56, -32.82, -71.38, -32.69)  # lon_min, lat_min, lon_max, lat_max
PAGE = 200  # ids por consulta
FIELDS = "MANZENT,CUT,COMUNA,NOMBRE_DIS,TOTAL_PERS,TOTAL_VIVI"
R_EARTH = 6371000.0
OUT = Path(__file__).resolve().parent / "ine_manzanas.geojson"


def get_json(url, params, retries=3):
    full = f"{url}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  reintento {attempt + 1}: {e}")
            time.sleep(5 * (attempt + 1))


def signed_area_m2(ring):
    """> 0 antihorario, < 0 horario (proyección equirectangular local)."""
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring))
    xy = [(math.radians(lon) * R_EARTH * math.cos(lat0), math.radians(lat) * R_EARTH) for lon, lat in ring]
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1])) / 2


def esri_rings_to_multipolygon(rings):
    """Esri: anillo exterior horario, huecos antihorarios. GeoJSON: exterior antihorario, huecos horarios.
    Cada hueco se asigna al último exterior leído (orden en que Esri los entrega)."""
    polys = []
    for ring in rings:
        ring = [[round(x, 6), round(y, 6)] for x, y in ring]
        if signed_area_m2(ring) < 0:  # exterior
            polys.append([ring[::-1]])
        elif polys:  # hueco
            polys[-1].append(ring[::-1])
    return polys


def main():
    # 1) ids de las manzanas en el área; 2) geometrías por lotes de ids
    # (el servidor no soporta paginación con resultOffset de forma confiable)
    ids = get_json(URL, {
        "where": "1=1",
        "geometry": ",".join(map(str, AOI)),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
        "f": "json",
    })["objectIds"] or []
    ids.sort()
    print(f"{len(ids)} manzanas intersectan el área de estudio")

    features = []
    for i in range(0, len(ids), PAGE):
        data = get_json(URL, {
            "objectIds": ",".join(map(str, ids[i:i + PAGE])),
            "outFields": FIELDS,
            "outSR": 4326,
            "f": "json",
        })
        if "error" in data:
            raise RuntimeError(f"ArcGIS REST: {data['error']}")
        for ft in data["features"]:
            a, polys = ft["attributes"], esri_rings_to_multipolygon(ft["geometry"]["rings"])
            if not polys:
                continue
            area = sum(abs(signed_area_m2(p[0])) - sum(abs(signed_area_m2(h)) for h in p[1:]) for p in polys)
            persons = a["TOTAL_PERS"] or 0
            features.append({
                "type": "Feature",
                "geometry": {"type": "MultiPolygon", "coordinates": polys},
                "properties": {
                    "manzent": a["MANZENT"],
                    "cut": a["CUT"],
                    "commune": a["COMUNA"],
                    "district": a["NOMBRE_DIS"],
                    "persons": persons,
                    "dwellings": a["TOTAL_VIVI"],
                    "area_m2": round(area, 1),
                    "density_hab_km2": round(persons / (area / 1e6), 1) if area > 0 else None,
                },
            })

    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "INE Censo 2017 - Manzanas censales (IDE SMA, ArcGIS REST)",
            "url": URL,
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "parametros": {"aoi": AOI},
            "total": len(features),
        },
        "features": features,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False)
    total = sum(ft["properties"]["persons"] for ft in features)
    print(f"{len(features)} manzanas, {total} habitantes -> {OUT.name}")


if __name__ == "__main__":
    main()
