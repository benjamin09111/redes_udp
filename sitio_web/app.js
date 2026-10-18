// Sitio de la fase 2 (Leaflet). Lee los .geojson que generan infraestructura/, metadata/,
// amenazas/ y ruteo/. Sin frameworks: solo Leaflet y JavaScript del navegador.

const FUENTES = {
  nodos: '../infraestructura/nodos.geojson',
  aristas: '../infraestructura/aristas.geojson',
  zonas: '../infraestructura/zonas_urbanas.geojson',
  aire: '../metadata/sinca_calidad_aire.geojson',
  relieve: '../metadata/srtm_relieve.geojson',
  manzanas: '../metadata/ine_manzanas.geojson',
  antenas: '../metadata/osm_antenas.geojson',
  incendios: '../amenazas/firms_incendios.geojson',
  sismos: '../amenazas/csn_sismos.geojson',
  viento: '../amenazas/openmeteo_viento.geojson',
  lluvia: '../amenazas/metno_lluvia.geojson',
  rutas: 'data/ruta_dijkstra.geojson',
};

const COLOR_CATEGORIA = {
  base: '#10b981', sinca: '#f59e0b', emission_source: '#ef4444', health: '#ec4899',
  education: '#8b5cf6', commercial: '#06b6d4', crowded_area: '#84cc16', beach: '#0ea5e9',
  hospitality: '#f97316', restaurant: '#d946ef', attraction: '#14b8a6', historic: '#a16207',
  auxiliary_hub: '#64748b',
};
const NOMBRE_CATEGORIA = {
  base: 'Base', sinca: 'Estación SINCA', emission_source: 'Fuente emisora', health: 'Salud',
  education: 'Educación', commercial: 'Comercial', crowded_area: 'Área concurrida',
  beach: 'Playa', hospitality: 'Hospedaje', restaurant: 'Restaurante',
  attraction: 'Atractivo', historic: 'Histórico', auxiliary_hub: 'Hub auxiliar',
};
// Códigos de estado SINCA: 1 bueno, 2 regular, 3 alerta, 4 preemergencia, 5 emergencia
const COLOR_AIRE = { 1: '#22c55e', 2: '#eab308', 3: '#f97316', 4: '#dc2626', 5: '#7e22ce' };

