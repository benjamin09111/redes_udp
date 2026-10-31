# Guía de corrección — Informe Fase 2 / Paper (Grupo 09)

Oct 31, 2026 · @Benjamin

## Cómo usar esta guía

El informe cambia de foco: deja de ser solo «cómo volar seguro» y pasa a ser «cómo volar seguro **para medir bien**». Ese es el hilo que une todo el feedback. Trabajen los pasos en orden: primero arreglar errores (Paso 1), luego actualizar el contexto (Paso 2), y recién después reescribir la justificación física y las amenazas (Pasos 3 a 7).

Checklist de cobertura: cada punto del feedback del profesor está asignado a un paso. Marquen cada casilla cuando el texto esté en el informe.

- [ ] Profundizar por qué estos lugares y no otros (fuente + receptor, historial, estaciones activas) → Paso 3
- [ ] Justificar zonas según alcance del dron desde el aeródromo; mejor zona chica que no llegar → Paso 3
- [ ] Explicar contaminación en eje horizontal (fuente, viento, distancia); Quintero ≠ Ventanas → Paso 4
- [ ] Justificar cada nodo de medición → Paso 3
- [ ] Cierre Fundición Ventanas (31 mayo 2023) → Paso 2
- [ ] Mapa/evaluación previa a la misión según amenazas → Paso 8
- [ ] Mejorar mapeo con vientos, calor, industrias, POI, alcance → Pasos 3 y 8
- [ ] Altura de medición respecto a la capa de mezcla, no universal → Paso 5
- [ ] Discutir la hora de las mediciones → Paso 5
- [ ] Qué gana y qué deja fuera medir a \~100 m (torre Puchuncaví 40 m, techo DAN 151) → Paso 5
- [ ] Dividir amenazas: a la aeronave vs a la validez de la medición → Paso 6
- [ ] Incendios como confusor, viento como criterio de ruteo, niebla/humedad sobre sensores ópticos → Paso 6
- [ ] Aerosol marino, lluvia (scavenging), tráfico marítimo → Paso 6
- [ ] Sección de riesgos de medición (mezcla de aire, mala lectura) → Paso 7
- [ ] Anillos de 2, 4, 6, 8, 10 km en el mapa → Paso 3
- [ ] Figura de corte transversal suroeste→noreste → Paso 4
- [ ] Por qué hay distintas estaciones SINCA → Paso 3
- [ ] Sacar lo de aves → Paso 1
- [ ] Párrafo «por qué medir en altura y no solo en suelo» (D.S. 105 modificado por D.S. 39/2023) → Paso 2
- [ ] 80 m vs 100 m: diferencia según estabilidad; registrar altura relativa a la capa de mezcla → Paso 5
- [ ] Tiempo de respuesta del sensor vs velocidad del dron y ancho de pluma → Paso 7
- [ ] Radio de una zona de contaminación (pluma, 2 km SMA, variograma, AERMOD/CALPUFF) → Paso 7
- [ ] Integrar el mapa visual (fuentes, viento 48 h, zonas a sotavento, destinos) y sus dos advertencias → Paso 8
- [ ] Coordenadas exactas vs aproximadas; estado de la termoeléctrica y Codelco → Pasos 2 y 8

## Paso 1 — Arreglar errores e inconsistencias antes de agregar nada

Revisando el PDF encontré errores que un evaluador puede pillar en la defensa. Arréglenlos primero, porque varios cambian números que después van a reutilizar.

