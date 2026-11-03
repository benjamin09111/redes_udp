Velocidad y autonomía no calzan. El informe calcula el tiempo de vuelo a 15 m/s, pero usa una autonomía de 26,4 km. Esa cifra corresponde a 55 min a 8 m/s; a 15 m/s serían ≈49,5 km. Con eso, la conclusión de que “ida y vuelta a Puchuncaví supera la autonomía” cambia según qué valor usen. Elijan una velocidad y úsenla en todo el informe y el sitio.
P1–P3 se responden en las conclusiones, pero nunca se plantean. Agréguenlas al final de la sección de objetivos.
La exposición de la ruta base es cualitativa. Etiquetas como “alta densidad urbana” o “sombra C2” no son una medición. Si pueden, reporten los km sobre manzanas densas y fuera de cobertura (está la consulta en la guía anterior). Eso convierte “peor caso” en un dato.
Viento. El informe dice que 14 m/s “deriva del límite de control del UAV”, pero la ficha del Matrice 350 que citan indica 12 m/s. O cambian el umbral a 12 m/s o declaran 14 m/s como supuesto del equipo.
Lluvia. La frase “protege contra pérdida de estanqueidad (IP43/IP54)” no tiene fuente, y el UAV de referencia es IP55. Elimínenla o cítenla.
“DAN 151 Art. 9” como autorización del aeródromo: verifiquen ese artículo en la norma o quítenlo y dejen la autorización como supuesto.
“57 pruebas automatizadas” en el objetivo 7: confirmen que existen en el repositorio con ese número.
Tono de la introducción. “Oportunidad sin precedentes” y “necesidad imperiosa” restan seriedad; reemplácenlos por afirmaciones concretas.

# Evaluación y correcciones del informe final de la Fase 2

**Archivo evaluado:** `informe_final.md` (fuente LaTeX, 764 líneas)
**Pauta:** TG2, 16 criterios, 60 puntos
**Destinatario:** agente de desarrollo. Cada corrección indica la línea del archivo, el problema y la acción.

---

## 0. Veredicto e instrucciones

**Estado general:** el informe ya respeta el alcance de la fase 2 (solo `pgr_dijkstra` con costo = longitud) y la red es coherente con el código (237 nodos y 633 aristas). Es una buena base. Sin embargo, tiene:

- **riesgos de puntaje** en los criterios que piden "explicar estructura y valores", "indicar script" y en los de 6 puntos (5.1, 6.2, 7.0 y 8.0), por falta de evidencia concreta;
- **inconsistencias numéricas** que un evaluador puede detectar con una calculadora;
- **afirmaciones sin respaldo** (normativa, estándares y frases como "confirmó cuantitativamente" sin números);
- **secciones faltantes** para un nivel de magíster: resumen, marco conceptual, supuestos numerados, definición de P1 a P3 y verificación;
- **9 referencias en la bibliografía que nunca se citan en el texto**.

**Reglas para el agente:**

1. Toda cifra nueva o corregida debe salir del código o de una ejecución real (`python3 main.py --sin-descarga`). Si no se puede verificar, se elimina o se declara como supuesto.
2. No agregar puntajes, autoevaluaciones ni adjetivos de venta.
3. No agregar contenido de la fase 3 (W(e), R, ΔR, comparación de algoritmos) fuera de la subsección de proyección.
4. Entregar al final la lista de la sección 9.

---

## 1. Prioridad 1: criterios de la pauta en riesgo

