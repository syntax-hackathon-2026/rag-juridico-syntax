"""Rutas del proyecto: repo (codigo + manifest) y carpeta externa (corpus + indice).

El corpus procesado y el indice viven fuera del repo, en una carpeta compartida
(OneDrive) cuya ruta es distinta en cada maquina. Se define en `CORPUS_DIR`:

    1. variable de entorno CORPUS_DIR, o
    2. archivo `.env` en la raiz del repo (una linea `CORPUS_DIR=...`), o
    3. por defecto `<repo>/data_corpus` (ignorado por git; es lo que ve un
       contenedor limpio, donde el pipeline reconstruye todo desde el manifest).

Estructura esperada dentro de CORPUS_DIR:

    corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
    indice/   index.faiss + chunks.jsonl
    raw/      descargas originales (opcional)

`corpus_manifest.json` NO esta en CORPUS_DIR: vive versionado en la raiz del repo.

Todo el codigo debe importar las rutas de aqui; nadie escribe rutas a mano.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "corpus_manifest.json"
DEFAULT_CORPUS_DIR = ROOT / "data_corpus"


def _leer_env(ruta: Path) -> dict[str, str]:
    """Lee lineas KEY=VALOR de un .env (comillas opcionales, # comenta).

    No interpreta secuencias de escape: `C:\\Users\\ana\\OneDrive` se conserva tal cual.
    """
    valores: dict[str, str] = {}
    if not ruta.is_file():
        return valores
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.replace("export", "", 1).strip()
        valores[clave] = valor.strip().strip('"').strip("'")
    return valores


def _resolver_corpus_dir() -> Path:
    bruto = os.environ.get("CORPUS_DIR", "").strip()
    if not bruto:
        bruto = _leer_env(ROOT / ".env").get("CORPUS_DIR", "").strip()
    if not bruto:
        return DEFAULT_CORPUS_DIR
    ruta = Path(os.path.expandvars(bruto)).expanduser()
    if not ruta.is_absolute():
        ruta = ROOT / ruta
    return ruta


CORPUS_DIR = _resolver_corpus_dir()
CORPUS_TEXTOS = CORPUS_DIR / "corpus"
INDICE_DIR = CORPUS_DIR / "indice"
RAW_DIR = CORPUS_DIR / "raw"
CHUNKS_PATH = INDICE_DIR / "chunks.jsonl"
FAISS_PATH = INDICE_DIR / "index.faiss"


def exigir_corpus_dir() -> Path:
    """Devuelve CORPUS_DIR o termina con un mensaje accionable si no existe."""
    if not CORPUS_DIR.is_dir():
        raise SystemExit(
            f"CORPUS_DIR no existe: {CORPUS_DIR}\n"
            "Definir CORPUS_DIR en .env (ver .env.example) apuntando a la carpeta "
            "sincronizada de OneDrive, y marcarla 'mantener siempre en este dispositivo'."
        )
    return CORPUS_DIR


def contar_chunks() -> int:
    """Numero de fragmentos en chunks.jsonl (lineas no vacias)."""
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        return sum(1 for linea in f if linea.strip())


def verificar_indice() -> int:
    """Comprueba que indice/ este completo y coherente; devuelve el numero de fragmentos.

    Protege contra leer un indice a medio sincronizar: chunks.jsonl e index.faiss
    deben existir y tener el mismo numero de vectores/fragmentos.
    """
    for ruta in (CHUNKS_PATH, FAISS_PATH):
        if not ruta.is_file() or ruta.stat().st_size == 0:
            raise SystemExit(
                f"Falta o esta vacio: {ruta}\n"
                "Si OneDrive aun sincroniza, esperar; si no, reconstruir el indice."
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
            f"chunks.jsonl {n_chunks} fragmentos. Posible sincronizacion a medias "
            "o conflicto de OneDrive."
        )
    return n_chunks
