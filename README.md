# Ruteo Resiliente de UAV — Bahía de Quintero, Ventanas y Puchuncaví

**CIT3435 · Algoritmos de Ruteo y Redes Resilientes · Universidad Diego Portales · Grupo 09**

Sistema ciberfísico de planificación de rutas para vehículos aéreos no tripulados (UAV) que
muestrean contaminación atmosférica en la bahía de Quintero. Compara cuatro técnicas de ruteo
sobre una red de **322 nodos y 855 aristas**, modela cada amenaza como una probabilidad de falla
por enlace y por nodo, y mide qué técnica resiste mejor.

---

## Ejecución en un comando

Requiere **Docker** y **Docker Compose**. Desde la raíz del repositorio:

```bash
python3 main.py --sin-descarga
```

Esto levanta PostgreSQL 16 + PostGIS + pgRouting, crea el esquema desde cero, carga las once
capas de datos, calcula las rutas y publica el sitio junto con la API.

| URL | Qué es |
|---|---|
| `http://localhost:8000/sitio_web/` | Plataforma web: mapa, panel de control y comparación de técnicas |
| `http://localhost:8000/docs` | Swagger de la API, generado automáticamente |
| `http://localhost:8000/api/rutas?destino=sinca_ventanas` | Las cuatro rutas en GeoJSON |

`python3 main.py` sin la bandera descarga además las nueve APIs en vivo (NASA FIRMS, Open-Meteo,
MET Norway, OpenSky, SINCA, SRTM, INE, Overpass). Tarda bastante más y los resultados dependen de
las condiciones del día: con `--sin-descarga` se reproducen los valores reportados en el informe.

Para detener todo: `docker compose down`.

### Verificación

```bash
python3 tests/verificar.py                                   # 57 chequeos de datos y RFC 7946
docker compose run --rm etl python tests/test_fase3.py       # 9 pruebas del backend de ruteo
```

---

## Qué hace cada parte

### La infraestructura de vuelo

La red es un grafo georreferenciado sobre el espacio aéreo de la bahía, no sobre calles. Cada
**nodo** es un punto de interés real cosechado de OpenStreetMap, SINCA, BCN e INE: estaciones de
monitoreo, fuentes emisoras industriales, colegios, centros de salud, playas, áreas concurridas.
Cada **arista** es un corredor aéreo entre un nodo y uno de sus cuatro vecinos más cercanos, con
las aristas puente que hagan falta para mantener el grafo conexo.

Las rutas no son líneas rectas sobre cualquier cosa. El modelo de fallas **muestrea cinco puntos a
lo largo de cada arista** y la marca como bloqueada si alguna muestra cae dentro de una zona
prohibida: viento sobre 12 m/s, niebla densa, foco de incendio activo. Una arista que cruza un
obstáculo queda fuera del grafo navegable aunque sus extremos estén despejados, de modo que el
planificador rodea en vez de atravesar.

Sobre la geometría se superponen capas de contexto. Las que **entran al modelo de fallas y por lo
tanto cambian las rutas** son ocho: incendios FIRMS, sismicidad CSN, viento, lluvia, niebla,
humedad, densidad censal INE y cobertura celular C2. El relieve SRTM, los obstáculos verticales de
OSM y el tráfico aéreo OpenSky se extraen, se cargan en la base y se visualizan, pero **todavía no
ponderan el costo de las aristas**. La calidad del aire SINCA está conectada como recompensa de
muestreo R(e), que vale cero mientras ninguna estación esté en alerta.

El muestreo de cinco puntos por arista es una aproximación: en los corredores más largos (hasta
1,95 km) las muestras quedan separadas unos 490 m, así que una zona prohibida muy pequeña podría
pasar entre dos muestras sin detectarse.

### El modelo de fallas

`ruteo/simulacion_fallas.py` convierte cada amenaza en una probabilidad de falla. Para cada nodo y
cada arista acumula las tasas λ de las capas activas y aplica supervivencia de Poisson:

```
p_falla(arista) = 1 − exp(−λ_total · longitud_km)
p_falla(nodo)   = 1 − exp(−λ_total)
```

Un elemento bloqueado por restricción dura queda con `p_falla = 1`.

### Las cuatro técnicas

`ruteo/tecnicas.py` resuelve el mismo par origen-destino con cuatro enfoques:

| Técnica | Qué optimiza |
|---|---|
| `dijkstra_distancia` | `pgr_dijkstra` con el peso en metros. Ignora amenazas **y bloqueos**: es la línea base del peor caso y puede atravesar zonas prohibidas. La leyenda lo advierte. |
| `milp_exacto` | Modelo de flujo entero. Autonomía como restricción dura. Ver la nota de solvers más abajo. |
| `dijkstra_multicriterio` | `pgr_dijkstra` con el costo ponderado por riesgo: `W(e) = max(L(e) + β·H(e) − R(e), ε), con H(e) = λ(e)·L_km(e)`. |
| `metaheuristica_akgun` | K caminos disimilares por penalización iterativa de aristas (Akgün et al., 2000). |

