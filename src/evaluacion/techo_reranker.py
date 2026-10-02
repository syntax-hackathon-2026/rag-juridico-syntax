"""Metricas offline del techo top-40 del plan 05, sin modelos."""
from __future__ import annotations


def metricas_techo(filas: list[dict]) -> dict:
    if not filas:
        raise ValueError("No hay preguntas evaluables")
    con_art = [f for f in filas if f["referencia_articulos"]]
    def hit(campo, registros, k):
        return (sum(f.get(campo) is not None and 1 <= f[campo] <= k
                    for f in registros) / len(registros)) if registros else None
    rangos = {"1-5": [], "6-10": [], "11-20": [], "21-40": [], "fuera": []}
    for f in con_art:
        r = f.get("rank_art")
        categoria = next((nombre for nombre, a, b in
                          (("1-5", 1, 5), ("6-10", 6, 10), ("11-20", 11, 20), ("21-40", 21, 40))
                          if r is not None and a <= r <= b), "fuera")
        rangos[categoria].append(f["id"])
    ganancia = len(rangos["11-20"]) + len(rangos["21-40"])
    pp = ganancia / len(con_art) * 100 if con_art else None
    return {
        "art_hit@20": hit("rank_art", con_art, 20),
        "art_hit@40": hit("rank_art", con_art, 40),
        "doc_hit@40": hit("rank_doc", filas, 40),
        "mrr@40": sum(1 / f["rank_doc"] for f in filas
                      if f.get("rank_doc") and f["rank_doc"] <= 40) / len(filas),
        "distribucion_rank_art": {k: len(v) for k, v in rangos.items()},
        "ids_por_rango_art": rangos,
        "techo_ganancia_preguntas": ganancia,
        "techo_ganancia_pp": pp,
        # OR literal del plan; continuar no significa activar por defecto.
        "continuacion_fase1": bool(con_art and (ganancia >= 4 or pp >= 8)),
        "n_con_articulo_techo": len(con_art),
    }
