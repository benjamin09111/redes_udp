## Ruteo y Redes Resilientes

Temática: Contaminación ambiental

Integrantes: Benjamín Morales, Benjamin Polanco, Benjamin Aceituno, Aldo Morales

## 1. Introducción

El monitoreo de la calidad del aire en el complejo industrial de Quintero, Ventanas y Puchuncaví representa uno de los desafíos de gestión ambiental y salud pública más urgentes de Chile, encontrándose regulado de manera prioritaria mediante un Plan de Prevención y Descontaminación Atmosférica (PPDA). A diferencia de valles interiores o zonas urbanas del sur como Santiago o Temuco, la Bahía de Quintero presenta una dinámica microclimática crítica caracterizada por la contención topográfica de emisiones e inversión térmica costera. Esta condición desencadena el fenómeno de fumigación costera, donde las masas contaminantes retenidas en estratos atmosféricos elevados descienden de forma abrupta a nivel de suelo al incrementarse la temperatura matinal, generando picos históricos de intoxicación en la población.

Debido a esta vulnerabilidad sistemática, la zona concentra la mayor densidad de estaciones del Sistema de Información Nacional de Calidad del Aire (SINCA) del país, contando con una topología oficial de 9 estaciones de monitoreo terrestre. La disposición geográfica de estas estaciones responde a modelos de dispersión de contaminantes, a la dirección de vientos dominantes de la bahía y a la necesidad de resguardar receptores vulnerables como colegios, centros de salud y áreas residenciales en Loncura, Quintero centro y Ventanas. Sin embargo, las chimeneas industriales del sector liberan contaminantes tóxicos (como Dióxido de Azufre, material particulado y compuestos orgánicos) a alturas de entre 50 y 110 metros, acumulándose de forma no lineal en capas elevadas de la atmósfera. Dado que las estaciones fijas del SINCA miden únicamente a nivel de suelo (~2 m AGL), la red tradicional presenta un 100% de ceguera vertical sobre la nube contaminante en altura. El despliegue de Vehículos Aéreos No Tripulados (UAVs) operando en el rango normativo de 0 a 120 metros AGL (fijado por la normativa de la DGAC en Chile) permite interceptar estas plumas en altura antes de su descenso. Asimismo, operar sobre la infraestructura oficial de las 9 estaciones del SINCA ofrece un marco metodológico válido para contrastar las lecturas de superficie con los perfiles en altura, permitiendo al mismo tiempo realizar la calibración e intercalibración in-situ (co-location) del sensor portátil del dron al compararlo con los instrumentos fijos de alta precisión. No obstante, el uso de aeronaves no tripuladas en entornos costeros se enfrenta a restricciones ciberfísicas severas, incluyendo el Consumo Energético Estimado acotado por las baterías, los límites cinemáticos de viraje de la nave y la presencia de ráfagas de viento marino desfavorables.


Para resolver estas limitaciones, el trabajo de referencia de Kosior et al. (2024) propone una arquitectura de Planificador de Trayectorias Adaptativo (APP) estructurada en dos niveles. Este marco combina un Planificador Global de Rutas (GPP), que calcula en fase offline trayectorias globales eficientes en energía y libres de obstáculos, con un Planificador Local de Rutas (LPP) que opera online a bordo de la aeronave para recalcular rutas alternativas en tiempo real ante imprevistos o fallas de comunicación. En este trabajo se modela la operación de una flota de UAVs de monitoreo ambiental con base de despacho en el Aeródromo de Quintero, navegando hacia las 9 estaciones de medición del SINCA como nodos objetivo en la bahía. La infraestructura aérea se representa mediante un grafo espacial geolocalizado en el entorno QGIS, donde las aristas constituyen corredores aéreos de vuelo seguro. Para evaluar la resiliencia ciberfísica de esta red no tripulada frente a contingencias reales de la región (tales como incendios forestales de interfaz, sismos, turbulencias por vientos, pérdida de telemetría y restricciones de espacio aéreo mediante boletines NOTAM de la DGAC), el sistema se nutre dinámicamente mediante consultas activas a un motor multi-API en tiempo real (Open-Meteo, SINCA, DGAC). Se exploran y evalúan diversos algoritmos de enrutamiento (Dijkstra, A*, Algoritmos Genéticos y Colonias de Hormigas) y se analiza la capacidad de reconfiguración activa de flujos sobre el grafo, implementando un protocolo interactivo de Retorno Seguro a Base (RTH) asistido por el relieve (sotavento) para garantizar la continuidad de la misión, la conectividad y la protección de la salud pública

## 2. Problemática identificada

