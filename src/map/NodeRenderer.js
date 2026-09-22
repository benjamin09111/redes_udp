/**
 * NodeRenderer.js
 * Responsable de renderizar los nodos en el mapa agrupados por capas temáticas,
 * creación de marcadores (puntos simples o íconos completos) y popups de telemetría.
 */

import { CATEGORIES, getCategoryConfig } from '../config/categories.js';

export class NodeRenderer {
  constructor(map) {
    this.map = map;
    this.categoryLayers = new Map(); // categoryId -> L.layerGroup()
    this.markersMap = new Map();     // nodeId -> L.marker
    this.showAllIcons = false;
    this.cachedNodes = [];
    this.cachedOnSelect = null;

    // Inicializar grupos de capas para cada categoría definida
    Object.keys(CATEGORIES).forEach(catId => {
      const group = L.layerGroup();
      this.categoryLayers.set(catId, group);
      if (this.map) {
        group.addTo(this.map);
      }
    });
  }

  /**
   * Renderiza todos los nodos en sus respectivas capas
   * @param {Array} nodes - Lista de nodos [{ id, properties, coords, utm }]
   * @param {Function} onSelect - Callback al hacer clic en un nodo
   */
  renderNodes(nodes, onSelect) {
    if (nodes) this.cachedNodes = nodes;
    if (onSelect) this.cachedOnSelect = onSelect;
    const nodesToRender = nodes || this.cachedNodes;
    const selectCallback = onSelect || this.cachedOnSelect;

    // Limpiar capas previas
    this.categoryLayers.forEach(layer => layer.clearLayers());
    this.markersMap.clear();

    nodesToRender.forEach(node => {
      const [lng, lat, alt] = node.coords;
      const catId = node.properties.category || 'other';
      const config = getCategoryConfig(catId);

      let targetLayer = this.categoryLayers.get(catId);
      if (!targetLayer) {
        targetLayer = L.layerGroup().addTo(this.map);
        this.categoryLayers.set(catId, targetLayer);
      }

      let marker;

      // Opción A: Modo Íconos completos con texto/emoji
      if (this.showAllIcons) {
        const iconChar = node.properties.icon || config.icon || '📍';
        const customIcon = L.divIcon({
          className: 'custom-node-icon',
          html: `<div class="marker-dot ${config.tagClass}" style="border-color: ${config.color};">${iconChar}</div>`,
          iconSize: [26, 26],
          iconAnchor: [13, 13]
        });

        marker = L.marker([lat, lng], { icon: customIcon });
      } 
      // Opción B: Modo Grafo Científico (círculos limpios de vector)
      else {
        // Marcador destacado para la Base SCER
        if (catId === 'base') {
          const baseIcon = L.divIcon({
            className: 'base-custom-marker',
            html: `<div style="background: #10b981; border: 2.5px solid #fff; border-radius: 50%; width: 28px; height: 28px; display:flex; align-items:center; justify-content:center; box-shadow: 0 0 16px rgba(16,185,129,0.9); font-size:15px; color:#fff;">✈</div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14]
          });
          marker = L.marker([lat, lng], { icon: baseIcon });
        } else {
          marker = L.circleMarker([lat, lng], {
            radius: catId === 'sinca' ? 7 : (catId === 'emission_source' ? 6.5 : 5),
            color: '#ffffff',
            weight: 1.2,
            fillColor: config.color,
            fillOpacity: 0.88
          });
        }
      }

      // Popup informativo enriquecido con elevación y metadatos
      const sensorsList = (node.properties.sensors && node.properties.sensors.length > 0)
        ? `<div class="popup-sensors"><strong>Sensores:</strong> ${node.properties.sensors.join(', ')}</div>`
        : '';

      const cityText = node.properties.city ? `<div class="popup-meta"><strong>Zona:</strong> ${node.properties.city}</div>` : '';

      marker.bindPopup(`
        <div class="node-popup">
          <div class="popup-header" style="border-left: 3px solid ${config.color}; padding-left: 8px;">
            <h4>${config.icon} ${node.properties.name}</h4>
            <span class="status-tag ${config.tagClass}">${config.shortName}</span>
          </div>
          ${cityText}
          <div class="popup-meta">
            <strong>Coordenadas:</strong> ${lat.toFixed(5)}, ${lng.toFixed(5)}
          </div>
          <div class="popup-meta">
            <strong>Altitud Terreno:</strong> ${alt || 0} msnm
          </div>
          <div class="popup-meta">
            <strong>Prioridad Misión:</strong> ${node.properties.priority || 5}/10
          </div>
          ${sensorsList}
        </div>
      `, {
        maxWidth: 280,
        className: 'custom-leaflet-popup'
      });

      marker.on('click', () => {
        if (typeof selectCallback === 'function') {
          selectCallback(node);
        }
      });

      marker.addTo(targetLayer);
      this.markersMap.set(node.id, marker);
    });
  }

  /**
   * Alterna entre íconos completos y puntos discretos de grafo
   */
  setShowAllIcons(show) {
    this.showAllIcons = show;
    this.renderNodes();
  }

  /**
   * Retorna el diccionario de capas agrupadas para el control de capas de Leaflet
   */
  getOverlayTree() {
    const overlays = {};
    Object.keys(CATEGORIES).forEach(catId => {
      const config = CATEGORIES[catId];
      const layer = this.categoryLayers.get(catId);
      if (layer) {
        overlays[config.layerName] = layer;
      }
    });
    return overlays;
  }
}
