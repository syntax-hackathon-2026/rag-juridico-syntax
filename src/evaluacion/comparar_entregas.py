"""Compara dos entregas item por item: normas citadas y pasajes recuperados.

    python src/evaluacion/comparar_entregas.py salidas/a.jsonl salidas/b.jsonl
    python src/evaluacion/comparar_entregas.py submissions.jsonl salidas/verificacion.jsonl --ids 51 60

Es el criterio de la verificacion en vivo (enunciado, seccion 7): deben coincidir las
normas citadas y los pasajes recuperados. Tambien se usa para comprobar el
determinismo (dos corridas iguales -> sin diferencias). Reporta ademas si el texto
de la respuesta es identico (con temperatura 0 deberia serlo). exit 1 si hay
diferencias en citas o pasajes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402
from common import read_jsonl  # noqa: E402
from evaluate import answer_text  # noqa: E402


def firma(reg: dict) -> dict:
    return {
        "abstencion": reg.get("abstencion"),
        "citas": citations.extract(answer_text(reg)),
        "pasajes": [(p["doc_id"], p.get("inicio"), p.get("fin")) for p in reg.get("pasajes_recuperados") or []],
        "texto": {k: v for k, v in reg.items() if k not in ("pasajes_recuperados", "latencia_ms")},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("--ids", type=int, nargs="+")
    args = ap.parse_args()
    a = {r["id"]: r for r in read_jsonl(args.a)}
    b = {r["id"]: r for r in read_jsonl(args.b)}
    ids = sorted(set(args.ids) if args.ids else set(a) & set(b))
    faltan = [i for i in ids if i not in a or i not in b]
    difieren = 0
    texto_distinto = 0
    for i in ids:
        if i in faltan:
            continue
        fa, fb = firma(a[i]), firma(b[i])
        problemas = []
        if fa["abstencion"] != fb["abstencion"]:
            problemas.append(f"abstencion {fa['abstencion']} vs {fb['abstencion']}")
        if fa["citas"] != fb["citas"]:
            problemas.append(f"citas: solo en A {sorted(fa['citas'] - fb['citas'], key=str)}, "
                             f"solo en B {sorted(fb['citas'] - fa['citas'], key=str)}")
        if fa["pasajes"] != fb["pasajes"]:
            problemas.append("pasajes distintos")
        if problemas:
            difieren += 1
            print(f"id={i}: " + "; ".join(problemas))
        elif fa["texto"] != fb["texto"]:
            texto_distinto += 1
            print(f"id={i}: mismas citas y pasajes, redaccion distinta")
    print(f"\n{len(ids) - len(faltan)} items comparados: {difieren} con citas/pasajes distintos, "
          f"{texto_distinto} solo con redaccion distinta" + (f"; ausentes en un archivo: {faltan}" if faltan else ""))
    return 1 if difieren or faltan else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
