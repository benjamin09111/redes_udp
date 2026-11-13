# Guion de grabación — Video Fase 3

> Grupo 09 · CIT3435 · Ruteo resiliente de UAV en Bahía de Quintero
>
> **Cómo leer esto:** cada toma es una lista de acciones numeradas. Debajo de cada
> acción está **entre comillas y en cursiva lo que tienes que decir, literal**,
> mientras haces esa acción. Los recuadros `ESPERADO` son para que verifiques que la
> pantalla muestra lo correcto; si no sale eso, detén la grabación.
>
> Duración estimada: 12–16 min. Cada toma cubre un punto de [pauta_fase3.md](pauta_fase3.md).

---

## Antes de grabar (no se graba)

```bash
cd "/Users/benjaminaceituno/Desktop/Algoritmos de Ruteo y Redes/fase3"
docker compose up -d
curl -s http://localhost:8000/api/salud
```

- [ ] Responde `{"estado":"ok","backend_por_defecto":"pgrouting"}`.
      Si dice `"python"` **no grabes**: el punto 6 exige `pgr_dijkstra`.
- [ ] Navegador en `http://localhost:8000/sitio_web/`, terminal al lado.
- [ ] Haz un cálculo de prueba y recarga la página. El primer cálculo sin caché
      tarda ~1,2 s y los siguientes ~4 ms; así no grabas la espera.

---

# TOMA 1 · Replicabilidad → punto 1
*Terminal · ~90 s*

### 1. Muestras la carpeta del proyecto en el terminal.
> *"Este es el repositorio del proyecto. Todo el sistema se levanta con un solo
> comando, sin configuración manual."*

### 2. Escribes `python3 main.py --sin-descarga` y lo ejecutas. **Acelera el video en esta parte.**
> *"Este comando levanta una base de datos PostgreSQL con las extensiones PostGIS y
> pgRouting, carga los datos de infraestructura, metadatos y amenazas, construye el
> grafo de la red, calcula las rutas y publica el sitio web junto con la API. La
> bandera 'sin descarga' hace que use los datos ya descargados en vez de volver a
> consultar las APIs externas, para que la ejecución sea reproducible."*

### 3. Cuando termina, señalas la última línea.
```
ESPERADO: Listo. Abre el sitio en: http://localhost:8000/sitio_web/
```
> *"Termina indicando la dirección del sitio. El mismo puerto sirve la interfaz web
> y la API."*

### 4. (Opcional, pero suma) Ejecutas la verificación.
```bash
docker compose run --rm etl python tests/verificar.py
```
```
ESPERADO: 97 de 97 chequeos ejecutados correctos
```
> *"El proyecto incluye una batería de verificación que comprueba la integridad de
> los datos cargados y la consistencia de las rutas. Noventa y siete chequeos, todos
> correctos."*

### 5. Abres el navegador en la dirección.
> *"Y este es el sistema funcionando."*

---

# TOMA 2 · Infraestructura realista → punto 2
*Pestaña **Grafo** · ~2 min*

### 1. Haces clic en la pestaña **Grafo**.
> *"Primero, en qué consiste la infraestructura. La red está modelada como un grafo."*

### 2. Señalas la cifra de nodos.
```
ESPERADO: 322 nodos
```
> *"Tenemos 322 nodos. Cada uno es un punto de interés real, extraído de
> OpenStreetMap, de las estaciones de calidad del aire del SINCA y de los datos
> censales del INE: hospitales, colegios, comercios, plazas, bomberos, estaciones de
> monitoreo e instalaciones industriales."*

### 3. Señalas la cifra de aristas.
```
ESPERADO: 855 aristas
```
> *"Y 855 aristas. Cada arista es un corredor aéreo entre un nodo y sus cuatro
> vecinos más cercanos, más las conexiones necesarias para que la red quede
> completamente conectada, sin islas."*

### 4. Te detienes en este punto. Es el corazón del punto 2.
> *"Ahora, lo importante: el sistema **no asume que la línea recta entre dos nodos se
> puede volar**. Eso sería irreal. Lo que hace es recorrer cada corredor tomando una
> muestra **cada 100 metros**, y en cada muestra evalúa si en ese punto se puede
> volar o no. Si una sola muestra cae en zona prohibida, el corredor completo queda
> marcado como impasable y sale del grafo navegable."*

