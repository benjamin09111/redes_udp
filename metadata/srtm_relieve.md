# srtm_relieve.geojson

Perfil del relieve bajo cada arista. Permite fijar la altitud segura de vuelo (DAN 151: máximo
120 m sobre el suelo), detectar cerros que obstruyen un corredor y estimar el gasto energético de
ascenso para la EEE.

- **Generado por:** `srtm_relieve.py`
- **Fuente (API):** NASA SRTM GL1 (resolución 30 m) vía OpenTopoData:
  `https://api.opentopodata.org/v1/srtm30m` (pública, máx. 100 puntos por consulta y 1 consulta/s)
- **Requiere:** `infraestructura/aristas.geojson`
- **Tabla destino:** `meta_edge_terrain` (una fila por arista)

## Transformación
- Cada arista se muestrea cada 100 m (`parametros.espaciado_muestras_m`) incluyendo sus extremos.
- Se consulta la elevación del terreno de todos los puntos únicos en lotes de 100.
- Los puntos sobre el mar (SRTM sin dato) se toman como 0 m.
- Se resume el perfil de cada arista (ver tabla).

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.espaciado_muestras_m` | number | Distancia entre muestras |
| `parametros.puntos_consultados` | int | Puntos únicos consultados a la API |
| `total` | int | Cantidad de aristas |

## `features[]`
**Geometría:** `LineString` (la misma de la arista).

| Propiedad | Tipo | Significado |
|---|---|---|
| `edge_id` | int | `id` de la arista en `aristas.geojson` |
| `source_code`, `target_code` | string | Nodos extremos de la arista |
| `samples` | int | Cantidad de puntos muestreados |
| `terrain_min_m` | number | Elevación mínima del terreno (m s.n.m.) |
| `terrain_max_m` | number | Elevación máxima del terreno (m s.n.m.): la altitud de vuelo debe superarla |
| `terrain_mean_m` | number | Elevación media |
| `relief_m` | number | Desnivel = máx − mín |
| `ascent_m` | number | Ascenso acumulado recorriendo la arista de `source` a `target` |
| `descent_m` | number | Descenso acumulado en el mismo sentido (en sentido inverso se intercambian) |
| `profile_m` | number[] | Elevación de cada muestra, en orden desde `source` |
