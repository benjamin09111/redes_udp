/**
 * mapManager.js
 * Fachada orquestadora del sistema cartográfico.
 * Desacopla la inicialización del lienzo (MapEngine), las zonas urbanas (UrbanZoneRenderer)
 * y los nodos espaciales (NodeRenderer).
 * 
 * Mantiene 100% de compatibilidad con la interfaz de main.js.
 */

import { MapEngine } from './MapEngine.js';
import { UrbanZoneRenderer } from './UrbanZoneRenderer.js';
import { NodeRenderer } from './NodeRenderer.js';

export class MapManager {
  constructor(containerId = 'map') {
    this.containerId = containerId;
    this.engine = new MapEngine(containerId);
    this.urbanRenderer = null;
    this.nodeRenderer = null;
  }

  get map() {
    return this.engine.map;
  }

  get markersMap() {
    return this.nodeRenderer ? this.nodeRenderer.markersMap : new Map();
  }

  /**
   * Inicializa el motor, las capas base, zonas urbanas y los renderizadores
   */
  async init() {
    this.engine.init();
    this.urbanRenderer = new UrbanZoneRenderer(this.map);
    this.nodeRenderer = new NodeRenderer(this.map);

    // Cargar los contornos de las 7 zonas urbanas oficiales
    await this.urbanRenderer.loadUrbanZones('./public/data/urban_zones.geojson');

    // Configurar el control de capas flotante colapsable
    const overlayTree = {
      "🏘 Zonas Urbanas y Exclusión": this.urbanRenderer.getLayer(),
      ...this.nodeRenderer.getOverlayTree()
    };

    L.control.layers(this.engine.baseLayers, overlayTree, {
      position: 'topright',
      collapsed: true
    }).addTo(this.map);

    return this;
  }

  /**
   * Renderiza todos los nodos del grafo en sus capas respectivas
   */
  renderNodes(nodes, onSelect) {
    if (this.nodeRenderer) {
      this.nodeRenderer.renderNodes(nodes, onSelect);
    }
  }

  /**
   * Alterna entre modo íconos y modo puntos discretos de grafo
   */
  setShowAllIcons(show) {
    if (this.nodeRenderer) {
      this.nodeRenderer.setShowAllIcons(show);
    }
  }

  /**
   * Recalcula tamaño del mapa (por ejemplo al colapsar el sidebar)
   */
  invalidateSize() {
    this.engine.invalidateSize();
  }
}