### 5. Explicas los dos mecanismos. El enunciado pide "por altitud **o** por bloqueos": los dos están implementados.
> *"Hay dos mecanismos por los que un tramo puede quedar prohibido.*
>
> *El primero es **la altitud**. La norma chilena DAN 151 de la DGAC limita la
> operación a 120 metros sobre el nivel del terreno, y nosotros además exigimos 40
> metros de separación mínima con el suelo. Eso deja una ventana vertical estrecha.
> Si el terreno sube tanto que el dron no cabe en esa ventana, el corredor se bloquea.
> Y si hay un obstáculo vertical, como las chimeneas del complejo de Ventanas que
> miden 152 metros, el corredor que entre en su radio de resguardo se penaliza con un
> lambda de 0,20.*
>
> *El segundo son **las restricciones operacionales**: niebla con visibilidad bajo mil
> metros, o viento sobre 12 metros por segundo. Ahí el tramo sale del grafo
> directamente."*

### 6. (Opcional, terminal) Ejecutas el modelo de amenazas.
```bash
docker compose run --rm etl python ruteo/simulacion_fallas.py
```
```
ESPERADO: 318 aristas bloqueadas (todas por niebla; 2 de ellas además por relieve)
          113 nodos bloqueados por niebla
          575 aristas penalizadas por ascenso · 33 por obstáculo vertical
```
> *"Veamos cuánto pesa cada mecanismo con los datos cargados.*
>
> *De las 855 aristas hay **318 bloqueadas, y todas por niebla**. Más 113 nodos, también
> por niebla. O sea que **en esta instantánea el que manda es el bloqueo operacional,
> no el de altitud**.*
>
> *Por altitud hay 2 corredores donde el relieve no cabe en la ventana de 120 metros,
> pero esos 2 además están bajo niebla, así que habrían salido igual. Y por obstáculo
> vertical no hay ningún bloqueo: 33 aristas quedan penalizadas por acercarse a una
> chimenea, pero ninguna la sobrevuela.*
>
> *Esto último tiene una explicación que vale la pena: **las chimeneas son nodos de la
> red**, son fuentes de emisión que el dron va a medir. Una arista que termina en una
> chimenea no la está sobrevolando, está llegando a ella, y el modelo distingue ese
> caso. Por eso penaliza la cercanía pero no bloquea el arribo.*
>
> *Los dos mecanismos están implementados y operando; cuál domina depende de las
> condiciones del día."*

---

# TOMA 3 · Parámetros del usuario → punto 3
*Pestaña **Simulador** → panel izquierdo → **segunda tarjeta**: "Fase 3 · Comparación de técnicas" · ~90 s*

> **⚠️ No aprietes "Calcular" en esta toma.** Solo configuras.

### 1. Vuelves a la pestaña **Simulador** y bajas a la segunda tarjeta del panel.
> *"Pasemos a la interfaz. Esta tarjeta es la de la Fase 3, donde el usuario ingresa
> los parámetros de su consulta."*

### 2. Abres el desplegable **Destino de la misión** y eliges **Estación SINCA La Greda**.
> *"Lo primero es el punto de destino. El origen es fijo: el Aeródromo de Quintero,
> código SCER, que es la base desde donde despega el dron. Y el destino se elige entre
> las ocho estaciones de monitoreo de calidad del aire de la red SINCA. Para esta
> demostración voy a usar **La Greda**, que es una de las zonas más críticas por su
> cercanía al complejo industrial."*

### 3. Escribes **10500** en **Autonomía máx. (m)**.
> *"Ahora las restricciones que impone el usuario según su aplicación. La primera es
> **la autonomía máxima**, en metros: el alcance físico que da la batería del dron.
> Pongo 10.500 metros, es decir 10,5 kilómetros de recorrido máximo. Ninguna ruta que
> supere ese valor sirve, porque el dron no llegaría."*