// ---------- utilidades ----------
const esc = (v) => String(v ?? '—').replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const fila = (k, v) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`;
const tabla = (filas) => `<table class="pop">${filas.map(([k, v]) => fila(k, v)).join('')}</table>`;
const km = (m) => `${(m / 1000).toFixed(2)} km`;
const fmt = (n) => (n == null ? null : Number(n).toLocaleString('es-CL'));
const si = (valor) => (valor ? 'sí' : 'no');
const bloquea = (p) => (p.exceeds ? 'Sí (zona activa)' : 'No');

async function cargar(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// ---------- mapa base ----------
const mapa = L.map('mapa').setView([-32.76, -71.47], 12);
const capasBase = {
  'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap',
  }),
  'Satélite (Esri)': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }),
};
capasBase['OpenStreetMap'].addTo(mapa);

// ---------- constructores de capas (cada una recibe el GeoJSON ya cargado) ----------
function capaNodos(fc) {
  return L.geoJSON(fc, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      radius: 5, color: '#0f172a', weight: 1,
      fillColor: COLOR_CATEGORIA[f.properties.category] ?? '#94a3b8', fillOpacity: 0.95,
    }),
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Nombre', f.properties.name],
      ['Categoría', NOMBRE_CATEGORIA[f.properties.category] ?? f.properties.category],
      ['Localidad', f.properties.city],
      ['Elevación (msnm)', f.properties.elevation_msnm],
      ['Contaminantes', (f.properties.pollutants || []).join(', ') || null],
      ['Código', f.properties.code],
    ])),
  });
}

function capaAristas(fc) {
  return L.geoJSON(fc, {
    style: { color: '#64748b', weight: 1.5, opacity: 0.65 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Arista', f.properties.id],
      ['Origen → destino', `${f.properties.source_code} → ${f.properties.target_code}`],
      ['Longitud', `${f.properties.length_m} m`],
    ])),
  });
}

function capaZonas(fc) {
  return L.geoJSON(fc, {
    style: { color: '#0284c7', weight: 2, fillColor: '#38bdf8', fillOpacity: 0.12 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Zona urbana', f.properties.name],
      ['Comuna', f.properties.city],
      ['Área', `${f.properties.area_km2} km²`],
    ])),
  });
}

function capaAire(fc) {
  return L.geoJSON(fc, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      radius: 9, color: '#ffffff', weight: 2,
      fillColor: COLOR_AIRE[f.properties.worst_status_code] ?? '#94a3b8', fillOpacity: 1,
    }),
    onEachFeature: (f, l) => {
      const p = f.properties;
      const medidas = (p.measurements || []).map((m) =>
        `<tr><td>${esc(m.pollutant)}</td><td>${esc(m.value)} ${esc(m.unit)}</td>` +
        `<td>${esc(m.averaging)}</td><td>${esc(m.status)}</td></tr>`).join('');
      l.bindPopup(
        `<strong>${esc(p.station_name)}</strong><br>${esc(p.commune)} · ${esc(p.network)}<br>` +
        `Nodo asociado: ${esc(p.node_code)}` +
        `<table class="pop"><tr><th>Contaminante</th><th>Valor</th><th>Promedio</th><th>Estado</th></tr>` +
        `${medidas}</table>`);
    },
  });
}

const colorRelieve = (r) => (r > 100 ? '#dc2626' : r > 50 ? '#f97316' : r > 20 ? '#eab308' : '#22c55e');
function capaRelieve(fc) {
  return L.geoJSON(fc, {
    style: (f) => ({ color: colorRelieve(f.properties.relief_m), weight: 4, opacity: 0.9 }),
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Arista', `${f.properties.source_code} → ${f.properties.target_code}`],
      ['Terreno mín / máx', `${f.properties.terrain_min_m} / ${f.properties.terrain_max_m} m s.n.m.`],
      ['Desnivel del relieve', `${f.properties.relief_m} m`],
      ['Subida / bajada acumulada', `${f.properties.ascent_m} / ${f.properties.descent_m} m`],
    ])),
  });
}

const colorDensidad = (d) => (d >= 40000 ? '#7f1d1d' : d >= 20000 ? '#b91c1c' :
  d >= 5000 ? '#f97316' : d >= 1000 ? '#facc15' : '#bbf7d0');
function capaManzanas(fc) {
  return L.geoJSON(fc, {
    style: (f) => ({ color: '#334155', weight: 0.5, fillColor: colorDensidad(f.properties.density_hab_km2 ?? 0), fillOpacity: 0.7 }),
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Manzana', f.properties.manzent],
      ['Comuna / distrito', `${f.properties.commune} / ${f.properties.district}`],
      ['Personas (Censo 2017)', f.properties.persons],
      ['Viviendas', f.properties.dwellings],
      ['Densidad', fmt(f.properties.density_hab_km2) && `${fmt(f.properties.density_hab_km2)} hab/km²`],
    ])),
  });
}

function capaAntenas(fc) {
  const grupo = L.layerGroup();
  const popup = (p) => tabla([
    ['Antena', p.name ?? p.osm_id],
    ['Operador', p.operator],
    ['Estructura', p.structure],
    ['Altura', p.height_m == null ? null : `${p.height_m} m`],
    ['Radio de cobertura', `${p.coverage_radius_m} m (supuesto)`],
  ]);
  L.geoJSON(fc, { style: { color: '#2563eb', weight: 1, fillColor: '#3b82f6', fillOpacity: 0.12 } })
    .eachLayer((l) => { l.bindPopup(popup(l.feature.properties)); grupo.addLayer(l); });
  fc.features.forEach((f) => grupo.addLayer(
    L.circleMarker([f.properties.lat, f.properties.lon],
      { radius: 4, color: '#1e3a8a', fillColor: '#60a5fa', fillOpacity: 1 })
      .bindPopup(popup(f.properties))));
  return grupo;
}

// Amenazas: todas son polígonos con `exceeds` (zona activa)
function capaAmenaza(fc, estilo, filas) {
  return L.geoJSON(fc, {
    style: (f) => estilo(f.properties),
    onEachFeature: (f, l) => l.bindPopup(tabla(filas(f.properties))),
  });
}

const capaIncendios = (fc) => capaAmenaza(fc,
  (p) => (p.exceeds
    ? { color: '#b91c1c', weight: 2, fillColor: '#ef4444', fillOpacity: 0.5 }
    : { color: '#f97316', weight: 1, dashArray: '4 4', fillColor: '#fdba74', fillOpacity: 0.2 }),
  (p) => [
    ['Tipo', 'Incendio (foco satelital)'],
    ['Potencia radiativa (FRP)', `${p.value} MW`],
    ['Instrumento', p.instrument],
    ['Confianza', p.confidence],
    ['Hora (UTC)', p.observed_at],
    ['Zona activa', bloquea(p)],
  ]);

const capaSismos = (fc) => capaAmenaza(fc,
  (p) => (p.exceeds
    ? { color: '#7e22ce', weight: 2, fillColor: '#a855f7', fillOpacity: 0.25 }
    : { color: '#2563eb', weight: 1, dashArray: '4 4', fillColor: '#93c5fd', fillOpacity: 0.12 }),
  (p) => [
    ['Tipo', 'Sismo'],
    ['Magnitud', p.value],
    ['Profundidad', `${p.depth_km} km`],
    ['Región', p.region],
    ['Autoría', p.authority],
    ['Radio de afectación', `${p.affect_radius_km} km`],
    ['Distancia a la base', `${p.distance_to_base_km} km`],
    ['Base dentro del radio', si(p.base_dentro_radio)],
    ['Zona activa', bloquea(p)],
  ]);

const capaViento = (fc) => capaAmenaza(fc,
  (p) => ({
    color: p.exceeds ? '#b91c1c' : '#16a34a', weight: 1,
    fillColor: p.exceeds ? '#ef4444' : '#4ade80', fillOpacity: 0.25,
  }),
  (p) => [
    ['Ráfaga 10 m', `${p.value} m/s`],
    ['Viento 10 m', `${p.wind_speed_10m} m/s (dirección ${p.wind_direction_10m}°)`],
    ['Viento 120 m', `${p.wind_speed_120m} m/s`],
    ['Umbral', `${p.threshold} m/s`],
    ['Hora (UTC)', p.observed_at],
    ['Zona activa', bloquea(p)],
  ]);

const capaLluvia = (fc) => capaAmenaza(fc,
  (p) => ({
    color: p.exceeds ? '#1e3a8a' : '#0284c7', weight: 1,
    fillColor: p.exceeds ? '#1d4ed8' : '#7dd3fc', fillOpacity: 0.3,
  }),
  (p) => [
    ['Precipitación próxima hora', `${p.value} mm/h`],
    ['Umbral', `${p.threshold} mm/h`],
    ['Válido', `${p.observed_at} → ${p.valid_until}`],
    ['Condición', p.symbol_code],
    ['Zona activa', bloquea(p)],
  ]);

// ---------- ruta pgr_dijkstra ----------
const rutaLayer = L.layerGroup();
let rutas = [];

function mostrarRuta(i) {
  rutaLayer.clearLayers();
  const f = rutas[i];
  const p = f.properties;
  const linea = L.geoJSON(f, { style: { color: '#f97316', weight: 6, opacity: 0.9 } }).addTo(rutaLayer);
  const [lon0, lat0] = f.geometry.coordinates[0];
  const [lon1, lat1] = f.geometry.coordinates.at(-1);
  L.circleMarker([lat0, lon0], { radius: 8, color: '#065f46', weight: 2, fillColor: '#10b981', fillOpacity: 1 })
    .bindTooltip('Origen: Aeródromo de Quintero').addTo(rutaLayer);
  L.circleMarker([lat1, lon1], { radius: 8, color: '#7c2d12', weight: 2, fillColor: '#fb923c', fillOpacity: 1 })
    .bindTooltip(`Destino: ${esc(p.destino_nombre)}`).addTo(rutaLayer);
  mapa.fitBounds(linea.getBounds(), { padding: [40, 40] });

  document.getElementById('ruta-info').innerHTML = [
    ['Origen', 'Aeródromo de Quintero'],
    ['Destino', p.destino_nombre],
    ['Longitud', km(p.longitud_m)],
    ['Costo (= longitud)', `${fmt(p.costo)} m`],
    ['Tramos', p.tramos],
    ['Nodos en la ruta', p.nodos],
  ].map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');
}

// ---------- panel: resumen y leyenda ----------
function mostrarResumen(d) {
  const F = (clave) => d[clave]?.features ?? [];
  const suma = (lista, campo) => lista.reduce((s, f) => s + (f.properties[campo] || 0), 0);
  const activas = (lista) => `${lista.filter((f) => f.properties.exceeds).length} / ${lista.length}`;
  const mediciones = F('aire').reduce((s, f) => s + f.properties.measurements.length, 0);

  const filas = [
    ['Nodos de la red', F('nodos').length],
    ['Aristas', `${F('aristas').length} (${(suma(F('aristas'), 'length_m') / 1000).toFixed(1)} km)`],
    ['Zonas urbanas', F('zonas').length],
    ['Estaciones SINCA / mediciones', `${F('aire').length} / ${mediciones}`],
    ['Perfiles de relieve', F('relieve').length],
    ['Manzanas / personas (INE)', `${fmt(F('manzanas').length)} / ${fmt(suma(F('manzanas'), 'persons'))}`],
    ['Antenas con cobertura', F('antenas').length],
    ['Incendios activos (zona activa / total)', activas(F('incendios'))],
    ['Sismos (zona activa M ≥ 5 / total)', activas(F('sismos'))],
    ['Celdas de viento sobre umbral', activas(F('viento'))],
    ['Celdas de lluvia sobre umbral', activas(F('lluvia'))],
  ];
  document.getElementById('resumen').innerHTML = filas
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');

  const conteo = {};
  F('nodos').forEach((f) => { conteo[f.properties.category] = (conteo[f.properties.category] || 0) + 1; });
  document.getElementById('leyenda').innerHTML = Object.keys(COLOR_CATEGORIA)
    .filter((c) => conteo[c])
    .map((c) => `<li><span class="punto" style="background:${COLOR_CATEGORIA[c]}"></span>` +
      `${esc(NOMBRE_CATEGORIA[c])} <b>${conteo[c]}</b></li>`).join('');
}

// ---------- arranque ----------
async function iniciar() {
  const claves = Object.keys(FUENTES);
  const resultados = await Promise.allSettled(claves.map((c) => cargar(FUENTES[c])));
  const d = {};
  const fallas = [];
  resultados.forEach((r, i) => (r.status === 'fulfilled'
    ? (d[claves[i]] = r.value)
    : fallas.push(`${claves[i]} (${r.reason.message})`)));

  // Cada capa se crea solo si su dato cargó; si no, queda un grupo vacío.
  const crear = (clave, constructor) => (d[clave] ? constructor(d[clave]) : L.layerGroup());
  const overlays = {
    'Infraestructura · Aristas': [crear('aristas', capaAristas), false],
    'Infraestructura · Nodos': [crear('nodos', capaNodos), true],
    'Infraestructura · Zonas urbanas': [crear('zonas', capaZonas), true],
    'Metadata · Calidad del aire (SINCA)': [crear('aire', capaAire), true],
    'Metadata · Relieve por arista (SRTM)': [crear('relieve', capaRelieve), false],
    'Metadata · Población por manzana (INE)': [crear('manzanas', capaManzanas), false],
    'Metadata · Cobertura de antenas (OSM)': [crear('antenas', capaAntenas), false],
    'Amenaza · Incendios (NASA FIRMS)': [crear('incendios', capaIncendios), true],
    'Amenaza · Sismos (EMSC / CSN)': [crear('sismos', capaSismos), true],
    'Amenaza · Viento (Open-Meteo)': [crear('viento', capaViento), false],
    'Amenaza · Lluvia (MET Norway)': [crear('lluvia', capaLluvia), false],
    'Ruta pgr_dijkstra (peor caso)': [rutaLayer, true],
  };
  const control = {};
  Object.entries(overlays).forEach(([nombre, [grupo, activa]]) => {
    control[nombre] = grupo;
    if (activa) grupo.addTo(mapa);
  });
  L.control.layers(capasBase, control, { collapsed: true, position: 'topright' }).addTo(mapa);

  // Selector de ruta: por defecto, la de mayor longitud (la más larga de la base a SINCA)
  rutas = d.rutas?.features ?? [];
  const select = document.getElementById('destino');
  select.innerHTML = rutas.map((f, i) =>
    `<option value="${i}">${esc(f.properties.destino_nombre)} (${km(f.properties.longitud_m)})</option>`).join('');
  select.addEventListener('change', () => mostrarRuta(Number(select.value)));
  if (rutas.length) {
    const mayor = rutas.reduce((mejor, f, i) =>
      (f.properties.longitud_m > rutas[mejor].properties.longitud_m ? i : mejor), 0);
    select.value = String(mayor);
    mostrarRuta(mayor);
  }

  mostrarResumen(d);
  document.getElementById('estado').textContent = fallas.length
    ? `Sin cargar: ${fallas.join('; ')}`
    : `Todas las fuentes cargadas (${claves.length}).`;
}

iniciar();
