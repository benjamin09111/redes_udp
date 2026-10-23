# Guía maestra: ruteo y sitio web (Fase 2 → Fase 3)

**Proyecto:** Ruteo resiliente de UAV para el muestreo de contaminación (Quintero, Ventanas, Puchuncaví)
**Destinatario:** agente de desarrollo del algoritmo y del sitio web
**Propósito:** auditar el código existente, corregir lo que esté mal y dejar el algoritmo propio bien especificado.

---

## 0. Cómo usar esta guía

1. Lee la sección 1 completa antes de tocar código. Define qué es obligatorio y qué es adicional.
2. Trabaja por prioridad:
   - **P0:** requisito obligatorio de la fase 2 (sección 3). Si falla, la entrega falla.
   - **P1:** datos y consistencia que el ruteo necesita (sección 4).
   - **P2:** algoritmo propio, que es contenido de la fase 3 adelantado (sección 5).
3. Ejecuta la auditoría de la sección 7 y las pruebas de la sección 8.
4. Reporta usando el formato de la sección 10.
5. Si una corrección cambia algún número del informe (Tablas 8 a 12), **no lo ocultes**: indícalo en el reporte con el valor anterior y el nuevo.

---

## 1. Qué pide cada fase

Instrucción 8 del profesor (textual):

> El sitio deberá mostrar una ruta generada con pgr_dijkstra, utilizando la longitud de la ruta como costo, que muestre a modo de ejemplo una ruta que sea una posible solución a su problema planteado. Esta ruta será el peor caso que podría resolver su problemática, ya que no considerará la metadata ni las posibles amenazas (eso será parte de la fase 3).

| Elemento | Fase 2 (ahora) | Fase 3 |
|---|---|---|
| Ruta de referencia | **Obligatoria:** `pgr_dijkstra`, costo = longitud, sin metadata ni amenazas. Es el "peor caso". | Se usa como línea base de comparación. |
| Metadata y amenazas | Se extraen, se cargan en la base y se muestran como capas del mapa. | Se convierten en costos y restricciones del algoritmo propio. |
| Algoritmo propio | No exigido. El equipo ya lo tiene: tratarlo como **adelanto de la fase 3**. | Es el entregable central y se compara contra Dijkstra. |
| Métrica de resiliencia | No exigida. | Necesaria para comparar. |

**Reglas que se derivan de esto:**
- La ruta `pgr_dijkstra` por longitud debe existir, funcionar y verse en el sitio **por sí sola**, aunque el algoritmo propio se apague o falle.
- La ruta de referencia **nunca** usa metadata ni amenazas. Si lo hace, deja de cumplir la instrucción.
- El algoritmo propio debe estar separado visualmente (otra capa y otro color) y en el código (otro módulo).
- Pendiente para el equipo, no para el agente: confirmar con el profesor si quiere ver ya el algoritmo propio o solo en la fase 3.

---

## 2. Arquitectura objetivo

```
fuentes externas ──ETL──> PostGIS (infra_edge, threat_event, meta_*)
                                   │
                                   ├── edge_exposure (exposición por arista, sección 4.6)
                                   │
            config/parametros.json ┤  (fuente única de λ, β, p, umbrales)
                                   │
         ruteo/ (Python) ── construye el SQL de aristas ──> pgr_dijkstra en la BD
                                   │
         API HTTP (/api/ruta_base, /api/ruta_propia) ──> sitio Leaflet
```

Principios:
1. **Un solo motor de ruteo: pgRouting.** Tanto la línea base como el algoritmo propio llaman a `pgr_dijkstra`. Lo único que cambia es el SQL de aristas (el costo). Así no hay dos implementaciones de Dijkstra que puedan dar resultados distintos.
2. **Una sola fuente de parámetros.** Todos los valores de λ, β, el factor de penalización p, los umbrales y los radios viven en `config/parametros.json`. El motor por lotes y la web leen el mismo archivo. Prohibido repetir constantes en JS y en Python.
3. **El navegador no calcula rutas.** La web solo pide rutas a la API y las dibuja.

