/**
 * categories.js
 * Configuración centralizada de las categorías de nodos de la red espacial.
 * Fuente única de verdad para nombres, íconos, colores CSS, etiquetas y prioridades.
 */

export const CATEGORIES = {
  base: {
    id: 'base',
    name: 'Base Operativa (SCER)',
    shortName: 'Base SCER',
    icon: '✈️',
    color: '#10b981', // Verde esmeralda
    tagClass: 'tag-base',
    colorClass: 'green',
    priority: 10,
    layerName: '✈ Base Operativa (Aeródromo Quintero)',
    description: 'Punto de despegue y aterrizaje principal / Retorno a Base (RTH)'
  },
  sinca: {
    id: 'sinca',
    name: 'Estaciones SINCA',
    shortName: 'SINCA',
    icon: '📡',
    color: '#38bdf8', // Cian
    tagClass: 'tag-sinca',
    colorClass: 'cyan',
    priority: 9,
    layerName: '📡 Estaciones SINCA (Calidad del Aire)',
    description: 'Estaciones oficiales de monitoreo atmosférico en tierra'
  },
  emission_source: {
    id: 'emission_source',
    name: 'Fuentes de Emisión',
    shortName: 'Industrias',
    icon: '🏭',
    color: '#ef4444', // Rojo
    tagClass: 'tag-emission_source',
    colorClass: 'red',
    priority: 8,
    layerName: '🏭 Fuentes Emisoras (Cordón Industrial)',
    description: 'Industrias, fundición y termoeléctricas de la Bahía'
  },
  health: {
    id: 'health',
    name: 'Centros de Salud',
    shortName: 'Salud',
    icon: '🏥',
    color: '#f43f5e', // Rosa rojizo
    tagClass: 'tag-health',
    colorClass: 'red',
    priority: 7,
    layerName: '🏥 Centros de Salud y Hospitales',
    description: 'Hospitales, CESFAM, postas y farmacias (receptores sensibles)'
  },
  education: {
    id: 'education',
    name: 'Red Educación',
    shortName: 'Educación',
    icon: '🏫',
    color: '#f97316', // Naranja
    tagClass: 'tag-education',
    colorClass: 'orange',
    priority: 7,
    layerName: '🏫 Colegios y Jardines Infantiles',
    description: 'Escuelas, liceos y jardines infantiles'
  },
  commercial: {
    id: 'commercial',
    name: 'Comercio / Abasto',
    shortName: 'Comercio',
    icon: '🛒',
    color: '#eab308', // Amarillo
    tagClass: 'tag-commercial',
    colorClass: 'yellow',
    priority: 5,
    layerName: '🛒 Comercio y Supermercados',
    description: 'Supermercados, locales de abasto y ferias libres'
  },
  crowded_area: {
    id: 'crowded_area',
    name: 'Concurrencia Masiva',
    shortName: 'Concurrencia',
    icon: '👥',
    color: '#ec4899', // Fucsia
    tagClass: 'tag-crowded_area',
    colorClass: 'pink',
    priority: 6,
    layerName: '👥 Plazas y Espacios Públicos',
    description: 'Plazas de Armas, estadios, bomberos y centros vecinales'
  },
  beach: {
    id: 'beach',
    name: 'Playas y Balnearios',
    shortName: 'Playas',
    icon: '🏖',
    color: '#0284c7', // Azul marino
    tagClass: 'tag-beach',
    colorClass: 'cyan',
    priority: 4,
    layerName: '🏖 Playas y Borde Costero',
    description: 'Playas, caletas y balnearios de la bahía'
  },
  hospitality: {
    id: 'hospitality',
    name: 'Hospedaje (Hoteles/Cabañas)',
    shortName: 'Hospedaje',
    icon: '🏨',
    color: '#a855f7', // Púrpura
    tagClass: 'tag-hospitality',
    colorClass: 'purple',
    priority: 3,
    layerName: '🏨 Hospedaje y Clubes Náuticos',
    description: 'Hoteles, cabañas de turismo y clubes náuticos'
  },
  restaurant: {
    id: 'restaurant',
    name: 'Gastronomía (Restaurantes)',
    shortName: 'Gastronomía',
    icon: '🍽',
    color: '#d97706', // Ámbar oscuro
    tagClass: 'tag-restaurant',
    colorClass: 'orange',
    priority: 3,
    layerName: '🍽 Gastronomía y Caletas',
    description: 'Restaurantes y locales gastronómicos costeros'
  },
  attraction: {
    id: 'attraction',
    name: 'Miradores y Turismo',
    shortName: 'Atracciones',
    icon: '📸',
    color: '#c026d3', // Magenta
    tagClass: 'tag-attraction',
    colorClass: 'pink',
    priority: 4,
    layerName: '📸 Miradores y Santuarios Naturales',
    description: 'Miradores turísticos, humedales y sitios de interés'
  },
  historic: {
    id: 'historic',
    name: 'Sitios Históricos',
    shortName: 'Históricos',
    icon: '🏛',
    color: '#92400e', // Marrón
    tagClass: 'tag-historic',
    colorClass: 'orange',
    priority: 4,
    layerName: '🏛 Sitios y Monumentos Históricos',
    description: 'Templos coloniales, sitios patrimoniales y museos'
  },
  auxiliary_hub: {
    id: 'auxiliary_hub',
    name: 'Hubs de Batería',
    shortName: 'Hubs',
    icon: '🔋',
    color: '#06b6d4', // Cyan verdoso
    tagClass: 'tag-auxiliary_hub',
    colorClass: 'green',
    priority: 9,
    layerName: '🔋 Hubs de Recarga y Pads Auxiliares',
    description: 'Puntos auxiliares de aterrizaje y carga de emergencia'
  }
};

/**
 * Retorna la configuración de una categoría por id, con fallback seguro
 */
export function getCategoryConfig(categoryId) {
  return CATEGORIES[categoryId] || {
    id: categoryId || 'other',
    name: 'Otros',
    shortName: 'Otros',
    icon: '📍',
    color: '#6b7280',
    tagClass: 'tag-other',
    colorClass: 'cyan',
    priority: 1,
    layerName: '📍 Otros Nodos',
    description: 'Nodos generales sin clasificar'
  };
}
