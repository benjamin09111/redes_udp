"""Las 4 técnicas de ruteo de la Fase 3 (requerimiento 6 de la rúbrica).

    1. dijkstra_distancia      pgr_dijkstra con costo = length_m (línea base, ignora amenazas)
    2. milp_exacto             MILP exacto (PuLP + solver) con flujo, autonomía, admisibilidad y MTZ
    3. dijkstra_multicriterio  pgr_dijkstra con costo W(e) = L + beta*H(e) - R(e), sin aristas bloqueadas
    4. metaheuristica_akgun    par de rutas disímiles (Akgün et al., 2000) con buffers de 200 m

Todas comparten el modelo de fallas de `simulacion_fallas.py`:
    H(e) = lambda(e) * L_km(e)      (fallas esperadas de la arista)
    W(e) = max(L + beta*H - R, 1)   (R = recompensa de muestreo; el piso evita costos <= 0)

Notas de diseño (revisar con el equipo):
  - El SQL de las instrucciones usa hazard_penalty / sample_reward / is_blocked, pero esas
    columnas NO existen en infra_edge. Aquí el costo se calcula en Python desde el modelo de
    fallas y se envía a pgRouting como una tabla VALUES dentro de la consulta de aristas.
  - Backend "python" (por defecto): Dijkstra propio. Backend "pgrouting": ejecuta pgr_dijkstra
    en PostgreSQL (requiere la BD levantada; si falla, se cae a Python y queda anotado).
    El backend pgrouting NO se pudo probar en el entorno de desarrollo (sin Docker).
  - El MILP prefiere GUROBI o CPLEX si están instalados y licenciados; si no, usa HiGHS.
  - Autonomía: es restricción dura solo en el MILP. En las demás técnicas se reporta
    `cumple_autonomia` (no se fuerza).
  - Recompensa R(e): 200 si la arista incide en una estación SINCA con estado peor que
    "bueno". La parte "cono a sotavento de chimenea" de la especificación NO está implementada.
    Con los datos actuales ninguna estación está en alerta, así que R(e) = 0 en todo el grafo.
  - Buffers: se calculan con shapely en metros (proyección local). Equivale a
    ST_Buffer(geom::geography, 200) de PostGIS; no se ejecuta en la BD.
"""

import heapq
import json
import math
import os
import threading
import time
from pathlib import Path

try:
    from ruteo import simulacion_fallas as sf
except ImportError:  # ejecución como script desde dentro de ruteo/
    import simulacion_fallas as sf

RAIZ = sf.RAIZ
AUTONOMIA_M = 10500.0
BETA = 1000.0
RECOMPENSA_M = 200.0        # R(e) en metros equivalentes
COSTO_MIN = 1.0             # piso del costo compuesto (pgr_dijkstra no admite costos <= 0)
BUFFER_M = 200.0
FACTORES_P2 = (2.0, 4.0, 8.0, 16.0)
LAT0 = -32.8                # latitud de referencia para proyectar a metros

TECNICAS = {
    "dijkstra_distancia": {"nombre": "Dijkstra por distancia (pgr_dijkstra)", "color": "#1f77b4"},
    "milp_exacto": {"nombre": "Optimización exacta MILP", "color": "#2ca02c"},
    "dijkstra_multicriterio": {"nombre": "Dijkstra multicriterio con riesgo", "color": "#ff7f0e"},
    "metaheuristica_akgun": {"nombre": "Metaheurística Akgün (rutas disímiles)", "color": "#9467bd"},
}
_PRIORIDAD_EMPATE = ["metaheuristica_akgun", "milp_exacto", "dijkstra_multicriterio", "dijkstra_distancia"]


# ==============================================================================
# 1. RED Y CONTEXTO (se cargan una sola vez)
# ==============================================================================

