import json
import math

# =============================================================================
# 0. BASE PRINCIPAL
# =============================================================================
base_nodes = [
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
    }
]

# =============================================================================
# 1. ESTACIONES SINCA OFICIALES (9)
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
# 2. FUENTES INDUSTRIALES (7)
# =============================================================================
industry_nodes = [
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
    }
]

# =============================================================================
# 3. RED DE SALUD Y ASISTENCIA COMUNITARIA (Hospitales, CESFAM, Postas, Farmacias)
# =============================================================================
health_nodes = [
    {
        "id": "health_hosp_adriana_cousino",
        "name": "Hospital Adriana Cousiño (Quintero)",
        "category": "health",
        "type": "health",
        "role": "Salud: Hospital Base Comunal Quintero",
        "icon": "🏥",
        "color": "#ef4444",
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
        "role": "Salud: Servicio de Atención Primaria de Urgencia Ventanas",
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
    },
    {
        "id": "health_cruz_verde_quintero",
        "name": "Farmacia Cruz Verde (Quintero Centro)",
        "category": "health",
        "type": "health",
        "role": "Salud y Farmacia: Dispensario Céntrico Alta Afluencia",
        "icon": "💊",
        "color": "#ef4444",
        "priority": 3,
        "coords": [-71.527475, -32.784812, 23]
    },
    {
        "id": "health_ahumada_quintero",
        "name": "Farmacias Ahumada (Quintero)",
        "category": "health",
        "type": "health",
        "role": "Salud y Farmacia: Cadena Farmacéutica Principal",
        "icon": "💊",
        "color": "#ef4444",
        "priority": 3,
        "coords": [-71.527347, -32.785460, 23]
    },
    {
        "id": "health_dr_simi_quintero",
        "name": "Farmacia Dr. Simi (Quintero Plaza)",
        "category": "health",
        "type": "health",
        "role": "Salud y Medicamentos: Farmacia Concurrida Plaza Quintero",
        "icon": "💊",
        "color": "#ef4444",
        "priority": 3,
        "coords": [-71.527098, -32.786908, 22]
    },
    {
        "id": "health_farmacia_puchuncavi",
        "name": "Farmacia La Plaza (Puchuncaví)",
        "category": "health",
        "type": "health",
        "role": "Salud y Farmacia: Farmacia Comunal Puchuncaví Centro",
        "icon": "💊",
        "color": "#ef4444",
        "priority": 3,
        "coords": [-71.414293, -32.726414, 88]
    },
    {
        "id": "health_farmacia_horcon",
        "name": "Farmacia Macarena (Horcón)",
        "category": "health",
        "type": "health",
        "role": "Salud y Farmacia: Asistencia Farmacéutica Caleta Horcón",
        "icon": "💊",
        "color": "#ef4444",
        "priority": 3,
        "coords": [-71.489941, -32.709606, 12]
    }
]

# =============================================================================
# 4. RED DE EDUCACIÓN (Colegios, Liceos, Escuelas, Especiales, Jardines)
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
        "role": "Educación Media y Técnico-Profesional Puchuncaví",
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
        "role": "Educación Media Técnico-Profesional (Enlace Educación Superior / Industrial)",
        "icon": "🎓",
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
        "role": "Educación: Colegio Científico-Humanista Alonso de Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.531874, -32.801792, 18]
    },
    {
        "id": "edu_colegio_alonso_norte",
        "name": "Colegio Alonso de Quintero (Sede Norte)",
        "category": "education",
        "type": "education",
        "role": "Educación: Campus Escolar Norte Alonso de Quintero",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 5,
        "coords": [-71.532820, -32.775423, 26]
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
        "id": "edu_escuela_ann_sullivan",
        "name": "Centro de Educación Especial Ann Sullivan",
        "category": "education",
        "type": "education",
        "role": "Educación Diferencial: Escuela Especial Ann Sullivan",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.531626, -32.777690, 25]
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
        "id": "edu_jardin_puchuncavi",
        "name": "Jardín Infantil San Agustín (Puchuncaví)",
        "category": "education",
        "type": "education",
        "role": "Educación Parvularia: Red JUNJI/Integra Puchuncaví",
        "icon": "🏫",
        "color": "#f97316",
        "priority": 4,
        "coords": [-71.408448, -32.729387, 86]
    }
]

