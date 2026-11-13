# Pauta — Tercer trabajo grupal (Fase 3)

> Transcripción del enunciado entregado por el curso. El texto de la sección
> **Enunciado** es literal; la tabla del final es nuestra y mapea cada punto al código.

---

## Enunciado

Para el tercer y último trabajo grupal del curso, deberá complementar el código en gitlab y
mostrar en funcionamiento su solución, a través de un video (a canvas deberá subir sólo el video),
en donde:

**1.-** Se ejecute la página desde el main en gitlab (puede acelerar esta parte). Lo importante es
que sirva para replicar la ejecución del proyecto.

**2.-** Explicar en qué consiste la infraestructura a utilizar, y esta deberá permitir generar
rutas realistas, es decir, no debe generar líneas rectas entre dos puntos que no se puedan
sobrevolar, ya sea por altitud o por bloqueos.

**3.-** La interfaz web deberá poder recibir los parámetros de consulta del usuario (restricciones
del usuario impuestas por su aplicación y punto de destino o área a recorrer según corresponda).

**4.-** La interfaz deberá ser capaz de cargar y considerar todos o solo algunos de los metadatos
y amenazas consideradas en el proyecto (utilizar popups o algún otro mecanismo para desplegar la
información que no se pueda visualizar como un polígono). Para habilitar o deshabilitar la
información mostrada, debe utilizar un panel de control que posea checkboxes.

**5.-** A partir de los datos obtenidos como amenaza, cada uno debe ser modelado como una
probabilidad de falla en su sistema. Para esto, deberá crear un archivo que genere la probabilidad
de fallo de cada enlace y nodo a partir de cada amenaza considerada en su trabajo.

**6.-** Deberá mostrar como solución la mejor ruta que satisfaga su problemática, utilizando y
detallando el funcionamiento de las siguientes técnicas:

- Pgr_dijkstra usando como peso solo la distancia en metros.
- Utilizando CPLEX o GUROBI, a partir del modelamiento formal de su problema de optimización,
  considere las variables de los metadatos y amenazas, y las condiciones del usuario como
  restricciones.
- Pgr_dijkstra utilizando los parámetros y condiciones propuestas en el punto anterior.
- Una metaheurística que considere viable para solucionar su problemática.

Las 4 rutas generadas deben ser posibles de habilitar o deshabilitar desde su panel de control.

**7.-** A partir de las probabilidades asignadas, deberá habilitar una opción que permita, a partir
de números aleatorios entre 0 y 100, determinar si ocurrirá o no la falla (a partir de si supera o
no el umbral de falla).

**8.-** Utilizar una métrica de resiliencia para su servicio, para cada una de las técnicas de
ruteo utilizadas e indicar cuál de ellas fue la más resiliente frente a las amenazas detectadas en
su infraestructura. Este valor debe ser desplegado junto a la leyenda que indica el algoritmo y
tiempo de cómputo de cada ruta.

**9.-** Realizar un ejemplo de caso en donde se pueda evidenciar que su solución provee una ruta
alternativa frente a una amenaza (mitigando lo más posible las amenazas), y que evidencie que se
logra cumplir sus objetivos iniciales.

---

## Dónde se cumple cada punto en este repositorio

*(Sección nuestra, no del enunciado.)*

| Punto | Dónde | Notas |
|---|---|---|
| 1 | `main.py --sin-descarga`, `docker-compose.yml`, [README.md](README.md) | El servicio `web` levanta sitio y API en `localhost:8000`. **El repositorio está en GitHub, no en GitLab.** |
| 2 | `ruteo/simulacion_fallas.py`: `_factores_altitud`, `_n_muestras` | Bloqueo por relieve (ventana de 120 m AGL menos 40 m de holgura) y por obstáculos verticales; muestreo del corredor cada 100 m. |
| 3 | `sitio_web/fase3.js` → `/api/rutas` | Destino, autonomía máxima, β y motor del camino mínimo. Cuando una técnica no respeta la autonomía, la leyenda lo advierte. |
| 4 | `sitio_web/index.html` `#f3-capas`, `/api/capas` | 10 checkboxes de amenazas y metadatos, más el de contingencia. Popups en rutas y en elementos caídos. |
| 5 | `ruteo/simulacion_fallas.py --guardar` → `sitio_web/data/probabilidades_falla.json` | 322 nodos y 855 aristas con `p_falla` y el desglose de factores. |
| 6 | `ruteo/tecnicas.py` | `dijkstra_distancia`, `milp_exacto`, `dijkstra_multicriterio`, `metaheuristica_akgun`. Una casilla por técnica en la leyenda. Ver la nota de solvers en el README. |
| 7 | `ruteo/simulacion_fallas.py`: `simular_fallas`; `/api/simulacion`; botón «Simular fallas» | `u = aleatorio[0,100)`, falla si `u < p_falla · 100`. |
| 8 | `/api/rutas` campo `resiliencia_R`; leyenda de `fase3.js` | Longitud, tiempo de cómputo, R y supervivencia Monte Carlo por técnica, con la ganadora marcada. |
| 9 | Destino La Greda con la casilla de contingencia | Dijkstra colapsa a R = 0 y las otras tres desvían manteniendo la misión. Tabla en el README. |

### Pendientes conocidos

- **Punto 1:** el enunciado dice «desde el main en gitlab». El repositorio del grupo está en
  GitHub (`benjamin09111/redes_udp`) y este trabajo vive en la rama `aceituno`, no en `main`.
- **Punto 6:** el MILP corre con GUROBI gracias a la licencia restringida que trae `gurobipy`,
  que **expira el 23-11-2026**. Después de esa fecha hay que actualizar el paquete o pedir la
  licencia académica, o la cadena de solvers cae a HiGHS.
- **Punto 8:** la resiliencia de la metaheurística se calcula sobre un par de caminos y la de las
  otras tres sobre uno solo, así que gana en parte por construcción.
