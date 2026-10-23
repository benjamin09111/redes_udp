"""Verifica los entregables de la fase 2 (pauta), la validez de los GeoJSON y la BD.

Uso (dentro de Docker, con la BD levantada y los datos generados):
    docker compose run --rm etl python tests/verificar.py

Sale con código 1 si algún chequeo falla.
"""
import json
import re
import sys
from pathlib import Path

try:
    from bd.conexion import RAIZ, conectar
except ImportError:
    RAIZ = Path(__file__).resolve().parent.parent
    conectar = None

RESULTADOS = []


def check(nombre, ok, detalle=""):
    RESULTADOS.append((nombre, ok, detalle))


def leer(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8")


# Archivos de datos: cada uno debe tener .md y un cargador cargar_<nombre>.py en su carpeta
DATOS = {
    "infraestructura": ["nodos", "aristas", "zonas_urbanas"],
    "metadata": ["sinca_calidad_aire", "srtm_relieve", "ine_manzanas", "osm_antenas"],
    "amenazas": ["firms_incendios", "opensky_aeronaves", "openmeteo_viento", "openmeteo_niebla"],
}


# ---------- 1. entregables de la pauta ----------
def chequear_entregables():
    check("0 · bd/schema.sql existe", (RAIZ / "bd/schema.sql").exists())
    check("0 · bd/bd_diagrama.png existe", (RAIZ / "bd/bd_diagrama.png").exists())

    check("1 · extractor de infraestructura", (RAIZ / "infraestructura/extraer_infraestructura.py").exists())
    extractores = {
        "metadata": ["sinca_calidad_aire", "srtm_relieve", "ine_manzanas", "osm_antenas"],
        "amenazas": ["firms_incendios", "opensky_aeronaves", "openmeteo_viento", "openmeteo_niebla"],
    }
    for carpeta, lista in extractores.items():
        check(f"2-3 · {carpeta}: {len(lista)} extractores (n = 4 integrantes)",
              all((RAIZ / carpeta / f"{n}.py").exists() for n in lista))

    for carpeta, nombres in DATOS.items():
        for n in nombres:
            ruta = f"{carpeta}/{n}.geojson"
            check(f"4 · {ruta} tiene .md", (RAIZ / carpeta / f"{n}.md").exists())
            check(f"6 · {ruta} tiene cargador", (RAIZ / carpeta / f"cargar_{n}.py").exists())

    check("7 · sitio Leaflet (sitio_web/index.html)", (RAIZ / "sitio_web/index.html").exists()
          and "leaflet@1.9.4" in leer("sitio_web/index.html"))
    ruta = json.loads(leer("sitio_web/data/ruta_dijkstra.geojson"))
    check("8 · ruta pgr_dijkstra con costo = longitud",
          ruta["etl"]["parametros"]["costo"] == "length_m" and ruta["etl"]["parametros"]["considera_metadata_y_amenazas"] is False,
          ruta["etl"]["fuente"])
    check("8 · ruta pgr_dijkstra contiene k=1 y k=2 como Features",
          any(f["properties"].get("k") == 1 for f in ruta["features"]) and any(f["properties"].get("k") == 2 for f in ruta["features"]))
    check("Parámetros · config/parametros.json existe", (RAIZ / "config/parametros.json").exists())
    check("9 · main.py en la raíz", (RAIZ / "main.py").exists())
    check("Docker · Dockerfile con versión de Python fijada",
          re.search(r"FROM python:\d+\.\d+\.\d+", leer("Dockerfile")) is not None)
    compose = leer("docker-compose.yml")
    check("Docker · imagen de BD fijada (sin 'latest')",
          "pgrouting/pgrouting:16-3.5-3.8.0" in compose and "latest" not in compose)
    check("Docker · dependencias fijadas con ==", re.search(r"==\d", leer("requirements.txt")) is not None)


# ---------- 2. GeoJSON válido (RFC 7946) y documentado ----------
def area_firmada(anillo):
    """> 0 antihorario, < 0 horario (en grados; basta para el signo)."""
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(anillo, anillo[1:] + anillo[:1])) / 2


