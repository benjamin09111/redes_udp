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

Las rutas no son líneas rectas sobre cualquier cosa. El modelo de fallas **muestrea el corredor
cada 100 m** y lo marca como bloqueado si alguna muestra cae dentro de una zona prohibida: viento
sobre 12 m/s, niebla densa o foco de incendio activo. Una arista que cruza un obstáculo queda
fuera del grafo navegable aunque sus extremos estén despejados, de modo que el planificador rodea
en vez de atravesar.

Sobre la geometría se superponen **diez capas que entran al modelo de fallas** y por lo tanto
cambian las rutas: incendios FIRMS, sismicidad CSN, viento, lluvia, niebla, humedad, densidad
censal INE, cobertura celular C2, **obstáculos verticales** y **relieve**. La calidad del aire
SINCA está conectada como recompensa de muestreo R(e), que vale cero mientras ninguna estación
esté en alerta. El tráfico aéreo OpenSky se extrae y se visualiza, pero no pondera el costo.

### La restricción de altitud

La DAN 151 limita la operación a 120 m sobre el terreno, y por seguridad se exige una separación
mínima de 40 m sobre el suelo. Eso deja una ventana vertical de 80 m, y de ahí salen dos reglas:

- **Relieve.** Un corredor solo es cruzable a cota constante si el terreno no varía más que esa
  ventana. Si `relief_m` la supera, no existe altura legal que respete a la vez el mínimo sobre el
  suelo y el techo: la arista queda bloqueada. El ascenso acumulado se penaliza aparte, por su
  coste energético.
- **Obstáculos verticales.** Una estructura más alta que el techo no se puede sobrevolar: si el
  corredor pasa por encima de ella, la arista queda bloqueada. Dentro del radio de resguardo pero
  con margen lateral se aplica penalización. Hay un matiz importante: varias chimeneas son a la vez
  nodos de la red (son fuentes de emisión que hay que muestrear), así que cuando el obstáculo está
  en un **extremo** del corredor el UAV está llegando a él, no sobrevolándolo, y eso se penaliza en
  vez de bloquearse.

Con los datos actuales el relieve de la bahía es suave (variación máxima de 82 m), así que la regla
de terreno bloquea solo 2 aristas, y ningún corredor pasa literalmente por encima de una chimenea.
Lo que sí ocurre es que **33 aristas quedan penalizadas** por pasar dentro del radio de resguardo
de una estructura vertical, y eso cambia las rutas elegidas.

El muestreo a lo largo de cada arista es adaptativo: un punto cada 100 m, entre 5 y 40 muestras.
Antes eran 5 fijas, lo que en los corredores de 1,95 km dejaba huecos de ~490 m por los que una
zona prohibida pequeña podía pasar sin detectarse.

### El modelo de fallas

`ruteo/simulacion_fallas.py` convierte cada amenaza en una probabilidad de falla. Con
`--guardar` exporta el resultado completo a `sitio_web/data/probabilidades_falla.json`
(322 nodos y 855 aristas, con el desglose de factores de cada uno). Para cada nodo y
cada arista acumula las tasas λ de las capas activas y aplica supervivencia de Poisson:

```
p_falla(arista) = 1 − exp(−λ_total · longitud_km)
p_falla(nodo)   = 1 − exp(−λ_total)
```

Toda arista suma además una tasa base de 0,005 km⁻¹. Un elemento bloqueado por restricción dura
queda con `p_falla = 1`.

Los valores de λ son **supuestos del equipo**, no parámetros calibrados con datos históricos de
falla. Están en `config/parametros.json` y en `ruteo/simulacion_fallas.py`.

### Las cuatro técnicas

`ruteo/tecnicas.py` resuelve el mismo par origen-destino con cuatro enfoques:

| Técnica | Qué optimiza |
|---|---|
| `dijkstra_distancia` | `pgr_dijkstra` con el peso en metros. Ignora amenazas **y bloqueos**: es la línea base del peor caso y puede atravesar zonas prohibidas. La leyenda lo advierte. |
| `milp_exacto` | Modelo de flujo entero. Autonomía como restricción dura. Ver la nota de solvers más abajo. |
| `dijkstra_multicriterio` | `pgr_dijkstra` con el costo ponderado por riesgo: `W(e) = max(L(e) + β·H(e) − R(e), ε), con H(e) = λ(e)·L_km(e)`. |
| `metaheuristica_akgun` | Par de caminos disimilares (k = 2): se penalizan las aristas del primero con varios factores y se elige el candidato que maximiza la resiliencia del par (Akgün et al., 2000). |

El MILP prueba los solvers en cadena (Gurobi → CPLEX → HiGHS → CBC), valida la solución y reporta
cuál lo resolvió; ese nombre aparece en la leyenda. **La imagen Docker incluye `gurobipy`, así que
el modelo se resuelve con GUROBI**, como pide la pauta.

No hace falta licencia académica: la licencia restringida que viene con el paquete admite 2000
variables y 2000 restricciones, y el modelo usa **1274 × 1484**. Esa licencia sí tiene fecha de
expiración (la de `gurobipy==12.0.3` vence el 23-11-2026); cuando caduque, basta actualizar el
paquete o pedir la licencia académica gratuita de Gurobi. Si el solver no está disponible, la
cadena cae sola a HiGHS y la leyenda lo informa, sin romper nada.

La metaheurística devuelve dos caminos disimilares: si uno cae, el otro puede sostener la misión.
Por eso su resiliencia se calcula sobre el par y no es directamente comparable con la de las
técnicas de un solo camino, que casi siempre resulta menor por construcción.

Las tres técnicas basadas en Dijkstra corren sobre **`pgr_dijkstra` dentro de PostgreSQL**, que es
el motor por defecto del servicio. El panel permite cambiarlo a una implementación equivalente en
Python (útil sin base de datos); la leyenda informa cuál resolvió cada ruta.

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
| MILP exacto | 8,69 km | 0,1676 | 16,7 % |
| Dijkstra multicriterio | 8,69 km | 0,1676 | 16,7 % |
| Metaheurística Akgün | 8,69 km | **0,1677** | 16,7 % |

Dijkstra mantiene la ruta corta y la atraviesa a ciegas: cae a cero. Las otras tres pagan 1,98 km
extra para rodear el foco y conservan la misión. Es la evidencia de que el sistema entrega una
ruta alternativa frente a la amenaza.

> **Nota sobre la capa de niebla.** Con los datos de referencia, la niebla bloquea 318 aristas y
> 113 nodos, lo que deja a Campiche y Puchuncaví sin ruta factible en las tres técnicas que
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
