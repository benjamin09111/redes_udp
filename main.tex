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
{\fbox{\parbox[c][3cm][c]{\dimexpr#1-2\fboxsep-2\fboxrule\relax}{\centering\small Imagen de referencia:\\\texttt{\detokenize{#2}}}}}}}

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
\section*{Resumen Ejecutivo}
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

El cordón industrial y litoral de la Bahía de Quintero, Ventanas y Puchuncaví constituye una de las zonas de mayor vulnerabilidad socio-ambiental de Chile, declarada zona saturada y sujeta prioritariamente a las medidas del Plan de Prevención y Descontaminación Atmosférica (PPDA) de Concón, Quintero y Puchuncaví mediante el Decreto Supremo N.º 105 del Ministerio del Medio Ambiente \cite{ppda_concon}. En este territorio conviven núcleos urbanos densamente poblados, establecimientos educacionales y centros de salud con un complejo polo industrial integrado por fundiciones de cobre, complejos termoeléctricos a carbón, terminales marítimos de hidrocarburos, plantas químicas y terminales de gas natural licuado.

Para la vigilancia ambiental, el Estado opera una red de estaciones fijas pertenecientes al Sistema de Información Nacional de Calidad del Aire (SINCA) \cite{sinca}. No obstante, la evidencia empírica acumulada durante la última década ha demostrado que las estaciones superficiales presentan una severa limitación estructural: miden exclusivamente a nivel de suelo y están geográficamente inmóviles, resultando incapaces de detectar la estratificación tridimensional de los gases contaminantes antes de que estos impacten a la población.

\subsection{El Mecanismo Físico Vertical y el Reconocimiento del Estado Chileno}
\label{subsec:mecanismo_vertical}

La dinámica de dispersión de contaminantes en este litoral está gobernada por fenómenos meteorológicos verticales reconocidos explícitamente en los instrumentos regulatorios de la República de Chile. Las resoluciones oficiales de la Superintendencia del Medio Ambiente (SMA) que aprueban los planes operacionales de las empresas del cordón industrial —como la Resolución Exenta N.º 05080/2025 que aprueba el Plan Operacional de ENAP Terminal Marítimo Quintero \cite{sma_enap}— fundamentan sus exigencias citando directamente el Capítulo I del PPDA (D.S. N.º 105/2019 MMA) \cite{ppda_concon}.

En dicho marco legal, el Estado formaliza que los episodios críticos de contaminación atmosférica se originan por la conjunción de dos factores físico-meteorológicos de escala vertical:
\begin{enumerate}
    \item \textbf{Inversión térmica marina de subsidencia:} Fenómeno donde una capa de aire cálido en altura actúa como una tapa impermeable que inhibe la dispersión turbulenta vertical de los efluentes. El propio texto del PPDA establece que la frecuencia, intensidad y altitud de la base de dicha inversión condicionan críticamente la capacidad de ventilación y la calidad del aire de la bahía.
    \item \textbf{Fenómeno de ``fumigación costera'':} Proceso derivado del rápido crecimiento matutino de la capa de mezcla térmica inducido por la radiación solar diurna sobre el litoral. Al erosionarse la inversión térmica desde abajo, la turbulencia intercepta súbitamente los penachos de contaminantes que habían quedado atrapados y concentrados en las capas superiores de la atmósfera, precipitándolos bruscamente hacia el nivel del suelo donde se asientan las comunidades residenciales y escolares.
\end{enumerate}

En consecuencia, el propio marco normativo chileno consagra una premisa irrefutable: \textbf{lo que ocurre en la dimensión vertical de la atmósfera explica y determina directamente la concentración de tóxicos que impacta en el suelo}.

\subsection{Evidencia Empírica de la Crisis: Estudios SMA, Brecha Instrumental y Precedentes}
\label{subsec:evidencia_empirica}

La necesidad de caracterizar la columna vertical no es una conjetura teórica, sino una urgencia empírica demostrada por estudios periciales oficiales y antecedentes científicos en la bahía:

\begin{enumerate}
    \item \textbf{El estudio oficial SMA / Dictuc (2020) sobre la crisis de agosto de 2018:}
    El informe pericial n.º 1535747 de la Superintendencia del Medio Ambiente y Dictuc, titulado \textit{Servicio de modelación de calidad del aire para la zona de Quintero-Puchuncaví} \cite{sma_dictuc}, analizó la crisis ambiental que intoxicó a cientos de personas entre el 21 y el 23 de agosto de 2018. El estudio constató que el 21 de agosto se configuró una aguda inversión térmica a aproximadamente $400\text{ m}$ sobre el nivel del suelo, impidiendo por completo la mezcla vertical.
    
    \item \textbf{La grave brecha instrumental vertical (Radiosondeo a 100 km):}
    Para poder reconstruir el perfil vertical de temperatura y viento en la modelación de la crisis de 2018, los peritos de la SMA y Dictuc debieron recurrir a los radiosondeos de la estación meteorológica de \textbf{Santo Domingo, ubicada a 100 km al sur de Quintero}, ante la inexistencia total de mediciones verticales locales en la Bahía de Quintero \cite{sma_dictuc}. Esta alarmante brecha geográfica e instrumental de $100\text{ km}$ representa con exactitud la necesidad técnica que resuelve un Vehículo Aéreo No Tripulado (UAV) dotado de instrumentación atmosférica.

    \item \textbf{La desconexión analítica de la red superficial vs. las intoxicaciones masivas:}
    Durante los días más agudos de la emergencia (21 al 23 de agosto de 2018), la concentración horaria de dióxido de azufre ($\text{SO}_2$) en las estaciones terrestres del SINCA \textbf{nunca superó la norma horaria chilena de $350\ \mu\text{g/m}^3\text{N}$} \cite{sma_dictuc}. Sin embargo, se produjo una masiva concurrencia hospitalaria de escolares y vecinos con síntomas de intoxicación neurotóxica. El informe de la SMA constató que la intoxicación no fue causada por el $\text{SO}_2$ normado, sino por otros compuestos químicos volátiles, advirtiendo taxativamente que en la zona industrial de Ventanas \textbf{no existía monitoreo continuo de Compuestos Orgánicos Volátiles (BTEX: benceno, tolueno, etilbenceno, xilenos), formaldehído (HCHO) ni sulfuro de hidrógeno ($\text{H}_2\text{S}$)} \cite{sma_dictuc}.

    \item \textbf{Diagnóstico de la comunidad científica:}
    Durante el desarrollo de la crisis, el académico de la Pontificia Universidad Católica de Chile, Luis Cifuentes, advirtió categóricamente que la crisis de salud pública no se explicaba por los contaminantes tradicionales que se miden habitualmente en Chile (los normados en la red SINCA), evidenciando la incapacidad de la infraestructura fija para caracterizar el cóctel de emisiones reales \cite{cifuentes}.

    \item \textbf{Precedentes de despliegue científico de UAVs en Quintero:}
    El uso de drones para abordar este vacío instrumental cuenta con antecedentes directos en la zona. El Centro de Ciencia del Clima y la Resiliencia (CR2, Universidad de Chile) lideró una campaña de medición intensiva en la Bahía de Quintero-Puchuncaví para capturar contaminantes no monitoreados por la red pública (como benceno y tolueno), realizando registros de perfiles térmicos verticales mediante drones y radiosondeos locales \cite{cr2_informe}.

    \item \textbf{Compromiso institucional del Estado chileno:}
    En junio de 2023, el Ministerio del Medio Ambiente anunció formalmente su plan de fiscalización atmosférica para Quintero y Puchuncaví, incorporando de manera explícita el fortalecimiento de la vigilancia mediante sensores atmosféricos montados en drones \cite{mma_drones}. Este anuncio gubernamental confirma que el problema es contemporáneo y que la propia autoridad ambiental identifica a los UAVs como la solución tecnológica prioritaria.

    \item \textbf{Persistencia y recurrencia de los episodios:}
    Los eventos críticos continúan afectando a la comunidad. El 6 de junio de 2022, la estación Quintero registró un pico horario extremo de $\text{SO}_2$ de $1.327\ \mu\text{g/m}^3\text{N}$, cuadruplicando la norma primaria \cite{sma_so2_2022}. Asimismo, durante el primer semestre de 2023 se registraron más de 500 consultas médicas por intoxicación aguda; los estudios del CR2 demostraron que tales episodios obedecieron a emisiones de Compuestos Orgánicos Volátiles (COVs) y no al $\text{SO}_2$ de las termoeléctricas \cite{eldesconcierto_2023}.
\end{enumerate}

\subsection{Planteamiento del Problema: La Cadena Lógica y el Enfoque en Enrutamiento Resiliente}
\label{subsec:problema}

Los antecedentes expuestos articulan una rigurosa \textbf{cadena lógica de cinco eslabones}:
\begin{enumerate}
    \item Los episodios de contaminación dependen críticamente de la estructura meteorológica vertical: la inversión térmica marina atrapa los efluentes en altura y la fumigación costera los precipita sobre la población (PPDA \cite{ppda_concon}, SMA \cite{sma_dictuc}).
    \item No existen mediciones de perfil vertical locales en la bahía: en la crisis de 2018 la autoridad debió recurrir a un radiosondeo a $100\text{ km}$ de distancia en Santo Domingo \cite{sma_dictuc}.
    \item La red de estaciones terrestres fijas no mide todos los compuestos tóxicos causantes del daño: el $\text{SO}_2$ estuvo bajo norma mientras la población se intoxicaba con COVs no monitoreados \cite{sma_dictuc,cr2_informe,cifuentes}.
    \item Los UAVs ya se utilizan científicamente en la zona \cite{cr2_informe} y el Ministerio del Medio Ambiente los incorporó en su plan de fiscalización \cite{mma_drones}.
    \item \textbf{El UAV requiere una trayectoria de vuelo segura, robusta y resiliente en un entorno costero de alto riesgo operático.}
\end{enumerate}

\noindent \textbf{Pivote central de la investigación:} Es crucial enfatizar que \textbf{el objeto del presente proyecto no es el desarrollo de sensores químicos ni la simulación fisicoquímica de la atmósfera}. Los eslabones 1 a 4 justifican formalmente \textbf{por qué es imprescindible volar en la Bahía de Quintero y Puchuncaví}. El problema científico e ingenieril que resuelve este trabajo radica en el eslabón 5: \textbf{¿Cómo planificar de forma automatizada y resiliente las rutas de vuelo de un UAV para que cumpla sus misiones de monitoreo minimizando la exposición a las severas amenazas del espacio aéreo y el terreno?}

El espacio aéreo y el entorno operacional de la Bahía de Quintero y Puchuncaví imponen restricciones sumamente exigentes que imposibilitan una navegación ingenua:
\begin{itemize}
    \item \textbf{Riesgo a terceros en tierra sobre áreas densamente pobladas:} Sobrevolar manzanas urbanas con densidades superiores a $2.500\text{ hab/km}^2$ en Quintero y Ventanas incrementa de forma crítica la clase de riesgo intrínseco en tierra (\textit{Ground Risk Class}, GRC) según la metodología internacional SORA \cite{sora} y transgrede las exigencias de seguridad pública de la norma chilena DAN 151 \cite{dan151}.
    \item \textbf{Obstáculos verticales industriales severos:} El cordón industrial presenta estructuras físicas de gran cota verificadas en los expedientes ambientales del SEIA, tales como la chimenea de la Fundición Ventanas de Codelco ($152\text{ m}$ de altitud física), la chimenea de la Termoeléctrica Campiche ($140\text{ m}$) y las unidades de Ventanas ($110\text{--}120\text{ m}$), a lo que se suman múltiples líneas de transmisión eléctrica de alta tensión ($110/220\text{ kV}$) que cruzan los valles litorales.
    \item \textbf{Segregación y conflicto con aviación tripulada:} Las operaciones de aproximación visual hacia la pista activa del Aeródromo de Quintero (SCER) poseen derecho de paso preferente y exigen zonas de resguardo cilíndricas que el UAV no puede vulnerar.
    \item \textbf{Condicionantes meteorológicas y ambientales adversas:} Ráfagas de viento costero que superan los $12\text{ m/s}$ a $120\text{ m}$ AGL (límite estructural de aeronaves industriales estándar como el DJI Matrice 350 RTK \cite{dji}), bancos densos de niebla y camanchaca marina que anulan la visibilidad visual mínima (condiciones VMC de la DAN 151), e incendios forestales que inducen cizalladura térmica.
    \item \textbf{Régimen de vuelo BVLOS y exigencia normativa chilena:} Una trayectoria de largo alcance entre el Aeródromo de Quintero y la estación SINCA de Puchuncaví ($14{,}41\text{ km}$) excede holgadamente la línea de vista visual del piloto ($\text{VLOS} \le 500\text{ m}$), clasificándose formalmente como una operación BVLOS (\textit{Beyond Visual Line of Sight}) que bajo la normativa DAN 151 de la DGAC requiere de una \textbf{autorización especial previa y sistemas de mitigación operacional certificados}.
\end{itemize}

Planificar una ruta basándose exclusivamente en la distancia mínima geodésica mediante un algoritmo clásico como Dijkstra ignora ciegamente estos riesgos, guiando al dron directamente a través de zonas densamente pobladas, sombras de telecomunicación o áreas de colisión. De allí surge la necesidad de formular una plataforma integral de modelado geoespacial y enrutamiento resiliente.

\subsection{Síntesis de Antecedentes, Brechas Identificadas y Enfoque del Proyecto}
\label{subsec:sintesis_brechas}

Para dimensionar con precisión la necesidad operativa y el estado del arte en la Bahía de Quintero y Puchuncaví, la Tabla~\ref{tab:que_existe} sintetiza qué iniciativas se han implementado, qué instituciones las llevaron a cabo y cuál es la brecha específica que dejan pendiente:

\begin{table}[H]
\centering
\small
\caption{Síntesis comparativa: iniciativas existentes, autores y brechas operacionales pendientes.}
\label{tab:que_existe}
\begin{tabularx}{\linewidth}{p{4.8cm}p{4.2cm}X}
\toprule
\textbf{Qué existe} & \textbf{Quién lo hizo} & \textbf{Qué deja pendiente (Brecha)} \\
\midrule
Estaciones fijas que miden a nivel de suelo; solo el $\text{SO}_2$ tiene norma horaria & Red oficial del Ministerio del Medio Ambiente (SINCA) \cite{mma_sinca_2021} & No ven lo que pasa en altura ni monitorean todos los compuestos tóxicos \\
\addlinespace
Más sensores fijos en colegios (2022) y en empresas (2023) & Superintendencia del Medio Ambiente (SMA) \cite{sma_estrategia_2023} & Siguen siendo puntos fijos en tierra sin cobertura tridimensional \\
\addlinespace
Estudio pericial de la crisis de 2018: inversión térmica a $\approx 400\text{ m}$; perfil vertical tomado de radiosondeo a $100\text{ km}$ & Estudio UC--Dictuc para la Superintendencia del Medio Ambiente \cite{sma_dictuc} & Inexistencia total de mediciones meteorológicas en altura en Quintero \\
\addlinespace
Drones en Quintero para registros térmicos (campaña de investigación de campo) & Universidad de Chile, CR2 \cite{cr2_campana_2022} & Despliegue científico puntual, sin operación regular ni planificador de rutas \\
\addlinespace
Compromiso de usar drones con sensores atmosféricos en fiscalización & Ministerio del Medio Ambiente (MMA) \cite{mma_plan_2023} & Sin información pública sobre su implementación operacional efectiva \\
\addlinespace
Planificador de rutas para drones que muestrean contaminación (global previo al vuelo y local reactivo) & Kosior et al., Universidad Tecnológica de Silesia, Polonia \cite{kosior} & Formulado para drones de gran altitud (HALE) en Europa, no adaptado a Quintero \\
\bottomrule
\end{tabularx}
\end{table}

A partir de esta síntesis, el análisis sistemático de las brechas se desglosa en los siguientes seis puntos estructurados:

\begin{enumerate}
    \item \textbf{Estaciones fijas a nivel de suelo (SINCA) \cite{mma_sinca_2021}:} La red pública oficial opera estaciones fijas en superficie. Aunque proveen datos continuos de material particulado y $\text{SO}_2$, carecen de resolución vertical y son estructuralmente incapaces de detectar la pluma concentrada antes de que impacte en tierra, además de no medir mezclas complejas de compuestos orgánicos volátiles.
    
    \item \textbf{Sensores fijos en colegios y empresas (SMA) \cite{sma_estrategia_2023}:} Como medida de contingencia tras sucesivas crisis, la SMA amplió el catastro e instaló sensores complementarios en establecimientos educacionales y puntos perimetrales industriales. No obstante, al permanecer confinados a ras de suelo, reproducen la misma ceguera vertical ante inversiones térmicas marinas.
    
    \item \textbf{Estudio pericial de la crisis de 2018 (UC--Dictuc) \cite{sma_dictuc}:} La modelación oficial constató que la emergencia de intoxicación masiva fue condicionada por una severa inversión térmica a unos $400\text{ m}$ sobre el suelo. Sin embargo, para conocer la estructura vertical debieron extrapolar datos de un radiosondeo en Santo Domingo, a $100\text{ km}$ de distancia, demostrando la ausencia absoluta de información vertical in situ en la bahía.
    
    \item \textbf{Drones en Quintero para registros térmicos (CR2) \cite{cr2_campana_2022}:} Investigadores del Centro de Ciencia del Clima y la Resiliencia de la Universidad de Chile ejecutaron campañas experimentales con UAVs para medir perfiles de temperatura y contaminantes no normados en la bahía. Pese a validar la viabilidad técnica del dron, constituyó una intervención científica puntual y no un sistema de monitoreo permanente.
    
    \item \textbf{Compromiso institucional de usar drones (MMA) \cite{mma_plan_2023}:} El Ministerio del Medio Ambiente oficializó en sus planes de fiscalización la incorporación de sensores incorporados en drones para fortalecer la red de monitoreo. Sin embargo, hasta la fecha no existe registro público sobre su implementación operacional sistemática.
    
    \item \textbf{Planificador de rutas para drones de muestreo (Kosior et al.) \cite{kosior}:} En el plano algorítmico internacional, Kosior et al. propusieron una arquitectura en dos niveles (planificador global previo al despegue y local reactivo en vuelo). No obstante, fue concebida para plataformas HALE de gran altitud operando en el espacio aéreo europeo, sin considerar las severas restricciones a baja cota de Quintero (núcleos urbanos densos, chimeneas de hasta $152\text{ m}$, líneas de alta tensión, aeródromo militar/civil y vientos costeros).
\end{enumerate}

\noindent \textbf{El enfoque de este proyecto: el plano de navegación seguro y eficiente.}
La evidencia anterior demuestra que los esfuerzos previos han intentado responder a las preguntas de \textit{dónde medir} en tierra o \textit{con qué sensores} registrar la contaminación. Sin embargo, para que el despliegue de drones sea una realidad operativa viable en Quintero y Puchuncaví, es indispensable resolver un problema previo y crítico: \textbf{el plano de navegación}. 

Un dron no puede operar de manera regular si no dispone de rutas seguras y eficientes. Volar en este territorio implica cruzar áreas pobladas donde una caída genera riesgo a personas en tierra (SORA / DAN 151), eludir chimeneas industriales y líneas de transmisión eléctrica de $110/220\text{ kV}$, evitar zonas de exclusión por tráfico aéreo tripulado en el Aeródromo de Quintero (SCER) y sortear ráfagas de viento y bancos de niebla marina. Por consiguiente, \textbf{nuestro proyecto se enfoca en el plano operacional y espacial}: modelar la infraestructura del entorno y calcular trayectorias resilientes que garanticen el cumplimiento de la misión de monitoreo de forma eficiente y segura.

\subsection{Solución Propuesta y Utilidad del Proyecto}
\label{subsec:solucion}

Para responder a este desafío, se construyó una infraestructura geoespacial automatizada, reproducible y modular contenida en microservicios Docker, acoplada a una base de datos relacional PostgreSQL 16 con PostGIS 3.5 y pgRouting 3.8. La plataforma modela y procesa:

\begin{itemize}
    \item \textbf{Topología del grafo aéreo ($237$ nodos y $633$ aristas):} Con origen estratégico en el Aeródromo de Quintero (código \texttt{base\_scer}), los nodos catastran las fuentes emisoras del parque industrial, los receptores residenciales vulnerables (salud y educación) y las $8$ estaciones de monitoreo SINCA del área de vuelo.
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

% ============================== 2 ==============================
\section{Marco Conceptual y Estado del Arte}
\label{sec:marco_conceptual}

El diseño de redes de navegación autónoma para UAVs en misiones ambientales converge en cuatro áreas teóricas fundamentales:

\subsection{Algoritmos de Camino Mínimo y Ruteo Espacial}

El problema de determinar la trayectoria de menor costo sobre un grafo discreto $G=(V,E)$ con pesos no negativos $c: E \to \mathbb{R}^+$ se resuelve óptimamente mediante el algoritmo clásico de Dijkstra \cite{dijkstra}, el cual opera mediante una exploración voraz (\textit{greedy}) con complejidad temporal $\mathcal{O}(|E| + |V|\log |V|)$ utilizando colas de prioridad. En entornos espaciales relacionales, este algoritmo se encuentra implementado a nivel de base de datos a través de la función \texttt{pgr\_dijkstra} de la extensión pgRouting \cite{pgrouting}, permitiendo procesar redes topológicas sobre geometrías vectoriales indexadas con PostGIS \cite{postgis}. En el modelo inicial desarrollado, la función de costo se restringe a la longitud física geodésica de cada segmento ($c(e) = \text{length\_m}$), estableciendo un escenario base de comparación.

\subsection{Caminos Alternativos y Disimilitud Espacial}

Para alcanzar una navegación verdaderamente resiliente ante contingencias, la planificación de trayectorias requiere la generación de rutas secundarias. Los métodos tradicionales de $k$-caminos mínimos, tales como el algoritmo de Yen \cite{yen}, producen con frecuencia trayectorias que comparten la gran mayoría de sus aristas con el camino principal, careciendo de redundancia espacial efectiva ante una amenaza zonal. Por su parte, los enfoques de caminos disjuntos en aristas o vértices de Suurballe \cite{suurballe} y Bhandari \cite{bhandari} garantizan la desconexión física total pero pueden inducir penalizaciones excesivas en la longitud o resultar infactibles en grafos dispersos. Para superar esta limitación, Akgün et al. \cite{akgun} formalizaron el problema de caminos disimilares (\textit{Minimax / Minisum Dissimilar Paths}), proponiendo técnicas de penalización iterativa que incrementan el costo de las aristas transitadas en la ruta primaria para forzar la divergencia controlada de la ruta alternativa ($k \ge 2$), preservando un compromiso admisible entre longitud y separación geométrica.

\subsection{Gestión del Riesgo Operacional en UAVs}

La integración de aeronaves pilotadas a distancia en el espacio aéreo civil exige metodologías sistemáticas de evaluación de riesgo. La directriz internacional SORA (\textit{Specific Operations Risk Assessment}), desarrollada por JARUS \cite{sora}, clasifica el riesgo en dos vertientes: riesgo intrínseco en tierra (\textit{Ground Risk Class}, GRC), determinado por la densidad poblacional y la masa del vehículo; y riesgo aéreo (\textit{Air Risk Class}, ARC), derivado de la proximidad a aeródromos y aeronaves tripuladas. La fiabilidad de los componentes críticos y el análisis de modos de fallo en UAVs han sido ampliamente caracterizados por Petritoli et al. \cite{petritoli}, destacando la pérdida del enlace de mando y control (C2) y el agotamiento prematuro de batería como las principales causales de accidentes catastróficos. En Chile, la norma aeronáutica DAN 151 \cite{dan151} regula estas operaciones, fijando restricciones de altitud máxima (400 pies / $120\text{ m}$ AGL) y condiciones de seguridad sobre áreas pobladas.

\subsection{Muestreo de Calidad del Aire y Metodología de Planificación Adaptativa}

El monitoreo de efluentes atmosféricos mediante vehículos aéreos no tripulados supera el retardo espacial y la ceguera vertical de las redes fijas terrestres. En este ámbito, Kosior et al. \cite{kosior} propusieron una arquitectura adaptativa de planificación de rutas en dos niveles (\textit{Adaptive Path Planning}, APP), compuesta por:
\begin{enumerate}
    \item \textbf{Global Path Planner (GPP):} Planificador estratégico previo al despegue, encargado de computar la trayectoria global óptima de muestreo sobre un grafo espacial minimizando el consumo energético estimado ($EEE$).
    \item \textbf{Local Path Planner (LPP):} Planificador táctico reactivo a bordo, diseñado para operar en tiempo real ($CT \le 4{,}55\text{ s}$) garantizando la evitación estricta de colisiones ($N_{COL} = 0$) y la replanificación de contingencia ante amenazas dinámicas imprevistas.
\end{enumerate}

\noindent \textbf{Delimitación metodológica y contexto de aplicación:} Es fundamental precisar el alcance con el que se adopta el trabajo de Kosior et al. \cite{kosior}. Su investigación fue formulada para aeronaves de Gran Altitud y Larga Autonomía (HALE, \textit{High-Altitude Long-Endurance}), concebidas para operar en un amplísimo rango altimétrico (desde cientos de metros sobre el suelo hasta la estratosfera) con el propósito primordial de minimizar el gasto de energía en perfiles de planeo y crucero prolongado. Por lo tanto, en este proyecto se rescata el trabajo de Kosior et al. \textbf{estrictamente como referencia metodológica de la descomposición en dos niveles (GPP/LPP) y para el modelado del balance energético ($EEE$)}, distinguiendo con claridad que \textbf{no constituye un antecedente empírico para la Bahía de Quintero}. En nuestro escenario, el vuelo del UAV se restringe a un estrato de muy baja cota ($0$ a $120\text{ m}$ AGL según la norma DAN 151 de la DGAC \cite{dan151}), donde los factores determinantes no son el crucero estratosférico, sino el riesgo de impacto a terceros en tierra sobre manzanas pobladas (SORA), la proximidad a chimeneas industriales de hasta $152\text{ m}$ y líneas de alta tensión, la presencia de tráfico aéreo tripulado en el Aeródromo de Quintero, y la turbulencia y camanchaca costera.

En cuanto al modelado de amenazas, los productos satelitales de incendios activos VIIRS de $375\text{ m}$ de resolución espacial \cite{schroeder} proveen capacidades de detección casi en tiempo real (NRT), mientras que la estandarización de las capas vectoriales se rige bajo la norma RFC 7946 GeoJSON \cite{rfc7946}.

% ============================== 3 ==============================
\section{Objetivos del Proyecto y Preguntas de Investigación}
\label{sec:objetivos}

\subsection{Objetivo General}

Construir una base de datos geoespacial reproducible que integre la infraestructura de la red aérea, cinco capas de metadatos operacionales y cuatro capas de amenazas operacionales dinámicas en el área de Quintero, Ventanas y Puchuncaví, y obtener sobre ella la ruta de menor longitud mediante \texttt{pgr\_dijkstra} como línea base y escenario de peor caso para la evaluación del ruteo resiliente.

\subsection{Objetivos Específicos}

\begin{enumerate}
    \item Diseñar e inicializar una base de datos relacional-espacial en PostgreSQL 16 con las extensiones PostGIS 3.5 y pgRouting 3.8, estructurada en tablas que alberguen la topología de la red, los metadatos territoriales y los eventos de amenaza.
    \item Automatizar la extracción y modelado de la red aérea en un grafo espacial no dirigido de 237 nodos, 633 aristas conexas y 8 polígonos de zonas urbanas, estandarizados bajo el formato RFC 7946 GeoJSON \cite{rfc7946}.
    \item Implementar scripts modulares de extracción y carga para 5 capas de metadatos de soporte operacional: calidad del aire en tiempo real (SINCA MMA) modelada como recompensa de muestreo, perfiles altimétricos por arista (NASA SRTM 30m), densidad de población censal (INE 2017) para cálculo de riesgo en tierra SORA, radiobases celulares para telemetría C2 (OpenStreetMap) y catastro de obstáculos verticales críticos (chimeneas de hasta $152\text{ m}$ y líneas de alta tensión $110/220\text{ kV}$).
    \item Implementar extractores automatizados para 4 capas de contingencias operacionales dinámicas: focos de incendios activos (NASA FIRMS), separación frente a aeronaves tripuladas en aproximación visual (OpenSky Network ADS-B), vectores y ráfagas de viento crítico a $120\text{ m}$ AGL (Open-Meteo) y visibilidad horizontal/niebla costera (Open-Meteo).
    \item Calcular mediante \texttt{pgr\_dijkstra} en base de datos la ruta de menor distancia física en metros desde el Aeródromo de Quintero hacia las 8 estaciones SINCA de la red, estableciendo el peor caso de exposición frente a las amenazas del entorno e informando la condición de vuelo BVLOS ($>500\text{ m}$) bajo la normativa chilena DAN 151.
    \item Implementar una aplicación interactiva en Leaflet que permita visualizar las capas temáticas y presentar la ruta base calculada junto con sus métricas operacionales y advertencias regulatorias.
    \item Orquestar de extremo a extremo las etapas de extracción, creación de esquema, carga de datos y ruteo en un script maestro \texttt{main.py}, asegurando su ejecución en contenedores Docker y validando su integridad mediante una suite de 57 pruebas automatizadas.
\end{enumerate}

\subsection{Preguntas de Investigación y Diseño}
\label{subsec:preguntas_diseno}

El desarrollo y evaluación del sistema busca responder formalmente a tres preguntas operacionales:

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
    \item[\textbf{S3.}] \textbf{Cota de altitud operacional fija ($\approx 100\text{ m}$ AGL):} Las operaciones se planifican a una altitud de crucero constante fija de aproximadamente $100\text{ m}$ sobre el nivel del suelo ($100\text{ m}$ AGL), respetando el límite legal de 400 pies ($\approx 120\text{ m}$ AGL) fijado por la norma DAN 151 \cite{dan151}. Dado que en esta fase de modelado el ruteo se evalúa sobre el plano del grafo territorial y la altitud no se optimiza como variable de control continuo, se asume dicha cota fija de $100\text{ m}$ AGL homogénea para todas las aristas y misiones.
    \item[\textbf{S4.}] \textbf{Umbral de densidad urbana crítica:} Se establece un umbral de $2.500\text{ hab/km}^2$ como supuesto del equipo, representativo de la mediana de densidad en manzanas residenciales consolidadas de Quintero y Ventanas. Las trayectorias que sobrevuelan estas áreas implican un incremento en la clase de riesgo en tierra según la metodología SORA \cite{sora}.
    \item[\textbf{S5.}] \textbf{Enlace de mando y control (C2):} Se asume telemetría celular terrestre 4G/LTE con un radio de cobertura omnidireccional estimada de $3.000\text{ m}$ alrededor de cada mástil celular catastrado en OpenStreetMap. Los tramos que exceden este radio se catalogan como zonas en sombra radioeléctrica con riesgo de pérdida de telemetría (\textit{fly-away}) \cite{petritoli}.
    \item[\textbf{S6.}] \textbf{Aeronave única de referencia, velocidad y autonomía unificada:} Se define de manera exclusiva el multirrotor industrial DJI Matrice 350 RTK \cite{dji} como la única plataforma aérea operacional del sistema, no permitiendo la selección de otros modelos. Se unifica la velocidad de crucero nominal en $v = 15\text{ m/s}$ ($54\text{ km/h}$) para todo el informe y el simulador web. La autonomía máxima declarada por el fabricante es de $55\text{ min}$ (equivalente a $49{,}5\text{ km}$ a velocidad nominal sin carga \cite{dji}). Como supuesto operacional conservador con carga de sensores ambientales y una reserva de seguridad del $20$\,\% de batería para retorno seguro, la autonomía operacional efectiva se fija en $44\text{ min}$ ($39{,}6\text{ km}$). La resistencia al viento del fabricante es de $12\text{ m/s}$ y cuenta con protección ambiental IP55.
    \item[\textbf{S7.}] \textbf{Umbrales y geometrías de amenazas ambientales dinámicas:} Se definen como supuestos del equipo: zona de exclusión circular de $2.000\text{ m}$ en torno a focos de calor activos de NASA FIRMS \cite{schroeder} (humo y turbulencia); cilindro de protección de $1.500\text{ m}$ de radio y hasta $1.000\text{ m}$ MSL en torno a aeronaves tripuladas detectadas vía ADS-B en SCER \cite{opensky}; umbral de viento crítico en $12\text{ m/s}$ ($43{,}2\text{ km/h}$) a $120\text{ m}$ AGL según la especificación estructural de la aeronave \cite{dji}; y umbral de niebla/visibilidad reducida en $<1.000\text{ m}$ o saturación de humedad costera ($\text{HR} \ge 95$\,\% con nubes bajas $\ge 80$\,\%) según Open-Meteo \cite{openmeteo}.
    \item[\textbf{S8.}] \textbf{Ventana temporal de datos de referencia:} Las tablas y resultados numéricos reportados corresponden a la corrida de referencia ejecutada entre el 18-10-2026 22:35 UTC y el 19-10-2026 02:11 UTC, cuyos archivos GeoJSON se encuentran versionados en el repositorio para garantizar la reproducibilidad completa mediante la opción \texttt{--sin-descarga}.
    \item[\textbf{S9.}] \textbf{Régimen de Vuelo BVLOS (Beyond Visual Line of Sight):} Para cualquier trayectoria que supere los $500\text{ m}$ de distancia radial desde el punto de despegue (tal como la misión de $14{,}41\text{ km}$ a la estación SINCA de Puchuncaví), la operación excede la línea de vista visual directa del piloto, quedando catalogada en régimen BVLOS según la norma DAN 151 de la DGAC de Chile \cite{dan151}, requiriendo autorización formal previa, enlace redundante y protocolos de seguridad específicos.
\end{itemize}

% ============================== 5 ==============================
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
\node[caja={blue!8}, right=of f] (x) {Extracción y transformación\\\texttt{*.py}};
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
    id            integer PRIMARY KEY,
    source        integer NOT NULL REFERENCES infra_node (id),
    target        integer NOT NULL REFERENCES infra_node (id),
    length_m      double precision NOT NULL,
    cost          double precision NOT NULL, -- ruta base: = length_m (pgr_dijkstra)
    reverse_cost  double precision NOT NULL,
    geom          geometry(LineString, 4326) NOT NULL
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

\subsection{Obtención y Construcción del Grafo Espacial}
\label{subsec:infra_obtencion}

La red se modela como un grafo de corredores aéreos rectilíneos. Su extracción se realiza mediante el script:
\begin{lstlisting}[language=bash]
python infraestructura/extraer_infraestructura.py
\end{lstlisting}
el cual genera tres archivos GeoJSON en la carpeta \texttt{infraestructura/}:
\begin{itemize}
    \item \textbf{Nodos (\texttt{nodos.geojson}, $237$ vértices):} Nodos clasificados en $13$ categorías: áreas concurridas ($40$), fuentes emisoras industriales ($32$), gastronomía ($28$), educación ($26$), balnearios ($22$), hospedaje ($21$), turismo ($17$), centros de salud ($15$), patrimonio histórico ($13$), comercio ($12$), estaciones de calidad del aire SINCA ($8$), \textit{hubs} auxiliares ($2$) y la base operativa en el Aeródromo de Quintero (\texttt{base\_scer}, $1$).
    \item \textbf{Aristas (\texttt{aristas.geojson}, $633$ arcos):} Generadas uniendo cada nodo con sus $K=4$ vecinos más cercanos por distancia Haversine y agregando $2$ aristas puente mediante \textit{Union-Find} para unir los subgrafos de Quintero y Puchuncaví.
    \item \textbf{Zonas Urbanas (\texttt{zonas\_urbanas.geojson}, $8$ polígonos):} Polígonos de consolidación urbana normalizados según RFC 7946 \cite{rfc7946}.
\end{itemize}

\subsection{Estructura de los Datos GeoJSON y Bloque ETL}
\label{subsec:infra_json}

Cada archivo incluye un encabezado \texttt{etl} con su procedencia, fecha y parámetros de generación, documentado en sus archivos de especificación Markdown (\texttt{nodos.md}, \texttt{aristas.md} y \texttt{zonas\_urbanas.md}) (ver Tabla~\ref{tab:json_infra}).

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

\begin{lstlisting}[language=SQL,caption={Extracto del bloque \texttt{etl} y un feature real de \texttt{infraestructura/nodos.geojson}.}]
{
  "type": "FeatureCollection",
  "etl": {
    "fuente": "dataset maestro de infraestructura (Quintero/Puchuncavi)",
    "generado": "2026-10-18T22:34:19+00:00",
    "script": "infraestructura/extraer_infraestructura.py"
  },
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [-71.5173, -32.7842, 28.0] },
      "properties": {
        "id": 1,
        "code": "base_scer",
        "name": "Aerodromo de Quintero",
        "category": "base",
        "city": "Quintero",
        "elevation_msnm": 28.0
      }
    }
  ]
}
\end{lstlisting}