# =============================================================================
# 5. COMERCIO, SUPERMERCADOS Y MERCADOS DE ABASTO (10)
# =============================================================================
commercial_nodes = [
    {
        "id": "comm_unimarc_quintero_centro",
        "name": "Supermercado Unimarc Quintero Centro",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio de Abasto Mayor: Unimarc Estrella de Chile",
        "icon": "🛒",
        "color": "#eab308", # Amber / Yellow
        "priority": 4,
        "coords": [-71.527081, -32.785623, 23]
    },
    {
        "id": "comm_unimarc_normandie",
        "name": "Supermercado Unimarc Normandie (Quintero)",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio de Abasto Mayor: Unimarc Av. Normandie",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.527169, -32.792341, 21]
    },
    {
        "id": "comm_acuenta_quintero",
        "name": "Super Bodega Acuenta (Quintero Sur)",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio Mayorista / Retail Popular Quintero",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.526812, -32.798536, 18]
    },
    {
        "id": "comm_unimarc_puchuncavi",
        "name": "Supermercado Unimarc Puchuncaví",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio de Abasto Principal Comuna de Puchuncaví",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.410148, -32.721627, 88]
    },
    {
        "id": "comm_el_descanso_loncura",
        "name": "Supermercado El Descanso (Loncura)",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio y Abastecimiento Balneario de Loncura",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 3,
        "coords": [-71.502803, -32.789344, 15]
    },
    {
        "id": "comm_el_carolo_horcon",
        "name": "Supermercado El Carolo (Horcón)",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio de Abastecimiento Caleta Horcón",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 3,
        "coords": [-71.488973, -32.710683, 14]
    },
    {
        "id": "comm_sdtodo_quintero",
        "name": "Supermercado S´DTodo (Quintero)",
        "category": "commercial",
        "type": "commercial",
        "role": "Comercio Local y Autoservicio Quintero Centro",
        "icon": "🛒",
        "color": "#eab308",
        "priority": 3,
        "coords": [-71.528224, -32.786825, 23]
    },
    {
        "id": "comm_feria_quintero",
        "name": "Feria Libre y Mercado de Abastos Quintero",
        "category": "commercial",
        "type": "commercial",
        "role": "Mercado Abierto y Feria de Gran Concurrencia Matutina",
        "icon": "🏪",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.526510, -32.782590, 24]
    },
    {
        "id": "comm_caleta_mercado_quintero",
        "name": "Mercado y Caleta Pesquera de Quintero",
        "category": "commercial",
        "type": "commercial",
        "role": "Mercado del Mar, Faena Pesquera y Polo Gastronómico",
        "icon": "🐟",
        "color": "#eab308",
        "priority": 4,
        "coords": [-71.527006, -32.782067, 5]
    },
    {
        "id": "comm_caleta_mercado_loncura",
        "name": "Mercado Pesquero Caleta Loncura",
        "category": "commercial",
        "type": "commercial",
        "role": "Mercado Local de Productos del Mar y Gastronomía",
        "icon": "🐟",
        "color": "#eab308",
        "priority": 3,
        "coords": [-71.507865, -32.782724, 6]
    }
]