### 4. Escribes **1000** en **β aversión al riesgo**.
> *"La segunda es **beta, el factor de aversión al riesgo**. Controla cuánto está
> dispuesto a desviarse el operador para evitar una zona peligrosa. Con beta en cero
> solo importaría la distancia; mientras más alto, más pesa el riesgo frente a los
> metros recorridos. Lo dejo en 1.000."*

### 5. Marcas la casilla naranja **Escenario de contingencia: incendio en Planta de Asfaltos**.
> *"Y activo el escenario de contingencia, que simula un incendio declarado en la
> Planta de Asfaltos de Quintero. Lo uso durante toda la demostración porque es el
> caso que permite comparar cómo reacciona cada técnica frente a una amenaza concreta."*

### 6. Escribes **2000** en **Monte Carlo (N)** y **15** en **Semilla**.
> *"Monte Carlo en 2.000 realizaciones: con eso se estima qué porcentaje de las veces
> la misión sobrevive. Y fijo la semilla en 15 para que el sorteo aleatorio sea
> reproducible, y cualquiera que repita esta ejecución obtenga exactamente los mismos
> resultados."*

### 7. Verificas que **Motor del camino mínimo** diga **pgr_dijkstra en PostgreSQL (pgRouting)**.
> *"Y el motor de camino mínimo es **pgr_dijkstra ejecutándose dentro de PostgreSQL**,
> que es lo que pide el enunciado. La alternativa sería un Dijkstra propio en Python,
> que dejamos implementado como respaldo."*

---

# TOMA 4 · Amenazas, metadatos y popups → punto 4
*Misma tarjeta, bloque "Amenazas y metadatos considerados" · ~2 min*

> **⚠️ No aprietes "Calcular" en esta toma.**

### 1. Señalas el bloque completo de las 10 casillas.
> *"Acá está el panel de control de las amenazas y los metadatos. Son diez capas, cada
> una con su casilla, y se pueden activar o desactivar de forma independiente para
> cargar todas o solo algunas."*

### 2. Explicas que hay **dos mecanismos distintos**. Esto es lo que da sentido a toda la lista.
> *"Antes de recorrerlas, hay que entender que una amenaza puede afectar la red de dos
> formas distintas.*
>
> *Unas **penalizan**: le suman un valor lambda al corredor, que es una tasa de falla
> por kilómetro. El corredor sigue siendo volable, pero se vuelve más arriesgado y el
> algoritmo lo va a evitar si tiene alternativa.*
>
> *Otras **bloquean**: cuando se cruza un umbral, el tramo deja de ser transitable y
> sale del grafo. Ahí no hay negociación posible.*
>
> *Cada etiqueta indica cuál de los dos mecanismos aplica."*

### 3. Recorres las capas **que penalizan**. Las vas señalando con el cursor.
> *"Las que penalizan, con su lambda:*
>
> - ***Incendios FIRMS**, lambda 5,0. Es con diferencia el más alto del sistema:
>   detectados por satélite, y hacen que el algoritmo evite la zona casi a cualquier costo.*
> - ***Alertas sísmicas del CSN**, lambda 0,05.*
> - ***Lluvia intensa**, lambda 0,03.*
> - ***Humedad relativa**, lambda 0,03, y acá aparece el primer umbral: solo se aplica
>   **sobre el 90 por ciento** de humedad relativa. Por debajo de eso no penaliza nada.*
> - ***Densidad poblacional**, lambda 0,08, sobre las manzanas censales del INE con
>   **más de 2.500 habitantes por kilómetro cuadrado**. Volar sobre población densa es
>   más riesgoso porque una caída tiene consecuencias mayores.*
> - ***Sombra de enlace C2**, lambda 0,05. Esta funciona al revés que las otras: se
>   aplica cuando el punto **no** tiene cobertura de ninguna antena de control. Si el
>   dron pierde el enlace de comando y control, deja de ser gobernable.*
> - ***Relieve SRTM**, lambda 0,06 **por cada 100 metros de ascenso acumulado**. Subir
>   consume batería, así que un corredor que obliga a trepar es más caro y más riesgoso.*
> - ***Obstáculos verticales**, lambda 0,20 cuando el corredor entra en el radio de
>   resguardo de una torre o una chimenea."*

