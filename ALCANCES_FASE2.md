# Alcances de la fase 2: ETL, base de datos y sitio web

Este documento resume qué se hizo en la fase 2, cómo se comprobó y qué queda pendiente.
Está pensado para revisión del grupo.

---

## 1. Cómo correrlo

```bash
python3 main.py                                          # pipeline completo desde cero
docker compose run --rm etl python tests/verificar.py    # comprobaciones
```

El sitio queda en **http://localhost:8000/sitio_web/**.

Solo se necesita Docker y Python 3 en la máquina. Todo lo demás corre en contenedores.

---

## 2. Pauta, punto por punto

| Punto | Estado | Evidencia |
|---|---|---|
| 0 · Diagrama y `.sql` de la BD | Cumple | `bd/schema.sql` crea las 9 tablas desde cero. Diagrama en `bd/bd_diagrama.png` |
| 1 · Extracción y transformación de nodos y aristas a JSON | **Parcial** | La transformación es automática, pero los nodos salen de un archivo curado a mano y no de una descarga (ver sección 6) |
| 2 · Un script por API o BD de metadata (n = 4) | Cumple | SINCA, SRTM, INE (polígonos) y OSM |
| 3 · Un script por API o BD de amenazas (n = 4) | Cumple | FIRMS, EMSC/CSN, Open-Meteo y MET Norway (polígonos) |
| 4 · Un `.md` por JSON que explique sus campos | Cumple | `tests/verificar.py` revisa que cada campo aparezca documentado |
| 6 · Un cargador por JSON | Cumple | 11 cargadores `cargar_*.py`, probados contra la BD |
| 7 · Sitio Leaflet con infraestructura, metadata y amenazas | Cumple | `sitio_web/`. Carga las 12 fuentes sin errores |
| 8 · Ruta con pgr_dijkstra, costo = longitud, sin metadata ni amenazas | Cumple | El costo es igual a la longitud en los 8 destinos. Aeródromo → Puchuncaví: 14,41 km, 22 tramos |
| 9 · `main` en la raíz que lo haga todo | Cumple | `python3 main.py` descarga, carga la BD, calcula la ruta y habilita el sitio |
| Docker · todo en contenedores con versiones fijadas | Cumple | Servicios `db`, `etl` y `web`. Python 3.12.15, PostgreSQL 16.9, PostGIS 3.5.2, pgRouting 3.8.0, psycopg 3.2.13 |

---

## 3. Cómo se probó

- **Corrida completa desde cero:** se borró el volumen de la base de datos, se ejecutó
  `python3 main.py` con descarga real de las 8 fuentes externas, y terminó con código 0.
- **`tests/verificar.py`:** 86 de 86 chequeos correctos. Revisa:
  - que estén todos los archivos de la pauta;
  - que cada GeoJSON cumpla RFC 7946;
  - que cada campo esté documentado;
  - que los conteos de la BD coincidan con los JSON;
  - que las geometrías sean válidas;
  - que el grafo sea conexo (1 componente);
  - que la ruta del sitio coincida con `pgr_dijkstra` recalculado en la BD.
- **Sitio:** se abrió en Chrome sin interfaz. Carga las 12 fuentes, no aparecen errores de
  JavaScript en la consola, y se revisó la captura del mapa.

La ruta se calcula en la BD y se exporta a `sitio_web/data/ruta_dijkstra.geojson`.
El sitio lee archivos; no consulta la BD en vivo.

---

## 4. Inconsistencias encontradas y corregidas

1. **`zonas_urbanas.geojson`** tenía los anillos en sentido horario. RFC 7946 pide antihorario.
   Se corrigió en el extractor.
2. **`exceeds` en sismos** significaba una cosa en el script y otra en la documentación.
   Ahora, en las cuatro amenazas, `exceeds = true` significa **zona activa**, y la fase 3 decide
   qué bloquea. Para sismos se agregó `base_dentro_radio`.
   **Esto cambia los datos:** ahora hay 1 sismo activo (M 5,2); antes había 0.
   Si se prefiere la regla anterior, se revierte fácil.
3. **AGENTS.md** decía 9 estaciones SINCA como nodos. Son 8 nodos (de 10 estaciones SINCA en el área).
4. **Documentación:** `sinca_calidad_aire.md` y `csn_sismos.md` no documentaban todos sus campos.
   Se reescribió `GUIA_PROYECTO.md`, se actualizó `GUIA_BD.md` con los comandos Docker y se
   corrigió la semántica de `exceeds`.
5. **Versiones:** la imagen de la BD estaba en `latest`. Ahora está fijada en `16-3.5-3.8.0`.
6. **Mapa:** el control de capas tapaba el destino de la ruta. Ahora está colapsado.

---

## 5. Qué incluye la fase 2 (estructura)

| Carpeta / archivo | Contenido |
|---|---|
| `bd/` | `schema.sql`, diagrama, `conexion.py` y `GUIA_BD.md` |
| `infraestructura/` | Extractor de nodos, aristas y zonas urbanas, con sus 3 `.geojson`, `.md` y cargadores |
| `metadata/` | 4 fuentes (SINCA, SRTM, INE, OSM), con sus `.geojson`, `.md` y cargadores |
| `amenazas/` | 4 fuentes (FIRMS, EMSC/CSN, Open-Meteo, MET Norway), con sus `.geojson`, `.md` y cargadores |
| `ruteo/` | `ruta_dijkstra.py`, la ruta base con `pgr_dijkstra` |
| `sitio_web/` | Mapa Leaflet (`index.html`, `app.js`, `estilo.css`) |
| `tests/` | `verificar.py` |
| `main.py`, `Dockerfile`, `docker-compose.yml`, `requirements.txt` | Ejecución completa en Docker |

---

## 6. Pendiente (requiere decisión del grupo)

1. **Punto 1 solo parcial.** Los nodos vienen del archivo que se curó a mano en la fase 1.
   Para que la extracción sea reproducible, hay que bajarlos de Overpass y aplicar las
   correcciones manuales como una lista.
2. **Lo que prometió el informe y no está implementado:** postes y torres como nodos, aristas que
   sigan caminos reales (la Red Vial del MOP está en la misma IDE de la SMA) y altura de vuelo.
   La pauta de fase 2 no lo exige, pero el informe sí.
   **Decisión:** ¿se agrega antes de la entrega o se deja para la fase 3?
3. **Altura de vuelo:** se usó 120 m AGL. La edición 3 de DAN 151 (2024) dice "400 pies (120 m)".
   No se confirmó si es la edición vigente; hay una edición 4 de 2026 que parece un borrador.
4. **Apple Silicon:** la imagen de pgRouting es amd64 y corre con emulación. Funciona, pero es más lenta.