| Criterio                | Pts   | Estado actual                           | Qué falta                                                                                                                                                                 | Acción                                                                                                                                                                                                                                        |
| ----------------------- | ----- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0 bd                  | 3     | Diagrama y mención de `schema.sql`      | Evidencia de que crea la BD **desde cero**. Además, la nota del diagrama dice que la afectación se calcula "en la fase 3", lo que contradice el texto (sec. 5.1, punto 4) | Agregar un extracto breve de `schema.sql` (`DROP/CREATE`, extensiones y `CREATE TABLE infra_edge`) y el comando que lo ejecuta. **Regenerar el diagrama** con la nota corregida                                                               |
| 2.0 infraestructura     | 3     | Script nombrado                         | Ruta exacta de los archivos de salida y cómo se ejecuta el script por separado                                                                                            | Indicar `infraestructura/extraer_infraestructura.py` → `infraestructura/{nodos,aristas,zonas_urbanas}.geojson` y el comando individual                                                                                                        |
| 2.1 explica JSON        | 3     | Tabla con campos y ejemplos             | No muestra el bloque `etl` ni un feature real                                                                                                                             | Agregar un listado JSON corto: un feature de `nodos.geojson` más el bloque `etl`                                                                                                                                                              |
| 2.2 carga infra         | 3     | Nombra los cargadores                   | No indica **dónde están** ni cómo se ejecutan                                                                                                                             | Indicar la ruta de cada `cargar_*.py` y el comando                                                                                                                                                                                            |
| 3.0 metadata            | 3     | Tabla de scripts                        | **No nombra los GeoJSON de salida** ni el endpoint consultado                                                                                                             | Agregar a la Tabla 5 (`tab:metadata`) una columna "archivo de salida" y la URL o servicio exacto                                                                                                                                              |
| 3.1 explica JSON        | 3     | Lista de nombres de campos              | **Sin tipos, unidades ni valores de ejemplo.** El criterio dice "explica estructura **y valores**". Tampoco menciona los `.md` de cada archivo                            | Convertir la sec. 7.2 en tabla `archivo · campo · tipo · unidad · ejemplo real` y citar los `.md`                                                                                                                                             |
| 3.2 carga metadata      | 3     | Nombra los cargadores (sec. 7.3)        | Correcto, falta el comando                                                                                                                                                | Agregar el comando                                                                                                                                                                                                                            |
| 4.0 amenazas            | 3     | Tabla de scripts                        | Archivos de salida y endpoint                                                                                                                                             | Igual que en 3.0                                                                                                                                                                                                                              |
| 4.1 explica JSON        | 3     | Tabla de estructura común               | Sin valores de ejemplo reales; no menciona los `.md`                                                                                                                      | Agregar una columna "ejemplo" y un feature JSON real (por ejemplo, una celda de viento)                                                                                                                                                       |
| 4.2 carga amenazas      | 3     | Bien                                    | Comando                                                                                                                                                                   | Agregar el comando                                                                                                                                                                                                                            |
| 5.0 sitio Leaflet       | 3     | Bien                                    | —                                                                                                                                                                         | —                                                                                                                                                                                                                                             |
| **5.1 visualiza datos** | **6** | Una sola captura (`img_plataforma.PNG`) | Evidencia visual de las **tres** familias de capas                                                                                                                        | Agregar 3 capturas con leyenda visible: infraestructura, metadata y amenazas (puede ser una figura con 3 subfiguras)                                                                                                                          |
| 6.1 `pgr_dijkstra`      | 3     | Consulta mostrada                       | Verificar que la consulta esté **copiada del código** (usa `destino_id` como marcador)                                                                                    | Copiar la consulta literal de `ruteo/ruta_dijkstra.py` e indicar el parámetro real (`%s`)                                                                                                                                                     |
| **6.2 muestra ruta**    | **6** | Una captura                             | La figura debe mostrar la ruta con su rótulo de "peor caso" legible y la leyenda. La tabla de capas dice "magenta", así que la captura debe coincidir                     | Revisar la captura y agregar un acercamiento a la ruta y al panel de métricas                                                                                                                                                                 |
| **7.0 main**            | **6** | Descripción en prosa                    | Evidencia de ejecución                                                                                                                                                    | Agregar la lista de etapas de `main.py` en orden y un **extracto del log real** (conteos por tabla y rutas calculadas)                                                                                                                        |
| **8.0 docker**          | **6** | Tabla de servicios                      | **Requisitos del evaluador y comandos exactos desde cero.** No queda claro si `main.py` corre en el anfitrión (y entonces exige Python allí) o dentro del contenedor      | Agregar la subsección "Ejecución desde cero": requisitos (Docker y Docker Compose; Python 3 en el anfitrión solo si `main.py` corre fuera del contenedor), clonar, ejecutar, URL. Confirmar que todo el ETL corre dentro del contenedor `etl` |

