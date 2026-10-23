CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

DROP TABLE IF EXISTS threat_event, meta_telecom_antenna, meta_census_block, meta_edge_terrain,
                     meta_air_quality, urban_zone, infra_edge, infra_node, data_source CASCADE;

-- CATÁLOGO DE FUENTES (trazabilidad ETL)
CREATE TABLE data_source (
    id          serial PRIMARY KEY,
    code        varchar NOT NULL UNIQUE,     -- nombre del archivo json, ej. 'sinca_calidad_aire'
    layer       varchar NOT NULL CHECK (layer IN ('infraestructura', 'metadata', 'amenaza')),
    name        varchar NOT NULL,            -- etl.fuente del json
    url         text,                        -- etl.url del json
    kind        varchar NOT NULL CHECK (kind IN ('api', 'bd_geoespacial', 'dataset')),
    fetched_at  timestamptz                  -- etl.generado del json
);

-- INFRAESTRUCTURA
CREATE TABLE infra_node (                    -- infraestructura/nodos.geojson
    id              integer PRIMARY KEY,     -- id del json (vértice pgRouting)
    code            varchar NOT NULL UNIQUE, -- ej. base_scer, sinca_ventanas
    name            varchar NOT NULL,
    category        varchar NOT NULL,        -- base, sinca, emission_source, health, education, ...
    type            varchar,
    role            varchar,
    priority        smallint,
    city            varchar,
    elevation_msnm  real,
    pollutants      text[],
    geom            geometry(Point, 4326) NOT NULL
);
CREATE INDEX infra_node_geom_idx ON infra_node USING gist (geom);
CREATE INDEX infra_node_category_idx ON infra_node (category);

CREATE TABLE infra_edge (                    -- infraestructura/aristas.geojson
    id            integer PRIMARY KEY,
    source        integer NOT NULL REFERENCES infra_node (id),
    target        integer NOT NULL REFERENCES infra_node (id),
    length_m      double precision NOT NULL,
    cost          double precision NOT NULL, -- fase 2: = length_m (pgr_dijkstra)
    reverse_cost  double precision NOT NULL, -- arista bidireccional
    geom          geometry(LineString, 4326) NOT NULL,
    CHECK (source <> target)
);
CREATE INDEX infra_edge_geom_idx ON infra_edge USING gist (geom);
CREATE INDEX infra_edge_source_idx ON infra_edge (source);
CREATE INDEX infra_edge_target_idx ON infra_edge (target);