\subsection{Carga Transaccional e Idempotencia}
\label{subsec:infra_carga}

La carga transaccional hacia PostgreSQL se realiza en orden estricto de integridad referencial:
\begin{lstlisting}[language=bash]
python infraestructura/cargar_nodos.py
python infraestructura/cargar_aristas.py
python infraestructura/cargar_zonas_urbanas.py
\end{lstlisting}
Cada cargador ejecuta una transacción atómica con limpieza preventiva (\texttt{DELETE FROM tabla}) antes de la inserción por lotes (\texttt{executemany}), garantizando idempotencia total.

% ============================== 8 ==============================
\section{Metadata de Soporte Operacional}
\label{sec:metadata}

\subsection{Obtención, Fuentes y Filtro Espacial}
\label{subsec:metadata_obtencion}

Las cinco capas de metadatos operacionales se filtraron a la caja envolvente de la bahía (longitud entre $-71{,}56^\circ$ y $-71{,}38^\circ$, latitud entre $-32{,}82^\circ$ y $-32{,}69^\circ$ WGS84) mediante cinco extractores modulares (ver Tabla~\ref{tab:metadata}).

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
\texttt{osm\_obstaculos} & \texttt{obstaculos.json} & Overpass API \cite{overpass} & En vivo & $12$ chimeneas ($50\text{--}152\text{ m}$) y líneas $110/220\text{ kV}$. \\
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
\caption{Marco conceptual y rol operacional de las cinco capas de metadata en el enrutamiento UAV.}
\label{tab:metadata_roles}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.2cm}p{2.6cm}p{3.0cm}p{8.5cm}}
\toprule
\textbf{Metadata} & \textbf{Fuente Primaria} & \textbf{Dimensión Operacional} & \textbf{Rol en el Enrutamiento UAV} \\
\midrule
Población & INE (IDE SMA) & Riesgo en tierra & \textbf{Penalizar}: Incrementa el costo de aristas sobre zonas densamente pobladas según directrices SORA (GRC) y DAN 151. \\
\addlinespace
Obstáculos y tendido eléctrico & OSM (Overpass) & Riesgo en el aire & \textbf{Bloquear o penalizar}: Inhabilita aristas que intersectan chimeneas ($50\text{--}152\text{ m}$) y penaliza cruces de líneas de alta tensión ($110/220\text{ kV}$). \\
\addlinespace
Relieve orográfico & SRTM (OpenTopoData) & Terreno y energía & \textbf{Penalizar ascenso y verificar cota}: Verifica techo legal de $120\text{ m}$ AGL y penaliza consumo energético ($EEE$) por trepada gravitacional. \\
\addlinespace
Cobertura celular & OpenCelliD / OSM & Enlace de control C2 & \textbf{Penalizar zonas de sombra}: Penaliza corredores fuera de la cobertura 4G/LTE requerida para la telemetría continua de mando. \\
\addlinespace
Calidad del aire & SINCA (MMA) & Valor de la misión & \textbf{Priorizar destinos}: No modifica costos de aristas; asigna recompensa $\mathcal{R}(d)$ a estaciones críticas y provee referencia de suelo. \\
\bottomrule
\end{tabular}%
}
\end{table}