class Red:
    """Nodos y aristas de la infraestructura con su geometría."""

    def __init__(self, nodos, aristas):
        self.coord, self.props_nodo, self.codigo_id = {}, {}, {}
        for f in nodos:
            p = f["properties"]
            self.coord[p["id"]] = tuple(f["geometry"]["coordinates"][:2])
            self.props_nodo[p["id"]] = p
            self.codigo_id[p["code"]] = p["id"]
        self.aristas = {}
        for f in aristas:
            p = f["properties"]
            self.aristas[p["id"]] = {"source": p["source"], "target": p["target"],
                                     "length_m": float(p["length_m"]),
                                     "coords": f["geometry"]["coordinates"]}
        self._geom_m = {}

    def coords_camino(self, camino):
        """Coordenadas [lon, lat] de la ruta, orientando cada arista en el sentido del viaje."""
        coords, actual = [], camino["nodos"][0]
        for eid in camino["aristas"]:
            a = self.aristas[eid]
            c = a["coords"] if a["source"] == actual else a["coords"][::-1]
            actual = a["target"] if a["source"] == actual else a["source"]
            coords.extend(c if not coords else c[1:])
        return [[float(p[0]), float(p[1])] for p in coords]

    def geom_m(self, eid):
        """LineString de la arista en metros (para buffers y solapes)."""
        g = self._geom_m.get(eid)
        if g is None:
            from shapely.geometry import LineString
            kx, ky = math.cos(math.radians(LAT0)) * 111320.0, 110540.0
            g = LineString([(p[0] * kx, p[1] * ky) for p in self.aristas[eid]["coords"]])
            self._geom_m[eid] = g
        return g

    def longitud_m(self, camino):
        return sum(self.aristas[e]["length_m"] for e in camino["aristas"])


class Contexto:
    """Datos cargados una vez + caché de modelos de fallas por conjunto de capas."""

    def __init__(self):
        self.datos = sf.cargar_infraestructura_y_capas()
        self.red = Red(self.datos[0], self.datos[1])
        self.recompensa = _recompensas(self.red)
        self._modelos = {}
        self._lock = threading.Lock()

    def modelo(self, capas=None):
        clave = frozenset(sf.CAPAS_POR_DEFECTO if capas is None else capas)
        with self._lock:
            if clave not in self._modelos:
                self._modelos[clave] = sf.construir_modelo_fallas(clave, datos=self.datos)
            return self._modelos[clave]

    def destinos(self):
        out = [p for p in self.red.props_nodo.values() if p.get("category") == "sinca"]
        return sorted(out, key=lambda p: p["name"])

    def origen_por_defecto(self):
        codigo = "base_scer"
        if sf.CONFIG_PATH.exists():
            with open(sf.CONFIG_PATH, encoding="utf-8") as f:
                codigo = json.load(f).get("algoritmo", {}).get("origen_default", codigo)
        return self.red.codigo_id[codigo]


def _recompensas(red):
    """R(e) = 200 en aristas incidentes a una estación SINCA con estado peor que 'bueno'."""
    en_alerta = set()
    for f in sf._leer("metadata/sinca_calidad_aire.geojson"):
        p = f["properties"]
        if p.get("node_code") in red.codigo_id and p.get("worst_status_code", 1) > 1:
            en_alerta.add(red.codigo_id[p["node_code"]])
    return {eid: RECOMPENSA_M for eid, a in red.aristas.items()
            if a["source"] in en_alerta or a["target"] in en_alerta}


# ==============================================================================
# 2. COSTOS Y ADMISIBILIDAD
# ==============================================================================

def aristas_admisibles(modelo):
    """a_ij = 1 salvo que la arista, o alguno de sus extremos, esté bloqueada (P = 1)."""
    return {eid for eid, e in modelo["aristas"].items()
            if not e["bloqueado"]
            and not modelo["nodos"][e["source"]]["bloqueado"]
            and not modelo["nodos"][e["target"]]["bloqueado"]}


def costos_distancia(red):
    return {eid: a["length_m"] for eid, a in red.aristas.items()}


def costos_compuestos(modelo, recompensa, beta, admisibles):
    """W(e) = max(L + beta*H - R, COSTO_MIN) con H = lambda * L_km, solo aristas admisibles."""
    out = {}
    for eid in admisibles:
        e = modelo["aristas"][eid]
        h = e["lambda"] * e["length_m"] / 1000.0
        out[eid] = max(e["length_m"] + beta * h - recompensa.get(eid, 0.0), COSTO_MIN)
    return out


