# Fundamentos Matemáticos, Métricas y Modelos Físicos

Este documento especifica las ecuaciones, métricas de desempeño y formulaciones para la implementación de los planificadores de ruta (GPP y LPP) basados en el marco de **Kosior et al. (2024)** y la normativa **DGAC DAN 151**.

---

## 1. Métricas de Evaluación Cuantitativa (Estándar Paper)

Cualquier algoritmo implementado debe ser evaluable bajo el siguiente vector de métricas:

| Métrica | Símbolo | Unidad | Descripción |
| :--- | :---: | :---: | :--- |
| **Longitud de Ruta** | $LEN$ | metros ($m$) | Distancia 3D total recorrida a lo largo de los waypoints. |
| **Consumo Energético Estimado** | $EEE$ | Joules ($J$) o $\%$ batería | Energía consumida integrando sustentación, avance y resistencia al viento. |
| **Suavidad de Trayectoria** | $SMOO$ | rad o $m/s^2$ | Integral de la curvatura o cambios angulares de viraje entre segmentos consecutivos. |
| **Tiempo de Cómputo** | $CT$ | segundos ($s$) | Tiempo requerido por el planificador para calcular o recalcular la ruta ($CT \le 4.55\text{ s}$ para LPP). |
| **Colisiones** | $N_{COL}$ | entero | Cantidad de intersecciones con zonas de exclusión o terreno ($N_{COL} = 0$ mandatorio). |
| **Reserva de Batería en RTH** | $SOC_{RTH}$ | $\%$ | Batería restante al tocar tierra en el Aeródromo de Quintero ($\ge 15\%$). |

---

## 2. Modelo Físico y Energético del UAV

### 2.1. Vector de Viento y Velocidad Terrestre ($v_g$)
Sea $\vec{v}_a$ el vector de velocidad del UAV respecto al aire ($|\vec{v}_a| \approx 10\text{--}15\text{ m/s}$) y $\vec{w} = (w_x, w_y)$ el vector de viento ambiental obtenido de Open-Meteo:
$$\vec{v}_g = \vec{v}_a + \vec{w}$$
- Si el vuelo es contra el viento (viento de frente), $v_g < v_a$, incrementando el tiempo de tránsito y disparando el consumo $EEE$.
- Si el vuelo es a favor del viento (viento de cola), $v_g > v_a$, reduciendo el consumo $EEE$.

### 2.2. Consumo Energético Estimado ($EEE$)
La potencia total requerida $P(t)$ por un multirotor considera tres componentes:
$$P(t) = P_{ind} + P_{par} + P_{climb}$$
Donde:
- $P_{ind}$: Potencia inducida para mantener la sustentación en hover y avance.
- $P_{par}$: Potencia parásita debida a la resistencia aerodinámica del fuselaje frente al viento relativo $\vec{v}_a$.
- $P_{climb}$: Potencia de ascenso/descenso ($m \cdot g \cdot v_z$).

La energía acumulada en una arista $e_{ij}$ de longitud $d_{ij}$ con velocidad sobre el suelo $v_g$ es:
$$EEE_{ij} = P(t) \cdot \frac{d_{ij}}{v_g}$$

---

## 3. Función de Costo Multi-Objetivo de las Aristas del Grafo

El peso de una arista $W(e_{ij})$ en el grafo espacial $G = (V, E)$ integra múltiples criterios:

$$W(e_{ij}) = \alpha \cdot \frac{d_{ij}}{d_{max}} + \beta \cdot \frac{EEE_{ij}}{EEE_{max}} + \gamma \cdot R(e_{ij}) + \delta \cdot P_{obs}(e_{ij})$$

Donde:
- $\alpha, \beta, \gamma, \delta$: Coeficientes de ponderación ajustables ($\sum = 1.0$).
- $R(e_{ij})$: Penalización por factor de riesgo (sobrevuelo cercano a aglomeraciones urbanas según `urban_zones.geojson`, zonas de cables de alta tensión, o áreas de fuego NASA FIRMS).
- $P_{obs}(e_{ij})$: Penalización infinita si la arista cruza el relieve topográfico o una zona de exclusión activa (NOTAM de la DGAC).

---

## 4. Protocolo de Retorno Seguro a Base (RTH) por Sotavento

En caso de emergencia (batería baja, pérdida de telemetría o alarma manual):
1. **Evaluación de Ruta Directa**: Se calcula el costo $EEE_{direct}$ en línea recta hacia el Aeródromo de Quintero considerando el viento $\vec{w}$.
2. **Detección de Viento de Frente Crítico**: Si el viento en contra reduce la autonomía proyectada por debajo del 15% de reserva:
3. **Desvío Táctico por Sotavento**: El LPP selecciona corredores aéreos ubicados en la ladera protegida (sotavento) de los cordones de cerros costeros entre Puchuncaví y Quintero, donde la velocidad efectiva del viento decae significativamente ($\vec{w}_{eff} < \vec{w}$), permitiendo un vuelo de retorno de menor consumo.
4. **Garantía**: Asegurar aterrizaje con al menos **15% de State of Charge (SOC)**.
