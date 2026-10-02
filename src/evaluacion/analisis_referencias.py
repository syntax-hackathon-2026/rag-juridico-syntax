"""Fase 0 y comparacion keep/revert del lookup; solo lectura de datos versionados."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from recuperacion.consulta import consulta_de
from recuperacion.referencias import referencias_de
sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl


def acierto(fila: dict, campo: str) -> bool:
    r = fila.get(campo)
    return r is not None and 1 <= r <= 10


def fase0(items: list[dict], baseline: list[dict]) -> dict:
    por_id = {f["id"]: f for f in baseline}
    salida = {}
    for fuente in ("pregunta", "pregunta+opciones"):
        detalles = []
        for it in items:
            refs = referencias_de(consulta_de(it, fuente))
            f = por_id.get(it["id"])
            detalles.append({"id": it["id"], "referencias": [list(r) for r in refs],
                             "con_cuerpo": bool(refs), "con_articulo": any(r[3] is not None for r in refs),
                             "evaluacion_disponible": f is not None,
                             "rank_art_baseline": f.get("rank_art") if f else None,
                             "gt_con_articulo": bool(f and f["referencia_articulos"])})
        fallos = [d["id"] for d in detalles if d["con_cuerpo"] and d["evaluacion_disponible"]
                  and d["gt_con_articulo"] and not (d["rank_art_baseline"] and d["rank_art_baseline"] <= 10)]
        salida[fuente] = {"n_items": len(items), "n_con_cuerpo": sum(d["con_cuerpo"] for d in detalles),
                          "n_con_articulo": sum(d["con_articulo"] for d in detalles),
                          "n_evaluables_con_cuerpo_y_articulo_gt": sum(d["con_cuerpo"] and d["gt_con_articulo"] for d in detalles),
                          "n_evaluables_con_articulo_explicito_y_gt": sum(d["con_articulo"] and d["gt_con_articulo"] for d in detalles),
                          "ids_con_referencia_sin_baseline": [d["id"] for d in detalles if d["con_cuerpo"] and not d["evaluacion_disponible"]],
                          "ids_fallos_art_con_referencia": fallos,
                          "prueba_de_concepto": len(fallos) < 3, "detalle": detalles}
    return salida


def comparar(base: list[dict], candidato: list[dict]) -> dict:
    a = {f["id"]: f for f in base}
    b = {f["id"]: f for f in candidato}
    if len(a) != len(base) or len(b) != len(candidato) or a.keys() != b.keys():
        raise ValueError("A/B requiere IDs unicos y el mismo conjunto evaluable")
    for i in a:
        if a[i]["referencia"] != b[i]["referencia"] or a[i]["referencia_articulos"] != b[i]["referencia_articulos"]:
            raise ValueError("A/B requiere los mismos fundamentos de evaluacion")
        if "referencias_explicitas" not in b[i]:
            raise ValueError("Candidato sin reporte de referencias explicitas")
    ganancias = sorted(i for i in a if b[i]["referencias_explicitas"] and
                       not acierto(a[i], "rank_art") and acierto(b[i], "rank_art"))
    perdidas_doc = sorted(i for i in a if acierto(a[i], "rank_doc") and not acierto(b[i], "rank_doc"))
    perdidas_art = sorted(i for i in a if acierto(a[i], "rank_art") and not acierto(b[i], "rank_art"))
    def metricas(grupo):
        n = len(grupo)
        return {"n": n, "doc_hit@10": sum(acierto(f, "rank_doc") for f in grupo) / n if n else None,
                "mrr": sum(1 / f["rank_doc"] for f in grupo if acierto(f, "rank_doc")) / n if n else None}
    resto = [i for i in a if not b[i]["referencias_explicitas"]]
    control_a = metricas([a[i] for i in resto])
    control_b = metricas([b[i] for i in resto])
    control_mrr = not resto or control_b["mrr"] >= control_a["mrr"]
    return {"ganancias_art_exp": ganancias, "perdidas_doc": perdidas_doc, "perdidas_art": perdidas_art,
            "control_resto_baseline": control_a,
            "control_resto_candidato": control_b,
            "keep_segun_conteos": len(ganancias) >= 2 and not perdidas_doc and not perdidas_art and control_mrr,
            "nota": "Conteos de calidad; revisar latencia y control MRR antes de adoptar. No activa flags."}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", type=Path, default=config.REFERENCIAS_BASELINE_PATH)
    ap.add_argument("--comparar", type=Path, help="detalle de una variante para comparar contra baseline")
    args = ap.parse_args()
    base = read_jsonl(args.baseline)
    resultado = comparar(base, read_jsonl(args.comparar)) if args.comparar else fase0(read_jsonl(config.SAMPLE_PATH), base)
    print(json.dumps({"baseline": args.baseline.relative_to(config.ROOT).as_posix() if args.baseline.is_relative_to(config.ROOT) else args.baseline.name,
                      "baseline_sha256": hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
                      "resultado": resultado}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
