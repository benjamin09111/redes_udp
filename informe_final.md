\documentclass[letterpaper,12pt]{article}
\usepackage[paperheight=27.94cm,paperwidth=21.59cm,bindingoffset=0in,left=3cm,right=2.0cm,top=3.5cm,bottom=2.5cm,headheight=40pt,headsep=1.0\baselineskip]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-tabla,es-noshorthands]{babel}
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

% Indice: ancho del numero de seccion para que "10." no quede pegado al titulo
\makeatletter
\renewcommand*\l@section{\@dottedtocline{1}{0em}{2.3em}}
\renewcommand*\l@subsection{\@dottedtocline{2}{2.3em}{3.2em}}
\makeatother

% Configuracion de codigo SQL y bash
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
{\fbox{\parbox[c][3cm][c]{\dimexpr#1-2\fboxsep-2\fboxrule\relax}{\centering\small Falta la imagen:\\\texttt{\detokenize{#2}}}}}}

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
{\scshape\LARGE Fase 2: Ruteo resiliente de UAV para el muestreo de contaminación en la Bahía de Quintero \par}
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
\tableofcontents
\newpage

% ============================== 1 ==============================
\section{Introducción}
\label{sec:introduccion}

El cordón industrial y costero de Quintero, Ventanas y Puchuncaví constituye una de las zonas de mayor vulnerabilidad y saturación atmosférica de Chile, sujeta prioritariamente a las medidas del Plan de Prevención y Descontaminación Atmosférica (PPDA) \cite{estaciones}. En este territorio opera la red de estaciones del Sistema de Información Nacional de Calidad del Aire (SINCA), las cuales registran concentraciones de material particulado ($\text{MP}_{10}$, $\text{MP}_{2.5}$) y dióxido de azufre ($\text{SO}_2$) exclusivamente a nivel de superficie \cite{sinca}. No obstante, los complejos termoeléctricos, fundiciones y terminales de hidrocarburos evacuan sus efluentes a través de chimeneas industriales situadas entre $50\text{ m}$ y $110\text{ m}$ de altitud. A estas cotas, los gases y aerosoles quedan confinados bajo la capa de inversión térmica marina antes de descender hacia los centros poblados mediante el fenómeno de fumigación costera \cite{altura}.

El empleo de Vehículos Aéreos No Tripulados (UAV) operando en el estrato de $0$ a $120\text{ m}$ AGL (\textit{Above Ground Level}), conforme a las atribuciones de la norma técnica aeronáutica DAN 151 de la Dirección General de Aeronáutica Civil (DGAC) \cite{dan151}, ofrece una oportunidad sin precedentes para interceptar y caracterizar la pluma contaminante directamente en altura antes de su dispersión en tierra.

\subsection{Planteamiento del Problema}
\label{subsec:problema}

La supervisión de la calidad del aire y la gestión del riesgo aéreo en este litoral enfrentan una doble problemática interdependiente:

\begin{enumerate}
    \item \textbf{Ceguera vertical de la red de monitoreo superficial:} Las estaciones terrestres presentan un retardo temporal crítico; solo detectan el contaminante cuando la pluma ya ha fumigado las zonas residenciales. Al no existir un perfil vertical de muestreo, se desconoce la concentración real en la capa de mezcla y la magnitud de la pérdida de información entre el estrato de emisión industrial ($50$--$110\text{ m}$) y el suelo.
    \item \textbf{Fragilidad operacional del enrutamiento aéreo convencional:} La navegación de un UAV en la bahía no puede basarse en trayectorias geodésicas en línea recta ni en la distancia euclidiana mínima. El espacio aéreo de Quintero y Puchuncaví impone severas restricciones: proximidad a zonas densamente pobladas y recintos sensibles (escuelas y centros de salud) donde un fallo mecánico maximiza el riesgo a terceros en tierra; turbulencia costera y ráfagas que superan la envolvente de vuelo; precipitaciones que vulneran la estanqueidad de la nave; e intermitencia en el enlace de mando y control (C2) celular por sombras de cobertura. Un enrutador que ignore estas variables expone a la aeronave a colisiones, pérdida de enlace (\textit{fly-away}) o abortos de misión.
\end{enumerate}

\subsection{Solución Propuesta y Utilidad del Proyecto}
\label{subsec:solucion}

Para resolver esta brecha, el proyecto propone una plataforma integral de modelado geoespacial y enrutamiento resiliente para UAVs. La arquitectura de datos y la red de vuelo se diseñaron bajo criterios operacionales específicos:

\begin{itemize}
    \item \textbf{Infraestructura del grafo ($237$ nodos y $633$ aristas):} La topología no sigue la traza vial terrestre, sino corredores aéreos rectilíneos. Su origen operacional es el Aeródromo de Quintero (código \texttt{base\_scer}), único punto habilitado logísticamente y autorizado bajo la DAN 151 Art. 9 para operaciones aéreas coordinadas. Los nodos abarcan las fuentes emisoras industriales, los receptores residenciales vulnerables (salud y educación) y, principalmente, las $8$ estaciones de monitoreo SINCA del área.
    \item \textbf{Construcción de aristas por $K$-vecinos y Union-Find ($633$ enlaces):} Para evitar la fragilidad de grafos lineales y prescindir de una malla completa computacionalmente inviable, cada nodo se enlazó a sus $K=4$ vecinos más cercanos mediante distancia de semiverseno (\textit{haversine}). Esto produce un grado medio de conectividad de $\bar{d} \approx 5{,}34$ aristas por nodo, garantizando suficientes caminos alternativos para evasión de amenazas. Debido a la fragmentación espacial que impone la bahía marina, se aplicó el algoritmo \textit{Union-Find} para detectar componentes disjuntas, incorporando deterministamente $2$ aristas puente de mínima separación inter-cluster. Con ello se asegura matemáticamente una red $100\,\%$ conexa ($1$ sola componente), permitiendo que cualquier estación SINCA sea accesible desde el aeródromo.
    \item \textbf{Muestreo en estaciones SINCA y co-localización de sensores:} Los destinos prioritarios de la red son las estaciones SINCA debido a que constituyen la verdad de terreno (\textit{ground-truth}) oficial. Planificar misiones hacia estos nodos permite la \textbf{co-localización sensorial}: el UAV muestrea la vertical a diferentes cotas ($50$, $80$ y $110\text{ m}$) exactamente sobre el sensor terrestre de referencia. Esta estrategia permitirá, en fases posteriores, comparar estadísticamente los registros de altura con las series históricas de suelo, cuantificando la discrepancia vertical y determinando cuánta masa contaminante escapa a la red de monitoreo tradicional. Asimismo, la posibilidad de seleccionar zonas de interés sensibles (hospitales y escuelas) permite planificar auditorías en receptores críticos de alta exposición poblacional.
    \item \textbf{Metadata ambiental y de soporte a la navegación ($4$ capas):} Se integró el modelo de elevación SRTM (para respetar los $120\text{ m}$ AGL según el relieve costero), la densidad habitacional por manzana censal del INE (para cuantificar el riesgo a terceros según la metodología SORA), la cobertura radioeléctrica de antenas celulares (para asegurar el enlace C2) y los registros horarios de calidad del aire del SINCA.
    \item \textbf{Amenazas dinámicas al vuelo ($4$ capas):} Se modelaron zonas de exclusión activa para campos de viento crítico ($\ge 14\text{ m/s}$), lluvia intensa ($\ge 2\text{ mm/h}$), focos de incendios forestales (amortiguamiento de $2000\text{ m}$ por turbulencia térmica y combate aéreo) y actividad sísmica superficial.
\end{itemize}

En esta segunda fase se implementó un proceso ETL automatizado y reproducible sobre contenedores Docker, cargando la información en PostgreSQL/PostGIS/pgRouting. Sobre esta infraestructura se computa la ruta de menor longitud mediante el algoritmo \texttt{pgr\_dijkstra}. Esta ruta constituye la \textbf{línea base del peor caso}: al optimizar únicamente la distancia física y desestimar la metadata y las amenazas activas, evidencia cuantitativamente el nivel de exposición al riesgo al que se sometería una aeronave con navegación convencional. La solución entrega a las autoridades ambientales y operadores una plataforma cartográfica interactiva en Leaflet para auditar estas rutas frente a las capas de amenaza en tiempo real.

\vspace{0.3cm}

El código fuente, scripts ETL, esquema de base de datos y plataforma web se encuentran alojados en el repositorio oficial del curso: \url{https://giteit.udp.cl/CIT3435/2026-2/trabajo-grupal/grupo09}.

% ============================== 2 ==============================
\section{Objetivos del Proyecto}
\label{sec:objetivos}

\subsection{Objetivo General}

Construir una base de datos geoespacial reproducible que integre la infraestructura de la red aérea, cuatro fuentes de metadata y cuatro fuentes de amenazas en el área de Quintero, Ventanas y Puchuncaví, y obtener sobre ella la ruta de menor longitud mediante \texttt{pgr\_dijkstra} como línea base y escenario de peor caso para la evaluación del ruteo resiliente.

\subsection{Objetivos Específicos}

\begin{enumerate}
    \item Diseñar e inicializar una base de datos relacional-espacial en PostgreSQL 16 con las extensiones PostGIS 3.5 y pgRouting 3.8, estructurada en 9 tablas que alberguen la topología de la red, los metadatos territoriales y los eventos de amenaza.
    \item Automatizar la extracción y modelado de la red aérea en un grafo espacial no dirigido de 237 nodos, 633 aristas y 8 polígonos de zonas urbanas, estandarizados bajo el formato RFC 7946 GeoJSON.
    \item Implementar scripts modulares de extracción para 4 fuentes de datos de soporte operacional: calidad del aire en tiempo real (SINCA MMA), perfiles altimétricos por arista (NASA SRTM 30m), densidad de población censal (INE 2017) y radiobases celulares para telemetría (OpenStreetMap).
    \item Implementar extractores automatizados para 4 fuentes de contingencias ambientales: focos de incendios activos (NASA FIRMS), sismicidad reciente (CSN / EMSC), vectores de viento y ráfagas (Open-Meteo) y tasa horaria de precipitación (MET Norway).
    \item Calcular mediante \texttt{pgr\_dijkstra} en base de datos la ruta de menor distancia física en metros desde el Aeródromo de Quintero hacia las 8 estaciones SINCA de la red, estableciendo el peor caso de exposición frente a las amenazas del entorno.
    \item Implementar una aplicación interactiva en Leaflet que permita visualizar las 11 capas temáticas y presentar la ruta base calculada junto con sus métricas operacionales.
    \item Orquestar de extremo a extremo las etapas de extracción, creación de esquema, carga de datos y ruteo en un script maestro \texttt{main.py}, asegurando su ejecución en contenedores Docker y validando su integridad mediante una suite de 57 pruebas automatizadas.
\end{enumerate}

% ============================== 3 ==============================
\section{Alcance y Supuestos Operacionales}
\label{sec:alcance}

\begin{itemize}
    \item \textbf{Planificación previa al despegue:} La solución corresponde al nivel de planificación estratégica offline (\textit{Global Path Planning}, GPP) \cite{kosior}, sin replanificación reactiva a bordo ni operaciones multi-UAV simultáneas en esta fase.
    \item \textbf{Origen y destinos de la misión:} El origen operacional oficial está fijado en el Aeródromo de Quintero (\texttt{base\_scer}). Los destinos primarios corresponden a las $8$ estaciones SINCA de la red, permitiendo además la selección de cualquier nodo del mapa para inspección interactiva.
    \item \textbf{Navegación bidimensional y costo métrico:} En esta Fase 2, el grafo opera sobre corredores aéreos rectilíneos donde el único costo de cada arista es su longitud geodésica ($c(e) = \text{length\_m}$). No se optimiza el consumo energético ni se penalizan las amenazas en la función de costo.
    \item \textbf{Línea base del peor caso:} El enrutamiento se ejecuta exclusivamente con el algoritmo de Dijkstra, generando el escenario de comparación más vulnerable contra el cual se evaluará el ruteo resiliente multiobjetivo en la Fase 3.
\end{itemize}

\newpage

% ============================== 4 ==============================
\section{Arquitectura del Sistema y Proceso ETL}
\label{sec:arquitectura}

\subsection{Visión General del Pipeline}
\label{subsec:arquitectura_vision}

Para asegurar la reproducibilidad científica y aislar las dependencias del sistema anfitrión, la plataforma se implementó bajo una arquitectura modular de microservicios contenerizada en \textbf{Docker} y orquestada con \textbf{Docker Compose} (\texttt{docker-compose.yml}).

El flujo de procesamiento de datos sigue un esquema secuencial desacoplado de cuatro fases (ver Figura~\ref{fig:arquitectura}):
\begin{enumerate}
    \item \textbf{Extracción:} 9 scripts independientes consultan APIs públicas y datasets maestros.
    \item \textbf{Transformación:} Normalización de geometrías, ajuste de unidades, proyección de distancias Haversine y generación de archivos GeoJSON conformes a la norma RFC 7946 con un bloque de metadatos \texttt{etl}.
    \item \textbf{Carga:} 11 cargadores Python realizan inserciones transaccionales masivas en PostgreSQL mediante \texttt{bd/conexion.py}.
    \item \textbf{Inferencia y Ruteo:} Ejecución de \texttt{pgr\_dijkstra} en pgRouting y serialización de resultados hacia la interfaz web.
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
\node[caja={blue!8}, right=of x] (g) {GeoJSON con bloque \texttt{etl}\\y documentación \texttt{.md}};
\node[caja={blue!8}, below=of g] (c) {Cargadores transaccionales\\\texttt{cargar\_*.py}};
\node[caja={green!10}, left=of c] (b) {PostgreSQL 16.9 +\\PostGIS 3.5 + pgRouting 3.8};
\node[caja={blue!8}, left=of b] (r) {Ruteo: \texttt{pgr\_dijkstra}\\(\texttt{cost} = \texttt{length\_m})};
\node[caja={orange!12}, below=of r] (w) {Sitio web Leaflet\\(puerto 8000)};
\draw[flecha] (f) -- (x); \draw[flecha] (x) -- (g); \draw[flecha] (g) -- (c);
\draw[flecha] (c) -- (b); \draw[flecha] (b) -- (r); \draw[flecha] (r) -- (w);
\end{tikzpicture}
\caption{Arquitectura del pipeline ETL y microservicios Docker. Azul: contenedor \texttt{etl}; verde: contenedor \texttt{db}; naranja: contenedor \texttt{web}; gris: fuentes externas.}
\label{fig:arquitectura}
\end{figure}

\subsection{Cálculo de Distancias, Geometrías y Superficies Espaciales}
\label{subsec:calculo_distancias}

Para prescindir de librerías binarias complejas (GDAL/GeoPandas) durante el ETL, las transformaciones espaciales se implementaron exclusivamente con la biblioteca estándar de Python:
\begin{enumerate}
    \item \textbf{Longitud geodésica de aristas (Fórmula de Haversine):} La distancia entre dos vértices $u=(\phi_1, \lambda_1)$ y $v=(\phi_2, \lambda_2)$ se calcula asumiendo una esfera terrestre de radio medio $R = 6.371.000\text{ m}$:
    \begin{equation}
        d(u,v) = 2 R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)
        \label{eq:haversine}
    \end{equation}
    donde $\Delta \phi = \phi_2 - \phi_1$ y $\Delta \lambda = \lambda_2 - \lambda_1$ en radianes. Este valor se almacena en el atributo \texttt{length\_m}. En la auditoría frente al cálculo elipsoidal de PostGIS (\texttt{ST\_Length(geom::geography)} sobre WGS84), el error medio es inferior al $0{,}12\,\%$ (discrepancia absoluta $< 1{,}2\text{ m}$ en aristas kilométricas), margen despreciable para operaciones UAV.
    \item \textbf{Generación de círculos de cobertura y amortiguamiento:} Los radios métricos de antenas ($3.000\text{ m}$) y focos de calor ($2.000\text{ m}$) se proyectan al espacio angular $(\Delta \lambda, \Delta \phi)$ ajustando por la latitud local $\phi$:
    \begin{equation}
        \Delta \phi = \frac{R_m}{111.320}, \quad \Delta \lambda = \frac{R_m}{111.320 \cdot \cos(\phi)}
    \end{equation}
    A partir de estos deltas, el contorno circular se discretiza como un polígono regular cerrado de $n=32$ vértices:
    \begin{equation}
        \left( \lambda + \Delta \lambda \cos\left(\frac{2\pi i}{n}\right), \; \phi + \Delta \phi \sin\left(\frac{2\pi i}{n}\right) \right), \quad i \in \{0, \dots, n\}
    \end{equation}
    Esta discretización preserva la suavidad del límite operacional sin sobrecargar los índices GiST.
    \item \textbf{Área superficial y orientación de polígonos (RFC 7946):} Las áreas de manzanas censales y zonas urbanas se calculan proyectando las coordenadas a un plano equirrectangular local tangente a la latitud media $\phi_0$ ($x_i = R \cdot \lambda_i \cos(\phi_0)$, $y_i = R \cdot \phi_i$) y aplicando la fórmula de Gauss (\textit{Shoelace}):
    \begin{equation}
        A = \frac{1}{2} \sum_{i=1}^{k} (x_i y_{i+1} - x_{i+1} y_i)
    \end{equation}
    El signo de $A$ determina la orientación del anillo. Conforme a RFC 7946, se asegura que el anillo exterior posea orientación antihoraria ($A > 0$) y los huecos interiores sigan el sentido horario ($A < 0$), corrigiendo la convención inversa provista por los servicios Esri ArcGIS REST.
\end{enumerate}

\subsection{Docker y Orquestación de Microservicios}
\label{subsec:docker_orquestacion}

El archivo \texttt{docker-compose.yml} define tres servicios especializados con versiones fijadas (ver Tabla~\ref{tab:docker}):

\begin{table}[H]
\centering
\small
\caption{Servicios definidos en \texttt{docker-compose.yml}.}
\label{tab:docker}
\begin{tabularx}{\linewidth}{|l|l|c|X|}
\hline
\textbf{Servicio} & \textbf{Imagen / Tag} & \textbf{Puerto} & \textbf{Rol y Responsabilidad} \\
\hline
\texttt{db} & \texttt{pgrouting/pgrouting:16-3.5-3.8.0} & \texttt{5433:5432} & Motor PostgreSQL 16.9, PostGIS 3.5.2 y pgRouting 3.8.0. Persistencia en volumen \texttt{uav\_pgdata} y \textit{healthcheck} (\texttt{pg\_isready}). \\
\hline
\texttt{etl} & \texttt{uav-ruteo:local} (\texttt{python:3.12.15-slim}) & — & Ejecución de extractores, cargadores y ruteo. Única dependencia externa: \texttt{psycopg[binary]==3.2.13}. \\
\hline
\texttt{web} & \texttt{uav-ruteo:local} (\texttt{python:3.12.15-slim}) & \texttt{8000:8000} & Servidor HTTP estático nativo (\texttt{http.server}) montado en solo lectura (\texttt{:ro}) para servir el visor Leaflet. \\
\hline
\end{tabularx}
\end{table}

\subsection{Reproducibilidad y Trazabilidad Operacional}
\label{subsec:reproducibilidad}

El script \texttt{main.py} orquesta de forma desatendida la construcción de contenedores, la creación del esquema (\texttt{bd/schema.sql}), las descargas de red, la carga transaccional, el cálculo de rutas y la verificación. Para entornos sin conexión a internet, incorpora la bandera:
\begin{lstlisting}[language=bash]
python3 main.py --sin-descarga
\end{lstlisting}
Este modo omite las consultas de red y carga directamente los archivos GeoJSON persistidos en el repositorio, asegurando la reproducibilidad íntegra del sistema. La tabla \texttt{data\_source} registra de forma inmutable la URL de origen y la marca temporal UTC \texttt{fetched\_at} de cada conjunto de datos ingestada.

% ============================== 5 ==============================
\section{Diseño e Implementación de la Base de Datos Espacial}
\label{sec:bd}

El modelo de almacenamiento relacional-espacial se estructuró sobre PostgreSQL 16.9 con PostGIS y pgRouting. La inicialización se realiza mediante \texttt{bd/schema.sql}, estructurando $9$ tablas (ver Figura~\ref{fig:bd} y Tabla~\ref{tab:bd}).

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\linewidth]{images/bd_diagrama.png}
\caption{Diagrama de entidades y relaciones de la base de datos (\texttt{bd/bd\_diagrama.puml}).}
\label{fig:bd}
\end{figure}

\begin{table}[htbp]
\centering
\small
\caption{Esquema relacional y resumen de registros cargados en PostgreSQL.}
\label{tab:bd}
\begin{tabularx}{\linewidth}{|l|l|X|r|}
\hline
\textbf{Tabla} & \textbf{Geometría} & \textbf{Contenido y Rol Operacional en la Fase 2} & \textbf{Filas} \\
\hline
\texttt{data\_source} & Ninguna & Catálogo maestro de trazabilidad ETL (fuente, URL y marca UTC). & $11$ \\
\hline
\texttt{infra\_node} & \texttt{Point} (4326) & Red de $237$ nodos y vértices de cálculo para pgRouting. & $237$ \\
\hline
\texttt{infra\_edge} & \texttt{LineString} (4326) & Corredores aéreos no dirigidos (\texttt{cost} = \texttt{reverse\_cost} = \texttt{length\_m}). & $633$ \\
\hline
\texttt{urban\_zone} & \texttt{MultiPolygon} (4326) & Polígonos de consolidación urbana de las $8$ localidades de la bahía. & $8$ \\
\hline
\texttt{meta\_air\_quality} & \texttt{Point} (4326) & Mediciones horarias de calidad del aire vinculadas a estaciones SINCA. & $52$ \\
\hline
\texttt{meta\_edge\_terrain} & Ninguna & Perfiles altimétricos muestreados cada $100\text{ m}$ (FK $1:1$ hacia \texttt{infra\_edge}). & $633$ \\
\hline
\texttt{meta\_census\_block} & \texttt{MultiPolygon} (4326) & Manzanas censales del INE con población, viviendas y densidad. & $703$ \\
\hline
\texttt{meta\_telecom\_antenna} & \texttt{Point} y \texttt{Polygon} & Ubicación de mástiles celulares y áreas de cobertura estimada ($3.000\text{ m}$). & $25$ \\
\hline
\texttt{threat\_event} & \texttt{Point} y \texttt{Polygon} & Eventos de amenazas dinámicas con área de exclusión y bandera \texttt{exceeds}. & $131$ \\
\hline
\end{tabularx}
\end{table}

\subsection{Integridad Referencial e Índices Espaciales GiST}
\label{subsec:bd_integridad}

\begin{enumerate}
    \item \textbf{Integridad de llaves foráneas:} Las aristas en \texttt{infra\_edge} referencian estrictamente a los vértices de origen y destino (\texttt{source} y \texttt{target} con \texttt{REFERENCES infra\_node(id)}), garantizando la integridad topológica requerida por pgRouting. La tabla \texttt{meta\_edge\_terrain} utiliza su clave primaria como foránea (\texttt{edge\_id REFERENCES infra\_edge(id) ON DELETE CASCADE}), y todas las tablas de metadata y amenazas vinculan su procedencia mediante \texttt{data\_source(id)}.
    \item \textbf{Tratamiento de estaciones SINCA:} La tabla \texttt{meta\_air\_quality} almacena $52$ mediciones individuales de $10$ estaciones del SINCA. Las $8$ estaciones situadas en el área de vuelo se asocian mediante su clave foránea (\texttt{node\_id REFERENCES infra\_node(id)}); las $2$ restantes (Valle Alegre y Los Maitenes) se conservan para trazabilidad ambiental manteniendo \texttt{node\_id} en \texttt{NULL}, preservando la consistencia relacional.
    \item \textbf{Indexación espacial GiST:} Se crearon índices \textit{Generalized Search Tree} (GiST) sobre todas las columnas geométricas (\texttt{infra\_node.geom}, \texttt{infra\_edge.geom}, \texttt{urban\_zone.geom}, \texttt{meta\_census\_block.geom}, \texttt{meta\_telecom\_antenna.coverage\_geom} y \texttt{threat\_event.geom}), permitiendo evaluaciones espaciales en tiempo sublineal $\mathcal{O}(\log N)$.
    \item \textbf{Desacoplamiento entre Amenazas y Red:} La tabla \texttt{threat\_event} no define llaves foráneas rígidas hacia la red. Dado que los incendios y vientos son fenómenos dinámicos y continuos en el espacio, la afectación se evalúa en tiempo de consulta mediante predicados geométricos (\texttt{ST\_Intersects(infra\_edge.geom, threat\_event.geom)} condicionado a \texttt{threat\_event.exceeds = true}).
\end{enumerate}

% ============================== 6 ==============================
\section{Infraestructura de la Red de Vuelo}
\label{sec:infra}

\subsection{Obtención y Construcción del Grafo Espacial}
\label{subsec:infra_obtencion}

La red se modela como un grafo de corredores aéreos rectilíneos. Su procesamiento en \texttt{infraestructura/extraer\_infraestructura.py} genera tres archivos GeoJSON:
\begin{itemize}
    \item \textbf{Nodos ($237$ vértices):} Puntos de interés y receptores de riesgo clasificados en $13$ categorías temáticas: áreas concurridas ($40$), fuentes emisoras industriales ($32$), gastronomía ($28$), educación ($26$), balnearios y playas ($22$), hospedaje ($21$), atractivos turísticos ($17$), centros de salud ($15$), patrimonio histórico ($13$), comercio ($12$), estaciones de calidad del aire SINCA ($8$), \textit{hubs} auxiliares ($2$) y la base operativa central en el Aeródromo de Quintero (\texttt{base\_scer}, $1$).
    \item \textbf{Aristas ($633$ enlaces bidireccionales):} Se construyen uniendo cada nodo con sus $K=4$ vecinos más cercanos según distancia Haversine. Debido a la fragmentación impuesta por la bahía, se aplicó el algoritmo \textit{Union-Find} para tender deterministamente $2$ aristas puente entre componentes disjuntas.
    \item \textbf{Propiedades topológicas:} El grafo es \textbf{no dirigido} (simétrico, con $\text{cost} = \text{reverse\_cost} = \text{length\_m}$) y \textbf{estrictamente conexo} ($1$ sola componente conexa verificada con \texttt{pgr\_connectedComponents}), asegurando la navegabilidad hacia cualquier punto desde la base.
    \item \textbf{Zonas Urbanas ($8$ polígonos):} Polígonos de consolidación urbana normalizados bajo RFC 7946 para cálculo de sobrevuelo poblacional.
\end{itemize}

\subsection{Estructura de los Datos GeoJSON}
\label{subsec:infra_json}

Cada conjunto de datos incluye su cabecera \texttt{etl} y su archivo de especificación Markdown (\texttt{nodos.md}, \texttt{aristas.md} y \texttt{zonas\_urbanas.md}) (ver Tabla~\ref{tab:json_infra}).

\begin{table}[htbp]
\centering
\small
\caption{Estructura de atributos en los archivos GeoJSON de infraestructura.}
\label{tab:json_infra}
\begin{tabularx}{\linewidth}{|l|l|X|}
\hline
\textbf{Archivo} & \textbf{Geometría} & \textbf{Campos Principales y Ejemplo Real} \\
\hline
\texttt{nodos.geojson} ($237$) & \texttt{Point} & \texttt{id} ($1$), \texttt{code} (\texttt{base\_scer}), \texttt{name}, \texttt{category} (\texttt{base}), \texttt{city} (\texttt{Quintero}), \texttt{elevation\_msnm} ($28{,}0$), \texttt{pollutants}. \\
\hline
\texttt{aristas.geojson} ($633$) & \texttt{LineString} & \texttt{id} ($1$), \texttt{source} ($1$), \texttt{target} ($14$), \texttt{source\_code}, \texttt{target\_code}, \texttt{length\_m} ($879{,}4$), \texttt{cost} ($879{,}4$), \texttt{reverse\_cost} ($879{,}4$). \\
\hline
\texttt{zonas\_urbanas.geojson} ($8$) & \texttt{MultiPolygon} & \texttt{code} (\texttt{urban\_quintero}), \texttt{name} (\texttt{Quintero}), \texttt{city}, \texttt{area\_km2} ($9{,}62$). \\
\hline
\end{tabularx}
\end{table}

\subsection{Carga Transaccional e Idempotencia}
\label{subsec:infra_carga}

La ingesta hacia PostgreSQL se realiza mediante \texttt{cargar\_nodos.py}, \texttt{cargar\_aristas.py} y \texttt{cargar\_zonas\_urbanas.py}. Este orden es obligatorio para respetar la integridad referencial de las llaves foráneas de \texttt{infra\_edge}. Cada cargador ejecuta una transacción atómica con limpieza preventiva (\texttt{DELETE}) antes de las inserciones parametrizadas por lotes, garantizando la \textbf{idempotencia total} del proceso.

% ============================== 7 ==============================
\section{Metadata de Soporte Operacional}
\label{sec:metadata}

\subsection{Obtención y Filtro Espacial}
\label{subsec:metadata_obtencion}

Todas las capas se filtraron a la caja envolvente de la bahía (longitud $[-71{,}56; -71{,}38]^\circ\text{W}$ y latitud $[-32{,}82; -32{,}69]^\circ\text{S}$). La extracción se automatizó en cuatro scripts modulares (ver Tabla~\ref{tab:metadata}).

\begin{table}[htbp]
\centering
\small
\caption{Fuentes de metadata integradas en el sistema.}
\label{tab:metadata}
\begin{tabularx}{\linewidth}{|l|X|X|}
\hline
\textbf{Script ETL} & \textbf{Fuente y Ventana de Datos} & \textbf{Alcance de la Extracción y Procesamiento} \\
\hline
\texttt{sinca\_calidad\_aire.py} & SINCA, MMA (API REST JSON) \cite{sinca}; registros horarios del 19-10-2026. & $10$ estaciones del litoral; extrae última concentración de $\text{SO}_2, \text{NO}_2, \text{CO}, \text{O}_3, \text{MP}_{10}$ y $\text{MP}_{2{,}5}$. Asocia al nodo si dista menos de $500\text{ m}$. \\
\hline
\texttt{srtm\_relieve.py} & SRTM $30\text{ m}$ vía OpenTopoData (API) \cite{opentopo}. & Perfil topográfico muestreado cada $100\text{ m}$ a lo largo de cada una de las $633$ aristas. \\
\hline
\texttt{ine\_manzanas.py} & INE, Censo 2017, vía geoservicio IDE SMA (ArcGIS REST) \cite{idesma}. & $703$ polígonos censales; extrae población y viviendas, calculando la densidad en $\text{hab/km}^2$. \\
\hline
\texttt{osm\_antenas.py} & OpenStreetMap vía Overpass API \cite{overpass}. & $25$ mástiles y torres celulares; genera búfer circular de cobertura de $3.000\text{ m}$. \\
\hline
\end{tabularx}
\end{table}

\noindent \textbf{Relevancia para el Vuelo y Proyección a la Fase 3:}
\begin{itemize}
    \item \textbf{Relieve SRTM:} Imprescindible para garantizar el cumplimiento de la cota $0$--$120\text{ m}$ AGL sobre orografía irregular (DAN 151). En la Fase 3, los perfiles de elevación (\texttt{ascent\_m}) alimentarán el cálculo de Consumo Energético Estimado ($EEE$).
    \item \textbf{Densidad Habitacional INE:} Cuantifica el riesgo a terceros en tierra conforme a SORA. Las aristas que sobrevuelan manzanas con densidades superiores a $2.500\text{ hab/km}^2$ recibirán un factor de penalización en la función de costo multiobjetivo.
    \item \textbf{Cobertura de Antenas OSM:} El enlace C2 depende de la proximidad a torres base. Los tramos a más de $3\text{ km}$ de una antena entran en sombras de telemetría con riesgo de pérdida de enlace (\textit{fly-away}).
    \item \textbf{Calidad del Aire SINCA:} Permite priorizar dinámicamente misiones de muestreo hacia nodos con episodios ambientales críticos.
\end{itemize}

\noindent \textbf{Limitaciones Declaradas:}
\begin{itemize}
    \item \textit{Desfase censal (INE):} Los datos validados y publicados con geometría vectorial a nivel de manzana corresponden al Censo 2017.
    \item \textit{Subregistro en OSM vs Subtel:} OpenStreetMap presenta un subregistro voluntario de mástiles. Aunque la base de Subtel (RNC) fue considerada, su visor web implementa reCAPTCHA v3 que impide la cosecha desatendida. No obstante, el subregistro de OSM induce un sesgo conservador (asume más sombras de las reales, favoreciendo trayectorias más precavidas).
\end{itemize}

\subsection{Estructura de los Datos GeoJSON}
\label{subsec:metadata_json}

Las propiedades estructuradas por elemento son:
\begin{itemize}
    \item \textbf{SINCA (\texttt{Point}):} \texttt{station\_key}, \texttt{station\_name}, \texttt{node\_id} y lista \texttt{measurements} (\texttt{pollutant}, \texttt{value}, \texttt{unit}, \texttt{status}, \texttt{observed\_at}).
    \item \textbf{SRTM (\texttt{LineString}):} \texttt{edge\_id}, \texttt{samples}, \texttt{terrain\_min\_m}, \texttt{terrain\_max\_m}, \texttt{terrain\_mean\_m}, \texttt{ascent\_m}, \texttt{descent\_m} y arreglo \texttt{profile\_m}.
    \item \textbf{INE Manzanas (\texttt{MultiPolygon}):} \texttt{manzent}, \texttt{commune}, \texttt{persons}, \texttt{dwellings}, \texttt{area\_m2} y \texttt{density\_hab\_km2}.
    \item \textbf{Antenas Celulares (\texttt{Polygon}):} \texttt{osm\_id}, \texttt{structure}, \texttt{operator}, \texttt{coverage\_radius\_m}, \texttt{lon} y \texttt{lat}.
\end{itemize}

\subsection{Carga Transaccional}
\label{subsec:metadata_carga}

La carga se realiza mediante cargadores en \texttt{metadata/}: \texttt{cargar\_sinca\_calidad\_aire.py} ($52$ filas en \texttt{meta\_air\_quality}), \texttt{cargar\_srtm\_relieve.py} ($633$ filas en \texttt{meta\_edge\_terrain}), \texttt{cargar\_ine\_manzanas.py} ($703$ filas en \texttt{meta\_census\_block}) y \texttt{cargar\_osm\_antenas.py} ($25$ filas en \texttt{meta\_telecom\_antenna}).

% ============================== 8 ==============================
\section{Amenazas Operacionales}
\label{sec:amenazas}

\subsection{Obtención y Modelado Espacial}
\label{subsec:amenazas_obtencion}

Para modelar las contingencias ambientales dinámicas, se desarrollaron extractores automatizados para cuatro amenazas críticas (ver Tabla~\ref{tab:amenazas}).

\begin{table}[htbp]
\centering
\small
\caption{Fuentes de amenazas y parámetros operacionales en la ejecución de referencia.}
\label{tab:amenazas}
\begin{tabularx}{\linewidth}{|l|X|X|c|}
\hline
\textbf{Script ETL} & \textbf{Fuente y Ventana Temporal} & \textbf{Modelo Geométrico y Umbral} & \textbf{Eventos (Activos)} \\
\hline
\texttt{firms\_incendios.py} & NASA FIRMS \cite{firms}, NRT de $7$ días, sensores VIIRS ($375\text{ m}$) y MODIS ($1\text{ km}$). & Círculo de $2\text{ km}$ ($32$ vértices) por foco con confianza nominal o alta. & $1$ ($1$) \\
\hline
\texttt{csn\_sismos.py} & EMSC (FDSN) \cite{emsc}, catálogo CSN de $30$ días, $M \ge 3{,}0$. & Círculo de radio $R = 10^{0{,}5M-1{,}8}\text{ km}$; activo si $M \ge 5{,}0$. & $98$ ($1$) \\
\hline
\texttt{openmeteo\_viento.py} & Open-Meteo \cite{openmeteo}, condiciones horarias en superficie y $120\text{ m}$ AGL. & Grilla $4 \times 4$ ($\approx 4{,}2 \times 3{,}6\text{ km}$/celda); activo si viento o ráfaga $\ge 14\text{ m/s}$. & $16$ ($0$) \\
\hline
\texttt{metno\_lluvia.py} & MET Norway \cite{metno}, pronóstico horario de precipitación inmediata. & Grilla $4 \times 4$ ($\approx 4{,}2 \times 3{,}6\text{ km}$/celda); activo si lluvia $\ge 2{,}0\text{ mm/h}$. & $16$ ($0$) \\
\hline
\end{tabularx}
\end{table}

\noindent \textbf{Justificación Operacional de las Amenazas:}
\begin{itemize}
    \item \textbf{Incendios forestales e industriales:} La ventana de $7$ días previene vacíos por nubosidad costera. El amortiguamiento de $2\text{ km}$ evita turbulencias convectivas térmicas y asfixia de sensores. En la ejecución reportada, la única anomalía se situó a más de $30\text{ km}$ de la bahía sin tocar la red.
    \item \textbf{Sismicidad regional:} No afecta a la nave en vuelo, sino que compromete la infraestructura de apoyo en tierra (pista de despegue y zonas de aterrizaje de emergencia para RTH). La fórmula $R = 10^{0{,}5M-1{,}8}\text{ km}$ es una heurística del equipo. El único sismo de magnitud $M \ge 5{,}0$ ocurrió a $144\text{ km}$ mar adentro sin tocar la red.
    \item \textbf{Viento en altura:} El umbral de $14\text{ m/s}$ ($50{,}4\text{ km/h}$) deriva del límite de control de actitud del UAV. En la corrida analizada, la ráfaga máxima fue de $5{,}5\text{ m/s}$, manteniendo las $16$ celdas inactivas.
    \item \textbf{Precipitación:} El umbral de $2\text{ mm/h}$ protege contra pérdida de estanqueidad (estándar IP43/IP54). La lluvia máxima prevista fue de $0{,}6\text{ mm/h}$ (celdas inactivas).
\end{itemize}

\noindent \textbf{Auditoría de afectación en la Fase 2:} En la corrida reportada, \textbf{ninguna amenaza activa intersectó físicamente la red de aristas}. Por ende, el riesgo demostrado por la ruta de Dijkstra en la Sección~\ref{sec:resultados} deriva de factores estáticos: densidad habitacional y sombras de telecomunicaciones.

\subsection{Estructura Común de los GeoJSON de Amenazas}
\label{subsec:json_amenazas}

Los cuatro archivos de amenazas comparten un formato base homogéneo (ver Tabla~\ref{tab:json_amenazas}). La evaluación del umbral se efectúa durante el ETL, fijando la bandera booleana \texttt{exceeds} (\texttt{true} indica zona activa).

\begin{table}[htbp]
\centering
\small
\caption{Estructura común de atributos en los archivos GeoJSON de amenazas.}
\label{tab:json_amenazas}
\begin{tabularx}{\linewidth}{|l|l|X|}
\hline
\textbf{Propiedad} & \textbf{Tipo} & \textbf{Significado y Rol Operacional} \\
\hline
\texttt{geometry} & \texttt{Polygon} & Área de exclusión (círculo discretizado a $32$ vértices o celda de grilla $4 \times 4$). \\
\hline
\texttt{external\_id} & Texto & Identificador único en el catálogo de origen. \\
\hline
\texttt{event\_type} & Texto & Clasificación (\texttt{incendio}, \texttt{sismo}, \texttt{viento} o \texttt{lluvia}). \\
\hline
\texttt{value}, \texttt{unit} & Numérico, Texto & Magnitud física (FRP en $\text{MW}$, magnitud Richter, $\text{m/s}$ o $\text{mm/h}$). \\
\hline
\texttt{threshold} & Numérico & Umbral crítico que define la condición de riesgo de la aeronave. \\
\hline
\texttt{exceeds} & Booleano & \texttt{true} si supera el umbral (zona de riesgo operacional activa). \\
\hline
\texttt{observed\_at} & ISO 8601 & Fecha y hora UTC del registro o previsión meteorológica. \\
\hline
\texttt{lon}, \texttt{lat} & Numérico & Coordenadas geográficas del foco o centroide de celda. \\
\hline
\end{tabularx}
\end{table}

\noindent Los atributos propios de cada sensor (\texttt{confidence} en FIRMS, \texttt{depth\_km} en sismos, o el viento a $120\text{ m}$ en Open-Meteo) se almacenan en la columna \texttt{properties JSONB} de PostgreSQL.

\subsection{Carga Transaccional en Base de Datos}
\label{subsec:carga_amenazas}

La inserción en la tabla \texttt{threat\_event} se ejecuta mediante \texttt{cargar\_firms\_incendios.py}, \texttt{cargar\_csn\_sismos.py}, \texttt{cargar\_openmeteo\_viento.py} y \texttt{cargar\_metno\_lluvia.py}. En total se cargan exactamente \textbf{$131$ registros} ($1$ incendio, $98$ sismos, $16$ celdas de viento y $16$ celdas de lluvia). La tabla no define llave foránea hacia la red: la afectación espacial se calcula dinámicamente mediante \texttt{ST\_Intersects(infra\_edge.geom, threat\_event.geom)} condicionado a \texttt{threat\_event.exceeds = true}.

% ============================== 9 ==============================
\section{Algoritmo de Ruteo Base: \texttt{pgr\_dijkstra}}
\label{sec:ruteo_dijkstra}

Conforme a la instrucción oficial de la Fase 2, la ruta de referencia se genera directamente en PostgreSQL utilizando la función \texttt{pgr\_dijkstra} de pgRouting sobre el costo métrico puro (\texttt{length\_m}), sin considerar metadata ni amenazas.

El script \texttt{ruteo/ruta\_dijkstra.py} ejecuta la siguiente consulta SQL parametrizada desde la base (\texttt{base\_scer}) hacia cada una de las $8$ estaciones SINCA:

\begin{lstlisting}[language=SQL,caption={Consulta SQL ejecutada en pgRouting para generar la ruta base.}]
SELECT count(*) FILTER (WHERE d.edge <> -1)                AS tramos,
       COALESCE(SUM(e.length_m), 0)                        AS longitud_m,
       MAX(d.agg_cost)                                     AS costo,
       COUNT(DISTINCT d.node)                              AS nodos,
       ST_AsGeoJSON(ST_MakeLine(n.geom ORDER BY d.seq))    AS linea
FROM pgr_dijkstra(
       'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
       (SELECT id FROM infra_node WHERE code = 'base_scer'),
       destino_id,
       directed := false) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
JOIN infra_node n ON n.id = d.node;
\end{lstlisting}

\noindent \textbf{Justificación de Parámetros:} El parámetro \texttt{directed := false} y los costos simétricos (\texttt{cost} = \texttt{reverse\_cost} = \texttt{length\_m}) modelan los corredores aéreos como bidireccionales. La geometría calculada se exporta al archivo \texttt{sitio\_web/data/ruta\_dijkstra.geojson} para su despliegue cartográfico en Leaflet. Esta ruta representa el peor caso posible, sirviendo como benchmark cuantitativo contra el cual se evaluará el ruteo adaptativo en la Fase 3.

% ============================== 10 ==============================
\section{Plataforma Web Interactiva}
\label{sec:plataforma_web}

La visualización y auditoría geoespacial se implementó como una aplicación web desacoplada en \textbf{Leaflet (v1.9.4)} con HTML5 y CSS3 en modo oscuro técnico, sirviendo directamente los archivos GeoJSON generados en el pipeline.

\subsection{Despliegue y Acceso Local}
\label{subsec:web_despliegue}

La aplicación se sirve mediante el microservicio \texttt{web} orquestado en Docker Compose:
\begin{lstlisting}[language=bash]
# Despliegue del contenedor web
docker compose up -d web

# URL de acceso local en el navegador
http://localhost:8000/sitio_web/
\end{lstlisting}

\subsection{Organización Modular de la Interfaz}
\label{subsec:web_modulos}

La interfaz implementa una barra de navegación con seis módulos especializados:
\begin{enumerate}
    \item \textbf{Simulador (Principal):} Mapa interactivo con selección de misiones, panel colapsable de capas y ventana modal flotante (arrastrable) con desglose de métricas.
    \item \textbf{Grafo:} Visualización topológica pura de los $237$ nodos y $633$ aristas conexas.
    \item \textbf{Infraestructura:} Desglose de nodos clasificados por las $13$ categorías temáticas, aristas y los $8$ polígonos urbanos.
    \item \textbf{Metadata:} Diagnóstico de las $4$ capas de soporte (calidad del aire SINCA, relieve SRTM, manzanas censales INE y antenas OSM).
    \item \textbf{Amenazas:} Monitoreo dinámico de focos FIRMS, sismicidad CSN y grillas de viento y lluvia.
    \item \textbf{Documentación:} Catálogo de metadatos y trazabilidad de fuentes.
\end{enumerate}

\subsection{Catálogo de Capas Cartográficas}
\label{subsec:web_capas}

El visor soporta mapas base \textit{OpenStreetMap} y \textit{Esri Satelital}, integrando capas vectoriales con control de encendido independiente (ver Tabla~\ref{tab:capas_web}):

\begin{table}[htbp]
\centering
\small
\caption{Capas vectoriales desplegadas en la plataforma web Leaflet.}
\label{tab:capas_web}
\begin{tabularx}{\linewidth}{|l|l|X|}
\hline
\textbf{Grupo} & \textbf{Capa Geoespacial} & \textbf{Estilo Visual y Simbología en el Mapa} \\
\hline
\textbf{Base} & Topología de Red & $237$ marcadores circulares clasificados por color ($13$ categorías); aristas grises de corredores aéreos bidireccionales. \\
\cline{2-3}
 & Zonas Urbanas & $8$ polígonos translúcidos violeta con borde continuo. \\
\hline
\textbf{Metadata} & Calidad del Aire (SINCA) & Marcadores azules con popups interactivos de concentración ($\text{SO}_2, \text{MP}_{10}, \text{MP}_{2.5}$) y estado ambiental. \\
\cline{2-3}
 & Relieve SRTM & Perfil interactivo que reporta elevación mínima, media, máxima y pendiente al hacer clic en cada arista. \\
\cline{2-3}
 & Manzanas Censales (INE) & $703$ polígonos coloreados por gradiente de densidad poblacional ($> 2.500\text{ hab/km}^2$). \\
\cline{2-3}
 & Antenas Celulares (OSM) & Mástiles con círculos concéntricos de cobertura radioeléctrica de $3.000\text{ m}$ (verde translúcido). \\
\hline
\textbf{Amenazas} & Incendios (NASA FIRMS) & Focos térmicos con círculo de exclusión de $2.000\text{ m}$ (rojo/ámbar de advertencia). \\
\cline{2-3}
 & Sismicidad (CSN/EMSC) & Epicentros con radios de afectación en tierra según magnitud. \\
\cline{2-3}
 & Viento (Open-Meteo) & Grilla $4 \times 4$; celdas que superan $14\text{ m/s}$ se iluminan como condición \textit{No-Go}. \\
\cline{2-3}
 & Precipitación (MET Norway) & Grilla $4 \times 4$; celdas con lluvia $\ge 2\text{ mm/h}$ destacan en azul cian como zona activa. \\
\hline
\textbf{Ruteo Base} & \texttt{pgr\_dijkstra} & Corredor continuo resaltado en magenta grueso (\textit{stroke-width: 4px}), rotulado como \textbf{Línea Base del Peor Caso}. \\
\hline
\end{tabularx}
\end{table}

\subsection{Interacción y Visualización de la Línea Base}
\label{subsec:web_interaccion}

El usuario puede seleccionar el nodo origen (\texttt{base\_scer}) y cualquiera de los destinos disponibles mediante una lista desplegable o haciendo clic directo sobre el marcador en el mapa. Al presionar \textit{Ejecutar Misión}:
\begin{enumerate}
    \item La plataforma renderiza la ruta calculada por \texttt{pgr\_dijkstra} en color magenta sobre la red.
    \item Se abre una ventana modal interactiva con el resumen de métricas: longitud acumulada en metros y kilómetros, tiempo de vuelo a $15\text{ m/s}$ ($54\text{ km/h}$), perfil de elevación y auditoría de exposición a áreas pobladas y sombras de antena.
\end{enumerate}

\begin{figure}[H]
\centering
\IfFileExists{img_plataforma.PNG}{\includegraphics[width=0.95\textwidth]{img_plataforma.PNG}}{\imagen{0.95\textwidth}{img_plataforma.PNG}}
\caption{Visualizador cartográfico Leaflet desplegando la ruta base de mínima distancia (\texttt{pgr\_dijkstra}) hacia Puchuncaví, rotulada explícitamente como el peor caso de referencia.}
\label{fig:zoom}
\end{figure}

% ============================== 11 ==============================
\section{Resultados y Análisis del Ruteo Base}
\label{sec:resultados}

Para verificar la conectividad global y la línea base de ruteo, se ejecutaron simulaciones de navegación desde el Aeródromo de Quintero (\texttt{base\_scer}, cota $28\text{ msnm}$) hacia las $8$ estaciones SINCA y hacia nodos críticos de salud, industria, educación y comercio.

Las métricas analizadas corresponden a la longitud geodésica ($L$), número de aristas o saltos topológicos ($h$), tiempo de vuelo ($T_v$) a velocidad de crucero nominal ($15\text{ m/s} = 54\text{ km/h}$), desnivel orográfico ($\Delta z$) y exposición a riesgos de la Fase 2.

\subsection{Resultados Numéricos de la Simulación}
\label{subsec:tabla_resultados}

La Tabla~\ref{tab:resultados_sinca} presenta las métricas operacionales hacia las $8$ estaciones de monitoreo SINCA:

\begin{table}[!ht]
\centering
\small
\caption{Métricas del ruteo base (\texttt{pgr\_dijkstra}) hacia las $8$ estaciones SINCA (costo = longitud).}
\label{tab:resultados_sinca}
\resizebox{\linewidth}{!}{%
\begin{tabular}{|l|c|c|c|c|p{5.5cm}|}
\hline
\textbf{Estación SINCA} & \textbf{Distancia} & \textbf{Saltos} & \textbf{$T_v$ est.} & \textbf{$\Delta z$} & \textbf{Exposición a Riesgo (Línea Base)} \\
\hline
Centro Quintero & $1{,}69\text{ km}$ & $6$ & $1{,}9\text{ min}$ & $-6{,}0\text{ m}$ & Alta densidad urbana ($>2.500\text{ hab/km}^2$) \\
\hline
Loncura & $2{,}35\text{ km}$ & $4$ & $2{,}6\text{ min}$ & $-13{,}0\text{ m}$ & Despejado (corredor costero) \\
\hline
Quintero & $2{,}35\text{ km}$ & $9$ & $2{,}6\text{ min}$ & $-10{,}0\text{ m}$ & Alta densidad urbana ($>2.500\text{ hab/km}^2$) \\
\hline
Sur Puchuncaví & $3{,}74\text{ km}$ & $5$ & $4{,}2\text{ min}$ & $-3{,}0\text{ m}$ & Despejado (enlace intercomunal) \\
\hline
La Greda & $6{,}71\text{ km}$ & $11$ & $7{,}5\text{ min}$ & $+7{,}0\text{ m}$ & Densidad urbana y sombra C2 ($>3\text{ km}$) \\
\hline
Ventanas & $7{,}80\text{ km}$ & $14$ & $8{,}7\text{ min}$ & $-16{,}0\text{ m}$ & Densidad urbana y sombra C2 ($>3\text{ km}$) \\
\hline
Campiche & $9{,}53\text{ km}$ & $16$ & $10{,}6\text{ min}$ & $+2{,}0\text{ m}$ & Densidad urbana y sombra C2 ($>3\text{ km}$) \\
\hline
Puchuncaví & $14{,}41\text{ km}$ & $22$ & $16{,}0\text{ min}$ & $+67{,}0\text{ m}$ & Desnivel pronunciado y sombra C2 \\
\hline
\end{tabular}%
}
\end{table}

Asimismo, la Tabla~\ref{tab:resultados_otros} resume los resultados obtenidos hacia receptores críticos de la bahía, validando la navegabilidad sobre las diversas categorías del grafo:

\begin{table}[!ht]
\centering
\small
\caption{Métricas de validación en receptores críticos de la bahía.}
\label{tab:resultados_otros}
\resizebox{\linewidth}{!}{%
\begin{tabular}{|l|l|c|c|c|p{5.2cm}|}
\hline
\textbf{Nodo Destino} & \textbf{Categoría} & \textbf{Distancia} & \textbf{Saltos} & \textbf{$T_v$} & \textbf{Observación Operacional} \\
\hline
Hospital Adriana Cousiño & Salud & $1{,}43\text{ km}$ & $5$ & $1{,}6\text{ min}$ & Sobrevuelo centro urbano de Quintero \\
\hline
Planta Asfaltos Quintero & Industria & $2{,}33\text{ km}$ & $4$ & $2{,}6\text{ min}$ & Proximidad a istmo y zona industrial \\
\hline
Terminal GNL Quintero & Industria & $2{,}74\text{ km}$ & $5$ & $3{,}0\text{ min}$ & Corredor costero de baja cota ($-23\text{ m}$) \\
\hline
Fundición Codelco Ventanas & Industria & $5{,}28\text{ km}$ & $9$ & $5{,}9\text{ min}$ & Complejo industrial de Ventanas \\
\hline
Termoeléctrica Ventanas (AES) & Industria & $7{,}48\text{ km}$ & $13$ & $8{,}3\text{ min}$ & Zona de efluentes térmicos \\
\hline
CESFAM Las Ventanas & Salud & $8{,}05\text{ km}$ & $15$ & $8{,}9\text{ min}$ & Densidad urbana y sombra C2 \\
\hline
Colegio Don Orione (Quintero) & Educación & $1{,}86\text{ km}$ & $7$ & $2{,}1\text{ min}$ & Zona residencial escolar de Quintero \\
\hline
Escuela La Chocota & Educación & $9{,}77\text{ km}$ & $19$ & $10{,}9\text{ min}$ & Corredor rural interurbano \\
\hline
Colegio San Hernaldo & Educación & $13{,}67\text{ km}$ & $20$ & $15{,}2\text{ min}$ & Ascenso orográfico hacia Puchuncaví \\
\hline
Unimarc Quintero Centro & Comercial & $1{,}25\text{ km}$ & $5$ & $1{,}4\text{ min}$ & Alta concurrencia de personas en tierra \\
\hline
\end{tabular}%
}
\end{table}

\subsection{Discusión y Hallazgos Principales}
\label{subsec:discusion_resultados}

\begin{enumerate}
    \item \textbf{Accesibilidad y Autonomía de Vuelo:} Todas las rutas de ida hacia Quintero y Ventanas se sitúan entre $1{,}25\text{ km}$ y $7{,}80\text{ km}$ ($<9\text{ min}$ de vuelo). Con una autonomía nominal de $26{,}4\text{ km}$ ($55\text{ min}$), estas misiones permiten muestreo y retorno con reserva segura. Sin embargo, hacia Puchuncaví ($14{,}41\text{ km}$), el viaje completo de ida y retorno ($28{,}82\text{ km}$) supera la batería nominal, evidenciando la necesidad de planificar recargas intermedias en la Fase 3.
    \item \textbf{Incidencia del Relieve Orográfico ($\Delta z$):} Mientras que las trayectorias costeras son planas o descendentes ($\Delta z \in [-23{,}0; -3{,}0]\text{ m}$), hacia el valle de Puchuncaví el terreno asciende hasta $+67{,}0\text{ msnm}$. Esto valida la integración de SRTM para ajustar dinámicamente la cota barométrica y no vulnerar el techo de $120\text{ m}$ AGL de la DAN 151.
    \item \textbf{Evidencia Cuantitativa del Peor Caso:} Al optimizar únicamente la distancia física métrica, Dijkstra traza trayectorias que vulneran principios de seguridad operacional: atraviesa manzanas con más de $2.500\text{ hab/km}^2$ en Quintero y cruza extensas sombras celulares C2 ($>3\text{ km}$) hacia Ventanas y Puchuncaví, demostrando la necesidad imperiosa de incorporar funciones de costo con riesgo en la Fase 3.
\end{enumerate}

% ============================== 12 ==============================
\section{Conclusiones y Proyecciones}
\label{sec:conclusiones}

\subsection{Conclusiones y Respuestas a las Preguntas de Diseño}
\label{subsec:conclusiones_fase2}

En el marco de la Fase 2, se implementó y validó una infraestructura geoespacial reproducible y una línea base de ruteo para operaciones UAV en la Bahía de Quintero y Puchuncaví, respondiendo formalmente a las tres preguntas de diseño:
\begin{enumerate}
    \item \textbf{Respuesta a P1 (Integración automatizada y reproducibilidad):} Se comprobó la viabilidad de integrar desatendidamente $8$ fuentes heterogéneas. La contenerización en Docker con una única dependencia externa (\texttt{psycopg==3.2.13}) permite reproducir el entorno desde cero o mediante la bandera \texttt{--sin-descarga}. La tabla \texttt{data\_source} garantiza la trazabilidad inmutable de cada ingesta.
    \item \textbf{Respuesta a P2 (Conexidad y navegabilidad territorial):} La construcción con $K=4$ vecinos y $2$ aristas puente de Union-Find garantizó un grafo $100\,\%$ conexo ($1$ sola componente) de $237$ nodos y $633$ aristas, haciendo físicamente accesible cualquiera de las $8$ estaciones SINCA desde la base aeroportuaria.
    \item \textbf{Respuesta a P3 (Exposición de la línea base):} La ruta calculada con \texttt{pgr\_dijkstra} confirmó cuantitativamente su condición de peor caso: minimiza la distancia pero expone la nave a áreas de alta densidad poblacional y sombras de telemetría C2.
\end{enumerate}

\subsection{Limitaciones Identificadas}
\label{subsec:limitaciones_fase2}

\begin{itemize}
    \item \textbf{Autonomía energética en trayectos largos:} El viaje de ida y vuelta a Puchuncaví ($28{,}82\text{ km}$) excede los $26{,}4\text{ km}$ de autonomía nominal del UAV, exigiendo hubs de recarga en el norte.
    \item \textbf{Cuello de botella en el istmo de Quintero:} Los corredores hacia el continente convergen en Planta Asfaltos; un incidente severo en ese istmo particionaría el grafo terrestre.
    \item \textbf{Desfase del Censo INE y subregistro en OSM:} El Censo 2017 puede subestimar áreas de reciente expansión, y el subregistro voluntario de OSM induce un sesgo conservador en la cobertura C2.
\end{itemize}

\subsection{Proyección hacia la Fase 3}
\label{subsec:proyeccion_fase3}

Sobre esta base validada se implementará en la siguiente etapa:
\begin{enumerate}
    \item \textbf{Función de costo multiobjetivo con riesgo ($W(e)$):} Ponderación del consumo energético orográfico (SRTM), densidad poblacional (INE) y alertas de viento y lluvia.
    \item \textbf{Rutas alternativas disimilares ($k \ge 2$):} Generación de caminos espacialmente diversos para contingencias.
    \item \textbf{Protocolo reactivo RTH:} Replanteamiento dinámico del retorno aprovechando el sotavento de los cerros costeros con garantía de $\ge 15\,\%$ de batería de reserva al aterrizar.
\end{enumerate}

\newpage

% ============================== REFERENCIAS ==============================
\begin{thebibliography}{99}
\addcontentsline{toc}{section}{Referencias}

\bibitem{estaciones} Ministerio del Medio Ambiente. (2019). \textit{Decreto Supremo N.º 105: Establece Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví}. Diario Oficial de la República de Chile, 30 de marzo de 2019. Biblioteca del Congreso Nacional de Chile. \url{https://www.bcn.cl/leychile/navegar?idNorma=1130344}

\bibitem{altura} Ministerio del Medio Ambiente, ``Plan de Prevención y Descontaminación Atmosférica para las comunas de Concón, Quintero y Puchuncaví,'' Memoria Técnica y Modelación de Dispersión, Santiago, Chile, 2019.

\bibitem{sinca} Ministerio del Medio Ambiente, ``Sistema de Información Nacional de Calidad del Aire (SINCA).'' [En línea]. Disponible en: \url{https://sinca.mma.gob.cl}. Consultado el 20 de octubre de 2026.

\bibitem{kosior} M. Kosior, P. Przystałka y W. Panfil, ``Adaptive path planning for UAV-based pollution sampling,'' \textit{Applied Sciences}, vol. 14, n.º 24, art. 12065, 2024. doi: 10.3390/app142412065.

\bibitem{akgun} V. Akgün, E. Erkut y R. Batta, ``On finding dissimilar paths,'' \textit{European Journal of Operational Research}, vol. 121, n.º 2, pp. 232--246, 2000.

\bibitem{dijkstra} E. W. Dijkstra, ``A note on two problems in connexion with graphs,'' \textit{Numerische Mathematik}, vol. 1, pp. 269--271, 1959.

\bibitem{yen} J. Y. Yen, ``Finding the $k$ shortest loopless paths in a network,'' \textit{Management Science}, vol. 17, n.º 11, pp. 712--716, 1971.

\bibitem{suurballe} J. W. Suurballe, ``Disjoint paths in a network,'' \textit{Networks}, vol. 4, n.º 2, pp. 125--145, 1974.

\bibitem{bhandari} R. Bhandari, \textit{Survivable Networks: Algorithms for Diverse Routing}. Boston: Kluwer Academic Publishers, 1999.

\bibitem{sora} Joint Authorities for Rulemaking of Unmanned Systems (JARUS), \textit{JARUS guidelines on Specific Operations Risk Assessment (SORA)}, ed. 2.5, 2024.

\bibitem{petritoli} E. Petritoli, F. Leccese y L. Ciani, ``Reliability and maintenance analysis of unmanned aerial vehicles,'' \textit{Sensors}, vol. 18, n.º 9, art. 3171, 2018. doi: 10.3390/s18093171.

\bibitem{schroeder} W. Schroeder, P. Oliva, L. Giglio e I. A. Csiszar, ``The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment,'' \textit{Remote Sensing of Environment}, vol. 143, pp. 85--96, 2014.

\bibitem{dan151} Dirección General de Aeronáutica Civil, \textit{DAN 151: Operaciones de aeronaves pilotadas a distancia (RPAS) en asuntos de interés público, que se efectúen sobre áreas pobladas}, ed. 3, mayo de 2024. [En línea]. Disponible en: \url{https://www.dgac.gob.cl/wp-content/uploads/2024/05/DAN-151-ED3-27MAY2024.pdf}. Consultado el 20 de octubre de 2026.

\bibitem{dji} DJI, ``Matrice 350 RTK: especificaciones.'' [En línea]. Disponible en: \url{https://enterprise.dji.com/matrice-350-rtk/specs}. Consultado el 20 de octubre de 2026.

\bibitem{opentopo} OpenTopoData, ``SRTM 30 m.'' [En línea]. Disponible en: \url{https://www.opentopodata.org}. Consultado el 20 de octubre de 2026.

\bibitem{idesma} Superintendencia del Medio Ambiente, ``Infraestructura de Datos Geoespaciales: capa de manzanas censales (INE, Censo 2017).'' [En línea]. Disponible en: \url{https://ideserver.sma.gob.cl}. Consultado el 20 de octubre de 2026.

\bibitem{overpass} OpenStreetMap, ``Overpass API.'' [En línea]. Disponible en: \url{https://overpass-api.de}. Consultado el 20 de octubre de 2026.

\bibitem{firms} NASA, ``Fire Information for Resource Management System (FIRMS).'' [En línea]. Disponible en: \url{https://firms.modaps.eosdis.nasa.gov}. Consultado el 20 de octubre de 2026.

\bibitem{emsc} European-Mediterranean Seismological Centre (EMSC), ``FDSN Event Service.'' [En línea]. Disponible en: \url{https://www.seismicportal.eu}. Consultado el 20 de octubre de 2026.

\bibitem{openmeteo} Open-Meteo, ``Forecast API.'' [En línea]. Disponible en: \url{https://open-meteo.com}. Consultado el 20 de octubre de 2026.

\bibitem{metno} Norwegian Meteorological Institute (MET Norway), ``Locationforecast 2.0.'' [En línea]. Disponible en: \url{https://api.met.no}. Consultado el 20 de octubre de 2026.

\end{thebibliography}

\end{document}
