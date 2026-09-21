# Roadmap de Desarrollo: Simulador de Ruteo Resiliente UAV

Este documento registra el estado de avance del proyecto, las fases completadas y las tareas prioritarias pendientes. Sirve como guía de navegación para el equipo de desarrollo y cualquier agente de IA.

---

## 📊 Estado General del Proyecto

| Fase | Componente / Hito | Estado | Responsables / Notas |
| :--- | :--- | :---: | :--- |
| **Fase 1** | Modelado Geoespacial y Cosecha de Nodos (OSM/QGIS) | ✅ **100% Completado** | Datasets de 13 capas (`nodes.geojson`, `urban_zones.geojson`) listos y validados. |
| **Fase 2** | Visor Cartográfico Web y Dashboard UI Base | ✅ **100% Completado** | Leaflet con capas satelitales Esri/Carto/OSM, filtros temáticos, panel de métricas. |
| **Fase 3** | Conectores Multi-API en Tiempo Real (`src/services/`) | 🟡 **Pendiente** | Integrar Open-Meteo (viento/temp) y consulta SINCA. |
| **Fase 4** | Algoritmos GPP (Global Path Planner) | 🟡 **Pendiente** | Dijkstra, A*, Genético y ACO_R para cálculo offline de rutas multi-destino. |
| **Fase 5** | Algoritmos LPP (Local Path Planner) y RTH Sotavento | 🟡 **Pendiente** | Recálculo dinámico ($CT \le 4.55\text{ s}$), evasión de fallas y RTH asistido por relieve. |
| **Fase 6** | Motor de Simulación Temporal y Telemetría Multinave | 🟡 **Pendiente** | Reloj de simulación, consumo de batería en vivo, HUD de telemetría y animación de vuelo. |
| **Fase 7** | Evaluación de Métricas de Resiliencia (Estándar Paper) | 🟡 **Pendiente** | Comparativa cuantitativa: $LEN$, $EEE$, $SMOO$, $CT$, misiones exitosas vs. fallas. |

---

## 🛠️ Detalle de Tareas Pendientes (Backlog Priorizado)

### 📌 Prioridad 1: Servicios Multi-API (`src/services/`)
- [ ] **`WeatherService.js`**:
  - Implementar llamada fetch a la API de Open-Meteo para las coordenadas de Quintero (`-32.7550, -71.4550`).
  - Extraer: velocidad del viento ($m/s$), dirección en grados, ráfagas, temperatura y lluvia.
  - Convertir dirección y velocidad en vector cartesiano $\vec{w} = (w_x, w_y)$.
  - Implementar lógica **No-Go** ante lluvia moderada/fuerte ($> 2\text{ mm/h}$) o ráfagas extremas ($> 14\text{ m/s}$).
- [ ] **`SincaService.js`**:
  - Adaptador para consultar niveles de $\text{SO}_2$ y $\text{MP}_{2.5}$ en las 9 estaciones del SINCA.
  - Ajuste dinámico de prioridades de nodos según alertas ambientales.

---

### 📌 Prioridad 2: Construcción de Aristas y Algoritmos GPP (`src/algorithms/gpp/`)
- [ ] **Generador de Corredores de Vuelo 3D**:
  - Algoritmo en `src/core/NetworkGraph.js` para generar aristas navegables entre nodos cercanos (por ejemplo, Delaunay 3D o radio de conectividad $R_{comm} \approx 3\text{--}5\text{ km}$).
  - Ponderación de aristas con la función de costo multi-objetivo ($W(e_{ij})$) integrando distancia y vector de viento de Open-Meteo.
- [ ] **`AStar.js` / `Dijkstra.js`**:
  - Implementar A* 3D con heurística admissible para encontrar el camino óptimo entre el Aeródromo de Quintero y cualquier nodo o secuencia de destinos.
- [ ] **`GeneticGPP.js` / `ACOR.js`**:
  - Planificador de misiones multi-parada (TSP / VRP con restricciones de batería).

---

### 📌 Prioridad 3: LPP y Protocolo de Retorno Seguro (RTH) por Sotavento
- [ ] **`RTHPlanner.js`**:
  - Cuando el usuario presiona el botón "Retorno Seguro a Base (RTH)":
    1. Obtiene la posición actual del dron y vector de viento.
    2. Si el viento en contra es adverso, calcula la trayectoria utilizando las áreas protegidas por el relieve (cerros de Puchuncaví y Quintero).
    3. Asegura llegada con $\ge 15\%$ de batería.
- [ ] **Inyector de Fallas Dinámicas (`src/simulation/FailureInjector.js`)**:
  - Botón o panel para bloquear un corredor aéreo (incendio simulado o NOTAM) o apagar una estación.
  - LPP gatilla recálculo en tiempo real ($CT \le 4.55\text{ s}$).

---

### 📌 Prioridad 4: Motor de Simulación y Visualización de Vuelo
- [ ] **`SimulationEngine.js`**:
  - Bucle de simulación (tick) a velocidad 1x, 2x, 5x.
  - Actualización del estado del dron: posición GPS, altitud (0-120 m AGL), porcentaje de batería ($SOC$), velocidad ($v_g$).
- [ ] **`FlightRenderer.js`**:
  - Marcador dinámico del dron en Leaflet con estela de trayectoria recorrida.
  - Panel HUD con velocímetro, altímetro, nivel de batería e indicador de viento.