def chequear_geojson(carpeta, nombre):
    ruta = f"{carpeta}/{nombre}.geojson"
    fc = json.loads(leer(ruta))
    problemas = []
    if fc.get("type") != "FeatureCollection":
        problemas.append("no es FeatureCollection")
    for i, f in enumerate(fc["features"]):
        g = f.get("geometry")
        if not g or not isinstance(f.get("properties"), dict):
            problemas.append(f"feature {i} sin geometría o propiedades")
            continue
        if g["type"] == "Polygon":
            poligonos = [g["coordinates"]]
        elif g["type"] == "MultiPolygon":
            poligonos = g["coordinates"]
        else:
            continue
        for poli in poligonos:
            for k, anillo in enumerate(poli):
                if anillo[0] != anillo[-1]:
                    problemas.append(f"feature {i}: anillo no cerrado")
                a = area_firmada(anillo)
                if k == 0 and a < 0:
                    problemas.append(f"feature {i}: exterior horario (RFC 7946 pide antihorario)")
                if k > 0 and a > 0:
                    problemas.append(f"feature {i}: hueco antihorario (RFC 7946 pide horario)")
        for x, y in _coords(g["coordinates"]):
            if not (-180 <= x <= 180 and -90 <= y <= 90):
                problemas.append(f"feature {i}: coordenada fuera de rango")
                break
    check(f"GeoJSON RFC 7946 · {ruta}", not problemas, "; ".join(problemas[:3]))
    return fc


def _coords(c):
    if isinstance(c[0], (int, float)):
        yield c
    else:
        for sub in c:
            yield from _coords(sub)


def chequear_documentacion(carpeta, nombre, fc):
    """Cada propiedad del json debe aparecer en su .md (entre comillas invertidas)."""
    texto = leer(f"{carpeta}/{nombre}.md")
    claves = set()
    for f in fc["features"]:
        for k, v in f["properties"].items():
            claves.add(k)
            if isinstance(v, list) and v and isinstance(v[0], dict):
                claves.update(v[0].keys())
    faltan = sorted(k for k in claves if f"`{k}`" not in texto)
    check(f"4 · {carpeta}/{nombre}.md documenta todos los campos", not faltan,
          f"faltan: {', '.join(faltan)}" if faltan else f"{len(claves)} campos")


