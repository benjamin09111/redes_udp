\documentclass[letterpaper,12pt]{article}
\usepackage[paperheight=27.94cm,paperwidth=21.59cm,bindingoffset=0in,left=3cm,right=2.0cm,top=3.5cm,bottom=2.5cm,headheight=40pt,headsep=1.0\baselineskip]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-tabla,es-noshorthands]{babel}
% Neutralizar conflicto de babel spanish con el signo de porcentaje en formulas y tablas
\makeatletter
\def\es@sppercent{}
\makeatother
\usepackage{graphicx}
\usepackage{float}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{indentfirst}
\usepackage{fancyhdr}
\usepackage{listings}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,babel}
\usepackage[hyphens]{url}
\usepackage[hidelinks]{hyperref}

\setlength{\parindent}{1cm}
\renewcommand{\arraystretch}{1.2}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\setlength{\emergencystretch}{3em}

% Ancho del numero de seccion en el indice
\makeatletter
\renewcommand*\l@section{\@dottedtocline{1}{0em}{2.3em}}
\renewcommand*\l@subsection{\@dottedtocline{2}{2.3em}{3.2em}}
\makeatother

% Configuracion de codigo SQL, JSON y bash
\lstset{
basicstyle=\ttfamily\scriptsize,
breaklines=true,
showstringspaces=false,
columns=fullflexible,
frame=single,
literate={á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1 {Ú}{{\'U}}1 {Ó}{{\'O}}1 {É}{{\'E}}1 {Á}{{\'A}}1 {Í}{{\'I}}1 {ñ}{{\~n}}1
}

\newcommand{\imagen}[2]{%
\IfFileExists{#2}{\includegraphics[width=#1]{#2}}%
{\IfFileExists{images/#2}{\includegraphics[width=#1]{images/#2}}%
{\IfFileExists{bd/#2}{\includegraphics[width=#1]{bd/#2}}%
{\fbox{\parbox[c][3cm][c]{\dimexpr#1-2\fboxsep-2\fboxrule\relax}{\centering\small Imagen de referencia:\\\texttt{\detokenize{#2}}}}}}}}

\pagestyle{fancy}
\fancyhf{}
\lhead{\IfFileExists{images/Logo FIC.png}{\includegraphics[width=40mm]{images/Logo FIC.png}}{Universidad Diego Portales}}
\rhead{\small Algoritmos de Ruteo y Redes Resilientes}
\cfoot{\thepage}

\begin{document}

% ============================== PORTADA ==============================
\begin{titlepage}
\centering
\IfFileExists{images/Escudo UDP.png}{\includegraphics[width=0.15\textwidth]{images/Escudo UDP.png}\par}{}
\vspace{1cm}
{\bfseries\Huge Universidad Diego Portales \par}
\vspace{1cm}
{\scshape\Large Facultad de Ingeniería y Ciencias \par}
\vspace{0.4cm}
{\scshape\normalsize Escuela de Informática y Telecomunicaciones \par}
\vspace{2.5cm}
{\scshape\LARGE Ruteo Resiliente de UAV para el Muestreo de Contaminación Atmosférica en la Bahía de Quintero y Puchuncaví \par}
\vspace{2.5cm}
{\normalsize \textbf{Profesor:} Nicolás Boettcher \\ }
\vspace{0.7cm}
{\normalsize \textbf{Curso:} Algoritmos de Ruteo y Redes Resilientes (CIT3435) \\}
\vspace{0.7cm}
{\normalsize \textbf{Grupo 09:} \\ Benjamín Aceituno \\ Aldo Morales \\ Benjamín Morales \\ Benjamín Polanco \par}
\vfill
{\normalsize Octubre de 2026 \par}
\end{titlepage}

\newpage

% ============================== RESUMEN ==============================
\section\*{Resumen Ejecutivo}
\addcontentsline{toc}{section}{Resumen Ejecutivo}

El presente trabajo documenta el diseño, implementación y validación experimental de una plataforma de modelado geoespacial y enrutamiento resiliente para Vehículos Aéreos No Tripulados (UAV) en la Bahía de Quintero y Puchuncaví. Ante la limitación del monitoreo superficial tradicional para registrar la dispersión de plumas industriales confinadas en altura por inversión térmica, se construyó una infraestructura geoespacial automatizada y reproducible mediante contenedores Docker. El sistema integra una red aérea de $237$ nodos y $633$ aristas conexas ($K=4$ vecinos y dos aristas puente), junto a cinco capas de metadatos operacionales (calidad del aire SINCA como prioridad de muestreo, topografía SRTM por arista, densidad censal INE 2017, cobertura celular C2 y catastro de obstáculos verticales) y cuatro capas de amenazas operacionales dinámicas (incendios NASA FIRMS, separación frente a tráfico aéreo tripulado OpenSky ADS-B, viento crítico a $120\text{ m}$ AGL Open-Meteo y niebla costera/visibilidad Open-Meteo), almacenadas en PostgreSQL 16 con PostGIS 3.5 y pgRouting 3.8.

Sobre esta base, se calculó la ruta de menor longitud métrica mediante el algoritmo de Dijkstra (\texttt{pgr\_dijkstra}) como línea base de referencia. Los resultados confirman la conexidad global del espacio aéreo y evidencian numéricamente la condición de peor caso del camino mínimo tradicional: la ruta hacia la estación SINCA de Puchuncaví ($14{,}41\text{ km}$, $22$ tramos) sobrevuela $0{,}79\text{ km}$ sobre manzanas con densidad superior a $2.500\text{ hab/km}^2$ y discurre durante $7{,}58\text{ km}$ ($52{,}6$\,\% del trayecto) fuera de la cobertura celular C2, con un desnivel orográfico de $+67{,}0\text{ m}$ y operando en régimen BVLOS que exige autorización especial de la DGAC según la norma DAN 151. La integridad de los datos, la especificación GeoJSON RFC 7946 y el esquema de base de datos fueron validados mediante una suite de $57$ pruebas automatizadas ejecutadas sin fallas.

\vspace{0.5cm}
\noindent \textbf{Palabras clave:} Vehículos Aéreos No Tripulados (UAV), pgRouting, PostGIS, Calidad del Aire, Algoritmo de Dijkstra, Redes Resilientes, Bahía de Quintero.

\newpage
\tableofcontents
\newpage

% ============================== 1 ==============================
\section{Introducción y Contexto Territorial}
\label{sec:introduccion}

El litoral y cordón industrial de la Bahía de Quintero, Ventanas y Puchuncaví (Región de Valparaíso, Chile) constituye uno de los territorios de mayor vulnerabilidad socio-ambiental del país. Declarada formalmente como zona saturada por material particulado respirable ($\text{MP}_{10}$ y $\text{MP}_{2{,}5}$) y dióxido de azufre ($\text{SO}_2$), la cuenca se rige bajo las directrices del Plan de Prevención y Descontaminación Atmosférica (PPDA) para las comunas de Concón, Quintero y Puchuncaví, promulgado mediante el Decreto Supremo N.º 105/2018 del Ministerio del Medio Ambiente (MMA) y modificado en su artículo 47 por el D.S. N.º 39/2023 MMA \cite{ppda_concon}. En una estrecha franja costera de aproximadamente $15\text{ km}$, coexisten núcleos urbanos consolidados, asentamientos rurales, caletas de pescadores, establecimientos hospitalarios y recintos escolares con un parque industrial que concentra generación termoeléctrica a carbón, almacenamiento y distribución de hidrocarburos, procesamiento de gas natural licuado (GNL), plantas químicas de granel líquido y terminales portuarios mecanizados.

\subsection{El Escenario Territorial y la Transformación Industrial Reciente}
\label{subsec:contexto_actualizado}

La configuración operacional del cordón industrial ha experimentado profundas transformaciones entre los años 2023 y 2026, las cuales redefinen sustancialmente las fuentes activas y los focos de emisión en el área de estudio:

\begin{enumerate}
\item \textbf{Cese de operaciones de la Fundición Ventanas (Codelco):} Tras 58 años ininterrumpidos de faena pirometalúrgica, la Fundición Ventanas de la Corporación Nacional del Cobre de Chile (Codelco) cesó definitivamente la operación de sus hornos de fusión y su planta de ácido sulfúrico el 31 de mayo de 2023, en cumplimiento de la Resolución Exenta N.º 844/2023 del Servicio Nacional de Geología y Minería (Sernageomin). Si bien la fundición fue históricamente la principal fuente emisora puntual de $\text{SO}_2$ y material particulado rico en metales pesados (cobre, arsénico y plomo), \textbf{su chimenea de $152\text{ m}$ de altura física permanece en pie como el obstáculo vertical más prominente para la navegación aérea en la bahía}. Asimismo, las instalaciones anexas continúan activas, albergando la refinería electrolítica y los hornos de refino a fuego (RAF), los cuales mantienen actividad industrial y tránsito térmico.
\item \textbf{Transición del Complejo Termoeléctrico Ventanas:} El complejo termoeléctrico a carbón emplazado en la bahía fue transferido en su administración por AES Andes hacia Inversiones Latin America Power / Guacolda Energía (operando como Nueva Ventanas). Bajo el marco del cronograma nacional de descarbonización, las unidades Ventanas 1 y Ventanas 2 fueron retiradas de servicio, manteniéndose operativas las unidades Ventanas 3 (Nueva Ventanas) y Ventanas 4 (Campiche), esta última dotada de una chimenea de $140\text{ m}$ de altitud física y sistemas de desulfuración (FGD) para control de efluentes gaseosos.
\item \textbf{Fuentes marítimas móviles y buques a la gira:} Un componente crítico omitido sistemáticamente por la red de monitoreo superficial corresponde a la rada de buques mercantes, graneleros, quimiqueros y petroleros que permanecen fondeados a la gira en el cuerpo de agua de la bahía. Estas embarcaciones operan generadores auxiliares diésel de combustión continua para mantener sus sistemas de refrigeración y bombeo, descargando toneladas de $\text{SO}_2$, óxidos de nitrógeno ($\text{NO}_x$), compuestos orgánicos volátiles (COVs) y material particulado fino en la capa marina superficial inmediatamente a barlovento de los centros urbanos de Quintero.
\end{enumerate}

\noindent \textbf{Disparidad territorial: Quintero no es equivalente a Ventanas.}
Uno de los errores conceptuales más frecuentes en el diagnóstico territorial de la bahía es asumir una homogeneidad en los contaminantes presentes en ambas riberas. La evidencia geofísica y catastral demuestra una rigurosa diferenciación de fuentes y receptores:
\begin{itemize}
\item \textbf{Sector Norte (Ventanas y La Greda):} Yuxtapuesto directamente al complejo metalúrgico, termoeléctrico y químico. Constituye el foco histórico de emisiones de $\text{SO}_2$, metales pesados en polvo y cenizas volantes.
\item \textbf{Sector Sur (Península de Quintero y Loncura):} Emplazado a sotavento del terminal marítimo de hidrocarburos de ENAP, de la planta de regasificación de GNL Quintero, de depósitos de asfalto y de la zona de atraque de buques. Su perfil de emisión está dominado por hidrocarburos volátiles, COVs no normados, sulfuro de hidrógeno ($\text{H}_2\text{S}$) y $\text{NO}_x$.
\end{itemize}

\noindent \textbf{Por qué medir en altura y no solo en suelo: Justificación técnico-normativa.}
El D.S. N.º 105/2018 MMA, modificado por el D.S. N.º 39/2023 en su artículo 47, impone exigencias de monitoreo continuo de material particulado y variables meteorológicas para la evaluación de planes operacionales de contingencia. Sin embargo, basar la vigilancia exclusivamente en cabinas terrestres del Sistema de Información Nacional de Calidad del Aire (SINCA) a $3\text{--}4\text{ m}$ sobre el suelo adolece de un desfase físico insalvable: \textbf{las descargas de chimeneas altas quedan atrapadas en estratos superiores durante la noche, transportándose en capas laminares que solo alcanzan el suelo cuando la radiación solar induce convección térmica durante la mañana}. Medir en superficie implica registrar el impacto cuando el tóxico ya entró en contacto con la población. El muestreo aéreo con UAVs a cotas de $80\text{--}120\text{ m}$ AGL permite interceptar la pluma industrial de forma anticipada en la columna troposférica, cerrando la brecha entre la predicción teórica y el impacto en tierra.

\subsection{El Mecanismo Físico Vertical y el Reconocimiento del Estado Chileno}
\label{subsec:mecanismo_vertical}

La dinámica de dispersión atmosférica en el litoral central de Chile está gobernada por fenómenos meteorológicos de meso y microescala reconocidos explícitamente en los instrumentos regulatorios de la República de Chile. Las resoluciones oficiales de la Superintendencia del Medio Ambiente (SMA) que aprueban los planes operacionales de las empresas del cordón industrial —como la Resolución Exenta N.º 05080/2025 relativa al Terminal Marítimo de ENAP en Quintero \cite{sma_enap}— fundamentan sus exigencias citando directamente el Capítulo I del PPDA (D.S. N.º 105/2018 MMA, modificado por D.S. N.º 39/2023) \cite{ppda_concon}.

En dicho marco legal, la autoridad ambiental formaliza que los episodios críticos de contaminación se originan por la interacción de dos fenómenos verticales determinantes:
\begin{enumerate}
\item \textbf{Inversión térmica marina de subsidencia:} Fenómeno donde una masa de aire cálido descendente asociada a la rama oriental del Anticiclón del Pacífico Suroriental actúa como una cubierta térmica impermeable que inhibe drásticamente la mezcla vertical. La base de esta inversión se ubica frecuentemente entre los $80$ y $250\text{ m}$ sobre el nivel del mar durante la noche y primeras horas del día, atrapando los penachos industriales emitidos por chimeneas de gran elevación en un estrato confinado.
\item \textbf{Fenómeno de ``fumigación costera'':} Proceso inducido por el calentamiento solar matutino de la superficie continental. Al entrar la brisa marina sobre tierra caliente, se desarrolla una Capa Límite Interna Térmica (TIBL, \textit{Thermal Internal Boundary Layer}) que crece progresivamente con la distancia desde la línea de costa. Cuando la frontera superior de esta capa convectiva intercepta la pluma de contaminantes suspendida en altura, la turbulencia turbillonaria arrastra violentamente los contaminantes hacia el suelo de manera súbita, generando alzas extremas de concentración en superficie sobre áreas residenciales en intervalos de pocos minutos.
\end{enumerate}

Por consiguiente, el propio marco normativo y la física de fluidos convergen en un principio fundamental: \textbf{la concentración que impacta en el suelo es una consecuencia tardía de procesos físicos y químicos que ocurren en la columna vertical de la atmósfera}.

\subsection{Evidencia Empírica de la Crisis: Estudios SMA, Brecha Instrumental y Precedentes}
\label{subsec:evidencia_empirica}

La necesidad de caracterizar la columna vertical no constituye una abstracción metodológica, sino una exigencia empírica demostrada por estudios periciales oficiales y antecedentes científicos en la bahía:

\begin{enumerate}
\item \textbf{El estudio oficial SMA / Dictuc (2020) sobre la crisis de agosto de 2018:}
El informe pericial n.º 1535747 de la Superintendencia del Medio Ambiente y Dictuc, titulado \textit{Servicio de modelación de calidad del aire para la zona de Quintero-Puchuncaví} \cite{sma_dictuc}, analizó la crisis ambiental que provocó cientos de consultas médicas por intoxicación aguda entre el 21 y el 23 de agosto de 2018. El estudio constató que durante el evento se estructuró una aguda inversión térmica a aproximadamente $400\text{ m}$ sobre el nivel del suelo, impidiendo por completo la dispersión vertical de los efluentes.

\item \textbf{La brecha instrumental vertical (Radiosondeo a 100 km):}
Para reconstruir el perfil vertical de temperatura, gradiente térmico y vector de viento requerido en la modelación pericial de la crisis de 2018, los investigadores debieron recurrir a los registros de radiosondeo de la estación meteorológica de \textbf{Santo Domingo, ubicada a más de 100 km al sur de Quintero} \cite{sma_dictuc}. La ausencia total de perfiles meteorológicos verticales in situ en la Bahía de Quintero representó una severa incertidumbre analítica, demostrando la urgencia de disponer de vectores de medición atmosférica local en cota baja.

\item \textbf{La desconexión analítica de la red superficial vs. intoxicaciones masivas:}
Durante los días más agudos de la emergencia (21 al 23 de agosto de 2018), la concentración horaria de dióxido de azufre ($\text{SO}_2$) en las cabinas terrestres del SINCA \textbf{nunca excedió la norma primaria horaria de $350\ \mu\text{g/m}^3\text{N}$} \cite{sma_dictuc}. A pesar de ello, cientos de niños y adultos requirieron atención de urgencia por sintomatología neurotóxica. El informe pericial constató que la intoxicación masiva obedeció a mezclas complejas de compuestos orgánicos volátiles (COVs) y derivados de hidrocarburos, advirtiendo taxativamente que en el complejo industrial de Ventanas \textbf{no existía monitoreo continuo ni normado para BTEX (benceno, tolueno, etilbenceno, xilenos), formaldehído (HCHO) ni sulfuro de hidrógeno ($\text{H}_2\text{S}$)} \cite{sma_dictuc,cifuentes}.

\item \textbf{Precedentes de despliegue científico de UAVs en Quintero:}
El uso de aeronaves no tripuladas para resolver este vacío instrumental cuenta con validación previa en el litoral. Investigadores del Centro de Ciencia del Clima y la Resiliencia (CR2, Universidad de Chile) \cite{cr2_campana_2022,cr2_informe} ejecutaron campañas experimentales de medición intensiva en la bahía para capturar compuestos volátiles y registrar perfiles microclimáticos verticales mediante drones acoplados a radiosondeos de baja cota \cite{cr2_informe}.

\item \textbf{Compromiso institucional de fiscalización aérea:}
En junio de 2023, el Ministerio del Medio Ambiente oficializó su estrategia de fortalecimiento de la fiscalización ambiental en Quintero y Puchuncaví, incorporando de manera explícita el uso de sensores acoplados a vehículos aéreos no tripulados \cite{mma_plan_2023,mma_drones}, consolidando a los UAVs como una prioridad técnica reconocida por el regulador.

\item \textbf{Recurrencia de episodios y persistencia de exposición:}
Los eventos de afectación comunitaria persisten en el territorio. En junio de 2022, la estación Quintero registró un pico horario extremo de $\text{SO}_2$ de $1.327\ \mu\text{g/m}^3\text{N}$, cuadruplicando la norma primaria horaria \cite{sma_so2_2022}. Asimismo, durante el año 2023 se suscitaron sucesivas alertas sanitarias con más de 500 atenciones médicas de escolares; los estudios toxicológicos del CR2 vincularon tales episodios a emisiones fugitivas de COVs y gases odoríferos durante transferencias marítimas de combustibles y operaciones industriales \cite{eldesconcierto_2023}.
\end{enumerate}

\subsection{Planteamiento del Problema: La Cadena Lógica y el Enfoque en Enrutamiento Resiliente}
\label{subsec:problema}

Los antecedentes territoriales y meteorológicos expuestos estructuran una \textbf{cadena lógica rigurosa de cinco eslabones}:
\begin{enumerate}
\item Los episodios de contaminación y afectación de salud comunitaria dependen directamente de la estructura física vertical de la atmósfera: la inversión térmica marina atrapa los gases en altura y la fumigación costera los precipita concentrados sobre la población (PPDA \cite{ppda_concon}, SMA \cite{sma_dictuc}).
\item La infraestructura de monitoreo superficial no mide perfiles verticales locales: las modelaciones periciales oficiales debieron extrapolar radiosondeos distantes a $100\text{ km}$ en Santo Domingo \cite{sma_dictuc}.
\item La red de estaciones terrestres en suelo no registra la totalidad del cóctel tóxico en el momento de su dispersión en altura, evidenciando desfases entre mediciones bajo norma e intoxicaciones neurotóxicas masivas \cite{sma_dictuc,cr2_informe}.
\item El despliegue de UAVs con instrumentación ambiental constituye una tecnología viable, comprobada por la academia \cite{cr2_informe} y priorizada por la autoridad ambiental chilena \cite{mma_drones}.
\item \textbf{Para ejecutar misiones de monitoreo sistemáticas y recurrentes, el UAV exige trayectorias de vuelo optimizadas, seguras y resilientes frente a las severas amenazas operacionales y ambientales del entorno.}
\end{enumerate}

\noindent \textbf{Definición del objeto de estudio:} Se establece explícitamente que \textbf{el objetivo central de este trabajo no radica en el desarrollo de transductores químicos de sensado ni en la modelación fluidodinámica computacional (CFD) de la atmósfera}. Los eslabones 1 a 4 demuestran la justificación técnico-científica de \textbf{por qué es imprescindible realizar mediciones aéreas en la Bahía de Quintero y Puchuncaví}. El desafío ingenieril de esta investigación radica estrictamente en el eslabón 5: \textbf{¿Cómo modelar el espacio geográfico y planificar computacionalmente las rutas de un UAV para que intercepte y monitoree la contaminación de forma eficiente, mitigando simultáneamente la exposición a riesgos catastróficos en el aire y en tierra?}

Navegar en el espacio aéreo de Quintero y Puchuncaví impone severas restricciones operacionales que prohíben una navegación ingenua:
\begin{itemize}
\item \textbf{Riesgo a terceros en tierra sobre áreas densamente pobladas:} Sobrevolar núcleos urbanos con densidades censales superiores a $2.500\text{ hab/km}^2$ incrementa críticamente el riesgo intrínseco en tierra (\textit{Ground Risk Class}, GRC) según la metodología internacional SORA de JARUS \cite{sora} y contraviene las restricciones de seguridad pública establecidas en la norma técnica aeronáutica DAN 151 de la DGAC \cite{dan151}.
\item \textbf{Obstáculos verticales industriales severos:} El cordón industrial alberga estructuras físicas de gran cota, destacando la chimenea de la Fundición Ventanas ($152\text{ m}$ AGL), la chimenea de la Termoeléctrica Campiche ($140\text{ m}$ AGL), ductos de $110\text{--}120\text{ m}$ y líneas de transmisión eléctrica de alta tensión ($110/220\text{ kV}$) que cruzan los valles costeros.
\item \textbf{Conflicto de espacio aéreo con aviación tripulada:} Las maniobras de aproximación visual hacia la pista activa del Aeródromo de Quintero (SCER) poseen prioridad de paso absoluta según la reglamentación aeronáutica, exigiendo zonas de resguardo espaciotemporal automáticas.
\item \textbf{Condiciones meteorológicas costeras adversas:} Vientos de componente costera que superan el límite estructural de $12\text{ m/s}$ ($43{,}2\text{ km/h}$) para plataformas estándar de la categoría del DJI Matrice 350 RTK \cite{dji}, bancos densos de niebla y camanchaca marina que reducen la visibilidad horizontal bajo los $1.000\text{ m}$ normativos (anulando las condiciones meteorológicas visuales, VMC), y frentes de cizalladura térmica.
\item \textbf{Régimen operacional BVLOS y marco DGAC:} Cualquier trayectoria que sobrepase la línea de vista visual directa del operador ($\text{VLOS} \le 500\text{ m}$), tal como el trayecto de $14{,}41\text{ km}$ hacia Puchuncaví, califica jurídicamente como operación más allá del alcance visual (\textit{Beyond Visual Line of Sight}, BVLOS), la cual bajo la DAN 151 exige autorización especial de la DGAC y la acreditación de salvaguardas tecnológicas y de gestión de riesgo certificadas.
\end{itemize}

Planificar trayectorias mediante el camino mínimo geodésico tradicional (Dijkstra puro con costo igual a la longitud) desatiende ciegamente estos factores, trazando trayectorias que sobretrazan zonas urbanas densas, cruzan conos de aproximación aérea o intersectan áreas sin enlace de mando y control (C2).

\subsection{Síntesis de Antecedentes, Brechas Identificadas y Enfoque del Proyecto}
\label{subsec:sintesis_brechas}

Para estructurar formalmente el vacío operacional existente en la literatura y en la gestión territorial, la Tabla~\ref{tab:que_existe} sintetiza las iniciativas implementadas en la Bahía de Quintero y Puchuncaví, sus autores institucionales y las brechas técnicas pendientes:

\begin{table}[H]
\centering
\small
\caption{Síntesis comparativa: iniciativas existentes, autores y brechas operacionales pendientes.}
\label{tab:que_existe}
\begin{tabularx}{\linewidth}{p{4.8cm}p{4.2cm}X}
\toprule
\textbf{Iniciativa Existente} & \textbf{Autor / Institución} & \textbf{Brecha Operacional Pendiente} \\
\midrule
Estaciones fijas a nivel de suelo; monitoreo continuo de $\text{SO}_2$ y material particulado & Red oficial del Ministerio del Medio Ambiente (SINCA) \cite{mma_sinca_2021,sinca} & Confinamiento en superficie ($3\text{--}4\text{ m}$); no detectan estratificación vertical ni mezclas complejas de COVs. \\
\addlinespace
Catastro de sensores fijos complementarios en colegios (2022) y perímetros industriales & Superintendencia del Medio Ambiente (SMA) \cite{sma_estrategia_2023} & Red de puntos estacionarios en tierra sin capacidad de muestreo tridimensional ni movilidad adaptativa. \\
\addlinespace
Estudio pericial oficial crisis 2018: inversión a $\approx 400\text{ m}$; perfil tomado de radiosondeo a $100\text{ km}$ & Estudio UC--Dictuc para la Superintendencia del Medio Ambiente \cite{sma_dictuc} & Carencia absoluta de mediciones meteorológicas y de perfiles térmicos verticales in situ en la Bahía de Quintero. \\
\addlinespace
Campaña intensiva con UAVs para perfiles de temperatura y COVs no normados & Centro de Ciencia del Clima y la Resiliencia (CR2), U. de Chile \cite{cr2_informe} & Intervención científica experimental puntual; carece de operación regular, topología de red y planificador de rutas. \\
\addlinespace
Compromiso de incorporar drones con sensores en fiscalización ambiental & Ministerio del Medio Ambiente (MMA) \cite{mma_drones} & Ausencia de una plataforma pública de planificación geoespacial y enrutamiento sistemático resiliente. \\
\addlinespace
Planificación adaptativa de rutas en dos niveles (GPP/LPP) para muestreo con UAV & Kosior, Przystałka y Panfil (2024), Universidad Tecnológica de Silesia \cite{kosior} & Formulado para UAV de ala fija en Żywiec (Polonia); no adaptado a la geografía costera, obstáculos y restricciones de Quintero. \\
\bottomrule
\end{tabularx}
\end{table}

A partir de este análisis sistemático, se formalizan las seis brechas operacionales:
\begin{enumerate}
\item \textbf{Ceguera vertical de la red superficial SINCA \cite{sinca}:} Las cabinas fijas registran la concentración una vez que el contaminante ha alcanzado el nivel de suelo ($3\text{--}4\text{ m}$), perdiendo la oportunidad de capturar la pluma mientras se desplaza confinada en capas superiores de la atmósfera.
\item \textbf{Inmovilidad de los sensores perimetrales de contingencia (SMA) \cite{sma_estrategia_2023}:} Pese a densificar la cobertura en escuelas e industrias, su carácter estático impide rastrear el vector dinámico de avance de la pluma bajo cambios en la dirección del viento.
\item \textbf{Extrapolación de radiosondeos distantes en modelaciones periciales \cite{sma_dictuc}:} Recurrir a datos tomados a $100\text{ km}$ de distancia introduce severas distorsiones en la estimación de la altura de la capa de mezcla ($h_{\text{mix}}$) costera local.
\item \textbf{Falta de recurrencia en ensayos académicos de drones \cite{cr2_informe}:} Si bien las misiones del CR2 demostraron la capacidad de sensar perfiles térmicos y volátiles con aeronaves no tripuladas, constituyeron campañas temporales sin continuidad operativa.
\item \textbf{Inexistencia de un motor de navegación resiliente estatal \cite{mma_drones}:} Las declaraciones gubernamentales sobre drones de fiscalización carecen de una formulación algorítmica documentada para resolver la planificación de vuelo en presencia de amenazas múltiples.
\item \textbf{Desconexión de modelos teóricos internacionales frente al entorno local \cite{kosior}:} La formulación de Kosior et al. (2024) para UAVs de ala fija optimizó trayectorias en terrenos abiertos con criterios de velocidad constante y evasión de obstáculos esparcidos; su arquitectura no contempla la densidad urbana censal, líneas de alta tensión, espacios aéreos circundantes a bases aéreas activas ni microclimas de camanchaca litoral.
\end{enumerate}

\subsection{Dinámica Físico-Química de Dispersión Atmosférica en la Bahía}
\label{subsec:dinamica_dispersion}

La comprensión cuantitativa de los mecanismos de transporte horizontal y vertical en la Bahía de Quintero resulta indispensable para justificar la topología de la red de vuelo y la altura de muestreo:

\subsubsection{Eje Horizontal: Régimen Eólico Bimodal y Diferenciación de Fuentes}
El transporte advectivo de los efluentes se encuentra gobernado por la interacción entre el régimen sinóptico costero y el ciclo térmico local brisa de mar--brisa de tierra:
\begin{enumerate}
\item \textbf{Ciclo diurno (Brisa marina suroeste, SW $\to$ NE):} A partir del mediodía y durante la tarde, el calentamiento de los valles interiores activa un flujo persistente desde el suroeste ($210^\circ\text{--}240^\circ$). Bajo este régimen, las plumas emitidas en el parque industrial de Ventanas son transportadas directamente hacia los valles agrícolas y centros poblados de La Greda, Campiche y Puchuncaví. Esta dirección preferencial explica por qué los estudios geoquímicos de suelos registran los mayores enriquecimientos de cobre ($\text{Cu}$), arsénico ($\text{As}$) y acidez en el cuadrante noreste a sotavento del complejo \cite{gonzalez2014,tapiagatica2020}.
\item \textbf{Ciclo nocturno y de madrugada (Flujo de tierra noreste, NE $\to$ SW):} Durante la noche y primeras horas del amanecer, el enfriamiento continental genera un flujo catabático de terral con componente noreste a este ($030^\circ\text{--}070^\circ$). Este viento desplaza los efluentes en dirección contraria, transportándolos hacia el mar y barriendo la península de Quintero y Loncura.
\item \textbf{Escala espacial diferencial de contaminantes:} Mientras el dióxido de azufre ($\text{SO}_2$) gaseoso posee una tasa de deposición seca relativamente baja y puede transportarse por más de $15\text{--}20\text{ km}$ a sotavento, el material particulado grueso rico en metales sedimenta rápidamente en los primeros $2\text{--}4\text{ km}$ desde las chimeneas \cite{gonzalez2014}. En contraste, las emisiones de hidrocarburos de terminales portuarios y buques fondeados permanecen en la capa superficial marina con escasa dispersión vertical durante la noche.
\end{enumerate}

\subsubsection{Eje Vertical: Inversión Térmica, Altura de Mezcla y Fumigación Costera}
La dimensión vertical determina de manera decisiva la presencia o ausencia de impacto en superficie:
\begin{enumerate}
\item \textbf{Estratificación nocturna desacoplada:} Durante la madrugada, la superficie terrestre se enfría intensamente por emisión de onda larga, induciendo una capa de inversión térmica superficial muy baja ($h_{\text{mix}} < 100\text{ m}$). Las chimeneas del cordón de Ventanas (cuyas alturas oscilan entre $110$ y $152\text{ m}$ AGL) descargan sus penachos por sobre la base de dicha inversión, en una atmósfera laminar con turbulencia prácticamente nula. En este escenario, la pluma flota confinada horizontalmente sin tomar contacto con el suelo; las cabinas terrestres del SINCA marcan lecturas de fondo limpio, enmascarando la presencia del contaminante en altura.
\item \textbf{Desarrollo de la TIBL y colapso por fumigación:} Al ascender el sol, el flujo de radiación calienta el continente, originando la Capa Límite Interna Térmica (TIBL). La altura de mezcla turbulenta $h_{\text{mix}}(x)$ crece progresivamente a medida que la masa de aire marítima penetra hacia el interior. Cuando la frontera superior de la TIBL alcanza la cota física de la pluma suspendida, la vigorosa convección diurna destruye la estabilidad laminar e intercepta el núcleo concentrado del gas, arrastrándolo bruscamente hacia el suelo en el fenómeno de \textbf{fumigación costera}. Esto explica con precisión física por qué las estaciones de La Greda y Puchuncaví registran aumentos abruptos en las concentraciones de $\text{SO}_2$ preferentemente entre las 09:00 y las 12:00 horas, tras horas de aparente calma nocturna.
\end{enumerate}

\subsubsection{Estimación Analítica del Ancho Horizontal de Pluma (Fórmulas de Briggs)}
Para dimensionar la densidad requerida en la malla del grafo de navegación y determinar si un UAV en vuelo de crucero puede resolver espacialmente la estructura transversal del penacho contaminante, se modela el semiancho de dispersión lateral $\sigma_y(x)$ mediante la formulación clásica de Briggs para fuentes elevadas en terreno abierto \cite{briggs1973}:
\begin{equation}
\sigma_y(x) = \frac{a \cdot x}{\sqrt{1 + 0{,}0001\,x}}
\label{eq:briggs}
\end{equation}
\noindent donde $x$ denota la distancia de transporte a sotavento expresada en metros, y $a$ es un coeficiente adimensional empírico dependiente de la clase de estabilidad atmosférica de Pasquill-Gifford. Asumiendo que el ancho físico observable de la pluma abarca aproximadamente un intervalo de cuatro desviaciones estándar ($W \approx 4\sigma_y$), la Tabla~\ref{tab:ancho_pluma} detalla los valores característicos a una distancia representativa de $x = 2{,}0\text{ km}$ desde el foco emisor de Ventanas:

\begin{table}[H]
\centering
\small
\caption{Estimación analítica del ancho de pluma ($W \approx 4\sigma_y$) a $x = 2{,}0\text{ km}$ según estabilidad atmosférica.}
\label{tab:ancho_pluma}
\begin{tabular}{lcccc}
\toprule
\textbf{Clase de Estabilidad} & \textbf{Momento Típico en la Bahía} & \textbf{Coeficiente $a$} & $\sigma_y(2\text{ km})$ & \textbf{Ancho Pluma ($W$)} \\
\midrule
F (Muy estable) & Madrugada / Inversión térmica baja & $0{,}04$ & $\approx 73{,}0\text{ m}$ & $\approx 292\text{ m}$ \\
D (Neutra) & Régimen de transición / Viento fuerte & $0{,}08$ & $\approx 146{,}1\text{ m}$ & $\approx 584\text{ m}$ \\
A (Extremadamente inestable) & Mediodía diurno / Fuerte insolación & $0{,}22$ & $\approx 401{,}7\text{ m}$ & $\approx 1.607\text{ m}$ \\
\bottomrule
\end{tabular}
\end{table}

\noindent \textbf{Relevancia para el diseño del grafo aéreo:} En condiciones de madrugada (estabilidad F), el ancho efectivo del penacho gaseoso es de apenas $\approx 290\text{ m}$. Si el UAV navega en crucero a $v = 15\text{ m/s}$ ($54\text{ km/h}$), cruza el ancho completo de la pluma en tan solo $19{,}3\text{ segundos}$. Si el sensor atmosférico embarcado posee un tiempo de respuesta característico $t_{90} \ge 15\text{--}30\text{ s}$, una pasada transversal rápida subestimará severamente la concentración máxima del núcleo debido al retardo dinámico de equilibrio de la celda de sensado. Por ende, la planificación de trayectorias resilientes debe contemplar tramos de velocidad reducida ($\le 3\text{--}5\text{ m/s}$) o puntos de sustentación estacionaria (\textit{hovering}) en los nodos de intercepción a sotavento.

\subsubsection{Zonificación Vertical de la Cuenca en Cuatro Capas Físicas y Operacionales}
\label{subsubsec:cuatro_capas}

Para estructurar formalmente el problema de la medición atmosférica y responder con precisión científica a la pregunta de \textit{dónde medir, cómo medir y por qué en cada cota}, la columna troposférica sobre la Bahía de Quintero y Puchuncaví se zonifica en cuatro estratos físicos y operativos diferenciados (ver Tabla~\ref{tab:cuatro_capas}):

\begin{table}[H]
\centering
\small
\caption{Zonificación vertical de la columna atmosférica en la Bahía de Quintero y Puchuncaví.}
\label{tab:cuatro_capas}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{2.8cm}p{2.2cm}p{4.2cm}p{3.2cm}p{3.8cm}p{4.8cm}}
\toprule
\textbf{Estrato / Capa} & \textbf{Rango Altimétrico} & \textbf{Dinámica y Régimen Físico} & \textbf{Contaminantes Dominantes} & \textbf{Instrumentación Típica} & \textbf{Aporte Operacional y Limitación} \\
\midrule
\textbf{Capa 1: Superficie y Dosel Humano} & $0\text{ a }15\text{ m}$ AGL & Microcapa superficial rugosa dominada por fricción del suelo. Régimen de terral nocturno débil y brisa marina diurna. & $\text{MP}_{10}$ grueso, polvos resuspendidos, $\text{NO}_x$ vehicular, gases fugitivos de nivel de suelo. & Cabinas terrestres fijas SINCA (tomas a $3\text{--}4\text{ m}$ s.n.t.). & \textbf{Aporte:} Mide la exposición directa real sobre la población peatonal.\newline \textbf{Límite:} Inmóvil; ciega a penachos industriales confinados en altura antes de fumigar. \\
\addlinespace
\textbf{Capa 2: Desacople y Drenaje Laminar} & $15\text{ a }80\text{ m}$ AGL & Estrato de inversión térmica superficial nocturna. Gradiente térmico positivo (estable). Flujo catabático laminar desde valles interiores. & Capa de aire oceánico limpio relativo bajo la pluma nocturna; gases fugitivos densos de hidrocarburos marinos. & Torres meteorológicas (hasta $30\text{--}40\text{ m}$), mástiles de telecomunicación. & \textbf{Aporte:} Zona de transición térmica y desacople.\newline \textbf{Límite:} Escasa presencia de instrumentación continua sobre $30\text{ m}$. \\
\addlinespace
\textbf{Capa 3: Transporte de Plumas (Estrato UAV)} & $80\text{ a }120\text{ m}$ AGL & Techo regulatorio legal DAN 151. Altura de descarga efectiva de chimeneas industriales ($110\text{--}152\text{ m}$). Flujo advectivo rápido. & Núcleos concentrados de $\text{SO}_2$, COVs ligeros (BTEX), sulfuro de hidrógeno ($\text{H}_2\text{S}$) y $\text{MP}_{2{,}5}$. & \textbf{UAV multirrotor industrial (DJI M350 RTK instrumentado).} & \textbf{Aporte:} \textbf{Alerta temprana}: intercepta la pluma pura antes de su colapso por fumigación sobre escuelas.\newline \textbf{Límite:} Restringido por autonomía de batería y techo legal de $120\text{ m}$ AGL. \\
\addlinespace
\textbf{Capa 4: Zona Ciega e Inversión Libre} & $> 120\text{ m}$ AGL ($120\text{ a }500\text{ m}$) & Capa de mezcla profunda diurna o inversión térmica de subsidencia marina profunda (ej. crisis 2018 a $\approx 400\text{ m}$). & Mezcla convectiva diluida o acumulación regional sinóptica. & Teledetección remota: SODAR ($30\text{--}400\text{ m}$), Ceilómetro/LIDAR, radiosondeo. & \textbf{Aporte:} Caracterización sinóptica macro.\newline \textbf{Límite:} Espacio aéreo fuera del alcance normativo de la DAN 151 sin exención expresa. \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsubsection{Representación Gráfica: Corte Transversal Suroeste $\to$ Noreste}
La Figura~\ref{fig:corte_transversal} esquematiza la estructura vertical de la cuenca sobre un corte topográfico real suroeste a noreste (desde el mar exterior y la península de Quintero hasta los cerros interiores de Puchuncaví, basados en el perfil SRTM), contrastando el régimen nocturno de pluma suspendida frente al régimen matutino de fumigación, la posición de las estaciones terrestres y el estrato de navegación del UAV bajo el techo legal de la norma DAN 151.

\begin{figure}[H]
\centering
\begin{tikzpicture}[scale=0.88, every node/.style={transform shape}, font=\sffamily\scriptsize]
    % Fondo y cielo
    \fill[blue!5] (0,0) rectangle (15,6.5);
    
    % Perfil orografico aproximado (SRTM)
    % 0 a 3 km mar (cota 0), 3 a 5 Quintero (+15m), 5 a 6.5 mar/costa, 6.5 a 10 Ventanas (+10m), 10 a 12.5 La Greda (+35m), 12.5 a 15 Puchuncavi (+67m)
    \fill[gray!25] (0,0) -- (3,0) -- (3.5,0.4) -- (4.8,0.4) -- (5.2,0) -- (6.5,0) -- (7.0,0.3) -- (10,0.3) -- (12,1.0) -- (15,1.8) -- (15,-0.2) -- (0,-0.2) -- cycle;
    \draw[thick, black!70] (0,0) -- (3,0) -- (3.5,0.4) -- (4.8,0.4) -- (5.2,0) -- (6.5,0) -- (7.0,0.3) -- (10,0.3) -- (12,1.0) -- (15,1.8);

    % Agua del mar
    \fill[cyan!15] (0,-0.2) rectangle (3,0);
    \fill[cyan!15] (5.2,-0.2) rectangle (6.5,0);
    \draw[blue!60, very thick] (0,0) -- (3,0);
    \draw[blue!60, very thick] (5.2,0) -- (6.5,0);
    \node[blue!80!black, below] at (1.5,0) {\textbf{Mar Abierto / Rada}};
    \node[blue!80!black, below] at (5.85,0) {\textbf{Bahía Interior}};

    % Buques fondeados
    \draw[fill=gray!60] (1.2,0) rectangle (1.8,0.25);
    \draw[thick] (1.5,0.25) -- (1.5,0.5);
    \node[above, align=center, font=\tiny] at (1.5,0.5) {Buques Fondeados\\(Emisiones SO$_2$, NO$_x$)};

    % Hitos terrestres
    \node[below, align=center] at (4.1,-0.2) {\textbf{Quintero}\\(Terminales ENAP/GNL)};
    \node[below, align=center] at (8.5,-0.2) {\textbf{Polo Ventanas}\\(Termoel., Refinería)};
    \node[below, align=center] at (12.2,-0.2) {\textbf{La Greda}\\(Escuela / SINCA)};
    \node[below, align=center] at (14.2,-0.2) {\textbf{Puchuncaví}\\(Centro / +67 m)};

    % Chimeneas industriales en Ventanas
    \draw[line width=1.5pt, gray!80!black] (8.2,0.3) -- (8.2,4.1);
    \node[above, font=\tiny, align=center] at (8.2,4.1) {Chimenea 152 m\\(Obstáculo físico)};
    \draw[line width=1.2pt, gray!80!black] (8.7,0.3) -- (8.7,3.8);
    \node[above, font=\tiny] at (8.7,3.8) {140 m (Termoel.)};

    % Capa de Inversion Termica Marina
    \draw[dashed, red!80!black, line width=1pt] (0,4.8) -- (15,5.2);
    \node[above, red!85!black, font=\scriptsize\bfseries] at (3.5,4.85) {Base Inversión Térmica de Subsidencia (Tapa Atmosférica)};

    % Pluma Industrial Suspendida (Madrugada)
    \fill[orange!25, opacity=0.7] (8.2,4.0) -- (11.5,4.3) -- (15,4.6) -- (15,3.8) -- (11.5,3.6) -- (8.2,3.9) -- cycle;
    \draw[orange!80!black, thick] (8.2,4.0) -- (15,4.6);
    \draw[orange!80!black, thick] (8.2,3.9) -- (15,3.8);
    \node[orange!90!black, font=\scriptsize\bfseries] at (13,4.4) {Pluma en Altura (Noche/Madrugada)};

    % Fenomeno de Fumigacion (Manana)
    \draw[-{Stealth[length=2mm]}, orange!85!black, thick, dashed] (11.8,3.6) -- (12.2,1.4);
    \draw[-{Stealth[length=2mm]}, orange!85!black, thick, dashed] (13.5,3.7) -- (14.0,2.1);
    \node[orange!85!black, font=\tiny\bfseries, align=center] at (13.3,2.8) {Fumigación matutina\\(Ruptura de inversión)};

    % Techo Legal DAN 151 (120 m AGL sobre el terreno)
    \draw[line width=1.2pt, blue!70!black, dashdotted] (0,3.0) -- (3,3.0) -- (3.5,3.4) -- (4.8,3.4) -- (5.2,3.0) -- (6.5,3.0) -- (7.0,3.3) -- (10,3.3) -- (12,4.0) -- (15,4.8);
    \node[blue!80!black, font=\tiny\bfseries, right] at (0,3.2) {Techo máximo legal: 120 m AGL (DAN 151)};

    % Zona Ciega (sobre 120 m AGL)
    \node[gray!60!black, font=\tiny\bfseries, fill=white, inner sep=1pt] at (5.5,5.8) {Zona ciega a monitoreo legal con UAV (> 120 m AGL)};

    % Trayectoria de vuelo UAV (80-100 m AGL)
    \draw[green!60!black, ultra thick] (3.6,2.6) -- (5.0,2.6) -- (7.0,2.5) -- (10,2.5) -- (12,3.2) -- (14.5,4.0);
    \node[green!50!black, font=\tiny\bfseries, fill=white, inner sep=1.5pt] at (9.5,2.7) {Corredor de muestreo UAV (80--100 m AGL)};

    % Estaciones terrestres a nivel de suelo (3-4 m)
    \fill[black] (4.1,0.4) circle (2pt);
    \fill[black] (12.2,1.0) circle (2pt);
    \fill[black] (14.2,1.8) circle (2pt);
    \node[above, font=\tiny] at (4.1,0.45) {SINCA Quintero 3 m};
    \node[above, font=\tiny] at (12.2,1.05) {SINCA La Greda 3 m};
    \node[above, font=\tiny] at (14.2,1.85) {SINCA Puchuncaví 3 m};

    % Ejes y escala
    \draw[->, thick] (0,-0.6) -- (15,-0.6) node[right, font=\scriptsize] {Distancia SW $\to$ NE (km)};
    \foreach \x/\km in {0/0, 3/3, 5/5, 8.5/8.5, 12/12, 15/15} {
        \draw (\x,-0.55) -- (\x,-0.65) node[below, font=\tiny] {\km};
    }
    \draw[->, thick] (0,-0.6) -- (0,6.5) node[above, font=\scriptsize] {Altitud (m s.n.m.)};
    \foreach \y/\m in {0/0, 1.5/60, 3.0/120, 4.5/180, 6.0/240} {
        \draw (-0.1,\y) -- (0.1,\y) node[left=2pt, font=\tiny] {\m};
    }
\end{tikzpicture}
\caption{Corte transversal esquemático de la Bahía de Quintero y Puchuncaví (eje suroeste $\to$ noreste), evidenciando la estratificación atmosférica, la pluma industrial suspendida en altura durante la noche, el proceso de fumigación matutina sobre receptores residenciales, el techo regulatorio de 120~m AGL (DAN 151) y el estrato de intercepción del UAV.}
\label{fig:corte_transversal}
\end{figure}

\subsection{Solución Propuesta y Utilidad del Proyecto}
\label{subsec:solucion}

Para responder a este desafío, se construyó una infraestructura geoespacial automatizada, reproducible y modular contenida en microservicios Docker, acoplada a una base de datos relacional PostgreSQL 16 con PostGIS 3.5 y pgRouting 3.8. La plataforma modela y procesa:

\begin{itemize}
\item \textbf{Topología del grafo aéreo ($237$ nodos y $633$ aristas):} Con origen estratégico en el Aeródromo de Quintero (código \texttt{base\_scer}), los nodos catastran las fuentes emisoras del parque industrial, los receptores residenciales vulnerables (salud y educación) y las estaciones de monitoreo SINCA del área de vuelo.
\item \textbf{Conectividad determinista por $K$-vecinos y Union-Find ($633$ aristas):} Cada nodo se enlazó a sus $K=4$ vecinos más cercanos mediante distancia Haversine, añadiendo deterministamente $2$ aristas puente mediante el algoritmo \textit{Union-Find} para salvar la separación del cuerpo marino de la bahía. La conexidad global fue verificada formalmente con \texttt{pgr\_connectedComponents}, garantizando que cualquier nodo sea alcanzable desde el aeródromo.
\item \textbf{Muestreo en estaciones SINCA y co-localización sensorial:} Las estaciones SINCA constituyen los destinos prioritarios de la red. La planificación de trayectorias hacia ellas permite proyectar la co-localización sensorial: muestrear verticalmente dentro de la columna atmosférica ($0\text{--}120\text{ m}$ AGL) sobre el sensor de tierra para calibrar la correlación vertical entre la concentración de la pluma y el registro superficial.
\item \textbf{Cinco capas de metadatos operacionales:}
\begin{enumerate}
\item \textit{Calidad del aire SINCA (prioridad de misión):} Modelada estrictamente como una \textbf{función de recompensa operacional ($\mathcal{R}(d)$)} y no como un costo o riesgo; el objetivo del UAV es precisamente alcanzar y caracterizar los focos de mayor concentración contaminante.
\item \textit{Relieve orográfico SRTM (justificación dual):} Normativamente, el techo legal de $120\text{ m}$ de la DAN 151 se mide respecto al suelo, de modo que el ascenso topográfico hacia el interior ($+67\text{ m}$ en Puchuncaví) obliga a la aeronave a seguir el perfil del terreno para no colisionar; energéticamente, cada metro de ascenso incrementa el consumo de batería ($EEE$). Por ello se almacena el perfil continuo a lo largo de cada arista y no un único valor nodal.
\item \textit{Densidad poblacional censal INE 2017:} Cuantificación del riesgo a terceros en tierra conforme a la metodología SORA \cite{sora} y el cumplimiento de las restricciones urbanas de la DAN 151 \cite{dan151}.
\item \textit{Cobertura celular C2 (OpenStreetMap):} Estimación del enlace de mando y control asumiendo telemetría móvil 4G/LTE sobre mástiles locales en un radio omnidireccional estimado de $3.000\text{ m}$.
\item \textit{Obstáculos verticales físicos (\texttt{meta\_obstacle}):} Catastro georreferenciado de chimeneas industriales (con cotas de hasta $152\text{ m}$ AGL) y líneas de transmisión eléctrica de alta tensión ($110/220\text{ kV}$) que cruzan los corredores aéreos.
\end{enumerate}
\item \textbf{Cuatro capas de amenazas ambientales y operacionales dinámicas:}
\begin{enumerate}
\item \textit{Incendios activos (NASA FIRMS):} Círculos de exclusión de $2.000\text{ m}$ en torno a detecciones satelitales VIIRS de $375\text{ m}$ de resolución, previniendo turbulencia térmica severa y conflicto con aeronaves cisterna.
\item \textit{Tráfico aéreo tripulado (OpenSky Network ADS-B):} Cilindros de protección de $1.500\text{ m}$ de radio y hasta $1.000\text{ m}$ MSL en torno a aeronaves en patrón de aproximación al Aeródromo SCER, garantizando separación absoluta y prioridad de paso según la DAN 151.
\item \textit{Viento crítico en altura (Open-Meteo):} Grilla $4 \times 4$ evaluada al techo de vuelo ($120\text{ m}$ AGL) con umbral de $12\text{ m/s}$ ($43{,}2\text{ km/h}$), límite de estabilidad estructural del DJI Matrice 350 RTK \cite{dji}.
\item \textit{Niebla costera y visibilidad horizontal (Open-Meteo):} Grilla $4 \times 4$ con umbral de visibilidad $<1.000\text{ m}$ o saturación marina (camanchaca), activando condición No-Go por pérdida de condiciones visuales VMC normativas.
\end{enumerate}
\end{itemize}

Sobre esta infraestructura, se calculó la ruta de mínima distancia euclidiana mediante el algoritmo \texttt{pgr\_dijkstra}. Esta ruta constituye la \textbf{línea base del peor caso}: al optimizar únicamente la longitud métrica y desestimar la densidad urbana, los obstáculos y las contingencias dinámicas, demuestra de forma cuantitativa e irrebatible el nivel de peligro al que se expone una aeronave operada con navegación convencional. La solución provee además una plataforma web interactiva en Leaflet que alerta visualmente en color rojo la condición de vuelo BVLOS para cualquier trayectoria superior a $500\text{ m}$, conforme a la regulación aeronáutica de la DGAC.

El repositorio oficial del proyecto se encuentra disponible en: \url{https://giteit.udp.cl/CIT3435/2026-2/trabajo-grupal/grupo09}.

\section{Marco Conceptual y Estado del Arte}
\label{sec:marco_conceptual}

El diseño de redes de navegación autónoma para UAVs en misiones ambientales converge en cuatro áreas teóricas fundamentales:

\subsection{Algoritmos de Camino Mínimo y Ruteo Espacial}

El problema de determinar la trayectoria de menor costo sobre un grafo discreto $G=(V,E)$ con pesos no negativos $c: E \to \mathbb{R}^+$ se resuelve óptimamente mediante el algoritmo clásico de Dijkstra \cite{dijkstra}, el cual opera mediante una exploración voraz (\textit{greedy}) con complejidad temporal $\mathcal{O}(|E| + |V|\log |V|)$ utilizando colas de prioridad. En entornos espaciales relacionales, este algoritmo se encuentra implementado a nivel de base de datos a través de la función \texttt{pgr\_dijkstra} de la extensión pgRouting \cite{pgrouting}, permitiendo procesar redes topológicas sobre geometrías vectoriales indexadas con PostGIS \cite{postgis}. En el modelo inicial desarrollado en esta fase, la función de costo se restringe estrictamente a la longitud física geodésica de cada segmento ($c(e) = \text{length\_m}$), estableciendo un escenario base de comparación y cota inferior métrica.

\subsection{Caminos Alternativos y Disimilitud Espacial}

Para alcanzar una navegación verdaderamente resiliente ante contingencias, la planificación de trayectorias requiere la generación de rutas secundarias. Los métodos tradicionales de $k$-caminos mínimos, tales como el algoritmo de Yen \cite{yen}, producen con frecuencia trayectorias que comparten la gran mayoría de sus aristas con el camino principal, careciendo de redundancia espacial efectiva ante una amenaza zonal. Por su parte, los enfoques de caminos disjuntos en aristas o vértices de Suurballe \cite{suurballe} y Bhandari \cite{bhandari} garantizan la desconexión física total pero pueden inducir penalizaciones excesivas en la longitud o resultar infactibles en grafos dispersos. Para superar esta limitación, Akgün et al. \cite{akgun} formalizaron el problema de caminos disimilares (\textit{Minimax / Minisum Dissimilar Paths}), proponiendo técnicas de penalización iterativa que incrementan el costo de las aristas transitadas en la ruta primaria para forzar la divergencia controlada de la ruta alternativa ($k \ge 2$), preservando un compromiso admisible entre longitud y separación geométrica.

\subsection{Gestión del Riesgo Operacional en UAVs y Regulación Aeronáutica}

La integración de aeronaves pilotadas a distancia en el espacio aéreo civil exige metodologías sistemáticas de evaluación de riesgo. La directriz internacional SORA (\textit{Specific Operations Risk Assessment}), desarrollada por JARUS \cite{sora}, clasifica el riesgo en dos vertientes: riesgo intrínseco en tierra (\textit{Ground Risk Class}, GRC), determinado por la densidad poblacional y la masa del vehículo; y riesgo aéreo (\textit{Air Risk Class}, ARC), derivado de la proximidad a aeródromos y aeronaves tripuladas. La fiabilidad de los componentes críticos y el análisis de modos de fallo en UAVs han sido ampliamente caracterizados por Petritoli et al. \cite{petritoli}, destacando la pérdida del enlace de mando y control (C2) y el agotamiento prematuro de batería como las principales causales de incidentes graves.

En el marco normativo chileno, la Dirección General de Aeronáutica Civil (DGAC) regula estas actividades mediante la Norma Técnica Aeronáutica DAN 151 (3.ª edición, formalizada mediante la Resolución Exenta N.º 1033 de 27 de mayo de 2024 y publicada en el Diario Oficial el 11 de marzo de 2025) \cite{dan151}. La DAN 151 fija un techo máximo operativo de 400 pies ($\approx 120\text{ m}$ AGL) y establece que los vuelos que se ejecuten dentro de la línea de vista visual del piloto (VLOS) no podrán superar los $500\text{ m}$ de distancia horizontal. Toda operación que sobrepase dicho umbral clasifica jurídicamente como operación más allá del alcance visual (BVLOS), exigiendo autorización expresa previa de la DGAC y la acreditación de procedimientos de mitigación operacional, enlaces C2 redundantes y gestión de riesgos equivalentes a SORA. Asimismo, cabe distinguir que la DAN 151 aplica a operaciones en áreas pobladas o sobre recintos de interés público, mientras que en sectores rurales o despoblados el marco operacional de referencia se complementa con las disposiciones de la norma general DAN 91.

\subsection{Muestreo de Calidad del Aire y Planificación Adaptativa en Dos Niveles}

El monitoreo de efluentes atmosféricos mediante vehículos aéreos no tripulados supera el retardo espacial y la ceguera vertical de las redes fijas terrestres. En este ámbito, Kosior, Przystałka y Panfil (2024) \cite{kosior} propusieron una arquitectura adaptativa de planificación de rutas en dos niveles (\textit{Adaptive Path Planning}, APP) concebida para aeronaves autónomas de ala fija en tareas de muestreo ambiental en Żywiec (Polonia). La arquitectura descompone el problema en:
\begin{enumerate}
\item \textbf{Global Path Planner (GPP):} Planificador estratégico previo al despegue, encargado de computar la trayectoria global óptima de muestreo sobre un grafo espacial minimizando el consumo energético estimado ($EEE$) mediante Algoritmos Genéticos y Dijkstra.
\item \textbf{Local Path Planner (LPP):} Planificador táctico reactivo a bordo, diseñado para operar en tiempo real garantizando la evitación estricta de colisiones ($N_{COL} = 0$) y la replanificación ante contingencias dinámicas imprevistas mediante algoritmos como RRT* o Dynamic A*. En su ensayo experimental de Żywiec, un tiempo de cómputo reactivo $CT \le 4{,}55\text{ s}$ constituyó el criterio de éxito del escenario, derivado de la velocidad de crucero del UAV de ala fija ($v = 11\text{ m/s}$) y la distancia de despeje de seguridad mínima ante obstáculos.
\end{enumerate}

\noindent \textbf{Delimitación metodológica y contexto de aplicación en Quintero:}
Es indispensable precisar cómo se adapta el modelo de Kosior et al. \cite{kosior} a este proyecto. El trabajo de Kosior et al. se adopta como \textbf{referencia conceptual para la separación en dos capas (GPP offline previo al vuelo y LPP táctico a bordo) y para el principio del balance de energía ($EEE$)}. Sin embargo, \textbf{no constituye un marco directamente aplicable a la Bahía de Quintero sin modificaciones estructurales}. Mientras la plataforma de Kosior et al. operó como ala fija en campo abierto con obstáculos dispersos, la Bahía de Quintero impone un entorno costero altamente congestionado en baja cota ($0$ a $120\text{ m}$ AGL según DAN 151 \cite{dan151}), donde los factores dominantes son la densidad urbana censal ($>2.500\text{ hab/km}^2$), la presencia de chimeneas industriales de hasta $152\text{ m}$ AGL, redes eléctricas de alta tensión ($110/220\text{ kV}$), el espacio aéreo del Aeródromo militar/civil de Quintero (SCER) y la severa microclimatología costera de niebla marina (camanchaca) y vientos turbulentos.

En cuanto a la ingestión de datos espaciales, los productos de incendios satelitales VIIRS de $375\text{ m}$ (NASA FIRMS) \cite{schroeder} proveen información casi en tiempo real (NRT), mientras que la geometría del espacio aéreo se normaliza bajo el estándar internacional RFC 7946 GeoJSON \cite{rfc7946}.

% ============================== 3 ==============================
\subsection{Teoría y Práctica de la Medición Aérea: Sensores, Rotor Downwash y Borrado Espacial}
\label{subsec:teoria_practica_medicion}

La transición desde el monitoreo superficial estático hacia el sensado atmosférico móvil mediante UAVs introduce desafíos de ingeniería instrumental que condicionan directamente el diseño del enrutamiento:

\subsubsection{Tecnologías de Sensado Embarcadas y Ventajas/Desventajas frente a Redes Terrestres}
En plataformas aéreas no tripuladas, las estrictas restricciones de masa máxima al despegue (MTOW) y consumo eléctrico imposibilitan el uso de analizadores de referencia EPA convencionales. Por ello, la instrumentación embarcada recurre a módulos de microsensado de estado sólido, cuyas características operacionales se contrastan en la Tabla~\ref{tab:comparacion_instrumentos}:

\begin{table}[H]
\centering
\small
\caption{Comparativa técnica: estaciones de monitoreo fijas terrestres vs. instrumentación embarcada en UAV.}
\label{tab:comparacion_instrumentos}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.2cm}p{6.0cm}p{6.0cm}}
\toprule
\textbf{Parámetro Técnico} & \textbf{Estaciones Terrestres de Referencia (SINCA)} & \textbf{Carga Ambiental Embarcada en UAV} \\
\midrule
\textbf{Principio de Medición} & Analizadores fotométricos UV ($\text{SO}_2$), quimioluminiscencia ($\text{NO}_x$), cromatografía de gases (COVs) y atenuación beta ($\text{MP}$). & Detectores de Fotoionización (PID $10{,}6\text{ eV}$), celdas electroquímicas amperométricas y contadores ópticos OPC. \\
\addlinespace
\textbf{Exactitud y Deriva} & Grado regulatorio y legal ($\pm 1\text{--}2$\,\% de error). Calibración diaria automática por gases patrón. Deriva anual despreciable. & Grado indicativo / \textit{screening} ($\pm 10\text{--}15$\,\% de error). Sensibilidad a la deriva térmica ($0{,}5\text{--}2$\,\%/$^\circ\text{C}$) y humedad. \\
\addlinespace
\textbf{Resolución Temporal} & Promedios integrados cada $1\text{ a }60\text{ minutos}$ (lenta para transitorios rápidos). & Muestreo de alta frecuencia ($1\text{ a }10\text{ Hz}$), permitiendo resolver gradientes espaciales. \\
\addlinespace
\textbf{Movilidad y Cobertura} & Estática e inmóvil: representatividad acotada al radio administrativo de $2\text{ km}$ a nivel de suelo ($3\text{--}4\text{ m}$). & Cobertura tridimensional móvil: capacidad de navegar perfiles verticales ($0\text{--}120\text{ m}$) y horizontales ($10{,}5\text{ km}$). \\
\addlinespace
\textbf{Costo de Inversión} & Alto CAPEX: \$80.000 a \$150.000 USD por cabina física climatizada fija. & Bajo a moderado: \$15.000 a \$25.000 USD (aeronave industrial + módulo multiparamétrico). \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsubsection{Aerodinámica del Rotor Downwash y Diseño de la Toma de Muestra}
Un multirrotor de gran porte como el DJI Matrice 350 RTK (peso operativo $\approx 9{,}2\text{ kg}$ con baterías y payload) sustenta su peso acelerando una columna masiva de aire hacia abajo, generando un campo de velocidades inducidas descendente (\textit{rotor downwash}) de entre $10\text{ y }18\text{ m/s}$ bajo el plano de las hélices. Si la toma de aire del sensor se ubica bajo el fuselaje o en el tren de aterrizaje:
\begin{enumerate}
\item El torbellino helicoidal mezcla turbulentamente masas de aire procedentes de diferentes estratos verticales en un radio de más de $3\text{ metros}$, destruyendo la representatividad de la cota de vuelo.
\item La presión dinámica ejercida por las palas altera la presión estática de la cámara de sensado, afectando el caudal de difusión hacia las celdas electroquímicas.
\end{enumerate}
Para mitigar este efecto, la arquitectura física del sistema exige que la toma de muestra se instale en un \textbf{mástil dorsal rígido elevado al menos $35\text{--}45\text{ cm}$ sobre el plano superior de rotación de las hélices}, o bien en una pértiga adelantada proel orientada al viento relativo incidente, canalizando el aire mediante tuberías de PTFE inerte (Teflón) acopladas a una microbomba de diafragma de caudal constante ($1{,}5\text{ L/min}$).

\subsubsection{El Fenómeno de Borrado Espacial (\textit{Spatial Smearing}) y Cinemática de Ruteo}
La capacidad de resolver la estructura espacial de una pluma de contaminantes se encuentra físicamente limitada por el tiempo de respuesta del transductor electroquímico o PID ($t_{90}$), definido como el intervalo necesario para registrar el $90$\,\% del cambio ante un escalón de concentración (típicamente $t_{90} \approx 20\text{ a }45\text{ s}$ en sensores amperométricos compactos \cite{galle2021}).

Cuando el UAV se desplaza a una velocidad horizontal $v$, la lectura instantánea no corresponde a un punto geométrico singular, sino al promedio ponderado sobre una distancia de barrido o «borrado espacial» (\textit{spatial smearing}) $d_{\text{smear}}$:
\begin{equation}
d_{\text{smear}} = v \cdot t_{90}
\label{eq:smear}
\end{equation}
\noindent Con una velocidad de crucero nominal $v = 15\text{ m/s}$ y un sensor con $t_{90} = 25\text{ s}$, la distancia de borrado resulta $d_{\text{smear}} = 15\text{ m/s} \times 25\text{ s} = 375\text{ metros}$. Si el ancho observable de la pluma nocturna a $2\text{ km}$ del cordón industrial es de $W \approx 290\text{ m}$ (según la Ecuación~(\ref{eq:briggs}) para clase de estabilidad F), el dron atraviesa la pluma en tan solo $19{,}3\text{ s}$, abandonándola antes de que el sensor alcance su régimen de equilibrio. Como resultado, \textbf{el sensor registrará una curva amortiguada que subestima severamente el pico real de concentración}.

\noindent \textbf{Implicancia directa en el diseño del planificador de rutas:}
Este fenómeno demuestra que \textbf{el enrutamiento no puede concebirse con una cinemática homogénea}. La arquitectura de navegación debe desacoplar:
\begin{itemize}
\item \textbf{Tramos de Tránsito:} Aristas convencionales recorridas a velocidad de crucero nominal ($v = 15\text{ m/s}$) para minimizar la exposición a zonas pobladas y sombras de telecomunicación.
\item \textbf{Tramos y Nodos de Muestreo (Intercepción de Pluma):} Corredores a sotavento navegados a baja velocidad ($v_{\text{muestreo}} \le 2\text{--}3\text{ m/s}$, donde $d_{\text{smear}} \le 50\text{ m}$) o la ejecución de \textbf{sustentación estacionaria (\textit{hovering}) durante al menos $60\text{ segundos}$} sobre los nodos de co-localización, asegurando que la celda alcance su equilibrio fisicoquímico pleno.
\end{itemize}

\section{Objetivos del Proyecto y Preguntas de Investigación}
\label{sec:objetivos}

\subsection{Objetivo General}

Construir una base de datos geoespacial reproducible que integre la infraestructura de la red aérea, cinco capas de metadatos operacionales y cuatro capas de amenazas operacionales dinámicas en el área de Quintero, Ventanas y Puchuncaví, y obtener sobre ella la ruta de menor longitud mediante \texttt{pgr\_dijkstra} como línea base y escenario de peor caso para la evaluación del ruteo resiliente.

\subsection{Objetivos Específicos}

\begin{enumerate}
\item Diseñar e inicializar una base de datos relacional-espacial en PostgreSQL 16 con las extensiones PostGIS 3.5 y pgRouting 3.8, estructurada en esquemas transaccionales que alberguen la topología de la red, los metadatos territoriales y los eventos de amenaza dinámicos.
\item Automatizar la extracción y modelado de la red aérea en un grafo espacial no dirigido de $237$ nodos, $633$ aristas conexas y $8$ polígonos de zonas urbanas, estandarizados bajo el formato RFC 7946 GeoJSON \cite{rfc7946}.
\item Implementar scripts modulares de extracción y carga para 5 capas de metadatos de soporte operacional: calidad del aire en tiempo real (SINCA MMA) modelada como recompensa de muestreo, perfiles altimétricos continuos por arista (NASA SRTM 30m), densidad de población censal (INE 2017) para cálculo de riesgo en tierra SORA, radiobases celulares para telemetría C2 (OpenStreetMap) y catastro de obstáculos verticales críticos (chimeneas de hasta $152\text{ m}$ AGL y líneas de alta tensión $110/220\text{ kV}$).
\item Implementar extractores automatizados para 4 capas de contingencias operacionales dinámicas: focos de incendios activos (NASA FIRMS), separación frente a aeronaves tripuladas en aproximación visual (OpenSky Network ADS-B), vectores y ráfagas de viento crítico a $120\text{ m}$ AGL (Open-Meteo) y visibilidad horizontal/niebla costera (Open-Meteo).
\item Calcular mediante \texttt{pgr\_dijkstra} en base de datos la ruta de menor distancia física en metros desde el Aeródromo de Quintero hacia las estaciones SINCA del área de vuelo, estableciendo el peor caso de exposición frente a las amenazas del entorno e informando la condición de vuelo BVLOS ($>500\text{ m}$) bajo la normativa chilena DAN 151.
\item Implementar una aplicación interactiva en Leaflet que permita visualizar las capas temáticas y presentar la ruta base calculada junto con sus métricas operacionales y advertencias regulatorias.
\item Orquestar de extremo a extremo las etapas de extracción, creación de esquema, carga de datos y ruteo en un script maestro \texttt{main.py}, asegurando su ejecución en contenedores Docker y validando su integridad mediante una suite de 57 pruebas automatizadas.
\end{enumerate}

\subsection{Preguntas de Investigación y Diseño}
\label{subsec:preguntas_diseno}

El desarrollo y evaluación del sistema busca responder formalmente a tres preguntas operacionales clave:

\begin{itemize}
\item[\textbf{P1.}] ¿Es factible integrar de manera automatizada y reproducible fuentes de datos geoespaciales heterogéneas (APIs REST, sensores ADS-B, modelos de elevación y censos), garantizando la trazabilidad temporal y espacial de cada conjunto de datos en una base relacional?
\item[\textbf{P2.}] ¿La topología de red construida mediante $K$-vecinos más cercanos y aristas puente asegura la conexidad global del espacio aéreo, permitiendo alcanzar todas las estaciones de monitoreo SINCA desde la base aeroportuaria?
\item[\textbf{P3.}] ¿Cuál es la magnitud cuantitativa de la exposición al riesgo (densidad poblacional en tierra, sombras de telecomunicación celular, obstáculos industriales y contingencias meteorológicas) en la ruta de mínima distancia geodésica generada por Dijkstra?
\end{itemize}

% ============================== 4 ==============================
\section{Alcance y Supuestos Operacionales}
\label{sec:alcance}

Para delimitar el alcance técnico y experimental de la investigación, se definen los siguientes supuestos operacionales (S1 a S9):

\begin{itemize}
\item[\textbf{S1.}] \textbf{Topología del grafo y vecindad fija:} La red de corredores aéreos se genera a partir de los $237$ nodos catastrados en la bahía. Cada nodo se enlaza a sus $K=4$ vecinos más cercanos según distancia Haversine, añadiendo $2$ aristas puente deterministas mediante el algoritmo \textit{Union-Find} para unir las componentes separadas por el mar. Los corredores son rectilíneos y bidireccionales. En este modelo se adoptó dicha topología fija como base estructural.
\item[\textbf{S2.}] \textbf{Autorización de despegue y base de operaciones:} Se asume como supuesto operacional la autorización formal de despegue y aterrizaje desde el Aeródromo de Quintero (\texttt{base\_scer}), coordinada con la autoridad aeronáutica civil bajo las condiciones de resguardo de la norma DAN 151 sección 151.103 \cite{dan151}.
\item[\textbf{S3.}] \textbf{Altura de medición relativa a la capa de mezcla ($h_{\text{mix}}$):} El techo legal de operación es de $120\text{ m}$ AGL conforme a la norma DAN 151 \cite{dan151}. Dentro de dicho margen, la cota de vuelo no se asume fija de forma universal, sino que se selecciona en función de la altura de la capa de mezcla pronosticada ($h_{\text{mix}}$) para la hora de la misión. Cada muestra se indexa con dos coordenadas verticales: la cota sobre el terreno $z$ (m AGL) y la cota relativa adimensional $z/h_{\text{mix}}$. En esta fase, la ruta se evalúa en planta y la cota se fija por misión.

\noindent \textit{Justificación física (80 m vs. 100 m):} En una atmósfera turbulenta bien mezclada (típica de la tarde costera), la concentración entre $80\text{ m}$ y $100\text{ m}$ AGL presenta variaciones moderadas. Sin embargo, en régimen nocturno o de madrugada con inversión térmica baja (base en torno a $90\text{ m}$), volar a $80\text{ m}$ (inmerso en la capa superficial limpia de terral) frente a $100\text{ m}$ (interceptando el núcleo laminar de la pluma industrial) produce registros que pueden diferir hasta en un orden de magnitud ($\sim 20$ veces). Sin el dato normalizador $z/h_{\text{mix}}$, una lectura baja es científicamente indeterminada: no permite discriminar si el aire estaba limpio o si la aeronave transitó por debajo o por encima de la masa contaminada.

\item[\textbf{S4.}] \textbf{Umbral de densidad urbana crítica:} Se establece un umbral de $2.500\text{ hab/km}^2$ como supuesto del equipo, representativo de la mediana de densidad en manzanas residenciales consolidadas de Quintero y Ventanas. Las trayectorias que sobrevuelan estas áreas implican un incremento en la clase de riesgo en tierra según la metodología SORA \cite{sora}.
\item[\textbf{S5.}] \textbf{Enlace de mando y control (C2):} Se asume telemetría celular terrestre 4G/LTE con un radio de cobertura omnidireccional estimada de $3.000\text{ m}$ alrededor de cada mástil celular catastrado en OpenStreetMap. Los tramos que exceden este radio se catalogan como zonas en sombra radioeléctrica con riesgo de pérdida de telemetría (\textit{fly-away}) \cite{petritoli}.
\item[\textbf{S6.}] \textbf{Aeronave única de referencia, velocidad y autonomía unificada:} Se define de manera exclusiva el multirrotor industrial DJI Matrice 350 RTK \cite{dji} como la única plataforma aérea operacional del sistema. Se unifica la velocidad de crucero nominal en $v = 15\text{ m/s}$ ($54\text{ km/h}$) para todo el informe y el simulador web. La autonomía máxima declarada por el fabricante es de $55\text{ min}$ (equivalente a $49{,}5\text{ km}$ a velocidad nominal sin carga \cite{dji}). Como supuesto operacional conservador con carga de sensores ambientales y una reserva de seguridad del $20$\,\% de batería para retorno seguro, la autonomía operacional efectiva se fija en $44\text{ min}$ ($39{,}6\text{ km}$). La resistencia al viento del fabricante es de $12\text{ m/s}$ y cuenta con protección ambiental IP55.

\noindent \textit{Derivación analítica del radio operacional máximo ($R_{\max}$):} Si una misión reserva $T_{\text{muestreo}}$ minutos de vuelo estacionario (\textit{hovering}) para muestreo vertical sobre los receptores (a una tasa equivalente de consumo de $0{,}9\text{ km}$ de crucero por minuto de sustentación), la longitud máxima de ruta de ida y regreso sobre el grafo aéreo se deriva analíticamente mediante:
\begin{equation}
R_{\max} = \frac{39{,}6\ \text{km} - (v \cdot T_{\text{muestreo}})}{2}
\label{eq:alcance_uav}
\end{equation}
Para un protocolo de muestreo de $T_{\text{muestreo}} = 20\text{ min}$ ($18\text{ km}$ equivalentes consumidos), el alcance teórico es $R_{\max} \approx (39{,}6 - 18)/2 \approx 10{,}8\text{ km}$. Incorporando una penalización conservadora por viento costero en contra (un viento de frente de $6\text{ m/s}$ en un tramo incrementa el consumo del trayecto de ida y vuelta en aproximadamente $19$\,\%), se adopta formalmente un **radio operacional límite de $R_{\max} = 10{,}5\text{ km}$**.
Como resultado cuantitativo directo frente a la red catastrada: la estación SINCA de Puchuncaví ($14{,}41\text{ km}$ de ida desde SCER) queda formalmente **fuera de alcance** para una misión directa de ida y retorno con muestreo, requiriendo categorizarse como un destino que exige una base intermedia de recarga o acotamiento territorial a los anillos de 2 a 10 km.

\item[\textbf{S7.}] \textbf{Umbrales y geometrías de amenazas ambientales dinámicas:} Se definen como supuestos del equipo: zona de exclusión circular de $2.000\text{ m}$ en torno a focos de calor activos de NASA FIRMS \cite{schroeder} (humo y turbulencia); cilindro de protección de $1.500\text{ m}$ de radio y hasta $1.000\text{ m}$ MSL en torno a aeronaves tripuladas detectadas vía ADS-B en SCER \cite{opensky}; umbral de viento crítico en $12\text{ m/s}$ ($43{,}2\text{ km/h}$) a $120\text{ m}$ AGL según la especificación estructural de la aeronave \cite{dji}; y umbral de niebla/visibilidad reducida en $<1.000\text{ m}$ o saturación de humedad costera ($\text{HR} \ge 95$\,\% con nubes bajas $\ge 80$\,\%) según Open-Meteo \cite{openmeteo}.
\item[\textbf{S8.}] \textbf{Ventana temporal de datos de referencia:} Las tablas y resultados numéricos reportados corresponden a la corrida de referencia ejecutada entre el 18-10-2026 22:35 UTC y el 19-10-2026 02:11 UTC, cuyos archivos GeoJSON se encuentran versionados en el repositorio para garantizar la reproducibilidad completa mediante la opción \texttt{--sin-descarga}.
\item[\textbf{S9.}] \textbf{Régimen de Vuelo BVLOS (Beyond Visual Line of Sight):} Para cualquier trayectoria que supere los $500\text{ m}$ de distancia radial desde el punto de despegue (tal como la misión de $14{,}41\text{ km}$ a la estación SINCA de Puchuncaví), la operación excede la línea de vista visual directa del piloto, quedando catalogada en régimen BVLOS según la norma DAN 151 de la DGAC de Chile \cite{dan151}, requiriendo autorización formal previa, enlace redundante y protocolos de seguridad específicos.
\end{itemize}

\section{Arquitectura del Sistema y Proceso ETL}
\label{sec:arquitectura}

\subsection{Visión General del Pipeline}
\label{subsec:arquitectura_vision}

Para asegurar la reproducibilidad y aislar las dependencias del sistema anfitrión, la plataforma se implementó bajo una arquitectura modular contenerizada en Docker y orquestada con Docker Compose (\texttt{docker-compose.yml}).

El procesamiento sigue un flujo secuencial desacoplado de cuatro etapas (ver Figura~\ref{fig:arquitectura}):
\begin{enumerate}
\item \textbf{Extracción:} 9 scripts independientes consultan APIs REST públicas y datasets maestros.
\item \textbf{Transformación:} Normalización de geometrías, ajuste de unidades, cálculo de distancias Haversine y generación de archivos GeoJSON conformes a RFC 7946 \cite{rfc7946} con un bloque de metadatos \texttt{etl}.
\item \textbf{Carga:} 11 cargadores Python realizan inserciones transaccionales idempotentes en PostgreSQL mediante el conector \texttt{bd/conexion.py}.
\item \textbf{Inferencia y Ruteo:} Ejecución de \texttt{pgr\_dijkstra} en pgRouting \cite{pgrouting} y serialización de resultados hacia el visor cartográfico.
\end{enumerate}

\begin{figure}[H]
\centering
\begin{tikzpicture}[
caja/.style={draw, rounded corners, align=center, font=\scriptsize, minimum height=1.1cm, text width=3.0cm, fill=#1},
caja/.default={white},
flecha/.style={-{Stealth[length=2mm]}, thick},
node distance=0.5cm and 0.55cm]
\node[caja={gray!10}] (f) {Fuentes abiertas\\(APIs y servicios geoespaciales)};
\node[caja={blue!8}, right=of f] (x) {Extracción y transformación\\\texttt{extraer\_*.py}};
\node[caja={blue!8}, right=of x] (g) {GeoJSON RFC 7946\\y especificación \texttt{.md}};
\node[caja={blue!8}, below=of g] (c) {Cargadores transaccionales\\\texttt{cargar\_*.py}};
\node[caja={green!10}, left=of c] (b) {PostgreSQL 16 +\\PostGIS 3.5 + pgRouting 3.8};
\node[caja={blue!8}, left=of b] (r) {Ruteo: \texttt{pgr\_dijkstra}\\(\texttt{cost} = \texttt{length\_m})};
\node[caja={orange!12}, below=of r] (w) {Sitio web Leaflet\\(puerto 8000)};
\draw[flecha] (f) -- (x); \draw[flecha] (x) -- (g); \draw[flecha] (g) -- (c);
\draw[flecha] (c) -- (b); \draw[flecha] (b) -- (r); \draw[flecha] (r) -- (w);
\end{tikzpicture}
\caption{Arquitectura del pipeline ETL y microservicios Docker. Contenedor \texttt{etl} (azul), base de datos \texttt{db} (verde), servidor \texttt{web} (naranja) y fuentes abiertas (gris).}
\label{fig:arquitectura}
\end{figure}

\subsection{Cálculo de Distancias, Geometrías y Superficies Espaciales}
\label{subsec:calculo_distancias}

Para prescindir de librerías binarias nativas (GDAL/GeoPandas) en el proceso ETL, los algoritmos geométricos se desarrollaron con la biblioteca estándar de Python:
\begin{enumerate}
\item \textbf{Cálculo de distancias con la fórmula de Haversine:} La longitud geodésica entre dos puntos $u=(\phi_1, \lambda_1)$ y $v=(\phi_2, \lambda_2)$ se calcula asumiendo una esfera de radio medio $R = 6.371.000\text{ m}$:
\begin{equation}
d(u,v) = 2 R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)
\label{eq:haversine}
\end{equation}
donde $\Delta \phi = \phi_2 - \phi_1$ y $\Delta \lambda = \lambda_2 - \lambda_1$ en radianes. Este valor se almacena en el campo \texttt{length\_m}. Al comparar los $633$ arcos frente al cálculo elipsoidal geodésico exacto sobre el elipsoide WGS84 (\texttt{ST\_Length(geom::geography)} de PostGIS \cite{postgis}), el error medio obtenido es de apenas $0{,}465\text{ m}$ ($0{,}157$\,\%) y el error máximo absoluto es de $6{,}220\text{ m}$ ($0{,}272$\,\% en arcos kilométricos), margen plenamente aceptable para la navegación de UAVs.
\item \textbf{Generación de círculos de cobertura y exclusión:} Los radios métricos de antenas ($3.000\text{ m}$) y focos de calor ($2.000\text{ m}$) se convierten a incrementos angulares $(\Delta \lambda, \Delta \phi)$ considerando la curvatura meridiana:
\begin{equation}
\Delta \phi = \frac{R_m}{110.574}, \quad \Delta \lambda = \frac{R_m}{111.320 \cdot \cos(\phi)}
\end{equation}
donde $110.574\text{ m/grado}$ es la longitud de un grado de latitud a $-32{,}7^\circ$ y $111.320\text{ m/grado}$ es el factor ecuatorial. El perímetro se discretiza como un polígono regular cerrado de $n=32$ vértices:
\begin{equation}
\left( \lambda + \Delta \lambda \cos\left(\frac{2\pi i}{n}\right), \; \phi + \Delta \phi \sin\left(\frac{2\pi i}{n}\right) \right), \quad i \in \{0, \dots, n\}
\end{equation}
\item \textbf{Área superficial y orientación de anillos (RFC 7946):} Las áreas de manzanas y zonas urbanas se calculan en un plano tangente local a la latitud media $\phi_0$ ($x_i = R \cdot \lambda_i \cos\phi_0$, $y_i = R \cdot \phi_i$) aplicando la fórmula de Gauss (\textit{Shoelace}):
\begin{equation}
A = \frac{1}{2} \sum_{i=1}^{k} (x_i y_{i+1} - x_{i+1} y_i)
\end{equation}
Conforme a RFC 7946 \cite{rfc7946}, se asegura que el anillo exterior posea orientación antihoraria ($A > 0$) y los anillos interiores sigan sentido horario ($A < 0$).
\end{enumerate}

\subsection{Docker y Orquestación de Microservicios}
\label{subsec:docker_orquestacion}

El archivo \texttt{docker-compose.yml} define tres servicios especializados con versiones fijadas (ver Tabla~\ref{tab:docker}):

\begin{table}[H]
\centering
\small
\caption{Servicios definidos en \texttt{docker-compose.yml}.}
\label{tab:docker}
\begin{tabularx}{\linewidth}{llcY}
\toprule
\textbf{Servicio} & \textbf{Imagen / Versión} & \textbf{Puerto} & \textbf{Rol y Responsabilidad} \\
\midrule
\texttt{db} & \texttt{pgrouting/pgrouting:16-3.5-3.8.0} & \texttt{5433:5432} & PostgreSQL 16.9, PostGIS 3.5.2 y pgRouting 3.8.0. Persistencia en volumen \texttt{uav\_pgdata} y \textit{healthcheck} (\texttt{pg\_isready}). \\
\texttt{etl} & \texttt{uav-ruteo:local} (\texttt{python:3.12.15-slim}) & — & Ejecución de extractores, cargadores y ruteo. Dependencia fijada: \texttt{psycopg[binary]==3.2.13}. \\
\texttt{web} & \texttt{uav-ruteo:local} (\texttt{python:3.12.15-slim}) & \texttt{8000:8000} & Servidor HTTP estático nativo (\texttt{http.server}) en solo lectura (\texttt{:ro}) para el visor Leaflet. \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Ejecución desde Cero y Reproducibilidad}
\label{subsec:reproducibilidad}

Para reproducir el entorno desde cero en cualquier máquina con Docker y Docker Compose instalados, se ejecutan los siguientes comandos:

\begin{lstlisting}[language=bash]

# 1. Clonar el repositorio

git clone https://giteit.udp.cl/CIT3435/2026-2/trabajo-grupal/grupo09.git
cd grupo09

# 2. Ejecutar el pipeline completo (crea BD desde cero, descarga datos, carga y rutea)

python3 main.py

# Alternativa: reproducir sin conexion a internet usando los GeoJSON versionados

python3 main.py --sin-descarga

# 3. Acceder al visor cartografico interactivo en el navegador

# URL: http://localhost:8000/sitio_web/

\end{lstlisting}

Todo el procesamiento analítico y de base de datos ocurre dentro de los contenedores Docker; Python 3 en la máquina anfitriona solo es requerido como disparador de \texttt{main.py}.

% ============================== 6 ==============================
\section{Diseño e Implementación de la Base de Datos Espacial}
\label{sec:bd}

El modelo relacional-espacial se estructuró sobre PostgreSQL 16 con PostGIS y pgRouting. La inicialización se realiza mediante el script \texttt{bd/schema.sql}, el cual destruye cualquier versión previa y construye las tablas del modelo desde cero (ver Figura~\ref{fig:bd} y Tabla~\ref{tab:bd}).

\begin{figure}[H]
\centering
\imagen{0.95\linewidth}{bd_diagrama.png}
\caption{Diagrama de entidades y relaciones de la base de datos geoespacial (\texttt{bd/bd\_diagrama.puml}).}
\label{fig:bd}
\end{figure}

\begin{lstlisting}[language=SQL,caption={Extracto inicial de \texttt{bd/schema.sql} que evidencia la creación desde cero y extensiones.}]
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;

DROP TABLE IF EXISTS threat_event, meta_telecom_antenna, meta_obstacle, meta_census_block,
meta_edge_terrain, meta_air_quality, urban_zone,
infra_edge, infra_node, data_source CASCADE;

CREATE TABLE infra_edge (
id integer PRIMARY KEY,
source integer NOT NULL REFERENCES infra_node (id),
target integer NOT NULL REFERENCES infra_node (id),
length_m double precision NOT NULL,
cost double precision NOT NULL, -- ruta base: = length_m (pgr_dijkstra)
reverse_cost double precision NOT NULL,
geom geometry(LineString, 4326) NOT NULL
);
CREATE INDEX infra_edge_geom_idx ON infra_edge USING gist (geom);
\end{lstlisting}

\begin{table}[H]
\centering
\small
\caption{Esquema relacional y resumen de registros cargados en PostgreSQL.}
\label{tab:bd}
\begin{tabularx}{\linewidth}{llXr}
\toprule
\textbf{Tabla} & \textbf{Geometría} & \textbf{Contenido y Rol Operacional en la Red Base} & \textbf{Filas} \\
\midrule
\texttt{data\_source} & Ninguna & Catálogo de trazabilidad ETL (código, fuente, URL y marca UTC). & $11$ \\
\texttt{infra\_node} & \texttt{Point} (4326) & Red de $237$ nodos y vértices de cálculo para pgRouting. & $237$ \\
\texttt{infra\_edge} & \texttt{LineString} (4326) & Corredores aéreos no dirigidos (\texttt{cost} = \texttt{reverse\_cost} = \texttt{length\_m}). & $633$ \\
\texttt{urban\_zone} & \texttt{MultiPolygon} (4326) & Polígonos de consolidación urbana de las $8$ localidades de la bahía. & $8$ \\
\texttt{meta\_air\_quality} & \texttt{Point} (4326) & Mediciones horarias de calidad del aire vinculadas a estaciones SINCA. & $52$ \\
\texttt{meta\_edge\_terrain} & Ninguna & Perfiles altimétricos muestreados cada $100\text{ m}$ (FK $1:1$ a \texttt{infra\_edge}). & $633$ \\
\texttt{meta\_census\_block} & \texttt{MultiPolygon} (4326) & Manzanas censales del INE con población, viviendas y densidad. & $703$ \\
\texttt{meta\_telecom\_antenna} & \texttt{Point} y \texttt{Polygon} & Ubicación de mástiles celulares y áreas de cobertura estimada ($3.000\text{ m}$). & $25$ \\
\texttt{meta\_obstacle} & \texttt{Point} y \texttt{LineString} (4326) & Chimeneas industriales ($50\text{--}152\text{ m}$), líneas de alta tensión ($110/220\text{ kV}$) y torres. & $12$ \\
\texttt{threat\_event} & \texttt{Point} y \texttt{Polygon} & Eventos de amenazas dinámicas (\texttt{point\_geom} centro, \texttt{geom} afectación). & $34$ \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Integridad Referencial e Indexación Espacial GiST}
\label{subsec:bd_integridad}

\begin{enumerate}
\item \textbf{Integridad de llaves foráneas:} Las aristas en \texttt{infra\_edge} referencian estrictamente a \texttt{infra\_node(id)} en sus extremos \texttt{source} y \texttt{target}, garantizando la consistencia topológica exigida por pgRouting \cite{pgrouting}. La tabla \texttt{meta\_edge\_terrain} implementa una relación $1:1$ en cascada hacia \texttt{infra\_edge(id)}, y las tablas temáticas vinculan su procedencia hacia \texttt{data\_source(id)}.
\item \textbf{Indexación espacial GiST:} Se crearon índices \textit{Generalized Search Tree} (GiST) sobre todas las columnas geométricas (\texttt{infra\_node.geom}, \texttt{infra\_edge.geom}, \texttt{urban\_zone.geom}, \texttt{meta\_census\_block.geom}, \texttt{meta\_telecom\_antenna.coverage\_geom} y \texttt{threat\_event.geom}). Estos índices aceleran las consultas espaciales al filtrar candidatos por su caja envolvente mínima (\textit{bounding box}), reduciendo el espacio de búsqueda.
\item \textbf{Desacoplamiento entre Amenazas y Red:} La tabla \texttt{threat\_event} no define llaves foráneas rígidas hacia las aristas. La afectación se evalúa en tiempo de consulta mediante intersección geométrica espacial condicional:
\begin{lstlisting}[language=SQL]
ST_Intersects(infra_edge.geom, threat_event.geom) AND threat_event.exceeds = true
\end{lstlisting}
\end{enumerate}

% ============================== 7 ==============================
\section{Infraestructura de la Red de Vuelo}
\label{sec:infra}

\subsection{Justificación Territorial de la Red y Escala Espacial (Anillos 2 a 10 km)}
\label{subsec:infra_justificacion}

La delimitación geográfica de la red aérea y la disposición de sus nodos no responde a un mallado arbitrario, sino que se fundamenta rigurosamente en tres criterios físico-territoriales y normativos complementarios:

\begin{enumerate}
\item \textbf{Diseño concéntrico por gradiente de afectación (2, 4, 6, 8 y 10 km):}
Los estudios geoquímicos y ambientales más extensos realizados en la bahía —en particular las investigaciones de Aponte et al. (2021) sobre la dispersión de metales pesados desde la Fundición Ventanas \cite{aponte2021} y los análisis de kriging de acidez y cobre en suelos de González et al. (2014) \cite{gonzalez2014} y Tapia-Gatica et al. (2020) \cite{tapiagatica2020}— establecieron un diseño experimental basado en anillos concéntricos a \textbf{2, 4, 6, 8 y 10 km} desde el epicentro del cordón industrial. La evidencia constata que en los primeros $2\text{--}4\text{ km}$ sedimenta el material particulado grueso rico en cobre ($\text{Cu}$) y plomo ($\text{Pb}$), mientras que el $\text{SO}_2$ gaseoso y las fracciones finas se transportan en el corredor de sotavento hasta los $8\text{--}10\text{ km}$. La red de vuelo adopta este radio envolvente de $10\text{ km}$ como la cota máxima representativa de la cuenca.

\item \textbf{Radio administrativo de representatividad poblacional (2 km SMA):}
Para calificar una estación como representativa de la exposición humana (estación EMRP), la Superintendencia del Medio Ambiente y el Ministerio de Salud (D.S. 59/1998, D.S. 12/2011 MMA y D.S. 61/2008 modificado por D.S. 30/2009 MINSAL) exigen formalmente que el sensor se ubique dentro de un \textbf{radio de representatividad de 2 kilómetros} de un núcleo poblado. Este umbral es una delimitación administrativa que deja desprovistas de cobertura directa a las áreas periurbanas intermedias y los corredores de transporte de la pluma. El UAV cubre justamente esos vacíos intersticiales entre los radios de 2 km de cada estación.

\item \textbf{Delimitación por alcance físico del UAV ($R_{\max} = 10{,}5\text{ km}$):}
Conforme a la derivación analítica de la Ecuación~(\ref{eq:alcance_uav}) en S6, el radio de acción máximo del DJI Matrice 350 RTK para una misión completa que incluya $20\text{ min}$ de muestreo vertical estacionario y retorno seguro con $20$\,\% de reserva y viento en contra es de $10{,}5\text{ km}$. La red de vuelo permite alcanzar todas las fuentes y receptores del cordón de Ventanas y Quintero desde el aeródromo; no obstante, el extremo noreste (estación SINCA de Puchuncaví, a $14{,}41\text{ km}$ por el grafo) queda catalogado como un destino que demanda el establecimiento de una base de operaciones intermedia o el acotamiento de la misión sin retorno directo.
\end{enumerate}

\subsection{Estructura Nodal y Justificación de Estaciones de Muestreo}
\label{subsec:infra_nodos_detalle}

La red aérea consta de $237$ nodos clasificados funcionalmente en cuatro roles operativos:
\begin{itemize}
\item \textbf{Fuentes emisoras industriales ($32$ nodos):} Focos de emisión puntual (complejo termoeléctrico Nueva Ventanas, Campiche, refinería Codelco, terminales de hidrocarburos ENAP, GNL Quintero, plantas de asfalto y químicos). Su muestreo caracteriza la tasa de emisión inicial.
\item \textbf{Receptores residenciales sensibles ($41$ nodos de salud y educación):} Escuelas, jardines infantiles y centros de atención primaria (CESFAM Puchuncaví, Hospital Adriana Cousiño de Quintero, Posta Las Ventanas, Escuela La Greda), priorizados por albergar a la población de mayor vulnerabilidad frente a tóxicos respiratorios.
\item \textbf{Estaciones de calidad del aire SINCA ($8$ nodos en la red):} Nodos de co-localización sensorial. Entre ellos destacan los nuevos \textbf{Super-Sitios} de la red pública (Super-Sitio Ventanas y Super-Sitio Quintero, dotados de medición continua de 11 compuestos incluidos BTEX, $\text{H}_2\text{S}$ y meteorología completa), la estación histórica de Escuela La Greda, Puchuncaví Centro y la estación Los Maitenes (identificada por la SMA como receptora de plumas por viento sur).
\item \textbf{Nodos de control y fondo atmosférico (a barlovento):} Vértices costeros ubicados al sur-suroeste de la península (como Caleta Loncura y el borde costero abierto), los cuales, bajo régimen de brisa marina, reciben aire oceánico limpio libre de pluma industrial, sirviendo como línea base de contraste (control negativo).
\item \textbf{Corredores de paso e infraestructura auxiliar ($156$ nodos):} Vértices de conectividad sobre áreas comerciales, vialidad, hospedaje y la base aeroportuaria en SCER.
\end{itemize}

La Tabla~\ref{tab:justificacion_nodos_muestra} detalla una muestra representativa de nodos catastrados en el sistema, indicando su rol, distancia y azimut respecto a la Fundición Ventanas, anillo concéntrico y factibilidad de alcance directo desde SCER.

\begin{table}[H]
\centering
\small
\caption{Justificación funcional y geométrica de nodos representativos de la red.}
\label{tab:justificacion_nodos_muestra}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.2cm}p{3.0cm}ccccp{3.5cm}}
\toprule
\textbf{Código Nodo} & \textbf{Rol Operacional} & \textbf{Dist. Complejo} & \textbf{Azimut} & \textbf{Anillo} & \textbf{Alcance SCER} & \textbf{Justificación de Muestreo} \\
\midrule
\texttt{base\_scer} & Base despacho / RTH & $7{,}85\text{ km}$ & $215^\circ$ & $8\text{ km}$ & Origen ($0\text{ km}$) & Despacho, calibración y ascenso vertical inicial. \\
\texttt{fuente\_codelco} & Fuente / Obstáculo & $0{,}00\text{ km}$ & $0^\circ$ & Núcleo & Sí ($8{,}1\text{ km}$) & Chimenea $152\text{ m}$; refinería y hornos RAF activos. \\
\texttt{fuente\_campiche} & Fuente industrial & $0{,}82\text{ km}$ & $042^\circ$ & $2\text{ km}$ & Sí ($8{,}9\text{ km}$) & Termoeléctrica a carbón; chimenea $140\text{ m}$ con FGD. \\
\texttt{sinca\_ventanas} & Super-Sitio SINCA & $1{,}15\text{ km}$ & $320^\circ$ & $2\text{ km}$ & Sí ($7{,}6\text{ km}$) & Co-localización; monitoreo continuo de 11 compuestos. \\
\texttt{sinca\_lagreda} & Receptor / SINCA & $2{,}10\text{ km}$ & $075^\circ$ & $4\text{ km}$ & Sí ($9{,}8\text{ km}$) & Escuela vulnerable; zona de impacto por fumigación. \\
\texttt{sinca\_losmaitenes} & Receptor / SINCA & $2{,}85\text{ km}$ & $145^\circ$ & $4\text{ km}$ & Sí ($9{,}2\text{ km}$) & Receptor histórico de vientos de componente norte. \\
\texttt{sinca\_quintero} & Super-Sitio SINCA & $7{,}20\text{ km}$ & $220^\circ$ & $8\text{ km}$ & Sí ($2{,}4\text{ km}$) & Foco de COVs, hidrocarburos y terminal marítimo ENAP. \\
\texttt{sinca\_puchuncavi} & Receptor / SINCA & $9{,}45\text{ km}$ & $068^\circ$ & $10\text{ km}$ & \textbf{No} ($14{,}4\text{ km}$) & Población urbana interior; requiere base intermedia. \\
\texttt{ctrl\_costa\_sur} & Fondo / Control & $8{,}90\text{ km}$ & $205^\circ$ & $10\text{ km}$ & Sí ($3{,}1\text{ km}$) & Aire oceánico limpio a barlovento (blanco analítico). \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Obtención, Bloque ETL y Estructura GeoJSON}
\label{subsec:infra_obtencion_etl}

La extracción y modelado se automatiza mediante el script:
\begin{lstlisting}[language=bash]
python infraestructura/extraer_infraestructura.py
\end{lstlisting}
el cual genera los archivos normalizados según el estándar RFC 7946 \cite{rfc7946}:
\begin{itemize}
\item \textbf{Nodos (\texttt{nodos.geojson}, $237$ vértices):} Geometrías 3D de tipo \texttt{Point} con coordenadas WGS84 $\text{[longitud, latitud, altitud\_msnm]}$, incluyendo elevación superficial SRTM.
\item \textbf{Aristas (\texttt{aristas.geojson}, $633$ arcos conexos):} Generadas vinculando cada vértice a sus $K=4$ vecinos más cercanos por distancia geodésica Haversine y añadiendo deterministamente $2$ aristas puente mediante el algoritmo \textit{Union-Find} para salvar el cuerpo marino de la bahía.
\item \textbf{Zonas Urbanas (\texttt{zonas\_urbanas.geojson}, $8$ polígonos):} Huellas urbanas consolidadas para el cálculo de penalizaciones poblacionales.
\end{itemize}

Cada archivo GeoJSON contiene un bloque formal de metadatos \texttt{etl} que certifica fecha de ejecución, script generador y fuente, detallado en la Tabla~\ref{tab:json_infra}.

\begin{table}[H]
\centering
\small
\caption{Estructura de atributos en los archivos GeoJSON de infraestructura.}
\label{tab:json_infra}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.4cm}p{2.8cm}p{2.0cm}p{3.2cm}p{5.5cm}}
\toprule
\textbf{Archivo} & \textbf{Campo} & \textbf{Tipo} & \textbf{Unidad / Formato} & \textbf{Ejemplo Real en Dataset} \\
\midrule
\texttt{nodos.geojson} & \texttt{code} & String & Texto único & \texttt{"base\_scer"}, \texttt{"sinca\_ventanas"} \\
& \texttt{category} & String & Clasificación & \texttt{"base"}, \texttt{"sinca"}, \texttt{"health"} \\
& \texttt{elevation\_msnm} & Float & Metros s.n.m. & \texttt{28.0} \\
\midrule
\texttt{aristas.geojson} & \texttt{source}, \texttt{target} & Integer & ID de nodo & \texttt{1}, \texttt{14} \\
& \texttt{length\_m} & Float & Metros & \texttt{879.4} \\
& \texttt{cost}, \texttt{reverse\_cost} & Float & Metros & \texttt{879.4} \\
\midrule
\texttt{zonas\_urbanas.geojson} & \texttt{code} & String & Identificador & \texttt{"urban\_quintero"} \\
& \texttt{area\_km2} & Float & $\text{km}^2$ & \texttt{9.62} \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Carga Transaccional e Idempotencia}
\label{subsec:infra_carga}

La carga en PostgreSQL se ejecuta en orden estricto de integridad referencial:
\begin{lstlisting}[language=bash]
python infraestructura/cargar_nodos.py
python infraestructura/cargar_aristas.py
python infraestructura/cargar_zonas_urbanas.py
\end{lstlisting}
Cada cargador implementa transacciones ACID atómicas con limpieza preventiva (\texttt{DELETE FROM tabla}) antes de la inserción por lotes (\texttt{executemany}), asegurando idempotencia ante reejecuciones.

% ============================== 8 ==============================
\section{Metadata de Soporte Operacional}
\label{sec:metadata}

\subsection{Obtención, Fuentes y Filtro Espacial}
\label{subsec:metadata_obtencion}

Las cinco capas de metadatos operacionales se circunscriben a la caja envolvente de la bahía (longitud entre $-71{,}56^\circ$ y $-71{,}38^\circ$, latitud entre $-32{,}82^\circ$ y $-32{,}69^\circ$ WGS84) mediante cinco extractores modulares (ver Tabla~\ref{tab:metadata}).

\begin{table}[H]
\centering
\small
\caption{Fuentes de metadata integradas en el sistema.}
\label{tab:metadata}
\begin{tabularx}{\linewidth}{p{2.8cm}p{2.6cm}p{3.0cm}p{2.2cm}X}
\toprule
\textbf{Script ETL} & \textbf{Salida} & \textbf{Endpoint / Servicio} & \textbf{Datos} & \textbf{Resumen del Procesamiento} \\
\midrule
\texttt{ine\_manzanas} & \texttt{manzanas.json} & IDE SMA \cite{idesma} & Censo 2017 & $703$ manzanas censales; cálculo de densidad hab/$\text{km}^2$. \\
\addlinespace
\texttt{osm\_obstaculos} & \texttt{obstaculos.json} & Overpass API \cite{overpass} & En vivo & $12$ chimeneas ($50\text{--}152\text{ m}$ AGL) y líneas $110/220\text{ kV}$. \\
\addlinespace
\texttt{srtm\_relieve} & \texttt{relieve.json} & OpenTopoData \cite{opentopo} & SRTM 30m & Perfil altimétrico cada $100\text{ m}$ en $633$ aristas ($EEE$). \\
\addlinespace
\texttt{osm\_antenas} & \texttt{antenas.json} & Overpass API \cite{overpass} & En vivo & $25$ mástiles celulares con radio C2 de $3.000\text{ m}$. \\
\addlinespace
\texttt{sinca\_aire} & \texttt{calidad.json} & API SINCA \cite{sinca} & 19-10-2026 & Última concentración $\text{SO}_2, \text{MP}$; prioridad de misión. \\
\bottomrule
\end{tabularx}
\end{table}

\begin{table}[H]
\centering
\small
\caption{Marco conceptual y rol operacional de las capas de metadata en el enrutamiento UAV.}
\label{tab:metadata_roles}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.2cm}p{2.6cm}p{3.0cm}p{8.5cm}}
\toprule
\textbf{Metadata} & \textbf{Fuente Primaria} & \textbf{Dimensión Operacional} & \textbf{Rol en el Enrutamiento UAV} \\
\midrule
Población & INE (IDE SMA) & Riesgo en tierra & \textbf{Penalizar}: Incrementa el costo de aristas sobre zonas densamente pobladas según directrices SORA (GRC) y DAN 151. \\
\addlinespace
Obstáculos y tendido eléctrico & OSM (Overpass) & Riesgo en el aire & \textbf{Bloquear o penalizar}: Inhabilita aristas que intersectan chimeneas ($50\text{--}152\text{ m}$ AGL) y penaliza cruces de líneas de alta tensión ($110/220\text{ kV}$). \\
\addlinespace
Relieve orográfico & SRTM (OpenTopoData) & Terreno y energía & \textbf{Penalizar ascenso y verificar cota}: Verifica techo legal de $120\text{ m}$ AGL y penaliza consumo energético ($EEE$) por trepada gravitacional. \\
\addlinespace
Cobertura celular & OpenCelliD / OSM & Enlace de control C2 & \textbf{Penalizar zonas de sombra}: Penaliza corredores fuera de la cobertura 4G/LTE requerida para la telemetría continua de mando. \\
\addlinespace
Calidad del aire & SINCA (MMA) & Valor de la misión & \textbf{Priorizar destinos}: No modifica costos de aristas; define la recompensa $\mathcal{R}(d)$ para guiar la selección de destinos de muestreo. \\
\bottomrule
\end{tabular}%
}
\end{table}

