# MASTER_SPEC_FASE3.md — Especificación Técnica Maestra de Desarrollo (Fase 3)
## CIT3435: Algoritmos de Ruteo y Redes Resilientes — UDP — Grupo 09
### Sistema de Ruteo Resiliente de UAV para Muestreo Atmosférico en Quintero–Puchuncaví

> **PROPÓSITO DE ESTE DOCUMENTO:**  
> Este es el documento maestro de especificación y arquitectura que debe ser leído y ejecutado por el **Agente de Desarrollo** en el repositorio `ruteo_redes`.  
> Todo lo que se programe debe ser **100 % fiel y exacto a este documento**, ya que cada fórmula, variable, restricción y algoritmo aquí definido está documentado formalmente en el paper académico (`main.tex`).  
> **Regla de oro:** No cambiar nombres de variables, coeficientes $\lambda$, fórmulas de resiliencia ni criterios de selección sin actualizar el paper.

---

## 1. Alcance, Plataforma y Parámetros Operacionales de la Aeronave

La misión modela un vehículo aéreo no tripulado (UAV) multirrotor **DJI Matrice 350 RTK** equipado con sensores ambientales para caracterizar la contaminación en la bahía de Quintero--Puchuncaví.

| Parámetro | Símbolo / Variable | Valor Nominal | Justificación Técnica / Fuente |
|---|---|---|---|
| **Base de Operaciones** | `s_base` (`base_scer`) | Aeródromo Quintero | Único nodo habilitado para despegue y retorno seguro. |
| **Velocidad de Crucero** | $v_{\text{crucero}}$ | $\qty{15}{m/s}$ ($\approx 54\,\text{km/h}$) | Velocidad en aristas de traslado para minimizar gasto de batería. |
| **Velocidad de Muestreo** | $v_{\text{muestreo}}$ | $\leq \qty{3}{m/s}$ | Aristas a sotavento; evita el borrado espacial ($d_{\text{smear}} = v \cdot \tnoventa$). |
| **Tiempo de Muestreo (Hover)** | $t_{\text{hover}}$ | $\qty{60}{s}$ | Tiempo de estabilización en nodos receptores y estaciones SINCA. |
| **Autonomía Total Útil** | $T_{\text{max}}$ | $\qty{44}{min}$ | $\qty{55}{min}$ del fabricante menos $20\,\%$ de reserva de seguridad. |
| **Presupuesto para Muestreo**| $T_{\text{muestreo}}$ | $\qty{20}{min}$ | Equivalente a $\qty{18}{km}$ de energía de traslado. |
| **Presupuesto para Traslado**| $T_{\text{traslado}}$ | $\qty{24}{min}$ | $(44 - 20) = \qty{24}{min} \implies \qty{21,6}{km}$ ida y vuelta. |
| **Alcance Máximo de Ida** | $\Lmax$ | $\mathbf{10{,}5\,\text{km}}$ | Longitud máxima permitida de ruta de ida. Rutas $> 10{,}5\,\text{km}$ son **infactibles**. |
| **Límite de Viento** | $v_{\text{viento\_max}}$ | $\mathbf{12{,}0\,\text{m/s}}$ | Resistencia máxima del UAV. Ráfagas $> 12\,\text{m/s}$ son **restricción dura**. |
| **Techo Legal de Operación** | $z_{\text{max}}$ | $\qty{120}{m}$ AGL ($\approx 400\,\text{ft}$) | Límite normativo DGAC DAN 151 sobre el terreno. |
| **Cota Vertical de Vuelo** | $z_{\text{mision}}$ | $\min(120\,\text{m}, 0{,}8 \cdot h_{\text{mix}})$ | $h_{\text{mix}}$ de Open-Meteo. Debe volar bajo la inversión térmica. |

---

## 2. Definición Estricta de Capas Territoriales (Metadata y Amenazas)

Cada capa tiene un rol matemático y metrológico definido. Se eliminó `sismo` (no afecta el espacio aéreo) y se separó niebla de humedad.

### A. Capas de Metadata (Mínimo 5 capas, casi estáticas)
Nutren al grafo $\G = (\V, \E)$ asignando atributos a los nodos y aristas:

1. **M1 — Calidad del Aire (SINCA / MMA):**
   * *Entidad:* Nodos tipo `sinca` (8 estaciones oficiales).
   * *Rol:* Puntos de calibración instrumental. Si la estación registra superación de norma primaria ($\text{SO}_2, \text{NO}_2, \text{MP}$), activa la **recompensa de muestreo $R(e)$** en las aristas incidentes.
2. **M2 — Fuentes de Emisión Industrial (RETC / SNIFA / OSM):**
   * *Entidad:* Nodos tipo `emission_source` (32 chimeneas de Ventanas).
   * *Rol:* Origen de la pluma contaminante. Define el corredor a sotavento según el vector de viento. Las chimeneas imponen un radio de colisión física de $\qty{50}{m}$ (**restricción dura**).
3. **M3 — Relieve y Topografía (SRTM 30 m / OpenTopoData):**
   * *Entidad:* Aristas (`meta_edge_terrain`).
   * *Rol:* Asigna elevación sobre el terreno (AGL) y desnivel acumulado $\Delta z(e)$. Mantiene cota constante para comparabilidad metrológica y penaliza aristas con ascenso empinado por gasto energético.
4. **M4 — Densidad Poblacional (INE Censo 2017):**
   * *Entidad:* Polígonos censales (`meta_census_block`).
   * *Rol:* Identifica manzanas con densidad $> \num{2500}\,\text{hab/km}^2$. Aplica penalización por riesgo en tierra (GRC de SORA 2.5 y DAN 151). Prioriza muestreo en receptores sensibles (escuelas, consultorios).
5. **M5 — Cobertura de Telecomunicaciones C2 (OSM / OpenCelliD):**
   * *Entidad:* Polígonos de cobertura teórica de antenas celulares ($\qty{3000}{m}$).
   * *Rol:* Aristas fuera de cobertura quedan en sombra de mando y telemetría, activando penalización por riesgo de pérdida de enlace.

### B. Capas de Amenazas Dinámicas (Mínimo 5 capas)
Eventos temporales que inhabilitan aristas o aumentan la tasa de falla $\lambda(e)$:

1. **A1 — Incendios Activos (NASA FIRMS, VIIRS 375 m):**
   * *Efecto:* Humo de biomasa aporta partículas ajenas a la industria (arruina la muestra) y causa turbulencia térmica.
   * *Acción:* **Restricción dura** en el radio de exclusión ($\qty{180}{m}$ en foco industrial); penalización máxima ($\lambda_{\text{incendio}} = 5{,}0$) en el entorno.
2. **A2 — Viento Severo y Ráfagas (Open-Meteo `wind_speed`):**
   * *Efecto:* Desplaza la pluma; sobre $\qty{12}{m/s}$ desestabiliza el UAV.
   * *Acción:* Si $v_{\text{viento}} > \qty{12}{m/s}$, **restricción dura** (arista eliminada). Si $v \le \qty{12}{m/s}$ y es viento en contra, penalización energética ($\lambda_{\text{viento}} = 0{,}04$).
3. **A3 — Humedad Relativa Elevada (Open-Meteo `relative_humidity`):**
   * *Efecto:* Crecimiento higroscópico infla artificialmente la lectura del sensor óptico de partículas.
   * *Acción:* Amenaza exclusiva a la medición. Penalización blanda ($\lambda_{\text{humedad}} = 0{,}03$) o flag de corrección $\kappa$-Köhler.
4. **A4 — Niebla Costera / Camanchaca (Open-Meteo `visibility`):**
   * *Efecto:* Microgotas que causan pérdida de contacto visual del operador (VLOS) y condensación en el sensor.
   * *Acción:* Si $\text{visibilidad} < \qty{1000}{m}$, **restricción dura** por infracción a la norma DAN 151.
5. **A5 — Precipitación / Lluvia (Open-Meteo `precipitation`):**
   * *Efecto:* Lavado húmedo (*scavenging*) que limpia los contaminantes solubles ($\text{SO}_2$), dejando la muestra no representativa.
   * *Acción:* Restricción no-go de misión. Aristas post-lluvia quedan marcadas con bandera de atmósfera lavada.

---

## 3. Formulación Matemática de Costos y Restricciones

### 3.1 Función de Costo con Riesgo $W(e)$
Para cada arista $e = (u, v) \in \E_{\text{factible}}$:
$$W(e) = L(e) + \beta \cdot H(e) - R(e)$$

