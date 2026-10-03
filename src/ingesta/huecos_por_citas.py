"""Normas que el propio corpus cita y que no estan en el corpus (grafo de citas internas).

    python src/ingesta/huecos_por_citas.py                       # tabla en consola
    python src/ingesta/huecos_por_citas.py --md docs/ingesta/huecos_por_citas.md
    python src/ingesta/huecos_por_citas.py --contiene "doble imposicion" --min-docs 1
    python src/ingesta/huecos_por_citas.py --min-docs 10 --csv salidas/huecos_v5.csv   # entrada de ampliar_desde_citas.py

Lee data_corpus/indice/chunks.jsonl, extrae con scripts/citations.py las referencias de cada
fragmento (sin su cabecera, que se cita a si misma) y resta los cuerpos canonicos que ya
estan en el corpus. Ordena los cuerpos ausentes por numero de documentos distintos que los
citan (una norma citada por muchas fuentes es un hueco estructural, no una mencion suelta).
`--contiene` filtra por texto cercano a la cita (titulo de la norma en la frase que la cita).

Solo stdlib + citations: no descarga nada. La lista sirve de entrada para
data/registros/fuentes_override.json y src/ingesta/descargar_fuentes.py (ingesta automatica:
lo que las reglas de descarga no resuelvan se descarta).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

TIPOS_NORMA = {"ley", "decreto", "decreto_ley", "decision", "acto_legislativo", "resolucion"}
VENTANA = 120  # caracteres antes y despues de la cita para el contexto


def _clave(cuerpo: tuple) -> tuple:
    """Cuerpo comparable: sin ceros a la izquierda en el numero ("01" de 1984 = "1" de 1984)."""
    tipo, numero, anio = cuerpo
    return (tipo, numero.lstrip("0") or "0" if numero and numero.isdigit() else numero, anio)


def doc_id_de(cuerpo: tuple) -> str:
    """doc_id propuesto con la convencion del manifest (tipo_numero_anio)."""
    tipo, numero, anio = cuerpo
    if tipo == "jurisprudencia":
        sala, num = numero.lower().split("-", 1)
        return f"sentencia_{sala}_{int(num) if num.isdigit() else num}_{anio}"
    return "_".join(str(x).lower() for x in (tipo, numero, anio) if x)


def _patron(cuerpo: tuple) -> re.Pattern | None:
    tipo, numero, anio = cuerpo
    if not numero:
        return None
    return re.compile(rf"\b{re.escape(numero)}\s*(?:de|del|/|-)\s*{anio}\b" if anio else rf"\b{re.escape(numero)}\b",
                      re.IGNORECASE)


_CANDIDATO = re.compile(r"\b(?:ley|decreto|decisi[oó]n|sentencia|acto legislativo|resoluci[oó]n)\b", re.IGNORECASE)


def _citas_de(args: tuple[str, str]) -> list[tuple[tuple, str]]:
    """(cuerpo citado, contexto) de un fragmento; corre en un proceso hijo."""
    linea, filtro = args
    c = json.loads(linea)
    cuerpo_txt = c["texto"].split("\n", 1)[-1]
    if not _CANDIDATO.search(cuerpo_txt) or (filtro and filtro not in citations.norm(cuerpo_txt)):
        return []
    salida = []
    for cuerpo in citations.bodies(citations.extract(cuerpo_txt)):
        if cuerpo == tuple(c["canonico"]):
            continue
        pat = _patron(cuerpo)
        m = pat.search(cuerpo_txt) if pat else None
        ctx = (cuerpo_txt[max(0, m.start() - VENTANA):m.end() + VENTANA] if m else "").replace("\n", " ")
        if filtro and filtro not in citations.norm(ctx):
            continue
        salida.append((cuerpo, ctx))
    return salida


def huecos(contiene: str | None = None, procesos: int | None = None) -> list[dict]:
    from multiprocessing import Pool

    presentes: set[tuple] = set()
    menciones: dict[tuple, Counter] = defaultdict(Counter)  # cuerpo -> doc citante -> n
    contextos: dict[tuple, str] = {}
    areas_doc = {d["doc_id"]: d.get("areas") or []
                 for d in json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]}
    filtro = citations.norm(contiene) if contiene else ""
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        lineas = [l for l in f if l.strip()]
    docs = []
    for linea in lineas:
        c = json.loads(linea)
        presentes.add(_clave(tuple(c["canonico"])))
        docs.append(c["doc_id"])
    # chunksize grande y orden de entrada conservado (imap): el resultado es determinista
    with Pool(procesos) as pool:
        for doc_id, citas in zip(docs, pool.imap(_citas_de, ((l, filtro) for l in lineas), chunksize=500)):
            for cuerpo, ctx in citas:
                cuerpo = _clave(cuerpo)
                menciones[cuerpo][doc_id] += 1
                if cuerpo not in contextos and ctx:
                    contextos[cuerpo] = ctx
    filas = []
    for cuerpo, por_doc in menciones.items():
        if cuerpo in presentes or cuerpo[0] in citations.CODES:
            continue
        areas = Counter(a for d in por_doc for a in areas_doc.get(d, []))
        filas.append({
            "cuerpo": list(cuerpo), "doc_id": doc_id_de(cuerpo),
            "tipo": "norma" if cuerpo[0] in TIPOS_NORMA else ("sentencia" if cuerpo[0] == "jurisprudencia" else cuerpo[0]),
            "docs_citantes": len(por_doc), "menciones": sum(por_doc.values()),
            "areas": [a for a, _ in areas.most_common(3)],
            "ejemplos": sorted(por_doc, key=lambda d: (-por_doc[d], d))[:3],
            "contexto": contextos.get(cuerpo, ""),
        })
    return sorted(filas, key=lambda f: (-f["docs_citantes"], -f["menciones"], f["doc_id"]))


def markdown(filas: list[dict], limite: int) -> str:
    lineas = ["# Huecos por citas internas", "",
              "Generado por `src/ingesta/huecos_por_citas.py`: normas citadas por documentos del corpus que no estan en el corpus, "
              "ordenadas por documentos citantes. No editar a mano.", "",
              "| doc_id propuesto | tipo | docs citantes | menciones | areas | contexto |", "|---|---|---:|---:|---|---|"]
    for f in filas[:limite]:
        ctx = f["contexto"][:160].replace("|", "/")
        lineas.append(f"| `{f['doc_id']}` | {f['tipo']} | {f['docs_citantes']} | {f['menciones']} | "
                      f"{', '.join(f['areas'])} | {ctx} |")
    return "\n".join(lineas) + "\n"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--contiene", help="solo citas con este texto cerca (sin tildes ni mayusculas)")
    ap.add_argument("--tipo", choices=["norma", "sentencia", "todos"], default="norma")
    ap.add_argument("--min-docs", type=int, default=2, help="minimo de documentos citantes")
    ap.add_argument("--limite", type=int, default=60)
    ap.add_argument("--md", type=Path, help="escribe la tabla en este .md")
    ap.add_argument("--json", type=Path, help="escribe la lista completa en este .json")
    ap.add_argument("--csv", type=Path, help="CSV de entrada de src/ingesta/ampliar_desde_citas.py "
                    "(n_preguntas = documentos citantes)")
    args = ap.parse_args()
    filas = [f for f in huecos(args.contiene)
             if f["docs_citantes"] >= args.min_docs and (args.tipo == "todos" or f["tipo"] == args.tipo)]
    if args.json:
        args.json.write_text(json.dumps(filas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.csv:
        with args.csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["tipo", "numero", "anio", "areas", "n_preguntas", "ids"])
            for fila in filas[:args.limite]:
                w.writerow([*fila["cuerpo"], ";".join(fila["areas"]), fila["docs_citantes"], ""])
    if args.md:
        args.md.write_text(markdown(filas, args.limite), encoding="utf-8", newline="\n")
    for f in filas[:args.limite]:
        print(f"{f['docs_citantes']:>4} docs {f['menciones']:>5} menc  {f['doc_id']:<28} {', '.join(f['areas'])[:50]:<50}  "
              f"{f['contexto'][:110]}")
    print(f"{len(filas)} cuerpos ausentes (tipo={args.tipo}, min_docs={args.min_docs})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
