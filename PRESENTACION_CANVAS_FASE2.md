# Guion y Estructura Formal: Presentación Canvas Fase 2

Este documento contiene la estructura temática diapositiva por diapositiva para la **presentación de evaluación de la Fase 2**. Cada lámina responde con evidencia directa del código, respaldo experimental y formulación matemática a los criterios de la rúbrica oficial.

---

## Índice de Diapositivas vs. Criterios de Evaluación

| Lámina | Título / Tema | Criterio Rúbrica Canvas | Ponderación |
| :---: | :--- | :--- | :---: |
| **1** | Portada e Identificación del Proyecto | General / Integrantes | — |
| **2** | Arquitectura del Entorno Docker (Postgres, PostGIS, pgRouting) | Criterio 1: Base Docker | 2 pts |
| **3** | Modelo Relacional de Base de Datos y Script `.sql` | Criterio 2: Explicar BD y DDL | 2 pts |
| **4** | Pipeline ETL: Ingesta y Carga de Metadata ($n = 4$) | Criterios 3.1 & 3.2: $n$-Metadata | 8 pts |
| **5** | Pipeline ETL: Ingesta y Carga de Amenazas / Fallas ($n = 4$) | Criterios 4.1 & 4.2: $n$-Fallas | 8 pts |
| **6** | Modelamiento Físico y Operacional de Fallas Dinámicas | Criterio 5.1: Modelos de Fallas | 3 pts |
| **7** | Formulación Matemática de Asignación de Pesos en Aristas | Criterio 5.2: Asignación de Pesos | 2 pts |
| **8** | Conversión de Metadata en Restricciones y Preferencias por Defecto | Criterios 6.1 & 6.2: Restricciones | 5 pts |
| **9** | Fundamento Teórico: Kosior et al. (2024) y Akgün et al. (2000) | Criterios 7.1 & 7.2: Algoritmo y Paper | 10 pts |
| **10** | Generación de Rutas con Dijkstra en pgRouting ($k \ge 2$) (Peor Caso) | Criterio 8: Rutas Dijkstra | 4 pts |
| **11** | Generación de Rutas con Algoritmo Resiliente ($k \ge 2$) | Criterio 9: Rutas Resilientes | 4 pts |
| **12** | Formulación de la Métrica Cuantitativa de Resiliencia $\mathcal{R}(K)$ | Criterio 10: Métrica de Resiliencia | 6 pts |
| **13** | Plataforma Web Interactiva: Dupla (Inicio, Objetivo) y Restricciones | Criterio 11.1: Plataforma Web | 4 pts |
| **14** | Análisis del Diferencial de Resiliencia ($\Delta \mathcal{R}$) y Conclusiones | Criterio 11.2: Diferencial $\Delta \mathcal{R}$ | 2 pts |
| **TOTAL** | **Evaluación Integral de la Fase 2** | **Rúbrica Completa** | **60 pts** |

---

### Diapositiva 1: Portada
* **Título:** Sistema Ciberfísico de Ruteo Resiliente UAV en la Bahía de Quintero
* **Subtítulo:** Fase 2: Pipeline ETL, Base de Datos PostGIS/pgRouting y Planificación Adaptativa Multiobjetivo
* **Curso:** Redes de Computadores / Ruteo y Redes Resilientes
* **Integrantes:** Benjamín Morales, Benjamin Polanco, Benjamín Aceituno, Aldo Morales
* **Repositorio GitLab UDP:** `https://giteit.udp.cl/benjamin09111/redes_udp`

---

### Diapositiva 2: Entorno Dockerizado y Reproducibilidad (Criterio 1 · 2 pts)
* **Objetivo:** Garantizar compatibilidad estricta de versiones, portabilidad y aislamiento completo.
* **Servicios orquestados en `docker-compose.yml`:**
  * `db`: Imagen `pgrouting/pgrouting:16-3.5-3.8.0` (PostgreSQL 16.9 + PostGIS 3.5.2 + pgRouting 3.8.0).
  * `etl`: Imagen `python:3.12.15-slim` con `psycopg==3.2.13` para la ingesta y persistencia.
  * `web`: Servidor HTTP ligero para el visualizador Leaflet en puerto 8000.
