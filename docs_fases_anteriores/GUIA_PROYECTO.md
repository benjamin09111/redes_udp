# Guía del proyecto: cómo funciona todo (fase 2 completa)

Esta guía explica el proyecto con palabras simples: qué problema resolvemos, qué piezas hay en el
repositorio, cómo fluyen los datos, cómo se ejecuta todo y qué falta.

---

## 1. La idea en una frase

Queremos que un **dron que mide contaminación** en Quintero, Ventanas y Puchuncaví pueda elegir
**rutas seguras** entre puntos de interés, y que pueda **cambiar de ruta** cuando algo falla
(incendio, viento fuerte, lluvia, sismo, falta de señal).

Para eso modelamos la zona como una **red (grafo)**:

- **Nodos** = lugares (la base del dron, estaciones de monitoreo, fuentes industriales, hospitales, colegios, etc.).
- **Aristas** = "calles aéreas" que unen un nodo con otro.
- **Metadata** = información extra que hace que una calle aérea sea más o menos conveniente
  (contaminación, relieve, población debajo, señal celular).
- **Amenazas** = eventos que pueden **bloquear** nodos o aristas (incendios, sismos, viento, lluvia).

---

## 2. Las tres fases del curso

| Fase | Qué se pide | Estado |
|---|---|---|
| **Fase 1** (informe) | Problema, hipótesis, objetivos, fuentes de datos | Entregada |
| **Fase 2** (ETL + BD + Ruteo Resiliente + Sitio) | Descargar, transformar, cargar en BD, ruteo base pgr_dijkstra y ruteo resiliente multiobjetivo con visor Leaflet interactivo | **Completa** (ver sección 13) |
| **Fase 3** (Validación avanzada) | Simulación dinámica a bordo y pruebas de campo | Próxima fase |

---

## 3. Qué es ETL (la base de la fase 2)

ETL significa **Extract, Transform, Load** (extraer, transformar, cargar):

1. **Extract (extraer):** pedir los datos a una API o base de datos de internet.
   *Ejemplo: pedirle al SINCA las mediciones de contaminación de ahora.*
2. **Transform (transformar):** limpiar y ordenar esos datos en un formato común.
   *Ejemplo: el SINCA entrega `&micro;g&#8725;m<sup>3</sup>N` y lo convertimos a `µg/m3N`; filtramos solo las estaciones de nuestra zona.*
3. **Load (cargar):** guardar los datos limpios en la base de datos.
   *Ejemplo: insertar cada medición como una fila en la tabla `meta_air_quality`.*

En el proyecto, cada script de `infraestructura/`, `metadata/` y `amenazas/` hace la **E** y la **T**
y deja un `.geojson`. Cada `cargar_*.py` hace la **L**.

---

## 4. El flujo completo de los datos

```text
   INTERNET (APIs y bases de datos)
   ┌──────────────┬───────────────────────┬──────────────────────┐
   │ Dataset      │ SINCA, SRTM, INE, OSM │ FIRMS, EMSC, Open-   │
   │ fase 1       │                       │ Meteo, MET Norway    │
   └──────┬───────┴───────────┬───────────┴──────────┬───────────┘
          │                   │                      │
   EXTRAER + TRANSFORMAR  (un script por fuente, en Docker)
          │                   │                      │
          ▼                   ▼                      ▼
   infraestructura/*.geojson  metadata/*.geojson   amenazas/*.geojson
          │                   │                      │
          └───────────────────┼──────────────────────┘
                              │  CARGAR (un cargar_*.py por cada .geojson)
                              ▼
            PostgreSQL 16 + PostGIS + pgRouting (bd/schema.sql)
                              │
                              │  pgr_dijkstra (costo = longitud)
                              ▼
            sitio_web/data/ruta_dijkstra.geojson
                              │
                              ▼
            Sitio Leaflet (sitio_web/): red, metadata, amenazas y ruta
```

