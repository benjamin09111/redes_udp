"""Motor de Ruteo Resiliente Multiobjetivo y Evaluación de Resiliencia UAV.

Fundamento metodológico:
- Algoritmo de K-caminos disimilares mediante penalización iterativa de aristas
  (Akgün, Erkut & Batta, 2000, European Journal of Operational Research 121(2): 232-246).
- Inspirado en la etapa GPP (Global Path Planner) de Kosior, Przystałka y Panfil (2024),
  "Adaptive Path Planning for UAV-Based Pollution Sampling", Applied Sciences, 14(24), 12065.
  DOI: 10.3390/app142412065.
- Confiabilidad estocástica exacta de sistemas con rutas parcialmente disyuntas:
  R = S(E_C) * [1 - (1 - S(E_1)) * (1 - S(E_2))], donde E_C es el conjunto de aristas comunes.

Exporta a:
    sitio_web/data/rutas_comparativas.geojson
    sitio_web/data/resumen_resiliencia.json
"""

import heapq
import json
import math
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN_BASE = "base_scer"  # Aeródromo de Quintero (SCER)

# Escenario de contingencia industrial: Foco en Planta Asfaltos Quintero
# Se modela un incendio en las instalaciones industriales (radio de afección térmica de 180 m).
# Radios superiores a 450 m bloquean por completo el istmo hacia el norte, evidenciando un cuello
# de botella estructural y conjunto de corte topológico de la red de Quintero a Puchuncaví.
FOCO_ESTRES = {
    "lon": -71.4935,
    "lat": -32.7801,
    "radio_m": 180.0,
    "descripcion": "Foco de contingencia: Incendio industrial en Planta Asfaltos Quintero"
}

# ==============================================================================
# 1. UTILIDADES GEOMÉTRICAS Y ESPACIALES
# ==============================================================================

def bbox_poligono(anillo):
    xs = [p[0] for p in anillo]
    ys = [p[1] for p in anillo]
    return [min(xs), min(ys), max(xs), max(ys)]


def punto_en_poligono(x, y, anillo, bbox=None):
    if bbox:
        min_x, min_y, max_x, max_y = bbox
        if x < min_x or x > max_x or y < min_y or y > max_y:
            return False

    n = len(anillo)
    adentro = False
    p1x, p1y = anillo[0]
    for i in range(1, n + 1):
        p2x, p2y = anillo[i % n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                adentro = not adentro
        p1x, p1y = p2x, p2y
    return adentro


def dist_metros(p1, p2):
    lat_mid = (p1[1] + p2[1]) / 2.0 * math.pi / 180.0
    dx = (p2[0] - p1[0]) * math.cos(lat_mid) * 111320.0
    dy = (p2[1] - p1[1]) * 110540.0
    return math.hypot(dx, dy)


def dist_punto_a_segmento_m(p1, p2, p):
    lat_rad = p[1] * math.pi / 180.0
    x1, y1 = p1[0] * math.cos(lat_rad) * 111320.0, p1[1] * 110540.0
    x2, y2 = p2[0] * math.cos(lat_rad) * 111320.0, p2[1] * 110540.0
    px, py = p[0] * math.cos(lat_rad) * 111320.0, p[1] * 110540.0

    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / L2))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def arista_interseca_poligonos(coord_u, coord_v, features_poligonos, num_muestras=5):
    if not features_poligonos:
        return False, None
    for i in range(num_muestras):
        t = i / float(num_muestras - 1)
        mx = coord_u[0] + t * (coord_v[0] - coord_u[0])
        my = coord_u[1] + t * (coord_v[1] - coord_u[1])
        for f in features_poligonos:
            geom = f["geometry"]
            bbox = f.get("_bbox")
            if geom["type"] == "Polygon":
                if punto_en_poligono(mx, my, geom["coordinates"][0], bbox):
                    return True, f["properties"]
            elif geom["type"] == "MultiPolygon":
                for poly in geom["coordinates"]:
                    if punto_en_poligono(mx, my, poly[0], bbox):
                        return True, f["properties"]
    return False, None


# ==============================================================================
# 2. CARGA DE CAPAS GEOESPACIALES
# ==============================================================================