* **Comandos de Ejecución y Validación:**
  ```bash
  # Pipeline completo de extracción, carga a BD y cálculo de rutas
  python3 main.py

  # Suite de verificación de consistencia geoespacial y base de datos
  docker compose run --rm etl python tests/verificar.py
  ```

---

### Diapositiva 3: Modelo Relacional de Base de Datos Espacial (Criterio 2 · 2 pts)
* **Esquema Relacional (`bd/schema.sql`):**
  * `infra_node`: 237 vértices clasificados (`base`, `sinca`, industrias, salud, educación).
  * `infra_edge`: 633 corredores aéreos con topología de red (`source`, `target`, `length_m`, `geom`).
  * `urban_zone`: 8 polígonos urbanos RFC 7946 antihorarios.
  * **4 tablas de metadata:** `meta_air_quality`, `meta_edge_terrain`, `meta_census_block`, `meta_telecom_antenna`.
  * **1 tabla unificada de contingencias:** `threat_event` con geometrías de polígono e índices espaciales GiST.
* **Diagrama ER:** Disponible en `bd/bd_diagrama.png` (generado desde `bd/bd_diagrama.puml`).

---

### Diapositiva 4: Pipeline ETL de Metadata del Entorno (Criterios 3.1 & 3.2 · 8 pts)
* **Extracción y Transformación:** Scripts en Python estándar (`metadata/`):
  1. `sinca_calidad_aire.py`: Ingesta desde API SINCA (MMA) con mediciones horarias de contaminantes (PM2.5, PM10, SO2).
  2. `srtm_relieve.py`: Perfil de elevación y cálculo de desniveles ($\Delta h$) vía OpenTopoData / SRTM.
  3. `ine_manzanas.py`: 703 manzanas censales desde ArcGIS REST de la SMA con población y densidad hab/km².
  4. `osm_antenas.py`: Extracción vía Overpass API de 25 mástiles y torres celulares con radio de cobertura C2.
* **Carga (`cargar_*.py`):** 4 cargadores directos a PostGIS con control de idempotencia y unicidad.

---

### Diapositiva 5: Pipeline ETL de Amenazas en Tiempo Real (Criterios 4.1 & 4.2 · 8 pts)
* **Extracción e Ingesta:** Scripts en Python estándar (`amenazas/`):
  1. `firms_incendios.py`: Focos activos satelitales NASA FIRMS (MODIS/VIIRS) con radio de exclusión de 2 km.
  2. `csn_sismos.py`: Feed FDSN de EMSC con eventos sísmicos de autoría CSN (Chile).
  3. `openmeteo_viento.py`: Malla 4×4 de pronóstico con velocidad de viento a 10m y 120m AGL y ráfagas.
  4. `metno_lluvia.py`: Precipitaciones en malla 4×4 desde MET Norway.
* **Normalización:** Formato común `threat_event` con convención `exceeds = true` para zonas activas que degradan aristas.

---

