/**
 * MapEngine.js
 * Responsable exclusivo de instanciar el mapa Leaflet, capas base satelitales,
 * controles de escala, límites elásticos y redimensionamiento.
 */

export class MapEngine {
  constructor(containerId = 'map') {
    this.containerId = containerId;
    this.map = null;
    this.baseLayers = {};
  }

  /**
   * Inicializa el lienzo Leaflet con capas satelitales de alta definición
   */
  init() {
    // Cobertura focalizada estrictamente en la Bahía de Quintero, Ventanas y Puchuncaví Centro
    const focusBounds = L.latLngBounds(
      L.latLng(-32.8350, -71.5500), // Sur-oeste: Península de Quintero / borde norte Ritoque
      L.latLng(-32.6850, -71.3980)  // Norte-este: Horcón, El Rungue y Puchuncaví Centro
    );

    // Margen elástico exterior para evitar bloqueos bruscos de paneo
    const regionalMaxBounds = L.latLngBounds(
      L.latLng(-32.9200, -71.6500),
      L.latLng(-32.6200, -71.3200)
    );

    this.map = L.map(this.containerId, {
      center: [-32.7600, -71.4700],
      zoom: 12,
      minZoom: 10,
      maxZoom: 19,
      maxBounds: regionalMaxBounds,
      maxBoundsViscosity: 0.3,
      zoomControl: true
    });

    this.map.fitBounds(focusBounds, { padding: [25, 25] });

    // Capas Base Satelitales Continuas
    const satelliteEsri = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        attribution: 'Tiles &copy; Esri &mdash; Bahía de Quintero y Puchuncaví',
        maxZoom: 19,
        minZoom: 10
      }
    );

    const darkTiles = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19,
        minZoom: 10
      }
    );

    const osmTiles = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 19,
        minZoom: 10
      }
    );

    // Esri por defecto
    satelliteEsri.addTo(this.map);

    this.baseLayers = {
      "🛰 Satélite Esri (Limpio)": satelliteEsri,
      "🌙 CartoDB Modo Oscuro": darkTiles,
      "🗺 OpenStreetMap Calles": osmTiles
    };

    // Escala métrica aeronáutica
    L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(this.map);

    return this;
  }

  /**
   * Recalcula las dimensiones del mapa cuando el sidebar se minimiza o cambia el viewport
   */
  invalidateSize() {
    if (this.map) {
      this.map.invalidateSize();
    }
  }
}
