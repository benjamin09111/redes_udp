# sinca_calidad_aire.geojson

Calidad del aire en tiempo real de las estaciones SINCA del área de estudio. Define la **prioridad de
muestreo** de los nodos: a peor calidad del aire, más atractivo es el nodo para el GPP.

- **Generado por:** `sinca_calidad_aire.py`
- **Fuente (API):** SINCA, Ministerio del Medio Ambiente. JSON público del mapa:
  `https://sinca.mma.gob.cl/index.php/json/listadomapa2k19/`
- **Requiere:** `infraestructura/nodos.geojson` (para asociar estación ↔ nodo)
- **Tabla destino:** `meta_air_quality` (una fila por estación × contaminante)

## Transformación
- Se filtran las estaciones dentro del área de estudio (`parametros.aoi`).
- Se usa el valor oficial de `tableRow` (último dato validado de cada contaminante).
- Contaminantes normalizados: `0001`→`SO2`, `0003`→`NO2`, `0004`→`CO`, `0008`→`O3`, `PM10`, `PM25`→`PM2.5`.
- Unidades sin HTML (`&micro;g&#8725;m<sup>3</sup>N` → `µg/m3N`) y fechas a ISO 8601 con zona horaria.
- Cada estación se asocia al nodo `sinca` más cercano si está a ≤ 500 m.

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.aoi` | number[4] | Área de estudio `[lon_min, lat_min, lon_max, lat_max]` |
| `parametros.radio_asociacion_nodo_m` | number | Distancia máxima para asociar estación y nodo |
| `total` | int | Cantidad de estaciones |

## `features[]`
**Geometría:** `Point` (ubicación de la estación).

| Propiedad | Tipo | Significado |
|---|---|---|
| `station_key` | string | Identificador de la estación en SINCA |
| `station_name` | string | Nombre de la estación |
| `commune` | string | Comuna |
| `network` | string | Red de monitoreo a la que pertenece |
| `operator` | string | Empresa u organismo que la opera |
| `ownership` | string | `Pública` / `Privada` |
| `node_code` | string / null | `code` del nodo asociado; `null` si la estación no tiene nodo en la red |
| `node_distance_m` | number | Distancia al nodo `sinca` más cercano |
| `worst_status` | string / null | Peor estado de calidad del aire entre sus contaminantes |
| `worst_status_code` | int / null | Código del peor estado (1 = bueno; mayor = peor) |
| `measurements[]` | object[] | Una entrada por contaminante (ver abajo) |

### `measurements` (lista)
| Campo | Tipo | Significado |
|---|---|---|
| `pollutant` | string | `SO2`, `NO2`, `CO`, `O3`, `PM10`, `PM2.5` |
| `value` | number | Concentración |
| `unit` | string | `µg/m3N`, `µg/m3`, `ppbv`, `ppmv` |
| `averaging` | string | Ventana de cálculo (`concentración 1 h`, `media móvil 8 h`, `media móvil 24 h`) |
| `status` | string | Estado SINCA (`bueno`, `regular`, `alerta`, `preemergencia`, `emergencia`) |
| `status_code` | int | Código numérico del estado |
| `icap` | int / null | Índice de calidad del aire (solo algunos contaminantes) |
| `observed_at` | string ISO 8601 | Hora de la medición |

> Observación: en la ejecución actual las estaciones **Los Maitenes** y **Valle Alegre** no tienen nodo
> en la red (`node_code = null`).