### 4. Recorres las capas **que bloquean**, con sus umbrales.
> *"Y las que bloquean, con su umbral:*
>
> - ***Niebla**: si la visibilidad baja de **mil metros**, el corredor se bloquea.
>   Es la única capa que no tiene lambda, porque no penaliza: directamente impide volar.*
> - ***Viento**: tiene los dos comportamientos. Desde **8 metros por segundo** penaliza
>   con lambda 0,04, y sobre **12 metros por segundo** bloquea el tramo.*
> - ***Obstáculos verticales**: además de penalizar, si el obstáculo es **más alto que
>   el techo de 120 metros** el corredor que lo cruce queda bloqueado. Con la salvedad
>   que mencioné antes: llegar a una chimenea no cuenta como sobrevolarla.*
> - ***Relieve**: igual, si el terreno sube tanto que el dron no cabe en la ventana de
>   120 metros sobre el suelo, bloquea."*

### 5. Aprietas el botón **"Ninguna"**. Se apagan las 10 casillas.
> *"El panel permite desactivarlas todas de una vez..."*

### 6. Aprietas **"Todas"**. Se vuelven a encender las 10.
> *"...o volver a activarlas. Y cada combinación intermedia también es válida: se
> puede calcular considerando solo algunas de las amenazas. Más adelante voy a
> demostrar que esto cambia el resultado de verdad."*

### 7. Haces clic en un nodo del mapa. Se abre el popup.
> *"Para la información que no se puede representar como polígono, usamos popups. Si
> hago clic en cualquier nodo de la red, se despliega su ficha: el nombre, la
> categoría, la elevación sobre el nivel del mar y los contaminantes medidos si es una
> estación de monitoreo."*

- [ ] **Al salir de esta toma: las 10 capas marcadas.**

---

# TOMA 5 · Probabilidad de falla por nodo y enlace → punto 5
*Terminal · ~90 s*

### 1. Vuelves al terminal y ejecutas el generador.
```bash
docker compose run --rm etl python ruteo/simulacion_fallas.py --guardar
```
> *"El enunciado pide un archivo que genere la probabilidad de fallo de cada enlace y
> cada nodo a partir de las amenazas. Este script lo produce."*

### 2. Inspeccionas el archivo generado.
```bash
python3 -c "import json;d=json.load(open('sitio_web/data/probabilidades_falla.json'));print(len(d['nodos']),'nodos |',len(d['aristas']),'aristas');print(d['aristas']['1'])"
```
```
ESPERADO:
322 nodos | 855 aristas
{'source': 1, 'target': 63, 'length_m': 879.4, 'lambda': 0.0476,
 'p_falla': 0.041, 'bloqueado': False,
 'factores': {'humedad': 0.03, 'relieve': 0.0126}}
```

### 3. Explicas la fórmula señalando la salida.
> *"Hay una entrada por cada uno de los 322 nodos y las 855 aristas. Miremos esta
> arista: conecta el nodo 1 con el 63, mide 879 metros, y su lambda total es 0,0476.*
>
> *Ese lambda es la suma de los aportes de cada amenaza que la afecta, y el campo
> 'factores' lo deja desglosado: 0,03 viene de la humedad y 0,0126 del relieve.*
>
> *De ahí sale la probabilidad de falla con la fórmula **p igual a uno menos e elevado
> a menos lambda por kilómetros**. Para esta arista da 0,041, es decir un 4,1 por
> ciento de probabilidad de fallar. Y si el elemento está bloqueado, su probabilidad
> se fija directamente en uno."*

---

# TOMA 6 · Las cuatro técnicas → punto 6
*Tarjeta Fase 3 · ~5 min · **primera vez que se calcula***

## 6a — Cálculo base

