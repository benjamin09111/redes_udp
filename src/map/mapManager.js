/**
 * mapManager.js
 * Visualizador cartográfico avanzado basado en Leaflet.js
 * Mapa acotado estrictamente a la zona activa de la Bahía con panel de capas colapsable/ocultable.
 */

export class MapManager {
  constructor(containerId = 'map') {
    this.containerId = containerId;
    this.map = null;
    this.layers = {
      base: {},
      overlays: {
        urbanZones: null,
        baseNode: null,
        sinca: null,
        emissions: null,
        health: null,
        education: null,
        commercial: null,
        crowded: null,
        beaches: null,
        hospitality: null,
        restaurants: null,
        attractions: null,
        hubs: null,
        corridors: null
      }
    };
    this.markersMap = new Map();
    this.showAllIcons = false; // Por defecto desactivado
    this.cachedNodes = [];
    this.cachedOnSelect = null;
  }

  /**
   * Inicializa el visor cartográfico con amplia cobertura espacial y paneo fluido
   */
  init() {
    // Cobertura amplia para abarcar toda la bahía y valles interiores sin cortes
    const focusBounds = L.latLngBounds(
      L.latLng(-32.8400, -71.5550), // Sur-oeste: Ritoque y Península de Quintero
      L.latLng(-32.6850, -71.3550)  // Norte-este: El Rungue, El Rincón y La Estancilla
    );

    // Margen exterior generoso para permitir desplazamiento natural sin bloqueos
    const regionalMaxBounds = L.latLngBounds(
      L.latLng(-32.9200, -71.6500),
      L.latLng(-32.6200, -71.2800)
    );

    this.map = L.map(this.containerId, {
      center: [-32.7550, -71.4550],
      zoom: 12,
      minZoom: 10,
      maxZoom: 19,
      maxBounds: regionalMaxBounds,
      maxBoundsViscosity: 0.3, // Paneo suave y elástico, nunca se traba
      zoomControl: true
    });

    this.map.fitBounds(focusBounds, { padding: [30, 30] });

    // 2. Capas Base Satelitales Continuas (sin recorte de teselas)
    const satelliteEsri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Bahía de Quintero y Puchuncaví',
      maxZoom: 19,
      minZoom: 10
    });

    const darkTiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      subdomains: 'abcd',
      maxZoom: 19,
      minZoom: 10
    });

    const osmTiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap',
      maxZoom: 19,
      minZoom: 10
    });

    satelliteEsri.addTo(this.map);

    this.layers.base = {
      "🛰 Satélite Esri (Limpio)": satelliteEsri,
      "🌙 CartoDB Modo Oscuro": darkTiles,
      "🗺 OpenStreetMap Calles": osmTiles
    };

    // 3. Grupos de Capas de Datos y Contornos Urbanos
    this.layers.overlays.urbanZones = L.layerGroup().addTo(this.map);
    this.layers.overlays.baseNode = L.layerGroup().addTo(this.map);
    this.layers.overlays.sinca = L.layerGroup().addTo(this.map);
    this.layers.overlays.emissions = L.layerGroup().addTo(this.map);
    this.layers.overlays.health = L.layerGroup().addTo(this.map);
    this.layers.overlays.education = L.layerGroup().addTo(this.map);
    this.layers.overlays.commercial = L.layerGroup().addTo(this.map);
    this.layers.overlays.crowded = L.layerGroup().addTo(this.map);
    this.layers.overlays.beaches = L.layerGroup().addTo(this.map);
    this.layers.overlays.hospitality = L.layerGroup().addTo(this.map);
    this.layers.overlays.restaurants = L.layerGroup().addTo(this.map);
    this.layers.overlays.attractions = L.layerGroup().addTo(this.map);
    this.layers.overlays.historic = L.layerGroup().addTo(this.map);
    this.layers.overlays.hubs = L.layerGroup().addTo(this.map);
    this.layers.overlays.corridors = L.layerGroup().addTo(this.map);

    const overlayTree = {
      "🏙 Zonas Urbanas Multicolores (13 Localidades)": this.layers.overlays.urbanZones,
      "✈ Base de Despacho (Aeródromo)": this.layers.overlays.baseNode,
      "📡 Estaciones SINCA (Calidad de Aire)": this.layers.overlays.sinca,
      "🏭 Fábricas y Fuentes Contaminantes (33 Nodos Industriales)": this.layers.overlays.emissions,
      "🏛 Patrimonio y Sitios Históricos": this.layers.overlays.historic,
      "🏥 Red de Salud (Hospitales, CESFAM, Postas)": this.layers.overlays.health,
      "🏫 Red de Educación (Colegios, Escuelas)": this.layers.overlays.education,
      "🛒 Comercio y Supermercados": this.layers.overlays.commercial,
      "👥 Concurrencia Masiva (Plazas, Cívico, Estadios)": this.layers.overlays.crowded,
      "🏖 Playas y Borde Costero": this.layers.overlays.beaches,
      "🏨 Hoteles, Cabañas y Hospedaje": this.layers.overlays.hospitality,
      "🍽 Gastronomía y Restaurantes": this.layers.overlays.restaurants,
      "📸 Miradores y Atracciones": this.layers.overlays.attractions,
      "🔋 Hubs de Recarga Auxiliares": this.layers.overlays.hubs,
      "〰 Corredores Aéreos": this.layers.overlays.corridors
    };



    // Panel colapsable/ocultable (collapsed: true): solo se abre al hacer clic o pasar el cursor
    L.control.layers(this.layers.base, overlayTree, { position: 'topright', collapsed: true }).addTo(this.map);
    L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(this.map);

    // Cargar los contornos de las ciudades (Quintero, Ventanas, Puchuncaví)
    this.loadUrbanZones();

    return this;
  }

  /**
   * Carga y dibuja los polígonos de contorno urbano de Quintero, Ventanas y Puchuncaví
   */
  async loadUrbanZones() {
    try {
      const resp = await fetch('./public/data/urban_zones.geojson');
      if (!resp.ok) return;
      const data = await resp.json();

      const layer = L.geoJSON(data, {
        style: (feature) => {
          const color = feature.properties.color || '#38bdf8';
          const fillColor = feature.properties.fillColor || color;
          return {
            color: color,
            weight: 2,
            dashArray: '6, 6',
            fillColor: fillColor,
            fillOpacity: 0.12,
            lineJoin: 'round'
          };
        },
        onEachFeature: (feature, polygonLayer) => {
          const name = feature.properties.name || feature.properties.city;
          polygonLayer.bindTooltip(`<strong>${name}</strong>`, {
            sticky: true,
            className: 'urban-tooltip'
          });

          // Efecto hover sutil
          polygonLayer.on('mouseover', function () {
            this.setStyle({
              weight: 3,
              fillOpacity: 0.22,
              dashArray: ''
            });
          });
          polygonLayer.on('mouseout', function () {
            layer.resetStyle(this);
          });
        }
      });

      layer.addTo(this.layers.overlays.urbanZones);
    } catch (err) {
      console.warn('No se pudieron cargar los contornos urbanos:', err);
    }
  }

  /**
   * Renderiza todos los nodos asignándolos a su respectiva capa temática
   */
  renderNodes(nodes, onSelect) {
    if (nodes) this.cachedNodes = nodes;
    if (onSelect) this.cachedOnSelect = onSelect;
    const nodesToRender = nodes || this.cachedNodes;
    const selectCallback = onSelect || this.cachedOnSelect;

    this.layers.overlays.baseNode.clearLayers();
    this.layers.overlays.sinca.clearLayers();
    this.layers.overlays.emissions.clearLayers();
    this.layers.overlays.health.clearLayers();
    this.layers.overlays.education.clearLayers();
    this.layers.overlays.commercial.clearLayers();
    this.layers.overlays.crowded.clearLayers();
    this.layers.overlays.beaches.clearLayers();
    this.layers.overlays.hospitality.clearLayers();
    this.layers.overlays.restaurants.clearLayers();
    this.layers.overlays.attractions.clearLayers();
    this.layers.overlays.historic.clearLayers();
    this.layers.overlays.hubs.clearLayers();
    this.markersMap.clear();

    nodesToRender.forEach(node => {
      const [lng, lat, alt] = node.coords;
      const cat = node.properties.category || 'other';

      let targetLayer = this.layers.overlays.sinca;
      let markerClass = 'sinca-marker';
      let iconChar = node.properties.icon || '📍';

      switch (cat) {
        case 'base':
          targetLayer = this.layers.overlays.baseNode;
          markerClass = 'base-marker';
          break;
        case 'sinca':
          targetLayer = this.layers.overlays.sinca;
          markerClass = 'sinca-marker';
          break;
        case 'emission_source':
          targetLayer = this.layers.overlays.emissions;
          markerClass = 'emission-marker';
          break;
        case 'health':
          targetLayer = this.layers.overlays.health;
          markerClass = 'health-marker';
          break;
        case 'education':
          targetLayer = this.layers.overlays.education;
          markerClass = 'education-marker';
          break;
        case 'commercial':
          targetLayer = this.layers.overlays.commercial;
          markerClass = 'commercial-marker';
          break;
        case 'crowded_area':
          targetLayer = this.layers.overlays.crowded;
          markerClass = 'crowded-marker';
          break;
        case 'beach':
          targetLayer = this.layers.overlays.beaches;
          markerClass = 'beach-marker';
          break;
        case 'hospitality':
          targetLayer = this.layers.overlays.hospitality;
          markerClass = 'hospitality-marker';
          break;
        case 'restaurant':
          targetLayer = this.layers.overlays.restaurants;
          markerClass = 'restaurant-marker';
          break;
        case 'attraction':
          targetLayer = this.layers.overlays.attractions;
          markerClass = 'attraction-marker';
          break;
        case 'historic':
          targetLayer = this.layers.overlays.historic;
          markerClass = 'historic-marker';
          break;
        case 'auxiliary_hub':
          targetLayer = this.layers.overlays.hubs;
          markerClass = 'hub-marker';
          break;
      }

      const isAlwaysIcon = (cat === 'base' || cat === 'sinca');
      const showIcon = isAlwaysIcon || this.showAllIcons;

      let iconHtml = '';
      let iconSize = [14, 14];
      let iconAnchor = [7, 7];

      if (showIcon) {
        iconHtml = `<div class="node-marker ${markerClass}" title="${node.properties.name}">${iconChar}</div>`;
        iconSize = (cat === 'base') ? [34, 34] : [30, 30];
        iconAnchor = (cat === 'base') ? [17, 17] : [15, 15];
      } else {
        iconHtml = `<div class="node-marker node-dot ${markerClass}" title="${node.properties.name}"></div>`;
        iconSize = [14, 14];
        iconAnchor = [7, 7];
      }

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-div-icon',
        iconSize: iconSize,
        iconAnchor: iconAnchor
      });

      const marker = L.marker([lat, lng], { icon: customIcon });

      const polText = Array.isArray(node.properties.pollutants) 
        ? node.properties.pollutants.join(', ') 
        : (typeof node.properties.pollutants === 'string' ? node.properties.pollutants : '');
      const pollutants = polText
        ? `<p><strong>Contaminantes:</strong> <span class="pollutant-badge">${polText}</span></p>`
        : '';

      const cityText = node.properties.city
        ? `<p><strong>Sector / Ciudad:</strong> ${node.properties.city}</p>`
        : '';

      const priorityBadge = `<span class="priority-badge priority-${node.properties.priority || 1}">Prioridad: ${node.properties.priority || 1}</span>`;

      const popupContent = `
        <div class="gis-popup">
          <div class="popup-header">
            <span class="popup-icon">${iconChar}</span>
            <h4>${node.properties.name}</h4>
          </div>
          <p class="popup-role">${node.properties.role || node.properties.type}</p>
          <hr class="popup-divider"/>
          <p><strong>Categoría:</strong> ${this.getCategoryLabel(cat)}</p>
          ${cityText}
          <p><strong>Coordenadas:</strong> [${lat.toFixed(5)}, ${lng.toFixed(5)}]</p>
          <p><strong>Altitud relieve:</strong> ${alt || node.properties.elevation_msnm || 0} msnm</p>
          ${pollutants}
          <div class="popup-footer">
            ${priorityBadge}
            <span class="status-tag tag-${cat}">${cat.toUpperCase()}</span>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      marker.on('click', () => {
        if (onSelect) onSelect(node);
      });

      marker.addTo(targetLayer);
      this.markersMap.set(node.id, marker);
    });
  }

  getCategoryLabel(category) {
    const labels = {
      'base': 'Base Principal de Despacho (RTH)',
      'sinca': 'Estación Oficial Calidad del Aire (SINCA)',
      'emission_source': 'Fábrica / Fuente de Emisión Contaminante',
      'health': 'Centro de Salud y Farmacia (Hospital, CESFAM, Posta)',
      'education': 'Establecimiento Educacional (Colegio, Escuela, Liceo)',
      'commercial': 'Comercio, Supermercados y Abasto',
      'crowded_area': 'Lugar de Gran Concurrencia (SORA / GRC)',
      'beach': 'Playa y Balneario (Borde Costero)',
      'hospitality': 'Hospedaje Turístico (Hotel, Hostal, Cabaña)',
      'restaurant': 'Gastronomía y Restaurante de Caleta',
      'attraction': 'Mirador y Atractivo Turístico (Afluencia Visitantes)',
      'historic': 'Patrimonio y Sitio Histórico (Monumento / Museo)',
      'auxiliary_hub': 'Hub de Recarga Auxiliar (Baterías)'
    };
    return labels[category] || category;
  }

  /**
   * Alterna la visualización de íconos en todos los nodos o solo en Base/SINCA
   */
  setShowAllIcons(show) {
    this.showAllIcons = Boolean(show);
    this.renderNodes(this.cachedNodes, this.cachedOnSelect);
  }



  /**
   * Dibuja corredores aéreos (aristas) entre nodos
   */
  renderEdges(edges, nodesMap) {
    const corridorsLayer = this.layers.overlays.corridors;
    corridorsLayer.clearLayers();

    edges.forEach(edge => {
      const nodeA = nodesMap.get(edge.from);
      const nodeB = nodesMap.get(edge.to);

      if (!nodeA || !nodeB) return;

      const latlngs = [
        [nodeA.coords[1], nodeA.coords[0]],
        [nodeB.coords[1], nodeB.coords[0]]
      ];

      const polyline = L.polyline(latlngs, {
        color: '#38bdf8',
        weight: 2,
        dashArray: '4, 6',
        opacity: 0.75
      });

      polyline.bindTooltip(`Corredor: ${(edge.distance / 1000).toFixed(2)} km`, { sticky: true });
      polyline.addTo(corridorsLayer);
    });
  }
}
