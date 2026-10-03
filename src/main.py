"""Comando unico: preguntas -> entrega JSONL conforme a schema/submission.schema.json.

    python src/main.py --split sample                      # data/sample_50.jsonl -> salidas/sample_<exp>.jsonl
    python src/main.py --split test                        # data/test_992.jsonl  -> submissions.jsonl
    python src/main.py --split sample --limite 5           # humo
    python src/main.py --split sample --ids 51 60          # regenerar items concretos (verificacion en vivo)

Requisitos: indice en data_corpus/indice/ y el decoder servido en local
(`python src/generacion/modelo.py servir` en otra terminal).

La salida se escribe linea a linea y se reanuda: si la corrida se cae, volver a
lanzar el mismo comando salta los ids ya escritos. Al final se reordena en el orden
de entrada y se valida contra el schema. Trazas por item (pasajes, llamadas al
decoder, citas, senales de abstencion, latencias) en salidas/trazas/<exp>.jsonl, y
la configuracion de la corrida en salidas/trazas/<exp>.meta.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl  # noqa: E402


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=config.ROOT,
                             capture_output=True, text=True, check=True).stdout.strip()
        sucio = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=config.ROOT,
                               capture_output=True, text=True).stdout.strip()
        return out + ("+cambios" if sucio else "")
    except (OSError, subprocess.CalledProcessError):
        return ""


def main() -> int:
    from generacion import abstencion, modelo, postproceso, prompts
    from generacion.llm import Decoder
    from generacion.responder import responder
    from recuperacion.retriever import cargar

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--split", choices=["sample", "test"], default="sample")
    ap.add_argument("--entrada", type=Path, help="JSONL de preguntas (por defecto el del split)")
    ap.add_argument("--salida", type=Path, help="JSONL de la entrega")
    ap.add_argument("--experimento", help="nombre de la corrida (trazas y experiments.csv)")
    ap.add_argument("--ids", type=int, nargs="+", help="solo estos ids")
    ap.add_argument("--limite", type=int, help="solo los N primeros items")
    ap.add_argument("--particion", help="I/N: solo los items de indice i con i %% N == I-1")
    ap.add_argument("--sin-reanudar", action="store_true", help="borrar la salida previa y empezar de cero")
    ap.add_argument("--generation-k", type=int, choices=(3, 5, 7, 10),
                    help="pasajes al decoder (alternativa a SYNTAX_GENERATION_K)")
    ap.add_argument("--replay-trazas", type=Path,
                    help="repetir el top-10 de las trazas de otra corrida (prueba de generacion, sin encoder)")
    args = ap.parse_args()

    if args.generation_k is not None:
        config.GENERATION_K = args.generation_k

    entrada = args.entrada or (config.SAMPLE_PATH if args.split == "sample" else config.TEST_PATH)
    items = read_jsonl(entrada)
    if args.ids:
        items = [it for it in items if it["id"] in set(args.ids)]
    if args.particion:
        i, n = map(int, args.particion.split("/"))
        items = [it for j, it in enumerate(items) if j % n == i - 1]
    if args.limite:
        items = items[:args.limite]

    llm = config.llm_config()
    experimento = args.experimento or f"{llm['nombre']}_{prompts.PROMPT_VERSION}_k{config.GENERATION_K}"
    regla_abstencion = (
        abstencion.cargar_regla(config.ABSTENCION_CONFIG_PATH)
        if config.ABSTENCION_MODO == "reglas" else None
    )
    # Cada particion (una por maquina) escribe sus propios archivos; unir_entregas.py las junta.
    sufijo = "_p{}de{}".format(*args.particion.split("/")) if args.particion else ""
    if args.salida:
        salida = args.salida
    elif args.split == "test" and not (args.ids or args.limite or args.particion):
        salida = config.SUBMISSION_PATH
    else:
        salida = config.SALIDAS_DIR / f"{args.split}_{experimento}{sufijo}.jsonl"
    trazas = config.TRAZAS_DIR / f"{experimento}{sufijo}.jsonl"
    salida.parent.mkdir(parents=True, exist_ok=True)
    trazas.parent.mkdir(parents=True, exist_ok=True)
    if args.sin_reanudar:
        for p in (salida, trazas):
            p.unlink(missing_ok=True)

    if not args.replay_trazas:
        config.verificar_indice()
    info_llm = modelo.verificar()
    info_indice = json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8"))
    meta = {
        "experimento": experimento, "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": git_commit(), "entrada": entrada.name, "n_items": len(items),
        "decoder": info_llm, "prompt_version": prompts.PROMPT_VERSION,
        "pensar": {"formatos": sorted(config.PENSAR_FORMATOS), "tokens": config.PENSAR_TOKENS,
                   "casos_min_palabras": config.PENSAR_CASOS},
        "texto_libre": {"prompt_tl": config.PROMPT_TL, "seccion_sentencia": config.SECCION_SENTENCIA},
        "retrieval": {"modo": config.MODO_RECUPERACION, "retrieval_k": config.RETRIEVAL_K,
                      "generation_k": config.GENERATION_K, "citar_evidencia": config.CITAR_EVIDENCIA,
                      "lookup": config.lookup_metadata(),
                      "filtro_cita": config.filtro_metadata(), "area": config.area_metadata(),
                      "composicion": config.composicion_metadata(), "metadatos": config.metadatos_metadata(),
                      "agentico": config.agentico_metadata()},
        "indice": {k: info_indice.get(k) for k in ("n_fragmentos", "sha256_chunks", "version_segmentador")}
                  | {"encoder": (info_indice.get("denso") or {}).get("modelo"),
                     "encoder_revision": (info_indice.get("denso") or {}).get("revision")},
        "device_encoder": config.resolver_device(),
        "abstencion": config.abstencion_metadata(),
        "llm_cache": config.LLM_CACHE,
    }
    (config.TRAZAS_DIR / f"{experimento}{sufijo}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    hechos = {r["id"] for r in read_jsonl(salida)} if salida.is_file() else set()
    pendientes = [it for it in items if it["id"] not in hechos]
    print(f"{experimento}: {len(items)} items, {len(hechos & {it['id'] for it in items})} ya hechos, "
          f"{len(pendientes)} por hacer -> {salida.relative_to(config.ROOT).as_posix()}", flush=True)

    if args.replay_trazas:
        from recuperacion.fijo import RetrieverFijo
        retriever = RetrieverFijo(args.replay_trazas)
        meta["replay_trazas"] = args.replay_trazas.as_posix()
        (config.TRAZAS_DIR / f"{experimento}{sufijo}.meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        retriever = cargar(cargar_denso=config.MODO_RECUPERACION != "bm25")
    decoder = Decoder()
    t0 = time.perf_counter()
    with salida.open("a", encoding="utf-8", newline="\n") as fs, trazas.open("a", encoding="utf-8", newline="\n") as ft:
        for n, it in enumerate(pendientes, 1):
            if args.replay_trazas:
                retriever.fijar(it["id"])
            reg, traza = responder(
                it, retriever, decoder, regla_abstencion=regla_abstencion
            )
            fs.write(json.dumps(reg, ensure_ascii=False) + "\n")
            ft.write(json.dumps(traza, ensure_ascii=False) + "\n")
            fs.flush()
            ft.flush()
            media = (time.perf_counter() - t0) / n
            estado = "ABSTIENE " + ",".join(traza["abstencion"]["motivos"]) if reg["abstencion"] else "ok"
            if traza["latencia"]["n_cache"]:
                estado += " (cache)"
            if traza["errores_schema"]:
                estado += f" SCHEMA {traza['errores_schema']}"
            print(f"[{n}/{len(pendientes)}] id={it['id']} {it['formato']:<15} {reg['latencia_ms'] / 1000:5.1f} s  "
                  f"{estado}  (media {media:.1f} s, faltan ~{media * (len(pendientes) - n) / 60:.0f} min)", flush=True)

    # Orden de entrada, sin duplicados, y validacion final de todo el archivo.
    por_id = {r["id"]: r for r in read_jsonl(salida)}
    orden = [it["id"] for it in read_jsonl(entrada) if it["id"] in por_id]
    orden += sorted(set(por_id) - set(orden))
    with salida.open("w", encoding="utf-8", newline="\n") as f:
        for i in orden:
            f.write(json.dumps(por_id[i], ensure_ascii=False) + "\n")
    errores = {i: e for i in orden if (e := postproceso.validar(por_id[i]))}
    n_abst = sum(por_id[i]["abstencion"] for i in orden)
    print(f"\n{len(orden)} registros en {salida.relative_to(config.ROOT).as_posix()}; "
          f"{n_abst} abstenciones; {len(errores)} con errores de schema")
    for i, e in list(errores.items())[:10]:
        print(f"  id={i}: {e}")
    return 1 if errores else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
