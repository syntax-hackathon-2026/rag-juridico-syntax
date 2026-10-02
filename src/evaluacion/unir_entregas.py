"""Une las particiones de una corrida (main.py --particion I/N en varias maquinas) en una entrega.

    python src/evaluacion/unir_entregas.py salidas/test_final_p1.jsonl salidas/test_final_p2.jsonl \
        salidas/test_final_p3.jsonl --entrada data/test_992.jsonl --salida submissions.jsonl

Ordena en el orden de la entrada y valida la entrega completa antes de escribirla:
cada id de la entrada exactamente una vez, formato igual al de la pregunta, schema
oficial (postproceso.validar, que tambien exige pasajes si no hay abstencion) y
doc_id de cada pasaje dentro de corpus_manifest.json. Con errores no escribe nada
(exit 1), salvo --forzar.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl, write_jsonl  # noqa: E402


def validar_entrega(registros: list[dict], items: list[dict], doc_ids: set[str]) -> list[str]:
    from generacion import postproceso

    errores = []
    conteo = Counter(r["id"] for r in registros)
    errores += [f"id={i}: {n} veces" for i, n in sorted(conteo.items()) if n > 1]
    por_id = {r["id"]: r for r in registros}
    esperados = {it["id"]: it for it in items}
    errores += [f"id={i}: falta" for i in esperados if i not in por_id]
    errores += [f"id={i}: no esta en la entrada" for i in por_id if i not in esperados]
    for i, r in por_id.items():
        if i in esperados and r.get("formato") != esperados[i]["formato"]:
            errores.append(f"id={i}: formato {r.get('formato')} != {esperados[i]['formato']}")
        errores += [f"id={i}: {e}" for e in postproceso.validar(r)]
        ajenos = sorted({p["doc_id"] for p in r.get("pasajes_recuperados") or []} - doc_ids)
        if ajenos:
            errores.append(f"id={i}: doc_id fuera del manifest {ajenos}")
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
    errores = validar_entrega(registros, items, {d["doc_id"] for d in manifest["documentos"]})

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