# ---------- 3. base de datos ----------
def chequear_bd(datos):
    if conectar is None:
        check("BD accesible y comprobación pgRouting", "SKIP", "omitido en host sin psycopg; se ejecuta dentro del contenedor Docker")
        return
    try:
        conn = conectar()
    except Exception as e:  # noqa: BLE001 - reportar cualquier falla de conexión
        check("BD accesible", False, str(e))
        return

    esperado = {
        "data_source": 11,
        "infra_node": len(datos["nodos"]["features"]),
        "infra_edge": len(datos["aristas"]["features"]),
        "urban_zone": len(datos["zonas_urbanas"]["features"]),
        "meta_air_quality": sum(len(f["properties"]["measurements"]) for f in datos["sinca_calidad_aire"]["features"]),
        "meta_edge_terrain": len(datos["srtm_relieve"]["features"]),
        "meta_census_block": len(datos["ine_manzanas"]["features"]),
        "meta_telecom_antenna": len(datos["osm_antenas"]["features"]),
        "threat_event": sum(len(datos[n]["features"]) for n in
                            ["firms_incendios", "opensky_aeronaves", "openmeteo_viento", "openmeteo_niebla"]),
    }
    with conn, conn.cursor() as cur:
        for tabla, n in esperado.items():
            cur.execute(f"SELECT count(*) FROM {tabla}")
            real = cur.fetchone()[0]
            check(f"BD · {tabla} = features del json", real == n, f"{real} de {n}")

        for tabla, col in [("infra_edge", "geom"), ("urban_zone", "geom"), ("meta_census_block", "geom"),
                           ("meta_telecom_antenna", "coverage_geom"), ("threat_event", "geom")]:
            cur.execute(f"SELECT count(*) FROM {tabla} WHERE NOT ST_IsValid({col})")
            check(f"BD · geometrías válidas en {tabla}.{col}", cur.fetchone()[0] == 0)

        cur.execute("""SELECT count(DISTINCT component) FROM
                       pgr_connectedComponents('SELECT id, source, target, cost, reverse_cost FROM infra_edge')""")
        componentes = cur.fetchone()[0]
        check("BD · grafo conexo (1 componente)", componentes == 1, f"{componentes} componentes")

        # La ruta del sitio debe coincidir con pgr_dijkstra recalculado en la BD
        rutas_k1 = [ft for ft in datos["ruta_dijkstra"]["features"] if ft["properties"].get("k", 1) == 1]
        rutas_k2 = [ft for ft in datos["ruta_dijkstra"]["features"] if ft["properties"].get("k") == 2]

        for ft in rutas_k1:
            p = ft["properties"]
            cur.execute("""
                SELECT round(sum(e.length_m)::numeric, 1), round(max(d.agg_cost)::numeric, 1)
                FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM infra_edge',
                     (SELECT id FROM infra_node WHERE code = 'base_scer'),
                     (SELECT id FROM infra_node WHERE code = %s), directed := true) d
                LEFT JOIN infra_edge e ON e.id = d.edge""", (p["destino"],))
            longitud, costo = cur.fetchone()
            ok = abs(float(longitud) - p["longitud_m"]) < 0.5 and abs(float(costo) - p["costo"]) < 0.5
            check(f"Ruta · base → {p['destino']} coincide con la BD", ok,
                  f"{p['longitud_m']} m (BD {longitud} m), costo {p['costo']} vs {costo}")
            check(f"Ruta · costo = longitud ({p['destino']})", abs(p["costo"] - p["longitud_m"]) < 0.5)

        # Chequeo de k=2 (Criterio 8)
        check("Ruta · contiene k=2 para cada estación SINCA", len(rutas_k2) == len(rutas_k1), f"{len(rutas_k2)} de {len(rutas_k1)}")
        for ft2 in rutas_k2:
            code = ft2["properties"]["destino"]
            ft1 = next(f for f in rutas_k1 if f["properties"]["destino"] == code)
            ok_k2 = ft2["properties"]["longitud_m"] >= ft1["properties"]["longitud_m"]
            check(f"Ruta · k=2 distinta y longitud >= k=1 ({code})", ok_k2, f"k1={ft1['properties']['longitud_m']}m, k2={ft2['properties']['longitud_m']}m")
    conn.close()


def main():
    chequear_entregables()

    datos = {}
    for carpeta, nombres in DATOS.items():
        for n in nombres:
            datos[n] = chequear_geojson(carpeta, n)
            chequear_documentacion(carpeta, n, datos[n])
    datos["ruta_dijkstra"] = json.loads(leer("sitio_web/data/ruta_dijkstra.geojson"))
    chequear_bd(datos)

    fallas = [r for r in RESULTADOS if r[1] is False]
    omitidos = [r for r in RESULTADOS if r[1] == "SKIP"]
    correctos = [r for r in RESULTADOS if r[1] is True]

    for nombre, ok, detalle in RESULTADOS:
        if ok == "SKIP":
            marca = "SKIP  "
        elif ok is True:
            marca = "OK    "
        else:
            marca = "FALLA "
        print(f"{marca} {nombre}" + (f"  ({detalle})" if detalle else ""))

    resumen_txt = f"\n{len(correctos)} de {len(RESULTADOS) - len(omitidos)} chequeos ejecutados correctos"
    if omitidos:
        resumen_txt += f" ({len(omitidos)} omitidos en host; se verifican en Docker)"
    print(resumen_txt)
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