### 1. Aprietas **Calcular las 4 rutas**. No tocaste nada desde la Toma 3.
```
ESPERADO
  Dijkstra distancia       6,709 km   R = 0,0000   pgrouting   ⚠ resiliencia casi nula
  MILP exacto              8,692 km   R = 0,1676   GUROBI
  Dijkstra multicriterio   8,692 km   R = 0,1676   pgrouting
  Akgün                    8,692 km   R = 0,1677   pgrouting · 2 caminos · mejor R
```
> *"Calculo las cuatro rutas sobre el mismo destino y los mismos parámetros. Cada una
> se dibuja en el mapa con su color y aparece en la leyenda con sus métricas."*

### 2. Señalas la primera tarjeta de la leyenda.
> *"La primera técnica es **pgr_dijkstra usando como peso solo la distancia en
> metros**, tal como lo pide el enunciado. Es la referencia ingenua: busca el camino
> más corto y nada más. Devuelve 6,7 kilómetros, que es efectivamente el recorrido
> mínimo."*

### 3. Señalas la segunda tarjeta y en particular el motor.
> *"La segunda es el **modelo de optimización exacto resuelto con GUROBI** —la leyenda
> indica el solver utilizado—. Acá partimos del modelamiento formal del problema: las
> variables de decisión son las aristas del grafo, la función objetivo minimiza el
> costo compuesto, los metadatos y amenazas entran como coeficientes de ese costo, y
> las condiciones del usuario entran como restricciones del modelo. Devuelve 8,7
> kilómetros."*

### 4. Señalas la tercera tarjeta.
> *"La tercera es otra vez **pgr_dijkstra**, pero ya no con la distancia pura sino con
> los parámetros y condiciones del punto anterior. El peso de cada arista pasa a ser
> el costo compuesto: **W igual a L más beta por H menos la recompensa**, acotado por
> abajo. L son los metros, H es el riesgo acumulado."*

### 5. Señalas la cuarta tarjeta.
> *"Y la cuarta es la **metaheurística**: el algoritmo de Akgün y otros, del año 2000,
> que genera k caminos disimilares por penalización iterativa de aristas. Devuelve un
> par de rutas en vez de una sola, por eso la leyenda dice 'dos caminos': una
> principal y una alternativa que comparte la menor cantidad posible de tramos, para
> que si una falla la otra siga disponible."*

### 6. Marcas y desmarcas las casillas de cada técnica en la leyenda.
> *"Las cuatro rutas se pueden habilitar o deshabilitar de forma independiente desde
> el panel de control."*

### 7. Vuelves a marcar las cuatro y haces notar la coincidencia.
> *"Un detalle que conviene explicar: **el MILP y el Dijkstra multicriterio entregan
> exactamente la misma ruta**. No es un error, es lo esperable. Los dos minimizan el
> mismo costo, que es aditivo y no negativo, y Dijkstra es un algoritmo exacto para
> ese tipo de problema. Si dieran resultados distintos, uno de los dos estaría mal
> implementado. Funciona como validación cruzada del modelo formal. Ahora les muestro
> cuándo sí se separan."*

- [ ] **Deja las 4 casillas de técnica marcadas.** El panel recuerda ese estado entre
      cálculos; si una queda apagada no aparecerá en las tomas 7, 8 y 9.

## 6b — Se aprieta la autonomía

### 1. Cambias **Autonomía a 8000** y aprietas **Calcular**.
```
ESPERADO
  Dijkstra distancia       6,709 km   R = 0,0000   ⚠ resiliencia casi nula
  MILP exacto              7,110 km   R = 0,0136   · mejor R
  Dijkstra multicriterio   8,692 km   R = 0,1676   ⚠ excede la autonomía
  Akgün                    8,692 km   R = 0,1677   ⚠ excede la autonomía
```
> *"Bajo la autonomía a 8 kilómetros, simulando un dron con menos batería, y recalculo."*

### 2. Señalas los dos avisos naranjas.
> *"Acá se rompe el empate. El Dijkstra multicriterio y la metaheurística siguen
> proponiendo la ruta de 8,69 kilómetros, que ahora **excede el límite** —la leyenda
> lo advierte explícitamente—. No pueden evitarlo: Dijkstra minimiza un costo, pero no
> sabe imponer un tope a la longitud total del camino."*