def cargar_capas():
    def leer_gj(rel_path):
        p = RAIZ / rel_path
        if not p.exists():
            return {"type": "FeatureCollection", "features": []}
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    nodos = leer_gj("infraestructura/nodos.geojson")
    aristas = leer_gj("infraestructura/aristas.geojson")
    manzanas = leer_gj("metadata/ine_manzanas.geojson")
    antenas = leer_gj("metadata/osm_antenas.geojson")
    incendios = leer_gj("amenazas/firms_incendios.geojson")
    sismos = leer_gj("amenazas/csn_sismos.geojson")
    viento = leer_gj("amenazas/openmeteo_viento.geojson")
    lluvia = leer_gj("amenazas/metno_lluvia.geojson")

    manzanas_densas = []
    for f in manzanas["features"]:
        densidad = f["properties"].get("density_hab_km2", 0)
        if densidad > 2500:
            anillo = f["geometry"]["coordinates"][0] if f["geometry"]["type"] == "Polygon" else f["geometry"]["coordinates"][0][0]
            f["_bbox"] = bbox_poligono(anillo)
            manzanas_densas.append(f)

    antenas_activas = []
    for f in antenas["features"]:
        geom = f["geometry"]
        anillo = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
        f["_bbox"] = bbox_poligono(anillo)
        antenas_activas.append(f)

    incendios_activos = []
    for f in incendios["features"]:
        if f["properties"].get("exceeds"):
            geom = f["geometry"]
            anillo = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
            f["_bbox"] = bbox_poligono(anillo)
            incendios_activos.append(f)

    sismos_activos = []
    for f in sismos["features"]:
        if f["properties"].get("exceeds"):
            geom = f["geometry"]
            anillo = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
            f["_bbox"] = bbox_poligono(anillo)
            sismos_activos.append(f)

    viento_activo = []
    for f in viento.get("features", []):
        if f["properties"].get("exceeds"):
            anillo = f["geometry"]["coordinates"][0]
            f["_bbox"] = bbox_poligono(anillo)
            viento_activo.append(f)

    lluvia_activa = []
    for f in lluvia.get("features", []):
        if f["properties"].get("exceeds"):
            anillo = f["geometry"]["coordinates"][0]
            f["_bbox"] = bbox_poligono(anillo)
            lluvia_activa.append(f)

    return {
        "nodos": nodos["features"],
        "aristas": aristas["features"],
        "manzanas_densas": manzanas_densas,
        "antenas": antenas_activas,
        "incendios": incendios_activos,
        "sismos": sismos_activos,
        "viento": viento_activo,
        "lluvia": lluvia_activa,
    }


# ==============================================================================
# 3. CONSTRUCCIÓN DEL GRAFO ESPACIAL CON MODELO DE RIESGO
# ==============================================================================

