// =============================================================================
// Plataforma de Ruteo Resiliente UAV · Bahía de Quintero – Puchuncaví
// Algoritmo: K-caminos disimilares mediante penalización iterativa de aristas
// (Akgün, Erkut & Batta, 2000, European Journal of Operational Research 121(2): 232-246),
// inspirado en el Global Path Planner (GPP) de Kosior, Przystałka y Panfil (2024),
// Applied Sciences 14(24), 12065. DOI: 10.3390/app142412065.
// =============================================================================

const FUENTES = {
  nodos: '../infraestructura/nodos.geojson',
  aristas: '../infraestructura/aristas.geojson',
  zonas: '../infraestructura/zonas_urbanas.geojson',
  aire: '../metadata/sinca_calidad_aire.geojson',
  relieve: '../metadata/srtm_relieve.geojson',
  manzanas: '../metadata/ine_manzanas.geojson',
  antenas: '../metadata/osm_antenas.geojson',
  obstaculos: '../metadata/osm_obstaculos.geojson',
  incendios: '../amenazas/firms_incendios.geojson',
  aeronaves: '../amenazas/opensky_aeronaves.geojson',
  sismos: '../amenazas/opensky_aeronaves.geojson',
  viento: '../amenazas/openmeteo_viento.geojson',
  niebla: '../amenazas/openmeteo_niebla.geojson',
  lluvia: '../amenazas/openmeteo_niebla.geojson',
  rutas_pgrouting: 'data/ruta_dijkstra.geojson',
  rutas_comparativas: 'data/rutas_comparativas.geojson',
  resumen_resiliencia: 'data/resumen_resiliencia.json',
  parametros: '../config/parametros.json',
  traza_urbana: 'data/traza_urbana_quebradas.geojson',
};

const COLOR_CATEGORIA = {
  base: '#15803d',            // Verde bosque aeronáutico
  sinca: '#0369a1',           // Cerúleo / azul marino (estaciones ambientales)
  emission_source: '#b91c1c', // Carmesí oscuro (fuentes industriales)
  health: '#be185d',          // Magenta formal (red asistencial)
  education: '#6d28d9',       // Púrpura formal (educación)
  commercial: '#475569',      // Pizarra técnica (comercial)
  crowded_area: '#c2410c',    // Ámbar óxido (densidad poblacional)
  beach: '#0891b2',           // Azul verdoso costero (playas)
  hospitality: '#b45309',     // Bronce (hospedaje)
  restaurant: '#78716c',      // Piedra neutra (gastronomía)
  attraction: '#0f766e',      // Verde azulado (atractivos)
  historic: '#713f12',        // Pardo formal (patrimonio)
  auxiliary_hub: '#334155',   // Carbón (nodos de soporte)
};

const NOMBRE_CATEGORIA = {
  base: 'Base Aérea', sinca: 'Estación SINCA', emission_source: 'Fuente Emisora', health: 'Salud',
  education: 'Educación', commercial: 'Comercial', crowded_area: 'Área Concurrida',
  beach: 'Playa', hospitality: 'Hospedaje', restaurant: 'Restaurante',
  attraction: 'Atractivo', historic: 'Histórico', auxiliary_hub: 'Hub Auxiliar',
};

