import json

# =============================================================================
# 1. BASE PRINCIPAL
# =============================================================================
base_nodes = [
    {
        "id": "base_scer",
        "name": "Aeródromo de Quintero (SCER)",
        "category": "base",
        "type": "base",
        "role": "Base de Despacho Principal y Retorno Seguro (RTH)",
        "icon": "✈",
        "color": "#10b981",
        "priority": 0,
        "coords": [-71.517300, -32.784200, 28]
    }
]

# =============================================================================
# 2. ESTACIONES SINCA OFICIALES (9)
# =============================================================================
sinca_nodes = [
    {
        "id": "sinca_puchuncavi",
        "name": "Estación SINCA Puchuncaví",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 1,
        "coords": [-71.407326, -32.718731, 95]
    },
    {
        "id": "sinca_campiche",
        "name": "Estación SINCA Campiche",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2,
        "coords": [-71.450857, -32.736201, 30]
    },
    {
        "id": "sinca_ventanas",
        "name": "Estación SINCA Ventanas",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3,
        "coords": [-71.480844, -32.741842, 12]
    },
    {
        "id": "sinca_la_greda",
        "name": "Estación SINCA La Greda",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3,
        "coords": [-71.474214, -32.748276, 35]
    },
    {
        "id": "sinca_los_maitenes",
        "name": "Estación SINCA Los Maitenes",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10"],
        "priority": 2,
        "coords": [-71.454509, -32.764345, 45]
    },
    {
        "id": "sinca_quintero",
        "name": "Estación SINCA Quintero",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5", "O3"],
        "priority": 2,
        "coords": [-71.535258, -32.772321, 18]
    },
    {
        "id": "sinca_centro_quintero",
        "name": "Estación SINCA Centro Quintero",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3,
        "coords": [-71.532226, -32.787721, 22]
    },
    {
        "id": "sinca_loncura",
        "name": "Estación SINCA Loncura",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2,
        "coords": [-71.496420, -32.794914, 15]
    },
    {
        "id": "sinca_sur",
        "name": "Estación SINCA Sur",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9",
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2,
        "coords": [-71.483406, -32.801052, 25]
    }
]

# =============================================================================
# 3. FUENTES DE EMISIÓN INDUSTRIAL (Misiones 3D en Altura 50-110m)
# =============================================================================
industry_nodes = [
    {
        "id": "ind_codelco",
        "name": "Fundición Codelco Ventanas",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Fundición de Cobre (Emisión SO2/MP)",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 4,
        "coords": [-71.481620, -32.759610, 15]
    },
    {
        "id": "ind_termoelectrica",
        "name": "Termoeléctrica Ventanas (AES Andes)",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Generación Eléctrica a Carbón/Gas",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 4,
        "coords": [-71.479200, -32.744500, 10]
    },
    {
        "id": "ind_gnl",
        "name": "Terminal Marítimo GNL Quintero",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Terminal Regasificadora de Gas Natural",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 3,
        "coords": [-71.489460, -32.778690, 5]
    },
    {
        "id": "ind_enap",
        "name": "Terminal y Refinería ENAP Quintero",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Almacenamiento y Carga de Hidrocarburos",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 3,
        "coords": [-71.490990, -32.782650, 12]
    },
    {
        "id": "ind_oxiquim",
        "name": "Planta Química Oxiquim",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Terminal Químico y Graneles Líquidos",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 3,
        "coords": [-71.487960, -32.768810, 8]
    },
    {
        "id": "ind_puerto_ventanas",
        "name": "Puerto Ventanas",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Terminal Portuario de Graneles Sólidos",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 2,
        "coords": [-71.489630, -32.752690, 5]
    },
    {
        "id": "ind_asfalto_quintero",
        "name": "Planta Asfaltos / Combustibles Quintero",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Derivados de Petróleo y Asfaltos",
        "icon": "🏭",
        "color": "#a855f7",
        "priority": 2,
        "coords": [-71.493500, -32.780100, 10]
    }
]

