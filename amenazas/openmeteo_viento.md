# openmeteo_viento.geojson

Viento y ráfagas actuales sobre una grilla de 4 × 4 celdas que cubre el área de estudio. Si las
ráfagas superan el límite del dron, las aristas que cruzan esa celda se inhabilitan.

- **Generado por:** `openmeteo_viento.py`
- **Fuente (API):** Open-Meteo Forecast API: `https://api.open-meteo.com/v1/forecast` (sin clave)
- **Tabla destino:** `threat_event` (`event_type = 'viento'`)

## Por qué Open-Meteo y no DMC/Windy
La API de la DMC exige registro y token, y la API de pronóstico de Windy es de pago. Open-Meteo es
abierta y además entrega viento a 80 y 120 m, que corresponde al techo de vuelo de la DAN 151.

## Transformación
- El área de estudio (`parametros.aoi`) se divide en 4 × 4 celdas rectangulares (~4 × 3,6 km).
- Una sola consulta pide las condiciones actuales en el centro de las 16 celdas.
- `exceeds = true` si la ráfaga a 10 m o el viento a 120 m superan 14 m/s (umbral No-Go definido en
  `.agents/rules/geo_and_apis.md`).

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.aoi` | number[4] | Área de estudio `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.grilla` | string | Tamaño de la grilla |
| `parametros.umbral_rafaga_ms` | number | Umbral de bloqueo |
| `total` | int | Cantidad de celdas (16) |

## `features[]`
**Geometría:** `Polygon` (celda de la grilla).

Propiedades comunes a todos los archivos de amenazas:

| Propiedad | Tipo | Significado |
|---|---|---|
| `external_id` | string | `<celda>_<hora>` |
| `event_type` | string | `viento` |
| `value` | number | Ráfaga a 10 m |
| `unit` | string | `m/s (ráfaga 10 m)` |
| `threshold` | number | 14 m/s |
| `exceeds` | bool | `true` = zona activa; la fase 3 bloquea las aristas que cruzan la celda |
| `observed_at` | string ISO 8601 | Hora de las condiciones actuales (UTC, intervalos de 15 min) |
| `lon`, `lat` | number | Centro de la celda (punto consultado) |

Propiedades propias:

| Propiedad | Tipo | Significado |
|---|---|---|
| `cell` | string | Celda `r<fila>c<columna>` (fila 0 = sur, columna 0 = oeste) |
| `wind_speed_10m` | number | Viento medio a 10 m (m/s) |
| `wind_direction_10m` | number | Dirección de procedencia a 10 m (grados, 0 = norte) |
| `wind_speed_80m` | number | Viento medio a 80 m (m/s) |
| `wind_speed_120m` | number | Viento medio a 120 m (m/s), techo DAN 151 |
| `wind_direction_120m` | number | Dirección de procedencia a 120 m (grados) |