def construir_grafo(datos, restricciones=None, incluir_estres=True, lambda_incendio=5.0):
    if restricciones is None:
        restricciones = {
            "evitar_incendios": True,
            "evitar_poblacion": True,
            "evitar_sismos": True,
            "garantizar_telecom": True,
            "evitar_viento": True,
            "evitar_lluvia": True,
        }

    nodos_por_id = {}
    nodos_por_code = {}
    for f in datos["nodos"]:
        nid = f["properties"]["id"]
        code = f["properties"]["code"]
        nodos_por_id[nid] = f["properties"]
        nodos_por_id[nid]["coord"] = f["geometry"]["coordinates"]
        nodos_por_code[code] = f["properties"]
        nodos_por_code[code]["coord"] = f["geometry"]["coordinates"]

    adj_dijkstra = {nid: [] for nid in nodos_por_id}
    adj_resiliente = {nid: [] for nid in nodos_por_id}
    info_aristas = {}

    for f in datos["aristas"]:
        eid = f["properties"]["id"]
        u = f["properties"]["source"]
        v = f["properties"]["target"]
        length = float(f["properties"]["length_m"])
        coords = f["geometry"]["coordinates"]

        coord_u = nodos_por_id[u]["coord"]
        coord_v = nodos_por_id[v]["coord"]

        hay_incendio_real, _ = arista_interseca_poligonos(coord_u, coord_v, datos["incendios"])
        hay_sismo, _ = arista_interseca_poligonos(coord_u, coord_v, datos["sismos"])
        hay_poblacion, _ = arista_interseca_poligonos(coord_u, coord_v, datos["manzanas_densas"])
        hay_telecom, _ = arista_interseca_poligonos(coord_u, coord_v, datos["antenas"])
        hay_viento, _ = arista_interseca_poligonos(coord_u, coord_v, datos["viento"])
        hay_lluvia, _ = arista_interseca_poligonos(coord_u, coord_v, datos["lluvia"])

        # Foco de contingencia en Planta Asfaltos Quintero (radio 180 m)
        d_foco = dist_punto_a_segmento_m(coord_u, coord_v, (FOCO_ESTRES["lon"], FOCO_ESTRES["lat"]))
        hay_estres = d_foco <= FOCO_ESTRES["radio_m"]

        # 1. Ponderación de costo de búsqueda resiliente (Routing weights)
        penalizacion = 0.0
        factores_riesgo = []

        if restricciones.get("evitar_incendios"):
            if hay_incendio_real:
                penalizacion += 15.0
                factores_riesgo.append("incendio_activo")
            if incluir_estres and hay_estres:
                penalizacion += 30.0  # Penalización suficiente para activar el bypass
                factores_riesgo.append("incendio_contingencia_simulado")

        if restricciones.get("evitar_sismos") and hay_sismo:
            penalizacion += 4.0
            factores_riesgo.append("alerta_sismica")

        if restricciones.get("evitar_poblacion") and hay_poblacion:
            penalizacion += 6.0  # Restricción DGAC DAN 151
            factores_riesgo.append("densidad_urbana_dan151")

        if restricciones.get("garantizar_telecom") and not hay_telecom:
            penalizacion += 2.5
            factores_riesgo.append("sombra_telecom")

        if restricciones.get("evitar_viento") and hay_viento:
            penalizacion += 2.0
            factores_riesgo.append("viento_extremo")

        if restricciones.get("evitar_lluvia") and hay_lluvia:
            penalizacion += 2.0
            factores_riesgo.append("lluvia_intensa")

        costo_resiliente = length * (1.0 + penalizacion)

        # 2. Tasa de riesgo física supuesta (Hazard Rate por km para evaluación de resiliencia)
        hazard_rate = 0.005  # Tasa base nominal por fallas mecánicas / ambientales generales
        if hay_incendio_real or (incluir_estres and hay_estres):
            hazard_rate += lambda_incendio
        if hay_poblacion:
            hazard_rate += 0.08  # Riesgo operacional y regulatorio sobre zonas densas
        if hay_sismo:
            hazard_rate += 0.05  # Riesgo por líneas oscilantes
        if not hay_telecom:
            hazard_rate += 0.03  # Riesgo por interrupción de enlace C2
        if hay_viento:
            hazard_rate += 0.04  # Viento sobre umbral operacional
        if hay_lluvia:
            hazard_rate += 0.03  # Precipitaciones sobre umbral

        info_aristas[eid] = {
            "id": eid,
            "source": u,
            "target": v,
            "length_m": length,
            "cost_resiliente": costo_resiliente,
            "hazard_rate": hazard_rate,
            "coords": coords,
            "hay_incendio": hay_incendio_real or (incluir_estres and hay_estres),
            "hay_sismo": hay_sismo,
            "hay_poblacion": hay_poblacion,
            "hay_telecom": hay_telecom,
            "hay_viento": hay_viento,
            "hay_lluvia": hay_lluvia,
            "hay_estres": hay_estres,
            "factores_riesgo": factores_riesgo,
        }

        adj_dijkstra[u].append((v, length, eid))
        adj_dijkstra[v].append((u, length, eid))
        adj_resiliente[u].append((v, costo_resiliente, eid))
        adj_resiliente[v].append((u, costo_resiliente, eid))

    return {
        "nodos_id": nodos_por_id,
        "nodos_code": nodos_por_code,
        "adj_dijkstra": adj_dijkstra,
        "adj_resiliente": adj_resiliente,
        "info_aristas": info_aristas,
    }


# ==============================================================================
# 4. ALGORITMO DE RUTEO DE K CAMINOS DISIMILARES (AKGÜN ET AL., 2000)
# ==============================================================================