> **Archivo de imagen:** la figura usa `img_plataforma.PNG` (con mayúsculas) y la macro `\imagen` imprime "Falta la imagen" si el archivo no existe. En Linux los nombres distinguen mayúsculas. **Compilar y revisar que ninguna figura salga como recuadro de "Falta la imagen".**

---

## 2. Prioridad 2: inconsistencias numéricas y técnicas

### 2.1 Velocidad y autonomía del UAV (líneas 583, 599, 676, 699)

- **Problema:** el tiempo de vuelo se calcula a 15 m/s (54 km/h), pero la autonomía usada es 26,4 km "(55 min)". 55 min a 15 m/s son **49,5 km**; 26,4 km corresponden a 55 min a **8 m/s**. Por eso la conclusión de que "ida y vuelta a Puchuncaví (28,82 km) supera la autonomía" depende de qué cifra se tome.
- **Acción:** definir una sola velocidad de crucero y una sola autonomía en un supuesto (ver 4.3, S6), citando la ficha técnica `\cite{dji}`, y usarlas en todo el informe y en el sitio web. Considerar además una reserva de batería, declarada como supuesto. Recalcular la discusión (l. 676) y la limitación (l. 699).

### 2.2 Exposición de la ruta base: "cuantitativa" sin números (líneas 116, 678, 692)

- **Problema:** se afirma que la ruta "evidencia cuantitativamente" y "confirmó cuantitativamente" su condición de peor caso, pero la Tabla `tab:resultados_sinca` solo trae etiquetas cualitativas ("Alta densidad urbana", "Despejado", "sombra C2").
- **Acción:** reemplazar la columna cualitativa por columnas numéricas: **km sobre manzanas > 2.500 hab/km²**, **km fuera de cobertura** y **km dentro de amenazas activas**. La sección 583 dice que el modal web ya calcula una "auditoría de exposición", así que usar esa misma lógica. Si no se pueden calcular, cambiar "cuantitativamente" por "cualitativamente". Consulta sugerida:

```sql
WITH ruta AS (
  SELECT e.geom FROM pgr_dijkstra(
    'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
    (SELECT id FROM infra_node WHERE code='base_scer'), :destino, directed := false) d
  JOIN infra_edge e ON e.id = d.edge),
densas AS (SELECT ST_Union(geom) g FROM meta_census_block WHERE density_hab_km2 > 2500),
cobertura AS (SELECT ST_Union(coverage_geom) g FROM meta_telecom_antenna)
SELECT
  SUM(ST_Length(ST_Intersection(r.geom, d.g)::geography))/1000 AS km_densas,
  SUM(ST_Length(ST_Difference(r.geom, c.g)::geography))/1000  AS km_sin_cobertura
FROM ruta r, densas d, cobertura c;
```

### 2.3 Rango de distancias en la discusión (línea 676)

- **Problema:** "Todas las rutas de ida hacia Quintero y Ventanas se sitúan entre 1,25 km y 7,80 km". 1,25 km es Unimarc (Tabla `tab:resultados_otros`), no una estación, y CESFAM Las Ventanas mide 8,05 km, que supera el máximo declarado.
- **Acción:** separar las dos tablas en la redacción o corregir el rango con los valores reales.

### 2.4 Δz frente a altitud (líneas 631, 677)

- **Problema:** la tabla da Δz = +67,0 m hacia Puchuncaví (desnivel), pero la discusión dice "el terreno asciende hasta +67,0 msnm" (altitud absoluta). Con la base a 28 msnm, el destino estaría a ≈95 msnm.
- **Acción:** usar Δz de forma consistente. Indicar cómo se calcula Δz (cota del destino menos cota del origen, o ascenso acumulado del perfil SRTM) y de qué campo sale (`elevation_msnm` o `meta_edge_terrain`).

### 2.5 Filtro espacial de las amenazas (líneas 351, 434, 435)

