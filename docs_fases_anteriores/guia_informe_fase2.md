# Guía para redactar el informe de la Fase 2

**Proyecto:** Ruteo resiliente de UAV para el muestreo de contaminación en la Bahía de Quintero
**Curso:** Algoritmos de Ruteo y Redes Resilientes (CIT3435) · Grupo 09
**Destinatario:** agente de desarrollo que conoce el código
**Objetivo:** producir un informe de la fase 2 con nivel de magíster, **fiel al código que se entrega**, que cumpla la pauta del profesor y respete el límite de la fase.

---

## 0. Cómo usar esta guía

Sigue el orden:

1. Lee las **reglas de oro** (sección 1). No se negocian.
2. Ejecuta la **auditoría de hechos** (sección 2) y llena la ficha de hechos. **Ningún número entra al informe si no sale de esa ficha.**
3. Respeta el **límite de la fase** (sección 3).
4. Redacta **sección por sección** según la sección 4.
5. Aplica las reglas de **estilo, figuras y referencias** (secciones 6 a 8).
6. Pasa la **lista de verificación final** (sección 10).
7. Entrega lo que pide la sección 11.

Existen dos documentos previos: un PDF del equipo (25 páginas, buena forma, pero con contenido de la fase 3) y un MD generado anteriormente (`INFORME_FASE2_MAGISTER.md`), con errores graves. **Úsalos solo como borradores de redacción, nunca como fuente de datos.** La única fuente de datos es el código y su ejecución.

---

## 1. Reglas de oro

1. **Fidelidad al código.** Todo número, nombre de tabla, nombre de campo, nombre de archivo, parámetro, umbral, radio y versión debe coincidir con el repositorio que se entrega. Si el código y un borrador no coinciden, gana el código.
2. **Cero invención.** No escribas afirmaciones que no puedas respaldar con el código, con una ejecución o con una referencia verificable. Si algo no se puede verificar, se elimina o se declara como supuesto del equipo.
3. **Límite de la fase 2.** En ruteo, la fase 2 llega solo hasta `pgr_dijkstra` con costo igual a la longitud. Nada de funciones de costo con riesgo, métricas de resiliencia, ΔR, Monte Carlo ni comparaciones entre algoritmos (sección 3).
4. **Sin autoevaluación.** Prohibido escribir puntajes, "60/60", "100 % bien logrado", "aprobado", "puntaje garantizado" o cualquier juicio sobre la propia nota. El informe muestra evidencia; el profesor evalúa.
5. **Tono sobrio.** El informe convence con precisión, no con adjetivos. Ver la lista de frases prohibidas en la sección 6.
6. **Honestidad sobre los límites.** Toda simplificación se declara como supuesto (S1, S2, …) o como limitación. Un evaluador valora más una limitación bien declarada que una afirmación inflada.
7. **Reproducibilidad.** El informe indica la fecha y hora exactas de la ejecución cuyos números reporta, y cómo reproducirla.

---

## 2. Auditoría de hechos (hacer ANTES de escribir)

### 2.1 Discrepancias detectadas entre los borradores

Los dos borradores describen redes distintas. Determina con el código cuál es la verdad para cada fila:

| Dato | Borrador PDF | Borrador MD | Valor real (llenar) |
|---|---|---|---|
| Nodos / aristas | 237 / 633 | 42 / 122 | |
| Construcción del grafo | 4 vecinos + 2 aristas puente | 3 vecinos + enlaces a SCER | |
| ¿Grafo dirigido? | No dirigido | 122 dirigidas, `directed := true` | |
| Unidad de `cost` | metros | kilómetros | |
| Zonas urbanas | 8 | 13 | |
| Manzanas INE | 703 | 185 | |
| Antenas / radio de cobertura | 25 / 3 km | 24 / 2 km | |
| Radio del círculo de incendio | 2 km | 500 m | |
| Umbral de viento | 14 m/s | 12 m/s | |
| Muestreo SRTM | cada 100 m | 5 puntos por arista | |
| Estaciones SINCA que son nodos | incluye Campiche y La Greda | incluye Valle Alegre y Maitencillo | |
| Nombres de tablas | `urban_zone`, `meta_census_block`, `meta_edge_terrain` | `infra_urban_zone`, `meta_populated_block`, `meta_relief_profile`, `route_segment` | |
| Distancias k=1 (p. ej., Centro Quintero) | 1,69 km | 3,94 km | |
| UAV de referencia | 8 m/s, autonomía 26,4 km | 15 m/s, alcance 32 km | |
| Dependencias Python | `psycopg[binary]==3.2.13` | "solo biblioteca estándar" + psycopg | |
| Número de pruebas automáticas | — | 57 | |

