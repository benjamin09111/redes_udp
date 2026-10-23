# osm_obstaculos.geojson

Obstáculos verticales físicos y tendido eléctrico de alta tensión en la Bahía de Quintero y el Complejo Industrial de Ventanas. Modela el **riesgo en el aire** frente a colisiones físicas e interferencia electromagnética severa para operaciones de UAV entre 0 y 120 m AGL según la normativa DAN 151 de la DGAC.

- **Generado por:** `osm_obstaculos.py`
- **Fuente (API):** OpenStreetMap vía Overpass API (`https://overpass-api.de/api/interpreter`) e Infraestructura Crítica de Ventanas.
- **Tabla destino:** `meta_obstacle`

## Por qué es fundamental esta metadata
En la franja operativa de vuelo del UAV ($0$ a $120\text{ m}$ sobre el terreno):
1. **Chimeneas industriales:** En el cordón de Ventanas existen chimeneas de fundición y termoeléctricas que alcanzan entre $50\text{ m}$ y $152\text{ m}$ de altura, penetrando y superando el techo legal de vuelo. Constituyen obstáculos físicos no franqueables y fuentes de cizalladura térmica.
2. **Líneas y torres de alta tensión:** Las líneas de transmisión de $110\text{ kV}$ y $220\text{ kV}$ que evacúan energía desde la Subestación Ventanas hacia San Pedro y Quintero imponen un doble riesgo: impacto mecánico con cables tensores y desorientación del compás magnético del dron por campos electromagnéticos intensos.

## Transformación y Reglas de Bloqueo / Penalización
- Las aristas cuyos corredores aéreos intersectan el radio de seguridad (`buffer_radius_m`) de obstáculos con cota superior a la altura de crucero se consideran de **restricción dura** (`operational_action` = `'bloquear'`).
- Los obstáculos de menor altura o mástiles periféricos aplican penalizaciones de costo en la trayectoria (`operational_action` = `'penalizar'`).
- Para elementos que carecen del tag explícito `height` en OSM, se asigna una altura técnica conservadora por defecto (`height_estimated` = `true`).

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente` | string | Origen de los datos (OpenStreetMap Overpass / Infraestructura) |
| `generado` | string ISO 8601 | Fecha y hora UTC de la extracción |
| `parametros.bbox_consulta` | number[4] | Bounding box consultada `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.franja_vuelo_agl_m` | number[2] | Rango altimétrico normativo `[0, 120]` |
| `parametros.normativa` | string | Marco regulatorio aplicable (DAN 151 DGAC) |
| `total` | int | Cantidad de obstáculos identificados |

## `features[]`
**Geometría:** `Point` (chimeneas, torres, mástiles) o `LineString` (trazas de líneas de alta tensión).

| Propiedad | Tipo | Significado |
|---|---|---|
| `osm_id` | string | Identificador único en OpenStreetMap |
| `name` | string | Denominación de la estructura o tendido |
| `obstacle_type` | string | Tipo de obstáculo (`chimney`, `power_line`, `power_tower`, `mast`) |
| `height_m` | number | Altura física de la estructura en metros |
| `height_estimated` | bool | Indica si la altura fue estimada por omisión en OSM |
| `buffer_radius_m` | number | Radio de seguridad en metros |
| `voltage_kv` | number / null | Nivel de tensión eléctrica en kV (para líneas de poder) |
| `operational_action` | string | Acción recomendada (`bloquear` o `penalizar`) |
| `lon` | number | Longitud representativa WGS84 |
| `lat` | number | Latitud representativa WGS84 |
