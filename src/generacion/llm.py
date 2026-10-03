"""Interfaz unica del decoder: generar(mensajes, schema) -> Respuesta.

    from generacion.llm import Decoder
    dec = Decoder()
    r = dec.generar([{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
                    schema={...}, max_tokens=600)
    r.texto, r.tiempos

Backend: llama-server (llama.cpp) por HTTP en localhost, API compatible con OpenAI,
solo con stdlib. El resto del pipeline no sabe que motor hay detras.

Determinismo (temperatura 0, enunciado 3.1): temperature=0 (greedy), seed fija,
un solo slot en el servidor (modelo.py) y cache_prompt=false: la documentacion de
llama-server advierte que reutilizar la cache KV puede cambiar los logits segun el
tamano de lote, y la verificacion en vivo exige salida practicamente literal.
El JSON Schema se pasa como response_format: llama.cpp lo convierte en gramatica y
la salida siempre parsea, con las claves en el orden del schema.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402


@dataclass
class Respuesta:
    texto: str
    fin: str = ""  # finish_reason: "stop" | "length"
    uso: dict = field(default_factory=dict)  # prompt_tokens, completion_tokens
    tiempos: dict = field(default_factory=dict)  # ms de prefill y generacion, tokens/s
    ms: float = 0.0
    razonamiento: str = ""  # reasoning_content (solo con pensar=True)
    cache: bool = False  # True si salio de la cache de respuestas (ms es el de la llamada original)


class CacheRespuestas:
    """Respuestas del decoder por hash de la peticion (SYNTAX_LLM_CACHE=on).

    A temperatura 0, con seed fija, un slot y cache_prompt=false, la misma peticion al
    mismo GGUF y la misma build de llama.cpp da la misma salida (comprobado con
    comparar_entregas.py), asi que reutilizarla equivale a volver a llamar. Sirve para
    repetir las 992 con un indice nuevo: solo se regeneran las preguntas cuyo prompt
    cambio. Un JSONL por GGUF en salidas/cache_llm/, solo se agregan lineas; se puede
    copiar entre maquinas iguales. La verificacion en vivo corre con SYNTAX_LLM_CACHE=off.
    """

    def __init__(self, ruta: Path, firma: str):
        self.ruta = ruta
        self.firma = firma
        self.datos: dict[str, dict] = {}
        if ruta.is_file():
            with ruta.open(encoding="utf-8") as f:
                for linea in f:
                    if linea.strip():
                        r = json.loads(linea)
                        self.datos[r["clave"]] = r

    def clave(self, cuerpo: dict) -> str:
        canon = json.dumps(cuerpo, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256((self.firma + "\n" + canon).encode("utf-8")).hexdigest()

    def leer(self, clave: str) -> Respuesta | None:
        r = self.datos.get(clave)
        if r is None:
            return None
        return Respuesta(texto=r["texto"], fin=r["fin"], uso=r["uso"], tiempos=r["tiempos"], ms=r["ms"],
                         razonamiento=r.get("razonamiento", ""), cache=True)

    def guardar(self, clave: str, r: Respuesta) -> None:
        reg = {"clave": clave, "texto": r.texto, "fin": r.fin, "uso": r.uso, "tiempos": r.tiempos,
               "ms": r.ms, "razonamiento": r.razonamiento}
        self.datos[clave] = reg
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with self.ruta.open("a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")


def build_servidor(url: str) -> str:
    """build_info de llama-server (/props); vacio si no responde o no lo publica."""
    try:
        with urllib.request.urlopen(url.rstrip("/").removesuffix("/v1") + "/props", timeout=5) as r:
            return str(json.loads(r.read().decode("utf-8")).get("build_info") or "")
    except (urllib.error.URLError, OSError, ValueError):
        return ""


class Decoder:
    def __init__(self, url: str | None = None, cache: bool | None = None):
        base = url or config.LLM_URL
        self.url = base.rstrip("/") + "/chat/completions"
        self.cfg = config.llm_config()
        self.cache = None
        if config.LLM_CACHE == "on" if cache is None else cache:
            firma = f"{self.cfg['sha256']}|{build_servidor(base)}"
            self.cache = CacheRespuestas(config.CACHE_LLM_DIR / f"{self.cfg['nombre']}.jsonl", firma)

    def generar(self, mensajes: list[dict], schema: dict | None = None, max_tokens: int = 800,
                pensar: bool = False) -> Respuesta:
        """`pensar`: thinking de Qwen3 con tope config.PENSAR_TOKENS. max_tokens cuenta
        razonamiento + respuesta, asi que se le suma el tope. llama-server separa el
        razonamiento en reasoning_content y aplica la gramatica del schema despues."""
        pensar = pensar and bool(self.cfg.get("thinking"))
        cuerpo = {
            "model": self.cfg["nombre"],
            "messages": mensajes,
            "temperature": 0.0,
            "seed": config.LLM_SEED,
            "max_tokens": max_tokens + (config.PENSAR_TOKENS if pensar else 0),
            "cache_prompt": False,
            "stream": False,
        }
        if self.cfg.get("thinking"):
            cuerpo["chat_template_kwargs"] = {"enable_thinking": pensar}
        if pensar:
            cuerpo["thinking_budget_tokens"] = config.PENSAR_TOKENS
        if schema is not None:
            cuerpo["response_format"] = {"type": "json_schema",
                                         "json_schema": {"name": "respuesta", "strict": True, "schema": schema}}
        clave = self.cache.clave(cuerpo) if self.cache else None
        if clave and (guardada := self.cache.leer(clave)) is not None:
            return guardada
        req =urllib.request.Request(self.url, data=json.dumps(cuerpo).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT_S) as r:
                datos = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"llama-server {e.code}: {e.read().decode('utf-8', 'replace')[:500]}") from e
        ms = (time.perf_counter() - t0) * 1000
        eleccion = datos["choices"][0]
        t = datos.get("timings") or {}
        tiempos = {k: round(t[k], 1) for k in ("prompt_n", "prompt_ms", "prompt_per_second",
                                               "predicted_n", "predicted_ms", "predicted_per_second") if k in t}
        resp = Respuesta(texto=eleccion["message"].get("content") or "", fin=eleccion.get("finish_reason", ""),
                         uso=datos.get("usage") or {}, tiempos=tiempos, ms=round(ms, 1),
                         razonamiento=eleccion["message"].get("reasoning_content") or "")
        if clave:
            self.cache.guardar(clave, resp)
        return resp
