# Dossier de evidencia — Ruteo UAV Quintero/Puchuncaví

Oct 31, 2026 · @Benjamin

## Qué cambia en el informe

El feedback reorienta el eje del trabajo: el problema deja de ser solo «volar seguro» y pasa a ser **volar seguro para obtener una medición válida y atribuible**. Esa frase debe quedar en el Resumen Ejecutivo, en el Pivote Central (sec. 1.3) y en la definición de amenazas (sec. 9).

Tres consecuencias estructurales:

1. **Las amenazas se parten en dos familias.** Las que ponen en riesgo la aeronave (viento, obstáculos, tráfico aéreo, VMC) y las que ponen en riesgo la validez del dato (humo, aerosol marino, lluvia, humedad, buques a barlovento, hora del día). La segunda familia es la que da identidad científica al proyecto y hoy no existe en el informe.
2. **La altura deja de ser un supuesto fijo.** Pasa de «100 m AGL constante» a una variable relativa a la capa de mezcla, con dato previo a cada vuelo.
3. **La zona se justifica, no se asume.** Por alcance real del UAV desde SCER, por anillos de distancia a la fuente y por dirección del viento dominante.

Este dossier reúne el dato duro y la cita verificada para cada uno de esos puntos. Cada sección está ordenada para que se pueda copiar directo al LaTeX: afirmación, cifra, fuente oficial y dónde va en el informe.

**Advertencia de uso.** Todo lo que aparece aquí fue verificado contra la fuente que se enlaza. Donde no encontré respaldo público lo digo explícitamente en vez de rellenar: esos puntos quedan marcados como *pendiente de verificación* y no deben entrar al paper sin confirmarlos.

## Estado actual de las fuentes emisoras (dato clave del feedback)

El informe describe el polo industrial como en 2018. Cambió, y el cambio es un argumento **a favor** del proyecto: el mapa de fuentes ya no es el que motivó la ubicación de las estaciones fijas.

### Inventario oficial vigente (año 2025)

