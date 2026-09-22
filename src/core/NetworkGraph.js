/**
 * NetworkGraph.js
 * Módulo core para el modelado de la red espacial 3D como grafo matemático.
 * Desacoplado del motor de visualización (Leaflet).
 * 
 * Basado en la formulación de Kosior et al. (2024) y la normativa DGAC DAN 151.
 * Optimizado con proyección plana métrica WGS84 UTM Zona 19S (EPSG:32719).
 */

import { forwardUTM19S } from './projection.js';

export class NetworkGraph {
  constructor() {
    this.nodes = new Map(); // id -> { id, properties, coords: [lng, lat, alt], utm: [x, y, z] }
    this.adjacencyList = new Map(); // id -> Map(neighborId -> edgeData)
  }

  /**
   * Agrega un nodo espacial al grafo
   * @param {string} id - Identificador único del nodo
   * @param {Object} properties - Metadatos (nombre, tipo, sensores, prioridad, zona)
   * @param {[number, number, number]} coords - [longitud, latitud, altitud_msnm]
   */
  addNode(id, properties = {}, coords = [0, 0, 0]) {
    const [lng, lat, alt = 0] = coords;
    // Proyección cartesiana en metros WGS84 UTM 19S
    const [x, y] = forwardUTM19S(lng, lat);

    this.nodes.set(id, {
      id,
      properties,
      coords: [lng, lat, alt], // Angular WGS84
      utm: [x, y, alt],        // Métrico UTM 19S [Easting, Northing, Altitud]
      active: true
    });

    if (!this.adjacencyList.has(id)) {
      this.adjacencyList.set(id, new Map());
    }
  }

  /**
   * Agrega una arista (corredor aéreo) entre dos nodos
   * @param {string} fromId 
   * @param {string} toId 
   * @param {Object} properties - Metadatos de la arista (riesgo, restricciones)
   * @param {boolean} bidirectional - Si el vuelo es posible en ambos sentidos
   */
  addEdge(fromId, toId, properties = {}, bidirectional = true) {
    if (!this.nodes.has(fromId) || !this.nodes.has(toId)) {
      console.warn(`No se puede crear arista: nodos ${fromId} o ${toId} no existen.`);
      return;
    }

    const nodeA = this.nodes.get(fromId);
    const nodeB = this.nodes.get(toId);
    // Distancia métrica euclidiana ultrarrápida usando coordenadas UTM 19S
    const distanceMeters = this.calculateCartesianDistance(nodeA.utm, nodeB.utm);

    const edgeData = {
      from: fromId,
      to: toId,
      distance: distanceMeters,
      active: true,
      cost: distanceMeters, // Costo base (ponderable por función multi-objetivo)
      properties: { ...properties }
    };

    this.adjacencyList.get(fromId).set(toId, edgeData);

    if (bidirectional) {
      const reverseEdge = {
        ...edgeData,
        from: toId,
        to: fromId
      };
      this.adjacencyList.get(toId).set(fromId, reverseEdge);
    }
  }

  /**
   * Distancia espacial cartesiana euclidiana directa en metros (UTM 19S)
   * Complejidad: O(1) puro, ~15x más rápido que Haversine en exploraciones masivas (A*, Genéticos)
   * @param {[number, number, number]} u1 - [x1, y1, z1] en metros
   * @param {[number, number, number]} u2 - [x2, y2, z2] en metros
   * @returns {number} Distancia en metros
   */
  calculateCartesianDistance(u1, u2) {
    const dx = u2[0] - u1[0];
    const dy = u2[1] - u1[1];
    const dz = (u2[2] || 0) - (u1[2] || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  /**
   * Distancia espacial considerando esferoide terrestre (Haversine 3D aproximado)
   * Mantenido como fallback de compatibilidad para coordenadas angulares puras
   * @param {[number, number, number]} c1 - [lng1, lat1, alt1]
   * @param {[number, number, number]} c2 - [lng2, lat2, alt2]
   * @returns {number} Distancia en metros
   */
  calculateDistance(c1, c2) {
    const [lon1, lat1, alt1 = 0] = c1;
    const [lon2, lat2, alt2 = 0] = c2;

    const R = 6371000; // Radio de la Tierra en metros
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const horizontalDistance = R * c;
    const verticalDistance = Math.abs(alt2 - alt1);

    return Math.sqrt(horizontalDistance * horizontalDistance + verticalDistance * verticalDistance);
  }

  getNode(id) {
    return this.nodes.get(id);
  }

  getNeighbors(id) {
    return this.adjacencyList.get(id) || new Map();
  }

  getAllNodes() {
    return Array.from(this.nodes.values());
  }

  getAllEdges() {
    const edges = [];
    const seen = new Set();

    for (const [fromId, neighbors] of this.adjacencyList) {
      for (const [toId, edgeData] of neighbors) {
        const key = [fromId, toId].sort().join('--');
        if (!seen.has(key)) {
          seen.add(key);
          edges.push(edgeData);
        }
      }
    }
    return edges;
  }
}
