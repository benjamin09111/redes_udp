import json

nodes = [
    # =========================================================================
    # NIVEL 0: BASE PRINCIPAL DE DESPACHO Y RTH
    # =========================================================================
    {
        "id": "base_scer",
        "name": "Aeródromo de Quintero (SCER)",
        "category": "base",
        "type": "base",
        "role": "Base de Despacho Principal y Retorno Seguro (RTH)",
        "icon": "✈",
        "color": "#10b981", # Emerald
        "priority": 0,
        "coords": [-71.517300, -32.784200, 28]
    },

    # =========================================================================
    # NIVEL 1A: ESTACIONES OFICIALES SINCA (Calidad de Aire Terrestre)
    # =========================================================================
    {
        "id": "sinca_puchuncavi",
        "name": "Estación SINCA Puchuncaví",
        "category": "sinca",
        "type": "station",
        "role": "Monitoreo Oficial Calidad del Aire (MMA)",
        "icon": "📡",
        "color": "#0ea5e9", # Sky Blue
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
    },

    # =========================================================================
    # NIVEL 1B: FUENTES DE EMISIÓN INDUSTRIAL (Misiones 3D en Altura 50-110m)
    # =========================================================================
    {
        "id": "ind_codelco",
        "name": "Fundición Codelco Ventanas",
        "category": "emission_source",
        "type": "industry",
        "role": "Fuente Industrial: Fundición de Cobre (Emisión SO2/MP)",
        "icon": "🏭",
        "color": "#a855f7", # Purple
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
    },

    # =========================================================================
    # NIVEL 2: RECEPTORES SENSIBLES (Restricción DAN 151 / Evitar Multitudes)
    # =========================================================================
    {
        "id": "rec_hospital_quintero",
        "name": "Hospital Adriana Cousiño (Quintero)",
        "category": "sensitive_receptor",
        "type": "health",
        "role": "Receptor Sensible: Hospital Base Comunal",
        "icon": "🏥",
        "color": "#ef4444", # Red
        "priority": 5,
        "coords": [-71.531100, -32.779340, 25]
    },
    {
        "id": "rec_cesfam_quintero",
        "name": "CESFAM Quintero",
        "category": "sensitive_receptor",
        "type": "health",
        "role": "Receptor Sensible: Centro de Salud Familiar",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.534960, -32.795310, 20]
    },
    {
        "id": "rec_cesfam_ventanas",
        "name": "CESFAM Las Ventanas",
        "category": "sensitive_receptor",
        "type": "health",
        "role": "Receptor Sensible: Centro de Salud Ventanas",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.484560, -32.742330, 14]
    },
    {
        "id": "rec_cesfam_puchuncavi",
        "name": "CESFAM Puchuncaví",
        "category": "sensitive_receptor",
        "type": "health",
        "role": "Receptor Sensible: Centro de Salud Familiar Puchuncaví",
        "icon": "🏥",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.415980, -32.725770, 90]
    },
    {
        "id": "rec_escuela_la_greda",
        "name": "Escuela Básica La Greda",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible Crítico: Colegio Básico La Greda",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.460890, -32.736270, 35]
    },
    {
        "id": "rec_colegio_chocota",
        "name": "Colegio Chocota (Puchuncaví)",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible: Escuela Rural Chocota",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.487170, -32.729570, 20]
    },
    {
        "id": "rec_liceo_quintero",
        "name": "Liceo Politécnico Quintero",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible: Establecimiento Educación Media",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.527470, -32.788290, 22]
    },
    {
        "id": "rec_colegio_velasquez",
        "name": "Complejo Educacional Gral. Velásquez",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible: Liceo Principal Puchuncaví",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.417070, -32.726600, 85]
    },
    {
        "id": "rec_colegio_don_orione",
        "name": "Colegio Don Orione (Quintero)",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible: Escuela Básica y Media",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.526800, -32.781500, 22]
    },
    {
        "id": "rec_escuela_sargento_aldea",
        "name": "Escuela Sargento Aldea (Ventanas)",
        "category": "sensitive_receptor",
        "type": "education",
        "role": "Receptor Sensible: Colegio Las Ventanas",
        "icon": "🏫",
        "color": "#ef4444",
        "priority": 4,
        "coords": [-71.479500, -32.746000, 12]
    },
    {
        "id": "rec_plaza_quintero",
        "name": "Plaza Ignacio Carrera Pinto (Centro)",
        "category": "sensitive_receptor",
        "type": "urban",
        "role": "Receptor Sensible: Centro Cívico y Comercial de Quintero",
        "icon": "👥",
        "color": "#ef4444",
        "priority": 5,
        "coords": [-71.528410, -32.784020, 24]
    },

    # =========================================================================
    # NIVEL 3: ZONAS DE ATERRIZAJE DE EMERGENCIA (Safe Ditching / Sin Personas)
    # =========================================================================
    {
        "id": "safe_dunas_ritoque_sur",
        "name": "Campo Dunar de Ritoque (Sur)",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Ditching: Dunas Extensas Despobladas (Failsafe Sur)",
        "icon": "🛡",
        "color": "#eab308", # Amber / Gold
        "priority": 1,
        "coords": [-71.505190, -32.847200, 30]
    },
    {
        "id": "safe_dunas_ritoque_norte",
        "name": "Dunas de Ritoque (Acceso Norte)",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Landing: Terreno Arenoso Plano Deshabitado",
        "icon": "🛡",
        "color": "#eab308",
        "priority": 1,
        "coords": [-71.512000, -32.818000, 25]
    },
    {
        "id": "safe_playa_ventanas",
        "name": "Playa Las Ventanas (Norte)",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Ditching: Franja Costera Abierta Despejada (Failsafe Norte)",
        "icon": "🛡",
        "color": "#eab308",
        "priority": 1,
        "coords": [-71.469440, -32.710300, 2]
    },
    {
        "id": "safe_playa_loncura",
        "name": "Playa Loncura (Sector Desierto)",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Landing: Costa Despejada al Este de Loncura",
        "icon": "🛡",
        "color": "#eab308",
        "priority": 1,
        "coords": [-71.501000, -32.791500, 2]
    },
    {
        "id": "safe_estadio_puchuncavi",
        "name": "Estadio Municipal de Puchuncaví",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Landing: Cancha Abierta y Espacio Despejado",
        "icon": "🛡",
        "color": "#eab308",
        "priority": 2,
        "coords": [-71.402790, -32.719540, 92]
    },
    {
        "id": "safe_valle_alegre_rural",
        "name": "Descampado Rural Valle Alegre",
        "category": "safe_landing",
        "type": "emergency",
        "role": "Safe Ditching: Terreno Agrícola Abierto sin Estructuras",
        "icon": "🛡",
        "color": "#eab308",
        "priority": 1,
        "coords": [-71.435000, -32.775000, 60]
    },

    # =========================================================================
    # NIVEL 4: NIDOS / HUBS AUXILIARES DE RECARGA Y BATERÍAS (Drone-in-a-Box)
    # =========================================================================
    {
        "id": "hub_puchuncavi",
        "name": "Hub Auxiliar Puchuncaví (Bomberos/Estadio)",
        "category": "auxiliary_hub",
        "type": "hub",
        "role": "Nido de Recarga Auxiliar y Baterías de Reemplazo (Sector Este)",
        "icon": "🔋",
        "color": "#06b6d4", # Cyan
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

features = []
for n in nodes:
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
    "name": "Red_Completa_Bahia_Quintero_Puchuncavi",
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

print(f"GeoJSON generado exitosamente con {len(features)} nodos estratificados en: {output_path}")
