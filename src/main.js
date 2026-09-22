/**
 * main.js
 * Orquestador principal del Simulador Ciberfísico de Redes Resilientes.
 */

import { NetworkGraph } from './core/NetworkGraph.js';
import { MapManager } from './map/mapManager.js';
import { CATEGORIES, getCategoryConfig } from './config/categories.js';

class App {
  constructor() {
    this.graph = new NetworkGraph();
    this.mapManager = new MapManager('map');
    this.allNodes = [];
    this.currentFilter = 'all';
  }

  async init() {
    await this.mapManager.init();
    await this.loadNetworkData();
    this.setupUI();
  }

  async loadNetworkData() {
    try {
      const response = await fetch(`./public/data/nodes.geojson?t=${Date.now()}`, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error(`Error al leer nodes.geojson: ${response.statusText}`);
      }

      const geojsonData = await response.json();
      console.log('Datos GeoJSON cargados con éxito:', geojsonData);

      // Ingresar nodos al grafo matemático con proyección métrica UTM 19S automática
      geojsonData.features.forEach(feature => {
        const id = feature.properties.id;
        const coords = feature.geometry.coordinates; // [lng, lat, alt]
        this.graph.addNode(id, feature.properties, coords);
      });

      this.allNodes = this.graph.getAllNodes();

      // Renderizar en Leaflet por capas temáticas
      this.mapManager.renderNodes(this.allNodes, (selectedNode) => {
        console.log('Nodo seleccionado en mapa:', selectedNode);
      });

      // Actualizar métricas del panel y lista de nodos
      this.updateDashboardMetrics();
      this.populateNodesList(this.allNodes);

    } catch (err) {
      console.error('Error inicializando datos de la red:', err);
      const listContainer = document.getElementById('nodesList');
      if (listContainer) {
        listContainer.innerHTML = `<p style="color: #ef4444; font-size: 0.8rem;">Error cargando nodos: ${err.message}</p>`;
      }
    }
  }

  updateDashboardMetrics() {
    const totalEl = document.getElementById('metricTotalNodes');
    if (totalEl) totalEl.textContent = this.allNodes.length;

    const counts = {};
    Object.keys(CATEGORIES).forEach(k => counts[k] = 0);

    this.allNodes.forEach(node => {
      const cat = node.properties.category;
      if (counts[cat] !== undefined) counts[cat]++;
    });

    const metricIdMap = {
      sinca: 'metricSincaNodes',
      emission_source: 'metricIndustryNodes',
      health: 'metricHealthNodes',
      education: 'metricEducationNodes',
      commercial: 'metricCommercialNodes',
      crowded_area: 'metricCrowdedNodes',
      beach: 'metricBeachNodes',
      hospitality: 'metricHospitalityNodes',
      restaurant: 'metricRestaurantNodes',
      attraction: 'metricAttractionNodes',
      historic: 'metricHistoricNodes',
      auxiliary_hub: 'metricHubNodes'
    };

    Object.entries(metricIdMap).forEach(([catKey, elId]) => {
      const el = document.getElementById(elId);
      if (el) el.textContent = counts[catKey] || 0;
    });
  }

  populateNodesList(nodes) {
    const listContainer = document.getElementById('nodesList');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    const filtered = (this.currentFilter === 'all')
      ? nodes
      : nodes.filter(n => n.properties.category === this.currentFilter);

    if (filtered.length === 0) {
      listContainer.innerHTML = `<p style="color: var(--text-secondary); font-size: 0.75rem; padding: 10px;">No hay nodos en esta categoría.</p>`;
      return;
    }

    filtered.forEach(node => {
      const cat = node.properties.category || 'other';
      const config = getCategoryConfig(cat);
      const iconChar = node.properties.icon || config.icon || '📍';
      const cityText = node.properties.city ? `<span style="color: var(--accent-cyan); font-size: 0.68rem; margin-left: 4px;">• ${node.properties.city}</span>` : '';

      const item = document.createElement('div');
      item.className = 'node-item';
      item.innerHTML = `
        <div class="node-header">
          <span style="font-weight: 500;">${iconChar} ${node.properties.name}</span>
          <span class="status-tag ${config.tagClass}">
            ${config.shortName}
          </span>
        </div>
        <div class="node-coords">
          ${node.coords[1].toFixed(4)}, ${node.coords[0].toFixed(4)} &bull; ${node.coords[2] || 0} msnm ${cityText}
        </div>
      `;

      item.addEventListener('click', () => {
        const marker = this.mapManager.markersMap.get(node.id);
        if (marker) {
          this.mapManager.map.flyTo([node.coords[1], node.coords[0]], 14, { duration: 1.2 });
          marker.openPopup();
        }
      });

      listContainer.appendChild(item);
    });
  }

  setupUI() {
    // 1. Botón RTH de Emergencia
    const rthBtn = document.getElementById('btnRTH');
    if (rthBtn) {
      rthBtn.addEventListener('click', () => {
        alert('⚡ Protocolo de Retorno Seguro (RTH): Calculando ruta óptima asistida por sotavento hacia el Aeródromo de Quintero...');
      });
    }

    // 2. Filtros de categoría en barra lateral
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentFilter = btn.getAttribute('data-filter');
        this.populateNodesList(this.allNodes);
      });
    });

    // 3. Interruptor de Configuración: "Mostrar íconos" (desactivado por defecto)
    const toggleShowIcons = document.getElementById('toggleShowIcons');
    if (toggleShowIcons) {
      toggleShowIcons.checked = false;
      toggleShowIcons.addEventListener('change', (e) => {
        this.mapManager.setShowAllIcons(e.target.checked);
      });
    }

    // 4. Minimizar / Restaurar Barra Lateral Completa (Sidebar)
    const sidebar = document.getElementById('gisSidebar');
    const btnCollapse = document.getElementById('btnCollapseSidebar');
    const btnExpand = document.getElementById('btnExpandSidebar');
    const btnHeaderToggle = document.getElementById('headerToggleSidebar');

    const setSidebarCollapsed = (collapse) => {
      if (!sidebar) return;
      if (collapse) {
        sidebar.classList.add('collapsed');
        if (btnExpand) btnExpand.classList.add('visible');
      } else {
        sidebar.classList.remove('collapsed');
        if (btnExpand) btnExpand.classList.remove('visible');
      }

      // Disparar recálculo de dimensiones en Leaflet durante y después de la transición
      const triggerResize = () => {
        if (this.mapManager && this.mapManager.map) {
          this.mapManager.map.invalidateSize();
        }
      };

      // Inmediato, a mitad de animación y al terminar
      triggerResize();
      setTimeout(triggerResize, 160);
      setTimeout(triggerResize, 350);
    };

    if (btnCollapse) {
      btnCollapse.addEventListener('click', () => setSidebarCollapsed(true));
    }

    if (btnExpand) {
      btnExpand.addEventListener('click', () => setSidebarCollapsed(false));
    }

    if (btnHeaderToggle) {
      btnHeaderToggle.addEventListener('click', () => {
        const isCollapsed = sidebar.classList.contains('collapsed');
        setSidebarCollapsed(!isCollapsed);
      });
    }

    // Atajo de teclado: Tecla 'M' para minimizar/expandir
    window.addEventListener('keydown', (e) => {
      if (e.key === 'm' || e.key === 'M') {
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
          const isCollapsed = sidebar.classList.contains('collapsed');
          setSidebarCollapsed(!isCollapsed);
        }
      }
    });
  }
}

// Iniciar aplicación al cargar el DOM
window.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
