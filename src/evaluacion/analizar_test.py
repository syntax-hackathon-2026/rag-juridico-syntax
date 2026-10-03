"""Huecos del corpus frente a un conjunto de preguntas sin ground truth (las 992 del sabado).

    python src/evaluacion/analizar_test.py                                  # data/test_992.jsonl
    python src/evaluacion/analizar_test.py --entrada data/sample_50.jsonl --experimento simulacro

Solo lee los campos de runtime (responder.entrada_runtime: id, formato, area,
pregunta, opciones) y, para los conteos, tema/sub_tarea/complejidad si vienen;
nunca legal_basis ni respuestas. Corre la recuperacion del pipeline (la misma
consulta, el mismo retriever con prioridad por area) y escribe en
evaluation/test/<experimento>/:

  nombradas_faltantes.csv   cuerpos nombrados en las preguntas (citations.extract) que no
                            estan en el indice, por n_preguntas; entrada de ampliar_desde_citas.py
  nombradas_sin_respaldo.csv  cuerpos nombrados que si estan pero no llegan al top-10, y
                            articulos nombrados que no existen como fragmento (INGESTION)
  confianza.csv             senales por pregunta (abstencion.senales + area del top-10)
  triage/<area>.md          las preguntas de menor confianza por area, para revision humana
  resumen.json              conteos, respaldo nombrado@10 y horas proyectadas

respaldo nombrado@10 = fraccion de cuerpos nombrados en la pregunta que el top-10
respalda (citas.permitidas, el mismo criterio del evaluador). Es la metrica sin
ground truth para decidir KEEP/REVERT de una ampliacion del corpus.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from generacion import abstencion, citas  # noqa: E402
from generacion.responder import entrada_runtime  # noqa: E402
from recuperacion.consulta import consulta_de  # noqa: E402
from recuperacion.referencias import normalizar_articulo, referencias_de  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl  # noqa: E402

CAMPOS_REPORTE = ("tema", "sub_tarea", "complejidad")  # solo para conteos; no entran a la recuperacion
SENTENCIA_CC = re.compile(r"^(C|T|SU)-(\d+)$")
SENTENCIA = re.compile(r"^([A-Z]+)-(\d+)$")


def doc_id_propuesto(cuerpo: tuple) -> tuple[str | None, bool]:
    """(doc_id por convencion, resoluble automaticamente). Ver descargar_fuentes.py y CLAUDE.md."""
    tipo, num, anio = cuerpo
    if tipo in ("ley", "decreto", "acto_legislativo") and num and anio:
        return f"{tipo}_{int(num)}_{anio}", True
    if tipo == "jurisprudencia" and num and anio:
        m = SENTENCIA.match(num)
        if m:
            # Relatoria de la Corte Constitucional: patron fijo. CSJ (SL/SC/SP/STC...) y otras: a mano.
            return f"sentencia_{m.group(1).lower()}_{int(m.group(2))}_{anio}", bool(SENTENCIA_CC.match(num))
    if tipo == "resolucion" and num and anio:
        return f"resolucion_{int(num)}_{anio}", False
    return None, False


def nombre(cuerpo: tuple) -> str:
    return citas.nombre(cuerpo)


def escribir_csv(ruta: Path, filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        if not filas:
            f.write("")
            return
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def main() -> int:
    from recuperacion.retriever import cargar

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrada", type=Path, default=config.TEST_PATH)
    ap.add_argument("--experimento", default=None, help="carpeta en evaluation/test/ (por defecto el nombre de la entrada)")
    ap.add_argument("--limite", type=int)
    ap.add_argument("--por-area", type=int, default=20, help="preguntas por hoja de triage")
    ap.add_argument("--seg-por-pregunta", type=float, default=4.3, help="latencia de generacion para proyectar horas")
    ap.add_argument("--maquinas", type=int, default=1)
    args = ap.parse_args()

    crudos = read_jsonl(args.entrada)[:args.limite] if args.limite else read_jsonl(args.entrada)
    exp = args.experimento or args.entrada.stem
    destino = config.EVALUATION_DIR / "test" / exp
    config.verificar_indice()
    retriever = cargar(cargar_denso=config.MODO_RECUPERACION != "bm25")
    en_indice = {tuple(c["canonico"]) for c in retriever.chunks}
    titulo_doc = {d["doc_id"]: d.get("titulo", d["doc_id"])
                  for d in json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]}

    faltantes: dict[tuple, dict] = {}
    sin_respaldo: list[dict] = []
    filas_conf: list[dict] = []
    reporte = Counter()
    conteos = {k: Counter() for k in ("area", "formato", *CAMPOS_REPORTE)}
    n_nombrados = n_respaldados = 0
    t0 = time.perf_counter()
    for n, crudo in enumerate(crudos, 1):
        for k in CAMPOS_REPORTE:
            if crudo.get(k) is not None:
                conteos[k][crudo[k]] += 1
        item = entrada_runtime(crudo)
        conteos["area"][item.get("area")] += 1
        conteos["formato"][item["formato"]] += 1
        consulta = consulta_de(item)
        top = retriever.retrieve(consulta, k=config.RETRIEVAL_K, modo=config.MODO_RECUPERACION,
                                 area=item.get("area"))
        perm = citas.permitidas([p.texto for p in top])
        sen = abstencion.senales(consulta, top, perm)
        nombrados = citas.cuerpos(consulta)
        for cuerpo in sorted(nombrados, key=str):
            n_nombrados += 1
            if cuerpo in perm:
                n_respaldados += 1
                continue
            if cuerpo not in en_indice:
                doc_id, auto = doc_id_propuesto(cuerpo)
                f = faltantes.setdefault(cuerpo, {"cuerpo": nombre(cuerpo), "tipo": cuerpo[0],
                                                  "numero": cuerpo[1] or "", "anio": cuerpo[2] or "",
                                                  "doc_id_propuesto": doc_id or "", "resoluble_auto": auto,
                                                  "n_preguntas": 0, "ids": [], "areas": Counter()})
                f["n_preguntas"] += 1
                f["ids"].append(item["id"])
                f["areas"][item.get("area")] += 1
            else:
                sin_respaldo.append({"id": item["id"], "area": item.get("area"), "cuerpo": nombre(cuerpo),
                                     "articulo": "", "problema": "en_indice_fuera_top10"})
        for ref in referencias_de(consulta):  # articulo nombrado que no existe como fragmento
            if ref[3] is not None and ref[:3] in en_indice and \
                    (*ref[:3], normalizar_articulo(ref[3])) not in retriever.indice_referencias.por_articulo:
                sin_respaldo.append({"id": item["id"], "area": item.get("area"), "cuerpo": nombre(ref[:3]),
                                     "articulo": ref[3], "problema": "articulo_sin_fragmento"})
        area_match = [p.meta.get("area_match") for p in top]
        filas_conf.append({
            "id": item["id"], "area": item.get("area"), "formato": item["formato"],
            "sub_tarea": crudo.get("sub_tarea") or "",
            "score_top1": sen.get("score_top1"), "margen_top1_top2": sen.get("margen_top1_top2"),
            "frac_en_ambas_ramas": sen.get("frac_en_ambas_ramas"),
            "frac_area_top10": round(sum(bool(a) for a in area_match) / len(top), 3) if top else 0.0,
            "n_cuerpos_top10": sen.get("n_cuerpos_top10"), "n_sentencias_top10": sen.get("n_sentencias_top10"),
            "n_nombrados": len(nombrados), "n_nombrados_respaldados": len(nombrados & perm),
            "doc_top1": top[0].doc_id if top else "",
            "top3": " | ".join(titulo_doc.get(p.doc_id, p.doc_id) for p in top[:3]),
            "pregunta": item["pregunta"],
        })
        reporte["con_nombrados"] += bool(nombrados)
        if n % 100 == 0:
            print(f"[{n}/{len(crudos)}] {(time.perf_counter() - t0) / n:.2f} s/pregunta", flush=True)
    ms_por_pregunta = (time.perf_counter() - t0) * 1000 / max(len(crudos), 1)

    # nombradas_faltantes.csv: mas preguntas primero; desempate por nombre (determinista)
    filas_falt = sorted(faltantes.values(), key=lambda f: (-f["n_preguntas"], f["cuerpo"]))
    for f in filas_falt:
        f["areas"] = ";".join(a for a, _ in f["areas"].most_common() if a)
        f["ids"] = " ".join(map(str, f["ids"]))
    escribir_csv(destino / "nombradas_faltantes.csv", filas_falt)
    escribir_csv(destino / "nombradas_sin_respaldo.csv", sin_respaldo)

    # Confianza: primero lo que nombra algo sin respaldo, luego menos acuerdo entre ramas,
    # menos area en el top-10 y menor score. Solo ordena la revision humana.
    def clave(f: dict) -> tuple:
        return (-(f["n_nombrados"] - f["n_nombrados_respaldados"]), f["frac_en_ambas_ramas"] or 0.0,
                f["frac_area_top10"], f["score_top1"] or 0.0, f["id"])

    filas_conf.sort(key=clave)
    escribir_csv(destino / "confianza.csv", filas_conf)
    por_area: dict[str, list[dict]] = defaultdict(list)
    for f in filas_conf:
        por_area[f["area"] or "sin_area"].append(f)
    for area, filas in sorted(por_area.items()):
        lineas = [f"# Triage: {area}", "",
                  f"{len(filas)} preguntas; las {min(args.por_area, len(filas))} de menor confianza de la recuperacion.",
                  "Objetivo: anotar normas o sentencias que falten en el corpus (temas, no respuestas).",
                  "Formato para ampliar_desde_citas.py: una por linea, p. ej. `Ley 1480 de 2011` o `Sentencia T-123 de 2024`.",
                  ""]
        for f in filas[:args.por_area]:
            lineas += [f"## id {f['id']} ({f['formato']}{', ' + f['sub_tarea'] if f['sub_tarea'] else ''})", "",
                       f["pregunta"], "",
                       f"- top-3: {f['top3']}",
                       f"- acuerdo BM25/denso {f['frac_en_ambas_ramas']}, area en top-10 {f['frac_area_top10']}, "
                       f"nombrados respaldados {f['n_nombrados_respaldados']}/{f['n_nombrados']}",
                       "- falta: ", ""]
        ruta = destino / "triage" / f"{re.sub(r'[^a-z0-9]+', '_', area.lower()).strip('_')}.md"
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text("\n".join(lineas), encoding="utf-8", newline="\n")

    n = len(crudos)
    resumen = {
        "entrada": args.entrada.name, "n_preguntas": n,
        "indice": json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8")).get("sha256_chunks"),
        "retrieval": {"modo": config.MODO_RECUPERACION, "filtro_cita": config.FILTRO_CITA,
                      "area_boost": config.AREA_BOOST, "lookup": config.LOOKUP_MODO},
        "conteos": {k: dict(v.most_common()) for k, v in conteos.items() if v},
        "preguntas_con_nombrados": reporte["con_nombrados"],
        "cuerpos_nombrados": n_nombrados,
        "respaldo_nombrado@10": round(n_respaldados / n_nombrados, 4) if n_nombrados else None,
        "cuerpos_faltantes": len(filas_falt),
        "faltantes_resolubles_auto": sum(f["resoluble_auto"] for f in filas_falt),
        "preguntas_afectadas_por_faltantes": len({i for f in filas_falt for i in f["ids"].split()}),
        "nombrados_sin_respaldo_en_indice": sum(s["problema"] == "en_indice_fuera_top10" for s in sin_respaldo),
        "articulos_sin_fragmento": sum(s["problema"] == "articulo_sin_fragmento" for s in sin_respaldo),
        "ms_recuperacion_por_pregunta": round(ms_por_pregunta, 1),
        "horas_proyectadas": round(n * args.seg_por_pregunta / 3600 / args.maquinas, 2),
        "supuesto_proyeccion": {"seg_por_pregunta": args.seg_por_pregunta, "maquinas": args.maquinas},
    }
    (destino / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in resumen.items() if k != "conteos"}, ensure_ascii=False, indent=2))
    print(f"-> {destino.relative_to(config.ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
