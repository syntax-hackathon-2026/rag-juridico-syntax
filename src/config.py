"""Rutas del proyecto: repo (codigo + manifest) y carpeta local del corpus.

El corpus procesado y el indice se generan en `<repo>/data_corpus/`, una carpeta
local de cada persona, ignorada por git. El pipeline la reconstruye desde cero a
partir del manifest; al entregar se comprime y se publica aparte.

Estructura de CORPUS_DIR:

    corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
    indice/   index.faiss + chunks.jsonl

`corpus_manifest.json` NO esta en CORPUS_DIR: vive versionado en la raiz del repo.

Las fuentes originales (sin procesar) viven aparte, en `<repo>/data/raw_sources/`,
clasificadas por tipo de archivo:

    raw_sources/<tipo>/<doc_id>/<archivo original>

con `tipo` en TIPOS_FUENTE (html, pdf, pdf_escaneado, otros). Las descargas
automaticas y las manuales (p. ej. los PDF de la Constitucion y del CGP) usan la
misma estructura.

Todo el codigo debe importar las rutas de aqui; nadie escribe rutas a mano.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "corpus_manifest.json"
CORPUS_DIR = ROOT / "data_corpus"
CORPUS_TEXTOS = CORPUS_DIR / "corpus"
INDICE_DIR = CORPUS_DIR / "indice"
RAW_SOURCES_DIR = ROOT / "data" / "raw_sources"
TIPOS_FUENTE = ("html", "pdf", "pdf_escaneado", "otros")
CHUNKS_PATH = INDICE_DIR / "chunks.jsonl"
FAISS_PATH = INDICE_DIR / "index.faiss"


def raw_dir(tipo: str, doc_id: str) -> Path:
    """Carpeta de las fuentes originales de un doc_id para un tipo de archivo."""
    if tipo not in TIPOS_FUENTE:
        raise ValueError(f"tipo de fuente desconocido: {tipo!r} (validos: {TIPOS_FUENTE})")
    return RAW_SOURCES_DIR / tipo / doc_id


def raw_dirs_existentes(doc_id: str) -> list[Path]:
    """Carpetas con archivos originales de un doc_id, en cualquier tipo."""
    dirs = (raw_dir(tipo, doc_id) for tipo in TIPOS_FUENTE)
    return [d for d in dirs if d.is_dir() and any(d.iterdir())]


def tipo_por_extension(nombre: str) -> str:
    """Tipo de fuente segun la extension. No distingue PDF escaneado: eso es manual."""
    ext = Path(nombre).suffix.lower()
    if ext in (".html", ".htm"):
        return "html"
    if ext == ".pdf":
        return "pdf"
    return "otros"


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