const ESTILO_BADGE_CATEGORIA = {
  base: { bg: '#dcfce7', text: '#15803d', border: '#86efac' },
  sinca: { bg: '#e0f2fe', text: '#0369a1', border: '#7dd3fc' },
  emission_source: { bg: '#fee2e2', text: '#991b1b', border: '#fca5a5' },
  health: { bg: '#fce7f3', text: '#9d174d', border: '#f472b6' },
  education: { bg: '#ede9fe', text: '#5b21b6', border: '#c4b5fd' },
  commercial: { bg: '#f1f5f9', text: '#334155', border: '#cbd5e1' },
  crowded_area: { bg: '#ffedd5', text: '#9a3412', border: '#fdba74' },
  beach: { bg: '#cffafe', text: '#155e75', border: '#67e8f9' },
  hospitality: { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' },
  restaurant: { bg: '#f5f5f4', text: '#44403c', border: '#d6d3d1' },
  attraction: { bg: '#ccfbf1', text: '#115e59', border: '#5eead4' },
  historic: { bg: '#fef9c3', text: '#713f12', border: '#fde047' },
  auxiliary_hub: { bg: '#f1f5f9', text: '#1e293b', border: '#cbd5e1' },
};

// Utilidades generales de renderizado
const esc = (v) => String(v ?? '—').replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const fila = (k, v) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`;
const tabla = (filas) => `<table class="pop">${filas.map(([k, v]) => fila(k, v)).join('')}</table>`;
const km = (m) => (m == null ? '—' : `${(m / 1000).toFixed(2).replace('.', ',')} km`);
const pct = (p) => (p == null ? '—' : `${Number(p).toFixed(1).replace('.', ',')}%`);
const fmt = (n) => (n == null ? null : Number(n).toLocaleString('es-CL'));
const bloquea = (p) => (p.exceeds ? 'Sí (zona activa)' : 'No');

async function cargar(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// -----------------------------------------------------------------------------
// MAPA BASE LEAFLET (Acotado al área de estudio Quintero – Puchuncaví)
// -----------------------------------------------------------------------------
const BOUNDS_QUINTERO = [
  [-32.84, -71.58], // Suroeste: Base Aérea Quintero / Costa sur
  [-32.68, -71.36], // Noreste: Puchuncaví / Los Maitenes norte
];
const BOUNDS_MAX = [
  [-32.88, -71.64],
  [-32.64, -71.30],
];

const mapa = L.map('mapa', {
  minZoom: 11,
  maxZoom: 18,
  maxBounds: BOUNDS_MAX,
  maxBoundsViscosity: 1.0,
}).fitBounds(BOUNDS_QUINTERO);

// Panel propio para los nodos, sobre zonas, rutas y amenazas (overlayPane = 400),
// para que el clic en un nodo siempre llegue al nodo.
mapa.createPane('nodos').style.zIndex = 450;
const capasBase = {
  'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '&copy; OpenStreetMap',
  }),
  'Satélite (Esri)': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }),
};
capasBase['OpenStreetMap'].addTo(mapa);

// Capas vectoriales dinámicas
const layerRutasDijkstra = L.layerGroup().addTo(mapa);
const layerRutasResiliente = L.layerGroup().addTo(mapa);
const layerMarcadoresExtremos = L.layerGroup().addTo(mapa);
const layerEscenarioSimulado = L.layerGroup();
const layerRutaPgrouting = L.layerGroup();
const layerDijkstraAuditoria = L.layerGroup().addTo(mapa);
const layerSimuladorUav = L.layerGroup().addTo(mapa);

// Capas de control de nodos y aristas (controladas por la leyenda rápida inferior)
let layerTodosLosNodos = null;
const layerNodosRuta = L.layerGroup().addTo(mapa);
const layerCostosEnlace = L.layerGroup();
let capaAristasGlobal = null;
let capaZonasGlobal = null;
let ultimosNodosRutaActiva = [];
const VELOCIDAD_CRUCERO_KMH = 54.0; // 15 m/s según estándar operacional DAN 151 DGAC

// Capas de Metadata (solo visualización en mapa)
let capaAireGlobal = null;
let capaRelieveGlobal = null;
let capaManzanasGlobal = null;
let capaAntenasGlobal = null;
let capaObstaculosGlobal = null;
let capaTrazaUrbanaGlobal = null;

// Capas de Amenazas (solo visualización en mapa)
let capaIncendiosGlobal = null;
let capaSismosGlobal = null;
let capaVientoGlobal = null;
let capaLluviaGlobal = null;

// Estado de simulación de vuelo y auditoría de costos Dijkstra
let simulacionVueloActiva = false;
let simulacionTimerId = null;
let marcadorDronSimulado = null;
let rutaDijkstraActiva = null;

// Mapas de vistas secundarias (módulos)
let mapaGrafo = null;
let mapaGrafoInicializado = false;
let mapaInfra = null;
let mapaInfraInicializado = false;
let mapaMeta = null;
let mapaMetaInicializado = false;
let mapaAmenazas = null;
let mapaAmenazasInicializado = false;

// Parámetros unificados (leídos desde config/parametros.json)
let FOCO_SIMULADO = {
  lon: -71.4935,
  lat: -32.7801,
  radio_m: 180.0,
  nombre: 'Escenario de Contingencia: Incendio industrial en Planta Asfaltos Quintero'
};
let LAMBDAS = {
  base: 0.005,
  incendio: 5.0,
  urbana: 0.08,
  aeronave: 0.15,
  sismo: 0.15,
  sin_cobertura: 0.03,
  viento: 0.04,
  niebla: 0.06,
  lluvia: 0.06,
};
let BETA = 1000.0;
let FACTOR_PENALIZACION_P = 4.0;
let ORIGEN_PREDETERMINADO = 'base_scer';

// Estructuras de datos del Grafo en memoria
let grafoNodos = {};      // id -> { code, name, category, coord }
let grafoNodosPorCode = {};
let grafoAristas = [];    // lista de aristas con atributos espaciales
let grafoAdyacencia = {}; // id -> [ { vecino, edge_id, length_m } ]
let datosCargados = {};

// -----------------------------------------------------------------------------
// UTILIDADES GEOMÉTRICAS RÁPIDAS EN JS
// -----------------------------------------------------------------------------
function puntoEnPoligono(px, py, anillo) {
  let dentro = false;
  const n = anillo.length;
  let p1x = anillo[0][0];
  let p1y = anillo[0][1];
  for (let i = 1; i <= n; i++) {
    const p2x = anillo[i % n][0];
    const p2y = anillo[i % n][1];
    if (py > Math.min(p1y, p2y) && py <= Math.max(p1y, p2y) && px <= Math.max(p1x, p2x)) {
      if (p1y !== p2y) {
        const xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
        if (p1x === p2x || px <= xinters) {
          dentro = !dentro;
        }
      }
    }
    p1x = p2x;
    p1y = p2y;
  }
  return dentro;
}

function distPuntoASegmentoM(p1, p2, p) {
  const latRad = p[1] * Math.PI / 180.0;
  const x1 = p1[0] * Math.cos(latRad) * 111320.0, y1 = p1[1] * 110540.0;
  const x2 = p2[0] * Math.cos(latRad) * 111320.0, y2 = p2[1] * 110540.0;
  const px = p[0] * Math.cos(latRad) * 111320.0, py = p[1] * 110540.0;

  const dx = x2 - x1, dy = y2 - y1;
  const L2 = dx * dx + dy * dy;
  if (L2 === 0) return Math.hypot(px - x1, py - y1);
  const t = Math.max(0.0, Math.min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2));
  return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
}

function aristaTocaPoligonos(coordU, coordV, features) {
  if (!features || !features.length) return false;
  for (let step = 0; step <= 4; step++) {
    const t = step / 4.0;
    const mx = coordU[0] + t * (coordV[0] - coordU[0]);
    const my = coordU[1] + t * (coordV[1] - coordU[1]);
    for (let i = 0; i < features.length; i++) {
      const g = features[i].geometry;
      if (g.type === 'Polygon') {
        if (puntoEnPoligono(mx, my, g.coordinates[0])) return true;
      } else if (g.type === 'MultiPolygon') {
        for (let j = 0; j < g.coordinates.length; j++) {
          if (puntoEnPoligono(mx, my, g.coordinates[j][0])) return true;
        }
      }
    }
  }
  return false;
}

// -----------------------------------------------------------------------------
// CONSTRUCCIÓN DEL GRAFO ESPACIAL
// -----------------------------------------------------------------------------
function inicializarGrafo(d) {
  grafoNodos = {};
  grafoNodosPorCode = {};
  d.nodos.features.forEach(f => {
    const props = f.properties;
    const item = {
      id: props.id,
      code: props.code,
      name: props.name,
      category: props.category,
      city: props.city,
      coord: f.geometry.coordinates,
    };
    grafoNodos[props.id] = item;
    grafoNodosPorCode[props.code] = item;
    grafoAdyacencia[props.id] = [];
  });

  const manzanasDensas = d.manzanas.features.filter(f => (f.properties.density_hab_km2 || 0) > 2500);
  const antenas = d.antenas.features;
  const incendios = d.incendios.features.filter(f => f.properties.exceeds);
  const aeronaves = (d.aeronaves || d.sismos).features.filter(f => f.properties.exceeds);
  const vientoActivo = (d.viento?.features || []).filter(f => f.properties.exceeds);
  const nieblaActiva = (d.niebla || d.lluvia)?.features?.filter(f => f.properties.exceeds) || [];

  grafoAristas = d.aristas.features.map(f => {
    const props = f.properties;
    const u = props.source;
    const v = props.target;
    const coordU = grafoNodos[u].coord;
    const coordV = grafoNodos[v].coord;
    const length_m = parseFloat(props.length_m);

    const hayIncendio = aristaTocaPoligonos(coordU, coordV, incendios);
    const hayAeronave = aristaTocaPoligonos(coordU, coordV, aeronaves);
    const hayPoblacion = aristaTocaPoligonos(coordU, coordV, manzanasDensas);
    const hayTelecom = aristaTocaPoligonos(coordU, coordV, antenas);
    const hayViento = aristaTocaPoligonos(coordU, coordV, vientoActivo);
    const hayNiebla = aristaTocaPoligonos(coordU, coordV, nieblaActiva);
    const dFoco = distPuntoASegmentoM(coordU, coordV, [FOCO_SIMULADO.lon, FOCO_SIMULADO.lat]);
    const hayEstres = dFoco <= FOCO_SIMULADO.radio_m;

    // Tasa de riesgo física objetiva (Hazard rate por km)
    let hazardRate = LAMBDAS.base; // Tasa base nominal
    if (hayIncendio) hazardRate += LAMBDAS.incendio;
    if (hayPoblacion) hazardRate += LAMBDAS.urbana;
    if (hayAeronave) hazardRate += (LAMBDAS.aeronave || LAMBDAS.sismo);
    if (!hayTelecom) hazardRate += LAMBDAS.sin_cobertura;
    if (hayViento) hazardRate += LAMBDAS.viento;
    if (hayNiebla) hazardRate += (LAMBDAS.niebla || LAMBDAS.lluvia);

    const item = {
      id: props.id,
      source: u,
      target: v,
      length_m,
      coords: f.geometry.coordinates,
      hayIncendio,
      haySismo: hayAeronave,
      hayAeronave,
      hayPoblacion,
      hayTelecom,
      hayViento,
      hayLluvia: hayNiebla,
      hayNiebla,
      hayEstres,
      hazardRate,
    };

    grafoAdyacencia[u].push({ vecino: v, edge_id: props.id, length_m, edgeRef: item });
    grafoAdyacencia[v].push({ vecino: u, edge_id: props.id, length_m, edgeRef: item });

    return item;
  });
}

// -----------------------------------------------------------------------------
// MOTOR REACTIVO DE RUTEO DIJKSTRA Y K-CAMINOS DISIMILARES (AKGÜN ET AL. 2000)
// -----------------------------------------------------------------------------
function dijkstraCamino(origenId, destinoId, getCostoArista, factorPenalizacion, aristasPenalizadas = new Set()) {
  const dist = {};
  const padreNodo = {};
  const padreArista = {};
  const pq = new MinPriorityQueue();

  Object.keys(grafoNodos).forEach(nid => { dist[nid] = Infinity; });

  dist[origenId] = 0;
  pq.push(origenId, 0);

  while (!pq.isEmpty()) {
    const { element: u, priority: dAct } = pq.pop();
    if (dAct > dist[u]) continue;
    if (u === destinoId) break;

    const vecinos = grafoAdyacencia[u] || [];
    for (let i = 0; i < vecinos.length; i++) {
      const v = vecinos[i].vecino;
      const eid = vecinos[i].edge_id;
      const edgeRef = vecinos[i].edgeRef;

      let costo = getCostoArista(edgeRef);
      if (aristasPenalizadas.has(eid)) {
        costo *= factorPenalizacion;
      }

      const nuevaD = dAct + costo;
      if (nuevaD < dist[v]) {
        dist[v] = nuevaD;
        padreNodo[v] = u;
        padreArista[v] = eid;
        pq.push(v, nuevaD);
      }
    }
  }

  if (dist[destinoId] === Infinity) return null;

  const nodos = [];
  const aristas = [];
  let curr = destinoId;
  while (curr !== origenId) {
    nodos.push(curr);
    aristas.push(padreArista[curr]);
    curr = padreNodo[curr];
  }
  nodos.push(origenId);
  nodos.reverse();
  aristas.reverse();

  return { dist: dist[destinoId], nodos, aristas };
}

// Priority Queue ligera
class MinPriorityQueue {
  constructor() { this.heap = []; }
  push(element, priority) {
    this.heap.push({ element, priority });
    this._bubbleUp(this.heap.length - 1);
  }
  pop() {
    const min = this.heap[0];
    const end = this.heap.pop();
    if (this.heap.length > 0) {
      this.heap[0] = end;
      this._sinkDown(0);
    }
    return min;
  }
  isEmpty() { return this.heap.length === 0; }
  _bubbleUp(n) {
    const element = this.heap[n];
    while (n > 0) {
      const pIdx = Math.floor((n - 1) / 2);
      const parent = this.heap[pIdx];
      if (element.priority >= parent.priority) break;
      this.heap[pIdx] = element;
      this.heap[n] = parent;
      n = pIdx;
    }
  }
  _sinkDown(n) {
    const len = this.heap.length;
    const element = this.heap[n];
    while (true) {
      let left = 2 * n + 1;
      let right = 2 * n + 2;
      let swap = null;
      if (left < len && this.heap[left].priority < element.priority) swap = left;
      if (right < len && this.heap[right].priority < (swap === null ? element.priority : this.heap[left].priority)) swap = right;
      if (swap === null) break;
      this.heap[n] = this.heap[swap];
      this.heap[swap] = element;
      n = swap;
    }
  }
}

// -----------------------------------------------------------------------------
// MÉTRICA DE RESILIENCIA PROBABILÍSTICA EXACTA PARA K RUTAS
// -----------------------------------------------------------------------------
function evaluarConfiabilidadConjuntoExacta(aristasK1, aristasK2, aristasMap, incluirEstres) {
  const s1 = new Set(aristasK1);
  const s2 = new Set(aristasK2 || []);
  const ec = new Set([...s1].filter(x => s2.has(x)));
  const e1Only = new Set([...s1].filter(x => !s2.has(x)));
  const e2Only = new Set([...s2].filter(x => !s1.has(x)));
  const enFuego = (e) => e.hayIncendio || (incluirEstres && e.hayEstres);

  function surv(edgeSet) {
    let h = 0.0;
    edgeSet.forEach(eid => {
      const edge = aristasMap[eid];
      if (!edge) return;
      const tasa = edge.hazardRate + (incluirEstres && edge.hayEstres && !edge.hayIncendio ? LAMBDAS.incendio : 0);
      h += tasa * (edge.length_m / 1000.0);
    });
    return Math.exp(-h);
  }

  const Sc = surv(ec);
  const S1 = surv(e1Only);
  const S2 = surv(e2Only);

  // Fórmula exacta de confiabilidad para dos caminos con tramo común E_C:
  // R = S(E_C) * [1 - (1 - S(E_1)) * (1 - S(E_2))]
  const RExacta = Sc * (1.0 - (1.0 - S1) * (1.0 - S2));

  const Sk1 = surv(s1);
  const Sk2 = surv(s2);

  const totalUnion = new Set([...s1, ...s2]);
  const diversidad = totalUnion.size > 0 ? (1.0 - (ec.size / totalUnion.size)) * 100.0 : 0.0;

  const amenazasK1 = new Set();
  s1.forEach(eid => {
    const e = aristasMap[eid];
    if (e) {
      if (enFuego(e)) amenazasK1.add('Incendio');
      if (e.hayPoblacion) amenazasK1.add('Densidad Urbana (DAN 151)');
      if (e.haySismo) amenazasK1.add('Alerta Sísmica');
      if (!e.hayTelecom) amenazasK1.add('Sombra Telecom C2');
    }
  });

  let lK1 = 0, lK2 = 0;
  aristasK1.forEach(eid => { if (aristasMap[eid]) lK1 += aristasMap[eid].length_m; });
  (aristasK2 || []).forEach(eid => { if (aristasMap[eid]) lK2 += aristasMap[eid].length_m; });

  return {
    resilienciaConjuntoPct: RExacta * 100.0,
    supervivenciaK1Pct: Sk1 * 100.0,
    supervivenciaK2Pct: Sk2 * 100.0,
    diversidadPct: diversidad,
    longitudK1M: lK1,
    longitudK2M: lK2,
    amenazasK1: Array.from(amenazasK1),
  };
}

// -----------------------------------------------------------------------------
// RECALCULO REACTIVO Y ACTUALIZACIÓN EN VIVO DEL MAPA
// -----------------------------------------------------------------------------
// Según el informe, el dron sale de la base hacia estaciones de monitoreo y zonas de contaminación.
// El resto de los nodos se pueden elegir para explorar rutas, pero no son puntos de medición.
const DESTINOS_MEDICION = new Set(['sinca', 'emission_source']);

function mostrarAvisoDestino(nodo) {
  const aviso = document.getElementById('aviso-destino');
  if (!aviso) return;
  const esMedicion = DESTINOS_MEDICION.has(nodo.category) || nodo.category === 'base';
  aviso.hidden = esMedicion;
  if (!esMedicion) {
    const cat = NOMBRE_CATEGORIA[nodo.category] || nodo.category;
    aviso.textContent = `${nodo.name} (${cat}) es un nodo de paso, no un punto de medición. ` +
      'La ruta se muestra solo como exploración: la misión real apunta a estaciones SINCA o fuentes emisoras.';
  }
}

// -----------------------------------------------------------------------------
// CONTROL DE EJECUCIÓN DE LA MISIÓN (DIJKSTRA PURO)
// -----------------------------------------------------------------------------
function habilitarEjecucion() {
  const btn = document.getElementById('btn-ejecutar-mision');
  if (btn) {
    btn.disabled = false;
    btn.innerHTML = `<svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Ejecutar Misión</span>`;
  }
}

function ejecutarMision() {
  const selOrigen = document.getElementById('select-origen');
  const selDestino = document.getElementById('select-destino');
  const btnEjecutar = document.getElementById('btn-ejecutar-mision');
  if (!selOrigen || !selDestino || !btnEjecutar) return;

  const origenCode = selOrigen.value;
  const destinoCode = selDestino.value;

  const nodoOrig = grafoNodosPorCode[origenCode];
  const nodoDest = grafoNodosPorCode[destinoCode];

  if (!nodoOrig || !nodoDest) {
    return;
  }

  if (origenCode === destinoCode) {
    alert('El origen y el destino deben ser diferentes.');
    return;
  }

  const aristasMap = {};
  grafoAristas.forEach(e => { aristasMap[e.id] = e; });

  // Costo Dijkstra puro: longitud física en metros
  const costoDijkstra = (edge) => edge.length_m;
  const camino = dijkstraCamino(nodoOrig.id, nodoDest.id, costoDijkstra, 1.0, new Set());

  if (!camino || !camino.nodos || camino.nodos.length < 2) {
    alert('No se encontró una ruta factible entre los nodos seleccionados.');
    return;
  }

  // Limpiar capas previas de rutas
  layerRutasDijkstra.clearLayers();
  layerRutasResiliente.clearLayers();
  layerMarcadoresExtremos.clearLayers();
  layerCostosEnlace.clearLayers();

  // Construir coordenadas precisas del camino
  const coords = [nodoOrig.coord];
  let totalLongitudM = 0;
  for (let i = 0; i < camino.aristas.length; i++) {
    const eid = camino.aristas[i];
    const edge = aristasMap[eid];
    if (edge) {
      totalLongitudM += edge.length_m;
      const eCoords = edge.coords;
      const last = coords[coords.length - 1];
      const dDir = Math.hypot(eCoords[0][0] - last[0], eCoords[0][1] - last[1]);
      const dInv = Math.hypot(eCoords[eCoords.length - 1][0] - last[0], eCoords[eCoords.length - 1][1] - last[1]);
      const seg = dDir <= dInv ? eCoords : [...eCoords].reverse();
      for (let j = 1; j < seg.length; j++) coords.push(seg[j]);
    }
  }

  const latlngs = coords.map(c => [c[1], c[0]]);

  const esBVLOS = totalLongitudM > 500;
  const distKmNum = totalLongitudM / 1000;
  const distKmFmt = distKmNum.toFixed(2).replace('.', ',');
  const legalBadgeHtml = esBVLOS
    ? `<div style="margin-top:6px; padding:5px 8px; background:#fee2e2; border-left:3px solid #dc2626; color:#991b1b; font-size:11px; border-radius:3px; line-height:1.35;">
         <strong style="color:#b91c1c;">Vuelo BVLOS (&gt; 500 m)</strong><br>
         Sobrepasa el límite visual del piloto (DAN 151).<br>
         <strong style="color:#991b1b;">Requiere Autorización Especial DGAC (Chile)</strong>
       </div>`
    : `<div style="margin-top:5px; padding:3px 6px; background:#dcfce7; border-left:3px solid #16a34a; color:#166534; font-size:11px; border-radius:3px;">
         <strong>Régimen:</strong> VLOS (Línea de vista directa &le; 500 m)
       </div>`;

  // Polilínea de la ruta Dijkstra (azul técnico nítido y formal)
  const rutaPolyline = L.polyline(latlngs, {
    color: '#1d4ed8',
    weight: 4.0,
    opacity: 0.95,
  }).bindPopup(`<b>Ruta Planificada</b><br>Distancia: ${distKmFmt} km<br>Saltos: ${camino.aristas.length}${legalBadgeHtml}`)
    .addTo(layerRutasDijkstra);

  mapa.fitBounds(rutaPolyline.getBounds(), { padding: [50, 50] });

  // Marcadores de origen y destino sobrios con borde blanco nítido
  L.circleMarker([nodoOrig.coord[1], nodoOrig.coord[0]], {
    radius: 8, color: '#ffffff', weight: 2, fillColor: '#15803d', fillOpacity: 1
  }).bindTooltip(`Origen: ${nodoOrig.name}`).addTo(layerMarcadoresExtremos);

  L.circleMarker([nodoDest.coord[1], nodoDest.coord[0]], {
    radius: 8, color: '#ffffff', weight: 2, fillColor: '#b91c1c', fillOpacity: 1
  }).bindTooltip(`Destino: ${nodoDest.name}`).addTo(layerMarcadoresExtremos);

  // Badges de costo por enlace
  for (let i = 0; i < camino.aristas.length; i++) {
    const eid = camino.aristas[i];
    const edge = aristasMap[eid];
    const uId = camino.nodos[i];
    const vId = camino.nodos[i + 1];
    const uNode = grafoNodos[uId];
    const vNode = grafoNodos[vId];
    if (edge && uNode && vNode) {
      let midLat = (uNode.coord[1] + vNode.coord[1]) / 2;
      let midLon = (uNode.coord[0] + vNode.coord[0]) / 2;
      if (edge.coords && edge.coords.length >= 2) {
        const cMid = edge.coords[Math.floor(edge.coords.length / 2)];
        midLat = cMid[1];
        midLon = cMid[0];
      }
      const distKm = (edge.length_m / 1000).toFixed(2).replace('.', ',');
      const badgeMarker = L.marker([midLat, midLon], {
        icon: L.divIcon({
          className: 'edge-cost-icon',
          html: `<span class="edge-cost-badge">${distKm} km</span>`,
          iconAnchor: [24, 10],
        }),
        interactive: false,
      });
      badgeMarker.addTo(layerCostosEnlace);
    }
  }

  const checkCosto = document.getElementById('check-costo-enlace');
  if (checkCosto && checkCosto.checked) {
    if (!mapa.hasLayer(layerCostosEnlace)) mapa.addLayer(layerCostosEnlace);
  } else {
    if (mapa.hasLayer(layerCostosEnlace)) mapa.removeLayer(layerCostosEnlace);
  }

  // Actualizar nodos visibles de la ruta
  actualizarVisualizacionNodos(camino.nodos);

  // Cálculos de métricas
  const kmTotales = distKmNum.toFixed(2).replace('.', ',') + ' km';
  const cantSaltos = `${camino.aristas.length} saltos`;
  const cantSaltosFooter = `${camino.aristas.length} saltos`;
  const tiempoSeg = Math.round(distKmNum / (VELOCIDAD_CRUCERO_KMH / 3600));
  const min = Math.floor(tiempoSeg / 60);
  const seg = tiempoSeg % 60;
  const tiempoVuelo = `${min} min ${String(seg).padStart(2, '0')} s`;
  const tiempoMinNum = tiempoSeg / 60;

  // Actualizar métricas
  const setTxt = (id, txt) => {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  };
  setTxt('res-km', kmTotales);
  setTxt('res-tiempo', tiempoVuelo);
  setTxt('res-saltos', cantSaltos);

  // Actualizar origen / destino y modelo de dron en la ventana flotante estilo MATLAB
  const selOrig = document.getElementById('select-origen');
  const selDest = document.getElementById('select-destino');
  const origenTxt = selOrig && selOrig.selectedOptions && selOrig.selectedOptions[0] ? selOrig.selectedOptions[0].textContent : 'Origen';
  const destinoTxt = selDest && selDest.selectedOptions && selDest.selectedOptions[0] ? selDest.selectedOptions[0].textContent : 'Destino';
  setTxt('ventana-origen-lbl', origenTxt);
  setTxt('ventana-destino-lbl', destinoTxt);

  // Actualizar footer inferior del mapa
  setTxt('mapa-footer-km', kmTotales);
  setTxt('mapa-footer-saltos', cantSaltosFooter);
  setTxt('mapa-footer-tiempo', tiempoVuelo);

  // Actualizar evaluación de batería y distancia según modelo de dron en Chile
  actualizarEvaluacionDronFooter(distKmNum, tiempoMinNum);

  // Mostrar ventana flotante de resultados estilo MATLAB y habilitar botón de reapertura en sidebar
  const ventana = document.getElementById('ventana-resultados-uav');
  if (ventana) {
    ventana.style.display = 'block';
    ventana.classList.remove('minimizada');
  }
  const btnAbrirVentana = document.getElementById('btn-abrir-ventana-resultados');
  if (btnAbrirVentana) {
    btnAbrirVentana.style.display = 'flex';
  }

  // Deshabilitar botón de ejecución hasta que haya un cambio
  btnEjecutar.disabled = true;
  btnEjecutar.innerHTML = `<svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg><span>Misión Ejecutada</span>`;
}

// Modelo de UAV homologado único para la misión: DJI Matrice 350 RTK (DGAC DAN 151)
// Altitud de crucero fijada a ~100m AGL sobre el terreno (sin variación vertical por ahora)
const MODELOS_DRON = {
  m350: {
    nombre: 'DJI Matrice 350 RTK',
    tipo: 'Multirotor Industrial (Única Plataforma Operacional)',
    distanciaMaxKm: 32.0,
    tiempoMaxMin: 55,
    bateriaReservaPct: 15, // reserva obligatoria DGAC DAN 151
    altitudFijaM: 100,      // ~100 m AGL fija
  },
};

let ultimaDistanciaKmRuta = null;
let ultimoTiempoMinutosRuta = null;

function actualizarEvaluacionDronFooter(distKm = ultimaDistanciaKmRuta, tiempoMin = ultimoTiempoMinutosRuta) {
  if (distKm != null) ultimaDistanciaKmRuta = distKm;
  if (tiempoMin != null) ultimoTiempoMinutosRuta = tiempoMin;

  const selDron = document.getElementById('select-drone-model');
  const elAlcance = document.getElementById('mapa-footer-alcance');
  const elBateria = document.getElementById('mapa-footer-bateria');
  const resBateria = document.getElementById('res-bateria');
  const resAlcance = document.getElementById('res-alcance');
  const elDronModelo = document.getElementById('ventana-dron-modelo');
  const elDronAltitud = document.getElementById('ventana-dron-altitud');
  const elFooterAltitud = document.getElementById('mapa-footer-altitud');

  const elLegal = document.getElementById('mapa-footer-legal');
  const resLegal = document.getElementById('res-regimen-legal');
  const bannerBvlos = document.getElementById('alerta-bvlos-banner');
  const descBvlos = document.getElementById('alerta-bvlos-desc');

  if (elDronAltitud) elDronAltitud.textContent = '~100 m AGL (fija)';
  if (elFooterAltitud) elFooterAltitud.textContent = '~100 m AGL';

  if (ultimaDistanciaKmRuta == null) {
    if (elAlcance) elAlcance.textContent = '—';
    if (elBateria) elBateria.textContent = '—';
    if (elLegal) elLegal.textContent = '—';
    if (resBateria) resBateria.textContent = '—';
    if (resAlcance) resAlcance.textContent = '—';
    if (resLegal) resLegal.textContent = '—';
    if (bannerBvlos) bannerBvlos.style.display = 'none';
    if (elDronModelo) elDronModelo.textContent = 'DJI Matrice 350 RTK';
    return;
  }

  const modeloKey = 'm350';
  const dron = MODELOS_DRON.m350;
  if (elDronModelo) elDronModelo.textContent = dron.nombre;

  // 1. Evaluación de Alcance / Distancia
  const distRuta = ultimaDistanciaKmRuta;
  const distMax = dron.distanciaMaxKm;
  const excedeDistancia = distRuta > distMax;

  let badgeAlcanceHtml = '';
  let txtResAlcance = '';
  if (excedeDistancia) {
    const excesoKm = (distRuta - distMax).toFixed(1).replace('.', ',');
    badgeAlcanceHtml = `<span class="badge-status-danger" title="La ruta (${distRuta.toFixed(1)} km) supera el alcance máximo recomendado de ${distMax} km para ${dron.nombre}. Exceso: +${excesoKm} km">Excede (+${excesoKm} km)</span>`;
    txtResAlcance = `<span class="text-bad">Excede recomendación (+${excesoKm} km)</span>`;
  } else {
    badgeAlcanceHtml = `<span class="badge-status-ok" title="Ruta dentro del rango seguro (${distRuta.toFixed(1)} km de ${distMax} km máx).">Operacional (${distRuta.toFixed(1)} / ${distMax} km)</span>`;
    txtResAlcance = `<span class="text-good">Dentro de rango (${distRuta.toFixed(1)} / ${distMax} km)</span>`;
  }

  // 2. Evaluación de Batería y Tiempo de Vuelo
  const tVueloMin = ultimoTiempoMinutosRuta || 0;
  const tMaxMin = dron.tiempoMaxMin;
  const pctConsumo = (tVueloMin / tMaxMin) * 100;
  const pctRestante = Math.max(0, 100 - pctConsumo);
  const reservaMinima = dron.bateriaReservaPct || 15;

  let badgeBateriaHtml = '';
  let txtResBateria = '';
  if (pctRestante < reservaMinima) {
    badgeBateriaHtml = `<span class="badge-status-danger" title="Batería restante estimada (${pctRestante.toFixed(0)}%) inferior a la reserva mínima obligatoria del ${reservaMinima}% (DAN 151). ¡No alcanza!">Insuficiente (${pctRestante.toFixed(0)}%)</span>`;
    txtResBateria = `<span class="text-bad">Insuficiente (&lt;${reservaMinima}% reserva)</span>`;
  } else if (pctRestante < 30) {
    badgeBateriaHtml = `<span class="badge-status-warning" title="Batería ajustada (${pctRestante.toFixed(0)}% restante). Cumple reserva del ${reservaMinima}%, pero requiere precaución ante viento">Ajustada (${pctRestante.toFixed(0)}%)</span>`;
    txtResBateria = `<span class="text-warning">Ajustada (${pctRestante.toFixed(0)}% restante)</span>`;
  } else {
    badgeBateriaHtml = `<span class="badge-status-ok" title="Batería suficiente: ${pctRestante.toFixed(0)}% restante estimado al aterrizar (Consumo: ${pctConsumo.toFixed(0)}% en ${tVueloMin.toFixed(1)} min)">Alcanza (${pctRestante.toFixed(0)}%)</span>`;
    txtResBateria = `<span class="text-good">Alcanza (${pctRestante.toFixed(0)}% restante)</span>`;
  }

  // 3. Evaluación de Legalidad Aeronáutica (DAN 151 DGAC Chile: Límite VLOS 500 m)
  const LIMITE_VLOS_KM = 0.5; // 500 metros límite visual estándar en Chile
  const esBVLOS = distRuta > LIMITE_VLOS_KM;

  if (esBVLOS) {
    if (resLegal) {
      resLegal.innerHTML = `<span class="badge-status-danger" style="background:#fee2e2; color:#b91c1c; border-color:#fca5a5; font-weight:700;" title="La distancia (${distRuta.toFixed(1)} km) sobrepasa la línea de vista del piloto (máx. 500 m). Requiere Autorización Especial DGAC según DAN 151.">BVLOS: Requiere Autorización Especial DGAC (&gt; 500 m)</span>`;
    }
    if (elLegal) {
      elLegal.innerHTML = `<span class="badge-status-danger" title="Ruta BVLOS (${distRuta.toFixed(1)} km &gt; 500 m): Exige autorización especial emitida por la DGAC bajo la norma DAN 151.">BVLOS (Requiere Autorización DGAC)</span>`;
    }
    if (bannerBvlos) {
      bannerBvlos.style.display = 'flex';
      if (descBvlos) {
        descBvlos.innerHTML = `Esta ruta (<strong>${distRuta.toFixed(1)} km</strong>) sobrepasa el límite legal de línea de vista del piloto (máx. 500 m según DAN 151). Conforme a la legislación aeronáutica de Chile, <strong>requiere Autorización Especial de la DGAC</strong> con análisis de riesgo operacional SORA aprobado y enlace C2 redundante.`;
      }
    }
  } else {
    if (resLegal) {
      resLegal.innerHTML = `<span class="badge-status-ok" style="background:#dcfce7; color:#15803d; border-color:#86efac; font-weight:700;" title="Operación estándar a la vista del operador (&le; 500 m). Cumple norma DAN 151.">VLOS: Operación Estándar a la Vista (&le; 500 m)</span>`;
    }
    if (elLegal) {
      elLegal.innerHTML = `<span class="badge-status-ok" title="Vuelo dentro del alcance visual directo del operador (&le; 500 m). Cumple norma DAN 151.">VLOS (Línea de Vista)</span>`;
    }
    if (bannerBvlos) {
      bannerBvlos.style.display = 'none';
    }
  }

  if (elAlcance) elAlcance.innerHTML = badgeAlcanceHtml;
  if (elBateria) elBateria.innerHTML = badgeBateriaHtml;
  if (resBateria) resBateria.innerHTML = txtResBateria;
  if (resAlcance) resAlcance.innerHTML = txtResAlcance;
}

const actualizarRutasEnVivo = ejecutarMision;

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------
// SELECCIÓN DE ORIGEN Y DESTINO DIRECTA DESDE EL MAPA
// -----------------------------------------------------------------------------
let modoSeleccionOrigen = false;
let modoSeleccionDestino = false;

function activarSeleccionOrigenMapa() {
  desactivarSeleccionDestinoMapa();
  modoSeleccionOrigen = true;
  const banner = document.getElementById('mapa-banner-seleccion-origen');
  if (banner) banner.hidden = false;

  // Forzar activación de todos los nodos en el mapa
  const checkSoloElegidos = document.getElementById('check-solo-nodos-elegidos');
  if (checkSoloElegidos && checkSoloElegidos.checked) {
    checkSoloElegidos.checked = false;
  }
  actualizarVisualizacionNodos();

  // Acercar el mapa lo máximo posible sin dejar fuera ningún nodo
  if (layerTodosLosNodos && layerTodosLosNodos.getBounds && layerTodosLosNodos.getBounds().isValid()) {
    mapa.fitBounds(layerTodosLosNodos.getBounds(), { padding: [30, 30] });
  } else {
    mapa.fitBounds(BOUNDS_MAX, { padding: [30, 30] });
  }

  mapa.getContainer().style.cursor = 'crosshair';
}

function desactivarSeleccionOrigenMapa() {
  modoSeleccionOrigen = false;
  const banner = document.getElementById('mapa-banner-seleccion-origen');
  if (banner) banner.hidden = true;
  if (!modoSeleccionDestino) {
    mapa.getContainer().style.cursor = '';
  }
}

function activarSeleccionDestinoMapa() {
  desactivarSeleccionOrigenMapa();
  modoSeleccionDestino = true;
  const banner = document.getElementById('mapa-banner-seleccion-destino');
  if (banner) banner.hidden = false;

  // Forzar activación de todos los nodos en el mapa
  const checkSoloElegidos = document.getElementById('check-solo-nodos-elegidos');
  if (checkSoloElegidos && checkSoloElegidos.checked) {
    checkSoloElegidos.checked = false;
  }
  actualizarVisualizacionNodos();

  if (layerTodosLosNodos && layerTodosLosNodos.getBounds && layerTodosLosNodos.getBounds().isValid()) {
    mapa.fitBounds(layerTodosLosNodos.getBounds(), { padding: [30, 30] });
  } else {
    mapa.fitBounds(BOUNDS_MAX, { padding: [30, 30] });
  }

  mapa.getContainer().style.cursor = 'crosshair';
}

function desactivarSeleccionDestinoMapa() {
  modoSeleccionDestino = false;
  const banner = document.getElementById('mapa-banner-seleccion-destino');
  if (banner) banner.hidden = true;
  if (!modoSeleccionOrigen) {
    mapa.getContainer().style.cursor = '';
  }
}

function procesarClickEnNodo(nodoProp) {
  if (modoSeleccionOrigen) {
    // Solo disponibles: Base Aérea SCER o Estaciones SINCA
    const esOrigenValido = (nodoProp.category === 'base' || nodoProp.category === 'sinca');
    if (esOrigenValido) {
      const selOrigen = document.getElementById('select-origen');
      if (selOrigen) {
        selOrigen.value = nodoProp.code;
        desactivarSeleccionOrigenMapa();
        habilitarEjecucion();
      }
    } else {
      alert(`El nodo "${nodoProp.name}" (${NOMBRE_CATEGORIA[nodoProp.category] || nodoProp.category}) no es un punto de despegue autorizado.\n\nSolo se permite despegar desde la Base Aérea SCER o las estaciones SINCA.`);
    }
    return;
  }

  if (modoSeleccionDestino) {
    const selDestino = document.getElementById('select-destino');
    if (selDestino) {
      selDestino.value = nodoProp.code;
      desactivarSeleccionDestinoMapa();
      habilitarEjecucion();
    }
    return;
  }

  // Comportamiento normal: seleccionar destino
  const selDestino = document.getElementById('select-destino');
  if (selDestino) {
    selDestino.value = nodoProp.code;
    habilitarEjecucion();
  }
}

window.fijarDestinoDesdeMapa = function(code) {
  const selDestino = document.getElementById('select-destino');
  if (selDestino) {
    selDestino.value = code;
    desactivarSeleccionDestinoMapa();
    habilitarEjecucion();
    mapa.closePopup();
  }
};

window.fijarOrigenDesdeMapa = function(code) {
  const selOrigen = document.getElementById('select-origen');
  if (selOrigen) {
    selOrigen.value = code;
    desactivarSeleccionOrigenMapa();
    habilitarEjecucion();
    mapa.closePopup();
  }
};

function crearPopupNodo(p) {
  const esOrigenValido = (p.category === 'base' || p.category === 'sinca');
  const catNom = NOMBRE_CATEGORIA[p.category] ?? p.category;
  const col = COLOR_CATEGORIA[p.category] ?? '#64748b';
  return `
    <div class="nodo-popup-card">
      <div class="nodo-popup-header">
        <span class="nodo-popup-cat-badge" style="background:${col};"></span>
        <strong class="nodo-popup-title">${esc(p.name)}</strong>
      </div>
      <table class="pop">
        <tr><th>Categoría</th><td>${esc(catNom)}</td></tr>
        <tr><th>Código</th><td><code>${esc(p.code)}</code></td></tr>
        ${p.city ? `<tr><th>Comuna</th><td>${esc(p.city)}</td></tr>` : ''}
      </table>
      <div class="nodo-popup-actions">
        <button type="button" class="btn-popup-set btn-popup-set-dest" onclick="window.fijarDestinoDesdeMapa('${esc(p.code)}')">
          <svg class="ui-icon ui-icon-xs" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
          <span>Fijar como Destino</span>
        </button>
        ${esOrigenValido ? `
        <button type="button" class="btn-popup-set btn-popup-set-orig" onclick="window.fijarOrigenDesdeMapa('${esc(p.code)}')">
          <svg class="ui-icon ui-icon-xs" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span>Fijar como Origen</span>
        </button>
        ` : ''}
      </div>
    </div>
  `;
}

// -----------------------------------------------------------------------------
// CONTROL DINÁMICO DE VISUALIZACIÓN DE NODOS EN EL MAPA
// -----------------------------------------------------------------------------
function actualizarVisualizacionNodos(nodosIds) {
  if (nodosIds && Array.isArray(nodosIds)) {
    ultimosNodosRutaActiva = nodosIds;
  }
  const checkSoloElegidos = document.getElementById('check-solo-nodos-elegidos');
  const soloElegidos = checkSoloElegidos ? checkSoloElegidos.checked : true;

  if (soloElegidos) {
    if (layerTodosLosNodos && mapa.hasLayer(layerTodosLosNodos)) {
      mapa.removeLayer(layerTodosLosNodos);
    }
    if (!mapa.hasLayer(layerNodosRuta)) {
      mapa.addLayer(layerNodosRuta);
    }
    layerNodosRuta.clearLayers();

    const origenVal = document.getElementById('select-origen')?.value;
    const destinoVal = document.getElementById('select-destino')?.value;

    const listaNodos = ultimosNodosRutaActiva || [];
    listaNodos.forEach(nid => {
      const nodo = grafoNodos[nid];
      if (!nodo || !nodo.coord) return;
      if (nodo.code === origenVal || nodo.code === destinoVal) return;

      const marker = L.circleMarker([nodo.coord[1], nodo.coord[0]], {
        pane: 'nodos',
        radius: nodo.category === 'sinca' ? 6.5 : 4.5,
        color: '#ffffff',
        weight: 1.2,
        fillColor: COLOR_CATEGORIA[nodo.category] ?? '#1d4ed8',
        fillOpacity: 0.95,
      });

      marker.bindTooltip(nodo.name, { direction: 'top', offset: [0, -5] });
      marker.bindPopup(crearPopupNodo(nodo));

      marker.on('click', () => {
        procesarClickEnNodo(nodo);
      });

      marker.addTo(layerNodosRuta);
    });
  } else {
    layerNodosRuta.clearLayers();
    if (layerTodosLosNodos && !mapa.hasLayer(layerTodosLosNodos)) {
      mapa.addLayer(layerTodosLosNodos);
    }
  }
}

// -----------------------------------------------------------------------------
// CONSTRUCCIÓN DE CAPAS CARTOGRÁFICAS RESTAURADAS
// -----------------------------------------------------------------------------
function capaAmenaza(fc, estilo, filas) {
  return L.geoJSON(fc, {
    style: (f) => estilo(f.properties),
    onEachFeature: (f, l) => l.bindPopup(tabla(filas(f.properties))),
  });
}

function inicializarCapasCartograficas(d) {
  // 1. Capa Aristas
  const capaAristas = L.geoJSON(d.aristas, {
    style: { color: '#94a3b8', weight: 1.2, opacity: 0.6 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Arista ID', f.properties.id],
      ['Origen → Destino', `${f.properties.source} → ${f.properties.target}`],
      ['Longitud', `${f.properties.length_m} m`],
    ])),
  });
  capaAristasGlobal = capaAristas;

  // 2. Capa Nodos clasificados
  const capaNodos = L.geoJSON(d.nodos, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      pane: 'nodos',
      radius: f.properties.category === 'base' ? 7.5 : (f.properties.category === 'sinca' ? 6.5 : 4.5),
      color: '#ffffff', weight: 1.2,
      fillColor: COLOR_CATEGORIA[f.properties.category] ?? '#64748b', fillOpacity: 0.95,
    }),
    onEachFeature: (f, l) => {
      l.bindPopup(crearPopupNodo(f.properties));
      l.on('click', (e) => {
        const selOrigen = document.getElementById('select-origen');
        if (e.originalEvent.shiftKey) {
          const esOrigenValido = (f.properties.category === 'base' || f.properties.category === 'sinca');
          if (esOrigenValido && selOrigen) {
            selOrigen.value = f.properties.code;
            habilitarEjecucion();
          }
        } else {
          procesarClickEnNodo(f.properties);
        }
      });
    },
  });
  layerTodosLosNodos = capaNodos;

  // 3. Zonas urbanas (Mapeo)
  const capaZonas = L.geoJSON(d.zonas, {
    style: { color: '#0369a1', weight: 1.4, fillColor: '#0284c7', fillOpacity: 0.08 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Zona Urbana', f.properties.name || f.properties.nombre || 'Área urbana'],
    ])),
  });
  capaZonasGlobal = capaZonas;

  // 4. Calidad del aire (SINCA) con mediciones
  const capaAire = L.geoJSON(d.aire, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      radius: 8, color: '#0f172a', weight: 2, fillColor: '#f59e0b', fillOpacity: 0.95,
    }),
    onEachFeature: (f, l) => {
      const p = f.properties;
      const mediciones = (p.measurements || []).map(m => `${m.parameter}: ${m.value} ${m.unit}`).join('<br>') || 'Sin mediciones';
      l.bindPopup(tabla([
        ['Estación SINCA', p.name],
        ['Código', p.code],
        ['Rol Operacional', 'Valor de la Misión: Prioridad de muestreo R(d) (no penaliza aristas)'],
        ['Referencia de superficie', 'Base de comparación para sensores del dron'],
        ['Mediciones recientes', mediciones],
      ]));
    },
  });

  // 5. Relieve SRTM por arista
  const capaRelieve = L.geoJSON(d.relieve, {
    style: (f) => ({
      color: (f.properties.slope_pct || 0) > 15 ? '#b91c1c' : '#3b82f6',
      weight: 2, opacity: 0.7,
    }),
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Arista', f.properties.edge_id],
      ['Rol Operacional', 'Verificación Techo 120m AGL (DAN 151) y Consumo EEE de Ascenso'],
      ['Desnivel (Δh)', `${f.properties.delta_h_m ?? '—'} m`],
      ['Pendiente', `${f.properties.slope_pct ?? '—'} %`],
      ['Elevación máx', `${f.properties.elevation_max_m ?? '—'} m`],
    ])),
  });

  // 6. Manzanas censales INE
  const capaManzanas = L.geoJSON(d.manzanas, {
    style: (f) => {
      const dHab = f.properties.density_hab_km2 || 0;
      const color = dHab > 2500 ? '#ea580c' : '#22c55e';
      return { color, weight: 0.8, fillColor: color, fillOpacity: 0.25 };
    },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Manzana INE (Censo 2017)', f.properties.block_id || f.properties.manzent],
      ['Población', `${fmt(f.properties.persons)} hab`],
      ['Densidad', `${fmt(f.properties.density_hab_km2)} hab/km²`],
      ['Rol Operacional', 'Riesgo en Tierra (SORA) - Penalizar aristas sobrevoladas'],
      ['Restricción DAN 151', (f.properties.density_hab_km2 || 0) > 2500 ? 'Área residencial densa (penalización severa)' : 'Área de baja densidad (despejada)'],
    ])),
  });

  // 7. Cobertura de antenas OSM (Mástil con radiobases y círculo de alcance C2)
  const capaAntenas = L.featureGroup();
  if (d.antenas && d.antenas.features) {
    d.antenas.features.forEach(f => {
      const p = f.properties;
      const radioM = p.coverage_radius_m || 3000;
      const poly = L.geoJSON(f, {
        style: { color: '#7c3aed', weight: 1.2, fillColor: '#8b5cf6', fillOpacity: 0.08, dashArray: '4 4' }
      });
      poly.bindPopup(tabla([
        ['Antena C2 (OSM / OpenCelliD)', p.name || 'Mástil de telecomunicaciones'],
        ['Supuesto de Enlace', '4G / LTE (Banda 7/28) a 120m AGL'],
        ['Radio de cobertura', `${radioM} m`],
        ['Rol Operacional', 'Enlace C2 - Penalizar sombra de telemetría'],
      ]));
      poly.addTo(capaAntenas);

      if (p.lat && p.lon) {
        const iconHtml = `
          <div class="antenna-marker-pin" title="Antena C2: ${p.name || 'Radiobase'} (${radioM}m)">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v20"/><path d="m17 7-5 5-5-5"/><path d="M4 12a8 8 0 0 1 16 0"/>
            </svg>
          </div>
        `;
        const marker = L.marker([p.lat, p.lon], {
          icon: L.divIcon({
            className: 'div-icon-antenna',
            html: iconHtml,
            iconSize: [24, 24],
            iconAnchor: [12, 12]
          })
        });
        marker.bindPopup(tabla([
          ['Radiobase C2 (OSM / OpenCelliD)', p.name || 'Mástil Telecom'],
          ['Estructura', p.structure || 'Mástil'],
          ['Supuesto Tecnológico', '4G / LTE (Banda 7/28) a 120 m AGL'],
          ['Radio de Cobertura', `${radioM} m`],
          ['Rol Operacional', 'Enlace C2 - Penalizar tramos fuera de cobertura']
        ]));
        marker.addTo(capaAntenas);
      }
    });
  }

  // 7b. Obstáculos verticales y tendido eléctrico (OSM)
  const capaObstaculos = L.featureGroup();
  if (d.obstaculos && d.obstaculos.features) {
    d.obstaculos.features.forEach(f => {
      const p = f.properties;
      const g = f.geometry;
      const esLinea = g.type === 'LineString';
      if (esLinea) {
        const poly = L.geoJSON(f, {
          style: {
            color: '#f59e0b',
            weight: 3.5,
            opacity: 0.9,
            dashArray: '6 4'
          }
        });
        poly.bindPopup(tabla([
          ['Infraestructura', p.name || 'Línea de Alta Tensión'],
          ['Tipo', 'Línea de Transmisión Eléctrica'],
          ['Tensión', `${p.voltage_kv || '110/220'} kV`],
          ['Radio de Seguridad', `${p.buffer_radius_m || 50} m`],
          ['Peligro aeronáutico', 'Cables tensores e interferencia electromagnética con el compás magnético'],
          ['Acción de Ruteo', p.operational_action === 'bloquear' ? 'Bloqueo Duro (Inhabilita arista)' : 'Penalización por Margen']
        ]));
        poly.addTo(capaObstaculos);
      } else {
        const esChimenea = p.obstacle_type === 'chimney';
        const colorMarker = esChimenea ? '#dc2626' : '#d97706';
        const circleBuffer = L.circle([p.lat, p.lon], {
          radius: p.buffer_radius_m || 100,
          color: colorMarker,
          weight: 1.2,
          dashArray: '3 3',
          fillColor: colorMarker,
          fillOpacity: 0.15
        });
        circleBuffer.bindPopup(tabla([
          ['Zona de Exclusión', `Buffer de seguridad ${p.buffer_radius_m}m`],
          ['Obstáculo', p.name],
          ['Altura', `${p.height_m} m` + (p.height_estimated ? ' (estimada)' : ' (registrada)')],
          ['Acción', p.operational_action === 'bloquear' ? 'Bloqueo Duro' : 'Penalización']
        ]));
        circleBuffer.addTo(capaObstaculos);

        const iconHtml = `
          <div class="obstacle-hazard-badge ${esChimenea ? 'obstacle-chimney' : 'obstacle-tower'}" title="${p.name} (${p.height_m}m)">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v20M8 6h8M6 12h12M4 18h16"/>
            </svg>
            <span>${p.height_m}m</span>
          </div>
        `;
        const marker = L.marker([p.lat, p.lon], {
          icon: L.divIcon({
            className: 'div-icon-obstacle',
            html: iconHtml,
            iconSize: [60, 24],
            iconAnchor: [30, 12]
          })
        });
        marker.bindPopup(tabla([
          ['Obstáculo Físico', p.name],
          ['Tipo de Estructura', p.obstacle_type],
          ['Altura Física', `${p.height_m} m` + (p.height_estimated ? ' (estimada)' : '')],
          ['Techo de Vuelo (DAN 151)', '120 m AGL sobre terreno'],
          ['Impacto Operacional', p.height_m >= 120 ? 'SUPERACIÓN CRÍTICA DEL TECHO DE VUELO' : 'Riesgo de colisión en maniobra'],
          ['Acción de Ruteo', p.operational_action === 'bloquear' ? 'Bloqueo Duro (Inhabilita arista)' : 'Penalización por Margen']
        ]));
        marker.addTo(capaObstaculos);
      }
    });
  }

  // 7c. Quebradas y Planes (Traza Urbana / MINVU / DGA)
  const capaTrazaUrbana = L.geoJSON(d.traza_urbana, {
    style: () => ({
      color: '#0284c7',
      weight: 2.2,
      dashArray: '4 4',
      opacity: 0.85,
    }),
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Cauce / Quebrada', f.properties?.nombre || f.properties?.name || 'Quebrada natural'],
      ['Tipo fluvial', f.properties?.tipo || 'Drenaje natural'],
      ['Comuna', f.properties?.comuna || 'Quintero / Puchuncaví'],
      ['Fuente', f.properties?.fuente || 'Traza Urbana (MINVU / DGA / OSM)'],
      ['Riesgo orográfico', 'Zona de escorrentía y potencial turbulencia térmica'],
    ])),
  });

  // 8. Incendios (NASA FIRMS) con polígono térmico y badge de potencia radiativa
  const capaIncendios = L.featureGroup();
  if (d.incendios && d.incendios.features) {
    d.incendios.features.forEach(f => {
      const p = f.properties;
      const poly = L.geoJSON(f, {
        style: () => (p.exceeds
          ? { color: '#b91c1c', weight: 2, fillColor: '#ef4444', fillOpacity: 0.35 }
          : { color: '#f97316', weight: 1, dashArray: '4 4', fillColor: '#fdba74', fillOpacity: 0.15 })
      });
      poly.bindPopup(tabla([
        ['Tipo', 'Incendio satelital (NASA FIRMS)'],
        ['Potencia (FRP)', `${p.value} MW`],
        ['Instrumento', p.instrument],
        ['Confianza', p.confidence],
        ['Zona activa', bloquea(p)],
      ]));
      poly.addTo(capaIncendios);

      if (p.lat && p.lon) {
        const frpVal = Number(p.value || 0).toFixed(1);
        const iconHtml = `
          <div class="fire-hazard-badge" title="Foco Térmico: ${frpVal} MW (NASA FIRMS)">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
            </svg>
            <span>${frpVal} MW</span>
          </div>
        `;
        const marker = L.marker([p.lat, p.lon], {
          icon: L.divIcon({
            className: 'div-icon-fire',
            html: iconHtml,
            iconSize: [66, 24],
            iconAnchor: [33, 12]
          })
        });
        marker.bindPopup(tabla([
          ['Foco Térmico Satelital', 'NASA FIRMS VIIRS'],
          ['Potencia Radiativa (FRP)', `${frpVal} MW`],
          ['Confianza', p.confidence || 'Nominal'],
          ['Peligro aeronáutico', 'Turbulencia térmica convectiva y visibilidad nula']
        ]));
        marker.addTo(capaIncendios);
      }
    });
  }

  // 9. Tráfico Aéreo Tripulado (OpenSky ADS-B) con cilindro de exclusión y badge de telemetría
  const capaSismos = L.featureGroup();
  const coleccionAeronaves = d.aeronaves || d.sismos;
  if (coleccionAeronaves && coleccionAeronaves.features) {
    coleccionAeronaves.features.forEach(f => {
      const p = f.properties;
      const esAeronave = p.event_type === 'aeronave' || p.callsign;
      const poly = L.geoJSON(f, {
        style: () => (esAeronave
          ? { color: p.exceeds ? '#ea580c' : '#f59e0b', weight: 2, dashArray: '4 4', fillColor: p.exceeds ? '#f97316' : '#fbbf24', fillOpacity: p.exceeds ? 0.25 : 0.08 }
          : (p.exceeds
            ? { color: '#7e22ce', weight: 2, fillColor: '#a855f7', fillOpacity: 0.2 }
            : { color: '#2563eb', weight: 1, dashArray: '4 4', fillColor: '#93c5fd', fillOpacity: 0.1 }))
      });
      poly.bindPopup(tabla(esAeronave ? [
        ['Amenaza', 'Tráfico Aéreo Tripulado (OpenSky ADS-B)'],
        ['Callsign / Matrícula', p.callsign || p.external_id],
        ['ICAO 24-bit', p.icao24 || '—'],
        ['Altitud Barométrica', `${p.baro_altitude_m || p.value} m MSL`],
        ['Velocidad Terrestre', `${p.velocity_ms || 0} m/s (${((p.velocity_ms || 0) * 3.6).toFixed(0)} km/h)`],
        ['Cilindro de Exclusión', `${p.exclusion_radius_m || 1500} m`],
        ['Conflicto / Bloqueo', bloquea(p)],
      ] : [
        ['Tipo', 'Evento Sísmico'],
        ['Magnitud', p.value],
        ['Profundidad', `${p.depth_km} km`],
        ['Radio de afectación', `${p.affect_radius_km} km`],
        ['Zona activa', bloquea(p)],
      ]));
      poly.addTo(capaSismos);

      if (p.lat && p.lon) {
        if (esAeronave) {
          const altVal = Math.round(p.baro_altitude_m || p.value || 0);
          const iconHtml = `
            <div class="aircraft-hazard-badge ${p.exceeds ? 'aircraft-danger' : ''}" title="Aeronave Tripulada: ${p.callsign || 'VFR'} (${altVal}m MSL)">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
              <span>${p.callsign || 'CC-SCER1'} (${altVal}m)</span>
            </div>
          `;
          const marker = L.marker([p.lat, p.lon], {
            icon: L.divIcon({
              className: 'div-icon-aircraft',
              html: iconHtml,
              iconSize: [110, 26],
              iconAnchor: [55, 13]
            })
          });
          marker.bindPopup(tabla([
            ['Aeronave Tripulada', `${p.callsign || 'CC-SCER1'} (${p.icao24 || 'VFR'})`],
            ['Altitud Barométrica', `${altVal} m MSL`],
            ['Velocidad', `${p.velocity_ms || 0} m/s`],
            ['Radio de Protección', `${p.exclusion_radius_m || 1500} m`],
            ['Prioridad Normativa', 'DAN 151 DGAC (Derecho de paso irrestricto)']
          ]));
          marker.addTo(capaSismos);
        } else {
          const magVal = Number(p.value || 0).toFixed(1);
          const iconHtml = `
            <div class="quake-hazard-badge" title="Epicentro Sísmico: M ${magVal}">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 12h5l3-9 4 18 3-9h5"/>
              </svg>
              <span>M ${magVal}</span>
            </div>
          `;
          const marker = L.marker([p.lat, p.lon], {
            icon: L.divIcon({
              className: 'div-icon-quake',
              html: iconHtml,
              iconSize: [58, 24],
              iconAnchor: [29, 12]
            })
          });
          marker.bindPopup(tabla([
            ['Epicentro Sísmico', `Magnitud ${magVal} M_L`],
            ['Profundidad Focal', `${p.depth_km} km`],
            ['Radio de Afectación', `${p.affect_radius_km} km`],
            ['Monitoreo', 'Centro Sismológico Nacional (CSN) / EMSC']
          ]));
          marker.addTo(capaSismos);
        }
      }
    });
  }

  // 10. Viento (Open-Meteo) con grilla 4x4, vector direccional rotado y velocidad en m/s
  const capaViento = L.featureGroup();
  if (d.viento && d.viento.features) {
    d.viento.features.forEach(f => {
      const p = f.properties;
      const poly = L.geoJSON(f, {
        style: () => ({
          color: p.exceeds ? '#dc2626' : '#16a34a',
          weight: 1.5,
          dashArray: '3 3',
          fillColor: p.exceeds ? '#ef4444' : '#22c55e',
          fillOpacity: 0.16,
        })
      });
      poly.bindPopup(tabla([
        ['Tipo', 'Celda Meteorológica (Open-Meteo)'],
        ['Ráfaga 10 m', `${p.value} m/s`],
        ['Viento 10 m', `${p.wind_speed_10m} m/s (${p.wind_direction_10m}°)`],
        ['Viento 120 m', `${p.wind_speed_120m} m/s (${p.wind_direction_120m || p.wind_direction_10m}°)`],
        ['Umbral operacional', `${p.threshold} m/s`],
        ['Zona activa (Bloqueo)', bloquea(p)],
      ]));
      poly.addTo(capaViento);

      if (p.lat && p.lon) {
        const rot = p.wind_direction_10m ?? 0;
        const vel = Number(p.wind_speed_10m || 0).toFixed(1);
        const colorClase = p.exceeds ? 'viento-peligro' : 'viento-seguro';
        const iconHtml = `
          <div class="vector-viento-badge ${colorClase}" title="Viento 10m: ${vel} m/s hacia ${rot}°">
            <svg class="ui-icon-wind-arrow" style="transform: rotate(${rot}deg);" viewBox="0 0 24 24" width="14" height="14">
              <path d="M12 2L19 21L12 17L5 21L12 2Z" fill="currentColor" stroke="none"/>
            </svg>
            <span>${vel} m/s</span>
          </div>
        `;
        const marker = L.marker([p.lat, p.lon], {
          icon: L.divIcon({
            className: 'div-icon-wind',
            html: iconHtml,
            iconSize: [66, 24],
            iconAnchor: [33, 12]
          })
        });
        marker.bindPopup(tabla([
          ['Vector de Viento 10 m', `${vel} m/s`],
          ['Dirección', `${rot}° (hacia donde sopla)`],
          ['Ráfaga máxima', `${p.value} m/s`],
          ['Estado', p.exceeds ? 'Riesgo Crítico (supera umbral)' : 'Operación Nominal Segura']
        ]));
        marker.addTo(capaViento);
      }
    });
  }

  // 11. Niebla Costera y Visibilidad (Open-Meteo) con grilla 4x4 y badge de visibilidad / humedad
  const capaLluvia = L.featureGroup();
  const coleccionNiebla = d.niebla || d.lluvia;
  if (coleccionNiebla && coleccionNiebla.features) {
    coleccionNiebla.features.forEach(f => {
      const p = f.properties;
      const esNiebla = p.event_type === 'niebla' || p.relative_humidity !== undefined;
      const poly = L.geoJSON(f, {
        style: () => (esNiebla
          ? {
            color: p.exceeds ? '#0284c7' : '#0d9488',
            weight: 1.5,
            dashArray: '3 3',
            fillColor: p.exceeds ? '#38bdf8' : '#99f6e4',
            fillOpacity: p.exceeds ? 0.32 : 0.12,
          }
          : {
            color: p.exceeds ? '#1e40af' : '#0284c7',
            weight: 1.5,
            dashArray: '3 3',
            fillColor: p.exceeds ? '#2563eb' : '#38bdf8',
            fillOpacity: 0.20,
          })
      });
      poly.bindPopup(tabla(esNiebla ? [
        ['Amenaza', 'Niebla Costera / Camanchaca (Open-Meteo)'],
        ['Visibilidad Horizontal', `${p.value} m`],
        ['Umbral VMC DAN 151', `${p.threshold} m`],
        ['Humedad Relativa', `${p.relative_humidity || 0}%`],
        ['Nubosidad Baja', `${p.cloud_cover_low || 0}%`],
        ['Condición', p.condition || (p.exceeds ? 'Niebla activa (Restricción DAN 151)' : 'Visibilidad normal')],
        ['Zona activa (Bloqueo)', bloquea(p)],
      ] : [
        ['Precipitación', `${p.value} mm/h`],
        ['Umbral IPx4', `${p.threshold} mm/h`],
        ['Símbolo / Condición', p.symbol_code || 'Normal'],
        ['Zona activa (Bloqueo)', bloquea(p)],
      ]));
      poly.addTo(capaLluvia);

      if (p.lat && p.lon) {
        if (esNiebla) {
          const visVal = Math.round(p.value || 0);
          const iconHtml = `
            <div class="fog-cell-badge ${p.exceeds ? 'fog-danger' : 'fog-normal'}" title="Visibilidad: ${visVal} m | HR: ${p.relative_humidity}%">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 15h18M3 18h14M5 12h14M7 9h10"/>
              </svg>
              <span>${visVal}m (HR ${p.relative_humidity}%)</span>
            </div>
          `;
          const marker = L.marker([p.lat, p.lon], {
            icon: L.divIcon({
              className: 'div-icon-fog',
              html: iconHtml,
              iconSize: [85, 24],
              iconAnchor: [42, 12]
            })
          });
          marker.bindPopup(tabla([
            ['Celda Espacial', p.cell || '4x4'],
            ['Visibilidad en Superficie', `${p.value} m (umbral: ${p.threshold} m)`],
            ['Humedad Relativa', `${p.relative_humidity || 0}%`],
            ['Cobertura Nubosa Baja', `${p.cloud_cover_low || 0}%`],
            ['Condición Atmosférica', p.condition || 'VMC Nominal']
          ]));
          marker.addTo(capaLluvia);
        } else {
          const lluviaVal = Number(p.value || 0).toFixed(1);
          const iconHtml = `
            <div class="rain-cell-badge ${p.exceeds ? 'rain-danger' : 'rain-normal'}" title="Precipitación: ${lluviaVal} mm/h">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/>
                <path d="M16 14v6"/><path d="M8 14v6"/><path d="M12 16v6"/>
              </svg>
              <span>${lluviaVal} mm/h</span>
            </div>
          `;
          const marker = L.marker([p.lat, p.lon], {
            icon: L.divIcon({
              className: 'div-icon-rain',
              html: iconHtml,
              iconSize: [68, 24],
              iconAnchor: [34, 12]
            })
          });
          marker.bindPopup(tabla([
            ['Tasa de Precipitación', `${p.value} mm/h`],
            ['Límite IPx4', `${p.threshold} mm/h`],
            ['Condición', p.symbol_code || 'Sin precipitación']
          ]));
          marker.addTo(capaLluvia);
        }
      }
    });
  }

  // 12. Ruta oficial pgr_dijkstra generada por PostgreSQL
  if (d.rutas_pgrouting && d.rutas_pgrouting.features) {
    L.geoJSON(d.rutas_pgrouting, {
      style: (f) => (f.properties.k === 2
        ? { color: '#fb923c', weight: 2.5, dashArray: '2 6', opacity: 0.8 }
        : { color: '#ea580c', weight: 3, dashArray: '6 6', opacity: 0.8 }),
      onEachFeature: (f, l) => l.bindPopup(tabla([
        ['Ruta de referencia', `pgr_dijkstra en PostgreSQL (k=${f.properties.k})`],
        ['Condición', 'Línea base del peor caso: distancia física métrica sin mitigación de riesgo ni metadata'],
        ['Destino', f.properties.destino_nombre || f.properties.destino],
        ['Longitud', km(f.properties.longitud_m)],
        ['Costo (longitud pura)', `${fmt(Math.round(f.properties.costo))} m`],
        ['Tramos', f.properties.tramos],
      ])),
    }).addTo(layerRutaPgrouting);
  }

  const overlays = {
    'Ruta de referencia — pgr_dijkstra (costo = longitud)': layerRutaPgrouting,
    'Ruta Dijkstra (Peor caso: distancia pura en km)': layerRutasDijkstra,
    'Rutas Resilientes (Akgün et al. 2000: penalización iterativa)': layerRutasResiliente,
    'Escenario de Contingencia (Planta Asfaltos)': layerEscenarioSimulado,
    'Infraestructura · Nodos': capaNodos,
    'Infraestructura · Aristas': capaAristas,
    'Infraestructura · Zonas urbanas': capaZonas,
    'Metadata · Calidad del aire (SINCA)': capaAire,
    'Metadata · Relieve por arista (SRTM)': capaRelieve,
    'Metadata · Manzanas pobladas (INE)': capaManzanas,
    'Metadata · Cobertura antenas (OSM)': capaAntenas,
    'Metadata · Obstáculos físicos y alta tensión (OSM)': capaObstaculos,
    'Metadata · Quebradas (Traza Urbana)': capaTrazaUrbana,
    'Amenaza · Incendios (NASA FIRMS)': capaIncendios,
    'Amenaza · Tráfico Aéreo (OpenSky ADS-B)': capaSismos,
    'Amenaza · Viento (Open-Meteo)': capaViento,
    'Amenaza · Niebla Costera (Open-Meteo)': capaLluvia,
  };

  // Asignar referencias globales de las capas para los checkboxes del panel lateral
  capaAireGlobal = capaAire;
  capaRelieveGlobal = capaRelieve;
  capaManzanasGlobal = capaManzanas;
  capaAntenasGlobal = capaAntenas;
  capaObstaculosGlobal = capaObstaculos;
  capaTrazaUrbanaGlobal = capaTrazaUrbana;
  capaIncendiosGlobal = capaIncendios;
  capaSismosGlobal = capaSismos;
  capaVientoGlobal = capaViento;
  capaLluviaGlobal = capaLluvia;

  // Conectar checkboxes del panel lateral (Solo visualización, no afectan algoritmo ni costo)
  function enlazarCapaVisual(checkId, capa) {
    const chk = document.getElementById(checkId);
    if (!chk) return;
    chk.checked = false; // por defecto apagado
    chk.addEventListener('change', () => {
      if (!capa) return;
      if (chk.checked) {
        if (!mapa.hasLayer(capa)) mapa.addLayer(capa);
      } else {
        if (mapa.hasLayer(capa)) mapa.removeLayer(capa);
      }
    });
  }

  enlazarCapaVisual('check-layer-aire', capaAireGlobal);
  enlazarCapaVisual('check-layer-relieve', capaRelieveGlobal);
  enlazarCapaVisual('check-layer-manzanas', capaManzanasGlobal);
  enlazarCapaVisual('check-layer-antenas', capaAntenasGlobal);
  enlazarCapaVisual('check-layer-obstaculos', capaObstaculosGlobal);
  enlazarCapaVisual('check-layer-traza', capaTrazaUrbanaGlobal);

  enlazarCapaVisual('check-layer-incendios', capaIncendiosGlobal);
  enlazarCapaVisual('check-layer-sismos', capaSismosGlobal);
  enlazarCapaVisual('check-layer-viento', capaVientoGlobal);
  enlazarCapaVisual('check-layer-lluvia', capaLluviaGlobal);

  // Conectar controles de la leyenda rápida del mapa (abajo a la derecha)
  const checkSoloElegidos = document.getElementById('check-solo-nodos-elegidos');
  if (checkSoloElegidos) {
    checkSoloElegidos.addEventListener('change', () => {
      actualizarVisualizacionNodos();
    });
  }

  const checkAristas = document.getElementById('check-ver-aristas');
  if (checkAristas) {
    checkAristas.addEventListener('change', () => {
      if (checkAristas.checked) {
        if (capaAristasGlobal && !mapa.hasLayer(capaAristasGlobal)) {
          mapa.addLayer(capaAristasGlobal);
        }
      } else {
        if (capaAristasGlobal && mapa.hasLayer(capaAristasGlobal)) {
          mapa.removeLayer(capaAristasGlobal);
        }
      }
    });
  }

  const checkCostoEnlace = document.getElementById('check-costo-enlace');
  if (checkCostoEnlace) {
    checkCostoEnlace.addEventListener('change', () => {
      if (checkCostoEnlace.checked) {
        if (!mapa.hasLayer(layerCostosEnlace)) mapa.addLayer(layerCostosEnlace);
      } else {
        if (mapa.hasLayer(layerCostosEnlace)) mapa.removeLayer(layerCostosEnlace);
      }
    });
  }

  const checkMapeo = document.getElementById('check-ver-mapeo');
  if (checkMapeo) {
    checkMapeo.addEventListener('change', () => {
      if (checkMapeo.checked) {
        if (capaZonasGlobal && !mapa.hasLayer(capaZonasGlobal)) {
          mapa.addLayer(capaZonasGlobal);
        }
      } else {
        if (capaZonasGlobal && mapa.hasLayer(capaZonasGlobal)) {
          mapa.removeLayer(capaZonasGlobal);
        }
      }
    });
  }

  const checkOsm = document.getElementById('check-mapa-osm');
  if (checkOsm) {
    checkOsm.addEventListener('change', () => {
      if (checkOsm.checked) {
        if (mapa.hasLayer(capasBase['Satélite (Esri)'])) {
          mapa.removeLayer(capasBase['Satélite (Esri)']);
        }
        if (!mapa.hasLayer(capasBase['OpenStreetMap'])) {
          mapa.addLayer(capasBase['OpenStreetMap']);
        }
      } else {
        if (mapa.hasLayer(capasBase['OpenStreetMap'])) {
          mapa.removeLayer(capasBase['OpenStreetMap']);
        }
        if (!mapa.hasLayer(capasBase['Satélite (Esri)'])) {
          mapa.addLayer(capasBase['Satélite (Esri)']);
        }
      }
    });
  }

  // Visualización inicial: solo nodos de la ruta activa por defecto
  actualizarVisualizacionNodos();
}

// -----------------------------------------------------------------------------
// LEYENDA DESPLEGABLE DE COLORES DE NODOS (ARRIBA A LA DERECHA DEL MAPA)
// -----------------------------------------------------------------------------
function inicializarLeyendaColoresNodos(d) {
  const listaCont = document.getElementById('leyenda-nodos-lista');
  const btnToggle = document.getElementById('btn-toggle-leyenda-nodos');
  const bodyCont = document.getElementById('leyenda-nodos-body');
  const arrow = document.getElementById('leyenda-nodos-arrow');

  if (!listaCont || !btnToggle || !bodyCont) return;

  // Contar cantidad de nodos por categoría
  const conteos = {};
  if (d.nodos && Array.isArray(d.nodos.features)) {
    d.nodos.features.forEach(f => {
      const c = f.properties?.category || 'auxiliary_hub';
      conteos[c] = (conteos[c] || 0) + 1;
    });
  }

  // Lista ordenada de categorías temáticas
  const ordenCategorias = [
    'base', 'sinca', 'emission_source', 'health', 'education',
    'commercial', 'crowded_area', 'beach', 'hospitality',
    'restaurant', 'attraction', 'historic', 'auxiliary_hub',
  ];

  listaCont.innerHTML = ordenCategorias.map(cat => {
    const color = COLOR_CATEGORIA[cat] || '#64748b';
    const nombre = NOMBRE_CATEGORIA[cat] || cat;
    const count = conteos[cat] || 0;
    return `
      <div class="leyenda-nodo-item" title="${esc(nombre)} (${count} nodos en la red)">
        <span class="leyenda-nodo-dot" style="background:${color};"></span>
        <span class="leyenda-nodo-name">${esc(nombre)}</span>
        <span class="leyenda-nodo-count">(${count})</span>
      </div>
    `;
  }).join('');

  // Toggle abrir / cerrar interactivo
  let abierta = true;
  btnToggle.addEventListener('click', () => {
    abierta = !abierta;
    bodyCont.hidden = !abierta;
    btnToggle.setAttribute('aria-expanded', abierta ? 'true' : 'false');
    if (arrow) {
      arrow.style.transform = abierta ? 'rotate(0deg)' : 'rotate(-90deg)';
      arrow.style.transition = 'transform 0.2s ease';
    }
  });
}

// -----------------------------------------------------------------------------
// VENTANA FLOTANTE DRAGGABLE ESTILO MATLAB PARA RESULTADOS DE MISIÓN
// -----------------------------------------------------------------------------
function inicializarVentanaResultadosDraggable() {
  const ventana = document.getElementById('ventana-resultados-uav');
  const header = document.getElementById('ventana-header-drag');
  const btnMinimizar = document.getElementById('btn-minimizar-ventana');
  const btnCerrar = document.getElementById('btn-cerrar-ventana');
  const btnAbrir = document.getElementById('btn-abrir-ventana-resultados');
  const viewport = document.querySelector('.mapa-viewport');

  if (!ventana || !header) return;

  // Botón cerrar (✕)
  if (btnCerrar) {
    btnCerrar.addEventListener('click', (e) => {
      e.stopPropagation();
      ventana.style.display = 'none';
    });
  }

  // Botón minimizar / expandir (_)
  if (btnMinimizar) {
    btnMinimizar.addEventListener('click', (e) => {
      e.stopPropagation();
      const isMin = ventana.classList.toggle('minimizada');
      btnMinimizar.title = isMin ? 'Expandir ventana' : 'Minimizar ventana';
    });
  }

  // Botón en el sidebar para reabrir
  if (btnAbrir) {
    btnAbrir.addEventListener('click', () => {
      ventana.style.display = 'block';
      ventana.classList.remove('minimizada');
      clampingVentana();
    });
  }

  // Lógica de arrastre estilo MATLAB Figure Window
  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let initialLeft = 0;
  let initialTop = 0;

  function clampingVentana() {
    if (!viewport) return;
    const vpRect = viewport.getBoundingClientRect();
    const vRect = ventana.getBoundingClientRect();
    let curLeft = ventana.offsetLeft;
    let curTop = ventana.offsetTop;
    const maxLeft = Math.max(10, vpRect.width - vRect.width - 10);
    const maxTop = Math.max(10, vpRect.height - (ventana.classList.contains('minimizada') ? 45 : vRect.height) - 45);

    if (curLeft > maxLeft) curLeft = maxLeft;
    if (curLeft < 10) curLeft = 10;
    if (curTop > maxTop) curTop = maxTop;
    if (curTop < 10) curTop = 10;

    ventana.style.left = `${curLeft}px`;
    ventana.style.top = `${curTop}px`;
    ventana.style.right = 'auto';
    ventana.style.bottom = 'auto';
  }

  const startDrag = (clientX, clientY, target) => {
    if (target.closest('.btn-ventana-action')) return;
    isDragging = true;
    startX = clientX;
    startY = clientY;
    initialLeft = ventana.offsetLeft;
    initialTop = ventana.offsetTop;
    document.body.style.userSelect = 'none';
  };

  const moveDrag = (clientX, clientY) => {
    if (!isDragging || !viewport) return;
    const dx = clientX - startX;
    const dy = clientY - startY;

    let newLeft = initialLeft + dx;
    let newTop = initialTop + dy;

    const vpRect = viewport.getBoundingClientRect();
    const vRect = ventana.getBoundingClientRect();
    const maxLeft = Math.max(10, vpRect.width - vRect.width - 10);
    const maxTop = Math.max(10, vpRect.height - (ventana.classList.contains('minimizada') ? 45 : vRect.height) - 45);

    newLeft = Math.max(10, Math.min(newLeft, maxLeft));
    newTop = Math.max(10, Math.min(newTop, maxTop));

    ventana.style.left = `${newLeft}px`;
    ventana.style.top = `${newTop}px`;
    ventana.style.right = 'auto';
    ventana.style.bottom = 'auto';
  };

  const stopDrag = () => {
    if (isDragging) {
      isDragging = false;
      document.body.style.userSelect = '';
    }
  };

  // Mouse events
  header.addEventListener('mousedown', (e) => {
    startDrag(e.clientX, e.clientY, e.target);
  });
  window.addEventListener('mousemove', (e) => {
    moveDrag(e.clientX, e.clientY);
  });
  window.addEventListener('mouseup', stopDrag);

  // Touch events (para notebooks táctiles o tablets)
  header.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      startDrag(e.touches[0].clientX, e.touches[0].clientY, e.target);
    }
  }, { passive: true });
  window.addEventListener('touchmove', (e) => {
    if (isDragging && e.touches.length === 1) {
      moveDrag(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });
  window.addEventListener('touchend', stopDrag);
}

// -----------------------------------------------------------------------------
// ARRANQUE DE LA APLICACIÓN
// -----------------------------------------------------------------------------
async function iniciar() {
  const claves = Object.keys(FUENTES);
  const resultados = await Promise.allSettled(claves.map((c) => cargar(FUENTES[c])));
  const d = {};
  const fallas = [];

  resultados.forEach((r, i) => {
    if (r.status === 'fulfilled') {
      d[claves[i]] = r.value;
    } else {
      fallas.push(`${claves[i]} (${r.reason.message})`);
    }
  });
  datosCargados = d;

  if (d.parametros) {
    if (d.parametros.lambdas) LAMBDAS = { ...LAMBDAS, ...d.parametros.lambdas };
    if (d.parametros.algoritmo) {
      if (d.parametros.algoritmo.beta != null) BETA = Number(d.parametros.algoritmo.beta);
      if (d.parametros.algoritmo.factor_penalizacion_p != null) FACTOR_PENALIZACION_P = Number(d.parametros.algoritmo.factor_penalizacion_p);
      if (d.parametros.algoritmo.origen_default) ORIGEN_PREDETERMINADO = d.parametros.algoritmo.origen_default;
    }
    if (d.parametros.contingencia) {
      FOCO_SIMULADO = { ...FOCO_SIMULADO, ...d.parametros.contingencia };
    }
  }

  // Inicializar estructuras de grafo en memoria
  inicializarGrafo(d);

  // Poblar selectores de Origen y Destino con todos los nodos de la red, agrupados por categoría
  const selOrigen = document.getElementById('select-origen');
  const selDestino = document.getElementById('select-destino');

  const categorias = {};
  d.nodos.features.forEach(f => {
    const cat = f.properties.category || 'otros';
    if (!categorias[cat]) categorias[cat] = [];
    categorias[cat].push(f.properties);
  });

  // Opciones completas para Destino (Monitoreo e Inspección)
  let htmlOptionsDestino = '';
  const ordenCategorias = [...new Set([...Object.keys(NOMBRE_CATEGORIA), ...Object.keys(categorias)])];
  ordenCategorias.forEach(cat => {
    if (categorias[cat]) {
      const nombreCat = NOMBRE_CATEGORIA[cat] || cat;
      const etiqueta = DESTINOS_MEDICION.has(cat) ? `${nombreCat} · punto de medición`
        : (cat === 'base' ? nombreCat : `${nombreCat} · nodo de paso`);
      htmlOptionsDestino += `<optgroup label="--- ${etiqueta} ---">`;
      categorias[cat].sort((a, b) => a.name.localeCompare(b.name)).forEach(p => {
        htmlOptionsDestino += `<option value="${p.code}">${p.name} (${p.city || 'Quintero'})</option>`;
      });
      htmlOptionsDestino += `</optgroup>`;
    }
  });

  // Opciones exclusivas para ORIGEN (Base SCER y Estaciones SINCA con nido/hangar)
  let htmlOptionsOrigen = '';
  ['base', 'sinca'].forEach(cat => {
    if (categorias[cat]) {
      const etiqueta = cat === 'base' ? 'Base Aérea Principal (Hangar SCER)' : 'Estaciones SINCA (Nidos Automatizados)';
      htmlOptionsOrigen += `<optgroup label="--- ${etiqueta} ---">`;
      categorias[cat].sort((a, b) => a.name.localeCompare(b.name)).forEach(p => {
        htmlOptionsOrigen += `<option value="${p.code}">${p.name} (${p.city || 'Quintero'})</option>`;
      });
      htmlOptionsOrigen += `</optgroup>`;
    }
  });

  selOrigen.innerHTML = htmlOptionsOrigen;
  selDestino.innerHTML = htmlOptionsDestino;

  selOrigen.value = 'base_scer';
  selDestino.value = 'sinca_puchuncavi';

  // Inicializar capas cartográficas
  inicializarCapasCartograficas(d);

  // Conectar botón de ejecución de la misión
  const btnEjecutar = document.getElementById('btn-ejecutar-mision');
  if (btnEjecutar) {
    btnEjecutar.addEventListener('click', ejecutarMision);
  }

  // Al cambiar origen o destino, habilitar botón para nueva ejecución
  selOrigen.addEventListener('change', habilitarEjecucion);
  selDestino.addEventListener('change', habilitarEjecucion);

  // Inicializar selector avanzado de destino y modos de selección en mapa
  inicializarSelectorDestinoAvanzado(d);

  // Inicializar acordeones de Metadata y Amenazas
  inicializarAcordeonesSidebar();

  // Inicializar leyenda desplegable de colores de nodos (arriba a la derecha)
  inicializarLeyendaColoresNodos(d);

  // Inicializar ventana flotante draggable estilo MATLAB para resultados
  inicializarVentanaResultadosDraggable();

  // Configurar navegación de módulos
  configurarNavegacionModulos(d);

  // Inicializar selector de modelo de dron en footer
  const selDronFooter = document.getElementById('select-drone-model');
  if (selDronFooter) {
    selDronFooter.addEventListener('change', () => {
      actualizarEvaluacionDronFooter();
    });
  }

  // Inicializar módulos del sistema
  inicializarModuloGrafo(d);
  inicializarModuloInfraestructura(d);
  inicializarModuloMetadata(d);
  inicializarModuloAmenazas(d);
  inicializarModuloDocumentacion(d);
  inicializarAuditoriaDijkstra(d);
}

// -----------------------------------------------------------------------------
// SELECTOR DE DESTINO AVANZADO (MODAL INTERACTIVO CON FILTROS Y DISTANCIAS KM)
// -----------------------------------------------------------------------------
let categoriaFiltroDestino = 'todos';
let busquedaDestinoTexto = '';
let ordenDestinoCriterio = 'distancia_asc';
let nodosParaDestino = [];

function abrirModalDestino() {
  const modal = document.getElementById('modal-selector-destino');
  if (!modal) return;

  const selOrigen = document.getElementById('select-origen');
  const origenCode = selOrigen ? selOrigen.value : 'base_scer';
  const nodoOrig = grafoNodosPorCode[origenCode];

  const lblOrigen = document.getElementById('modal-destino-origen-nombre');
  if (lblOrigen) {
    lblOrigen.textContent = nodoOrig ? `${nodoOrig.name} (${nodoOrig.city || 'Quintero'})` : 'Base Aérea SCER';
  }

  // Calcular distancias directas en km desde el origen actual
  nodosParaDestino.forEach(n => {
    if (nodoOrig && nodoOrig.coord && n.coord) {
      const dMetros = L.latLng(nodoOrig.coord[1], nodoOrig.coord[0]).distanceTo(L.latLng(n.coord[1], n.coord[0]));
      n._distKm = dMetros / 1000;
    } else {
      n._distKm = 0;
    }
  });

  renderizarPillsCategoriasDestino();
  renderizarDestinosCards();

  modal.hidden = false;
  const inputBusq = document.getElementById('modal-destino-busqueda');
  if (inputBusq) {
    inputBusq.value = busquedaDestinoTexto;
    setTimeout(() => inputBusq.focus(), 60);
  }
}

function cerrarModalDestino() {
  const modal = document.getElementById('modal-selector-destino');
  if (modal) modal.hidden = true;
}

function renderizarPillsCategoriasDestino() {
  const cont = document.getElementById('modal-pills-container');
  if (!cont) return;

  const selOrigen = document.getElementById('select-origen');
  const origenCode = selOrigen ? selOrigen.value : '';

  // Conteo por categoría (excluyendo el origen actual)
  const conteo = { todos: 0 };
  nodosParaDestino.forEach(n => {
    if (n.code === origenCode) return;
    conteo.todos++;
    conteo[n.category] = (conteo[n.category] || 0) + 1;
  });

  const categorias = [
    { id: 'todos', nombre: 'Todos' },
    { id: 'sinca', nombre: 'Estaciones SINCA' },
    { id: 'emission_source', nombre: 'Fuentes Emisoras' },
    { id: 'health', nombre: 'Salud' },
    { id: 'education', nombre: 'Educación' },
    { id: 'commercial', nombre: 'Comercial' },
    { id: 'crowded_area', nombre: 'Áreas Concurridas' },
    { id: 'beach', nombre: 'Playas' },
    { id: 'hospitality', nombre: 'Hotelería' },
    { id: 'restaurant', nombre: 'Restaurantes' },
    { id: 'attraction', nombre: 'Atracciones' },
    { id: 'historic', nombre: 'Histórico' },
    { id: 'auxiliary_hub', nombre: 'Centros Auxiliares' },
  ];

  cont.innerHTML = categorias
    .filter(cat => cat.id === 'todos' || conteo[cat.id] > 0)
    .map(cat => {
      const activeClass = categoriaFiltroDestino === cat.id ? 'active' : '';
      const dot = cat.id !== 'todos' ? `<span class="punto" style="background:${COLOR_CATEGORIA[cat.id] || '#38bdf8'}; width:7px; height:7px; margin-right:4px;"></span>` : '';
      return `<button type="button" class="modal-pill ${activeClass}" data-cat="${cat.id}">
        ${dot}${cat.nombre} <span style="opacity:0.75; font-size:0.68rem;">(${conteo[cat.id] || 0})</span>
      </button>`;
    }).join('');

  cont.querySelectorAll('.modal-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      categoriaFiltroDestino = btn.getAttribute('data-cat');
      cont.querySelectorAll('.modal-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderizarDestinosCards();
    });
  });
}

function renderizarDestinosCards() {
  const grid = document.getElementById('modal-cards-grid');
  const contador = document.getElementById('modal-destinos-contador');
  if (!grid) return;

  const selOrigen = document.getElementById('select-origen');
  const selDestino = document.getElementById('select-destino');
  const origenCode = selOrigen ? selOrigen.value : '';
  const destinoActual = selDestino ? selDestino.value : '';

  const q = busquedaDestinoTexto.trim().toLowerCase();

  let filtrados = nodosParaDestino.filter(n => {
    if (n.code === origenCode) return false;
    if (categoriaFiltroDestino !== 'todos' && n.category !== categoriaFiltroDestino) return false;
    if (q) {
      const matchName = n.name.toLowerCase().includes(q);
      const matchCode = n.code.toLowerCase().includes(q);
      const matchCity = (n.city || '').toLowerCase().includes(q);
      const matchCat = (NOMBRE_CATEGORIA[n.category] || '').toLowerCase().includes(q);
      if (!matchName && !matchCode && !matchCity && !matchCat) return false;
    }
    return true;
  });

  // Ordenamiento
  if (ordenDestinoCriterio === 'distancia_asc') {
    filtrados.sort((a, b) => a._distKm - b._distKm);
  } else if (ordenDestinoCriterio === 'distancia_desc') {
    filtrados.sort((a, b) => b._distKm - a._distKm);
  } else if (ordenDestinoCriterio === 'nombre_asc') {
    filtrados.sort((a, b) => a.name.localeCompare(b.name));
  }

  if (contador) {
    contador.textContent = `${filtrados.length} destino${filtrados.length === 1 ? '' : 's'} disponible${filtrados.length === 1 ? '' : 's'}`;
  }

  if (filtrados.length === 0) {
    grid.innerHTML = `<div class="placeholder-msg" style="grid-column: 1 / -1; padding: 24px;">
      No se encontraron destinos que coincidan con "${esc(q)}" en la categoría seleccionada.
    </div>`;
    return;
  }

  grid.innerHTML = filtrados.map(n => {
    const isSelected = n.code === destinoActual;
    const isPriority = (n.category === 'sinca' || n.category === 'emission_source');
    const badgeStyle = ESTILO_BADGE_CATEGORIA[n.category] || { bg: '#f1f5f9', text: '#334155', border: '#cbd5e1' };
    const dotColor = COLOR_CATEGORIA[n.category] || '#64748b';
    const catName = NOMBRE_CATEGORIA[n.category] || n.category;
    const distFmt = n._distKm.toFixed(2).replace('.', ',') + ' km';

    return `
      <div class="destino-card ${isSelected ? 'active-dest' : ''}" data-code="${esc(n.code)}">
        <div class="destino-card-top">
          <span class="destino-badge" style="background:${badgeStyle.bg}; color:${badgeStyle.text}; border: 1px solid ${badgeStyle.border};">
            <span class="punto" style="background:${dotColor}; width:6px; height:6px; display:inline-block; border-radius:50%; margin-right:4px;"></span>
            ${esc(catName)}
          </span>
          <span class="destino-distancia" title="Distancia de vuelo directa desde el origen">
            <svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
            <span>${distFmt}</span>${n.distanciaKmDirecta > 0.5 ? '<span class="tag-bvlos-mini" title="Vuelo BVLOS (> 500 m): Requiere Autorización Especial DGAC">BVLOS</span>' : ''}
          </span>
        </div>
        <div class="destino-nombre">${esc(n.name)}</div>
        <div class="destino-comuna">
          <svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
          <span>${esc(n.city || 'Quintero')} &bull; <code>${esc(n.code)}</code></span>
        </div>
        ${isPriority ? `
          <div class="destino-tag-monitoreo">
            <svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span>Objetivo Prioritario de Misión</span>
          </div>` : ''}
      </div>
    `;
  }).join('');

  grid.querySelectorAll('.destino-card').forEach(card => {
    card.addEventListener('click', () => {
      const code = card.getAttribute('data-code');
      if (selDestino && code) {
        selDestino.value = code;
        cerrarModalDestino();
        habilitarEjecucion();

        const nodoDest = grafoNodosPorCode[code];
        if (nodoDest && nodoDest.coord) {
          mapa.panTo([nodoDest.coord[1], nodoDest.coord[0]]);
        }
      }
    });
  });
}

function inicializarSelectorDestinoAvanzado(d) {
  nodosParaDestino = d.nodos.features.map(f => ({
    ...f.properties,
    coord: f.geometry.coordinates,
  }));

  const btnAbrirModal = document.getElementById('btn-abrir-modal-destino');
  const selDestino = document.getElementById('select-destino');
  const btnCerrarModal = document.getElementById('btn-cerrar-modal-destino');
  const btnCancelarModal = document.getElementById('btn-cancelar-modal-destino');
  const modal = document.getElementById('modal-selector-destino');
  const inputBusq = document.getElementById('modal-destino-busqueda');
  const btnClearSearch = document.getElementById('btn-limpiar-busqueda-destino');
  const selOrden = document.getElementById('modal-destino-orden');

  if (btnAbrirModal) btnAbrirModal.addEventListener('click', abrirModalDestino);

  if (selDestino) {
    selDestino.addEventListener('mousedown', (e) => {
      e.preventDefault();
      abrirModalDestino();
    });
    selDestino.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        abrirModalDestino();
      }
    });
  }

  if (btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModalDestino);
  if (btnCancelarModal) btnCancelarModal.addEventListener('click', cerrarModalDestino);

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) cerrarModalDestino();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modal && !modal.hidden) cerrarModalDestino();
      if (modoSeleccionOrigen) desactivarSeleccionOrigenMapa();
    }
  });

  if (inputBusq) {
    inputBusq.addEventListener('input', () => {
      busquedaDestinoTexto = inputBusq.value;
      if (btnClearSearch) btnClearSearch.hidden = !busquedaDestinoTexto;
      renderizarDestinosCards();
    });
  }

  if (btnClearSearch) {
    btnClearSearch.addEventListener('click', () => {
      busquedaDestinoTexto = '';
      if (inputBusq) {
        inputBusq.value = '';
        inputBusq.focus();
      }
      btnClearSearch.hidden = true;
      renderizarDestinosCards();
    });
  }

  if (selOrden) {
    selOrden.addEventListener('change', () => {
      ordenDestinoCriterio = selOrden.value;
      renderizarDestinosCards();
    });
  }

  // Conectar botón para seleccionar origen desde el mapa
  const btnSelOrigenMapa = document.getElementById('btn-seleccionar-origen-mapa');
  if (btnSelOrigenMapa) {
    btnSelOrigenMapa.addEventListener('click', activarSeleccionOrigenMapa);
  }

  const btnCancelBanner = document.getElementById('btn-cancelar-seleccion-origen');
  if (btnCancelBanner) {
    btnCancelBanner.addEventListener('click', desactivarSeleccionOrigenMapa);
  }

  // Conectar botón para seleccionar destino desde el mapa
  const btnSelDestinoMapa = document.getElementById('btn-seleccionar-destino-mapa');
  if (btnSelDestinoMapa) {
    btnSelDestinoMapa.addEventListener('click', activarSeleccionDestinoMapa);
  }

  const btnCancelDestinoBanner = document.getElementById('btn-cancelar-seleccion-destino');
  if (btnCancelDestinoBanner) {
    btnCancelDestinoBanner.addEventListener('click', desactivarSeleccionDestinoMapa);
  }
}

// -----------------------------------------------------------------------------
// CONTROL DE ACORDEONES EN PANEL LATERAL (METADATA Y AMENAZAS)
// -----------------------------------------------------------------------------
function inicializarAcordeonesSidebar() {
  function enlazarAcordeon(btnId, bodyId) {
    const btn = document.getElementById(btnId);
    const body = document.getElementById(bodyId);
    if (!btn || !body) return;

    btn.addEventListener('click', () => {
      const expandido = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', expandido ? 'false' : 'true');
      body.hidden = expandido;
    });
  }

  enlazarAcordeon('btn-accordion-metadata', 'body-accordion-metadata');
  enlazarAcordeon('btn-accordion-amenazas', 'body-accordion-amenazas');
}

// =============================================================================
// GESTIÓN DE NAVEGACIÓN ENTRE MÓDULOS
// =============================================================================
function configurarNavegacionModulos(d) {
  const tabBtnSimulador = document.getElementById('tab-btn-simulador');
  const tabBtnGrafo = document.getElementById('tab-btn-grafo');
  const tabBtnInfra = document.getElementById('tab-btn-infraestructura');
  const tabBtnMeta = document.getElementById('tab-btn-metadata');
  const tabBtnAmenazas = document.getElementById('tab-btn-amenazas');
  const tabBtnDoc = document.getElementById('tab-btn-documentacion');

  const vistaSimulador = document.getElementById('vista-simulador');
  const vistaGrafo = document.getElementById('vista-grafo');
  const vistaInfra = document.getElementById('vista-infraestructura');
  const vistaMeta = document.getElementById('vista-metadata');
  const vistaAmenazas = document.getElementById('vista-amenazas');
  const vistaDoc = document.getElementById('vista-documentacion');

  function cambiarPestaña(tab) {
    [tabBtnSimulador, tabBtnGrafo, tabBtnInfra, tabBtnMeta, tabBtnAmenazas, tabBtnDoc].forEach(btn => btn?.classList.remove('active'));
    [vistaSimulador, vistaGrafo, vistaInfra, vistaMeta, vistaAmenazas, vistaDoc].forEach(v => { if (v) v.hidden = true; });

    if (tab === 'simulador') {
      tabBtnSimulador.classList.add('active');
      vistaSimulador.hidden = false;
      setTimeout(() => mapa.invalidateSize(), 60);
    } else if (tab === 'grafo') {
      if (tabBtnGrafo) tabBtnGrafo.classList.add('active');
      if (vistaGrafo) vistaGrafo.hidden = false;
      if (!mapaGrafoInicializado) {
        montarMapaGrafo(d);
      }
      setTimeout(() => {
        if (mapaGrafo) mapaGrafo.invalidateSize();
      }, 60);
    } else if (tab === 'infraestructura') {
      tabBtnInfra.classList.add('active');
      vistaInfra.hidden = false;
      if (!mapaInfraInicializado) {
        montarMapaInfra(d);
      }
      setTimeout(() => {
        if (mapaInfra) mapaInfra.invalidateSize();
      }, 60);
    } else if (tab === 'metadata') {
      tabBtnMeta.classList.add('active');
      vistaMeta.hidden = false;
      if (!mapaMetaInicializado) {
        montarMapaMeta(d);
      }
      setTimeout(() => {
        if (mapaMeta) mapaMeta.invalidateSize();
      }, 60);
    } else if (tab === 'amenazas') {
      tabBtnAmenazas.classList.add('active');
      vistaAmenazas.hidden = false;
      if (!mapaAmenazasInicializado) {
        montarMapaAmenazas(d);
      }
      setTimeout(() => {
        if (mapaAmenazas) mapaAmenazas.invalidateSize();
      }, 60);
    } else if (tab === 'documentacion') {
      tabBtnDoc.classList.add('active');
      vistaDoc.hidden = false;
    }
  }

  tabBtnSimulador.addEventListener('click', () => cambiarPestaña('simulador'));
  if (tabBtnGrafo) tabBtnGrafo.addEventListener('click', () => cambiarPestaña('grafo'));
  tabBtnInfra.addEventListener('click', () => cambiarPestaña('infraestructura'));
  if (tabBtnMeta) tabBtnMeta.addEventListener('click', () => cambiarPestaña('metadata'));
  if (tabBtnAmenazas) tabBtnAmenazas.addEventListener('click', () => cambiarPestaña('amenazas'));
  if (tabBtnDoc) tabBtnDoc.addEventListener('click', () => cambiarPestaña('documentacion'));
}

// =============================================================================
// MÓDULO DE GRAFO (ARQUITECTURA, MAPEO Y CONSTRUCCIÓN TOPOLÓGICA)
// =============================================================================
function inicializarModuloGrafo(d) {
  // Desglose de categorías de nodos
  const conteoCat = {};
  if (d.nodos && d.nodos.features) {
    d.nodos.features.forEach(f => {
      const c = f.properties.category || 'otros';
      conteoCat[c] = (conteoCat[c] || 0) + 1;
    });
  }

  const catsContainer = document.getElementById('grafo-cats-list');
  if (catsContainer) {
    catsContainer.innerHTML = Object.keys(COLOR_CATEGORIA)
      .filter(c => conteoCat[c])
      .map(c => `
        <div class="cat-item-pill">
          <div class="cat-left">
            <span class="punto" style="background:${COLOR_CATEGORIA[c]}"></span>
            <span>${esc(NOMBRE_CATEGORIA[c])}</span>
          </div>
          <span class="cat-count-badge">${conteoCat[c]}</span>
        </div>
      `).join('');
  }
}

function montarMapaGrafo(d) {
  if (mapaGrafoInicializado) return;
  mapaGrafoInicializado = true;

  mapaGrafo = L.map('mapa-grafo').setView([-32.76, -71.47], 12);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }).addTo(mapaGrafo);

  const layerZonas = L.layerGroup().addTo(mapaGrafo);
  const layerAristas = L.layerGroup().addTo(mapaGrafo);
  const layerNodos = L.layerGroup().addTo(mapaGrafo);

  // Inspector UI updater
  const inspBox = document.getElementById('grafo-inspector-details');
  const inspHint = document.getElementById('grafo-inspector-placeholder');
  const inspType = document.getElementById('grafo-insp-type-badge');
  const inspTitle = document.getElementById('grafo-insp-title');
  const inspTable = document.getElementById('grafo-insp-table-content');

  function mostrarEnInspector(tipo, titulo, props) {
    if (!inspType || !inspTitle || !inspTable) return;
    inspType.textContent = tipo;
    inspTitle.textContent = titulo;
    inspTable.innerHTML = `<table class="insp-table"><tbody>${
      Object.entries(props).map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`).join('')
    }</tbody></table>`;
    if (inspHint) inspHint.hidden = true;
    if (inspBox) inspBox.hidden = false;
  }

  // 1. Zonas Urbanas Mapeadas
  if (d.zonas && d.zonas.features) {
    d.zonas.features.forEach(f => {
      const p = f.properties;
      L.geoJSON(f, {
        style: {
          color: '#6366f1',
          weight: 1.5,
          fillColor: '#818cf8',
          fillOpacity: 0.16,
          dashArray: '3 3',
        },
        onEachFeature: (feat, layer) => {
          layer.bindTooltip(`<b>${esc(p.name)}</b><br>Área: ${p.area_km2 || '—'} km²`, { sticky: true });
          layer.on('click', () => {
            mostrarEnInspector('Zona Urbana (DAN 151)', p.name, {
              'Código': p.code || '—',
              'Nombre': p.name || 'Área Urbana',
              'Superficie': p.area_km2 ? `${p.area_km2} km²` : '—',
              'Restricción': 'DAN 151 (Penalización por densidad poblacional)',
            });
          });
        }
      }).addTo(layerZonas);
    });
  }

  // 2. Corredores Aéreos K=4
  if (d.aristas && d.aristas.features) {
    d.aristas.features.forEach(f => {
      const p = f.properties;
      const coords = f.geometry.coordinates.map(c => [c[1], c[0]]);
      const len = parseFloat(p.length_m || 0);
      const polyline = L.polyline(coords, {
        color: len < 500 ? '#38bdf8' : (len < 1500 ? '#0284c7' : '#64748b'),
        weight: 2,
        opacity: 0.7,
      });
      polyline.bindTooltip(`Corredor #${p.id}: ${km(len)}`, { sticky: true });
      polyline.on('click', () => {
        mostrarEnInspector('Corredor Aéreo (Arista)', `Corredor #${p.id} (${p.source_code || p.source} → ${p.target_code || p.target})`, {
          'ID Arista': p.id,
          'Nodo Origen': `${p.source} (${p.source_code || '—'})`,
          'Nodo Destino': `${p.target} (${p.target_code || '—'})`,
          'Longitud Física': `${p.length_m} m (${km(len)})`,
          'Costo Base': `${p.cost || p.length_m} m`,
          'Topología': 'K=4 Vecinos (Haversine + Union-Find)',
        });
      });
      polyline.addTo(layerAristas);
    });
  }

  // 3. Vértices 3D
  if (d.nodos && d.nodos.features) {
    d.nodos.features.forEach(f => {
      const p = f.properties;
      const [lon, lat] = f.geometry.coordinates;
      const color = COLOR_CATEGORIA[p.category] || '#38bdf8';
      const marker = L.circleMarker([lat, lon], {
        radius: p.category === 'base' ? 8 : (p.category === 'sinca' ? 7 : 5),
        fillColor: color,
        fillOpacity: 0.95,
        color: '#ffffff',
        weight: 1.5,
      });
      marker.bindTooltip(`<b>${esc(p.name)}</b><br>${NOMBRE_CATEGORIA[p.category] || p.category}`, { sticky: true });
      marker.on('click', () => {
        mostrarEnInspector('Vértice de Red (Nodo)', p.name, {
          'ID pgRouting': p.id,
          'Código': p.code,
          'Categoría': NOMBRE_CATEGORIA[p.category] || p.category,
          'Tipo': p.type || '—',
          'Rol Operacional': p.role || 'Nodo de paso',
          'Elevación Terreno': p.elevation_msnm != null ? `${p.elevation_msnm} m.s.n.m.` : '—',
          'Comuna / Localidad': p.city || 'Quintero / Puchuncaví',
          'Coordenadas [Lon, Lat]': `[${lon.toFixed(5)}, ${lat.toFixed(5)}]`,
        });
      });
      marker.addTo(layerNodos);
    });
  }

  // Controles de visibilidad de capas
  const chkNodos = document.getElementById('toggle-grafo-nodos');
  if (chkNodos) {
    chkNodos.addEventListener('change', (e) => {
      if (e.target.checked) mapaGrafo.addLayer(layerNodos);
      else mapaGrafo.removeLayer(layerNodos);
    });
  }

  const chkAristas = document.getElementById('toggle-grafo-aristas');
  if (chkAristas) {
    chkAristas.addEventListener('change', (e) => {
      if (e.target.checked) mapaGrafo.addLayer(layerAristas);
      else mapaGrafo.removeLayer(layerAristas);
    });
  }

  const chkZonas = document.getElementById('toggle-grafo-zonas');
  if (chkZonas) {
    chkZonas.addEventListener('change', (e) => {
      if (e.target.checked) mapaGrafo.addLayer(layerZonas);
      else mapaGrafo.removeLayer(layerZonas);
    });
  }

  const btnCloseInsp = document.getElementById('btn-close-grafo-insp');
  if (btnCloseInsp) {
    btnCloseInsp.addEventListener('click', () => {
      if (inspBox) inspBox.hidden = true;
      if (inspHint) inspHint.hidden = false;
    });
  }

  setTimeout(() => {
    if (mapaGrafo) mapaGrafo.invalidateSize();
  }, 250);
}