\noindent \textbf{Definición estricta de cotas en obstáculos verticales:} Se declara expresamente que el atributo \texttt{height\_m} en la tabla \texttt{meta\_obstacle} mide exclusivamente la \textbf{altura física de la estructura sobre el nivel del suelo (AGL, Above Ground Level)}, corrigiendo cualquier ambigüedad con altitudes sobre el nivel del mar (s.n.m.). La chimenea mayor de Ventanas alcanza $152\text{ m}$ AGL, la chimenea de Campiche $140\text{ m}$ AGL y las torres de transmisión eléctrica entre $35$ y $45\text{ m}$ AGL.

\subsection{Carga Transaccional}
\label{subsec:metadata_carga}

La carga en base de datos se orquesta individualmente:
\begin{lstlisting}[language=bash]
python metadata/cargar_ine_manzanas.py # 703 filas
python metadata/cargar_osm_obstaculos.py # 12 filas
python metadata/cargar_srtm_relieve.py # 633 perfiles
python metadata/cargar_osm_antenas.py # 25 radiobases
python metadata/cargar_sinca_calidad_aire.py # 8 estaciones
\end{lstlisting}

% ============================== 9 ==============================
\section{Amenazas Operacionales y Validez de la Medición}
\label{sec:amenazas}

Un aporte metodológico fundamental de esta investigación radica en establecer una \textbf{distinción taxonómica formal entre dos tipos de contingencias}: las amenazas a la seguridad de la aeronave y las amenazas a la validez científica de la medición ambiental.

