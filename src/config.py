"""Rutas del proyecto: repo (codigo + manifest) y carpeta local del corpus.

El corpus procesado y el indice se generan en `<repo>/data_corpus/`, una carpeta
local de cada persona, ignorada por git. El pipeline la reconstruye desde cero a
partir del manifest; al entregar se comprime y se publica aparte.

Estructura de CORPUS_DIR:

    corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
    indice/   index.faiss + chunks.jsonl
    raw/      descargas originales (opcional)

`corpus_manifest.json` NO esta en CORPUS_DIR: vive versionado en la raiz del repo.

Todo el codigo debe importar las rutas de aqui; nadie escribe rutas a mano.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "corpus_manifest.json"
CORPUS_DIR = ROOT / "data_corpus"
CORPUS_TEXTOS = CORPUS_DIR / "corpus"
INDICE_DIR = CORPUS_DIR / "indice"
RAW_DIR = CORPUS_DIR / "raw"
CHUNKS_PATH = INDICE_DIR / "chunks.jsonl"
FAISS_PATH = INDICE_DIR / "index.faiss"


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
