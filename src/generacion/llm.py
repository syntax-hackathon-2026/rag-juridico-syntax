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


class Decoder:
    def __init__(self, url: str | None = None):
        self.url = (url or config.LLM_URL).rstrip("/") + "/chat/completions"
        self.cfg = config.llm_config()

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
        req = urllib.request.Request(self.url, data=json.dumps(cuerpo).encode("utf-8"),
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
        return Respuesta(texto=eleccion["message"].get("content") or "", fin=eleccion.get("finish_reason", ""),
                         uso=datos.get("usage") or {}, tiempos=tiempos, ms=round(ms, 1),
                         razonamiento=eleccion["message"].get("reasoning_content") or "")