**Orden obligatorio:** primero la infraestructura, porque dos scripts de metadata la necesitan:

- `srtm_relieve.py` lee las aristas para medir el terreno bajo cada una.
- `sinca_calidad_aire.py` lee los nodos para saber a qué nodo corresponde cada estación.

`main.py` ejecuta todo en ese orden (sección 11).

---

## 5. Qué hay en cada carpeta

```text
redes_udp/
├── main.py                  ← Ejecuta todo el pipeline (descarga, BD, ruta, sitio)
├── Dockerfile               ← Imagen Python fijada (ETL, cargadores, ruteo y servidor web)
├── docker-compose.yml       ← Servicios: base de datos, ETL y sitio web
├── requirements.txt         ← Dependencia fijada: psycopg 3.2.13
├── bd/                      ← Punto 0: base de datos
│   ├── schema.sql           (crea todas las tablas desde cero)
│   ├── bd_diagrama.png      (dibujo de las tablas y sus relaciones)
│   ├── bd_diagrama.puml     (código con el que se genera el dibujo)
│   ├── conexion.py          (conexión a la BD y funciones comunes de carga)
│   └── GUIA_BD.md           (explicación del diagrama)
├── infraestructura/         ← Punto 1: la red (nodos, aristas, zonas urbanas)
│   ├── extraer_infraestructura.py
│   ├── cargar_nodos.py, cargar_aristas.py, cargar_zonas_urbanas.py
│   └── nodos.* / aristas.* / zonas_urbanas.*  (.geojson, .md)
├── metadata/                ← Punto 2: 4 fuentes de información extra
│   ├── sinca_calidad_aire.py, srtm_relieve.py, ine_manzanas.py, osm_antenas.py
│   ├── cargar_*.py          (un cargador por cada .geojson)
│   └── *.geojson, *.md
├── amenazas/                ← Punto 3: 4 fuentes de eventos que pueden bloquear la red
│   ├── firms_incendios.py, csn_sismos.py, openmeteo_viento.py, metno_lluvia.py
│   ├── cargar_*.py
│   └── *.geojson, *.md
├── ruteo/
│   └── ruta_dijkstra.py     ← Punto 8: ruta base → SINCA con pgr_dijkstra
├── sitio_web/               ← Punto 7: mapa Leaflet
│   ├── index.html, app.js, estilo.css
│   └── data/ruta_dijkstra.geojson
├── tests/
│   └── verificar.py         ← Comprueba la pauta, los GeoJSON y la BD
├── public/data/             ← Datos de la fase 1 (nodos y zonas curados a mano)
├── scripts/                 ← Scripts de la fase 1 que cosecharon los nodos desde OSM
├── src/ + index.html        ← Visor web de la fase 1 (Leaflet)
└── AGENTS.md                ← Reglas del proyecto para agentes de IA y desarrolladores
```

En `infraestructura/`, `metadata/` y `amenazas/` cada fuente tiene **cuatro archivos**:

| Archivo | Para qué sirve | Punto de la pauta |
|---|---|---|
| `algo.py` | Descarga y transforma los datos a un `.geojson` | 1, 2 o 3 |
| `algo.geojson` | Resultado: los datos limpios | 1, 2 o 3 |
| `algo.md` | Explica qué significa cada campo | 4 |
| `cargar_algo.py` | Carga el `.geojson` en su tabla de la BD | 6 |

---

## 6. Formato de los archivos: GeoJSON

Todos los resultados son **GeoJSON**, un JSON estándar para datos con ubicación. QGIS lo abre directo,
Leaflet lo dibuja directo y PostGIS lo lee directo.

```json
{
  "type": "FeatureCollection",
  "etl": { "fuente": "...", "generado": "2026-10-18T21:34:13+00:00", "total": 10 },
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [-71.4808, -32.7418] },
      "properties": { "station_name": "Ventanas", "...": "..." }
    }
  ]
}
```

