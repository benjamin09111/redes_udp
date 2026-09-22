/**
 * projection.js
 * Conversor analítico de alta precisión WGS84 (EPSG:4326) <-> UTM Zona 19S (EPSG:32719).
 * Implementación matemática pura en ES Modules sin librerías externas pesadas (ej. Proj4).
 * 
 * Permite transformar coordenadas angulares [lng, lat] en coordenadas métricas cartesianas [x, y],
 * reduciendo el cálculo de distancias 3D en los planificadores (A*, Genéticos, ACO)
 * de funciones trigonométricas (Haversine) a distancia euclidiana en CPU (10-15x más rápido).
 */

// Parámetros Elipsoide WGS84
const A = 6378137.0; // Semieje mayor en metros
const F = 1 / 298.257223563; // Aplanamiento
const B = A * (1 - F); // Semieje menor
const E2 = (A * A - B * B) / (A * A); // Primera excentricidad al cuadrado: ~0.00669437999
const E_PRIME2 = (A * A - B * B) / (B * B); // Segunda excentricidad al cuadrado
const K0 = 0.9996; // Factor de escala en el meridiano central

// UTM Zona 19S (Chile Central: 72°W a 66°W)
const ZONE = 19;
const CENTRAL_MERIDIAN = -69.0; // Grados
const FALSE_EASTING = 500000.0;
const FALSE_NORTHING = 10000000.0; // Hemisferio Sur

/**
 * Convierte [longitud, latitud] (grados decimales) a [Easting, Northing] (metros) en UTM 19S
 * @param {number} lng - Longitud en grados (ej: -71.53)
 * @param {number} lat - Latitud en grados (ej: -32.78)
 * @returns {[number, number]} [x, y] en metros UTM 19S
 */
export function forwardUTM19S(lng, lat) {
  const radLat = (lat * Math.PI) / 180.0;
  const radLng = (lng * Math.PI) / 180.0;
  const radLng0 = (CENTRAL_MERIDIAN * Math.PI) / 180.0;

  const sinLat = Math.sin(radLat);
  const cosLat = Math.cos(radLat);
  const tanLat = Math.tan(radLat);

  const N = A / Math.sqrt(1 - E2 * sinLat * sinLat);
  const T = tanLat * tanLat;
  const C = E_PRIME2 * cosLat * cosLat;
  const A_coeff = cosLat * (radLng - radLng0);

  // Distancia meridional M
  const M = A * (
    (1 - E2 / 4 - 3 * E2 * E2 / 64 - 5 * E2 * E2 * E2 / 256) * radLat -
    (3 * E2 / 8 + 3 * E2 * E2 / 32 + 45 * E2 * E2 * E2 / 1024) * Math.sin(2 * radLat) +
    (15 * E2 * E2 / 256 + 45 * E2 * E2 * E2 / 1024) * Math.sin(4 * radLat) -
    (35 * E2 * E2 * E2 / 3072) * Math.sin(6 * radLat)
  );

  const x = FALSE_EASTING + K0 * N * (
    A_coeff +
    (1 - T + C) * Math.pow(A_coeff, 3) / 6 +
    (5 - 18 * T + T * T + 72 * C - 58 * E_PRIME2) * Math.pow(A_coeff, 5) / 120
  );

  let y = K0 * (
    M + N * tanLat * (
      A_coeff * A_coeff / 2 +
      (5 - T + 9 * C + 4 * C * C) * Math.pow(A_coeff, 4) / 24 +
      (61 - 58 * T + T * T + 600 * C - 330 * E_PRIME2) * Math.pow(A_coeff, 6) / 720
    )
  );

  // Ajuste de hemisferio sur
  if (lat < 0) {
    y += FALSE_NORTHING;
  }

  return [x, y];
}

/**
 * Convierte [x, y] (metros UTM 19S) a [longitud, latitud] (grados WGS84)
 * @param {number} x - Easting en metros
 * @param {number} y - Northing en metros
 * @returns {[number, number]} [lng, lat] en grados WGS84
 */
export function inverseUTM19S(x, y) {
  let adjustedY = y;
  // Si estamos en hemisferio sur
  adjustedY -= FALSE_NORTHING;

  const e1 = (1 - Math.sqrt(1 - E2)) / (1 + Math.sqrt(1 - E2));
  const M = adjustedY / K0;
  const mu = M / (A * (1 - E2 / 4 - 3 * E2 * E2 / 64 - 5 * E2 * E2 * E2 / 256));

  const phi1Rad = mu +
    (3 * e1 / 2 - 27 * Math.pow(e1, 3) / 32) * Math.sin(2 * mu) +
    (21 * e1 * e1 / 16 - 55 * Math.pow(e1, 4) / 32) * Math.sin(4 * mu) +
    (151 * Math.pow(e1, 3) / 96) * Math.sin(6 * mu);

  const sinPhi1 = Math.sin(phi1Rad);
  const cosPhi1 = Math.cos(phi1Rad);
  const tanPhi1 = Math.tan(phi1Rad);

  const N1 = A / Math.sqrt(1 - E2 * sinPhi1 * sinPhi1);
  const T1 = tanPhi1 * tanPhi1;
  const C1 = E_PRIME2 * cosPhi1 * cosPhi1;
  const R1 = A * (1 - E2) / Math.pow(1 - E2 * sinPhi1 * sinPhi1, 1.5);
  const D = (x - FALSE_EASTING) / (N1 * K0);

  const latRad = phi1Rad - (N1 * tanPhi1 / R1) * (
    D * D / 2 -
    (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * E_PRIME2) * Math.pow(D, 4) / 24 +
    (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * E_PRIME2 - 3 * C1 * C1) * Math.pow(D, 6) / 720
  );

  const radLng0 = (CENTRAL_MERIDIAN * Math.PI) / 180.0;
  const lngRad = radLng0 + (
    D -
    (1 + 2 * T1 + C1) * Math.pow(D, 3) / 6 +
    (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * E_PRIME2 + 24 * T1 * T1) * Math.pow(D, 5) / 120
  ) / cosPhi1;

  return [(lngRad * 180.0) / Math.PI, (latRad * 180.0) / Math.PI];
}
