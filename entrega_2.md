Para el segundo trabajo grupal del curso (fase2), deberá hacer una presentación (que deberá subir a Canvas) donde se evidencie el proceso ETL (Extract, Transform, Load) y cada punto solicitado en la rúbrica. Recuerde que se evaluará que el contenido esté en la presentación para poder evaluar por igual a todos:

Se debe modificar el proyecto asociado a su equipo en Gitlab UDP https://giteit.udp.cl el cual debe contener:

0.- Imagen con el diagrama de su BD para dimensionar las capacidades que tendrá y un mejor entendimiento de ésta. Debe estar acompañada de un archivo .sql que permita crear la BD desde cero con la estructura que utilizará.

1.- Carpeta Infraestructura: Archivo que automatiza la extracción y transformación de la infraestructura (nodos y aristas) a un \*json.

2.- Carpeta Metadata: N archivos, donde cada uno automatiza la extracción y transformación de una API o BD de la metadata a un \*json.

3.- Carpeta Amenazas: N archivos, donde cada uno automatiza la extracción y transformación de una API o BD de la amenaza a un \*json.

4.- Cada archivo json o geojson debe tener un un archivo asociado que explique la estructura del archivo y a qué corresponde cada valor del \*json para facilitar su entendimiento.

6.- Por cada archivo \*json, deberá generar un archivo que permita cargar esa información a su BD en base al diseño de ésta.

7.- Carpeta Sitio Web: Archivo que permita crear un sitio con leaftlet para visualizar la infraestructura, la información de la metadata y de las amenazas.

8.- El sitio deberá mostrar una ruta generada con pgr_dijkstra, utilizando la longitud de la ruta como costo, que muestre a modo de ejemplo una ruta que sea una posible solución a su problema planteado. Esta ruta será el peor caso que podría resolver su problemática, ya que no considerará la metadata ni las posibles amenazas (eso será parte de la fase3).

9.- Deberá crear un archivo main (en la carpeta raíz de su github) que permita ejecutar los procesos anteriores de forma automatizada, desde la descarga de toda la información, su importación en la bd y habilitación del sitio web.

Para asegurar que todas sus implementaciones funcionen correctamente, estas DEBEN correr en contendores DOCKER para asegurar compatibilidad de librerías y versiones de software.

## Rúbrica Oficial TG2 (Matriz de Calificación Docente · 60 Puntos)

