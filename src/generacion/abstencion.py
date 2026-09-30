"""Abstencion: regla v0 y senales para calibrarla despues.

Por que casi nunca se abstiene (scripts/evaluate.py): abstenerse vale 0,5 en el
componente de abstencion (10 pts), pero 0 en exactitud de cerradas y 0 en RAGAS (las
abstenciones no se juzgan y cuentan como cero), y 0 en citacion. Con respaldo@10 ~0,9
responder es casi siempre mejor. La regla v0 solo se abstiene cuando no hay nada que
entregar con garantias:

  - sin_pasajes:          la recuperacion no devolvio nada.
  - salida_invalida:      el decoder no produjo un JSON util tras reintentar.
  - citas_irreparables:   quitar las citas sin respaldo deja vacio un campo obligatorio.

Las senales se registran en cada traza para elegir despues una regla simple con
datos (CLAUDE.md: no ajustar umbrales finos a 50 muestras).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generacion import citas  # noqa: E402


def senales(consulta: str, top: list, perm: set) -> dict:
    """Senales de suficiencia de la evidencia. `top`: RetrievedChunk del top-10."""
    if not top:
        return {"n_pasajes": 0}
    scores = [p.score for p in top]
    en_ambas = [p for p in top if p.meta.get("rank_bm25") and p.meta.get("rank_denso")]
    explicitas = citas.cuerpos(consulta)
    return {
        "n_pasajes": len(top),
        "score_top1": round(scores[0], 6),
        "margen_top1_top2": round(scores[0] - scores[1], 6) if len(scores) > 1 else None,
        "top1_rank_bm25": top[0].meta.get("rank_bm25"),
        "top1_rank_denso": top[0].meta.get("rank_denso"),
        "frac_en_ambas_ramas": round(len(en_ambas) / len(top), 3),
        "n_cuerpos_top10": len({tuple(p.meta.get("canonico") or ()) for p in top}),
        "n_sentencias_top10": sum(p.meta.get("tipo") == "sentencia" for p in top),
        "normas_en_pregunta": sorted(map(list, explicitas), key=str),
        "normas_pregunta_en_evidencia": len(explicitas & perm),
    }


def decidir(motivos: list[str]) -> bool:
    return bool(motivos)