def dijkstra_camino(adj, origen_id, destino_id, penalizaciones=None):
    if penalizaciones is None:
        penalizaciones = {}

    dist = {nid: float("inf") for nid in adj}
    padre_nodo = {}
    padre_arista = {}

    dist[origen_id] = 0.0
    pq = [(0.0, origen_id)]

    while pq:
        d_act, u = heapq.heappop(pq)
        if d_act > dist[u]:
            continue
        if u == destino_id:
            break

        for v, costo_base, eid in adj[u]:
            factor = penalizaciones.get(eid, 1.0)
            peso = costo_base * factor
            nueva_d = d_act + peso
            if nueva_d < dist[v]:
                dist[v] = nueva_d
                padre_nodo[v] = u
                padre_arista[v] = eid
                heapq.heappush(pq, (nueva_d, v))

    if dist[destino_id] == float("inf"):
        return None, [], []

    camino_nodos = []
    camino_aristas = []
    curr = destino_id
    while curr != origen_id:
        camino_nodos.append(curr)
        camino_aristas.append(padre_arista[curr])
        curr = padre_nodo[curr]
    camino_nodos.append(origen_id)

    camino_nodos.reverse()
    camino_aristas.reverse()

    return dist[destino_id], camino_nodos, camino_aristas


def calcular_par_ksp(adj, origen_id, destino_id, factor_penalizacion=4.0):
    costo_1, nodos_1, aristas_1 = dijkstra_camino(adj, origen_id, destino_id)
    if not nodos_1:
        return None, None

    penalizaciones = {eid: factor_penalizacion for eid in aristas_1}
    costo_2, nodos_2, aristas_2 = dijkstra_camino(adj, origen_id, destino_id, penalizaciones)
    if not nodos_2:
        costo_2, nodos_2, aristas_2 = costo_1, nodos_1, aristas_1

    return (costo_1, nodos_1, aristas_1), (costo_2, nodos_2, aristas_2)


# ==============================================================================
# 5. MÉTRICA DE RESILIENCIA PROBABILÍSTICA EXACTA PARA K RUTAS
# ==============================================================================

def calcular_resiliencia_conjunto_exacta(aristas_k1, aristas_k2, info_aristas):
    """
    Confiabilidad exacta del conjunto de 2 caminos con tramo común E_C:
    E_C = Pi_1 inter Pi_2 (aristas compartidas)
    E_1 = Pi_1 - Pi_2     (aristas exclusivas de ruta 1)
    E_2 = Pi_2 - Pi_1     (aristas exclusivas de ruta 2)

    Supuestos explícitos del modelo:
    1. Las fallas entre aristas no compartidas son probabilísticamente independientes.
    2. Una arista se considera completamente expuesta a la tasa de riesgo si su segmento intersecta la zona de amenaza.
    3. R = S(E_C) * [1 - (1 - S(E_1)) * (1 - S(E_2))].
    """
    s1 = set(aristas_k1)
    s2 = set(aristas_k2)
    ec = s1.intersection(s2)
    e1_only = s1 - s2
    e2_only = s2 - s1

    def surv(edge_set):
        h = sum(info_aristas[e]["hazard_rate"] * (info_aristas[e]["length_m"] / 1000.0) for e in edge_set)
        return math.exp(-h)

    S_c = surv(ec)
    S_1 = surv(e1_only)
    S_2 = surv(e2_only)

    R_exacta = S_c * (1.0 - (1.0 - S_1) * (1.0 - S_2))
    S_k1 = surv(s1)
    S_k2 = surv(s2)

    total_union = s1.union(s2)
    diversidad = (1.0 - (len(ec) / len(total_union))) * 100.0 if total_union else 0.0

    amenazas_k1 = set()
    for e in s1:
        amenazas_k1.update(info_aristas[e]["factores_riesgo"])

    amenazas_k2 = set()
    for e in s2:
        amenazas_k2.update(info_aristas[e]["factores_riesgo"])

    l_k1 = sum(info_aristas[e]["length_m"] for e in aristas_k1)
    l_k2 = sum(info_aristas[e]["length_m"] for e in aristas_k2)

    return {
        "resiliencia_conjunto_pct": round(R_exacta * 100.0, 1),
        "supervivencia_k1_pct": round(S_k1 * 100.0, 1),
        "supervivencia_k2_pct": round(S_k2 * 100.0, 1),
        "diversidad_pct": round(diversidad, 1),
        "longitud_k1_m": round(l_k1, 1),
        "longitud_k2_m": round(l_k2, 1),
        "amenazas_k1": sorted(list(amenazas_k1)),
        "amenazas_k2": sorted(list(amenazas_k2)),
    }