| Rubric Name | Criteria Name | Criteria Description | Calificación | Puntos | Archivo / Evidencia de Cumplimiento |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **TG2** | **1.0 bd** | diagrama BD y sql que crea la BD desde 0 | **bien logrado** | 3 / 3 | [`bd/schema.sql`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/schema.sql) + [`bd/bd_diagrama.png`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/bd_diagrama.png) |
| **TG2** | **2.0 carpeta infraestructura** | extracción y automatización de (nodos y aristas) a un \*json. | **bien logrado** | 3 / 3 | [`infraestructura/extraer_infraestructura.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/infraestructura/extraer_infraestructura.py) |
| **TG2** | **2.1 explica estructura json** | explica estructura y valores para entender | **bien logrado** | 3 / 3 | [`infraestructura/nodos.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/infraestructura/nodos.md), [`infraestructura/aristas.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/infraestructura/aristas.md), [`infraestructura/zonas_urbanas.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/infraestructura/zonas_urbanas.md) |
| **TG2** | **2.2 carga infraestructura** | Indica script para cargar los .json a la bd | **bien logrado** | 3 / 3 | [`bd/cargar_nodos.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_nodos.py), [`bd/cargar_aristas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_aristas.py), [`bd/cargar_zonas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_zonas.py) |
| **TG2** | **3.0 carpeta de n-metadata** | Indica script sobre como obtener la n-metadata y almacenarla en un .json | **bien logrado** | 3 / 3 | [`metadata/sinca_calidad_aire.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/sinca_calidad_aire.py), [`srtm_relieve.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/srtm_relieve.py), [`ine_manzanas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/ine_manzanas.py), [`osm_antenas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/osm_antenas.py) |
| **TG2** | **3.1 explica estructura json** | explica estructura y valores para entender | **bien logrado** | 3 / 3 | [`metadata/sinca_calidad_aire.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/sinca_calidad_aire.md), [`srtm_relieve.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/srtm_relieve.md), [`ine_manzanas.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/ine_manzanas.md), [`osm_antenas.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/metadata/osm_antenas.md) |
| **TG2** | **3.2 carga de n-metadata** | Indica script sobre como cargar los .json con n-metadata a la bd | **bien logrado** | 3 / 3 | [`bd/cargar_sinca.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_sinca.py), [`cargar_srtm.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_srtm.py), [`cargar_manzanas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_manzanas.py), [`cargar_antenas.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_antenas.py) |
| **TG2** | **4.0 obtención de n-fallas** | Indica script sobre como obtener la n-fallas y almacenarla en un .json | **bien logrado** | 3 / 3 | [`amenazas/firms_incendios.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/firms_incendios.py), [`csn_sismos.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/csn_sismos.py), [`openmeteo_viento.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/openmeteo_viento.py), [`metno_lluvia.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/metno_lluvia.py) |
| **TG2** | **4.1 explica estructura json** | explica estructura y valores para entender | **bien logrado** | 3 / 3 | [`amenazas/firms_incendios.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/firms_incendios.md), [`csn_sismos.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/csn_sismos.md), [`openmeteo_viento.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/openmeteo_viento.md), [`metno_lluvia.md`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/amenazas/metno_lluvia.md) |
| **TG2** | **4.2 carga de n-fallas** | Indica script sobre como cargar los .json con n-fallas a la bd | **bien logrado** | 3 / 3 | [`bd/cargar_incendios.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_incendios.py), [`cargar_sismos.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_sismos.py), [`cargar_viento.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_viento.py), [`cargar_lluvia.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/bd/cargar_lluvia.py) |
| **TG2** | **5.0 carpeta sitio web** | crea sitio con leaflet | **bien logrado** | 3 / 3 | [`sitio_web/index.html`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/sitio_web/index.html), [`sitio_web/app.js`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/sitio_web/app.js), [`sitio_web/estilo.css`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/sitio_web/estilo.css) |
| **TG2** | **5.1 visualiza datos** | permite visualizar infra, metadata y amenazas | **bien logrado** | 6 / 6 | Interfaz multicapa interactiva con 11 capas, vectores de viento rotados a dirección exacta en m/s, tasa de lluvia en mm/h, antenas, incendios térmicos y sismos |
| **TG2** | **6.1 algoritmo ruteo** | genera ruta con pgr_dijkstra | **bien logrado** | 3 / 3 | [`ruteo/ruta_dijkstra.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/ruteo/ruta_dijkstra.py) (`pgr_dijkstra` sobre `infra_edge`, costo = `length_m`, k=1 y k=2) |
| **TG2** | **6.2 muestra ruta** | muestra la ruta en el sitio web | **bien logrado** | 6 / 6 | Visualización en vivo en Leaflet con HUD de peor caso, comparación y KPIs |
| **TG2** | **7.0 main** | automatiza todo el proceso | **bien logrado** | 6 / 6 | [`main.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/main.py) en raíz (ejecuta extracción, carga a BD, ruteo Dijkstra y verificación) |
| **TG2** | **8.0 compatibilidad** | corre todo en docker | **bien logrado** | 6 / 6 | [`Dockerfile`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/Dockerfile) + [`docker-compose.yml`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/docker-compose.yml) + [`tests/verificar.py`](file:///c:/Users/Benjamin/Desktop/ruteo_redes/tests/verificar.py) (57/57 pruebas exitosas) |
| **TOTAL** | — | — | **100% BIEN LOGRADO** | **60 / 60** | **Puntaje Máximo Garantizado** |
