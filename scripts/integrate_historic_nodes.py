import json
import math

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

features = geojson_data['features']
print(f"Features iniciales: {len(features)}")

# 1. Re-clasificar nodos existentes con valor histórico reconocido a category="historic"
existing_to_historic_ids = {
    'attr_12463695125': {
        'name': 'Museo de Sitio Melinka-Puchuncaví',
        'role': 'Museo de Memoria Histórica y Derechos Humanos Melinka-Puchuncaví'
    },
    'attr_13271144993': {
        'name': 'Museo Quintero Vive (Casa Estación)',
        'role': 'Museo Histórico Municipal y Centro de Interpretación Patrimonial'
    },
    'attr_980749157': {
        'name': 'Museo de Historia Natural de Puchuncaví',
        'role': 'Museo Paleontológico y Arqueológico (Yacimiento Fósil y Cultura Bato)'
    },
    'attr_1300318200': {
        'name': 'Casa Museo Almirante Lord Thomas Cochrane (Valle Alegre)',
        'role': 'Casona Histórica y Museo Colonial del Almirante Lord Cochrane'
    },
    'attr_1347402689': {
        'name': 'Casa Museo Downey (Quintero)',
        'role': 'Residencia Patrimonial Histórica y Museo de Arte y Tradición'
    },
    'church_150951528': {
        'name': 'Iglesia de Piedra (Monumento Arquitectónico Quintero)',
        'role': 'Monumento Histórico y Arquitectónico Religioso de Piedra Tallada'
    },
    'crowd_parroquia_puchuncavi': {
        'name': 'Parroquia Nuestra Señora del Rosario (Templo Histórico Colonial 1691)',
        'role': 'Templo Colonial de 1691 - Hito Histórico y Religioso de Puchuncaví'
    }
}

for feat in features:
    fid = feat['properties'].get('id')
    if fid in existing_to_historic_ids:
        info = existing_to_historic_ids[fid]
        feat['properties']['category'] = 'historic'
        feat['properties']['icon'] = '🏛'
        feat['properties']['color'] = '#d97706'
        feat['properties']['name'] = info['name']
        feat['properties']['role'] = info['role']
        feat['properties']['priority'] = 4

