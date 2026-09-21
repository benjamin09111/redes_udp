# Arquitectura de Software y Separación de Responsabilidades

Este documento define la estructura del código para que cualquier desarrollador o agente de IA mantenga la coherencia del sistema.

## 1. Principio Fundamental: Desacoplamiento del Motor Cartográfico
- La lógica matemática, física y de enrutamiento debe ser **agnóstica** del motor de visualización (Leaflet o MapLibre).
- Ningún algoritmo de enrutamiento (`src/algorithms/`), modelo de grafo (`src/core/`) o simulador físico (`src/simulation/`) debe importar ni depender de `L` (Leaflet) o del DOM.
- El visualizador (`src/map/`) solo consume datos del grafo o de la simulación y los dibuja en el lienzo cartográfico.

## 2. Estructura de Directorios (`src/`)

```text
src/
├── core/                  # Modelos matemáticos puros y estructuras de datos
│   ├── NetworkGraph.js    # Grafo tridimensional (nodos x, y, z, aristas, distancias)
│   ├── Kinematics.js      # Modelo de vuelo UAV (velocidades horizontal/vertical, viraje)
│   └── EnergyModel.js     # Modelo EEE de consumo de batería LiPo (Kosior et al., 2024)
│
├── algorithms/            # Algoritmos de enrutamiento (independientes de UI/Leaflet)
│   ├── gpp/               # Global Path Planners (offline, pre-vuelo)
│   │   ├── Dijkstra.js    # Camino más corto clásico ponderado
│   │   ├── AStar.js       # A* con heurística euclidiana 3D + viento
│   │   ├── GeneticGPP.js  # Optimización multiobjetivo por algoritmo genético
│   │   └── ACOR.js        # Colonia de hormigas continuo (ACO_R)
│   │
│   └── lpp/               # Local Path Planners (online, reactivo a bordo)
│       ├── DynamicAStar.js# Recálculo rápido ante aristas caídas (CT <= 4.55 s)
│       ├── RRTStar.js     # Evasión de obstáculos dinámicos en 3D
│       └── RTHPlanner.js  # Planificador de retorno a base asistido por sotavento
│
├── services/              # Conectores y adaptadores a APIs externas
│   ├── WeatherService.js  # Conector Open-Meteo (viento u/v, ráfagas, temp, lluvia)
│   ├── SincaService.js    # Consulta de calidad de aire en estaciones terrestres (SO2, MP2.5)
│   └── ElevationService.js# Modelo de elevación / topografía costera
│
├── simulation/            # Motor de ejecución temporal y eventos
│   ├── SimulationEngine.js# Ciclo de reloj (tick), posición del UAV, estado de batería
│   ├── FailureInjector.js # Inyector de fallas (NOTAMs, caída de antenas, ráfagas)
│   └── MissionManager.js  # Gestión de misiones: origen, paradas, muestreo, RTH
│
├── map/                   # Capa de presentación geoespacial (Leaflet)
│   ├── mapManager.js      # Orquestador del mapa, capas satelitales y grupos
│   ├── LayerStyles.js     # Colores, íconos y radios de nodos y polígonos
│   └── FlightRenderer.js  # Renderizado de trayectorias, estela 3D y posición del dron
│
├── ui/                    # Controladores de interfaz y telemetría
│   ├── Dashboard.js       # Actualización de métricas de red y telemetría en tiempo real
│   ├── ControlPanel.js    # Botones de misión, disparo de fallas y RTH
│   └── MissionConfig.js   # Selección de destinos, número de drones y parámetros
│
└── main.js                # Punto de entrada de la aplicación web (orquestador)
```

## 3. Filosofía de Desarrollo (Vanilla ES Modules)
1. **Sin Build Step Pesado**: Utilizar JavaScript ES Modules nativo (`import`/`export`) en el navegador.
2. **YAGNI (You Aren't Gonna Need It)**: No agregar dependencias de npm ni frameworks a menos que sea estrictamente necesario.
3. **GeoJSON Estándar**: Toda la información geoespacial de entrada y salida debe ser compatible con la especificación RFC 7946 GeoJSON y directamente legible en **QGIS Desktop**.