> Si hoy el algoritmo resiliente usa un Dijkstra propio en Python (`dijkstra_camino(adj, ...)`), migrarlo a `pgr_dijkstra` con costo modificado. Si por alguna razón se mantiene en Python, es obligatorio el test T3 de la sección 8, que verifica que ambos motores coinciden.

---

## 3. P0 — Ruta `pgr_dijkstra` por longitud (requisito 8)

### 3.1 Requisitos

- R1. Se calcula con `pgr_dijkstra` **dentro de PostgreSQL**, no en Python ni en JS.
- R2. `cost = reverse_cost = length_m`, con la longitud en **metros geodésicos** (ver 4.1).
- R3. Grafo no dirigido: `directed := false`, o `reverse_cost = cost`.
- R4. No usa ninguna tabla `meta_*` ni `threat_event`.
- R5. Hay al menos una ruta de ejemplo hacia una estación SINCA, y la ideal es poder elegir cualquiera de las 8.
- R6. El sitio la muestra siempre, con una etiqueta explícita.

### 3.2 SQL de referencia

```sql
-- Ruta de referencia (peor caso): costo = longitud
SELECT d.seq,
       d.node,
       d.edge,
       d.cost,
       d.agg_cost,
       e.geom
FROM pgr_dijkstra(
       'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost
          FROM infra_edge',
       :origen_id, :destino_id,
       directed := false
     ) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
ORDER BY d.seq;
-- La última fila trae edge = -1 (llegada) y geom NULL: es normal.
```

Geometría única para el mapa:

```sql
SELECT ST_AsGeoJSON(ST_LineMerge(ST_Collect(e.geom ORDER BY d.seq))) AS geojson,
       MAX(d.agg_cost) AS longitud_m
FROM pgr_dijkstra(
       'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
       :origen_id, :destino_id, directed := false) d
JOIN infra_edge e ON e.id = d.edge;
```

### 3.3 Cómo llega la ruta al sitio

Usa una de estas dos opciones, en orden de preferencia:
1. **Endpoint** `GET /api/ruta_base?origen=..&destino=..` que ejecuta el SQL de 3.2 y devuelve un GeoJSON con `longitud_m`, `n_aristas` y `lista_aristas`.
2. **Precalculada:** `ruta_dijkstra.py` ejecuta 3.2 para las 8 estaciones y escribe `sitio_web/data/rutas_pgr_dijkstra.geojson`. Cada feature debe incluir `origen`, `destino`, `longitud_m`, `aristas` y `generado_en`.

En ambos casos, la geometría debe salir de la BD, no reconstruirse en JS.

### 3.4 Cómo se muestra

- Capa propia con el nombre **"Ruta de referencia — pgr_dijkstra (costo = longitud)"**.
- Texto visible: *"Peor caso: no considera metadata ni amenazas (Fase 3)."*
- Panel con: origen, destino, longitud en km (2 decimales y coma decimal, igual que el informe) y número de aristas.
- Color y estilo distintos de cualquier ruta del algoritmo propio, con leyenda en el mapa.
- Debe verse aunque todas las casillas de amenazas estén apagadas y aunque el algoritmo propio no exista.

### 3.5 Verificaciones obligatorias

```sql
-- V1: la ruta es continua (cada arista comparte nodo con la siguiente)
-- Se cumple si pgr_dijkstra devuelve filas; validar además en el test T1.

-- V2: agg_cost final = suma de length_m de las aristas de la ruta
SELECT MAX(d.agg_cost) - SUM(e.length_m) AS diferencia   -- debe ser ~0
FROM pgr_dijkstra('SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
                  :o, :d, directed := false) d
JOIN infra_edge e ON e.id = d.edge;

-- V3: hay ruta hacia las 8 estaciones SINCA (0 filas = sin ruta = ERROR)
```