- `features`: la lista de elementos (un nodo, una arista, una manzana, un incendio...).
- `geometry`: **dónde** está. Puede ser `Point` (punto), `LineString` (línea), `Polygon` o `MultiPolygon` (área).
- `properties`: **qué es** (nombre, valores, etc.).
- `etl`: bloque que agregamos para saber de dónde salió el archivo y cuándo se generó.

Las coordenadas van siempre como `[longitud, latitud]` (WGS84, EPSG:4326). Los polígonos siguen la
regla de RFC 7946: anillo exterior antihorario y huecos horarios. `tests/verificar.py` lo comprueba.

---

## 7. Punto 1: infraestructura (la red)

**Script:** `infraestructura/extraer_infraestructura.py`

Toma los nodos y zonas urbanas que curamos en la fase 1 (`public/data/`) y genera tres archivos:

| Archivo | Qué contiene | Cantidad |
|---|---|---|
| `nodos.geojson` | Los lugares de la red (puntos) | 237 nodos |
| `aristas.geojson` | Las calles aéreas (líneas) | 633 aristas |
| `zonas_urbanas.geojson` | Los límites de los pueblos (polígonos) | 8 zonas |

### Cómo se crean las aristas

No existe un mapa oficial de "calles aéreas" para drones, así que las generamos con una regla simple:

1. **Cada nodo se une con sus 4 vecinos más cercanos** (método "K vecinos", con K = 4).
2. Si algún grupo de nodos queda aislado, se une al resto por el par de nodos más cercano.
   Así **siempre existe un camino** entre cualquier par de nodos (el grafo es conexo).
3. El **costo** de cada arista es su **largo en metros**.

Resultado: aristas de 11 m a 3 km, con un promedio de 301 m.

---

## 8. Punto 2: metadata (4 fuentes)

La metadata **no bloquea** rutas: hace que algunas sean más caras o más baratas. Se usará en la fase 3.

| Script | Fuente | Qué entrega | Para qué sirve |
|---|---|---|---|
| `sinca_calidad_aire.py` | API del SINCA (Ministerio del Medio Ambiente) | Contaminantes de 10 estaciones de la zona (SO2, NO2, CO, O3, PM10, PM2.5) | Dar **prioridad** a los nodos con peor aire |
| `srtm_relieve.py` | SRTM de la NASA (vía OpenTopoData) | Altura del terreno cada 100 m bajo cada arista | Saber si hay **cerros** en el camino y cuánto debe subir el dron |
| `ine_manzanas.py` | Censo 2017 del INE (vía IDE de la SMA) | 703 manzanas (polígonos) con su población | **Riesgo poblacional**: no conviene volar sobre zonas con mucha gente |
| `osm_antenas.py` | OpenStreetMap (vía Overpass) | 25 antenas y su cobertura estimada (círculo de 3 km) | Detectar **zonas sin señal** |

### ¿Por qué cambiaron algunas fuentes respecto al informe?

| En el informe | Ahora | Motivo |
|---|---|---|
| Subtel (cobertura) | Antenas de OSM | La página de Subtel tiene captcha y no tiene API: no se puede automatizar |
| Overpass (riesgo poblacional) | Manzanas del INE | El INE entrega **población real por manzana** y en **polígonos** |

---

## 9. Punto 3: amenazas (4 fuentes)

Cada amenaza entrega un **polígono** (el área afectada) y un campo `exceeds`:
**`exceeds = true` significa que la zona está activa.** La fase 3 decidirá qué nodos y aristas
bloquea cada tipo de zona activa.

