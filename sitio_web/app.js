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
  incendios: '../amenazas/firms_incendios.geojson',
  sismos: '../amenazas/csn_sismos.geojson',
  viento: '../amenazas/openmeteo_viento.geojson',
  lluvia: '../amenazas/metno_lluvia.geojson',
  rutas_pgrouting: 'data/ruta_dijkstra.geojson',
  rutas_comparativas: 'data/rutas_comparativas.geojson',
  resumen_resiliencia: 'data/resumen_resiliencia.json',
};

const COLOR_CATEGORIA = {
  base: '#10b981', sinca: '#f59e0b', emission_source: '#ef4444', health: '#ec4899',
  education: '#8b5cf6', commercial: '#06b6d4', crowded_area: '#84cc16', beach: '#0ea5e9',
  hospitality: '#f97316', restaurant: '#d946ef', attraction: '#14b8a6', historic: '#a16207',
  auxiliary_hub: '#64748b',
};

const NOMBRE_CATEGORIA = {
  base: 'Base Aérea', sinca: 'Estación SINCA', emission_source: 'Fuente Emisora', health: 'Salud',
  education: 'Educación', commercial: 'Comercial', crowded_area: 'Área Concurrida',
  beach: 'Playa', hospitality: 'Hospedaje', restaurant: 'Restaurante',
  attraction: 'Atractivo', historic: 'Histórico', auxiliary_hub: 'Hub Auxiliar',
};

// Utilidades generales de renderizado
const esc = (v) => String(v ?? '—').replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);
const fila = (k, v) => `<tr><th>${esc(k)}</th><td>${esc(v)}</td></tr>`;
const tabla = (filas) => `<table class="pop">${filas.map(([k, v]) => fila(k, v)).join('')}</table>`;
const km = (m) => `${(m / 1000).toFixed(2)} km`;
const fmt = (n) => (n == null ? null : Number(n).toLocaleString('es-CL'));
const bloquea = (p) => (p.exceeds ? 'Sí (zona activa)' : 'No');