### 3. Señalas la tarjeta del MILP.
> *"El MILP sí puede, porque la autonomía está formulada como **una restricción dura
> del modelo**. Reformula y entrega una ruta de 7,11 kilómetros que sí cabe en la
> batería. Es **la única que llega con resiliencia distinta de cero respetando el
> límite**: la ruta por distancia también cabe en 8 kilómetros, pero su resiliencia es
> cero, así que no sirve. Por eso el sistema le asigna a esta la etiqueta de mejor
> resiliencia: se elige entre las rutas viables.*
>
> *Esto responde para qué sirve tener las cuatro técnicas: **cada una aporta algo que
> las otras no pueden**."*

- [ ] **Devuelve Autonomía a 10500.**

## 6c — Campiche con niebla

### 1. Cambias **Destino a Campiche** y aprietas **Calcular**.
```
ESPERADO
  Dijkstra distancia       9,734 km   R = 0,0000
  MILP / multicriterio / Akgün        Sin ruta
```
> *"Ahora cambio el destino a Campiche, que está más al norte. Y miren lo que pasa:
> **tres de las cuatro técnicas dicen 'sin ruta'**. Con las condiciones meteorológicas
> actuales, la niebla bloquea tantos corredores que no existe ningún camino
> transitable hasta allá. Solo la técnica por distancia devuelve algo, porque ignora
> los bloqueos por definición, y por eso su resiliencia es cero: la ruta que propone
> cruza tramos impracticables."*

## 6d — Campiche sin niebla

### 1. **Desmarcas la casilla de niebla** y aprietas **Calcular**.
```
ESPERADO
  Dijkstra distancia       9,734 km    R = 0,0000   pgrouting
  MILP exacto             10,135 km    R = 0,0059   HiGHS · mejor R
  Dijkstra multicriterio  11,717 km    R = 0,0725   pgrouting · ⚠ excede la autonomía
  Akgün                   11,717 km    R = 0,0725   pgrouting · ⚠ excede · 1 camino
```
> *"Desactivo una sola casilla, la de niebla, y recalculo. **Las tres rutas que eran
> imposibles ahora existen.** Esto demuestra que las capas del panel no son
> decorativas: entran de verdad al cálculo y cambian el resultado."*

### 2. Señalas los avisos de autonomía.
> *"Y de nuevo se separan las técnicas: el multicriterio y la metaheurística proponen
> 11,7 kilómetros, que excede la autonomía de 10,5. El MILP se queda en 10,1 y respeta
> el límite, esta vez sin que yo tocara ningún parámetro."*

### 3. Señalas el motor del MILP. **No te saltes esto.**
> *"Y un detalle importante: fíjense que acá el solver dice **HiGHS**, no GUROBI.*
>
> *Al desactivar la niebla el grafo transitable crece, y el modelo de optimización
> pasa de 1.275 a **2.020 variables**. Eso queda justo por encima del tope de 2.000
> variables de la licencia restringida de Gurobi, así que Gurobi falla. El sistema
> detecta la excepción y **baja automáticamente al siguiente solver de la cadena**,
> sin intervención del usuario. La API deja registro de qué solver se descartó y por
> qué. Es una degradación controlada: el modelo se resuelve igual."*

---

# TOMA 7 · Simulación de fallas → punto 7
*Tarjeta Fase 3 · ~2 min*

### 1. Restauras el estado. **En este orden.**
- Destino → **La Greda**
- **Remarcas la casilla de niebla** ⚠️
- Verificas que las **4 casillas de técnica** sigan marcadas
- Semilla = **15**
- Aprietas **Calcular** (vuelves a los números de 6a)

> *"Vuelvo al escenario de La Greda con todas las capas activas."*

### 2. Aprietas el botón **Simular fallas**.
```
ESPERADO
  334 aristas y 120 nodos caídos, pintados en rojo
  Dijkstra distancia          Falló
  MILP exacto                 Sobrevivió
  Dijkstra multicriterio      Sobrevivió
  Akgün                       Sobrevivió
```
> *"El enunciado pide una opción que, a partir de números aleatorios entre 0 y 100,
> determine si la falla ocurre o no. Esto es exactamente eso."*

