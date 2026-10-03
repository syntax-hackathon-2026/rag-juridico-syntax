"""Rutas del proyecto: repo (codigo + manifest) y carpeta local del corpus.

El corpus procesado y el indice se generan en `<repo>/data_corpus/`, una carpeta
local de cada persona, ignorada por git. El pipeline la reconstruye desde cero a
partir del manifest; al entregar se comprime y se publica aparte.

Estructura de CORPUS_DIR:

    corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
    indice/   index.faiss + chunks.jsonl

`corpus_manifest.json` NO esta en CORPUS_DIR: vive versionado en la raiz del repo.

Las fuentes originales (sin procesar) viven en `<repo>/data/raw/` (ignorada por
git, regenerable con src/ingesta/descargar_fuentes.py), por formato:

    raw/html/<doc_id>/<archivo original>   descargas automaticas (Senado en partes
                                           <base>.html, <base>_pr001.html, ...)
    raw/pdf/<archivo original>             PDF manuales o descargados
    raw/rtf/<archivo original>             RTF/DOCX manuales

Los PDF/RTF se asocian a su doc_id en data/registros/mapa_archivos.json; las carpetas de
raw/html/ ya se llaman como el doc_id.

Todo el codigo debe importar las rutas de aqui; nadie escribe rutas a mano.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ABSTENCION_MODO = os.environ.get("SYNTAX_ABSTENCION", "off")
if ABSTENCION_MODO not in {"off", "reglas"}:
    raise ValueError(
        "SYNTAX_ABSTENCION debe ser 'off' o 'reglas', "
        f"no {ABSTENCION_MODO!r}"
    )
ABSTENCION_CONFIG_PATH = ROOT / "config" / "abstencion.json"
MANIFEST_PATH = ROOT / "corpus_manifest.json"
CORPUS_DIR = ROOT / "data_corpus"
CORPUS_TEXTOS = CORPUS_DIR / "corpus"
INDICE_DIR = CORPUS_DIR / "indice"
RAW_DIR = ROOT / "data" / "raw"  # originales por formato (html/, pdf/, rtf/); leen los parsers de src/ingesta/parsear_*.py
RAW_HTML_DIR = RAW_DIR / "html"
PARSEO_PATH = CORPUS_DIR / "parseo.json"  # inventario del parseo, fuera de corpus/ (que se publica tal cual)
MAPA_ARCHIVOS_PATH = ROOT / "data" / "registros" / "mapa_archivos.json"  # archivo original -> doc_id (versionado)
FUENTES_PATH = ROOT / "data" / "registros" / "fuentes_descargadas.json"  # url/fuente/canonico por doc_id (versionado)
CHUNKS_PATH = INDICE_DIR / "chunks.jsonl"
FAISS_PATH = INDICE_DIR / "index.faiss"
BM25_DIR = INDICE_DIR / "bm25"
INDICE_INFO_PATH = INDICE_DIR / "indice_info.json"  # encoder, revision, n, sha256 de chunks.jsonl
RESUMEN_INDICE_PATH = INDICE_DIR / "resumen_indice.json"  # por doc_id: fragmentos, articulos, avisos
EMB_CACHE_DIR = CORPUS_DIR / "cache_emb"  # fuera de indice/ (no se publica): vectores por hash de texto
EVALUATION_DIR = ROOT / "evaluation"
REFERENCIAS_BASELINE_PATH = EVALUATION_DIR / "retrieval" / "e01_bge_m3_hibrido.jsonl"
# Plan 06: lookup por metadata; KEEP en e13_lookup (mejora doc_hit@1 y MRR sin regresiones, INDEXACION.md 14).
LOOKUP_MODO = os.environ.get("SYNTAX_LOOKUP", "on")
LOOKUP_VARIANTE = os.environ.get("SYNTAX_LOOKUP_VARIANTE", "a")
LOOKUP_FUENTE = os.environ.get("SYNTAX_LOOKUP_FUENTE", "consulta")
LOOKUP_BONUS = float(os.environ.get("SYNTAX_LOOKUP_BONUS", "0.005"))
LOOKUP_M = int(os.environ.get("SYNTAX_LOOKUP_M", "2"))
if LOOKUP_MODO not in {"off", "on"}:
    raise ValueError("SYNTAX_LOOKUP debe ser off|on")
if LOOKUP_VARIANTE not in {"a", "b", "c"}:
    raise ValueError("SYNTAX_LOOKUP_VARIANTE debe ser a|b|c")
if LOOKUP_FUENTE not in {"consulta", "pregunta"}:
    raise ValueError("SYNTAX_LOOKUP_FUENTE debe ser consulta|pregunta")
if not 0 <= LOOKUP_BONUS < float("inf") or LOOKUP_M < 1:
    raise ValueError("LOOKUP_BONUS debe ser finito no negativo y LOOKUP_M positivo")
# Filtro "solo por cita" (docs/INDEXACION.md 14): los documentos del registro se
# quitan de las ramas BM25/densa salvo que la consulta nombre su cuerpo canonico.
# off | sentencias (las 279 sentencias nuevas de v3) | todo (+ las normas nuevas).
SOLO_POR_CITA_PATH = ROOT / "data" / "registros" / "solo_por_cita.json"
FILTRO_CITA = os.environ.get("SYNTAX_FILTRO_CITA", "sentencias")
if FILTRO_CITA not in {"off", "sentencias", "todo"}:
    raise ValueError("SYNTAX_FILTRO_CITA debe ser off|sentencias|todo")
# Prioridad por area (docs/INDEXACION.md 15): en el hibrido, el score RRF de los fragmentos
# cuyo documento lleva el `area` de la pregunta (areas de corpus_manifest.json) se multiplica
# por este factor. Solo reordena los candidatos de las ramas, nunca descarta. 1.0 = apagado.
AREA_BOOST = float(os.environ.get("SYNTAX_AREA_BOOST", "2.0"))
if not 1.0 <= AREA_BOOST < float("inf"):
    raise ValueError("SYNTAX_AREA_BOOST debe ser un factor finito >= 1")
# Composicion del top-k (docs/INDEXACION.md 17): las ventanas de sentencias desplazan
# articulos (#647: CC art. 176 en el puesto 17 con 6 sentencias en el top-10).
# CUPO_NORMAS = minimo de fragmentos de normas en el top-k (cambia sentencias por las
# mejores normas que siguen). MAX_POR_DOC = maximo de ventanas por sentencia. 0 = apagado.
CUPO_NORMAS = int(os.environ.get("SYNTAX_CUPO_NORMAS", "0"))
MAX_POR_DOC = int(os.environ.get("SYNTAX_MAX_POR_DOC", "0"))
if CUPO_NORMAS < 0 or MAX_POR_DOC < 0:
    raise ValueError("SYNTAX_CUPO_NORMAS y SYNTAX_MAX_POR_DOC deben ser >= 0")
# Busqueda por metadatos (docs/INDEXACION.md 19). Todo en el hibrido, solo reordena o suma.
# FACTOR_VOTO: score de las ventanas salvamento/aclaracion (salvo que la consulta pida el voto).
# FACTOR_VIGENCIA: score de los fragmentos `derogado` (salvo que la consulta hable de vigencia).
# CUERPO: con un cuerpo nombrado en la consulta, off | boost (x CUERPO_BOOST a sus fragmentos)
#   | rama (BM25 + denso restringidos a ese documento como ramas RRF de peso CUERPO_PESO).
# ALIAS: nombres de normas que citations.py no reconoce (titulos del manifest + pocos fijos).
# KEEP en r48_voto_boost (voto 0.5 + alias + boost); vigencia neutra y rama REVERT (seccion 19).
FACTOR_VOTO = float(os.environ.get("SYNTAX_FACTOR_VOTO", "0.5"))
FACTOR_VIGENCIA = float(os.environ.get("SYNTAX_FACTOR_VIGENCIA", "1.0"))
CUERPO = os.environ.get("SYNTAX_CUERPO", "boost")
CUERPO_PESO = float(os.environ.get("SYNTAX_CUERPO_PESO", "1.0"))
CUERPO_BOOST = float(os.environ.get("SYNTAX_CUERPO_BOOST", "1.5"))
ALIAS = os.environ.get("SYNTAX_ALIAS", "on")
if not (0 < FACTOR_VOTO <= 1 and 0 < FACTOR_VIGENCIA <= 1):
    raise ValueError("SYNTAX_FACTOR_VOTO y SYNTAX_FACTOR_VIGENCIA deben estar en (0, 1]")
if CUERPO not in {"off", "boost", "rama"} or ALIAS not in {"off", "on"}:
    raise ValueError("SYNTAX_CUERPO debe ser off|boost|rama y SYNTAX_ALIAS off|on")
if CUERPO_PESO < 0 or CUERPO_BOOST < 1:
    raise ValueError("SYNTAX_CUERPO_PESO >= 0 y SYNTAX_CUERPO_BOOST >= 1")
EXPERIMENTS_CSV = EVALUATION_DIR / "experiments.csv"

# Encoder denso (enunciado 3.1). bge-m3: MIT, 1024 dim, 8192 tokens, sin prefijos.
# La revision fija el commit del modelo en Hugging Face: el indice publicado y las
# consultas en vivo deben usar exactamente los mismos pesos.
ENCODER_MODEL = "BAAI/bge-m3"
ENCODER_REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
ENCODER_MAX_SEQ = 1024

# cuda | mps | cpu | auto (cuda > mps > cpu). Por configuracion, nunca por plataforma.
DEVICE = os.environ.get("SYNTAX_DEVICE", "auto")

# Decoder (enunciado 3.1): GGUF servido en local por llama.cpp (llama-server, API
# compatible con OpenAI en localhost). Cada entrada fija repo, revision (commit de
# Hugging Face) y sha256 del archivo: la corrida final y la verificacion en vivo
# deben usar exactamente el mismo archivo. SYNTAX_LLM elige la entrada.
MODELOS_DIR = ROOT / "modelos"  # GGUF descargados (en .gitignore)
LLM_MODELOS = {
    "qwen3-8b-q4": {
        "repo": "Qwen/Qwen3-8B-GGUF",
        "revision": "7c41481f57cb95916b40956ab2f0b139b296d974",
        "archivo": "Qwen3-8B-Q4_K_M.gguf",
        "sha256": "d98cdcbd03e17ce47681435b5150e34c1417f50b5c0019dd560e4882c5745785",
        "cuantizacion": "Q4_K_M",
        "thinking": True,  # Qwen3 hibrido: se apaga con enable_thinking=false
    },
    "qwen3-8b-q8": {  # mismo modelo y repo, cuantizacion mas fiel (8,7 GB): para GPUs de 24 GB (RTX 4090)
        "repo": "Qwen/Qwen3-8B-GGUF",
        "revision": "7c41481f57cb95916b40956ab2f0b139b296d974",
        "archivo": "Qwen3-8B-Q8_0.gguf",
        "sha256": "408b955510e196121c1c375201744783b5c9a43c7956d73fc78df54c66e883d6",
        "cuantizacion": "Q8_0",
        "thinking": True,
    },
    "qwen3-4b-2507-q4": {  # plan B si el 8B no cabe en el tiempo (no hay GGUF oficial de Qwen)
        "repo": "unsloth/Qwen3-4B-Instruct-2507-GGUF",
        "revision": "a06e946bb6b655725eafa393f4a9745d460374c9",
        "archivo": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
        "sha256": "3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597",
        "cuantizacion": "Q4_K_M",
        "thinking": False,
    },
}
LLM = os.environ.get("SYNTAX_LLM", "qwen3-8b-q8")
LLM_URL = os.environ.get("SYNTAX_LLM_URL", "http://127.0.0.1:8080/v1")
LLM_CTX = 8192
LLM_SEED = 0
LLM_TIMEOUT_S = 600
# Cache de respuestas del decoder por hash de la peticion (generacion/llm.py): on | off.
# off en la verificacion en vivo y al medir latencia.
LLM_CACHE = os.environ.get("SYNTAX_LLM_CACHE", "on")
if LLM_CACHE not in ("on", "off"):
    raise ValueError("SYNTAX_LLM_CACHE: on | off")

# Pipeline de respuesta. retrieval_k fijo en 10 (el evaluador mira los 10 primeros
# pasajes); generation_k es el hiperparametro de cuantos ve el decoder.
MODO_RECUPERACION = "hibrido"
RETRIEVAL_K = 10
GENERATION_K = int(os.environ.get("SYNTAX_GENERATION_K", "5"))
# Cabeceras de la evidencia agregadas a los campos citables: no | generacion (los
# pasajes que vio el decoder) | top10. Ver generacion/responder.py.
CITAR_EVIDENCIA = os.environ.get("SYNTAX_CITAR_EVIDENCIA", "top10")
# Thinking de Qwen3 por formato (docs/GENERACION.md): formatos separados por coma
# (p. ej. "multiple_choice") y tope de tokens de razonamiento por llamada
# (thinking_budget_tokens de llama-server). El razonamiento va solo a la traza.
PENSAR_FORMATOS = frozenset(f for f in os.environ.get("SYNTAX_PENSAR_FORMATOS", "").split(",") if f.strip())
PENSAR_TOKENS = int(os.environ.get("SYNTAX_PENSAR_TOKENS", "768"))
if not PENSAR_FORMATOS <= {"multiple_choice", "semi_open", "open_ended"} or PENSAR_TOKENS < 1:
    raise ValueError("SYNTAX_PENSAR_FORMATOS: multiple_choice,semi_open,open_ended; SYNTAX_PENSAR_TOKENS > 0")
# Recuperacion agentica y glosario (docs/GENERACION.md, seccion 9). Todo off|on.
# GLOSARIO: equivalencias nombre <-> numero de norma (titulo del manifest) en el prompt,
#   para cabeceras de pasajes y opciones; nunca toca pasajes_recuperados.texto.
# CONSULTA_OPCIONES: en cerradas, una consulta por opcion sustantiva fusionada por RRF.
# PLANIFICADOR: una llamada corta al decoder reformula la consulta y nombra normas
#   candidatas (que entran por lookup); PESO_EXTRA pondera las listas extra en el RRF.
GLOSARIO = os.environ.get("SYNTAX_GLOSARIO", "on")
CONSULTA_OPCIONES = os.environ.get("SYNTAX_CONSULTA_OPCIONES", "off")
PLANIFICADOR = os.environ.get("SYNTAX_PLANIFICADOR", "off")
PESO_EXTRA = float(os.environ.get("SYNTAX_PESO_EXTRA", "1.0"))
PLAN_NORMAS = os.environ.get("SYNTAX_PLAN_NORMAS", "on")  # off: solo las reformulaciones del plan
# Version de las instrucciones de cerradas (generacion/prompts.py): p-v0 | p-v2.
PROMPT_MC = os.environ.get("SYNTAX_PROMPT_MC", "p-v0")
if PROMPT_MC not in {"p-v0", "p-v2"}:
    raise ValueError("SYNTAX_PROMPT_MC debe ser p-v0|p-v2")
# Texto libre (docs/GENERACION.md, seccion 10).
# PROMPT_TL: instrucciones de semi_open/open_ended: p-v0 | p-tl1 (forma segun la pregunta).
# SECCION_SENTENCIA: si la pregunta nombra una sentencia y pide una seccion (problema
#   juridico, hechos, decision), sus fragmentos de esa seccion suben dentro del top-10.
# PENSAR_CASOS: thinking en texto libre cuando la pregunta tiene al menos N palabras (0 = off).
PROMPT_TL = os.environ.get("SYNTAX_PROMPT_TL", "p-v0")
if PROMPT_TL not in {"p-v0", "p-tl1"}:
    raise ValueError("SYNTAX_PROMPT_TL debe ser p-v0|p-tl1")
SECCION_SENTENCIA = os.environ.get("SYNTAX_SECCION_SENTENCIA", "off")
PENSAR_CASOS = int(os.environ.get("SYNTAX_PENSAR_CASOS", "0"))
for _nombre, _valor in (("SYNTAX_GLOSARIO", GLOSARIO), ("SYNTAX_CONSULTA_OPCIONES", CONSULTA_OPCIONES),
                        ("SYNTAX_PLANIFICADOR", PLANIFICADOR), ("SYNTAX_PLAN_NORMAS", PLAN_NORMAS),
                        ("SYNTAX_SECCION_SENTENCIA", SECCION_SENTENCIA)):
    if _valor not in {"off", "on"}:
        raise ValueError(f"{_nombre} debe ser off|on")
if not 0.0 <= PESO_EXTRA < float("inf"):
    raise ValueError("SYNTAX_PESO_EXTRA debe ser finito no negativo")
SALIDAS_DIR = ROOT / "salidas"  # entregas de desarrollo (en .gitignore)
PLANES_DIR = SALIDAS_DIR / "planes"  # cache determinista de planes (planificador)
TRAZAS_DIR = SALIDAS_DIR / "trazas"
CACHE_LLM_DIR = SALIDAS_DIR / "cache_llm"  # un JSONL por GGUF; se puede copiar entre maquinas iguales
SCHEMA_PATH = ROOT / "schema" / "submission.schema.json"
SAMPLE_PATH = ROOT / "data" / "sample_50.jsonl"
TEST_PATH = ROOT / "data" / "test_992.jsonl"  # se entrega el sabado 09:00
SUBMISSION_PATH = ROOT / "submissions.jsonl"


def lookup_metadata() -> dict:
    return {"modo": LOOKUP_MODO, "variante": LOOKUP_VARIANTE,
            "fuente": LOOKUP_FUENTE, "bonus": LOOKUP_BONUS, "m": LOOKUP_M,
            "aplica_a": "hibrido", "parser": "scripts/citations.py"}


def filtro_metadata() -> dict:
    return {"modo": FILTRO_CITA, "registro": str(SOLO_POR_CITA_PATH.relative_to(ROOT)).replace("\\", "/")}


def area_metadata() -> dict:
    return {"boost": AREA_BOOST, "fuente": "corpus_manifest.json", "aplica_a": "hibrido"}


def metadatos_metadata() -> dict:
    return {"factor_voto": FACTOR_VOTO, "factor_vigencia": FACTOR_VIGENCIA, "cuerpo": CUERPO,
            "cuerpo_peso": CUERPO_PESO, "cuerpo_boost": CUERPO_BOOST, "alias": ALIAS}


def composicion_metadata() -> dict:
    return {"cupo_normas": CUPO_NORMAS, "max_por_doc": MAX_POR_DOC, "aplica_a": "top-k"}


def agentico_metadata() -> dict:
    return {"glosario": GLOSARIO, "consulta_opciones": CONSULTA_OPCIONES,
            "planificador": PLANIFICADOR, "plan_normas": PLAN_NORMAS, "peso_extra": PESO_EXTRA,
            "prompt_mc": PROMPT_MC}


def abstencion_metadata() -> dict:
    """Modo de abstencion y hash del archivo versionado para la meta de corrida."""
    return {
        "modo": ABSTENCION_MODO,
        "config_sha256": hashlib.sha256(ABSTENCION_CONFIG_PATH.read_bytes()).hexdigest(),
    }


def llm_config() -> dict:
    """Entrada de LLM_MODELOS elegida por SYNTAX_LLM, con su ruta local."""
    if LLM not in LLM_MODELOS:
        raise SystemExit(f"SYNTAX_LLM={LLM!r} no existe; opciones: {sorted(LLM_MODELOS)}")
    return {**LLM_MODELOS[LLM], "nombre": LLM, "ruta": MODELOS_DIR / LLM_MODELOS[LLM]["archivo"]}


def resolver_device() -> str:
    """Device efectivo segun DEVICE; 'auto' elige el mejor disponible."""
    if DEVICE != "auto":
        return DEVICE
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def raw_html_dir(doc_id: str) -> Path:
    """Carpeta con las paginas HTML originales de un doc_id."""
    return RAW_HTML_DIR / doc_id


def docs_en_raw() -> set[str]:
    """doc_id que ya tienen algun original en data/raw/ (HTML o PDF/RTF mapeado)."""
    import json
    import unicodedata

    nfc = lambda s: unicodedata.normalize("NFC", s)  # macOS entrega nombres en NFD
    docs = {d.name for d in RAW_HTML_DIR.glob("*") if d.is_dir() and any(d.iterdir())}
    if MAPA_ARCHIVOS_PATH.is_file():
        mapa = json.loads(MAPA_ARCHIVOS_PATH.read_text(encoding="utf-8"))
        presentes = {nfc(f.name) for sub in ("pdf", "rtf") for f in (RAW_DIR / sub).glob("*")}
        docs |= {doc for nombre, doc in mapa.items() if nfc(nombre) in presentes}
    return docs


def contar_chunks() -> int:
    """Numero de fragmentos en chunks.jsonl (lineas no vacias)."""
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        return sum(1 for linea in f if linea.strip())


def verificar_indice() -> int:
    """Comprueba que indice/ este completo y coherente; devuelve el numero de fragmentos.

    Protege contra leer un indice a medio construir: chunks.jsonl e index.faiss
    deben existir y tener el mismo numero de vectores/fragmentos.
    """
    for ruta in (CHUNKS_PATH, FAISS_PATH):
        if not ruta.is_file() or ruta.stat().st_size == 0:
            raise SystemExit(
                f"Falta o esta vacio: {ruta}\n"
                "Reconstruir el indice."
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
            f"chunks.jsonl {n_chunks} fragmentos. Reconstruir el indice."
        )
    return n_chunks
