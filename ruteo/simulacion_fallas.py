"""Probabilidades de falla, simulación Monte Carlo y métrica de resiliencia (Fase 3).

Cubre los requerimientos 5, 7 y 8 de la rúbrica:

  5. Cada amenaza se modela como una tasa de falla lambda_f; con ellas se calcula la
     probabilidad de falla de cada ARISTA y de cada NODO:

         lambda(e) = lambda_base + sum_f lambda_f(e)      P(e) = 1 - exp(-lambda(e) * L_km(e))
         lambda(v) = sum_f lambda_f(v)                    P(v) = 1 - exp(-lambda(v))

     Viento sobre el umbral (> 12 m/s) y niebla bajo el umbral de visibilidad (< 1000 m)
     son bloqueos deterministas: P = 1.

  7. Monte Carlo: para cada nodo y arista se sortea u ~ U[0, 100); el elemento FALLA si
     u < P * 100. Una ruta sobrevive si ninguno de sus nodos ni aristas falló.

  8. Resiliencia analítica R (independiente de la simulación):
         S(P)  = prod_e S(e) * prod_v S(v),                S = 1 - P
         R(P1, P2) = S(E_C) * [1 - (1 - S(E_1)) * (1 - S(E_2))]
     con E_C = P1 ∩ P2, E_1 = P1 \\ P2, E_2 = P2 \\ P1 (aristas y nodos).

Notas de diseño / supuestos (revisar con el equipo):
  - Los lambdas salen de DEFAULTS_FASE3 y pueden sobrescribirse con config/parametros.json
    (clave "fallas"). Los de la especificación del equipo son: incendio 5.0, viento
    moderado 0.04, humedad > 90 % 0.03, manzana densa 0.08, sombra C2 0.05.
    OJO: ruteo_resiliente.py usa sin_cobertura = 0.03 y trata el viento > 12 m/s como
    lambda 0.04 (no como bloqueo). Aquí se sigue la especificación.
  - "Viento moderado" no tiene umbral definido en la especificación: se asume >= 8 m/s
    (configurable con "viento_moderado_ms").
  - sismo (0.05) y lluvia (0.03) se mantienen porque ya existen como capas del proyecto.
  - Una arista queda expuesta a una amenaza si alguno de 5 puntos muestreados a lo largo
    de su segmento cae dentro de la zona (mismo criterio que ruteo_resiliente.py).

Uso:
    python3 ruteo/simulacion_fallas.py              # demo con el escenario base
    python3 ruteo/simulacion_fallas.py --contingencia   # activa el foco Planta Asfaltos
"""

import argparse
import heapq
import json
import math
import random
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_PATH = RAIZ / "config" / "parametros.json"

DEFAULTS_FASE3 = {
    "base": 0.005,
    "incendio": 5.0,
    "viento_moderado": 0.04,
    "viento_moderado_ms": 8.0,       # supuesto: la especificación no fija este umbral
    "humedad": 0.03,
    "humedad_umbral_pct": 90.0,
    "densidad": 0.08,
    "densidad_umbral_hab_km2": 2500.0,
    "sin_c2": 0.05,
    "sismo": 0.05,
    "lluvia": 0.03,
}

CAPAS_POR_DEFECTO = {"incendio", "sismo", "viento", "lluvia", "niebla", "humedad", "densidad", "c2"}
CAPAS_TODAS = CAPAS_POR_DEFECTO | {"contingencia"}
NUM_MUESTRAS_ARISTA = 5


# ==============================================================================
# 1. GEOMETRÍA Y CARGA DE CAPAS
# ==============================================================================