# =============================================================================
# 6. LUGARES DE GRAN CONCURRENCIA / AGLOMERACIÓN POBLACIONAL (SORA / GRC) (28)
# =============================================================================
crowded_nodes = [
    # Plazas y Espacios Cívicos Centrales
    {
        "id": "crowd_plaza_quintero",
        "name": "Plaza Ignacio Carrera Pinto (Plaza de Armas Quintero)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Núcleo Cívico Principal y Zona de Alta Densidad Peatonal",
        "icon": "👥",
        "color": "#ec4899", # Pink
        "priority": 5,
        "coords": [-71.528399, -32.783928, 23]
    },
    {
        "id": "crowd_plaza_puchuncavi",
        "name": "Plaza de Armas de Puchuncaví",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Plaza Mayor y Núcleo Cívico Comunal de Puchuncaví",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 5,
        "coords": [-71.415106, -32.725987, 88]
    },
    {
        "id": "crowd_plaza_ventanas",
        "name": "Plaza Central Las Ventanas (Plaza Vadinho)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Espacio Público Central y Concurrencia Las Ventanas",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.475878, -32.743039, 14]
    },
    {
        "id": "crowd_plaza_horcon",
        "name": "Plaza Los Pescadores (Caleta Horcón)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Polo Turístico, Feria Artesanal y Fuerte Concurrencia",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.489833, -32.712876, 12]
    },
    {
        "id": "crowd_plaza_loncura",
        "name": "Plaza Central de Loncura",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Punto de Reunión Comunitaria Balneario Loncura",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.502290, -32.787705, 15]
    },
    {
        "id": "crowd_plaza_fuerza_aerea",
        "name": "Plaza Fuerza Aérea (Quintero)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Espacio Cívico Costero Quintero",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.526616, -32.782856, 22]
    },
    {
        "id": "crowd_plaza_bicentenario",
        "name": "Plaza Bicentenario (Quintero Sur)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Área Verde y Recreacional Residencial Quintero Sur",
        "icon": "👥",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.527290, -32.797636, 18]
    },
    {
        "id": "crowd_parque_cousino",
        "name": "Parque Municipal Luisa Sebiré de Cousiño",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Gran Parque Comunal, Mirador y Eventos Masivos",
        "icon": "🌳",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.530448, -32.770174, 30]
    },

    # Terminales de Pasajeros y Movilidad Masiva
    {
        "id": "crowd_terminal_buses_quintero",
        "name": "Terminal de Buses Rodoviario de Quintero",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Hub de Transporte Interurbano Sol del Pacífico / Cóndor Bus",
        "icon": "🚌",
        "color": "#ec4899",
        "priority": 5,
        "coords": [-71.526876, -32.777165, 24]
    },
    {
        "id": "crowd_terminal_buses_sur",
        "name": "Terminal de Buses Quintero Sur",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Estación de Buses Interurbanos Acceso Sur Quintero",
        "icon": "🚌",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.527818, -32.797389, 18]
    },

    # Estadios y Centros Deportivos de Gran Convocatoria
    {
        "id": "crowd_estadio_quintero",
        "name": "Estadio Municipal Raúl Vargas Verdejo (Quintero)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Complejo Deportivo y Eventos Masivos de Quintero",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.529555, -32.799484, 18]
    },
    {
        "id": "crowd_gimnasio_quintero",
        "name": "Gimnasio Municipal Techado de Quintero",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Polideportivo Techado y Asambleas Ciudadanas",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.528430, -32.785570, 23]
    },
    {
        "id": "crowd_estadio_puchuncavi",
        "name": "Estadio Municipal de Puchuncaví",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Recinto Deportivo Principal de Puchuncaví",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.403188, -32.719721, 85]
    },
    {
        "id": "crowd_estadio_ventanas",
        "name": "Estadio Las Ventanas",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Cancha Deportiva Comunitaria Las Ventanas",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.474350, -32.747280, 22]
    },
    {
        "id": "crowd_medialuna_puchuncavi",
        "name": "Medialuna de Puchuncaví",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Recinto Tradicional de Fiestas Costumbristas y Alta Concurrencia",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.412200, -32.727401, 86]
    },
    {
        "id": "crowd_club_valle_alegre",
        "name": "Club Deportivo Valle Alegre",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Cancha y Espacio Deportivo Rural Valle Alegre",
        "icon": "🏟",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.434059, -32.808799, 65]
    },

    # Edificios Consistoriales, Seguridad y Justicia
    {
        "id": "crowd_muni_quintero",
        "name": "Ilustre Municipalidad de Quintero",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Edificio Consistorial y Servicios Públicos Comunales",
        "icon": "🏛",
        "color": "#ec4899",
        "priority": 5,
        "coords": [-71.527692, -32.785385, 23]
    },
    {
        "id": "crowd_muni_puchuncavi",
        "name": "Ilustre Municipalidad de Puchuncaví",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Edificio Consistorial Comuna de Puchuncaví",
        "icon": "🏛",
        "color": "#ec4899",
        "priority": 5,
        "coords": [-71.416110, -32.725423, 88]
    },
    {
        "id": "crowd_subcomisaria_quintero",
        "name": "Subcomisaría de Carabineros Quintero",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Cuartel Policial y Control Operativo de Emergencias",
        "icon": "👮",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.528055, -32.787698, 22]
    },
    {
        "id": "crowd_tenencia_puchuncavi",
        "name": "Tenencia de Carabineros Puchuncaví",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Cuartel Policial Comunal Puchuncaví",
        "icon": "👮",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.408431, -32.718983, 86]
    },
    {
        "id": "crowd_reten_ventanas",
        "name": "Retén de Carabineros Las Ventanas",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Unidad Policial Sector Las Ventanas",
        "icon": "👮",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.486238, -32.743767, 14]
    },
    {
        "id": "crowd_reten_horcon",
        "name": "Retén de Carabineros Horcón",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Unidad Policial Caleta Horcón",
        "icon": "👮",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.486523, -32.715967, 16]
    },
    {
        "id": "crowd_capitania_puerto",
        "name": "Capitanía de Puerto de Quintero (Directemar)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Autoridad Marítima, Control Tráfico Marítimo y Seguridad Costera",
        "icon": "⚓",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.526590, -32.776470, 8]
    },
    {
        "id": "crowd_bomberos_quintero",
        "name": "Cuerpo de Bomberos de Quintero (1ª Compañía)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Cuartel Central de Bomberos y Respuesta Rápida a Emergencias",
        "icon": "🚒",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.527570, -32.786240, 22]
    },
    {
        "id": "crowd_juzgado_quintero",
        "name": "Juzgado de Letras y Garantía de Quintero",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Tribunal de Justicia y Fiscalía Quintero",
        "icon": "⚖",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.528229, -32.786524, 23]
    },

    # Caletas y Polos de Actividad Marina
    {
        "id": "crowd_caleta_ventanas",
        "name": "Caleta de Pescadores Las Ventanas",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Caleta Pesquera, Embarcadero y Afluencia de Pescadores",
        "icon": "⚓",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.491040, -32.742980, 5]
    },
    {
        "id": "crowd_caleta_horcon",
        "name": "Caleta de Horcón (Muelle y Borde Costero)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Borde Costero Histórico, Polo Turístico y Gastronómico",
        "icon": "⚓",
        "color": "#ec4899",
        "priority": 5,
        "coords": [-71.489710, -32.708760, 6]
    },

    # Templos y Centros de Culto Masivo
    {
        "id": "crowd_parroquia_filomena",
        "name": "Parroquia Santa Filomena (Quintero)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Templo Principal y Centro de Culto Masivo Quintero",
        "icon": "⛪",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.527985, -32.781513, 24]
    },
    {
        "id": "crowd_parroquia_puchuncavi",
        "name": "Parroquia Nuestra Señora del Rosario (Puchuncaví)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Templo Parroquial Histórico Comuna de Puchuncaví",
        "icon": "⛪",
        "color": "#ec4899",
        "priority": 4,
        "coords": [-71.415108, -32.726716, 88]
    },
    {
        "id": "crowd_capilla_santa_ana",
        "name": "Capilla de Santa Ana (Horcón)",
        "category": "crowded_area",
        "type": "crowd",
        "role": "Templo Comunitario y Centro de Festividades Patronales",
        "icon": "⛪",
        "color": "#ec4899",
        "priority": 3,
        "coords": [-71.490090, -32.709740, 10]
    }
]

