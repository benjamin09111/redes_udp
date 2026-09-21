# Guía Maestra para Agentes de IA y Desarrolladores: Simulador de Ruteo Resiliente UAV

Este documento es la **fuente única de verdad (Single Source of Truth)** para cualquier agente de IA (Antigravity, Claude, Cursor, Windsurf, Copilot, ChatGPT) o desarrollador que colabore en este repositorio.

---

## 1. Fundamento Metodológico y Científico
1. **Marco Teórico Principal**:
   - Basado en la arquitectura adaptativa de planificación de rutas en dos niveles de **Kosior et al. (2024)**:
     - **GPP (Global Path Planner)**: Planificación estratégica offline previa al despegue (Dijkstra, A*, Algoritmos Genéticos, ACO).
     - **LPP (Local Path Planner)**: Planificación táctica online reactiva a bordo ($CT \le 4.55\text{ s}$, evitación estricta de colisiones $N_{COL} = 0$, RRT* / A* Dinámico).
2. **Restricción Normativa Aeronáutica**:
   - Norma **DAN 151 de la DGAC (Chile)**: Límite estricto de altitud de operación entre **0 y 120 metros AGL** (Above Ground Level).
   - Zona de intercepción estratégica: Plumas industriales (50 a 110 m) e inversión térmica costera (80 a 120 m).
   - Prohibición estricta de sobrevuelo sobre aglomeraciones de personas y zonas de exclusión aérea (NOTAM).
3. **Métricas de Evaluación Cuantitativa (Estándar Paper)**:
   - Longitud de ruta ($LEN$).
   - Consumo Energético Estimado ($EEE$).
   - Suavidad de trayectoria ($SMOO$).
   - Tiempo de cómputo de recálculo ($CT$).
   - Resiliencia de red: porcentaje de misiones completadas vs. fallas de aristas/nodos, conectividad y preservación de al menos **15% de batería de respaldo en RTH**.

---

## 2. Estado Actual del Proyecto (¿Qué llevamos hecho?)

Hasta este momento se ha completado con éxito la **Fase de Modelado Geoespacial e Interfaz Cartográfica**:
1. **Base de Datos Geoespacial Master (`public/data/nodes.geojson`)**:
   - Red de nodos clasificada en 13 categorías temáticas:
     - `base`: Aeródromo de Quintero (despacho y base RTH principal).
     - `sinca`: Las 9 estaciones oficiales de monitoreo de calidad del aire del SINCA.
     - `emission_source`: Fuentes emisoras del parque industrial de Ventanas (Codelco, AES Gener, Oxiquim, Enap, GNL Quintero, etc.).
     - `health`: Hospitales (Adriana Cousiño), CESFAMs y postas rurales.
     - `education`: Red de colegios, liceos y jardines infantiles.
     - `commercial`, `crowded_area`, `beach`, `hospitality`, `restaurant`, `attraction`, `historic`, `auxiliary_hub`.
   - Coordenadas geográficas precisas en formato WGS84 `[longitud, latitud, altitud_msnm]`.
2. **Límites Urbanos y Amortiguamiento (`public/data/urban_zones.geojson`)**:
   - Polígonos de las 13 localidades urbanas de la zona para cálculo de zonas de exclusión y densidad poblacional.
3. **Visor Cartográfico Web (`index.html`, `src/map/mapManager.js`, `src/styles/main.css`)**:
   - Visualizador en Leaflet con capas satelitales (Esri World Imagery, CartoDB Dark, OpenStreetMap).
   - Capas de nodos agrupadas con encendido/apagado independiente y panel de métricas en vivo.
   - Paneo elástico acotado a la Bahía de Quintero y Puchuncaví.
   - Botón inicial de RTH y filtros temáticos por categoría de nodo.
4. **Scripts de Cosecha y Procesamiento (`scripts/`)**:
   - Scripts en Python con Overpass API, Nominatim y Open-Elevation para cosecha, enriquecimiento y validación de datos.

---

## 3. Mapa de Arquitectura y Código

