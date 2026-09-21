import json
import math

# 1. Cargar nodos existentes
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson', 'r', encoding='utf-8') as f:
    master_geojson = json.load(f)

existing_features = master_geojson['features']
print(f"Nodos base actuales: {len(existing_features)}")

# 2. Cargar nodos industriales compilados
with open(r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\compiled_industrial_nodes.json', 'r', encoding='utf-8') as f:
    industrial_nodes = json.load(f)

# 3. Nodos específicos para las 5 nuevas localidades solicitadas por el usuario
new_locality_nodes = [
    # --- EL RUNGUE ---
    {
        "id": "civic_rungue_centro",
        "name": "Localidad y Centro de El Rungue",
        "category": "crowded_area",
        "type": "civic",
        "role": "Poblado Rural y Concurrencia Central El Rungue",
        "icon": "👥",
        "color": "#6366f1",
        "priority": 4,
        "city": "El Rungue",
        "coords": [-71.406327, -32.696091, 75]
    },
    {
        "id": "edu_escuela_el_rungue",
        "name": "Escuela Básica El Rungue",
        "category": "education",
        "type": "school",
        "role": "Establecimiento Educacional Rural El Rungue - Zona de Protección SORA",
        "icon": "🏫",
        "color": "#3b82f6",
        "priority": 5,
        "city": "El Rungue",
        "coords": [-71.406807, -32.697141, 78]
    },
    {
        "id": "rest_caballito_de_palo_rungue",
        "name": "Restaurante El Caballito de Palo",
        "category": "restaurant",
        "type": "restaurant",
        "role": "Gastronomía Tradicional y Concurrencia de Visitantes El Rungue",
        "icon": "🍽",
        "color": "#f59e0b",
        "priority": 3,
        "city": "El Rungue",
        "coords": [-71.406087, -32.696191, 75]
    },
    {
        "id": "comm_minimarket_tio_miky_rungue",
        "name": "Minimarket Tío Miky",
        "category": "commercial",
        "type": "shop",
        "role": "Abastecimiento y Comercio Local El Rungue",
        "icon": "🛒",
        "color": "#10b981",
        "priority": 3,
        "city": "El Rungue",
        "coords": [-71.406318, -32.695817, 75]
    },
    {
        "id": "comm_comercio_san_esteban_rungue",
        "name": "Comercio y Provisiones San Esteban",
        "category": "commercial",
        "type": "shop",
        "role": "Comercio Minorista El Rungue",
        "icon": "🛒",
        "color": "#10b981",
        "priority": 3,
        "city": "El Rungue",
        "coords": [-71.405999, -32.696404, 76]
    },
    {
        "id": "hosp_cabanas_victoria_rungue",
        "name": "Cabañas Victoria (El Rungue)",
        "category": "hospitality",
        "type": "hospitality",
        "role": "Alojamiento Turístico Rural y Descanso El Rungue",
        "icon": "🏨",
        "color": "#8b5cf6",
        "priority": 3,
        "city": "El Rungue",
        "coords": [-71.406844, -32.693110, 72]
    },
    {
        "id": "sport_cancha_el_rungue",
        "name": "Cancha y Complejo Deportivo El Rungue",
        "category": "crowded_area",
        "type": "sports",
        "role": "Recinto Deportivo y Encuentro Comunitario El Rungue",
        "icon": "⚽",
        "color": "#6366f1",
        "priority": 4,
        "city": "El Rungue",
        "coords": [-71.407185, -32.697180, 80]
    },

    # --- EL RINCÓN ---
    {
        "id": "civic_el_rincon_centro",
        "name": "Localidad y Centro Comunitario El Rincón",
        "category": "crowded_area",
        "type": "civic",
        "role": "Poblado Rural El Rincón y Sector Residencial",
        "icon": "👥",
        "color": "#e11d48",
        "priority": 4,
        "city": "El Rincón",
        "coords": [-71.369826, -32.724445, 120]
    },
    {
        "id": "edu_escuela_el_rincon",
        "name": "Escuela El Rincón",
        "category": "education",
        "type": "school",
        "role": "Establecimiento Educacional Rural El Rincón - Zona Sensible DGAC",
        "icon": "🏫",
        "color": "#3b82f6",
        "priority": 5,
        "city": "El Rincón",
        "coords": [-71.368697, -32.724875, 122]
    },
    {
        "id": "leisure_plaza_el_rincon",
        "name": "Plaza y Parque Recreativo El Rincón",
        "category": "crowded_area",
        "type": "park",
        "role": "Espacio Público Verde y Juegos El Rincón",
        "icon": "🌳",
        "color": "#e11d48",
        "priority": 4,
        "city": "El Rincón",
        "coords": [-71.369422, -32.724238, 120]
    },
    {
        "id": "sport_cancha_el_rincon",
        "name": "Cancha de Fútbol El Rincón",
        "category": "crowded_area",
        "type": "sports",
        "role": "Campo Deportivo y Concurrencia de Fin de Semana El Rincón",
        "icon": "⚽",
        "color": "#e11d48",
        "priority": 4,
        "city": "El Rincón",
        "coords": [-71.368945, -32.723989, 121]
    },
    {
        "id": "civic_el_rincon_poniente",
        "name": "Sector El Rincón Poniente",
        "category": "crowded_area",
        "type": "civic",
        "role": "Poblado Rural y Conexión Agrícola Poniente",
        "icon": "👥",
        "color": "#e11d48",
        "priority": 3,
        "city": "El Rincón",
        "coords": [-71.391306, -32.724888, 105]
    },

    # --- COMUNIDAD LA ESTANCILLA ---
    {
        "id": "civic_la_estancilla_centro",
        "name": "Comunidad La Estancilla",
        "category": "crowded_area",
        "type": "civic",
        "role": "Asentamiento Rural Tradicional Comunidad La Estancilla",
        "icon": "👥",
        "color": "#f97316",
        "priority": 4,
        "city": "Comunidad La Estancilla",
        "coords": [-71.389997, -32.743157, 135]
    },
    {
        "id": "civic_sede_la_estancilla",
        "name": "Sede Social y Junta Vecinal La Estancilla",
        "category": "crowded_area",
        "type": "civic",
        "role": "Centro de Encuentro Comunitario Rural La Estancilla",
        "icon": "🏛",
        "color": "#f97316",
        "priority": 4,
        "city": "Comunidad La Estancilla",
        "coords": [-71.389200, -32.744100, 136]
    },

    # --- LOS TOMES ---
    {
        "id": "civic_los_tomes_centro",
        "name": "Localidad Rural Los Tomes",
        "category": "crowded_area",
        "type": "civic",
        "role": "Sector Rural Residencial y Turístico Los Tomes",
        "icon": "👥",
        "color": "#84cc16",
        "priority": 4,
        "city": "Los Tomes",
        "coords": [-71.450000, -32.716700, 48]
    },
    {
        "id": "hosp_cabanas_los_tomes",
        "name": "Complejo Turístico y Cabañas Los Tomes",
        "category": "hospitality",
        "type": "hospitality",
        "role": "Alojamiento Turístico Campestre y Recreacional",
        "icon": "🏨",
        "color": "#84cc16",
        "priority": 3,
        "city": "Los Tomes",
        "coords": [-71.448451, -32.719319, 45]
    },
    {
        "id": "attr_estero_los_tomes",
        "name": "Paseo y Ribera Estero Los Tomes",
        "category": "attraction",
        "type": "nature",
        "role": "Corredor Ecológico y Natural Estero Los Tomes",
        "icon": "🌿",
        "color": "#84cc16",
        "priority": 3,
        "city": "Los Tomes",
        "coords": [-71.449224, -32.719885, 42]
    },

    # --- EL ALTO (PUCHUNCAVÍ) ---
    {
        "id": "civic_el_alto_puchuncavi",
        "name": "Sector Rural El Alto (Puchuncaví)",
        "category": "crowded_area",
        "type": "civic",
        "role": "Poblado Rural y Conexión Vial Interior Puchuncaví Norte",
        "icon": "👥",
        "color": "#14b8a6",
        "priority": 4,
        "city": "El Alto",
        "coords": [-71.430630, -32.715738, 70]
    },
    {
        "id": "attr_ecoturismo_vivo_el_alto",
        "name": "Centro Ecoturismo Vivo (El Alto)",
        "category": "attraction",
        "type": "tourism",
        "role": "Actividades de Ecoturismo, Senderismo y Recreación al Aire Libre",
        "icon": "🏕",
        "color": "#14b8a6",
        "priority": 3,
        "city": "El Alto",
        "coords": [-71.429188, -32.711223, 72]
    },
    {
        "id": "sport_cancha_el_alto",
        "name": "Cancha Deportiva El Alto",
        "category": "crowded_area",
        "type": "sports",
        "role": "Recinto Deportivo Comunitario El Alto",
        "icon": "⚽",
        "color": "#14b8a6",
        "priority": 3,
        "city": "El Alto",
        "coords": [-71.424752, -32.705568, 80]
    },
    {
        "id": "civic_las_catitas_el_alto",
        "name": "Sector Las Catitas - El Alto",
        "category": "crowded_area",
        "type": "civic",
        "role": "Asentamiento Rural y Agrario Las Catitas",
        "icon": "👥",
        "color": "#14b8a6",
        "priority": 3,
        "city": "El Alto",
        "coords": [-71.424176, -32.726895, 65]
    },

    # --- INFRAESTRUCTURA CÍVICA Y SALUD CLAVE PREVIAMENTE NO INCORPORADA ---
    {
        "id": "civic_mun_puchuncavi",
        "name": "Ilustre Municipalidad de Puchuncaví",
        "category": "crowded_area",
        "type": "civic",
        "role": "Edificio Consistorial Municipal y Centro Administrativo Comunal",
        "icon": "🏛",
        "color": "#10b981",
        "priority": 5,
        "city": "Puchuncaví Centro",
        "coords": [-71.416110, -32.725423, 85]
    },
    {
        "id": "civic_plaza_armas_puchuncavi",
        "name": "Plaza de Armas de Puchuncaví",
        "category": "crowded_area",
        "type": "park",
        "role": "Plaza Cívica Histórica y Punto de Encuentro Masivo Central",
        "icon": "🌳",
        "color": "#10b981",
        "priority": 5,
        "city": "Puchuncaví Centro",
        "coords": [-71.415007, -32.725986, 85]
    },
    {
        "id": "health_posta_loncura",
        "name": "Posta de Salud Rural Loncura",
        "category": "health",
        "type": "health",
        "role": "Atención Primaria de Urgencia y Salud Rural Loncura",
        "icon": "🏥",
        "color": "#06b6d4",
        "priority": 5,
        "city": "Loncura",
        "coords": [-71.502156, -32.789708, 12]
    },
    {
        "id": "health_cecof_loncura",
        "name": "CECOF Loncura",
        "category": "health",
        "type": "health",
        "role": "Centro Comunitario de Salud Familiar Loncura",
        "icon": "🏥",
        "color": "#06b6d4",
        "priority": 5,
        "city": "Loncura",
        "coords": [-71.503992, -32.788325, 14]
    },
    {
        "id": "civic_centro_civico_loncura",
        "name": "Centro Cívico y Junta Vecinal Loncura",
        "category": "crowded_area",
        "type": "civic",
        "role": "Sede Social y Trámites Comunitarios de Loncura",
        "icon": "🏛",
        "color": "#f59e0b",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.503490, -32.788246, 14]
    },
    {
        "id": "civic_plaza_loncura",
        "name": "Plaza de Loncura",
        "category": "crowded_area",
        "type": "park",
        "role": "Plaza Principal y Juegos Infantiles Loncura",
        "icon": "🌳",
        "color": "#f59e0b",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.502290, -32.787705, 12]
    },
    {
        "id": "civic_capilla_loncura",
        "name": "Capilla San Alberto Hurtado (Loncura)",
        "category": "crowded_area",
        "type": "worship",
        "role": "Lugar de Culto y Ceremonias Religiosas Loncura",
        "icon": "⛪",
        "color": "#f59e0b",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.504423, -32.787931, 14]
    },
    {
        "id": "attr_humedal_el_bato_loncura",
        "name": "Humedal Urbano El Bato (Loncura / El Alto)",
        "category": "attraction",
        "type": "nature",
        "role": "Santuario y Humedal Urbano Protegido por Ley 21.202",
        "icon": "🌿",
        "color": "#10b981",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.496777, -32.780982, 8]
    },
    {
        "id": "comm_super_el_descanso_loncura",
        "name": "Supermercado El Descanso Loncura",
        "category": "commercial",
        "type": "supermarket",
        "role": "Comercio de Abasto y Supermercado Loncura",
        "icon": "🛒",
        "color": "#10b981",
        "priority": 4,
        "city": "Loncura",
        "coords": [-71.502803, -32.789344, 15]
    },
    {
        "id": "civic_terminal_buses_campiche",
        "name": "Terminal y Paradero Interurbano Campiche / Puchuncaví",
        "category": "crowded_area",
        "type": "transport",
        "role": "Punto Neurálgico de Transporte de Pasajeros y Concurrencia",
        "icon": "🚌",
        "color": "#06b6d4",
        "priority": 4,
        "city": "Las Salinas / Campiche",
        "coords": [-71.451821, -32.732211, 40]
    }
]