**Alerta específica:** ambos borradores reportan Puchuncaví k=1 = 14,41 km y k=2 = 15,60 km pese a describir redes distintas. Además, en el MD la ruta k=2 es siempre la k=1 más 0,94 km o más 1,19 km. Verifica esas cifras directamente en la base de datos.

### 2.2 Cómo obtener cada número

Ejecuta el pipeline completo y guarda la salida:

```bash
python3 main.py --sin-descarga 2>&1 | tee ejecucion_informe.log
```

Consultas mínimas (ajusta los nombres de tablas a los reales de `bd/schema.sql`):

```sql
-- Conteos de todas las tablas
SELECT 'infra_node', COUNT(*) FROM infra_node
UNION ALL SELECT 'infra_edge', COUNT(*) FROM infra_edge
-- ... repetir para cada tabla del esquema
;

-- ¿Grafo conexo?
SELECT COUNT(DISTINCT component) AS n_componentes
FROM pgr_connectedComponents(
  'SELECT id, source, target, cost, reverse_cost FROM infra_edge');

-- ¿La longitud almacenada coincide con la geodésica?
SELECT MAX(ABS(length_m - ST_Length(geom::geography))) AS error_max_m,
       AVG(ABS(length_m - ST_Length(geom::geography))) AS error_medio_m
FROM infra_edge;

-- ¿cost y reverse_cost son iguales?
SELECT COUNT(*) FROM infra_edge WHERE cost <> reverse_cost;

-- Unidad de cost (debe ser coherente con length_m)
SELECT MIN(cost / NULLIF(length_m,0)), MAX(cost / NULLIF(length_m,0)) FROM infra_edge;

-- Ruta base hacia cada estación SINCA
SELECT n.code, MAX(d.agg_cost) AS costo_total, COUNT(d.edge) FILTER (WHERE d.edge > 0) AS n_aristas
FROM infra_node n
CROSS JOIN LATERAL pgr_dijkstra(
  'SELECT id, source, target, cost, reverse_cost FROM infra_edge',
  (SELECT id FROM infra_node WHERE code = 'base_scer'), n.id, directed := false) d
WHERE n.category = 'sinca'
GROUP BY n.code ORDER BY n.code;

-- Amenazas activas por tipo
SELECT event_type, COUNT(*) AS total, COUNT(*) FILTER (WHERE exceeds) AS activas
FROM threat_event GROUP BY event_type;
```

Revisa también, leyendo el código:
- Cómo se calcula `length_m` (haversine, `geography` u otro).
- Cómo se construyen los círculos (radio en metros convertido a grados, o `ST_Buffer(geography)`).
- Qué valor de `directed` usa `ruta_dijkstra.py`.
- Cómo se obtiene la ruta k=2, si existe.
- Los parámetros reales de cada extractor: ventanas de tiempo, filtros, umbrales y radios.
- El rectángulo de estudio (coordenadas).
- La fecha y hora de generación de cada GeoJSON (bloque `etl`).
- La lista exacta de pruebas automáticas y su resultado.

### 2.3 Ficha de hechos (entregable obligatorio)

Crea `docs/ficha_hechos_fase2.md` con una tabla `dato | valor | cómo se obtuvo (archivo:línea, consulta o log)`. Esa ficha es la **única fuente** de números del informe. Si un número del informe no está en la ficha, no va.

---

## 3. Límite de la fase 2

### 3.1 La instrucción del profesor

> El sitio deberá mostrar una ruta generada con pgr_dijkstra, utilizando la longitud de la ruta como costo, que muestre a modo de ejemplo una ruta que sea una posible solución a su problema planteado. Esta ruta será el peor caso que podría resolver su problemática, ya que no considerará la metadata ni las posibles amenazas (eso será parte de la fase 3).

