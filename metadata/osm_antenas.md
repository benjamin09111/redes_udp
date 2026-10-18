# osm_antenas.geojson

Antenas de telecomunicaciones y su **cobertura estimada** (polígonos). Las aristas fuera de toda
cobertura son "sombras de telemetría": ahí aumenta el riesgo de perder el enlace con la estación
de control (GCS).

- **Generado por:** `osm_antenas.py`
- **Fuente (API):** OpenStreetMap vía Overpass API (`https://overpass-api.de/api/interpreter`,
  con un mirror de respaldo).
- **Tabla destino:** `meta_telecom_antenna`

## Por qué OSM y no Subtel
El informe proponía los mapas de cobertura de Subtel (Registro Nacional de Conectividad). Ese visor
está protegido por reCAPTCHA y no tiene una API pública, así que no se puede automatizar. Se
reemplaza por las antenas de telecomunicaciones registradas en OSM, con un radio de cobertura supuesto.

## Transformación
- Se consultan torres y mástiles de comunicación en el área de estudio más un margen de ~8 km
  (una antena fuera del área también da cobertura dentro de ella).
- Se descartan estructuras que no son de telecomunicaciones (sirenas, faros, etc.).
- Se genera un polígono circular de cobertura de 3 km por antena (supuesto: celda macro LTE en
  zona suburbana, de 1 a 5 km).

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos (mirror Overpass usado) |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.bbox_consulta` | number[4] | Caja consultada `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.radio_cobertura_m` | number | Radio de cobertura supuesto |
| `total` | int | Cantidad de antenas |

## `features[]`
**Geometría:** `Polygon` (círculo de cobertura estimada).

| Propiedad | Tipo | Significado |
|---|---|---|
| `osm_id` | string | Identificador OSM (`node/123`, `way/456`) |
| `name` | string / null | Nombre de la estructura |
| `operator` | string / null | Operador (Entel, Movistar, Claro...) si está registrado |
| `structure` | string / null | Tipo de estructura OSM (`mast`, `tower`) |
| `mobile_phone` | bool | `true` si está etiquetada como antena de telefonía móvil |
| `height_m` | number / null | Altura en metros si está registrada |
| `coverage_radius_m` | number | Radio usado para el polígono |
| `lon`, `lat` | number | Ubicación de la antena |

> Limitación: OSM no registra todas las antenas, por lo que las sombras de telemetría quedan
> sobrestimadas (supuesto conservador).