# 2. Nuevos nodos históricos a incorporar (incluyendo Juan Manuel Ureta 222)
new_historic_nodes = [
    {
        "id": "hist_fundo_ureta_222_campiche",
        "name": "Sitio Histórico y Casona Fundo Cordero Contreras (Juan Manuel Ureta 222, Campiche)",
        "category": "historic",
        "type": "historic",
        "role": "Lugar Histórico Rural, Casona y Fundo Patrimonial (Juan Manuel Ureta 222, Campiche)",
        "icon": "🏛",
        "color": "#d97706",
        "priority": 4,
        "city": "Las Salinas / Campiche",
        "coords": [-71.448500, -32.731500, 45]
    },
    {
        "id": "hist_sitio_memoria_melinka",
        "name": "Sitio de Memoria Balneario Popular y Campo Melinka (Monumento Nacional D.38)",
        "category": "historic",
        "type": "monument",
        "role": "Monumento Histórico Nacional (Sitio de Memoria y Conciencia DDHH)",
        "icon": "📜",
        "color": "#d97706",
        "priority": 5,
        "city": "Puchuncaví",
        "coords": [-71.408080, -32.719707, 85]
    },
    {
        "id": "hist_santuario_las_petras",
        "name": "Santuario de la Naturaleza Bosque Las Petras (Loncura)",
        "category": "historic",
        "type": "sanctuary",
        "role": "Santuario de la Naturaleza y Bosque Relicto Protegido por Decreto 1993",
        "icon": "🌳",
        "color": "#15803d",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.503500, -32.783000, 10]
    },
    {
        "id": "hist_conchal_bato_aconcagua",
        "name": "Conchal Indígena Arqueológico Bato y Aconcagua (Loncura)",
        "category": "historic",
        "type": "archaeological_site",
        "role": "Yacimiento Arqueológico Prehispánico - Asentamiento Tradición Bato",
        "icon": "🏺",
        "color": "#d97706",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.512628, -32.791928, 14]
    },
    {
        "id": "hist_parque_luisa_sebire",
        "name": "Parque Histórico Municipal Luisa Sebiré de Cousiño",
        "category": "historic",
        "type": "park",
        "role": "Parque Histórico Emblemático y Legado Fundacional de Quintero",
        "icon": "🏛",
        "color": "#d97706",
        "priority": 4,
        "city": "Quintero",
        "coords": [-71.526500, -32.778500, 25]
    },
    {
        "id": "hist_puente_de_los_deseos",
        "name": "Puente de los Deseos (Hito Histórico Horcón)",
        "category": "historic",
        "type": "historic",
        "role": "Hito Patrimonial y Tradición Cultural de Caleta Horcón",
        "icon": "🌉",
        "color": "#d97706",
        "priority": 3,
        "city": "Horcón",
        "coords": [-71.492676, -32.708922, 12]
    },
    {
        "id": "hist_cruz_ermita_campiche",
        "name": "Cruz y Ermita Devocional Histórica de Campiche",
        "category": "historic",
        "type": "shrine",
        "role": "Monumento Devocional Campesino y Patrimonio Tradicional Campiche",
        "icon": "✝",
        "color": "#d97706",
        "priority": 3,
        "city": "Las Salinas / Campiche",
        "coords": [-71.452159, -32.734692, 42]
    },
    {
        "id": "hist_faro_punta_condell",
        "name": "Faro Punta Condell (Faro Histórico Bahía Quintero)",
        "category": "historic",
        "type": "lighthouse",
        "role": "Hito Histórico de Navegación Marítima y Señalización Costera",
        "icon": "🚨",
        "color": "#d97706",
        "priority": 4,
        "city": "Quintero",
        "coords": [-71.533800, -32.766100, 30]
    },
    {
        "id": "hist_cueva_del_pirata",
        "name": "Cueva del Pirata (Sitio Histórico y Legendario Quintero)",
        "category": "historic",
        "type": "historic",
        "role": "Sitio Histórico-Cultural Asociado a Corsarios Ingleses del Siglo XVI",
        "icon": "🏴‍☠️",
        "color": "#d97706",
        "priority": 3,
        "city": "Quintero",
        "coords": [-71.537200, -32.775800, 15]
    }
]

existing_coords = [(f['geometry']['coordinates'][0], f['geometry']['coordinates'][1]) for f in features]

def dist_m(p1, p2):
    R = 6371000
    phi1, phi2 = math.radians(p1[1]), math.radians(p2[1])
    dphi = math.radians(p2[1] - p1[1])
    dlam = math.radians(p2[0] - p1[0])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

added_count = 0
for nh in new_historic_nodes:
    lon, lat, z = nh['coords']
    # Check if existing within 25m
    too_close = False
    for ex in existing_coords:
        if dist_m((lon, lat), ex) < 25:
            too_close = True
            break
    if too_close:
        print(f"Omitiendo nodo duplicado: {nh['name']}")
        continue
        
    feat = {
        "type": "Feature",
        "properties": {
            "id": nh['id'],
            "name": nh['name'],
            "category": nh['category'],
            "type": nh['type'],
            "role": nh['role'],
            "icon": nh['icon'],
            "color": nh['color'],
            "priority": nh['priority'],
            "city": nh['city']
        },
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon, 6), round(lat, 6), z]
        }
    }
    features.append(feat)
    existing_coords.append((lon, lat))
    added_count += 1

print(f"Nuevos nodos históricos agregados: {added_count}")
print(f"TOTAL FINAL DE NODOS: {len(features)}")

# Resumen de categorías
cat_counts = {}
for f in features:
    c = f['properties']['category']
    cat_counts[c] = cat_counts.get(c, 0) + 1

print("\n--- NUEVO RESUMEN POR CATEGORÍA ---")
for k, v in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"- {k}: {v}")

geojson_data['features'] = features
out_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)

print(f"\n[ÉXITO] Archivo {out_path} actualizado correctamente.")
