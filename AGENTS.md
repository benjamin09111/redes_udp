# Reglas y Contexto del Proyecto: Simulador de Ruteo y Redes Resilientes (UAV)

Este proyecto desarrolla un **simulador ciberfísico web de enrutamiento resiliente de UAVs** para monitoreo ambiental tridimensional (0 a 120 m AGL) en la Bahía de Quintero, Ventanas y Puchuncaví (Chile), con estándar de **tesis de Magíster y publicación científica (paper profesional)**.

---

## 1. Fundamento Metodológico y Científico
1. **Marco Teórico Principal**:
   - Basado en la arquitectura adaptativa de planificación de rutas en dos niveles de **Kosior et al. (2024)**:
     - **GPP (Global Path Planner)**: Planificación estratégica offline previa al despegue (Dijkstra, A*, Algoritmos Genéticos, ACO).
     - **LPP (Local Path Planner)**: Planificación táctica online reactiva a bordo ($CT \le 4.55\text{ s}$, evitación de colisiones $N_{COL} = 0$, RRT* / A* Dinámico).
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

## 2. Principios de Desarrollo y Buenas Prácticas
1. **Filosofía Minimalista (YAGNI & Ponytail)**:
   - Evitar sobreingeniería, dependencias innecesarias o wrappers prematuros.
   - Utilizar APIs nativas del navegador (HTML5, CSS moderno, ES Modules nativos).
   - Sin dependencias de build complejas para el prototipado inicial; mantener el código entendible y depurable.
2. **Interoperabilidad SIG (Estándar QGIS)**:
   - Los datos espaciales (nodos, corredores, zonas de exclusión) se almacenan y consumen en formato **GeoJSON** estándar ($x, y, z$).
   - Todo archivo `.geojson` generado debe ser 100% compatible y visualizable directamente en QGIS de escritorio.
3. **Separación Estricta de Responsabilidades**:
   - **`src/core/`**: Estructuras matemáticas del grafo y modelos físicos (cinemática, energía).
   - **`src/algorithms/`**: Algoritmos de enrutamiento puros (independientes del motor de render).
   - **`src/map/`**: Visualizador geoespacial (Leaflet / MapLibre).
   - **`src/services/`**: Conectores a APIs externas (Open-Meteo, SINCA, etc.).
   - **`src/simulation/`**: Lógica temporal, consumo de batería y generador de eventos/fallas.
   - **`src/ui/`**: Interfaz de usuario y telemetría.

---

## 3. Protocolo de Resiliencia Ciberfísica
- **Retorno Seguro a Base (RTH)**: No es una línea recta simplista. Debe considerar el vector de viento (Open-Meteo) y el relieve topográfico para aprovechar el **sotavento** de los cerros costeros en caso de viento de frente crítico.
- **Inyección de Fallas Dinámicas**:
  - Caída de nodos terrestres (pérdida de enlace/estación).
  - Bloqueo de corredores aéreos por incendios forestales (NASA FIRMS) o ráfagas.
  - Zonas de exclusión temporal (NOTAM DGAC).