- **Problema:** la sec. 7.1 dice que las capas se filtran a la caja de la bahía (≈17 × 14 km), pero se reporta un incendio "a más de 30 km de la bahía" y un sismo "a 144 km". Si se cargaron, el filtro de amenazas no es esa caja.
- **Acción:** documentar el filtro real de cada amenaza (radio o caja ampliada, en km o grados) en la Tabla `tab:amenazas`. Verificar en el código si el sismo está "mar adentro" o solo "a 144 km de la base".

### 2.6 Umbral de viento (líneas 109, 425, 436, 568)

- **Problema:** "14 m/s deriva del límite de control de actitud del UAV", pero la ficha del Matrice 350 RTK indica una resistencia al viento de 12 m/s.
- **Acción:** usar 12 m/s con `\cite{dji}`, o declarar 14 m/s como **supuesto del equipo**. Si se cambia en el código, regenerar los datos y los números.

### 2.7 Umbral de lluvia (línea 437)

- **Problema:** "protege contra pérdida de estanqueidad (estándar IP43/IP54)" no tiene fuente, y el UAV de referencia es IP55.
- **Acción:** eliminar la referencia a IP o reemplazarla por "umbral supuesto por el equipo; el UAV de referencia tiene protección IP55 \cite{dji}".

### 2.8 Conversión de radios a grados (línea 202)

- **Problema:** se usa 111.320 m por grado tanto para latitud como para longitud. Un grado de latitud mide ≈110.574 m (la diferencia es de ≈0,7 %).
- **Acción:** usar 110.574 para Δφ, o declarar la aproximación y su error.

### 2.9 Complejidad de GiST (línea 297)

- **Problema:** "tiempo sublineal O(log N)" es una afirmación que no se garantiza en general para índices R-tree/GiST.
- **Acción:** cambiar por "aceleran las consultas espaciales al filtrar candidatos por caja envolvente".

### 2.10 "Proyección de distancias Haversine" (línea 163)

- **Problema:** haversine no es una proyección.
- **Acción:** "cálculo de distancias con la fórmula de haversine".

### 2.11 Error de haversine (línea 199)

- **Acción:** reportar el **error máximo y el medio**, y la consulta usada (`MAX/AVG(ABS(length_m - ST_Length(geom::geography)))`). Hoy solo dice "error medio inferior al 0,12 %".

### 2.12 Nombre de la estación "Sur" (línea 622)

- **Acción:** usar el mismo nombre que el nodo en `nodos.geojson` en todas las tablas y en la presentación ("Sur Puchuncaví" o "Sur").

### 2.13 Geometría de `threat_event` (líneas 286 y 455)

- **Problema:** la Tabla `tab:bd` dice "Point y Polygon", y la Tabla `tab:json_amenazas` dice `Polygon`.
- **Acción:** explicar que existen las dos columnas (`point_geom` para el centro y `geom` para la zona de afectación), igual que en el diagrama.

### 2.14 Magnitud "Richter" (línea 462)

- **Acción:** usar "magnitud (M, según el catálogo)". Los catálogos sísmicos reportan Mw, ML u otras escalas, no necesariamente Richter.

### 2.15 Limitación del "istmo" (línea 700)

- **Problema:** dice "particionaría el grafo **terrestre**", pero el grafo es aéreo. Además, el cuello de botella proviene en parte de la construcción con K = 4.
- **Acción:** "particionaría la red de corredores; este cuello de botella es en parte un efecto de la construcción con K = 4 y no necesariamente del espacio aéreo real".

### 2.16 Coordenadas con doble signo (línea 351)

- **Problema:** "[−71,56; −71,38]° W" y "[−32,82; −32,69]° S" niegan dos veces.
- **Acción:** usar "longitud entre −71,56° y −71,38°, latitud entre −32,82° y −32,69° (WGS84)".

### 2.17 Notación decimal de MP2,5 (líneas 85 y 556 frente a 362)

- **Acción:** usar la misma forma en todo el documento (`MP_{2{,}5}` con coma decimal).

