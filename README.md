# redes_udp

## Simulador Ciberfísico de Ruteo Resiliente de UAVs (Bahía de Quintero - Ventanas - Puchuncaví)

Este repositorio contiene el simulador y entorno de análisis para el enrutamiento y resiliencia de vehículos aéreos no tripulados (UAV) en misiones de monitoreo ambiental atmosférico e industrial en la zona costera de Quintero, Ventanas y Puchuncaví (Chile), con estándar de tesis de Magíster y publicación científica.

---

## 🤖 Guía Rápida para Agentes de IA y Desarrolladores

Si eres un **agente de IA** (Antigravity, Cursor, Claude, Windsurf, Copilot, ChatGPT) o un nuevo desarrollador colaborando en este proyecto:

1. **Lee primero [AGENTS.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/AGENTS.md)**: Contiene las directrices de diseño, el estado actual del proyecto, la arquitectura de código y las restricciones no negociables (desacoplamiento, YAGNI, DAN 151, ES Modules nativos).
2. **Revisa el [ROADMAP.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/ROADMAP.md)**: Encontrarás el backlog priorizado con las próximas tareas listas para implementar (`WeatherService.js`, aristas 3D, algoritmo A*, protocolo RTH con sotavento).
3. **Consulta las especificaciones en `.agents/rules/`**:
   - [architecture.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/.agents/rules/architecture.md): Estructura modular y separación estricta de responsabilidades (`core`, `algorithms`, `map`, `simulation`, `services`, `ui`).
   - [algorithms_and_math.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/.agents/rules/algorithms_and_math.md): Modelos matemáticos de Kosior et al. (2024), métricas ($LEN$, $EEE$, $SMOO$, $CT$, $N_{COL}$) y función de costo multi-objetivo con viento.
   - [geo_and_apis.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/.agents/rules/geo_and_apis.md): Especificación de datos GeoJSON (WGS84 3D), compatibilidad QGIS y APIs (Open-Meteo, SINCA).

---

## 🎯 Objetivos y Marco Científico
- **Arquitectura de Planificación en Dos Niveles** (Kosior et al., 2024):
  - **GPP (Global Path Planner)**: Planificación estratégica global previa al despegue (Dijkstra, A*, Algoritmos Genéticos, ACO).
  - **LPP (Local Path Planner)**: Planificación táctica en tiempo real para evasión de obstáculos y fallas dinámicas ($CT \le 4.55\text{ s}$, evitación estricta de colisiones $N_{COL} = 0$).
- **Normativa Aeronáutica DGAC**:
  - Restricción estricta de altitud: **0 a 120 metros AGL** (Above Ground Level) según norma **DAN 151**.
  - Zonas de exclusión aérea sobre aglomeraciones urbanas, colegios, centros de salud y áreas sensibles.
- **Topología Geoespacial Real**:
  - Nodos de infraestructura crítica (base aérea SCER, 9 estaciones SINCA, industrias de Ventanas, hospitales, colegios, hubs de recarga).
  - Integración nativa de relieve y sotavento para protocolos de retorno seguro a base (RTH) ante vientos costeros.

---

## 📂 Estructura del Proyecto

```text
ruteo_redes/
├── index.html                   # Interfaz principal del simulador web
├── AGENTS.md                    # Guía maestra para agentes y desarrolladores
├── ROADMAP.md                   # Backlog de tareas y estado de avance
├── redes_r_2.md                 # Documento teórico completo de investigación
├── .agents/
│   └── rules/                   # Reglas de arquitectura, modelos matemáticos y APIs
├── src/
│   ├── core/                    # Estructuras del grafo, cinemática y modelos físicos
│   │   └── NetworkGraph.js      # Definición de nodos, aristas y conectividad 3D
│   ├── map/                     # Motor geoespacial y visualización de capas (Leaflet)
│   │   └── mapManager.js        # Gestión de capas de satélite, nodos, buffers y polígonos
│   ├── styles/                  # Estilos CSS de la interfaz moderna
│   │   └── main.css
│   └── main.js                  # Inicialización y puente de la aplicación
├── public/
│   └── data/                    # Datasets espaciales estándar GeoJSON (compatibles con QGIS)
│       ├── nodes.geojson        # Nodos clasificados en 13 categorías (WGS84 3D)
│       └── urban_zones.geojson  # Polígonos de amortiguamiento y zonas urbanas
└── scripts/                     # Scripts de Python para extracción (OSM/Overpass), análisis y compilación
```

---

## 🚀 Cómo Ejecutar el Simulador Localmente

El proyecto está diseñado con estándares web nativos (HTML5, ES Modules nativos y CSS moderno), por lo que no requiere compilación pesada ni frameworks complejos para iniciar.

### Opción 1: Con Python (Recomendado)
```bash
# Desde la raíz del repositorio
python -m http.server 8000
```
Luego abre tu navegador en `http://localhost:8000`.

### Opción 2: Con Node.js / npx
```bash
npx serve .
```

### Opción 3: Extensión Live Server de VS Code
Abre la carpeta en VS Code, haz clic derecho en `index.html` y selecciona **"Open with Live Server"**.

---

## 🗺️ Visualización en QGIS
Todos los archivos espaciales generados en `public/data/` (`nodes.geojson`, `urban_zones.geojson`) son 100% compatibles con **QGIS Desktop**. Puedes arrastrarlos directamente a un proyecto QGIS para realizar análisis espaciales complementarios.

---

## 👥 Colaboración y Flujo de Trabajo en Equipo
1. Clona el repositorio:
   ```bash
   git clone https://github.com/benjamin09111/redes_udp.git
   ```
2. Crea una rama de trabajo para tus aportes:
   ```bash
   git checkout -b feature/nombre-de-la-funcionalidad
   ```
3. Realiza tus cambios y abre un Pull Request hacia `main`.