La recolección de datos de calidad del aire mediante redes convencionales en el complejo industrial y residencial de Quintero, Ventanas y Puchuncaví se enfrenta a una ceguera metodológica y física crítica: las estaciones terrestres fijas del Sistema de Información Nacional de Calidad del Aire (SINCA) miden la contaminación únicamente a nivel de suelo (~2 metros de altitud) y en coordenadas estáticas. Sin embargo, en esta bahía industrial, las fuentes emisoras (termoeléctricas, fundiciones de cobre y refinerías) liberan contaminantes tóxicos (como Dióxido de Azufre, Material Particulado y Compuestos Orgánicos Volátiles) a alturas de entre 50 y 110 metros. Bajo la influencia de la inversión térmica costera y el atrapamiento de gases en la zona, la contaminación no se distribuye de forma lineal ni proporcional con la altitud, sino que se acumula en capas o estratos atmosféricos específicos (entre 80 y 120 metros) sin tocar la superficie. Como resultado, las redes de tierra dejan un 100% de ceguera sobre la distribución tridimensional (3D) de los contaminantes en altura, registrando aire aparentemente limpio hasta que el calentamiento solar rompe la capa y provoca el fenómeno de fumigación costera, donde la nube tóxica desciende abruptamente sobre colegios y zonas residenciales. Por ello, el uso de Vehículos Aéreos No Tripulados (UAVs o drones) en el rango de 0 a 120 metros


sobre el nivel del suelo —cumpliendo estrictamente con la normativa de la DGAC en Chile— surge como la única tecnología capaz de realizar un perfilamiento 3D para interceptar las concentraciones tóxicas en altura antes de su descenso y prevenir episodios de intoxicación con la debida anticipación23.Existen restricciones de energía muy estrictas (Consumo Energético Estimado, \$\text{EEE}\$) y límites de giro y ascenso de la propia aeronave que dificultan el diseño de rutas viables45. Al operar en una zona costera hostil, el dron se enfrenta constantemente a ráfagas de viento marino imprevistas y cambiantes provenientes de la bahía de Quintero que alteran severamente su velocidad respecto al suelo (\$v_g\$)5. La potencia requerida para que el UAV mantenga la sustentación contra este viento de frente puede agotar la batería mucho antes de completar el itinerario de muestreo tridimensional, impidiendo que la nave retorne a salvo a su base de despacho en el Aeródromo de Quintero45.En adición, la compleja geografía local representa un riesgo físico constante: el relieve de la zona, caracterizado por acantilados, cerros costeros y cordones montañosos colindantes, actúa como un conjunto de obstáculos terrestres fijos que los drones deben esquivar5. Asimismo, las condiciones meteorológicas dinámicas de esta costa alteran el rendimiento de la nave; por ejemplo, las temperaturas extremas degradan la eficiencia de la batería LiPo, mientras que precipitaciones moderadas o fuertes imponen vetos de despegue5. A esto se suman los eventos dinámicos y catástrofes comunes en Chile, como la alta sismicidad, los incendios forestales de interfaz en los cerros, la pérdida imprevista de señal de telemetría/celular y las restricciones de espacio aéreo de emergencia decretadas por la DGAC mediante boletines NOTAM, eventos que pueden destruir físicamente o desestabilizar la infraestructura terrestre de soporte e inhabilitar tramos de vuelo5.Actualmente, estas redes de monitoreo y planificación de vuelo presentan una gran falta de resiliencia al operar de manera estática y rígida45. Si un nodo terrestre de comunicaciones se apaga, si se pierde la señal con la Estación de Control Terrestre (GCS) o si una ruta se bloquea imprevistamente por un incendio o un NOTAM, los sistemas convencionales no tienen la capacidad de reconfigurar su trayectoria de manera autónoma en tiempo real45. Esta vulnerabilidad provoca que, ante cualquier falla local o cambio ambiental repentino, toda la misión de monitoreo de contaminación se vea afectada, arriesgando la pérdida de la aeronave y fallando en el propósito de alertar y resguardar oportunamente la salud de la comunidad15.

## 3. La solución

Para resolver la ceguera metodológica de las redes terrestres y garantizar la resiliencia operativa ante la hostilidad costera y las fallas de infraestructura en la Bahía de Quintero, se propone un sistema ciberfísico de enrutamiento aéreo adaptativo, desarrollado sobre la plataforma QGIS y fundamentado en la arquitectura en dos niveles de Kosior et al. (2024)12. La solución se articula


