"""Pruebas del backend de la Fase 3 (técnicas de ruteo, modelo de fallas y API).

    python3 tests/test_fase3.py          (o: pytest tests/test_fase3.py)
Necesita: pulp, shapely, fastapi, httpx (ver requirements.txt). No requiere la BD.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from ruteo import simulacion_fallas as sf  # noqa: E402
from ruteo import tecnicas as tec  # noqa: E402

_CTX = tec.Contexto()
_ORIGEN = _CTX.origen_por_defecto()
_DEST = {d["code"]: d["id"] for d in _CTX.destinos()}


def _correr(codigo, **kw):
    return tec.ejecutar_tecnicas(_CTX, _ORIGEN, _DEST[codigo], **kw)


def test_milp_y_multicriterio_tienen_el_mismo_costo():
    for codigo in ("sinca_quintero", "sinca_la_greda", "sinca_ventanas"):
        t = _correr(codigo)["tecnicas"]
        assert abs(t["milp_exacto"]["costo"] - t["dijkstra_multicriterio"]["costo"]) < 1e-3, codigo


def test_milp_respeta_la_autonomia():
    r = _correr("sinca_ventanas", autonomia_m=5000)["tecnicas"]["milp_exacto"]
    assert r["estado"] == "infactible" and r["motivo"] == "autonomia_insuficiente"
    r = _correr("sinca_ventanas")["tecnicas"]["milp_exacto"]
    assert r["estado"] == "ok" and r["caminos"][0]["longitud_m"] <= tec.AUTONOMIA_M


def test_milp_prueba_el_siguiente_solver_si_uno_falla():
    """Regresión: CPLEX Community Edition devuelve 'Infeasible' en modelos grandes. Eso no debe
    leerse como 'autonomía insuficiente': hay que seguir con el siguiente solver."""
    import pulp

    class SolverRoto(pulp.LpSolver):
        def available(self):
            return True

        def actualSolve(self, lp, **kwargs):
            lp.status = pulp.LpStatusInfeasible
            return lp.status

    original = tec._solvers_disponibles
    reales = original()
    tec._solvers_disponibles = lambda limite_s=60: [(SolverRoto(), "ROTO")] + reales
    try:
        r = _correr("sinca_ventanas")["tecnicas"]["milp_exacto"]
    finally:
        tec._solvers_disponibles = original
    assert r["estado"] == "ok", r.get("motivo")
    assert r["solver"] != "ROTO"
    assert r["solvers_descartados"][0] == {"solver": "ROTO", "motivo": "estado_Infeasible"}


def test_tecnicas_con_riesgo_evitan_bloqueos_y_la_base_no():
    s = _correr("sinca_ventanas")["tecnicas"]
    for t in ("milp_exacto", "dijkstra_multicriterio", "metaheuristica_akgun"):
        assert s[t]["bloqueos_en_ruta"] == 0
    base = _correr("sinca_campiche")["tecnicas"]            # niebla bloquea el camino
    assert base["dijkstra_distancia"]["bloqueos_en_ruta"] > 0
    assert base["dijkstra_distancia"]["resiliencia_R"] == 0.0
    assert base["dijkstra_multicriterio"]["estado"] == "sin_ruta"


def test_desactivar_niebla_habilita_destinos_bloqueados():
    capas = sf.CAPAS_POR_DEFECTO - {"niebla"}
    s = _correr("sinca_campiche", capas=capas)["tecnicas"]
    assert all(s[t]["estado"] == "ok" for t in tec.TECNICAS)


def test_akgun_nunca_es_menos_resiliente_que_su_ruta_principal():
    for codigo in ("sinca_quintero", "sinca_sur", "sinca_loncura"):
        t = _correr(codigo)["tecnicas"]
        assert t["metaheuristica_akgun"]["resiliencia_R"] >= t["dijkstra_multicriterio"]["resiliencia_R"] - 1e-9


def test_contingencia_hace_colapsar_a_dijkstra_base():
    s = _correr("sinca_la_greda", capas=sf.CAPAS_POR_DEFECTO | {"contingencia"})["tecnicas"]
    assert s["dijkstra_distancia"]["resiliencia_R"] < 0.01
    assert s["milp_exacto"]["resiliencia_R"] > 0.1
    assert s["milp_exacto"]["longitud_km"] > s["dijkstra_distancia"]["longitud_km"]   # desvío


def test_monte_carlo_converge_a_la_resiliencia_analitica():
    s = _correr("sinca_quintero", mc_n=5000, seed=11)["tecnicas"]
    for t in tec.TECNICAS:
        assert abs(s[t]["supervivencia_mc_pct"] / 100 - s[t]["resiliencia_R"]) < 0.03, t


def test_api():
    from fastapi.testclient import TestClient
    from api.servidor import app
    c = TestClient(app)
    assert c.get("/api/salud").json()["estado"] == "ok"
    r = c.get("/api/rutas", params={"destino": "sinca_quintero"}).json()
    assert r["type"] == "FeatureCollection" and len(r["features"]) == 5      # 4 técnicas, Akgün con 2 caminos
    assert set(r["tecnicas"]) == set(tec.TECNICAS) and r["mejor_resiliencia"]
    s1 = c.get("/api/simulacion", params={"destino": "sinca_quintero", "seed": 3}).json()
    s2 = c.get("/api/simulacion", params={"destino": "sinca_quintero", "seed": 3}).json()
    assert s1["n_aristas_caidas"] == s2["n_aristas_caidas"]                  # misma semilla, misma realización
    assert c.get("/api/rutas").status_code == 422
    assert c.get("/api/rutas?destino_id=99999").status_code == 404
    assert c.get("/api/rutas?destino=sinca_loncura&capas=foo").status_code == 422


if __name__ == "__main__":
    fallos = 0
    for nombre, fn in sorted((n, f) for n, f in globals().items() if n.startswith("test_")):
        try:
            fn()
            print("OK    ", nombre)
        except Exception as e:
            fallos += 1
            print("FALLA ", nombre, type(e).__name__, e)
    sys.exit(1 if fallos else 0)
