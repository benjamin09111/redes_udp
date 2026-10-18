"""Conexión a PostgreSQL y funciones comunes de los cargadores (json -> BD).

Variables de entorno (las define docker-compose.yml):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

Los cargadores asumen una BD recién creada con bd/schema.sql (main.py lo hace siempre).
"""
import json
import os
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parent.parent

# Propiedades comunes a todas las amenazas. Lo que no está aquí va al campo jsonb `properties`.
BASE_AMENAZA = {"external_id", "event_type", "value", "unit", "threshold", "exceeds",
                "observed_at", "valid_until", "lon", "lat"}


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5433")),
        dbname=os.getenv("DB_NAME", "uav"),
        user=os.getenv("DB_USER", "uav"),
        password=os.getenv("DB_PASSWORD", "uav"),
    )


def leer_geojson(ruta):
    with open(RAIZ / ruta, encoding="utf-8") as f:
        return json.load(f)


def registrar_fuente(cur, code, layer, kind, fc):
    """Inserta (o actualiza) la fila de data_source con el bloque etl del json."""
    etl = fc["etl"]
    cur.execute(
        """
        INSERT INTO data_source (code, layer, name, url, kind, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (code) DO UPDATE
            SET name = EXCLUDED.name, url = EXCLUDED.url, fetched_at = EXCLUDED.fetched_at
        RETURNING id
        """,
        (code, layer, etl["fuente"], etl.get("url"), kind, etl.get("generado")),
    )
    return cur.fetchone()[0]


def insertar_amenazas(cur, archivo, code):
    """Carga un json de amenazas en threat_event (los cuatro comparten el mismo formato)."""
    fc = leer_geojson(archivo)
    source_id = registrar_fuente(cur, code, "amenaza", "api", fc)
    for f in fc["features"]:
        p = f["properties"]
        extra = {k: v for k, v in p.items() if k not in BASE_AMENAZA}
        cur.execute(
            """
            INSERT INTO threat_event (source_id, external_id, event_type, value, unit, threshold,
                                      exceeds, observed_at, valid_until, properties,
                                      point_geom, geom)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb,
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326),
                    ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            """,
            (source_id, p["external_id"], p["event_type"], p["value"], p["unit"], p["threshold"],
             p["exceeds"], p["observed_at"], p.get("valid_until"),
             json.dumps(extra, ensure_ascii=False), p["lon"], p["lat"],
             json.dumps(f["geometry"])),
        )
    return len(fc["features"])


def ejecutar(nombre, funcion):
    """Ejecuta la carga en una transacción: si algo falla, no queda nada a medias."""
    with conectar() as conn, conn.cursor() as cur:
        n = funcion(cur)
    print(f"  {nombre}: {n} filas cargadas")
