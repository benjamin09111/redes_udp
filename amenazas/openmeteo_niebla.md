# `openmeteo_niebla.geojson` - Niebla Costera y Visibilidad Reducida

## Origen y Metodología
- **Fuente**: Open-Meteo Forecast API (`https://api.open-meteo.com/v1/forecast`).
- **Área y Grilla**: Cuadrícula regular de $4 \times 4$ celdas poligonales cubriendo el litoral de Quintero, Ventanas y Puchuncaví.
- **Justificación**: La niebla marina (camanchaca) reduce drásticamente la visibilidad visual obligatoria bajo la norma DAN 151 (DGAC) para operaciones de aeronaves pilotadas a distancia (VLOS). La humedad de saturación degrada además la calidad de las mediciones de los sensores electroquímicos de gases y compromete la aviónica no presurizada.
- **Umbral**: Zona activa (`exceeds = true`) si la visibilidad es inferior a 1.000 m (`threshold` = 1000.0) o la humedad relativa es $\ge 95\,\%$ en presencia de nubosidad baja.

## Estructura de Atributos GeoJSON
Cada elemento de la colección representa una celda poligonal de la grilla meteorológica con las siguientes propiedades:
- `external_id`: Identificador único de la celda y marca temporal (ej. `niebla_r0c0_...`).
- `event_type`: Categoría de la contingencia (`niebla`).
- `value`: Visibilidad horizontal en superficie.
- `unit`: Unidad de medida de visibilidad (`m (visibilidad)`).
- `threshold`: Umbral crítico operacional (1000.0 metros).
- `exceeds`: Booleano (`true` si la celda se encuentra bajo condición de niebla o baja visibilidad).
- `observed_at`: Marca temporal ISO 8601 en UTC del pronóstico u observación.
- `lon`: Longitud geográfica del centroide de la celda en grados WGS84.
- `lat`: Latitud geográfica del centroide de la celda en grados WGS84.
- `cell`: Identificador matricial de fila y columna (`r0c0` a `r3c3`).
- `relative_humidity`: Humedad relativa medida a 2 metros en porcentaje.
- `cloud_cover_low`: Porcentaje de cobertura de nubes bajas (estrato marino costero).
- `weather_code`: Código meteorológico sinóptico WMO.