function inicializarModuloInfraestructura(d) {
  // 2. Poblar KPIs de Infraestructura
  const numNodos = d.nodos.features.length;
  const numAristas = d.aristas.features.length;
  const numZonas = d.zonas.features.length;
  const lens = d.aristas.features.map(f => parseFloat(f.properties.length_m || 0));
  const minLen = Math.round(Math.min(...lens));
  const maxLen = Math.round(Math.max(...lens));
  const promLen = Math.round(lens.reduce((a, b) => a + b, 0) / lens.length);

  document.getElementById('kpi-infra-nodos').textContent = numNodos;
  document.getElementById('kpi-infra-aristas').textContent = numAristas;
  document.getElementById('kpi-infra-zonas').textContent = numZonas;
  document.getElementById('kpi-infra-promedio').textContent = `${fmt(promLen)} m`;
  document.getElementById('count-chip-nodos').textContent = numNodos;
  document.getElementById('count-chip-aristas').textContent = numAristas;

  // 3. Desglose de Categorías de Nodos
  const conteoCat = {};
  d.nodos.features.forEach(f => {
    const c = f.properties.category || 'otros';
    conteoCat[c] = (conteoCat[c] || 0) + 1;
  });

  const catsContainer = document.getElementById('infra-cats-list');
  catsContainer.innerHTML = Object.keys(COLOR_CATEGORIA)
    .filter(c => conteoCat[c])
    .map(c => `
      <div class="cat-item-pill">
        <div class="cat-left">
          <span class="punto" style="background:${COLOR_CATEGORIA[c]}"></span>
          <span>${esc(NOMBRE_CATEGORIA[c])}</span>
        </div>
        <span class="cat-count-badge">${conteoCat[c]}</span>
      </div>
    `).join('');

  // 4. Descargar Todo Unificado (.json)
  document.getElementById('btn-descargar-todo').addEventListener('click', () => {
    const paquete = {
      descripcion: "Infraestructura Completa de Red UAV · Bahía de Quintero",
      metodologia: "K-vecinos (K=4) + Conectividad Union-Find + Zonas Urbanas DAN 151",
      modulo: "Infraestructura Geoespacial",
      fecha_exportacion: new Date().toISOString(),
      nodos: d.nodos,
      aristas: d.aristas,
      zonas_urbanas: d.zonas,
    };
    const blob = new Blob([JSON.stringify(paquete, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'infraestructura_completa.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });

  // 5. Explorador de Código y Datos (Tabs)
  const expTabs = document.querySelectorAll('.exp-tab');
  expTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      expTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetId = `exp-${tab.dataset.exp}`;
      document.querySelectorAll('.exp-panel').forEach(p => p.hidden = true);
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.hidden = false;
    });
  });

  // Cargar Muestras de JSON en el Explorador
  function sampleGeoJSON(fc) {
    return {
      type: fc.type,
      etl: fc.etl,
      total_features: fc.features.length,
      muestra_primeros_features: fc.features.slice(0, 3),
    };
  }

  document.getElementById('code-nodos-text').textContent = JSON.stringify(sampleGeoJSON(d.nodos), null, 2);
  document.getElementById('code-aristas-text').textContent = JSON.stringify(sampleGeoJSON(d.aristas), null, 2);
  document.getElementById('code-zonas-text').textContent = JSON.stringify(sampleGeoJSON(d.zonas), null, 2);

  // Cargar script Python
  fetch('../infraestructura/extraer_infraestructura.py')
    .then(r => r.text())
    .then(code => {
      document.getElementById('code-script-text').textContent = code;
    })
    .catch(() => {
      document.getElementById('code-script-text').textContent = '# No se pudo cargar el script vía HTTP';
    });

  // Documentación Markdown (.md)
  const docMarkdownContent = document.getElementById('doc-markdown-content');
  const docSubBtns = document.querySelectorAll('.doc-subbtn');

  function cargarDoc(filename) {
    docMarkdownContent.innerHTML = '<em>Cargando ' + filename + '…</em>';
    fetch(`../infraestructura/${filename}`)
      .then(r => r.text())
      .then(text => {
        docMarkdownContent.innerHTML = renderMarkdownSimple(text);
      })
      .catch(() => {
        docMarkdownContent.innerHTML = '<span class="text-bad">Error al cargar ' + filename + '</span>';
      });
  }

  docSubBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      docSubBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      cargarDoc(btn.dataset.docfile);
    });
  });
  cargarDoc('nodos.md');

  // Botones de copiar código
  document.querySelectorAll('.btn-copy-code').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.copy;
      const el = document.getElementById(targetId);
      if (el) {
        navigator.clipboard.writeText(el.textContent).then(() => {
          const original = btn.textContent;
          btn.textContent = '¡Copiado!';
          setTimeout(() => { btn.textContent = original; }, 1800);
        });
      }
    });
  });

  // Botón cerrar inspector
  document.getElementById('btn-close-insp').addEventListener('click', () => {
    document.getElementById('inspector-details').hidden = true;
    document.getElementById('inspector-placeholder').hidden = false;
  });
}