El dato más fuerte que encontré: el [Informe de Inventario de Emisiones año 2025](https://ppda.mma.gob.cl/wp-content/uploads/2026/05/Informe-de-emisiones-correspondiente-al-ano-2025-1.pdf) de la SEREMI del Medio Ambiente de Valparaíso (mayo 2026), elaborado en el marco de los artículos 32 y 52 del D.S. 105/2018. Reemplaza cualquier cifra de emisiones anterior que tengan.

| Contaminante | 2024 (t/año) | 2025 (t/año) | Tendencia |
| --- | --- | --- | --- |
| MP | 267,8 | 303,9 | Aumenta |
| SO₂ | 2.371 | 3.528 | Aumenta |
| NOx | 2.496 | 3.378 | Aumenta |
| COVs | 528,7 | 661,4 | Aumenta |
| Benceno | 2,2 | 2,26 | Estable |
| Tolueno | 4,73 | 4,62 | Estable |
| Xileno | 3,67 | 3,59 | Estable |

**Esto es oro para la introducción:** las emisiones de SO₂, NOx, MP y COVs *aumentaron* entre 2024 y 2025 pese al PPDA. El problema no es histórico, está vigente.

### Quién emite qué, hoy (2025)

Tomado de las tablas 2 a 8 del mismo informe. Úsenlo para justificar qué nodo mide qué contaminante.

| Instalación | SO₂ (t/año) | NOx (t/año) | MP (t/año) | COVs (t/año) | Implicancia para el muestreo |
| --- | --- | --- | --- | --- | --- |
| AES / Quintero Energía (termoeléctrica) | 2.639 | 2.528 | 45,2 | 0,009 | **Fuente dominante de SO₂ y NOx.** Casi no emite COVs: sirve para separar firmas químicas |
| ENAP Aconcagua | 841 | 599 | 78 | 465 | **Fuente dominante de COVs y BTEX** (1,83 t benceno). Está en Concón, fuera del área inmediata |
| Puerto Ventanas S.A. | 0,14 | 51,3 | 156,7 | 6,69 | **Principal emisor de MP** del inventario. Graneles: polvo fugitivo, no de chimenea |
| ENEL Central Quintero | 16,5 | 142,2 | 19 | 26,8 | Fuente de NOx y COVs en el sector sur |
| CODELCO (División Ventanas) | 30,8 | 4,6 | 1,03 | 0,0007 | Colapsó tras el cierre de la fundición. Solo refinería/RAF |
| ENAP TMQ | 0,07 | 2,1 | 0,16 | 54 | Terminal marítimo: COVs por carga/descarga |
| GNL Quintero | 0,002 | 3,7 | 0,05 | 9,8 | COVs crecientes (de 4,4 a 9,8 t en un año) |

El mayor aumento individual lo explica AES / Quintero Energía: SO₂ de 1.435 a 2.639 t/año y NOx de 1.502 a 2.528 t/año entre 2024 y 2025.

### Cierre de la Fundición Ventanas

El cese de la operación de la fundición, incluida su planta de ácido, se concretó el **31 de mayo de 2023**, tras la Ley 21.546 (20-04-2023) y la Res. Ex. 844/2023 de Sernageomin (16-05-2023) que aprobó el plan de cierre temporal parcial. Fuente primaria: [informe SMA/SNIFA](https://snifa.sma.gob.cl/General/Descargar/1104418388) y [segundo expediente SNIFA](https://snifa.sma.gob.cl/General/Descargar/1104374183).

Dos matices que deben quedar en el paper, porque son los que un evaluador va a preguntar:

- **Codelco no desapareció de la bahía.** Posterior al cese de la fundición continuó en operación el proceso RAF (hornos de refino) y la refinería. El inventario 2025 lo confirma: Codelco sigue declarando 30,8 t/año de SO₂.
- **La chimenea sigue en pie.** Como obstáculo físico de 152 m es igual de relevante para el ruteo; como fuente de emisión de fundición, ya no.

### Cambio de propiedad de la termoeléctrica

AES Andes anunció en diciembre de 2024 la venta del complejo Ventanas a **Quintero Energía SpA**, cerrada en enero de 2025. Operan las unidades 3 (Nueva Ventanas, 267 MW) y 4 (Campiche, 270 MW), 537 MW en total; los nuevos dueños declararon que ambas seguirían operando «hasta nuevo aviso» ([La Tercera](https://www.latercera.com/pulso/noticia/los-nuevos-duenos-pagaron-solo-us-5-millones-a-aes-por-el-complejo-termoelectrico-ventanas/), [Global Energy Monitor](https://www.gem.wiki/Ventana_power_station)). El inventario SEREMI 2025 ya la nombra «AES (Quintero Energía)».

### Buques: la fuente que el informe ignora

El PPDA obliga explícitamente a incluir en el inventario **las emisiones atmosféricas de las naves que ingresen a la bahía de Quintero** (art. 52, [informe SEREMI 2024](https://ppda.mma.gob.cl/wp-content/uploads/2025/05/INVENTARIO-EMISIONES-PERIODO-2024-120525.pdf)). Existe además un estudio encargado por el MMA: [«Consultoría para la Estimación de las Emisiones Producidas por las Embarcaciones Marítimas en la Bahía de Quintero»](https://pras.mma.gob.cl/wp-content/uploads/2025/01/INFORME-FINAL-4.-Accion-Quintero-Puchuncavi-2023.pdf) (AMBIOSIS, 2023), que cubre el periodo 2018–2023 y concluye sobre el impacto de los NO₂ de motores de buques y remolcadores en la calidad del aire de la bahía.

Una memoria de la USM estimó para 2023: 12.940 t de NOx, 866 t de MP, 217 t de COVs no metánicos y 38 t de SOx por transporte naviero en la bahía ([repositorio USM](https://repositorio.usm.cl/handle/123456789/74807)). Cítenla como tesis de pregrado, no como dato oficial; el dato oficial es el informe AMBIOSIS/MMA.

La Capitanía de Puerto de Quintero dictó además normas complementarias de control de emisiones para naves que recalan en la bahía ([DIRECTEMAR, ord. 12000/420 del 02-08-2023](https://prontus.directemar.cl/directemar/site/docs/20230804/20230804122012/40__12000_420__020823__c_p__qui_publ.pdf)).

**Por qué importa para la medición:** si hay un buque fondeado a barlovento del punto de muestreo, el dron atribuye a la industria terrestre una pluma que viene del mar. Esto va a la sección de amenazas a la validez.

## La red de monitoreo real, y por qué sus estaciones son distintas

Sus 8 nodos «SINCA» no corresponden a la red vigente. Hay que actualizarlos: es un error verificable en segundos por el evaluador.

### La nueva Red Pública (2023–2025)

La Res. Ex. 222 del 15-03-2023 del MMA estableció las acciones para implementar una nueva red pública de **catorce estaciones** bajo administración del propio Ministerio, cuyo diseño salió del estudio «Mejoramiento de la red de monitoreo de calidad del aire en las comunas de Concón, Quintero y Puchuncaví», desarrollado por la Fundación Eurochile en colaboración con el **Instituto Meteorológico Finlandés (FMI)**. La red contempla los contaminantes normados (MP10, MP2,5, SO₂ y NO₂), caracterización fisicoquímica del material particulado y medición de COVs tipo BTEX. Fuente: [Res. Ex. 2.607/2025, Diario Oficial del 04-06-2025](https://www.diariooficial.interior.gob.cl/publicaciones/2025/06/04/44165/01/2653860.pdf).

Dos detalles de esa resolución que sirven directamente al paper:

- El **Súper Sitio Quintero** medirá ácido sulfhídrico (H₂S) y compuestos orgánicos volátiles de manera continua, incluyendo benceno, tolueno, etilbenceno y xilenos. Es decir: el Estado está cerrando, en 2025, exactamente el vacío que la SMA denunció en 2018. Buen punto para matizar su argumento —el vacío ya no es total— y a la vez reforzarlo: sigue siendo medición **a nivel de suelo**.
- La resolución reconoce que las estaciones Valle Alegre y Súper Sitio Quintero **quedaron duplicadas en el mismo territorio** porque no se consiguió otro comodato con representatividad poblacional adecuada. Esto es un argumento potente: la ubicación de las estaciones fijas está condicionada por disponibilidad de terreno, no solo por criterio técnico. El UAV no tiene esa restricción.

El listado de las 14 estaciones inauguradas en 2025: en **Puchuncaví** (Súper Sitio Ventanas, Escuela La Greda, Puchuncaví Centro, Pucalán, Maitencillo); en **Quintero** (Súper Sitio Quintero, Loncura, Valle Alegre, Quintero Sur, Mantagua); en **Concón** (Súper Sitio Concón, Estadio Atlético Municipal, Puente Colmo, Concón Oeste y Bomberos Concón) ([El Mostrador](https://www.elmostrador.cl/agenda-pais/agenda-sustentable/2025/05/13/inauguran-red-publica-de-monitoreo-de-calidad-del-aire-en-concon-quintero-y-puchuncavi/), [El Mercurio de Valparaíso](https://www.mercuriovalpo.cl/impresa/2025/04/29/full/cuerpo-principal/5)).

La red histórica industrial (Codelco/AES, entregada al Estado en 2018) comprendía siete estaciones: Quintero, Ventanas, Puchuncaví, Los Maitenes, La Greda, Valle Alegre y Sur ([Codelco](https://codelco.com/operaciones/ventanas/noticias/codelco-ventanas-y-aes-gener-entregan-la-supervision-de-sus-estaciones)).

**Acción concreta:** revisen si su nodo `sinca_campiche` existe; no aparece en ningún listado oficial que encontré. Y agreguen **Los Maitenes**, que sí es una estación histórica relevante por su cercanía al complejo.

### Por qué cada estación mide algo distinto (respuesta al feedback)

Esta es la justificación que pide el profesor, y hay evidencia publicada para sostenerla con distancias reales. Un estudio de biomonitoreo caracterizó los sitios por distancia y azimut respecto del complejo industrial ([Gorena et al., *Atmosphere* 14(5):893](https://www.mdpi.com/2073-4433/14/5/893/htm)):

| Sitio | Distancia y dirección al complejo | Qué representa |
| --- | --- | --- |
| La Greda | 0,8 km NE | Impacto máximo bajo brisa marina del SO. Receptor sensible (escuela) pegado a la fuente |
| Los Maitenes | 3,5 km E | Valle interior, impacto intermedio |
| Puchuncaví | 7,3 km NE | Extremo del gradiente a sotavento; donde llega la fumigación |
| Valle Alegre | 10,4 km SE | Borde del área de influencia; sirve de referencia |

El mismo trabajo recuerda que las concentraciones de Cu, As y Pb en suelo **disminuyen en función de la distancia al complejo industrial**, y que el análisis de factores de enriquecimiento separa tres a cuatro fuentes: fundición y refinería de cobre, centrales a carbón y fuentes geogénicas.

Agreguen a eso el componente temporal: el viento de la bahía rota sistemáticamente de componente noreste (noche y madrugada) a suroeste (tarde), como se ve en los pronósticos diarios del MMA ([ejemplo del 03-09-2024](https://airecqp.mma.gob.cl/wp-content/uploads/2024/09/2024-09-03_PRONOSTICO_CONCON-QUINTERO-PUCHUNCAVI_MMA.pdf)). Por eso una estación al NE y una al SO del complejo no solo miden concentraciones distintas: las miden **a horas distintas**.

El CR2 lo documentó para COVs: ciertos compuestos emitidos por procesos de petróleo y gas ubicados **al sur de la bahía** llegan hasta Quintero por efecto del viento, bajo vientos débiles del norte y noroeste, generando las quejas por olores ([CR2, Policy Brief N°14, dic. 2023](https://www.cr2.cl/wp-content/uploads/2023/12/Policy-brief-Los-desafíos-ante-la-contaminación-atmosférica-en-la-bahía-de-Quintero-Puchuncaví.pdf)).

### El dato que cierra el argumento

La recomendación n.º 5 de ese mismo Policy Brief del CR2 es: **optimizar la configuración de la red de monitoreo de Concón-Quintero-Puchuncaví de acuerdo con el complejo patrón de circulación del viento y transporte de contaminantes observado en la zona.**

Úsenla literalmente en la introducción. Es un centro de investigación nacional diciendo que la red fija está mal configurada respecto al viento, que es precisamente el problema que su planificador de rutas resuelve de forma móvil.

## Física del problema, con evidencia local publicada

Aquí está el material para la sección nueva que explica cómo se mueve la contaminación. Toda la evidencia es **de esta bahía**, no genérica, que es lo que el feedback exige.

### El régimen meteorológico de la bahía

La referencia central es Seguel et al. (2023), *Environmental Pollution* 330:121759 ([DOI 10.1016/j.envpol.2023.121759](https://doi.org/10.1016/j.envpol.2023.121759)), del DGF de la U. de Chile y el CR2. Describe el marco físico así:

- El clima regional está dominado por el **anticiclón subtropical del Pacífico sureste**, que produce viento predominante del sur-suroeste a lo largo de la costa y una **capa límite marina (MBL) coronada por una inversión térmica de subsidencia**.
- Se desarrolla una **brisa mar-tierra débil en la tarde**, cuyo alcance tierra adentro está limitado por el cordón costero de unos 700 m s.n.m.
- Ese patrón puede ser alterado varias veces al mes por **bajas costeras** de núcleo cálido, que modifican la profundidad de la MBL, la nubosidad y el régimen de viento.

La campaña de enero 2022 capturó los dos regímenes: primero una baja costera al sur de Quintero, con flujo del norte y **capa límite marina profunda cubierta de nubes**; después del colapso de esa condición, un régimen de cielo despejado con **capa límite somera** y vientos fuertes del sur durante el día.

**Esto es exactamente lo que su proyecto necesita citar.** La profundidad de la capa límite en esta bahía no es un parámetro fijo: cambia de régimen en días. Por eso una altura de vuelo fija de 100 m no tiene sentido físico sin conocer dónde está el techo de la capa de mezcla ese día.

### Qué instrumentos se usaron y qué vacío dejan

En esa campaña se desplegaron en la costa este de la península de Quintero (32,78° S; 71,53° W, 5 m s.n.m.) un PTR-TOF-MS, un aetalómetro y un **SODAR**, además de lanzamientos de radiosondas. El proyecto CR2 detalla que el SODAR (modelo MFAS-Scintec) entrega perfiles de magnitud y dirección del viento cada 15 minutos **desde 30 m hasta aproximadamente 300–400 m** en zonas costeras ([CR2 – proyecto Quintero](https://www.cr2.cl/quintero/)).

Y un dato decisivo para su argumento sobre la brecha instrumental: el paper reconstruye los **perfiles verticales de temperatura de la baja tropósfera usando Santo Domingo**, confirmando que la MBL estaba coronada por una inversión térmica de profundidad variable. Es decir: la brecha de los 100 km que ustedes denuncian para 2018 **seguía vigente en 2022** en la literatura científica más reciente.

Matiz honesto que deben incluir: desde 2022 el CR2 sí ha operado SODAR y radiosondas puntuales en Quintero, y en 2025 inició una nueva campaña coincidente con la actualización de la red del MMA ([U. de Chile](https://uchile.cl/noticias/226589/u-de-chile-medira-contaminantes-en-concon-quintero-y-puchuncavi)). El vacío no es «no existe nada», es «no existe operación regular ni cobertura espacial móvil». Decirlo así los hace más creíbles, no menos.

### El ciclo diario: el dato que justifica la hora de vuelo

Un análisis de 10 sitios de la red oficial entre 2010 y 2021 concluye que la variabilidad estacional de MP10, MP2,5 y SO₂ se caracteriza por **niveles más altos en otoño e invierno, especialmente durante las noches y primeras horas de la mañana, en condiciones de baja ventilación o calma** ([Araya et al., *Urban Climate* 55:101880, 2024](https://www.sciencedirect.com/science/article/pii/S2212095524000762)).

El mismo trabajo agrega el argumento que sostiene todo su proyecto: los niveles de MP10, MP2,5 y SO₂ durante los eventos de intoxicación aguda **no explican los síntomas** de los pacientes que han colapsado los centros de salud desde 2011, y concluye que deben estudiarse en profundidad las concentraciones de contaminantes no normados **bajo condiciones de estabilidad atmosférica y baja ventilación**.

Eso es, literalmente, una convocatoria publicada a hacer lo que ustedes proponen: medir no normados, de noche o madrugada, bajo inversión.

### Episodios y magnitudes para citar

| Hecho | Dato | Fuente |
| --- | --- | --- |
| Crisis agosto 2018 | 1.370 atenciones de urgencia | [CR2 Policy Brief N°14](https://www.cr2.cl/wp-content/uploads/2023/12/Policy-brief-Los-desafíos-ante-la-contaminación-atmosférica-en-la-bahía-de-Quintero-Puchuncaví.pdf) |
| Episodio junio 2022 | SO₂ horario de 1.326,5 µg/m³ en estación Quintero, con peak de 2.240 µg/m³ a las 00:20; norma horaria (350 µg/m³) superada cuatro veces | [Fundación Terram](https://www.terram.cl/el-mundo-al-reves-quintero-puchuncavi-y-las-prioridades-invertidas/) |
| Año 2023 | 728 consultas médicas por síntomas asociados a hidrocarburos en el aire (MINSAL) | CR2 Policy Brief N°14 |
| Mayo 2023 | 177 casos tras niveles de hidrocarburos no metánicos de 6.000 ppb, más de 70 veces el promedio anual de Quintero | CR2 Policy Brief N°14 |
| Norma nueva | D.S. 15/2023 MMA establece norma primaria de calidad del aire para benceno | [BCN](https://www.bcn.cl/leychile/navegar?i=1192010) |

Noten el detalle del peak de SO₂ **a las 00:20 horas**: es contaminación nocturna bajo inversión, exactamente el escenario donde el dron a 100 m aporta y la estación de suelo llega tarde.

### Contraargumento que les van a hacer

El MMA sostiene que los episodios horarios de SO₂ se redujeron un 93 % entre 2018 y 2022 gracias a la Gestión de Episodios Críticos del PPDA ([MMA](https://mma.gob.cl/a-3-anos-de-la-implementacion-del-plan-de-prevencion-y-descontaminacion-atmosferica-de-concon-quintero-y-puchuncavi-se-han-reducido-en-mas-de-un-90-los-peaks-de-so2/)). Anticípenlo: el SO₂ bajó, pero los episodios por COVs e hidrocarburos continuaron (728 consultas en 2023) y las emisiones declaradas de SO₂, NOx, MP y COVs **aumentaron** entre 2024 y 2025. El problema migró de contaminante, no desapareció.

## Altura y hora de medición

### El cambio conceptual

No existe una altura universal de medición. Lo que determina si el dato sirve es **la posición del dron respecto de la capa de mezcla y de la pluma**, y eso cambia durante el día. Por lo tanto la variable a registrar no es «altura sobre el suelo» sino **altura relativa a la capa de mezcla**, z/h\_mix.

El respaldo local está en la sección anterior: la campaña de enero 2022 en Quintero documentó dos regímenes con capa límite **profunda** y luego **somera** en el mismo mes (Seguel et al., 2023). Si la profundidad de la capa cambia de régimen en días, una cota fija carece de sentido físico.

Consecuencia práctica: si la base de la inversión está a 90 m, medir a 80 m y a 100 m es medir en dos masas de aire distintas. Sin el dato de h\_mix, una lectura baja es ambigua: puede significar «aire limpio» o «volé por encima de la inversión».

### De dónde sacar la altura de la capa de mezcla

| Fuente | Variable | Cobertura vertical | Limitación | Uso propuesto |
| --- | --- | --- | --- | --- |
| Open-Meteo | `boundary_layer_height` | Columna completa | Solo disponible en el modelo **GFS** (gfs\_seamless), resolución \~13 km: no resuelve la capa límite interna costera | Planificación previa al vuelo |
| Open-Meteo | Temperatura en niveles de presión | 1000/975/950 hPa | Resolución vertical gruesa | Detectar presencia de inversión |
| Perfil del propio UAV | T, HR vs. altura en ascenso 0–120 m | Hasta 120 m AGL | Techo legal | **Dato in situ que hoy no existe** |
| Pronóstico MMA | Factor de ventilación horario (Buena/Regular/Mala) | Cualitativo | No da altura | Elegir ventana horaria |
| SODAR CR2 | Perfil de viento cada 15 min, 30–400 m | Campaña puntual | No operacional continuo | Validación/comparación |

La disponibilidad de `boundary_layer_height` solo en GFS está documentada en la [tabla de variables de la API GFS de Open-Meteo](https://open-meteo.com/en/docs/gfs-api). **Declárenlo como limitación**: GFS a \~13 km no resuelve la capa límite interna térmica costera, que es justamente el mecanismo de la fumigación. Eso refuerza por qué hace falta el perfil in situ del dron.

### Propuesta de redacción para el supuesto S3

> **S3. Altura de medición referida a la capa de mezcla.** El techo legal de operación es 120 m AGL (DAN 151). Dentro de ese techo, la cota de muestreo se selecciona según la altura de la capa de mezcla (h\_mix) pronosticada para la ventana de vuelo, obtenida de Open-Meteo (`boundary_layer_height`, modelo GFS) y verificada mediante un perfil vertical in situ de temperatura y humedad relativa ejecutado por el propio UAV sobre el punto de despegue. Cada muestra se registra con dos coordenadas verticales: z (m AGL) y la razón adimensional z/h\_mix. En esta fase del proyecto el ruteo se resuelve en planta y la cota se fija por misión, no por arista.

### Ventanas horarias

| Ventana | Estado atmosférico | Qué captura el dron a \~100 m | Valor | Restricción |
| --- | --- | --- | --- | --- |
| Noche y madrugada | Capa estable, inversión baja, pluma suspendida en altura | La pluma **antes** de que descienda sobre la población | Alerta temprana. Es el escenario del peak de SO₂ de las 00:20 del 06-06-2022 | Vuelo nocturno requiere autorización adicional DGAC |
| Mañana (fumigación) | Capa de mezcla creciendo, pluma descendiendo | El momento del impacto sobre La Greda y Puchuncaví | Atribución de fuente y validación contra estaciones | Niebla matinal frecuente (VMC) |
| Tarde | Mezcla profunda, brisa del SO | Concentraciones diluidas | Control y medición de fondo | Viento más intenso |

Esto calza con el hallazgo de Araya et al. (2024): máximos de MP y SO₂ en noches y primeras horas de la mañana bajo baja ventilación.

### Qué gana y qué deja fuera volar bajo 120 m

**Gana:** cubre el estrato entre las estaciones (3–4 m) y el techo legal; detecta la pluma nocturna cuando la inversión está por debajo de 120 m; genera el perfil T/HR in situ que hoy solo existe en campañas puntuales.

**Deja fuera:** todo lo que ocurre sobre 120 m. En la crisis de 2018 la inversión estuvo a \~400 m, fuera del alcance legal: en ese escenario **el dron no habría visto la pluma**, y el informe debe decirlo. Para esa franja existen otras herramientas (radiosondeo, SODAR hasta 300–400 m, ceilómetro/LIDAR). Preséntenlas como complemento, no como competencia.

**Pendiente de verificación:** la afirmación de que la torre de Puchuncaví entrega información solo hasta 40 m. No encontré fuente pública que lo confirme. Búsquenla en los expedientes de SNIFA o en las especificaciones de la red Ventanas, y si no aparece, reemplácenla por el dato que sí está documentado: las estaciones de la red miden a nivel de suelo y el SODAR del CR2 parte en 30 m, de modo que el estrato bajo los 30 m y la continuidad temporal sobre él quedan sin cobertura operacional regular.

## Amenazas a la validez de la medición (sección nueva, la más importante)

Esta es la contribución que el feedback pide y que hoy no existe en el informe. La idea rectora: **una amenaza a la medición no vuelve peligrosa la zona, vuelve inválido el dato.** Se tratan distinto: no se bloquea la arista, se marca la muestra como contaminada o se reprograma la ventana de vuelo.

### Tabla maestra para el paper

| Amenaza | Qué le hace a la medición | Variable observable | Fuente de datos | Umbral propuesto | Acción |
| --- | --- | --- | --- | --- | --- |
| Humo de incendios | Aporta MP y COVs de combustión de biomasa: la muestra deja de representar a la industria | Foco activo a barlovento | NASA FIRMS VIIRS 375 m | Foco activo dentro de 10 km en sector de barlovento | Invalidar muestra de MP; marcar como confusor |
| Viento (dirección) | Decide si el punto está o no dentro de la pluma: es el criterio de dónde medir | Dirección y velocidad a 10/80/120 m | Open-Meteo, DMC | Define sector a sotavento (abanico 15°–40°) | Seleccionar destino, no bloquear |
| Viento (velocidad) | Diluye o concentra; cambia el ancho de la pluma | Velocidad a 120 m | Open-Meteo | > 12 m/s: además No-Go aeronáutico | Registrar junto al dato |
| Humedad relativa | Hincha partículas higroscópicas: el sensor óptico **sobrestima** MP | HR 2 m y a cota de vuelo | Open-Meteo, METAR | HR > 70–80 % | Corregir por crecimiento higroscópico o invalidar |
| Niebla / camanchaca | Saturación: además de VMC, arruina la lectura óptica | Visibilidad | Open-Meteo, [aviationweather.gov](https://aviationweather.gov) METAR | < 1.000 m | No-Go doble (aeronave y dato) |
| Aerosol marino | Sal marina cuenta como MP sin ser industrial | Oleaje, viento del mar | Copernicus CAMS, Open-Meteo Marine | Brisa marina fuerte + oleaje | Usar razón MP/SO₂ para discriminar |
| Lluvia (scavenging) | Lava la atmósfera: la pluma ya no está en el aire | Precipitación reciente | Open-Meteo | Lluvia en las últimas N horas | Declarar condición; no comparar con días secos |
| Buques fondeados | Emiten NOx, SO₂ y MP desde el mar: atribución errónea | Posición AIS | AIS / DIRECTEMAR | Buque a barlovento dentro de X km | Marcar riesgo de atribución |
| Hora del día | Cambia la altura de la pluma respecto al dron | Hora y capa de mezcla | Open-Meteo `boundary_layer_height` | Ver sección de altura | Elegir ventana |

### Respaldo de cada una

**Humedad y sensores ópticos.** Es el efecto mejor documentado y el que más les conviene citar, porque es cuantitativo. Los sensores ópticos de bajo costo no secan la muestra, de modo que el tamaño de partícula se sobrestima con HR alta. Un estudio midió una sobrestimación de **factor \~5 antes de corregir, reducida a 1,05** aplicando una corrección basada en crecimiento higroscópico con valores físicamente razonables de κ ([Crilley et al., *Sensors* 18(9):2790](http://dx.doi.org/10.3390/s18092790)). Otro trabajo reporta reducción del factor de 4,59 a 1,01 y mejora del R² de 0,34 a 0,78 con la misma corrección. La sobrestimación aparece típicamente sobre **70–75 % de HR**, y en algunos equipos desde 60 % ([Badura et al., *Journal of Sensors* 2018:5096540](https://onlinelibrary.wiley.com/doi/10.1155/2018/5096540)). La teoría de referencia es κ-Köhler ([Malings et al., *AMT* 17:1051, 2024](https://amt.copernicus.org/articles/17/1051/2024/)).

En una bahía con camanchaca y HR costera alta, **esto no es un detalle: es la principal fuente de sesgo del dato de MP.** Su sección de niebla hoy solo habla de VMC; debe hablar también de esto.

**Aerosol marino.** El argumento físico se apoya en lo anterior: la sal marina es higroscópica, crece con la HR y el sensor óptico no distingue composición. La literatura de calibración de sensores ópticos trata explícitamente las sales como la causa más discutida de sobrestimación. Para la bahía hay además un respaldo local relevante: Seguel et al. (2023) señalan que la bahía de Quintero-Puchuncaví es una zona de **alta productividad por surgencia**, donde el sulfuro de dimetilo (DMS) biogénico marino alcanza 300–500 pptv, y que además el DMS se incorpora al GLP como odorizante junto con el terbutilmercaptano. Es decir: hay una firma química marina real que puede confundirse con la industrial.

*Estrategia de discriminación para el paper:* la sal sube MP10 pero no sube SO₂. Si el dron registra MP10 alto con SO₂ bajo bajo brisa marina fuerte, probablemente es sal. Es la misma lógica de separación por química que se usa con el humo. Para la norma la sal sí cuenta —MP10 es MP10—, así que la amenaza es a la **atribución de fuente**, que es justamente lo que su sistema promete aportar.

**Lluvia y scavenging.** La prueba local es fuerte: en los valles de Puchuncaví y Catemu, las concentraciones de cobre y selenio **en agua de lluvia disminuyeron exponencialmente con la distancia a las fuentes** y estaban significativamente correlacionadas entre sí ([Bol. Soc. Chil. Quím., 2000](https://hal-univ-pau.archives-ouvertes.fr/hal-00291432)). Si la lluvia arrastra metales del complejo, esos metales ya no están en el aire que el dron mediría. Conclusión para el paper: medir inmediatamente después de una lluvia subestima; la condición de precipitación reciente debe registrarse como metadato de cada muestra.

**Incendios como confusor.** Hoy su informe trata el fuego solo como riesgo aeronáutico (turbulencia, aeronaves cisterna). Agreguen el otro lado: el humo aporta MP2,5, CO y COVs de combustión de biomasa que **no provienen del cordón industrial**. Una muestra tomada con humo a barlovento sobrestima la contribución industrial. El producto VIIRS 375 m de NASA FIRMS sigue siendo la fuente ([Schroeder et al., *RSE* 143:85–96](https://doi.org/10.1016/j.rse.2013.12.008)); lo que cambia es el uso: evaluar la posición del foco **respecto al viento**, no solo la distancia.

**Buques.** Ver sección de fuentes. El dato oficial es el estudio AMBIOSIS/MMA sobre emisiones de embarcaciones en la bahía, que el propio PPDA exige incorporar al inventario.

### Tiempo de respuesta del sensor: el límite físico de la misión

Este punto merece su propia subsección en el informe, porque es un hallazgo de ingeniería, no una advertencia.

Los sensores electroquímicos de gases tienen tiempos de respuesta **t90 típicos de 15 a 60 segundos** ([Honeywell, Nota Técnica 114](https://automation.honeywell.com/content/dam/his-sandbox/products/gas-and-flame-detection/documents/Technical-Note-114_updated_03-26-2018.pdf)). A eso se suma el retardo de transporte del sistema de muestreo, igual al volumen del tubo dividido por el caudal de la bomba.

La consecuencia operacional, con sus propios números (S6: v = 15 m/s):

```latex
d_{\text{smear}} = v \cdot t_{90}
```

Con t90 = 30 s y v = 15 m/s, **la lectura queda promediada sobre 450 m de trayectoria**. Si el ancho de la pluma a 2 km de la fuente en condición estable es de unos 300 m (ver sección de escala espacial), el dron la cruza en menos tiempo del que el sensor tarda en reaccionar: **subestima el peak o directamente no lo detecta.**

Tres consecuencias de diseño que deben entrar al informe:

1. **La velocidad de crucero no sirve para medir.** Hay que definir una velocidad de muestreo distinta, o directamente vuelo estacionario en el punto. Si quieren resolver una pluma de 300 m con t90 = 30 s, necesitan v ≤ 2–3 m/s en el tramo de medición. Esto cambia el cálculo de autonomía y de alcance.
2. **El ruteo debe distinguir tramos de tránsito y tramos de muestreo**, con velocidades y costos distintos. Es una extensión natural de su función de costo multiobjetivo y una buena contribución original.
3. **El retardo debe corregirse como offset fijo** al georreferenciar el dato, y hay que registrar todo con un solo reloj (preferentemente GPS) y muestrear más rápido que la respuesta del sensor (1–10 Hz).

Un trabajo de referencia que hace exactamente este análisis en plumas volcánicas con drones y sensores electroquímicos de SO₂ es [Galle et al., *AMT*](https://research.chalmers.se/publication/524626/file/524626_Fulltext.pdf), que formaliza la relación entre el tiempo de variabilidad de la concentración y el t90 del sensor. Cítenlo: es el antecedente metodológico directo de este problema.

## Amenazas a la aeronave, reclasificadas

Esta familia ya existe en su informe. Lo que cambia es que ahora es **una de dos**, y que varias amenazas pertenecen a ambas categorías con umbrales distintos.

| Amenaza | Riesgo a la aeronave | ¿También afecta la medición? | Acción sobre la arista |
| --- | --- | --- | --- |
| Obstáculos verticales (chimeneas 50–152 m, líneas 110/220 kV) | Colisión, interferencia electromagnética sobre brújula y magnetómetro | No | **Bloqueo duro** |
| Tráfico aéreo tripulado (ADS-B) | Colisión; obligación de ceder el paso | No | **Bloqueo temporal** |
| Viento > 12 m/s a 120 m | Pérdida de control, límite estructural | Sí: modifica dilución y ancho de pluma | No-Go aeronáutico |
| Niebla / visibilidad < 1.000 m | Pérdida de VMC | Sí: HR alta sesga el sensor óptico de MP | No-Go doble |
| Incendios activos | Turbulencia convectiva, humo, aeronaves de combate | Sí: humo como confusor químico | Bloqueo + invalidación de muestra |
| Densidad poblacional > 2.500 hab/km² | Riesgo a terceros en tierra (SORA GRC) | No | Penalización |
| Sombra de cobertura C2 | Pérdida de telemetría, fly-away | No | Penalización |

El mensaje para el informe: **viento, niebla e incendios son amenazas duales.** Hoy su texto solo documenta la mitad aeronáutica de cada una.

### Corrección normativa importante

La DAN 151 vigente **cambió de título y de alcance**. Su bibliografía la cita como «Operaciones de aeronaves pilotadas a distancia (RPAS) **en asuntos de interés público**, que se efectúen sobre áreas pobladas». La tercera edición, aprobada por Resolución Exenta N.º 04/3/0089/1033 del 27 de mayo de 2024 y publicada en el Diario Oficial el **11 de marzo de 2025**, se titula simplemente **«Operaciones de aeronaves pilotadas a distancia (RPAS) sobre áreas pobladas»** ([vLex, texto de la resolución](https://vlex.cl/vid/resolucion-num-1033-exenta-1073913272)).

En esa edición, «asuntos de interés público» pasó a ser una **definición** dentro del Capítulo A (151.001), no el ámbito del título. Su definición incluye el «cumplimiento de las obligaciones legales de organismos de la Administración del Estado» y «actividades de apoyo en casos de desastres o emergencias».

**Esto les sirve estratégicamente.** Una misión de monitoreo atmosférico ejecutada en el marco de la fiscalización del PPDA encaja en «cumplimiento de obligaciones legales de organismos de la Administración del Estado». Argumenten la calificación de interés público de su operación citando esa definición: justifica el escenario regulatorio completo del proyecto.

La norma también define **Certificado Especial de Operación (CEO)**, por el cual se autoriza a una institución o empresa a realizar determinadas operaciones aéreas sin fines de lucro, públicas o privadas. Es probablemente la figura que corresponde a su caso de uso, no el AOC comercial. Verifíquenlo en el texto completo.

### Qué deben verificar directamente en el PDF de la DGAC

No pude acceder al articulado completo (está tras pago en vLex y el PDF que ustedes citan corresponde a la edición anterior). Antes de entregar, confirmen en el documento oficial de la DGAC y **citen número de sección, no solo la norma**:

- El artículo que fija la altura máxima de 120 m / 400 ft AGL.
- El artículo que fija la distancia VLOS máxima y las condiciones de BVLOS.
- Los mínimos VMC (visibilidad de 1.000 m) y las condiciones de vuelo nocturno.
- La sección 151.103 que citan en S2: verifiquen que la numeración sigue vigente en la tercera edición.

Además, revisen si para operaciones **fuera** de áreas pobladas aplica la DAN 91 en lugar de la DAN 151. Buena parte de su red de vuelo es costera y rural; si el régimen cambia según el tramo, es un hallazgo relevante para el ruteo y da pie a una capa nueva: régimen normativo por arista.

### Dato que deben corregir sobre la aeronave

Su S6 fija el DJI Matrice 350 RTK con resistencia al viento de 12 m/s. Verifíquenlo en la ficha oficial vigente al momento de entregar ([DJI Enterprise](https://enterprise.dji.com/matrice-350-rtk/specs)), porque el modelo fue sucedido por el Matrice 400 y las especificaciones publicadas cambian. Si el dato ya no está disponible públicamente, declárenlo como supuesto del equipo con la fecha de consulta.

## Escala espacial: hasta dónde medir y qué tan ancha es una pluma

El feedback pregunta cuál es el radio de una zona de contaminación. La respuesta correcta para el paper: **no es un círculo**, y hay tres formas legítimas de acotarla.

### 1. Escala de afectación documentada: 10 km y anillos

Los estudios de suelo de esta bahía usaron un diseño por anillos que ustedes pueden adoptar directamente: muestras compuestas tomadas aleatoriamente en zonas de **2, 4, 6, 8 y 10 km** desde la fundición de cobre ([Aponte et al., *Science of the Total Environment* 779:146423, 2021](https://repositorio.uoh.cl/handle/611/492?show=full)).

Evidencia complementaria sobre el gradiente:

| Hallazgo | Dato | Fuente |
| --- | --- | --- |
| El Cu y la acidez del suelo son mayores cerca del complejo **y en la dirección de los vientos dominantes** | Distribución por kriging universal | [González et al., *J. Soil Sci. Plant Nutr.* 14(4):943–953, 2014](https://investigadores.anid.cl/es/public_search/work?id=288134) |
| Cu, As y Pb correlacionados entre sí: apuntan a la fundición como fuente común; Zn no | 77 %, 32 % y 35 % del área con Cu, As y Pb sobre nivel de fondo; Zn solo 6 % | [Tapia-Gatica et al., *Environmental Pollution* 113488, 2019](https://repository.rudn.ru/en/records/article/record/56479) |
| Concentraciones de fondo en estos suelos | Cu 100, As 16, Pb 35, Zn 122 mg/kg (245 muestras de suelo superficial) | Tapia-Gatica et al., 2019 |
| El SO₂ se dispersa más lejos que el MP con Cu | El SO₂ es más pequeño que el material particulado que contiene cobre, por lo que se dispersa a mayores distancias sin depositarse | González et al., 2014 |

Ese último punto es fino y vale la pena usarlo: **distintos contaminantes tienen distinta escala espacial**. Un diseño de muestreo que trate SO₂ y MP con el mismo radio está mal planteado.

### 2. Radio administrativo: los 2 km de la norma chilena

Para que una estación se califique como de representatividad poblacional, la SMA verifica entre otras cosas que esté **emplazada en un área urbana habitada en un radio de 2 kilómetros**, conforme al D.S. 59/1998 MINSEGPRES (MP10) y al D.S. 12/2011 MMA (MP2,5), junto con el reglamento de estaciones D.S. 61/2008 modificado por D.S. 30/2009 del MINSAL ([ejemplo de informe de evaluación SMA](https://snifa.sma.gob.cl/General/Descargar/1104212443)).

Úsenlo así en el paper: es un **radio administrativo de representatividad**, no una escala física de dispersión. Sirve como referencia oficial para decir «qué área representa una estación», y por contraste muestra que todo lo que está fuera de esos 2 km queda sin representación directa. Ahí entra el dron.

### 3. Ancho real de la pluma según estabilidad

La pluma es una franja alargada en la dirección del viento, no un círculo. Su ancho se estima con las curvas de dispersión de Pasquill-Gifford en la formulación de Briggs para terreno abierto:

```latex
\sigma_y(x) = \frac{a\,x}{\sqrt{1 + 0{,}0001\,x}}
```

con x en metros y el coeficiente a según clase de estabilidad: A ≈ 0,22; B ≈ 0,16; C ≈ 0,11; D ≈ 0,08; E ≈ 0,06; F ≈ 0,04. El ancho visible se toma como 4σy.

| Clase de estabilidad | Momento típico en la bahía | σy a 2 km | Ancho ≈ 4σy |
| --- | --- | --- | --- |
| F (muy estable) | Madrugada, inversión | ≈ 73 m | ≈ 290 m |
| D (neutra) | Transición, cielo cubierto, viento | ≈ 146 m | ≈ 585 m |
| A (muy inestable) | Mediodía despejado | ≈ 402 m | ≈ 1,6 km |

Estos valores reproducen las cifras del feedback (≈300 m en madrugada, ≈600 m neutra, > 1,5 km al mediodía). **Decláren­los explícitamente como estimación de planificación**, no como modelo de dispersión: el paso siguiente sería una pluma gaussiana o AERMOD/CALPUFF con meteorología horaria.

Este es el número que conecta con el tiempo de respuesta del sensor: una pluma de 290 m cruzada a 15 m/s dura 19 segundos, menos que el t90 de un sensor electroquímico típico.

### 4. Alternativa empírica: variograma

Una tercera vía, que es la más defendible metodológicamente y que pueden ejecutar con datos que ya existen: calcular el **variograma** de las series de SINCA entre estaciones. El rango del variograma da la distancia a la que dos puntos dejan de estar correlacionados, es decir, la escala real de la contaminación en esta bahía. Es exactamente la técnica geoestadística que González et al. (2014) aplicaron a los suelos de Puchuncaví. Con 10 estaciones y varios años de datos horarios es un cálculo factible y le daría al paper un resultado propio.

### Alcance del UAV: cómo derivar el límite

Con S6 (39,6 km de autonomía operacional a 15 m/s con 20 % de reserva), si se reserva un tiempo T de muestreo en sitio:

```latex
R_{\max} = \frac{39{,}6\ \text{km} - v\,T}{2}
```

Con T = 20 min a velocidad reducida, R\_max ≈ 10,5 km de longitud de ruta (no distancia en línea recta). Eso deja la estación SINCA de Puchuncaví (14,41 km por el grafo) **fuera de alcance operacional**, lo que hay que declarar en vez de presentarla como misión viable.

Ajuste por viento que conviene incluir: con componente en contra de 6 m/s en un tramo, la velocidad respecto a tierra baja de 15 a 9 m/s y el tiempo de ese tramo crece \~67 %. Por eso el alcance debe recalcularse en la planificación previa de cada misión, no fijarse una vez.

## Metadata reconsiderada

Sus cinco capas actuales responden a «¿puedo volar seguro?». Falta la mitad que responde «¿sirve el dato que voy a tomar?». Esta es la tabla que reemplaza a su Tabla 6.

### Capas actuales, rol revisado

| Capa | Rol actual en el informe | Rol que debe tener |
| --- | --- | --- |
| Densidad censal INE 2017 | Penaliza riesgo en tierra (SORA GRC) | Igual. Agregar que también identifica **receptores expuestos**: el valor de medir ahí no es solo el riesgo de volar ahí |
| Obstáculos OSM | Bloquea/penaliza colisión | Igual, **pero** reclasificar la chimenea de Codelco: obstáculo sí, fuente de fundición no |
| Relieve SRTM | Techo legal + consumo energético | Agregar tercera función: el terreno condiciona el desarrollo de la **capa límite interna** tierra adentro |
| Cobertura celular C2 | Penaliza sombra de telemetría | Igual |
| Calidad del aire SINCA | Recompensa R(d) para priorizar destino | Igual, y es el **punto de co-localización** para validar el sensor de a bordo contra una referencia |

### Capas nuevas que el feedback exige

| Capa nueva | Fuente | Para qué sirve | Dificultad |
| --- | --- | --- | --- |
| **Altura de capa de mezcla** | Open-Meteo `boundary_layer_height` (GFS) | Decide la cota de muestreo; sin ella el dato es ambiguo | Baja: un parámetro más en una llamada que ya hacen |
| **Catastro de fuentes con su firma química** | Inventario SEREMI 2025 (tablas 2–8) | Permite atribución: qué contaminante se espera en cada destino | Baja: son 19 instalaciones con cifras publicadas |
| **Anillos de distancia (2–10 km)** | `ST_Buffer` desde el centroide del complejo | Diseño de muestreo comparable con la literatura de suelos | Baja |
| **Sector a sotavento por fuente** | Viento Open-Meteo + azimut calculado | Define a qué destinos tiene sentido ir en esa hora | Media: es geometría, no dispersión |
| **Precipitación reciente** | Open-Meteo | Condición de scavenging; metadato de validez | Baja |
| **Oleaje / brisa marina** | Open-Meteo Marine API | Riesgo de aerosol marino sesgando MP | Media |
| **Buques fondeados** | AIS | Riesgo de atribución errónea | Alta: requiere fuente AIS |
| **Régimen normativo por arista** | Polígonos de área poblada vs. rural | Determina si aplica DAN 151 o DAN 91 en ese tramo | Media |

### Estructura de datos sugerida

Agreguen una tabla que capture el **contexto de cada muestra**, porque es lo que convierte un dato en un dato atribuible:

```sql
CREATE TABLE sample_context (
    id                  serial PRIMARY KEY,
    node_id             integer REFERENCES infra_node (id),
    sampled_at          timestamptz NOT NULL,
    altitude_agl_m      double precision NOT NULL,
    mixing_height_m     double precision,          -- Open-Meteo boundary_layer_height
    z_over_hmix         double precision GENERATED ALWAYS AS
                        (altitude_agl_m / NULLIF(mixing_height_m, 0)) STORED,
    wind_dir_deg        double precision,
    wind_speed_ms       double precision,
    rh_pct              double precision,
    visibility_m        double precision,
    precip_last_6h_mm   double precision,
    fire_upwind         boolean DEFAULT false,     -- FIRMS en sector de barlovento
    vessel_upwind       boolean DEFAULT false,     -- AIS en sector de barlovento
    stability_class     char(1),                   -- A..F (Pasquill)
    validity_flag       text                       -- 'valido' | 'sesgo_hr' | 'confusor_humo' | ...
);
```

Esa tabla sola justifica la sección de metadata reformulada y es una contribución concreta y defendible: **no están midiendo contaminación, están construyendo la infraestructura que hace que una medición con dron sea atribuible.**

### Cómo calcular el sector a sotavento en PostGIS

El mapa que les mostró el profesor usa una regla geométrica simple: dirección del viento más un abanico de 15° a 40° según la velocidad. Se implementa así:

```sql
-- Sector a sotavento de una fuente, hasta 8 km, abanico +/- semiangulo
SELECT f.code,
       ST_Intersection(
         ST_Buffer(f.geom::geography, 8000)::geometry,
         ST_MakePolygon(ST_MakeLine(ARRAY[
           f.geom,
           ST_Project(f.geom::geography, 8000, radians(:wind_to_deg - :semiangle))::geometry,
           ST_Project(f.geom::geography, 8000, radians(:wind_to_deg))::geometry,
           ST_Project(f.geom::geography, 8000, radians(:wind_to_deg + :semiangle))::geometry,
           f.geom]))
       ) AS sector_sotavento
FROM infra_node f
WHERE f.category = 'source';
```

Donde `wind_to_deg` es la dirección **hacia donde va** el viento (dirección meteorológica + 180°) y `semiangle` va de 15° con viento fuerte a 40° con viento débil. Declárenlo explícitamente como regla de planificación geométrica, no como modelo de dispersión: esa es la advertencia que el propio profesor pidió incluir.

## Referencias nuevas, listas para pegar

Todas verificadas contra la fuente enlazada en este dossier. Péguenlas en su `thebibliography`.

```latex
% --- Contexto y fuentes emisoras ---
\bibitem{inventario2025} Secretaría Regional Ministerial del Medio Ambiente de Valparaíso. (2026). \textit{Informe inventario de emisiones año 2025 en el marco de los artículos 32 y 52 del D.S. N°105/2018 del Ministerio del Medio Ambiente}. Santiago: Gobierno de Chile. Disponible en: \url{https://ppda.mma.gob.cl/wp-content/uploads/2026/05/Informe-de-emisiones-correspondiente-al-ano-2025-1.pdf}.

\bibitem{ds39_2023} Ministerio del Medio Ambiente [MMA]. (2024). \textit{Decreto Supremo N.º 39, de 2023: Modifica el artículo 47 del Decreto Supremo N.º 105, de 2018}. Diario Oficial, 18 de marzo de 2024. Disponible en: \url{https://ppda.mma.gob.cl/wp-content/uploads/2024/03/D.S.-39-2023-modifica-art-47-PPDA-publicado-DO.pdf}.

\bibitem{cierre_ventanas} Superintendencia del Medio Ambiente [SMA]. (2023). \textit{Expediente de fiscalización ambiental: cese de operación de la Fundición Ventanas y su planta de ácido, 31 de mayo de 2023}. SNIFA. Disponible en: \url{https://snifa.sma.gob.cl/General/Descargar/1104418388}.

\bibitem{quintero_energia} La Tercera / Pulso. (2025, 29 de marzo). \textit{Los nuevos dueños pagaron solo US\$ 5 millones a AES por el complejo termoeléctrico Ventanas}. Disponible en: \url{https://www.latercera.com/pulso/noticia/los-nuevos-duenos-pagaron-solo-us-5-millones-a-aes-por-el-complejo-termoelectrico-ventanas/}.

\bibitem{ambiosis} AMBIOSIS S.A. (2024). \textit{Consultoría para la estimación de las emisiones producidas por las embarcaciones marítimas en la Bahía de Quintero}. Informe final preparado para el Ministerio del Medio Ambiente. Disponible en: \url{https://pras.mma.gob.cl/wp-content/uploads/2025/01/INFORME-FINAL-4.-Accion-Quintero-Puchuncavi-2023.pdf}.

% --- Red de monitoreo ---
\bibitem{red_monitoreo} Ministerio del Medio Ambiente [MMA]. (2025). \textit{Resolución Exenta N.º 2.607: Modifica Resolución N.º 222 exenta, de 2023, que establece las acciones para implementar la nueva red de monitoreo de calidad del aire en las comunas de Concón, Quintero y Puchuncaví}. Diario Oficial, 4 de junio de 2025. Disponible en: \url{https://www.diariooficial.interior.gob.cl/publicaciones/2025/06/04/44165/01/2653860.pdf}.

\bibitem{sma_emrp} Superintendencia del Medio Ambiente [SMA]. \textit{Informe de evaluación de representatividad poblacional de estaciones de monitoreo (criterio de área urbana habitada en un radio de 2 km)}. SNIFA. Disponible en: \url{https://snifa.sma.gob.cl/General/Descargar/1104212443}.

% --- Física atmosférica local ---
\bibitem{seguel2023} Seguel, R. J., Garreaud, R., Muñoz, R., Bozkurt, D., Gallardo, L., Opazo, C., Jorquera, H., Castillo, L., \& Menares, C. (2023). Volatile organic compounds measured by proton transfer reaction mass spectrometry over the complex terrain of Quintero Bay, Central Chile. \textit{Environmental Pollution}, 330, 121759. doi: \url{https://doi.org/10.1016/j.envpol.2023.121759}.

\bibitem{araya2024} Araya, R. T., et al. (2024). Long-term assessment and acute air pollution events in a mega-industrial area in Central Chile. \textit{Urban Climate}, 55, 101880. doi: \url{https://doi.org/10.1016/j.uclim.2024.101880}.

\bibitem{cr2_policy} Seguel, R. (2023). \textit{Los desafíos ante la contaminación atmosférica en la bahía de Quintero-Puchuncaví} (Policy Brief N.º 14). Centro de Ciencia del Clima y la Resiliencia (CR)2. Disponible en: \url{https://www.cr2.cl/wp-content/uploads/2023/12/Policy-brief-Los-desafios-ante-la-contaminacion-atmosferica-en-la-bahia-de-Quintero-Puchuncavi.pdf}.

% --- Escala espacial y gradientes ---
\bibitem{aponte2021} Aponte, H., Mondaca, P., Santander, C., Meier, S., Paolini, J., Butler, B., Rojas, C., Diez, M. C., \& Cornejo, P. (2021). Enzyme activities and microbial functional diversity in metal(loid) contaminated soils near to a copper smelter. \textit{Science of the Total Environment}, 779, 146423. doi: \url{https://doi.org/10.1016/j.scitotenv.2021.146423}.

\bibitem{gonzalez2014} González, I., Neaman, A., Rubio, P., \& Cortés, A. (2014). Spatial distribution of copper and pH in soils affected by intensive industrial activities in Puchuncaví and Quintero, central Chile. \textit{Journal of Soil Science and Plant Nutrition}, 14(4), 943--953. doi: \url{https://doi.org/10.4067/S0718-95162014005000074}.

\bibitem{tapia2019} Tapia-Gatica, J., González-Miranda, I., Salgado, E., Bravo, M. A., Tessini, C., Dovletyarova, E. A., Paltseva, A. A., \& Neaman, A. (2019). Advanced determination of the spatial gradient of human health risk and ecological risk from exposure to As, Cu, Pb, and Zn in soils near the Ventanas Industrial Complex (Puchuncaví, Chile). \textit{Environmental Pollution}, 113488. doi: \url{https://doi.org/10.1016/j.envpol.2019.113488}.

\bibitem{gorena2023} Gorena, T., Sandoval, F., Fadic, X., et al. (2023). Comparison of trace element deposition in \textit{Cupressus macrocarpa} leaves and soils from a high-pollution area in the Puchuncaví Valley (Chile) using a biomonitoring method. \textit{Atmosphere}, 14(5), 893. doi: \url{https://doi.org/10.3390/atmos14050893}.

% --- Amenazas a la validez de la medicion ---
\bibitem{crilley2018} Crilley, L. R., Shaw, M., Pound, R., Kramer, L. J., Price, R., Young, S., Lewis, A. C., \& Pope, F. D. (2018). Evaluation of a low-cost optical particle counter (Alphasense OPC-N2) for ambient air monitoring. \textit{Atmospheric Measurement Techniques}, 11, 709--720. Véase también: Developing a relative humidity correction for low-cost sensors measuring ambient particulate matter. \textit{Sensors}, 18(9), 2790. doi: \url{https://doi.org/10.3390/s18092790}.

\bibitem{badura2018} Badura, M., Batog, P., Drzeniecka-Osiadacz, A., \& Modzel, P. (2018). Evaluation of low-cost sensors for ambient PM2.5 monitoring. \textit{Journal of Sensors}, 2018, 5096540. doi: \url{https://doi.org/10.1155/2018/5096540}.

\bibitem{amt_kappa} Malings, C., et al. (2024). Towards a hygroscopic growth calibration for low-cost PM2.5 sensors. \textit{Atmospheric Measurement Techniques}, 17, 1051--1068. doi: \url{https://doi.org/10.5194/amt-17-1051-2024}.

\bibitem{galle2021} Galle, B., Arellano, S., Bobrowski, N., et al. (2021). A multi-purpose, multi-rotor drone system for long-range and high-altitude volcanic gas plume measurements. \textit{Atmospheric Measurement Techniques}, 14, 4255--4277. doi: \url{https://doi.org/10.5194/amt-14-4255-2021}.

\bibitem{lluvia_puchuncavi} Lobos, S., et al. (2000). Copper and selenium in rainwater, soils and alfalfa from agricultural ecosystems of Valparaíso region, Chile. \textit{Boletín de la Sociedad Chilena de Química}. Disponible en: \url{https://hal-univ-pau.archives-ouvertes.fr/hal-00291432}.

% --- Normativa aeronautica actualizada ---
\bibitem{dan151} Dirección General de Aeronáutica Civil [DGAC]. (2024). \textit{DAN 151: Operaciones de aeronaves pilotadas a distancia (RPAS) sobre áreas pobladas} (3.ª ed.). Aprobada por Resolución Exenta N.º 04/3/0089/1033 del 27 de mayo de 2024, publicada en el Diario Oficial el 11 de marzo de 2025. Santiago: Gobierno de Chile.

% --- Correccion de la referencia de Kosior ---
\bibitem{kosior} Kosior, M., Przysta\l{}ka, P., \& Panfil, W. (2024). Adaptive path planning for UAV-based pollution sampling. \textit{Applied Sciences}, 14(24), 12065. doi: \url{https://doi.org/10.3390/app142412065}.
```

### Cuatro cosas que quedaron sin verificar

No las usen sin confirmar primero:

1. **La torre de Puchuncaví que mide hasta 40 m.** No hallé fuente pública.
2. **El DOI exacto de Araya et al. (2024)**: verifíquenlo en ScienceDirect, lo reconstruí por patrón.
3. **La existencia de una estación SINCA «Campiche»**: no aparece en los listados oficiales.
4. **El articulado numerado de la DAN 151 tercera edición**: necesitan el PDF oficial de la DGAC, no la edición 2024 que citan hoy.
