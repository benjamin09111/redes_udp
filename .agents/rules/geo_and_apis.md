# Estándar Geoespacial, Datasets y Especificaciones de APIs

Este documento detalla la estructura de datos geoespaciales, la compatibilidad con QGIS y la integración de servicios de datos en tiempo real.

---

## 1. Datasets GeoJSON (`public/data/`)

Todos los archivos espaciales siguen la especificación **RFC 7946 GeoJSON** en coordenadas **WGS84** (`[longitud, latitud, altitud_msnm]`).

### 1.1. `public/data/nodes.geojson` (Nodos de la Red)
Contiene la totalidad de los puntos de interés de la red clasificados por categorías:

- **Propiedades de cada nodo (`feature.properties`)**:
  - `id` (string): Identificador único (ej. `node_base_aerodromo_quintero`, `node_sinca_puchuncavi`, `ind_codelco_ventanas`).
  - `name` (string): Nombre formal descriptivo.
  - `category` (string): Categoría temática del nodo:
    - `base`: Base principal de operaciones y RTH (Aeródromo de Quintero).
    - `sinca`: Estaciones oficiales de monitoreo de calidad del aire del SINCA (9 estaciones).
    - `emission_source`: Fuentes emisoras industriales (Codelco, AES Gener, Oxiquim, Enap, GNL, etc.).
    - `health`: Hospitales, CESFAM, postas rurales y centros de atención médica.
    - `education`: Colegios, escuelas, jardines infantiles y liceos.
    - `commercial`: Supermercados, farmacias y centros de abastecimiento.
    - `crowded_area`: Plazas públicas, parques, estadios y ferias.
    - `beach`: Playas y balnearios costeros.
    - `hospitality`: Hoteles, cabañas y complejos turísticos.
    - `restaurant`: Restaurantes y caletas gastronómicas.
    - `attraction`: Miradores, humedales y sitios de interés turístico.
    - `historic`: Monumentos y sitios históricos patrimoniales.
    - `auxiliary_hub`: Puntos de recarga de batería y pads de emergencia.
  - `city` (string): Localidad administrativa (ej. Quintero, Ventanas, Puchuncaví, Loncura, Maitencillo, etc.).
  - `icon` (string): Emoji representativo para la interfaz.
  - `priority` (number): Nivel de prioridad para misiones de muestreo o inspección (1 a 10).
  - `sensors` (array de strings): Sensores requeridos o disponibles (ej. `["SO2", "PM2.5", "PM10", "COV", "Meteo"]`).

- **Geometría**:
  - `Point`: `[longitud, latitud, altitud_msnm]` (ej. `[-71.5284, -32.7845, 12]`).

### 1.2. `public/data/urban_zones.geojson` (Polígonos Urbanos y Zonas de Amortiguamiento)
- Polígonos de límites urbanos de las 13 localidades principales de la bahía (Quintero, Loncura, Ventanas, Puchuncaví, Maitencillo, Campiche, Las Ventanas, Horcón, etc.).
- Utilizado para calcular densidades poblacionales, evaluar restricciones de sobrevuelo normativo (DAN 151) y penalizar aristas del grafo que crucen zonas densamente pobladas.

---

## 2. Compatibilidad con QGIS Desktop
1. Cualquier archivo `.geojson` en `public/data/` puede ser arrastrado directamente a una sesión de **QGIS 3.x**.
2. El sistema de referencia de coordenadas (CRS) es `EPSG:4326` (WGS 84).
3. Las geometrías respetan topologías cerradas y atributos legibles en la tabla de atributos de QGIS.

---

## 3. Conectores de APIs Externas

### 3.1. Open-Meteo API (Meteorología en Tiempo Real)
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Parámetros requeridos**:
  - `latitude`, `longitude` (coordenadas de la Bahía: `-32.7550`, `-71.4550`).
  - `current`: `temperature_2m`, `relative_humidity_2m`, `precipitation`, `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`.
  - `hourly`: perfiles de viento por altitud (si está disponible) para análisis de pluma.
- **Uso en el simulador**:
  - Descomponer velocidad y dirección en vector cartesiano $\vec{w} = (w_x, w_y)$.
  - Si `precipitation > 2.0 mm/h` o `wind_gusts_10m > 14 m/s`, declarar condición **No-Go** (veto de despegue por seguridad de vuelo).
  - Alimentar el cálculo de $EEE$ y la estrategia de sotavento para el RTH.

### 3.2. SINCA API (Calidad del Aire)
- Monitoreo de las 9 estaciones de la zona (Quintero, Puchuncaví, Los Maitenes, La Greda, Ventanas, etc.).
- Concentraciones de $\text{SO}_2$ ($\mu\text{g/m}^3$) y $\text{MP}_{2.5}$ en tiempo real.
- Ante superación de umbrales PPDA (Alerta, Preemergencia, Emergencia), incrementar la prioridad de los nodos y aristas colindantes para despacho inmediato del dron.
