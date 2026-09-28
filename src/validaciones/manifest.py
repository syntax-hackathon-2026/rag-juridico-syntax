"""Valida corpus_manifest.json contra la carpeta externa (corpus/ e indice/).

Comprueba el formato descrito en CLAUDE.md y la coherencia entre archivos:
  - campos de raiz y por documento, `doc_id` unico y en snake_case, fechas ISO,
    `areas` del banco, `n_articulos` entero o null, sin rutas absolutas;
  - existe corpus/<doc_id>.<ext> y su sha256 coincide con el del manifest;
  - n_fragmentos coincide con los fragmentos de ese doc_id en indice/chunks.jsonl;
  - todo doc_id de chunks.jsonl esta en el manifest.

Por defecto los placeholders de la plantilla (`<URL>`, `2026-XX-XX`) y los
archivos ausentes son avisos; con --strict (entrega final) son errores.

Uso:
    python src/validaciones/manifest.py
    python src/validaciones/manifest.py --strict
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import config  # noqa: E402
from common import AREAS  # noqa: E402

CAMPOS_RAIZ = ("equipo", "licencia", "fecha_generacion", "enlace_nube", "documentos")
CAMPOS_DOC = ("doc_id", "titulo", "fuente", "url", "fecha_consulta", "areas",
              "n_articulos", "n_fragmentos", "metodo_ingesta", "sha256")
RE_DOC_ID = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_PLACEHOLDER = re.compile(r"<[^>]*>|XX")
RE_RUTA_ABS = re.compile(r"^(/|[A-Za-z]:[\\/]|\\\\)")
AREAS_VALIDAS = set(AREAS) | {a.split(" [")[0] for a in AREAS}


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def fragmentos_por_doc(ruta: Path) -> Counter:
    cuenta: Counter = Counter()
    with ruta.open(encoding="utf-8") as f:
        for linea in f:
            if linea.strip():
                cuenta[json.loads(linea).get("doc_id")] += 1
    return cuenta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--strict", action="store_true",
                    help="placeholders y archivos ausentes cuentan como error (entrega final)")
    ap.add_argument("--manifest", default=str(config.MANIFEST_PATH),
                    help="por defecto corpus_manifest.json de la raiz del repo")
    args = ap.parse_args()

    errores: list[str] = []
    avisos: list[str] = []
    blando = errores if args.strict else avisos

    ruta = Path(args.manifest)
    if not ruta.is_file() or ruta.stat().st_size == 0:
        print(f"ERROR: {ruta.name} no existe o esta vacio (aun no hay documentos registrados)")
        return 1
    try:
        manifest = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: {ruta.name} no es JSON valido: {e}")
        return 1

    for campo in CAMPOS_RAIZ:
        if campo not in manifest:
            errores.append(f"raiz: falta '{campo}'")
    for campo in ("equipo", "licencia", "fecha_generacion", "enlace_nube"):
        valor = str(manifest.get(campo, ""))
        if RE_PLACEHOLDER.search(valor):
            blando.append(f"raiz: '{campo}' es un placeholder: {valor!r}")
    if manifest.get("licencia") not in (None, "CC-BY-4.0"):
        avisos.append(f"raiz: licencia {manifest['licencia']!r} (el equipo acordo CC-BY-4.0)")

    docs = manifest.get("documentos", [])
    ids = [d.get("doc_id") for d in docs]
    for doc_id, n in Counter(ids).items():
        if n > 1:
            errores.append(f"doc_id repetido: {doc_id}")

    chunks_ok = config.CHUNKS_PATH.is_file()
    por_doc = fragmentos_por_doc(config.CHUNKS_PATH) if chunks_ok else Counter()
    if not chunks_ok:
        blando.append(f"no existe {config.CHUNKS_PATH}: se omite la coherencia con el indice")

    for d in docs:
        doc_id = d.get("doc_id", "<sin doc_id>")
        pre = f"{doc_id}:"
        for campo in CAMPOS_DOC:
            if campo not in d:
                errores.append(f"{pre} falta '{campo}'")
        if not RE_DOC_ID.match(str(doc_id)):
            errores.append(f"{pre} doc_id debe ser snake_case minusculas sin tildes")
        for campo in ("titulo", "fuente", "url", "fecha_consulta", "metodo_ingesta", "sha256"):
            if RE_PLACEHOLDER.search(str(d.get(campo, ""))):
                blando.append(f"{pre} '{campo}' es un placeholder: {d.get(campo)!r}")
        if not RE_FECHA.match(str(d.get("fecha_consulta", ""))) \
                and not RE_PLACEHOLDER.search(str(d.get("fecha_consulta", ""))):
            errores.append(f"{pre} fecha_consulta debe ser AAAA-MM-DD")
        areas = d.get("areas")
        if not isinstance(areas, list) or not areas:
            errores.append(f"{pre} areas debe ser una lista no vacia")
        else:
            for a in areas:
                if a not in AREAS_VALIDAS:
                    errores.append(f"{pre} area desconocida: {a!r}")
        n_art = d.get("n_articulos", None)
        if n_art is not None and (not isinstance(n_art, int) or isinstance(n_art, bool)):
            errores.append(f"{pre} n_articulos debe ser entero o null")
        n_frag = d.get("n_fragmentos")
        if not isinstance(n_frag, int) or isinstance(n_frag, bool):
            errores.append(f"{pre} n_fragmentos debe ser entero")
        for campo, valor in d.items():
            if isinstance(valor, str) and RE_RUTA_ABS.match(valor) and campo != "url":
                errores.append(f"{pre} '{campo}' parece una ruta absoluta: {valor!r}")

        archivos = sorted(config.CORPUS_TEXTOS.glob(f"{doc_id}.*")) if config.CORPUS_TEXTOS.is_dir() else []
        if len(archivos) != 1:
            blando.append(f"{pre} se esperaba exactamente 1 archivo corpus/{doc_id}.* y hay {len(archivos)}")
        elif re.fullmatch(r"[0-9a-f]{64}", str(d.get("sha256", ""))):
            real = sha256_archivo(archivos[0])
            if real != d["sha256"]:
                errores.append(f"{pre} sha256 no coincide con {archivos[0].name} (real {real[:12]}...)")
        if chunks_ok and isinstance(n_frag, int) and por_doc.get(doc_id, 0) != n_frag:
            errores.append(f"{pre} n_fragmentos={n_frag} pero chunks.jsonl tiene {por_doc.get(doc_id, 0)}")

    for doc_id in por_doc:
        if doc_id not in ids:
            errores.append(f"chunks.jsonl tiene doc_id ausente del manifest: {doc_id}")

    print(f"Manifest: {len(docs)} documentos | CORPUS_DIR = {config.CORPUS_DIR}")
    for a in avisos:
        print(f"AVISO:  {a}")
    for e in errores:
        print(f"ERROR:  {e}")
    print(f"{len(errores)} errores, {len(avisos)} avisos" + (" (modo estricto)" if args.strict else ""))
    return 1 if errores else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows cp1252
    except AttributeError:
        pass
    sys.exit(main())
