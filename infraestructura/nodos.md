# nodos.geojson

Vértices de la red aérea: puntos de origen (base), destinos de muestreo (estaciones SINCA, fuentes
emisoras) y puntos de paso (salud, educación, comercio, playas, etc.).

- **Generado por:** `extraer_infraestructura.py`
- **Fuente:** `public/data/nodes.geojson`, dataset maestro construido en la fase 1 con Overpass/OSM,
  SINCA, BCN y Open-Elevation (scripts en `scripts/`) y curado manualmente.
- **Formato:** GeoJSON `FeatureCollection` (RFC 7946, WGS84 / EPSG:4326). Se abre directo en QGIS.
- **Tabla destino:** `infra_node`

## Bloque `etl` (raíz del archivo)
| Campo | Tipo | Significado |
|---|---|---|
| `fuente` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución del ETL |
| `parametros` | object | Parámetros usados en la extracción (vacío aquí) |
| `total` | int | Cantidad de features |

## `features[]`
**Geometría:** `Point` `[longitud, latitud]`.

| Propiedad | Tipo | Significado |
|---|---|---|
| `id` | int | Identificador numérico del vértice (lo usa pgRouting) |
| `code` | string | Identificador textual estable del nodo (ej. `base_scer`, `sinca_ventanas`) |
| `name` | string | Nombre del lugar |
| `category` | string | `base`, `sinca`, `emission_source`, `health`, `education`, `commercial`, `crowded_area`, `beach`, `hospitality`, `restaurant`, `attraction`, `historic`, `auxiliary_hub` |
| `type` | string | Subtipo dentro de la categoría |
| `role` | string | Rol del nodo en la misión |
| `priority` | int | Prioridad de monitoreo (0 = base) |
| `city` | string | Localidad |
| `elevation_msnm` | number / null | Elevación del terreno en metros sobre el nivel del mar |
| `pollutants` | string[] | Contaminantes medidos (SINCA) o emitidos (fuentes industriales); `[]` si no aplica |

> `id` depende del orden del dataset maestro: si se agregan o quitan nodos, los `id` cambian.
> Para referencias estables entre archivos se usa `code`.
