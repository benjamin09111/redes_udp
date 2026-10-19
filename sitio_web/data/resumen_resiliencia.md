# resumen_resiliencia.json

Resumen cuantitativo comparativo de la resiliencia del conjunto de $k$ rutas ($k=2$) para las 8 estaciones SINCA de la red.

- **Generado por:** `ruteo/ruteo_resiliente.py`
- **Métrica:** Confiabilidad estocástica exacta $R = S(E_C) \cdot [1 - (1 - S(E_1))(1 - S(E_2))]$

## Campos principales
| Campo | Tipo | Significado |
|---|---|---|
| `generado` | string ISO 8601 | Fecha y hora UTC del cálculo |
| `paper` | string | Cita bibliográfica (Kosior et al., 2024, Applied Sciences 14(24), 12065) |
| `algoritmo` | string | Nombre formal del algoritmo (Akgün et al., 2000 / GPP Kosior et al., 2024) |
| `metrica` | string | Formulación matemática de confiabilidad exacta de dos rutas |
| `destinos` | object | Diccionario indexado por código de estación SINCA |

## Objeto `destinos.<codigo>`
| Campo | Tipo | Significado |
|---|---|---|
| `nombre` | string | Nombre de la estación SINCA |
| `dijkstra` | object | Métricas del conjunto de $k=2$ rutas Dijkstra (peor caso) |
| `resiliente` | object | Métricas del conjunto de $k=2$ rutas resilientes adaptativas |
| `delta_resiliencia_pp` | number | Diferencial neto de resiliencia ($\Delta \mathcal{R}$ en puntos porcentuales) |

### Estructura de `dijkstra` y `resiliente`
| Campo | Tipo | Significado |
|---|---|---|
| `longitud_k1_m` | number | Distancia de la ruta primaria $k=1$ en metros |
| `longitud_k2_m` | number | Distancia de la ruta de contingencia $k=2$ en metros |
| `supervivencia_k1_pct` | number | Probabilidad de supervivencia de la ruta $k=1$ ($S(\Pi_1)$ en %) |
| `supervivencia_k2_pct` | number | Probabilidad de supervivencia de la ruta $k=2$ ($S(\Pi_2)$ en %) |
| `diversidad_pct` | number | Diversidad espacial de aristas (distancia de Jaccard en %) |
| `resiliencia_conjunto_pct` | number | Resiliencia conjunta del par de rutas ($\mathcal{R}(K)$ en %) |
| `amenazas` | array[string] | Amenazas activas que intersectan la ruta primaria |
