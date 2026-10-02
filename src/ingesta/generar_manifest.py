"""Genera corpus_manifest.json desde el registro de fuentes y el parseo.

    python src/ingesta/generar_manifest.py            # escribe corpus_manifest.json
    python src/ingesta/generar_manifest.py --revisar  # solo muestra que cambiaria

Fuentes de cada campo:
  - titulo, fuente, url, fecha_consulta, areas: data/fuentes_descargadas.json (estado
    `descargado`, en su orden: semilla por items_del_banco y luego _adicionales);
  - metodo_ingesta, sha256: data_corpus/parseo.json (sha256 de corpus/<doc_id>.txt);
  - n_fragmentos: data_corpus/indice/chunks.jsonl (0 si aun no se segmento);
  - n_articulos: el valor ya registrado en el manifest (revisado a mano: en normas
    modificatorias no coincide con lo que detecta el segmentador). Si no hay, el conteo
    de articulos base de resumen_indice.json; null en sentencias y documentos.
  - equipo, licencia, enlace_nube: se conservan del manifest actual.

Un doc_id descargado sin .txt en corpus/ es error (falta parsearlo). Salida en JSON con
indentacion de 2, UTF-8 y "\\n"; despues correr src/validaciones/manifest.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "src" / "indexacion"))
import cabeceras  # noqa: E402

RAIZ_FIJA = {"equipo": "Syntax", "licencia": "CC-BY-4.0", "enlace_nube": "<URL>"}


def _leer(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}


def fragmentos_por_doc() -> Counter:
    cuenta: Counter = Counter()
    if config.CHUNKS_PATH.is_file():
        with config.CHUNKS_PATH.open(encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    cuenta[json.loads(linea)["doc_id"]] += 1
    return cuenta


def n_articulos(doc_id: str, previo: dict, resumen: dict) -> int | None:
    if cabeceras.tipo(cabeceras.canonico(doc_id)) in ("sentencia", "documento"):
        return None
    if isinstance(previo.get("n_articulos"), int):
        return previo["n_articulos"]
    base = resumen.get(doc_id, {}).get("articulos_base")
    return base if isinstance(base, int) and base else None


def generar() -> tuple[dict, list[str]]:
    registro = _leer(config.FUENTES_PATH).get("documentos", [])
    parseo = _leer(config.PARSEO_PATH)
    actual = _leer(config.MANIFEST_PATH)
    previos = {d["doc_id"]: d for d in actual.get("documentos", [])}
    resumen = _leer(config.RESUMEN_INDICE_PATH).get("documentos", {})
    frags = fragmentos_por_doc()

    errores, docs = [], []
    for r in registro:
        if r["estado"] != "descargado":
            continue
        d = r["doc_id"]
        p = parseo.get(d)
        if not p or not (config.CORPUS_TEXTOS / f"{d}.txt").is_file():
            errores.append(f"{d}: descargado pero sin corpus/{d}.txt (falta parsearlo)")
            continue
        docs.append({
            "doc_id": d,
            "titulo": r["titulo"],
            "fuente": r["fuente"],
            "url": r["url"],
            "fecha_consulta": r["fecha_consulta"],
            "areas": r["areas"],
            "n_articulos": n_articulos(d, previos.get(d, {}), resumen),
            "n_fragmentos": frags.get(d, 0),
            "metodo_ingesta": p["metodo_ingesta"],
            "sha256": p["sha256"],
        })

    raiz = {k: actual.get(k, v) for k, v in RAIZ_FIJA.items()}
    cambio = [d for d in docs if previos.get(d["doc_id"]) != d] or set(previos) != {d["doc_id"] for d in docs}
    fecha = dt.date.today().isoformat() if cambio else actual.get("fecha_generacion")
    manifest = {
        "equipo": raiz["equipo"],
        "licencia": raiz["licencia"],
        "fecha_generacion": fecha,
        "enlace_nube": raiz["enlace_nube"],
        "n_documentos": len(docs),
        "n_fragmentos": sum(d["n_fragmentos"] for d in docs),
        "documentos": docs,
    }
    return manifest, errores


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--revisar", action="store_true", help="no escribir; solo listar los cambios")
    args = ap.parse_args()

    manifest, errores = generar()
    for e in errores:
        print(f"ERROR {e}")
    previos = {d["doc_id"]: d for d in _leer(config.MANIFEST_PATH).get("documentos", [])}
    nuevos = [d["doc_id"] for d in manifest["documentos"] if d["doc_id"] not in previos]
    cambiados = [d["doc_id"] for d in manifest["documentos"]
                 if d["doc_id"] in previos and previos[d["doc_id"]] != d]
    quitados = sorted(set(previos) - {d["doc_id"] for d in manifest["documentos"]})
    print(f"{manifest['n_documentos']} documentos, {manifest['n_fragmentos']} fragmentos; "
          f"{len(nuevos)} nuevos, {len(cambiados)} cambiados, {len(quitados)} quitados")
    for etiqueta, ids in (("nuevos", nuevos), ("cambiados", cambiados), ("quitados", quitados)):
        if ids:
            print(f"  {etiqueta}: {', '.join(ids)}")
    if errores:
        return 1
    if not args.revisar:
        config.MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8", newline="\n")
        print(f"Escrito {config.MANIFEST_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