Además: la longitud que muestra el sitio para cada estación debe coincidir con la Tabla 8 del informe (columna Dijkstra k=1). Si no coincide, reportarlo.

---

## 4. P1 — Datos que el ruteo necesita correctos

### 4.1 Longitudes en metros reales

La base está en EPSG:4326 (grados). Verificar:

```sql
SELECT MAX(ABS(length_m - ST_Length(geom::geography))) AS error_max_m FROM infra_edge;
-- Criterio OK: error_max_m < 1
```

Si falla, recalcular: `UPDATE infra_edge SET length_m = ST_Length(geom::geography), cost = ..., reverse_cost = ...;`
Lo mismo aplica a los círculos de amenaza: se crean con `ST_Buffer(geom::geography, radio_m)::geometry`, nunca con un radio en grados.

### 4.2 Conectividad del grafo

```sql
SELECT COUNT(DISTINCT component) AS n_componentes
FROM pgr_connectedComponents('SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge');
-- Criterio OK: 1. Si es >1, listar qué nodos quedan aislados y si alguno es una estación.
```

### 4.3 Integridad de aristas

- No hay `source = target` (bucles).
- No hay `length_m <= 0` ni NULL.
- No hay aristas duplicadas (el mismo par de nodos en ambos sentidos con dos ids distintos).

### 4.4 Idempotencia del ETL

Correr `python3 main.py --sin-descarga` dos veces seguidas debe dejar los mismos conteos (Tabla 3 del informe). Si los conteos se duplican, los cargadores no hacen `TRUNCATE` o `ON CONFLICT`.

### 4.5 Snapshot reproducible

- Los resultados del informe corresponden a una ejecución concreta. Guardar los GeoJSON de esa ejecución en `data/snapshot_AAAAMMDD_HHMM/` y registrar la fecha en el README.
- `--sin-descarga --snapshot <carpeta>` debe reproducir exactamente las Tablas 8 a 12.

### 4.6 Foco de contingencia en la BD

El foco simulado de Planta Asfaltos (180 m) **no está en `threat_event`**, porque 130 = 1 + 97 + 16 + 16. Hay que:
- Agregar la columna `simulated boolean default false` a `threat_event`.
- Insertar el foco con `event_type = 'incendio'`, `simulated = true` y `exceeds = true`.
- Eliminar cualquier coordenada de contingencia escrita directamente en Python o JS.

### 4.7 Tabla de exposición por arista (base para el algoritmo propio)

En lugar de marcar una arista como expuesta "toda o nada", se mide **cuántos metros de cada arista** caen dentro de cada amenaza. Primero se unen los polígonos del mismo tipo, para no contar dos veces las zonas superpuestas.

```sql
CREATE TABLE edge_exposure AS
WITH zonas AS (
  SELECT event_type, simulated, ST_Union(geom) AS geom
  FROM threat_event
  WHERE exceeds
  GROUP BY event_type, simulated
  UNION ALL
  SELECT 'urbana', false, ST_Union(geom)
  FROM meta_census_block
  WHERE density_hab_km2 > 2500          -- leer el umbral desde parametros.json
)
SELECT e.id AS edge_id,
       z.event_type,
       z.simulated,
       ST_Length(ST_Intersection(e.geom, z.geom)::geography) AS len_in_m
FROM infra_edge e
JOIN zonas z ON ST_Intersects(e.geom, z.geom);

-- Sin cobertura = longitud de la arista FUERA de la unión de coberturas
INSERT INTO edge_exposure
SELECT e.id, 'sin_cobertura', false,
       ST_Length(ST_Difference(e.geom, c.geom)::geography)
FROM infra_edge e,
     (SELECT ST_Union(coverage_geom) AS geom FROM meta_telecom_antenna) c
WHERE ST_Length(ST_Difference(e.geom, c.geom)::geography) > 0;

CREATE INDEX ON edge_exposure (edge_id);
```

Criterio OK: para toda arista y todo tipo, `0 <= len_in_m <= length_m`.