| Script | Fuente | Qué entrega | Cuándo la zona está activa (`exceeds = true`) |
|---|---|---|---|
| `firms_incendios.py` | NASA FIRMS (satélites) | Focos de incendio de los últimos 7 días + círculo de 2 km | Si la detección es confiable (confianza nominal o alta) |
| `csn_sismos.py` | EMSC (incluye los sismos que calcula el CSN de Chile) | Sismos de los últimos 30 días + círculo de afectación según magnitud | Si la magnitud es ≥ 5. Además indica si la base queda dentro del círculo (`base_dentro_radio`) |
| `openmeteo_viento.py` | Open-Meteo | Viento actual en una grilla de 4×4 celdas sobre la zona | Si las ráfagas o el viento a 120 m superan 14 m/s |
| `metno_lluvia.py` | MET Norway | Lluvia de la próxima hora en la misma grilla | Si supera 2 mm/h |

### ¿Qué es la grilla 4×4?

El viento y la lluvia no son "un punto": cubren áreas. Dividimos la zona en 16 rectángulos y
consultamos el clima en el centro de cada uno. Si una celda está activa, las aristas que la cruzan
quedan marcadas para la fase 3.

### ¿Por qué cambiaron algunas fuentes?

| En el informe | Ahora | Motivo |
|---|---|---|
| DMC / Windy | Open-Meteo | La DMC pide registro y token; Windy es de pago |
| JAXA GSMaP / RainViewer | MET Norway | JAXA pide una cuenta FTP; RainViewer solo entrega imágenes, sin números |
| CSN | EMSC | El CSN no tiene API; EMSC publica sus mismos sismos (campo `authority = "CSN"`) |

---

## 10. Punto 0: la base de datos

Usamos **PostgreSQL 16.9** con dos extensiones:

- **PostGIS 3.5.2:** permite guardar puntos, líneas y polígonos, y hacer preguntas espaciales
  ("¿esta arista cruza esta zona de incendio?").
- **pgRouting 3.8.0:** trae algoritmos de rutas como **Dijkstra** (`pgr_dijkstra`).

Hay 9 tablas. El diagrama y su explicación están en **`bd/GUIA_BD.md`**.

---

## 11. Cómo se ejecuta

Todo corre en contenedores Docker. Se necesita Docker Desktop (o Docker Engine con Compose) e internet,
porque las APIs se consultan en vivo.

```bash
python3 main.py
```

`main.py` hace, en orden:

1. Construye la imagen del ETL (`Dockerfile`).
2. Levanta la base de datos (`docker-compose.yml`, servicio `db`) y espera a que responda.
3. Ejecuta las 9 extracciones (infraestructura, 4 de metadata, 4 de amenazas).
4. Borra y vuelve a crear la BD con `bd/schema.sql`.
5. Ejecuta los 11 cargadores (uno por cada `.geojson`).
6. Calcula las rutas con `pgr_dijkstra` y guarda `sitio_web/data/ruta_dijkstra.geojson`.
7. Levanta el sitio web y muestra los conteos de la BD.

Al final, el sitio queda en **http://localhost:8000/sitio_web/**.

Opciones:

```bash
python3 main.py --sin-descarga   # no consulta APIs: usa los .geojson ya generados
```

Para comprobar que todo está bien (pauta, GeoJSON y BD):

```bash
docker compose run --rm etl python tests/verificar.py
```

Cada corrida con descarga cambia los datos en vivo (otras mediciones, otros sismos, otro viento).

---

## 12. Sitio web y ruta

El sitio (`sitio_web/`) usa Leaflet y muestra:

- **Infraestructura:** nodos por categoría, aristas y zonas urbanas.
- **Metadata:** calidad del aire por estación (con sus mediciones), relieve por arista, población por
  manzana y cobertura de antenas.
- **Amenazas:** incendios, sismos, celdas de viento y de lluvia. Las zonas activas se ven resaltadas.
- **Ruta:** la ruta de pgr_dijkstra desde el Aeródromo de Quintero hasta cada estación SINCA.
  El selector cambia de destino. El costo es la longitud, y la ruta **no considera** metadata ni amenazas.

