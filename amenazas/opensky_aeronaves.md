# `opensky_aeronaves.geojson` - Tráfico Aéreo Tripulado en Baja Altura

## Origen y Metodología
- **Fuente**: OpenSky Network API (`https://opensky-network.org/api/states/all`).
- **Área y Ventana**: Espacio aéreo circundante al Aeródromo de Quintero (SCER), Ventanas y Puchuncaví.
- **Justificación**: El conflicto espacial con aeronaves tripuladas (aviones ligeros, helicópteros de enlace y patrullaje costero) constituye el mayor riesgo de seguridad para operaciones UAV (Air Risk Class ARC en la metodología SORA \cite{sora} y DAN 151 \cite{dan151}). Toda aeronave tripulada tiene prioridad de paso irrestricta.
- **Umbral**: Aeronaves operando a cotas inferiores o iguales a 1.000 m sobre el nivel medio del mar (`threshold` = 1000.0) generan una zona circular de exclusión aérea obligatoria de 1.500 m de radio para el enrutador de drones (`exceeds = true`).

## Estructura de Atributos GeoJSON
Cada elemento de la colección representa el área de exclusión circular en torno a una aeronave tripulada con las siguientes propiedades:
- `external_id`: Identificador del evento compuesto por código ICAO24 y marca temporal.
- `event_type`: Categoría de la contingencia (`aeronave`).
- `value`: Altitud barométrica en metros de la aeronave.
- `unit`: Unidad de altitud (`m (altitud barométrica)`).
- `threshold`: Techo crítico de conflicto para operaciones a baja cota (1000.0 metros).
- `exceeds`: Booleano (`true` si la aeronave vuela en la cota de riesgo y activa la zona de exclusión).
- `observed_at`: Marca temporal ISO 8601 en UTC del reporte ADS-B.
- `lon`: Longitud geográfica de la aeronave en grados WGS84.
- `lat`: Latitud geográfica de la aeronave en grados WGS84.
- `callsign`: Indicativo de llamada de la aeronave o matrícula aeronáutica.
- `icao24`: Dirección hexadecimal transponder de 24 bits ICAO.
- `baro_altitude_m`: Altitud barométrica en metros reportada por transponder modo S / ADS-B.
- `velocity_ms`: Velocidad horizontal sobre el terreno en metros por segundo.
- `exclusion_radius_m`: Radio métrico de la burbuja de protección espacial (1500.0 metros).