### 3.2 Qué entra y qué no

| Entra en el informe de la fase 2 | NO entra (fase 3) |
|---|---|
| Base de datos, ETL, estructura de los JSON, carga | Función de costo con riesgo (W(e), α, β, λ) |
| Ruta con `pgr_dijkstra`, costo = longitud | Algoritmo resiliente propio |
| Visualización de capas y ruta en Leaflet | Métrica de resiliencia R, supervivencia S, ΔR |
| Docker, `main.py`, reproducibilidad, pruebas | Monte Carlo, sensibilidad, escenarios de contingencia |
| **Descripción** de la exposición de la ruta base a las capas (sección 5) | Comparación entre algoritmos o funciones de costo |
| Una sección breve de proyección a la fase 3, sin resultados | Hipótesis sobre ΔR |

### 3.3 Qué hacer con el contenido de la fase 3 del borrador PDF

- Las secciones 11 (modelo de fallas), 13 (métrica de resiliencia), 14 (diseño experimental) y 16.2 a 16.8 (E1 a E7) **se eliminan** del informe de la fase 2.
- Las hipótesis H1 a H3 **se eliminan**. Se reemplazan por preguntas de diseño (sección 4, apartado 3).
- La idea del algoritmo resiliente puede ocupar **como máximo una página** en "Proyección a la fase 3", redactada en futuro y sin ningún número de resultados.
- Si el código conserva el motor resiliente o la ruta k=2, el informe lo dice en una línea ("el repositorio incluye un prototipo para la fase 3, que no se evalúa en este informe"), pero no lo desarrolla.

### 3.4 Sobre la ruta k=2

La instrucción pide **una** ruta. Si el código calcula además una segunda ruta:
- No la llames "disjunta" ni "segunda más corta", salvo que lo sea. Si se obtiene multiplicando el costo de las aristas de la primera ruta, es una ruta alternativa por **penalización**.
- Preséntala como complemento y calcula su solapamiento con la primera (porcentaje de aristas compartidas).
- Si no aporta a la fase 2, es preferible omitirla del informe.

---

## 4. Estructura y contenido, sección por sección

Extensión total orientativa: **15 a 20 páginas** más anexos. Para cada sección se indica qué debe contener, qué preguntas debe responder y qué evitar.

### Portada
Universidad, facultad, escuela, título, profesor (**Nicolás Boettcher**, verificar ortografía), curso con código, grupo e integrantes, fecha.

### Resumen (150 a 200 palabras)
- **Debe contener:** problema en una frase, qué construye la fase 2, las 8 fuentes, el tamaño de la red, la ruta base y un resultado numérico concreto (por ejemplo, la longitud hacia Puchuncaví y, si se hace la sección 5, su exposición).
- **Evitar:** adjetivos, promesas de la fase 3, cualquier puntaje.

Plantilla (reemplazar los corchetes con datos de la ficha):

> Las estaciones del Sistema de Información Nacional de Calidad del Aire (SINCA) en Quintero, Ventanas y Puchuncaví miden contaminantes a nivel de suelo, mientras que las emisiones industriales se dispersan en altura. Este proyecto propone planificar las rutas de un UAV de muestreo de modo que la misión se mantenga ante amenazas del entorno. Este informe documenta la fase 2, que construye la base de datos y la línea base de ruteo. Se implementó un proceso ETL reproducible en Docker que integra la infraestructura de la red ([N] nodos y [M] aristas), cuatro fuentes de metadata ([…]) y cuatro fuentes de amenazas ([…]) en PostgreSQL con PostGIS y pgRouting. Sobre esa base, `pgr_dijkstra` calcula la ruta de menor longitud desde el Aeródromo de Quintero hasta las [K] estaciones SINCA de la red, y un sitio web con Leaflet muestra la ruta junto con todas las capas. La ruta no considera metadata ni amenazas y constituye el peor caso contra el que se evaluará el algoritmo resiliente de la fase 3. Hacia Puchuncaví mide [X] km y recorre [Y] km sobre manzanas con más de [umbral] hab/km² y [Z] km fuera de la cobertura celular estimada.