---

## 5. P2 — Algoritmo propio (adelanto de la fase 3)

### 5.1 Idea en una frase

Se usa el **mismo** `pgr_dijkstra`, pero con un costo que suma a la distancia el riesgo de cada tramo. Después se obtiene una segunda ruta distinta penalizando la primera. La "inteligencia" del algoritmo está en la **función de costo** y en la **estrategia para obtener dos rutas**, no en un Dijkstra diferente.

### 5.2 Riesgo por arista: H(e)

Cada tipo de amenaza f tiene una tasa de falla por km, λ_f (Tabla 9 del informe). El riesgo acumulado de una arista es:

```
H(e) = λ_base · L_km(e)  +  Σ_f  on_f · λ_f · Lin_f,km(e)
```

donde:
- `L_km(e)` es la longitud total de la arista en km.
- `Lin_f,km(e)` es la longitud dentro de la zona f, sacada de `edge_exposure`.
- `on_f ∈ {0, 1}` es la casilla del usuario para la amenaza f.

La supervivencia de un conjunto de aristas es `S(E) = exp(−Σ_{e∈E} H(e))`, que es la misma fórmula del informe pero con exposición parcial.

> **Por qué es mejor que el modelo actual:** hoy, si una arista de 1 km toca un círculo de 180 m, se cuenta el kilómetro entero como expuesto. Con `Lin_f` se cuentan solo los metros que realmente están dentro.

### 5.3 Función de costo

```
W(e) = L_m(e) + β · H(e)
```

- `β` (en metros) indica cuántos metros extra estás dispuesto a volar para evitar una unidad de riesgo.
- Con `β = 0`, el algoritmo es exactamente el Dijkstra de la línea base. Esto se usa como prueba de cordura (test T3).
- Con `β → ∞`, minimiza Σ H, es decir, encuentra **la ruta de máxima supervivencia**.

**Esto reemplaza a los α actuales.** Hoy el costo usa α (15, 6, 4, 2,5, 2, 2) y la evaluación usa λ (5, 0,08, 0,05, 0,03, 0,04, 0,03). Esos dos conjuntos de números no son coherentes entre sí: para α el incendio es 2,5 veces peor que la zona urbana, y para λ es 62,5 veces peor. Por eso aparecen ΔR negativos en Loncura y Sur. Con W = L + β·H, la ruta se elige con el mismo modelo con el que se evalúa.

Valores de β para el barrido del experimento: `{0, 250, 500, 1000, 2000, 5000, 10000}` metros, y elegir un valor por defecto a partir de la curva R vs. distancia (experimento E3).

**Restricciones duras (opcional, recomendado).** pgRouting ignora las aristas con costo negativo. Se puede prohibir un tramo, por ejemplo uno dentro de un incendio confirmado, así:

```sql
CASE WHEN prohibida THEN -1 ELSE <W(e)> END AS cost
```

### 5.4 Par de rutas (k = 2) por penalización iterativa

```
Entrada: grafo G, costo W, origen o, destino d, factor p (por defecto 4)
1. P1 ← pgr_dijkstra(G, W, o, d)
2. W'(e) ← p · W(e)   si e ∈ P1;   W(e) en otro caso
3. P2 ← pgr_dijkstra(G, W', o, d)
4. Si P2 no existe: P2 ← P1                  (se informa como "sin alternativa")
5. E_C ← E1 ∩ E2,  E1x ← E1 \ E_C,  E2x ← E2 \ E_C
6. D ← 1 − |E1 ∩ E2| / |E1 ∪ E2|
7. R ← S(E_C) · [1 − (1 − S(E1x)) · (1 − S(E2x))]
Salida: P1, P2, longitudes, D, R, S(P1), S(P2)
```

SQL del paso 3:

```sql
SELECT id, source, target,
       CASE WHEN id = ANY('{<ids P1>}'::int[]) THEN <p> * w ELSE w END AS cost,
       CASE WHEN id = ANY('{<ids P1>}'::int[]) THEN <p> * w ELSE w END AS reverse_cost
FROM v_edge_cost
```