# Función para determinar ciudad según coordenadas si está en unknown o para normalizar
def determine_city(lon, lat, current_city="unknown", category=""):
    if current_city and current_city != "unknown":
        return current_city
    
    # Industrial park
    if category == "emission_source" and (-71.488 <= lon <= -71.465) and (-32.775 <= lat <= -32.742):
        return "Cordón Industrial Ventanas"
    
    # Quintero peninsula
    if lon < -71.515 and lat < -32.765:
        return "Quintero"
    # Loncura
    if -71.515 <= lon <= -71.490 and -32.802 <= lat <= -32.778:
        return "Loncura"
    # Las Ventanas
    if -71.495 <= lon <= -71.478 and -32.756 <= lat <= -32.738:
        return "Las Ventanas"
    # La Chocota
    if -71.495 <= lon <= -71.475 and -32.738 < lat <= -32.720:
        return "La Chocota"
    # La Greda
    if -71.478 < lon <= -71.458 and -32.755 <= lat <= -32.738:
        return "La Greda"
    # Horcón
    if -71.512 <= lon <= -71.482 and -32.718 <= lat <= -32.705:
        return "Horcón"
    # Salinas / Campiche
    if -71.465 <= lon <= -71.438 and -32.748 <= lat <= -32.725:
        return "Las Salinas / Campiche"
    # Los Tomes
    if -71.462 <= lon <= -71.440 and -32.725 <= lat <= -32.708:
        return "Los Tomes"
    # El Alto (Puchuncaví)
    if -71.438 <= lon <= -71.418 and -32.722 <= lat <= -32.705:
        return "El Alto"
    # El Rungue
    if -71.418 <= lon <= -71.395 and -32.708 <= lat <= -32.685:
        return "El Rungue"
    # Comunidad La Estancilla
    if -71.402 <= lon <= -71.378 and -32.755 <= lat <= -32.735:
        return "Comunidad La Estancilla"
    # El Rincón
    if -71.395 <= lon <= -71.360 and -32.732 <= lat <= -32.715:
        return "El Rincón"
    # Puchuncaví Centro
    if -71.428 <= lon <= -71.400 and -32.738 <= lat <= -32.718:
        return "Puchuncaví Centro"
    
    # Rest of Quintero or Puchuncaví
    if lon < -71.480:
        return "Quintero"
    else:
        return "Puchuncaví"

