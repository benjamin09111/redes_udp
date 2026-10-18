# csn_sismos.geojson

Sismos de los últimos 30 días en un radio de ~330 km del área de estudio. Un sismo fuerte cerca de
un nodo base lo deja inaccesible (falla de energía en la estación de recarga) y obliga a recalcular
la ruta hacia otra base.

- **Generado por:** `csn_sismos.py`
- **Fuente (API):** EMSC FDSN Event Service: `https://www.seismicportal.eu/fdsnws/event/1/query`.
  El Centro Sismológico Nacional (CSN, U. de Chile) no publica una API JSON oficial; sus eventos se
  distribuyen por EMSC y se identifican con `authority = "CSN"`.
- **Tabla destino:** `threat_event` (`event_type = 'sismo'`)

## Transformación
- Se calcula la distancia del epicentro a la base (Aeródromo de Quintero).
- Se estima un radio de afectación `R_km = 10^(0.5·M − 1.8)` (M5 ≈ 5 km, M6 ≈ 16 km,
  M7 ≈ 50 km, M8 ≈ 160 km). Es una **heurística** de la zona con intensidad ≥ VI, a calibrar en la fase 3.
- Se genera el polígono circular de afectación.
- `exceeds = true` si `M ≥ 5.0` (zona activa, igual que en las demás amenazas).
- `base_dentro_radio` indica si el Aeródromo de Quintero cae dentro del polígono. La regla del informe
  (un nodo base dentro del radio queda sin energía de recarga) se aplica en la fase 3, no en este archivo.

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.dias` | int | Ventana de tiempo consultada |
| `parametros.radio_busqueda_grados` | number | Radio de búsqueda alrededor de la base |
| `parametros.magnitud_min` | number | Magnitud mínima consultada |
| `parametros.umbral_magnitud` | number | Magnitud desde la que un sismo puede dejar caído un nodo |
| `total` | int | Cantidad de sismos |

## `features[]`
**Geometría:** `Polygon` (círculo de afectación centrado en el epicentro).

Propiedades comunes a todos los archivos de amenazas:

| Propiedad | Tipo | Significado |
|---|---|---|
| `external_id` | string | Identificador único EMSC del evento (`unid`) |
| `event_type` | string | `sismo` |
| `value` | number | Magnitud |
| `unit` | string | `magnitud (<tipo>)`: `ml` local, `mw` momento, `mb` ondas de cuerpo |
| `threshold` | number | Umbral de magnitud (5.0) |
| `exceeds` | bool | `true` = zona activa (M ≥ 5) |
| `observed_at` | string ISO 8601 | Hora de origen del sismo (UTC) |
| `lon`, `lat` | number | Epicentro |

Propiedades propias:

| Propiedad | Tipo | Significado |
|---|---|---|
| `depth_km` | number | Profundidad del hipocentro |
| `region` | string | Región Flinn-Engdahl (ej. `VALPARAISO, CHILE`) |
| `authority` | string | Agencia autora del cálculo (`CSN` = Centro Sismológico Nacional) |
| `affect_radius_km` | number | Radio de afectación estimado |
| `distance_to_base_km` | number | Distancia del epicentro al Aeródromo de Quintero |
| `base_dentro_radio` | bool | `true` si el Aeródromo de Quintero está dentro del polígono de afectación |