function montarMapaInfra(d) {
  if (mapaInfraInicializado) return;
  mapaInfraInicializado = true;

  mapaInfra = L.map('mapa-infra').setView([-32.76, -71.47], 12);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }).addTo(mapaInfra);

  const layerZonas = L.layerGroup().addTo(mapaInfra);
  const layerAristas = L.layerGroup().addTo(mapaInfra);
  const layerNodos = L.layerGroup().addTo(mapaInfra);

  // Inspector UI updater
  const inspBox = document.getElementById('inspector-details');
  const inspHint = document.getElementById('inspector-placeholder');
  const inspType = document.getElementById('insp-type-badge');
  const inspTitle = document.getElementById('insp-title');
  const inspTable = document.getElementById('insp-table-content');

  function mostrarEnInspector(tipo, titulo, props) {
    inspType.textContent = tipo;
    inspTitle.textContent = titulo;
    inspTable.innerHTML = `<table class="insp-table"><tbody>${
      Object.entries(props).map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`).join('')
    }</tbody></table>`;
    inspHint.hidden = true;
    inspBox.hidden = false;
  }

  // 1. Zonas Urbanas
  d.zonas.features.forEach(f => {
    const p = f.properties;
    L.geoJSON(f, {
      style: {
        color: '#6366f1',
        weight: 1.5,
        fillColor: '#818cf8',
        fillOpacity: 0.18,
        dashArray: '3 3',
      },
      onEachFeature: (feat, layer) => {
        layer.bindTooltip(`<b>${esc(p.name)}</b><br>Área: ${p.area_km2} km²`, { sticky: true });
        layer.on('click', () => {
          mostrarEnInspector('Zona Urbana (DAN 151)', p.name, {
            'Código': p.code,
            'Nombre': p.name,
            'Comuna / Ciudad': p.city || 'Quintero / Puchuncaví',
            'Superficie': `${p.area_km2} km²`,
            'Restricción': 'DAN 151 (Penalización por densidad habitacional)',
          });
        });
      }
    }).addTo(layerZonas);
  });

  // 2. Aristas (Corredores Aéreos K=4)
  d.aristas.features.forEach(f => {
    const p = f.properties;
    const coords = f.geometry.coordinates.map(c => [c[1], c[0]]);
    const len = parseFloat(p.length_m);
    // Color según longitud
    const colorArista = len < 500 ? '#38bdf8' : (len < 1500 ? '#06b6d4' : '#64748b');
    const polyline = L.polyline(coords, {
      color: colorArista,
      weight: 2,
      opacity: 0.65,
    });
    polyline.bindTooltip(`Corredor #${p.id}: ${km(len)}`, { sticky: true });
    polyline.on('click', () => {
      mostrarEnInspector('Corredor Aéreo (Arista)', `Arista #${p.id} (${p.source_code} → ${p.target_code})`, {
        'ID Arista': p.id,
        'Nodo Origen (source)': `${p.source} (${p.source_code})`,
        'Nodo Destino (target)': `${p.target} (${p.target_code})`,
        'Longitud Real': `${p.length_m} m (${km(len)})`,
        'Costo Directo': `${p.cost} m`,
        'Costo Inverso': `${p.reverse_cost} m`,
        'Topología': 'K=4 Vecinos (Haversine + Union-Find)',
      });
    });
    polyline.addTo(layerAristas);
  });

  // 3. Nodos (Vértices)
  d.nodos.features.forEach(f => {
    const p = f.properties;
    const [lon, lat] = f.geometry.coordinates;
    const color = COLOR_CATEGORIA[p.category] || '#38bdf8';
    const marker = L.circleMarker([lat, lon], {
      radius: p.category === 'base' ? 8 : (p.category === 'sinca' ? 7 : 5),
      fillColor: color,
      fillOpacity: 0.9,
      color: '#ffffff',
      weight: 1.5,
    });
    marker.bindTooltip(`<b>${esc(p.name)}</b><br>${NOMBRE_CATEGORIA[p.category] || p.category}`, { sticky: true });
    marker.on('click', () => {
      mostrarEnInspector('Vértice de Red (Nodo)', p.name, {
        'ID pgRouting': p.id,
        'Código Estable': p.code,
        'Categoría': NOMBRE_CATEGORIA[p.category] || p.category,
        'Tipo': p.type || '—',
        'Rol en la Misión': p.role || 'Nodo de paso',
        'Prioridad': p.priority != null ? p.priority : '—',
        'Comuna / Localidad': p.city || 'Quintero',
        'Elevación del Terreno': p.elevation_msnm != null ? `${p.elevation_msnm} m.s.n.m.` : '—',
        'Contaminantes (SINCA/Emisoras)': (p.pollutants && p.pollutants.length) ? p.pollutants.join(', ') : 'Ninguno (nodo de paso)',
        'Coordenadas [Lon, Lat]': `[${lon.toFixed(5)}, ${lat.toFixed(5)}]`,
      });
    });
    marker.addTo(layerNodos);
  });

  // Controles de visibilidad de capas
  document.getElementById('toggle-infra-nodos').addEventListener('change', (e) => {
    if (e.target.checked) mapaInfra.addLayer(layerNodos);
    else mapaInfra.removeLayer(layerNodos);
  });
  document.getElementById('toggle-infra-aristas').addEventListener('change', (e) => {
    if (e.target.checked) mapaInfra.addLayer(layerAristas);
    else mapaInfra.removeLayer(layerAristas);
  });
  document.getElementById('toggle-infra-zonas').addEventListener('change', (e) => {
    if (e.target.checked) mapaInfra.addLayer(layerZonas);
    else mapaInfra.removeLayer(layerZonas);
  });

  setTimeout(() => {
    mapaInfra.invalidateSize();
  }, 250);
}