### Diapositiva 6: Modelamiento Físico y Operacional de Fallas (Criterio 5.1 · 3 pts)
* **Modelos Físicos de Degradación de la Red UAV:**
  * **Incendio Industrial (Foco en Planta Asfaltos Quintero):**
    * *Ubicación y dimensión:* `[-71.4935, -32.7801]`, radio de exclusión térmica local de $180\text{ m}$.
    * *Mecanismo físico:* Columna térmica convectiva donde los gases calientes disminuyen drásticamente la densidad del aire ($\rho$), causando pérdida inmediata de sustentación aerodinámica ($L = \frac{1}{2}\rho v^2 S C_L$) y turbulencia que supera la envolvente de control del UAV.
    * *Hallazgo de resiliencia territorial:* Un radio de $180\text{ m}$ modela un siniestro contenido en la planta y bloquea la vía directa; un radio $\ge 450\text{ m}$ en este punto constituye un **conjunto de corte topológico (cut-set)** que aísla por completo el norte de la bahía respecto a Quintero, evidenciando un cuello de botella estructural crítico de la red vial/aérea.
  * **Sismo / Integridad Estructural:**
    * *Modelo de afectación:* Magnitud $M \ge 5.0$ con radio de afectación empírico $R = 10^{0.5M - 1.8}\text{ km}$.
    * *Mecanismo:* Riesgo de oscilación y corte de tendidos de alta tensión y desprendimiento de estructuras.
  * **Viento y Ráfagas Costeras:**
    * *Umbral operacional:* Ráfaga a 10 m o viento a 120 m AGL $> 14.0\text{ m/s}$.
    * *Mecanismo:* Deriva aerodinámica y disminución severa de la velocidad terrestre efectiva ($v_g = v_a - w$).
  * **Precipitaciones:**
    * *Umbral operacional:* Precipitación $> 2.0\text{ mm/h}$.
    * *Mecanismo:* Superación del índice de estanqueidad IPx4 de la aviónica del UAV y ceguera de sensores ópticos/LiDAR.

---

### Diapositiva 7: Asignación Matemática de Pesos en Aristas (Criterio 5.2 · 2 pts)
* **Formulación del Costo Ponderado de la Arista $e$:**
  $$W(e) = L(e) \times \left(1 + \sum_{f \in \mathcal{F}} \lambda_f \cdot \Omega_f(e)\right)$$
  Donde:
  * $L(e)$: Longitud física euclidiana/geodésica de la arista en metros (`length_m`).
  * $\Omega_f(e) \in \{0, 1\}$: Indicador de intersección espacial mediante muestreo de 5 puntos a lo largo del segmento de vuelo con los polígonos y radios de influencia.
  * **Factores de ponderación operacional ($\lambda_f$):**
    * $\lambda_{\text{incendio}} = 15.0$ (o $30.0$ ante foco de contingencia activo).
    * $\lambda_{\text{urbano}} = 6.0$ (cumplimiento mandatorio de la norma DGAC DAN 151 sobre manzanas con densidad $> 2500\text{ hab/km}^2$).
    * $\lambda_{\text{sismo}} = 4.0$ (penalización por evento sísmico en proximidad).
    * $\lambda_{\text{telecom}} = 2.5$ (vuelo fuera del cono de cobertura celular de antenas OSM, riesgo de pérdida C2).
    * $\lambda_{\text{viento}} = 2.0$ (celdas activas con ráfagas o vientos $> 14\text{ m/s}$).
    * $\lambda_{\text{lluvia}} = 2.0$ (celdas activas con precipitación $> 2\text{ mm/h}$).

---

### Diapositiva 8: Conversión de Metadata en Restricciones (Criterios 6.1 & 6.2 · 5 pts)
* **Conversión de Metadata en Restricciones (Criterio 6.1):**
  * **Población INE Censo 2017:** Cumplimiento de la norma **DGAC DAN 151** (prohibición de sobrevuelo sobre aglomeraciones). Se penalizan corredores sobre manzanas densas.
  * **Antenas OSM:** Aristas sin cobertura celular sufren penalización para asegurar enlace de telemetría y telemando (Command & Control).
* **Preferencias por Defecto del Sistema (Criterio 6.2):**
  * `evitar_incendios: TRUE` (Mandatorio por integridad física de la aeronave).
  * `evitar_zonas_pobladas: TRUE` (Mandatorio por regulación aeronáutica DAN 151).
  * `evitar_sismos_activos: TRUE`.
  * `garantizar_enlace_c2: TRUE` (Prioridad de enlace de comando).
  * `escenario_contingencia_simulado: FALSE` (Inactivo por defecto para observar la red basal; activable interactivamente para pruebas de estrés).