Al construir el SQL en Python: los ids deben ser `int` y los parámetros deben pasar por `float()` antes de insertarlos en el texto, para evitar inyección.

**La línea base debe usar el mismo procedimiento con β = 0.** Así la comparación aísla el efecto de la función de costo.

### 5.5 Vista de costo en SQL

```sql
-- v_edge_cost se genera en Python con los valores on_f y β ya validados
CREATE OR REPLACE VIEW v_edge_cost AS
SELECT e.id, e.source, e.target, e.length_m,
       ( <lambda_base> * e.length_m / 1000.0
         + COALESCE(SUM(
             CASE x.event_type
               WHEN 'incendio'      THEN <on_inc>  * <lambda_inc>
               WHEN 'urbana'        THEN <on_urb>  * <lambda_urb>
               WHEN 'sismo'         THEN <on_sis>  * <lambda_sis>
               WHEN 'sin_cobertura' THEN <on_cob>  * <lambda_cob>
               WHEN 'viento'        THEN <on_vie>  * <lambda_vie>
               WHEN 'lluvia'        THEN <on_llu>  * <lambda_llu>
             END * x.len_in_m / 1000.0), 0)
       ) AS h,
       e.length_m + <beta> * ( ...misma expresión h... ) AS w
FROM infra_edge e
LEFT JOIN edge_exposure x
       ON x.edge_id = e.id
      AND (NOT x.simulated OR <contingencia_activa>)
GROUP BY e.id;
```

(Se puede escribir como función SQL con parámetros en lugar de una vista generada; lo importante es que el cálculo sea uno solo.)

### 5.6 ¿Dónde está la "heurística"?

- La heurística del algoritmo es la **penalización iterativa** (Akgün, Erkut y Batta, 2000). No garantiza el mejor par posible, pero obtiene rutas disímiles de forma barata y controlable con `p`.
- La función de costo `W = L + β·H` **no** es una heurística: es un modelo explícito del compromiso entre distancia y riesgo.
- **Opcional:** usar `pgr_aStar` con distancia euclidiana como heurística de búsqueda. Es admisible porque W(e) ≥ L(e). Solo acelera el cálculo y no cambia el resultado, así que no es necesario con 633 aristas. Si se menciona en la presentación, explicar esa diferencia.

### 5.7 Métrica R: definición e interpretación

- **Definición:** R = P(al menos una de las dos rutas completa) bajo fallas independientes entre aristas.
- **Interpretación operativa:** probabilidad de que, al momento del despegue, exista al menos una ruta operativa. El cambio de ruta en vuelo es el planificador local (LPP), que queda fuera de alcance.
- **Limitación conocida:** un mismo incendio afecta a todas las aristas cercanas a la vez (falla de causa común), así que la independencia sobreestima R. El experimento E4 lo corrige con simulación.

### 5.8 Líneas base para comparar

| Código | Método | Costo | Rutas | Uso |
|---|---|---|---|---|
| **B0** | `pgr_dijkstra` | longitud | 1 | **Requisito 8.** Peor caso. |
| B1 | penalización iterativa, β = 0 | longitud | 2 | Mismo procedimiento sin riesgo. |
| B2 | `pgr_KSP` (Yen), K = 2 | longitud | 2 | Las 2 rutas más cortas reales. |
| A1 | `pgr_dijkstra` | W, con β | 1 | Efecto de evitar riesgo sin respaldo. |
| **A2** | penalización iterativa | W, con β | 2 | Algoritmo propio completo. |

Comparar A2 con B1 aísla el efecto de la función de costo, y A2 con A1 aísla el efecto de tener una ruta de respaldo. B2 responde a la pregunta "¿por qué no usaron Yen?".

```sql
SELECT * FROM pgr_KSP(
  'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
  :o, :d, 2, directed := false);
```

---

## 6. Experimentos (para la fase 3 y el informe)