def reconstruir_linea_geom(camino_aristas, camino_nodos, info_aristas, nodos_id):
    coords = [nodos_id[camino_nodos[0]]["coord"]]
    for next_node, eid in zip(camino_nodos[1:], camino_aristas):
        e_coords = info_aristas[eid]["coords"]
        d_dir = math.hypot(e_coords[0][0] - coords[-1][0], e_coords[0][1] - coords[-1][1])
        d_inv = math.hypot(e_coords[-1][0] - coords[-1][0], e_coords[-1][1] - coords[-1][1])
        segmento = e_coords if d_dir <= d_inv else list(reversed(e_coords))
        for pt in segmento[1:]:
            coords.append(pt)
    return {"type": "LineString", "coordinates": coords}


# ==============================================================================
# 6. EJECUCIÓN Y GENERACIÓN DE ENTREGABLES
# ==============================================================================

def evaluar_escenario(grafo, destinos_sinca, origen_id, etiqueta="contingencia"):
    nodos_id = grafo["nodos_id"]
    adj_dijkstra = grafo["adj_dijkstra"]
    adj_resiliente = grafo["adj_resiliente"]
    info_aristas = grafo["info_aristas"]

    features = []
    resumen = {}

    for dest in destinos_sinca:
        dest_id = dest["id"]
        dest_code = dest["code"]
        dest_name = dest["name"]

        dijkstra_k1, dijkstra_k2 = calcular_par_ksp(adj_dijkstra, origen_id, dest_id, factor_penalizacion=4.0)
        resiliente_k1, resiliente_k2 = calcular_par_ksp(adj_resiliente, origen_id, dest_id, factor_penalizacion=4.0)

        if not dijkstra_k1 or not resiliente_k1:
            continue

        met_dijkstra = calcular_resiliencia_conjunto_exacta(dijkstra_k1[2], dijkstra_k2[2], info_aristas)
        met_resiliente = calcular_resiliencia_conjunto_exacta(resiliente_k1[2], resiliente_k2[2], info_aristas)

        delta_res = round(met_resiliente["resiliencia_conjunto_pct"] - met_dijkstra["resiliencia_conjunto_pct"], 1)

        resumen[dest_code] = {
            "nombre": dest_name,
            "dijkstra": {
                "longitud_k1_m": met_dijkstra["longitud_k1_m"],
                "longitud_k2_m": met_dijkstra["longitud_k2_m"],
                "supervivencia_k1_pct": met_dijkstra["supervivencia_k1_pct"],
                "supervivencia_k2_pct": met_dijkstra["supervivencia_k2_pct"],
                "diversidad_pct": met_dijkstra["diversidad_pct"],
                "resiliencia_conjunto_pct": met_dijkstra["resiliencia_conjunto_pct"],
                "amenazas": met_dijkstra["amenazas_k1"],
            },
            "resiliente": {
                "longitud_k1_m": met_resiliente["longitud_k1_m"],
                "longitud_k2_m": met_resiliente["longitud_k2_m"],
                "supervivencia_k1_pct": met_resiliente["supervivencia_k1_pct"],
                "supervivencia_k2_pct": met_resiliente["supervivencia_k2_pct"],
                "diversidad_pct": met_resiliente["diversidad_pct"],
                "resiliencia_conjunto_pct": met_resiliente["resiliencia_conjunto_pct"],
                "amenazas": met_resiliente["amenazas_k1"],
            },
            "delta_resiliencia_pp": delta_res,
        }

        features.append({
            "type": "Feature",
            "geometry": reconstruir_linea_geom(dijkstra_k1[2], dijkstra_k1[1], info_aristas, nodos_id),
            "properties": {
                "tipo_algoritmo": "dijkstra_k1",
                "etiqueta": f"Dijkstra k=1 ({etiqueta})",
                "k_orden": 1,
                "origen": ORIGEN_BASE,
                "destino": dest_code,
                "destino_nombre": dest_name,
                "longitud_m": met_dijkstra["longitud_k1_m"],
                "supervivencia_pct": met_dijkstra["supervivencia_k1_pct"],
                "amenazas": met_dijkstra["amenazas_k1"],
            }
        })
        features.append({
            "type": "Feature",
            "geometry": reconstruir_linea_geom(dijkstra_k2[2], dijkstra_k2[1], info_aristas, nodos_id),
            "properties": {
                "tipo_algoritmo": "dijkstra_k2",
                "etiqueta": f"Dijkstra k=2 ({etiqueta})",
                "k_orden": 2,
                "origen": ORIGEN_BASE,
                "destino": dest_code,
                "destino_nombre": dest_name,
                "longitud_m": met_dijkstra["longitud_k2_m"],
                "supervivencia_pct": met_dijkstra["supervivencia_k2_pct"],
                "amenazas": met_dijkstra["amenazas_k2"],
            }
        })
        features.append({
            "type": "Feature",
            "geometry": reconstruir_linea_geom(resiliente_k1[2], resiliente_k1[1], info_aristas, nodos_id),
            "properties": {
                "tipo_algoritmo": "resiliente_k1",
                "etiqueta": f"Resiliente k=1 ({etiqueta})",
                "k_orden": 1,
                "origen": ORIGEN_BASE,
                "destino": dest_code,
                "destino_nombre": dest_name,
                "longitud_m": met_resiliente["longitud_k1_m"],
                "supervivencia_pct": met_resiliente["supervivencia_k1_pct"],
                "amenazas": met_resiliente["amenazas_k1"],
            }
        })
        features.append({
            "type": "Feature",
            "geometry": reconstruir_linea_geom(resiliente_k2[2], resiliente_k2[1], info_aristas, nodos_id),
            "properties": {
                "tipo_algoritmo": "resiliente_k2",
                "etiqueta": f"Resiliente k=2 ({etiqueta})",
                "k_orden": 2,
                "origen": ORIGEN_BASE,
                "destino": dest_code,
                "destino_nombre": dest_name,
                "longitud_m": met_resiliente["longitud_k2_m"],
                "supervivencia_pct": met_resiliente["supervivencia_k2_pct"],
                "amenazas": met_resiliente["amenazas_k2"],
            }
        })

    return resumen, features


