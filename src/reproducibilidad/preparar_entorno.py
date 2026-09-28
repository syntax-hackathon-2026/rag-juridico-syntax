"""Crea el entorno virtual del proyecto (.venv) e instala requirements.txt.

Portable Windows/Mac/Linux, solo stdlib. Usa el interprete con el que se
ejecuta (objetivo: Python 3.11) y al final corre verificar_deps.py dentro del
entorno para confirmar que todo import de src/ esta declarado.

Uso:
    python3.11 src/reproducibilidad/preparar_entorno.py
    python3.11 src/reproducibilidad/preparar_entorno.py --evaluador   # + deps del juez (ragas)
    python3.11 src/reproducibilidad/preparar_entorno.py --recrear     # borra .venv antes
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENV = ROOT / ".venv"
PYTHON_OBJETIVO = (3, 11)


def venv_python() -> Path:
    # Unica distincion de plataforma inevitable: el layout de venv.
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(*cmd: str | Path) -> None:
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, cwd=ROOT)


def has_requirements(path: Path) -> bool:
    return path.exists() and any(
        l.split("#", 1)[0].strip() for l in path.read_text(encoding="utf-8").splitlines()
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--evaluador", action="store_true",
                    help="instala tambien scripts/requirements-evaluador.txt")
    ap.add_argument("--recrear", action="store_true", help="borra .venv y lo crea de cero")
    args = ap.parse_args()

    if sys.version_info[:2] != PYTHON_OBJETIVO:
        print(f"aviso: Python {sys.version_info.major}.{sys.version_info.minor} "
              f"(objetivo {PYTHON_OBJETIVO[0]}.{PYTHON_OBJETIVO[1]}); las versiones fijadas "
              "pueden no tener wheels para este interprete")

    if args.recrear and VENV.exists():
        shutil.rmtree(VENV)
    if not venv_python().exists():
        print(f"creando {VENV.relative_to(ROOT)}")
        venv.EnvBuilder(with_pip=True).create(VENV)

    py = venv_python()
    run(py, "-m", "pip", "install", "--upgrade", "pip")
    for req in [ROOT / "requirements.txt"] + ([ROOT / "scripts/requirements-evaluador.txt"] if args.evaluador else []):
        if has_requirements(req):
            run(py, "-m", "pip", "install", "-r", req.relative_to(ROOT).as_posix())
        else:
            print(f"{req.relative_to(ROOT).as_posix()} vacio, nada que instalar")

    activar = r".venv\Scripts\activate" if os.name == "nt" else "source .venv/bin/activate"
    if subprocess.run([str(py), "src/reproducibilidad/verificar_deps.py"], cwd=ROOT).returncode:
        print(f"\nentorno creado, pero requirements.txt no cubre todos los imports de src/ (ver arriba). Activar con: {activar}")
        return 1
    print(f"\nlisto. Activar con: {activar}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