### 1. Introducción (1 a 1,5 páginas)
- **1.1 Problema.** Contexto ambiental de la zona con cita (episodios de 2018 y el plan de descontaminación vigente; verificar número y año del decreto). Medición a nivel de suelo contra dispersión en altura [SINCA, Kosior]. Amenazas al vuelo.
- **1.2 Enfoque del proyecto en tres fases**, en un párrafo.
- **1.3 Alcance de la fase 2**, con una tabla "incluido / fuera de la fase", y esta frase explícita: "Conforme a la instrucción de la fase, la ruta de `pgr_dijkstra` usa como costo únicamente la longitud de cada arista y no considera metadata ni amenazas."
- **1.4 Contribución**, en una frase.
- **1.5 Estructura del documento**, en un párrafo.
- **Evitar:** descripción meteorológica extensa sin cita, listas de empresas (si se nombran, verificar que sigan operando y con ese nombre), planes de algoritmos de la fase 3 (ACO, GA, RRT*), resultados de la fase 3.

### 2. Marco conceptual (1 página)
Breve y solo lo que se usa o se usará:
- Camino mínimo: Dijkstra [Dijkstra 1959]; implementación `pgr_dijkstra` [documentación de pgRouting].
- Rutas alternativas (contexto para la fase 3): Yen [1971], Suurballe [1974], Akgün et al. [2000].
- Datos geoespaciales: GeoJSON [RFC 7946], PostGIS.
- Riesgo en operaciones de UAV: SORA [JARUS], DAN 151 [DGAC].
- UAV para muestreo de contaminación: Kosior et al. [2024].

### 3. Objetivos y preguntas de diseño (0,5 páginas)
- **Objetivo general (propuesta):** "Construir una base de datos geoespacial reproducible que integre la infraestructura de la red, cuatro fuentes de metadata y cuatro fuentes de amenazas del área de Quintero, Ventanas y Puchuncaví, y obtener sobre ella la ruta de menor longitud con `pgr_dijkstra` como línea base del ruteo resiliente."
- **Objetivos específicos:** uno por cada bloque de la pauta (BD, infraestructura, metadata, amenazas, ruta, sitio web, automatización y Docker), redactados con verbo y entregable verificable.
- **Preguntas de diseño** (reemplazan a las hipótesis, porque esta fase no tiene experimento comparativo):
  - P1. ¿Se pueden integrar las 8 fuentes de forma automática y reproducible, con trazabilidad de origen y fecha?
  - P2. ¿La red construida es conexa y permite alcanzar todas las estaciones SINCA desde el aeródromo?
  - P3. ¿Cuánto se expone la ruta de menor longitud a las zonas de riesgo que registran la metadata y las amenazas? (Se responde en la sección 5 de esta guía.)

### 4. Alcance y supuestos (1 página)
- **4.1 Alcance**, en viñetas cortas.
- **4.2 Supuestos numerados (S1, S2, …).** Cada supuesto con su justificación o fuente:
  - Red: qué representan los nodos y su origen (fase 1), cómo se construyen las aristas (k vecinos, aristas extra), por qué corredores rectos (el UAV no sigue calles) y que no se evaluaron otros valores de k.
  - Altura: vuelo bidimensional; límite de altura con artículo exacto de la DAN 151 (verificar letra y número).
  - Aeródromo: restricción de la DAN 151 cerca de aeródromos y supuesto de autorización (verificar artículo).
  - Población: umbral de densidad y su justificación.
  - Telemetría: supuesto de enlace celular y radio de cobertura.
  - UAV de referencia: modelo, autonomía y velocidad **tomados de la ficha técnica citada**, con los mismos valores que use el sitio web.
  - Umbrales y radios de amenazas: supuestos del equipo, salvo que tengan fuente.
- **Evitar:** presentar supuestos del equipo como normativa.

### 5. Arquitectura, Docker y reproducibilidad (1,5 páginas) — criterios 7.0 y 8.0
- Figura de arquitectura (fuentes → extractores → GeoJSON → cargadores → BD → ruteo → web), indicando qué contenedor ejecuta cada etapa.
- Tabla de servicios de `docker-compose.yml`: imagen exacta, versión y función.
- Dependencias reales (`requirements.txt`).
- Etapas que ejecuta `python3 main.py`, en orden, y opciones como `--sin-descarga`.
- **Cálculo de distancias:** método exacto y error máximo frente a `ST_Length(geography)` (de la auditoría).
- **Reproducibilidad:** fecha y hora de la ejecución reportada, GeoJSON versionados y comando para reproducirla.