en cuatro pilares integrados:1. Perfilamiento 3D Normativo e Intercepción TempranaPara superar la falta de cobertura en altura del sistema SINCA, la solución despliega UAVs programados para realizar patrones de vuelo tridimensionales en el estrato de 0 a 120 metros AGL (Above Ground Level), respetando de manera estricta el límite legal fijado por la Dirección General de Aeronáutica Civil (DGAC) en Chile34. Al volar e interceptar las plumas contaminantes directamente en su rango de emisión industrial (50 a 110 metros) y en la zona de atrapamiento por inversión térmica (80 a 120 metros), el dron captura la concentración real de gases tóxicos (\$\text{SO}_2\$, MP y COVs) antes de que ocurra el fenómeno de fumigación costera sobre la población35. Asimismo, el dron realiza maniobras de calibración in-situ (co-location) suspendido junto a las 9 estaciones de referencia del SINCA para corregir dinámicamente la deriva de sus sensores portátiles antes de iniciar la misión en zonas sin cobertura5.2. Arquitectura de Enrutamiento Adaptativo en Dos Niveles (GPP / LPP)Para gestionar las restricciones de energía (\$\text{EEE}\$), la cinemática de vuelo y la falta de resiliencia ante imprevistos, se implementa una estructura jerárquica de planificación de rutas16:Planificador Global de Rutas (GPP - Global Path Planner): Opera en la fase offline (pre-vuelo) dentro del entorno QGIS12. Modela el espacio como un grafo georreferenciado que conecta la base de despacho en el Aeródromo de Quintero con los nodos de medición del SINCA25. El GPP resuelve un problema de optimización multiobjetivo para calcular la trayectoria inicial más eficiente en distancia y consumo energético (\$\text{EEE}\$), respetando los límites de viraje de la aeronave y evitando la topografía terrestre fija (\$M_t\$)7more_horiz.Planificador Local de Rutas (LPP - Local Path Planner): Opera en la fase online de forma autónoma a bordo de la aeronave o desde la Estación de Control Terrestre (GCS)610. Ante la pérdida imprevista de la señal de telemetría o el bloqueo de un tramo por emergencias, el LPP asume el control e imparte un recálculo dinámico de la ruta en tiempo real (\$CT \le 4.55\text{ s}\$), garantizando un retorno seguro a la base (RTH) o bordear el obstáculo sin riesgo de colisión (\$N_{COL} = 0\$)10more_horiz.3. Nutrición Dinámica del Grafo mediante Motor Multi-APIEl grafo de transporte aéreo no es estático; se reconfigura continuamente al consumir datos en vivo provenientes de una arquitectura distribuida de APIs y bases de datos24:Open-Meteo API (Viento, Temperatura y Precipitación): Actualiza las aristas del grafo con la velocidad y dirección del viento marino, recalculando la velocidad terrestre (\$v_g\$) y el consumo de batería restante. Ante temperaturas extremas que degradan la química LiPo, ajusta el radio de vuelo; ante precipitaciones moderadas o fuertes, gatilla un bloqueo preventivo


de despegue (No-Go)24.DGAC NOTAM API (Espacio Aéreo): Ingiere boletines de cierre temporal de espacio aéreo (por ejercicios militares o combate aéreo de incendios por CONAF), dibujando polígonos de exclusión aérea (\$M_a\$) en QGIS para que el LPP rodee la zona prohibida en caliente4more_horiz.SINCA API (Episodios Críticos PPDA): Detecta picos de \$\text{SO}_2\$ en estaciones terrestres, alterando dinámicamente los pesos del grafo para redirigir la prioridad del dron hacia la sobremedición de las fuentes emisoras industriales4.NASA FIRMS API y OpenStreetMap (Incendios y Densidad Poblacional): Identifica focos térmicos activos para crear zonas de exclusión por turbulencia y aplica reglas horarias/espaciales para evitar el sobrevuelo de multitudes, cumpliendo la normativa de seguridad aeronáutica24.4. Protocolo de Resiliencia Ciberfísica y Retorno de Emergencia (RTH)En caso de falla crítica, desconexión de red o agotamiento acelerado de energía, el sistema activa el protocolo autónomo de Retorno Seguro a Base (RTH)210. A diferencia de los sistemas tradicionales que fuerzan una línea recta, el algoritmo evalúa la posición GPS y el vector de viento de la API; si el viento de frente compromete el regreso directo, recalcula una ruta protegida utilizando el sotavento de los cerros costeros (protección física del relieve), asegurando que la aeronave aterrice en el Aeródromo de Quintero con al menos un 15% de batería de respaldo2.

## 3.4. Objetivos del Proyecto