// =============================================================================
// MÓDULO DE METADATA TERRITORIAL Y OPERACIONAL
// =============================================================================
function inicializarModuloMetadata(d) {
  // 1. Poblar KPIs de Metadata
  document.getElementById('kpi-meta-sinca').textContent = d.aire.features.length;
  document.getElementById('kpi-meta-srtm').textContent = d.relieve.features.length;
  document.getElementById('kpi-meta-ine').textContent = d.manzanas.features.length;
  document.getElementById('kpi-meta-antenas').textContent = d.antenas.features.length;
  const kpiObs = document.getElementById('kpi-meta-obstaculos');
  if (kpiObs) kpiObs.textContent = (d.obstaculos && d.obstaculos.features ? d.obstaculos.features.length : 12);

  // 2. Descargar Todo Consolidado de Metadata
  const btnDl = document.getElementById('btn-descargar-todo-metadata');
  if (btnDl) {
    btnDl.addEventListener('click', () => {
      const paqueteMeta = {
        descripcion: "Metadata Territorial y Operacional · Bahía de Quintero",
        referencia: "Dimensiones de Riesgo y Operación UAV",
        fecha_exportacion: new Date().toISOString(),
        fuentes: {
          sinca_calidad_aire: d.aire,
          srtm_relieve: d.relieve,
          ine_manzanas: d.manzanas,
          osm_antenas: d.antenas,
          osm_obstaculos: d.obstaculos,
        }
      };
      const blob = new Blob([JSON.stringify(paqueteMeta, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'metadata_consolidada.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // 3. Explorador de Metadata
  const META_SPECS = {
    sinca: {
      nombre: 'sinca_calidad_aire',
      archivoGeojson: '../metadata/sinca_calidad_aire.geojson',
      archivoScript: '../metadata/sinca_calidad_aire.py',
      archivoDoc: '../metadata/sinca_calidad_aire.md',
      dataRef: d.aire,
      tablaBD: 'meta_air_quality',
      desc: `${d.aire.features.length} Estaciones · Calidad del Aire MMA`,
    },
    srtm: {
      nombre: 'srtm_relieve',
      archivoGeojson: '../metadata/srtm_relieve.geojson',
      archivoScript: '../metadata/srtm_relieve.py',
      archivoDoc: '../metadata/srtm_relieve.md',
      dataRef: d.relieve,
      tablaBD: 'meta_edge_terrain',
      desc: `${d.relieve.features.length} Perfiles de Aristas · NASA SRTM 30m`,
    },
    ine: {
      nombre: 'ine_manzanas',
      archivoGeojson: '../metadata/ine_manzanas.geojson',
      archivoScript: '../metadata/ine_manzanas.py',
      archivoDoc: '../metadata/ine_manzanas.md',
      dataRef: d.manzanas,
      tablaBD: 'meta_census_block',
      desc: `${d.manzanas.features.length} Manzanas Censales · INE Censo 2017`,
    },
    antenas: {
      nombre: 'osm_antenas',
      archivoGeojson: '../metadata/osm_antenas.geojson',
      archivoScript: '../metadata/osm_antenas.py',
      archivoDoc: '../metadata/osm_antenas.md',
      dataRef: d.antenas,
      tablaBD: 'meta_telecom_antenna',
      desc: `${d.antenas.features.length} Antenas de Telecomunicaciones · Celdas C2 3km`,
    },
    obstaculos: {
      nombre: 'osm_obstaculos',
      archivoGeojson: '../metadata/osm_obstaculos.geojson',
      archivoScript: '../metadata/osm_obstaculos.py',
      archivoDoc: '../metadata/osm_obstaculos.md',
      dataRef: d.obstaculos || { type: 'FeatureCollection', features: [] },
      tablaBD: 'meta_obstacle',
      desc: `${(d.obstaculos && d.obstaculos.features ? d.obstaculos.features.length : 12)} Obstáculos Físicos y Alta Tensión (OSM)`,
    },
  };

  let metaFuenteActiva = 'sinca';
  let metaTipoVistaActivo = 'geojson';
  const cacheTextos = {};

  function actualizarExploradorMeta() {
    const spec = META_SPECS[metaFuenteActiva];
    const infoText = document.getElementById('meta-exp-info-text');
    const preEl = document.getElementById('meta-code-viewer-pre');
    const codeEl = document.getElementById('meta-code-viewer-code');
    const docEl = document.getElementById('meta-doc-viewer');

    if (infoText) {
      infoText.innerHTML = `<code>${spec.nombre}</code> &bull; ${spec.desc} &bull; Tabla BD: <code>${spec.tablaBD}</code>`;
    }

    if (metaTipoVistaActivo === 'geojson') {
      preEl.hidden = false;
      docEl.hidden = true;
      const sample = {
        type: spec.dataRef.type,
        etl: spec.dataRef.etl,
        total_features: spec.dataRef.features.length,
        muestra_features: spec.dataRef.features.slice(0, 2),
      };
      codeEl.textContent = JSON.stringify(sample, null, 2);
    } else if (metaTipoVistaActivo === 'script') {
      preEl.hidden = false;
      docEl.hidden = true;
      if (cacheTextos[spec.archivoScript]) {
        codeEl.textContent = cacheTextos[spec.archivoScript];
      } else {
        codeEl.textContent = 'Cargando script Python…';
        fetch(spec.archivoScript)
          .then(r => r.text())
          .then(text => {
            cacheTextos[spec.archivoScript] = text;
            if (metaTipoVistaActivo === 'script') codeEl.textContent = text;
          })
          .catch(() => { codeEl.textContent = '# No se pudo cargar el script vía HTTP'; });
      }
    } else if (metaTipoVistaActivo === 'doc') {
      preEl.hidden = true;
      docEl.hidden = false;
      if (cacheTextos[spec.archivoDoc]) {
        docEl.innerHTML = cacheTextos[spec.archivoDoc];
      } else {
        docEl.innerHTML = '<em>Cargando especificación técnica…</em>';
        fetch(spec.archivoDoc)
          .then(r => r.text())
          .then(text => {
            const html = renderMarkdownSimple(text);
            cacheTextos[spec.archivoDoc] = html;
            if (metaTipoVistaActivo === 'doc') docEl.innerHTML = html;
          })
          .catch(() => { docEl.innerHTML = '<span class="text-bad">Error al cargar especificación</span>'; });
      }
    }
  }

  // Tabs de Fuentes
  document.querySelectorAll('.meta-exp-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.meta-exp-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      metaFuenteActiva = tab.dataset.meta;
      actualizarExploradorMeta();
    });
  });

  // Subtabs de Tipo de Vista (GeoJSON / Script / Doc)
  document.querySelectorAll('.meta-type-subbtn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.meta-type-subbtn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      metaTipoVistaActivo = btn.dataset.viewtype;
      actualizarExploradorMeta();
    });
  });

  // Copiar código
  const btnCopy = document.getElementById('btn-copy-meta-code');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const codeEl = document.getElementById('meta-code-viewer-code');
      if (codeEl && !codeEl.hidden) {
        navigator.clipboard.writeText(codeEl.textContent).then(() => {
          btnCopy.textContent = 'Copiado';
          setTimeout(() => { btnCopy.textContent = 'Copiar'; }, 1600);
        });
      }
    });
  }

  // Cerrar inspector
  const btnClose = document.getElementById('btn-close-meta-insp');
  if (btnClose) {
    btnClose.addEventListener('click', () => {
      document.getElementById('meta-inspector-details').hidden = true;
      document.getElementById('meta-inspector-placeholder').hidden = false;
    });
  }

  // Ejecución inicial de vista
  actualizarExploradorMeta();
}

