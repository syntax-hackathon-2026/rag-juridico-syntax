"""PDF -> texto limpio en data_corpus/corpus/<doc_id>.txt.

    python src/ingesta/parsear_pdf.py [--input-dir DIR ...] [--solo DOC_ID ...] [--forzar]

Extrae la capa de texto con PyMuPDF (sin OCR) y limpia encabezados/pies, ligaduras
y saltos de linea (ver _texto.py). Detecta PDF por contenido, no por carpeta. Si un
PDF trae muy poco texto por pagina lo marca como posible escaneado (habria que
mandarlo a data/raw/pdf_scan/ y usar OCR, fuera de alcance por ahora).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pymupdf  # noqa: E402

import _texto  # noqa: E402

METODO = "extraccion de PDF con PyMuPDF + limpieza de encabezados"
MIN_CHARS_POR_PAGINA = 200


def extraer(ruta: Path, formato: str) -> tuple[str, dict]:
    with pymupdf.open(ruta) as doc:
        paginas = [p.get_text("text", sort=True) for p in doc]
    texto = _texto.limpiar_paginas(paginas)
    crudo = sum(len(p) for p in paginas)
    info = {"metodo_ingesta": METODO, "n_paginas": len(paginas)}
    if crudo / max(len(paginas), 1) < MIN_CHARS_POR_PAGINA:
        info["aviso"] = f"posible PDF escaneado ({crudo // max(len(paginas), 1)} chars/pagina); requiere OCR"
    return texto, info


if __name__ == "__main__":
    raise SystemExit(_texto.ejecutar_cli(__doc__.splitlines()[0], {"pdf"}, extraer))