# =============================================================================
# 4. RED DE SALUD Y EMERGENCIAS MÉDICAS (Hospitales, CESFAM, Postas, SAPU)
# =============================================================================
health_nodes = [
    {
        "id": "health_hosp_adriana_cousino",
        "name": "Hospital Adriana Cousiño (Quintero)",
        "category": "health",
        "type": "health",
        "role": "Salud: Hospital Base Comunal Quintero",
        "icon": "🏥",
        "color": "#ef4444", # Red
        "priority": 5,
        "coords": [-71.531107, -32.779310, 25]
    },
    {
        "id": "health_cesfam_quintero",
        "name": "CESFAM Quintero",
        "category": "health",
        "type": "health",
        "role": "Salud: Centro de Salud Familiar Quintero",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.534964, -32.795313, 20]
    },
    {
        "id": "health_cesfam_ventanas",
        "name": "CESFAM Las Ventanas",
        "category": "health",
        "type": "health",
        "role": "Salud: Centro de Salud Familiar Las Ventanas",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.484575, -32.742325, 14]
    },
    {
        "id": "health_cesfam_puchuncavi",
        "name": "CESFAM Puchuncaví",
        "category": "health",
        "type": "health",
        "role": "Salud: Centro de Salud Familiar Puchuncaví Centro",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.415978, -32.725774, 90]
    },
    {
        "id": "health_sapu_ventanas",
        "name": "SAPU Las Ventanas",
        "category": "health",
        "type": "health",
        "role": "Salud: Servicio de Atención Primaria de Urgencia",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.483818, -32.742342, 14]
    },
    {
        "id": "health_cecof_loncura",
        "name": "CECOF Loncura",
        "category": "health",
        "type": "health",
        "role": "Salud: Centro Comunitario de Salud Familiar Loncura",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.503992, -32.788325, 15]
    },
    {
        "id": "health_posta_loncura",
        "name": "Posta de Salud Rural Loncura",
        "category": "health",
        "type": "health",
        "role": "Salud: Posta de Atención Rural Loncura",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.502156, -32.789708, 15]
    },
    {
        "id": "health_posta_horcon",
        "name": "Posta de Salud Rural Horcón",
        "category": "health",
        "type": "health",
        "role": "Salud: Posta Rural Caleta Horcón",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.488710, -32.711267, 10]
    },
    {
        "id": "health_cruz_roja",
        "name": "Cruz Roja Chilena (Quintero)",
        "category": "health",
        "type": "health",
        "role": "Salud y Rescate: Sede Comunal Cruz Roja",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.527323, -32.787385, 22]
    },
    {
        "id": "health_centro_medico_quintero",
        "name": "Centro Médico y Dental Quintero",
        "category": "health",
        "type": "health",
        "role": "Salud: Centro Médico Ambulatorio Quintero",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.528235, -32.782790, 24]
    }
]

# =============================================================================
# 5. RED DE EDUCACIÓN (Colegios, Escuelas Básicas, Liceos, Jardines)
# =============================================================================
education_nodes = [
    {
        "id": "edu_escuela_la_greda",
        "name": "Escuela Básica La Greda",
        "category": "education",
        "type": "education",
        "role": "Educación Crítica: Escuela La Greda (Zona PPDA)",
        "icon": "🏫",
        "color": "#f97316", # Orange
        "priority": 5,
        "coords": [-71.460807, -32.736423, 35]
    },
    {
        "id": "edu_colegio_sargento_aldea",
        "name": "Colegio Sargento Aldea (Ventanas)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Básico Las Ventanas",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.485693, -32.742413, 12]
    },
    {
        "id": "edu_escuela_la_chocota",
        "name": "Escuela La Chocota",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Rural Chocota",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.487073, -32.729684, 20]
    },
    {
        "id": "edu_escuela_campiche",
        "name": "Escuela Campiche",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Rural Campiche",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.451108, -32.735326, 30]
    },
    {
        "id": "edu_escuela_horcon",
        "name": "Escuela Básica de Horcón",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Caleta Horcón",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.488109, -32.713264, 18]
    },
    {
        "id": "edu_colegio_velasquez",
        "name": "Complejo Educacional Gral. José Velásquez",
        "category": "education",
        "type": "education",
        "role": "Educación: Liceo Principal Comuna de Puchuncaví",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.417052, -32.726495, 85]
    },
    {
        "id": "edu_colegio_san_hernaldo",
        "name": "Colegio San Hernaldo (Puchuncaví)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Particular Subvencionado Puchuncaví",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.411281, -32.728541, 88]
    },
    {
        "id": "edu_escuela_el_rungue",
        "name": "Escuela Básica El Rungue",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Rural Sector El Rungue",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.406807, -32.697141, 95]
    },
    {
        "id": "edu_escuela_tortel",
        "name": "Escuela Juan José Tortel (Valle Alegre)",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Valle Alegre",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.440806, -32.811670, 70]
    },
    {
        "id": "edu_liceo_politecnico_quintero",
        "name": "Liceo Politécnico de Quintero",
        "category": "education",
        "type": "education",
        "role": "Educación: Liceo Técnico Profesional de Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.527444, -32.788239, 22]
    },
    {
        "id": "edu_colegio_don_orione",
        "name": "Colegio Don Orione (Quintero)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Básico y Media Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.533909, -32.785821, 24]
    },
    {
        "id": "edu_colegio_ingles",
        "name": "Colegio Inglés Quintero",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Inglés de Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.531017, -32.783333, 22]
    },
    {
        "id": "edu_colegio_alonso_quintero",
        "name": "Colegio Alonso de Quintero",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Básico y Medio Alonso de Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.531874, -32.801792, 18]
    },
    {
        "id": "edu_colegio_santa_filomena",
        "name": "Colegio Santa Filomena (Quintero)",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Básico Santa Filomena",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.529165, -32.780896, 25]
    },
    {
        "id": "edu_escuela_francia",
        "name": "Escuela República de Francia (Quintero)",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Municipal Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.530809, -32.791122, 20]
    },
    {
        "id": "edu_escuela_narau",
        "name": "Escuela Valle de Narau (Quintero)",
        "category": "education",
        "type": "education",
        "role": "Educación: Escuela Básica Valle de Narau",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.534055, -32.794139, 20]
    },
    {
        "id": "edu_colegio_costa_mauco",
        "name": "Colegio Artístico Costa Mauco",
        "category": "education",
        "type": "education",
        "role": "Educación: Colegio Artístico Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.530444, -32.785358, 23]
    },
    {
        "id": "edu_centro_faro",
        "name": "Centro Educacional El Faro",
        "category": "education",
        "type": "education",
        "role": "Educación: Centro Educativo Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.530829, -32.776888, 25]
    },
    {
        "id": "edu_escuela_nuevo_mundo",
        "name": "Escuela de Lenguaje Nuevo Mundo",
        "category": "education",
        "type": "education",
        "role": "Educación Especial: Escuela de Lenguaje Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.531264, -32.776616, 25]
    },
    {
        "id": "edu_escuela_san_gabriel",
        "name": "Escuela de Lenguaje San Gabriel",
        "category": "education",
        "type": "education",
        "role": "Educación Especial: Escuela de Lenguaje San Gabriel",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.529683, -32.789190, 22]
    },
    {
        "id": "edu_parvulos_altamira",
        "name": "Escuela de Párvulos Altamira",
        "category": "education",
        "type": "education",
        "role": "Educación Parvularia: Kinder y Pre-Kinder Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.532615, -32.787692, 22]
    },
    {
        "id": "edu_jardin_bambi",
        "name": "Jardín Infantil Bambi (JUNJI)",
        "category": "education",
        "type": "education",
        "role": "Educación Inicial: Jardín Infantil Comunal Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.536773, -32.797418, 18]
    },
    {
        "id": "edu_escuela_lourdes",
        "name": "Escuela Especial Lourdes (Quintero)",
        "category": "education",
        "type": "education",
        "role": "Educación Diferencial: Escuela Especial Lourdes",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.534410, -32.777271, 20]
    }
]