Ejemplo con los datos de la última corrida: del Aeródromo a la **Estación SINCA Puchuncaví** hay
**14,41 km en 22 tramos**; a la Estación Centro Quintero hay 1,69 km en 6 tramos.

---

## 13. Estado de la fase 2 (pauta)

| Punto | Qué pide la pauta | Dónde está | Estado |
|---|---|---|---|
| 0 | Diagrama de la BD y `.sql` para crearla | `bd/bd_diagrama.png`, `bd/schema.sql` | Listo |
| 1 | Script que extrae y transforma nodos y aristas a JSON | `infraestructura/extraer_infraestructura.py` | Listo (ver punto débil 1 de la sección 14) |
| 2 | Un script por cada API o BD de metadata | `metadata/*.py` (4) | Listo |
| 3 | Un script por cada API o BD de amenazas | `amenazas/*.py` (4) | Listo |
| 4 | Un `.md` por cada JSON que explique sus campos | `*.md` junto a cada `.geojson` | Listo (comprobado por `tests/verificar.py`) |
| 6 | Un cargador por cada JSON | `cargar_*.py` (11) | Listo |
| 7 | Sitio web con Leaflet | `sitio_web/` | Listo |
| 8 | Ruta con pgr_dijkstra, costo = longitud, sin metadata ni amenazas | `ruteo/ruta_dijkstra.py` | Listo |
| 9 | Un `main` en la raíz que ejecute todo | `main.py` | Listo |
| Docker | Todo debe correr en contenedores Docker con versiones fijadas | `Dockerfile`, `docker-compose.yml`, `requirements.txt` | Listo |

### Lo que comprueba `tests/verificar.py`

- Están todos los archivos de la pauta (schema, diagrama, extractores, cargadores, sitio, main).
- Cada `.geojson` es válido según RFC 7946 (anillos cerrados y con el sentido correcto).
- Cada campo de cada `.geojson` aparece en su `.md`.
- Cada tabla de la BD tiene la misma cantidad de filas que su archivo.
- Todas las geometrías son válidas.
- El grafo es conexo (1 componente).
- La ruta del sitio coincide con `pgr_dijkstra` recalculado en la BD, y su costo es igual a su longitud.

---

## 14. Puntos débiles y pendientes

1. **Los nodos no se descargan en vivo.** Salen del dataset que curamos a mano en la fase 1. Los
   scripts de `scripts/` los cosecharon desde Overpass y después se limpiaron a mano. Por eso el
   punto 1 de la pauta está cumplido solo en la transformación. Para cumplirlo completo, hay que
   automatizar la extracción desde Overpass y aplicar las correcciones manuales como una lista.
2. **Faltan dos estaciones SINCA como nodos:** Los Maitenes y Valle Alegre existen en el SINCA pero no en la red.
3. **34 nodos no tienen elevación.**
4. **La red no incluye postes ni torres.** El informe de la fase 1 los proponía como nodos de paso.
   Hoy las antenas están solo en la metadata.
5. **Las aristas no siguen caminos reales.** Son líneas rectas entre vecinos cercanos. Se podría
   usar la Red Vial del MOP (disponible en la misma IDE de la SMA) como fuente de aristas.
6. **La red es 2D.** La altura no forma parte del grafo; el relieve se guarda aparte.
7. **Algunos valores son supuestos** y están documentados en cada `.md`: radio de antena de 3 km,
   radio de incendio de 2 km y fórmula del radio de un sismo. Se pueden ajustar en la fase 3.
8. **Altura de vuelo:** DAN 151 (edición 3, 2024) fija **400 pies (120 m) AGL**. El informe dice
   "120 a 200 m", lo que contradice la norma y hay que corregirlo.
9. **Corre en una máquina Apple Silicon con emulación:** la imagen de PostgreSQL con pgRouting es
   amd64. Funciona, pero es más lenta. En un servidor amd64 no hay emulación.
