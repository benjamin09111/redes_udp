"""Genera sitio_web/data/resumen_fase3.json para la Tabla 7 del paper.

Para cada destino SINCA corre las 4 técnicas y registra longitud, tiempo de cómputo,
% de ruta en zonas densas / sin cobertura C2, resiliencia analítica R y supervivencia
Monte Carlo. Incluye el escenario base y el de contingencia (Planta de Asfaltos).

    python3 ruteo/exportar_resumen_fase3.py                 # N = 2000, semilla 42
    python3 ruteo/exportar_resumen_fase3.py --mc-n 5000 --seed 7

Formato: ver api/CONTRATO_API.md. Los destinos sin ruta (p. ej. por bloqueo de niebla)
quedan con estado "sin_ruta" y valores null.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from ruteo import simulacion_fallas as sf  # noqa: E402
from ruteo import tecnicas as tec  # noqa: E402

CLAVES = ("dijkstra_distancia", "milp_exacto", "dijkstra_multicriterio", "metaheuristica_akgun")


def _redondear(x, n):
    return None if x is None else round(x, n)


def _entrada_tecnica(r):
    if r["estado"] != "ok":
        return {"estado": r["estado"], "motivo": r["motivo"], "longitud_km": None, "computo_ms": _redondear(r["computo_ms"], 1),
                "pct_densas": None, "pct_sin_c2": None, "resiliencia_R": None, "supervivencia_mc_pct": None}
    return {"estado": "ok", "motivo": r.get("advertencia"), "backend": r["backend"],
            "longitud_km": _redondear(r["longitud_km"], 2), "computo_ms": _redondear(r["computo_ms"], 1),
            "pct_densas": _redondear(r["pct_densas"], 1), "pct_sin_c2": _redondear(r["pct_sin_c2"], 1),
            "resiliencia_R": _redondear(r["resiliencia_R"], 3),
            "supervivencia_mc_pct": _redondear(r.get("supervivencia_mc_pct"), 1),
            "viable": r["viable"], "cumple_autonomia": r["cumple_autonomia"],
            "bloqueos_en_ruta": r["bloqueos_en_ruta"]}


def construir(ctx, capas, mc_n, seed, autonomia_m, beta, backend):
    origen = ctx.origen_por_defecto()
    destinos = []
    for d in ctx.destinos():
        s = tec.ejecutar_tecnicas(ctx, origen, d["id"], autonomia_m=autonomia_m, beta=beta,
                                  capas=capas, backend=backend, mc_n=mc_n, seed=seed)
        destinos.append({
            "nombre": d["name"].replace("Estación SINCA ", ""), "codigo": d["code"], "node_id": d["id"],
            "mejor_resiliencia": s["mejor_resiliencia"],
            "tecnicas": {k: _entrada_tecnica(s["tecnicas"][k]) for k in CLAVES},
        })
    return destinos


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mc-n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--autonomia", type=float, default=tec.AUTONOMIA_M)
    ap.add_argument("--beta", type=float, default=tec.BETA)
    ap.add_argument("--backend", choices=["python", "pgrouting"], default="python")
    ap.add_argument("--salida", default="sitio_web/data/resumen_fase3.json")
    args = ap.parse_args()

    ctx = tec.Contexto()
    base = construir(ctx, sf.CAPAS_POR_DEFECTO, args.mc_n, args.seed, args.autonomia, args.beta, args.backend)
    cont = construir(ctx, sf.CAPAS_POR_DEFECTO | {"contingencia"}, args.mc_n, args.seed, args.autonomia,
                     args.beta, args.backend)
    salida = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "parametros": {"autonomia_max_m": args.autonomia, "beta": args.beta, "mc_n": args.mc_n,
                       "seed": args.seed, "backend": args.backend, "origen": "base_scer",
                       "capas_base": sorted(sf.CAPAS_POR_DEFECTO)},
        "destinos": base,
        "contingencia": {"descripcion": "Incendio simulado en Planta de Asfaltos Quintero (foco de 180 m)",
                         "destinos": cont},
    }
    destino = RAIZ / args.salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"Escrito {destino}")
    for etiqueta, lista in (("BASE", base), ("CONTINGENCIA", cont)):
        print(f"\n[{etiqueta}]  R analítica por técnica (dist / MILP / multicrit / Akgün)")
        for d in lista:
            fila = []
            for k in CLAVES:
                r = d["tecnicas"][k]["resiliencia_R"]
                fila.append("  --  " if r is None else f"{r:6.3f}")
            print(f"  {d['nombre']:16s}", " ".join(fila), "|", d["mejor_resiliencia"])


if __name__ == "__main__":
    main()