# ==============================================================================
# 3. CAMINO MÍNIMO (Python o pgRouting)
# ==============================================================================

def _dijkstra(red, costos, origen, destino):
    adj = {}
    for eid, c in costos.items():
        a = red.aristas[eid]
        adj.setdefault(a["source"], []).append((a["target"], c, eid))
        adj.setdefault(a["target"], []).append((a["source"], c, eid))
    dist, prev, pq = {origen: 0.0}, {}, [(0.0, origen)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        if u == destino:
            break
        for v, c, eid in adj.get(u, ()):
            nd = d + c
            if nd < dist.get(v, math.inf):
                dist[v], prev[v] = nd, (u, eid)
                heapq.heappush(pq, (nd, v))
    if destino not in dist:
        return None
    nodos, aristas, cur = [destino], [], destino
    while cur != origen:
        cur, eid = prev[cur]
        nodos.append(cur)
        aristas.append(eid)
    return {"nodos": nodos[::-1], "aristas": aristas[::-1]}


def _pgr_dijkstra(costos, origen, destino):
    """pgr_dijkstra en PostgreSQL. El costo por arista se pasa como tabla VALUES, porque
    infra_edge no tiene columnas de riesgo. SIN PROBAR en el entorno de desarrollo."""
    from bd.conexion import conectar
    valores = ",".join(f"({int(eid)},{float(c)!r})" for eid, c in costos.items())
    if not valores:
        return None
    sql_aristas = ("SELECT e.id, e.source, e.target, v.c AS cost, v.c AS reverse_cost "
                   f"FROM infra_edge e JOIN (VALUES {valores}) AS v(id, c) ON v.id = e.id")
    sql = ("SELECT d.node, d.edge FROM pgr_dijkstra(%s::text, %s::bigint, %s::bigint, "
           "directed := false) AS d ORDER BY d.seq")
    with conectar() as conn, conn.cursor() as cur:
        cur.execute(sql, (sql_aristas, origen, destino))
        filas = cur.fetchall()
    if not filas:
        return None
    return {"nodos": [int(n) for n, _ in filas], "aristas": [int(e) for _, e in filas if e != -1]}


def _camino_minimo(red, costos, origen, destino, backend):
    """Devuelve (camino | None, backend_usado)."""
    if backend == "pgrouting":
        try:
            return _pgr_dijkstra(costos, origen, destino), "pgrouting"
        except Exception as exc:  # BD apagada, pgRouting ausente, etc.
            return (_dijkstra(red, costos, origen, destino),
                    f"python (pgrouting no disponible: {type(exc).__name__})")
    return _dijkstra(red, costos, origen, destino), "python"


# ==============================================================================
# 4. LAS CUATRO TÉCNICAS
# Cada una devuelve un dict: estado, motivo, backend, caminos, costo/objetivo y computo_ms.
# ==============================================================================

def _ok(caminos, backend, t0, **extra):
    return {"estado": "ok", "motivo": None, "backend": backend, "caminos": caminos,
            "computo_ms": (time.perf_counter() - t0) * 1000.0, **extra}


def _sin_ruta(motivo, backend, t0):
    return {"estado": "sin_ruta", "motivo": motivo, "backend": backend, "caminos": [],
            "computo_ms": (time.perf_counter() - t0) * 1000.0}


def tecnica_dijkstra_distancia(ctx, modelo, origen, destino, backend="python", **_):
    """Técnica 1: línea base. Solo longitud en metros; ignora bloqueos y amenazas."""
    t0 = time.perf_counter()
    camino, usado = _camino_minimo(ctx.red, costos_distancia(ctx.red), origen, destino, backend)
    if not camino:
        return _sin_ruta("sin_camino_en_la_red", usado, t0)
    return _ok([camino], usado, t0)


def tecnica_dijkstra_multicriterio(ctx, modelo, origen, destino, beta=BETA, backend="python", **_):
    """Técnica 3: pgr_dijkstra con W(e) = L + beta*H - R, excluyendo aristas bloqueadas."""
    t0 = time.perf_counter()
    costos = costos_compuestos(modelo, ctx.recompensa, beta, aristas_admisibles(modelo))
    camino, usado = _camino_minimo(ctx.red, costos, origen, destino, backend)
    if not camino:
        return _sin_ruta("destino_bloqueado_o_inalcanzable", usado, t0)
    return _ok([camino], usado, t0,
               costo=sum(costos[e] for e in camino["aristas"]))


ORDEN_SOLVERS = ("GUROBI", "CPLEX_PY", "CPLEX_CMD", "HiGHS", "PULP_CBC_CMD")


def _solvers_disponibles(limite_s=60):
    """Lista [(solver, nombre)] en orden de preferencia: GUROBI / CPLEX primero (requisito de la
    rúbrica) y HiGHS / CBC como respaldo. Se devuelven TODOS los disponibles, no solo el primero,
    porque un solver instalado puede fallar (p. ej. CPLEX Community Edition rechaza modelos con
    más de ~1000 variables/restricciones y PuLP lo reporta como \"Infeasible\")."""
    import pulp
    out = []
    for nombre in ORDEN_SOLVERS:
        cls = getattr(pulp, nombre, None)
        if cls is None:
            continue
        try:
            try:
                solver = cls(msg=False, timeLimit=limite_s)
            except TypeError:
                solver = cls(msg=False)
            if solver.available():
                out.append((solver, nombre))
        except Exception:
            continue
    if not out:
        raise RuntimeError("No hay ningún solver MILP disponible (instala highspy o gurobipy).")
    return out


def _elegir_solver(limite_s=60):
    """Primer solver disponible (se conserva por compatibilidad)."""
    return _solvers_disponibles(limite_s)[0]


def tecnica_milp(ctx, modelo, origen, destino, autonomia_m=AUTONOMIA_M, beta=BETA, **_):
    """Técnica 2: MILP exacto.

        min  sum_{(i,j)} W_ij x_ij
        s.a. sum_j x_sj - sum_j x_js = 1        (origen s)
             sum_j x_dj - sum_j x_jd = -1       (destino d)
             sum_j x_ij - sum_j x_ji = 0        (resto de nodos)
             sum_ij L_ij x_ij <= autonomia      (restriccion dura de energia)
             x_ij <= a_ij                       (solo arcos admisibles: se omiten los bloqueados)
             t_j >= t_i + 1 - N (1 - x_ij)      (MTZ: elimina subciclos)
             x_ij in {0,1}
    """
    t0 = time.perf_counter()
    red = ctx.red
    adm = aristas_admisibles(modelo)
    costos = costos_compuestos(modelo, ctx.recompensa, beta, adm)

    # Se restringe a la componente conexa del origen (reduce variables y MTZ).
    vecinos = {}
    for eid in adm:
        a = red.aristas[eid]
        vecinos.setdefault(a["source"], []).append(a["target"])
        vecinos.setdefault(a["target"], []).append(a["source"])
    visto, pila = {origen}, [origen]
    while pila:
        for v in vecinos.get(pila.pop(), ()):
            if v not in visto:
                visto.add(v)
                pila.append(v)
    if destino not in visto:
        return _sin_ruta("destino_bloqueado_o_inalcanzable", "milp", t0)

    # --- Verificación exacta de autonomía, independiente del solver -----------------------
    # Existe una ruta con L <= autonomía  <=>  el camino más corto por longitud la cumple.
    # Así "infactible por autonomía" lo decide un hecho verificable y no el estado que
    # reporte un solver (que puede fallar por licencia/tamaño y decir "Infeasible" sin ser cierto).
    corto = _dijkstra(red, {eid: red.aristas[eid]["length_m"] for eid in adm}, origen, destino)
    if corto is None:
        return _sin_ruta("sin_camino", "milp", t0)
    if red.longitud_m(corto) > autonomia_m:
        r = _sin_ruta("autonomia_insuficiente", "milp (verificación de autonomía)", t0)
        r["estado"] = "infactible"
        return r
    # Cota inferior del objetivo: sin la restricción de autonomía el mínimo es el de Dijkstra.
    ref = _dijkstra(red, costos, origen, destino)
    cota_inf = sum(costos[e] for e in ref["aristas"]) if ref else 0.0

    import pulp

    arcos = []  # (u, v, eid)
    for eid in adm:
        a = red.aristas[eid]
        if a["source"] in visto and a["target"] in visto:
            for u, v in ((a["source"], a["target"]), (a["target"], a["source"])):
                if v != origen and u != destino:
                    arcos.append((u, v, eid))

    prob = pulp.LpProblem("ruta_uav", pulp.LpMinimize)
    x = {k: pulp.LpVariable(f"x_{i}", cat="Binary") for i, k in enumerate(arcos)}
    t = {n: pulp.LpVariable(f"t_{n}", 0, len(visto)) for n in visto}
    prob += pulp.lpSum(costos[eid] * x[(u, v, eid)] for u, v, eid in arcos)

    salen, entran = {n: [] for n in visto}, {n: [] for n in visto}
    for k in arcos:
        salen[k[0]].append(x[k])
        entran[k[1]].append(x[k])
    for n in visto:
        balance = 1 if n == origen else (-1 if n == destino else 0)
        prob += pulp.lpSum(salen[n]) - pulp.lpSum(entran[n]) == balance
        prob += pulp.lpSum(entran[n]) <= 1
    prob += pulp.lpSum(red.aristas[eid]["length_m"] * x[(u, v, eid)] for u, v, eid in arcos) <= autonomia_m
    big_n = len(visto)
    for k in arcos:
        prob += t[k[1]] >= t[k[0]] + 1 - big_n * (1 - x[k])

    tamano = {"variables": prob.numVariables(), "restricciones": prob.numConstraints()}
    # --- Resolver probando solvers en orden hasta obtener una solución válida ------------
    descartados = []   # [(solver, motivo)]
    for solver, nombre_solver in _solvers_disponibles():
        try:
            prob.solve(solver)
        except Exception as exc:
            descartados.append((nombre_solver, f"excepcion_{type(exc).__name__}"))
            continue
        estado_pulp = pulp.LpStatus[prob.status]
        if estado_pulp != "Optimal":
            # Como la autonomía ya fue verificada, un "Infeasible" aquí es falla del solver.
            descartados.append((nombre_solver, f"estado_{estado_pulp}"))
            continue
        sucesor = {u: (v, eid) for (u, v, eid), var in x.items() if (var.value() or 0) > 0.5}
        nodos, aristas, cur = [origen], [], origen
        while cur != destino and cur in sucesor and len(nodos) <= big_n:
            cur, eid = sucesor[cur]
            nodos.append(cur)
            aristas.append(eid)
        if cur != destino:
            descartados.append((nombre_solver, "solucion_no_reconstruible"))
            continue
        camino = {"nodos": nodos, "aristas": aristas}
        valor = pulp.value(prob.objective)
        if red.longitud_m(camino) > autonomia_m + 1e-6 or valor < cota_inf - 1e-6:
            descartados.append((nombre_solver, "solucion_inconsistente"))
            continue
        return _ok([camino], nombre_solver, t0, costo=valor, solver=nombre_solver,
                   solvers_descartados=[{"solver": n, "motivo": m} for n, m in descartados],
                   modelo_tamano=tamano)

    r = _sin_ruta("ningun_solver_resolvio: " + ", ".join(f"{n}={m}" for n, m in descartados),
                  "milp", t0)
    r["estado"] = "error"
    r["solvers_descartados"] = [{"solver": n, "motivo": m} for n, m in descartados]
    r["modelo_tamano"] = tamano
    return r


def _union_buffer(red, eids):
    from shapely.ops import unary_union
    return unary_union([red.geom_m(e) for e in eids]).buffer(BUFFER_M)


def solape_buffers_pct(red, camino1, camino2):
    """Área(buffer1 ∩ buffer2) / área del menor buffer, en %. Equivale a
    ST_Area(ST_Intersection(ST_Buffer(g1,200), ST_Buffer(g2,200))) en PostGIS."""
    b1, b2 = _union_buffer(red, camino1["aristas"]), _union_buffer(red, camino2["aristas"])
    menor = min(b1.area, b2.area)
    return 100.0 * b1.intersection(b2).area / menor if menor > 0 else 0.0


def tecnica_akgun(ctx, modelo, origen, destino, autonomia_m=AUTONOMIA_M, beta=BETA,
                  backend="python", **_):
    """Técnica 4: par {P1*, P2*} (k = 2), adaptación de Akgün, Erkut y Batta (2000).

    P1* minimiza W(e). P2* se busca penalizando las aristas de P1* (x f) y, con menor
    intensidad, las que caen dentro del buffer de 200 m de P1* (para desacoplar el corredor
    geográfico). Se prueban varios factores f y se elige el candidato que cumple la autonomía
    y maximiza R(P1, P2); a igualdad, el de menor solape de buffers.
    """
    from shapely.prepared import prep
    t0 = time.perf_counter()
    red = ctx.red
    costos = costos_compuestos(modelo, ctx.recompensa, beta, aristas_admisibles(modelo))
    c1, usado = _camino_minimo(red, costos, origen, destino, backend)
    if not c1:
        return _sin_ruta("destino_bloqueado_o_inalcanzable", usado, t0)

    en_p1 = set(c1["aristas"])
    zona = prep(_union_buffer(red, c1["aristas"]))
    en_buffer = {eid for eid in costos if eid not in en_p1 and zona.intersects(red.geom_m(eid))}

    candidatos = {}
    for f in FACTORES_P2:
        pen = {eid: c * (f if eid in en_p1 else (1.0 + (f - 1.0) / 2.0 if eid in en_buffer else 1.0))
               for eid, c in costos.items()}
        c2, _ = _camino_minimo(red, pen, origen, destino, backend)
        if c2 and c2["aristas"] != c1["aristas"]:
            candidatos[tuple(c2["aristas"])] = c2
    validos = [c for c in candidatos.values() if red.longitud_m(c) <= autonomia_m]

    if not validos:
        # Sin segundo camino viable se devuelve UNO solo. Antes se duplicaba c1, lo que
        # hacia que la leyenda anunciara "2 caminos" siendo el mismo trazado.
        motivo = "sin_alternativa" if not candidatos else "alternativas_exceden_autonomia"
        return _ok([c1], usado, t0, advertencia=motivo, solape_pct=100.0,
                   diversidad_pct=0.0, costo=sum(costos[e] for e in c1["aristas"]))

    mejor, mejor_clave = None, None
    for c2 in validos:
        r = sf.resiliencia_par(modelo, c1, c2)
        solape = solape_buffers_pct(red, c1, c2)
        clave = (round(r, 12), -solape)
        if mejor_clave is None or clave > mejor_clave:
            mejor, mejor_clave = (c2, solape), clave
    c2, solape = mejor
    union = set(c1["aristas"]) | set(c2["aristas"])
    comunes = set(c1["aristas"]) & set(c2["aristas"])
    return _ok([c1, c2], usado, t0, solape_pct=solape,
               diversidad_pct=100.0 * (1 - len(comunes) / len(union)),
               costo=sum(costos[e] for e in c1["aristas"]))


# ==============================================================================
# 5. ORQUESTACIÓN: ejecuta las 4 técnicas y calcula las métricas comunes
# ==============================================================================

def _metricas_camino(ctx, modelo, camino):
    red, aristas = ctx.red, camino["aristas"]
    total = red.longitud_m(camino) or 1.0
    densas = sum(red.aristas[e]["length_m"] for e in aristas if "densidad" in modelo["aristas"][e]["factores"])
    sin_c2 = sum(red.aristas[e]["length_m"] for e in aristas if "sin_c2" in modelo["aristas"][e]["factores"])
    bloqueos = (sum(modelo["aristas"][e]["bloqueado"] for e in aristas)
                + sum(modelo["nodos"][n]["bloqueado"] for n in camino["nodos"]))
    return {"pct_densas": 100.0 * densas / total, "pct_sin_c2": 100.0 * sin_c2 / total,
            "bloqueos_en_ruta": int(bloqueos)}


def ejecutar_tecnicas(ctx, origen_id, destino_id, autonomia_m=AUTONOMIA_M, beta=BETA,
                      capas=None, backend=None, mc_n=0, seed=None):
    """Corre las 4 técnicas. Devuelve un dict serializable a JSON."""
    backend = backend or os.getenv("RUTEO_BACKEND", "python")
    t0 = time.perf_counter()
    modelo = ctx.modelo(capas)
    modelo_ms = (time.perf_counter() - t0) * 1000.0

    funciones = {"dijkstra_distancia": tecnica_dijkstra_distancia, "milp_exacto": tecnica_milp,
                 "dijkstra_multicriterio": tecnica_dijkstra_multicriterio,
                 "metaheuristica_akgun": tecnica_akgun}
    resultados = {}
    for tid, fn in funciones.items():
        r = fn(ctx, modelo, origen_id, destino_id, autonomia_m=autonomia_m, beta=beta, backend=backend)
        r.update({"id": tid, **TECNICAS[tid]})
        if r["estado"] == "ok":
            for i, c in enumerate(r["caminos"]):
                c["rol"] = "principal" if i == 0 else "alternativa"
                c["longitud_m"] = ctx.red.longitud_m(c)
                c["geometria"] = ctx.red.coords_camino(c)
            principal = r["caminos"][0]
            r["longitud_km"] = principal["longitud_m"] / 1000.0
            r["cumple_autonomia"] = principal["longitud_m"] <= autonomia_m
            r["resiliencia_R"] = sf.resiliencia_tecnica(modelo, r["caminos"])
            r.update(_metricas_camino(ctx, modelo, principal))
            r["viable"] = r["bloqueos_en_ruta"] == 0 and r["cumple_autonomia"]
        resultados[tid] = r

    if mc_n > 0:
        mc = sf.monte_carlo_supervivencia(
            modelo, {t: r["caminos"] for t, r in resultados.items() if r["estado"] == "ok"},
            n=mc_n, seed=seed)
        for t, pct in mc.items():
            resultados[t]["supervivencia_mc_pct"] = pct

    # La "más resiliente" se elige entre las rutas viables (sin bloqueos y dentro de la autonomía).
    con_r = [t for t in _PRIORIDAD_EMPATE if resultados[t]["estado"] == "ok" and resultados[t]["viable"]]
    mejor = max(con_r, key=lambda t: round(resultados[t]["resiliencia_R"], 9)) if con_r else None
    return {
        "parametros": {"origen_id": origen_id, "destino_id": destino_id, "autonomia_max_m": autonomia_m,
                       "beta": beta, "backend": backend, "mc_n": mc_n, "seed": seed},
        "capas_activas": modelo["meta"]["capas_activas"],
        "modelo_ms": modelo_ms,
        "tecnicas": resultados,
        "mejor_resiliencia": mejor,
    }


def a_geojson(salida, ctx):
    """FeatureCollection con una LineString por camino (para pintar directamente en Leaflet)."""
    feats = []
    for tid, r in salida["tecnicas"].items():
        for c in r.get("caminos", []):
            feats.append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": c["geometria"]},
                "properties": {
                    "tecnica": tid, "nombre": r["nombre"], "color": r["color"], "rol": c["rol"],
                    "longitud_km": round(c["longitud_m"] / 1000.0, 3),
                    "computo_ms": round(r["computo_ms"], 2),
                    "resiliencia_R": round(r["resiliencia_R"], 4),
                    "mejor_resiliencia": tid == salida["mejor_resiliencia"],
                    "viable": r["viable"], "nodos": c["nodos"], "aristas": c["aristas"],
                },
            })
    return {"type": "FeatureCollection", "features": feats}