def _anillos(geom):
    """Lista de anillos exteriores de un Polygon o MultiPolygon."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def _punto_en_anillo(x, y, anillo):
    adentro = False
    p1x, p1y = anillo[0]
    n = len(anillo)
    for i in range(1, n + 1):
        p2x, p2y = anillo[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x or x <= xinters:
                adentro = not adentro
        p1x, p1y = p2x, p2y
    return adentro


def _preparar(features):
    """Precalcula anillos y bbox (de TODOS los anillos) para acelerar las consultas."""
    listos = []
    for f in features:
        anillos = _anillos(f["geometry"])
        if not anillos:
            continue
        xs = [p[0] for a in anillos for p in a]
        ys = [p[1] for a in anillos for p in a]
        listos.append({"props": f["properties"], "anillos": anillos,
                       "bbox": (min(xs), min(ys), max(xs), max(ys))})
    return listos


def _celdas_en(x, y, capa):
    """Propiedades de todas las zonas de la capa que contienen el punto (lon, lat)."""
    res = []
    for z in capa:
        x0, y0, x1, y1 = z["bbox"]
        if x < x0 or x > x1 or y < y0 or y > y1:
            continue
        if any(_punto_en_anillo(x, y, a) for a in z["anillos"]):
            res.append(z["props"])
    return res


def _dist_m(p1, p2):
    lat_mid = (p1[1] + p2[1]) / 2.0 * math.pi / 180.0
    dx = (p2[0] - p1[0]) * math.cos(lat_mid) * 111320.0
    dy = (p2[1] - p1[1]) * 110540.0
    return math.hypot(dx, dy)


def _dist_punto_segmento_m(p1, p2, p):
    lat = p[1] * math.pi / 180.0
    kx, ky = math.cos(lat) * 111320.0, 110540.0
    x1, y1, x2, y2, px, py = p1[0] * kx, p1[1] * ky, p2[0] * kx, p2[1] * ky, p[0] * kx, p[1] * ky
    dx, dy = x2 - x1, y2 - y1
    l2 = dx * dx + dy * dy
    if l2 == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _leer(rel):
    p = RAIZ / rel
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("features", [])


def _cargar_parametros():
    cfg = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
    lam = dict(DEFAULTS_FASE3)
    lam["base"] = cfg.get("lambdas", {}).get("base", lam["base"])
    lam.update(cfg.get("fallas", {}))
    lam["_contingencia"] = cfg.get("contingencia", {"lon": -71.4935, "lat": -32.7801, "radio_m": 180.0})
    return lam


def cargar_infraestructura_y_capas():
    nodos = _leer("infraestructura/nodos.geojson")
    aristas = _leer("infraestructura/aristas.geojson")
    capas = {
        "incendio": _preparar([f for f in _leer("amenazas/firms_incendios.geojson")
                               if f["properties"].get("exceeds")]),
        "sismo": _preparar([f for f in _leer("amenazas/csn_sismos.geojson")
                            if f["properties"].get("exceeds")]
                           ),
        "viento": _preparar(_leer("amenazas/openmeteo_viento.geojson")),   # todas: se usa el valor
        "lluvia": _preparar([f for f in _leer("amenazas/metno_lluvia.geojson")
                             if f["properties"].get("exceeds")]),
        "niebla": _preparar(_leer("amenazas/openmeteo_niebla.geojson")),   # todas: bloqueo + humedad
        "manzanas": _preparar(_leer("metadata/ine_manzanas.geojson")),
        "antenas": _preparar(_leer("metadata/osm_antenas.geojson")),
    }
    return nodos, aristas, capas


# ==============================================================================
# 2. MODELO DE PROBABILIDADES DE FALLA
# ==============================================================================

def _factores_en_punto(x, y, capas, params, activas):
    """Devuelve (lambdas_por_factor, bloqueado, causas_bloqueo) para un punto (lon, lat)."""
    lam, bloqueos = {}, []

    if "incendio" in activas and _celdas_en(x, y, capas["incendio"]):
        lam["incendio"] = params["incendio"]
    if "sismo" in activas and _celdas_en(x, y, capas["sismo"]):
        lam["sismo"] = params["sismo"]
    if "lluvia" in activas and _celdas_en(x, y, capas["lluvia"]):
        lam["lluvia"] = params["lluvia"]

    if "viento" in activas:
        for p in _celdas_en(x, y, capas["viento"]):
            if p.get("exceeds"):
                bloqueos.append("viento_extremo")
            elif p.get("value", 0) >= params["viento_moderado_ms"]:
                lam["viento_moderado"] = params["viento_moderado"]

    for p in _celdas_en(x, y, capas["niebla"]):
        if "niebla" in activas and p.get("exceeds"):
            bloqueos.append("niebla")
        if "humedad" in activas and p.get("relative_humidity", 0) > params["humedad_umbral_pct"]:
            lam["humedad"] = params["humedad"]

    if "densidad" in activas:
        for p in _celdas_en(x, y, capas["manzanas"]):
            if p.get("density_hab_km2", 0) > params["densidad_umbral_hab_km2"]:
                lam["densidad"] = params["densidad"]
                break

    if "c2" in activas and not _celdas_en(x, y, capas["antenas"]):
        lam["sin_c2"] = params["sin_c2"]

    return lam, sorted(set(bloqueos))


def construir_modelo_fallas(capas_activas=None, params=None, datos=None):
    """Calcula P_falla de cada nodo y cada arista a partir de las amenazas activas.

    capas_activas: subconjunto de CAPAS_TODAS (permite enlazarlo a los checkboxes del panel).
                   Por defecto todas menos 'contingencia'.
    """
    activas = set(CAPAS_POR_DEFECTO if capas_activas is None else capas_activas)
    params = params or _cargar_parametros()
    nodos, aristas, capas = datos or cargar_infraestructura_y_capas()
    foco = params["_contingencia"]
    coord = {n["properties"]["id"]: n["geometry"]["coordinates"] for n in nodos}

    def foco_activo(p1, p2=None):
        if "contingencia" not in activas:
            return False
        c = (foco["lon"], foco["lat"])
        d = _dist_punto_segmento_m(p1, p2, c) if p2 else _dist_m(p1, c)
        return d <= foco["radio_m"]

    modelo_nodos = {}
    for n in nodos:
        nid = n["properties"]["id"]
        x, y = coord[nid]
        lam, bloq = _factores_en_punto(x, y, capas, params, activas)
        if foco_activo((x, y)):
            lam["incendio_contingencia"] = params["incendio"]
        total = sum(lam.values())
        bloqueado = bool(bloq)
        modelo_nodos[nid] = {
            "lambda": total,
            "p_falla": 1.0 if bloqueado else 1.0 - math.exp(-total),
            "bloqueado": bloqueado,
            "factores": {**lam, **{b: None for b in bloq}},
        }

    modelo_aristas = {}
    for e in aristas:
        pr = e["properties"]
        eid, u, v = pr["id"], pr["source"], pr["target"]
        largo_m = float(pr["length_m"])
        cu, cv = coord[u], coord[v]
        lam, bloq = {}, set()
        # Una amenaza afecta a la arista si alguna muestra del segmento cae dentro.
        for i in range(NUM_MUESTRAS_ARISTA):
            t = i / (NUM_MUESTRAS_ARISTA - 1)
            x, y = cu[0] + t * (cv[0] - cu[0]), cu[1] + t * (cv[1] - cu[1])
            l_i, b_i = _factores_en_punto(x, y, capas, params, activas)
            bloq.update(b_i)
            for k, val in l_i.items():
                if k != "sin_c2":
                    lam[k] = val
            # La sombra C2 solo cuenta si NINGUNA muestra tiene cobertura (igual que
            # ruteo_resiliente: la arista con alguna cobertura se considera cubierta).
        if "c2" in activas:
            cubierta = any(
                _celdas_en(cu[0] + (i / (NUM_MUESTRAS_ARISTA - 1)) * (cv[0] - cu[0]),
                           cu[1] + (i / (NUM_MUESTRAS_ARISTA - 1)) * (cv[1] - cu[1]),
                           capas["antenas"])
                for i in range(NUM_MUESTRAS_ARISTA))
            if not cubierta:
                lam["sin_c2"] = params["sin_c2"]
        if foco_activo(cu, cv):
            lam["incendio_contingencia"] = params["incendio"]

        total = params["base"] + sum(lam.values())
        km = largo_m / 1000.0
        bloqueado = bool(bloq)
        modelo_aristas[eid] = {
            "source": u, "target": v, "length_m": largo_m,
            "lambda": total,
            "p_falla": 1.0 if bloqueado else 1.0 - math.exp(-total * km),
            "bloqueado": bloqueado,
            "factores": {**lam, **{b: None for b in sorted(bloq)}},
        }

    return {
        "nodos": modelo_nodos,
        "aristas": modelo_aristas,
        "meta": {"capas_activas": sorted(activas),
                 "lambdas": {k: v for k, v in params.items() if not k.startswith("_")}},
    }


def guardar_modelo(modelo, ruta="sitio_web/data/probabilidades_falla.json"):
    """Exporta las probabilidades para que la web las pinte/consulte."""
    destino = RAIZ / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(modelo, f, ensure_ascii=False)
    return destino


# ==============================================================================
# 3. RESILIENCIA ANALÍTICA R
# ==============================================================================
# Un "camino" es {"nodos": [ids], "aristas": [ids]}.

def _supervivencia(modelo, elementos):
    """S(conjunto) = producto de (1 - P) de los elementos ('n', id) y ('e', id)."""
    s = 1.0
    for tipo, eid in elementos:
        p = (modelo["nodos"] if tipo == "n" else modelo["aristas"])[eid]["p_falla"]
        s *= (1.0 - p)
    return s


def _elementos(camino):
    return {("n", n) for n in camino["nodos"]} | {("e", e) for e in camino["aristas"]}


def supervivencia_ruta(modelo, camino):
    return _supervivencia(modelo, _elementos(camino))


def resiliencia_par(modelo, camino1, camino2):
    """R(P1, P2) = S(E_C) * [1 - (1 - S(E_1)) * (1 - S(E_2))]."""
    a, b = _elementos(camino1), _elementos(camino2)
    s_c = _supervivencia(modelo, a & b)
    s_1 = _supervivencia(modelo, a - b)
    s_2 = _supervivencia(modelo, b - a)
    return s_c * (1.0 - (1.0 - s_1) * (1.0 - s_2))


def resiliencia_tecnica(modelo, caminos):
    """R de una técnica: un camino -> S(P); dos caminos -> R(P1, P2)."""
    if len(caminos) == 1:
        return supervivencia_ruta(modelo, caminos[0])
    return resiliencia_par(modelo, caminos[0], caminos[1])


# ==============================================================================
# 4. MONTE CARLO (u ~ U[0, 100))
# ==============================================================================

def simular_fallas(modelo, rng=None, seed=None):
    """Una realización completa: sortea u para TODOS los nodos y aristas.

    Devuelve los ids caídos (para pintarlos en rojo en el mapa) y los u sorteados.
    """
    rng = rng or random.Random(seed)
    u_nodos = {nid: rng.random() * 100.0 for nid in modelo["nodos"]}
    u_aristas = {eid: rng.random() * 100.0 for eid in modelo["aristas"]}
    return {
        "u_nodos": u_nodos,
        "u_aristas": u_aristas,
        "nodos_caidos": sorted(n for n, u in u_nodos.items() if u < modelo["nodos"][n]["p_falla"] * 100.0),
        "aristas_caidas": sorted(e for e, u in u_aristas.items() if u < modelo["aristas"][e]["p_falla"] * 100.0),
    }


def camino_sobrevive(realizacion, camino):
    caidos_n = set(realizacion["nodos_caidos"])
    caidas_e = set(realizacion["aristas_caidas"])
    return not (caidos_n & set(camino["nodos"])) and not (caidas_e & set(camino["aristas"]))


def tecnica_sobrevive(realizacion, caminos):
    """Una técnica con 2 caminos (redundante) sobrevive si al menos uno sobrevive."""
    return any(camino_sobrevive(realizacion, c) for c in caminos)


def evaluar_simulacion(modelo, tecnicas, rng=None, seed=None):
    """Simula una realización y dice qué técnicas 'Sobrevivió' o 'Falló'."""
    real = simular_fallas(modelo, rng=rng, seed=seed)
    return real, {nombre: tecnica_sobrevive(real, caminos) for nombre, caminos in tecnicas.items()}


def monte_carlo_supervivencia(modelo, tecnicas, n=2000, seed=None):
    """% de realizaciones en que sobrevive cada técnica (misma realización para todas)."""
    rng = random.Random(seed)
    ok = {nombre: 0 for nombre in tecnicas}
    for _ in range(n):
        real = simular_fallas(modelo, rng=rng)
        for nombre, caminos in tecnicas.items():
            ok[nombre] += tecnica_sobrevive(real, caminos)
    return {nombre: 100.0 * c / n for nombre, c in ok.items()}


# ==============================================================================
# 5. DEMO (CLI): valida el modelo con rutas simples del proyecto
# ==============================================================================

def _adyacencia(modelo, beta=None):
    """Adyacencia sin aristas bloqueadas. beta=None -> solo distancia."""
    adj = {nid: [] for nid in modelo["nodos"]}
    for eid, e in modelo["aristas"].items():
        if e["bloqueado"] or modelo["nodos"][e["source"]]["bloqueado"] or modelo["nodos"][e["target"]]["bloqueado"]:
            continue
        costo = e["length_m"] if beta is None else e["length_m"] + beta * e["lambda"] * (e["length_m"] / 1000.0)
        adj[e["source"]].append((e["target"], costo, eid))
        adj[e["target"]].append((e["source"], costo, eid))
    return adj


def _dijkstra(adj, origen, destino, penal=None):
    penal = penal or {}
    dist = {u: math.inf for u in adj}
    prev = {}
    dist[origen] = 0.0
    pq = [(0.0, origen)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == destino:
            break
        for v, c, eid in adj[u]:
            nd = d + c * penal.get(eid, 1.0)
            if nd < dist[v]:
                dist[v], prev[v] = nd, (u, eid)
                heapq.heappush(pq, (nd, v))
    if dist[destino] == math.inf:
        return None
    nodos, aristas, cur = [destino], [], destino
    while cur != origen:
        cur, eid = prev[cur]
        nodos.append(cur)
        aristas.append(eid)
    return {"nodos": nodos[::-1], "aristas": aristas[::-1]}


def _largo_km(modelo, camino):
    return sum(modelo["aristas"][e]["length_m"] for e in camino["aristas"]) / 1000.0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--contingencia", action="store_true", help="activa el foco Planta Asfaltos")
    ap.add_argument("--n", type=int, default=2000, help="realizaciones Monte Carlo")
    ap.add_argument("--guardar", action="store_true", help="escribe sitio_web/data/probabilidades_falla.json")
    args = ap.parse_args()

    activas = CAPAS_POR_DEFECTO | ({"contingencia"} if args.contingencia else set())
    t0 = time.perf_counter()
    modelo = construir_modelo_fallas(activas)
    print(f"Modelo construido en {1000 * (time.perf_counter() - t0):.0f} ms "
          f"({len(modelo['nodos'])} nodos, {len(modelo['aristas'])} aristas)")

    bl_a = sum(a["bloqueado"] for a in modelo["aristas"].values())
    bl_n = sum(n["bloqueado"] for n in modelo["nodos"].values())
    pa = sorted(a["p_falla"] for a in modelo["aristas"].values())
    print(f"Bloqueos deterministas: {bl_a} aristas, {bl_n} nodos | "
          f"P_falla aristas: min {pa[0]:.3f}  mediana {pa[len(pa) // 2]:.3f}  max {pa[-1]:.3f}")
    conteo = {}
    for a in modelo["aristas"].values():
        for f in a["factores"]:
            conteo[f] = conteo.get(f, 0) + 1
    print("Aristas expuestas por factor:", dict(sorted(conteo.items(), key=lambda x: -x[1])))

    if args.guardar:
        print("Guardado en", guardar_modelo(modelo))

    # Demo de rutas: base SCER -> primer destino SINCA (por nombre)
    nodos, _, _ = cargar_infraestructura_y_capas()
    origen = next(n["properties"]["id"] for n in nodos if n["properties"]["code"] == "base_scer")
    destinos = sorted((n["properties"] for n in nodos if n["properties"].get("category") == "sinca"),
                      key=lambda p: p["name"])
    print("\nDemo (NO son las 4 técnicas finales): Dijkstra distancia, Dijkstra riesgo, par Akgün")
    for d in destinos[:8]:
        adj_d, adj_r = _adyacencia(modelo), _adyacencia(modelo, beta=1000.0)
        # Dijkstra "distancia pura" ignora bloqueos: usa todas las aristas (línea base del enunciado)
        adj_base = {n: [] for n in modelo["nodos"]}
        for eid, e in modelo["aristas"].items():
            adj_base[e["source"]].append((e["target"], e["length_m"], eid))
            adj_base[e["target"]].append((e["source"], e["length_m"], eid))
        p_d = _dijkstra(adj_base, origen, d["id"])
        p_r = _dijkstra(adj_r, origen, d["id"])
        if not p_d or not p_r:
            print(f"- {d['name']}: sin ruta (todo bloqueado)")
            continue
        p_2 = _dijkstra(adj_r, origen, d["id"], {e: 4.0 for e in p_r["aristas"]}) or p_r
        tecnicas = {"dijkstra_distancia": [p_d], "dijkstra_riesgo": [p_r], "akgun_par": [p_r, p_2]}
        mc = monte_carlo_supervivencia(modelo, tecnicas, n=args.n, seed=42)
        print(f"- {d['name']}")
        for nombre, caminos in tecnicas.items():
            lk = sum(_largo_km(modelo, c) for c in caminos[:1])
            print(f"    {nombre:20s} L={lk:5.2f} km  R={100 * resiliencia_tecnica(modelo, caminos):6.2f}%  "
                  f"MC={mc[nombre]:6.1f}%")


if __name__ == "__main__":
    main()