---

## 3. Prioridad 3: afirmaciones sin respaldo o riesgosas

| Línea   | Texto actual                                                                                      | Problema                                                                                                  | Acción                                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 105     | "autorizado bajo la DAN 151 **Art. 9**"                                                           | La DAN 151 numera sus secciones como 151.xxx (por ejemplo, 151.103 letra (g)); "Art. 9" parece incorrecto | Verificar en el PDF de la DAN 151 y citar la sección exacta, o reemplazar por "se supone la autorización de operación desde el aeródromo" (supuesto) |
| 85      | "zonas de mayor vulnerabilidad y saturación atmosférica de Chile"                                 | Superlativo sin cita                                                                                      | Citar la declaración de zona saturada o latente que corresponda, o suavizar a "zona sujeta a un plan de descontaminación"                            |
| 85, 95  | "chimeneas entre 50 m y 110 m", "fumigación costera"                                              | Se apoyan en `\cite{altura}`, una referencia vaga sin URL ni título exacto                                | Verificar que el documento lo diga y completar la referencia (título exacto, año, URL), o eliminar las cifras                                        |
| 87      | "oportunidad sin precedentes"                                                                     | Tono                                                                                                      | "permite medir directamente dentro de la pluma \cite{kosior}"                                                                                        |
| 95      | "retardo temporal crítico; solo detectan … cuando la pluma ya ha fumigado"                        | Afirmación fuerte sin fuente                                                                              | Citar o reformular: "miden a nivel de suelo y no registran la concentración en altura"                                                               |
| 96      | "no puede basarse en trayectorias geodésicas en línea recta ni en la distancia euclidiana mínima" | Contradice lo que hace la fase 2 (corredores rectos y distancia mínima)                                   | "no debería basarse **solo** en la distancia mínima"                                                                                                 |
| 106     | "asegura **matemáticamente** una red 100 % conexa"                                                | Redundante e inflado                                                                                      | "el grafo resultante tiene una sola componente conexa (verificado con `pgr_connectedComponents`)"                                                    |
| 107     | Muestreo "a 50, 80 y 110 m" y "comparar estadísticamente"                                         | Es trabajo futuro                                                                                         | Dejar explícito que corresponde a fases posteriores                                                                                                  |
| 382     | Subregistro de OSM "favoreciendo trayectorias más precavidas"                                     | En la fase 2 nada se rutea con esa capa                                                                   | "sobreestima las zonas sin cobertura"                                                                                                                |
| 506     | "benchmark … contra el cual se evaluará el ruteo **adaptativo**"                                  | Término inconsistente                                                                                     | "ruteo resiliente"                                                                                                                                   |
| 678     | "necesidad imperiosa"                                                                             | Tono                                                                                                      | "motiva incorporar el riesgo en la función de costo de la fase 3"                                                                                    |
| 711     | "garantía de ≥ 15 % de batería de reserva", "sotavento de los cerros"                             | Sin fuente y especulativo                                                                                 | Eliminar, o dejar como idea sin cifras                                                                                                               |
| 135     | "suite de **57** pruebas automatizadas"                                                           | No hay ninguna sección que las describa                                                                   | Ver 4.5: agregar la sección o eliminar la cifra                                                                                                      |
| 529–535 | "modo oscuro técnico"                                                                             | Adjetivo                                                                                                  | Eliminar                                                                                                                                             |

---

## 4. Prioridad 4: estructura faltante para nivel de magíster

### 4.1 Resumen (falta)

Agregar antes del índice, con 150 a 200 palabras: problema, qué construye la fase 2, las 8 fuentes, el tamaño de la red, la ruta base y **un resultado numérico** (por ejemplo, la longitud hacia Puchuncaví y sus km expuestos, de 2.2).

### 4.2 Marco conceptual o estado del arte (falta)

Agregar una sección breve (≈1 página) después de la introducción. Así se citan las referencias que hoy están huérfanas:

- Camino mínimo: Dijkstra `\cite{dijkstra}`; implementación en pgRouting (agregar la referencia a la documentación de pgRouting 3.8).
- Rutas alternativas, como contexto de la fase 3: Yen `\cite{yen}`, Suurballe `\cite{suurballe}`, Bhandari `\cite{bhandari}` y Akgün et al. `\cite{akgun}`.
- Riesgo en operaciones UAV: SORA `\cite{sora}`, DAN 151 `\cite{dan151}` y fiabilidad de UAV `\cite{petritoli}`.
- UAV para muestreo de contaminación: Kosior et al. `\cite{kosior}`.
- Datos: GeoJSON (agregar la referencia a RFC 7946) y VIIRS `\cite{schroeder}`.

### 4.3 Supuestos numerados (incompletos)

La sec. 3 se titula "Alcance y Supuestos", pero casi no declara supuestos. Agregar la lista S1 a S8 y citarla desde el texto:

- S1. Red: origen de los nodos (fase 1), K = 4 más 2 aristas puente, corredores rectos; **no se evaluaron otros valores de K**.
- S2. Operación desde el aeródromo: se supone autorizada (citar la sección correcta de la DAN 151 sobre aeródromos).
- S3. Altura: vuelo 2D bajo 400 pies (≈122 m) (citar la sección exacta de la DAN 151).
- S4. Población: umbral de 2.500 hab/km² como supuesto del equipo, con una justificación breve (por ejemplo, la mediana de densidad del área).
- S5. Telemetría por red celular (4G/LTE), con cobertura de 3 km por antena.
- S6. UAV de referencia: modelo, **una** velocidad de crucero, autonomía y resistencia al viento \cite{dji} (resuelve 2.1).
- S7. Umbrales y radios de amenazas (2 km, 14 o 12 m/s, 2 mm/h, fórmula del radio sísmico): supuestos del equipo.
- S8. Datos: corresponden a la ejecución del [fecha y hora UTC] (resuelve 4.6).

### 4.4 Preguntas de diseño P1 a P3 (se responden pero no se plantean)

Las conclusiones (l. 685–692) responden P1 a P3, pero nunca se definen. Agregar al final de la sección de objetivos:

- **P1.** ¿Se pueden integrar las 8 fuentes de forma automática y reproducible, con trazabilidad de origen y fecha?
- **P2.** ¿La red es conexa y permite alcanzar las 8 estaciones SINCA desde el aeródromo?
- **P3.** ¿Cuánto se expone la ruta de menor longitud a zonas de riesgo registradas por la metadata y las amenazas?

### 4.5 Sección de verificación (falta)

Agregar una subsección con una tabla `grupo de pruebas | n.º | qué comprueba` (formato GeoJSON, documentación de campos en `.md`, conectividad, validez geométrica, coincidencia de la ruta precalculada con `pgr_dijkstra` en vivo, etc.) y el resultado en forma neutra: "las [n] pruebas se ejecutaron sin fallos el [fecha]". Indicar el archivo y el comando. Si las 57 pruebas no existen, eliminar la cifra del objetivo 7.

### 4.6 Fecha de la ejecución reportada (falta)

La sec. 4.4 explica `--sin-descarga`, pero no dice **a qué ejecución corresponden las tablas**. Agregar la fecha y hora UTC de generación de los GeoJSON y confirmar que están versionados en el repositorio.

### 4.7 Limitaciones (incompletas)

Agregar a la sec. 12.2, cada una con su efecto:

- K = 4 no se comparó con otros valores, y la topología condiciona las rutas.
- Red 2D y corredores rectos.
- Haversine sobre una esfera y círculos aproximados en grados.
- Ventana de 7 días de FIRMS: puede incluir focos ya extinguidos.
- Resultados de una sola ejecución con datos en vivo.
- Umbrales y radios supuestos.

### 4.8 Proyección a la fase 3 (l. 704–712)

Mantenerla, pero sin cifras ni garantías (ver la tabla de la sección 3). Citar a Akgün et al. en el punto de rutas alternativas.

---

## 5. Referencias

