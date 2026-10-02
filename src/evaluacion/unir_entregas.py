"""Une las particiones de una corrida (main.py --particion I/N en varias maquinas) en una entrega.

    python src/evaluacion/unir_entregas.py salidas/test_final_p1.jsonl salidas/test_final_p2.jsonl \
        salidas/test_final_p3.jsonl --entrada data/test_992.jsonl --salida submissions.jsonl

Ordena en el orden de la entrada y valida la entrega completa antes de escribirla, con
reproducibilidad/validar_entrega.py (schema oficial, pasajes si no hay abstencion, ids
unicos y exactamente los de la entrada, doc_id dentro de corpus_manifest.json) mas el
formato igual al de la pregunta. Con errores no escribe nada (exit 1), salvo --forzar.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl, write_jsonl  # noqa: E402


def validar(registros: list[dict], items: list[dict], doc_ids: set[str]) -> list[str]:
    """Las comprobaciones de validar_entrega.py (schema, ids, doc_id) + formato igual al de la pregunta."""
    from reproducibilidad.validar_entrega import validar_entrega

    res = validar_entrega(registros, doc_ids, {it["id"] for it in items})
    errores = list(res["globales"]) + [f"id={i}: {'; '.join(e)}" for i, e in res["errores"].items()]
    formato = {it["id"]: it["formato"] for it in items}
    errores += [f"id={r['id']}: formato {r.get('formato')} != {formato[r['id']]}"
                for r in registros if r["id"] in formato and r.get("formato") != formato[r["id"]]]
    return errores


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("partes", type=Path, nargs="+")
    ap.add_argument("--entrada", type=Path, default=config.TEST_PATH)
    ap.add_argument("--salida", type=Path, default=config.SUBMISSION_PATH)
    ap.add_argument("--forzar", action="store_true", help="escribir aunque haya errores")
    args = ap.parse_args()

    items = read_jsonl(args.entrada)
    registros = [r for p in args.partes for r in read_jsonl(p)]
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    errores = validar(registros, items, {d["doc_id"] for d in manifest["documentos"]})

    por_id = {r["id"]: r for r in registros}
    orden = [por_id[it["id"]] for it in items if it["id"] in por_id]
    n_abst = sum(r["abstencion"] for r in orden)
    print(f"{len(registros)} registros de {len(args.partes)} partes; {len(orden)}/{len(items)} ids de la entrada; "
          f"{n_abst} abstenciones ({n_abst / max(len(orden), 1):.1%}); {len(errores)} errores")
    for e in errores[:30]:
        print("  " + e)
    if errores and not args.forzar:
        print("No se escribe la entrega (usar --forzar para escribirla igual).")
        return 1
    write_jsonl(args.salida, orden)
    print(f"-> {args.salida}")
    return 1 if errores else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
