# Sistema Ciberfísico de Ruteo Resiliente UAV en la Bahía de Quintero

[![Docker](https://img.shields.io/badge/Docker-Compose%20v2-blue?logo=docker&logoColor=white)](docker-compose.yml)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.9-336791?logo=postgresql&logoColor=white)](bd/schema.sql)
[![PostGIS](https://img.shields.io/badge/PostGIS-3.5.2-brightgreen)](bd/schema.sql)
[![pgRouting](https://img.shields.io/badge/pgRouting-3.8.0-orange)](ruteo/k_dijkstra_pgrouting.sql)
[![Python](https://img.shields.io/badge/Python-3.12.15-yellow?logo=python&logoColor=white)](Dockerfile)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9.4-green?logo=leaflet&logoColor=white)](sitio_web/index.html)
[![Architecture](https://img.shields.io/badge/Architecture-Resilient%20Routing-blue)](ruteo/ruteo_resiliente.py)

> **Fase 2:** Pipeline ETL geoespacial, base de datos relacional espacial PostGIS/pgRouting, enrutamiento resiliente multiobjetivo ($k \ge 2$) y plataforma interactiva Leaflet para monitoreo atmosférico con vehículos aéreos no tripulados (UAV) en la Bahía de Quintero, Ventanas y Puchuncaví (Chile).

---

## 👥 Integrantes del Equipo
* **Benjamín Morales**
* **Benjamin Polanco**
* **Benjamín Aceituno**
* **Aldo Morales**

**Curso:** Redes de Computadores / Ruteo y Redes Resilientes — Universidad Diego Portales  
**Repositorio Oficial:** `https://github.com/benjamin09111/redes_udp.git`

---

## 🚀 Guía Rápida de Ejecución

El proyecto ofrece dos modalidades de ejecución según las herramientas instaladas en tu equipo:

### Opción A: Pipeline Completo en Docker (Recomendado)
Requiere **Docker** y **Docker Compose**. Ejecuta desde cero la descarga de datos desde las APIs en vivo, la creación de la base de datos PostGIS, la carga de datos espaciales, el ruteo pgRouting y el servidor web:

```bash
# 1. Clonar el repositorio
git clone https://github.com/benjamin09111/redes_udp.git
cd redes_udp

# 2. Ejecutar el pipeline maestro completo
python3 main.py

# Alternativa offline (si deseas usar los GeoJSON precompilados sin esperar descargas externas):
python3 main.py --sin-descarga

# 3. Ejecutar la suite de verificación integral en el contenedor:
docker compose run --rm etl python tests/verificar.py
```
El visualizador cartográfico quedará activo en: 👉 **`http://localhost:8000/sitio_web/`**

---

### Opción B: Ejecución Rápida sin Docker (Navegación Inmediata)
Si no dispones de Docker instalado en tu máquina local, puedes explorar la plataforma web interactiva y ejecutar las pruebas de datos directamente con Python estándar (librería estándar, sin dependencias externas):

```bash
# 1. Levantar el servidor web local desde la raíz del proyecto
python -m http.server 8000
```
Abre tu navegador en: 👉 **`http://localhost:8000/sitio_web/`**

Para correr la suite de verificación de consistencia RFC 7946 y documentación:
```bash
python tests/verificar.py
```
*(Valida 55/55 chequeos de archivos y estándares geoespaciales con código de salida 0).*

---

## 📋 Matriz de Especificaciones Técnicas y Módulos del Sistema

A continuación se detalla la arquitectura modular del sistema y la correspondencia con los entregables de software:

| Módulo | Especificación del Sistema | Estado | Componentes / Evidencia Técnica |
| :---: | :--- | :---: | :--- |
| **0** | **Base de Datos y Modelo Entidad-Relación**<br>Diagrama espacial y script DDL reproducible desde cero | **Operativo** | • Diagrama ER: [`bd/bd_diagrama.png`](bd/bd_diagrama.png) (código en [`bd/bd_diagrama.puml`](bd/bd_diagrama.puml))<br>• DDL SQL: [`bd/schema.sql`](bd/schema.sql) (crea 9 tablas espaciales e índices GiST) |
| **1** | **Infraestructura y Red Topológica Base**<br>Automatización de nodos y aristas a formato GeoJSON | **Operativo** | • Extractor: [`infraestructura/extraer_infraestructura.py`](infraestructura/extraer_infraestructura.py)<br>• Salidas: `nodos.geojson` (237 vértices), `aristas.geojson` (633 corredores) y `zonas_urbanas.geojson` |
| **2** | **Metadata Operacional del Entorno ($n = 4$)**<br>Un script modular por API/BD para ingesta a GeoJSON | **Operativo** | 1. [`metadata/sinca_calidad_aire.py`](metadata/sinca_calidad_aire.py) (API SINCA - MMA)<br>2. [`metadata/srtm_relieve.py`](metadata/srtm_relieve.py) (SRTM / OpenTopoData)<br>3. [`metadata/ine_manzanas.py`](metadata/ine_manzanas.py) (Censo 2017 - IDE SMA)<br>4. [`metadata/osm_antenas.py`](metadata/osm_antenas.py) (Overpass API - OSM) |
| **3** | **Amenazas y Restricciones Dinámicas ($n = 4$)**<br>Un script modular por API/BD de amenaza a GeoJSON | **Operativo** | 1. [`amenazas/firms_incendios.py`](amenazas/firms_incendios.py) (NASA FIRMS MODIS/VIIRS)<br>2. [`amenazas/csn_sismos.py`](amenazas/csn_sismos.py) (EMSC / CSN Chile)<br>3. [`amenazas/openmeteo_viento.py`](amenazas/openmeteo_viento.py) (Malla 4×4 Open-Meteo)<br>4. [`amenazas/metno_lluvia.py`](amenazas/metno_lluvia.py) (Malla 4×4 MET Norway) |
| **4** | **Diccionario Semántico y Documentación de Datos**<br>Un archivo `.md` por cada JSON que define su esquema de datos | **Operativo** | Cada `.geojson` cuenta con su respectivo `.md` especificando cada clave semántica (validado por `tests/verificar.py`). |
| **5** | **Pipeline de Carga Transaccional a Base de Datos**<br>Cargadores dedicados por dataset para persistencia PostGIS | **Operativo** | 11 cargadores independientes (`cargar_*.py` en cada directorio), con manejo de idempotencia y transacciones. |
| **6** | **Consola Web de Monitoreo Cartográfico (C2 / UTM)**<br>Plataforma Leaflet interactiva para visualización multicapa | **Operativo** | [`sitio_web/index.html`](sitio_web/index.html), [`sitio_web/app.js`](sitio_web/app.js) y [`sitio_web/estilo.css`](sitio_web/estilo.css). Contiene **12 capas cartográficas** independientes y telemetría en tiempo real. |
| **7** | **Línea Base Geodésica con `pgr_dijkstra` ($k \ge 2$)**<br>Optimización por distancia euclidiana (peor caso operacional) | **Operativo** | • Generador: [`ruteo/ruta_dijkstra.py`](ruteo/ruta_dijkstra.py) (ejecuta `pgr_dijkstra` en PostgreSQL)<br>• Consultas SQL: [`ruteo/k_dijkstra_pgrouting.sql`](ruteo/k_dijkstra_pgrouting.sql)<br>• Salida: [`sitio_web/data/ruta_dijkstra.geojson`](sitio_web/data/ruta_dijkstra.geojson) (16 Features con $k=1$ y $k=2$) |
| **8** | **Pipeline de Ejecución Maestro (`main.py`)**<br>Orquestador integral desde la raíz del proyecto | **Operativo** | [`main.py`](main.py): Orquesta descarga de APIs, importación en BD, cálculo de rutas y despliegue del servidor web. |
| **Docker** | **Contenedores y Entorno Aislado**<br>Postgres 16 + PostGIS + pgRouting con versiones fijadas | **Operativo** | [`Dockerfile`](Dockerfile) (`python:3.12.15-slim`) y [`docker-compose.yml`](docker-compose.yml) (`pgrouting/pgrouting:16-3.5-3.8.0`). |
| **Modelos** | **Modelos de Fallas y Ponderación de Costos**<br>Asignación física de riesgos y penalizaciones demográficas | **Operativo** | Documentados conceptualmente en [`bd/GUIA_BD.md`](bd/GUIA_BD.md) e implementados en [`ruteo/ruteo_resiliente.py`](ruteo/ruteo_resiliente.py). |
| **Paper** | **Fundamento Teórico y Algoritmo Resiliente**<br>Planificación adaptativa y rutas disimilares ($k \ge 2$) | **Operativo** | Basado en **Kosior et al. (2024)** y algoritmo de penalización de aristas de **Akgün et al. (2000)** ($\times 4.0$). |
| **Métrica** | **Métrica Cuantitativa de Resiliencia Conjunta**<br>Evaluación estocástica diferencial ($\Delta \mathcal{R}$) | **Operativo** | Formulación estocástica exacta Poisson/Markov: $\mathcal{R}(\Pi_1, \Pi_2) = S(E_C) \times [1 - (1 - S(E_1))(1 - S(E_2))]$. |

---

## 🔬 Fundamento Teórico y Algoritmos de Ruteo

### 1. Marco Metodológico Principal
* **Paper Científico Base:**
  > **Kosior, M., Przystałka, P., & Panfil, W. (2024).** *"Adaptive Path Planning for UAV-Based Pollution Sampling"*. **Applied Sciences**, 14(24), 12065. DOI: [10.3390/app142412065](https://doi.org/10.3390/app142412065).
* **Algoritmo de K Caminos Disimilares:**
  > **Akgün, V., Erkut, E., & Batta, R. (2000).** *"On finding dissimilar paths"*. **European Journal of Operational Research**, 121(2), 232–246. DOI: [10.1016/S0377-2217(99)00214-3](https://doi.org/10.1016/S0377-2217(99)00214-3).

### 2. Generación de Alternativas ($k=2$)
1. **Ruta Primaria ($k=1$):** Se calcula sobre el grafo de costos ponderados por riesgos operacionales $W(e) = L(e) \cdot (1 + \sum \lambda_f \Omega_f(e))$.
2. **Ruta de Contingencia ($k=2$):** Se penalizan transitoriamente las aristas de $k=1$ por un factor de **$\times 4.0$**, forzando al algoritmo a descubrir trayectorias disimilares que compartan el mínimo de infraestructura expuesta.

### 3. Métrica de Resiliencia Conjunta $\mathcal{R}(K) \in [0, 100\%]$
Sean $\Pi_1$ y $\Pi_2$ dos rutas que comparten un tramo común $E_C = \Pi_1 \cap \Pi_2$ y tramos disyuntos $E_1 = \Pi_1 \setminus \Pi_2$ y $E_2 = \Pi_2 \setminus \Pi_1$. Bajo un proceso estocástico de supervivencia de Poisson $S(E) = e^{-\sum_{e \in E} \lambda(e) L_{\text{km}}(e)}$:
$$\mathcal{R}(\Pi_1, \Pi_2) = S(E_C) \times \left[ 1 - \left(1 - S(E_1)\right) \cdot \left(1 - S(E_2)\right) \right] \times 100\%$$

---

## 📊 Resultados Experimentales y Diferencial de Resiliencia ($\Delta \mathcal{R}$)

El sistema evalúa de forma transparente el comportamiento del ruteo en dos escenarios territoriales:

### 1. Escenario Base (Datos Reales Satelitales y Meteorológicos)
*En condiciones normales (sin incendios industriales ni tormentas activas en la bahía), la red basal es altamente confiable y el algoritmo resiliente aporta mejoras consistentes (+0,4 a +1,4 p.p.) al evitar sobrevuelos sobre manzanas densamente pobladas según la norma **DGAC DAN 151**:*

| Estación Destino SINCA | Distancia Dijkstra ($k=1$) | $\mathcal{R}(K_{\text{Dijkstra}})$ | Distancia Resiliente ($k=1$) | $\mathcal{R}(K_{\text{Resiliente}})$ | Diferencial ($\Delta \mathcal{R}$) | Análisis Territorial Real |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Campiche** | 9,53 km | 91,2% | 9,61 km | 91,9% | **+0,7 p.p.** | Evita manzanas densas (DAN 151), reduce riesgo a solo sombra telecom (+80 m) |
| **Centro Quintero** | 1,69 km | 99,5% | 1,74 km | 99,6% | **+0,1 p.p.** | Corredor costero despejado |
| **La Greda** | 6,71 km | 96,0% | 6,78 km | 96,4% | **+0,4 p.p.** | Evita manzanas densas de Quintero norte (+70 m) |
| **Loncura** | 2,35 km | 99,8% | 2,35 km | 99,7% | **-0,1 p.p.** | Trayectoria óptima coincidente |
| **Puchuncaví** | 14,41 km | 87,5% | 14,51 km | 88,9% | **+1,4 p.p.** | Desvío perimetral de manzanas censales densas (+100 m) |
| **Quintero** | 2,35 km | 98,2% | 2,87 km | 99,1% | **+0,9 p.p.** | Desvío perimetral de zona urbana central (+520 m) |
| **Sur** | 3,74 km | 99,8% | 3,74 km | 99,6% | **-0,2 p.p.** | Mínima variación por arista secundaria |
| **Ventanas** | 7,80 km | 92,5% | 8,01 km | 93,6% | **+1,1 p.p.** | Reducción de vuelo sobre manzanas densas y sombra telecom (+210 m) |

### 2. Escenario de Contingencia (Incendio Activo en Planta Asfaltos Quintero)
*Al activarse un siniestro térmico en `[-71.4935, -32.7801]` (radio de 180 m), Dijkstra $k=1$ colapsa a $\approx 1\%$ al volar a ciegas sobre las aristas afectadas. El planificador resiliente descubre el bypass oriental por Loncura/valle, manteniendo entre **$88,6\%$ y $96,2\%$** de confiabilidad:*

| Estación Destino SINCA | Distancia Dijkstra ($k=1$) | $\mathcal{R}(K_{\text{Dijkstra}})$ | Distancia Resiliente ($k=1$) | $\mathcal{R}(K_{\text{Resiliente}})$ | Diferencial ($\Delta \mathcal{R}$) | Foco Térmico en Dijkstra | Foco Térmico en Resiliente |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Campiche** | 9,53 km | 1,3% | 11,56 km | **91,6%** | **+90,3 p.p.** | 2 aristas afectadas | **0 aristas** |
| **La Greda** | 6,71 km | 1,5% | 8,74 km | **96,2%** | **+94,7 p.p.** | 2 aristas afectadas | **0 aristas** |
| **Puchuncaví** | 14,41 km | 1,2% | 16,46 km | **88,6%** | **+87,4 p.p.** | 2 aristas afectadas | **0 aristas** |
| **Ventanas** | 7,80 km | 1,3% | 9,97 km | **93,3%** | **+92,0 p.p.** | 2 aristas afectadas | **0 aristas** |
| **Quintero** | 2,35 km | 98,2% | 2,87 km | **99,1%** | **+0,9 p.p.** | 0 aristas | 0 aristas |
| **Centro Quintero** | 1,69 km | 99,5% | 1,74 km | **99,6%** | **+0,1 p.p.** | 0 aristas | 0 aristas |
| **Loncura** | 2,35 km | 99,8% | 2,35 km | **99,7%** | **-0,1 p.p.** | 0 aristas | 0 aristas |
| **Sur** | 3,74 km | 99,8% | 3,74 km | **99,6%** | **-0,2 p.p.** | 0 aristas | 0 aristas |

### 3. Análisis de Sensibilidad ($\lambda_{\text{incendio}}$ en Puchuncaví)
| $\lambda_{\text{incendio}}$ ($\text{km}^{-1}$) | Severidad Operacional Supuesta | $\mathcal{R}(K_{\text{Dijkstra}})$ | $\mathcal{R}(K_{\text{Resiliente}})$ | Diferencial ($\Delta \mathcal{R}$) | Dominancia Resiliente |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **0,5** | Humo denso y turbulencia moderada | 65,6% | 88,6% | **+23,0 p.p.** | Resiliente Domina |
| **1,0** | Foco térmico relevante / visibilidad reducida | 44,5% | 88,6% | **+44,1 p.p.** | Resiliente Domina |
| **5,0** | Incendio industrial crítico con pérdida de sustentación | 1,2% | 88,6% | **+87,4 p.p.** | Resiliente Domina |

* **Hallazgo de Resiliencia Territorial:** Se descubrió que focos de incendio con radio $\ge 450\text{ m}$ en este sector constituyen un **conjunto de corte topológico (cut-set)** que aísla por completo el norte de la bahía respecto a Quintero, evidenciando la vulnerabilidad estructural de la red de transporte y la criticidad del bypass oriental.

---

## 📁 Estructura del Repositorio

```text
redes_udp/
├── Dockerfile                            # Entorno Python 3.12.15-slim fijado
├── docker-compose.yml                    # Servicios db (PostGIS/pgRouting), etl y web
├── requirements.txt                      # Dependencias fijadas (psycopg==3.2.13)
├── main.py                               # Pipeline maestro de ejecución automatizada
├── GUIA_PROYECTO.md                      # Guía conceptual y de arquitectura del proyecto
├── redes_r_2.md                          # Memoria teórica y marco normativo DGAC DAN 151
│
├── bd/                                   # Base de Datos Relacional Espacial
│   ├── schema.sql                        # DDL de las 9 tablas espaciales e índices GiST
│   ├── conexion.py                       # Módulo de conexión psycopg con manejo de errores
│   ├── bd_diagrama.png                   # Diagrama ER de la BD espacial
│   └── bd_diagrama.puml                  # Código fuente PlantUML del diagrama
│
├── infraestructura/                      # Red Topológica Base
│   ├── extraer_infraestructura.py        # Generación de nodos, aristas y zonas urbanas
│   ├── nodos.geojson / .md / cargar_...  # 237 vértices clasificados
│   ├── aristas.geojson / .md / cargar_...# 633 corredores aéreos con topología
│   └── zonas_urbanas.geojson / .md / ... # 8 polígonos urbanos RFC 7946 antihorarios
│
├── metadata/                             # Metadata Geoespacial (n = 4)
│   ├── sinca_calidad_aire.py / .md / ... # Mediciones horarias de estaciones MMA
│   ├── srtm_relieve.py / .md / ...       # Perfil altimétrico por arista
│   ├── ine_manzanas.py / .md / ...       # Manzanas censales y densidad hab/km²
│   └── osm_antenas.py / .md / ...        # Antenas celulares y radio de cobertura C2
│
├── amenazas/                             # Modelos de Amenazas Dinámicas (n = 4)
│   ├── firms_incendios.py / .md / ...    # Focos satelitales NASA FIRMS (MODIS/VIIRS)
│   ├── csn_sismos.py / .md / ...         # Sismicidad histórica CSN/EMSC
│   ├── openmeteo_viento.py / .md / ...   # Grilla 4x4 de velocidad de viento y ráfagas
│   └── metno_lluvia.py / .md / ...       # Grilla 4x4 de precipitaciones MET Norway
│
├── ruteo/                                # Algoritmos de Ruteo Resiliente y pgRouting
│   ├── ruta_dijkstra.py                  # pgr_dijkstra en PostgreSQL (k=1 y k=2 con factor x4.0)
│   ├── k_dijkstra_pgrouting.sql          # Consultas SQL con IDs reales de aristas
│   └── ruteo_resiliente.py               # Motor multiobjetivo y confiabilidad estocástica
│
├── sitio_web/                            # Plataforma Web de Telemetría (C2 / Leaflet)
│   ├── index.html                        # Interfaz con selectores y control de capas
│   ├── app.js                            # Lógica interactiva en Vanilla ES Modules (< 50 ms)
│   ├── estilo.css                        # Estilos técnicos minimalistas (modo claro)
│   └── data/                             # Datos GeoJSON y documentación .md
│       ├── ruta_dijkstra.geojson / .md   # 16 Features independientes k=1 y k=2 de pgRouting
│       ├── rutas_comparativas.geojson/.md# 32 rutas comparativas base y contingencia
│       └── resumen_resiliencia.json / .md# Métricas agregadas y sensibilidad
│
└── tests/
    └── verificar.py                      # Suite integral de verificación geoespacial y de datos
```