function montarMapaMeta(d) {
  if (mapaMetaInicializado) return;
  mapaMetaInicializado = true;

  mapaMeta = L.map('mapa-meta').setView([-32.76, -71.47], 12);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }).addTo(mapaMeta);

  const layerManzanas = L.layerGroup().addTo(mapaMeta);
  const layerAntenas = L.layerGroup().addTo(mapaMeta);
  const layerRelieve = L.layerGroup().addTo(mapaMeta);
  const layerSinca = L.layerGroup().addTo(mapaMeta);

  const inspBox = document.getElementById('meta-inspector-details');
  const inspHint = document.getElementById('meta-inspector-placeholder');
  const inspType = document.getElementById('meta-insp-type-badge');
  const inspTitle = document.getElementById('meta-insp-title');
  const inspTable = document.getElementById('meta-insp-table-content');

  function mostrarEnMetaInspector(tipo, titulo, props) {
    inspType.textContent = tipo;
    inspTitle.textContent = titulo;
    inspTable.innerHTML = `<table class="insp-table"><tbody>${
      Object.entries(props).map(([k, v]) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`).join('')
    }</tbody></table>`;
    inspHint.hidden = true;
    inspBox.hidden = false;
  }

  // 1. Manzanas INE (Polígonos de Densidad)
  d.manzanas.features.forEach(f => {
    const p = f.properties;
    const dens = p.density_hab_km2 || 0;
    const esDensa = dens > 2500;
    const color = esDensa ? '#ef4444' : (dens > 1000 ? '#f97316' : (dens > 200 ? '#eab308' : '#64748b'));
    L.geoJSON(f, {
      style: {
        color: color,
        weight: 1,
        fillColor: color,
        fillOpacity: esDensa ? 0.35 : 0.12,
      },
      onEachFeature: (feat, layer) => {
        layer.bindTooltip(`<b>Manzana ${esc(p.manzent)}</b><br>${fmt(dens)} hab/km² (${p.commune})`, { sticky: true });
        layer.on('click', () => {
          mostrarEnMetaInspector('Manzana Censal (INE Censo 2017)', `Manzana ${p.manzent}`, {
            'Código INE (manzent)': p.manzent,
            'Comuna': p.commune,
            'Distrito Censal': p.district,
            'Población Censada': fmt(p.persons),
            'Viviendas': fmt(p.dwellings),
            'Superficie Manzana': `${fmt(p.area_m2)} m²`,
            'Densidad Habitacional': `${fmt(dens)} hab/km²`,
            'Restricción DAN 151': esDensa ? 'Zona densamente poblada (>2.500 hab/km²) · Penalizada en costo' : 'Bajo umbral crítico',
          });
        });
      }
    }).addTo(layerManzanas);
  });

  // 2. Antenas de Telecomunicaciones (Celdas Macro C2)
  d.antenas.features.forEach(f => {
    const p = f.properties;
    L.geoJSON(f, {
      style: {
        color: '#06b6d4',
        weight: 1.5,
        fillColor: '#0891b2',
        fillOpacity: 0.14,
        dashArray: '4 4',
      },
      onEachFeature: (feat, layer) => {
        layer.bindTooltip(`<b>Antena ${esc(p.name || p.osm_id)}</b><br>Cobertura: 3.000 m`, { sticky: true });
        layer.on('click', () => {
          mostrarEnMetaInspector('Telecomunicaciones (Enlace C2 OSM)', `Antena ${p.name || p.osm_id}`, {
            'ID OSM': p.osm_id,
            'Estructura': `${p.name || 'Sin nombre'} (${p.structure || 'torre'})`,
            'Operador Registrado': p.operator || 'No registrado',
            'Telefonía Celular': p.mobile_phone ? 'Sí' : 'No',
            'Altura Estructura': p.height_m ? `${p.height_m} m` : 'No especificada',
            'Radio Cobertura': `${fmt(p.coverage_radius_m)} m (Supuesto celda macro)`,
            'Función en Ruteo': 'Garantiza enlace continuo C2; áreas externas son sombras de telemetría',
          });
        });
      }
    }).addTo(layerAntenas);
  });

  // 3. Relieve por Arista (NASA SRTM 30m)
  d.relieve.features.forEach(f => {
    const p = f.properties;
    const coords = f.geometry.coordinates.map(c => [c[1], c[0]]);
    const desnivel = p.relief_m;
    const color = desnivel > 80 ? '#ec4899' : (desnivel > 30 ? '#a855f7' : '#0ea5e9');
    const poly = L.polyline(coords, {
      color: color,
      weight: 2.5,
      opacity: 0.7,
    });
    poly.bindTooltip(`Arista #${p.edge_id}: Cota máx ${p.terrain_max_m}m · Desnivel ${p.relief_m}m`, { sticky: true });
    poly.on('click', () => {
      mostrarEnMetaInspector('Perfil Orográfico (NASA SRTM 30m)', `Arista #${p.edge_id} (${p.source_code} → ${p.target_code})`, {
        'ID Arista': p.edge_id,
        'Nodos Extremos': `${p.source_code} ↔ ${p.target_code}`,
        'Cota Terreno Mínima': `${p.terrain_min_m} m.s.n.m.`,
        'Cota Terreno Máxima': `${p.terrain_max_m} m.s.n.m.`,
        'Cota Media': `${p.terrain_mean_m} m.s.n.m.`,
        'Desnivel Relativo (máx - mín)': `${p.relief_m} m`,
        'Ascenso Acumulado': `${p.ascent_m} m`,
        'Descenso Acumulado': `${p.descent_m} m`,
        'Muestreo Altimétrico': `${p.samples} puntos (intervalo 100 m)`,
        'Normativa DAN 151': 'Altitud segura: [cota_max + 0m, cota_max + 120m AGL]',
      });
    });
    poly.addTo(layerRelieve);
  });

  // 4. Estaciones SINCA (Calidad del Aire)
  d.aire.features.forEach(f => {
    const p = f.properties;
    const [lon, lat] = f.geometry.coordinates;
    const st = (p.worst_status || '').toLowerCase();
    const color = st.includes('bueno') ? '#10b981' : (st.includes('regular') ? '#f59e0b' : '#ef4444');
    const marker = L.circleMarker([lat, lon], {
      radius: 8,
      fillColor: color,
      fillOpacity: 0.95,
      color: '#ffffff',
      weight: 2,
    });
    marker.bindTooltip(`<b>${esc(p.station_name)}</b><br>Estado: ${esc(p.worst_status || 'Sin datos')}`, { sticky: true });
    marker.on('click', () => {
      mostrarEnMetaInspector('Calidad del Aire (SINCA MMA)', p.station_name, {
        'Identificador': p.station_key,
        'Nombre': p.station_name,
        'Comuna': p.commune,
        'Red de Monitoreo': p.network,
        'Operador': p.operator,
        'Nodo Asociado': p.node_code ? `${p.node_code} (dist: ${Math.round(p.node_distance_m)}m)` : 'Sin nodo en red',
        'Peor Condición': p.worst_status || 'Sin datos',
        'Mediciones Recientes': p.measurements && p.measurements.length
          ? p.measurements.map(m => `${m.pollutant}: ${m.value} ${m.unit} [${m.status}]`).join(' | ')
          : 'Sin mediciones reportadas',
        'Impacto en Misión': 'Determina la urgencia y prioridad de vuelo del dron hacia este punto',
      });
    });
    marker.addTo(layerSinca);
  });

  // 5. Obstáculos Verticales y Líneas de Alta Tensión (OSM)
  const layerObstaculos = L.layerGroup().addTo(mapaMeta);
  if (d.obstaculos && d.obstaculos.features) {
    d.obstaculos.features.forEach(f => {
      const p = f.properties;
      const g = f.geometry;
      if (g.type === 'LineString') {
        const coords = g.coordinates.map(c => [c[1], c[0]]);
        const poly = L.polyline(coords, {
          color: '#f59e0b',
          weight: 3.5,
          opacity: 0.9,
          dashArray: '6 4'
        });
        poly.bindTooltip(`<b>${esc(p.name)}</b><br>${p.voltage_kv || 'Alta'} kV · ${p.operational_action}`, { sticky: true });
        poly.on('click', () => {
          mostrarEnMetaInspector('Línea de Transmisión Eléctrica (OSM)', p.name, {
            'ID OSM': p.osm_id,
            'Infraestructura': p.name,
            'Nivel de Tensión': `${p.voltage_kv || '110/220'} kV`,
            'Radio de Seguridad': `${p.buffer_radius_m} m`,
            'Peligro Aeronáutico': 'Cables tensores e interferencia electromagnética con el compás magnético del UAV',
            'Acción en Ruteo': p.operational_action === 'bloquear' ? 'Bloqueo duro (Inhabilita aristas que la cruzan)' : 'Penalización por margen',
          });
        });
        poly.addTo(layerObstaculos);
      } else {
        const esChimenea = p.obstacle_type === 'chimney';
        const color = esChimenea ? '#dc2626' : '#d97706';
        const marker = L.circleMarker([p.lat, p.lon], {
          radius: esChimenea ? 8 : 6,
          fillColor: color,
          fillOpacity: 0.95,
          color: '#ffffff',
          weight: 2,
        });
        marker.bindTooltip(`<b>${esc(p.name)}</b><br>Altura: ${p.height_m}m · ${p.operational_action}`, { sticky: true });
        marker.on('click', () => {
          mostrarEnMetaInspector('Obstáculo Físico en Altura (OSM)', p.name, {
            'ID OSM': p.osm_id,
            'Estructura': p.name,
            'Tipo de Obstáculo': p.obstacle_type,
            'Altura Física': `${p.height_m} m` + (p.height_estimated ? ' (estimada)' : ' (registrada)'),
            'Techo Legal DAN 151': '120 m AGL sobre el terreno',
            'Invasión de Franja': p.height_m >= 120 ? 'SUPERACIÓN CRÍTICA DEL TECHO DE VUELO' : 'Riesgo de colisión en maniobra',
            'Radio de Seguridad': `${p.buffer_radius_m} m`,
            'Acción en Ruteo': p.operational_action === 'bloquear' ? 'Bloqueo duro (Exclusión absoluta)' : 'Penalización conservadora',
          });
        });
        marker.addTo(layerObstaculos);
      }
    });
  }

  // Toggles de capas
  document.getElementById('toggle-meta-sinca').addEventListener('change', (e) => {
    if (e.target.checked) mapaMeta.addLayer(layerSinca);
    else mapaMeta.removeLayer(layerSinca);
  });
  document.getElementById('toggle-meta-srtm').addEventListener('change', (e) => {
    if (e.target.checked) mapaMeta.addLayer(layerRelieve);
    else mapaMeta.removeLayer(layerRelieve);
  });
  document.getElementById('toggle-meta-ine').addEventListener('change', (e) => {
    if (e.target.checked) mapaMeta.addLayer(layerManzanas);
    else mapaMeta.removeLayer(layerManzanas);
  });
  document.getElementById('toggle-meta-antenas').addEventListener('change', (e) => {
    if (e.target.checked) mapaMeta.addLayer(layerAntenas);
    else mapaMeta.removeLayer(layerAntenas);
  });
  const tglObs = document.getElementById('toggle-meta-obstaculos');
  if (tglObs) {
    tglObs.addEventListener('change', (e) => {
      if (e.target.checked) mapaMeta.addLayer(layerObstaculos);
      else mapaMeta.removeLayer(layerObstaculos);
    });
  }

  setTimeout(() => {
    mapaMeta.invalidateSize();
  }, 250);
}

// =============================================================================
// MÓDULO DE AMENAZAS DINÁMICAS Y MODELAMIENTO DE CONTINGENCIAS
// =============================================================================
function inicializarModuloAmenazas(d) {
  // 1. Poblar KPIs de Amenazas
  document.getElementById('kpi-amenaza-incendios').textContent = `${d.incendios.features.length} foco`;
  const cantAeronaves = (d.aeronaves || d.sismos)?.features?.length || 1;
  document.getElementById('kpi-amenaza-sismos').textContent = `${cantAeronaves} aeronave${cantAeronaves > 1 ? 's' : ''}`;
  document.getElementById('kpi-amenaza-viento').textContent = `${d.viento.features.length} celdas`;
  const cantNiebla = (d.niebla || d.lluvia)?.features?.length || 16;
  document.getElementById('kpi-amenaza-lluvia').textContent = `${cantNiebla} celdas`;

  // 2. Descargar Todo Consolidado de Amenazas
  const btnDl = document.getElementById('btn-descargar-todo-amenazas');
  if (btnDl) {
    btnDl.addEventListener('click', () => {
      const paqueteAmenazas = {
        descripcion: "Amenazas Dinámicas y Eventos de Falla · Bahía de Quintero",
        marco_metodologico: "NASA FIRMS (incendios) + OpenSky ADS-B (tráfico aéreo) + Open-Meteo (viento y niebla costera)",
        modulo: "Amenazas y Restricciones Dinámicas",
        modelo_bd: "PostgreSQL 16 + PostGIS 3.4 (tabla threat_event)",
        fecha_exportacion: new Date().toISOString(),
        fuentes: {
          firms_incendios: d.incendios,
          opensky_aeronaves: d.aeronaves || d.sismos,
          openmeteo_viento: d.viento,
          openmeteo_niebla: d.niebla || d.lluvia,
        }
      };
      const blob = new Blob([JSON.stringify(paqueteAmenazas, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'amenazas_consolidadas.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // 3. Explorador de Amenazas
  const specAeronaves = {
    nombre: 'opensky_aeronaves',
    archivoGeojson: '../amenazas/opensky_aeronaves.geojson',
    archivoScript: '../amenazas/opensky_aeronaves.py',
    archivoCarga: '../amenazas/cargar_opensky_aeronaves.py',
    archivoDoc: '../amenazas/opensky_aeronaves.md',
    dataRef: d.aeronaves || d.sismos,
    tablaBD: 'threat_event (event_type = \'aeronave\')',
    desc: `${(d.aeronaves || d.sismos).features.length} Aeronave ADS-B · OpenSky Network (separación SCER)`,
  };

  const specNiebla = {
    nombre: 'openmeteo_niebla',
    archivoGeojson: '../amenazas/openmeteo_niebla.geojson',
    archivoScript: '../amenazas/openmeteo_niebla.py',
    archivoCarga: '../amenazas/cargar_openmeteo_niebla.py',
    archivoDoc: '../amenazas/openmeteo_niebla.md',
    dataRef: d.niebla || d.lluvia,
    tablaBD: 'threat_event (event_type = \'niebla\')',
    desc: `${(d.niebla || d.lluvia).features.length} Celdas 4×4 · Open-Meteo Forecast (visibilidad < 1000m)`,
  };

  const AMENAZA_SPECS = {
    firms: {
      nombre: 'firms_incendios',
      archivoGeojson: '../amenazas/firms_incendios.geojson',
      archivoScript: '../amenazas/firms_incendios.py',
      archivoCarga: '../amenazas/cargar_firms_incendios.py',
      archivoDoc: '../amenazas/firms_incendios.md',
      dataRef: d.incendios,
      tablaBD: 'threat_event (event_type = \'incendio\')',
      desc: `${d.incendios.features.length} Foco Activo · NASA FIRMS VIIRS/MODIS`,
    },
    opensky: specAeronaves,
    csn: specAeronaves,
    viento: {
      nombre: 'openmeteo_viento',
      archivoGeojson: '../amenazas/openmeteo_viento.geojson',
      archivoScript: '../amenazas/openmeteo_viento.py',
      archivoCarga: '../amenazas/cargar_openmeteo_viento.py',
      archivoDoc: '../amenazas/openmeteo_viento.md',
      dataRef: d.viento,
      tablaBD: 'threat_event (event_type = \'viento\')',
      desc: `${d.viento.features.length} Celdas 4×4 · Open-Meteo Forecast API (umbral 12 m/s)`,
    },
    niebla: specNiebla,
    lluvia: specNiebla,
  };

  let amenazaFuenteActiva = 'firms';
  let amenazaTipoVistaActivo = 'geojson';
  const cacheAmenazasTextos = {};

  function actualizarExploradorAmenaza() {
    const spec = AMENAZA_SPECS[amenazaFuenteActiva];
    const infoText = document.getElementById('amenaza-exp-info-text');
    const preEl = document.getElementById('amenaza-code-viewer-pre');
    const codeEl = document.getElementById('amenaza-code-viewer-code');
    const docEl = document.getElementById('amenaza-doc-viewer');

    if (infoText) {
      infoText.innerHTML = `<code>${spec.nombre}</code> &bull; ${spec.desc} &bull; Tabla BD: <code>${spec.tablaBD}</code>`;
    }

    if (amenazaTipoVistaActivo === 'geojson') {
      preEl.hidden = false;
      docEl.hidden = true;
      const sample = {
        type: spec.dataRef.type,
        etl: spec.dataRef.etl,
        total_features: spec.dataRef.features.length,
        muestra_features: spec.dataRef.features.slice(0, 2),
      };
      codeEl.textContent = JSON.stringify(sample, null, 2);
    } else if (amenazaTipoVistaActivo === 'script') {
      preEl.hidden = false;
      docEl.hidden = true;
      if (cacheAmenazasTextos[spec.archivoScript]) {
        codeEl.textContent = cacheAmenazasTextos[spec.archivoScript];
      } else {
        codeEl.textContent = 'Cargando script Python de extracción…';
        fetch(spec.archivoScript)
          .then(r => r.text())
          .then(text => {
            cacheAmenazasTextos[spec.archivoScript] = text;
            if (amenazaTipoVistaActivo === 'script') codeEl.textContent = text;
          })
          .catch(() => { codeEl.textContent = '# No se pudo cargar el script vía HTTP'; });
      }
    } else if (amenazaTipoVistaActivo === 'carga') {
      preEl.hidden = false;
      docEl.hidden = true;
      if (cacheAmenazasTextos[spec.archivoCarga]) {
        codeEl.textContent = cacheAmenazasTextos[spec.archivoCarga];
      } else {
        codeEl.textContent = 'Cargando script Python de carga a BD…';
        fetch(spec.archivoCarga)
          .then(r => r.text())
          .then(text => {
            cacheAmenazasTextos[spec.archivoCarga] = text;
            if (amenazaTipoVistaActivo === 'carga') codeEl.textContent = text;
          })
          .catch(() => { codeEl.textContent = '# No se pudo cargar el script de carga vía HTTP'; });
      }
    } else if (amenazaTipoVistaActivo === 'doc') {
      preEl.hidden = true;
      docEl.hidden = false;
      if (cacheAmenazasTextos[spec.archivoDoc]) {
        docEl.innerHTML = cacheAmenazasTextos[spec.archivoDoc];
      } else {
        docEl.innerHTML = '<em>Cargando especificación técnica…</em>';
        fetch(spec.archivoDoc)
          .then(r => r.text())
          .then(text => {
            const html = renderMarkdownSimple(text);
            cacheAmenazasTextos[spec.archivoDoc] = html;
            if (amenazaTipoVistaActivo === 'doc') docEl.innerHTML = html;
          })
          .catch(() => { docEl.innerHTML = '<span class="text-bad">Error al cargar especificación técnica</span>'; });
      }
    }
  }

  // Tabs de Amenazas
  document.querySelectorAll('.amenaza-exp-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.amenaza-exp-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      amenazaFuenteActiva = tab.dataset.amenaza;
      actualizarExploradorAmenaza();
    });
  });

  // Subtabs de Tipo de Vista (GeoJSON / Script / Carga BD / Doc)
  document.querySelectorAll('.amenaza-type-subbtn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.amenaza-type-subbtn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      amenazaTipoVistaActivo = btn.dataset.viewtype;
      actualizarExploradorAmenaza();
    });
  });

  // Copiar código
  const btnCopy = document.getElementById('btn-copy-amenaza-code');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const codeEl = document.getElementById('amenaza-code-viewer-code');
      if (codeEl && !codeEl.hidden) {
        navigator.clipboard.writeText(codeEl.textContent).then(() => {
          btnCopy.textContent = 'Copiado';
          setTimeout(() => { btnCopy.textContent = 'Copiar'; }, 1600);
        });
      }
    });
  }

  // Cerrar inspector
  const btnClose = document.getElementById('btn-close-amenaza-insp');
  if (btnClose) {
    btnClose.addEventListener('click', () => {
      document.getElementById('amenaza-inspector-details').hidden = true;
      document.getElementById('amenaza-inspector-placeholder').hidden = false;
    });
  }

  // Ejecución inicial de vista
  actualizarExploradorAmenaza();
}

