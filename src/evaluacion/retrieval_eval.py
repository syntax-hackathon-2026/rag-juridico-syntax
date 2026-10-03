"""Mide la recuperacion sobre data/sample_50.jsonl antes de generar nada.

    python src/evaluacion/retrieval_eval.py --modo bm25
    python src/evaluacion/retrieval_eval.py --modo bm25 denso hibrido --experimento e01_bge_m3

El fundamento de referencia sale de `citations.extract(legal_basis)`: legal_basis es
ground truth y SOLO se usa aqui, para evaluar (nunca en runtime). Preguntas sin citas
extraibles (~16 % del banco) no entran.

Metricas por modo (promedio sobre las preguntas con fundamento):
  - doc_hit@k: algun fragmento del top-k es del cuerpo normativo de referencia
    (canonico del fragmento). MRR sobre el mismo criterio.
  - respaldo@10: fraccion de los cuerpos de referencia que el evaluador daria por
    respaldados con estos 10 pasajes (citations.extract sobre su texto, igual que
    evaluate.citas_respaldadas). Es el techo de los 20 pts de citacion.
  - art_hit@k: el top-k trae el articulo exacto (cuerpo + numero) de la referencia,
    sobre las preguntas cuyo fundamento llega a nivel de articulo.
  - latencia media por consulta.

Guarda el detalle por pregunta en evaluation/retrieval/<experimento>_<modo>.jsonl, una
fila por modo en evaluation/experiments.csv y el entorno en evaluation/entornos/.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from generacion import planificador  # noqa: E402
from recuperacion.consulta import consulta_de  # noqa: E402
from recuperacion.referencias import referencias_de, normalizar_articulo  # noqa: E402
from evaluacion.techo_reranker import metricas_techo  # noqa: E402
MODOS = ("bm25", "denso", "hibrido")


def cargar(cargar_denso=True):
    from recuperacion.retriever import cargar as cargar_retriever
    return cargar_retriever(cargar_denso=cargar_denso)

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402
from common import read_jsonl  # noqa: E402

KS = (1, 3, 5, 10)
COLUMNAS = [
    "fecha", "experimento", "commit", "n_documentos", "n_fragmentos", "version_segmentador",
    "retriever", "encoder", "fusion", "reranker", "retrieval_k", "generation_k", "decoder",
    "cuantizacion", "prompt_version", "consulta", "n_preguntas",
    "doc_hit@1", "doc_hit@3", "doc_hit@5", "doc_hit@10", "mrr", "respaldo@10",
    "art_hit@1", "art_hit@10", "n_con_articulo",
    "exactitud_cerradas", "citacion_pts", "abstencion_pts", "ragas", "latencia_ret_ms",
    "latencia_total_ms", "plataforma", "entorno_json", "notas",
]


_art = normalizar_articulo  # compatibilidad para evaluar_entrega y plan 05


def evaluar(modo: str, items: list[dict], tipo_consulta: str, techo: bool = False) -> tuple[dict, list[dict]]:
    if techo and modo != "hibrido":
        raise ValueError("El techo se mide sobre RRF hibrido")
    ret = cargar(cargar_denso=modo != "bm25")
    compuesta = modo == "hibrido" and tipo_consulta == "pregunta+opciones" and (
        config.CONSULTA_OPCIONES == "on" or config.PLANIFICADOR == "on")
    decoder = None
    if compuesta and config.PLANIFICADOR == "on":
        from generacion.llm import Decoder

        decoder = Decoder()
    filas = []
    for it in items:
        ref = citations.extract(it.get("legal_basis") or "")
        ref_b = citations.bodies(ref)
        if not ref_b:
            continue
        ref_art = {(c[0], c[1], c[2], _art(c[3])) for c in citations.article_level(ref)}
        consulta = consulta_de(it, tipo_consulta)
        refs_explicitas = referencias_de(it["pregunta"] if config.LOOKUP_FUENTE == "pregunta" else consulta)
        kwargs = ({"consulta_lookup": it["pregunta"]} if config.LOOKUP_MODO == "on"
                  and config.LOOKUP_FUENTE == "pregunta" else {})
        t0 = time.perf_counter()
        info_ret: dict = {}
        if compuesta:  # la misma recuperacion de responder.py (generacion/planificador.py)
            entrada = {kk: it[kk] for kk in ("id", "formato", "area", "pregunta", "opciones") if kk in it}
            top, info_ret = planificador.recuperar(entrada, ret, decoder, k=40 if techo else max(KS))
        else:
            top = ret.retrieve(consulta, k=40 if techo else max(KS), modo=modo, area=it.get("area"), **kwargs)
        ms = (time.perf_counter() - t0) * 1000
        cuerpos = [tuple(p.meta["canonico"]) for p in top]
        arts = [(*p.meta["canonico"], _art(p.meta["articulo"])) for p in top]
        rank_doc = next((r for r, c in enumerate(cuerpos, 1) if c in ref_b), None)
        rank_art = next((r for r, a in enumerate(arts, 1) if a in ref_art), None)
        respaldadas = set()
        for p in top[:10]:
            respaldadas |= citations.bodies(citations.extract(p.texto))
        filas.append({
            "id": it["id"], "formato": it["formato"], "area": it.get("area"),
            "referencia": sorted(map(list, ref_b), key=str), "referencia_articulos": sorted(map(list, ref_art), key=str),
            "rank_doc": rank_doc, "rank_art": rank_art,
            "referencias_explicitas": [list(r) for r in refs_explicitas],
            "respaldo": len(ref_b & respaldadas) / len(ref_b),
            "latencia_ms": round(ms, 1),
            **({"plan": info_ret["plan"]} if "plan" in info_ret else {}),
            "disparos": top[0].meta.get("disparos", []) if top else [],
            "top": [[p.chunk_id, round(p.score, 5)] for p in top],
        })
    n = len(filas)
    if not n:
        raise ValueError("No hay preguntas evaluables")
    con_art = [f for f in filas if f["referencia_articulos"]]
    met = {f"doc_hit@{k}": sum(bool(f["rank_doc"] and f["rank_doc"] <= k) for f in filas) / n for k in KS}
    met["mrr"] = sum(1 / f["rank_doc"] for f in filas if f["rank_doc"] and f["rank_doc"] <= 10) / n
    met["respaldo@10"] = sum(f["respaldo"] for f in filas) / n
    for k in (1, 10):
        met[f"art_hit@{k}"] = (sum(bool(f["rank_art"] and f["rank_art"] <= k) for f in con_art) / len(con_art)
                               if con_art else None)
    met["n_con_articulo"] = len(con_art)
    met["n_preguntas"] = n
    met["latencia_ret_ms"] = sum(f["latencia_ms"] for f in filas) / n
    if techo:
        met.update(metricas_techo(filas))
    met["subconjuntos_referencias"] = metricas_subconjuntos(filas)
    return met, filas


def metricas_subconjuntos(filas: list[dict]) -> dict:
    salida = {}
    for nombre, grupo in (("con_referencia", [f for f in filas if f.get("referencias_explicitas")]),
                          ("sin_referencia", [f for f in filas if not f.get("referencias_explicitas")]),
                          ("cerradas", [f for f in filas if f.get("formato") == "multiple_choice"]),
                          ("texto_libre", [f for f in filas if f.get("formato") != "multiple_choice"])):
        n = len(grupo)
        art = [f for f in grupo if f["referencia_articulos"]]
        salida[nombre] = {
            "n": n, "n_con_articulo_gt": len(art),
            "doc_hit@10": sum(bool(f["rank_doc"] and f["rank_doc"] <= 10) for f in grupo) / n if n else None,
            "art_hit@10": sum(bool(f["rank_art"] and f["rank_art"] <= 10) for f in art) / len(art) if art else None,
            "mrr": sum(1 / f["rank_doc"] for f in grupo if f["rank_doc"] and f["rank_doc"] <= 10) / n if n else None,
            "respaldo@10": sum(f["respaldo"] for f in grupo) / n if n else None,
        }
    return salida


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=config.ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        sucio = subprocess.run(["git", "status", "--porcelain"], cwd=config.ROOT,
                               capture_output=True, text=True).stdout.strip()
        return out + ("+cambios" if sucio else "")
    except (OSError, subprocess.CalledProcessError):
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modo", nargs="+", choices=MODOS, default=["bm25"])
    ap.add_argument("--split", default="sample", choices=["sample"])
    ap.add_argument("--consulta", choices=["pregunta", "pregunta+opciones"], default="pregunta+opciones")
    ap.add_argument("--experimento", default=None, help="nombre de la fila en experiments.csv")
    ap.add_argument("--notas", default="")
    ap.add_argument("--no-csv", action="store_true", help="solo imprimir, sin escribir en evaluation/")
    ap.add_argument("--techo-reranker", action="store_true", help="fase 0: top-40 RRF sin modelo nuevo")
    args = ap.parse_args()
    if args.techo_reranker and args.modo != ["hibrido"]:
        ap.error("--techo-reranker requiere --modo hibrido")
    if args.techo_reranker and config.LOOKUP_MODO != "off":
        ap.error("--techo-reranker mide RRF baseline: requiere SYNTAX_LOOKUP=off")
    if not config.CHUNKS_PATH.is_file() or not config.BM25_DIR.is_dir():
        ap.error("Falta indice local chunks.jsonl/BM25; usar el indice congelado. No se reconstruye automaticamente.")
    if any(m != "bm25" for m in args.modo):
        config.verificar_indice()

    items = read_jsonl(config.ROOT / "data" / "sample_50.jsonl")
    info = json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8")) if config.INDICE_INFO_PATH.is_file() else {}
    experimento = args.experimento or datetime.now().strftime("ret_%Y%m%d_%H%M")
    entorno = ""
    if not args.no_csv:
        entorno_path = config.EVALUATION_DIR / "entornos" / f"{experimento}.json"
        entorno_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(config.ROOT / "src/reproducibilidad/registrar_entorno.py"),
                        "--salida", str(entorno_path)], cwd=config.ROOT, capture_output=True)
        entorno = entorno_path.relative_to(config.ROOT).as_posix()

    for modo in args.modo:
        met, filas = evaluar(modo, items, args.consulta, techo=args.techo_reranker)
        print(f"\n== {modo}  ({met['n_preguntas']} preguntas con fundamento, {met['n_con_articulo']} a nivel de articulo)")
        for k in ("doc_hit@1", "doc_hit@3", "doc_hit@5", "doc_hit@10", "mrr", "respaldo@10", "art_hit@1", "art_hit@10"):
            v = met[k]
            print(f"   {k:<12} {v:.3f}" if v is not None else f"   {k:<12} -")
        print(f"   latencia     {met['latencia_ret_ms']:.0f} ms/consulta")
        if args.techo_reranker:
            print(json.dumps(metricas_techo(filas), ensure_ascii=False, indent=2))
        print(json.dumps(met["subconjuntos_referencias"], ensure_ascii=False, indent=2))
        fallos = [f["id"] for f in filas if not f["rank_doc"] or f["rank_doc"] > 10]
        print(f"   sin el cuerpo de referencia en el top-10: {fallos}")
        if args.no_csv:
            continue
        det = config.EVALUATION_DIR / "retrieval" / f"{experimento}_{modo}.jsonl"
        det.parent.mkdir(parents=True, exist_ok=True)
        with det.open("w", encoding="utf-8", newline="\n") as f:
            for fila in filas:
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        resumen = {"experimento": experimento, "modo": modo, "reranker": "off",
                   "fusion": "rrf60" if modo == "hibrido" else "",
                   "n_candidatos_por_rama": 40, "lookup": config.lookup_metadata(),
                   "filtro_cita": config.filtro_metadata(), "area": config.area_metadata(),
                   "composicion": config.composicion_metadata(), "metadatos": config.metadatos_metadata(),
                   "agentico": config.agentico_metadata(), "consulta": args.consulta, "metricas": met}
        with det.with_suffix(".meta.json").open("w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n")
        denso = info.get("denso") or {}
        fila_csv = {
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "experimento": f"{experimento}_{modo}", "commit": git_commit(),
            "n_documentos": len({c["doc_id"] for c in cargar(cargar_denso=False).chunks}),
            "n_fragmentos": info.get("n_fragmentos"), "version_segmentador": info.get("version_segmentador"),
            "retriever": modo, "encoder": denso.get("modelo", "") if modo != "bm25" else "",
            "fusion": "rrf60" if modo == "hibrido" else "", "reranker": "", "retrieval_k": 10,
            "consulta": args.consulta, "latencia_ret_ms": round(met["latencia_ret_ms"], 1),
            "plataforma": denso.get("device", "") if modo != "bm25" else "cpu",
            "entorno_json": entorno, "notas": args.notas + (
                "; fase0_reranker=" + json.dumps(metricas_techo(filas), ensure_ascii=False, sort_keys=True)
                if args.techo_reranker else "") + "; lookup=" + json.dumps(config.lookup_metadata(), sort_keys=True)
                + "; filtro_cita=" + config.FILTRO_CITA + f"; area_boost={config.AREA_BOOST}"
                + "; composicion=" + json.dumps(config.composicion_metadata(), sort_keys=True)
                + "; metadatos=" + json.dumps(config.metadatos_metadata(), sort_keys=True)
                + "; agentico=" + json.dumps(config.agentico_metadata(), sort_keys=True)
                + "; subconjuntos=" + json.dumps(met["subconjuntos_referencias"], sort_keys=True),
            **{k: (round(met[k], 4) if isinstance(met[k], float) else met[k])
               for k in COLUMNAS if k in met},
        }
        nuevo = not config.EXPERIMENTS_CSV.is_file()
        with config.EXPERIMENTS_CSV.open("a", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS, lineterminator="\n")
            if nuevo:
                w.writeheader()
            w.writerow({k: fila_csv.get(k, "") for k in COLUMNAS})
        print(f"   -> {det.relative_to(config.ROOT).as_posix()} y fila en {config.EXPERIMENTS_CSV.name}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
