"""Carga metadata/osm_obstaculos.geojson en la base de datos (meta_obstacle)."""
import json

from bd.conexion import ejecutar, leer_geojson, registrar_fuente

ARCHIVO = "metadata/osm_obstaculos.geojson"


def cargar(cur):
    fc = leer_geojson(ARCHIVO)
    source_id = registrar_fuente(cur, "osm_obstaculos", "metadata", "api", fc)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS meta_obstacle (
            id serial PRIMARY KEY,
            source_id integer NOT NULL REFERENCES data_source (id),
            osm_id varchar NOT NULL UNIQUE,
            name varchar,
            obstacle_type varchar NOT NULL,
            height_m real,
            height_estimated boolean,
            buffer_radius_m real NOT NULL,
            voltage_kv real,
            operational_action varchar NOT NULL,
            geom geometry(Geometry, 4326) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS meta_obstacle_geom_idx ON meta_obstacle USING gist (geom);
        DELETE FROM meta_obstacle WHERE source_id = %s;
        """,
        (source_id,),
    )
    for f in fc["features"]:
        p = f["properties"]
        cur.execute(
            """
            INSERT INTO meta_obstacle (
                source_id, osm_id, name, obstacle_type, height_m, height_estimated,
                buffer_radius_m, voltage_kv, operational_action, geom
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
            ON CONFLICT (osm_id) DO UPDATE SET
                height_m = EXCLUDED.height_m,
                operational_action = EXCLUDED.operational_action;
            """,
            (
                source_id,
                p["osm_id"],
                p["name"],
                p["obstacle_type"],
                p["height_m"],
                p["height_estimated"],
                p["buffer_radius_m"],
                p["voltage_kv"],
                p["operational_action"],
                json.dumps(f["geometry"]),
            ),
        )
    return len(fc["features"])


if __name__ == "__main__":
    ejecutar("meta_obstacle", cargar)
