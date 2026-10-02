"""PDF -> texto limpio en data_corpus/corpus/<doc_id>.txt.

    python src/ingesta/parsear_pdf.py [--input-dir DIR ...] [--solo DOC_ID ...] [--forzar]

Extrae la capa de texto con PyMuPDF y limpia encabezados/pies, ligaduras y saltos de
linea (ver _texto.py). Detecta PDF por contenido, no por carpeta. Si un PDF trae muy
poco texto por pagina lo marca como posible escaneado.

Los doc_id de OCR_FORZADO (escaneados o con una capa OCR ilegible) se pasan por
Tesseract (`brew install tesseract tesseract-lang`, idioma spa) en lugar de leer su capa
de texto: cada pagina se renderiza a OCR_DPI y va por stdin al binario, como pandoc en
parsear_rtf.py (sin dependencias de pip). La lista es fija para que una corrida sin
flags reproduzca el mismo corpus.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pymupdf  # noqa: E402

import _texto  # noqa: E402

METODO = "extraccion de PDF con PyMuPDF + limpieza de encabezados"
METODO_OCR = "OCR con Tesseract (spa, 300 dpi) + limpieza de encabezados"
MIN_CHARS_POR_PAGINA = 200
OCR_DPI = 300
OCR_HILOS = 4

# Sentencias de la Corte Suprema bajadas de la Relatoria sin capa de texto (SL648-2018,
# SP1945-2019) o con una capa OCR ilegible ("RepdblicadeColombia", caracteres CJK).
OCR_FORZADO = {
    "sentencia_sl_648_2018",
    "sentencia_sp_1945_2019",
    "sentencia_sc_10291_2017",
    "sentencia_sc_18392_2017",
    "sentencia_sc_8453_2016",
}
# Diapositivas con texto en capas (sombra): el orden por coordenadas de PyMuPDF (sort=True)
# intercala las capas palabra por palabra; el orden del flujo del PDF sale limpio.
SIN_ORDENAR = {"doctrina_ompi_agotamiento_patentes_2012"}


def _version_tesseract() -> str:
    if shutil.which("tesseract") is None:
        raise SystemExit("Falta tesseract: brew install tesseract tesseract-lang")
    salida = subprocess.run(["tesseract", "--version"], capture_output=True, text=True, check=True)
    return (salida.stdout or salida.stderr).splitlines()[0]


def _ocr_pagina(png: bytes) -> str:
    # un hilo por proceso: el paralelismo va por paginas y asi la salida no depende de OpenMP
    r = subprocess.run(["tesseract", "stdin", "stdout", "-l", "spa", "--psm", "3"], input=png,
                       capture_output=True, check=True, env={**os.environ, "OMP_THREAD_LIMIT": "1"})
    return r.stdout.decode("utf-8")


def _ocr(doc: pymupdf.Document) -> list[str]:
    imagenes = [p.get_pixmap(dpi=OCR_DPI).tobytes("png") for p in doc]
    with ThreadPoolExecutor(OCR_HILOS) as pool:
        return list(pool.map(_ocr_pagina, imagenes))


def extraer(ruta: Path, formato: str) -> tuple[str, dict]:
    doc_id = _texto.resolver_doc_id(ruta.name)
    ocr = doc_id in OCR_FORZADO
    with pymupdf.open(ruta) as doc:
        paginas = _ocr(doc) if ocr else [p.get_text("text", sort=doc_id not in SIN_ORDENAR) for p in doc]
    texto = _texto.limpiar_paginas(paginas)
    crudo = sum(len(p) for p in paginas)
    info = {"metodo_ingesta": METODO_OCR if ocr else METODO, "n_paginas": len(paginas)}
    if ocr:
        info["herramienta"] = _version_tesseract()
    if crudo / max(len(paginas), 1) < MIN_CHARS_POR_PAGINA:
        info["aviso"] = f"posible PDF escaneado ({crudo // max(len(paginas), 1)} chars/pagina); requiere OCR"
    return texto, info


if __name__ == "__main__":
    raise SystemExit(_texto.ejecutar_cli(__doc__.splitlines()[0], {"pdf"}, extraer))
