"""Amplia el corpus desde una lista de referencias: resolver -> descargar -> parsear -> validar [-> indexar].

    # automatico: los cuerpos que nombran las preguntas y no estan (analizar_test.py)
    python src/ingesta/ampliar_desde_citas.py evaluation/test/<exp>/nombradas_faltantes.csv --min-preguntas 1
    # lista a mano (triage): una referencia por linea, areas opcionales tras ';'
    #   Ley 2294 de 2023 ; Derecho administrativo
    #   Sentencia T-123 de 2024
    python src/ingesta/ampliar_desde_citas.py lista.txt --area-defecto "Derecho constitucional"
    # descargas manuales (cola de no resueltos): CSV doc_id,titulo,fuente,url,areas,archivo
    #   con el archivo ya guardado en data/raw/pdf/ (o rtf/)
    python src/ingesta/ampliar_desde_citas.py --manual manual.csv
    # cualquiera de los anteriores + rehacer manifest e indice (CUDA si SYNTAX_DEVICE=cuda)
    python src/ingesta/ampliar_desde_citas.py ... --indexar --batch 64
    python src/ingesta/ampliar_desde_citas.py ... --plan        # solo resolver y listar, sin tocar nada

Reutiliza las reglas de descargar_fuentes.resolver (Senado y espejos de Avance
Juridico para leyes y decretos, relatoria de la Corte Constitucional para C/T/SU).
Lo que no tiene regla (Corte Suprema, Consejo de Estado, resoluciones) o no se
encuentra va a no_resueltos.csv: es la cola de busqueda manual, no se adivinan URLs.
Comprobaciones automaticas despues de parsear: norma con articulos detectados y
sin avisos; sentencia de la relatoria completa. Lo que falla se marca `error` en
fuentes_descargadas.json, sale de `_adicionales` y no entra al manifest.

Cada documento nuevo lleva en `_adicionales` las areas de las preguntas que lo
nombran (prioridad por area del retriever) y la nota "ampliacion sabado". Las
sentencias nuevas se agregan al grupo `sentencias` de solo_por_cita.json (se
recuperan solo si la pregunta las nombra, igual que el resto del lote).
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from ingesta import descargar_fuentes as df  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

NOTA = f"ampliacion sabado ({date.today().isoformat()}): dirigida por las preguntas del test"
TIPOS_CON_NUMERO = ("ley", "decreto", "acto_legislativo", "jurisprudencia", "resolucion")
PY = sys.executable


def _cuerpos_de_texto(linea: str) -> list[tuple]:
    return sorted(citations.bodies(citations.extract(linea)), key=str)


def leer_entrada(ruta: Path, area_defecto: str | None, min_preguntas: int) -> list[dict]:
    """-> [{cuerpo, areas, n_preguntas, ids}] sin repetir cuerpos."""
    filas: dict[tuple, dict] = {}
    if ruta.suffix.lower() == ".csv":
        with ruta.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if int(r.get("n_preguntas") or 1) < min_preguntas:
                    continue
                cuerpo = (r["tipo"], r["numero"] or None, r["anio"] or None)
                areas = [a for a in (r.get("areas") or "").split(";") if a] or ([area_defecto] if area_defecto else [])
                filas[cuerpo] = {"cuerpo": cuerpo, "areas": areas, "n_preguntas": int(r.get("n_preguntas") or 1),
                                 "ids": r.get("ids", "")}
    else:
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.split("#", 1)[0].strip()
            if not linea:
                continue
            ref, _, areas_txt = linea.partition(";")
            areas = [a.strip() for a in areas_txt.split(",") if a.strip()] or ([area_defecto] if area_defecto else [])
            cuerpos = _cuerpos_de_texto(ref)
            if not cuerpos:
                filas[("sin_extraer", ref.strip(), None)] = {"cuerpo": ("sin_extraer", ref.strip(), None),
                                                              "areas": areas, "n_preguntas": 0, "ids": ""}
            for c in cuerpos:
                filas.setdefault(c, {"cuerpo": c, "areas": areas, "n_preguntas": 0, "ids": ""})
    return list(filas.values())


def cargar_override() -> dict:
    return json.loads(df.OVERRIDE_PATH.read_text(encoding="utf-8"))


def guardar_json(ruta: Path, datos: dict) -> None:
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def correr(etapa: str, args: list[str], tiempos: dict) -> int:
    t0 = time.perf_counter()
    print(f"\n=== {etapa}: {' '.join(args)}", flush=True)
    rc = subprocess.run([PY, *args], cwd=config.ROOT).returncode
    tiempos[etapa] = round(time.perf_counter() - t0, 1)
    print(f"=== {etapa}: exit {rc}, {tiempos[etapa]} s", flush=True)
    return rc


def normalizar_areas(areas: list[str], conocidas: set[str]) -> tuple[list[str], list[str]]:
    """Nombre exacto del banco (la prioridad por area compara strings); acepta un prefijo unico."""
    ok, malas = [], []
    for a in areas:
        candidatas = [c for c in conocidas if c.lower() == a.lower()] or \
                     [c for c in conocidas if c.lower().startswith(a.lower())]
        (ok.append(candidatas[0]) if len(candidatas) == 1 else malas.append(a))
    return list(dict.fromkeys(ok)), malas


def resolver(filas: list[dict], existentes: set[str],
             conocidas: set[str]) -> tuple[list[tuple[dict, df.Objetivo]], list[dict]]:
    a_bajar, descartes = [], []
    vistos: set[str] = set()
    for fila in filas:
        fila["areas"], malas = normalizar_areas(fila["areas"], conocidas)
        if malas:
            descartes.append({"cuerpo": " ".join(x for x in fila["cuerpo"] if x), "n_preguntas": fila["n_preguntas"],
                              "ids": fila["ids"], "doc_id": "", "motivo": f"area desconocida o ambigua: {malas}"})
            continue
        tipo, num, anio = fila["cuerpo"]
        base = {"cuerpo": " ".join(x for x in fila["cuerpo"] if x), "n_preguntas": fila["n_preguntas"],
                "ids": fila["ids"]}
        if tipo == "sin_extraer":
            descartes.append({**base, "doc_id": "", "motivo": "citations.extract no reconoce la referencia"})
            continue
        if tipo not in TIPOS_CON_NUMERO or not (num and anio):
            descartes.append({**base, "doc_id": "", "motivo": f"cuerpo sin numero/anio ({tipo}): codigo o norma "
                              "que deberia estar ya; revisar a mano"})
            continue
        if not fila["areas"]:
            descartes.append({**base, "doc_id": "", "motivo": "sin area (usar '; area' o --area-defecto)"})
            continue
        obj = df.resolver({"canonico": [tipo, num, anio], "areas": fila["areas"],
                           "items_del_banco": fila["n_preguntas"], "norma": base["cuerpo"], "donde_buscar": ""})
        if obj.doc_id in existentes or obj.doc_id in vistos:
            descartes.append({**base, "doc_id": obj.doc_id, "motivo": "ya en el corpus o en _adicionales"})
            continue
        if obj.estado == "sin_resolver":
            descartes.append({**base, "doc_id": obj.doc_id, "motivo": f"sin regla de URL ({obj.fuente or tipo}): "
                              "busqueda manual -> --manual"})
            continue
        vistos.add(obj.doc_id)
        a_bajar.append((fila, obj))
    return a_bajar, descartes


def validar_parseo(doc_id: str, es_sentencia: bool, parseo: dict) -> str | None:
    """Motivo de rechazo, o None si el texto parece completo."""
    info = parseo.get(doc_id)
    if not info or not (config.CORPUS_TEXTOS / f"{doc_id}.txt").is_file():
        return "sin texto parseado"
    if info.get("aviso"):
        return f"aviso del parser: {info['aviso']}"
    if not es_sentencia and info.get("extractor") == "avance_juridico" and not info.get("n_articulos_detectados"):
        return "norma sin articulos detectados"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("entrada", type=Path, nargs="?", help="nombradas_faltantes.csv o lista .txt")
    ap.add_argument("--manual", type=Path, help="CSV doc_id,titulo,fuente,url,areas,archivo de descargas manuales")
    ap.add_argument("--min-preguntas", type=int, default=1, help="solo cuerpos nombrados por >= N preguntas (CSV)")
    ap.add_argument("--area-defecto", help="area para las lineas sin area")
    ap.add_argument("--plan", action="store_true", help="solo resolver y listar; no escribe nada")
    ap.add_argument("--indexar", action="store_true", help="despues: manifest + segmentar + indice + validar")
    ap.add_argument("--batch", type=int, default=64, help="batch del encoder para construir_indice.py")
    ap.add_argument("--salida", type=Path, help="carpeta de los reportes (por defecto la de la entrada)")
    args = ap.parse_args()
    if not (args.entrada or args.manual or args.indexar):
        ap.error("falta la entrada, --manual o --indexar")

    destino = args.salida or (args.entrada or args.manual or config.ROOT / "salidas").parent
    destino.mkdir(parents=True, exist_ok=True)
    override = cargar_override()
    adicionales = override.setdefault("_adicionales", [])
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    existentes = {d["doc_id"] for d in manifest["documentos"]} | {a["doc_id"] for a in adicionales}
    conocidas = {a for d in manifest["documentos"] for a in d.get("areas") or ()}

    nuevos: list[tuple[dict, df.Objetivo]] = []
    descartes: list[dict] = []
    if args.entrada:
        filas = leer_entrada(args.entrada, args.area_defecto, args.min_preguntas)
        nuevos, descartes = resolver(filas, existentes, conocidas)
    manuales: list[dict] = []
    if args.manual:
        with args.manual.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["doc_id"] in existentes:
                    descartes.append({"cuerpo": r["titulo"], "n_preguntas": "", "ids": "", "doc_id": r["doc_id"],
                                      "motivo": "ya en el corpus o en _adicionales"})
                    continue
                if not (config.RAW_DIR / "pdf" / r["archivo"]).is_file() and \
                        not (config.RAW_DIR / "rtf" / r["archivo"]).is_file():
                    descartes.append({"cuerpo": r["titulo"], "n_preguntas": "", "ids": "", "doc_id": r["doc_id"],
                                      "motivo": f"no esta data/raw/pdf|rtf/{r['archivo']}"})
                    continue
                areas, malas = normalizar_areas([a.strip() for a in r["areas"].split(";") if a.strip()], conocidas)
                if malas or not areas:
                    descartes.append({"cuerpo": r["titulo"], "n_preguntas": "", "ids": "", "doc_id": r["doc_id"],
                                      "motivo": f"area desconocida, ambigua o vacia: {malas}"})
                    continue
                manuales.append({**r, "areas": areas})

    print(f"{len(nuevos)} por descargar, {len(manuales)} manuales, {len(descartes)} descartados")
    for fila, obj in nuevos:
        print(f"  + {obj.doc_id:<32} {obj.fuente:<40} {obj.url}  areas={fila['areas']}")
    for d in descartes:
        print(f"  - {d['doc_id'] or d['cuerpo']:<32} {d['motivo']}")
    if args.plan:
        return 0

    # 1. _adicionales (+ mapa de archivos para los manuales)
    for fila, obj in nuevos:
        adicionales.append({"doc_id": obj.doc_id, "titulo": obj.titulo, "fuente": obj.fuente, "url": obj.url,
                            "areas": fila["areas"], "nota": NOTA})
    if manuales:
        mapa = df._leer_mapa()
        for r in manuales:
            mapa[r["archivo"]] = r["doc_id"]
            adicionales.append({"doc_id": r["doc_id"], "titulo": r["titulo"], "fuente": r["fuente"], "url": r["url"],
                                "areas": r["areas"], "nota": NOTA + " (descarga manual)"})
        df._guardar_mapa(mapa)
    guardar_json(df.OVERRIDE_PATH, override)

    tiempos: dict[str, float] = {}
    ids = [o.doc_id for _, o in nuevos] + [r["doc_id"] for r in manuales]
    resultado: list[dict] = []
    if ids:
        # 2. descargar (o solo registrar los manuales) y parsear
        correr("descargar", ["src/ingesta/descargar_fuentes.py", "--solo", *ids], tiempos)
        registro = df.cargar_registro()
        bajados = [i for i in ids if registro.get(i, {}).get("estado") == "descargado"]
        por_formato = {"html": [], "pdf": [], "rtf": []}
        for i in bajados:
            por_formato.get(registro[i].get("tipo_fuente") or "html", por_formato["html"]).append(i)
        for formato, lista in por_formato.items():
            if lista:
                correr(f"parsear_{formato}", [f"src/ingesta/parsear_{formato}.py", "--solo", *lista], tiempos)

        # 3. comprobaciones; lo que falla sale de _adicionales y del manifest
        parseo = json.loads(config.PARSEO_PATH.read_text(encoding="utf-8")) if config.PARSEO_PATH.is_file() else {}
        sentencias = {o.doc_id for _, o in nuevos if o.canonico and o.canonico[0] == "jurisprudencia"}
        sentencias |= {r["doc_id"] for r in manuales if r["doc_id"].startswith("sentencia_")}
        rechazados: dict[str, str] = {}
        for i in ids:
            estado = registro.get(i, {}).get("estado", "sin registro")
            if estado != "descargado":
                rechazados[i] = f"{estado}: {registro.get(i, {}).get('nota', '')}"
            elif motivo := validar_parseo(i, i in sentencias, parseo):
                rechazados[i] = motivo
                registro[i]["estado"] = "error"
                registro[i]["nota"] = f"ampliar_desde_citas: {motivo}"
                (config.CORPUS_TEXTOS / f"{i}.txt").unlink(missing_ok=True)
        if rechazados:
            df.guardar_registro(registro)
            override["_adicionales"] = [a for a in adicionales if a["doc_id"] not in rechazados]
            guardar_json(df.OVERRIDE_PATH, override)
        aceptados = [i for i in ids if i not in rechazados]
        nuevas_sentencias = sorted(set(aceptados) & sentencias)
        if nuevas_sentencias:
            registro_filtro = json.loads(config.SOLO_POR_CITA_PATH.read_text(encoding="utf-8"))
            registro_filtro["sentencias"] = sorted(set(registro_filtro["sentencias"]) | set(nuevas_sentencias))
            registro_filtro["ampliacion_sabado"] = sorted(set(registro_filtro.get("ampliacion_sabado", []))
                                                          | set(nuevas_sentencias))
            guardar_json(config.SOLO_POR_CITA_PATH, registro_filtro)
        info = {o.doc_id: (f, o) for f, o in nuevos}
        for i in ids:
            fila, obj = info.get(i, ({"n_preguntas": "", "ids": "", "areas": []}, None))
            resultado.append({"doc_id": i, "estado": "aceptado" if i in aceptados else "rechazado",
                              "motivo": rechazados.get(i, ""), "url": registro.get(i, {}).get("url", ""),
                              "n_preguntas": fila["n_preguntas"], "ids": fila["ids"]})
            if i in rechazados and obj is not None:
                descartes.append({"cuerpo": obj.titulo, "n_preguntas": fila["n_preguntas"], "ids": fila["ids"],
                                  "doc_id": i, "motivo": rechazados[i]})
        print(f"\n{len(aceptados)} aceptados, {len(rechazados)} rechazados; "
              f"{len(nuevas_sentencias)} sentencias nuevas en solo_por_cita.json")
        for i, m in rechazados.items():
            print(f"  x {i:<32} {m}")

    marca = time.strftime("%H%M%S")
    for nombre, filas in ((f"ampliacion_{marca}.csv", resultado), (f"no_resueltos_{marca}.csv", descartes)):
        if filas:
            with (destino / nombre).open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
                w.writeheader()
                w.writerows(filas)
            print(f"-> {(destino / nombre).as_posix()}")

    # 4. manifest e indice (orden de CLAUDE.md para un documento nuevo)
    if args.indexar:
        pasos = [("manifest", ["src/ingesta/generar_manifest.py"]),
                 ("segmentar", ["src/indexacion/segmentar.py"]),
                 ("manifest2", ["src/ingesta/generar_manifest.py"]),
                 ("indice", ["src/indexacion/construir_indice.py", "--batch", str(args.batch)]),
                 ("validar", ["src/validaciones/manifest.py"])]
        for etapa, cmd in pasos:
            if correr(etapa, cmd, tiempos) != 0:
                print(f"FALLO en {etapa}; el indice puede estar a medias: no publicar ni generar con el.")
                print(json.dumps(tiempos))
                return 1
    if tiempos:
        print("tiempos (s):", json.dumps(tiempos))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    raise SystemExit(main())
