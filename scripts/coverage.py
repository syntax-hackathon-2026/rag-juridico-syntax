"""Cobertura del corpus frente al banco de preguntas.

Cruza los `legal_basis` de las preguntas (sample_50.jsonl) y los cuerpos de
seed_targets.json contra lo que realmente esta en el indice, usando el mismo
extractor de citas que el evaluador (citations.extract) para que "cubierto"
signifique "respaldable".

Sin indice, reporta que normas hay que descargar (necesarias vs seed).
Con indice (indice/chunks.jsonl, una linea JSON por fragmento con campo
"texto"), reporta ademas que cuerpos y articulos faltan.

Uso:
    python scripts/coverage.py
    python scripts/coverage.py --chunks indice/chunks.jsonl --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import citations  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def basis_text(row: dict) -> str:
    lb = row.get("legal_basis") or ""
    if isinstance(lb, list):
        lb = " ; ".join(map(str, lb))
    return str(lb)


def label(body: tuple) -> str:
    kind, num, year = body
    return f"{kind} {num}/{year}" if num else kind


def corpus_cites(chunks: list[dict]) -> set[tuple]:
    """Citas (cuerpo, articulo) respaldables por el indice."""
    found: set[tuple] = set()
    for ch in chunks:
        found |= citations.extract(str(ch.get("texto") or ch.get("text") or ""))
    return found


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--questions", default=str(ROOT / "data/sample_50.jsonl"))
    ap.add_argument("--seed", default=str(ROOT / "data/seed_targets.json"))
    ap.add_argument("--chunks", help="indice/chunks.jsonl; sin el, solo se compara con el seed")
    ap.add_argument("--verbose", action="store_true", help="lista articulos faltantes e items no cubiertos")
    args = ap.parse_args()

    rows = load_jsonl(Path(args.questions))
    seed = json.loads(Path(args.seed).read_text(encoding="utf-8"))["documentos"]
    seed_bodies = {tuple(d["canonico"]): d for d in seed}

    # Necesidad: por cuerpo, items que lo citan y articulos citados.
    items_by_body: dict[tuple, set] = defaultdict(set)
    arts_by_body: dict[tuple, set] = defaultdict(set)
    item_cites: dict[int, set[tuple]] = {}
    for r in rows:
        cs = citations.extract(basis_text(r))
        item_cites[r["id"]] = cs
        for c in cs:
            b = c[:3]
            items_by_body[b].add(r["id"])
            if c[3] is not None:
                arts_by_body[b].add(c[3])

    have: set[tuple] | None = None
    if args.chunks:
        have = corpus_cites(load_jsonl(Path(args.chunks)))
    have_bodies = {c[:3] for c in have} if have is not None else set()

    print(f"Preguntas: {len(rows)} | cuerpos citados: {len(items_by_body)}"
          f" | seed: {len(seed_bodies)} cuerpos\n")

    header = f"{'cuerpo':32} {'items':>5} {'arts':>4} {'seed':>4}"
    if have is not None:
        header += f" {'indice':>6} {'arts_ok':>7}"
    print(header)
    print("-" * len(header))
    missing_bodies: list[tuple] = []
    order = sorted(items_by_body, key=lambda b: -len(items_by_body[b]))
    for b in order:
        line = (f"{label(b):32} {len(items_by_body[b]):>5} {len(arts_by_body[b]):>4}"
                f" {'si' if b in seed_bodies else 'NO':>4}")
        if have is not None:
            ok = sum((*b, a) in have for a in arts_by_body[b])
            line += f" {'si' if b in have_bodies else 'NO':>6} {ok:>3}/{len(arts_by_body[b]):<3}"
            if b not in have_bodies:
                missing_bodies.append(b)
        print(line)
        if args.verbose and have is not None:
            falt = sorted(a for a in arts_by_body[b] if (*b, a) not in have)
            if falt:
                print(f"    articulos faltantes: {', '.join(falt)}")

    not_in_seed = [b for b in order if b not in seed_bodies]
    print(f"\nCitados en la muestra y ausentes del seed ({len(not_in_seed)}): "
          + (", ".join(label(b) for b in not_in_seed) or "ninguno"))

    if have is None:
        print("\n(sin --chunks: descargar primero lo marcado 'NO' en seed y los items con mas peso)")
        return

    # Cobertura por item: cuerpo presente y todos los articulos citados presentes.
    full = body_only = 0
    uncovered = []
    for qid, cs in item_cites.items():
        arts = {c for c in cs if c[3] is not None}
        if not cs:
            continue
        if arts and all(c in have for c in arts):
            full += 1
        elif all(c[:3] in have_bodies for c in cs):
            body_only += 1
        else:
            uncovered.append(qid)
    n = sum(1 for cs in item_cites.values() if cs)
    print(f"\nItems con citas: {n}")
    print(f"  articulos citados todos respaldables : {full}")
    print(f"  cuerpo presente, articulo(s) faltan  : {body_only}")
    print(f"  cuerpo ausente                       : {len(uncovered)}")
    if args.verbose and uncovered:
        print(f"  ids sin cobertura: {sorted(uncovered)}")
    if missing_bodies:
        print("\nDescargar, por peso: "
              + ", ".join(f"{label(b)} ({len(items_by_body[b])})" for b in missing_bodies))


if __name__ == "__main__":
    main()