### 6. Base de datos (1,5 páginas) — criterio 1.0
- Diagrama legible, exportado en formato vectorial (PDF o SVG). **Las notas del diagrama deben coincidir con el texto** (en el borrador anterior, una nota decía "fase 3" cuando el cálculo era de la fase 2).
- Tabla `tabla | geometría | contenido | rol en la fase 2 | filas`.
- Llaves foráneas, índices GiST y por qué las amenazas no tienen llave foránea hacia la red.
- Explicar cualquier cifra que llame la atención (por ejemplo, más filas de calidad del aire que estaciones en la red: indicar cuántas estaciones se cargan y por qué).

### 7. Infraestructura (1 página) — criterios 2.0, 2.1 y 2.2
- **Obtención:** script, fuente (conjunto de datos de la fase 1), algoritmo de construcción del grafo.
- **Estructura del JSON:** tabla `archivo | geometría | campos principales con un ejemplo real`, y referencia al `.md` de cada archivo.
- **Carga:** scripts, orden de carga (por las llaves foráneas) e idempotencia.
- **Debe responder:** qué es un nodo, cuántos hay por categoría, por qué esa conectividad, si el grafo es conexo y si es dirigido.

### 8. Metadata (1,5 páginas) — criterios 3.0, 3.1 y 3.2
Para **cada** fuente: script, API o servicio, **fecha o ventana temporal de los datos**, filtro espacial (rectángulo de estudio con coordenadas, una sola vez para todo el informe), qué se extrae, transformaciones y número de registros.
- **Debe responder:** ¿por qué esta fuente importa para el vuelo? ¿Cómo se usará en la fase 3? ¿Qué limitaciones tiene? Por ejemplo: Censo 2017 (indicar si hay un censo más reciente disponible a nivel de manzana) y el subregistro de antenas en OpenStreetMap.
- Estructura del JSON (campos principales) y carga.

### 9. Amenazas (1,5 páginas) — criterios 4.0, 4.1 y 4.2
Igual que la metadata, más:
- Tabla `script | fuente y ventana | modelo geométrico | umbral | eventos totales | eventos activos`.
- **Significado de `exceeds`** y dónde se aplica el umbral (ETL o ruteo).
- Estructura común de los GeoJSON de amenazas (tabla de campos).
- **Debe responder:**
  - Incendios: qué sensor, qué niveles de confianza y por qué esa ventana temporal.
  - Sismos: por qué un sismo es amenaza para la operación (daño en tierra, no al UAV en vuelo) y de dónde sale la fórmula del radio (si es heurística del equipo, decirlo).
  - Viento y lluvia: tamaño de celda, hora del pronóstico, origen del umbral (ficha del UAV de referencia, coherente con el supuesto del UAV).
  - ¿Alguna amenaza activa tocó la red en la ejecución reportada?

### 10. Ruta base con `pgr_dijkstra` (1,5 páginas) — criterio 6.1
- Formulación breve: grafo, costo c(e) = longitud, origen, destino.
- **Consulta SQL exacta** que ejecuta el código (copiada del repositorio, no reescrita).
- Valor real de `directed` y su justificación. Si el grafo es no dirigido, usar `directed := false` o explicar por qué `directed := true` con `cost = reverse_cost` es equivalente.
- Cómo se exporta la ruta al sitio (archivo GeoJSON y campos).
- **Por qué es el peor caso**, en dos o tres frases, apoyadas en la sección 5 de esta guía si se hace el análisis. Evitar afirmaciones sin datos (como "duplica el consumo de batería").
- Si existe k=2, ver la sección 3.4.

### 11. Plataforma web (1 a 1,5 páginas) — criterios 5.0, 5.1 y 6.2
- Cómo se accede (URL local y comando).
- Lista de capas por grupo (infraestructura, metadata, amenazas, ruta).
- **Captura con leyenda visible** donde se vea la ruta `pgr_dijkstra` rotulada como peor caso.
- Interacción: selección de destino y qué información muestra el panel.
- Si el sitio calcula tiempo de vuelo o batería, indicar la fórmula, los parámetros y su fuente, y que coincidan con el supuesto del UAV de referencia. Si no aporta a la fase 2, mencionarlo en una línea.
- **Evitar:** describir la interfaz con adjetivos ("tipo MATLAB", "estándar profesional"); describir funciones, no impresiones.

