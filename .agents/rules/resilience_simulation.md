# Reglas de Simulación y Enrutamiento Resiliente

1. Mantener siempre la fidelidad científica al modelo de Kosior et al. (2024) y a la normativa DGAC DAN 151 (0-120m AGL).
2. Todo dato geoespacial debe ser GeoJSON estándar (WGS84 [longitud, latitud, altitud]).
3. Mantener arquitectura desacoplada: algoritmos puros en JavaScript ES Modules, independientes de Leaflet.
4. Código minimalista (YAGNI): sin librerías pesadas innecesarias.