# =============================================================================
# 7. HUBS AUXILIARES DE RECARGA (2)
# =============================================================================
hub_nodes = [
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

all_nodes = (
    base_nodes +
    sinca_nodes +
    industry_nodes +
    health_nodes +
    education_nodes +
    commercial_nodes +
    crowded_nodes +
    hub_nodes
)

features = []
seen_ids = set()
for n in all_nodes:
    node_id = n["id"]
    if node_id in seen_ids:
        print(f"Advertencia: ID duplicado omitido: {node_id}")
        continue
    seen_ids.add(node_id)
    
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
    "name": "Red_Resiliente_Quintero_Puchuncavi_MultiCapa",
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

print("\n==================================================")
print("REPORTE DE GENERACION DE RED ESPACIAL GEOJSON")
print("==================================================")
print(f"Total nodos integrados y validados: {len(features)}")
print(f"  - Base Despacho (SCER):             {len(base_nodes)}")
print(f"  - Estaciones SINCA:                 {len(sinca_nodes)}")
print(f"  - Fuentes Industriales (Emision):   {len(industry_nodes)}")
print(f"  - Red de Salud y Farmacias:         {len(health_nodes)}")
print(f"  - Red de Educacion:                 {len(education_nodes)}")
print(f"  - Comercio y Supermercados:         {len(commercial_nodes)}")
print(f"  - Concurrencia Masiva / Civico:     {len(crowded_nodes)}")
print(f"  - Hubs Auxiliares de Recarga:       {len(hub_nodes)}")
print("==================================================")
print(f"Archivo guardado exitosamente en:\n  {output_path}")