Donde:
*   $L(e)$: Longitud geodésica en metros (Haversine sobre WGS84).
*   $\beta$: Coeficiente de aversión al riesgo. Valor por defecto: $\mathbf{\beta = 1000{,}0}$.
*   $R(e)$: Recompensa de muestreo ($\geq 0$). Vale $R(e) = \num{200{,}0}$ si la arista discurre en el cono a sotavento de una chimenea activa o incide en una estación con alerta; $0$ en caso contrario.
*   $H(e)$: Penalización por exposición territorial:
    $$H(e) = \lambda(e) \cdot L_{\text{km}}(e) \quad \text{con} \quad L_{\text{km}}(e) = \frac{L(e)}{1000}$$

### 3.2 Tasa de Falla Territorial Compuesta $\lambda(e)$
$$\lambda(e) = \lambda_{\text{base}} + \sum_{f \in \mathcal{F}(e)} \lambda_f$$

Valores fijos calibrados (registrados en `config/parametros.json`):
*   $\lambda_{\text{base}} = \mathbf{0{,}005}\,\text{km}^{-1}$ (tasa intrínseca de falla del hardware).
*   $\lambda_{\text{incendio}} = \mathbf{5{,}0}$ (foco térmico o humo denso).
*   $\lambda_{\text{urbana}} = \mathbf{0{,}08}$ (manzanas con densidad $> \num{2500}\,\text{hab/km}^2$).
*   $\lambda_{\text{telecom}} = \mathbf{0{,}03}$ (tramo sin cobertura de antena C2).
*   $\lambda_{\text{viento}} = \mathbf{0{,}04}$ (viento en contra o cizalladura moderada).
*   $\lambda_{\text{lluvia}} = \mathbf{0{,}03}$ (precipitación ligera activa).

### 3.3 Clasificación Formal de Restricciones
*   **Restricciones Duras (Poda de aristas $\E_{\text{factible}} \subset \E$):**
    Una arista se elimina inmediatamente del grafo si:
    1.  Interseca el radio de $\qty{50}{m}$ de una chimenea u obstáculo sin libramiento.
    2.  Registra viento local $> \qty{12{,}0}{m/s}$.
    3.  Registra visibilidad $< \qty{1000}{m}$ (niebla).
    4.  Interseca el núcleo de exclusión de incendio ($\qty{180}{m}$ en contingencia simulada).
*   **Restricciones Blandas (Modulables por el Usuario):**
    El usuario en la web puede encender/apagar penalizaciones mediante un vector de checkboxes:
    $$\mathbf{w} = [w_{\text{incendio}}, w_{\text{poblacion}}, w_{\text{telecom}}, w_{\text{viento}}, w_{\text{lluvia}}] \in \{0, 1\}^5$$
    Por defecto, **todas están activadas ($\mathbf{w} = [1, 1, 1, 1, 1]$)**.

---

## 4. Algoritmos de Ruteo a Implementar ($k = 2$)

### A. Algoritmo 1: Línea Base Dijkstra ($k = 2$) — Pauta Ítem 8
*Agnóstico al riesgo territorial. Usa ÚNICAMENTE distancia en km.*

1.  **Ruta Primaria $P_1^D$:**
    $$P_1^D = \text{pgr\_dijkstra}(\G, s, d, \text{cost} = L(e), \text{reverse\_cost} = L(e))$$
2.  **Penalización Iterativa (IPM):**
    Multiplicar el costo de las aristas usadas por el factor $p_{\text{pen}} = 4{,}0$:
    $$L'(e) = \begin{cases} 4{,}0 \cdot L(e) & \text{si } e \in P_1^D \\ L(e) & \text{si } e \notin P_1^D \end{cases}$$
3.  **Ruta Secundaria $P_2^D$:**
    $$P_2^D = \text{pgr\_dijkstra}(\G, s, d, \text{cost} = L'(e), \text{reverse\_cost} = L'(e))$$
4.  Retornar el par $\{P_1^D, P_2^D\}$.

---

### B. Algoritmo 2: Propuesto — Akgün et al. (2000) Adaptado con Buffers PostGIS — Pauta Ítems 7 y 9
*Multi-criterio, con riesgo $W(e)$, filtros físicos y disimilitud espacial por zonas de influencia.*