function montarMapaAmenazas(d) {
  if (mapaAmenazasInicializado) return;
  mapaAmenazasInicializado = true;

  mapaAmenazas = L.map('mapa-amenazas').setView([-32.76, -71.47], 12);
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, attribution: 'Tiles &copy; Esri',
  }).addTo(mapaAmenazas);

  const layerRedFondo = L.layerGroup().addTo(mapaAmenazas);
  const layerViento = L.layerGroup().addTo(mapaAmenazas);
  const layerLluvia = L.layerGroup().addTo(mapaAmenazas);
  const layerSismos = L.layerGroup().addTo(mapaAmenazas);
  const layerIncendios = L.layerGroup().addTo(mapaAmenazas);

  function mostrarEnAmenazaInspector(tipo, nombre, datos) {
    const box = document.getElementById('amenaza-inspector-details');
    const ph = document.getElementById('amenaza-inspector-placeholder');
    const badge = document.getElementById('amenaza-insp-badge');
    const nameEl = document.getElementById('amenaza-insp-name');
    const tbody = document.querySelector('#amenaza-insp-table tbody');

    badge.textContent = tipo;
    nameEl.textContent = nombre;
    tbody.innerHTML = Object.entries(datos).map(([k, v]) => `
      <tr>
        <th>${k}</th>
        <td>${v}</td>
      </tr>
    `).join('');

    ph.hidden = true;
    box.hidden = false;
  }

  // 1. Red UAV de Fondo
  d.aristas.features.forEach(f => {
    const coords = f.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
    L.polyline(coords, {
      color: '#64748b', weight: 1.2, opacity: 0.35,
    }).addTo(layerRedFondo);
  });
  d.nodos.features.forEach(f => {
    const [lon, lat] = f.geometry.coordinates;
    L.circleMarker([lat, lon], {
      radius: 2.5, color: '#94a3b8', fillColor: '#cbd5e1', fillOpacity: 0.5, weight: 0.5,
    }).addTo(layerRedFondo);
  });

  // 2. Grilla de Viento (Open-Meteo)
  d.viento.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;
    const poly = L.polygon(ring, {
      color: isExceed ? '#ef4444' : '#38bdf8',
      weight: isExceed ? 2 : 1,
      fillColor: isExceed ? '#ef4444' : '#0284c7',
      fillOpacity: isExceed ? 0.35 : 0.10,
    });
    poly.on('click', () => {
      mostrarEnAmenazaInspector('Viento y Ráfagas (Open-Meteo)', `Celda ${p.cell} · ${p.external_id}`, {
        'Tipo de Evento': 'viento',
        'Celda Espacial': p.cell,
        'Ráfaga Máx (10m)': `${p.value} ${p.unit}`,
        'Viento Medio (10m)': `${p.wind_speed_10m} m/s (dir: ${p.wind_direction_10m}°)`,
        'Viento Medio (80m)': `${p.wind_speed_80m} m/s`,
        'Viento Medio (120m DAN 151)': `${p.wind_speed_120m} m/s (dir: ${p.wind_direction_120m}°)`,
        'Umbral Crítico': `${p.threshold} m/s`,
        'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (Bloquea aristas)</span>' : '<span class="text-good">OPERACIONAL</span>',
        'Fecha Observación': p.observed_at,
        'Regla de Pesos Operacionales': isExceed ? 'Inhabilita aristas que cruzan la celda (C = ∞)' : 'Modula velocidad terrestre v_g y consumo EEE por viento de frente',
      });
    });
    poly.addTo(layerViento);
  });

  // 3. Grilla de Niebla Costera (Open-Meteo)
  const coleccionNieblaMap = d.niebla || d.lluvia;
  coleccionNieblaMap.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;
    const esNiebla = p.event_type === 'niebla' || p.relative_humidity !== undefined;
    const poly = L.polygon(ring, {
      color: isExceed ? '#0284c7' : '#0d9488',
      weight: isExceed ? 2 : 1,
      fillColor: isExceed ? '#38bdf8' : '#99f6e4',
      fillOpacity: isExceed ? 0.35 : 0.12,
    });
    poly.on('click', () => {
      if (esNiebla) {
        mostrarEnAmenazaInspector('Niebla Costera / Camanchaca (Open-Meteo)', `Celda ${p.cell} · ${p.external_id}`, {
          'Tipo de Evento': 'niebla',
          'Celda Espacial': p.cell,
          'Visibilidad en Superficie': `${p.value} m`,
          'Umbral VMC DAN 151': `${p.threshold} m`,
          'Humedad Relativa': `${p.relative_humidity || 0}%`,
          'Nubosidad Baja': `${p.cloud_cover_low || 0}%`,
          'Condición Atmosférica': p.condition || (isExceed ? 'Niebla activa (Restricción VLOS)' : 'VMC Nominal'),
          'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (Bloquea aristas por visibilidad &lt; 1000m)</span>' : '<span class="text-good">OPERACIONAL</span>',
          'Fecha Observación': p.observed_at,
          'Regla de Pesos Operacionales': isExceed ? 'Inhabilita aristas; activa desvío hacia zonas despejadas o aterrizaje preventivo' : 'Vuelo permitido bajo reglas visuales VMC nominales',
        });
      } else {
        mostrarEnAmenazaInspector('Precipitación (MET Norway)', `Celda ${p.cell} · ${p.external_id}`, {
          'Tipo de Evento': 'lluvia',
          'Celda Espacial': p.cell,
          'Precipitación Prevista': `${p.value} ${p.unit} (próxima hora)`,
          'Condición Meteorológica': p.symbol_code || 'No reportada',
          'Umbral Crítico': `${p.threshold} mm/h`,
          'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (No-Go por agua)</span>' : '<span class="text-good">OPERACIONAL</span>',
          'Periodo Válido': `${p.observed_at} → ${p.valid_until || '—'}`,
          'Regla de Pesos Operacionales': isExceed ? 'Inhabilita aristas; activa retorno de emergencia LPP hacia sotavento' : 'Vuelo permitido con sensores ópticos en condiciones estándar',
        });
      }
    });
    poly.addTo(layerLluvia);
  });

  // 4. Sismos (CSN / EMSC)
  // 4. Tráfico Aéreo Tripulado (OpenSky ADS-B)
  const coleccionAeronavesMap = d.aeronaves || d.sismos;
  coleccionAeronavesMap.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;
    const esAeronave = p.event_type === 'aeronave' || p.callsign;

    const poly = L.polygon(ring, {
      color: esAeronave ? (isExceed ? '#ea580c' : '#f59e0b') : (isExceed ? '#ef4444' : '#a855f7'),
      weight: isExceed ? 2 : 1,
      dashArray: '4 4',
      fillColor: esAeronave ? (isExceed ? '#f97316' : '#fbbf24') : (isExceed ? '#f59e0b' : '#a855f7'),
      fillOpacity: isExceed ? 0.25 : 0.08,
    });

    const marker = L.circleMarker([p.lat, p.lon], {
      radius: esAeronave ? 7 : Math.max(4, Math.min(12, p.value * 1.6)),
      color: isExceed ? '#ffffff' : '#d97706',
      fillColor: esAeronave ? '#ea580c' : (isExceed ? '#ef4444' : '#d97706'),
      fillOpacity: 0.9,
      weight: 2,
    });

    const handler = () => {
      if (esAeronave) {
        mostrarEnAmenazaInspector('Tráfico Aéreo Tripulado (OpenSky ADS-B)', `${p.callsign || 'Aeronave'} · ${Math.round(p.baro_altitude_m || p.value)}m MSL`, {
          'Tipo de Evento': 'aeronave',
          'ID Externo / Registro': p.external_id,
          'Callsign / Matrícula': p.callsign || 'VFR-SCER',
          'Transpondedor (ICAO24)': p.icao24 || 'e802a1',
          'Altitud Barométrica': `${Math.round(p.baro_altitude_m || p.value)} m MSL`,
          'Velocidad Terrestre': `${p.velocity_ms || 0} m/s (${((p.velocity_ms || 0) * 3.6).toFixed(0)} km/h)`,
          'Cilindro de Exclusión': `${p.exclusion_radius_m || 1500} m`,
          'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (Conflicto Potencial en SCER)</span>' : 'Crucero (> 1000m)',
          'Fecha Observación': p.observed_at,
          'Regla de Pesos Operacionales': isExceed
            ? 'Inhabilita aristas que intersecan el cilindro de exclusión (C = ∞); DAN 151 exige derecho de paso prioritario a aeronaves tripuladas'
            : 'Vuelo nominal sin conflicto de separación',
        });
      } else {
        mostrarEnAmenazaInspector('Evento Sísmico (CSN / EMSC)', `${p.region || 'Sismo'} · M ${p.value}`, {
          'Tipo de Evento': 'sismo',
          'ID Externo (EMSC unid)': p.external_id,
          'Magnitud': `${p.value} (${p.unit})`,
          'Profundidad': `${p.depth_km} km`,
          'Autoría': p.authority || 'CSN (U. de Chile)',
          'Radio de Afectación': `${p.affect_radius_km ? p.affect_radius_km.toFixed(1) : '—'} km (heurística intensidad ≥ VI)`,
          'Distancia a Base Quintero': `${p.distance_to_base_km ? p.distance_to_base_km.toFixed(1) : '—'} km`,
          'Afectación a Base': p.base_dentro_radio ? '<span class="text-bad">Base dentro del radio de daño</span>' : 'Base fuera de zona crítica',
          'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (M ≥ 5.0)</span>' : 'Baja intensidad (M < 5.0)',
          'Fecha Observación': p.observed_at,
          'Regla de Pesos Operacionales': p.base_dentro_radio
            ? 'Deshabilita base aérea de Quintero por corte eléctrico; fuerza desvío a vertipuerto auxiliar o RTH'
            : 'Monitoreo preventivo sin corte de nodos base',
        });
      }
    };

    poly.on('click', handler);
    marker.on('click', handler);

    poly.addTo(layerSismos);
    marker.addTo(layerSismos);
  });

  // 5. Focos de Incendio (NASA FIRMS)
  d.incendios.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;

    const poly = L.polygon(ring, {
      color: '#ef4444',
      weight: 2,
      dashArray: '5, 5',
      fillColor: '#dc2626',
      fillOpacity: 0.28,
    });

    const marker = L.circleMarker([p.lat, p.lon], {
      radius: 8,
      color: '#fef08a',
      fillColor: '#dc2626',
      fillOpacity: 0.95,
      weight: 2,
    });

    const handler = () => {
      mostrarEnAmenazaInspector('Foco de Incendio (NASA FIRMS)', `Foco Activo · ${p.instrument}`, {
        'Tipo de Evento': 'incendio',
        'ID Externo': p.external_id,
        'Potencia Radiativa (FRP)': `${p.value} ${p.unit}`,
        'Instrumento / Satélite': `${p.instrument} (${p.satellite})`,
        'Confianza Detección': p.confidence,
        'Temperatura de Brillo': `${p.brightness_k} K`,
        'Radio de Exclusión': `${p.radius_m} m (humo, calor y turbulencia)`,
        'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (Bloqueo Total)</span>' : 'Baja confianza',
        'Fecha Observación': p.observed_at,
        'Regla de Pesos Operacionales': 'Bloqueo estricto e insalvable (C = ∞) de todas las aristas que intersectan el radio de 2 km',
      });
    };

    poly.on('click', handler);
    marker.on('click', handler);

    poly.addTo(layerIncendios);
    marker.addTo(layerIncendios);
  });

  // Toggles de capas de amenazas
  document.getElementById('toggle-amenaza-incendios').addEventListener('change', (e) => {
    if (e.target.checked) mapaAmenazas.addLayer(layerIncendios);
    else mapaAmenazas.removeLayer(layerIncendios);
  });
  document.getElementById('toggle-amenaza-sismos').addEventListener('change', (e) => {
    if (e.target.checked) mapaAmenazas.addLayer(layerSismos);
    else mapaAmenazas.removeLayer(layerSismos);
  });
  document.getElementById('toggle-amenaza-viento').addEventListener('change', (e) => {
    if (e.target.checked) mapaAmenazas.addLayer(layerViento);
    else mapaAmenazas.removeLayer(layerViento);
  });
  document.getElementById('toggle-amenaza-lluvia').addEventListener('change', (e) => {
    if (e.target.checked) mapaAmenazas.addLayer(layerLluvia);
    else mapaAmenazas.removeLayer(layerLluvia);
  });
  document.getElementById('toggle-amenaza-red').addEventListener('change', (e) => {
    if (e.target.checked) mapaAmenazas.addLayer(layerRedFondo);
    else mapaAmenazas.removeLayer(layerRedFondo);
  });

  setTimeout(() => {
    mapaAmenazas.invalidateSize();
  }, 250);
}

