/* ============================================================================
 * fase3.js — Panel de comparación de las 4 técnicas de ruteo (Fase 3)
 *
 * Consume la API de api/servidor.py:
 *   GET /api/destinos    -> selector de destino
 *   GET /api/capas       -> checkboxes de amenazas y metadatos
 *   GET /api/rutas       -> 4 técnicas: geometrías + métricas para la leyenda
 *   GET /api/simulacion  -> una realización Monte Carlo (u ∈ [0,100) por elemento)
 *
 * Se carga después de app.js, que ya creó el mapa Leaflet en la constante `mapa`.
 * No modifica nada de app.js: dibuja en sus propias capas.
 * ========================================================================== */
(function () {
  'use strict';

  const TECNICAS = ['dijkstra_distancia', 'milp_exacto', 'dijkstra_multicriterio', 'metaheuristica_akgun'];

  // Capa de rutas por técnica + capa de fallas simuladas.
  const capasRuta = {};
  let capaFallas = null;
  let ultimaConsulta = null;   // parámetros de la última llamada a /api/rutas
  let ultimaRespuesta = null;
  const visibles = new Set(TECNICAS);

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (m) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]));
  const num = (v, d = 2) => (v === null || v === undefined ? '—' : Number(v).toFixed(d));

  function mapaListo() {
    return typeof mapa !== 'undefined' && mapa && typeof mapa.addLayer === 'function';
  }

  function estado(txt, tipo) {
    const el = $('f3-estado');
    if (!el) return;
    el.textContent = txt || '';
    el.className = 'f3-estado' + (tipo ? ' f3-estado-' + tipo : '');
  }

  async function pedir(url) {
    const r = await fetch(url);
    if (!r.ok) {
      let detalle = r.statusText;
      try { detalle = (await r.json()).detail || detalle; } catch (e) { /* respuesta sin JSON */ }
      throw new Error(`${r.status} · ${typeof detalle === 'string' ? detalle : JSON.stringify(detalle)}`);
    }
    return r.json();
  }

  // --------------------------------------------------------------------------
  // Conteos del grafo en vivo: evita que la cabecera y los KPI se desfasen
  // cuando se agregan nodos y el extractor regenera las aristas.
  // --------------------------------------------------------------------------
  async function conteosReales() {
    try {
      const [n, a] = await Promise.all([
        pedir('../infraestructura/nodos.geojson'),
        pedir('../infraestructura/aristas.geojson'),
      ]);
      const nodos = n.etl?.total ?? n.features.length;
      const aristas = a.etl?.total ?? a.features.length;

      const badge = document.querySelector('.status-badge');
      if (badge) {
        badge.innerHTML = `<span class="dot-live"></span> Red Conexa &middot; ${nodos} Nodos &middot; ${aristas} Aristas`;
      }
      const kn = $('kpi-grafo-nodos');
      if (kn) kn.textContent = nodos;
      const ka = $('kpi-grafo-aristas');
      if (ka) ka.textContent = aristas;
    } catch (e) {
      /* si falla, quedan los valores del HTML */
    }
  }

  // --------------------------------------------------------------------------
  // Carga inicial: destinos y capas
  // --------------------------------------------------------------------------
  async function iniciar() {
    conteosReales();
    try {
      const [dest, capas] = await Promise.all([pedir('/api/destinos'), pedir('/api/capas')]);

      const sel = $('f3-destino');
      sel.innerHTML = dest.destinos
        .map((d) => `<option value="${esc(d.code)}">${esc(d.name)}</option>`).join('');
      sel.value = 'sinca_ventanas';

      const activas = new Set(capas.por_defecto);
      $('f3-capas').innerHTML = capas.capas.map((c) => `
        <label class="f3-check" for="f3-capa-${esc(c.id)}" title="${esc(c.descripcion)}">
          <input type="checkbox" id="f3-capa-${esc(c.id)}" data-capa="${esc(c.id)}"
                 ${activas.has(c.id) ? 'checked' : ''}>
          <span>${esc(c.descripcion)}</span>
        </label>`).join('');

      estado('Listo. Elige destino y restricciones, luego calcula las rutas.');
    } catch (e) {
      estado('No se pudo contactar la API: ' + e.message + '. Levanta el backend con "docker compose up -d web".', 'error');
    }
  }

  const capasActivas = () =>
    [...document.querySelectorAll('#f3-capas input[data-capa]:checked')].map((i) => i.dataset.capa);

  function parametros() {
    const p = new URLSearchParams();
    p.set('destino', $('f3-destino').value);
    p.set('autonomia_max', $('f3-autonomia').value || '10500');
    p.set('beta', $('f3-beta').value || '1000');
    p.set('capas', capasActivas().join(','));
    p.set('backend', $('f3-backend').value);
    if ($('f3-contingencia').checked) p.set('contingencia', 'true');
    return p;
  }

  // --------------------------------------------------------------------------
  // /api/rutas — dibuja las 4 técnicas y arma la leyenda
  // --------------------------------------------------------------------------
  async function calcular() {
    const btn = $('f3-calcular');
    btn.disabled = true;
    estado('Resolviendo las 4 técnicas…', 'cargando');
    try {
      const p = parametros();
      const mcN = parseInt($('f3-mcn').value, 10) || 0;
      if (mcN > 0) {
        p.set('mc_n', String(mcN));
        p.set('seed', $('f3-seed').value || '42');
      }
      ultimaConsulta = p;
      const data = await pedir('/api/rutas?' + p.toString());
      ultimaRespuesta = data;
      dibujar(data);
      leyenda(data);
      $('f3-leyenda-wrap').hidden = false;
      $('f3-simular').hidden = false;
      $('f3-sim').hidden = true;
      limpiarFallas();

      const ok = Object.values(data.tecnicas).filter((t) => t.estado === 'ok').length;
      const mejor = data.mejor_resiliencia ? nombreCorto(data.mejor_resiliencia) : 'ninguna';
      estado(`${ok} de 4 técnicas con ruta. Más resiliente: ${mejor}.`, ok ? 'ok' : 'aviso');
    } catch (e) {
      estado('Error: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  }

  const nombreCorto = (tid) => ({
    dijkstra_distancia: 'Dijkstra distancia',
    milp_exacto: 'MILP exacto',
    dijkstra_multicriterio: 'Dijkstra multicriterio',
    metaheuristica_akgun: 'Metaheurística Akgün',
  }[tid] || tid);

  function limpiarRutas() {
    Object.values(capasRuta).forEach((c) => { if (mapaListo()) mapa.removeLayer(c); });
    TECNICAS.forEach((t) => delete capasRuta[t]);
  }

  function dibujar(data) {
    if (!mapaListo()) return;
    limpiarRutas();

    data.features.forEach((f) => {
      const pr = f.properties;
      const tid = pr.tecnica;
      if (!capasRuta[tid]) capasRuta[tid] = L.layerGroup();

      const latlngs = f.geometry.coordinates.map((c) => [c[1], c[0]]);
      const alternativa = pr.rol === 'alternativa';

      // Halo oscuro debajo para que la ruta se lea sobre cualquier basemap.
      L.polyline(latlngs, { color: '#0f172a', weight: alternativa ? 7 : 9, opacity: 0.35 })
        .addTo(capasRuta[tid]);
      const linea = L.polyline(latlngs, {
        color: pr.color,
        weight: alternativa ? 3 : 5,
        opacity: 0.95,
        dashArray: alternativa ? '7 6' : null,
      }).addTo(capasRuta[tid]);

      linea.bindPopup(`
        <div class="f3-popup">
          <b>${esc(pr.nombre)}</b>
          ${alternativa ? '<span class="f3-tag">camino alternativo</span>' : ''}
          ${pr.mejor_resiliencia ? '<span class="f3-tag f3-tag-win">más resiliente</span>' : ''}
          <table>
            <tr><td>Longitud</td><td>${num(pr.longitud_km)} km</td></tr>
            <tr><td>Cómputo</td><td>${num(pr.computo_ms)} ms</td></tr>
            <tr><td>Resiliencia R</td><td>${num(pr.resiliencia_R, 4)}</td></tr>
            <tr><td>Nodos</td><td>${(pr.nodos || []).length}</td></tr>
          </table>
        </div>`);

      if (visibles.has(tid)) capasRuta[tid].addTo(mapa);
    });

    const conGeom = data.features.length
      ? L.featureGroup(data.features.map((f) =>
          L.polyline(f.geometry.coordinates.map((c) => [c[1], c[0]]))))
      : null;
    if (conGeom) mapa.fitBounds(conGeom.getBounds(), { padding: [40, 40] });
  }

  function leyenda(data) {
    const cont = $('f3-leyenda');
    $('f3-modelo-ms').textContent = data.modelo_ms ? `modelo ${num(data.modelo_ms, 0)} ms` : '';

    cont.innerHTML = TECNICAS.map((tid) => {
      const t = data.tecnicas[tid];
      if (!t) return '';
      const ok = t.estado === 'ok';
      const gana = data.mejor_resiliencia === tid;
      const motivo = { sin_ruta: 'Sin ruta', infactible: 'Infactible', error: 'Error' }[t.estado] || t.estado;

      // Una ruta puede venir "ok" y aun así violar lo que pidió el usuario: solo el
      // MILP trata la autonomía como restricción dura, y el Dijkstra por distancia
      // ignora los bloqueos por definición. Sin avisarlo, la comparación engaña.
      const avisos = [];
      if (ok && t.cumple_autonomia === false) {
        avisos.push(`excede la autonomía (${num(t.longitud_km)} km)`);
      }
      if (ok && t.advertencia) {
        avisos.push({
          sin_alternativa: 'no existe segundo camino disimilar: va un solo trazado',
          alternativas_exceden_autonomia: 'las alternativas excedían la autonomía: va un solo trazado',
        }[t.advertencia] || esc(t.advertencia));
      }
      if (ok && t.bloqueos_en_ruta) {
        avisos.push(`cruza ${t.bloqueos_en_ruta} elemento${t.bloqueos_en_ruta > 1 ? 's' : ''} bloqueado${t.bloqueos_en_ruta > 1 ? 's' : ''}`);
      }
      const bloqueAvisos = avisos.length
        ? `<div class="f3-aviso">⚠ ${avisos.map(esc).join(' · ')}</div>` : '';

      const metricas = ok ? `
        <div class="f3-metricas">
          <span><b>${num(t.longitud_km)}</b> km</span>
          <span><b>${num(t.computo_ms)}</b> ms</span>
          <span>R = <b>${num(t.resiliencia_R, 4)}</b></span>
          ${t.supervivencia_mc_pct !== undefined && t.supervivencia_mc_pct !== null
            ? `<span>MC <b>${num(t.supervivencia_mc_pct, 1)}%</b></span>` : ''}
        </div>
        <div class="f3-sub">
          ${esc(t.backend || 'python')}
          ${t.pct_densas !== undefined && t.pct_densas !== null ? ` · ${num(t.pct_densas, 1)}% denso` : ''}
          ${t.pct_sin_c2 !== undefined && t.pct_sin_c2 !== null ? ` · ${num(t.pct_sin_c2, 1)}% sin C2` : ''}
          ${t.n_caminos > 1 ? ` · ${t.n_caminos} caminos` : ''}
        </div>
        ${bloqueAvisos}`
      : `<div class="f3-sub f3-sub-malo">${esc(motivo)}${t.motivo ? ' · ' + esc(t.motivo) : ''}</div>`;

      return `
        <div class="f3-ruta ${ok ? '' : 'f3-ruta-off'} ${gana ? 'f3-ruta-win' : ''} ${avisos.length ? 'f3-ruta-aviso' : ''}">
          <label class="f3-ruta-head" for="f3-ver-${tid}">
            <input type="checkbox" id="f3-ver-${tid}" data-tecnica="${tid}"
                   ${visibles.has(tid) ? 'checked' : ''} ${ok ? '' : 'disabled'}>
            <span class="f3-swatch" style="background:${esc(t.color || '#888')}"></span>
            <span class="f3-ruta-nombre">${esc(nombreCorto(tid))}</span>
            ${gana ? '<span class="f3-tag f3-tag-win">mejor R</span>' : ''}
          </label>
          ${metricas}
        </div>`;
    }).join('');

    cont.querySelectorAll('input[data-tecnica]').forEach((inp) => {
      inp.addEventListener('change', () => {
        const tid = inp.dataset.tecnica;
        if (inp.checked) {
          visibles.add(tid);
          if (capasRuta[tid] && mapaListo()) capasRuta[tid].addTo(mapa);
        } else {
          visibles.delete(tid);
          if (capasRuta[tid] && mapaListo()) mapa.removeLayer(capasRuta[tid]);
        }
      });
    });
  }

  // --------------------------------------------------------------------------
  // /api/simulacion — sortea u ∈ [0,100) por nodo y arista, pinta lo caído
  // --------------------------------------------------------------------------
  function limpiarFallas() {
    if (capaFallas && mapaListo()) mapa.removeLayer(capaFallas);
    capaFallas = null;
  }

  async function simular() {
    if (!ultimaConsulta) return;
    const btn = $('f3-simular');
    btn.disabled = true;
    estado('Sorteando fallas…', 'cargando');
    try {
      const p = new URLSearchParams(ultimaConsulta);
      p.delete('mc_n');
      p.set('seed', String(Math.floor(Math.random() * 999999)));
      const data = await pedir('/api/simulacion?' + p.toString());

      limpiarFallas();
      capaFallas = L.layerGroup();
      data.features.forEach((f) => {
        const pr = f.properties;
        const texto = `<b>${pr.tipo === 'arista' ? 'Arista' : 'Nodo'} ${pr.id}</b><br>
          p(falla) = ${num(pr.p_falla, 3)}<br>sorteo u = ${num(pr.u, 1)}
          ${pr.bloqueada || pr.bloqueado ? '<br><i>elemento bloqueado</i>' : ''}`;
        if (f.geometry.type === 'LineString') {
          L.polyline(f.geometry.coordinates.map((c) => [c[1], c[0]]),
            { color: '#dc2626', weight: 3, opacity: 0.8 }).bindPopup(texto).addTo(capaFallas);
        } else {
          L.circleMarker([f.geometry.coordinates[1], f.geometry.coordinates[0]],
            { radius: 4, color: '#dc2626', fillColor: '#dc2626', fillOpacity: 0.85, weight: 1 })
            .bindPopup(texto).addTo(capaFallas);
        }
      });
      if (mapaListo()) capaFallas.addTo(mapa);

      const filas = TECNICAS.map((tid) => {
        const t = data.tecnicas[tid];
        if (!t) return '';
        const cls = t.sobrevive === true ? 'f3-vive' : t.sobrevive === false ? 'f3-muere' : 'f3-nulo';
        return `<div class="f3-sim-fila ${cls}">
            <span>${esc(nombreCorto(tid))}</span><b>${esc(t.texto)}</b></div>`;
      }).join('');

      $('f3-sim').innerHTML = `
        <div class="f3-sim-head">Semilla ${data.seed} ·
          ${data.n_aristas_caidas} aristas y ${data.n_nodos_caidos} nodos caídos</div>
        ${filas}`;
      $('f3-sim').hidden = false;
      estado('Simulación lista. En rojo, los elementos que fallaron.', 'ok');
    } catch (e) {
      estado('Error en la simulación: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
    }
  }

  // --------------------------------------------------------------------------
  function enlazar() {
    $('f3-calcular').addEventListener('click', calcular);
    $('f3-simular').addEventListener('click', simular);

    $('f3-capas-toggle').addEventListener('click', () => {
      const inputs = [...document.querySelectorAll('#f3-capas input[data-capa]')];
      const encender = inputs.some((i) => !i.checked);
      inputs.forEach((i) => { i.checked = encender; });
      $('f3-capas-toggle').textContent = encender ? 'Ninguna' : 'Todas';
    });

    // El preset de contingencia enciende la capa de incendio, que es la que lo modela.
    $('f3-contingencia').addEventListener('change', (e) => {
      if (e.target.checked) {
        const inc = document.querySelector('#f3-capas input[data-capa="incendio"]');
        if (inc) inc.checked = true;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { enlazar(); iniciar(); });
  } else {
    enlazar();
    iniciar();
  }
})();