### 3. Explicas el mecanismo mientras se ven los elementos rojos.
> *"Para cada nodo y cada arista de la red se sortea un número **u entre 0 y 100**. Si
> ese número **cae por debajo de la probabilidad de falla del elemento multiplicada
> por 100**, el elemento falla. Los que fallaron se pintan en rojo.*
>
> *En esta realización cayeron 334 corredores y 120 nodos."*

### 4. Haces clic en un elemento rojo. Se abre el popup.
> *"Si hago clic en cualquiera de ellos, el popup muestra su probabilidad de falla y
> el número que le tocó en el sorteo, para poder verificar el criterio."*

### 5. Señalas el resultado por técnica.
> *"Y acá está el resultado: **la ruta calculada por distancia pura quedó cortada**,
> porque pasaba por tramos que cayeron. Las tres técnicas que consideran las amenazas
> sobrevivieron."*

### 6. (Opcional) Cambias la semilla a **16** y vuelves a simular.
> *"Cambiando la semilla se obtiene otro sorteo distinto, y el contraste se mantiene."*

---

# TOMA 8 · Métrica de resiliencia → punto 8
*La leyenda, ya en pantalla · ~90 s*

### 1. Señalas la fila de métricas de una tarjeta cualquiera.
> *"El enunciado pide que la métrica de resiliencia se despliegue junto a la leyenda
> que indica el algoritmo y el tiempo de cómputo. Cada tarjeta muestra, en este orden:
> la longitud en kilómetros, el tiempo de cómputo en milisegundos, el valor de
> resiliencia R, el porcentaje de supervivencia Monte Carlo, y abajo el motor que
> resolvió esa ruta."*

### 2. Explicas la métrica.
> *"La métrica es la **confiabilidad estocástica exacta**: R igual a la supervivencia
> del tramo común, multiplicada por uno menos la probabilidad de que fallen los dos
> caminos a la vez. Y la supervivencia de un conjunto de aristas es **e elevado a menos
> la suma de lambda por la longitud de cada arista**. El porcentaje Monte Carlo es la
> fracción de las 2.000 realizaciones en que la misión sobrevivió, y sirve para
> contrastar empíricamente el valor analítico."*

### 3. Señalas la etiqueta **"mejor R"** y das la lectura honesta.
> *"La técnica más resiliente frente a las amenazas detectadas es **la metaheurística
> de Akgün**, marcada con la etiqueta 'mejor R'.*
>
> *Pero hay que ser precisos con esto: le gana al MILP por cinco cienmilésimas, o sea
> es prácticamente un empate. Y además tiene una ventaja metodológica, porque su
> resiliencia se calcula sobre **un par de caminos** mientras que la de las otras tres
> se calcula sobre **un solo trazado**. Entre las técnicas directamente comparables, el
> MILP y el Dijkstra multicriterio empatan en 0,1676, y la ruta por distancia queda en
> cero."*

> **⚠️ No leas los milisegundos en voz alta**: varían entre corridas según la caché
> (el MILP salta de 86 a 243 ms).

---

# TOMA 9 · Caso de ejemplo → punto 9
*Tarjeta Fase 3 · ~2 min*

## 9a — Sin la amenaza

### 1. **Desmarcas la casilla naranja de contingencia** y aprietas **Calcular**.
```
ESPERADO: las cuatro en 6,709 km · R = 0,2398 (Akgün 0,3590)
```
> *"Para cerrar, el caso que evidencia que el sistema entrega una ruta alternativa
> frente a una amenaza. Primero apago el escenario de contingencia, o sea la red en
> condiciones normales.*
>
> *Las cuatro técnicas coinciden: **6,7 kilómetros, la misma ruta por la costa**, con
> una resiliencia de 0,24. Es el camino óptimo y ninguna tiene motivo para desviarse."*

## 9b — Aparece la amenaza

