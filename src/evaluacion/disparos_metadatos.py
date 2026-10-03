"""Cuantas preguntas disparan cada regla de la busqueda por metadatos (docs/INDEXACION.md 19).

Sin indice ni modelos: solo `pregunta` y `opciones` (nunca legal_basis ni respuestas),
citations.py, recuperacion/alias.py y la lista de cuerpos de chunks.jsonl. Sirve para
ver si una regla medida en sample_50 generaliza al lote del sabado:

    python src/evaluacion/disparos_metadatos.py --entrada data/test_992.jsonl
    python src/evaluacion/disparos_metadatos.py --entrada data/test_992.jsonl --mostrar nombres
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from recuperacion import alias  # noqa: E402
from recuperacion.consulta import consulta_de  # noqa: E402
from recuperacion.referencias import cuerpos_de, referencias_de  # noqa: E402
from recuperacion.retriever import _PIDE_VIGENCIA, _PIDE_VOTO  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from citations import norm  # noqa: E402
from common import read_jsonl  # noqa: E402


def cuerpos_corpus() -> set[tuple]:
    cuerpos = set()
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        for linea in f:
            i = linea.find('"canonico": ')
            if i >= 0:
                cuerpos.add(tuple(json.loads(linea[i + 12:linea.index("]", i) + 1])))
    return cuerpos


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrada", type=Path, default=config.SAMPLE_PATH)
    ap.add_argument("--mostrar", choices=["nombres", "cuerpo"], default=None,
                    help="lista las preguntas que disparan esa regla, para revisarlas a mano")
    args = ap.parse_args()
    en_corpus = cuerpos_corpus()
    reglas: Counter = Counter()
    por_area: dict[str, Counter] = {}
    for item in read_jsonl(args.entrada):
        consulta = consulta_de(item)
        t = norm(consulta)
        oficiales = {c for c in cuerpos_de(consulta)}
        por_alias = alias.cuerpos_alias(consulta) - oficiales
        disparos = {
            "cuerpo_oficial_en_corpus": bool(oficiales & en_corpus),
            "cuerpo_oficial_fuera_corpus": bool(oficiales - en_corpus),
            "alias_nuevo_en_corpus": bool(por_alias & en_corpus),
            "articulo_explicito": any(r[3] for r in referencias_de(consulta)),
            "articulo_por_alias": bool(alias.referencias_alias(consulta)),
            "cuerpo_total(CUERPO)": bool((oficiales | por_alias) & en_corpus),
            "pide_voto(excepcion)": bool(_PIDE_VOTO.search(t)),
            "pide_vigencia(excepcion)": bool(_PIDE_VIGENCIA.search(t)),
        }
        area = item.get("area") or "?"
        por_area.setdefault(area, Counter())["n"] += 1
        for k, v in disparos.items():
            reglas[k] += v
            por_area[area][k] += v
        reglas["n"] += 1
        if args.mostrar == "nombres" and por_alias:
            print(f"#{item['id']} {sorted(por_alias, key=str)}  {item['pregunta'][:140]!r}")
        if args.mostrar == "cuerpo" and disparos["cuerpo_total(CUERPO)"]:
            print(f"#{item['id']} {sorted((oficiales | por_alias) & en_corpus, key=str)}  {item['pregunta'][:120]!r}")
    n = reglas.pop("n")
    print(f"\n{args.entrada.name}: {n} preguntas")
    for k, v in reglas.items():
        print(f"  {k:<30} {v:>4}  ({v / n:.0%})")
    print("\npor area (cuerpo_total / n):")
    for area, c in sorted(por_area.items()):
        print(f"  {area:<40} {c['cuerpo_total(CUERPO)']:>3}/{c['n']:<3} alias {c['alias_nuevo_en_corpus']}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
