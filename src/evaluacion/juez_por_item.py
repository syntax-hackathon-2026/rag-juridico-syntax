"""Juez RAGAS por item: el mismo de scripts/evaluate.py, pero guarda el score de cada item.

evaluate.py solo reporta el promedio, y con 35 items y +-0,03 de ruido del juez un
promedio no separa una variante de otra. Este script juzga varias entregas en una
sola corrida (cada texto distinto una sola vez), y deja un CSV por item con los
items sin veredicto marcados. evaluate.py no se modifica: es el evaluador oficial.

    # base completa (35 items)
    python src/evaluacion/juez_por_item.py juzgar --experimento j1_e24 \\
        --entrega e24=evaluation/generacion/e24_final/entrega.jsonl
    # variantes: solo los items cuyo texto difiere del de la base
    python src/evaluacion/juez_por_item.py juzgar --experimento j3 \\
        --entrega B=salidas/sample_tl_b.jsonl --entrega C=salidas/sample_tl_c.jsonl \\
        --solo-cambiados-vs salidas/sample_tl_a.jsonl
    # comparacion pareada (regla KEEP/REVERT de docs/GENERACION.md 10)
    python src/evaluacion/juez_por_item.py comparar evaluation/juez/j2.csv:A evaluation/juez/j3.csv:B
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import evaluate as ev  # noqa: E402
from common import DATA, read_jsonl  # noqa: E402

COLUMNAS = ["variante", "id", "formato", "correctness", "sin_veredicto", "n_palabras"]
DESTINO = config.EVALUATION_DIR / "juez"


def _clave() -> dict[int, dict]:
    return {r["id"]: r for r in read_jsonl(DATA / "sample_50.jsonl") if r["formato"] != "multiple_choice"}


def _subs(ruta: Path) -> dict[int, dict]:
    return {s["id"]: s for s in read_jsonl(ruta)}


def _texto(sub: dict | None) -> str | None:
    if not sub or sub.get("abstencion"):
        return None
    return ev.ragas_text(sub)


def juzgar(filas: list[tuple[str, int, str]], key: dict[int, dict]) -> list[float | None]:
    """filas: (variante, id, texto). Devuelve el score de cada fila (None = sin veredicto)."""
    llave = ev.api_key_juez(ev.JUEZ_BASE_URL)
    from datasets import Dataset
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    from ragas import evaluate as ragas_evaluate
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import answer_correctness

    unicos: dict[tuple[int, str], int] = {}
    for _, qid, texto in filas:
        unicos.setdefault((qid, texto), len(unicos))
    datos = {"question": [], "answer": [], "ground_truth": []}
    for qid, texto in unicos:
        datos["question"].append(key[qid]["pregunta"])
        datos["answer"].append(texto)
        datos["ground_truth"].append(key[qid]["respuesta_esperada"])
    print(f"juzgando {len(unicos)} textos distintos ({len(filas)} filas)", file=sys.stderr)
    llm = LangchainLLMWrapper(ChatOpenAI(
        model=ev.JUEZ_MODELO, base_url=ev.JUEZ_BASE_URL, api_key=llave, temperature=0,
        max_tokens=ev.JUEZ_MAX_TOKENS, extra_body={"reasoning": ev.JUEZ_REASONING}))
    emb = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name=ev.JUEZ_ENCODER))
    res = ragas_evaluate(Dataset.from_dict(datos), metrics=[answer_correctness], llm=llm, embeddings=emb)
    serie = list(res.to_pandas()["answer_correctness"])
    return [None if serie[unicos[(q, t)]] is None or math.isnan(serie[unicos[(q, t)]])
            else float(serie[unicos[(q, t)]]) for _, q, t in filas]


def cmd_juzgar(args) -> int:
    key = _clave()
    ids = set(args.ids) if args.ids else set(key)
    base = _subs(args.solo_cambiados_vs) if args.solo_cambiados_vs else None
    filas: list[tuple[str, int, str]] = []
    abstenidos: list[tuple[str, int]] = []
    for spec in args.entrega:
        nombre, _, ruta = spec.partition("=")
        subs = _subs(Path(ruta))
        for qid in sorted(ids):
            texto = _texto(subs.get(qid))
            if texto is None:
                abstenidos.append((nombre, qid))
                continue
            if base is not None and texto == _texto(base.get(qid)):
                continue
            filas.append((nombre, qid, texto))
    if not filas:
        print("nada que juzgar")
        return 0
    scores = juzgar(filas, key)
    DESTINO.mkdir(parents=True, exist_ok=True)
    salida = DESTINO / f"{args.experimento}.csv"
    with salida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, lineterminator="\n")
        w.writeheader()
        for (nombre, qid, texto), s in zip(filas, scores):
            w.writerow({"variante": nombre, "id": qid, "formato": key[qid]["formato"],
                        "correctness": "" if s is None else round(s, 4), "sin_veredicto": int(s is None),
                        "n_palabras": len(texto.split())})
        for nombre, qid in abstenidos:
            w.writerow({"variante": nombre, "id": qid, "formato": key[qid]["formato"], "correctness": 0.0,
                        "sin_veredicto": 0, "n_palabras": 0})
    por_var: dict[str, list[float | None]] = {}
    for (nombre, _, _), s in zip(filas, scores):
        por_var.setdefault(nombre, []).append(s)
    for nombre, ss in por_var.items():
        ok = [s for s in ss if s is not None]
        print(f"{nombre}: {len(ss)} juzgados, {len(ss) - len(ok)} sin veredicto, "
              f"media con veredicto {sum(ok) / max(len(ok), 1):.4f}, media (sin veredicto = 0) "
              f"{sum(ok) / len(ss):.4f}")
    print(f"-> {salida.relative_to(config.ROOT).as_posix()}")
    return 0


def _leer(spec: str) -> dict[int, float | None]:
    ruta, _, variante = spec.partition(":")
    salida = {}
    for r in csv.DictReader(open(ruta, encoding="utf-8")):
        if variante and r["variante"] != variante:
            continue
        salida[int(r["id"])] = None if r["sin_veredicto"] == "1" else float(r["correctness"])
    return salida


def cmd_comparar(args) -> int:
    """Pareado: items con veredicto en ambas. Sin veredicto se reporta aparte."""
    a, b = _leer(args.a), _leer(args.b)
    comunes = sorted(set(a) & set(b))
    pares = [(q, a[q], b[q]) for q in comunes if a[q] is not None and b[q] is not None]
    sin = [q for q in comunes if a[q] is None or b[q] is None]
    deltas = [y - x for _, x, y in pares]
    mejora = sum(d > 0.02 for d in deltas)
    empeora = sum(d < -0.02 for d in deltas)
    media = sum(deltas) / len(deltas) if deltas else 0.0
    for q, x, y in sorted(pares, key=lambda p: p[2] - p[1]):
        print(f"  #{q:<5} {x:.3f} -> {y:.3f}  ({y - x:+.3f})")
    print(f"pares {len(pares)}  media B-A {media:+.4f}  mejoran {mejora}  empeoran {empeora}  "
          f"sin veredicto {sin}")
    keep = media >= 0.03 and mejora >= empeora + 2
    print("KEEP" if keep else "REVERT (o empate)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    j = sub.add_parser("juzgar")
    j.add_argument("--experimento", required=True)
    j.add_argument("--entrega", action="append", required=True, help="nombre=ruta.jsonl (repetible)")
    j.add_argument("--ids", type=int, nargs="*")
    j.add_argument("--solo-cambiados-vs", type=Path, help="entrega base: se omiten los textos iguales")
    c = sub.add_parser("comparar")
    c.add_argument("a", help="csv[:variante] de la base")
    c.add_argument("b", help="csv[:variante] de la variante")
    args = ap.parse_args()
    return cmd_juzgar(args) if args.cmd == "juzgar" else cmd_comparar(args)


if __name__ == "__main__":
    raise SystemExit(main())