### 1. **Vuelves a marcar la contingencia** y aprietas **Calcular**.
```
ESPERADO
  Dijkstra distancia       6,709 km   R = 0,0000   ⚠ resiliencia casi nula
  MILP / multicriterio     8,692 km   R = 0,1676
  Akgün                    8,692 km   R = 0,1677
```
> *"Ahora declaro el incendio en la Planta de Asfaltos, que queda justo sobre ese
> corredor óptimo."*

### 2. Señalas la ruta de distancia en el mapa.
> *"La técnica por distancia **no cambia de ruta**: recorre los mismos 6,7 kilómetros,
> cruza el foco del incendio, y su resiliencia se desploma a cero. La leyenda lo
> advierte: 'resiliencia casi nula, la misión no sobrevive a las amenazas activas'.
> Esa misión se pierde."*

### 3. Señalas las otras tres rutas.
> *"Las otras tres recalculan y salen por un corredor completamente distinto: cambian
> los diez primeros nodos del trazado. Pagan **1,98 kilómetros adicionales**, un 30 por
> ciento más de recorrido, y a cambio mantienen la misión viable con una resiliencia
> de 0,17."*

### 4. Cierre del video.
> *"Y ese es exactamente el objetivo que nos planteamos al inicio del proyecto:
> sostener el monitoreo de calidad del aire sobre Quintero y Puchuncaví con una red
> que, frente a una amenaza, **degrada en vez de caerse**. Pierde eficiencia, recorre
> más kilómetros, pero sigue cumpliendo la misión."*

---

# Checklist de estado entre tomas

El panel recuerda lo que dejaste. Si no restauras, los números no coinciden.

| Después de | Restaurar |
|---|---|
| Toma 4 | las 10 capas marcadas |
| Toma 6a | las **4 casillas de técnica** marcadas |
| Toma 6b | **autonomía → 10500** |
| Toma 6d | **destino → La Greda** y **niebla → marcada** |
| Toma 9a | **contingencia → marcada** |

---

# Preguntas probables y su respuesta

**¿Por qué el MILP y el Dijkstra multicriterio dan la misma ruta?**
Porque minimizan el mismo costo aditivo no negativo, y Dijkstra es exacto para ese
problema. Si difirieran, uno estaría mal. Se separan cuando entra una restricción que
Dijkstra no puede expresar: con autonomía 8000 el MILP da 7,11 km y es el único viable
con resiliencia mayor que cero.

**¿Por qué las cuatro rutas se parecen tanto en condiciones normales?**
Porque con β = 1000 el costo queda W = L·(1+λ), y los λ naturales de la red van de
0,035 a 0,298. El piso de 0,035 —base más humedad— aplica a todas las aristas, así que
es un factor de escala que no cambia el óptimo. El recargo que realmente diferencia
vale alrededor de 0,26, de modo que un desvío más de un 26 % más largo no puede ganar
nunca. Frente a una amenaza real como el incendio (λ = 5,0, unas 17 veces el λ natural
máximo) la ruta cambia por completo.

**¿Por qué Akgün siempre gana en resiliencia?**
En parte por construcción: evalúa un par de caminos y las otras un solo trazado. Está
declarado como pendiente conocido en `pauta_fase3.md`.

**¿De dónde salen los λ?**
De la especificación del equipo, en `config/parametros.json`. El pipeline incluye un
análisis de sensibilidad con λ_incendio en 0,5 / 1,0 / 5,0: el ruteo resiliente domina
al de distancia en los tres escenarios.

**¿Por qué el solver cambia de GUROBI a HiGHS?**
Por el tope de 2.000 variables de la licencia restringida de Gurobi. El sistema tiene
una cadena de solvers —GUROBI, CPLEX, HiGHS, CBC— y baja al siguiente cuando uno falla.

---

# Antes de apretar REC

- [ ] **Subir la rama.** El punto 1 pide "desde el main". Hay commits sin subir en
      `aceituno` y cambios sin commitear. Si grabas y el profesor entra a `main`,
      no encuentra nada de esto.
- [ ] **La licencia de GUROBI expira el 23-11-2026.** Después, la toma 6a también
      caería a HiGHS y se perdería el único momento donde se ve GUROBI.