Diseñar, simular y evaluar un grafo espacial geolocalizado en tres dimensiones \$(x, y, z)\$ adaptado al complejo industrial y costero de Quintero, Ventanas y Puchuncaví para una flota de UAVs encargados del monitoreo ambiental 3D (en el rango normativo de 0 a 120 m AGL), implementando la arquitectura de planificación adaptativa en dos niveles (GPP/LPP) basada en el trabajo de Kosior et al. (2024) e integrando datos dinámicos mediante un motor multi-API en tiempo real, con el fin de optimizar el enrutamiento y maximizar la resiliencia operativa del sistema ante fallas de infraestructura, restricciones regulatorias y eventos ambientales adversos.

## 3.4.1. Objetivo General

## 3.4.2. Objetivos Específicos

- 1. Modelar la infraestructura espacial 3D de la red (Grafo Espacial): Definir y geolocalizar sobre la topografía real de la Bahía de Quintero un conjunto de nodos \$v_i \in V\$ (Aeródromo de Quintero como base de despacho/RTH, 9 estaciones de monitoreo del SINCA y receptores sensibles) y sus respectivas aristas (corredores o "calles aéreas" navegables), restringiendo la altitud operacional al estrato de 0 a 120 metros AGL para cumplir con la norma DAN 151 de la DGAC e interceptar las plumas contaminantes en altura.


- 2. Implementar el motor Multi-API de metadata y variables ambientales: Conectar e integrar fuentes de datos geoespaciales y en tiempo real (Open-Meteo API para viento y temperatura, Modelo Digital de Elevación DEM para relieve, Subtel/OpenCellID para sombras de telemetría y OpenStreetMap para densidad poblacional) con el objetivo de calcular dinámicamente las penalizaciones, la velocidad respecto al suelo (\$v_g\$), el Consumo Energético Estimado (\$\text{EEE}\$) y los costos de riesgo en las aristas del grafo.

- 3. Desarrollar el simulador de fallas ciberfísicas y eventos dinámicos: Programar un generador de riesgos interactivo y autónomo alimentado por APIs activas (DGAC NOTAM API para cierres de espacio aéreo, NASA FIRMS API para zonas de exclusión por incendios forestales, SINCA API para episodios críticos PPDA y Open-Meteo para precipitaciones o caídas de nodos por turbulencia/sismos), alterando en caliente los pesos del grafo y gatillando la reconfiguración de flujos sobre la red.

- 4. Programar y evaluar el Planificador Global de Rutas (GPP - Phase Offline): Implementar y evaluar algoritmos de optimización deterministas y metaheurísticos (Dijkstra, A, Algoritmos Genéticos y Colonias de Hormigas \$\text{ACO}_R\$*) para calcular las trayectorias globales iniciales multi-destino del UAV antes del despegue, minimizando la longitud total de la ruta (\$\text{LEN}\$), esquivando obstáculos fijos (\$M_t\$) y optimizando el consumo energético (\$\text{EEE}\$).

- 5. Codificar el Planificador Local Dinámico (LPP - Phase Online) y protocolo RTH: Desarrollar un algoritmo de reconfiguración activa a bordo (A Dinámico / RRT**) capaz de recalcular autónomamente la ruta de vuelo en tiempo real (\$\text{CT} \le 4.55\text{ s}\$) ante la caída imprevista de un enlace, la aparición de un NOTAM o la pérdida de telemetría, garantizando cero colisiones (\$N_{\text{COL}} = 0\$) y ejecutando un protocolo de Retorno Seguro a Base (RTH) asistido por la topografía (sotavento) con al menos un 15% de batería de respaldo.

- 6. Cuantificar y evaluar la resiliencia estructural de la red: Someter la red a pruebas de estrés computacional para comparar cuantitativamente el desempeño del sistema adaptativo resiliente frente a una red de rutas estáticas convencional, evaluando métricas de alto nivel (tasa de misiones completadas, porcentaje de datos ambientales capturados y conectividad de red) y métricas cinemático-energéticas del paper (suavidad de trayectoria \$\text{SMOO}\$, longitud \$\text{LEN}\$ y consumo \$\text{EEE}\$).

- 7. Implementar el entorno de simulación y visualización geoespacial en QGIS: Construir una interfaz interactiva en QGIS que represente la topografía real de la Bahía de Quintero con la red navegable, visualizando en tiempo real la navegación 3D multinave, la inyección de eventos desde las APIs, los


polígonos de exclusión aérea (\$M_a\$) y la reconfiguración visual de las rutas alternativas ante fallas simuladas de la infraestructura.

*Figura 1. Mockup conceptual de la interfaz de usuario propuesta para el simulador de enrutamiento y resiliencia.*

## 3. Arquitectura y Funcionamiento del Software (Simulador Ciberfísico)