#### Fase 1: Generación de Candidatas ($\mathcal{M}$)
1.  Inicializar $\mathcal{M} \gets \emptyset$ y pesos $W^{(0)}(e) \gets W(e)$ para todo $e \in \E_{\text{factible}}$.
2.  Para $m = 1, \dots, M$ (con $M = 30$ iteraciones):
    *   Calcular $P_m = \text{pgr\_dijkstra}(\G_{\text{factible}}, s, d, \text{cost} = W^{(m-1)})$.
    *   Si $P_m \neq \emptyset$, $P_m \notin \mathcal{M}$ y su longitud geométrica cumple $L(P_m) \leq \Lmax$ ($\qty{10,5}{km}$):
        $$\mathcal{M} \gets \mathcal{M} \cup \{P_m\}$$
    *   Penalizar las aristas usadas:
        $$W^{(m)}(e) = \begin{cases} 4{,}0 \cdot W^{(m-1)}(e) & \text{si } e \in P_m \\ W^{(m-1)}(e) & \text{si } e \notin P_m \end{cases}$$

#### Fase 2: Filtrado y Selección del Par de Máxima Disimilitud Espacial
1.  **Ruta Primaria $P_1^*$:** La ruta de menor costo generalizado:
    $$P_1^* = \arg\min_{P \in \mathcal{M}} W(P)$$
2.  **Filtro de Tolerancia de Costo ($\beta_{\text{tol}} = 0{,}30$):**
    $$\mathcal{M}_{\text{admisible}} = \{P \in \mathcal{M} \setminus \{P_1^*\} \mid W(P) \leq 1{,}30 \cdot W(P_1^*)\}$$
3.  **Cálculo de Disimilitud por Buffers en PostGIS (Radio $r = \qty{200}{m}$):**
    Para cada $P \in \mathcal{M}_{\text{admisible}}$, generar su buffer geodésico continuo:
    $$B(P) = \text{ST\_Buffer}(P\text{::geography}, 200)$$
    Calcular el índice de disimilitud espacial:
    $$D_{\text{buf}}(P_1^*, P) = 1 - \frac{\text{ST\_Area}(\text{ST\_Intersection}(B(P_1^*), B(P)))}{\text{ST\_Area}(\text{ST\_Union}(B(P_1^*), B(P)))}$$
4.  **Ruta Secundaria $P_2^*$:** La ruta que maximiza la disimilitud espacial con $P_1^*$:
    $$P_2^* = \arg\max_{P \in \mathcal{M}_{\text{admisible}}} D_{\text{buf}}(P_1^*, P)$$
5.  Retornar el par $\{P_1^*, P_2^*\}$.

---

## 5. Métrica de Resiliencia y Comparación (Pautas 10 y 11.2)

A **ambos pares de rutas** ($\{P_1^D, P_2^D\}$ y $\{P_1^*, P_2^*\}$) se les calcula la misma métrica de confiabilidad analítica:

### 5.1 Descomposición Topológica del Par
Para un par de rutas $\{P_1, P_2\}$:
*   $E_C = P_1 \cap P_2$ (Aristas compartidas / comunes).
*   $E_1 = P_1 \setminus P_2$ (Aristas exclusivas de la Ruta 1).
*   $E_2 = P_2 \setminus P_1$ (Aristas exclusivas de la Ruta 2).

### 5.2 Supervivencia de Tramos bajo Proceso de Poisson
La probabilidad de que un conjunto de aristas $E$ sobreviva sin fallas es:
$$S(E) = \exp\left(-\sum_{e \in E} \lambda(e) \cdot \frac{L(e)}{1000}\right)$$

### 5.3 Confiabilidad Analítica Exacta del Par $R(P_1, P_2)$
$$R(P_1, P_2) = S(E_C) \cdot \left[ 1 - \left(1 - S(E_1)\right) \left(1 - S(E_2)\right) \right]$$

*   Si las rutas son idénticas ($E_1 = E_2 = \emptyset \implies R = S(E_C)$): Confiabilidad de una ruta simple.
*   Si las rutas son totalmente disjuntas ($E_C = \emptyset \implies S(E_C) = 1$): Redundancia paralela perfecta.

