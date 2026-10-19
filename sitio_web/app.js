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

// Foco de contingencia simulado: Planta Asfaltos Quintero (radio 180 m)
const FOCO_SIMULADO = {
  lon: -71.4935,
  lat: -32.7801,
  radio_m: 180.0,
  nombre: 'Escenario de Contingencia: Incendio industrial en Planta Asfaltos Quintero'
};

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
    if (hayIncendio || hayEstres) hazardRate += 5.0; // Riesgo crítico dentro del fuego
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
function evaluarConfiabilidadConjuntoExacta(aristasK1, aristasK2, aristasMap) {
  const s1 = new Set(aristasK1);
  const s2 = new Set(aristasK2 || []);
  const ec = new Set([...s1].filter(x => s2.has(x)));
  const e1Only = new Set([...s1].filter(x => !s2.has(x)));
  const e2Only = new Set([...s2].filter(x => !s1.has(x)));

  function surv(edgeSet) {
    let h = 0.0;
    edgeSet.forEach(eid => {
      const edge = aristasMap[eid];
      if (edge) h += edge.hazardRate * (edge.length_m / 1000.0);
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
      if (e.hayIncendio || e.hayEstres) amenazasK1.add('Incendio');
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
  const metDijkstra = evaluarConfiabilidadConjuntoExacta(dijK1.aristas, dijK2 ? dijK2.aristas : [], aristasMap);
  const metResiliente = evaluarConfiabilidadConjuntoExacta(resK1.aristas, resK2 ? resK2.aristas : [], aristasMap);

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

  // Poblar selectores de Origen y Destino (94 nodos principales clasificados)
  const selOrigen = document.getElementById('select-origen');
  const selDestino = document.getElementById('select-destino');

  const categorias = {};
  d.nodos.features.forEach(f => {
    const cat = f.properties.category || 'otros';
    if (!categorias[cat]) categorias[cat] = [];
    categorias[cat].push(f.properties);
  });

  let htmlOptions = '';
  ['base', 'sinca', 'health', 'education', 'emission_source', 'commercial'].forEach(cat => {
    if (categorias[cat]) {
      const nombreCat = NOMBRE_CATEGORIA[cat] || cat;
      htmlOptions += `<optgroup label="--- ${nombreCat} ---">`;
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

  // Primera ejecución de rutas
  actualizarRutasEnVivo();
}

iniciar();
