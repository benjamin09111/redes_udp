# aristas.geojson

Corredores aéreos ("calles aéreas") entre nodos. Es el grafo sobre el que corre `pgr_dijkstra`.

- **Generado por:** `extraer_infraestructura.py` a partir de `nodos.geojson`
- **Formato:** GeoJSON `FeatureCollection` (RFC 7946, WGS84 / EPSG:4326)
- **Tabla destino:** `infra_edge`

## Cómo se generan
1. Cada nodo se une con sus **K vecinos más cercanos** (K = 4 por defecto, configurable:
   `python infraestructura/extraer_infraestructura.py 6`).
2. Si quedan componentes desconectados, se unen por el par de nodos más cercano entre ellos
   (union-find), de modo que el grafo es **conexo**: existe ruta entre cualquier par de nodos.
3. El costo de cada arista es su **longitud en metros** (fórmula de haversine). En la fase 3 este
   costo se ponderará con la metadata y las amenazas.

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.k_vecinos` | int | K usado |
| `parametros.aristas_puente` | int | Aristas agregadas para conectar componentes |
| `total` | int | Cantidad de aristas |

## `features[]`
**Geometría:** `LineString` `[[lon, lat] origen, [lon, lat] destino]`.

| Propiedad | Tipo | Significado |
|---|---|---|
| `id` | int | Identificador de la arista |
| `source`, `target` | int | `id` de los nodos que conecta (ver `nodos.geojson`) |
| `source_code`, `target_code` | string | `code` de los mismos nodos (referencia estable) |
| `length_m` | number | Longitud en metros |
| `cost` | number | Costo de ir `source` → `target` (fase 2: = `length_m`) |
| `reverse_cost` | number | Costo de ir `target` → `source` (arista bidireccional: = `cost`) |