\subsection{Amenazas a la Seguridad de la Aeronave (Riesgo Físico de Colisión y Pérdida)}
\label{subsec:amenazas_aeronave}

Estas contingencias comprometen la integridad estructural del UAV o la seguridad de terceros en el espacio aéreo, justificando el \textbf{bloqueo estricto e inhabilitación temporal de las aristas afectadas}:

\begin{table}[H]
\centering
\small
\caption{Taxonomía de amenazas a la aeronave integradas en el sistema.}
\label{tab:amenazas_nave}
\begin{tabularx}{\linewidth}{p{2.6cm}p{2.2cm}p{2.8cm}p{2.8cm}Xc}
\toprule
\textbf{Amenaza} & \textbf{Script ETL} & \textbf{Endpoint / Servicio} & \textbf{Filtro Espacial} & \textbf{Modelo y Umbral} & \textbf{Activos} \\
\midrule
Focos de incendio activo & \texttt{firms.py} & NASA FIRMS \cite{firms} & AOI margen $0{,}3^\circ$ & Búfer circular $2.000\text{ m}$; conf. alta \cite{schroeder} & $1$ ($1$) \\
\addlinespace
Tráfico aéreo tripulado & \texttt{opensky.py} & OpenSky API \cite{opensky} & Patrón SCER & Cilindro $R=1.500\text{ m}$, cota $\le 1.000\text{ m}$ & $1$ ($1$) \\
\addlinespace
Viento crítico en altura & \texttt{viento.py} & Open-Meteo \cite{openmeteo} & Grilla $4 \times 4$ & Ráfaga $\ge 12\text{ m/s}$ a $120\text{ m}$ AGL \cite{dji} & $16$ ($0$) \\
\addlinespace
Niebla / camanchaca & \texttt{niebla.py} & Open-Meteo \cite{openmeteo} & Grilla $4 \times 4$ & Visibilidad $<1.000\text{ m}$ o $\text{HR} \ge 95$\% & $16$ ($8$) \\
\bottomrule
\end{tabularx}
\end{table}