def dist_m(p1, p2):
    R = 6371000
    phi1, phi2 = math.radians(p1[1]), math.radians(p2[1])
    dphi = math.radians(p2[1] - p1[1])
    dlam = math.radians(p2[0] - p1[0])
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

final_features = []
existing_coords = []

# Procesar nodos existentes
for feat in existing_features:
    props = feat['properties'].copy()
    coords = feat['geometry']['coordinates']
    lon, lat = coords[0], coords[1]
    z = coords[2] if len(coords) > 2 else 15
    
    props['city'] = determine_city(lon, lat, props.get('city', 'unknown'), props.get('category'))
    
    # Si es emission_source previa, verificar icono y formato
    if props.get('category') == 'emission_source':
        props['icon'] = props.get('icon') or '🏭'
        props['color'] = '#dc2626'
        props['priority'] = 5
        
    feat['properties'] = props
    final_features.append(feat)
    existing_coords.append((lon, lat))

print(f"Features tras normalización de ciudades: {len(final_features)}")

# Agregar nodos industriales
added_ind = 0
for ind in industrial_nodes:
    lon, lat, z = ind['coords']
    # Check if already exists nearby (< 35m)
    too_close = any(dist_m((lon, lat), ex) < 35 for ex in existing_coords)
    if too_close:
        # Update properties if it was an emission source
        for ex_f in final_features:
            ex_c = ex_f['geometry']['coordinates']
            if dist_m((lon, lat), (ex_c[0], ex_c[1])) < 35:
                ex_f['properties']['pollutants'] = ind.get('pollutants', 'SO2, NOx, MP')
                ex_f['properties']['city'] = ind['city']
                ex_f['properties']['category'] = 'emission_source'
                ex_f['properties']['icon'] = ind.get('icon', '🏭')
                break
        continue
    
    feat = {
        "type": "Feature",
        "properties": {
            "id": ind['id'],
            "name": ind['name'],
            "category": "emission_source",
            "type": ind['type'],
            "role": ind['role'],
            "icon": ind['icon'],
            "color": ind['color'],
            "priority": ind['priority'],
            "city": ind['city'],
            "pollutants": ind.get('pollutants', 'SO2, NOx, MP10')
        },
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon, 6), round(lat, 6), z]
        }
    }
    final_features.append(feat)
    existing_coords.append((lon, lat))
    added_ind += 1

