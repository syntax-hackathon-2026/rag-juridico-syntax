"""Decoder local: descarga del GGUF, comando de llama-server y verificacion.

    python src/generacion/modelo.py descargar        # GGUF a modelos/ (revision y sha256 fijos)
    python src/generacion/modelo.py comando          # imprime el comando de llama-server
    python src/generacion/modelo.py servir           # lo ejecuta (bloquea; otra terminal para main.py)
    python src/generacion/modelo.py verificar        # el servidor responde y sirve ese archivo

El modelo se elige con SYNTAX_LLM (entradas en config.LLM_MODELOS) y el endpoint
con SYNTAX_LLM_URL. llama.cpp se instala aparte (README): `brew install llama.cpp`
en Mac, el zip de GitHub releases (CUDA o CPU) en Windows/Linux. La build usada se
registra en cada traza: salidas de builds distintas no son comparables.

Flags del servidor y por que:
  -np 1          un solo slot: el batching entre peticiones cambia la numerica y
                 rompe la reproducibilidad literal que exige la verificacion en vivo.
  --load-mode none   sin mmap (antes `--no-mmap`; cambio de nombre en builds recientes):
                 pesos cargados en buffers propios (Metal/CUDA). Con mmap, en un Mac de
                 16 GB con el encoder cargado en otro proceso, macOS desalojaba paginas
                 del modelo y la generacion caia a ~2 tok/s (medido 2026-09-30).
  --jinja        usa la plantilla de chat del GGUF (necesaria para enable_thinking).
  -c LLM_CTX     ventana total del slot (prompt + respuesta).
  -ngl 99        todas las capas en GPU (Metal/CUDA); en CPU se ignora.
  --temp 0 --seed LLM_SEED   por si una peticion no los manda.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(1 << 24), b""):
            h.update(bloque)
    return h.hexdigest()


def descargar(verificar_hash: bool = True) -> Path:
    """Baja el GGUF de config.llm_config() a modelos/ y comprueba su sha256."""
    from huggingface_hub import hf_hub_download

    cfg = config.llm_config()
    ruta = cfg["ruta"]
    if not ruta.is_file():
        config.MODELOS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"descargando {cfg['repo']}@{cfg['revision'][:10]} / {cfg['archivo']} ...", flush=True)
        hf_hub_download(repo_id=cfg["repo"], filename=cfg["archivo"], revision=cfg["revision"],
                        local_dir=str(config.MODELOS_DIR))
    if verificar_hash:
        real = sha256(ruta)
        if real != cfg["sha256"]:
            raise SystemExit(f"sha256 distinto para {ruta.name}: {real} (esperado {cfg['sha256']})")
        print(f"ok {ruta.relative_to(config.ROOT).as_posix()} sha256 verificado")
    return ruta


def puerto() -> str:
    return config.LLM_URL.split("://", 1)[-1].split("/", 1)[0].rsplit(":", 1)[-1]


def comando() -> list[str]:
    cfg = config.llm_config()
    binario = shutil.which("llama-server") or "llama-server"
    return [binario, "-m", str(cfg["ruta"]), "-c", str(config.LLM_CTX), "-np", "1", "-ngl", "99",
            "--load-mode", "none", "--jinja", "--seed", str(config.LLM_SEED), "--temp", "0", "--port", puerto(),
            "--alias", cfg["nombre"]]


def version_llama() -> str:
    """Build de llama.cpp instalada (p. ej. '0.5.0 (build 11146, commit 7fe450e19)')."""
    binario = shutil.which("llama-server")
    if not binario:
        return ""
    out = subprocess.run([binario, "--version"], capture_output=True, text=True)
    for linea in (out.stdout + out.stderr).splitlines():
        if linea.startswith("version:"):
            return linea.split(":", 1)[1].strip()
    return ""


def _get(url: str, timeout: float = 5) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def verificar() -> dict:
    """Comprueba que el servidor responde y sirve el GGUF configurado. Devuelve info para trazas."""
    cfg = config.llm_config()
    try:
        modelos = _get(config.LLM_URL.rstrip("/") + "/models")
    except (urllib.error.URLError, OSError) as e:
        raise SystemExit(
            f"No responde el decoder en {config.LLM_URL} ({e}).\n"
            f"Arrancarlo en otra terminal:  python src/generacion/modelo.py servir")
    servidos = json.dumps(modelos)
    if cfg["archivo"] not in servidos and cfg["nombre"] not in servidos:
        raise SystemExit(f"El servidor en {config.LLM_URL} no sirve {cfg['archivo']} "
                         f"(SYNTAX_LLM={cfg['nombre']}). Sirve: {servidos[:300]}")
    return {"llm": cfg["nombre"], "gguf": cfg["archivo"], "sha256": cfg["sha256"],
            "cuantizacion": cfg["cuantizacion"], "llama_cpp": version_llama(), "url": config.LLM_URL}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("accion", choices=["descargar", "comando", "servir", "verificar"])
    ap.add_argument("--sin-hash", action="store_true", help="no recalcular el sha256 (tarda ~10 s)")
    args = ap.parse_args()
    if args.accion == "descargar":
        descargar(verificar_hash=not args.sin_hash)
    elif args.accion == "comando":
        print(" ".join(f'"{c}"' if " " in c else c for c in comando()))
    elif args.accion == "servir":
        if not config.llm_config()["ruta"].is_file():
            descargar()
        print("llama.cpp", version_llama() or "(no encontrado en el PATH)", flush=True)
        return subprocess.call(comando())
    else:
        print(json.dumps(verificar(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
