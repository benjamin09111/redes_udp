# metno_lluvia.geojson

Precipitación prevista para la próxima hora sobre la misma grilla de 4 × 4 celdas del viento. Si la
lluvia supera el umbral operacional, las aristas de esa celda se inhabilitan (riesgo electrónico y
mediciones del sensor alteradas) y el dron activa el retorno de emergencia (LPP).

- **Generado por:** `metno_lluvia.py`
- **Fuente (API):** MET Norway Locationforecast 2.0:
  `https://api.met.no/weatherapi/locationforecast/2.0/compact` (sin clave; exige un User-Agent identificable)
- **Tabla destino:** `threat_event` (`event_type = 'lluvia'`)

## Por qué MET Norway y no JAXA GSMaP / RainViewer
GSMaP exige una cuenta FTP y RainViewer solo entrega teselas de radar en imagen PNG, sin valores
numéricos de lluvia. MET Norway entrega la precipitación en mm por punto, es gratuita y cubre Chile.
Se usa un proveedor distinto al del viento para que las cuatro amenazas provengan de fuentes distintas.

## Transformación
- Grilla de 4 × 4 celdas sobre el área de estudio; una consulta por celda (en el centro).
- Se toma `next_1_hours.precipitation_amount` del primer paso del pronóstico.
- `exceeds = true` si supera 2 mm/h (umbral No-Go definido en `.agents/rules/geo_and_apis.md`).

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.aoi` | number[4] | Área de estudio `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.grilla` | string | Tamaño de la grilla |
| `parametros.umbral_mm_h` | number | Umbral de bloqueo |
| `total` | int | Cantidad de celdas (16) |

## `features[]`
**Geometría:** `Polygon` (celda de la grilla).

Propiedades comunes a todos los archivos de amenazas:

| Propiedad | Tipo | Significado |
|---|---|---|
| `external_id` | string | `<celda>_<hora>` |
| `event_type` | string | `lluvia` |
| `value` | number | Precipitación prevista para la próxima hora |
| `unit` | string | `mm/h` |
| `threshold` | number | 2.0 mm/h |
| `exceeds` | bool | `true` = zona activa; la fase 3 bloquea las aristas que cruzan la celda |
| `observed_at` | string ISO 8601 | Inicio de la hora pronosticada (UTC) |
| `valid_until` | string ISO 8601 | Fin de la hora pronosticada |
| `lon`, `lat` | number | Centro de la celda (punto consultado) |

Propiedades propias:

| Propiedad | Tipo | Significado |
|---|---|---|
| `cell` | string | Celda `r<fila>c<columna>` (fila 0 = sur, columna 0 = oeste) |
| `symbol_code` | string | Condición prevista (`clearsky_day`, `cloudy`, `rain`, ...) |
| `model_updated_at` | string ISO 8601 | Hora de actualización del modelo de MET Norway |