### 12. Verificación (0,5 a 1 página)
- Tabla de pruebas automáticas **agrupadas por tipo**, con número de pruebas y qué comprueba cada grupo: formato GeoJSON, documentación de campos, conectividad, validez de geometrías, coincidencia de la ruta precalculada con `pgr_dijkstra` en vivo, etc.
- Resultado en forma neutra: "las [n] pruebas se ejecutaron sin fallos en la ejecución del [fecha]".
- Pruebas recomendadas si no existen: continuidad de la ruta, suma de costos igual a `agg_cost`, error de longitud frente a `geography`, y comparación con un Dijkstra independiente (por ejemplo, en Python puro) sobre el mismo grafo.

### 13. Resultados de la fase 2 (2 páginas)
- Tabla de conteos por tabla.
- Tabla de rutas base: `destino | longitud (km, 2 decimales) | número de aristas | (opcional) km expuestos por capa`.
- Una figura de la ruta hacia un destino representativo, con leyenda, escala y norte, y las capas relevantes.
- Respuesta explícita a P1, P2 y P3.

### 14. Discusión, limitaciones y proyección a la fase 3 (1,5 páginas)
- **Discusión:** qué muestran los resultados sobre la red y sobre la ruta base.
- **Limitaciones**, cada una con su efecto:
  - Red de k vecinos: crea cuellos de botella artificiales.
  - Datos en vivo: los resultados corresponden a una ejecución.
  - OpenStreetMap subregistra antenas: sobreestima las zonas sin cobertura.
  - Censo 2017: puede no reflejar la población actual.
  - Umbrales y radios supuestos.
  - Red bidimensional, sin energía.
- **Proyección a la fase 3** (máximo una página, en futuro, sin resultados): cómo entrarán la metadata y las amenazas al costo de las aristas, qué algoritmo se usará para obtener rutas alternativas y cómo se medirá la resiliencia contra esta línea base.

### 15. Conclusiones (0,5 páginas)
- Responder a P1, P2 y P3 con datos.
- Una frase sobre qué deja lista esta fase para la siguiente.
- **Evitar:** repetir el resumen o autoevaluarse.

### Referencias
Ver la sección 8 de esta guía.

### Anexo A: correspondencia con la pauta
Tabla `criterio de la pauta | sección del informe | archivos del repositorio`. **Sin columna de puntaje ni de calificación.**

Si la pauta oficial contiene estos criterios, úsalos tal como aparecen: 1.0 bd; 2.0, 2.1 y 2.2 infraestructura; 3.0, 3.1 y 3.2 metadata; 4.0, 4.1 y 4.2 fallas; 5.0 y 5.1 sitio web; 6.1 algoritmo de ruteo; 6.2 muestra ruta; 7.0 main; 8.0 compatibilidad (Docker). **Verifica los nombres con la pauta original** antes de copiarlos.

### Anexo B (opcional)
Consultas SQL completas, extracto del log de ejecución y estructura de carpetas del repositorio.

---

## 5. Análisis recomendado: exposición descriptiva de la ruta base

Este análisis convierte "peor caso" en un dato **sin salir de la fase 2**: no cambia la ruta, solo la describe superponiéndola a las capas.

Para cada ruta base, calcular los km que pasan por:
- Manzanas con densidad sobre el umbral.
- Zonas fuera de la cobertura celular estimada.
- Zonas de amenazas activas (`exceeds = true`), por tipo.

```sql
-- Ejemplo: km de la ruta hacia un destino sobre manzanas densas
WITH ruta AS (
  SELECT e.geom
  FROM pgr_dijkstra('SELECT id, source, target, cost, reverse_cost FROM infra_edge',
                    :origen, :destino, directed := false) d
  JOIN infra_edge e ON e.id = d.edge
),
densas AS (
  SELECT ST_Union(geom) AS geom FROM <tabla_manzanas> WHERE density_hab_km2 > <umbral>
)
SELECT SUM(ST_Length(ST_Intersection(r.geom, z.geom)::geography)) / 1000.0 AS km_sobre_manzanas_densas
FROM ruta r, densas z;

-- Fuera de cobertura: longitud de la ruta menos la longitud dentro de la unión de coberturas
-- Amenazas activas: misma lógica con la unión de geometrías de threat_event WHERE exceeds
```

