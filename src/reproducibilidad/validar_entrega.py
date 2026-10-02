"""Valida una entrega JSONL contra schema/submission.schema.json y la regla de pasajes (sin clave de respuestas).

    python src/reproducibilidad/validar_entrega.py submissions.jsonl [--preguntas data/test_992.jsonl]

Sirve para el test de 992 cuando no se tiene el answer_key (solo lo tiene el jurado): comprueba schema, ids
unicos, que `doc_id` de cada pasaje exista en corpus_manifest.json y, con --preguntas, que no falte ni sobre
ningun id. Exit 1 si hay algun error. Corre dentro del .venv (usa jsonschema via generacion.postproceso).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import config  # noqa: E402
from common import read_jsonl  # noqa: E402


def validar_entrega(registros: list[dict], doc_ids: set[str], ids_esperados: set[int] | None = None) -> dict:
    """{'n', 'abstenciones', 'por_formato', 'errores': {id: [msg]}, 'globales': [msg]}."""
    from generacion import postproceso

    errores: dict = {}
    globales: list[str] = []
    ids = [r.get("id") for r in registros]
    for i, c in Counter(ids).items():
        if c > 1:
            globales.append(f"id {i} repetido {c} veces")
    for r in registros:
        e = list(postproceso.validar(r))
        for p in r.get("pasajes_recuperados") or []:
            if p.get("doc_id") not in doc_ids:
                e.append(f"doc_id fuera del manifest: {p.get('doc_id')}")
        if e:
            errores[r.get("id")] = e
    if ids_esperados is not None:
        faltan, sobran = ids_esperados - set(ids), set(ids) - ids_esperados
        if faltan:
            globales.append(f"faltan {len(faltan)} ids: {sorted(faltan)[:10]}")
        if sobran:
            globales.append(f"sobran {len(sobran)} ids: {sorted(sobran)[:10]}")
    return {"n": len(registros), "abstenciones": sum(bool(r.get("abstencion")) for r in registros),
            "por_formato": dict(Counter(r.get("formato") for r in registros)),
            "errores": errores, "globales": globales}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("entrega", type=Path)
    ap.add_argument("--preguntas", type=Path, help="JSONL de preguntas: exige exactamente esos ids")
    args = ap.parse_args()

    registros = read_jsonl(args.entrega)
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    ids_esperados = {q["id"] for q in read_jsonl(args.preguntas)} if args.preguntas else None
    res = validar_entrega(registros, {d["doc_id"] for d in manifest["documentos"]}, ids_esperados)
    print(f"{args.entrega.name}: {res['n']} registros, {res['abstenciones']} abstenciones, formatos {res['por_formato']}")
    for g in res["globales"]:
        print("  ERROR", g)
    for i, e in list(res["errores"].items())[:10]:
        print(f"  ERROR id={i}: {'; '.join(e[:3])}")
    n_err = len(res["errores"]) + len(res["globales"])
    print(f"validacion de schema: {'OK' if not n_err else f'{n_err} problemas'}")
    return 1 if n_err else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