### 5.4 Diferencial de Resiliencia ($\Delta R$) — Pauta 11.2
Para cada destino:
$$\mathbf{\Delta R = R(P_1^*, P_2^*) - R(P_1^D, P_2^D)}$$

---

## 6. Los 8 Destinos Oficiales de Evaluación

Origen fijo: `base_scer` (Aeródromo Quintero).

| # | Código Destino | Nombre Destino | Categoría | Distancia Nominal | Estado Esperado en Fase 3 |
|---|---|---|---|---|---|
| 1 | `centro_quintero` | Centro Quintero | Urbano corto | $\qty{1,69}{km}$ | Factible. Dijkstra cruza $23\,\%$ en zona densa. |
| 2 | `loncura` | Loncura | Residencial corto | $\qty{2,35}{km}$ | Factible. Desvío marítimo/costero. |
| 3 | `sinca_quintero` | Quintero Super-Sitio | Receptor crítico | $\qty{2,35}{km}$ | **Caso estrella urbano:** Dijkstra expone $45{,}1\,\%$ en zona densa. |
| 4 | `sur` | Sur Quintero | Borde costero | $\qty{3,74}{km}$ | Factible. Transición a zona rural. |
| 5 | `la_greda` | La Greda | Rural / Fumigación | $\qty{6,71}{km}$ | Factible. Dijkstra pierde C2 en $49{,}6\,\%$. |
| 6 | `sinca_ventanas` | Ventanas Super-Sitio | Industrial medio | $\qty{7,80}{km}$ | Factible. Dijkstra pierde C2 en $56{,}5\,\%$. |
| 7 | `campiche` | Campiche | Industrial extendido | $\qty{9,53}{km}$ | Factible (límite). Dijkstra pierde C2 en $64{,}5\,\%$. |
| 8 | `puchuncavi_centro`| Puchuncaví Centro | Control Negativo | $\qty{14,41}{km}$ | **INFACTIBLE por energía** ($> \qty{10,5}{km}$). El sistema debe rechazarlo. |

---

## 7. Reparto de Tareas para el Equipo de Desarrollo (3 Personas)

```
+-----------------------------------------------------------------------------------------+
|                                    MASTER ROADMAP FASE 3                                |
+------------------------------------+------------------------------------+---------------+
| PERSONA 1: Backend de Ruteo        | PERSONA 2: Lógica de Costos        | PERSONA 3: UI |
| - Algoritmo Dijkstra k=2           | - Cálculo de Lambda(e) y W(e)      | - Mapa Leaflet|
| - Algoritmo Akgün con buffers      | - Filtros Batería, Cota, Vel.      | - Selectores  |
| - Integración PostGIS / pgRouting  | - Fórmula Resiliencia R y Delta R  | - Dashboard   |
| - Exportador GeoJSON               | - Simulación Contingencia Asfaltos | - Gráficos    |
+------------------------------------+------------------------------------+---------------+
```

### 👤 Persona 1: Motores de Ruteo y PostGIS
1.  Crear `ruteo/motor_dijkstra_k2.py`: Genera el par Dijkstra $k=2$ sobre distancia pura mediante IPM ($p_{\text{pen}}=4{,}0$).
2.  Crear `ruteo/motor_akgun_postgis.py`:
    *   Generación de $M=30$ candidatas sobre $W(e)$.
    *   Filtro de alcance ($\le \qty{10,5}{km}$) y tolerancia ($+30\,\% W$).
    *   Función SQL / PostGIS para calcular `D_buf` con buffers de $\qty{200}{m}$.
    *   Selección del par $\{P_1^*, P_2^*\}$.
3.  Crear script de exportación que entregue las rutas en GeoJSON listo para el frontend.

### 👤 Persona 2: Lógica de Costos, Física y Resiliencia
1.  Crear `ruteo/calculo_costos.py`:
    *   Cruce espacial de aristas con capas de metadata y amenazas activas.
    *   Generación de $\lambda(e)$ y $W(e)$ con $\beta = 1000{,}0$.
    *   Filtrado de restricciones duras (viento $> 12$, niebla $< 1000$, colisión).
