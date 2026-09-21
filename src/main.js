/**
 * main.js
 * Orquestador principal del Simulador Ciberfísico de Redes Resilientes.
 */

import { NetworkGraph } from './core/NetworkGraph.js';
import { MapManager } from './map/mapManager.js';

class App {
  constructor() {
    this.graph = new NetworkGraph();
    this.mapManager = new MapManager('map');
    this.allNodes = [];
    this.currentFilter = 'all';
  }

  async init() {
    this.mapManager.init();
    await this.loadNetworkData();
    this.setupUI();
  }

  async loadNetworkData() {
    try {
      const response = await fetch('./public/data/nodes.geojson');
      if (!response.ok) {
        throw new Error(`Error al leer nodes.geojson: ${response.statusText}`);
      }

      const geojsonData = await response.json();
      console.log('Datos GeoJSON cargados con éxito:', geojsonData);

      // Ingresar nodos al grafo matemático
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

      // Actualizar métricas del panel
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
    const sincaEl = document.getElementById('metricSincaNodes');
    const indEl = document.getElementById('metricIndustryNodes');
    const healthEl = document.getElementById('metricHealthNodes');
    const eduEl = document.getElementById('metricEducationNodes');
    const commEl = document.getElementById('metricCommercialNodes');
    const crowdEl = document.getElementById('metricCrowdedNodes');
    const beachEl = document.getElementById('metricBeachNodes');
    const hospEl = document.getElementById('metricHospitalityNodes');
    const restoEl = document.getElementById('metricRestaurantNodes');
    const attrEl = document.getElementById('metricAttractionNodes');
    const histEl = document.getElementById('metricHistoricNodes');
    const hubEl = document.getElementById('metricHubNodes');

    const counts = {
      sinca: 0,
      emission_source: 0,
      health: 0,
      education: 0,
      commercial: 0,
      crowded_area: 0,
      beach: 0,
      hospitality: 0,
      restaurant: 0,
      attraction: 0,
      historic: 0,
      auxiliary_hub: 0
    };

    this.allNodes.forEach(node => {
      const cat = node.properties.category;
      if (counts[cat] !== undefined) counts[cat]++;
    });

    if (totalEl) totalEl.textContent = this.allNodes.length;
    if (sincaEl) sincaEl.textContent = counts.sinca;
    if (indEl) indEl.textContent = counts.emission_source;
    if (healthEl) healthEl.textContent = counts.health;
    if (eduEl) eduEl.textContent = counts.education;
    if (commEl) commEl.textContent = counts.commercial;
    if (crowdEl) crowdEl.textContent = counts.crowded_area;
    if (beachEl) beachEl.textContent = counts.beach;
    if (hospEl) hospEl.textContent = counts.hospitality;
    if (restoEl) restoEl.textContent = counts.restaurant;
    if (attrEl) attrEl.textContent = counts.attraction;
    if (histEl) histEl.textContent = counts.historic;
    if (hubEl) hubEl.textContent = counts.auxiliary_hub;
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
      const iconChar = node.properties.icon || '📍';
      const cat = node.properties.category || 'other';

      const cityText = node.properties.city ? `<span style="color: var(--accent-cyan); font-size: 0.68rem; margin-left: 4px;">• ${node.properties.city}</span>` : '';

      const item = document.createElement('div');
      item.className = 'node-item';
      item.innerHTML = `
        <div class="node-header">
          <span style="font-weight: 500;">${iconChar} ${node.properties.name}</span>
          <span class="status-tag tag-${cat}">
            ${node.properties.category}
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
  }
}

// Iniciar aplicación al cargar el DOM
window.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