async function cargar(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// -----------------------------------------------------------------------------
// MAPA BASE LEAFLET
// -----------------------------------------------------------------------------
const mapa = L.map('mapa').setView([-32.76, -71.47], 12);
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

// Estado de simulación de vuelo y auditoría de costos Dijkstra (Criterio 8)
let simulacionVueloActiva = false;
let simulacionTimerId = null;
let marcadorDronSimulado = null;
let rutaDijkstraActiva = null;

// Foco de contingencia simulado: Planta Asfaltos Quintero (radio 180 m)
const FOCO_SIMULADO = {
  lon: -71.4935,
  lat: -32.7801,
  radio_m: 180.0,
  nombre: 'Escenario de Contingencia: Incendio industrial en Planta Asfaltos Quintero'
};
const LAMBDA_INCENDIO = 5.0; // km^-1, mismo supuesto que ruteo/ruteo_resiliente.py

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
  const sismos = d.sismos.features.filter(f => f.properties.exceeds);
  const vientoActivo = (d.viento?.features || []).filter(f => f.properties.exceeds);
  const lluviaActiva = (d.lluvia?.features || []).filter(f => f.properties.exceeds);

  grafoAristas = d.aristas.features.map(f => {
    const props = f.properties;
    const u = props.source;
    const v = props.target;
    const coordU = grafoNodos[u].coord;
    const coordV = grafoNodos[v].coord;
    const length_m = parseFloat(props.length_m);

    const hayIncendio = aristaTocaPoligonos(coordU, coordV, incendios);
    const haySismo = aristaTocaPoligonos(coordU, coordV, sismos);
    const hayPoblacion = aristaTocaPoligonos(coordU, coordV, manzanasDensas);
    const hayTelecom = aristaTocaPoligonos(coordU, coordV, antenas);
    const hayViento = aristaTocaPoligonos(coordU, coordV, vientoActivo);
    const hayLluvia = aristaTocaPoligonos(coordU, coordV, lluviaActiva);
    const dFoco = distPuntoASegmentoM(coordU, coordV, [FOCO_SIMULADO.lon, FOCO_SIMULADO.lat]);
    const hayEstres = dFoco <= FOCO_SIMULADO.radio_m;

    // Tasa de riesgo física objetiva (Hazard rate por km)
    let hazardRate = 0.005; // Tasa base nominal
    if (hayIncendio) hazardRate += LAMBDA_INCENDIO;   // Riesgo crítico dentro del fuego (el foco simulado se suma solo si el escenario está activo)
    if (hayPoblacion) hazardRate += 0.08;             // Restricción DAN 151
    if (haySismo) hazardRate += 0.05;                 // Oscilación de infraestructuras
    if (!hayTelecom) hazardRate += 0.03;              // Sombra C2
    if (hayViento) hazardRate += 0.04;                // Alerta por viento extremo
    if (hayLluvia) hazardRate += 0.03;                // Precipitaciones sobre umbral

    const item = {
      id: props.id,
      source: u,
      target: v,
      length_m,
      coords: f.geometry.coordinates,
      hayIncendio,
      haySismo,
      hayPoblacion,
      hayTelecom,
      hayViento,
      hayLluvia,
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
      const tasa = edge.hazardRate + (incluirEstres && edge.hayEstres && !edge.hayIncendio ? LAMBDA_INCENDIO : 0);
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
    aviso.textContent = `⚠️ ${nodo.name} (${cat}) es un nodo de paso, no un punto de medición. ` +
      'La ruta se muestra solo como exploración: la misión real apunta a estaciones SINCA o fuentes emisoras.';
  }
}

function actualizarRutasEnVivo() {
  const selOrigen = document.getElementById('select-origen');
  const selDestino = document.getElementById('select-destino');
  if (!selOrigen || !selDestino) return;

  const origenCode = selOrigen.value;
  const destinoCode = selDestino.value;

  const nodoOrig = grafoNodosPorCode[origenCode];
  const nodoDest = grafoNodosPorCode[destinoCode];

  if (!nodoOrig || !nodoDest || origenCode === destinoCode) {
    return;
  }
  mostrarAvisoDestino(nodoDest);

  const origenId = nodoOrig.id;
  const destinoId = nodoDest.id;

  // Preferencias de búsqueda del usuario
  const chkIncendios = document.getElementById('check-incendios').checked;
  const chkPoblacion = document.getElementById('check-poblacion').checked;
  const chkSismos = document.getElementById('check-sismos').checked;
  const chkTelecom = document.getElementById('check-telecom').checked;
  const chkEstres = document.getElementById('check-escenario-estres').checked;
  const verK = document.getElementById('select-k-alternativa').value;

  // Actualizar visibilidad de la capa del foco simulado
  layerEscenarioSimulado.clearLayers();
  if (chkEstres) {
    L.circle([FOCO_SIMULADO.lat, FOCO_SIMULADO.lon], {
      radius: FOCO_SIMULADO.radio_m,
      color: '#dc2626',
      weight: 2,
      fillColor: '#ef4444',
      fillOpacity: 0.45,
    }).bindPopup(tabla([
      ['Amenaza Simulada', FOCO_SIMULADO.nombre],
      ['Radio de afectación', `${FOCO_SIMULADO.radio_m} m`],
      ['Ubicación', `${FOCO_SIMULADO.lat.toFixed(4)}, ${FOCO_SIMULADO.lon.toFixed(4)}`],
    ])).addTo(layerEscenarioSimulado);
  }

  // Costo Dijkstra: longitud geométrica pura
  const costoDijkstra = (edge) => edge.length_m;

  // Costo Resiliente: ponderado por preferencias de usuario
  const costoResiliente = (edge) => {
    let factor = 1.0;
    if (chkIncendios && edge.hayIncendio) factor += 15.0;
    if (chkEstres && edge.hayEstres) factor += 30.0;
    if (chkPoblacion && edge.hayPoblacion) factor += 6.0;
    if (chkSismos && edge.haySismo) factor += 4.0;
    if (chkTelecom && !edge.hayTelecom) factor += 2.5;
    return edge.length_m * factor;
  };

  // Cálculo de K=1 y K=2
  const dijK1 = dijkstraCamino(origenId, destinoId, costoDijkstra, 4.0);
  const dijK2 = dijK1 ? dijkstraCamino(origenId, destinoId, costoDijkstra, 4.0, new Set(dijK1.aristas)) : null;

  const resK1 = dijkstraCamino(origenId, destinoId, costoResiliente, 4.0);
  const resK2 = resK1 ? dijkstraCamino(origenId, destinoId, costoResiliente, 4.0, new Set(resK1.aristas)) : null;

  if (!dijK1 || !resK1) {
    document.getElementById('badge-delta-resiliencia').textContent = 'Ruta no encontrada';
    return;
  }

  // Mapa de aristas para consulta rápida
  const aristasMap = {};
  grafoAristas.forEach(e => { aristasMap[e.id] = e; });

  // Evaluación con la métrica probabilística exacta
  const metDijkstra = evaluarConfiabilidadConjuntoExacta(dijK1.aristas, dijK2 ? dijK2.aristas : [], aristasMap, chkEstres);
  const metResiliente = evaluarConfiabilidadConjuntoExacta(resK1.aristas, resK2 ? resK2.aristas : [], aristasMap, chkEstres);

  const deltaR = metResiliente.resilienciaConjuntoPct - metDijkstra.resilienciaConjuntoPct;

  // Dibujar en el mapa
  layerRutasDijkstra.clearLayers();
  layerRutasResiliente.clearLayers();
  layerMarcadoresExtremos.clearLayers();

  function construirCoords(nodosRuta, aristasRuta) {
    const coords = [grafoNodos[nodosRuta[0]].coord];
    for (let i = 0; i < aristasRuta.length; i++) {
      const eCoords = aristasMap[aristasRuta[i]].coords;
      const last = coords[coords.length - 1];
      const dDir = Math.hypot(eCoords[0][0] - last[0], eCoords[0][1] - last[1]);
      const dInv = Math.hypot(eCoords[eCoords.length - 1][0] - last[0], eCoords[eCoords.length - 1][1] - last[1]);
      const seg = dDir <= dInv ? eCoords : [...eCoords].reverse();
      for (let j = 1; j < seg.length; j++) coords.push(seg[j]);
    }
    return coords.map(c => [c[1], c[0]]); // Leaflet espera [lat, lon]
  }

  const latlngsDijK1 = construirCoords(dijK1.nodos, dijK1.aristas);
  const latlngsResK1 = construirCoords(resK1.nodos, resK1.aristas);

  const mostrarK1 = (verK === '1' || verK === 'k1' || verK === 'ambas');
  const mostrarK2 = (verK === '2' || verK === 'k2' || verK === 'ambas');

  // Rutas Dijkstra
  if (mostrarK1) {
    L.polyline(latlngsDijK1, {
      color: '#ef4444', weight: 4.5, dashArray: '8 6', opacity: 0.9,
    }).bindPopup(`<b>Dijkstra k=1 (Peor Caso)</b><br>Longitud: ${km(metDijkstra.longitudK1M)}<br>Supervivencia: ${metDijkstra.supervivenciaK1Pct.toFixed(1)}%`)
      .addTo(layerRutasDijkstra);
  }

  if (dijK2 && mostrarK2) {
    const latlngsDijK2 = construirCoords(dijK2.nodos, dijK2.aristas);
    L.polyline(latlngsDijK2, {
      color: '#f87171', weight: 3, dashArray: '4 4', opacity: 0.7,
    }).bindPopup(`<b>Dijkstra k=2 (Alternativa)</b><br>Longitud: ${km(metDijkstra.longitudK2M)}<br>Supervivencia: ${metDijkstra.supervivenciaK2Pct.toFixed(1)}%`)
      .addTo(layerRutasDijkstra);
  }

  // Rutas Resilientes
  if (mostrarK1) {
    L.polyline(latlngsResK1, {
      color: '#10b981', weight: 5, opacity: 0.95,
    }).bindPopup(`<b>Resiliente k=1 (Ruta Primaria)</b><br>Longitud: ${km(metResiliente.longitudK1M)}<br>Supervivencia: ${metResiliente.supervivenciaK1Pct.toFixed(1)}%`)
      .addTo(layerRutasResiliente);
  }

  if (resK2 && mostrarK2) {
    const latlngsResK2 = construirCoords(resK2.nodos, resK2.aristas);
    L.polyline(latlngsResK2, {
      color: '#06b6d4', weight: 3.5, opacity: 0.85,
    }).bindPopup(`<b>Resiliente k=2 (Contingencia)</b><br>Longitud: ${km(metResiliente.longitudK2M)}<br>Supervivencia: ${metResiliente.supervivenciaK2Pct.toFixed(1)}%`)
      .addTo(layerRutasResiliente);
  }

  // Marcadores de inicio y fin
  const pOrig = [nodoOrig.coord[1], nodoOrig.coord[0]];
  const pDest = [nodoDest.coord[1], nodoDest.coord[0]];

  L.circleMarker(pOrig, { radius: 9, color: '#065f46', weight: 2, fillColor: '#10b981', fillOpacity: 1 })
    .bindTooltip(`Origen: ${nodoOrig.name}`).addTo(layerMarcadoresExtremos);
  L.circleMarker(pDest, { radius: 9, color: '#7c2d12', weight: 2, fillColor: '#f97316', fillOpacity: 1 })
    .bindTooltip(`Destino: ${nodoDest.name}`).addTo(layerMarcadoresExtremos);

  // Actualizar tarjetas de interfaz
  const signo = deltaR >= 0 ? '+' : '';
  const valDelta = `${signo}${deltaR.toFixed(1)} p.p.`;

  const elemDelta = document.getElementById('diferencial-valor');
  if (elemDelta) {
    elemDelta.textContent = valDelta;
    elemDelta.style.color = deltaR > 0 ? '#34d399' : (deltaR === 0 ? '#60a5fa' : '#f87171');
  }

  const setTxt = (id, txt) => {
    const el = document.getElementById(id);
    if (el) el.textContent = txt;
  };

  // Métricas Dijkstra
  setTxt('dijkstra-distancia', km(metDijkstra.longitudK1M));
  setTxt('dijkstra-supervivencia', `${metDijkstra.supervivenciaK1Pct.toFixed(1)}%`);
  setTxt('dijkstra-amenazas', metDijkstra.amenazasK1.length ? metDijkstra.amenazasK1.join(', ') : 'Ninguna');
  setTxt('conjunto-dijkstra-res', `${metDijkstra.resilienciaConjuntoPct.toFixed(1)}%`);

  // Métricas Resiliente
  setTxt('resiliente-distancia', km(metResiliente.longitudK1M));
  setTxt('resiliente-supervivencia', `${metResiliente.supervivenciaK1Pct.toFixed(1)}%`);
  setTxt('resiliente-amenazas', metResiliente.amenazasK1.length ? metResiliente.amenazasK1.join(', ') : 'Despejada (0 amenazas)');
  setTxt('conjunto-resiliente-res', `${metResiliente.resilienciaConjuntoPct.toFixed(1)}%`);
  setTxt('resiliente-diversidad', `${metResiliente.diversidadPct.toFixed(1)}%`);

  // Actualizar auditoría visual detallada de Dijkstra (Criterio 8 Entrega 2)
  if (typeof actualizarAuditoriaDijkstraUI === 'function') {
    actualizarAuditoriaDijkstraUI(dijK1, nodoOrig, nodoDest, metDijkstra, aristasMap);
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
    style: { color: '#475569', weight: 1.2, opacity: 0.4 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Arista ID', f.properties.id],
      ['Origen → Destino', `${f.properties.source} → ${f.properties.target}`],
      ['Longitud', `${f.properties.length_m} m`],
    ])),
  });

  // 2. Capa Nodos clasificados
  const capaNodos = L.geoJSON(d.nodos, {
    pointToLayer: (f, ll) => L.circleMarker(ll, {
      pane: 'nodos',
      radius: f.properties.category === 'base' ? 8 : (f.properties.category === 'sinca' ? 7 : 5),
      color: '#0f172a', weight: 1.5,
      fillColor: COLOR_CATEGORIA[f.properties.category] ?? '#94a3b8', fillOpacity: 0.95,
    }),
    onEachFeature: (f, l) => {
      l.bindPopup(tabla([
        ['Nombre', f.properties.name],
        ['Categoría', NOMBRE_CATEGORIA[f.properties.category] ?? f.properties.category],
        ['Código', f.properties.code],
      ]));
      l.on('click', (e) => {
        const selOrigen = document.getElementById('select-origen');
        const selDestino = document.getElementById('select-destino');
        if (e.originalEvent.shiftKey) {
          selOrigen.value = f.properties.code;
        } else {
          selDestino.value = f.properties.code;
        }
        actualizarRutasEnVivo();
      });
    },
  });

  // 3. Zonas urbanas
  const capaZonas = L.geoJSON(d.zonas, {
    style: { color: '#0284c7', weight: 1.8, fillColor: '#38bdf8', fillOpacity: 0.12 },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Zona Urbana', f.properties.name || f.properties.nombre || 'Área urbana'],
    ])),
  });

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
      ['Manzana INE', f.properties.block_id || f.properties.manzent],
      ['Población', `${fmt(f.properties.persons)} hab`],
      ['Densidad', `${fmt(f.properties.density_hab_km2)} hab/km²`],
      ['Restricción DAN 151', (f.properties.density_hab_km2 || 0) > 2500 ? 'Zona no sobrevolable' : 'Sobrevolable'],
    ])),
  });

  // 7. Cobertura de antenas OSM
  const capaAntenas = L.geoJSON(d.antenas, {
    style: { color: '#8b5cf6', weight: 1.5, fillColor: '#c4b5fd', fillOpacity: 0.15, dashArray: '4 4' },
    onEachFeature: (f, l) => l.bindPopup(tabla([
      ['Antena C2', f.properties.name || 'Mástil de telecomunicaciones'],
      ['Radio de cobertura', `${f.properties.radius_m || 2000} m`],
    ])),
  });

  // 8. Incendios (NASA FIRMS)
  const capaIncendios = capaAmenaza(d.incendios,
    (p) => (p.exceeds
      ? { color: '#b91c1c', weight: 2, fillColor: '#ef4444', fillOpacity: 0.5 }
      : { color: '#f97316', weight: 1, dashArray: '4 4', fillColor: '#fdba74', fillOpacity: 0.2 }),
    (p) => [
      ['Tipo', 'Incendio satelital (NASA FIRMS)'],
      ['Potencia (FRP)', `${p.value} MW`],
      ['Instrumento', p.instrument],
      ['Confianza', p.confidence],
      ['Zona activa', bloquea(p)],
    ]
  );

  // 9. Sismos (EMSC / CSN)
  const capaSismos = capaAmenaza(d.sismos,
    (p) => (p.exceeds
      ? { color: '#7e22ce', weight: 2, fillColor: '#a855f7', fillOpacity: 0.25 }
      : { color: '#2563eb', weight: 1, dashArray: '4 4', fillColor: '#93c5fd', fillOpacity: 0.12 }),
    (p) => [
      ['Tipo', 'Evento Sísmico'],
      ['Magnitud', p.value],
      ['Profundidad', `${p.depth_km} km`],
      ['Radio de afectación', `${p.affect_radius_km} km`],
      ['Zona activa', bloquea(p)],
    ]
  );

  // 10. Viento (Open-Meteo)
  const capaViento = capaAmenaza(d.viento,
    (p) => ({
      color: p.exceeds ? '#b91c1c' : '#16a34a', weight: 1,
      fillColor: p.exceeds ? '#ef4444' : '#4ade80', fillOpacity: 0.25,
    }),
    (p) => [
      ['Ráfaga 10 m', `${p.value} m/s`],
      ['Viento 10 m', `${p.wind_speed_10m} m/s (${p.wind_direction_10m}°)`],
      ['Viento 120 m', `${p.wind_speed_120m} m/s`],
      ['Umbral operacional', `${p.threshold} m/s`],
      ['Zona activa', bloquea(p)],
    ]
  );

  // 11. Lluvia (MET Norway)
  const capaLluvia = capaAmenaza(d.lluvia,
    (p) => ({
      color: p.exceeds ? '#1e3a8a' : '#0284c7', weight: 1,
      fillColor: p.exceeds ? '#1d4ed8' : '#7dd3fc', fillOpacity: 0.3,
    }),
    (p) => [
      ['Precipitación', `${p.value} mm/h`],
      ['Umbral IPx4', `${p.threshold} mm/h`],
      ['Condición', p.symbol_code],
      ['Zona activa', bloquea(p)],
    ]
  );

  // 12. Ruta oficial pgr_dijkstra generada por PostgreSQL
  if (d.rutas_pgrouting && d.rutas_pgrouting.features) {
    L.geoJSON(d.rutas_pgrouting, {
      style: (f) => (f.properties.k === 2
        ? { color: '#fb923c', weight: 2.5, dashArray: '2 6', opacity: 0.8 }
        : { color: '#ea580c', weight: 3, dashArray: '6 6', opacity: 0.8 }),
      onEachFeature: (f, l) => l.bindPopup(tabla([
        ['Ruta pgRouting', `pgr_dijkstra en BD (k=${f.properties.k})`],
        ['Destino', f.properties.destino_nombre || f.properties.destino],
        ['Longitud', km(f.properties.longitud_m)],
        ['Costo pgRouting', `${fmt(f.properties.costo)} m`],
        ['Tramos', f.properties.tramos],
      ])),
    }).addTo(layerRutaPgrouting);
  }

  const overlays = {
    'Rutas Resilientes (Akgün / Kosior)': layerRutasResiliente,
    'Rutas Dijkstra (Peor Caso reactivo)': layerRutasDijkstra,
    'Ruta pgr_dijkstra (Base de Datos)': layerRutaPgrouting,
    'Escenario de Contingencia (Quintero)': layerEscenarioSimulado,
    'Infraestructura · Nodos': capaNodos,
    'Infraestructura · Aristas': capaAristas,
    'Infraestructura · Zonas urbanas': capaZonas,
    'Metadata · Calidad del aire (SINCA)': capaAire,
    'Metadata · Relieve por arista (SRTM)': capaRelieve,
    'Metadata · Manzanas pobladas (INE)': capaManzanas,
    'Metadata · Cobertura antenas (OSM)': capaAntenas,
    'Amenaza · Incendios (NASA FIRMS)': capaIncendios,
    'Amenaza · Sismos (EMSC / CSN)': capaSismos,
    'Amenaza · Viento (Open-Meteo)': capaViento,
    'Amenaza · Lluvia (MET Norway)': capaLluvia,
  };

  const controlCapas = {};
  Object.entries(overlays).forEach(([nom, layer]) => {
    controlCapas[nom] = layer;
    if ([
      'Rutas Resilientes (Akgün / Kosior)',
      'Rutas Dijkstra (Peor Caso reactivo)',
      'Infraestructura · Nodos',
      'Infraestructura · Zonas urbanas',
    ].includes(nom)) {
      layer.addTo(mapa);
    }
  });

  L.control.layers(capasBase, controlCapas, { collapsed: true, position: 'topright' }).addTo(mapa);
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

  let htmlOptions = '';
  const ordenCategorias = [...new Set([...Object.keys(NOMBRE_CATEGORIA), ...Object.keys(categorias)])];
  ordenCategorias.forEach(cat => {
    if (categorias[cat]) {
      const nombreCat = NOMBRE_CATEGORIA[cat] || cat;
      const etiqueta = DESTINOS_MEDICION.has(cat) ? `${nombreCat} · punto de medición`
        : (cat === 'base' ? nombreCat : `${nombreCat} · nodo de paso`);
      htmlOptions += `<optgroup label="--- ${etiqueta} ---">`;
      categorias[cat].sort((a, b) => a.name.localeCompare(b.name)).forEach(p => {
        htmlOptions += `<option value="${p.code}">${p.name} (${p.city || 'Quintero'})</option>`;
      });
      htmlOptions += `</optgroup>`;
    }
  });

  selOrigen.innerHTML = htmlOptions;
  selDestino.innerHTML = htmlOptions;

  selOrigen.value = 'base_scer';
  selDestino.value = 'sinca_puchuncavi';

  // Inicializar capas cartográficas
  inicializarCapasCartograficas(d);

  // Event Listeners interactivos
  selOrigen.addEventListener('change', actualizarRutasEnVivo);
  selDestino.addEventListener('change', actualizarRutasEnVivo);
  document.getElementById('select-k-alternativa').addEventListener('change', actualizarRutasEnVivo);

  ['check-incendios', 'check-poblacion', 'check-sismos', 'check-telecom', 'check-escenario-estres'].forEach(id => {
    document.getElementById(id).addEventListener('change', actualizarRutasEnVivo);
  });

  document.getElementById('btn-default-restricciones').addEventListener('click', () => {
    document.getElementById('check-incendios').checked = true;
    document.getElementById('check-poblacion').checked = true;
    document.getElementById('check-sismos').checked = true;
    document.getElementById('check-telecom').checked = true;
    document.getElementById('check-escenario-estres').checked = false;
    actualizarRutasEnVivo();
  });

  // Resumen en panel lateral
  const suma = (lista, c) => lista.reduce((s, f) => s + (f.properties[c] || 0), 0);
  document.getElementById('resumen').innerHTML = [
    ['Nodos de la red', d.nodos.features.length],
    ['Aristas de vuelo', `${d.aristas.features.length} (${(suma(d.aristas.features, 'length_m') / 1000).toFixed(1)} km)`],
    ['Zonas urbanas', d.zonas.features.length],
    ['Estaciones SINCA', d.aire.features.length],
    ['Perfiles SRTM', d.relieve.features.length],
    ['Manzanas censales (INE)', fmt(d.manzanas.features.length)],
    ['Antenas de telecom', d.antenas.features.length],
    ['Incendios satelitales', d.incendios.features.length],
    ['Sismos en registro', d.sismos.features.length],
  ].map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('');

  const conteo = {};
  d.nodos.features.forEach(f => { conteo[f.properties.category] = (conteo[f.properties.category] || 0) + 1; });
  document.getElementById('leyenda').innerHTML = Object.keys(COLOR_CATEGORIA)
    .filter(c => conteo[c])
    .map(c => `<li><span class="punto" style="background:${COLOR_CATEGORIA[c]}"></span>${esc(NOMBRE_CATEGORIA[c])} <b>${conteo[c]}</b></li>`)
    .join('');

  // Primera ejecución de rutas en el simulador
  actualizarRutasEnVivo();

  // Configurar navegación de módulos
  configurarNavegacionModulos(d);

  // Inicializar módulos de Entrega 2
  inicializarModuloInfraestructura(d);
  inicializarModuloMetadata(d);
  inicializarModuloAmenazas(d);
  inicializarModuloDocumentacion(d);
  inicializarAuditoriaDijkstra(d);
}