---

### Diapositiva 9: Fundamento Teórico y Algoritmo de Ruteo (Criterios 7.1 & 7.2 · 10 pts)
* **Paper Científico (Criterio 7.1):**
  > **Kosior, M., Przystałka, P., & Panfil, W. (2024).** *"Adaptive Path Planning for UAV-Based Pollution Sampling"*. **Applied Sciences**, 14(24), 12065. DOI: [10.3390/app142412065](https://doi.org/10.3390/app142412065).
* **Algoritmo de K Caminos Disimilares (Criterio 7.1):**
  > **Akgün, V., Erkut, E., & Batta, R. (2000).** *"On finding dissimilar paths"*. **European Journal of Operational Research**, 121(2), 232–246. DOI: [10.1016/S0377-2217(99)00214-3](https://doi.org/10.1016/S0377-2217(99)00214-3).
* **Mecanismo de Planificación Adaptativa (Criterio 7.2):**
  * Se toma como base la etapa GPP (Global Path Planner) de **Kosior et al. (2024)** para la planificación espacial sobre la matriz de costos.
  * Para generar el conjunto de $k$ alternativas ($k=2$), se aplica el **algoritmo de penalización iterativa de aristas de Akgün et al. (2000)**: una vez obtenida la ruta primaria $k=1$, las aristas pertenecientes a dicha ruta se penalizan por un factor $\times 4$, obligando a una segunda ejecución de Dijkstra a explorar trayectorias disimilares con un nivel acotado de solapamiento.

---

### Diapositiva 10: Generación de Rutas Dijkstra con `pgr_dijkstra` ($k \ge 2$) (Criterio 8 · 4 pts)
* **Definición:** Ruta base del "Peor Caso" que optimiza únicamente la distancia geométrica en km ($cost = \text{length\_m}$) e ignora metadata y amenazas.
* **Ejecución con `pgr_dijkstra` en PostgreSQL:**
  ```sql
  -- Ruta k=1 con pgr_dijkstra (longitud pura)
  SELECT d.seq, d.node, d.edge, e.length_m, d.agg_cost
  FROM pgr_dijkstra(
      'SELECT id, source, target, cost, reverse_cost FROM infra_edge',
      (SELECT id FROM infra_node WHERE code = 'base_scer'),
      (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
      directed := true
  ) AS d LEFT JOIN infra_edge e ON e.id = d.edge;

  -- Ruta k=2 mediante penalización iterativa de aristas de k=1 en SQL (factor x4.0)
  -- Aristas reales de k=1 a Puchuncaví: 3, 490, 573, 69, 71, 623, 622, 618, 616, 617, 24, 22, 584, 158, 159, 633, 574, 149, 147, 251, 253, 9
  SELECT d.seq, d.node, d.edge, e.length_m, d.agg_cost
  FROM pgr_dijkstra(
      'SELECT id, source, target,
              CASE WHEN id IN (3,490,573,69,71,623,622,618,616,617,24,22,584,158,159,633,574,149,147,251,253,9)
                   THEN cost * 4.0 ELSE cost END AS cost,
              CASE WHEN id IN (3,490,573,69,71,623,622,618,616,617,24,22,584,158,159,633,574,149,147,251,253,9)
                   THEN reverse_cost * 4.0 ELSE reverse_cost END AS reverse_cost
       FROM infra_edge',
      (SELECT id FROM infra_node WHERE code = 'base_scer'),
      (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
      directed := true
  ) AS d LEFT JOIN infra_edge e ON e.id = d.edge;
  ```
* **Aclaración Metodológica de Costo:** La función objetivo de pgRouting sigue siendo exclusivamente la **distancia física euclidiana** en metros (`cost = length_m`). La penalización de $\times 4.0$ se aplica única y transitoriamente sobre las aristas ya recorridas por $k=1$ para forzar el descubrimiento de un camino alternativo disimilar ($k=2$), sin considerar metadata ni capas de amenazas.
* **Falla Crítica Evidenciada (Peor Caso):** Al optimizar solo distancia (14,41 km), Dijkstra $k=1$ atraviesa directamente la zona de exclusión térmica industrial de Planta Asfaltos (aristas 69 y 71 dentro del foco). La alternativa $k=2$ (15,60 km) comparte el cuello de botella o rodea con penalización puramente geométrica.

---

### Diapositiva 11: Generación de Rutas con Algoritmo Resiliente ($k \ge 2$) (Criterio 9 · 4 pts)
* **Definición:** Trayectorias calculadas mediante penalización iterativa de aristas (Akgün et al., 2000) sobre la matriz de costos con riesgos operacionales.
* **Comportamiento Táctico de las $k=2$ Rutas hacia Puchuncaví:**
  * **$k=1$ (Ruta Primaria Resiliente):** Detecta el foco de calor en Planta Asfaltos y toma el corredor oriental por Loncura/valle, atravesando **0 metros de fuego**.
  * **$k=2$ (Ruta de Contingencia):** Trayectoria alternativa que comparte únicamente 4 aristas en los accesos extremos de un total de 43 aristas únicas ($90,7\%$ de disimilitud Jaccard, $84,0\%$ de aristas exclusivas en $k=2$), proveyendo un corredor de respaldo verdaderamente independiente ante bloqueos.
* **Trade-off Distancia vs. Seguridad (Aeródromo $\rightarrow$ Puchuncaví):**
  * Distancia Dijkstra: 14,41 km (cruza 2 aristas de fuego directo).
  * Distancia Resiliente: 16,46 km (+2,05 km de desvío, plenamente viable para la autonomía del UAV), logrando una trayectoria completamente despejada de fuego.

---

### Diapositiva 12: Formulación de la Métrica Cuantitativa de Resiliencia (Criterio 10 · 6 pts)
* **Formulación de Confiabilidad Probabilística Exacta:**
  * Sean $\Pi_1$ y $\Pi_2$ dos rutas que comparten un tramo común $E_C = \Pi_1 \cap \Pi_2$, con tramos exclusivos $E_1 = \Pi_1 \setminus \Pi_2$ y $E_2 = \Pi_2 \setminus \Pi_1$.
  * La ocurrencia de fallas sigue un proceso de Poisson con tasa acumulada $H(E) = \sum_{e \in E} \lambda(e) \cdot L_{\text{km}}(e)$ y probabilidad de supervivencia $S(E) = e^{-H(E)}$.
  * Para que al menos una ruta del sistema sobreviva:
    1. El tramo común $E_C$ debe sobrevivir ($S(E_C)$).
    2. Al menos uno de los tramos disyuntos ($E_1$ o $E_2$) debe sobrevivir ($1 - (1 - S(E_1))(1 - S(E_2))$).
  * **Métrica de Resiliencia Conjunta $\mathcal{R}(K) \in [0, 100\%]$:**
    $$\mathcal{R}(\Pi_1, \Pi_2) = S(E_C) \times \left[ 1 - (1 - S(E_1)) \cdot (1 - S(E_2)) \right] \times 100\%$$
* **Supuestos de Modelación Explícitos:**
  1. *Independencia condicional de fallas:* La tasa acumulada de falla es aditiva a lo largo de las aristas del corredor.
  2. *Criterio de contacto uniforme:* Si un segmento de vuelo toca el radio de influencia de una amenaza, la tasa $\lambda_f$ aplica proporcionalmente a su longitud física $L_{\text{km}}(e)$.
  3. *Parámetros $\lambda$ como supuestos operacionales relativos:* $\lambda_0 = 0.005\text{ km}^{-1}$; $\lambda_{\text{incendio}} = 5.0\text{ km}^{-1}$; $\lambda_{\text{urbano}} = 0.08\text{ km}^{-1}$; $\lambda_{\text{sismo}} = 0.05\text{ km}^{-1}$; $\lambda_{\text{telecom}} = 0.03\text{ km}^{-1}$; $\lambda_{\text{viento}} = 0.04\text{ km}^{-1}$; $\lambda_{\text{lluvia}} = 0.03\text{ km}^{-1}$.

---

### Diapositiva 13: Plataforma Web Interactiva en Leaflet (Criterio 11.1 · 4 pts)
* **Capacidades Operacionales (`http://localhost:8000/sitio_web/`):**
  * **Dupla (Inicio, Objetivo) Dinámica:** Selector categorizado con los 237 nodos de la red (13 categorías) o selección directa con clic sobre cualquier nodo del mapa (Shift + clic fija el origen).
  * **Recálculo Reactivo en Caliente:** Algoritmos ejecutados localmente en JavaScript en el navegador con tiempos de respuesta subsegundo (< 50 ms); cualquier cambio de nodo o preferencia recalcula y actualiza el trazado en vivo.
  * **Controles de Preferencias:** Checkboxes para evitar incendios, zonas pobladas (DAN 151), sismos, sombra telecom y foco de contingencia simulado, con botón de **"Valores por defecto"**.
  * **Capas Cartográficas Completas:** Visualización independiente de nodos, aristas, zonas urbanas, calidad del aire SINCA, relieve SRTM, manzanas INE, antenas OSM, sismos CSN, viento Open-Meteo, lluvia MET Norway y rutas `pgr_dijkstra` de la base de datos.

---

### Diapositiva 14: Diferencial de Resiliencia ($\Delta \mathcal{R}$) y Conclusiones (Criterio 11.2 · 2 pts)
* **Fórmula del Diferencial Cuantitativo:**
  $$\Delta \mathcal{R} = \mathcal{R}(K_{\text{resiliente}}) - \mathcal{R}(K_{\text{dijkstra}})$$

* **Tabla 1: Escenario Base (Datos Reales Satelitales y Meteorológicos - Red Basal):**
| Estación Destino SINCA | $\mathcal{R}(K_{\text{Dijkstra}})$ | $\mathcal{R}(K_{\text{Resiliente}})$ | $\Delta \mathcal{R}$ (Base) | Observación Territorial |
| :--- | :---: | :---: | :---: | :--- |
| **Campiche** | 91,2% | 91,9% | **+0,7 p.p.** | Evita sobrevuelo en manzanas censales densas |
| **La Greda** | 96,0% | 96,4% | **+0,4 p.p.** | Evita manzanas densas en acceso industrial |
| **Puchuncaví** | 87,5% | 88,9% | **+1,4 p.p.** | Reducción de vuelo sobre manzanas densas (+100 m) |
| **Ventanas** | 92,5% | 93,6% | **+1,1 p.p.** | Reducción de tramos urbanos y sombras de antenas |
| **Quintero** | 98,2% | 99,1% | **+0,9 p.p.** | Desvío perimetral de zona urbana central |
| **Centro Quintero** | 99,5% | 99,6% | **+0,1 p.p.** | Corredor periférico costero despejado |
| **Loncura** | 99,8% | 99,7% | **-0,1 p.p.** | Ruta coincidente con Dijkstra |
| **Sur** | 99,8% | 99,6% | **-0,2 p.p.** | Mínima variación por arista secundaria |
*Interpretación:* En condiciones normales actuales de la bahía (sin incendios industriales ni tormentas), la confiabilidad basal refleja la exposición acumulada a manzanas censales densas (DAN 151) y sombras de telecomunicaciones en rutas de largo alcance hacia el norte (87% a 96%). El algoritmo resiliente aporta mejoras consistentes (+0,4 a +1,4 p.p.) eliminando o mitigando la exposición urbana con desvíos geométricos mínimos (< 100 m).

* **Tabla 2: Escenario de Contingencia Simulado (Incendio Activo en Planta Asfaltos Quintero):**
| Estación Destino SINCA | Distancia Dijkstra ($k=1$) | Resiliencia Conjunto Dijkstra | Distancia Resiliente ($k=1$) | Resiliencia Conjunto Resiliente | Diferencial ($\Delta \mathcal{R}$) | Fuego en Dijkstra | Fuego en Resiliente |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Campiche** | 9,53 km | 1,3% | 11,56 km | **91,6%** | **+90,3 p.p.** | 2 aristas | **0 aristas** |
| **La Greda** | 6,71 km | 1,5% | 8,74 km | **96,2%** | **+94,7 p.p.** | 2 aristas | **0 aristas** |
| **Puchuncaví** | 14,41 km | 1,2% | 16,46 km | **88,6%** | **+87,4 p.p.** | 2 aristas | **0 aristas** |
| **Ventanas** | 7,80 km | 1,3% | 9,97 km | **93,3%** | **+92,0 p.p.** | 2 aristas | **0 aristas** |
| **Quintero** | 2,35 km | 98,2% | 2,87 km | **99,1%** | **+0,9 p.p.** | 0 aristas | 0 aristas |
| **Centro Quintero** | 1,69 km | 99,5% | 1,74 km | **99,6%** | **+0,1 p.p.** | 0 aristas | 0 aristas |
| **Loncura** | 2,35 km | 99,8% | 2,35 km | **99,7%** | **-0,1 p.p.** | 0 aristas | 0 aristas |
| **Sur** | 3,74 km | 99,8% | 3,74 km | **99,6%** | **-0,2 p.p.** | 0 aristas | 0 aristas |

* **Tabla 3: Análisis de Sensibilidad del Parámetro Supuesto $\lambda_{\text{incendio}}$ (Destino Puchuncaví):**
| $\lambda_{\text{incendio}}$ ($\text{km}^{-1}$) | Severidad Operacional Supuesta | $\mathcal{R}(K_{\text{Dijkstra}})$ | $\mathcal{R}(K_{\text{Resiliente}})$ | Diferencial ($\Delta \mathcal{R}$) | Dominancia Resiliente |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **0,5** | Humo denso y turbulencia moderada | 65,6% | 88,6% | **+23,0 p.p.** | Resiliente Domina |
| **1,0** | Foco de calor relevante y ceguera de sensores | 44,5% | 88,6% | **+44,1 p.p.** | Resiliente Domina |
| **5,0** | Incendio industrial crítico con pérdida de sustentación | 1,2% | 88,6% | **+87,4 p.p.** | Resiliente Domina |
*Conclusión de Robustez Científica:* Aunque la escala cuantitativa depende del supuesto de severidad $\lambda$, la dominancia estricta del algoritmo resiliente ($\Delta \mathcal{R} > 0$) se preserva de forma consistente en todo el espectro físico.

* **Conclusiones Metodológicas:**
  1. Ante contingencias críticas que intersectan el corredor central, Dijkstra colapsa a una confiabilidad de $\approx 1\%$ al volar a ciegas por la ruta geométrica más corta, mientras que el planificador resiliente mantiene entre **$88,6\%$ y $96,2\%$**, aportando un beneficio neto de **$+87$ a $+95$ puntos porcentuales**.
  2. En operaciones habituales sin contingencias, la red es robusta ($\approx 99\%$) y el planificador resiliente aporta mejoras acotadas pero reales al evadir aglomeraciones urbanas.
  3. El incremento en distancia ($+2,05\text{ km}$ hacia Puchuncaví) representa un trade-off plenamente admisible que garantiza la preservación de la aeronave y reduce sustancialmente el sobrevuelo de manzanas pobladas densas de acuerdo con la norma DGAC DAN 151.
