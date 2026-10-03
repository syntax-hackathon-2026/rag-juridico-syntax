"""Reproduce el pipeline completo en una maquina limpia (Windows/Linux/Mac), por etapas y solo stdlib.

Premisa: el corpus ya existe como .txt (data_corpus/corpus/<doc_id>.txt, identicos al sha256 de
corpus_manifest.json). Desde ahi todo se reconstruye: indice, respuestas y evaluacion.

    1. entorno    .venv con Python 3.13 + requirements.txt + deps del evaluador; en NVIDIA cambia torch por la CUDA
    2. corpus     data_corpus/corpus/*.txt identicos (sha256) a corpus_manifest.json
    3. indice     segmenta, congela hashes, codifica con bge-m3 en GPU y arma BM25 + FAISS
    4. decoder    llama.cpp (build fijada), GGUF con sha256 verificado y llama-server en local
    5. preguntas  src/main.py sobre las preguntas elegidas -> entrega JSONL, con latencia y proyeccion a 992
    6. evaluar    valida schema y puntua (evaluate.py oficial; juez de texto libre si hay OPENROUTER_API_KEY)

Que etapas correr:
    reproducir.py                                  # las 6, sobre sample_50
    reproducir.py --solo indice                    # solo esa(s); varias separadas por coma: --solo corpus,indice
    reproducir.py --desde preguntas                # de preguntas a evaluar
    reproducir.py --hasta indice                   # entorno + corpus + indice, sin decoder
    reproducir.py --dry-run --solo preguntas ...   # muestra el plan y lo que falta, sin ejecutar nada

Que preguntas responder (etapa preguntas):
    --split sample|test                            # data/sample_50.jsonl | data/test_992.jsonl
    --entrada <jsonl>                              # cualquier archivo de preguntas (manda sobre --split)
    --ids 51 60 748 | --rango 100-200 | --limite N # subconjunto (ids inclusivos en --rango)
    --particion I/N                                # reparte entre maquinas: items j con j % N == I-1

Otras: --corpus <carpeta|zip> copia los .txt antes de verificar; --reindexar; --recrear-entorno; --sin-reanudar;
--entrega <jsonl> y --ragas/--sin-ragas para la etapa evaluar; --device; --batch; --cuda-torch.

Cada etapa es idempotente: lo que ya esta bien se salta. Una etapa aislada no re-ejecuta las anteriores: comprueba
sus prerrequisitos y falla con el comando que los resuelve. Lo unico que no se instala es el driver NVIDIA ni
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
ETAPAS = ["entorno", "corpus", "indice", "decoder", "preguntas", "evaluar"]
REQ_EVALUADOR = "scripts/requirements-evaluador.txt"  # oficial del jurado: solo se instala, no se edita
JURADO_TEST = ("answer_key_992.jsonl", "test_992.jsonl", "scoring_subset.json")  # solo los tiene el jurado
ES_WIN = os.name == "nt"


def titulo(etapa: str, texto: str) -> None:
    print(f"\n{'=' * 78}\n[{ETAPAS.index(etapa) + 1}/{len(ETAPAS)}] {texto}\n{'=' * 78}", flush=True)


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


# --- logica pura (sin subprocesos; la cubre tests/test_reproducir.py) ---------------------------

def resolver_etapas(solo: str | None = None, desde: str | None = None, hasta: str | None = None) -> list[str]:
    """Etapas a correr, en orden canonico. `solo` (lista separada por comas) excluye a desde/hasta."""
    if solo is not None and (desde or hasta):
        raise ValueError("--solo no se combina con --desde/--hasta")
    if solo is not None:
        pedidas = [e.strip() for e in solo.split(",") if e.strip()]
        malas = [e for e in pedidas if e not in ETAPAS]
        if malas or not pedidas:
            raise ValueError(f"etapa desconocida: {', '.join(malas) or '(vacio)'}; validas: {', '.join(ETAPAS)}")
        return [e for e in ETAPAS if e in pedidas]
    i, j = ETAPAS.index(desde or ETAPAS[0]), ETAPAS.index(hasta or ETAPAS[-1])
    if i > j:
        raise ValueError(f"--desde {desde} va despues de --hasta {hasta}")
    return ETAPAS[i:j + 1]


def parsear_rango(texto: str) -> tuple[int, int]:
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", texto)
    if not m or int(m[1]) > int(m[2]):
        raise ValueError(f"--rango {texto!r}: se espera A-B con A <= B (ids inclusivos)")
    return int(m[1]), int(m[2])


def leer_preguntas(ruta: Path) -> list[dict]:
    """Lee y valida un JSONL de preguntas: existe, cada linea es JSON con id entero unico, formato y pregunta."""
    if not ruta.is_file():
        raise ValueError(f"No existe {ruta} (las 992 se entregan el sabado a las 09:00)")
    items, vistos = [], set()
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        if not linea.strip():
            continue
        try:
            it = json.loads(linea)
        except ValueError as e:
            raise ValueError(f"{ruta.name}:{n}: JSON invalido ({e})")
        if not isinstance(it, dict) or not isinstance(it.get("id"), int) or isinstance(it.get("id"), bool):
            raise ValueError(f"{ruta.name}:{n}: falta `id` entero")
        if it["id"] in vistos:
            raise ValueError(f"{ruta.name}:{n}: id {it['id']} repetido")
        if it.get("formato") not in ("multiple_choice", "semi_open", "open_ended") or not it.get("pregunta"):
            raise ValueError(f"{ruta.name}:{n}: id {it['id']} sin `formato` valido o sin `pregunta`")
        vistos.add(it["id"])
        items.append(it)
    if not items:
        raise ValueError(f"{ruta.name} no tiene preguntas")
    return items


def seleccion(args, items: list[dict]) -> list[int] | None:
    """ids explicitos pedidos (--ids o --rango, ya comprobados contra la entrada), o None si no hay."""
    if args.ids and args.rango:
        raise ValueError("--ids y --rango son excluyentes")
    if args.ids:
        pedidos = list(dict.fromkeys(args.ids))
    elif args.rango:
        a, b = parsear_rango(args.rango)
        pedidos = [it["id"] for it in items if a <= it["id"] <= b]
        if not pedidos:
            raise ValueError(f"--rango {args.rango}: ningun id de la entrada cae en ese rango")
    else:
        return None
    existentes = {it["id"] for it in items}
    ausentes = [i for i in pedidos if i not in existentes]
    if ausentes:
        raise ValueError(f"ids que no estan en la entrada: {ausentes[:10]}")
    return pedidos


def hay_seleccion(args) -> bool:
    return bool(args.ids or args.rango or args.limite or args.particion)


def ruta_entrada(args) -> Path:
    return args.entrada or (config.SAMPLE_PATH if args.split == "sample" else config.TEST_PATH)


def ruta_entrega(args) -> Path:
    """Misma regla que main.py: test completo -> submissions.jsonl; el resto, salidas/<split>_<exp>.jsonl."""
    if args.entrega:
        return args.entrega
    if args.split == "test" and not hay_seleccion(args):
        return config.SUBMISSION_PATH
    return config.SALIDAS_DIR / f"{args.split}_{args.experimento}.jsonl"


def comando_main(args, py, ids: list[int] | None, salida: Path) -> list:
    cmd = [py, "src/main.py", "--split", args.split, "--experimento", args.experimento, "--salida", salida]
    if args.entrada:
        cmd += ["--entrada", args.entrada]
    if ids:
        cmd += ["--ids", *map(str, ids)]
    for flag, valor in (("--limite", args.limite), ("--particion", args.particion)):
        if valor:
            cmd += [flag, str(valor)]
    if args.sin_reanudar:
        cmd += ["--sin-reanudar"]
    return cmd


def llave_juez(entorno: dict | None = None, env_file: Path | None = None) -> bool:
    """Hay OPENROUTER_API_KEY en el entorno o en scripts/.env (misma busqueda que scripts/evaluate.py)."""
    entorno = os.environ if entorno is None else entorno
    if entorno.get("OPENROUTER_API_KEY", "").strip():
        return True
    env_file = env_file or ROOT / "scripts" / ".env"
    if env_file.is_file():
        for linea in env_file.read_text(encoding="utf-8").splitlines():
            clave, sep, valor = linea.strip().partition("=")
            if sep and clave.replace("export", "", 1).strip() == "OPENROUTER_API_KEY" and valor.strip().strip("\"'"):
                return True
    return False


def usar_juez(args, tiene_llave: bool) -> tuple[bool, str]:
    """(correr el juez de texto libre, mensaje). --ragas lo exige (falla sin llave), --sin-ragas lo apaga."""
    if args.ragas and args.sin_ragas:
        raise ValueError("--ragas y --sin-ragas son excluyentes")
    if args.sin_ragas:
        return False, "juez omitido (--sin-ragas): los 30 pts de texto libre quedan sin medir"
    if tiene_llave:
        return True, "juez de texto libre activo (OPENROUTER_API_KEY presente)"
    if args.ragas:
        raise ValueError("--ragas pide el juez pero falta OPENROUTER_API_KEY (entorno o scripts/.env)")
    return False, ("juez omitido: falta OPENROUTER_API_KEY (entorno o scripts/.env); "
                   "los 30 pts de texto libre quedan sin medir")


def jurado_test_presente() -> bool:
    return all((ROOT / "data" / n).is_file() for n in JURADO_TEST)


def evaluable_sample(args) -> bool:
    """evaluar_entrega.py espera las 50 de sample_50: solo vale sin subconjunto y sin otra entrada."""
    return args.split == "sample" and not hay_seleccion(args) and ruta_entrada(args) == config.SAMPLE_PATH


def comandos_evaluar(args, py, entrega: Path, juez: bool) -> list[tuple[str, list]]:
    """[(descripcion, comando)] de la etapa evaluar; la primera entrada (schema) siempre va."""
    cmds: list[tuple[str, list]] = []
    validar = [py, "src/reproducibilidad/validar_entrega.py", entrega]
    if not hay_seleccion(args):
        validar += ["--preguntas", ruta_entrada(args)]
    cmds.append(("schema, ids y doc_id contra el manifest", validar))
    if evaluable_sample(args):
        cmds.append(("puntaje oficial + diagnostico por pregunta (evaluation/generacion/<exp>/)",
                     [py, "src/evaluacion/evaluar_entrega.py", "--entrega", entrega, "--experimento", args.experimento,
                      "--corrida", args.experimento, "--notas", f"reproducir.py; device={args.device}; batch={args.batch}"]
                     + (["--ragas"] if juez else []) + (["--no-csv"] if args.no_csv else [])))
    elif args.split == "test" and not hay_seleccion(args) and jurado_test_presente():
        cmds.append(("puntaje oficial sobre el test (clave del jurado presente)",
                     [py, "scripts/evaluate.py", "--submission", entrega, "--split", "test",
                      "--out", config.SALIDAS_DIR / f"test_{args.experimento}_reporte.json"] + (["--ragas"] if juez else [])))
    return cmds


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
    titulo("entorno", "Entorno: .venv, dependencias y torch con CUDA")
    py = python_objetivo()
    if not venv_py().exists() or args.recrear_entorno:  # app + evaluador (juez), ambos del mismo venv
        run(py + [ROOT / "src/reproducibilidad/preparar_entorno.py", "--evaluador"]
            + (["--recrear"] if args.recrear_entorno else []), env=entorno_utf8())
    else:  # ya existe: reinstala lo que falte (rapido si esta completo) y comprueba imports
        for req in ("requirements.txt", REQ_EVALUADOR):
            run([venv_py(), "-m", "pip", "install", "-q", "-r", req], env=entorno_utf8())
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
    # conjunto completo (app + evaluador, tras cambiar torch): sin conflictos, imports de src/ declarados y juez importable
    run([venv_py(), "-m", "pip", "check"], env=entorno_utf8())
    run([venv_py(), "src/reproducibilidad/verificar_deps.py", "--evaluador"], env=entorno_utf8())
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
    titulo("corpus", "Corpus: .txt contra corpus_manifest.json")
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
    titulo("indice", f"Indice: segmentar, verificar hashes, bge-m3 ({args.device}) + BM25 + FAISS")
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
    titulo("decoder", f"Decoder: llama.cpp {LLAMA_TAG} + {config.llm_config()['archivo']}")
    asegurar_llama(gpu)
    os.environ.update({k: v for k, v in entorno_utf8().items() if k in ("PATH", "LD_LIBRARY_PATH")})
    r = subprocess.run([str(shutil.which("llama-server")), "--version"], capture_output=True, text=True)
    print("llama-server:", next((l for l in (r.stdout + r.stderr).splitlines() if l.startswith("version")), "?"))
    run([venv_py(), "src/generacion/modelo.py", "descargar"], env=entorno_utf8())
    if config.RERANKER != "off":  # pesos del cross-encoder en la revision fijada (docs/INDEXACION.md 20)
        run([venv_py(), "-c", "from huggingface_hub import snapshot_download; "
             f"print(snapshot_download({config.RERANKER_MODEL!r}, revision={config.RERANKER_REVISION!r}))"],
            env=entorno_utf8())
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


def etapa_preguntas(args, ids: list[int] | None) -> None:
    entrada, salida = ruta_entrada(args), ruta_entrega(args)
    titulo("preguntas", f"Preguntas: {entrada.name} -> {salida.name}")
    env = entorno_utf8({"SYNTAX_DEVICE": args.device})
    run(comando_main(args, venv_py(), ids, salida), env=env)
    resumen_latencias(salida)


# --- 6. evaluar ---------------------------------------------------------------------------

def etapa_evaluar(args) -> int:
    """Valida el schema y puntua. Devuelve el codigo de salida (0 = todo bien); no aborta al primer fallo."""
    entrega = ruta_entrega(args)
    titulo("evaluar", f"Evaluar: {entrega.name}")
    env = entorno_utf8({"SYNTAX_DEVICE": args.device})
    juez, mensaje = usar_juez(args, llave_juez())
    print(mensaje)
    cmds = comandos_evaluar(args, venv_py(), entrega, juez)
    fallos = 0
    for descripcion, cmd in cmds:
        print(f"-- {descripcion}")
        fallos += bool(run(cmd, env=env, check=False).returncode)
    if len(cmds) == 1:
        if hay_seleccion(args) or ruta_entrada(args) != (config.SAMPLE_PATH if args.split == "sample" else config.TEST_PATH):
            print("(subconjunto o entrada propia: solo se valido el schema; el puntaje oficial espera las preguntas completas)")
        else:
            print("(test sin clave de respuestas: solo se valido el schema; el puntaje lo calcula el jurado)")
    return 1 if fallos else 0


# --- orquestacion -------------------------------------------------------------------------

def validar_argumentos(args, etapas: list[str]) -> tuple[list[int] | None, list[str]]:
    """(ids elegidos, problemas). Comprueba flags y prerrequisitos de las etapas aisladas, sin ejecutar nada."""
    problemas: list[str] = []
    ids = None

    def pide(msg: str) -> None:
        problemas.append(msg)

    necesita_venv = [e for e in etapas if e in ("indice", "decoder", "preguntas", "evaluar")]
    if "entorno" not in etapas and necesita_venv and not venv_py().exists():
        pide(f"no existe .venv (lo piden: {', '.join(necesita_venv)}): correr --solo entorno")
    if "indice" in etapas and "corpus" not in etapas and not any(config.CORPUS_TEXTOS.glob("*.txt")):
        pide(f"no hay .txt en {config.CORPUS_TEXTOS.relative_to(ROOT).as_posix()}/: correr --solo corpus --corpus <carpeta|zip>")
    if "preguntas" in etapas:
        if "indice" not in etapas and not indice_al_dia():
            pide("el indice falta o no corresponde a chunks.jsonl: correr --solo indice")
        try:
            ids = seleccion(args, leer_preguntas(ruta_entrada(args)))
        except ValueError as e:
            pide(str(e))
    if "evaluar" in etapas:
        if "preguntas" not in etapas and not ruta_entrega(args).is_file():
            pide(f"no existe la entrega {ruta_entrega(args)}: correr --solo preguntas o pasar --entrega <jsonl>")
        if evaluable_sample(args) and "indice" not in etapas and not config.CHUNKS_PATH.is_file():
            pide(f"el diagnostico por pregunta necesita {config.CHUNKS_PATH.relative_to(ROOT).as_posix()}: correr --solo indice "
                 "(o `python src/indexacion/segmentar.py`, que no necesita GPU)")
        try:
            usar_juez(args, llave_juez())
            if "preguntas" not in etapas and not hay_seleccion(args):
                leer_preguntas(ruta_entrada(args))
        except ValueError as e:
            pide(str(e))
    return ids, problemas


def device_sin_entorno(args, gpu) -> None:
    """Resuelve --device auto cuando no se corre la etapa entorno (usa el torch del .venv existente)."""
    if args.device == "auto":
        args.device = "cuda" if gpu and venv_py().exists() and torch_cuda_ok() else "cpu"


def describir_plan(args, etapas: list[str], ids: list[int] | None, problemas: list[str]) -> None:
    print(f"\nplan (--dry-run, no se ejecuta nada): {' -> '.join(etapas)}")
    py = ".venv/bin/python" if not ES_WIN else r".venv\Scripts\python.exe"
    acciones = {
        "entorno": f"crear/actualizar .venv con requirements.txt + {REQ_EVALUADOR}, torch CUDA si hay NVIDIA, "
                   "pip check y verificar_deps.py --evaluador",
        "corpus": "copiar los .txt de --corpus (si se pasa) y exigirlos identicos al sha256 del manifest",
        "indice": ("borrar indice/ y cache_emb/; " if args.reindexar else "")
                  + f"segmentar, verificar hashes, codificar con bge-m3 (device={args.device}, batch={args.batch}) y armar BM25 + FAISS"
                  + ("" if args.reindexar else " (se salta si ya esta vigente)"),
        "decoder": f"llama.cpp {LLAMA_TAG} + {config.llm_config()['archivo']}; levantar llama-server (si no hay uno) "
                   "y detenerlo al terminar",
    }
    for e in etapas:
        if e in acciones:
            print(f"  [{e}] {acciones[e]}")
        elif e == "preguntas":
            if "decoder" not in etapas:
                print("  [decoder] (requisito de preguntas) levantar llama-server si no hay uno")
            print(f"  [preguntas] {ruta_entrada(args).name}"
                  + (f", {len(ids)} ids elegidos" if ids else ", todas" if not hay_seleccion(args) else ", subconjunto")
                  + f" -> {ruta_entrega(args)}")
            print("     $", " ".join(map(str, comando_main(args, py, ids, ruta_entrega(args)))))
        elif e == "evaluar":
            try:
                juez, mensaje = usar_juez(args, llave_juez())
            except ValueError as err:
                juez, mensaje = False, f"ERROR: {err}"
            print(f"  [evaluar] {mensaje}")
            for descripcion, cmd in comandos_evaluar(args, py, ruta_entrega(args), juez):
                print(f"     {descripcion}\n     $", " ".join(map(str, cmd)))
    if problemas:
        print("\nprerrequisitos que faltan:")
        for p in problemas:
            print("  -", p)
    else:
        print("\nprerrequisitos: ok")


def crear_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog="\n".join(__doc__.splitlines()[1:]))
    g = ap.add_argument_group("etapas")
    g.add_argument("--solo", help=f"solo estas etapas, separadas por coma ({', '.join(ETAPAS)})")
    g.add_argument("--desde", choices=ETAPAS, help="primera etapa a ejecutar (por defecto: entorno)")
    g.add_argument("--hasta", choices=ETAPAS, help="ultima etapa a ejecutar (por defecto: evaluar)")
    g.add_argument("--dry-run", action="store_true", help="muestra el plan y los prerrequisitos que faltan; no ejecuta")
    g = ap.add_argument_group("preguntas")
    g.add_argument("--split", choices=["sample", "test"], default="sample")
    g.add_argument("--entrada", type=Path, help="JSONL de preguntas (por defecto el del split)")
    g.add_argument("--ids", type=int, nargs="+", help="solo estos ids")
    g.add_argument("--rango", help="solo los ids A-B (inclusivos), p. ej. 100-200")
    g.add_argument("--limite", type=int, help="solo las N primeras preguntas (humo)")
    g.add_argument("--particion", help="I/N: items j de la entrada con j %% N == I-1 (repartir entre maquinas)")
    g.add_argument("--experimento", default="windows_rtx4090", help="nombre de la corrida (trazas, experiments.csv)")
    g.add_argument("--sin-reanudar", action="store_true", help="empezar las preguntas de cero (medir latencias limpias)")
    g = ap.add_argument_group("evaluar")
    g.add_argument("--entrega", type=Path, help="entrega JSONL a evaluar (por defecto la que producen las preguntas)")
    g.add_argument("--ragas", action="store_true", help="exige el juez de texto libre (falla sin OPENROUTER_API_KEY)")
    g.add_argument("--sin-ragas", action="store_true", help="no correr el juez aunque haya llave")
    g.add_argument("--no-csv", action="store_true", help="no agregar fila a evaluation/experiments.csv")
    g = ap.add_argument_group("entorno, corpus e indice")
    g.add_argument("--corpus", type=Path, help="carpeta (con .txt o con corpus/) o .zip de donde copiar los .txt")
    g.add_argument("--reindexar", action="store_true", help="borrar indice/ y cache_emb/ y codificar todo de nuevo")
    g.add_argument("--recrear-entorno", action="store_true", help="borrar .venv y reinstalar")
    g.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto", help="encoder: auto usa CUDA si hay NVIDIA")
    g.add_argument("--batch", type=int, default=64, help="batch del encoder (64 cabe de sobra en 24 GB)")
    g.add_argument("--cuda-torch", choices=["cu126", "cu130"], help="forzar el indice de ruedas de torch")
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = crear_parser()
    args = ap.parse_args(argv)
    try:
        etapas = resolver_etapas(args.solo, args.desde, args.hasta)
    except ValueError as e:
        ap.error(str(e))
    if sys.platform == "darwin" and args.device == "cuda":
        ap.error("--device cuda no existe en Mac")

    gpu = gpu_nvidia()
    desc = "ninguna NVIDIA"
    if gpu:
        desc = f"{gpu['nombre']} ({gpu['memoria_mb'] // 1024} GB, driver CUDA {gpu['cuda'][0]}.{gpu['cuda'][1]})"
    print(f"repo: {ROOT}\nplataforma: {sys.platform}  python: {sys.version.split()[0]}  GPU: {desc}\netapas: {', '.join(etapas)}")
    ids, problemas = validar_argumentos(args, etapas)
    if args.dry_run:
        describir_plan(args, etapas, ids, problemas)
        return 1 if problemas else 0
    if problemas:
        raise SystemExit("No se puede empezar:\n  - " + "\n  - ".join(problemas))

    t0 = time.perf_counter()
    if "entorno" in etapas:
        etapa_entorno(args, gpu)
    elif any(e in etapas for e in ("indice", "preguntas", "evaluar")):
        device_sin_entorno(args, gpu)
    if "corpus" in etapas:
        etapa_corpus(args)
    if "indice" in etapas:
        etapa_indice(args)
    proc, codigo = None, 0
    try:
        if "decoder" in etapas or "preguntas" in etapas:  # preguntas necesita el servidor aunque no se pida la etapa
            proc = etapa_decoder(args, gpu)
        if "preguntas" in etapas:
            etapa_preguntas(args, ids)
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(15)
            except subprocess.TimeoutExpired:
                proc.kill()
    if "evaluar" in etapas:
        codigo = etapa_evaluar(args)
    print(f"\nlisto en {(time.perf_counter() - t0) / 60:.1f} min")
    return codigo


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    sys.exit(main())