// =============================================================================
// GESTIÓN DE NAVEGACIÓN ENTRE MÓDULOS (ENTREGA 2)
// =============================================================================
function configurarNavegacionModulos(d) {
  const tabBtnSimulador = document.getElementById('tab-btn-simulador');
  const tabBtnInfra = document.getElementById('tab-btn-infraestructura');
  const tabBtnMeta = document.getElementById('tab-btn-metadata');
  const tabBtnAmenazas = document.getElementById('tab-btn-amenazas');
  const tabBtnDoc = document.getElementById('tab-btn-documentacion');
  const tabBtnPauta = document.getElementById('tab-btn-pauta');

  const vistaSimulador = document.getElementById('vista-simulador');
  const vistaInfra = document.getElementById('vista-infraestructura');
  const vistaMeta = document.getElementById('vista-metadata');
  const vistaAmenazas = document.getElementById('vista-amenazas');
  const vistaDoc = document.getElementById('vista-documentacion');
  const vistaPauta = document.getElementById('vista-pauta');

  function cambiarPestaña(tab) {
    [tabBtnSimulador, tabBtnInfra, tabBtnMeta, tabBtnAmenazas, tabBtnDoc, tabBtnPauta].forEach(btn => btn?.classList.remove('active'));
    [vistaSimulador, vistaInfra, vistaMeta, vistaAmenazas, vistaDoc, vistaPauta].forEach(v => { if (v) v.hidden = true; });

    if (tab === 'simulador') {
      tabBtnSimulador.classList.add('active');
      vistaSimulador.hidden = false;
      mapa.invalidateSize();
    } else if (tab === 'infraestructura') {
      tabBtnInfra.classList.add('active');
      vistaInfra.hidden = false;
      if (!mapaInfraInicializado) {
        montarMapaInfra(d);
      } else if (mapaInfra) {
        mapaInfra.invalidateSize();
      }
    } else if (tab === 'metadata') {
      tabBtnMeta.classList.add('active');
      vistaMeta.hidden = false;
      if (!mapaMetaInicializado) {
        montarMapaMeta(d);
      } else if (mapaMeta) {
        mapaMeta.invalidateSize();
      }
    } else if (tab === 'amenazas') {
      tabBtnAmenazas.classList.add('active');
      vistaAmenazas.hidden = false;
      if (!mapaAmenazasInicializado) {
        montarMapaAmenazas(d);
      } else if (mapaAmenazas) {
        mapaAmenazas.invalidateSize();
      }
    } else if (tab === 'documentacion') {
      tabBtnDoc.classList.add('active');
      vistaDoc.hidden = false;
    } else if (tab === 'pauta') {
      tabBtnPauta?.classList.add('active');
      if (vistaPauta) vistaPauta.hidden = false;
    }
  }

  tabBtnSimulador.addEventListener('click', () => cambiarPestaña('simulador'));
  tabBtnInfra.addEventListener('click', () => cambiarPestaña('infraestructura'));
  if (tabBtnMeta) tabBtnMeta.addEventListener('click', () => cambiarPestaña('metadata'));
  if (tabBtnAmenazas) tabBtnAmenazas.addEventListener('click', () => cambiarPestaña('amenazas'));
  if (tabBtnDoc) tabBtnDoc.addEventListener('click', () => cambiarPestaña('documentacion'));
  if (tabBtnPauta) tabBtnPauta.addEventListener('click', () => cambiarPestaña('pauta'));

  const btnPautaSim = document.getElementById('btn-pauta-ir-simulador');
  if (btnPautaSim) {
    btnPautaSim.addEventListener('click', () => cambiarPestaña('simulador'));
  }
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
      referencia_rubrica: "Ítem 1 Entrega 2",
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
// MÓDULO DE METADATA (CRITERIO 2 Y 3.1 RÚBRICA ENTREGA 2)
// =============================================================================
let mapaMeta = null;
let mapaMetaInicializado = false;

function inicializarModuloMetadata(d) {
  // 1. Poblar KPIs de Metadata
  document.getElementById('kpi-meta-sinca').textContent = d.aire.features.length;
  document.getElementById('kpi-meta-srtm').textContent = d.relieve.features.length;
  document.getElementById('kpi-meta-ine').textContent = d.manzanas.features.length;
  document.getElementById('kpi-meta-antenas').textContent = d.antenas.features.length;

  // 2. Descargar Todo Consolidado de Metadata
  const btnDl = document.getElementById('btn-descargar-todo-metadata');
  if (btnDl) {
    btnDl.addEventListener('click', () => {
      const paqueteMeta = {
        descripcion: "Metadata Territorial y Operacional · Bahía de Quintero",
        referencia_rubrica: "Criterios 2 y 3.1 Entrega 2",
        fecha_exportacion: new Date().toISOString(),
        fuentes: {
          sinca_calidad_aire: d.aire,
          srtm_relieve: d.relieve,
          ine_manzanas: d.manzanas,
          osm_antenas: d.antenas,
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

  setTimeout(() => {
    mapaMeta.invalidateSize();
  }, 250);
}

// =============================================================================
// MÓDULO DE AMENAZAS (CRITERIOS 3, 4.1, 4.2, 5.1, 5.2 Y 6 RÚBRICA ENTREGA 2)
// =============================================================================
let mapaAmenazas = null;
let mapaAmenazasInicializado = false;

function inicializarModuloAmenazas(d) {
  // 1. Poblar KPIs de Amenazas
  document.getElementById('kpi-amenaza-incendios').textContent = `${d.incendios.features.length} foco`;
  document.getElementById('kpi-amenaza-sismos').textContent = `${d.sismos.features.length} sismos`;
  document.getElementById('kpi-amenaza-viento').textContent = `${d.viento.features.length} celdas`;
  document.getElementById('kpi-amenaza-lluvia').textContent = `${d.lluvia.features.length} celdas`;

  // 2. Descargar Todo Consolidado de Amenazas
  const btnDl = document.getElementById('btn-descargar-todo-amenazas');
  if (btnDl) {
    btnDl.addEventListener('click', () => {
      const paqueteAmenazas = {
        descripcion: "Amenazas Dinámicas y Eventos de Falla · Bahía de Quintero",
        marco_metodologico: "NASA FIRMS (incendios) + EMSC/CSN (sismos) + Open-Meteo (viento) + MET Norway (lluvia)",
        referencia_rubrica: "Criterios 3, 4.1, 4.2, 5.1, 5.2 y 6 Entrega 2",
        modelo_bd: "PostgreSQL 16 + PostGIS 3.4 (tabla threat_event)",
        fecha_exportacion: new Date().toISOString(),
        fuentes: {
          firms_incendios: d.incendios,
          csn_sismos: d.sismos,
          openmeteo_viento: d.viento,
          metno_lluvia: d.lluvia,
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
    csn: {
      nombre: 'csn_sismos',
      archivoGeojson: '../amenazas/csn_sismos.geojson',
      archivoScript: '../amenazas/csn_sismos.py',
      archivoCarga: '../amenazas/cargar_csn_sismos.py',
      archivoDoc: '../amenazas/csn_sismos.md',
      dataRef: d.sismos,
      tablaBD: 'threat_event (event_type = \'sismo\')',
      desc: `${d.sismos.features.length} Sismos (30 días) · EMSC FDSN / CSN U. de Chile`,
    },
    viento: {
      nombre: 'openmeteo_viento',
      archivoGeojson: '../amenazas/openmeteo_viento.geojson',
      archivoScript: '../amenazas/openmeteo_viento.py',
      archivoCarga: '../amenazas/cargar_openmeteo_viento.py',
      archivoDoc: '../amenazas/openmeteo_viento.md',
      dataRef: d.viento,
      tablaBD: 'threat_event (event_type = \'viento\')',
      desc: `${d.viento.features.length} Celdas 4×4 · Open-Meteo Forecast API`,
    },
    lluvia: {
      nombre: 'metno_lluvia',
      archivoGeojson: '../amenazas/metno_lluvia.geojson',
      archivoScript: '../amenazas/metno_lluvia.py',
      archivoCarga: '../amenazas/cargar_metno_lluvia.py',
      archivoDoc: '../amenazas/metno_lluvia.md',
      dataRef: d.lluvia,
      tablaBD: 'threat_event (event_type = \'lluvia\')',
      desc: `${d.lluvia.features.length} Celdas 4×4 · MET Norway Locationforecast`,
    },
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
        'Regla de Pesos (Criterio 5.2)': isExceed ? 'Inhabilita aristas que cruzan la celda (C = ∞)' : 'Modula velocidad terrestre v_g y consumo EEE por viento de frente',
      });
    });
    poly.addTo(layerViento);
  });

  // 3. Grilla de Lluvia (MET Norway)
  d.lluvia.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;
    const poly = L.polygon(ring, {
      color: isExceed ? '#dc2626' : '#60a5fa',
      weight: isExceed ? 2 : 1,
      fillColor: isExceed ? '#dc2626' : '#3b82f6',
      fillOpacity: isExceed ? 0.38 : Math.max(0.06, Math.min(0.25, p.value * 0.1)),
    });
    poly.on('click', () => {
      mostrarEnAmenazaInspector('Precipitación (MET Norway)', `Celda ${p.cell} · ${p.external_id}`, {
        'Tipo de Evento': 'lluvia',
        'Celda Espacial': p.cell,
        'Precipitación Prevista': `${p.value} ${p.unit} (próxima hora)`,
        'Condición Meteorológica': p.symbol_code || 'No reportada',
        'Umbral Crítico': `${p.threshold} mm/h`,
        'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (No-Go por agua)</span>' : '<span class="text-good">OPERACIONAL</span>',
        'Periodo Válido': `${p.observed_at} → ${p.valid_until || '—'}`,
        'Regla de Pesos (Criterio 5.2)': isExceed ? 'Inhabilita aristas; activa retorno de emergencia LPP hacia sotavento' : 'Vuelo permitido con sensores ópticos en condiciones estándar',
      });
    });
    poly.addTo(layerLluvia);
  });

  // 4. Sismos (CSN / EMSC)
  d.sismos.features.forEach(f => {
    const p = f.properties;
    const ring = f.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
    const isExceed = p.exceeds;
    const isBaseAffected = p.base_dentro_radio;

    const poly = L.polygon(ring, {
      color: isExceed ? '#ef4444' : '#a855f7',
      weight: isExceed ? 2 : 1,
      fillColor: isExceed ? '#f59e0b' : '#a855f7',
      fillOpacity: isExceed ? 0.22 : 0.06,
    });

    const marker = L.circleMarker([p.lat, p.lon], {
      radius: Math.max(4, Math.min(12, p.value * 1.6)),
      color: isExceed ? '#fef08a' : '#d97706',
      fillColor: isExceed ? '#ef4444' : '#d97706',
      fillOpacity: 0.85,
      weight: 1.5,
    });

    const handler = () => {
      mostrarEnAmenazaInspector('Evento Sísmico (CSN / EMSC)', `${p.region || 'Sismo'} · M ${p.value}`, {
        'Tipo de Evento': 'sismo',
        'ID Externo (EMSC unid)': p.external_id,
        'Magnitud': `${p.value} (${p.unit})`,
        'Profundidad': `${p.depth_km} km`,
        'Autoría': p.authority || 'CSN (U. de Chile)',
        'Radio de Afectación': `${p.affect_radius_km ? p.affect_radius_km.toFixed(1) : '—'} km (heurística intensidad ≥ VI)`,
        'Distancia a Base Quintero': `${p.distance_to_base_km ? p.distance_to_base_km.toFixed(1) : '—'} km`,
        'Afectación a Base': isBaseAffected ? '<span class="text-bad">Base dentro del radio de daño</span>' : 'Base fuera de zona crítica',
        'Estado (exceeds)': isExceed ? '<span class="text-bad">ACTIVO (M ≥ 5.0)</span>' : 'Baja intensidad (M < 5.0)',
        'Fecha Observación': p.observed_at,
        'Regla de Pesos (Criterio 5.2)': isBaseAffected
          ? 'Deshabilita base aérea de Quintero por corte eléctrico; fuerza desvío a vertipuerto auxiliar o RTH'
          : 'Monitoreo preventivo sin corte de nodos base',
      });
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
        'Regla de Pesos (Criterio 5.2)': 'Bloqueo estricto e insalvable (C = ∞) de todas las aristas que intersectan el radio de 2 km',
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
// MÓDULO DE DOCUMENTACIÓN Y ESTRUCTURA DE DATOS (CRITERIO 4 DE LA PAUTA)
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
    csn_sismos: {
      id: 'csn_sismos',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/csn_sismos.geojson',
      nombreDatos: 'csn_sismos.geojson',
      archivoDoc: '../amenazas/csn_sismos.md',
      nombreDoc: 'csn_sismos.md',
      scriptGenerador: 'amenazas/csn_sismos.py',
      tablaBD: 'threat_event (sismo)',
      tipoGeom: 'Polygon (atenuación)',
      entidades: `${d.sismos?.features?.length || 98} sismos`,
      resumen: '98 sismos (30 días) EMSC/CSN con modelo R = 10^(0.5M-1.8) y daño a bases.',
      datosRef: d.sismos,
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
      resumen: '16 celdas espaciales con ráfagas a 10m y viento a 120m (umbral No-Go 14 m/s).',
      datosRef: d.viento,
    },
    metno_lluvia: {
      id: 'metno_lluvia',
      dominio: 'Amenazas',
      archivoDatos: '../amenazas/metno_lluvia.geojson',
      nombreDatos: 'metno_lluvia.geojson',
      archivoDoc: '../amenazas/metno_lluvia.md',
      nombreDoc: 'metno_lluvia.md',
      scriptGenerador: 'amenazas/metno_lluvia.py',
      tablaBD: 'threat_event (lluvia)',
      tipoGeom: 'Polygon (grilla 4×4)',
      entidades: `${d.lluvia?.features?.length || 16} celdas`,
      resumen: '16 celdas con precipitación prevista en mm/h para la próxima hora (umbral 2.0 mm/h).',
      datosRef: d.lluvia,
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
        titulo: "Diccionario Maestro de Datos y Especificaciones (Criterio 4 de la Pauta)",
        total_archivos: Object.keys(CATALOGO_ARCHIVOS).length,
        norma_geoespacial: "RFC 7946 / EPSG:4326 (WGS84)",
        referencia_pauta: "Ítem 4 Entrega 2: Archivo descriptivo .md por cada .json o .geojson",
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
// AUDITORÍA INTERACTIVA DE COSTOS DIJKSTRA Y SIMULACIÓN UAV (CRITERIO 8)
// "El sitio deberá mostrar una ruta generada con pgr_dijkstra, utilizando la
//  longitud de la ruta como costo, que muestre a modo de ejemplo una ruta que
//  sea una posible solución a su problema planteado. Esta ruta será el peor caso
//  que podría resolver su problemática, ya que no considerará la metadata ni
//  las posibles amenazas."
// =============================================================================

function inicializarAuditoriaDijkstra(d) {
  const btnInspeccionar = document.getElementById('btn-abrir-auditoria-dijkstra');
  const hud = document.getElementById('hud-dijkstra-costos');
  const btnCerrar = document.getElementById('btn-hud-cerrar');
  const btnVuelo = document.getElementById('btn-hud-play-vuelo');
  const contenedorSinca = document.getElementById('pgrouting-sinca-buttons');

  if (btnInspeccionar && hud) {
    btnInspeccionar.addEventListener('click', () => {
      hud.hidden = !hud.hidden;
      if (!hud.hidden) {
        if (rutaDijkstraActiva) {
          actualizarAuditoriaDijkstraUI(
            rutaDijkstraActiva.dijK1,
            rutaDijkstraActiva.nodoOrig,
            rutaDijkstraActiva.nodoDest,
            rutaDijkstraActiva.metDijkstra,
            rutaDijkstraActiva.aristasMap
          );
        } else {
          actualizarRutasEnVivo();
        }
      } else {
        detenerSimulacionVuelo();
      }
    });
  }

  if (btnCerrar && hud) {
    btnCerrar.addEventListener('click', () => {
      hud.hidden = true;
      detenerSimulacionVuelo();
    });
  }

  if (btnVuelo) {
    btnVuelo.addEventListener('click', () => {
      if (simulacionVueloActiva) {
        detenerSimulacionVuelo();
      } else {
        simularVueloUav();
      }
    });
  }

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
      btn.innerHTML = `${esc(nomCorto)} <span style="opacity:0.75;font-size:0.65rem;">${(props.longitud_m / 1000).toFixed(1)}k</span>`;
      btn.title = `Ruta pgr_dijkstra oficial en BD:\n${props.destino_nombre}\nLongitud: ${props.longitud_m} m\nTramos: ${props.tramos}\nCosto: length_m (peor caso)`;

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
        if (hud) hud.hidden = false;
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

      let riesgoBadgeHtml = '<span class="hud-step-risk risk-safe">✅ TRAMO DESPEJADO</span>';
      if (t.hayFuego) {
        riesgoBadgeHtml = '<span class="hud-step-risk risk-danger">🔥 FUEGO / PLUMA ACTIVA</span>';
      } else if (t.hayPoblacion) {
        riesgoBadgeHtml = '<span class="hud-step-risk risk-danger">🏢 DAN 151 URBANO</span>';
      } else if (t.sinTelecom) {
        riesgoBadgeHtml = '<span class="hud-step-risk" style="background:rgba(139,92,246,0.2);color:#c4b5fd;border:1px solid rgba(139,92,246,0.4);">📡 SIN ENLACE C2</span>';
      } else if (t.haySismo) {
        riesgoBadgeHtml = '<span class="hud-step-risk" style="background:rgba(234,179,8,0.2);color:#facc15;border:1px solid rgba(234,179,8,0.4);">⚠️ ALERTA SÍSMICA</span>';
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
  const riesgoTexto = t.hayFuego ? '🔥 Pluma de fuego / Incendio'
    : (t.hayPoblacion ? '🏢 Zona urbana densa (DAN 151)'
    : (t.sinTelecom ? '📡 Sin enlace de telemetría C2' : '✅ Nominal'));

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
  if (btnVuelo) btnVuelo.textContent = '▶ Simular Vuelo';

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
  if (btnVuelo) btnVuelo.textContent = '⏸ Pausar Vuelo';

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
        if (btnVuelo) btnVuelo.textContent = '↺ Reiniciar Vuelo';
        if (statusInfo) {
          statusInfo.textContent = '🏁 Destino alcanzado (Misión fallida en peor caso)';
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
          statusInfo.textContent = '🔥 ALERTA: FUEGO ACTIVO / PLUMA';
          statusInfo.className = 'text-bad';
        }
      } else if (t.hayPoblacion) {
        if (telemBox) telemBox.classList.add('telemetry-alert');
        if (radarPulse) radarPulse.classList.add('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = '🏢 ALERTA: ZONA URBANA (DAN 151)';
          statusInfo.className = 'text-bad';
        }
      } else if (t.sinTelecom) {
        if (telemBox) telemBox.classList.add('telemetry-alert');
        if (radarPulse) radarPulse.classList.remove('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = '📡 ALERTA: PÉRDIDA ENLACE C2';
          statusInfo.className = 'text-warning';
        }
      } else {
        if (telemBox) telemBox.classList.remove('telemetry-alert');
        if (radarPulse) radarPulse.classList.remove('danger-pulse');
        if (statusInfo) {
          statusInfo.textContent = '✅ Vuelo nominal';
          statusInfo.className = 'text-good';
        }
      }
    }

    pIdx++;
  }, 220);
}

iniciar();