El MILP prueba los solvers en cadena (Gurobi → CPLEX → HiGHS → CBC), valida la solución y reporta
cuál lo resolvió; ese nombre aparece en la leyenda. **En la imagen Docker de este repositorio solo
están disponibles HiGHS y CBC**, porque Gurobi y CPLEX requieren licencia y no se pueden
distribuir. Para correrlo con Gurobi hay que instalar `gurobipy` con una licencia académica; el
código lo prefiere automáticamente si lo encuentra.

La metaheurística devuelve dos caminos disimilares: si uno cae, el otro puede sostener la misión.
Por eso su resiliencia se calcula sobre el par y no es directamente comparable con la de las
técnicas de un solo camino, que casi siempre resulta menor por construcción.

Las tres técnicas basadas en Dijkstra corren sobre `pgr_dijkstra` dentro de PostgreSQL o sobre una
implementación equivalente en Python; el motor se elige en el panel y se informa en la leyenda.

### La métrica de resiliencia

Con Π₁ y Π₂ dos caminos que comparten el tramo E_C y tienen tramos disjuntos E₁ y E₂:

```
R = S(E_C) · [1 − (1 − S(E₁)) · (1 − S(E₂))]        con   S(E) = exp(−Σ λ(e)·L_km(e))
```

Se reporta junto al tiempo de cómputo de cada técnica, y se contrasta con una simulación de Monte
Carlo que sortea `u ∈ [0,100)` por elemento y lo da por caído si `u < p_falla · 100`.

---

## Cómo usar la plataforma

En la pestaña **Simulador**, la tarjeta *Fase 3 · Comparación de técnicas*:

1. Elige el destino entre las ocho estaciones SINCA.
2. Fija tus restricciones: autonomía máxima en metros y β, la aversión al riesgo.
3. Marca qué amenazas y metadatos entran al modelo. Cada casilla cambia las probabilidades de
   falla y, por lo tanto, las rutas. Elige también el motor del camino mínimo: `pgr_dijkstra` en
   PostgreSQL o la implementación en Python.
4. **Calcular las 4 rutas.** Se dibujan sobre el mapa y aparece la leyenda con longitud, tiempo de
   cómputo, resiliencia R y supervivencia Monte Carlo de cada una. La más resiliente queda marcada.
5. Cada técnica tiene su casilla para mostrarla u ocultarla.
6. **Simular fallas** sortea una realización concreta y pinta en rojo lo que cayó, indicando si
   cada técnica sobrevivió.

La autonomía es restricción dura **solo en el MILP**: las otras tres técnicas pueden devolver una
ruta más larga que el límite pedido. Cuando eso ocurre, la tarjeta de esa técnica lo advierte en
naranja, igual que cuando la ruta cruza elementos bloqueados.

### Caso de ejemplo: incendio en Planta de Asfaltos

Destino **La Greda**, casilla *Escenario de contingencia* activada:

| Técnica | Longitud | R | Monte Carlo |
|---|---|---|---|
| Dijkstra por distancia | 6,71 km | **0,0000** | **0,0 %** |
| MILP exacto | 8,69 km | 0,2330 | 23,1 % |
| Dijkstra multicriterio | 8,69 km | 0,2330 | 23,1 % |
| Metaheurística Akgün | 8,69 km | **0,2331** | 23,1 % |

Dijkstra mantiene la ruta corta y la atraviesa a ciegas: cae a cero. Las otras tres pagan 1,98 km
extra para rodear el foco y conservan la misión. Es la evidencia de que el sistema entrega una
ruta alternativa frente a la amenaza.

> **Nota sobre la capa de niebla.** Con los datos de referencia, la niebla bloquea 198 aristas y
> 71 nodos, lo que deja a Campiche y Puchuncaví sin ruta factible en las tres técnicas que
> respetan bloqueos. Desactivar esa casilla las habilita. Es una condición real del territorio,
> no un error: el sistema está informando que ese día no se vuela hacia allá.

---

## Estructura

```
main.py                      Pipeline maestro: ETL, base de datos, ruteo y publicación
api/servidor.py              API FastAPI: /api/rutas, /api/simulacion, /api/destinos, /api/capas
api/CONTRATO_API.md          Contrato entre backend y frontend
ruteo/tecnicas.py            Las cuatro técnicas de ruteo
ruteo/simulacion_fallas.py   Probabilidades de falla por nodo y arista, y Monte Carlo
ruteo/exportar_resumen_fase3.py  Genera sitio_web/data/resumen_fase3.json
infraestructura/             Extractor del grafo: nodos, aristas y zonas urbanas
metadata/   amenazas/        Un script de extracción y uno de carga por capa
bd/schema.sql                DDL de las nueve tablas espaciales con índices GiST
sitio_web/                   Plataforma Leaflet; fase3.js conecta el panel con la API
tests/                       verificar.py (datos) y test_fase3.py (backend)
docs_fases_anteriores/       Informes y material de las fases 1 y 2
```

## Referencias

- Kosior, M., Przystałka, P. y Panfil, W. (2024). *Adaptive Path Planning for UAV-Based Pollution
  Sampling*. Applied Sciences, 14(24), 12065.
- Akgün, V., Erkut, E. y Batta, R. (2000). *On finding dissimilar paths*. European Journal of
  Operational Research, 121(2), 232–246.
- DGAC Chile, norma DAN 151: operación de aeronaves pilotadas a distancia.
