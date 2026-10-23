"""Pipeline completo del proyecto (fase 2): descarga -> transformación -> carga en BD -> ruteo -> sitio.

Cada paso corre dentro de un contenedor Docker (ver docker-compose.yml y Dockerfile).
Requiere Docker y conexión a internet (las APIs se consultan en vivo).

Uso:
    python3 main.py                  # pipeline completo, BD desde cero
    python3 main.py --sin-descarga   # usa los .geojson ya generados (BD, ruteo y sitio)
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
URL_SITIO = "http://localhost:8000/sitio_web/"

# 1) Extracción y transformación: cada script produce un .geojson
DESCARGA = [
    ("Infraestructura: nodos, aristas y zonas urbanas", "infraestructura/extraer_infraestructura.py"),
    ("Metadata: calidad del aire (SINCA)", "metadata/sinca_calidad_aire.py"),
    ("Metadata: relieve SRTM por arista", "metadata/srtm_relieve.py"),
    ("Metadata: manzanas censales (INE)", "metadata/ine_manzanas.py"),
    ("Metadata: antenas y cobertura (OSM)", "metadata/osm_antenas.py"),
    ("Amenaza: incendios (NASA FIRMS)", "amenazas/firms_incendios.py"),
    ("Amenaza: tráfico aéreo tripulado (OpenSky)", "amenazas/opensky_aeronaves.py"),
    ("Amenaza: viento (Open-Meteo)", "amenazas/openmeteo_viento.py"),
    ("Amenaza: niebla costera (Open-Meteo)", "amenazas/openmeteo_niebla.py"),
]

# 2) Carga: cada .geojson a su tabla (el orden respeta las llaves foráneas)
CARGA = [
    ("Nodos", "infraestructura/cargar_nodos.py"),
    ("Aristas", "infraestructura/cargar_aristas.py"),
    ("Zonas urbanas", "infraestructura/cargar_zonas_urbanas.py"),
    ("Calidad del aire (SINCA)", "metadata/cargar_sinca_calidad_aire.py"),
    ("Relieve por arista (SRTM)", "metadata/cargar_srtm_relieve.py"),
    ("Manzanas (INE)", "metadata/cargar_ine_manzanas.py"),
    ("Antenas (OSM)", "metadata/cargar_osm_antenas.py"),
    ("Incendios", "amenazas/cargar_firms_incendios.py"),
    ("Tráfico aéreo (OpenSky)", "amenazas/cargar_opensky_aeronaves.py"),
    ("Viento", "amenazas/cargar_openmeteo_viento.py"),
    ("Niebla costera (Open-Meteo)", "amenazas/cargar_openmeteo_niebla.py"),
]

# 3) Ruteo base con pgr_dijkstra -> sitio_web/data/ruta_dijkstra.geojson
RUTEO = "ruteo/ruta_dijkstra.py"
RUTEO_RESILIENTE = "ruteo/ruteo_resiliente.py"

RESUMEN_SQL = """
SELECT 'infra_node' AS tabla, count(*) FROM infra_node
UNION ALL SELECT 'infra_edge', count(*) FROM infra_edge
UNION ALL SELECT 'urban_zone', count(*) FROM urban_zone
UNION ALL SELECT 'meta_air_quality', count(*) FROM meta_air_quality
UNION ALL SELECT 'meta_edge_terrain', count(*) FROM meta_edge_terrain
UNION ALL SELECT 'meta_census_block', count(*) FROM meta_census_block
UNION ALL SELECT 'meta_telecom_antenna', count(*) FROM meta_telecom_antenna
UNION ALL SELECT 'threat_event', count(*) FROM threat_event
"""


def paso(titulo):
    print(f"\n== {titulo}", flush=True)


def compose(*args, entrada=None):
    subprocess.run(["docker", "compose", *args], cwd=RAIZ, check=True, stdin=entrada)


def en_etl(script):
    compose("run", "--rm", "etl", "python", script)


def esperar_bd(segundos=90):
    limite = time.time() + segundos
    while time.time() < limite:
        r = subprocess.run(["docker", "compose", "exec", "-T", "db", "pg_isready", "-U", "uav", "-d", "uav"],
                           cwd=RAIZ, capture_output=True)
        if r.returncode == 0:
            return
        time.sleep(2)
    raise RuntimeError("La base de datos no respondió a tiempo")


def reiniciar_bd():
    """Borra y vuelve a crear todas las tablas con bd/schema.sql."""
    with open(RAIZ / "bd" / "schema.sql", "rb") as f:
        compose("exec", "-T", "db", "psql", "-U", "uav", "-d", "uav",
                "-v", "ON_ERROR_STOP=1", "-q", entrada=f)


def main():
    parser = argparse.ArgumentParser(description="Pipeline de la fase 2 (todo en Docker).")
    parser.add_argument("--sin-descarga", action="store_true",
                        help="no consulta las APIs; usa los .geojson ya generados")
    args = parser.parse_args()

    try:
        if not args.sin_descarga:
            paso("Docker: construir la imagen del ETL")
            compose("build", "etl")

        paso("Base de datos: PostgreSQL 16 + PostGIS + pgRouting")
        compose("up", "-d", "db")
        esperar_bd()

        if not args.sin_descarga:
            for titulo, script in DESCARGA:
                paso(f"Extracción y transformación · {titulo}")
                en_etl(script)

        paso("Base de datos: crear el esquema desde cero (bd/schema.sql)")
        reiniciar_bd()

        for titulo, script in CARGA:
            paso(f"Carga a la BD · {titulo}")
            en_etl(script)

        paso("Ruteo base: pgr_dijkstra desde la base hacia cada estación SINCA (costo = longitud)")
        en_etl(RUTEO)

        paso("Ruteo resiliente multiobjetivo: penalización iterativa Akgün et al. (2000) (k >= 2)")
        en_etl(RUTEO_RESILIENTE)

        paso("Sitio web (Leaflet)")
        compose("up", "-d", "web")

        paso("Conteos en la BD")
        compose("exec", "-T", "db", "psql", "-U", "uav", "-d", "uav", "-c", RESUMEN_SQL)
    except subprocess.CalledProcessError as e:
        print(f"\nFALLÓ el paso: {' '.join(map(str, e.cmd))} (código {e.returncode})", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nListo. Abre el sitio en: {URL_SITIO}")


if __name__ == "__main__":
    main()
