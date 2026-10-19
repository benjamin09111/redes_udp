# rutas_comparativas.geojson

Rutas comparativas ($k=1$ y $k=2$) para Dijkstra y Ruteo Resiliente multiobjetivo hacia las 8 estaciones SINCA.

- **Generado por:** `ruteo/ruteo_resiliente.py`
- **Formato:** GeoJSON `FeatureCollection` (RFC 7946, WGS84 / EPSG:4326)
- **Algoritmo:** Akgün et al. (2000) K-caminos disimilares por penalización iterativa de aristas, inspirado en GPP de Kosior et al. (2024)

## Bloque `metadata`
| Campo | Tipo | Significado |
|---|---|---|
| `generado` | string ISO 8601 | Fecha y hora UTC del cálculo |
| `paper` | string | Cita bibliográfica del marco teórico (Kosior et al., 2024) |
| `algoritmo` | string | Nombre formal del algoritmo de caminos disimilares |
| `origen` | string | Nodo de origen base (`base_scer`) |
| `total_rutas` | int | Total de trayectorias generadas (32 rutas) |

## `features[]`
**Geometría:** `LineString` con la trayectoria de vuelo de cada ruta.

| Propiedad | Tipo | Significado |
|---|---|---|
| `tipo_algoritmo` | string | Clasificador (`dijkstra_k1`, `dijkstra_k2`, `resiliente_k1`, `resiliente_k2`) |
| `etiqueta` | string | Nombre descriptivo para visualización cartográfica |
| `k_orden` | int | Orden jerárquico de la ruta ($1$: primaria, $2$: alternativa/contingencia) |
| `origen` | string | Código del nodo de despacho (`base_scer`) |
| `destino` | string | Código del nodo objetivo SINCA |
| `destino_nombre` | string | Nombre de la estación destino |
| `longitud_m` | number | Distancia física de la trayectoria en metros |
| `supervivencia_pct` | number | Probabilidad de supervivencia de la ruta individual ($S(\Pi) \in [0, 100\%]$) |
| `amenazas` | array[string] | Amenazas o restricciones que cruza la trayectoria |
