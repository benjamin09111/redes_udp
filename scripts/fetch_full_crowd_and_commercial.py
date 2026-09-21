import urllib.request
import urllib.parse
import json
import time

# Lista exhaustiva de consultas puntuales en Nominatim para centros de alta concurrencia
# en Quintero, Puchuncaví, Ventanas, Loncura y Horcón
crowd_and_commerce_targets = [
    # --- 1. CENTROS COMERCIALES Y SUPERMERCADOS ---
    {"name": "Supermercado Santa Isabel Quintero", "q": "Santa Isabel Quintero", "cat": "commercial", "role": "Supermercado de Alta Afluencia: Santa Isabel", "icon": "🛒"},
    {"name": "Supermercado Unimarc Quintero Centro", "q": "Unimarc Quintero", "cat": "commercial", "role": "Supermercado Principal: Unimarc Quintero", "icon": "🛒"},
    {"name": "Super Bodega Acuenta Quintero", "q": "Super Bodega Acuenta Quintero", "cat": "commercial", "role": "Supermercado Mayorista / Retail: Acuenta", "icon": "🛒"},
    {"name": "Supermercado Unimarc Puchuncaví", "q": "Unimarc Puchuncaví", "cat": "commercial", "role": "Supermercado Comunal: Unimarc Puchuncaví", "icon": "🛒"},
    {"name": "Feria Libre y Mercado Municipal Quintero", "q": "Mercado Municipal Quintero", "cat": "commercial", "role": "Mercado y Abasto de Alta Concurrencia", "icon": "🏪"},
    {"name": "Centro Comercial Paseo El Rincón Quintero", "q": "Paseo Normandie Quintero", "cat": "commercial", "role": "Galería y Paseo Comercial Céntrico", "icon": "🛍"},

    # --- 2. LUGARES DE GRAN CONCURRENCIA Y AGLOMERACIÓN (SORA / GRC) ---
    {"name": "Plaza de Armas Ignacio Carrera Pinto (Quintero)", "q": "Plaza de Armas Quintero", "cat": "crowded_area", "role": "Plaza Principal / Núcleo Cívico de Quintero", "icon": "👥"},
    {"name": "Plaza de Armas de Puchuncaví", "q": "Plaza de Armas Puchuncaví", "cat": "crowded_area", "role": "Plaza Mayor / Núcleo Comunal Puchuncaví", "icon": "👥"},
    {"name": "Plaza Central Las Ventanas", "q": "Plaza Las Ventanas Puchuncaví", "cat": "crowded_area", "role": "Espacio Público Céntrico Las Ventanas", "icon": "👥"},
    {"name": "Plaza Central Caleta Horcón", "q": "Plaza Horcón Puchuncaví", "cat": "crowded_area", "role": "Punto de Encuentro y Concurrencia Turística Horcón", "icon": "👥"},
    {"name": "Terminal de Buses Rodoviario Quintero", "q": "Terminal de Buses Quintero", "cat": "crowded_area", "role": "Hub de Transporte Interurbano y Alta Concurrencia", "icon": "🚌"},
    {"name": "Terminal / Garita de Buses Puchuncaví", "q": "Buses Puchuncaví", "cat": "crowded_area", "role": "Paradero y Terminal de Pasajeros Puchuncaví", "icon": "🚌"},
    {"name": "Estadio Municipal Raúl Vargas Verdejo (Quintero)", "q": "Estadio Municipal Quintero", "cat": "crowded_area", "role": "Estadio Deportivo y Eventos Masivos Quintero", "icon": "🏟"},
    {"name": "Gimnasio Municipal de Quintero", "q": "Gimnasio Municipal Quintero", "cat": "crowded_area", "role": "Complejo Polideportivo Techado", "icon": "🏟"},
    {"name": "Estadio Municipal de Puchuncaví", "q": "Estadio Municipal Puchuncaví", "cat": "crowded_area", "role": "Estadio Principal Comuna de Puchuncaví", "icon": "🏟"},
    {"name": "Estadio Las Ventanas", "q": "Estadio Las Ventanas", "cat": "crowded_area", "role": "Cancha y Complejo Deportivo Comunitario", "icon": "🏟"},
    {"name": "Caleta El Manzano (Quintero)", "q": "Caleta El Manzano Quintero", "cat": "crowded_area", "role": "Caleta Pesquera y Polo Turístico Gastronómico", "icon": "⚓"},
    {"name": "Caleta de Pescadores de Quintero", "q": "Caleta de Pescadores Quintero", "cat": "crowded_area", "role": "Muelle y Caleta de Pescadores Artesanales", "icon": "⚓"},
    {"name": "Caleta Las Ventanas", "q": "Caleta Las Ventanas", "cat": "crowded_area", "role": "Caleta Pesquera e Interfaz Mar-Tierra", "icon": "⚓"},
    {"name": "Caleta de Horcón", "q": "Caleta Horcón Puchuncaví", "cat": "crowded_area", "role": "Polo Artesanal y Fuerte Aglomeración Turística", "icon": "⚓"},
    {"name": "Caleta Loncura", "q": "Caleta Loncura", "cat": "crowded_area", "role": "Caleta Pesquera y Balneario Loncura", "icon": "⚓"},
    {"name": "Ilustre Municipalidad de Quintero", "q": "Municipalidad de Quintero", "cat": "crowded_area", "role": "Edificio Consistorial y Servicios Públicos", "icon": "🏛"},
    {"name": "Ilustre Municipalidad de Puchuncaví", "q": "Municipalidad de Puchuncaví", "cat": "crowded_area", "role": "Edificio Consistorial Comunal Puchuncaví", "icon": "🏛"},
    {"name": "Subcomisaría de Carabineros Quintero", "q": "Carabineros Quintero", "cat": "crowded_area", "role": "Cuartel Policial y Control de Seguridad Quintero", "icon": "👮"},
    {"name": "Tenencia de Carabineros Puchuncaví", "q": "Carabineros Puchuncaví", "cat": "crowded_area", "role": "Cuartel Policial Puchuncaví", "icon": "👮"},
    {"name": "Capitanía de Puerto de Quintero (Armada)", "q": "Capitanía de Puerto Quintero", "cat": "crowded_area", "role": "Autoridad Marítima y Control Bahía (DGTM)", "icon": "⚓"},
    {"name": "Cuerpo de Bomberos de Quintero (1ª Cía)", "q": "Bomberos Quintero", "cat": "crowded_area", "role": "Cuartel General de Bomberos y Emergencias", "icon": "🚒"},
    {"name": "Cuerpo de Bomberos Puchuncaví", "q": "Bomberos Puchuncaví", "cat": "crowded_area", "role": "Cuartel de Bomberos Comuna de Puchuncaví", "icon": "🚒"},
    {"name": "Cuerpo de Bomberos Las Ventanas", "q": "Bomberos Las Ventanas Puchuncaví", "cat": "crowded_area", "role": "Compañía de Bomberos Ventanas", "icon": "🚒"},
    {"name": "Parroquia Santa Filomena (Quintero)", "q": "Parroquia Santa Filomena Quintero", "cat": "crowded_area", "role": "Templo Principal y Centro de Culto Masivo", "icon": "⛪"},
    {"name": "Parroquia Nuestra Señora del Rosario (Puchuncaví)", "q": "Parroquia Puchuncaví", "cat": "crowded_area", "role": "Templo Parroquial Histórico Puchuncaví", "icon": "⛪"},

    # --- 3. MÁS COLEGIOS, JARDINES Y ESCUELAS RURALES ---
    {"name": "Escuela Básica Los Maitenes", "q": "Escuela Los Maitenes Puchuncaví", "cat": "education", "role": "Educación Rural: Escuela Los Maitenes (Próxima a Complejo)", "icon": "🏫"},
    {"name": "Escuela Básica La Laguna (Puchuncaví)", "q": "Escuela La Laguna Puchuncaví", "cat": "education", "role": "Educación Rural: Escuela La Laguna", "icon": "🏫"},
    {"name": "Escuela Básica Pucalán (Puchuncaví)", "q": "Escuela Pucalán Puchuncaví", "cat": "education", "role": "Educación Rural: Escuela Pucalán", "icon": "🏫"},
    {"name": "Escuela San Antonio (Puchuncaví)", "q": "Escuela San Antonio Puchuncaví", "cat": "education", "role": "Educación Rural: Escuela San Antonio", "icon": "🏫"},
    {"name": "Jardín Infantil Rayito de Sol (Quintero)", "q": "Jardín Infantil Quintero", "cat": "education", "role": "Educación Inicial: Jardín y Sala Cuna Quintero", "icon": "🏫"},
    {"name": "Jardín Infantil Puchuncaví Centro", "q": "Jardín Infantil Puchuncaví", "cat": "education", "role": "Educación Parvularia: Red JUNJI/Integra Puchuncaví", "icon": "🏫"},
    {"name": "Centro de Educación Integrada de Adultos (CEIA Quintero)", "q": "CEIA Quintero", "cat": "education", "role": "Educación Adultos y Laboral Quintero", "icon": "🏫"},

    # --- 4. MÁS SALUD (Postas Rurales y Centros Comunitarios) ---
    {"name": "Posta de Salud Rural Los Maitenes", "q": "Posta Los Maitenes Puchuncaví", "cat": "health", "role": "Salud: Posta Rural Los Maitenes (Receptor Crítico)", "icon": "🏥"},
    {"name": "Posta de Salud Rural Campiche", "q": "Posta Campiche Puchuncaví", "cat": "health", "role": "Salud: Posta de Atención Rural Campiche", "icon": "🏥"},
    {"name": "Posta de Salud Rural La Laguna", "q": "Posta La Laguna Puchuncaví", "cat": "health", "role": "Salud: Posta de Atención Rural La Laguna", "icon": "🏥"},
    {"name": "Posta de Salud Rural Pucalán", "q": "Posta Pucalán Puchuncaví", "cat": "health", "role": "Salud: Posta de Atención Rural Pucalán", "icon": "🏥"},
    {"name": "Farmacia Municipal de Quintero", "q": "Farmacia Municipal Quintero", "cat": "health", "role": "Salud: Farmacia Popular / Punto de Asistencia", "icon": "💊"},
    {"name": "Asociación Chilena de Seguridad (ACHS Quintero)", "q": "ACHS Quintero", "cat": "health", "role": "Salud Ocupacional e Industrial: ACHS", "icon": "🏥"},
    {"name": "Instituto de Seguridad del Trabajo (IST Quintero)", "q": "IST Quintero", "cat": "health", "role": "Salud Ocupacional y Urgencias Laborales IST", "icon": "🏥"}
]