El software está diseñado como un simulador ciberfísico dinámico enfocado en el monitoreo aéreo ambiental y la evaluación de resiliencia en redes no tripuladas. La arquitectura desacopla la planificación estratégica offline de la reactividad táctica online, integrando los siguientes módulos operacionales:


## Requisitos funcionales

Botón de "Retorno Seguro" (RTH - Return to Home): Modelar la resiliencia ciberfísica en tiempo real. En la interfaz de nuestro simulador web, implementaremos un botón interactivo de "Retorno de Emergencia". Al presionarlo en cualquier momento del vuelo, el Planificador Local de Rutas (LPP) [5] tomará la coordenada GPS actual del dron y calculará el camino de regreso más seguro y eficiente hacia el Aeródromo de Quintero. El cálculo no será una línea recta. Si al apretar el botón la API de Open-Meteo detecta que el viento de frente en la ruta directa superará la autonomía de la batería restante, nuestro algoritmo de enrutamiento resiliente buscará un camino que aproveche el sotavento de los cerros costeros (protección física del relieve) para garantizar que la nave aterrice con al menos un 15% de batería de respaldo.

Misión del dron: destino objetivo, misiones secundarias, etc. Se configura todo.

Se pueden apretar eventos en el momento que sea: retorno a base en caso de perder conexión, simular incendio en la zona, simular viento más bajo o alto, todo configurable y muchos basados en datos históricos.

El Software consume api data real: muestra al lado el estado actual (Temperatura, Precipitación, Vientos, muestra los nodos más importantes actualmente, etc). Se muestra siempre la batería del dron y va bajando según muchos factores. Se muestra la hora que permite calcular zonas de mayor densidad poblacional, que hace tomar decisiones al dron, priorizando como nodos para medir en misiones automáticas o evitar zonas muy pobladas: Está estrictamente prohibido volar sobre concentraciones de personas, de noche, en eventos masivos, cerca de recintos militares, cárceles o a menos de 2 km de aeropuertos y aeródromos sin los permisos formales.

Apretar “Iniciar medición automática según nodos de prioridad” y según la prioridad actual del nodo va a medir zonas interesantes o donde hay más densidad de personas, puedo indicar cantidad de paradas si quiero, todo es configurable.

## 3.1. Modelamiento de la Red Espacial 3D y Configuración Multinave

- Grafo Geolocalizado Real: La red se construye sobre el mapa real de la Bahía de Quintero, Ventanas y Puchuncaví utilizando el entorno QGIS5. Los nodos representan puntos de interés operacional (Aeródromo de Quintero, estaciones SINCA y receptores vulnerables)12, mientras que los arcos o aristas actúan como "corredores o calles aéreas navegables".

- Vector de Posición Tridimensional \$(x, y, z)\$: Cada nodo \$v_i \in V\$ incorpora explícitamente la variable de altitud \$z\$.

- Restricción de Altitud Normativa (0 a 120 m AGL): Para dar cumplimiento estricto a la normativa DAN 151 de la DGAC en Chile, el espacio aéreo navegable se restringe al estrato de 0 a 120 metros sobre el nivel del suelo2. Este rango operacional intercepta directamente las plumas


- industriales emitidas a alturas de entre 50 y 110 metros y atrapadas por la inversión térmica costera23.

- Configuración Flota Multinave: El software permite configurar un número variable de \$M\$ UAVs navegando concurrentemente sobre un grafo de \$N\$ nodos.

- Ciclo de Misión de Muestreo: Cada aeronave parte desde un nodo de origen seguro (Aeródromo de Quintero), transita por los corredores aéreos hacia zonas de potencial contaminación, ejecuta un tiempo de permanencia/recolección de datos en el destino y retorna de forma obligatoria al mismo nodo de origen5.

## 3.2. Motor Macro de Enrutamiento, Resiliencia e Inyección de Fallas

- Gestión Macro de Flujos: El sistema administra el tráfico aéreo sobre el grafo, evaluando la resiliencia estructural de la red y reconfigurando los flujos de vuelo en tiempo real sin interrumpir la operación global5.

- Inyección Dinámica de Eventos y Fallas: El simulador permite inyectar fallas físicas o ambientales en tiempo real5:

- Caída Física de Nodos: Desconexión o destrucción de estaciones terrestres y repetidores de telemetría (por sismos, fallas eléctricas o vandalismo)4.

- Bloqueo Completo de Aristas: Inhabilitación de corredores aéreos enteros debido a incendios forestales activos, ráfagas de viento costero desfavorables o lloviznas que afectan los sensores4.