```text
ruteo_redes/
├── index.html                   # Interfaz de usuario del simulador web
├── README.md                    # Documentación pública para el equipo
├── AGENTS.md                    # Este archivo (guía para agentes y desarrolladores)
├── ROADMAP.md                   # Tareas pendientes organizadas por prioridad
├── redes_r_2.md                 # Documento teórico completo de la tesis/proyecto
├── .agents/
│   └── rules/
│       ├── architecture.md      # Guía de modularidad y responsabilidades
│       ├── algorithms_and_math.md# Fórmulas de EEE, métricas y modelos físicos
│       ├── geo_and_apis.md      # Estructura de GeoJSON y especificación de APIs
│       └── resilience_simulation.md # Reglas científicas del simulador
├── src/
│   ├── core/
│   │   └── NetworkGraph.js      # Estructura del grafo espacial 3D y distancias
│   ├── map/
│   │   └── mapManager.js        # Motor de mapas Leaflet, capas satelitales y marcadores
│   ├── styles/
│   │   └── main.css             # Estilos modernos de la interfaz (modo oscuro / cian)
│   └── main.js                  # Punto de entrada de la aplicación web
├── public/
│   └── data/
│       ├── nodes.geojson        # Nodos clasificados (WGS84 3D)
│       └── urban_zones.geojson  # Polígonos urbanos y zonas de amortiguamiento
└── scripts/                     # Herramientas auxiliares de datos (Python)
    ├── compile_expanded_network.py # Compilador maestro de nodes.geojson
    ├── build_all_urban_zones.py    # Compilador maestro de urban_zones.geojson
    └── ...                         # Scripts de extracción OSM / Overpass
```

---

## 4. Reglas Mandatorias para Agentes de IA

Si eres un agente de IA trabajando en este proyecto, **DEBES CUMPLIR ESTRICTAMENTE** las siguientes directivas:

1. **Desacoplamiento Estricto**:
   - Los algoritmos de enrutamiento (`src/algorithms/`) y modelos físicos (`src/core/`) deben ser funciones o clases puras en JavaScript. **NO** deben importar Leaflet (`L`) ni manipular elementos del DOM.
   - La visualización en el mapa corresponde exclusivamente a `src/map/` y los controles a `src/ui/`.
2. **Filosofía Minimalista (YAGNI & Vanilla ES Modules)**:
   - Usa ES Modules estándar del navegador (`import`/`export`).
   - **NO instales paquetes npm innecesarios ni introduzcas frameworks pesados** a menos que el usuario lo solicite explícitamente. El proyecto corre directamente con `python -m http.server 8000`.
3. **Interoperabilidad QGIS**:
   - Todo dato geoespacial debe permanecer como GeoJSON RFC 7946 estándar con coordenadas `[longitud, latitud, altitud]`.
   - No rompas la compatibilidad con QGIS Desktop.
4. **Fidelidad al Marco Científico**:
   - Consulta `.agents/rules/algorithms_and_math.md` para cualquier cálculo de consumo energético ($EEE$), velocidad terrestre ($v_g$), o función de costo multi-objetivo.
   - El protocolo RTH debe aprovechar el **sotavento** de los cerros costeros ante viento de frente, garantizando $\ge 15\%$ de batería.

---

## 5. Próximos Pasos (¿Qué construir ahora?)

Consulta [ROADMAP.md](file:///c:/Users/Benjamin/Desktop/ruteo_redes/ROADMAP.md) para el backlog detallado. Las prioridades inmediatas son:
1. **`src/services/WeatherService.js`**: Conexión a la API de Open-Meteo para obtener viento y temperatura de Quintero en tiempo real.
2. **`src/core/NetworkGraph.js` (Aristas y Corredores)**: Generar los corredores aéreos 3D entre nodos y calcular sus costos en función de la distancia y el vector de viento.
3. **`src/algorithms/gpp/AStar.js`**: Implementar el algoritmo A* para calcular la ruta óptima entre el Aeródromo de Quintero y los destinos seleccionados.
4. **`src/algorithms/lpp/RTHPlanner.js`**: Programar la lógica del botón RTH con protección por sotavento.