Todos los experimentos escriben un CSV en `resultados/` con estas columnas:
`experimento, metodo, destino, beta, p, escenario, semilla, L1_km, L2_km, D, S1, S2, R, n_aristas_en_amenaza, km_expuestos_EC, km_expuestos_E1x, km_expuestos_E2x`.

Las columnas de km expuestos permiten que cualquiera reproduzca R a mano.

- **E1 — Escenario base.** Snapshot real, sin contingencia, los 5 métodos y los 8 destinos.
- **E2 — Contingencia.** Foco de 180 m en Planta Asfaltos, los 5 métodos y los 8 destinos.
- **E3 — Barrido de β y p.** Valores de β según 5.3 y `p ∈ {2, 4, 10}`. Se grafica R contra la distancia extra (frontera de compromiso).
- **E4 — Monte Carlo con focos aleatorios.** Es el experimento que responde la crítica "pusieron el fuego justo en la ruta de Dijkstra".
  - N = 1000 focos con centro uniforme en el área de estudio, radios r ∈ {180, 450, 1000} m y semilla fija.
  - **Modo informado:** el planificador conoce el foco y recalcula las rutas.
  - **Modo no informado:** las rutas se planifican con el snapshot y el foco aparece después.
  - Una arista que toca el foco queda bloqueada. La misión se cumple si al menos una ruta no tiene aristas bloqueadas.
  - Reportar la tasa de éxito por método, la distribución de ΔR (media, p5, p50 y p95) y el porcentaje de casos en que A2 supera a B0.
- **E5 — Sensibilidad a λ_incendio** ∈ {0,5; 1; 5}, como la Tabla 12, pero para los 4 destinos afectados.

---

## 7. Checklist de auditoría (problemas detectados en la revisión)

| ID | Qué revisar | Cómo | Criterio OK |
|---|---|---|---|
| A1 | La ruta B0 sale de `pgr_dijkstra` en la BD | Leer `ruta_dijkstra.py` y el código de la web | Sin Dijkstra en JS ni en Python para B0 |
| A2 | B0 no usa metadata ni amenazas | Leer el SQL de aristas de B0 | Solo `length_m` |
| A3 | Longitudes geodésicas | Consulta de 4.1 | error < 1 m |
| A4 | Buffers de amenazas en metros | Revisar los scripts de `amenazas/` | Usan `::geography` |
| A5 | Grafo conexo | Consulta de 4.2 | 1 componente |
| A6 | Foco de contingencia en la BD | `SELECT * FROM threat_event WHERE simulated` | 1 fila |
| A7 | Un solo motor de ruteo | Buscar `def dijkstra` y `dijkstra_camino` | Solo pgRouting, o test T3 aprobado |
| A8 | Parámetros en un solo lugar | Buscar literales `0.005`, `5.0`, `4.0`, `15` en el código | Solo en `parametros.json` |
| A9 | La web y el motor por lotes usan el mismo costo | Comparar qué amenazas incluye cada uno (hoy el lote suma viento y lluvia y la web no) | Mismo conjunto y mismos valores |
| A10 | Nombres honestos | `calcular_par_ksp` no es KSP (Yen) | Renombrar a `par_penalizacion_iterativa` |
| A11 | Exposición parcial | El cálculo de `hazard_rate` hoy es binario por arista | Usa `edge_exposure.len_in_m` |
| A12 | Números del sitio = informe | Comparar el panel con las Tablas 8, 10 y 11 | Iguales, con 2 decimales y coma decimal |
| A13 | Redondeo consistente | Loncura y Quintero (ambos 2,35) muestran 2.3k y 2.4k | Mismo formato en todo el sitio |
| A14 | Etiquetas de la interfaz | "adaptativa", "geodésica", "rutas oficiales", "Sombra Telecom C2" | Términos iguales a los del informe |
| A15 | "Riesgos mitigados" | El panel resiliente no lista "Incendio" con la contingencia activa | Lista todas las amenazas evitadas |
| A16 | Caso sin alternativa | Forzar un destino donde P2 = P1 | El sitio lo muestra y R = S(P1) |
| A17 | 52 filas de calidad del aire | Contar estaciones distintas en `meta_air_quality` | Documentado (¿incluye Los Maitenes y Valle Alegre?) |

