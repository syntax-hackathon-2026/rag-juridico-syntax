"""Rutas del proyecto: repo (codigo + manifest) y carpeta local del corpus.

El corpus procesado y el indice se generan en `<repo>/data_corpus/`, una carpeta
local de cada persona, ignorada por git. El pipeline la reconstruye desde cero a
partir del manifest; al entregar se comprime y se publica aparte.

Estructura de CORPUS_DIR:

    corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
    indice/   index.faiss + chunks.jsonl

`corpus_manifest.json` NO esta en CORPUS_DIR: vive versionado en la raiz del repo.

Las fuentes originales (sin procesar) viven en `<repo>/data/raw/` (ignorada por
git, regenerable con src/ingesta/descargar_fuentes.py), por formato:

    raw/html/<doc_id>/<archivo original>   descargas automaticas (Senado en partes
                                           <base>.html, <base>_pr001.html, ...)
    raw/pdf/<archivo original>             PDF manuales o descargados
    raw/rtf/<archivo original>             RTF/DOCX manuales

Los PDF/RTF se asocian a su doc_id en data/mapa_archivos.json; las carpetas de
raw/html/ ya se llaman como el doc_id.

Todo el codigo debe importar las rutas de aqui; nadie escribe rutas a mano.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "corpus_manifest.json"
CORPUS_DIR = ROOT / "data_corpus"
CORPUS_TEXTOS = CORPUS_DIR / "corpus"
INDICE_DIR = CORPUS_DIR / "indice"
RAW_DIR = ROOT / "data" / "raw"  # originales por formato (html/, pdf/, rtf/); leen los parsers de src/ingesta/parsear_*.py
RAW_HTML_DIR = RAW_DIR / "html"
PARSEO_PATH = CORPUS_DIR / "parseo.json"  # inventario del parseo, fuera de corpus/ (que se publica tal cual)
MAPA_ARCHIVOS_PATH = ROOT / "data" / "mapa_archivos.json"  # archivo original -> doc_id (versionado)
CHUNKS_PATH = INDICE_DIR / "chunks.jsonl"
FAISS_PATH = INDICE_DIR / "index.faiss"


def raw_html_dir(doc_id: str) -> Path:
    """Carpeta con las paginas HTML originales de un doc_id."""
    return RAW_HTML_DIR / doc_id


def docs_en_raw() -> set[str]:
    """doc_id que ya tienen algun original en data/raw/ (HTML o PDF/RTF mapeado)."""
    import json
    import unicodedata

    nfc = lambda s: unicodedata.normalize("NFC", s)  # macOS entrega nombres en NFD
    docs = {d.name for d in RAW_HTML_DIR.glob("*") if d.is_dir() and any(d.iterdir())}
    if MAPA_ARCHIVOS_PATH.is_file():
        mapa = json.loads(MAPA_ARCHIVOS_PATH.read_text(encoding="utf-8"))
        presentes = {nfc(f.name) for sub in ("pdf", "rtf") for f in (RAW_DIR / sub).glob("*")}
        docs |= {doc for nombre, doc in mapa.items() if nfc(nombre) in presentes}
    return docs


def contar_chunks() -> int:
    """Numero de fragmentos en chunks.jsonl (lineas no vacias)."""
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        return sum(1 for linea in f if linea.strip())


def verificar_indice() -> int:
    """Comprueba que indice/ este completo y coherente; devuelve el numero de fragmentos.

    Protege contra leer un indice a medio construir: chunks.jsonl e index.faiss
    deben existir y tener el mismo numero de vectores/fragmentos.
    """
    for ruta in (CHUNKS_PATH, FAISS_PATH):
        if not ruta.is_file() or ruta.stat().st_size == 0:
            raise SystemExit(
                f"Falta o esta vacio: {ruta}\n"
                "Reconstruir el indice."
            )
    n_chunks = contar_chunks()
    try:
        import faiss  # type: ignore
    except ImportError:
        return n_chunks
    n_vectores = faiss.read_index(str(FAISS_PATH)).ntotal
    if n_vectores != n_chunks:
        raise SystemExit(
            f"Indice incoherente: index.faiss tiene {n_vectores} vectores y "
            f"chunks.jsonl {n_chunks} fragmentos. Reconstruir el indice."
        )
    return n_chunks