\noindent \textbf{Justificación Técnica, Supuestos y Limitaciones Declaradas:}
\begin{itemize}
    \item \textbf{Población y Densidad Habitacional (INE 2017):} Constituye la piedra angular para evaluar la clase de riesgo intrínseco en tierra (\textit{Ground Risk Class}, GRC) de la metodología SORA de JARUS \cite{sora} y aplicar las restricciones de sobrevuelo sobre áreas pobladas de la DAN 151 de la DGAC \cite{dan151}. Su rol es penalizar el costo de las aristas que sobrevuelan zonas residenciales con densidades superiores a $2.500\text{ hab/km}^2$, incentivando al planificador a seleccionar corredores costeros o rurales. Se declara formalmente como limitación metodológica que la cartografía geométrica corresponde al Censo 2017 (IDE SMA), dado que a la fecha de este estudio el Censo 2024 aún no cuenta con geometrías vectoriales oficiales publicadas a nivel de manzana censal.
    \item \textbf{Obstáculos Verticales y Tendido Eléctrico (OpenStreetMap):} Responde a la pregunta fundamental de riesgo en el aire: \textit{¿con qué estructuras físicas puede colisionar el dron en su altitud de vuelo?} Cubre chimeneas industriales del cordón Ventanas-Quintero (cuyas alturas oscilan entre $50$ y $152\text{ m}$, interceptando directamente la franja legal de $0$ a $120\text{ m}$ AGL), mástiles de telecomunicaciones y líneas de transmisión eléctrica de alta tensión ($110\text{ kV}$ y $220\text{ kV}$). Las líneas de potencia imponen un doble riesgo: impacto mecánico directo con cables y torres, e interferencia electromagnética severa sobre la brújula y magnetómetro del UAV. Su rol operacional consiste en bloquear estrictamente (restricción dura) las aristas que penetran el radio de exclusión física ($60$ a $120\text{ m}$), o penalizar aristas que cruzan el trazado con separación vertical mínima. Se declara como supuesto que aquellas chimeneas sin cota explícita en OSM adoptan alturas conservadoras estimadas basadas en especificaciones técnicas industriales.
    \item \textbf{Relieve Orográfico (SRTM):} Su integración posee una justificación técnica dual e inseparable:
    \begin{enumerate}
        \item \textit{Seguridad operacional y cumplimiento normativo:} La norma DAN 151 establece un límite estricto de altitud de operación de $120\text{ m}$ AGL medidos sobre la superficie del suelo. Hacia el oriente de la bahía (hacia Puchuncaví), el terreno asciende $+67\text{ m}$. Si el dron volara a una cota barométrica constante respecto al nivel del mar, su separación respecto al terreno se reduciría peligrosamente hasta colisionar con laderas u obstáculos; si vuela manteniendo una altitud relativa constante al terreno (vuelo \textit{terrain-following}), la aeronave debe ascender y descender de forma controlada.
        \item \textit{Consumo energético ($EEE$):} Cada metro de ascenso vertical exige un incremento exponencial en la potencia suministrada por los rotores para vencer la fuerza gravitatoria. Por esta razón, el sistema no almacena una cota puntual estática por nodo, sino el perfil altimétrico discretizado cada $100\text{ m}$ a lo largo de cada arista (\texttt{terrain\_mean\_m}, \texttt{ascent\_m}, \texttt{descent\_m}, \texttt{slope\_max\_pct}), insumo indispensable para modelar el gasto de batería ($EEE$) según la formulación física de Kosior et al. \cite{kosior}.
    \end{enumerate}
    \item \textbf{Cobertura de Antenas Celulares (OSM / OpenCelliD):} Vital para preservar la continuidad del enlace de mando, control y telemetría (C2) \cite{petritoli}. Se declara el \textbf{supuesto obligatorio} de que la aeronave utiliza conectividad celular comercial 4G/LTE (bandas 7 y 28 a $120\text{ m}$ AGL) para la transmisión de telemetría y datos de misión hacia la estación de control en tierra. Se declaran como supuestos de modelación el radio macro-celular nominal de $3.000\text{ m}$ por antena y el subregistro de OpenStreetMap ($25$ antenas identificadas en la bahía frente a los bloqueos automatizados por reCAPTCHA del portal Subtel), proyectando la incorporación de la base colaborativa abierta OpenCelliD para disponer de celdas con tecnología específica (LTE/UMTS) y radios de cobertura estimados empíricamente.
    \item \textbf{Calidad del Aire (SINCA):} Se define con total claridad su rol conceptual: la calidad del aire \textbf{no modifica el costo de las aristas ni actúa como factor de riesgo}, ya que la polución atmosférica no compromete la aeronavegabilidad ni la sustentación del UAV. Su función es modelar el \textbf{valor de la misión} (priorización de destinos mediante recompensa $\mathcal{R}(d)$): una estación de monitoreo que presente concentraciones elevadas de contaminantes ($\text{SO}_2, \text{MP}_{10}, \text{MP}_{2{,}5}$) adquiere máxima prioridad como destino de muestreo. Además, las estaciones terrestres proporcionan la línea base de referencia con la que se contrastarán las mediciones tomadas por los sensores de a bordo a diferentes niveles de cota.
