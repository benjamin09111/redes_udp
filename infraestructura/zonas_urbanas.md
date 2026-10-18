# zonas_urbanas.geojson

Polígonos de las localidades urbanas del área de estudio. Se usan para identificar sobrevuelo de
zonas pobladas (restricción DAN 151) y penalizar las aristas que las crucen.

- **Generado por:** `extraer_infraestructura.py`
- **Fuente:** `public/data/urban_zones.geojson`, construido en la fase 1 con límites de OSM/Overpass
  (`scripts/build_all_urban_zones.py`) y recortes manuales.
- **Formato:** GeoJSON `FeatureCollection` (RFC 7946, WGS84 / EPSG:4326)
- **Tabla destino:** `urban_zone`

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `total` | int | Cantidad de zonas |

## `features[]`
**Geometría:** `MultiPolygon` (se normaliza a MultiPolygon aunque la zona tenga un solo polígono,
para que todas las filas de la tabla tengan el mismo tipo).

| Propiedad | Tipo | Significado |
|---|---|---|
| `code` | string | Identificador de la zona (ej. `urban_quintero`) |
| `name` | string | Nombre de la localidad |
| `city` | string | Comuna / ciudad |
| `area_km2` | number | Área del polígono en km² (proyección equirectangular local) |
