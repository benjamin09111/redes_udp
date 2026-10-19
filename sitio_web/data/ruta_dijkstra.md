# ruta_dijkstra.geojson

Rutas de referencia (peor caso) calculadas con `pgr_dijkstra` en PostgreSQL/pgRouting desde la base hacia las estaciones SINCA.

- **Generado por:** `ruteo/ruta_dijkstra.py`
- **Formato:** GeoJSON `FeatureCollection` (RFC 7946, WGS84 / EPSG:4326)
- **Función en BD:** `pgr_dijkstra` sobre `infra_edge` con costo = `length_m`

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente` | string | Origen de los datos (pgRouting `pgr_dijkstra`) |
| `generado` | string ISO 8601 | Fecha y hora UTC del cálculo |
| `parametros.origen` | string | Código del nodo de despacho (`base_scer`) |
| `parametros.costo` | string | Atributo de costo utilizado (`length_m`) |
| `parametros.k_rutas` | int | Cantidad de alternativas calculadas ($k=2$) |
| `parametros.factor_penalizacion_k2` | number | Factor que multiplica el costo de las aristas de $k=1$ al calcular $k=2$ (4.0) |
| `parametros.considera_metadata_y_amenazas` | boolean | `false` (ruta de peor caso) |
| `total` | int | Total de features (2 por estación SINCA: $k=1$ y $k=2$) |

## `features[]`
Un feature por ruta: $k=1$ (camino más corto) y $k=2$ (alternativa obtenida con `pgr_dijkstra`
penalizando ×4 las aristas de $k=1$).

**Geometría:** `LineString` con los vértices de la ruta.

| Propiedad | Tipo | Significado |
|---|---|---|
| `origen` | string | Código del nodo origen (`base_scer`) |
| `destino` | string | Código del nodo destino SINCA |
| `destino_nombre` | string | Nombre de la estación SINCA (con sufijo "(k=2)" en la alternativa) |
| `tramos` | int | Número de aristas de la ruta |
| `nodos` | int | Número de vértices de la ruta |
| `longitud_m` | number | Distancia física total de la ruta en metros |
| `costo` | number | Costo acumulado en pgRouting. En $k=1$ es igual a `longitud_m`; en $k=2$ incluye la penalización |
| `k` | int | Orden de la ruta (1 = más corta, 2 = alternativa) |
