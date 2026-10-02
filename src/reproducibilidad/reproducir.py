"""Reproduce el pipeline completo en una maquina limpia (Windows/Linux/Mac), solo stdlib.

Partiendo de repo recien descargado + los .txt del corpus, deja todo listo y corre las preguntas:

    1. entorno   .venv con Python 3.13 + requirements.txt; en maquinas NVIDIA cambia torch por la rueda CUDA
    2. corpus    data_corpus/corpus/*.txt identicos (sha256) a corpus_manifest.json
    3. indice    segmenta, congela hashes, codifica con bge-m3 en GPU y arma BM25 + FAISS
    4. decoder   llama.cpp (build fijada), GGUF con sha256 verificado y llama-server en local
    5. preguntas src/main.py + evaluate.py oficial, con latencia media y proyeccion a 992

    python src/reproducibilidad/reproducir.py                          # todo, sobre sample_50
    python src/reproducibilidad/reproducir.py --corpus C:\\ruta\\corpus  # copia antes los .txt (carpeta o .zip)
    python src/reproducibilidad/reproducir.py --hasta indice           # entorno + corpus + indice, sin decoder
    python src/reproducibilidad/reproducir.py --reindexar              # borra indice y cache de vectores primero
    python src/reproducibilidad/reproducir.py --split test             # las 992 (sabado) -> submissions.jsonl

Cada etapa es idempotente: lo que ya esta bien se salta. Lo unico que no se instala es el driver NVIDIA ni
Python 3.13 (en Windows lo instala reproducir.ps1). Todos los subprocesos usan UTF-8.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import config  # noqa: E402  (solo stdlib a nivel de modulo)
from generacion import modelo  # noqa: E402  (idem; huggingface_hub se importa dentro de descargar)

VENV = ROOT / ".venv"
LLAMA_TAG = "b11146"  # la build con la que se midio (README: 0.5.0, build 11146)
LLAMA_DIR = ROOT / "herramientas" / "llama.cpp"  # en .gitignore
LLAMA_BASE = f"https://github.com/ggml-org/llama.cpp/releases/download/{LLAMA_TAG}/"
TORCH_INDEX = "https://download.pytorch.org/whl/"
ETAPAS = ["entorno", "corpus", "indice", "decoder", "preguntas"]
ES_WIN = os.name == "nt"


def titulo(n: int, texto: str) -> None:
    print(f"\n{'=' * 78}\n[{n}/5] {texto}\n{'=' * 78}", flush=True)


def run(cmd: list, env: dict | None = None, check: bool = True, **kw) -> subprocess.CompletedProcess:
    print("$", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, env=env, **kw)
    if check and r.returncode:
        raise SystemExit(f"fallo (exit {r.returncode}): {' '.join(str(c) for c in cmd[:4])} ...")
    return r


def venv_py() -> Path:
    return VENV / ("Scripts/python.exe" if ES_WIN else "bin/python")


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def requisito_python() -> tuple[int, int]:
    m = re.search(r"^#\s*python:\s*(\d+)\.(\d+)\s*$", (ROOT / "requirements.txt").read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit("requirements.txt no declara `# python: X.Y`")
    return int(m[1]), int(m[2])


def python_objetivo() -> list[str]:
    """Comando de un interprete con la version exacta de requirements.txt (el actual, `py -3.13` o `python3.13`)."""
    v = requisito_python()
    if sys.version_info[:2] == v:
        return [sys.executable]
    for cand in ([["py", f"-{v[0]}.{v[1]}"]] if ES_WIN else []) + [[f"python{v[0]}.{v[1]}"]]:
        if shutil.which(cand[0]):
            r = subprocess.run(cand + ["-c", "import sys;print(sys.version_info[:2]==(%d,%d))" % v],
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip() == "True":
                return cand
    raise SystemExit(f"Hace falta Python {v[0]}.{v[1]} (linea `# python:` de requirements.txt). "
                     + ("En Windows: powershell -ExecutionPolicy Bypass -File reproducir.ps1 lo instala."
                        if ES_WIN else f"Instalar python{v[0]}.{v[1]} y volver a lanzar."))


def entorno_utf8(extra: dict | None = None) -> dict:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8",
           "PIP_PROGRESS_BAR": "off", "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
    if LLAMA_DIR.is_dir():
        sep = os.pathsep
        env["PATH"] = str(llama_bin_dir() or LLAMA_DIR) + sep + env.get("PATH", "")
        if not ES_WIN:
            env["LD_LIBRARY_PATH"] = str(llama_bin_dir() or LLAMA_DIR) + sep + env.get("LD_LIBRARY_PATH", "")
    env.update(extra or {})
    return env


# --- 1. entorno ---------------------------------------------------------------------------

def gpu_nvidia() -> dict | None:
    """{'nombre', 'memoria_mb', 'cuda'} si hay una GPU NVIDIA con driver; None si no."""
    if not shutil.which("nvidia-smi"):
        return None
    q = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True)
    if q.returncode or not q.stdout.strip():
        return None
    nombre, mem = [x.strip() for x in q.stdout.strip().splitlines()[0].split(",")]
    banner = subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout
    m = re.search(r"CUDA Version:\s*(\d+)\.(\d+)", banner)
    return {"nombre": nombre, "memoria_mb": int(mem), "cuda": (int(m[1]), int(m[2])) if m else (0, 0)}


def torch_cuda_ok() -> bool:
    r = subprocess.run([str(venv_py()), "-c", "import torch,sys;sys.exit(0 if torch.cuda.is_available() else 1)"],
                       capture_output=True)
    return r.returncode == 0


def etapa_entorno(args, gpu) -> None:
    titulo(1, "Entorno: .venv, dependencias y torch con CUDA")
    py = python_objetivo()
    if not venv_py().exists() or args.recrear_entorno:
        run(py + [ROOT / "src/reproducibilidad/preparar_entorno.py"] + (["--recrear"] if args.recrear_entorno else []),
            env=entorno_utf8())
    else:  # ya existe: reinstala lo que falte (rapido si esta completo) y comprueba imports
        run([venv_py(), "-m", "pip", "install", "-q", "-r", "requirements.txt"], env=entorno_utf8())
    # En Windows `pip install torch==X` baja la rueda CPU de PyPI: se cambia por la CUDA de pytorch.org.
    if args.device != "cpu" and gpu and not torch_cuda_ok():
        cuda = gpu["cuda"]
        tag = args.cuda_torch or ("cu130" if cuda >= (13, 0) else "cu126" if cuda >= (12, 6) else None)
        if not tag:
            raise SystemExit(f"El driver NVIDIA solo soporta CUDA {cuda[0]}.{cuda[1]}; actualizarlo (hace falta >= 12.6).")
        version = re.search(r"^torch==(\S+)$", (ROOT / "requirements.txt").read_text(encoding="utf-8"), re.M)[1]
        print(f"torch sin CUDA en el venv; instalando torch=={version} ({tag})")
        run([venv_py(), "-m", "pip", "install", "--force-reinstall", "--no-deps", f"torch=={version}",
             "--index-url", TORCH_INDEX + tag], env=entorno_utf8())
    if args.device == "cuda" or (args.device == "auto" and gpu):
        if not torch_cuda_ok():
            raise SystemExit("torch no ve la GPU (torch.cuda.is_available() = False). Revisar driver NVIDIA "
                             "o forzar --cuda-torch cu126|cu130. Con --device cpu indexar tardaria horas.")
        args.device = "cuda"
    elif args.device == "auto":
        args.device = "cpu"
    run([venv_py(), "src/reproducibilidad/verificar_deps.py"], env=entorno_utf8())
    run([venv_py(), "-c", "import torch,faiss,bm25s,sentence_transformers;"
         "print('torch',torch.__version__,'cuda',torch.cuda.is_available(),'faiss',faiss.__version__)"],
        env=entorno_utf8())


# --- 2. corpus ----------------------------------------------------------------------------

def copiar_corpus(origen: Path) -> None:
    """Copia solo los .txt cuyo nombre es un doc_id del manifest (ignora requirements.txt, notas, etc.)."""
    validos = {d["doc_id"] for d in json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]}
    config.CORPUS_TEXTOS.mkdir(parents=True, exist_ok=True)
    n, ignorados = 0, []

    def copiar(nombre: str, datos: bytes) -> None:
        nonlocal n
        if nombre.endswith(".txt") and Path(nombre).stem in validos:
            (config.CORPUS_TEXTOS / Path(nombre).name).write_bytes(datos)  # binario: no toca los saltos de linea
            n += 1
        elif nombre.endswith(".txt"):
            ignorados.append(Path(nombre).name)

    if origen.is_file() and origen.suffix == ".zip":
        with zipfile.ZipFile(origen) as z:
            for info in z.infolist():
                if not info.is_dir():
                    copiar(info.filename, z.read(info))
    elif origen.is_dir():
        raiz = origen / "corpus" if (origen / "corpus").is_dir() else origen
        for f in raiz.glob("*.txt"):
            copiar(f.name, f.read_bytes())
    else:
        raise SystemExit(f"--corpus {origen}: no es una carpeta ni un .zip")
    print(f"copiados {n} .txt a {config.CORPUS_TEXTOS.relative_to(ROOT).as_posix()}/")
    if ignorados:
        print(f"ignorados {len(ignorados)} .txt que no son doc_id del manifest: {', '.join(ignorados[:8])}")


def etapa_corpus(args) -> None:
    titulo(2, "Corpus: .txt contra corpus_manifest.json")
    if args.corpus:
        copiar_corpus(args.corpus)
    docs = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]
    faltan, difieren = [], []
    for d in docs:
        ruta = config.CORPUS_TEXTOS / f"{d['doc_id']}.txt"
        if not ruta.is_file():
            faltan.append(d["doc_id"])
        elif sha256_archivo(ruta) != d["sha256"]:
            difieren.append(d["doc_id"])
    print(f"{len(docs) - len(faltan) - len(difieren)}/{len(docs)} documentos identicos al manifest")
    extra = sorted(p.name for p in config.CORPUS_TEXTOS.glob("*.txt") if p.stem not in {d["doc_id"] for d in docs})
    if extra:
        raise SystemExit(f"Sobran .txt en {config.CORPUS_TEXTOS} que no son doc_id del manifest (segmentar.py los rechaza): "
                         f"{', '.join(extra[:8])}. Borrarlos y repetir.")
    if faltan or difieren:
        if faltan:
            print(f"  faltan {len(faltan)}: {', '.join(faltan[:8])}{' ...' if len(faltan) > 8 else ''}")
        if difieren:
            print(f"  difieren {len(difieren)}: {', '.join(difieren[:8])}{' ...' if len(difieren) > 8 else ''}")
            print("  (si difieren todos: probable conversion de saltos de linea CRLF al copiar; copiar como binario / zip)")
        raise SystemExit(f"Copiar el corpus a {config.CORPUS_TEXTOS} (o pasar --corpus <carpeta|zip>) y repetir.")


# --- 3. indice ----------------------------------------------------------------------------

def indice_al_dia() -> bool:
    try:
        info = json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8"))
        return (config.FAISS_PATH.is_file() and config.BM25_DIR.is_dir()
                and info.get("sha256_chunks") == sha256_archivo(config.CHUNKS_PATH))
    except (OSError, ValueError):
        return False


def etapa_indice(args) -> None:
    titulo(3, f"Indice: segmentar, verificar hashes, bge-m3 ({args.device}) + BM25 + FAISS")
    env = entorno_utf8({"SYNTAX_DEVICE": args.device})
    py = venv_py()
    if args.reindexar:
        for p in (config.INDICE_DIR, config.EMB_CACHE_DIR):
            if p.exists():
                print(f"borrando {p.relative_to(ROOT).as_posix()}/ (--reindexar)")
                shutil.rmtree(p)
    run([py, "src/indexacion/segmentar.py"], env=env)
    run([py, "src/reproducibilidad/verificar_corpus.py"], env=env)  # chunks.jsonl == el congelado: misma segmentacion
    if indice_al_dia():
        print("indice vigente (sha256 de chunks.jsonl coincide); se salta la codificacion. --reindexar para rehacerlo")
    else:
        t0 = time.perf_counter()
        run([py, "src/indexacion/construir_indice.py", "--batch", str(args.batch), "--no-manifest"], env=env)
        print(f"indice construido en {(time.perf_counter() - t0) / 60:.1f} min")
    run([py, "src/validaciones/manifest.py"], env=env)
    run([py, "-c", "import sys;sys.path.insert(0,'src');import config;print('indice ok:',config.verificar_indice(),'fragmentos')"],
        env=env)


# --- 4. decoder ---------------------------------------------------------------------------

def llama_bin_dir() -> Path | None:
    if not LLAMA_DIR.is_dir():
        return None
    nombre = "llama-server.exe" if ES_WIN else "llama-server"
    hit = next(LLAMA_DIR.rglob(nombre), None)
    return hit.parent if hit else None


def descargar_url(url: str, destino: Path) -> None:
    print(f"descargando {url}", flush=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=60) as r, destino.open("wb") as f:
            shutil.copyfileobj(r, f, 1 << 20)
    except urllib.error.URLError as e:
        raise SystemExit(f"no se pudo descargar {url}: {e}")


def activos_llama(gpu) -> list[str]:
    if ES_WIN:
        if gpu:
            return [f"llama-{LLAMA_TAG}-bin-win-cuda-12.4-x64.zip", "cudart-llama-bin-win-cuda-12.4-x64.zip"]
        return [f"llama-{LLAMA_TAG}-bin-win-cpu-x64.zip"]
    if sys.platform.startswith("linux"):
        if gpu:
            return [f"llama-{LLAMA_TAG}-bin-ubuntu-cuda-12.8-x64.tar.gz", f"cudart-llama-{LLAMA_TAG}-bin-ubuntu-cuda-12.8-x64.tar.gz"]
        return [f"llama-{LLAMA_TAG}-bin-ubuntu-x64.tar.gz"]
    raise SystemExit("En Mac: brew install llama.cpp (Metal) y volver a lanzar.")


def asegurar_llama(gpu) -> None:
    if shutil.which("llama-server") or llama_bin_dir():
        return
    LLAMA_DIR.mkdir(parents=True, exist_ok=True)
    for nombre in activos_llama(gpu):
        arch = LLAMA_DIR / nombre
        descargar_url(LLAMA_BASE + nombre, arch)
        if nombre.endswith(".zip"):
            with zipfile.ZipFile(arch) as z:
                z.extractall(LLAMA_DIR)
        else:
            with tarfile.open(arch) as t:
                t.extractall(LLAMA_DIR)
        arch.unlink()
    if not llama_bin_dir():
        raise SystemExit(f"no aparecio llama-server dentro de {LLAMA_DIR}")


def servidor_responde() -> bool:
    try:
        modelo._get(config.LLM_URL.rstrip("/") + "/models", timeout=3)
        return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


def etapa_decoder(args, gpu) -> subprocess.Popen | None:
    titulo(4, f"Decoder: llama.cpp {LLAMA_TAG} + {config.llm_config()['archivo']}")
    asegurar_llama(gpu)
    os.environ.update({k: v for k, v in entorno_utf8().items() if k in ("PATH", "LD_LIBRARY_PATH")})
    r = subprocess.run([str(shutil.which("llama-server")), "--version"], capture_output=True, text=True)
    print("llama-server:", next((l for l in (r.stdout + r.stderr).splitlines() if l.startswith("version")), "?"))
    run([venv_py(), "src/generacion/modelo.py", "descargar"], env=entorno_utf8())
    if servidor_responde():
        print(f"ya hay un servidor en {config.LLM_URL}; se reutiliza (no se detendra al terminar)")
        return None
    log = config.SALIDAS_DIR / "llama-server.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = modelo.comando()
    print("$", " ".join(cmd), f"  > {log.relative_to(ROOT).as_posix()}", flush=True)
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=log.open("w", encoding="utf-8"), stderr=subprocess.STDOUT, env=entorno_utf8())
    t0 = time.time()
    while time.time() - t0 < 300:
        if proc.poll() is not None:
            print(log.read_text(encoding="utf-8", errors="replace")[-2000:])
            raise SystemExit(f"llama-server termino con exit {proc.returncode}")
        if servidor_responde():
            print(f"servidor listo en {time.time() - t0:.0f} s")
            salida = log.read_text(encoding="utf-8", errors="replace")
            gpu_ok = re.search(r"offloaded (\d+)/(\d+) layers", salida)
            if gpu_ok:
                print("capas en GPU:", gpu_ok[0])
            return proc
        time.sleep(2)
    proc.terminate()
    raise SystemExit(f"llama-server no respondio en 300 s (ver {log})")


# --- 5. preguntas -------------------------------------------------------------------------

def resumen_latencias(salida: Path, objetivo_s: float = 10.0) -> None:
    lat = [json.loads(l).get("latencia_ms") for l in salida.read_text(encoding="utf-8").splitlines() if l.strip()]
    lat = [x / 1000 for x in lat if x]
    if not lat:
        return
    media = statistics.mean(lat)
    print(f"\nlatencia por pregunta: media {media:.1f} s, mediana {statistics.median(lat):.1f} s, max {max(lat):.1f} s"
          f"  ->  992 preguntas ~ {media * 992 / 3600:.1f} h  (objetivo < {objetivo_s:.0f} s/pregunta)")


def etapa_preguntas(args) -> None:
    titulo(5, f"Preguntas: {args.split}")
    env = entorno_utf8({"SYNTAX_DEVICE": args.device})
    entrada = config.SAMPLE_PATH if args.split == "sample" else config.TEST_PATH
    if not entrada.is_file():
        raise SystemExit(f"No existe {entrada.relative_to(ROOT).as_posix()} (las 992 se entregan el sabado a las 09:00).")
    cmd = [venv_py(), "src/main.py", "--split", args.split, "--experimento", args.experimento]
    if args.limite:
        cmd += ["--limite", str(args.limite)]
    if args.sin_reanudar:
        cmd += ["--sin-reanudar"]
    run(cmd, env=env)
    salida = config.SALIDAS_DIR / f"{args.split}_{args.experimento}.jsonl"
    if args.split == "test" and not args.limite:
        salida = config.SUBMISSION_PATH
    resumen_latencias(salida)
    if args.split == "sample" and not args.limite:
        run([venv_py(), "scripts/evaluate.py", "--submission", salida, "--split", "sample"], env=env)
        run([venv_py(), "src/evaluacion/evaluar_entrega.py", "--entrega", salida, "--experimento", args.experimento,
             "--notas", f"reproducir.py; device={args.device}; batch={args.batch}"], env=env)
    elif args.split == "sample":
        print("(--limite: no se evalua, el evaluador espera las 50 preguntas)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.splitlines()[1:]))
    ap.add_argument("--hasta", choices=ETAPAS, default="preguntas", help="ultima etapa a ejecutar (por defecto: todas)")
    ap.add_argument("--corpus", type=Path, help="carpeta (con .txt o con corpus/) o .zip de donde copiar los .txt")
    ap.add_argument("--split", choices=["sample", "test"], default="sample")
    ap.add_argument("--limite", type=int, help="solo las N primeras preguntas (humo)")
    ap.add_argument("--experimento", default="windows_rtx4090", help="nombre de la corrida (trazas, experiments.csv)")
    ap.add_argument("--sin-reanudar", action="store_true", help="empezar las preguntas de cero (medir latencias limpias)")
    ap.add_argument("--reindexar", action="store_true", help="borrar indice/ y cache_emb/ y codificar todo de nuevo")
    ap.add_argument("--recrear-entorno", action="store_true", help="borrar .venv y reinstalar")
    ap.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto", help="encoder: auto usa CUDA si hay NVIDIA")
    ap.add_argument("--batch", type=int, default=64, help="batch del encoder (64 cabe de sobra en 24 GB)")
    ap.add_argument("--cuda-torch", choices=["cu126", "cu130"], help="forzar el indice de ruedas de torch")
    args = ap.parse_args()

    if sys.platform == "darwin" and args.device == "cuda":
        raise SystemExit("--device cuda no existe en Mac")
    gpu = gpu_nvidia()
    desc = "ninguna NVIDIA"
    if gpu:
        desc = f"{gpu['nombre']} ({gpu['memoria_mb'] // 1024} GB, driver CUDA {gpu['cuda'][0]}.{gpu['cuda'][1]})"
    print(f"repo: {ROOT}\nplataforma: {sys.platform}  python: {sys.version.split()[0]}  GPU: {desc}")
    hasta = ETAPAS.index(args.hasta)
    t0 = time.perf_counter()

    etapa_entorno(args, gpu)
    if hasta >= 1:
        etapa_corpus(args)
    if hasta >= 2:
        etapa_indice(args)
    proc = None
    try:
        if hasta >= 3:
            proc = etapa_decoder(args, gpu)
        if hasta >= 4:
            etapa_preguntas(args)
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(15)
            except subprocess.TimeoutExpired:
                proc.kill()
    print(f"\nlisto en {(time.perf_counter() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