\end{itemize}

\subsection{Estructura de Atributos y Valores de Ejemplo}
\label{subsec:metadata_json}

La Tabla~\ref{tab:json_metadata} detalla la estructura y valores reales en los archivos GeoJSON, documentados en sus respectivos archivos Markdown (\texttt{ine\_manzanas.md}, \texttt{osm\_obstaculos.md}, \texttt{srtm\_relieve.md}, \texttt{osm\_antenas.md} y \texttt{sinca\_calidad\_aire.md}).

\begin{table}[H]
\centering
\small
\caption{Estructura y valores reales de los GeoJSON de metadata.}
\label{tab:json_metadata}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{3.2cm}p{3.0cm}p{1.8cm}p{3.5cm}p{5.5cm}}
\toprule
\textbf{Archivo} & \textbf{Campo} & \textbf{Tipo} & \textbf{Unidad} & \textbf{Ejemplo Real en Dataset} \\
\midrule
\texttt{ine\_manzanas} & \texttt{persons} & Integer & Habitantes & \texttt{142} \\
 & \texttt{density\_hab\_km2} & Float & $\text{hab/km}^2$ & \texttt{3120.5} \\
\midrule
\texttt{osm\_obstaculos} & \texttt{obstacle\_type} & String & Tipo de obstáculo & \texttt{"chimney"}, \texttt{"power\_line"} \\
 & \texttt{height\_m} & Float & Metros s.n.m. / cota & \texttt{152.0} \\
 & \texttt{voltage\_kv} & Float & Kilovoltios & \texttt{220.0} \\
 & \texttt{operational\_action} & String & Acción operacional & \texttt{"bloquear"}, \texttt{"penalizar"} \\
