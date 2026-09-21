import json

with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

existing_ids = {feat['properties']['id'] for feat in geojson_data['features']}
existing_coords = {(round(feat['geometry']['coordinates'][0], 4), round(feat['geometry']['coordinates'][1], 4)) for feat in geojson_data['features']}

print(f"Total nodos actuales antes de agregar: {len(geojson_data['features'])}")

new_nodes_to_add = [
    # 1. Nuevas Escuelas y Colegios descubiertos en OSM
    {
        "id": "edu_escuela_la_quebrada",
        "name": "Escuela Básica La Quebrada",
        "category": "education",
        "type": "education",
        "role": "Educación Rural: Escuela La Quebrada (Puchuncaví)",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.354472, -32.681434, 85]
    },
    {
        "id": "edu_escuela_pucalan",
        "name": "Escuela Básica Pucalán",
        "category": "education",
        "type": "education",
        "role": "Educación Rural: Escuela Pucalán (Ruta F-220, Puchuncaví)",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.344504, -32.752103, 110]
    },
    {
        "id": "edu_escuela_el_rincon",
        "name": "Escuela Básica El Rincón",
        "category": "education",
        "type": "education",
        "role": "Educación Rural: Escuela El Rincón (Puchuncaví)",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.368697, -32.724875, 90]
    },
    {
        "id": "edu_colegio_pioneros",
        "name": "Colegio Pioneros Costa (Puchuncaví)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Particular Pioneros Costa (Alto Rungue)",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.430790, -32.671900, 75]
    },
    {
        "id": "edu_colegio_ingles_norte",
        "name": "Colegio Inglés (Sede Básica)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Inglés Quintero (Recinto Básica)",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.531588, -32.781632, 22]
    },
    {
        "id": "edu_jardin_ventanas",
        "name": "Jardín y Sala Cuna Las Ventanas",
        "category": "education",
        "type": "education",
        "role": "Educación Inicial: Jardín Infantil Bellavista Las Ventanas",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.486524, -32.740037, 14]
    },

    # 2. Infraestructura deportiva y cívica identificada en OSM
    {
        "id": "crowd_cancha_horcon",
        "name": "Cancha de Fútbol Horcón",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Complejo Deportivo y Cancha Comunitaria Caleta Horcón",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.488409, -32.737281, 15]
    },
    {
        "id": "crowd_quintero_padel",
        "name": "Club Quintero Pádel",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Centro Recreativo y Canchas Deportivas Quintero",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.527753, -32.799943, 18]
    },
    {
        "id": "crowd_banco_chile_ventanas",
        "name": "Banco de Chile (Sucursal Las Ventanas)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Servicio Bancario y Punto de Afluencia Las Ventanas",
        "icon": "🏦",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.480393, -32.769736, 12]
    },

    # 3. Puntos de Abasto de Combustible e Interfaz de Riesgo (SORA)
    {
        "id": "comm_copec_ventanas",
        "name": "Estación de Servicio Copec Ventanas",
        "category": "commercial",
        "type": "commercial",
        "role": "Abastecimiento de Combustible y Riesgo Inflamable (Ruta F-30E)",
        "icon": "⛽",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.468597, -32.741347, 15]
    },
    {
        "id": "comm_shell_puchuncavi",
        "name": "Estación de Servicio Shell Puchuncaví",
        "category": "commercial",
        "type": "commercial",
        "role": "Abastecimiento de Combustible y Punto Vial Puchuncaví",
        "icon": "⛽",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.416752, -32.723952, 88]
    }
]

added_count = 0
for n in new_nodes_to_add:
    c_key = (round(n['coords'][0], 4), round(n['coords'][1], 4))
    if n['id'] in existing_ids or c_key in existing_coords:
        print(f"Omitido por duplicidad: {n['name']}")
        continue
    
    existing_ids.add(n['id'])
    existing_coords.add(c_key)
    
    geojson_data['features'].append({
        "type": "Feature",
        "properties": {
            "id": n["id"],
            "name": n["name"],
            "category": n["category"],
            "type": n["type"],
            "role": n["role"],
            "icon": n["icon"],
            "color": n["color"],
            "priority": n["priority"],
            "elevation_msnm": n["coords"][2],
            "pollutants": []
        },
        "geometry": {
            "type": "Point",
            "coordinates": n["coords"]
        }
    })
    added_count += 1
    print(f"Agregado con éxito: {n['name']} [{n['category']}]")

output_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)

print(f"\nProceso finalizado. Total nuevos nodos agregados: {added_count}")
print(f"Total nodos en red: {len(geojson_data['features'])}")

# Conteo por categoria
counts = {}
for feat in geojson_data['features']:
    cat = feat['properties']['category']
    counts[cat] = counts.get(cat, 0) + 1

print("\n--- RESUMEN ACTUALIZADO ---")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