---

## 8. Pruebas automáticas mínimas (pytest)

- **T1 — Continuidad.** Para toda ruta devuelta, cada arista comparte un nodo con la siguiente, la primera parte en el origen y la última llega al destino.
- **T2 — Costo.** `agg_cost` final = Σ costo de las aristas (tolerancia 1e-6).
- **T3 — Cordura de la línea base.** Con β = 0 (o todas las casillas apagadas), A1 devuelve **exactamente** la misma secuencia de aristas que B0, para los 8 destinos.
- **T4 — Rango de R.** 0 ≤ S ≤ 1, 0 ≤ R ≤ 1 y 0 ≤ D ≤ 1.
- **T5 — R con rutas iguales.** Si P2 = P1, entonces R = S(P1).
- **T6 — Monotonía.** Con las rutas fijas, aumentar cualquier λ nunca aumenta R.
- **T7 — Máxima supervivencia.** Con β muy grande, S(P1) de A1 ≥ S(P1) de B0.
- **T8 — Exposición válida.** `0 <= len_in_m <= length_m` para todas las filas de `edge_exposure`.
- **T9 — Reproducibilidad.** Dos corridas con el mismo snapshot y la misma semilla dan CSV idénticos.
- **T10 — Regresión.** Con el snapshot del informe, B0 reproduce la columna Dijkstra k=1 de la Tabla 8.

---

## 9. Sitio web: requisitos

1. **Capas** (activables por separado): nodos, aristas, zonas urbanas, cada fuente de metadata, cada fuente de amenaza, **ruta B0** y rutas del algoritmo propio.
2. **Ruta B0 siempre disponible**, con la etiqueta de 3.4.
3. **Leyenda permanente** en el mapa: color de cada ruta, de cada amenaza y del foco de contingencia.
4. **Panel de resultados**, con los mismos nombres del informe:
   - Por método: longitud (km), S(P1), S(P2), D y R.
   - ΔR = R(A2) − R(B0 o B1), indicando explícitamente contra cuál se compara.
   - Amenazas atravesadas y km expuestos por amenaza.
5. **Controles:** origen, destino, casillas `on_f`, contingencia, β y p. Debe haber un botón para restablecer los valores por defecto, que se leen de `parametros.json`.
6. **Aviso** cuando el destino no es una estación SINCA.
7. **Formato numérico:** coma decimal y 2 decimales para km, 1 decimal para porcentajes.
8. **Sin cálculo de rutas en el navegador.**

---

## 10. Formato de reporte del agente

```
## Resumen
- P0 (requisito 8): CUMPLE / NO CUMPLE — una línea de justificación
- Pruebas: T1..T10 → aprobadas X/10

## Hallazgos
| ID | Severidad (alta/media/baja) | Archivo:línea | Problema | Corrección aplicada o propuesta |

## Cambios en resultados
| Tabla del informe | Fila | Valor anterior | Valor nuevo | Motivo |

## Pendientes que requieren decisión del equipo
- ...
```

---

## 11. Qué NO hacer

- No agregar metadata ni amenazas a la ruta B0. Dejaría de cumplir la instrucción 8.
- No eliminar ni ocultar la ruta B0 cuando el algoritmo propio está activo.
- No calcular rutas en JavaScript.
- No escribir parámetros directamente en el código.
- No llamar "KSP", "Yen" ni "adaptativo" a algo que no lo es.
- No ajustar λ, β ni p para que los resultados "se vean mejor". Cualquier cambio de parámetros va al reporte con su justificación.
- No presentar el foco de 180 m como el único caso de prueba: el experimento E4 es el que da validez a la comparación.