// =============================================================================
// MÓDULO DE DOCUMENTACIÓN Y ESTRUCTURA DE DATOS
// =============================================================================
function inicializarModuloDocumentacion(d) {
  const CATALOGO_ARCHIVOS = {
    nodos: {
      id: 'nodos',
      dominio: 'Infraestructura',
      archivoDatos: '../infraestructura/nodos.geojson',
      nombreDatos: 'nodos.geojson',
      archivoDoc: '../infraestructura/nodos.md',
      nombreDoc: 'nodos.md',
      scriptGenerador: 'infraestructura/extraer_infraestructura.py',
      tablaBD: 'infra_node',
      tipoGeom: 'Point (WGS84 3D)',
      entidades: `${d.nodos?.features?.length || 195} nodos`,
      resumen: '195 nodos clasificados en 13 categorías temáticas (bases, SINCA, industrias, salud, educación).',
      datosRef: d.nodos,
    },
    aristas: {
      id: 'aristas',
      dominio: 'Infraestructura',
      archivoDatos: '../infraestructura/aristas.geojson',
      nombreDatos: 'aristas.geojson',
      archivoDoc: '../infraestructura/aristas.md',
      nombreDoc: 'aristas.md',
      scriptGenerador: 'infraestructura/extraer_infraestructura.py',
      tablaBD: 'infra_edge',
      tipoGeom: 'LineString (3D)',
      entidades: `${d.aristas?.features?.length || 633} aristas`,
      resumen: '633 aristas de vuelo 3D entre K=4 vecinos más cercanos con distancia geodésica y azimut.',
      datosRef: d.aristas,
    },
    zonas_urbanas: {
      id: 'zonas_urbanas',
      dominio: 'Infraestructura',
      archivoDatos: '../infraestructura/zonas_urbanas.geojson',
      nombreDatos: 'zonas_urbanas.geojson',
      archivoDoc: '../infraestructura/zonas_urbanas.md',
      nombreDoc: 'zonas_urbanas.md',
      scriptGenerador: 'infraestructura/extraer_infraestructura.py',
      tablaBD: 'infra_urban_zone',
      tipoGeom: 'Polygon',
      entidades: `${d.zonas?.features?.length || 13} localidades`,
      resumen: '13 polígonos urbanos y zonas de amortiguamiento de 150 m (restricción DAN 151 DGAC).',
      datosRef: d.zonas,
    },
    sinca_calidad_aire: {
      id: 'sinca_calidad_aire',
      dominio: 'Metadata',
      archivoDatos: '../metadata/sinca_calidad_aire.geojson',
      nombreDatos: 'sinca_calidad_aire.geojson',
      archivoDoc: '../metadata/sinca_calidad_aire.md',
      nombreDoc: 'sinca_calidad_aire.md',
      scriptGenerador: 'metadata/sinca_calidad_aire.py',
      tablaBD: 'meta_air_quality',
      tipoGeom: 'Point',
      entidades: `${d.aire?.features?.length || 10} estaciones`,
      resumen: '10 estaciones de monitoreo MMA con mediciones horarias de MP2.5, MP10, SO2 y NO2.',
      datosRef: d.aire,
    },
    srtm_relieve: {
      id: 'srtm_relieve',
      dominio: 'Metadata',
      archivoDatos: '../metadata/srtm_relieve.geojson',
      nombreDatos: 'srtm_relieve.geojson',
      archivoDoc: '../metadata/srtm_relieve.md',
      nombreDoc: 'srtm_relieve.md',
      scriptGenerador: 'metadata/srtm_relieve.py',
      tablaBD: 'meta_edge_terrain',
      tipoGeom: 'LineString (3D)',
      entidades: `${d.relieve?.features?.length || 633} perfiles`,
      resumen: '633 perfiles altimétricos orográficos muestreados cada 100 m con DEM SRTM de 30 m.',
      datosRef: d.relieve,
    },
    ine_manzanas: {
      id: 'ine_manzanas',
      dominio: 'Metadata',
      archivoDatos: '../metadata/ine_manzanas.geojson',
      nombreDatos: 'ine_manzanas.geojson',
      archivoDoc: '../metadata/ine_manzanas.md',
      nombreDoc: 'ine_manzanas.md',
      scriptGenerador: 'metadata/ine_manzanas.py',
      tablaBD: 'meta_census_block',
      tipoGeom: 'MultiPolygon / Polygon',
      entidades: `${d.manzanas?.features?.length || 703} manzanas`,
      resumen: '703 manzanas censales Censo 2017 con conteo de personas, viviendas y densidad.',
      datosRef: d.manzanas,
    },
    osm_antenas: {
      id: 'osm_antenas',
      dominio: 'Metadata',
      archivoDatos: '../metadata/osm_antenas.geojson',
      nombreDatos: 'osm_antenas.geojson',
      archivoDoc: '../metadata/osm_antenas.md',
      nombreDoc: 'osm_antenas.md',
      scriptGenerador: 'metadata/osm_antenas.py',
      tablaBD: 'meta_telecom_antenna',
      tipoGeom: 'Polygon (buffer 3 km)',
      entidades: `${d.antenas?.features?.length || 25} antenas`,
      resumen: '25 antenas de telecomunicación celular con macro-celdas de 3 km para enlace C2.',
      datosRef: d.antenas,
    },
    osm_obstaculos: {
      id: 'osm_obstaculos',
      dominio: 'Metadata',
      archivoDatos: '../metadata/osm_obstaculos.geojson',
      nombreDatos: 'osm_obstaculos.geojson',
      archivoDoc: '../metadata/osm_obstaculos.md',
      nombreDoc: 'osm_obstaculos.md',
      scriptGenerador: 'metadata/osm_obstaculos.py',
      tablaBD: 'meta_obstacle',
      tipoGeom: 'Point / LineString (buffer 60-120 m)',
      entidades: `${d.obstaculos?.features?.length || 12} obstáculos`,
      resumen: '12 obstáculos verticales industriales (chimeneas 50-152 m, líneas de alta tensión 110/220 kV y torres).',
      datosRef: d.obstaculos,
    },
    firms_incendios: {
      id: 'firms_incendios',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/firms_incendios.geojson',
      nombreDatos: 'firms_incendios.geojson',
      archivoDoc: '../amenazas/firms_incendios.md',
      nombreDoc: 'firms_incendios.md',
      scriptGenerador: 'amenazas/firms_incendios.py',
      tablaBD: 'threat_event (incendio)',
      tipoGeom: 'Polygon (radio 2 km)',
      entidades: `${d.incendios?.features?.length || 1} foco activo`,
      resumen: 'Focos de incendio satelitales NRT (VIIRS/MODIS) con FRP y exclusión térmica total.',
      datosRef: d.incendios,
    },
    opensky_aeronaves: {
      id: 'opensky_aeronaves',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/opensky_aeronaves.geojson',
      nombreDatos: 'opensky_aeronaves.geojson',
      archivoDoc: '../amenazas/opensky_aeronaves.md',
      nombreDoc: 'opensky_aeronaves.md',
      scriptGenerador: 'amenazas/opensky_aeronaves.py',
      tablaBD: 'threat_event (aeronave)',
      tipoGeom: 'Polygon (cilindro 1.5 km)',
      entidades: `${(d.aeronaves || d.sismos)?.features?.length || 1} aeronave`,
      resumen: 'Vigilancia ADS-B en vivo (OpenSky Network) con cilindros de exclusión aérea de 1500 m en aproximación a SCER.',
      datosRef: d.aeronaves || d.sismos,
    },
    csn_sismos: {
      id: 'opensky_aeronaves',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/opensky_aeronaves.geojson',
      nombreDatos: 'opensky_aeronaves.geojson',
      archivoDoc: '../amenazas/opensky_aeronaves.md',
      nombreDoc: 'opensky_aeronaves.md',
      scriptGenerador: 'amenazas/opensky_aeronaves.py',
      tablaBD: 'threat_event (aeronave)',
      tipoGeom: 'Polygon (cilindro 1.5 km)',
      entidades: `${(d.aeronaves || d.sismos)?.features?.length || 1} aeronave`,
      resumen: 'Vigilancia ADS-B en vivo (OpenSky Network) con cilindros de exclusión aérea de 1500 m en aproximación a SCER.',
      datosRef: d.aeronaves || d.sismos,
    },
    openmeteo_viento: {
      id: 'openmeteo_viento',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/openmeteo_viento.geojson',
      nombreDatos: 'openmeteo_viento.geojson',
      archivoDoc: '../amenazas/openmeteo_viento.md',
      nombreDoc: 'openmeteo_viento.md',
      scriptGenerador: 'amenazas/openmeteo_viento.py',
      tablaBD: 'threat_event (viento)',
      tipoGeom: 'Polygon (grilla 4×4)',
      entidades: `${d.viento?.features?.length || 16} celdas`,
      resumen: '16 celdas espaciales con ráfagas a 10m y viento a 120m (umbral No-Go 12 m/s DJI Matrice 350).',
      datosRef: d.viento,
    },
    openmeteo_niebla: {
      id: 'openmeteo_niebla',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/openmeteo_niebla.geojson',
      nombreDatos: 'openmeteo_niebla.geojson',
      archivoDoc: '../amenazas/openmeteo_niebla.md',
      nombreDoc: 'openmeteo_niebla.md',
      scriptGenerador: 'amenazas/openmeteo_niebla.py',
      tablaBD: 'threat_event (niebla)',
      tipoGeom: 'Polygon (grilla 4×4)',
      entidades: `${(d.niebla || d.lluvia)?.features?.length || 16} celdas`,
      resumen: '16 celdas con visibilidad horizontal en superficie (m), humedad y nubosidad baja (umbral VMC 1000m DAN 151).',
      datosRef: d.niebla || d.lluvia,
    },
    metno_lluvia: {
      id: 'openmeteo_niebla',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/openmeteo_niebla.geojson',
      nombreDatos: 'openmeteo_niebla.geojson',
      archivoDoc: '../amenazas/openmeteo_niebla.md',
      nombreDoc: 'openmeteo_niebla.md',
      scriptGenerador: 'amenazas/openmeteo_niebla.py',
      tablaBD: 'threat_event (niebla)',
      tipoGeom: 'Polygon (grilla 4×4)',
      entidades: `${(d.niebla || d.lluvia)?.features?.length || 16} celdas`,
      resumen: '16 celdas con visibilidad horizontal en superficie (m), humedad y nubosidad baja (umbral VMC 1000m DAN 151).',
      datosRef: d.niebla || d.lluvia,
    },
    ruta_dijkstra: {
      id: 'ruta_dijkstra',
      dominio: 'Ruteo y Simulación',
      archivoDatos: 'data/ruta_dijkstra.geojson',
      nombreDatos: 'ruta_dijkstra.geojson',
      archivoDoc: 'data/ruta_dijkstra.md',
      nombreDoc: 'ruta_dijkstra.md',
      scriptGenerador: 'ruteo/ruta_dijkstra.py',
      tablaBD: 'pgr_dijkstra (infra_edge)',
      tipoGeom: 'LineString',
      entidades: '16 rutas (k=1 y k=2)',
      resumen: 'Rutas de peor caso calculadas en PostgreSQL/pgRouting con costo = longitud física.',
      datosRef: d.rutas_pgrouting,
    },
    rutas_comparativas: {
      id: 'rutas_comparativas',
      dominio: 'Ruteo y Simulación',
      archivoDatos: 'data/rutas_comparativas.geojson',
      nombreDatos: 'rutas_comparativas.geojson',
      archivoDoc: 'data/rutas_comparativas.md',
      nombreDoc: 'rutas_comparativas.md',
      scriptGenerador: 'ruteo/ruteo_resiliente.py',
      tablaBD: 'K-caminos disimilares',
      tipoGeom: 'LineString',
      entidades: '32 trayectorias (k=1 y k=2)',
      resumen: '32 trayectorias comparativas para Dijkstra vs Ruteo Resiliente adaptativo.',
      datosRef: d.rutas_comparativas,
    },
    resumen_resiliencia: {
      id: 'resumen_resiliencia',
      dominio: 'Ruteo y Simulación',
      archivoDatos: 'data/resumen_resiliencia.json',
      nombreDatos: 'resumen_resiliencia.json',
      archivoDoc: 'data/resumen_resiliencia.md',
      nombreDoc: 'resumen_resiliencia.md',
      scriptGenerador: 'ruteo/ruteo_resiliente.py',
      tablaBD: 'Métricas de resiliencia',
      tipoGeom: 'JSON (Métricas Cuantitativas)',
      entidades: '8 destinos SINCA evaluados',
      resumen: 'Evaluación cuantitativa comparativa de resiliencia estocástica exacta y diversidad.',
      datosRef: d.resumen_resiliencia,
    },
  };

  // 1. Poblar Tabla de Trazabilidad
  const tbody = document.getElementById('tabla-trazabilidad-body');
  if (tbody) {
    const badgesColor = {
      'Infraestructura': '#10b981',
      'Metadata': '#0284c7',
      'Amenazas': '#ef4444',
      'Ruteo y Simulación': '#8b5cf6',
    };

    tbody.innerHTML = Object.values(CATALOGO_ARCHIVOS).map(item => `
      <tr>
        <td><span style="display:inline-block; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75rem; background:rgba(255,255,255,0.06); color:${badgesColor[item.dominio] || '#38bdf8'}; border:1px solid ${badgesColor[item.dominio] || '#38bdf8'}33;">${item.dominio}</span></td>
        <td><strong><a href="${item.archivoDatos}" download="${item.nombreDatos}" style="color:#f8fafc; text-decoration:none; border-bottom:1px dotted #38bdf8;">${item.nombreDatos}</a></strong></td>
        <td><button class="btn-goto-doc" data-docid="${item.id}" type="button" style="background:transparent; border:none; color:#38bdf8; cursor:pointer; font-family:monospace; font-size:0.82rem; padding:0; text-decoration:underline;">${item.nombreDoc}</button></td>
        <td><code style="color:#94a3b8; font-size:0.78rem;">${item.scriptGenerador}</code></td>
        <td><code style="color:#f59e0b; font-size:0.78rem;">${item.tablaBD}</code></td>
        <td><span style="color:#cbd5e1;">${item.entidades}</span> <span style="color:#64748b; font-size:0.75rem;">(${item.tipoGeom})</span></td>
      </tr>
    `).join('');

    // Listener para links de la tabla que navegan al visor
    tbody.querySelectorAll('.btn-goto-doc').forEach(btn => {
      btn.addEventListener('click', () => {
        const docId = btn.dataset.docid;
        document.querySelectorAll('.doc-file-btn').forEach(b => {
          b.classList.toggle('active', b.dataset.docfile === docId);
        });
        docArchivoActivo = docId;
        actualizarVisorDualDoc();
        document.getElementById('doc-active-bar')?.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  // 2. Descargar Diccionario Completo (.json)
  const btnDlMatriz = document.getElementById('btn-descargar-matriz-doc');
  if (btnDlMatriz) {
    btnDlMatriz.addEventListener('click', () => {
      const matrizDoc = {
        titulo: "Diccionario Maestro de Datos y Especificaciones Técnicas",
        total_archivos: Object.keys(CATALOGO_ARCHIVOS).length,
        norma_geoespacial: "RFC 7946 / EPSG:4326 (WGS84)",
        especificacion: "Archivo descriptivo formal .md por cada capa GeoJSON",
        fecha_exportacion: new Date().toISOString(),
        archivos: Object.values(CATALOGO_ARCHIVOS).map(a => ({
          dominio: a.dominio,
          archivo_datos: a.nombreDatos,
          archivo_especificacion: a.nombreDoc,
          script_generador: a.scriptGenerador,
          tabla_bd: a.tablaBD,
          geometria: a.tipoGeom,
          resumen: a.resumen,
        }))
      };
      const blob = new Blob([JSON.stringify(matrizDoc, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'diccionario_maestro_datos.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // 3. Lógica del Visor Dual Lado a Lado
  let docArchivoActivo = 'nodos';
  let docModoMuestra = true;
  const cacheDocMarkdown = {};

  function actualizarVisorDualDoc() {
    const item = CATALOGO_ARCHIVOS[docArchivoActivo];
    if (!item) return;

    // Actualizar badges e info
    const infoText = document.getElementById('doc-active-info-text');
    const badgeDoc = document.getElementById('badge-doc-file');
    const badgeData = document.getElementById('badge-data-file');
    const dlBtn = document.getElementById('btn-descargar-archivo-activo');
    const renderedDoc = document.getElementById('doc-rendered-markdown');
    const codeEl = document.getElementById('doc-code-viewer-code');

    if (infoText) {
      infoText.innerHTML = `<strong>${item.nombreDatos}</strong> &bull; Especificación: <code>${item.nombreDoc}</code> &bull; Tabla BD: <code>${item.tablaBD}</code> &bull; Dominio: <span style="color:#38bdf8;">${item.dominio}</span>`;
    }
    if (badgeDoc) badgeDoc.textContent = item.nombreDoc;
    if (badgeData) badgeData.textContent = item.nombreDatos;
    if (dlBtn) {
      dlBtn.href = item.archivoDatos;
      dlBtn.download = item.nombreDatos;
    }

    // Panel Izquierdo: Markdown Renderizado
    if (cacheDocMarkdown[item.archivoDoc]) {
      renderedDoc.innerHTML = cacheDocMarkdown[item.archivoDoc];
    } else {
      renderedDoc.innerHTML = '<em>Cargando especificación técnica…</em>';
      fetch(item.archivoDoc)
        .then(r => r.text())
        .then(text => {
          const html = renderMarkdownSimple(text);
          cacheDocMarkdown[item.archivoDoc] = html;
          if (CATALOGO_ARCHIVOS[docArchivoActivo]?.archivoDoc === item.archivoDoc) {
            renderedDoc.innerHTML = html;
          }
        })
        .catch(() => {
          renderedDoc.innerHTML = `<span class="text-bad">Error al cargar la especificación ${item.nombreDoc}</span>`;
        });
    }

    // Panel Derecho: Datos Reales
    function mostrarDatos(data) {
      if (!data) {
        codeEl.textContent = '// Cargando o datos no disponibles';
        return;
      }
      if (docModoMuestra) {
        if (data.features) {
          const sample = {
            type: data.type,
            etl: data.etl || data.metadata || null,
            total_features: data.features.length,
            muestra_primeros_features: data.features.slice(0, 2),
          };
          codeEl.textContent = JSON.stringify(sample, null, 2);
        } else {
          // JSON de métricas (ej. resumen_resiliencia)
          const sample = {
            generado: data.generado,
            paper: data.paper,
            algoritmo: data.algoritmo,
            metrica: data.metrica,
            total_destinos: Object.keys(data.destinos || {}).length,
            muestra_primer_destino: Object.entries(data.destinos || {})[0] || null,
          };
          codeEl.textContent = JSON.stringify(sample, null, 2);
        }
      } else {
        codeEl.textContent = JSON.stringify(data, null, 2);
      }
    }

    if (item.datosRef) {
      mostrarDatos(item.datosRef);
    } else {
      codeEl.textContent = 'Cargando archivo de datos…';
      fetch(item.archivoDatos)
        .then(r => r.json())
        .then(jsonData => {
          item.datosRef = jsonData;
          if (CATALOGO_ARCHIVOS[docArchivoActivo]?.id === item.id) {
            mostrarDatos(jsonData);
          }
        })
        .catch(() => {
          codeEl.textContent = `// Error al cargar datos de ${item.nombreDatos}`;
        });
    }
  }

  // Listeners para botones de selección de archivo en el visor
  document.querySelectorAll('.doc-file-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.doc-file-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      docArchivoActivo = btn.dataset.docfile;
      actualizarVisorDualDoc();
    });
  });

  // Toggle de visualización (Muestra vs Completo)
  const btnMuestra = document.getElementById('btn-doc-muestra');
  const btnCompleto = document.getElementById('btn-doc-completo');

  if (btnMuestra && btnCompleto) {
    btnMuestra.addEventListener('click', () => {
      btnMuestra.classList.add('active');
      btnCompleto.classList.remove('active');
      docModoMuestra = true;
      actualizarVisorDualDoc();
    });
    btnCompleto.addEventListener('click', () => {
      btnCompleto.classList.add('active');
      btnMuestra.classList.remove('active');
      docModoMuestra = false;
      actualizarVisorDualDoc();
    });
  }

  // Botón Copiar Código JSON
  const btnCopy = document.getElementById('btn-copy-doc-code');
  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const codeEl = document.getElementById('doc-code-viewer-code');
      if (codeEl) {
        navigator.clipboard.writeText(codeEl.textContent).then(() => {
          const original = btnCopy.textContent;
          btnCopy.textContent = 'Copiado';
          setTimeout(() => { btnCopy.textContent = original; }, 1600);
        });
      }
    });
  }

  // Ejecución inicial del visor
  actualizarVisorDualDoc();
}

// =============================================================================
// AUDITORÍA INTERACTIVA DE COSTOS DIJKSTRA Y SIMULACIÓN UAV
// Análisis de ruta base mediante pgr_dijkstra sobre longitud geodésica
// como referencia de navegación inicial previa a la integración de restricciones.
// =============================================================================

function inicializarAuditoriaDijkstra(d) {
  const contenedorSinca = document.getElementById('pgrouting-sinca-buttons');

  // Poblar los 8 botones oficiales de pgRouting en base de datos
  if (contenedorSinca && d.rutas_pgrouting && d.rutas_pgrouting.features) {
    contenedorSinca.innerHTML = '';
    const rutasK1 = d.rutas_pgrouting.features.filter(f => f.properties.k === 1);
    rutasK1.forEach(f => {
      const props = f.properties;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn-sinca-sample';
      const nomCorto = (props.destino_nombre || props.destino)
        .replace('Estación SINCA ', '')
        .replace('SINCA ', '');
      btn.innerHTML = `${esc(nomCorto)} <span style="opacity:0.75;font-size:0.65rem;">${km(props.longitud_m)}</span>`;
      btn.title = `Ruta de referencia pgr_dijkstra en BD:\n${props.destino_nombre}\nLongitud: ${km(props.longitud_m)}\nTramos: ${props.tramos}\nCosto: longitud en km (peor caso)`;

      btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-sinca-sample').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const selOrigen = document.getElementById('select-origen');
        const selDestino = document.getElementById('select-destino');
        if (selOrigen && selDestino) {
          selOrigen.value = props.origen || 'base_scer';
          selDestino.value = props.destino;
          detenerSimulacionVuelo();
          actualizarRutasEnVivo();
        }
      });

      contenedorSinca.appendChild(btn);
    });
  }
}

function actualizarAuditoriaDijkstraUI(dijK1, nodoOrig, nodoDest, metDijkstra, aristasMap) {
  rutaDijkstraActiva = { dijK1, nodoOrig, nodoDest, metDijkstra, aristasMap };

  const hud = document.getElementById('hud-dijkstra-costos');
  if (!hud || !dijK1 || !dijK1.aristas || !dijK1.aristas.length) return;

  const titleEl = document.getElementById('hud-dijkstra-title');
  const totalDistEl = document.getElementById('hud-total-distancia');
  const totalTramosEl = document.getElementById('hud-total-tramos');
  const veredictoEl = document.getElementById('hud-veredicto-riesgo');
  const motivoEl = document.getElementById('hud-veredicto-motivo');
  const stepperList = document.getElementById('hud-stepper-list');
  const trackDist = document.querySelector('.meter-distance');
  const trackDang = document.querySelector('.meter-danger');
  const meterCaption = document.getElementById('hud-meter-caption');

  if (titleEl) {
    titleEl.innerHTML = `Ruta Dijkstra (Peor Caso) &bull; <span style="color:#f87171;">${esc(nodoOrig.name)}</span> &rarr; <span style="color:#fb923c;">${esc(nodoDest.name)}</span>`;
  }

  // Desglose de cada tramo
  let totalM = 0;
  let tramosConFuego = 0;
  let tramosConPoblacion = 0;
  let tramosSinTelecom = 0;
  let tramosConSismo = 0;
  const tramosCalculados = [];

  for (let i = 0; i < dijK1.aristas.length; i++) {
    const eid = dijK1.aristas[i];
    const edge = aristasMap[eid];
    const uId = dijK1.nodos[i];
    const vId = dijK1.nodos[i + 1];
    const uNode = grafoNodos[uId];
    const vNode = grafoNodos[vId];

    const cTramo = edge ? edge.length_m : 0;
    totalM += cTramo;

    const hayFuego = edge ? (edge.hayIncendio || (document.getElementById('check-escenario-estres').checked && edge.hayEstres)) : false;
    const hayPoblacion = edge ? edge.hayPoblacion : false;
    const sinTelecom = edge ? !edge.hayTelecom : false;
    const haySismo = edge ? edge.haySismo : false;

    if (hayFuego) tramosConFuego++;
    if (hayPoblacion) tramosConPoblacion++;
    if (sinTelecom) tramosSinTelecom++;
    if (haySismo) tramosConSismo++;

    tramosCalculados.push({
      index: i,
      eid,
      edge,
      uNode,
      vNode,
      costoTramo: cTramo,
      acumuladoM: totalM,
      hayFuego,
      hayPoblacion,
      sinTelecom,
      haySismo,
    });
  }

  rutaDijkstraActiva.tramosCalculados = tramosCalculados;
  rutaDijkstraActiva.totalM = totalM;

  if (totalDistEl) {
    totalDistEl.textContent = `${km(totalM)} (${fmt(Math.round(totalM))} m)`;
  }
  if (totalTramosEl) {
    totalTramosEl.textContent = `${dijK1.aristas.length} tramos (${dijK1.nodos.length} nodos)`;
  }

  const tramosCriticos = tramosConFuego + tramosConPoblacion + tramosSinTelecom;

  if (veredictoEl && motivoEl) {
    if (tramosConFuego > 0) {
      veredictoEl.textContent = 'FALLA CRÍTICA EN VUELO';
      veredictoEl.className = 'text-bad';
      motivoEl.textContent = `Atraviesa ${tramosConFuego} tramo(s) con foco de incendio activo o pluma industrial.`;
    } else if (tramosConPoblacion > 0) {
      veredictoEl.textContent = 'INVIABLE: DAN 151';
      veredictoEl.className = 'text-bad';
      motivoEl.textContent = `Cruza ${tramosConPoblacion} tramo(s) sobre zonas densamente pobladas sin desvío de seguridad.`;
    } else if (tramosSinTelecom > 0) {
      veredictoEl.textContent = 'RIESGO: PÉRDIDA C2';
      veredictoEl.className = 'text-warning';
      motivoEl.textContent = `Cruza ${tramosSinTelecom} tramo(s) en zona de sombra sin cobertura de radiobases terrestres.`;
    } else {
      veredictoEl.textContent = 'SUBÓPTIMO (SIN METADATA)';
      veredictoEl.className = 'text-warning';
      motivoEl.textContent = 'Optimiza únicamente distancia geométrica sin verificar resiliencia multi-criterio.';
    }
  }

  // Barra comparativa pedagógica
  if (trackDist && trackDang) {
    trackDist.style.width = '48%';
    trackDist.textContent = `Distancia: ${km(totalM)} (Atajo físico 100%)`;

    trackDang.style.width = '52%';
    if (tramosCriticos > 0) {
      trackDang.textContent = `Peligro: ${tramosCriticos} tramo(s) inviables (Supervivencia: ${metDijkstra.supervivenciaK1Pct.toFixed(1)}%)`;
      trackDang.style.background = 'linear-gradient(90deg, #ea580c, #dc2626)';
    } else {
      trackDang.textContent = `Peligro: Sin resiliencia adaptativa (${metDijkstra.supervivenciaK1Pct.toFixed(1)}% supervivencia)`;
      trackDang.style.background = 'linear-gradient(90deg, #f59e0b, #ea580c)';
    }
  }

  if (meterCaption) {
    meterCaption.innerHTML = `<strong>¿Por qué es el peor caso?</strong> Porque resuelve la conectividad matemática en el papel, pero en el mundo real el UAV se destruye al no considerar incendios, población ni cobertura C2.`;
  }

  // Renderizar tarjetas del stepper paso a paso
  if (stepperList) {
    stepperList.innerHTML = '';
    tramosCalculados.forEach((t) => {
      const card = document.createElement('div');
      card.className = 'hud-step-card';
      card.dataset.stepIndex = t.index;

      let riesgoBadgeHtml = '<span class="hud-step-risk risk-safe"><span class="dot-live" style="background:#16a34a;width:6px;height:6px;display:inline-block;border-radius:50%;margin-right:4px;"></span>TRAMO DESPEJADO</span>';
      if (t.hayFuego) {
        riesgoBadgeHtml = '<span class="hud-step-risk risk-danger"><span class="dot-live" style="background:#dc2626;width:6px;height:6px;display:inline-block;border-radius:50%;margin-right:4px;"></span>FUEGO / PLUMA ACTIVA</span>';
      } else if (t.hayPoblacion) {
        riesgoBadgeHtml = '<span class="hud-step-risk risk-danger"><span class="dot-live" style="background:#ea580c;width:6px;height:6px;display:inline-block;border-radius:50%;margin-right:4px;"></span>DAN 151 URBANO</span>';
      } else if (t.sinTelecom) {
        riesgoBadgeHtml = '<span class="hud-step-risk" style="background:rgba(139,92,246,0.15);color:#7c3aed;border:1px solid rgba(139,92,246,0.3);"><span class="dot-live" style="background:#8b5cf6;width:6px;height:6px;display:inline-block;border-radius:50%;margin-right:4px;"></span>SIN ENLACE C2</span>';
      } else if (t.haySismo) {
        riesgoBadgeHtml = '<span class="hud-step-risk" style="background:rgba(234,179,8,0.15);color:#b45309;border:1px solid rgba(234,179,8,0.3);"><span class="dot-live" style="background:#d97706;width:6px;height:6px;display:inline-block;border-radius:50%;margin-right:4px;"></span>ALERTA SÍSMICA</span>';
      }

      const nomU = t.uNode?.name || `Vértice ${t.edge?.source}`;
      const nomV = t.vNode?.name || `Vértice ${t.edge?.target}`;

      card.innerHTML = `
        <div class="hud-step-num">
          <span>TRAMO ${String(t.index + 1).padStart(2, '0')}</span>
          <span class="hud-step-cost">+${fmt(Math.round(t.costoTramo))} m</span>
        </div>
        <div style="font-size: 0.74rem; color: #f1f5f9; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${esc(nomU)} &rarr; ${esc(nomV)}">
          ${esc(nomU)} &rarr; ${esc(nomV)}
        </div>
        <div class="hud-step-acum">
          Acumulado: <strong>${fmt(Math.round(t.acumuladoM))} m</strong> (${(t.acumuladoM / 1000).toFixed(2)} km)
        </div>
        ${riesgoBadgeHtml}
      `;

      card.addEventListener('mouseenter', () => {
        if (!simulacionVueloActiva) {
          resaltarSegmentoEnMapa(t);
        }
      });

      card.addEventListener('mouseleave', () => {
        if (!simulacionVueloActiva) {
          layerDijkstraAuditoria.clearLayers();
        }
      });

      card.addEventListener('click', () => {
        resaltarSegmentoEnMapa(t, true);
        if (t.edge && t.edge.coords && t.edge.coords.length) {
          const latlngs = t.edge.coords.map(c => [c[1], c[0]]);
          mapa.fitBounds(L.latLngBounds(latlngs), { maxZoom: 16, padding: [60, 60] });
        }
      });

      stepperList.appendChild(card);
    });
  }
}

function resaltarSegmentoEnMapa(t, fijarTooltip = false) {
  layerDijkstraAuditoria.clearLayers();
  if (!t || !t.edge || !t.edge.coords) return;

  const latlngs = t.edge.coords.map(c => [c[1], c[0]]);
  const poly = L.polyline(latlngs, {
    color: '#facc15',
    weight: 7,
    opacity: 0.95,
  }).addTo(layerDijkstraAuditoria);

  const midpoint = latlngs[Math.floor(latlngs.length / 2)];
  const riesgoTexto = t.hayFuego ? 'Pluma de fuego / Incendio'
    : (t.hayPoblacion ? 'Zona urbana densa (DAN 151)'
    : (t.sinTelecom ? 'Sin enlace de telemetría C2' : 'Nominal'));

  const tooltipHtml = `
    <div style="font-size:0.78rem;line-height:1.3;">
      <strong style="color:#facc15;">Tramo ${t.index + 1}: +${Math.round(t.costoTramo)} m</strong><br>
      ${esc(t.uNode?.name)} &rarr; ${esc(t.vNode?.name)}<br>
      <span style="color:#94a3b8;">Acumulado: ${fmt(Math.round(t.acumuladoM))} m</span><br>
      <strong>${riesgoTexto}</strong>
    </div>`;

  poly.bindTooltip(tooltipHtml, {
    permanent: fijarTooltip,
    sticky: !fijarTooltip,
    direction: 'top',
    className: 'tooltip-dijkstra-tramo',
  }).openTooltip(midpoint);
}

function detenerSimulacionVuelo() {
  simulacionVueloActiva = false;
  if (simulacionTimerId) {
    clearInterval(simulacionTimerId);
    simulacionTimerId = null;
  }
  layerSimuladorUav.clearLayers();
  layerDijkstraAuditoria.clearLayers();
  marcadorDronSimulado = null;

  const btnVuelo = document.getElementById('btn-hud-play-vuelo');
  if (btnVuelo) btnVuelo.innerHTML = '<svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg><span>Simular Vuelo</span>';

  const telemBox = document.getElementById('hud-flight-telemetry-box');
  if (telemBox) telemBox.hidden = true;

  document.querySelectorAll('.hud-step-card').forEach(c => c.classList.remove('active-step'));
}

function simularVueloUav() {
  if (!rutaDijkstraActiva || !rutaDijkstraActiva.tramosCalculados || !rutaDijkstraActiva.tramosCalculados.length) {
    return;
  }

  detenerSimulacionVuelo();
  simulacionVueloActiva = true;

  const btnVuelo = document.getElementById('btn-hud-play-vuelo');
  if (btnVuelo) btnVuelo.innerHTML = '<svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pausar Vuelo</span>';

  const telemBox = document.getElementById('hud-flight-telemetry-box');
  const stepInfo = document.getElementById('telemetry-step-info');
  const distInfo = document.getElementById('telemetry-dist-info');
  const statusInfo = document.getElementById('telemetry-status-info');
  if (telemBox) telemBox.hidden = false;

  const tramos = rutaDijkstraActiva.tramosCalculados;
  const totalTramos = tramos.length;
  const totalM = rutaDijkstraActiva.totalM;

  // Interpolar camino de vuelo suave entre vértices
  const puntosVuelo = [];
  tramos.forEach((t) => {
    const coords = t.edge.coords;
    for (let c = 0; c < coords.length; c++) {
      puntosVuelo.push({
        lat: coords[c][1],
        lon: coords[c][0],
        tramoRef: t,
      });
    }
  });

  if (!puntosVuelo.length) return;

  const dronHtml = `
    <div class="drone-sim-icon-box">
      <div class="drone-sim-radar" id="drone-radar-pulse"></div>
      <svg class="drone-sim-svg" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3.5" fill="#0284c7" />
        <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="#f8fafc" />
        <circle cx="12" cy="4" r="2.2" fill="#38bdf8" />
        <circle cx="12" cy="20" r="2.2" fill="#38bdf8" />
        <circle cx="4" cy="12" r="2.2" fill="#38bdf8" />
        <circle cx="20" cy="12" r="2.2" fill="#38bdf8" />
      </svg>
    </div>`;

  const dronIcon = L.divIcon({
    html: dronHtml,
    className: 'dron-marker-leaflet',
    iconSize: [38, 38],
    iconAnchor: [19, 19],
  });

  marcadorDronSimulado = L.marker([puntosVuelo[0].lat, puntosVuelo[0].lon], {
    icon: dronIcon,
    zIndexOffset: 1000,
  }).addTo(layerSimuladorUav);

  let pIdx = 0;
  let ultimoTramoIdx = -1;

  simulacionTimerId = setInterval(() => {
    if (!simulacionVueloActiva || pIdx >= puntosVuelo.length) {
      if (pIdx >= puntosVuelo.length) {
        if (btnVuelo) btnVuelo.innerHTML = '<svg class="ui-icon ui-icon-sm" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg><span>Reiniciar Vuelo</span>';
        if (statusInfo) {
          statusInfo.textContent = 'Destino alcanzado (Misión fallida en peor caso)';
          statusInfo.className = 'text-bad';
        }
      }
      clearInterval(simulacionTimerId);
      simulacionTimerId = null;
      simulacionVueloActiva = false;
      return;
    }

    const p = puntosVuelo[pIdx];
    const t = p.tramoRef;

    marcadorDronSimulado.setLatLng([p.lat, p.lon]);

    if (t.index !== ultimoTramoIdx) {
      ultimoTramoIdx = t.index;
      resaltarSegmentoEnMapa(t, false);

      // Actualizar tarjeta del stepper
      document.querySelectorAll('.hud-step-card').forEach(c => c.classList.remove('active-step'));
      const activeCard = document.querySelector(`.hud-step-card[data-step-index="${t.index}"]`);
      if (activeCard) {
        activeCard.classList.add('active-step');
        activeCard.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      }

      // Actualizar telemetría
      if (stepInfo) stepInfo.textContent = `Tramo ${t.index + 1}/${totalTramos}`;
      if (distInfo) distInfo.textContent = `${(t.acumuladoM / 1000).toFixed(2)} km / ${km(totalM)}`;

      const radarPulse = document.getElementById('drone-radar-pulse');
      if (t.hayFuego) {
        if (telemBox) telemBox.classList.add('telemetry-alert');
        if (radarPulse) radarPulse.classList.add('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = 'ALERTA: FUEGO ACTIVO / PLUMA';
          statusInfo.className = 'text-bad';
        }
      } else if (t.hayPoblacion) {
        if (telemBox) telemBox.classList.add('telemetry-alert');
        if (radarPulse) radarPulse.classList.add('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = 'ALERTA: ZONA URBANA (DAN 151)';
          statusInfo.className = 'text-bad';
        }
      } else if (t.sinTelecom) {
        if (telemBox) telemBox.classList.add('telemetry-alert');
        if (radarPulse) radarPulse.classList.remove('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = 'ALERTA: PÉRDIDA ENLACE C2';
          statusInfo.className = 'text-warning';
        }
      } else {
        if (telemBox) telemBox.classList.remove('telemetry-alert');
        if (radarPulse) radarPulse.classList.remove('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = 'Vuelo nominal';
          statusInfo.className = 'text-good';
        }
      }
    }

    pIdx++;
  }, 220);
}

iniciar();