1. **Nueve referencias no se citan en el texto:** `akgun`, `dijkstra`, `yen`, `suurballe`, `bhandari`, `sora`, `petritoli`, `schroeder` y `dji`. Con `thebibliography` se imprimen igual, y un evaluador lo nota. Citarlas (ver 4.2 y 2.1) o eliminarlas.
2. **Referencias que faltan:** documentación de pgRouting 3.8 (`pgr_dijkstra`, `pgr_connectedComponents`), documentación de PostGIS 3.5 y RFC 7946 (GeoJSON), que se menciona varias veces sin cita.
3. **Mezcla de estilos:** `estaciones` está en formato APA y el resto en IEEE. Unificar en IEEE.
4. **`estaciones`:** verificar el número del decreto, la fecha de publicación y el enlace a la BCN.
5. **`altura`:** completar con el título exacto, año y URL, o eliminarla junto con las cifras que respalda.
6. **Citas faltantes en el texto:** SORA (l. 376, mencionada sin `\cite`), VIIRS (l. 421, agregar `\cite{schroeder}`), Dijkstra (sec. 9) y la ficha del UAV (cálculo de autonomía).

---

## 6. Forma y LaTeX

- **Tablas:** se carga `booktabs`, pero las tablas usan líneas verticales y `\hline`. Para nivel de magíster, migrar a `\toprule`, `\midrule` y `\bottomrule`, sin líneas verticales.
- **Etiquetas:** `fig:zoom` no describe la figura; renombrarla, por ejemplo `fig:ruta_puchuncavi`.
- **Leyendas de figuras:** toda captura de mapa debe indicar el destino, qué color es la ruta base y la fuente del mapa base (© OpenStreetMap contributors / Esri).
- **Decimales:** mismo número de decimales para la misma magnitud (km con 2 decimales, porcentajes con 1).
- **Siglas:** definir la primera vez: AGL, C2, GPP, RTH, SORA, NRT y FRP.
- **Compilar dos veces** y revisar que no queden referencias `??` ni recuadros de "Falta la imagen".

---

## 7. Coherencia con la presentación

Una vez corregido el informe, la presentación debe usar exactamente las mismas cifras y términos:

- 131 registros de amenazas (98 sismos), no 130 ni 97.
- Una sola velocidad y autonomía del UAV.
- El umbral de viento definitivo (12 o 14 m/s).
- Sin láminas de hipótesis, modelo de fallas, W(e) ni resiliencia R.
- Los km de exposición de la ruta base, si se calculan (2.2).

---

## 8. Resumen de prioridades

| Prioridad | Qué                                                                                                                                                                             | Impacto                     |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| 1         | Evidencia por criterio: capturas de 5.1 y 6.2, log de `main.py` (7.0), ejecución desde cero (8.0), estructura y valores de los JSON (3.1 y 4.1), archivos de salida (3.0 y 4.0) | Puntaje directo             |
| 2         | Velocidad y autonomía, exposición numérica, rango de distancias, Δz, filtro de amenazas, umbrales de viento y lluvia                                                            | Credibilidad ante preguntas |
| 3         | DAN 151 "Art. 9", cifras sin fuente, tono                                                                                                                                       | Credibilidad                |
| 4         | Resumen, marco conceptual, supuestos S1 a S8, P1 a P3, verificación, fecha de la ejecución                                                                                      | Nivel de magíster           |
| 5         | Referencias huérfanas y estilos                                                                                                                                                 | Rigor formal                |

---

## 9. Qué debe entregar el agente

1. El informe corregido.
2. Una tabla de cambios `n.º de corrección de esta guía | línea | antes | después | fuente del dato (archivo:línea, consulta o log)`.
3. Las cifras nuevas (exposición en km, error máximo de haversine, número de pruebas, fecha de la ejecución) con su consulta o comando de origen.
4. Una lista de **decisiones pendientes del equipo**, por ejemplo:
   - velocidad de crucero definitiva;
   - umbral de viento de 12 o 14 m/s;
   - sección de la DAN 151 que se cita;
   - si se mantiene la referencia `altura`.
5. Confirmación de que el PDF compila sin `??` ni imágenes faltantes.
