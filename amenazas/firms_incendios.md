# firms_incendios.geojson

Focos de incendio activos detectados por satélite en los últimos 7 días. Un incendio que coincide
con una arista la bloquea por humo, calor y turbulencia térmica.

- **Generado por:** `firms_incendios.py`
- **Fuente (API / archivos NRT):** NASA FIRMS, archivos públicos para Sudamérica de VIIRS S-NPP,
  VIIRS NOAA-20 y MODIS: `https://firms.modaps.eosdis.nasa.gov/data/active_fire/`
- **Tabla destino:** `threat_event` (`event_type = 'incendio'`)

## Transformación
- Se filtran los focos dentro del área de estudio ampliada en ~30 km (`parametros.bbox_region`).
- Cada foco se convierte en un polígono circular de exclusión de 2 km (supuesto: radio de humo y
  turbulencia que impide el vuelo).
- `exceeds = true` cuando la confianza de detección es nominal o alta (VIIRS `n`/`h`, MODIS ≥ 50 %).
  Las detecciones de baja confianza se conservan, pero no bloquean.

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.bbox_region` | number[4] | Caja filtrada `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.radio_exclusion_m` | number | Radio del polígono de exclusión |
| `total` | int | Cantidad de focos (puede ser 0 si no hay incendios) |

## `features[]`
**Geometría:** `Polygon` (zona de exclusión alrededor del foco).

Propiedades comunes a todos los archivos de amenazas:

| Propiedad | Tipo | Significado |
|---|---|---|
| `external_id` | string | Identificador único: instrumento, fecha, hora y coordenadas |
| `event_type` | string | `incendio` |
| `value` | number | Potencia radiativa del fuego (FRP) |
| `unit` | string | `MW (FRP)` |
| `threshold` | null | No aplica: toda detección confiable bloquea |
| `exceeds` | bool | `true` = zona activa; la fase 3 bloquea los nodos y aristas que intersecta |
| `observed_at` | string ISO 8601 | Fecha y hora UTC de la pasada del satélite |
| `lon`, `lat` | number | Centro del píxel del foco |

Propiedades propias de FIRMS:

| Propiedad | Tipo | Significado |
|---|---|---|
| `radius_m` | number | Radio de exclusión usado |
| `instrument` | string | `VIIRS_SNPP`, `VIIRS_NOAA20` o `MODIS` |
| `satellite` | string | Código del satélite (`N` S-NPP, `N20` NOAA-20, `T` Terra, `A` Aqua) |
| `confidence` | string | Confianza de la detección (VIIRS: `low`/`nominal`/`high`; MODIS: 0 a 100) |
| `brightness_k` | number | Temperatura de brillo del píxel (K) |
| `daynight` | string | `D` día / `N` noche |