- Protocolo de Retorno Seguro (RTH Interactivo): La interfaz incluye un botón interactivo de Return to Home5. Al activarse, el sistema toma la coordenada \$3D\$ actual de la nave y recalcula dinámicamente la ruta de regreso al Aeródromo de Quintero. Si la API meteorológica detecta viento de frente que comprometa la batería restante, el algoritmo desvía el vuelo aprovechando la protección física del relieve (sotavento de los cerros) para asegurar un aterrizaje con al menos un 15% de batería de respaldo5.

## 3.3. Motores Algorítmicos (GPP / LPP) y Función de Costo Multi-Objetivo

- Suma Ponderada de Costos Dinámicos: El peso de cada arista se evalúa continuamente mediante una función de costo multi-objetivo: \$\$C(S, \mathbf{p}) = \sum_{n=1}^{N_c} \omega_n c_n\$\$ Donde los factores de penalización (distancia, consumo energético \$EEE\$, riesgo poblacional y turbulencia) se actualizan dinámicamente según los datos de las APIs4more_horiz.


- Planificador Global de Rutas (GPP - Phase Offline): Encargado de calcular la trayectoria global inicial entre el origen y los nodos de medición814. Soporta algoritmos deterministas y metaheurísticos de optimización:

- Dijkstra / A:* Para la resolución eficiente de rutas óptimas en grafos estáticos7.

- Algoritmos Genéticos (GA): Para escenarios con alta necesidad de repetibilidad y estabilidad en la ruta15more_horiz.

- Optimización por Colonia de Hormigas (ACO / \$\text{ACO}_R\$): Para encontrar la combinación de menor consumo energético (\$EEE\$) y longitud de trayectoria en entornos de alta complejidad15more_horiz.

- Planificador Local de Rutas (LPP - Phase Online): Opera a bordo o en la estación terrena con alta velocidad computacional (\$CT \le 4.55\text{ s}\$) ante contingencias8more_horiz:

- A Dinámico / Dijkstra Mejorado:* Para la reconfiguración rápida de pesos cuando se bloquea una arista por un evento imprevisto721.

- Inspiraciones en RRT / RRT:* Para la generación ágil de trayectorias locales de evitación de obstáculos dinámicos y zonas de exclusión7more_horiz.

## 3.4. Motor de Consultas Activas Multi-API en Tiempo Real

El simulador ejecuta un demonio de consulta continua (peteo/pinging) a APIs externas para nutrir la matriz de riesgo del grafo45:

- Open-Meteo API: Ingiere velocidad/dirección del viento, precipitación y temperatura4. Ajusta el consumo de batería (\$EEE\$) en tiempo real y gatilla vetos de despegue (No-Go) si la lluvia o el viento superan los umbrales de seguridad4.

- SINCA API (Ministerio del Medio Ambiente): Recibe lecturas en vivo de las 9 estaciones de la bahía1. Ante picos de \$\text{SO}_2\$ o episodios PPDA, eleva automáticamente el peso de prioridad de los nodos industriales colindantes para enviar al dron a sobremedir la pluma4.

- DGAC NOTAM API: Descarga coordenadas de cierres temporales de espacio aéreo, proyectando polígonos de exclusión (No-Fly Zones) en QGIS que el LPP rodea autónomamente4.

- OpenStreetMap / NASA FIRMS API: Proporciona datos de densidad poblacional y focos térmicos activos de incendios45. Aplica reglas horarias para prohibir el sobrevuelo directo de multitudes (colegios y centros urbanos), desviando el dron a zonas adyacentes despejadas45.

## 4. Estructura y red


Para simular una red de comunicaciones se necesitan nodos basados en condiciones reales de Chile. La red se compone de tres partes: la infraestructura, que define el mapa y los nodos; la metadata, que entrega información sobre fallas, prioridad y conexión; y los eventos, que permiten evaluar la resiliencia de la red ante fallas.

## 4.1 Infraestructura a utilizar

Corresponde solo a los nodos físicos y sus coordenadas (además de la unión entre ellos) para crear el grafo y red, por ahora sin mayor información. A continuación, se detallan las fuentes utilizadas para la construcción del mapa de viaje.

