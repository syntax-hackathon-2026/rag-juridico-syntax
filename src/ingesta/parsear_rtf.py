"""RTF (y DOCX con extension .rtf) -> texto limpio en data_corpus/corpus/<doc_id>.txt.

    python src/ingesta/parsear_rtf.py [--input-dir DIR ...] [--solo DOC_ID ...] [--forzar]

Convierte con pandoc (`brew install pandoc`). Detecta el formato por contenido: en
data/raw/rtf/ hay archivos .rtf que en realidad son DOCX. Se conservan los
encabezados de relatoria de las sentencias (p. ej. `EXCEPCION DE PLEITO PENDIENTE-...`).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _texto  # noqa: E402

METODO = "conversion de RTF/DOCX con pandoc"


def _version_pandoc() -> str:
    if shutil.which("pandoc") is None:
        raise SystemExit("Falta pandoc: brew install pandoc")
    salida = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True)
    return salida.stdout.splitlines()[0]


def extraer(ruta: Path, formato: str) -> tuple[str, dict]:
    r = subprocess.run(
        ["pandoc", "-f", formato, "-t", "plain", "--wrap=none", str(ruta)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise RuntimeError(f"pandoc fallo: {r.stderr.strip()[:200]}")
    texto = _texto.limpiar_texto(r.stdout)
    info = {"metodo_ingesta": METODO, "herramienta": _version_pandoc()}
    if len(texto) < 2000:
        info["aviso"] = f"texto muy corto ({len(texto)} chars)"
    return texto, info


if __name__ == "__main__":
    _version_pandoc()
    raise SystemExit(_texto.ejecutar_cli(__doc__.splitlines()[0], {"rtf", "docx"}, extraer))
