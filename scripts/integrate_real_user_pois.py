import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NODES_PATH = ROOT / "public" / "data" / "nodes.geojson"

with open(NODES_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Existing IDs
existing_ids = {feat["properties"]["id"] for feat in data["features"]}
print(f"Nodos iniciales: {len(data['features'])}")

# Real POIs directly taken from the 3 user screenshots
# 1. Chocota / Horcon
# 2. Loncura residencial / interior
# 3. Quintero Sur residencial / equipamiento
# 4. Campiche interior
vetted_pois = [
    # --- ZONA 1: CHOCOTA / HORCÓN ---
    {
        "id": "poi_chocota_junta_camelias",
        "name": "Comunidad Vecinal Las Camelias de Horcón",
        "category": "crowded_area",
        "type": "community_centre",
        "role": "Organización Comunitaria y Zona Residencial Las Camelias",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 42.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48415,
        "lat": -32.72538
    },
    {
        "id": "poi_chocota_villa_horcomad",
        "name": "Villa Horcomad (Área Residencial)",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial Consolidado Villa Horcomad",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 38.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48989,
        "lat": -32.71623
    },
    {
        "id": "poi_chocota_centro",
        "name": "Cruce Central La Chocota",
        "category": "commercial",
        "type": "junction",
        "role": "Intersección y Eje de Servicios Locales La Chocota",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "elevation_msnm": 45.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48742,
        "lat": -32.73020
    },
    {
        "id": "poi_chocota_club_tebo",
        "name": "Club El Tebo / Caleta El Tebo",
        "category": "beach",
        "type": "beach_resort",
        "role": "Ensenada y Complejo Turístico El Tebo",
        "icon": "🏖️",
        "color": "#06b6d4",
        "priority": 4,
        "elevation_msnm": 12.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.50083,
        "lat": -32.72519
    },
    {
        "id": "poi_chocota_villa_bosque",
        "name": "Villa El Bosque de Horcón",
        "category": "crowded_area",
        "type": "residential",
        "role": "Conjunto Residencial Villa El Bosque",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 40.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48462,
        "lat": -32.72468
    },
    {
        "id": "poi_chocota_mirador_pelicanos",
        "name": "Mirador Bahía Pelícanos",
        "category": "attraction",
        "type": "viewpoint",
        "role": "Punto Panorámico y Atractivo Costero Pelícanos",
        "icon": "📷",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 28.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48750,
        "lat": -32.71250
    },
    {
        "id": "poi_chocota_alto_mar",
        "name": "Sector Alto Mar Horcón",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial Alto Mar y Acceso Este",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 52.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.47950,
        "lat": -32.71680
    },
    {
        "id": "poi_chocota_diagonal",
        "name": "Eje Diagonal Chocota / Los Corales",
        "category": "crowded_area",
        "type": "junction",
        "role": "Corredor Conector Diagonal Chocota",
        "icon": "🛣️",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 41.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48620,
        "lat": -32.72150
    },
    {
        "id": "poi_chocota_ponderosa",
        "name": "Villa La Ponderosa / Los Jotes",
        "category": "crowded_area",
        "type": "residential",
        "role": "Área Residencial La Ponderosa - Los Jotes",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 36.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.48810,
        "lat": -32.71850
    },
    {
        "id": "poi_chocota_camino_viejo",
        "name": "Acceso Norte / Camino Viejo Horcón",
        "category": "crowded_area",
        "type": "junction",
        "role": "Interconexión Vial Camino Viejo a Horcón",
        "icon": "🛣️",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 48.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.47720,
        "lat": -32.72300
    },

    # --- ZONA 2: LONCURA RESIDENCIAL E INTERIOR ---
    {
        "id": "poi_loncura_german_riesco",
        "name": "Villa Germán Riesco",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial Núcleo Villa Germán Riesco",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 18.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50180,
        "lat": -32.78834
    },
    {
        "id": "poi_loncura_los_alerces",
        "name": "Villa Los Alerces",
        "category": "crowded_area",
        "type": "residential",
        "role": "Población Los Alerces Loncura",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 20.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50259,
        "lat": -32.79041
    },
    {
        "id": "poi_loncura_manutara",
        "name": "Villa Manutara Loncura",
        "category": "crowded_area",
        "type": "residential",
        "role": "Zona Poblacional Villa Manutara",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 22.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50088,
        "lat": -32.79171
    },
    {
        "id": "poi_loncura_av_bosque",
        "name": "Eje Comercial Av. El Bosque Loncura",
        "category": "commercial",
        "type": "commercial",
        "role": "Arteria Comercial y Flujo Vecinal Av. El Bosque",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "elevation_msnm": 24.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50320,
        "lat": -32.79350
    },
    {
        "id": "poi_loncura_almacen_gaston",
        "name": "Almacén Donde el Gastón",
        "category": "commercial",
        "type": "shop",
        "role": "Comercio de Barrio y Abasto Local Loncura",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "elevation_msnm": 19.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50373,
        "lat": -32.78953
    },
    {
        "id": "poi_loncura_union_progreso",
        "name": "Junta de Vecinos Unión y Progreso Loncura",
        "category": "crowded_area",
        "type": "community_centre",
        "role": "Centro Comunitario y Sede Social Vecinal",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 19.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50421,
        "lat": -32.78793
    },
    {
        "id": "poi_loncura_estadio",
        "name": "Estadio Comunitario Loncura",
        "category": "crowded_area",
        "type": "pitch",
        "role": "Cancha de Fútbol y Actividad Deportiva Loncura",
        "icon": "⚽",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 25.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50150,
        "lat": -32.79580
    },
    {
        "id": "poi_loncura_las_jaibas",
        "name": "Sector Residencial Las Jaibas / Las Arenas",
        "category": "crowded_area",
        "type": "residential",
        "role": "Área Habitacional Las Jaibas y Pasajes Interiores",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 21.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.49850,
        "lat": -32.79320
    },
    {
        "id": "poi_loncura_los_mellizos",
        "name": "Villa Los Mellizos / Pomabamba",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial Norte Loncura",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 14.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50720,
        "lat": -32.78455
    },
    {
        "id": "poi_loncura_chimbote_huaras",
        "name": "Cruce Chimbote / Huaras",
        "category": "crowded_area",
        "type": "junction",
        "role": "Intersección Central y Conexión Vial Loncura",
        "icon": "🛣️",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 17.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.50350,
        "lat": -32.78750
    },
    {
        "id": "poi_loncura_parque_solar",
        "name": "Monitoreo Perimetral PFV Loncura",
        "category": "crowded_area",
        "type": "infrastructure",
        "role": "Instalación de Generación Fotovoltaica y Monitoreo",
        "icon": "⚡",
        "color": "#ec4899",
        "priority": 3,
        "elevation_msnm": 23.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.49700,
        "lat": -32.78950
    },

    # --- ZONA 3: QUINTERO SUR Y EQUIPAMIENTO ---
    {
        "id": "poi_quintero_sur_porvenir",
        "name": "Población Porvenir (Eje Cívico)",
        "category": "crowded_area",
        "type": "residential",
        "role": "Área de Concentración Poblacional Porvenir",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 5,
        "elevation_msnm": 32.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53073,
        "lat": -32.79148
    },
    {
        "id": "poi_quintero_sur_lomas",
        "name": "Población Lomas de Quintero",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial en Altura Lomas de Quintero",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 45.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53292,
        "lat": -32.79861
    },
    {
        "id": "poi_quintero_sur_independencia",
        "name": "Villa Independencia",
        "category": "crowded_area",
        "type": "residential",
        "role": "Sector Residencial Villa Independencia",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 42.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53702,
        "lat": -32.79876
    },
    {
        "id": "poi_quintero_sur_colinas_mar",
        "name": "Población Colinas del Mar",
        "category": "crowded_area",
        "type": "residential",
        "role": "Barrio Habitacional Colinas del Mar",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 48.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53342,
        "lat": -32.80106
    },
    {
        "id": "poi_quintero_sur_estadio_muni",
        "name": "Estadio Municipal de Quintero Raúl Vargas",
        "category": "crowded_area",
        "type": "stadium",
        "role": "Principal Recinto Polideportivo Municipal de Quintero",
        "icon": "⚽",
        "color": "#ec4899",
        "priority": 5,
        "elevation_msnm": 35.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52946,
        "lat": -32.79889
    },
    {
        "id": "poi_quintero_sur_copec_f210",
        "name": "Estación Copec F-210 Acceso Sur",
        "category": "commercial",
        "type": "fuel",
        "role": "Servicentro y Abastecimiento Ruta F-210",
        "icon": "⛽",
        "color": "#eab308",
        "priority": 4,
        "elevation_msnm": 30.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52666,
        "lat": -32.79153
    },
    {
        "id": "poi_quintero_sur_shell_prat",
        "name": "Estación Shell Arturo Prat",
        "category": "commercial",
        "type": "fuel",
        "role": "Servicentro Arturo Prat Cruce Sur",
        "icon": "⛽",
        "color": "#eab308",
        "priority": 4,
        "elevation_msnm": 28.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52705,
        "lat": -32.78709
    },
    {
        "id": "poi_quintero_sur_ann_sullivan",
        "name": "Escuela Especial Ann Sullivan",
        "category": "education",
        "type": "school",
        "role": "Establecimiento Educacional Especializado",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "elevation_msnm": 29.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52970,
        "lat": -32.78568
    },
    {
        "id": "poi_quintero_sur_multicancha_pinos",
        "name": "Multicancha Plaza Los Pinos",
        "category": "crowded_area",
        "type": "pitch",
        "role": "Espacio Deportivo y Parque Vecinal Los Pinos",
        "icon": "⚽",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 33.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52956,
        "lat": -32.79327
    },
    {
        "id": "poi_quintero_sur_diego_portales",
        "name": "Sector Residencial Diego Portales",
        "category": "crowded_area",
        "type": "residential",
        "role": "Población Diego Portales y Calles Salas",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 38.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53720,
        "lat": -32.79250
    },
    {
        "id": "poi_quintero_sur_sanfuentes",
        "name": "Plaza Sanfuentes Poniente",
        "category": "crowded_area",
        "type": "park",
        "role": "Plaza Pública y Área Verde Sanfuentes",
        "icon": "🌳",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 34.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.53680,
        "lat": -32.78520
    },
    {
        "id": "poi_quintero_sur_las_brisas",
        "name": "Sector Residencial Las Brisas",
        "category": "crowded_area",
        "type": "residential",
        "role": "Condominio y Zona Residencial Las Brisas de Quintero",
        "icon": "🏘️",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 31.0,
        "pollutants": [],
        "city": "Quintero",
        "lon": -71.52780,
        "lat": -32.79600
    },

    # --- ZONA 4: CAMPICHE RURAL / INTERIOR ---
    {
        "id": "poi_campiche_escuela_rural",
        "name": "Escuela Rural Campiche",
        "category": "education",
        "type": "school",
        "role": "Educación Rural Básica Campiche",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "elevation_msnm": 22.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.46820,
        "lat": -32.73850
    },
    {
        "id": "poi_campiche_plaza_comunitaria",
        "name": "Plaza Comunitaria Campiche",
        "category": "crowded_area",
        "type": "park",
        "role": "Espacio Público Central y Área de Recreación Campiche",
        "icon": "🌳",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 20.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.46550,
        "lat": -32.73600
    },
    {
        "id": "poi_campiche_sede_social",
        "name": "Sede Social y Club Campiche",
        "category": "crowded_area",
        "type": "community_centre",
        "role": "Club Social, Cultural y Deportivo Campiche",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "elevation_msnm": 21.0,
        "pollutants": [],
        "city": "Puchuncaví",
        "lon": -71.46300,
        "lat": -32.73520
    }
]

added_count = 0
for poi in vetted_pois:
    if poi["id"] in existing_ids:
        continue
    feat = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [poi["lon"], poi["lat"]]
        },
        "properties": {
            "id": poi["id"],
            "name": poi["name"],
            "category": poi["category"],
            "type": poi["type"],
            "role": poi["role"],
            "icon": poi["icon"],
            "color": poi["color"],
            "priority": poi["priority"],
            "elevation_msnm": poi["elevation_msnm"],
            "pollutants": poi["pollutants"],
            "city": poi["city"]
        }
    }
    data["features"].append(feat)
    existing_ids.add(poi["id"])
    added_count += 1

print(f"POIs reales agregados: {added_count}")
print(f"Total nuevo de nodos: {len(data['features'])}")

with open(NODES_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Guardado exitoso en public/data/nodes.geojson")