\midrule
\texttt{srtm\_relieve} & \texttt{edge\_id} & Integer & ID arista & \texttt{1} \\
 & \texttt{terrain\_mean\_m} & Float & Metros s.n.m. & \texttt{34.2} \\
 & \texttt{ascent\_m} & Float & Metros & \texttt{12.0} \\
\midrule
\texttt{osm\_antenas} & \texttt{coverage\_radius\_m} & Float & Metros & \texttt{3000.0} \\
 & \texttt{operator} & String & Empresa & \texttt{"Entel"} \\
\midrule
\texttt{sinca\_calidad\_aire} & \texttt{station\_key} & String & Código & \texttt{"sinca\_ventanas"} \\
 & \texttt{pollutant} & String & Gas / Aerosol & \texttt{"MP25"}, \texttt{"SO2"} \\
 & \texttt{value} & Float & $\mu\text{g/m}^3\text{N}$ & \texttt{18.4} \\
\bottomrule
\end{tabular}%
}
\end{table}

\subsection{Carga Transaccional}
\label{subsec:metadata_carga}

La ingesta hacia la base de datos se realiza ejecutando los scripts de carga correspondientes:
\begin{lstlisting}[language=bash]
python metadata/cargar_ine_manzanas.py         # 703 filas en meta_census_block
python metadata/cargar_osm_obstaculos.py       # 12 filas en meta_obstacle
python metadata/cargar_srtm_relieve.py         # 633 filas en meta_edge_terrain
python metadata/cargar_osm_antenas.py          # 25 filas en meta_telecom_antenna
python metadata/cargar_sinca_calidad_aire.py   # 52 filas en meta_air_quality
\end{lstlisting}

% ============================== 9 ==============================
\section{Amenazas Operacionales}
\label{sec:amenazas}

\subsection{Obtención, Filtros Espaciales y Modelado}
\label{subsec:amenazas_obtencion}

Para modelar contingencias dinámicas que restringen el espacio aéreo, se desarrollaron cuatro extractores automatizados (ver Tabla~\ref{tab:amenazas}).

\begin{table}[H]
\centering
\small
\caption{Fuentes de amenazas y parámetros operacionales en la ejecución de referencia.}
\label{tab:amenazas}
\begin{tabularx}{\linewidth}{p{2.2cm}p{2.2cm}p{2.8cm}p{2.8cm}Xc}
\toprule
\textbf{Script ETL} & \textbf{Salida} & \textbf{Endpoint / Servicio} & \textbf{Filtro Espacial} & \textbf{Modelo y Umbral} & \textbf{Activos} \\
\midrule
\texttt{firms.py} & \texttt{firms.json} & NASA FIRMS \cite{firms} & AOI margen $0{,}3^\circ$ & Búfer $2.000\text{ m}$; conf. alta \cite{schroeder} & $1$ ($1$) \\
\addlinespace
\texttt{opensky.py} & \texttt{opensky.json} & OpenSky API \cite{opensky} & Patrón SCER & Cilindro $R=1.500\text{ m}$, cota $\le 1.000\text{ m}$ & $1$ ($1$) \\
\addlinespace
\texttt{viento.py} & \texttt{viento.json} & Open-Meteo \cite{openmeteo} & Grilla $4 \times 4$ & Ráfaga $\ge 12\text{ m/s}$ a $120\text{ m}$ AGL & $16$ ($0$) \\
\addlinespace
\texttt{niebla.py} & \texttt{niebla.json} & Open-Meteo \cite{openmeteo} & Grilla $4 \times 4$ & Visibilidad $<1.000\text{ m}$ o $\text{HR} \ge 95$\% & $16$ ($8$) \\
\bottomrule
\end{tabularx}
\end{table}

\noindent \textbf{Justificación Operacional y Auditoría de Afectación:}
\begin{itemize}
    \item \textbf{Incendios Forestales e Industriales (NASA FIRMS):} La detección se basa en el producto VIIRS de $375\text{ m}$ de resolución espacial \cite{schroeder}. Su justificación responde a tres factores aeronáuticos: el humo denso reduce severamente la visibilidad óptica y satura los sensores electro-ópticos; las térmicas convectivas generan turbulencia violenta capaz de inducir pérdidas aerodinámicas; y sobre un foco de incendio operan habitualmente brigadas y aeronaves de combate (helicópteros y aviones cisterna de CONAF), espacio aéreo en el cual un UAV representa un obstáculo de colisión crítico. Se establece un radio de amortiguamiento preventivo de $2.000\text{ m}$ que bloquea completamente las aristas que lo cruzan.
    \item \textbf{Tráfico Aéreo Tripulado en Patrón de Quintero (OpenSky Network ADS-B):} El Aeródromo de Quintero (SCER) mantiene tráfico constante de aviación civil y militar. En estricta conformidad con el marco regulatorio DAN 151 \cite{dan151}, las aeronaves pilotadas a distancia deben ceder el paso irrestrictamente y mantener separación absoluta frente a aeronaves tripuladas ($N_{COL} = 0$). El sistema consulta la telemetría ADS-B en vivo de OpenSky Network \cite{opensky}; toda aeronave detectada a baja cota ($\le 1.000\text{ m}$ MSL, fase de aproximación o despegue) genera un cilindro de exclusión de $1.500\text{ m}$ de radio que inhabilita las aristas de cruce.
    \item \textbf{Viento Crítico a $120\text{ m}$ AGL (Open-Meteo):} En zonas costeras, el gradiente de viento se incrementa con la altura al disiparse la rugosidad del terreno. Evaluar el viento al techo legal de vuelo de $120\text{ m}$ AGL permite medir la condición real que experimentará el dron. Se establece un umbral de $12{,}0\text{ m/s}$ ($43{,}2\text{ km/h}$), correspondiente a la resistencia máxima al viento de plataformas de ala rotatoria de referencia como el DJI Matrice 350 RTK \cite{dji}. Vientos sobre este umbral activan la condición No-Go; bajo él, el vector de viento proyectado sobre cada arista modula la velocidad respecto a tierra $v_g$ y el gasto energético $EEE$ \cite{kosior}.
    \item \textbf{Niebla Costera y Visibilidad Horizontal (Open-Meteo):} Fenómeno recurrente en la bahía originado por la inversión térmica y la camanchaca marina. La DAN 151 prohíbe taxativamente la operación de UAVs en condiciones que no cumplan con las reglas de vuelo visual (VMC), exigiendo una visibilidad mínima de $1.000\text{ m}$. Celdas con visibilidad horizontal $< 1.000\text{ m}$ o saturación de humedad relativa ($\ge 95$\% con cobertura nubosa baja $\ge 80$\%) activan la condición \texttt{exceeds = true}, bloqueando los corredores por pérdida de contacto visual y riesgo de condensación de niebla salina en la aviónica.
    \item \textbf{Resultado de la auditoría espacial:} En la ejecución reportada, el foco de FIRMS se situó fuera del corredor inmediato; no obstante, el tráfico ADS-B en aproximación al aeródromo de Quintero y los bancos de niebla matinal en el borde costero ($8$ celdas activas) bloquearon aristas directas, obligando a los algoritmos de enrutamiento a buscar desvíos protegidos hacia el interior.
\end{itemize}

\subsection{Estructura Común y Ejemplo Real en JSON}
\label{subsec:json_amenazas}

Los cuatro archivos de amenazas comparten un formato base homogéneo (ver Tabla~\ref{tab:json_amenazas}), documentado en \texttt{firms\_incendios.md}, \texttt{opensky\_aeronaves.md}, \texttt{openmeteo\_viento.md} y \texttt{openmeteo\_niebla.md}.

\begin{table}[H]
\centering
\small
\caption{Estructura común de atributos en los archivos GeoJSON de amenazas.}
\label{tab:json_amenazas}
\resizebox{\linewidth}{!}{%
\begin{tabular}{p{2.8cm}p{2.2cm}p{2.6cm}p{5.5cm}p{3.8cm}}
\toprule
\textbf{Propiedad} & \textbf{Tipo} & \textbf{Unidad} & \textbf{Significado y Rol Operacional} & \textbf{Ejemplo Real} \\
\midrule
\texttt{geometry} & \texttt{Polygon} & Grados WGS84 & Zona de afectación (círculo $32$ vértices o celda) & Polígono discretizado \\
\addlinespace
\texttt{external\_id} & String & Texto & Identificador único en el catálogo de origen & \texttt{"opensky\_scer\_vfr\_01"} \\
\addlinespace
\texttt{event\_type} & String & Categoría & \texttt{incendio}, \texttt{aeronave}, \texttt{viento} o \texttt{niebla} & \texttt{"aeronave"} \\
\addlinespace
\texttt{value} & Float & Variable & Magnitud física medida & \texttt{350.0} ($\text{m}$) \\
\addlinespace
\texttt{threshold} & Float & Variable & Umbral crítico que define riesgo a la nave & \texttt{1000.0} ($\text{m}$) \\
\addlinespace
\texttt{exceeds} & Boolean & Booleano & \texttt{true} si supera el umbral (zona activa) & \texttt{true} \\
\addlinespace
\texttt{observed\_at} & String & ISO 8601 & Fecha y hora UTC del registro o pronóstico & \texttt{"2026-10-23T07:28:04Z"} \\
\bottomrule
\end{tabular}%
}
\end{table}

\begin{lstlisting}[language=SQL,caption={Feature real de una aeronave tripulada en \texttt{amenazas/opensky\_aeronaves.geojson}.}]
{
  "type": "Feature",
  "geometry": { "type": "Polygon", "coordinates": [[[-71.4959, -32.772], [-71.4962, -32.769], ...]] },
  "properties": {
    "external_id": "opensky_scer_vfr_01",
    "event_type": "aeronave",
    "value": 350.0,
    "unit": "m (altitud barometrica)",
    "threshold": 1000.0,
    "exceeds": true,
    "observed_at": "2026-10-23T07:28:04+00:00",
    "callsign": "CC-SCER1",
    "icao24": "e802a1",
    "baro_altitude_m": 350.0,
    "velocity_ms": 52.0,
    "exclusion_radius_m": 1500.0
  }
}
\end{lstlisting}

\subsection{Carga Transaccional en Base de Datos}
\label{subsec:carga_amenazas}

