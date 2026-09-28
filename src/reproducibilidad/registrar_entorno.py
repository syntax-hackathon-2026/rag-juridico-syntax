"""Foto del entorno de ejecucion para anotar junto a cada experimento.

Registra commit (y si hay cambios sin commitear), version de Python,
plataforma, dispositivo disponible (cuda/mps/cpu, si torch esta instalado),
hash de requirements.txt y todas las versiones instaladas. Sirve para llenar
las columnas de plataforma de evaluation/experiments.csv y para demostrar que
la corrida final y la verificacion en vivo usan la misma configuracion.

Uso:
    python src/reproducibilidad/registrar_entorno.py
    python src/reproducibilidad/registrar_entorno.py --salida evaluation/entornos/final.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip()


def device() -> dict:
    if importlib.util.find_spec("torch") is None:
        return {"torch": None, "device": "cpu"}
    import torch  # dep: opcional

    if torch.cuda.is_available():
        dev = "cuda"
    elif torch.backends.mps.is_available():
        dev = "mps"
    else:
        dev = "cpu"
    info = {"torch": torch.__version__, "device": dev}
    if dev == "cuda":
        info["gpu"] = torch.cuda.get_device_name(0)
        info["cuda"] = torch.version.cuda
    return info


def sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def snapshot() -> dict:
    status = git("status", "--porcelain")
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "cambios_sin_commit": bool(status) if status is not None else None,
        "python": platform.python_version(),
        "implementacion": platform.python_implementation(),
        "sistema": platform.system(),
        "version_sistema": platform.release(),
        "arquitectura": platform.machine(),
        **device(),
        "requirements_sha256": sha256(ROOT / "requirements.txt"),
        "paquetes": sorted(
            {f"{d.metadata['Name']}=={d.version}" for d in metadata.distributions() if d.metadata["Name"]},
            key=str.lower,
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--salida", type=Path, help="archivo JSON de salida (por defecto, stdout)")
    args = ap.parse_args()

    text = json.dumps(snapshot(), ensure_ascii=False, indent=2) + "\n"
    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        args.salida.write_text(text, encoding="utf-8", newline="\n")
        print(f"escrito {args.salida}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