\noindent \textbf{Justificación Operacional y Auditoría de Afectación:}
\begin{itemize}
\item \textbf{Incendios de Biomasa e Industriales (NASA FIRMS):} La detección satelital VIIRS de $375\text{ m}$ genera círculos de exclusión de $2.000\text{ m}$. El riesgo para la aeronave obedece a la pérdida súbita de sustentación por convección térmica extrema, visibilidad nula y riesgo crítico de colisión con aeronaves cisterna y helicópteros de CONAF.
\item \textbf{Tráfico Aéreo Tripulado en SCER (OpenSky Network ADS-B):} La aproximación visual civil y militar en Quintero posee prioridad irrestricta de paso según la DAN 151 \cite{dan151}. Una aeronave detectada a cota baja genera un cilindro de resguardo de $1.500\text{ m}$ de radio y $1.000\text{ m}$ de altura. En la corrida de calibración, el evento registrado con callsign \texttt{"CC-SCER1"} representa un \textit{evento de prueba / simulación de tráfico de aproximación} para validar la respuesta del sistema.
\item \textbf{Viento Crítico a $120\text{ m}$ AGL (Open-Meteo):} En la costa, la velocidad del viento a $120\text{ m}$ AGL es sensiblemente superior a la medida en suelo. Ráfagas sobre el umbral estructural de $12{,}0\text{ m/s}$ ($43{,}2\text{ km/h}$) del DJI Matrice 350 RTK \cite{dji} activan la condición de bloqueo No-Go.
\item \textbf{Niebla Costera y Visibilidad VMC (Open-Meteo):} Visibilidades horizontales inferiores a $1.000\text{ m}$ impiden la navegación visual y contravienen las condiciones VMC de la DAN 151, bloqueando los corredores litorales afectados.
\item \textbf{Auditoría de corte espacial sobre la ruta base de Dijkstra:} En la corrida de referencia, las amenazas activas (tráfico ADS-B en SCER y 8 celdas costeras de niebla matinal) \textbf{intersectan directamente aristas de la ruta base calculada por distancia}; al operar con costo igual a la longitud, el algoritmo clásico atraviesa ciegamente estas zonas prohibidas, demostrando la necesidad de penalizarlas en la fase de enrutamiento resiliente.
\end{itemize}

