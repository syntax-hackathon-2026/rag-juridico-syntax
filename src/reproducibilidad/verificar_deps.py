"""Verifica que cada import de terceros en src/ este declarado y fijado en requirements.txt.

Recorre con `ast` todos los .py de src/, descarta stdlib y modulos locales
(src/ y scripts/), traduce el nombre del import al paquete de pip y lo cruza
con requirements.txt. Falla (exit 1) si falta alguno o si alguna linea no esta
fijada con `==`.

Regla del repo: quien introduce un import nuevo de terceros agrega en el mismo
commit su linea `paquete==version` a requirements.txt. `--fix` lo hace solo
para los paquetes ya instalados en el entorno activo. Un import opcional a
proposito (p. ej. torch solo para detectar dispositivo) se excluye con el
comentario `# dep: opcional` en la misma linea.

Uso:
    python src/reproducibilidad/verificar_deps.py
    python src/reproducibilidad/verificar_deps.py --fix
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import defaultdict
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
REQUIREMENTS = ROOT / "requirements.txt"
OPCIONAL = "# dep: opcional"

# import -> paquete de pip, solo cuando no coinciden tras normalizar (_ -> -).
# Agregar aqui cualquier caso nuevo en el que el nombre del import difiera.
ALIAS = {
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "docx": "python-docx",
    "dotenv": "python-dotenv",
    "faiss": "faiss-cpu",
    "fitz": "pymupdf",
    "llama_cpp": "llama-cpp-python",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "yaml": "pyyaml",
}


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def local_modules() -> set[str]:
    names = {"src", "scripts"}
    for base in (SRC, ROOT / "scripts"):
        for p in base.iterdir():
            if p.suffix == ".py" or (p.is_dir() and not p.name.startswith((".", "__"))):
                names.add(p.stem)
    # modulos hermanos dentro de subcarpetas de src/ (p. ej. src/ingesta/_texto.py)
    names.update(p.stem for p in SRC.rglob("*.py"))
    return names


def collect_imports() -> dict[str, set[str]]:
    """Nombre de modulo de primer nivel -> archivos que lo importan."""
    found: dict[str, set[str]] = defaultdict(set)
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        for node in ast.walk(ast.parse(source, filename=rel)):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and OPCIONAL in lines[node.lineno - 1]:
                continue
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found[alias.name.split(".")[0]].add(rel)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                found[node.module.split(".")[0]].add(rel)
    return found


def to_distribution(module: str, installed: dict[str, list[str]]) -> str:
    if module in ALIAS:
        return ALIAS[module]
    if module in installed:
        return installed[module][0]
    return module


def read_requirements() -> dict[str, str]:
    """Paquete normalizado -> linea original."""
    reqs: dict[str, str] = {}
    if not REQUIREMENTS.exists():
        return reqs
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        m = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line)
        if m:
            reqs[normalize(m.group(0))] = line
    return reqs


def python_requerido() -> tuple[int, int] | None:
    """Version de Python declarada en la cabecera de requirements.txt (`# python: 3.13`)."""
    if not REQUIREMENTS.exists():
        return None
    m = re.search(r"^#\s*python:\s*(\d+)\.(\d+)\s*$", REQUIREMENTS.read_text(encoding="utf-8"), re.M)
    return (int(m[1]), int(m[2])) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fix", action="store_true",
                    help="agrega a requirements.txt los faltantes que esten instalados, fijados a su version")
    args = ap.parse_args()

    requerido = python_requerido()
    if requerido is None:
        print("FALTA la linea `# python: X.Y` en requirements.txt (version de Python del proyecto)")
        return 1
    if sys.version_info[:2] != requerido:
        print(f"PYTHON INCORRECTO: {sys.version_info.major}.{sys.version_info.minor} en uso, "
              f"requirements.txt pide {requerido[0]}.{requerido[1]} "
              "(recrear: python<X.Y> src/reproducibilidad/preparar_entorno.py --recrear)")
        return 1

    ignore = set(sys.stdlib_module_names) | local_modules() | {"__future__"}
    installed = metadata.packages_distributions()
    reqs = read_requirements()

    missing: dict[str, set[str]] = defaultdict(set)
    used: set[str] = set()
    for module, files in sorted(collect_imports().items()):
        if module in ignore:
            continue
        dist = to_distribution(module, installed)
        used.add(normalize(dist))
        if normalize(dist) not in reqs:
            missing[dist] |= files

    unpinned = [line for line in reqs.values() if "==" not in line]
    unused = sorted(line for key, line in reqs.items() if key not in used)

    added: list[str] = []
    if args.fix and missing:
        for dist in sorted(missing):
            try:
                added.append(f"{dist}=={metadata.version(dist)}")
            except metadata.PackageNotFoundError:
                continue
        if added:
            text = REQUIREMENTS.read_text(encoding="utf-8") if REQUIREMENTS.exists() else ""
            if text and not text.endswith("\n"):
                text += "\n"
            lines = sorted(set(text.splitlines()) | set(added), key=str.lower)
            REQUIREMENTS.write_text("\n".join(l for l in lines if l) + "\n",
                                    encoding="utf-8", newline="\n")
            for line in added:
                print(f"agregado: {line}")
                missing.pop(line.split("==")[0], None)

    for dist, files in sorted(missing.items()):
        print(f"FALTA en requirements.txt: {dist}  (usado en {', '.join(sorted(files))})")
        print(f"    -> pip install {dist} && python src/reproducibilidad/verificar_deps.py --fix")
    for line in unpinned:
        print(f"SIN FIJAR (usar ==): {line}")
    for line in unused:
        print(f"aviso: declarado pero sin import directo en src/ (ok si es dependencia de runtime): {line}")

    if missing or unpinned:
        return 1
    print(f"ok: {len(used)} paquetes de terceros usados en src/, todos declarados y fijados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
