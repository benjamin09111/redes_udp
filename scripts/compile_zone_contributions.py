"""
compile_zone_contributions.py
Herramienta para compilar y validar aportes de los integrantes del grupo
desde archivos individuales por zona hacia el GeoJSON maestro (nodes.geojson).

Permite que cada compañero trabaje en su zona de manera independiente
sin conflictos en Git ni inconsistencias en el software.
"""

import json
import os
import sys

MASTER_NODES_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'data', 'nodes.geojson')

OFFICIAL_ZONES = [
    'urban_quintero',
    'urban_loncura',
    'urban_ventanas',
    'urban_greda',
    'urban_salinas_campiche',
    'urban_horcon',
    'urban_puchuncavi'
]

VALID_CATEGORIES = [
    'base',
    'sinca',
    'emission_source',
    'health',
    'education',
    'commercial',
    'crowded_area',
    'beach',
    'hospitality',
    'restaurant',
    'attraction',
    'historic',
    'auxiliary_hub'
]

def load_master_geojson():
    if not os.path.exists(MASTER_NODES_PATH):
        raise FileNotFoundError(f"No se encontró el archivo maestro en: {MASTER_NODES_PATH}")
    with open(MASTER_NODES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_master_geojson(data):
    with open(MASTER_NODES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Archivo maestro guardado con éxito: {len(data['features'])} nodos totales.")

def validate_node(node_feature):
    props = node_feature.get('properties', {})
    geom = node_feature.get('geometry', {})

    if not props.get('id'):
        return False, "Falta el atributo 'id'"
    if not props.get('name'):
        return False, f"Falta el atributo 'name' en {props.get('id')}"
    if props.get('category') not in VALID_CATEGORIES:
        return False, f"Categoría '{props.get('category')}' inválida en {props.get('id')}. Válidas: {VALID_CATEGORIES}"
    
    coords = geom.get('coordinates', [])
    if len(coords) < 2:
        return False, f"Coordenadas inválidas en {props.get('id')}. Requiere [lng, lat, alt]"
    
    lng, lat = coords[0], coords[1]
    if not (-71.60 <= lng <= -71.35 and -32.85 <= lat <= -32.65):
        return False, f"Coordenadas [{lng}, {lat}] fuera del scope operacional de la Bahía."

    return True, "OK"

def main():
    print("--- Validador y Compilador de Aportes de Nodos por Zona ---")
    data = load_master_geojson()
    print(f"Estado actual: {len(data['features'])} nodos en {MASTER_NODES_PATH}")
    
    # Validar integridad actual
    valid_count = 0
    for feat in data['features']:
        ok, msg = validate_node(feat)
        if ok:
            valid_count += 1
        else:
            print(f"⚠️ Advertencia: {msg}")

    print(f"Nodos válidos verificados: {valid_count}/{len(data['features'])}")

if __name__ == '__main__':
    main()
