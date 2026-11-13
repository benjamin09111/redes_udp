"""API del ruteo resiliente (Fase 3) + servidor del sitio web.

Levantar desde la raíz del repo:
    uvicorn api.servidor:app --host 0.0.0.0 --port 8000
o  python3 api/servidor.py

Endpoints (formato detallado en api/CONTRATO_API.md):
    GET /api/salud          estado del servicio
    GET /api/destinos       origen por defecto y destinos (estaciones SINCA)
    GET /api/capas          capas de amenaza que se pueden activar/desactivar
    GET /api/rutas          corre las 4 técnicas y devuelve GeoJSON + métricas
    GET /api/simulacion     Monte Carlo (u ~ U[0,100)) sobre las rutas calculadas
    /sitio_web/             el sitio Leaflet (archivos estáticos)
"""
import secrets
import sys
import threading
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from ruteo import simulacion_fallas as sf  # noqa: E402
from ruteo import tecnicas as tec  # noqa: E402

app = FastAPI(title="Ruteo resiliente UAV - Fase 3", version="1.0")

DESCRIPCION_CAPAS = {
    "incendio": "Incendios FIRMS (λ = 5,0)",
    "sismo": "Alertas sísmicas CSN (λ = 0,05)",
    "viento": "Viento (> 12 m/s bloquea; ≥ 8 m/s λ = 0,04)",
    "lluvia": "Lluvia intensa (λ = 0,03)",
    "niebla": "Niebla (visibilidad < 1000 m bloquea)",
    "humedad": "Humedad relativa > 90 % (λ = 0,03)",
    "densidad": "Manzanas censales densas > 2500 hab/km² (λ = 0,08)",
    "c2": "Sombra de enlace C2 (λ = 0,05)",
    "obstaculos": "Obstáculos verticales: chimeneas y torres (λ = 0,20 en el radio de resguardo; más altas que el techo de 120 m AGL bloquean)",
    "relieve": "Relieve SRTM (λ = 0,06 por cada 100 m de ascenso; bloquea si el terreno no cabe en la ventana de 120 m AGL)",
    "contingencia": "Contingencia simulada: incendio Planta de Asfaltos Quintero",
}

_ctx = None
_ctx_lock = threading.Lock()


def contexto() -> tec.Contexto:
    """Carga única de la red y las capas (tarda ~1 s la primera vez)."""
    global _ctx
    with _ctx_lock:
        if _ctx is None:
            _ctx = tec.Contexto()
        return _ctx


def _parsear_capas(capas: Optional[str], contingencia: bool) -> tuple:
    if capas is None:
        activas = set(sf.CAPAS_POR_DEFECTO)
    else:
        activas = {c.strip() for c in capas.split(",") if c.strip()}
        invalidas = activas - sf.CAPAS_TODAS
        if invalidas:
            raise HTTPException(422, f"Capas desconocidas: {sorted(invalidas)}. "
                                     f"Válidas: {sorted(sf.CAPAS_TODAS)}")
    if contingencia:
        activas.add("contingencia")
    return tuple(sorted(activas))


def _resolver_nodos(origen_id, destino_id, destino):
    c = contexto()
    if origen_id is None:
        origen_id = c.origen_por_defecto()
    if destino_id is None and destino is not None:
        destino_id = c.red.codigo_id.get(destino)
    if destino_id is None:
        raise HTTPException(422, "Indica destino_id o destino (código, ej. sinca_quintero).")
    for nombre, nid in (("origen_id", origen_id), ("destino_id", destino_id)):
        if nid not in c.red.coord:
            raise HTTPException(404, f"{nombre}={nid} no existe en la red.")
    if origen_id == destino_id:
        raise HTTPException(422, "El origen y el destino no pueden ser el mismo nodo.")
    return origen_id, destino_id


@lru_cache(maxsize=64)
def _calcular(origen, destino, autonomia, beta, capas, backend, mc_n, seed):
    return tec.ejecutar_tecnicas(contexto(), origen, destino, autonomia_m=autonomia, beta=beta,
                                 capas=set(capas), backend=backend, mc_n=mc_n, seed=seed)


def _resumen(salida):
    """Métricas por técnica sin las geometrías (esas van en los features)."""
    out = {}
    for tid, r in salida["tecnicas"].items():
        d = {k: v for k, v in r.items() if k != "caminos"}
        d["n_caminos"] = len(r.get("caminos", []))
        out[tid] = d
    return out


@app.get("/api/salud")
def salud():
    return {"estado": "ok", "backend_por_defecto": __import__("os").getenv("RUTEO_BACKEND", "python")}


@app.get("/api/destinos")
def destinos():
    c = contexto()
    nodo = lambda p: {"id": p["id"], "code": p["code"], "name": p["name"],  # noqa: E731
                      "lon": c.red.coord[p["id"]][0], "lat": c.red.coord[p["id"]][1]}
    return {"origen": nodo(c.red.props_nodo[c.origen_por_defecto()]),
            "destinos": [nodo(p) for p in c.destinos()]}