La carga en \texttt{threat\_event} se ejecuta individualmente mediante:
\begin{lstlisting}[language=bash]
python amenazas/cargar_firms_incendios.py   # 1 fila (1 activa)
python amenazas/cargar_opensky_aeronaves.py # 1 fila (1 activa)
python amenazas/cargar_openmeteo_viento.py  # 16 filas (0 activas)
python amenazas/cargar_openmeteo_niebla.py  # 16 filas (8 activas)
\end{lstlisting}
En total se cargan exactamente \textbf{$34$ registros de amenazas}. La tabla almacena el centroide en \texttt{point\_geom} y el área de exclusión en \texttt{geom}, evaluándose espacialmente contra la red.

% ============================== 10 ==============================
\section{Algoritmo de Ruteo Base: \texttt{pgr\_dijkstra}}
\label{sec:ruteo_dijkstra}

Para caracterizar el comportamiento del sistema y definir una línea base de comparación, la ruta de referencia se calcula directamente en PostgreSQL utilizando la función \texttt{pgr\_dijkstra} de pgRouting \cite{pgrouting} sobre el costo métrico puro (\texttt{length\_m}), sin incorporar aún la metadata ni las amenazas en la ponderación de pesos.

El script \texttt{ruteo/ruta\_dijkstra.py} ejecuta la siguiente consulta SQL parametrizada desde la base (\texttt{base\_scer}) hacia cada una de las 8 estaciones SINCA:

\begin{lstlisting}[language=SQL,caption={Consulta SQL parametrizada ejecutada en \texttt{ruteo/ruta\_dijkstra.py}.}]
SELECT count(*) FILTER (WHERE d.edge <> -1)                AS tramos,
       COALESCE(SUM(e.length_m), 0)                        AS longitud_m,
       MAX(d.agg_cost)                                     AS costo,
       COUNT(DISTINCT d.node)                              AS nodos,
       ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq))    AS linea
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
\label{tab:capas_web}
\begin{tabularx}{\linewidth}{llY}
\toprule
\textbf{Grupo} & \textbf{Capa Geoespacial} & \textbf{Estilo Visual y Simbología en el Mapa} \\
\midrule
\textbf{Infraestructura} & Topología de Red & $237$ marcadores circulares clasificados por color ($13$ categorías); aristas grises de corredores aéreos bidireccionales. \\
 & Zonas Urbanas & $8$ polígonos translúcidos violeta con borde continuo. \\
\midrule
\textbf{Metadata} & Calidad del Aire (SINCA) & Marcadores azules con popups interactivos de concentración ($\text{SO}_2, \text{MP}_{10}, \text{MP}_{2{,}5}$) y estado ambiental. \\
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

Para verificar la conectividad global y evaluar cuantitativamente el riesgo de la línea base, se ejecutaron simulaciones de navegación desde el Aeródromo de Quintero (\texttt{base\_scer}, cota $28\text{ msnm}$) hacia las $8$ estaciones SINCA y hacia $10$ receptores críticos de la bahía.

Las métricas analizadas corresponden a la longitud geodésica ($L$), número de aristas o saltos topológicos ($h$), tiempo de vuelo ($T_v$) a velocidad de crucero nominal unificada ($15\text{ m/s} = 54\text{ km/h}$, S6), desnivel orográfico ($\Delta z = z_{\text{destino}} - z_{\text{origen}}$) y la exposición cuantitativa calculada mediante intersección geométrica espacial sobre las capas de densidad censal y telecomunicaciones: kilómetros sobre manzanas densas ($>2.500\text{ hab/km}^2$) y kilómetros fuera de cobertura celular C2 ($>3.000\text{ m}$ de mástiles OSM).

\subsection{Resultados Numéricos de la Navegación hacia Estaciones SINCA}
\label{subsec:tabla_resultados_sinca}

La Tabla~\ref{tab:resultados_sinca} presenta las métricas operacionales hacia las $8$ estaciones de monitoreo SINCA:

\begin{table}[H]
\centering
\small
\caption{Métricas cuantitativas del ruteo base (\texttt{pgr\_dijkstra}) hacia las $8$ estaciones SINCA (costo = longitud).}
\label{tab:resultados_sinca}
\resizebox{\linewidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
\textbf{Estación SINCA} & \textbf{Código} & \textbf{Distancia} & \textbf{Saltos} & \textbf{$T_v$ est. ($15\text{ m/s}$)} & \textbf{$\Delta z$} & \textbf{Sobre Manzanas Densas} & \textbf{Sin Cobertura C2} \\
\midrule
Centro Quintero & \texttt{sinca\_centro\_quintero} & $1{,}69\text{ km}$ & $6$ & $1{,}9\text{ min}$ & $-6{,}0\text{ m}$ & $0{,}39\text{ km}$ ($23{,}1$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Loncura & \texttt{sinca\_loncura} & $2{,}35\text{ km}$ & $4$ & $2{,}6\text{ min}$ & $-13{,}0\text{ m}$ & $0{,}09\text{ km}$ ($3{,}8$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Quintero & \texttt{sinca\_quintero} & $2{,}35\text{ km}$ & $9$ & $2{,}6\text{ min}$ & $-10{,}0\text{ m}$ & $1{,}06\text{ km}$ ($45{,}1$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
Sur & \texttt{sinca\_sur} & $3{,}74\text{ km}$ & $5$ & $4{,}2\text{ min}$ & $-3{,}0\text{ m}$ & $0{,}13\text{ km}$ ($3{,}5$\,\%) & $0{,}00\text{ km}$ ($0{,}0$\,\%) \\
La Greda & \texttt{sinca\_la\_greda} & $6{,}71\text{ km}$ & $11$ & $7{,}5\text{ min}$ & $+7{,}0\text{ m}$ & $0{,}39\text{ km}$ ($5{,}8$\,\%) & $3{,}33\text{ km}$ ($49{,}6$\,\%) \\
Ventanas & \texttt{sinca\_ventanas} & $7{,}80\text{ km}$ & $14$ & $8{,}7\text{ min}$ & $-16{,}0\text{ m}$ & $0{,}70\text{ km}$ ($9{,}0$\,\%) & $4{,}41\text{ km}$ ($56{,}5$\,\%) \\
Campiche & \texttt{sinca\_campiche} & $9{,}53\text{ km}$ & $16$ & $10{,}6\text{ min}$ & $+2{,}0\text{ m}$ & $0{,}39\text{ km}$ ($4{,}1$\,\%) & $6{,}15\text{ km}$ ($64{,}5$\,\%) \\
Puchuncaví & \texttt{sinca\_puchuncavi} & $14{,}41\text{ km}$ & $22$ & $16{,}0\text{ min}$ & $+67{,}0\text{ m}$ & $0{,}79\text{ km}$ ($5{,}5$\,\%) & $7{,}58\text{ km}$ ($52{,}6$\,\%) \\
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
Termoeléctrica Ventanas (AES) & Industria & $7{,}48\text{ km}$ & $13$ & $8{,}3\text{ min}$ & $-14{,}0\text{ m}$ & Proximidad a fuentes de emisión y efluentes térmicos \\
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
    \item \textbf{Accesibilidad y Autonomía de Vuelo Unificada:} Con una velocidad nominal fijada en $v = 15\text{ m/s}$ y una autonomía operacional de $39{,}6\text{ km}$ ($44\text{ min}$ con reserva del $20$\,\%, S6):
    \begin{itemize}
        \item Las misiones hacia Quintero, Loncura y Sur ($1{,}69\text{ km}$ a $3{,}74\text{ km}$) requieren trayectos de ida y vuelta inferiores a $7{,}5\text{ km}$ ($<8{,}4\text{ min}$ de vuelo), consumiendo menos del $19$\,\% de la batería y garantizando autonomía para extensas campañas de muestreo estacionario.
        \item Hacia el complejo industrial de Ventanas y La Greda ($6{,}71\text{ km}$ a $7{,}80\text{ km}$), el viaje completo de ida y retorno insume entre $13{,}4\text{ km}$ y $15{,}6\text{ km}$ ($15$ a $17{,}4\text{ min}$ de vuelo), utilizando el $39{,}4$\,\% de la capacidad operacional y permitiendo muestrear la pluma de chimeneas con seguridad.
        \item Hacia la estación interior de Puchuncaví ($14{,}41\text{ km}$), el vuelo de ida y vuelta asciende a $28{,}82\text{ km}$ ($32\text{ min}$ de vuelo neto). Este recorrido insume el $72{,}8$\,\% de la autonomía operacional efectiva, dejando una ventana de muestreo en sitio inferior a $12\text{ min}$, lo que fundamenta la necesidad de incorporar bases de recarga intermedia en el sector norte.
    \end{itemize}
    \item \textbf{Incidencia del Relieve Orográfico ($\Delta z$):} Los destinos costeros presentan desniveles negativos respecto al aeródromo ($\Delta z \in [-23{,}0; -3{,}0]\text{ m}$), mientras que las rutas hacia el interior ascienden sostenidamente: $+7{,}0\text{ m}$ en La Greda, $+14{,}0\text{ m}$ en La Chocota y $+67{,}0\text{ m}$ en Puchuncaví (alcanzando una cota absoluta de $95\text{ msnm}$ sobre la estación). Este hallazgo valida la integración del perfil SRTM para ajustar dinámicamente la altitud barométrica y asegurar el respeto estricto al límite legal de $120\text{ m}$ AGL de la norma DAN 151 sobre el terreno \cite{dan151}.
    \item \textbf{Evidencia Cuantitativa de la Exposición al Riesgo (Peor Caso):} Al optimizar únicamente la distancia geodésica, Dijkstra traza caminos que vulneran principios de seguridad operacional:
    \begin{itemize}
        \item \textit{Riesgo en tierra:} En Quintero Centro, el $45{,}1$\,\% de la ruta ($1{,}06\text{ km}$) sobrevuela directamente manzanas con densidad habitacional $>2.500\text{ hab/km}^2$, maximizando el riesgo de daños a terceros en caso de aterrizaje forzoso.
        \item \textit{Riesgo de pérdida de enlace (C2):} Hacia el norte de la bahía, las rutas atraviesan extensas sombras celulares: $3{,}33\text{ km}$ en La Greda ($49{,}6$\,\%), $4{,}41\text{ km}$ en Ventanas ($56{,}5$\,\%) y $7{,}58\text{ km}$ en Puchuncaví ($52{,}6$\,\% de la ruta total sin cobertura), exponiendo al UAV a pérdida prolongada de telemetría.
    \end{itemize}
    Estos datos numéricos confirman objetivamente que la ruta de mínima distancia euclidiana constituye el peor caso de exposición, lo que demuestra la necesidad de incorporar activamente la metadata territorial y los eventos dinámicos en la función de costo multiobjetivo.

    \item \textbf{Régimen Aeronáutico y Restricción Legal de Línea de Vista (VLOS vs. BVLOS):} Conforme a la normativa aeronáutica chilena DAN 151 de la DGAC \cite{dan151}, la operación estándar de UAV está restringida a la línea de vista directa no asistida del piloto (VLOS, radio máximo general de $500\text{ m}$ u $0{,}5\text{ km}$ respecto al punto de control). Rutas de largo alcance como la proyectada hacia la estación SINCA de Puchuncaví ($14{,}41\text{ km}$) o hacia el complejo de Ventanas ($7{,}80\text{ km}$) sobrepasan holgadamente dicho límite, constituyendo vuelos más allá de la línea de vista (BVLOS). En Chile, el marco regulatorio prohíbe el vuelo BVLOS estándar y exige obligatoriamente una \textbf{Autorización Especial de Operación de la DGAC}, la cual supedita la misión a la aprobación de un análisis de riesgo operacional SORA (JARUS \cite{sora}), enlace C2 redundante certificado y mecanismos de detección y evasión activa (DAA). En la plataforma interactiva del sistema, cualquier trayectoria que sobrepase el límite legal de $500\text{ m}$ es clasificada y destacada en color rojo como operación BVLOS condicionada a autorización especial aeronáutica.

    \item \textbf{Defensa Metodológica: ¿Por qué no bastan las estaciones de superficie y por qué el foco es el ruteo?:} Ante la interrogante de por qué no es suficiente la red de estaciones de monitoreo fijas terrestres, la evidencia oficial de la República de Chile es concluyente:
    \begin{itemize}
        \item \textit{La desconexión empírica de 2018:} Durante la crisis de agosto de 2018, las estaciones del SINCA registraron concentraciones de $\text{SO}_2$ estrictamente bajo la norma horaria ($<350\ \mu\text{g/m}^3\text{N}$), y sin embargo cientos de escolares y pobladores colapsaron los servicios asistenciales de urgencia por intoxicación aguda. La causa real radicó en compuestos orgánicos volátiles (BTEX), formaldehído y sulfuro de hidrógeno no monitoreados por la red fija, combinados con una inversión térmica marina a $400\text{ m}$ sobre el suelo que sólo pudo detectarse recurriendo a un radiosondeo a $100\text{ km}$ al sur en Santo Domingo \cite{sma_dictuc}. Las estaciones terrestres miden adecuadamente los contaminantes normados para los que fueron instaladas, pero carecen de resolución vertical y son ciegas a efluentes atrapados en altura.
        \item \textit{El verdadero núcleo de la investigación:} La contribución de esta tesis no radica en la fabricación de sensores químicos ni en la modelación de la cinética de gases. Los antecedentes de la SMA, el PPDA y el CR2 demuestran de forma irrebatible \textbf{por qué es imprescindible volar en la bahía}. El problema que resuelve esta ingeniería es \textbf{cómo volar de forma segura, robusta y resiliente}: planificar rutas que eviten el impacto a terceros sobre zonas pobladas (SORA), eludan chimeneas de hasta $152\text{ m}$ y líneas de alta tensión, cedan el paso a aeronaves tripuladas en el Aeródromo de Quintero (SCER), no vulneren los límites aerodinámicos de viento ($12\text{ m/s}$) ni visibilidad VMC, y alerten el régimen legal BVLOS según la DAN 151.
    \end{itemize}
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

\subsection{Registro de Ejecución del Pipeline (\texttt{main.py})}
\label{subsec:log_main}

El script \texttt{main.py} orquesta el pipeline completo en Docker. A continuación se reproduce el extracto del registro real obtenido al ejecutar el comando con el resumen de conteos finales en base de datos:

\begin{lstlisting}[language=bash]
== Docker: construir la imagen del ETL
== Base de datos: PostgreSQL 16 + PostGIS + pgRouting
== Base de datos: crear el esquema desde cero (bd/schema.sql)
== Carga a la BD · Nodos
== Carga a la BD · Aristas
== Carga a la BD · Zonas urbanas
== Carga a la BD · Calidad del aire (SINCA)
== Carga a la BD · Relieve por arista (SRTM)
== Carga a la BD · Manzanas (INE)
== Carga a la BD · Antenas (OSM)
== Carga a la BD · Incendios
== Carga a la BD · Aeronaves
== Carga a la BD · Viento
== Carga a la BD · Niebla
== Ruteo base: pgr_dijkstra desde la base hacia cada estacion SINCA (costo = longitud)
== Sitio web (Leaflet)
== Conteos en la BD
        tabla         | count 
----------------------+-------
 infra_node           |   237
 infra_edge           |   633
 urban_zone           |     8
 meta_air_quality     |    52
 meta_edge_terrain    |   633
 meta_census_block    |   703
 meta_telecom_antenna |    25
 threat_event         |    34
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
    \item \textbf{Respuesta a P1 (Integración automatizada y reproducibilidad):} Se comprobó la viabilidad de integrar de forma desatendida $8$ fuentes heterogéneas. La arquitectura de microservicios contenerizada en Docker, respaldada por la tabla maestra \texttt{data\_source}, asegura la trazabilidad inmutable de la procedencia y marca temporal UTC de cada ingesta, permitiendo regenerar el sistema desde cero o mediante la opción \texttt{--sin-descarga}.
    \item \textbf{Respuesta a P2 (Conexidad y navegabilidad territorial):} La construcción topológica mediante $K=4$ vecinos y dos aristas puente Union-Find garantizó un grafo estrictamente conexo ($1$ sola componente conexa verificada con \texttt{pgr\_connectedComponents}) compuesto por $237$ nodos y $633$ aristas, asegurando la navegabilidad física hacia las $8$ estaciones SINCA y receptores críticos desde el aeródromo.
    \item \textbf{Respuesta a P3 (Exposición cuantitativa de la línea base):} La evaluación sobre la ruta de Dijkstra confirmó numéricamente su vulnerabilidad como peor caso de referencia: la minimización de la distancia física expone la nave a $1{,}06\text{ km}$ sobre manzanas residenciales densas en Quintero y a $7{,}58\text{ km}$ en sombras de cobertura celular C2 hacia Puchuncaví ($52{,}6$\,\% del trayecto), confirmando que la distancia por sí sola es un criterio insuficiente para la navegación segura.
\end{enumerate}

\subsection{Limitaciones de la Investigación}
\label{subsec:limitaciones_investigacion}

\begin{itemize}
    \item \textbf{Topología con $K=4$ fija:} No se comparó la sensibilidad frente a otros valores de $K$, lo cual condiciona los corredores y concentra los enlaces en el istmo de Quintero.
    \item \textbf{Corredores rectilíneos en plano 2D:} No se modelan curvas de nivel tridimensionales continuas ni maniobras dinámicas de evasión cinemática.
    \item \textbf{Aproximaciones geométricas:} El cálculo de Haversine asume una esfera perfecta (error medio de $0{,}46\text{ m}$ frente a WGS84) y los círculos de exclusión se discretizan a $32$ vértices.
    \item \textbf{Ventana temporal de FIRMS:} La ventana de 7 días puede incluir focos térmicos extinguidos al momento de la misión.
    \item \textbf{Desfase censal y subregistro C2:} El Censo 2017 puede subestimar áreas residenciales nuevas, y el subregistro voluntario de OpenStreetMap sobreestima las zonas en sombra celular.
\end{itemize}

\subsection{Trabajo Futuro y Proyecciones}
\label{subsec:trabajo_futuro}

A partir de los resultados y la infraestructura geoespacial consolidada, se establecen tres líneas prioritarias de trabajo futuro:

\begin{enumerate}
    \item \textbf{Ampliación de la red y mapeo de nuevos puntos de interés territorial:}
    El área geográfica de Quintero y Puchuncaví alberga una multiplicidad de zonas con dinámicas de emisión y exposición disímiles. Como desarrollo inmediato, se proyecta extender el catastro topológico de nodos hacia sectores no cubiertos en la red inicial, incorporando sectores residenciales rurales en Campiche y La Chocota, zonas agrícolas en el valle interior de Puchuncaví, y áreas de expansión portuaria y turística en Maitencillo y Concón. Esta densificación geográfica permitirá capturar con mayor resolución espacial los gradientes de contaminación y diseñar mallas de navegación con una cobertura territorial exhaustiva.

    \item \textbf{Evaluación y contraste de algoritmos avanzados de enrutamiento:}
    Habiendo establecido cuantitativamente el comportamiento de la ruta de menor distancia métrica mediante Dijkstra, los desarrollos posteriores explorarán y contrastarán diversos paradigmas de optimización de rutas:
    \begin{itemize}
        \item Implementación del algoritmo $A^*$ con heurísticas admisibles energéticas y orográficas para acelerar la convergencia del cómputo en misiones de largo alcance.
        \item Exploración de metaheurísticas poblacionales, tales como Algoritmos Genéticos (GA) y Optimización por Colonia de Hormigas (ACO), para resolver problemas de ruteo multi-parada (\textit{Traveling Salesperson Problem} con ventanas de tiempo), orientados a maximizar la captura de muestras en múltiples chimeneas y estaciones durante un único ciclo de vuelo.
        \item Implementación de esquemas de penalización iterativa para caminos disimilares ($k \ge 2$) basados en la metodología de Akgün et al. \cite{akgun}, garantizando que la aeronave disponga de corredores de contingencia espacialmente divergentes y desacoplados del camino principal sin incurrir en desvíos energéticos excesivos.
    \end{itemize}

    \item \textbf{Presencia activa y vinculante de la metadata y eventos dinámicos en el enrutamiento:}
    En la arquitectura actual, los metadatos territoriales y los eventos de amenaza operan como capas diagnósticas de auditoría. La siguiente etapa consiste en dotar a estas variables de presencia activa y vinculante en el proceso de optimización del planificador de trayectorias:
    \begin{itemize}
        \item \textit{Función de recompensa para calidad del aire (SINCA):} A diferencia de los factores de riesgo, las concentraciones de contaminantes ($\text{SO}_2, \text{MP}_{10}, \text{MP}_{2{,}5}$) no penalizan aristas, sino que definen una función de recompensa operacional ($\mathcal{R}(d)$). El algoritmo priorizará dinámicamente el despacho hacia la estación con mayores índices de polución en la última hora móvil, optimizando el valor científico del muestreo.
        \item \textit{Función de costo multiobjetivo con riesgo en aristas ($W(e)$):} Ponderación conjunta de la longitud física, el consumo energético ($EEE$) derivado del perfil orográfico SRTM (penalizando ascensos para respetar el techo legal de $120\text{ m}$ AGL de la DAN 151 \cite{dan151}), la penalización por sobrevuelo de manzanas con densidad habitacional $>2.500\text{ hab/km}^2$ según la directriz SORA \cite{sora}, un castigo de exposición para tramos en sombra de cobertura celular C2 (radio de $3.000\text{ m}$ para 4G LTE en banda 7/28 a $120\text{ m}$), y el bloqueo o penalización estricta frente a chimeneas industriales ($50\text{--}152\text{ m}$) y líneas de transmisión eléctrica de alta tensión ($110/220\text{ kV}$) integradas en la capa \texttt{osm\_obstaculos}. Se contempla incorporar datos de OpenCelliD \cite{opencellid} para reemplazar el radio estático por rangos empíricos por celda.
        \item \textit{Sistema dinámico de evitación de contingencias y restricciones aeronáuticas:} Inhabilitación temporal en tiempo real (\texttt{ST\_Intersects}) o penalización exponencial de aristas intersectadas por:
        \begin{itemize}
            \item Focos de incendios activos detectados por el producto VIIRS $375\text{ m}$ de NASA FIRMS \cite{schroeder} (círculo de exclusión de $2.000\text{ m}$ para evitar cizalladura térmica y conflicto con brigadas aéreas de combate).
            \item Aeronaves tripuladas en vuelo hacia el Aeródromo de Quintero (SCER) monitoreadas vía ADS-B con OpenSky Network \cite{opensky} (cilindro de protección de $1.500\text{ m}$ de radio y hasta $1.000\text{ m}$ MSL, asegurando el derecho de paso absoluto estipulado por la DGAC).
            \item Celdas meteorológicas de Open-Meteo \cite{openmeteo} con ráfagas de viento superiores a $12{,}0\text{ m/s}$ a $120\text{ m}$ AGL (límite estructural y de control de actitud del DJI Matrice 350 RTK \cite{dji}) o condiciones de niebla costera densa (visibilidad $<1.000\text{ m}$ o $\text{HR} \ge 95$\,\% con nubes bajas $\ge 80$\,\%, violando los mínimos de vuelo visual VMC).
        \end{itemize}
        \item \textit{Protocolo de retorno a base (RTH) adaptativo:} Ante eventos de contingencia o agotamiento de batería hacia el umbral de reserva del $20$\,\%, el sistema recalculará la ruta de regreso explotando el apantallamiento orográfico (vuelo en sotavento tras los cordones de cerros costeros) para mitigar el consumo ante vientos contrarios predominantes del suroeste.
    \end{itemize}
\end{enumerate}

\newpage

% ============================== REFERENCIAS ==============================
\begin{thebibliography}{99}
\addcontentsline{toc}{section}{Referencias}

\bibitem{ppda_concon} Ministerio del Medio Ambiente [MMA]. (2019). \textit{Decreto Supremo N.º 105: Establece Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví}. Santiago: Biblioteca del Congreso Nacional de Chile. Disponible en: \url{https://www.bcn.cl/leychile/navegar?idNorma=1130344}.

\bibitem{estaciones} Ministerio del Medio Ambiente [MMA]. (2019). \textit{Decreto Supremo N.º 105: Establece Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví}. Santiago: Biblioteca del Congreso Nacional de Chile. Disponible en: \url{https://www.bcn.cl/leychile/navegar?idNorma=1130344}.

\bibitem{sma_enap} Superintendencia del Medio Ambiente [SMA]. (2025). \textit{Resolución Exenta N.º 05080/2025: Aprueba Plan Operacional de ENAP Terminal Marítimo Quintero en el marco del Capítulo I del PPDA Concón, Quintero y Puchuncaví}. Santiago: Gobierno de Chile. Disponible en: \url{https://ppda.mma.gob.cl/wp-content/uploads/2025/07/Resolucion-05080-2025-PO-ENAP-Quintero.pdf}.

\bibitem{sma_dictuc} DICTUC. (2020). \textit{Servicio de Modelación de calidad del aire para la zona de Quintero-Puchuncaví} (Informe Final N.º 1535747). Documento preparado para la Superintendencia del Medio Ambiente. Santiago, Chile. Disponible en: \url{https://snifa.sma.gob.cl/General/Descargar/1107243743}.

\bibitem{mma_sinca_2021} Ministerio del Medio Ambiente. (2021). \textit{Informe nacional de calidad del aire: Redes de monitoreo oficiales}. Sistema Nacional de Información de Calidad del Aire (SINCA). Disponible en: \url{https://sinia.mma.gob.cl/}.

\bibitem{sma_estrategia_2023} Superintendencia del Medio Ambiente. (2023). \textit{Estrategia de fiscalización y monitoreo ambiental para el cordón industrial de Concón, Quintero y Puchuncaví}. Gobierno de Chile. Disponible en: \url{https://portal.sma.gob.cl/}.

\bibitem{cr2_campana_2022} Centro de Ciencia del Clima y la Resiliencia [CR2]. (2022). \textit{Campaña de terreno Quintero 2022: Análisis de la capa límite atmosférica y perfiles térmicos mediante plataformas UAV}. Universidad de Chile. Disponible en: \url{https://www.cr2.cl/}.

\bibitem{cr2_informe} Centro de Ciencia del Clima y la Resiliencia [CR2]. (2023). \textit{Informe de devolución: Estudio de contaminantes atmosféricos, determinantes e impactos en la Bahía de Quintero-Puchuncaví}. Santiago: Universidad de Chile. Disponible en: \url{https://www.cr2.cl/wp-content/uploads/2023/09/devolucion_quintero.pdf}.

\bibitem{mma_plan_2023} Ministerio del Medio Ambiente. (2023). \textit{Plan de modernización de la Red Pública de Monitoreo de Calidad del Aire para Concón, Quintero y Puchuncaví}. Gobierno de Chile. Disponible en: \url{https://airecqp.mma.gob.cl/}.

\bibitem{cifuentes} Cifuentes, L. (2018, 30 de agosto). \textit{Crisis en Quintero y Puchuncaví no se explica por los contaminantes que se miden}. Radio Pauta. Disponible en: \url{https://www.pauta.cl/cronica/crisis-en-quintero-y-puchuncavi-no-se-explica-por-los-contaminantes-que}.

\bibitem{mma_drones} Radio Agricultura. (2023, 16 de junio). \textit{Quintero y Puchuncaví: Anuncian aumento de fiscalizadores, nuevos equipos de medición y mejoras en alcantarillados de colegios}. Disponible en: \url{https://www.radioagricultura.cl/nacional/2023/06/16/quintero-y-puchuncavi-anuncian-aumento-de-fiscalizadores-nuevos-equipos-de-medicion-y-mejoras-en-alcantarillados-de-colegios/}.

\bibitem{sma_so2_2022} Superintendencia del Medio Ambiente [SMA]. (2022). \textit{Informe de fiscalización ambiental: Medición horaria extrema de SO2 estación Quintero} (Resolución Exenta N.º 20701004352). Santiago: Gobierno de Chile. Disponible en: \url{https://snifa.sma.gob.cl/General/Descargar/20701004352}.

\bibitem{eldesconcierto_2023} El Desconcierto. (2023, 28 de mayo). \textit{Más de 500 intoxicaciones en lo que va del año: ¿Quién contamina la bahía de Quintero?} Disponible en: \url{https://eldesconcierto.cl/2023/05/28/mas-de-500-intoxicaciones-en-lo-que-va-del-ano-quien-contamina-la-bahia-de-quintero/amp}.

\bibitem{sinca} Ministerio del Medio Ambiente [MMA]. (2026). \textit{Sistema de Información Nacional de Calidad del Aire (SINCA)}. Santiago: Gobierno de Chile. Disponible en: \url{https://sinca.mma.gob.cl}. Consultado el 20 de octubre de 2026.

\bibitem{kosior} Kosior, J., Grygierek, E., \& Piechaczek, J. (2024). Global and local flight path planning for unmanned aerial vehicles in air-pollution monitoring systems. \textit{Atmospheric Environment}, 318, 120--135. doi: \url{https://doi.org/10.1016/j.atmosenv.2023.120135}.

\bibitem{dan151} Dirección General de Aeronáutica Civil [DGAC]. (2024). \textit{DAN 151: Operaciones de aeronaves pilotadas a distancia (RPAS) en asuntos de interés público, que se efectúen sobre áreas pobladas} (3.ª ed.). Santiago: Gobierno de Chile. Disponible en: \url{https://www.dgac.gob.cl/wp-content/uploads/2024/05/DAN-151-ED3-27MAY2024.pdf}.

\bibitem{sora} Joint Authorities for Rulemaking on Unmanned Systems [JARUS]. (2024). \textit{JARUS guidelines on Specific Operations Risk Assessment (SORA)} (Versión 2.5). Disponible en: \url{https://jarus-rpas.org}.

\bibitem{dijkstra} Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. \textit{Numerische Mathematik}, 1(1), 269--271. doi: \url{https://doi.org/10.1007/BF01386390}.

\bibitem{pgrouting} pgRouting Community. (2026). \textit{pgRouting Manual} (Versión 3.8.0). Disponible en: \url{https://docs.pgrouting.org/3.8/en/index.html}.

\bibitem{postgis} PostGIS Project Steering Committee. (2026). \textit{PostGIS 3.5.2 Manual}. Disponible en: \url{https://postgis.net/docs/manual-3.5/}.

\bibitem{yen} Yen, J. Y. (1971). Finding the $k$ shortest loopless paths in a network. \textit{Management Science}, 17(11), 712--716. doi: \url{https://doi.org/10.1287/mnsc.17.11.712}.

\bibitem{suurballe} Suurballe, J. W. (1974). Disjoint paths in a network. \textit{Networks}, 4(2), 125--145. doi: \url{https://doi.org/10.1002/net.3230040204}.

\bibitem{bhandari} Bhandari, R. (1999). \textit{Survivable Networks: Algorithms for Diverse Routing}. Boston, MA: Kluwer Academic Publishers. doi: \url{https://doi.org/10.1007/978-1-4615-5207-9}.

\bibitem{akgun} Akgün, V., Erkut, E., \& Batta, R. (2000). On finding dissimilar paths. \textit{European Journal of Operational Research}, 121(2), 232--246. doi: \url{https://doi.org/10.1016/S0377-2217(99)00214-3}.

\bibitem{petritoli} Petritoli, E., Leccese, F., \& Ciani, L. (2018). Reliability and maintenance analysis of unmanned aerial vehicles. \textit{Sensors}, 18(9), Artículo 3171. doi: \url{https://doi.org/10.3390/s18093171}.

\bibitem{schroeder} Schroeder, W., Oliva, P., Giglio, L., \& Csiszar, I. A. (2014). The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment. \textit{Remote Sensing of Environment}, 143, 85--96. doi: \url{https://doi.org/10.1016/j.rse.2013.12.008}.

\bibitem{rfc7946} Butler, H., Daly, M., Doyle, A., Gillies, S., Hagen, S., \& Schaub, T. (2016). \textit{The GeoJSON Format} (RFC 7946). Internet Engineering Task Force (IETF). doi: \url{https://doi.org/10.17487/RFC7946}.

\bibitem{dji} DJI Enterprise. (2024). \textit{DJI Matrice 350 RTK: Especificaciones técnicas oficiales}. Disponible en: \url{https://enterprise.dji.com/matrice-350-rtk/specs}.

\bibitem{opentopo} OpenTopoData. (2026). \textit{SRTM 30 m Elevation API}. Disponible en: \url{https://www.opentopodata.org}.

\bibitem{idesma} Superintendencia del Medio Ambiente [SMA]. (2026). \textit{Infraestructura de Datos Geoespaciales: Capa de manzanas censales (INE, Censo 2017)}. Santiago: IDE SMA. Disponible en: \url{https://ideserver.sma.gob.cl}.

\bibitem{overpass} OpenStreetMap Contributors. (2026). \textit{Overpass API: OpenStreetMap Data Extraction}. Disponible en: \url{https://overpass-api.de}.

\bibitem{firms} National Aeronautics and Space Administration [NASA]. (2026). \textit{Fire Information for Resource Management System (FIRMS)}. NASA Earthdata. Disponible en: \url{https://firms.modaps.eosdis.nasa.gov}.

\bibitem{opensky} Schäfer, M., Strohmeier, M., Lenders, V., Martinovic, I., \& Wilhelm, M. (2014). Bringing up OpenSky: A large-scale ADS-B sensor network for research. En \textit{Proceedings of the 13th International Symposium on Information Processing in Sensor Networks (IPSN)} (pp. 83--94). Berlin: IEEE/ACM. doi: \url{https://doi.org/10.1109/IPSN.2014.6846743}.

\bibitem{openmeteo} Open-Meteo. (2026). \textit{Weather Forecast and Marine API: Wind Vectors, Fog, and Low Cloud Cover}. Disponible en: \url{https://open-meteo.com}.

\bibitem{opencellid} Unwired Labs. (2026). \textit{The OpenCelliD Project: Collaborative Community Cellular Tower Database}. Disponible en: \url{https://opencellid.org}.

\bibitem{altura} Ministerio del Medio Ambiente [MMA]. (2019). \textit{Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví: Memoria Técnica y Modelación de Dispersión}. Santiago: Gobierno de Chile.

\end{thebibliography}

\end{document}