\subsection{Amenazas a la Validez Científica de la Medición Ambiental}
\label{subsec:amenazas_medicion}

A diferencia de las amenazas físicas a la aeronave, \textbf{una perturbación ambiental a la medición no vuelve peligrosa la zona, sino que falsea o invalida el dato recolectado}. Tratar estas variables como bloqueos de espacio aéreo constituye un error conceptual; su tratamiento consiste en la corrección matemática, el marcaje de la muestra como contaminada o la reprogramación de la ventana de vuelo:

\begin{table}[H]
\centering
\small
\caption{Matriz maestra de amenazas a la validez de la medición en la Bahía de Quintero.}
\label{tab:amenazas_medicion_matriz}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{2.8cm}p{3.8cm}p{2.4cm}p{2.6cm}p{2.4cm}p{3.4cm}}
\toprule
\textbf{Perturbación} & \textbf{Efecto Físico sobre el Sensor} & \textbf{Variable Medida} & \textbf{Fuente de Datos} & \textbf{Umbral Crítico} & \textbf{Acción en el Planificador} \\
\midrule
Humo de incendios & Aporte de MP y COVs de biomasa; altera firma química industrial & Foco activo a barlovento & NASA FIRMS VIIRS & Foco activo $\le 10\text{ km}$ a barlovento & Marcar muestra como afectada por biomasa (confusor). \\
\addlinespace
Humedad relativa alta & Crecimiento higroscópico; el sensor óptico sobrestima MP $\sim 5\times$ & Humedad relativa ($\text{HR}$) & Open-Meteo / Sensor in situ & $\text{HR} > 70\text{--}75$\,\% & Corregir mediante factor $\kappa$-Köhler o descartar MP. \\
\addlinespace
Aerosol marino (sal) & Sal higroscópica cuenta como MP; emisión biogénica de DMS (300--500 pptv, Seguel et al. \cite{seguel2023}) & Viento marino y oleaje & Open-Meteo Marine / CAMS & Brisa marina fuerte ($>6\text{ m/s}$) & Discriminar origen mediante razón $\text{MP}/\text{SO}_2$. \\
\addlinespace
Viento advectivo & Desplaza la pluma; determina si el sensor está dentro o fuera del núcleo & Vector y velocidad a $120\text{ m}$ & Open-Meteo / DMC & Dirección $\pm 20^\circ$ de la línea a fuente & Orientar la misión a sotavento; no bloquear. \\
\addlinespace
Lavado por lluvia (\textit{scavenging}) & Precipitación abate aerosoles solubles de la columna aérea & Lluvia acumulada & Open-Meteo & Lluvia en últimas $6\text{--}12\text{ h}$ & Registrar condición de lavado; no comparar con días secos. \\
\addlinespace
Buques fondeados & Emisiones de $\text{SO}_2$, $\text{NO}_x$ y COVs desde la rada exterior & Ubicación AIS de buques & Directemar / AIS & Buque a barlovento $\le 3\text{ km}$ & Registrar posible interferencia de fuente marina. \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsubsection{Crecimiento Higroscópico y Sensores Ópticos de Partículas}
El sesgo instrumental más crítico en el ambiente marino de Quintero corresponde al impacto de la humedad relativa sobre los contadores ópticos de partículas (OPC). Los sensores de bajo costo embarcables en UAVs no cuentan con columnas de secado térmico por restricciones de peso y potencia. Al operar en ambientes con $\text{HR} > 70\text{--}75$\,\%, las partículas higroscópicas absorben vapor de agua, hinchándose y aumentando drásticamente su diámetro óptico aparente. Investigaciones empíricas de calibración han demostrado que este fenómeno induce una **sobrestimación de masa de hasta un factor $\approx 5$** frente a monitores de referencia gravimétricos \cite{crilley2018,badura2018}. La literatura especializada modela este crecimiento mediante la teoría de $\kappa$-Köhler \cite{malings2024}:
\begin{equation}
C_{\text{real}} = \frac{C_{\text{medida}}}{1 + \kappa \cdot \frac{\text{HR}}{100 - \text{HR}}}
\label{eq:kohler}
\end{equation}
donde $\kappa$ representa el parámetro higroscópico empírico del aerosol (típicamente entre $0{,}1$ y $0{,}4$ para mezclas urbanas-marinas). Ignorar este factor en la bahía invalida cualquier perfil vertical matutino de material particulado.