print(f"Nuevos nodos industriales/fuentes de emisión agregados: {added_ind}")

# Agregar nodos de las nuevas localidades
added_loc = 0
for loc_n in new_locality_nodes:
    lon, lat, z = loc_n['coords']
    too_close = any(dist_m((lon, lat), ex) < 25 for ex in existing_coords)
    if too_close:
        continue
    feat = {
        "type": "Feature",
        "properties": {
            "id": loc_n['id'],
            "name": loc_n['name'],
            "category": loc_n['category'],
            "type": loc_n['type'],
            "role": loc_n['role'],
            "icon": loc_n['icon'],
            "color": loc_n['color'],
            "priority": loc_n['priority'],
            "city": loc_n['city']
        },
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon, 6), round(lat, 6), z]
        }
    }
    final_features.append(feat)
    existing_coords.append((lon, lat))
    added_loc += 1

print(f"Nuevos nodos de localidades y servicios agregados: {added_loc}")
print(f"TOTAL FINAL DE NODOS: {len(final_features)}")

# Resumen de categorías
cat_summary = {}
city_summary = {}
for f in final_features:
    c = f['properties']['category']
    ci = f['properties']['city']
    cat_summary[c] = cat_summary.get(c, 0) + 1
    city_summary[ci] = city_summary.get(ci, 0) + 1

print("\n--- RESUMEN POR CATEGORÍA ---")
for k, v in sorted(cat_summary.items(), key=lambda x: -x[1]):
    print(f"- {k}: {v}")

print("\n--- RESUMEN POR CIUDAD/LOCALIDAD ---")
for k, v in sorted(city_summary.items(), key=lambda x: -x[1]):
    print(f"- {k}: {v}")

master_geojson['features'] = final_features
master_geojson['name'] = "Red_Ciberfisica_Nodos_Resilientes_Bahia_Quintero_Full_Industrial"

out_nodes = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(out_nodes, 'w', encoding='utf-8') as f:
    json.dump(master_geojson, f, indent=2, ensure_ascii=False)

print(f"\n[ÉXITO] Archivo master de nodos actualizado en:\n  {out_nodes}")
