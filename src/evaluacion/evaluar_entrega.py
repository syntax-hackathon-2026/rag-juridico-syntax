"""Califica una entrega de sample_50 con el evaluador oficial y la registra.

    python src/evaluacion/evaluar_entrega.py --experimento e02_v0 --entrega salidas/sample_e02_v0.jsonl
    python src/evaluacion/evaluar_entrega.py --experimento e02_v0 --entrega ... --ragas   # + juez (OPENROUTER_API_KEY)

Hace cuatro cosas:
  1. scripts/evaluate.py --out evaluation/generacion/<exp>/reporte.json (puntaje oficial).
  2. Diagnostico por pregunta -> evaluation/generacion/<exp>/errores.csv, con la
     taxonomia de CLAUDE.md (CORPUS, DOCUMENT_RETRIEVAL, RANKING, GENERATION,
     CITATION, ARTICLE_RETRIEVAL, SCHEMA, ABSTENCION, OK). legal_basis y las respuestas
     se usan SOLO aqui, para evaluar.
  3. Copia entrega, trazas y meta de la corrida a evaluation/generacion/<exp>/.
  4. Una fila en evaluation/experiments.csv (mismas columnas que retrieval_eval.py)
     y el entorno en evaluation/entornos/<exp>.json.

Las trazas y la meta se buscan en salidas/trazas/<nombre de la corrida>.* (el
nombre sale del archivo de entrega: sample_<corrida>.jsonl) o con --corrida.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from evaluacion.retrieval_eval import COLUMNAS, _art  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402
from common import FLAWED_IDS, read_jsonl  # noqa: E402
from evaluate import answer_text, citas_respaldadas  # noqa: E402


def cargar_chunks() -> dict[str, tuple]:
    """chunk_id -> (canonico, articulo)."""
    salida = {}
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        for linea in f:
            c = json.loads(linea)
            salida[c["chunk_id"]] = (tuple(c["canonico"]), _art(c.get("articulo")))
    return salida


def diagnosticar(it: dict, reg: dict | None, traza: dict | None, chunks: dict, corpus_b: set) -> dict:
    ref = citations.extract(it.get("legal_basis") or "")
    ref_b = citations.bodies(ref)
    ref_art = {(c[0], c[1], c[2], _art(c[3])) for c in citations.article_level(ref)}
    fila = {"id": it["id"], "formato": it["formato"], "area": it.get("area"),
            "referencia": "; ".join(citations_str(ref_b))}
    if reg is None:
        return {**fila, "diagnostico": "SCHEMA", "detalle": "sin registro en la entrega"}
    top = [chunks.get(cid, ((), None)) for cid, _ in (traza or {}).get("top", [])]
    gen_k = (traza or {}).get("generation_k", config.GENERATION_K)
    cuerpos_top = [c for c, _ in top]
    rank_doc = next((r for r, c in enumerate(cuerpos_top, 1) if c in ref_b), None)
    rank_art = next((r for r, (c, a) in enumerate(top, 1) if (*c, a) in ref_art), None)
    citadas = citations.extract(answer_text(reg))
    sc = citations.score(answer_text(reg), it.get("legal_basis") or "", citas_respaldadas(reg)) if ref_b else {}
    correcta = None
    if it["formato"] == "multiple_choice":
        correcta = reg.get("respuesta_correcta") == it.get("respuesta_correcta")
    fila.update({
        "abstencion": reg.get("abstencion"),
        "respuesta": reg.get("respuesta_correcta") if it["formato"] == "multiple_choice" else "",
        "esperada": it.get("respuesta_correcta") or "",
        "correcta": "" if correcta is None else int(correcta),
        "rank_doc": rank_doc or "", "rank_art": rank_art or "",
        "citadas": "; ".join(citations_str(citations.bodies(citadas))),
        "aciertos_cita": sc.get("aciertos", ""), "sin_respaldo": sc.get("citas_sin_respaldo", ""),
        "latencia_s": round(reg.get("latencia_ms", 0) / 1000, 1),
        "motivos_abstencion": ",".join(((traza or {}).get("abstencion") or {}).get("motivos", [])),
        "regenerado": int(bool((traza or {}).get("regenerado"))),
    })
    if (traza or {}).get("errores_schema"):
        diag = "SCHEMA"
    elif reg.get("abstencion"):
        diag = "ABSTENCION"
    elif ref_b and not (ref_b & corpus_b):
        diag = "CORPUS"
    elif ref_b and rank_doc is None:
        diag = "DOCUMENT_RETRIEVAL"
    elif correcta is False:
        diag = "GENERATION" if (rank_doc and rank_doc <= gen_k) or not ref_b else "RANKING"
    elif ref_b and (sc.get("citas_sin_respaldo") or not sc.get("aciertos")):
        diag = "CITATION"
    elif ref_art and rank_art is None:
        diag = "ARTICLE_RETRIEVAL"
    else:
        diag = "OK"
    fila["diagnostico"] = diag
    return fila


def citations_str(cuerpos: set) -> list[str]:
    return sorted("/".join(str(x) for x in c if x) for c in cuerpos)


def metricas_recuperacion(filas: list[dict], subs: dict, items: list[dict]) -> dict:
    con_ref = [f for f in filas if f.get("referencia") and f["diagnostico"] != "SCHEMA"]
    n = len(con_ref) or 1
    met = {f"doc_hit@{k}": sum(bool(f["rank_doc"] and f["rank_doc"] <= k) for f in con_ref) / n for k in (1, 3, 5, 10)}
    met["mrr"] = sum(1 / f["rank_doc"] for f in con_ref if f["rank_doc"]) / n
    resp = []
    for it in items:
        ref_b = citations.bodies(citations.extract(it.get("legal_basis") or ""))
        if ref_b and it["id"] in subs:
            resp.append(len(ref_b & citations.bodies(citas_respaldadas(subs[it["id"]]))) / len(ref_b))
    met["respaldo@10"] = sum(resp) / len(resp) if resp else 0.0
    met["n_preguntas"] = len(con_ref)
    return met


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrega", type=Path, required=True)
    ap.add_argument("--experimento", required=True)
    ap.add_argument("--corrida", help="nombre de la corrida en salidas/trazas/ (por defecto, el de la entrega)")
    ap.add_argument("--ragas", action="store_true")
    ap.add_argument("--notas", default="")
    ap.add_argument("--no-csv", action="store_true")
    args = ap.parse_args()

    corrida = args.corrida or args.entrega.stem.removeprefix("sample_")
    destino = config.EVALUATION_DIR / "generacion" / args.experimento
    destino.mkdir(parents=True, exist_ok=True)
    reporte_path = destino / "reporte.json"
    cmd = [sys.executable, str(config.ROOT / "scripts" / "evaluate.py"), "--submission", str(args.entrega),
           "--split", "sample", "--out", str(reporte_path)] + (["--ragas"] if args.ragas else [])
    r = subprocess.run(cmd, cwd=config.ROOT, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-4000:])
        return r.returncode
    rep = json.loads(reporte_path.read_text(encoding="utf-8"))

    items = read_jsonl(config.SAMPLE_PATH)
    subs = {s["id"]: s for s in read_jsonl(args.entrega)}
    trazas_path = config.TRAZAS_DIR / f"{corrida}.jsonl"
    meta_path = config.TRAZAS_DIR / f"{corrida}.meta.json"
    trazas = {t["id"]: t for t in read_jsonl(trazas_path)} if trazas_path.is_file() else {}
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
    chunks = cargar_chunks()
    corpus_b = {c for c, _ in chunks.values()}
    filas = [diagnosticar(it, subs.get(it["id"]), trazas.get(it["id"]), chunks, corpus_b)
             for it in items if it["id"] not in FLAWED_IDS]

    columnas = ["id", "formato", "area", "diagnostico", "abstencion", "respuesta", "esperada", "correcta",
                "rank_doc", "rank_art", "referencia", "citadas", "aciertos_cita", "sin_respaldo", "regenerado",
                "motivos_abstencion", "latencia_s", "detalle"]
    with (destino / "errores.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for fila in filas:
            w.writerow({k: fila.get(k, "") for k in columnas})
    shutil.copyfile(args.entrega, destino / "entrega.jsonl")
    if trazas_path.is_file():
        shutil.copyfile(trazas_path, destino / "trazas.jsonl")
    if meta_path.is_file():
        shutil.copyfile(meta_path, destino / "meta.json")

    conteo: dict[str, int] = {}
    for fila in filas:
        conteo[fila["diagnostico"]] = conteo.get(fila["diagnostico"], 0) + 1
    met = metricas_recuperacion(filas, subs, items)
    lat_ret = [t["latencia"]["ret_ms"] for t in trazas.values()]
    lat_tot = [t["latencia"]["total_ms"] for t in trazas.values()]
    ragas = rep.get("correccion_ragas", {})
    print(f"== {args.experimento}")
    print(f"   cerradas   {rep['cerradas']['puntos']:>6} / 20   (accuracy {rep['cerradas']['accuracy']:.3f})")
    print(f"   ragas      {ragas.get('puntos')} / 30   (correctness {ragas.get('correctness', '-')})")
    print(f"   citacion   {rep['citas']['puntos']:>6} / 20   (recall {rep['citas']['recall_citas_ponderado']}, "
          f"sin respaldo {rep['citas']['tasa_sin_respaldo']})")
    print(f"   abstencion {rep['abstencion']['puntos']:>6} / 10")
    print(f"   total      {rep['total_automatico']['obtenidos']} / {rep['total_automatico']['posibles']}")
    print(f"   validacion {rep['validacion']['errores']} errores")
    if lat_tot:
        print(f"   latencia   {sum(lat_tot) / len(lat_tot) / 1000:.1f} s/pregunta (recuperacion {sum(lat_ret) / len(lat_ret):.0f} ms)")
    print(f"   diagnostico {dict(sorted(conteo.items()))}")
    print(f"   -> {destino.relative_to(config.ROOT).as_posix()}/")
    if args.no_csv:
        return 0

    entorno_path = config.EVALUATION_DIR / "entornos" / f"{args.experimento}.json"
    subprocess.run([sys.executable, str(config.ROOT / "src/reproducibilidad/registrar_entorno.py"),
                    "--salida", str(entorno_path)], cwd=config.ROOT, capture_output=True)
    dec = meta.get("decoder") or {}
    ret = meta.get("retrieval") or {}
    ind = meta.get("indice") or {}
    fila_csv = {
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"), "experimento": args.experimento,
        "commit": meta.get("commit", ""), "n_documentos": len({cid.split("#")[0] for cid in chunks}),
        "n_fragmentos": ind.get("n_fragmentos"), "version_segmentador": ind.get("version_segmentador"),
        "retriever": ret.get("modo"), "encoder": ind.get("encoder"),
        "fusion": "rrf60" if ret.get("modo") == "hibrido" else "", "reranker": "",
        "retrieval_k": ret.get("retrieval_k"), "generation_k": ret.get("generation_k"),
        "decoder": dec.get("gguf"), "cuantizacion": dec.get("cuantizacion"),
        "prompt_version": meta.get("prompt_version"), "consulta": "pregunta+opciones",
        **{k: round(v, 4) if isinstance(v, float) else v for k, v in met.items()},
        "exactitud_cerradas": rep["cerradas"]["accuracy"], "citacion_pts": rep["citas"]["puntos"],
        "abstencion_pts": rep["abstencion"]["puntos"], "ragas": ragas.get("correctness", ""),
        "latencia_ret_ms": round(sum(lat_ret) / len(lat_ret), 1) if lat_ret else "",
        "latencia_total_ms": round(sum(lat_tot) / len(lat_tot), 1) if lat_tot else "",
        "plataforma": f"{platform.system()} {platform.machine()}, llama.cpp {dec.get('llama_cpp', '')}, "
                      f"encoder {meta.get('device_encoder', '')}",
        "entorno_json": entorno_path.relative_to(config.ROOT).as_posix(),
        "notas": (f"citar_evidencia={ret.get('citar_evidencia')}; "
                  f"filtro_cita={(ret.get('filtro_cita') or {}).get('modo', 'off')}; prompt={meta.get('prompt_version', '')}; "
                  + "lookup=" + json.dumps(ret.get("lookup", {"modo": "off"}), sort_keys=True) + "; " + args.notas).strip(),
    }
    nuevo = not config.EXPERIMENTS_CSV.is_file()
    with config.EXPERIMENTS_CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, lineterminator="\n")
        if nuevo:
            w.writeheader()
        w.writerow({k: fila_csv.get(k, "") for k in COLUMNAS})
    print(f"   fila en {config.EXPERIMENTS_CSV.relative_to(config.ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
