"""Huecos del corpus frente a un lote de preguntas (sabado 09:00: data/test_992.jsonl).

    python src/ingesta/huecos_preguntas.py                         # sample_50
    python src/ingesta/huecos_preguntas.py --entrada data/test_992.jsonl --md salidas/huecos_test.md

Solo mira `pregunta` y `opciones` (lo que el sistema ve en runtime; nunca legal_basis):
  1. Referencias explicitas (scripts/citations.py) cuyo cuerpo no esta en el corpus: candidatas a
     descarga automatica (data/registros/fuentes_override.json -> descargar_fuentes.py --solo).
  2. Terminos que el indice BM25 no conoce o casi no conoce (frecuencia de documento < --df-min),
     agrupados por area: senal de un tema sin fuente. No se buscan a mano (regla del equipo).
Las referencias con articulo cuyo cuerpo si esta pero el articulo no, se listan aparte.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from ingesta.huecos_por_citas import _clave, doc_id_de  # noqa: E402
from recuperacion import lexico  # noqa: E402
from recuperacion.referencias import normalizar_articulo  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402
from common import read_jsonl  # noqa: E402


def _indice() -> tuple[set[tuple], set[tuple], dict[str, int]]:
    cuerpos, articulos = set(), set()
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        for linea in f:
            c = json.loads(linea)
            canon = _clave(tuple(c["canonico"]))
            cuerpos.add(canon)
            if c.get("articulo"):
                articulos.add((*canon, normalizar_articulo(c["articulo"])))
    vocab = json.loads((config.BM25_DIR / "vocab.index.json").read_text(encoding="utf-8"))
    indptr = np.load(config.BM25_DIR / "indptr.csc.index.npy")
    df = {tok: int(indptr[i + 1] - indptr[i]) for tok, i in vocab.items() if i + 1 < len(indptr)}
    return cuerpos, articulos, df


def analizar(items: list[dict], df_min: int) -> dict:
    cuerpos, articulos, df = _indice()
    faltan: dict[tuple, list] = defaultdict(list)
    arts_faltan: dict[tuple, list] = defaultdict(list)
    raros: dict[str, Counter] = defaultdict(Counter)
    ejemplos: dict[str, list] = defaultdict(list)
    for it in items:
        texto = " ".join([it["pregunta"], *(it.get("opciones") or {}).values()])
        for cita in citations.extract(texto):
            cuerpo = _clave(cita[:3])
            if cuerpo[0] in citations.CODES or cuerpo in cuerpos:
                if cita[3] and (*cuerpo, normalizar_articulo(cita[3])) not in articulos:
                    arts_faltan[(*cuerpo, cita[3])].append(it["id"])
                continue
            faltan[cuerpo].append(it["id"])
        for tok in set(lexico.tokenizar(texto)):
            if tok.isdigit() or len(tok) < 4:
                continue
            if df.get(tok, 0) < df_min:
                raros[it.get("area") or "?"][tok] += 1
                if len(ejemplos[tok]) < 3:
                    ejemplos[tok].append(it["id"])
    return {
        "normas_ausentes": sorted(({"doc_id": doc_id_de(c), "cuerpo": list(c), "preguntas": ids}
                                   for c, ids in faltan.items()), key=lambda r: (-len(r["preguntas"]), r["doc_id"])),
        "articulos_ausentes": sorted(({"cuerpo": list(c[:3]), "articulo": c[3], "preguntas": ids}
                                      for c, ids in arts_faltan.items()), key=lambda r: (-len(r["preguntas"]), str(r))),
        "terminos_raros": {area: [{"termino": t, "df": df.get(t, 0), "preguntas": n, "ejemplos": ejemplos[t]}
                                  for t, n in sorted(cnt.items(), key=lambda p: (-p[1], p[0]))]
                           for area, cnt in sorted(raros.items())},
    }


def markdown(res: dict, entrada: str) -> str:
    l = [f"# Huecos del corpus frente a `{entrada}`", "", "## Normas nombradas que no estan en el corpus", "",
         "| doc_id propuesto | preguntas |", "|---|---|"]
    l += [f"| `{r['doc_id']}` | {len(r['preguntas'])} ({', '.join(map(str, r['preguntas'][:6]))}) |"
          for r in res["normas_ausentes"]]
    l += ["", "## Articulos nombrados que no estan (el cuerpo si)", "", "| cuerpo | articulo | preguntas |", "|---|---|---|"]
    l += [f"| {' '.join(x for x in r['cuerpo'] if x)} | {r['articulo']} | {', '.join(map(str, r['preguntas'][:6]))} |"
          for r in res["articulos_ausentes"]]
    l += ["", "## Terminos raros en el indice, por area", ""]
    for area, filas in res["terminos_raros"].items():
        l.append(f"- **{area}**: " + ", ".join(f"{f['termino']} (df {f['df']}, {f['preguntas']} preg.)" for f in filas[:25]))
    return "\n".join(l) + "\n"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrada", type=Path, default=config.SAMPLE_PATH)
    ap.add_argument("--df-min", type=int, default=3, help="frecuencia de documento minima en BM25")
    ap.add_argument("--md", type=Path, help="escribe el reporte en este .md (usar salidas/, no versionado)")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    res = analizar(list(read_jsonl(args.entrada)), args.df_min)
    if args.json:
        args.json.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    texto = markdown(res, args.entrada.name)
    if args.md:
        args.md.write_text(texto, encoding="utf-8", newline="\n")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