\subsubsection{Compromiso Dinámico: Tiempo de Respuesta vs. Velocidad de Vuelo}
Un sensor electroquímico o fotoacústico posee una constante de tiempo de equilibrio $t_{90} \approx 10\text{--}30\text{ segundos}$ para alcanzar el $90$\,\% del valor real tras un escalón de concentración. Si el UAV transita a $v = 15\text{ m/s}$ a través de una pluma nocturna de ancho analítico $W \approx 290\text{ m}$ (conforme a la Ecuación~(\ref{eq:briggs}) para estabilidad F a $2\text{ km}$), el tiempo de residencia dentro del penacho es de solo $19{,}3\text{ s}$. En consecuencia, el sensor no alcanza el equilibrio analítico y reporta un pico diluido. Por esta razón, el sistema planifica protocolos de **vuelo estacionario (\textit{hovering}) de al menos $60\text{ s}$ en los nodos de muestreo**, garantizando la representatividad física de los perfiles verticales.

\subsection{Gestión Integral del Riesgo Operacional y de Medición (Matriz ISO 31000 / SORA)}
\label{subsec:matriz_riesgos}

Para consolidar la seguridad de vuelo y la validez analítica de los datos capturados, se formula una Matriz de Gestión de Riesgos conforme al estándar internacional ISO 31000 y las directrices SORA de JARUS \cite{sora}. Cada riesgo se evalúa mediante su Probabilidad ($P \in [1,5]$) y Severidad ($S \in [1,5]$), definiendo el Nivel de Riesgo Intrínseco como $R = P \times S$ (clasificado en Bajo: $1\text{--}6$, Medio: $8\text{--}12$ y Crítico: $15\text{--}25$), tal como se detalla en la Tabla~\ref{tab:matriz_riesgos}:

\begin{table}[H]
\centering
\small
\caption{Matriz maestra de gestión de riesgos operacionales y de medición ambiental.}
\label{tab:matriz_riesgos}
\resizebox{\linewidth}{!}{%
\begin{tabular}{cp{3.0cm}p{3.8cm}cccp{4.2cm}p{4.2cm}}
\toprule
\textbf{ID} & \textbf{Evento de Riesgo} & \textbf{Causa Raíz Fisiotécnica} & \textbf{$P$} & \textbf{$S$} & \textbf{Nivel} & \textbf{Mitigación Preventiva} & \textbf{Acción de Contingencia} \\
\midrule
\textbf{R1} & Pérdida de Mando y Control (\textit{Fly-Away} C2) & Atenuación en sombra celular 4G o interferencia electromagnética por cruce de líneas de $220\text{ kV}$. & $3$ & $4$ & \textbf{12 (Alto)} & Búfer de exclusión de $50\text{ m}$ sobre tendidos eléctricos; penalización en costo de aristas en sombra C2. & Activación de \textit{Fail-Safe}: ascenso a cota de seguridad de $120\text{ m}$ y retorno autónomo a base (RTH) por GPS. \\
\addlinespace
\textbf{R2} & Agotamiento Prematuro de Batería & Viento en contra no pronosticado a $120\text{ m}$ AGL ($>8\text{ m/s}$) durante el trayecto de regreso. & $3$ & $5$ & \textbf{15 (Crítico)} & Reserva estricta del $20$\,\% de batería; limitación del radio máximo a $10{,}5\text{ km}$; modelo $EEE$ con vector de viento. & Aterrizaje de emergencia preventivo en punto seguro predefinido o eyección de paracaídas balístico. \\
\addlinespace
\textbf{R3} & Distorsión de Muestra por \textit{Rotor Downwash} & Ingesta de aire turbulento mezclado por las palas en la cámara del sensor. & $4$ & $3$ & \textbf{12 (Alto)} & Montaje de sonda en mástil dorsal superior ($+40\text{ cm}$) sobre el plano de rotores con línea de PTFE inerte. & Descarte automático de mediciones capturadas durante maniobras de descenso vertical rápido ($>2\text{ m/s}$). \\
\addlinespace
\textbf{R4} & Falso Positivo de MP por Crecimiento Higroscópico & Humedad relativa $\text{HR} > 75$\,\% en bancos de camanchaca o brisa marina. & $5$ & $3$ & \textbf{15 (Crítico)} & Monitoreo continuo de HR in situ; aplicación en tiempo real del factor de corrección de $\kappa$-Köhler \cite{malings2024}. & Invalidar y marcar muestras de MP como «saturadas por aerosol higroscópico» si la humedad relativa $\text{HR} \ge 95$\,\%. \\
\addlinespace
\textbf{R5} & Subestimación de Pico por \textit{Spatial Smearing} & Vuelo a velocidad de crucero ($15\text{ m/s}$) atravesando penachos angostos ($<300\text{ m}$). & $4$ & $4$ & \textbf{16 (Crítico)} & Programación de aristas de muestreo a baja velocidad ($\le 3\text{ m/s}$) y puntos de \textit{hovering} de $60\text{ s}$ en nodos destino. & Aplicación de algoritmo numérico de deconvolución temporal basado en la constante $t_{90}$ de la celda de sensado. \\
\addlinespace
\textbf{R6} & Conflicto con Aviación Tripulada en SCER & Aeronave en aproximación visual VFR a pista activa en el Aeródromo de Quintero. & $2$ & $5$ & \textbf{10 (Medio)} & Integración ADS-B en vivo vía OpenSky Network; cilindro de exclusión dinámico de $1.500\text{ m}$ de radio y $1.000\text{ m}$ MSL. & Descenso inmediato a $30\text{ m}$ AGL y desvío táctico automático hacia la derecha del corredor según DAN 151 \cite{dan151}. \\
\addlinespace
\textbf{R7} & Corrosión Salina y Envenenamiento Químico & Niebla salina y condensación sobre la aviónica y sensores fotoiónicos PID. & $3$ & $3$ & \textbf{9 (Medio)} & Aeronave certificada IP55; purga con aire limpio mediante filtro de carbón activado al término de cada misión. & Cancelación de misión si la visibilidad horizontal es $<1.000\text{ m}$ (condición No-Go por pérdida de VMC). \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Carga Transaccional en Base de Datos}
\label{subsec:carga_amenazas}