print(f"Total objetivos a consultar: {len(crowd_and_commerce_targets)}")

results = []
for idx, target in enumerate(crowd_and_commerce_targets):
    q = target["q"]
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Thesis-Crowd-Nodes/1.0 (benjamin@uav.cl)'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                item = data[0]
                lat = float(item['lat'])
                lon = float(item['lon'])
                
                # Filtrar si está dentro de la zona de estudio o cerca
                # Bounds: lat [-32.84, -32.68], lon [-71.56, -71.38]
                in_bounds = (-32.85 <= lat <= -32.65) and (-71.58 <= lon <= -71.36)
                
                res_obj = {
                    "id": f"{target['cat']}_{idx:02d}",
                    "name": target["name"],
                    "query": q,
                    "category": target["cat"],
                    "role": target["role"],
                    "icon": target["icon"],
                    "coords": [round(lon, 6), round(lat, 6)],
                    "display_name": item.get('display_name', ''),
                    "in_bounds": in_bounds
                }
                results.append(res_obj)
                status = "OK (DENTRO)" if in_bounds else "FUERA DE BOUNDS"
                print(f"[{idx+1}/{len(crowd_and_commerce_targets)}] {status}: {target['name']} -> [{lat:.5f}, {lon:.5f}]")
            else:
                print(f"[{idx+1}/{len(crowd_and_commerce_targets)}] SIN RESULTADO: {target['name']}")
    except Exception as e:
        print(f"[{idx+1}/{len(crowd_and_commerce_targets)}] ERROR: {target['name']} -> {e}")
    time.sleep(1)

out_file = r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\crowd_and_commerce_results.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nTerminado! Se encontraron {len(results)}/{len(crowd_and_commerce_targets)} elementos. Guardado en {out_file}")

