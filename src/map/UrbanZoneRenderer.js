/**
 * UrbanZoneRenderer.js
 * Responsable de cargar, estilizar y gestionar los polígonos de zonas urbanas
 * y de amortiguamiento de la Bahía (Quintero, Loncura, Ventanas, Horcón, Puchuncaví).
 */

export class UrbanZoneRenderer {
  constructor(map) {
    this.map = map;
    this.layerGroup = L.layerGroup();
    if (this.map) {
      this.layerGroup.addTo(this.map);
    }
  }

  /**
   * Carga el archivo GeoJSON de zonas urbanas oficiales con anti-cache
   */
  async loadUrbanZones(url = './public/data/urban_zones.geojson') {
    try {
      const resp = await fetch(`${url}?t=${Date.now()}`, { cache: 'no-store' });
      if (!resp.ok) {
        throw new Error(`Error al leer urban_zones.geojson: ${resp.statusText}`);
      }

      const data = await resp.json();
      this.layerGroup.clearLayers();

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
          const name = feature.properties.name || feature.properties.city || 'Zona Urbana';
          polygonLayer.bindTooltip(`<strong>${name}</strong>`, {
            sticky: true,
            className: 'urban-tooltip'
          });

          // Efecto hover de realce
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

      layer.addTo(this.layerGroup);
      return layer;
    } catch (err) {
      console.warn('UrbanZoneRenderer: No se pudieron cargar las zonas urbanas:', err);
      return null;
    }
  }

  getLayer() {
    return this.layerGroup;
  }
}