Reportar el resultado en la tabla de rutas de la sección 13. Redactarlo así: "la ruta de menor longitud recorre X km sobre manzanas densas…". **No** concluir nada sobre qué ruta sería mejor; eso es la fase 3.

---

## 6. Estilo y redacción

### 6.1 Reglas
- Español formal, en tercera persona o impersonal ("se implementó", "el script calcula").
- Una idea por párrafo. Frases cortas.
- Cada afirmación técnica va respaldada por código, dato o cita.
- Números con coma decimal y punto de miles (14,41 km; 2.500 hab/km²), con el mismo número de decimales para la misma magnitud en todo el documento.
- Unidades del SI con espacio (120 m, 8 m/s).
- Código, nombres de archivos, tablas y campos en fuente monoespaciada.
- Toda tabla y figura numerada, con título y citada en el texto antes de aparecer.
- Siglas definidas la primera vez: UAV, SINCA, ETL, DAN, SRTM, INE, OSM, FIRMS.
- Usar un solo término para cada concepto en todo el documento (ver 6.2).

### 6.2 Glosario de términos únicos

| Usar | No usar |
|---|---|
| UAV | dron, RPAS, aeronave (salvo al citar la DAN: "RPAS en la terminología de la DGAC") |
| ruta base, línea base | ruta oficial, ruta geométrica |
| arista, corredor | tramo 3D, aerovía |
| amenaza | falla, contingencia, catástrofe (salvo en nombres propios de criterios de la pauta) |
| metadata | metadatos ambientales, variables ciberfísicas |
| `pgr_dijkstra` | "el algoritmo oficial" |

### 6.3 Frases y contenidos prohibidos
- Puntajes, calificaciones o juicios sobre la nota ("60/60", "bien logrado", "aprobado con distinción", "cumple el 100 % de la pauta").
- Superlativos y adjetivos de venta: "exhaustivo", "robusto", "de estándar profesional", "innovación", "máxima", "inteligente", "ciberfísico".
- Afirmaciones absolutas sin fuente: "100 % de ceguera vertical", "duplica el consumo", "destrucción del dron".
- Normativa no verificada: atribuir a la DAN 151 umbrales de viento, reservas de batería u otros valores sin citar el artículo exacto.
- Atribuir a un estándar algo que no dice (por ejemplo, relacionar 2 mm/h con un grado IP sin fuente).
- Llamar "disjuntas" a rutas que comparten aristas.
- Promesas detalladas de la fase 3 (ACO, GA, RRT*, tiempos de reconfiguración).
- Enlaces locales (`file:///c:/Users/...`). Usar rutas relativas del repositorio (`ruteo/ruta_dijkstra.py`).
- Diagramas en arte ASCII en el informe final; usar figuras reales.
- Referencias a la rúbrica en los títulos ("Punto 3 de la rúbrica"). La correspondencia va en el Anexo A.

---

## 7. Figuras y tablas

- **Mínimo esperado:** arquitectura (1), diagrama de la base de datos (1), mapa con la ruta base y las capas (1 o 2), captura del sitio web (1), y tablas de fuentes, conteos y rutas.
- **Mapas:** leyenda, escala, norte, origen y destino marcados, y fuente del mapa base (© OpenStreetMap contributors).
- **Capturas del sitio:** legibles, recortadas a lo relevante, con la ruta base visible y rotulada.
- Exportar gráficos y diagramas en vectorial cuando sea posible.
- Las cifras de las figuras deben coincidir exactamente con las tablas.

---

## 8. Referencias

### 8.1 Reglas
- Un solo estilo (IEEE numérico recomendado, como el borrador PDF).
- Toda fuente web con "Consultado el [fecha]".
- Enlaces directos al documento, no a portadas.
- **Verificar cada referencia** (autores, título, revista, volumen, páginas, DOI) antes de incluirla. No incluir referencias que no se usen en el texto.