La carga en la tabla espacial \texttt{threat\_event} se realiza mediante:
\begin{lstlisting}[language=bash]
python amenazas/cargar_firms_incendios.py # 1 fila (1 activa)
python amenazas/cargar_opensky_aeronaves.py # 1 fila (1 activa)
python amenazas/cargar_openmeteo_viento.py # 16 filas (0 activas)
python amenazas/cargar_openmeteo_niebla.py # 16 filas (8 activas)
\end{lstlisting}
En total se cargan exactamente \textbf{$34$ registros de amenazas dinámicas}. Cada registro almacena su geometría poligonal de afectación en \texttt{geom} y su centroide en \texttt{point\_geom}, permitiendo una auditoría topológica bidireccional contra el grafo aéreo.

\section{Algoritmo de Ruteo Base: \texorpdfstring{\texttt{pgr\_dijkstra}}{pgr\_dijkstra}}
\label{sec:ruteo_dijkstra}

Para caracterizar el comportamiento del sistema y definir una línea base de comparación, la ruta de referencia se calcula directamente en PostgreSQL utilizando la función \texttt{pgr\_dijkstra} de pgRouting \cite{pgrouting} sobre el costo métrico puro (\texttt{length\_m}), sin incorporar aún la metadata ni las amenazas en la ponderación de pesos.

El script \texttt{ruteo/ruta\_dijkstra.py} ejecuta la siguiente consulta SQL parametrizada desde la base (\texttt{base\_scer}) hacia cada una de las 8 estaciones SINCA:

\begin{lstlisting}[language=SQL,caption={Consulta SQL parametrizada ejecutada en \texttt{ruteo/ruta\_dijkstra.py}.}]
SELECT count(\*) FILTER (WHERE d.edge <> -1) AS tramos,
COALESCE(SUM(e.length_m), 0) AS longitud_m,
MAX(d.agg_cost) AS costo,
COUNT(DISTINCT d.node) AS nodos,
ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq)) AS linea
FROM pgr_dijkstra(
'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
(SELECT id FROM infra_node WHERE code = %s),
%s,
directed := false) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
JOIN infra_node n ON n.id = d.node;
\end{lstlisting}

\noindent \textbf{Justificación de Parámetros:} El parámetro \texttt{directed := false} y los costos simétricos (\texttt{cost} = \texttt{reverse\_cost} = \texttt{length\_m}) modelan los corredores aéreos como bidireccionales. La geometría calculada se exporta al archivo \texttt{sitio\_web/data/ruta\_dijkstra.geojson} para su despliegue cartográfico en Leaflet. Esta ruta representa el peor caso posible, sirviendo como benchmark cuantitativo contra el cual se contrastan cuantitativamente los esquemas de navegación resiliente multiobjetivo.

% ============================== 11 ==============================
\section{Plataforma Web Interactiva}
\label{sec:plataforma_web}

La visualización y auditoría geoespacial se implementó como una aplicación web desacoplada en Leaflet (v1.9.4) con HTML5 y CSS3, sirviendo directamente los archivos GeoJSON generados en el pipeline.

\subsection{Despliegue y Acceso Local}
\label{subsec:web_despliegue}

La aplicación se sirve mediante el microservicio \texttt{web} orquestado en Docker Compose:
\begin{lstlisting}[language=bash]

# Despliegue del contenedor web

docker compose up -d web

# URL de acceso local en el navegador

http://localhost:8000/sitio_web/
\end{lstlisting}

\subsection{Catálogo de Capas Cartográficas}
\label{subsec:web_capas}

El visor soporta mapas base \textit{OpenStreetMap} y \textit{Esri World Imagery}, integrando capas vectoriales con control de encendido independiente (ver Tabla~\ref{tab:capas_web}):

\begin{table}[H]
\centering
\small
\caption{Capas vectoriales desplegadas en la plataforma web Leaflet.}
\label{tab:capas*web}
\begin{tabularx}{\linewidth}{llY}
\toprule
\textbf{Grupo} & \textbf{Capa Geoespacial} & \textbf{Estilo Visual y Simbología en el Mapa} \\
\midrule
\textbf{Infraestructura} & Topología de Red & $237$ marcadores circulares clasificados por color ($13$ categorías); aristas grises de corredores aéreos bidireccionales. \\
& Zonas Urbanas & $8$ polígonos translúcidos violeta con borde continuo. \\
\midrule
\textbf{Metadata} & Calidad del Aire (SINCA) & Marcadores azules con popups interactivos de concentración ($\text{SO}\_2, \text{MP}*{10}, \text{MP}\_{2{,}5}$) y estado ambiental. \\
 & Relieve SRTM & Perfil interactivo que reporta elevación mínima, media, máxima y pendiente al hacer clic en cada arista. \\
 & Manzanas Censales (INE) & $703$ polígonos coloreados por gradiente de densidad habitacional ($> 2.500\text{ hab/km}^2$). \\
& Antenas Celulares (OSM) & Mástiles con círculos concéntricos de cobertura radioeléctrica de $3.000\text{ m}$ (verde translúcido). \\
\midrule
\textbf{Amenazas} & Incendios (NASA FIRMS) & Focos térmicos VIIRS ($375\text{ m}$) con círculo de exclusión de $2.000\text{ m}$ (rojo/ámbar de advertencia). \\
& Tráfico Aéreo (OpenSky ADS-B) & Aeronaves tripuladas con cilindro de exclusión de $1.500\text{ m}$ hasta $1.000\text{ m}$ MSL (derecho de paso DAN 151). \\
& Viento Operacional (Open-Meteo) & Grilla $4 \times 4$ a $120\text{ m}$ AGL; celdas que superan $12{,}0\text{ m/s}$ se iluminan como condición restrictiva. \\
& Niebla Costera (Open-Meteo) & Grilla $4 \times 4$; celdas con visibilidad $<1.000\text{ m}$ o $\text{HR} \ge 95$\,\% y nubes bajas $\ge 80$\,\% destacan como zona activa (restricción VMC). \\
\midrule
\textbf{Ruteo Base} & \texttt{pgr\_dijkstra} & Corredor continuo resaltado en magenta grueso, rotulado como \textbf{Línea Base del Peor Caso}. \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Interacción y Visualización de la Línea Base}
\label{subsec:web_interaccion}

El usuario puede seleccionar el nodo origen (\texttt{base\_scer}) y cualquiera de los destinos disponibles mediante una lista desplegable o haciendo clic directo sobre el marcador en el mapa. Al ejecutar la misión:
\begin{enumerate}
\item La plataforma renderiza la ruta calculada por \texttt{pgr\_dijkstra} en color magenta sobre la red.
\item Se abre una ventana modal interactiva con el resumen de métricas: longitud acumulada en metros y kilómetros, tiempo de vuelo a velocidad nominal $v = 15\text{ m/s}$, perfil de elevación y auditoría de exposición a áreas pobladas y sombras de antena.
\end{enumerate}

\begin{figure}[H]
\centering
\imagen{0.95\textwidth}{img_plataforma.PNG}
\caption{Visualizador cartográfico Leaflet desplegando la ruta base de mínima distancia (\texttt{pgr\_dijkstra}) hacia Puchuncaví, rotulada explícitamente como la línea base del peor caso de referencia. Mapa base: © OpenStreetMap contributors / Esri World Imagery.}
\label{fig:ruta_puchuncavi}
\end{figure}

% ============================== 12 ==============================
\section{Resultados y Análisis Cuantitativo del Ruteo Base}
\label{sec:resultados}

Para verificar la conectividad global y evaluar cuantitativamente el riesgo de la línea base, se ejecutaron simulaciones de navegación desde el Aeródromo de Quintero (\texttt{base\_scer}, cota $28\text{ msnm}$) hacia las estaciones SINCA y hacia $10$ receptores críticos de la bahía.

Las métricas analizadas corresponden a la longitud geodésica ($L$), número de aristas o saltos topológicos ($h$), tiempo de vuelo ($T_v$) a velocidad de crucero nominal unificada ($15\text{ m/s} = 54\text{ km/h}$, S6), desnivel orográfico ($\Delta z = z_{\text{destino}} - z_{\text{origen}}$) y la exposición cuantitativa calculada mediante intersección geométrica espacial sobre las capas de densidad censal y telecomunicaciones: kilómetros sobre manzanas densas ($>2.500\text{ hab/km}^2$) y kilómetros fuera de cobertura celular C2 ($>3.000\text{ m}$ de mástiles OSM).

\subsection{Resultados Numéricos de la Navegación hacia Estaciones SINCA}
\label{subsec:tabla_resultados_sinca}

La Tabla~\ref{tab:resultados_sinca} presenta las métricas operacionales hacia las $8$ estaciones de monitoreo SINCA del área de estudio:

\begin{table}[H]
\centering
\small
\caption{Métricas cuantitativas del ruteo base (\texttt{pgr\_dijkstra}) hacia las estaciones SINCA (costo = longitud).}
\label{tab:resultados_sinca}
\resizebox{\linewidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\textbf{Estación SINCA} & \textbf{Código} & \textbf{Distancia} & \textbf{Saltos} & \textbf{$T_v$ est. ($15\text{ m/s}$)} & \textbf{$\Delta z$} & \textbf{Sobre Manzanas Densas} & \textbf{Sin Cobertura C2} \\
\midrule
Centro Quintero & \texttt{sinca\_centro\_quintero} & $1{,}69\text{ km}$ & $6$ & $1{,}9\text{ min}$ & $-6{,}0\text{ m}$ & $0{,}39\text{ km}$ ($23{,}1$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Loncura & \texttt{sinca\_loncura} & $2{,}35\text{ km}$ & $4$ & $2{,}6\text{ min}$ & $-13{,}0\text{ m}$ & $0{,}09\text{ km}$ ($3{,}8$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Quintero (Super-Sitio) & \texttt{sinca\_quintero} & $2{,}35\text{ km}$ & $9$ & $2{,}6\text{ min}$ & $-10{,}0\text{ m}$ & $1{,}06\text{ km}$ ($45{,}1$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Sur & \texttt{sinca\_sur} & $3{,}74\text{ km}$ & $5$ & $4{,}2\text{ min}$ & $-3{,}0\text{ m}$ & $0{,}13\text{ km}$ ($3{,}5$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
La Greda & \texttt{sinca\_la\_greda} & $6{,}71\text{ km}$ & $11$ & $7{,}5\text{ min}$ & $+7{,}0\text{ m}$ & $0{,}39\text{ km}$ ($5{,}8$\,\%) & $3{,}33\text{ km}$ ($49{,}6$\,\%) \\
Ventanas (Super-Sitio) & \texttt{sinca\_ventanas} & $7{,}80\text{ km}$ & $14$ & $8{,}7\text{ min}$ & $-16{,}0\text{ m}$ & $0{,}70\text{ km}$ ($9{,}0$\,\%) & $4{,}41\text{ km}$ ($56{,}5$\,\%) \\
Campiche & \texttt{sinca\_campiche} & $9{,}53\text{ km}$ & $16$ & $10{,}6\text{ min}$ & $+2{,}0\text{ m}$ & $0{,}39\text{ km}$ ($4{,}1$\,\%) & $6{,}15\text{ km}$ ($64{,}5$\,\%) \\
Puchuncaví Centro & \texttt{sinca\_puchuncavi} & $14{,}41\text{ km}$ & $22$ & $16{,}0\text{ min}$ & $+67{,}0\text{ m}$ & $0{,}79\text{ km}$ ($5{,}5$\,\%) & $7{,}58\text{ km}$ ($52{,}6$\,\%) \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Resultados Numéricos en Receptores Críticos de la Bahía}
\label{subsec:tabla_resultados_otros}

La Tabla~\ref{tab:resultados_otros} resume los resultados obtenidos hacia diez receptores críticos (salud, industria, educación y comercio), validando la navegabilidad sobre las diversas categorías del grafo:

\begin{table}[H]
\centering
\small
\caption{Métricas de navegación hacia receptores críticos de la bahía.}
\label{tab:resultados_otros}
\resizebox{\linewidth}{!}{%
\begin{tabular}{llccccY}
\toprule
\textbf{Nodo Destino} & \textbf{Categoría} & \textbf{Distancia} & \textbf{Saltos} & \textbf{$T_v$ est. ($15\text{ m/s}$)} & \textbf{$\Delta z$} & \textbf{Observación Territorial} \\
\midrule
Hospital Adriana Cousiño & Salud & $1{,}43\text{ km}$ & $5$ & $1{,}6\text{ min}$ & $-8{,}0\text{ m}$ & Atraviesa centro densamente poblado de Quintero \\
CESFAM Las Ventanas & Salud & $8{,}05\text{ km}$ & $15$ & $8{,}9\text{ min}$ & $-12{,}0\text{ m}$ & Enlace costero norte con sectores en sombra C2 \\
Planta Asfaltos Quintero & Industria & $2{,}33\text{ km}$ & $4$ & $2{,}6\text{ min}$ & $-18{,}0\text{ m}$ & Istmo crítico de conexión interurbana \\
Terminal GNL Quintero & Industria & $2{,}74\text{ km}$ & $5$ & $3{,}0\text{ min}$ & $-23{,}0\text{ m}$ & Corredor costero industrial de baja cota \\
Fundición Codelco Ventanas & Industria & $5{,}28\text{ km}$ & $9$ & $5{,}9\text{ min}$ & $-15{,}0\text{ m}$ & Cordón de chimeneas industriales de Ventanas \\
Termoeléctrica Ventanas & Industria & $7{,}48\text{ km}$ & $13$ & $8{,}3\text{ min}$ & $-14{,}0\text{ m}$ & Proximidad a fuentes de emisión y efluentes térmicos \\
Colegio Don Orione & Educación & $1{,}86\text{ km}$ & $7$ & $2{,}1\text{ min}$ & $-5{,}0\text{ m}$ & Zona escolar residencial en Quintero \\
Escuela La Chocota & Educación & $9{,}77\text{ km}$ & $19$ & $10{,}9\text{ min}$ & $+14{,}0\text{ m}$ & Corredor rural hacia el sector norte \\
Colegio San Hernaldo & Educación & $13{,}67\text{ km}$ & $20$ & $15{,}2\text{ min}$ & $+58{,}0\text{ m}$ & Ascenso orográfico hacia el valle de Puchuncaví \\
Unimarc Quintero Centro & Comercial & $1{,}25\text{ km}$ & $5$ & $1{,}4\text{ min}$ & $-6{,}0\text{ m}$ & Máxima afluencia de personas en tierra \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Discusión y Hallazgos Cuantitativos Principales}
\label{subsec:discusion_resultados}

\begin{enumerate}
\item \textbf{Accesibilidad, Autonomía y Alcance Límite ($R_{\max} = 10{,}5\text{ km}$):} Con una velocidad nominal fijada en $v = 15\text{ m/s}$ y una autonomía operacional de $39{,}6\text{ km}$ ($44\text{ min}$ con reserva del $20$\,\%, S6):
\begin{itemize}
\item Las misiones hacia Quintero, Loncura y Sur ($1{,}69\text{ km}$ a $3{,}74\text{ km}$) requieren trayectos de ida y vuelta inferiores a $7{,}5\text{ km}$ ($<8{,}4\text{ min}$ de vuelo), consumiendo menos del $19$\,\% de la batería y garantizando autonomía para extensas campañas de muestreo estacionario.
\item Hacia el complejo industrial de Ventanas y La Greda ($6{,}71\text{ km}$ a $7{,}80\text{ km}$), el viaje completo de ida y retorno insume entre $13{,}4\text{ km}$ y $15{,}6\text{ km}$ ($15$ a $17{,}4\text{ min}$ de vuelo), utilizando el $39{,}4$\,\% de la capacidad operacional y permitiendo muestrear la pluma de chimeneas con seguridad.
\item Hacia la estación interior de Puchuncaví ($14{,}41\text{ km}$), el vuelo de ida y vuelta neto asciende a $28{,}82\text{ km}$ ($32\text{ min}$ de crucero). Al sumar los $20\text{ min}$ requeridos para el protocolo de muestreo vertical in situ ($18\text{ km}$ equivalentes), la demanda energética total asciende a $46{,}82\text{ km}$, sobrepasando la autonomía efectiva de $39{,}6\text{ km}$. Por lo tanto, \textbf{la estación de Puchuncaví queda formalmente fuera del alcance para una misión directa de ida y regreso desde SCER con muestreo}, confirmando que el radio seguro es de $10{,}5\text{ km}$ y demostrando cuantitativamente que Puchuncaví exige una base de recarga intermedia o un diseño de misión segmentado en los anillos concéntricos.
\end{itemize}
\item \textbf{Incidencia del Relieve Orográfico ($\Delta z$):} Los destinos costeros presentan desniveles negativos respecto al aeródromo ($\Delta z \in [-23{,}0; -3{,}0]\text{ m}$), mientras que las rutas hacia el interior ascienden sostenidamente: $+7{,}0\text{ m}$ en La Greda y $+67{,}0\text{ m}$ en Puchuncaví (alcanzando una cota absoluta de $95\text{ msnm}$ sobre la estación). Este hallazgo valida la integración del perfil SRTM continuo por arista para ajustar dinámicamente la cota sobre el terreno y asegurar el respeto estricto al límite legal de $120\text{ m}$ AGL de la norma DAN 151 \cite{dan151}.
\item \textbf{Evidencia Cuantitativa de la Exposición al Riesgo (Condición de Peor Caso):} Al optimizar únicamente la distancia geodésica, Dijkstra traza caminos que vulneran principios de seguridad operacional:
\begin{itemize}
\item \textit{Riesgo en tierra:} En Quintero Centro, el $45{,}1$\,\% de la ruta ($1{,}06\text{ km}$) sobrevuela directamente manzanas con densidad habitacional $>2.500\text{ hab/km}^2$, maximizando el riesgo a terceros (SORA).
\item \textit{Riesgo de pérdida de enlace (C2):} Hacia el norte de la bahía, las rutas atraviesan extensas sombras celulares: $3{,}33\text{ km}$ en La Greda ($49{,}6$\,\%), $4{,}41\text{ km}$ en Ventanas ($56{,}5$\,\%) y $7{,}58\text{ km}$ en Puchuncaví ($52{,}6$\,\% de la ruta total sin cobertura), exponiendo al UAV a pérdida prolongada de telemetría.
\item \textit{Intersección con amenazas activas:} La ruta base atraviesa directamente las celdas con niebla densa y el cilindro de resguardo ADS-B del aeródromo, confirmando que la distancia métrica por sí sola es un criterio inviable para la navegación autónoma.
\end{itemize}
\item \textbf{Régimen Aeronáutico y Restricción Legal de Línea de Vista (VLOS vs. BVLOS):} Conforme a la normativa chilena DAN 151 de la DGAC \cite{dan151}, la operación estándar de UAV está restringida a la línea de vista visual no asistida del piloto (VLOS, radio máximo general de $500\text{ m}$). Rutas de largo alcance como la proyectada hacia Puchuncaví ($14{,}41\text{ km}$) o hacia Ventanas ($7{,}80\text{ km}$) sobrepasan holgadamente dicho límite, constituyendo operaciones BVLOS que bajo la regulación chilena exigen una \textbf{Autorización Especial de Operación de la DGAC}, la cual supedita la misión a la acreditación de salvaguardas tecnológicas y análisis de riesgo SORA certificado. En la plataforma interactiva del sistema, cualquier trayectoria superior a $500\text{ m}$ es catalogada y alertada visualmente en color rojo como operación BVLOS condicionada.
\end{enumerate}

% ============================== 13 ==============================
\section{Verificación Automatizada del Sistema}
\label{sec:verificacion}

Para garantizar la consistencia relacional, integridad topológica y reproducibilidad del sistema, se diseñó la suite automatizada \texttt{tests/verificar.py}, la cual se ejecuta con:
\begin{lstlisting}[language=bash]
# Ejecucion en entorno local o dentro del contenedor Docker
python tests/verificar.py
\end{lstlisting}

La Tabla~\ref{tab:pruebas} resume los grupos de pruebas verificados:

\begin{table}[H]
\centering
\small
\caption{Suite de pruebas automatizadas implementada en \texttt{tests/verificar.py}.}
\label{tab:pruebas}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{4.2cm}cp{5.5cm}p{5.5cm}}
\toprule
\textbf{Grupo de Pruebas} & \textbf{Cantidad} & \textbf{Aspecto Auditado} & \textbf{Criterio de Aceptación} \\
\midrule
Componentes del sistema & $12$ & Esquema DDL, diagramas, scripts ETL, cargadores relacionales y visor web & Integridad estructural y dependencias fijadas \\
\addlinespace
Especificación GeoJSON & $11$ & Estructura RFC 7946, geometría válida y orientación de anillos de polígonos & Exterior antihorario, huecos horarios y rango WGS84 \\
\addlinespace
Documentación en Markdown & $11$ & Correspondencia entre campos del GeoJSON y archivo \texttt{.md} homónimo & $100$\,\% de propiedades documentadas entre comillas invertidas \\
\addlinespace
Configuración y Docker & $5$ & Versiones fijadas en Dockerfile, docker-compose y requirements & Python 3.12, pgRouting 16-3.5-3.8.0 y \texttt{==} \\
\addlinespace
Base de datos y pgRouting & $18$ & Conexión, conteo de filas, validez geométrica PostGIS y conexidad del grafo & Filas esperadas, $\text{ST\_IsValid} = \text{true}$ y $1$ componente \\
\bottomrule
\end{tabular}%
}
\end{table}

\noindent \textbf{Resultado de la Verificación:} Las $57$ pruebas automatizadas de estructura de datos, especificación GeoJSON y documentación se ejecutaron con éxito sin fallas ($57$ de $57$ correctas). Asimismo, en el entorno Docker con base de datos levantada, las pruebas relacionales confirmaron que la tabla \texttt{infra\_edge} conforma un grafo $100$\,\% conexo ($1$ componente) y que las longitudes precalculadas en \texttt{sitio\_web/data/ruta\_dijkstra.geojson} coinciden exactamente con la consulta de pgRouting ejecutada en vivo.

\subsection{Registro de Ejecución del Pipeline (\texorpdfstring{\texttt{main.py}}{main.py})}
\label{subsec:log_main}

El script \texttt{main.py} orquesta el pipeline completo en Docker. A continuación se reproduce el extracto del registro real obtenido al ejecutar el comando con el resumen de conteos finales en base de datos:

\begin{lstlisting}[language=bash]
== Docker: construir la imagen del ETL
== Base de datos: PostgreSQL 16 + PostGIS + pgRouting
== Base de datos: crear el esquema desde cero (bd/schema.sql)
== Carga a la BD — Nodos
== Carga a la BD — Aristas
== Carga a la BD — Zonas urbanas
== Carga a la BD — Calidad del aire (SINCA)
== Carga a la BD — Relieve por arista (SRTM)
== Carga a la BD — Manzanas (INE)
== Carga a la BD — Antenas (OSM)
== Carga a la BD — Incendios
== Carga a la BD — Aeronaves
== Carga a la BD — Viento
== Carga a la BD — Niebla
== Ruteo base: pgr_dijkstra desde la base hacia cada estacion SINCA (costo = longitud)
== Sitio web (Leaflet)
== Conteos en la BD
         tabla         | count 
-----------------------+-------
 infra_node            |   237
 infra_edge            |   633
 urban_zone            |     8
 meta_air_quality      |    52
 meta_edge_terrain     |   633
 meta_census_block     |   703
 meta_telecom_antenna  |    25
 threat_event          |    34
(8 filas)

Listo. Abre el sitio en: http://localhost:8000/sitio_web/
\end{lstlisting}

% ============================== 14 ==============================
\section{Conclusiones y Proyecciones}
\label{sec:conclusiones}

\subsection{Conclusiones y Respuestas a las Preguntas de Investigación}
\label{subsec:conclusiones_investigacion}

En esta investigación se diseñó, implementó y validó una infraestructura geoespacial integral y una metodología de evaluación de trayectorias aéreas para operaciones de muestreo ambiental con UAV en la Bahía de Quintero y Puchuncaví, respondiendo formalmente a las tres preguntas de investigación planteadas en la Sección~\ref{subsec:preguntas_diseno}:

\begin{enumerate}
\item \textbf{Respuesta a P1 (Integración automatizada y reproducibilidad):} Se comprobó la viabilidad de integrar de forma desatendida $9$ extractores de fuentes heterogéneas ($5$ capas de metadatos operacionales y $4$ capas de contingencias dinámicas) más la infraestructura de red geoespacial. La arquitectura de microservicios contenerizada en Docker, respaldada por la tabla maestra \texttt{data\_source}, asegura la trazabilidad inmutable de la procedencia y marca temporal UTC de cada ingesta, permitiendo regenerar el sistema desde cero o mediante la opción \texttt{--sin-descarga}.
\item \textbf{Respuesta a P2 (Conexidad y navegabilidad territorial):} La construcción topológica mediante $K=4$ vecinos y dos aristas puente Union-Find garantizó un grafo estrictamente conexo ($1$ sola componente conexa verificada con \texttt{pgr\_connectedComponents}) compuesto por $237$ nodos y $633$ aristas, asegurando la navegabilidad física hacia las estaciones SINCA y receptores críticos desde el aeródromo.
\item \textbf{Respuesta a P3 (Exposición cuantitativa de la línea base):} La evaluación sobre la ruta de Dijkstra confirmó numéricamente su vulnerabilidad como peor caso de referencia: la minimización de la distancia física expone la nave a $0{,}79\text{ km}$ sobre manzanas residenciales densas y a $7{,}58\text{ km}$ en sombras de cobertura celular C2 hacia Puchuncaví ($52{,}6$\,\% del trayecto), confirmando que la distancia por sí sola es un criterio insuficiente para la navegación segura. Asimismo, la distancia de ida y vuelta a Puchuncaví con protocolo de muestreo vertical ($46{,}8\text{ km}$ equivalentes) excede la autonomía del dron ($39{,}6\text{ km}$), demostrando cuantitativamente que el radio seguro es de $10{,}5\text{ km}$ y que el extremo noreste requiere bases intermedias de recarga.
\end{enumerate}

\subsection{Limitaciones de la Investigación}
\label{subsec:limitaciones_investigacion}

\begin{itemize}
\item \textbf{Topología con $K=4$ fija:} No se comparó la sensibilidad frente a otros valores de $K$, lo cual condiciona los corredores y concentra los enlaces en el istmo de Quintero.
\item \textbf{Corredores rectilíneos en plano 2D:} La ruta base se planifica sobre el plano territorial y la altitud se asigna por perfil continuo, sin optimizar maniobras tridimensionales cinemáticas complejas.
\item \textbf{Aproximaciones geométricas:} El cálculo de Haversine asume una esfera perfecta (error medio de $0{,}46\text{ m}$ frente a WGS84) y los círculos de exclusión se discretizan a $32$ vértices.
\item \textbf{Ventana temporal de FIRMS:} La ventana de 7 días puede incluir focos térmicos extinguidos al momento de la misión si no se filtra por hora de observación reciente.
\item \textbf{Desfase censal y subregistro C2:} El Censo 2017 puede subestimar áreas residenciales nuevas, y el catastro de OpenStreetMap sobrestima las zonas en sombra celular al no registrar todas las radiobases comerciales del territorio.
\end{itemize}

\subsection{Trabajo Futuro y Proyecciones}
\label{subsec:trabajo_futuro}

Para la Fase 3 del proyecto, se proyecta:
\begin{enumerate}
\item \textbf{Función de costo multiobjetivo con normalización z-score:} Formular una función de costo que pondere la longitud física, el riesgo a terceros (SORA), el balance energético con viento ($EEE$), la cobertura C2 y la penalización estricta por cruce de amenazas activas.
\item \textbf{Rutas alternativas disimilares ($k \ge 2$):} Implementar penalizaciones iterativas sobre las aristas transitadas para generar rutas secundarias con separación espacial efectiva ante contingencias dinámicas imprevistas.
\item \textbf{Protocolo RTH por sotavento:} Programar la lógica de retorno automático a base (RTH) aprovechando las zonas de abrigo orográfico y sotavento frente a vientos de frente, asegurando al menos un $15$\,\% de batería remanente al aterrizar.
\item \textbf{Integración horaria de la altura de mezcla ($h_{\text{mix}}$):} Incorporar pronósticos horarios de $h_{\text{mix}}$ para calcular la cota vertical óptima de vuelo en cada misión.
\end{enumerate}

\begin{thebibliography}{99}
\addcontentsline{toc}{section}{Referencias}

\bibitem{ppda_concon} Ministerio del Medio Ambiente [MMA]. (2018). \textit{Decreto Supremo N.º 105: Establece Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví} (modificado por D.S. N.º 39/2023 MMA). Santiago: Biblioteca del Congreso Nacional de Chile. Disponible en: \url{https://www.bcn.cl/leychile/navegar?idNorma=1130344}.

\bibitem{sma_enap} Superintendencia del Medio Ambiente [SMA]. (2025). \textit{Resolución Exenta N.º 05080/2025: Aprueba Plan Operacional de ENAP Terminal Marítimo Quintero en el marco del Capítulo I del PPDA Concón, Quintero y Puchuncaví}. Santiago: Gobierno de Chile.

\bibitem{sma_dictuc} DICTUC. (2020). \textit{Servicio de Modelación de calidad del aire para la zona de Quintero-Puchuncaví} (Informe Final N.º 1535747). Preparado para la Superintendencia del Medio Ambiente. Santiago, Chile.

\bibitem{mma_sinca_2021} Ministerio del Medio Ambiente. (2021). \textit{Informe nacional de calidad del aire: Redes de monitoreo oficiales}. Sistema Nacional de Información de Calidad del Aire (SINCA).

\bibitem{sma_estrategia_2023} Superintendencia del Medio Ambiente. (2023). \textit{Estrategia de fiscalización y monitoreo ambiental para el cordón industrial de Concón, Quintero y Puchuncaví}. Gobierno de Chile.

\bibitem{cr2_campana_2022} Centro de Ciencia del Clima y la Resiliencia [CR2]. (2022). \textit{Campaña de terreno Quintero 2022: Análisis de la capa límite atmosférica y perfiles térmicos mediante plataformas UAV}. Universidad de Chile.

\bibitem{cr2_informe} Centro de Ciencia del Clima y la Resiliencia [CR2]. (2023). \textit{Informe de devolución: Estudio de contaminantes atmosféricos, determinantes e impactos en la Bahía de Quintero-Puchuncaví}. Santiago: Universidad de Chile.

\bibitem{mma_plan_2023} Ministerio del Medio Ambiente. (2023). \textit{Plan de modernización de la Red Pública de Monitoreo de Calidad del Aire para Concón, Quintero y Puchuncaví}. Gobierno de Chile.

\bibitem{cifuentes} Cifuentes, L. (2018, 30 de agosto). \textit{Crisis en Quintero y Puchuncaví no se explica por los contaminantes que se miden}. Radio Pauta.

\bibitem{mma_drones} Radio Agricultura. (2023, 16 de junio). \textit{Quintero y Puchuncaví: Anuncian aumento de fiscalizadores, nuevos equipos de medición y mejoras en alcantarillados de colegios}.

\bibitem{sma_so2_2022} Superintendencia del Medio Ambiente [SMA]. (2022). \textit{Informe de fiscalización ambiental: Medición horaria extrema de SO2 estación Quintero} (Resolución Exenta N.º 20701004352). Santiago: Gobierno de Chile.

\bibitem{eldesconcierto_2023} El Desconcierto. (2023, 28 de mayo). \textit{Más de 500 intoxicaciones en lo que va del año: ¿Quién contamina la bahía de Quintero?}

\bibitem{sinca} Ministerio del Medio Ambiente [MMA]. (2026). \textit{Sistema de Información Nacional de Calidad del Aire (SINCA)}. Santiago: Gobierno de Chile. Disponible en: \url{https://sinca.mma.gob.cl}.

\bibitem{kosior} Kosior, M., Przystałka, P., \& Panfil, W. (2024). Adaptive Path Planning for UAV-Based Pollution Sampling. \textit{Applied Sciences}, 14(24), 12065. doi: \url{https://doi.org/10.3390/app142412065}.

\bibitem{dan151} Dirección General de Aeronáutica Civil [DGAC]. (2024). \textit{DAN 151: Operaciones de aeronaves pilotadas a distancia (RPAS) en asuntos de interés público, que se efectúen sobre áreas pobladas} (3.ª ed., Resolución Exenta N.º 1033 de 27 de mayo de 2024, Diario Oficial de Chile, 11 de marzo de 2025). Santiago: Gobierno de Chile.

\bibitem{sora} Joint Authorities for Rulemaking on Unmanned Systems [JARUS]. (2024). \textit{JARUS guidelines on Specific Operations Risk Assessment (SORA)} (Versión 2.5).

\bibitem{dijkstra} Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. \textit{Numerische Mathematik}, 1(1), 269--271. doi: \url{https://doi.org/10.1007/BF01386390}.

\bibitem{pgrouting} pgRouting Community. (2026). \textit{pgRouting Manual} (Versión 3.8.0). Disponible en: \url{https://docs.pgrouting.org/3.8/en/index.html}.

\bibitem{postgis} PostGIS Project Steering Committee. (2026). \textit{PostGIS 3.5.2 Manual}. Disponible en: \url{https://postgis.net/docs/manual-3.5/}.

\bibitem{yen} Yen, J. Y. (1971). Finding the $k$ shortest loopless paths in a network. \textit{Management Science}, 17(11), 712--716. doi: \url{https://doi.org/10.1287/mnsc.17.11.712}.

\bibitem{suurballe} Suurballe, J. W. (1974). Disjoint paths in a network. \textit{Networks}, 4(2), 125--145. doi: \url{https://doi.org/10.1002/net.3230040204}.

\bibitem{bhandari} Bhandari, R. (1999). \textit{Survivable Networks: Algorithms for Diverse Routing}. Boston, MA: Kluwer Academic Publishers.

\bibitem{akgun} Akgün, V., Erkut, E., \& Batta, R. (2000). On finding dissimilar paths. \textit{European Journal of Operational Research}, 121(2), 232--246. doi: \url{https://doi.org/10.1016/S0377-2217(99)00214-3}.

\bibitem{petritoli} Petritoli, E., Leccese, F., \& Ciani, L. (2018). Reliability and maintenance analysis of unmanned aerial vehicles. \textit{Sensors}, 18(9), 3171. doi: \url{https://doi.org/10.3390/s18093171}.

\bibitem{schroeder} Schroeder, W., Oliva, P., Giglio, L., \& Csiszar, I. A. (2014). The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment. \textit{Remote Sensing of Environment}, 143, 85--96. doi: \url{https://doi.org/10.1016/j.rse.2013.12.008}.

\bibitem{rfc7946} Butler, H., Daly, M., Doyle, A., Gillies, S., Hagen, S., \& Schaub, T. (2016). \textit{The GeoJSON Format} (RFC 7946). Internet Engineering Task Force (IETF). doi: \url{https://doi.org/10.17487/RFC7946}.

\bibitem{dji} DJI Enterprise. (2024). \textit{DJI Matrice 350 RTK: Especificaciones técnicas oficiales}. Disponible en: \url{https://enterprise.dji.com/matrice-350-rtk/specs}.

\bibitem{opentopo} OpenTopoData. (2026). \textit{SRTM 30 m Elevation API}. Disponible en: \url{https://www.opentopodata.org}.

\bibitem{idesma} Superintendencia del Medio Ambiente [SMA]. (2026). \textit{Infraestructura de Datos Geoespaciales: Capa de manzanas censales (INE, Censo 2017)}. Santiago: IDE SMA.

\bibitem{overpass} OpenStreetMap Contributors. (2026). \textit{Overpass API: OpenStreetMap Data Extraction}. Disponible en: \url{https://overpass-api.de}.

\bibitem{firms} National Aeronautics and Space Administration [NASA]. (2026). \textit{Fire Information for Resource Management System (FIRMS)}. NASA Earthdata.

\bibitem{opensky} Schäfer, M., Strohmeier, M., Lenders, V., Martinovic, I., \& Wilhelm, M. (2014). Bringing up OpenSky: A large-scale ADS-B sensor network for research. En \textit{Proceedings of the 13th International Symposium on Information Processing in Sensor Networks (IPSN)} (pp. 83--94). Berlin: IEEE/ACM. doi: \url{https://doi.org/10.1109/IPSN.2014.6846743}.

\bibitem{openmeteo} Open-Meteo. (2026). \textit{Weather Forecast and Marine API: Wind Vectors, Fog, and Low Cloud Cover}. Disponible en: \url{https://open-meteo.com}.

\bibitem{aponte2021} Aponte, C., et al. (2021). Environmental assessment of trace elements in soils surrounding the Ventanas copper smelter, Chile. \textit{Science of the Total Environment}, 779, 146423. doi: \url{https://doi.org/10.1016/j.scitotenv.2021.146423}.

\bibitem{gonzalez2014} González, I., et al. (2014). Spatial distribution of copper and soil acidity near a copper smelter in central Chile. \textit{Journal of Soil Science and Plant Nutrition}, 14(4), 943--953. doi: \url{https://doi.org/10.4067/S0718-95162014005000075}.

\bibitem{tapiagatica2020} Tapia-Gatica, J., et al. (2020). Source apportionment of heavy metals in topsoils around an industrial complex in central Chile. \textit{Environmental Pollution}, 256, 113488. doi: \url{https://doi.org/10.1016/j.envpol.2019.113488}.

\bibitem{crilley2018} Crilley, L. R., et al. (2018). Evaluation of a low-cost optical particle counter (Alphasense OPC-N2) for ambient air monitoring: In situ calibration and hygroscopic growth. \textit{Sensors}, 18(9), 2790. doi: \url{https://doi.org/10.3390/s18092790}.

\bibitem{badura2018} Badura, M., et al. (2018). Evaluation of low-cost sensors for particulate matter monitoring: Relative humidity interference. \textit{Journal of Sensors}, 2018, 5096540. doi: \url{https://doi.org/10.1155/2018/5096540}.

\bibitem{malings2024} Malings, C., et al. (2024). Application of $\kappa$-Köhler theory for the correction of optical particle sensors under elevated relative humidity. \textit{Atmospheric Measurement Techniques}, 17(3), 1051--1070. doi: \url{https://doi.org/10.5194/amt-17-1051-2024}.

\bibitem{seguel2023} Seguel, R., et al. (2023). Biogenic and anthropogenic volatile organic compounds in a highly industrialized coastal embayment: The case of Quintero Bay. \textit{Atmospheric Environment}, 294, 119500. doi: \url{https://doi.org/10.1016/j.atmosenv.2022.119500}.

\bibitem{briggs1973} Briggs, G. A. (1973). \textit{Diffusion Estimation for Small Emissions}. Atmospheric Turbulence and Diffusion Laboratory (ATDL) Contribution File No. 79. Oak Ridge, TN: National Oceanic and Atmospheric Administration (NOAA).

\bibitem{galle2021} Galle, B., Arellano, S., Bobrowski, N., et al. (2021). A multi-purpose, multi-rotor drone system for long-range and high-altitude volcanic gas and plume measurements. \textit{Atmospheric Measurement Techniques}, 14(6), 4255--4277. doi: \url{https://doi.org/10.5194/amt-14-4255-2021}.

\end{thebibliography}

\end{document}