CREATE TABLE urban_zone (                    -- infraestructura/zonas_urbanas.geojson (polígonos)
    id        serial PRIMARY KEY,
    code      varchar NOT NULL UNIQUE,
    name      varchar NOT NULL,
    city      varchar,
    area_km2  real,
    geom      geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX urban_zone_geom_idx ON urban_zone USING gist (geom);

-- METADATA 
CREATE TABLE meta_air_quality (              -- metadata/sinca_calidad_aire.geojson (1 fila por medición)
    id            bigserial PRIMARY KEY,
    source_id     integer NOT NULL REFERENCES data_source (id),
    station_key   varchar NOT NULL,          -- id de estación SINCA
    station_name  varchar NOT NULL,
    commune       varchar,
    network       varchar,
    operator      varchar,
    node_id       integer REFERENCES infra_node (id),  -- nodo sinca asociado (NULL si no existe)
    pollutant     varchar NOT NULL,          -- SO2, NO2, CO, O3, PM10, PM2.5
    value         double precision NOT NULL,
    unit          varchar,
    averaging     varchar,                   -- concentración 1 h, media móvil 8 h, ...
    status        varchar,                   -- bueno, regular, alerta, ...
    status_code   smallint,
    icap          smallint,
    observed_at   timestamptz NOT NULL,
    geom          geometry(Point, 4326) NOT NULL,
    UNIQUE (station_key, pollutant, observed_at)
);
CREATE INDEX meta_air_quality_geom_idx ON meta_air_quality USING gist (geom);
CREATE INDEX meta_air_quality_node_idx ON meta_air_quality (node_id);

CREATE TABLE meta_edge_terrain (             -- metadata/srtm_relieve.geojson (1 fila por arista)
    edge_id         integer PRIMARY KEY REFERENCES infra_edge (id) ON DELETE CASCADE,
    source_id       integer NOT NULL REFERENCES data_source (id),
    samples         smallint NOT NULL,
    terrain_min_m   real NOT NULL,
    terrain_max_m   real NOT NULL,
    terrain_mean_m  real NOT NULL,
    relief_m        real NOT NULL,
    ascent_m        real NOT NULL,           -- sentido source -> target
    descent_m       real NOT NULL,
    profile_m       real[] NOT NULL          -- perfil de elevación muestreado
);

CREATE TABLE meta_census_block (             -- metadata/ine_manzanas.geojson (polígonos)
    id               serial PRIMARY KEY,
    source_id        integer NOT NULL REFERENCES data_source (id),
    manzent          varchar NOT NULL UNIQUE, -- código de manzana INE
    cut              integer,                 -- código comunal
    commune          varchar,
    district         varchar,
    persons          integer NOT NULL,
    dwellings        integer,
    area_m2          double precision,
    density_hab_km2  double precision,
    geom             geometry(MultiPolygon, 4326) NOT NULL
);
CREATE INDEX meta_census_block_geom_idx ON meta_census_block USING gist (geom);

CREATE TABLE meta_telecom_antenna (          -- metadata/osm_antenas.geojson
    id                 serial PRIMARY KEY,
    source_id          integer NOT NULL REFERENCES data_source (id),
    osm_id             varchar NOT NULL UNIQUE,
    name               varchar,
    operator           varchar,
    structure          varchar,               -- mast, tower, ...
    mobile_phone       boolean,
    height_m           real,
    coverage_radius_m  real NOT NULL,
    geom               geometry(Point, 4326) NOT NULL,     -- ubicación de la antena
    coverage_geom      geometry(Polygon, 4326) NOT NULL    -- cobertura estimada
);
CREATE INDEX meta_telecom_antenna_cov_idx ON meta_telecom_antenna USING gist (coverage_geom);

-- AMENAZAS
-- Los cuatro json de amenazas comparten las mismas propiedades base, por lo que se cargan en una
-- sola tabla. Los atributos propios de cada fuente quedan en `properties`.
-- Sin FK a nodos/aristas: la afectación se calcula espacialmente en la fase 3
--   (ST_Intersects(infra_edge.geom, threat_event.geom) AND threat_event.exceeds).
CREATE TABLE threat_event (                  -- amenazas/*.geojson
    id           bigserial PRIMARY KEY,
    source_id    integer NOT NULL REFERENCES data_source (id),
    external_id  varchar NOT NULL,
    event_type   varchar NOT NULL CHECK (event_type IN ('incendio', 'sismo', 'viento', 'lluvia')),
    value        double precision,
    unit         varchar,
    threshold    double precision,
    exceeds      boolean NOT NULL,           -- true = zona activa (la fase 3 decide qué bloquea)
    simulated    boolean NOT NULL DEFAULT false,
    observed_at  timestamptz NOT NULL,
    valid_until  timestamptz,
    properties   jsonb,
    point_geom   geometry(Point, 4326) NOT NULL,     -- foco, epicentro o centro de celda
    geom         geometry(Polygon, 4326) NOT NULL,   -- área de afectación
    UNIQUE (source_id, external_id)
);
CREATE INDEX threat_event_geom_idx ON threat_event USING gist (geom);
CREATE INDEX threat_event_type_idx ON threat_event (event_type, observed_at);

--  EJEMPLO para pgRouting (punto 8)
-- SELECT * FROM pgr_dijkstra(
--   'SELECT id, source, target, cost, reverse_cost FROM infra_edge',
--   (SELECT id FROM infra_node WHERE code = 'base_scer'),
--   (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
--   directed := true);