- \- Aeródromo de Quintero: Permite extraer coordenadas para usarlas como nodos de despacho (origen de rutas) [https://www.bcn.cl/siit/mapasvectoriales]

- \- Estaciones SINCA: Red de monitoreo que contiene información nacional de la calidad de aire, estaciones que incluyen las de Quintero, Ventanas y Puchuncaví, usadas como destino ya que se mide contaminación.

- \- [https://sinca.mma.gob.cl/][https://ppda.mma.gob.cl/wp-content/uploads/2025/05/Exa men_Informacion_QPC_2025datos2024.pdf)] [URL 🔗](https://ppda.mma.gob.cl/wp-content/uploads/2025/05/Examen_Informacion_QPC_2025datos2024.pdf)

- \- Red de estaciones del MMA: Estaciones públicas adicionales (complementa a las anteriores) de destino como nodos donde se mide contaminación.

- [\- [https://airecqp.mma.gob.cl/nueva-red-mma/]](https://airecqp.mma.gob.cl/nueva-red-mma/)

- \- Geolocalización Arbitraria (Google Maps): Obtención directa de posiciones geográficas (x, y) mediante selección de puntos en áreas sin infraestructura registrada (cerros, zonas rurales o cuerpo de agua), garantizando la continuidad de los trayectos. [https://maps.google.com] [URL 🔗](https://maps.google.com/)

- \- Generación Algorítmica de Nodos (Discretización espacial): Creación matemática de coordenadas intermedias mediante técnicas geométricas (interpolación lineal a intervalos regulares, grillas en malla o muestreo estocástico), estructurando la densidad de vértices del grafo entre los nodos de origen y destino. [Entorno de Python: Shapely / GeoPandas]

- \- Overpass QL + OpenStreetMap (Infraestructura física de apoyo): Extracción de coordenadas geográficas (x, y) de infraestructura terrestre (postes eléctricos, torres de alta tensión e intersecciones) para utilizarlas como nodos de paso intermedios en el grafo. [https://overpass-turbo.eu/] [URL 🔗](https://overpass-turbo.eu/)

- \- Red Vial de Chile (Shapefile BCN-SIIT): Proporciona la red de carreteras y caminos rurales oficiales de Chile. Incluye también capas de división comunal, masas de agua, red ferroviaria, entre otros. [https://www.bcn.cl/siit/mapas_vectoriales_18-10-2019]

## 4.1.1 Información para los nodos

## 4.1.2 Información para las conexiones y aristas


- \- ArcGIS REST Services – Red Vial (MOP): Expone mapas y datos geográficos de los caminos del país mediante la tecnología ArcGIS REST API [https://rest-sit.mop.gob.cl/arcgis/rest/services/VIALIDAD/Red_Vial_Chile/MapServer]

- \- Geoportal IDE Chile – Red Vial Nacional: Es un conjunto de datos espaciales digitales que muestra la ubicación y el estado de los caminos públicos del país, detalla los tipos de carpeta o superficie de rodadura y caminos básicos.

- [\- [https://geoportal.cl/geoportal/catalog/36785/Red%20Vial%20Nacional]](https://geoportal.cl/geoportal/catalog/36785/Red%20Vial%20Nacional)

- \- Google Open Buildings (Polígonos de edificios): Permite identificar obstáculos tridimensionales estáticos (edificios) que los drones deben rodear. [https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_Research_o pen-buildings_v3_polygons?hl=es-419]

- \- ArcGIS REST – Infraestructura rural/urbana (SMA): Infraestructura de Datos Geoespaciales (IDE) de la institución. Su propósito fundamental es agrupar y disponibilizar capas de información geográfica (cartografía digital) sobre el equipamiento y redes conectivas básicas del país.

- \- [https://ideserver.sma.gob.cl/arcgis/rest/services/IDE/Infraestructura_rural_urbana/M apServer/10/query] [URL 🔗](https://ideserver.sma.gob.cl/arcgis/rest/services/IDE/Infraestructura_rural_urbana/MapServer/10/query)

## 4.2 Metadata

Corresponde a las características a incorporar en la infraestructura, nutriendo la información del grafo. Además, estos datos afectarán en las decisiones tomadas de enrutamiento.

- API del Sistema SINCA (Ministerio del Medio Ambiente): tiempo real e históricos de contaminantes normados (PM2.5, PM10, SO₂, NO₂, CO, O₃) medidos por cada estación de monitoreo de calidad del aire en Chile. Esta metadata se asigna a los nodos para definir su prioridad de muestreo: a mayor polución, más atractivo y prioridad se vuelve el nodo para el algoritmo GPP. [https://sinca.mma.gob.cl/] Entrega datos en

- \- Mapas de Cobertura Subtel (Registro Nacional de Conectividad): Plataforma ciudadana que muestra la cobertura de servicios de telecomunicaciones (2G a 5G) por operadora (Entel, Movistar, Claro, entre otros) y permite identificar zonas con señal y las sombras sin cobertura. Esta metadata se usa en las conexiones: si se pasa por una zona sin señal celular, el riesgo de pérdida de telecomunicaciones aumenta, perjudicando en la seguridad del vuelo. [https://rnc.subtel.gob.cl/]

- \- Google Earth Engine Catalog (SRTM DEM – NASA): Modelo Digital de Elevación (DEM) del Shuttle Radar Topography Mission (SRTM) con resolución aproximada de 30 metros, que proporciona la altitud del relieve sobre el nivel del mar para cualquier punto del mundo. Esta metadata da la elevación del terreno en cada punto intermedio de la arista para definir la altitud segura de vuelo y evitar colisiones con el relieve.


[https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003 ][https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D3 0_V3_2] [URL 🔗](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003)

- \- OpenStreetMap Metadata (Overpass QL): API que permite extraer coordenadas y atributos de puntos de interés específicos (hospitales, colegios, edificios, etc) en los alrededores. Esta metadata sirve para calcular el costo y riesgo en caso de caída del dron: nodos cercanos a infraestructura crítica o zonas de alta densidad cuestan más y requieren rutas más conservadoras. [https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL]

Permite ver donde hay mas gente tmbien…

## 4.3 Eventos o fallas geolocalizadas

Corresponde a los eventos que evaluarán la resiliencia de la red, gatillando problemas en el grafo y siendo las causas de calcular nuevamente los enrutamientos.

- \- API de Incendios Activos de la NASA (MODIS / FIRMS): Mapea incendios forestales en vivo mediante satélites, entregando coordenadas del frente de fuego, intensidad radiativa y hora de detección. Si un incendio coincide con una de las aristas de vuelo en Puchuncaví, Quintero o Ventanas, esa arista se bloquea dinámicamente por la presencia de humo extremo, calor y turbulencia térmica. [https://firms.modaps.eosdis.nasa.gov/]

- \- API de la DMC (Dirección Meteorológica de Chile) / Windy: Servicios meteorológicos que proporcionan vectores de viento en tiempo real a diferentes alturas. Si las ráfagas en una arista aérea superan el límite para el dron, la conexión se inhabilita para el ruteo hasta que las condiciones mejoren. [https://www.meteochile.gob.cl/]

- \- API del Centro Sismológico Nacional / Seismic World Records: Servicio del CSN (Universidad de Chile) y EMSC que entrega en tiempo real magnitud, profundidad, epicentro e intensidad de sismos en Chile. Si ocurre un sismo de gran magnitud cerca de un nodo base, este nodo se declara no accesible por falla de energía en la estación de recarga, haciendo que el dron vuelva a calcular la ruta a otra base que sí funcione. [https://www.sismologia.cl/] [URL 🔗](https://www.sismologia.cl/)

- \- API de Precipitaciones en Tiempo Real (JAXA GSMaP / RainViewer): Sistema de monitoreo de precipitaciones por hora derivado de sensores satelitales y de radar. Si la tasa de lluvia en una zona del grafo supera el umbral operacional de seguridad del UAV, las aristas de esa sección se inhabilitan dinámicamente por riesgo de falla electrónica en los componentes y alteración en las mediciones del sensor de polución, forzando al dron a abortar la misión actual y activar el protocolo LPP de retorno de emergencia a la base operativa más cercana. [https://sharaku.eorc.jaxa.jp/GSMaP/]


- \- Simulación de Pérdida de Telemetría / Enlace GCS (Falla Lógica): Desconexión aleatoria o por sombra de cobertura móvil (Subtel) del enlace de datos entre el dron y la estación base. Al perder conectividad en un nodo intermedio, la nave activa el protocolo LPP para retornar o desviarse a un nodo con señal confirmada. Esto no tiene una fuente API pero sí es un evento que se puede gatillar, entre algunos otros que directamente inhabiliten nodos. Aquellos se definirán más adelante.

- 1. Incendios: bloquear rutas de vuelo. Ver si vale la pena incluir, en estas zonas hay incendios seguidos? y cuando hay incendios también cambia el viento y puede malograr las mediciones?

- 2. Lluvia, precipitaciones: Para simular la misión del dron, se fija una fecha, por defecto la actual. Se calcula un riesgo por clima: llovizna o chispeo no afecta, pero debido al aire húmedo se asume mayor gasto de batería; si hay lluvia moderada a fuerte no se permite ejecutar la misión.

- 3. Temperatura: Afecta la batería, eligiendo rutas más cortas o modificando la misión ya que se debe calcular si alcanza a llegar y volver.

- 4. Densidad de personas | horarios: Dependiendo de la hora, o la cantidad de personas, si es que hay eventos, se puede priorizar zonas donde se mida contaminación, o donde se evite pasar ya que Chile prohibe volar por zonas donde hay muchas personas. Aqui hay que hacer un equilibrio. Aplicar regla horaria al ejecutar la misión.

- 5. Vientos: Afectan la batería de la nave, rutas a tomar.

- 6. NOTAM por la DGAC y su API pública: Cierran áreas para operar.

- 7. Eventos críticos PPDA