2.  Implementar `ruteo/metricas_resiliencia.py`:
    *   Descomposición en $E_C, E_1, E_2$ y cálculo exacto de $R(P_1, P_2)$ y $\Delta R$.
    *   Simulación del foco Planta Asfaltos Quintero ($\qty{180}{m}$, lat -32.7801, lon -71.4935) para comprobar la conmutación y supervivencia de la misión.
3.  Validación de energía: $T_{\text{mision}} \le \qty{44}{min}$ y cota $z \le \min(120, 0{,}8 \cdot h_{\text{mix}})$.

### 👤 Persona 3: Interfaz Web, Dashboard y Gráficos
1.  Actualizar `sitio_web/index.html` y `app.js`:
    *   Selectores de Origen (`base_scer`) y Destino (los 8 destinos).
    *   Panel de checkboxes de restricciones blandas (con botón "Restablecer por defecto").
    *   Pintar en Leaflet:
        - Dijkstra $k=2$ en rojo/naranja discontinuo.
        - Propuesto $k=2$ en verde/azul sólido con sombreado de buffer de $\qty{200}{m}$.
        - Polígonos de amenazas activas (foco de incendio, celdas de niebla/viento) y manzanas densas.
2.  Panel lateral de resultados en vivo (Pauta 11.2):
    *   Tabla comparativa: Longitud, $\%$ zona densa, $\%$ sin C2, $R_{\text{base}}$, $R_{\text{propuesto}}$.
    *   Badge destacado: **Diferencial de Resiliencia $\Delta R$**.
3.  Generar script de gráficos Python (`scripts/generar_graficos_fase3.py`):
    *   Gráfico de barras de $\Delta R$ en los 8 destinos.
    *   Gráfico de dispersión de Disimilitud ($D_{\text{buf}}$) vs. Kilometraje.

---

## 8. Formato de Salida Requerido (`sitio_web/data/resumen_fase3.json`)

Para que el autor del paper pueda insertar los números finales en la Sección 9 de `main.tex`, el sistema debe exportar un JSON con esta estructura exacta:

```json
{
  "metadata": {
    "fecha_ejecucion": "2026-11-XXT...",
    "beta": 1000.0,
    "buffer_m": 200.0,
    "tolerancia_pct": 30.0,
    "L_max_km": 10.5
  },
  "destinos": {
    "quintero_supersitio": {
      "dijkstra": {
        "k1_longitud_km": 2.35,
        "k2_longitud_km": 2.48,
        "saltos": 9,
        "tiempo_vuelo_min": 2.6,
        "desnivel_m": -10.0,
        "km_zona_densa": 1.06,
        "pct_zona_densa": 45.1,
        "km_sin_c2": 0.0,
        "pct_sin_c2": 0.0,
        "disimilitud_buffers_pct": 17.6,
        "resiliencia_R": 0.742
      },
      "propuesto": {
        "k1_longitud_km": 2.61,
        "k2_longitud_km": 2.89,
        "saltos": 11,
        "tiempo_vuelo_min": 2.9,
        "desnivel_m": -8.0,
        "km_zona_densa": 0.12,
        "pct_zona_densa": 4.6,
        "km_sin_c2": 0.0,
        "pct_sin_c2": 0.0,
        "disimilitud_buffers_pct": 85.9,
        "resiliencia_R": 0.968
      },
      "diferencial_delta_R": 0.226,
      "mision_exitosa_bajo_estres": {
        "dijkstra": false,
        "propuesto": true
      }
    }
  }
}
```

---

## 9. Checklist de Aceptación para Dar por Cerrada la Fase 3

- [ ] Contenedor Docker `db` corriendo con PostGIS 3.4 y pgRouting 3.6.
- [ ] Tablas espaciales con índices GiST activos y sin violaciones de integridad referencial.
- [ ] Ejecución de Dijkstra $k=2$ basada estrictamente en longitud.
- [ ] Ejecución de Akgün adaptado $k=2$ con cálculo de buffers en PostGIS y filtro de $10{,}5\,\text{km}$.
- [ ] Rechazo automático de la ruta a Puchuncaví Centro ($14{,}41\,\text{km}$) por agotamiento de batería.
- [ ] Interfaz web interactiva operativa que muestra ambos pares y el badge $\Delta R$.
- [ ] Archivo `resumen_fase3.json` generado para actualizar las tablas de `main.tex`.
- [ ] Suite de 57 tests en `pytest` pasando en verde.