### 8.2 Referencias correctas del borrador PDF (conservar)
- Akgün, Erkut y Batta, "On finding dissimilar paths", *European Journal of Operational Research*, 121(2), 232–246, 2000.
- Kosior, Przystałka y Panfil, "Adaptive path planning for UAV-based pollution sampling", *Applied Sciences*, 14(24), 12065, 2024. doi: 10.3390/app142412065.
- Dijkstra (1959); Yen (1971); Suurballe (1974); Bhandari (1999); JARUS SORA; Petritoli et al. (2018); Schroeder et al. (2014, VIIRS 375 m); DAN 151 ed. 3 de la DGAC; fuentes de datos SINCA, OpenTopoData, IDE SMA, Overpass, FIRMS, EMSC, Open-Meteo y MET Norway.

### 8.3 Referencias erróneas del borrador MD (NO usar)
- "Kosior, A., et al. (2024) … IEEE Transactions on Aerospace and Electronic Systems": revista y título incorrectos.
- "Akgün, V., et al. (2000). A min-max routing algorithm … EJOR 126(3)": no es el artículo que se usa.

### 8.4 Referencias que conviene agregar
- RFC 7946 (GeoJSON), IETF, 2016.
- Documentación de pgRouting 3.8 (`pgr_dijkstra`) y de PostGIS 3.5.
- El decreto del plan de descontaminación de Concón, Quintero y Puchuncaví (verificar número y año).
- Ficha técnica del UAV de referencia.

---

## 9. Formato (LaTeX)

- Conservar la plantilla del borrador PDF (portada UDP, encabezados).
- Índice: con secciones de dos dígitos, ampliar el ancho del número (`tocloft`: `\cftsecnumwidth`) para que no quede pegado al título.
- Consultas SQL en entorno `lstlisting` con título y numeración.
- Tablas con `booktabs`.
- Las tablas largas no deben cortarse entre páginas sin repetir el encabezado (`longtable`).

---

## 10. Lista de verificación final

### Fidelidad
- [ ] Todo número del informe está en `ficha_hechos_fase2.md` con su origen.
- [ ] Nombres de tablas, campos, archivos y scripts coinciden con el repositorio.
- [ ] La consulta SQL de la sección 10 está copiada del código.
- [ ] Los parámetros del UAV del informe coinciden con los del sitio web.
- [ ] Fecha y hora de la ejecución reportada están indicadas.

### Alcance
- [ ] No hay W(e), α, λ, R, ΔR, Monte Carlo ni comparación de algoritmos fuera de la sección de proyección.
- [ ] La ruta base usa solo la longitud como costo y el informe lo dice explícitamente.
- [ ] Las hipótesis se reemplazaron por preguntas de diseño respondidas con datos.

### Calidad académica
- [ ] Resumen con resultado numérico.
- [ ] Introducción con problema citado, alcance, contribución y estructura.
- [ ] Supuestos numerados y justificados.
- [ ] Cada fuente tiene fecha, filtro, transformación, número de registros y limitaciones.
- [ ] Limitaciones con su efecto.
- [ ] Referencias verificadas y en un solo estilo.

### Forma
- [ ] Ninguna autoevaluación ni puntaje.
- [ ] Ninguna frase de la lista prohibida.
- [ ] Figuras con leyenda; mapas con escala y norte.
- [ ] Terminología única según el glosario.
- [ ] Ortografía del nombre del profesor, integrantes y código del curso revisada.
- [ ] Sin enlaces locales ni arte ASCII.

---

## 11. Qué debe entregar el agente

1. `docs/ficha_hechos_fase2.md`: la ficha de hechos (sección 2.3).
2. La tabla de discrepancias de la sección 2.1 completada con el valor real.
3. El informe en LaTeX (o Markdown, si así se acordó), siguiendo la estructura de la sección 4.
4. Una lista de **dudas abiertas**: todo dato que no se pudo verificar o que requiere decisión del equipo, por ejemplo:
   - si se incluye la ruta k=2;
   - si se hace el análisis de exposición;
   - los artículos exactos de la DAN 151 que se citan;
   - el número del decreto del plan de descontaminación.
5. Un registro de cambios respecto al borrador PDF: qué se eliminó, qué se agregó y qué números cambiaron.
