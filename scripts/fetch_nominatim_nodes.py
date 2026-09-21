import urllib.request
import urllib.parse
import json
import time

queries = [
    # --- NIVEL 1: Fuentes de Emisión / Zonas Industriales ---
    {"query": "Codelco Ventanas", "category": "emission_source", "role": "Fundición Codelco Ventanas (Alta Emisión SO2/MP)"},
    {"query": "AES Andes Ventanas", "category": "emission_source", "role": "Complejo Termoeléctrico Ventanas"},
    {"query": "GNL Quintero", "category": "emission_source", "role": "Terminal Marítimo y Regasificadora GNL"},
    {"query": "ENAP Quintero", "category": "emission_source", "role": "Terminal y Almacenamiento de Combustibles ENAP"},
    {"query": "Oxiquim Quintero", "category": "emission_source", "role": "Planta Química y Terminal de Graneles Líquidos"},
    {"query": "Puerto Ventanas", "category": "emission_source", "role": "Terminal Portuario Industrial Ventanas"},

    # --- NIVEL 2: Receptores Sensibles (Salud, Educación, Densidad) ---
    {"query": "Hospital Adriana Cousiño Quintero", "category": "sensitive_receptor", "role": "Hospital Base Comunal"},
    {"query": "CESFAM Quintero", "category": "sensitive_receptor", "role": "Centro de Salud Familiar Quintero"},
    {"query": "CESFAM Las Ventanas Puchuncaví", "category": "sensitive_receptor", "role": "Centro de Salud Familiar Ventanas"},
    {"query": "Posta de Salud Rural Puchuncaví", "category": "sensitive_receptor", "role": "Centro de Salud Rural Puchuncaví"},
    {"query": "Escuela La Greda Puchuncaví", "category": "sensitive_receptor", "role": "Escuela Básica La Greda (Zona Crítica)"},
    {"query": "Colegio Chocota Puchuncaví", "category": "sensitive_receptor", "role": "Colegio Básico Chocota"},
    {"query": "Liceo Politécnico Quintero", "category": "sensitive_receptor", "role": "Liceo Politécnico Quintero"},
    {"query": "Colegio General Velásquez Puchuncaví", "category": "sensitive_receptor", "role": "Complejo Educacional Puchuncaví"},
    {"query": "Plaza de Armas Quintero", "category": "sensitive_receptor", "role": "Centro Urbano y Comercial Quintero"},

    # --- NIVEL 3: Aterrizaje de Emergencia / Safe Ditching (Despoblado) ---
    {"query": "Dunas de Ritoque Quintero", "category": "safe_landing", "role": "Zona Dunar Despoblada (Safe Ditching Sur)"},
    {"query": "Playa de Ritoque", "category": "safe_landing", "role": "Franja Costera Desierta (Safe Landing)"},
    {"query": "Playa Campiche", "category": "safe_landing", "role": "Playa y Zona Descampada Norte"},
    {"query": "Estadio Municipal de Puchuncaví", "category": "safe_landing", "role": "Espacio Abierto Despejado / Hub de Respaldo"}
]

results = []
print(f"Iniciando búsqueda en OpenStreetMap Nominatim para {len(queries)} puntos clave...")

for item in queries:
    q = item["query"]
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&limit=1&countrycodes=cl"
    req = urllib.request.Request(url, headers={'User-Agent': 'UAV-Resilience-Academic-Research/1.0 (benjamin@uav.cl)'})
    
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                res = data[0]
                lat = float(res['lat'])
                lon = float(res['lon'])
                results.append({
                    "id": item["query"].lower().replace(" ", "_"),
                    "name": item["query"],
                    "category": item["category"],
                    "role": item["role"],
                    "coords": [round(lon, 6), round(lat, 6)],
                    "display_name": res.get('display_name', '')
                })
                print(f"[OK] {item['query']} -> [{lat:.5f}, {lon:.5f}]")
            else:
                print(f"[SIN RESULTADO DIRECTO] {item['query']}")
    except Exception as e:
        print(f"[ERROR] {item['query']}: {e}")
    
    time.sleep(1) # Respetar política de uso de Nominatim (1 req/seg)

output_file = r'c:\Users\Benjamin\Desktop\ruteo_redes\scripts\nominatim_nodes.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nProceso finalizado. {len(results)} nodos obtenidos guardados en {output_file}")