def ejecutar_comparativa_completa():
    print("-> Cargando capas geoespaciales...")
    datos = cargar_capas()

    destinos_sinca = [f["properties"] for f in datos["nodos"] if f["properties"].get("category") == "sinca"]
    destinos_sinca.sort(key=lambda x: x["name"])

    # Encontrar ID de origen base
    origen_id = next(f["properties"]["id"] for f in datos["nodos"] if f["properties"]["code"] == ORIGEN_BASE)

    # 1. Escenario Base (Condiciones reales actuales, sin contingencia)
    print("-> Calculando Escenario Base (datos reales basales)...")
    grafo_base = construir_grafo(datos, incluir_estres=False)
    resumen_base, _ = evaluar_escenario(grafo_base, destinos_sinca, origen_id, etiqueta="base")

    # 2. Escenario de Contingencia (Incendio industrial en Planta Asfaltos)
    print("-> Calculando Escenario de Contingencia (foco simulado en Planta Asfaltos)...")
    grafo_estres = construir_grafo(datos, incluir_estres=True, lambda_incendio=5.0)
    resumen_estres, features_comparativas = evaluar_escenario(grafo_estres, destinos_sinca, origen_id, etiqueta="contingencia")

    # 3. Análisis de Sensibilidad para lambda_incendio hacia Puchuncaví
    print("-> Ejecutando análisis de sensibilidad de lambda_incendio...")
    sensibilidad_puchuncavi = []
    puchuncavi_prop = next(d for d in destinos_sinca if d["code"] == "sinca_puchuncavi")
    for lam in [0.5, 1.0, 5.0]:
        g_sens = construir_grafo(datos, incluir_estres=True, lambda_incendio=lam)
        d_k1, d_k2 = calcular_par_ksp(g_sens["adj_dijkstra"], origen_id, puchuncavi_prop["id"], factor_penalizacion=4.0)
        r_k1, r_k2 = calcular_par_ksp(g_sens["adj_resiliente"], origen_id, puchuncavi_prop["id"], factor_penalizacion=4.0)
        m_d = calcular_resiliencia_conjunto_exacta(d_k1[2], d_k2[2], g_sens["info_aristas"])
        m_r = calcular_resiliencia_conjunto_exacta(r_k1[2], r_k2[2], g_sens["info_aristas"])
        sensibilidad_puchuncavi.append({
            "lambda_incendio": lam,
            "resiliencia_dijkstra_pct": m_d["resiliencia_conjunto_pct"],
            "resiliencia_resiliente_pct": m_r["resiliencia_conjunto_pct"],
            "delta_pp": round(m_r["resiliencia_conjunto_pct"] - m_d["resiliencia_conjunto_pct"], 1)
        })

    # Guardar GeoJSON con bloque etl formal
    out_geojson = RAIZ / "sitio_web" / "data" / "rutas_comparativas.geojson"
    out_geojson.parent.mkdir(parents=True, exist_ok=True)
    fc = {
        "type": "FeatureCollection",
        "etl": {
            "fuente": "Ruteo Resiliente Akgün et al. (2000) / GPP Kosior et al. (2024)",
            "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "paper": "Kosior, M., Przystałka, P., & Panfil, W. (2024). Adaptive Path Planning for UAV-Based Pollution Sampling. Applied Sciences, 14(24), 12065.",
            "algoritmo": "Akgün et al. (2000) K-caminos disimilares por penalización iterativa de aristas",
            "parametros": {
                "origen": ORIGEN_BASE,
                "k_rutas": 2,
                "factor_penalizacion_k2": 4.0,
                "escenario_contingencia_activo": True,
                "foco_contingencia": FOCO_ESTRES,
                "tasas_riesgo_supuestas": {
                    "lambda_base": 0.005,
                    "lambda_incendio": 5.0,
                    "lambda_urbano_dan151": 0.08,
                    "lambda_sismo": 0.05,
                    "lambda_telecom": 0.03,
                    "lambda_viento": 0.04,
                    "lambda_lluvia": 0.03,
                },
            },
            "total": len(features_comparativas),
        },
        "features": features_comparativas,
    }
    with open(out_geojson, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Generadas {len(features_comparativas)} rutas en {out_geojson.name}")

    # Guardar JSON de Resumen con ambos escenarios y análisis de sensibilidad
    out_json = RAIZ / "sitio_web" / "data" / "resumen_resiliencia.json"
    resumen_data = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "paper": "Kosior, M., Przystałka, P., & Panfil, W. (2024). Adaptive Path Planning for UAV-Based Pollution Sampling. Applied Sciences, 14(24), 12065.",
        "algoritmo": "Akgün et al. (2000) K-caminos disimilares por penalización iterativa de aristas",
        "metrica": "Confiabilidad estocástica exacta R = S(E_C) * [1 - (1 - S(E_1))(1 - S(E_2))]",
        "parametros": {
            "origen": ORIGEN_BASE,
            "k_rutas": 2,
            "factor_penalizacion_k2": 4.0,
            "foco_contingencia": FOCO_ESTRES,
            "tasas_riesgo_supuestas": {
                "lambda_base": 0.005,
                "lambda_incendio": 5.0,
                "lambda_urbano_dan151": 0.08,
                "lambda_sismo": 0.05,
                "lambda_telecom": 0.03,
                "lambda_viento": 0.04,
                "lambda_lluvia": 0.03,
            },
        },
        "escenario_base_datos_reales": resumen_base,
        "escenario_contingencia_simulado": resumen_estres,
        "analisis_sensibilidad_puchuncavi": sensibilidad_puchuncavi,
        "destinos": resumen_estres,  # compatibilidad con clientes existentes
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(resumen_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Generado resumen cuantitativo en {out_json.name}")

    print("\n--- COMPARATIVA EN ESCENARIO DE CONTINGENCIA SIMULADO ---")
    for dest_code, d in resumen_estres.items():
        dij = d["dijkstra"]
        res = d["resiliente"]
        delta = d["delta_resiliencia_pp"]
        print(f"  {d['nombre']:<30} | D: {dij['longitud_k1_m']/1000:5.2f}km (R:{dij['resiliencia_conjunto_pct']:5.1f}%) -> "
              f"RES: {res['longitud_k1_m']/1000:5.2f}km (R:{res['resiliencia_conjunto_pct']:5.1f}%) | "
              f"Delta: {delta:+5.1f} p.p.")

    print("\n--- ANALISIS DE SENSIBILIDAD PUCHUNCAVI (lambda_incendio) ---")
    for s in sensibilidad_puchuncavi:
        print(f"  lambda={s['lambda_incendio']:3.1f} | R Dijkstra: {s['resiliencia_dijkstra_pct']:5.1f}% | "
              f"R Resiliente: {s['resiliencia_resiliente_pct']:5.1f}% | Delta R: {s['delta_pp']:+5.1f} p.p.")


if __name__ == "__main__":
    ejecutar_comparativa_completa()