# =============================================================================
# 6. HUBS AUXILIARES DE RECARGA (Nidos de Drones / Baterías)
# =============================================================================
hub_nodes = [
    {
        "id": "hub_puchuncavi",
        "name": "Hub Auxiliar Puchuncaví (Bomberos/Estadio)",
        "category": "auxiliary_hub",
        "type": "hub",
        "role": "Nido de Recarga Auxiliar y Baterías de Reemplazo (Sector Este)",
        "icon": "🔋",
        "color": "#06b6d4",
        "priority": 2,
        "coords": [-71.412000, -32.723000, 90]
    },
    {
        "id": "hub_loncura",
        "name": "Hub Auxiliar Loncura (Punto de Apoyo Sur)",
        "category": "auxiliary_hub",
        "type": "hub",
        "role": "Nido de Recarga y Mantenimiento Auxiliar (Sector Sur)",
        "icon": "🔋",
        "color": "#06b6d4",
        "priority": 2,
        "coords": [-71.488000, -32.793000, 15]
    }
]

all_nodes = base_nodes + sinca_nodes + industry_nodes + health_nodes + education_nodes + hub_nodes

features = []
for n in all_nodes:
    features.append({
        "type": "Feature",
        "properties": {
            "id": n["id"],
            "name": n["name"],
            "category": n["category"],
            "type": n["type"],
            "role": n["role"],
            "icon": n["icon"],
            "color": n["color"],
            "priority": n.get("priority", 1),
            "elevation_msnm": n["coords"][2],
            "pollutants": n.get("pollutants", [])
        },
        "geometry": {
            "type": "Point",
            "coordinates": n["coords"]
        }
    })

geojson_obj = {
    "type": "FeatureCollection",
    "name": "Red_Quintero_Puchuncavi_Sin_SafeLanding",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": features
}

output_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_obj, f, indent=2, ensure_ascii=False)

print(f"Total nodos generados: {len(features)}")
print(f"  - Base: {len(base_nodes)}")
print(f"  - SINCA: {len(sinca_nodes)}")
print(f"  - Industrias: {len(industry_nodes)}")
print(f"  - Salud (Hospitales/CESFAM/Postas): {len(health_nodes)}")
print(f"  - Educación (Colegios/Liceos/Jardines): {len(education_nodes)}")
print(f"  - Hubs de Recarga: {len(hub_nodes)}")
print(f"Archivo guardado exitosamente en: {output_path}")