@app.get("/api/capas")
def capas_disponibles():
    return {"por_defecto": sorted(sf.CAPAS_POR_DEFECTO),
            "capas": [{"id": k, "descripcion": v} for k, v in DESCRIPCION_CAPAS.items()]}


@app.get("/api/rutas")
def rutas(
    destino_id: Optional[int] = None,
    destino: Optional[str] = Query(None, description="Código del nodo destino, ej. sinca_quintero"),
    origen_id: Optional[int] = None,
    autonomia_max: float = Query(tec.AUTONOMIA_M, gt=0, le=100000, description="Autonomía máxima en metros"),
    beta: float = Query(tec.BETA, ge=0, description="Factor de aversión al riesgo"),
    capas: Optional[str] = Query(None, description="Capas activas separadas por coma"),
    contingencia: bool = False,
    backend: Optional[Literal["python", "pgrouting"]] = None,
    mc_n: int = Query(0, ge=0, le=20000, description="Realizaciones Monte Carlo para % de supervivencia"),
    seed: Optional[int] = None,
):
    o, d = _resolver_nodos(origen_id, destino_id, destino)
    activas = _parsear_capas(capas, contingencia)
    salida = _calcular(o, d, autonomia_max, beta, activas, backend, mc_n, seed)
    geo = tec.a_geojson(salida, contexto())
    geo.update({"parametros": salida["parametros"], "capas_activas": salida["capas_activas"],
                "modelo_ms": round(salida["modelo_ms"], 1), "mejor_resiliencia": salida["mejor_resiliencia"],
                "tecnicas": _resumen(salida)})
    return geo


@app.get("/api/simulacion")
def simulacion(
    destino_id: Optional[int] = None,
    destino: Optional[str] = None,
    origen_id: Optional[int] = None,
    autonomia_max: float = Query(tec.AUTONOMIA_M, gt=0, le=100000),
    beta: float = Query(tec.BETA, ge=0),
    capas: Optional[str] = None,
    contingencia: bool = False,
    backend: Optional[Literal["python", "pgrouting"]] = None,
    seed: Optional[int] = Query(None, description="Semilla; si falta se sortea y se devuelve"),
):
    """Una realización Monte Carlo: u ~ U[0,100) por nodo y arista; falla si u < P·100."""
    o, d = _resolver_nodos(origen_id, destino_id, destino)
    activas = _parsear_capas(capas, contingencia)
    salida = _calcular(o, d, autonomia_max, beta, activas, backend, 0, None)
    c = contexto()
    modelo = c.modelo(set(activas))
    semilla = seed if seed is not None else secrets.randbelow(2 ** 31)

    caminos = {t: r["caminos"] for t, r in salida["tecnicas"].items() if r["estado"] == "ok"}
    real, sobreviven = sf.evaluar_simulacion(modelo, caminos, seed=semilla)

    feats = []
    for eid in real["aristas_caidas"]:
        a = c.red.aristas[eid]
        feats.append({"type": "Feature",
                      "geometry": {"type": "LineString", "coordinates": [list(p[:2]) for p in a["coords"]]},
                      "properties": {"tipo": "arista", "id": eid, "p_falla": round(modelo["aristas"][eid]["p_falla"], 4),
                                     "u": round(real["u_aristas"][eid], 3),
                                     "bloqueada": modelo["aristas"][eid]["bloqueado"]}})
    for nid in real["nodos_caidos"]:
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": list(c.red.coord[nid])},
                      "properties": {"tipo": "nodo", "id": nid, "p_falla": round(modelo["nodos"][nid]["p_falla"], 4),
                                     "u": round(real["u_nodos"][nid], 3),
                                     "bloqueado": modelo["nodos"][nid]["bloqueado"]}})

    por_tecnica = {}
    for tid, r in salida["tecnicas"].items():
        if r["estado"] != "ok":
            por_tecnica[tid] = {"sobrevive": None, "texto": "Sin ruta", "estado": r["estado"]}
        else:
            ok = sobreviven[tid]
            por_tecnica[tid] = {"sobrevive": ok, "texto": "Sobrevivió" if ok else "Falló", "estado": "ok"}
    return {"type": "FeatureCollection", "features": feats, "seed": semilla,
            "n_aristas_caidas": len(real["aristas_caidas"]), "n_nodos_caidos": len(real["nodos_caidos"]),
            "tecnicas": por_tecnica, "capas_activas": list(activas)}


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse("/sitio_web/")


app.mount("/sitio_web", StaticFiles(directory=str(RAIZ / "sitio_web"), html=True), name="sitio_web")

# El sitio pide los GeoJSON y los scripts del ETL con rutas relativas (../infraestructura/...,
# ../amenazas/..., ../config/...). Este montaje al final sirve el resto del repo; va después de
# las rutas /api y de la raíz, así que no las tapa.
app.mount("/", StaticFiles(directory=str(RAIZ)), name="repo")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