| # | Dónde | Problema | Qué hacer |
| --- | --- | --- | --- |
| 1 | Ref. \[15\] y todo el texto sobre Kosior | La cita no existe tal como está: «Kosior J., Grygierek E., Piechaczek J., Atmospheric Environment 318». El trabajo real es Kosior, M., Przystałka, P. y Panfil, W. (2024), *Adaptive Path Planning for UAV-Based Pollution Sampling*, Applied Sciences 14(24), 12065 ([MDPI](https://www.mdpi.com/2076-3417/14/24/12065)). | Reemplazar la referencia completa. Además, «CT ≤ 4,55 s» no es una especificación del LPP: es el criterio de éxito de un escenario (Żywiec), derivado de margen de seguridad / velocidad. Y la plataforma es de ala fija, no multirrotor. Corregir sección 2.4. |
| 2 | Refs. \[1\] y \[2\] | Son la misma referencia duplicada. | Eliminar \[2\] y renumerar. Revisar si \[36\] se cita en algún lugar; si no, sacarla. |
| 3 | Año del PPDA | El texto dice «D.S. N.º 105/2019» y el feedback dice 105/2018. Lo correcto: D.S. N.º 105 **de 2018** (27-12-2018), publicado en el Diario Oficial el 30-03-2019, modificado en su art. 47 por el D.S. N.º 39 de 2023 (publicado el 18-03-2024). | Unificar como «D.S. N.º 105/2018 MMA, modificado por D.S. N.º 39/2023». |
| 4 | Tabla 1 vs secc. 1.2 | CR2 se cita como \[7\] en la tabla y como \[8\] en el texto; el compromiso MMA como \[9\] y \[11\]. | Una sola referencia por hecho. |
| 5 | Figura 3 vs Tabla 11 | La figura dice 14,00 km, 20 saltos, 15 min 33 s, destino «Unimarc Puchuncaví» y alcance «14,0 / 32 km». La tabla dice SINCA Puchuncaví 14,41 km, 22 saltos, 16,0 min y autonomía 39,6 km. | Volver a capturar la figura con el destino SINCA Puchuncaví y con la autonomía de S6 (39,6 km) en el visor web. |
| 6 | Listing 3 (ADS-B) | `observed_at` = 2026-10-23, pero S8 dice que la corrida de referencia fue el 18–19 de octubre. Además, callsign «CC-SCER1» parece un dato inventado. | Si el registro es sintético (no hubo aeronave real), declararlo explícitamente como «evento de prueba». Si es real, reemplazar por el dato real de la ventana S8. |
| 7 | Secc. 9.1, «Resultado de la auditoría» | Dice que las amenazas «obligaron a buscar desvíos», pero Dijkstra usa costo = longitud y no considera amenazas. Es contradictorio. | Reescribir: «las amenazas activas intersectan X aristas de la ruta base; la fase siguiente las incorporará al costo». |
| 8 | Fundición Ventanas | Se presenta la chimenea de 152 m como fuente activa. La fundición cerró el 31-05-2023 (ver Paso 2). | Reclasificar: obstáculo físico sí (sigue en pie), fuente de emisión de fundición no. Ojo: la refinería sigue operando. |
| 9 | Tabla 7, `height_m` | La unidad dice «Metros s.n.m. / cota», pero el texto habla de 152 m de altura. Si es altura sobre suelo es AGL, no s.n.m. | Definir una sola unidad (AGL) y declararlo. |
| 10 | Ec. (2) | 110.574 m/grado es la longitud de un grado de latitud **en el Ecuador**, no a −32,7°. A esa latitud es ≈110.900 m. | Corregir el texto o el valor (error ≈0,3 %, menor, pero es una afirmación falsa). |
| 11 | Resp. a P1 | Dice «8 fuentes heterogéneas» pero hay 9 extractores (5 metadata + 4 amenazas) más la infraestructura. | Contar bien y ser consistente con la secc. 5.1. |
| 12 | Typo secc. 1.3 | «riesgo operático». | «riesgo operativo». |
| 13 | Aves | El feedback pide sacarlo. En este PDF no aparece; debe estar en el código, el visor web o la presentación. | Buscar `aves`/`birds` en el repo y en las láminas y eliminar. |
| 14 | S3 (altitud fija 100 m) y secc. 8.1 («la calidad del aire no actúa como factor») | Ambos chocan con el feedback nuevo: la altura debe ser relativa a la capa de mezcla, y las amenazas afectan la validez de la medición. | Se reescriben en Pasos 5 y 6. |
| 15 | Alcance (secc. 12.3) | Puchuncaví ida y vuelta = 28,8 km deja < 12 min de muestreo. El mapa del profesor marca «fuera de alcance» sobre 10,5 km desde el aeródromo. | Se resuelve en Paso 3 (reducir zona). |

## Paso 2 — Actualizar el contexto territorial (obligatorio)

El informe describe el polo industrial como si fuera 2018. Tres hechos cambiaron y deben quedar en la Introducción (secc. 1) y en la tabla de obstáculos/fuentes.

| Hecho | Dato verificado | Fuente | Dónde va en el informe |
| --- | --- | --- | --- |
| Cierre Fundición Ventanas (Codelco) | El cese de la fundición, incluida su planta de ácido, se concretó el 31-05-2023, tras 58 años; Sernageomin aprobó el plan de cierre temporal parcial el 16-05-2023 (Res. Ex. 844/2023). Después del cierre **siguió operando el proceso RAF (hornos de refino) y la refinería**. | [SMA/SNIFA](https://snifa.sma.gob.cl/General/Descargar/1104418388), [SNIFA](https://snifa.sma.gob.cl/General/Descargar/1104374183), [DF](https://www.df.cl/empresas/mineria/tras-59-anos-codelco-cierra-fundicion-ventanas-y-gobierno-prepara) | Secc. 1 (contexto), Tabla de fuentes, secc. 1.3 «obstáculos» |
| Termoeléctrica Ventanas cambió de dueño | AES Andes anunció en dic-2024 la venta a Quintero Energía SpA; se cerró en ene-2025. Hoy operan solo las unidades 3 y 4 (537 MW). Quintero Energía dijo que seguirán operando «hasta nuevo aviso». | [La Tercera](https://www.latercera.com/pulso/noticia/los-nuevos-duenos-pagaron-solo-us-5-millones-a-aes-por-el-complejo-termoelectrico-ventanas/), [GEM](https://www.gem.wiki/Ventana_power_station) | Secc. 1, tabla de fuentes («Campiche» = Unidad 4, «Nueva Ventanas» = Unidad 3) |
| PPDA modificado | D.S. 105/2018 modificado en su art. 47 (gestión de episodios críticos) por el D.S. 39/2023, publicado el 18-03-2024. | [PPDA MMA](https://ppda.mma.gob.cl/wp-content/uploads/2024/03/D.S.-39-2023-modifica-art-47-PPDA-publicado-DO.pdf) | Secc. 1 y 1.1 |

Antes de entregar, verifiquen el estado actual (oct-2026) de la refinería Codelco y de las unidades 3–4 en SNIFA. Si algo cambió, actualicen la tabla.

**Consecuencia para el informe.** Con la fundición cerrada, el foco histórico de SO₂ y metales (As, Cu, Pb) cambia: las fuentes de SO₂ que quedan son la termoeléctrica, la refinería, ENAP y los buques. Esto **fortalece** el argumento del dron: el mapa de fuentes cambió y las estaciones fijas fueron ubicadas para el escenario anterior.

**Texto sugerido para la secc. 1.5 (pedido explícito del feedback):**

> Aunque las estaciones a nivel de suelo responden al cumplimiento normativo de lo que respira la población, resultan insuficientes para la detección anticipada de plumas en altura, la atribución oportuna de fuentes en emergencias sanitarias —como la crisis de 2018— y la medición de contaminantes no cubiertos por la red fija. Por ello, el UAV con sensores no busca reemplazar la red terrestre, sino complementarla donde esta es ciega: en altura, antes del episodio y en la identificación de la fuente responsable. Esta necesidad es reconocida por el Estado y es relevante frente a la actualización del PPDA (D.S. 105/2018, modificado por D.S. 39/2023).

## Paso 3 — Justificar la zona de estudio y cada nodo

La zona se justifica con una sola regla: **radio de 10 km alrededor del complejo Ventanas, recortado por el alcance real del dron desde el aeródromo**. Es mejor una zona chica que se cubre bien que una grande donde el dron no llega.

### 3.1 Por qué esta bahía (secc. 1, nuevo párrafo)

Argumenten con cuatro razones, cada una con su fuente: (1) coexisten fuente y receptor sensible a menos de 2 km (escuela La Greda junto al complejo); (2) hay historial y reconocimiento del Estado (PPDA, crisis 2018); (3) existen estaciones activas para co-localizar y validar; (4) el mapa de fuentes cambió en 2023–2025 (Paso 2), así que la red fija quedó diseñada para un escenario que ya no existe.

### 3.2 Anillos de 2, 4, 6, 8 y 10 km (pedido del feedback)

Usen directamente los anillos del estudio de suelos de Aponte et al. (2021): muestras compuestas tomadas en zonas de 2, 4, 6, 8 y 10 km de la fundición ([Sci. Total Environ. 779:146423](https://repositorio.uoh.cl/handle/611/492?show=full)). Complementen con dos hechos: el cobre y la acidez del suelo son mayores cerca del complejo y en la dirección de los vientos dominantes ([González et al., 2014](https://investigadores.anid.cl/es/public_search/work?id=288134)); y Cu, As y Pb están correlacionados entre sí, lo que apunta a la fundición como fuente ([Tapia-Gatica et al., 2020](https://repository.rudn.ru/records/article/record/56479)).

En el código: generen 5 buffers concéntricos con `ST_Buffer(geom::geography, r)` desde el centro del complejo y agréguenlos como capa `meta_ring` en el visor.

### 3.3 Alcance del dron: derivar el 10,5 km, no copiarlo

Con S6 (39,6 km = 44 min a 15 m/s), si se reservan T minutos de muestreo estacionario, la longitud máxima de ruta (por el grafo, no en línea recta) es aproximadamente:

```latex
R_{max} = \frac{39{,}6\ \text{km} - v \cdot T_{muestreo}}{2}
```

Con T = 20 min (0,9 km por minuto equivalente): R\_max ≈ (39,6 − 18) / 2 ≈ 10,8 km → usen **10,5 km** con margen. Agreguen un ajuste por viento: con 6 m/s en contra en un tramo, la ida y vuelta de 10,5 km tarda \~19 % más que en calma. Por eso el alcance debe recalcularse antes de cada misión (Paso 8).

Resultado con la Tabla 11: SINCA Puchuncaví (14,41 km) queda **fuera de alcance**; Campiche (9,53 km) queda en el límite. Declárenlo así y saquen Puchuncaví de las misiones o márquenlo como «requiere base intermedia».

### 3.4 Revisar qué estaciones existen hoy

Sus 8 nodos «SINCA» no calzan con la red real. Desde abril-mayo 2025 opera la nueva Red Pública MMA de 14 estaciones, con 3 «Super-Sitios» (Concón, Quintero, Ventanas) que miden 11 contaminantes. En Puchuncaví: Super-Sitio Ventanas, Escuela La Greda, Puchuncaví Centro, Pucalán y Maitencillo; en Quintero: Super-Sitio Quintero, Loncura, Valle Alegre, Quintero Sur y Mantagua ([El Mercurio de Valparaíso](https://www.mercuriovalpo.cl/impresa/2025/04/29/full/cuerpo-principal/5), [El Mostrador](https://www.elmostrador.cl/agenda-pais/agenda-sustentable/2025/05/13/inauguran-red-publica-de-monitoreo-de-calidad-del-aire-en-concon-quintero-y-puchuncavi/)). La red industrial histórica incluía además Los Maitenes y Valle Alegre ([MMA](https://ppda.mma.gob.cl/wp-content/uploads/2020/09/Presentacion-Estaciones-Calidad-del-Aire-CQP.pdf)).

Tareas: verifiquen si existe una estación «Campiche» (no aparece en las listas oficiales que revisé); agreguen **Los Maitenes** (el profesor la ubicó desde coordenadas UTM de la SMA); y prioricen los Super-Sitios, porque miden más compuestos y sirven mejor para co-localizar.

### 3.5 Por qué hay distintas estaciones (texto para el informe)

Cada estación representa una combinación distinta de distancia al complejo, dirección respecto del viento y fuente dominante. El viento típico rota en el día: de componente noreste en la noche y madrugada a suroeste en la tarde, según los pronósticos oficiales del MMA ([ejemplo 03-09-2024](https://airecqp.mma.gob.cl/wp-content/uploads/2024/09/2024-09-03_PRONOSTICO_CONCON-QUINTERO-PUCHUNCAVI_MMA.pdf)). Así, una estación al noreste (La Greda, Puchuncaví) recibe la pluma con brisa marina de la tarde, y una al suroeste (Quintero, Loncura) la recibe con flujo de tierra nocturno. Eso explica sus ciclos diarios diferentes.

Para demostrarlo con datos (muy recomendable): descarguen de SINCA un año de SO₂ horario por estación y grafiquen el promedio por hora del día. Una figura con 6–8 curvas de ciclo diario hace este argumento sola.

### 3.6 Justificar cada nodo con una tabla

Agreguen al informe una tabla con una fila por nodo de medición y estas columnas: rol (fuente cercana, receptor sensible, estación de co-localización, fondo/control), distancia al complejo (km), azimut desde el complejo (°), anillo (2–10 km), longitud de ruta desde SCER (km), dentro de alcance (sí/no) y qué se mide ahí y por qué. Los nodos «fondo» (a barlovento, sin pluma esperada) son importantes: sirven de control.

Calcúlenlo en PostGIS, no a mano:

```sql
SELECT n.code,
       ROUND((ST_Distance(n.geom::geography, c.geom::geography)/1000)::numeric, 2) AS dist_km,
       ROUND(degrees(ST_Azimuth(c.geom, n.geom))::numeric, 0) AS azimut_deg,
       CEIL(ST_Distance(n.geom::geography, c.geom::geography)/2000)*2 AS anillo_km
FROM infra_node n, (SELECT geom FROM infra_node WHERE code = 'fuente_codelco_ventanas') c
WHERE n.category IN ('sinca','education','health');
```

(Ajusten el `code` del centro del complejo al que usen en su tabla.)

## Paso 4 — Explicar cómo se mueve la contaminación (nueva sección 2.5 o 1.2 bis)

Esta sección conecta todo: si explican bien el eje horizontal y el vertical, los Pasos 5 a 7 se justifican solos. Escríbanla como dos subsecciones y una figura.

### 4.1 Eje horizontal: la fuente y el viento mandan

Ideas que deben quedar escritas:

1. La concentración cae con la distancia a la fuente, pero no igual en todas las direcciones: cae menos a sotavento. En la bahía, el viento dominante de tarde es del suroeste, por eso el gradiente es más fuerte hacia el noreste (La Greda, Puchuncaví) y los suelos muestran más Cu y acidez en esa dirección (González et al., 2014).
2. **Quintero no es igual a Ventanas.** Ventanas y La Greda están pegadas al polígono industrial (foco histórico de SO₂ y metales de la fundición, hoy termoeléctrica y refinería). Quintero está al suroeste, más cerca de ENAP, GNL, los terminales de graneles y los buques fondeados (NOx, COV, partículas). Por eso cada lado mide cosas distintas y conviene medir distintos contaminantes en cada nodo.
3. La pluma no es un círculo: es una franja alargada en la dirección del viento. Su ancho depende de la estabilidad (ver 4.3).
4. Con la fundición cerrada desde 2023, el patrón de metales en suelo es en parte histórico; el SO₂ actual viene de otras fuentes. Esto es un argumento para medir y no asumir.

### 4.2 Eje vertical: capa de mezcla, inversión y fumigación

1. De noche la superficie se enfría, se forma una capa estable y la inversión baja. Las chimeneas altas (140–152 m) emiten **sobre** esa capa: la pluma queda suspendida en altura y no toca el suelo. Las estaciones a 3–4 m no la ven.
2. En la mañana el sol calienta el suelo y crece la capa de mezcla desde abajo. En la costa, el aire marino que entra sobre tierra caliente forma una **capa límite interna térmica** que crece tierra adentro. Cuando esa capa alcanza la altura de la pluma, la turbulencia la arrastra hacia el suelo de golpe: es la **fumigación costera**. Los pronósticos oficiales del MMA marcan justamente condiciones de ventilación «malas» desde la noche hasta media mañana ([ejemplo 03-09-2024](https://airecqp.mma.gob.cl/wp-content/uploads/2024/09/2024-09-03_PRONOSTICO_CONCON-QUINTERO-PUCHUNCAVI_MMA.pdf)).
3. En la tarde la capa de mezcla es profunda, la pluma se diluye y se mezcla en toda la columna.
4. Conclusión para el paper: **un dron a \~100 m de noche o de madrugada puede detectar la pluma antes de que baje sobre la población.** Eso lo convierte en un sistema de alerta temprana, no solo en un medidor.

### 4.3 Ancho de la pluma (para usar en el Paso 7)

Las cifras del profesor salen de las curvas de Briggs para terreno abierto. El ancho visible de la pluma es aproximadamente 4σy, con σy a distancia x (m):

```latex
\sigma_y = a\,x\,(1 + 0{,}0001\,x)^{-1/2}, \quad a = 0{,}22\ (A),\ 0{,}16\ (B),\ 0{,}08\ (D),\ 0{,}04\ (F)
```

A 2 km de la fuente da: estable F ≈ 290 m, neutra D ≈ 585 m, inestable A ≈ 1,6 km. Coinciden con «madrugada \~300 m, neutra \~600 m, mediodía > 1,5 km». Pongan la ecuación, la tabla de clases y citen Briggs (1973) o un texto estándar (Seinfeld & Pandis). Aclaren que es una estimación de planificación, no un modelo de dispersión.

### 4.4 La figura que falta: corte transversal suroeste → noreste

Esta figura responde por sí sola los puntos 2, 3 y 5 del feedback. Háganla en Inkscape, draw.io o TikZ, como dos paneles (noche y mañana) sobre el mismo corte:

- Eje horizontal: mar y buques (SO) → Quintero → complejo Ventanas con chimeneas → La Greda → Puchuncaví (NE), con distancias reales en km.
- Eje vertical: 0 a \~500 m, con línea de 120 m (techo DAN 151) y la cota del terreno SRTM (+67 m hacia Puchuncaví).
- Panel noche: tapa de inversión, pluma horizontal suspendida en altura, viento de tierra (NE→SO).
- Panel mañana: capa límite interna creciendo tierra adentro, la pluma bajando sobre La Greda y Puchuncaví, brisa marina (SO→NE).
- Estaciones a 3–4 m, la torre/mástil hasta 40 m (verifiquen esta altura, ver Paso 5) y el dron a \~100 m **entre** las estaciones y la pluma.
- Una flecha o sombra que marque «zona ciega»: lo que queda sobre 120 m y no se puede medir legalmente.

## Paso 5 — Altura y hora de medición (reescribir S3 y agregar sección nueva)

Cambio central: **la altura que importa no es «metros sobre el suelo» sino «dónde está el dron respecto de la capa de mezcla y de la pluma».** Reemplacen S3 («cota fija 100 m») por un supuesto nuevo que diga esto.

### 5.1 Nuevo supuesto S3 (texto sugerido)

> S3. Altura de medición relativa a la capa de mezcla. El techo legal es 120 m AGL (DAN 151). Dentro de ese techo, la altura de vuelo se elige según la altura de la capa de mezcla (h\_mix) pronosticada para la hora de la misión. Cada medición se registra con dos alturas: z (m AGL) y z/h\_mix. En esta fase, la ruta se calcula en planta y la altura se fija por misión, no por arista.

### 5.2 80 m vs 100 m: por qué no da lo mismo (párrafo para el informe)

La diferencia entre medir a 80 m y a 100 m puede ser nula o enorme según la hora y la estabilidad: con atmósfera bien mezclada (tarde) ambas lecturas son parecidas; con inversión baja (noche, madrugada) la concentración puede cambiar en un orden de magnitud en pocas decenas de metros (el feedback habla de hasta \~20 veces). Si la base de la inversión está a 90 m, medir a 80 m y a 100 m es medir dos masas de aire distintas. Sin el dato de h\_mix, una lectura baja es ambigua: puede ser aire limpio o que el dron voló sobre la inversión.

### 5.3 De dónde sacar h\_mix

| Fuente | Qué da | Limitación | Uso |
| --- | --- | --- | --- |
| Open-Meteo, variable `boundary_layer_height` | Altura de capa límite horaria; disponible en los modelos GFS ([docs GFS](https://open-meteo.com/en/docs/gfs-api)) | Resolución GFS \~13 km: no resuelve la capa límite interna costera de la bahía | Planificación previa (Paso 8) |
| Open-Meteo, temperatura en niveles de presión (1000, 975, 950 hPa) | Detecta si hay inversión (T sube con la altura) | Muy gruesa verticalmente | Confirmar inversión |
| Perfil vertical del propio dron | Ascenso 0→120 m sobre el aeródromo al despegar, registrando T y HR | Solo hasta 120 m | **Recomendado**: es el dato in situ que no existe (el radiosondeo más cercano está a 100 km) |
| Pronóstico de ventilación MMA ([airecqp.mma.gob.cl](https://airecqp.mma.gob.cl/wp-content/uploads/2024/09/2024-09-03_PRONOSTICO_CONCON-QUINTERO-PUCHUNCAVI_MMA.pdf)) | Condición horaria Buena/Regular/Mala para la bahía | Cualitativo | Elegir la ventana horaria |

Agreguen `boundary_layer_height` al extractor de Open-Meteo (ya consultan viento y niebla, es un parámetro más en la misma llamada) y guárdenlo en la tabla de amenazas/condiciones con su hora.

### 5.4 Hora de medición: una tabla de ventanas

| Ventana | Estado de la atmósfera | Qué ve el dron a \~100 m | Valor para el proyecto |
| --- | --- | --- | --- |
| Noche y madrugada | Estable, inversión baja, pluma suspendida en altura | La pluma antes de que baje | **Alerta temprana** (objetivo principal). Ojo: vuelo nocturno requiere autorización adicional |
| Mañana (fumigación) | Capa de mezcla creciendo, pluma bajando | El momento del impacto sobre La Greda / Puchuncaví | Atribución de fuente y validación con estaciones |
| Tarde | Mezcla profunda, brisa marina SO | Concentraciones diluidas y homogéneas | Control / fondo; menor interés |

Crucen esto con el ciclo diario de SO₂ por estación (Paso 3.5) para mostrar con datos a qué hora suben las concentraciones en cada lado de la bahía.

### 5.5 Qué gana y qué deja fuera volar a ≤120 m (párrafo honesto)

- Gana: cubre el vacío entre las estaciones (3–4 m) y la parte alta de la columna; puede ver la pluma nocturna cuando la inversión está bajo \~120 m; mide in situ el perfil T/HR que hoy no existe.
- Deja fuera: todo lo que está sobre 120 m. En 2018 la inversión estuvo a \~400 m, fuera del alcance legal. En esos casos el dron no ve la pluma y lo debe declarar. Para mayor altura existen otras herramientas (radiosondeo, LIDAR/ceilómetro, SODAR); menciónenlas como complemento.
- Sobre la torre de Puchuncaví que mide hasta 40 m: **no encontré una fuente pública que confirme esa altura**. Búsquenla (SMA/SNIFA, red meteorológica de la red Ventanas) y citen; si no la encuentran, quiten el número.
- Verifiquen el artículo exacto de la DAN 151 (3.ª ed., Res. Ex. 1033 de 27-05-2024, publicada en el DO el 11-03-2025 según [vLex](https://vlex.cl/vid/resolucion-num-1033-exenta-1073913272)) que fija los 120 m y la distancia VLOS de 500 m, y citen el número de artículo, no solo la norma. Revisen también si en zonas no pobladas aplica la DAN 91 en vez de la 151.
