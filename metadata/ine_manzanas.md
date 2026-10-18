# ine_manzanas.geojson

Población por **manzana censal** (polígonos). Mide el riesgo poblacional en caso de caída del dron:
las aristas que sobrevuelan manzanas densas tienen mayor costo y requieren rutas más conservadoras.
Es la **base de datos geoespacial con polígonos** de la metadata.

- **Generado por:** `ine_manzanas.py`
- **Fuente (BD geoespacial):** INE, Censo 2017, publicado en la IDE de la Superintendencia del Medio
  Ambiente (ArcGIS REST, capa "Manzanas censales - INE"):
  `https://ideserver.sma.gob.cl/arcgis/rest/services/IDE/Infraestructura_rural_urbana/MapServer/11`
- **Tabla destino:** `meta_census_block`

## Transformación
- Se piden los `objectIds` de las manzanas que intersectan el área de estudio y luego sus
  atributos y geometrías en lotes de 200 (el servidor no pagina de forma confiable).
- La geometría Esri JSON (`rings`) se convierte a GeoJSON `MultiPolygon` con la orientación de
  RFC 7946 (anillo exterior antihorario, huecos horarios).
- Se calcula el área y la densidad poblacional.

## Bloque `etl`
| Campo | Tipo | Significado |
|---|---|---|
| `fuente`, `url` | string | Origen de los datos |
| `generado` | string ISO 8601 | Fecha y hora UTC de la ejecución |
| `parametros.aoi` | number[4] | Área de estudio `[lon_min, lat_min, lon_max, lat_max]` |
| `total` | int | Cantidad de manzanas |

## `features[]`
**Geometría:** `MultiPolygon` (contorno de la manzana).

| Propiedad | Tipo | Significado |
|---|---|---|
| `manzent` | string | Código único de la manzana INE |
| `cut` | int | Código Único Territorial de la comuna (5107 Quintero, 5105 Puchuncaví) |
| `commune` | string | Comuna |
| `district` | string | Distrito censal |
| `persons` | int | Personas censadas en la manzana |
| `dwellings` | int / null | Total de viviendas |
| `area_m2` | number | Área de la manzana en m² |
| `density_hab_km2` | number / null | Densidad = `persons` / área en km² |

> Limitación: son datos del Censo 2017 (los disponibles en el servicio). Las manzanas son urbanas;
> la población rural dispersa no queda representada.
