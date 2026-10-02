"""Recuperacion agentica: planificador (query translation + normas candidatas) y
recuperacion compuesta, compartida por responder.py y retrieval_eval.py.

    top, info = recuperar(item, retriever, decoder)

Diagnostico que lo motiva (docs/GENERACION.md, seccion 9): con la consulta literal
(pregunta + opciones) el articulo que responde no llega al top-10 en las preguntas
conceptuales (art_hit@10 = 0,58 en e20; #647 necesita el art. 176 del Codigo Civil y
trae sentencias). El 8B sabe a menudo que norma regula el caso aunque no la pueda
citar sin respaldo. El planificador lo aprovecha en una llamada corta:

  - "consultas": 1-3 reformulaciones en lenguaje tecnico-juridico (query translation),
    que entran como listas extra del RRF (multi-query);
  - "normas": hasta 4 referencias con articulo ("articulo 176 del Codigo Civil"), que
    se resuelven con el parser oficial (citations) y traen por lookup el texto literal
    del articulo. Asi el conocimiento del modelo termina como evidencia citable.

Solo suma candidatos (RRF): nada de lo que trae la consulta principal se filtra, y las
citas de la respuesta se siguen validando contra los 10 pasajes. Determinista:
temperatura 0 y cache por sha256 de (pregunta, opciones, formato, PLAN_VERSION, LLM).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from recuperacion.consulta import consulta_de, consultas_opciones  # noqa: E402
from recuperacion.referencias import referencias_de  # noqa: E402

PLAN_VERSION = "plan-v2"
MAX_TOKENS = 260

# plan-v1 daba ejemplos con articulos reales y el 8B los copiaba en casi todas las
# preguntas ("articulo 25 del Codigo General del Proceso" en 16 de 41): ahora el
# formato va con marcadores, sin ninguna norma concreta.
SISTEMA = """Eres un abogado colombiano experto en investigación jurídica. No respondes la pregunta: preparas la búsqueda de la respuesta en un corpus de normas y sentencias colombianas.

Devuelve un objeto JSON con:
- "consultas": de 1 a 3 búsquedas cortas (máximo 25 palabras cada una) en lenguaje técnico-jurídico colombiano. Describe la institución jurídica, el supuesto y el efecto que la pregunta exige, con las palabras que usaría la norma que lo regula, no las de la pregunta.
- "normas": de 0 a 3 disposiciones colombianas que regulan específicamente lo que se pregunta, con el formato «artículo N del <código>» o «artículo N de la Ley <número> de <año>». Pon una norma solo si estás seguro de que ese artículo concreto trata el tema de la pregunta; ante cualquier duda, deja la lista vacía. Una norma equivocada empeora la búsqueda."""

SCHEMA = {
    "type": "object",
    "properties": {
        "consultas": {"type": "array", "items": {"type": "string", "minLength": 3, "maxLength": 220},
                      "minItems": 1, "maxItems": 3},
        "normas": {"type": "array", "items": {"type": "string", "minLength": 3, "maxLength": 120},
                   "minItems": 0, "maxItems": 3},
    },
    "required": ["consultas", "normas"],
    "additionalProperties": False,
}


def _usuario(item: dict) -> str:
    texto = f"Pregunta: {item['pregunta'].strip()}"
    ops = item.get("opciones")
    if ops:
        pares = ops.items() if isinstance(ops, dict) else zip("ABCD", ops)
        texto += "\n\nOpciones:\n" + "\n".join(f"{l}. {str(t).strip()}" for l, t in pares)
    if item.get("area"):
        texto += f"\n\nÁrea: {item['area']}"
    return texto


def _clave(item: dict) -> str:
    datos = {"pregunta": item["pregunta"], "opciones": item.get("opciones"), "formato": item.get("formato"),
             "area": item.get("area"), "plan_version": PLAN_VERSION, "llm": config.LLM,
             "sistema": SISTEMA, "schema": SCHEMA}
    return hashlib.sha256(json.dumps(datos, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def planificar(item: dict, decoder) -> dict:
    """Plan de busqueda de un item (solo pregunta/opciones/formato/area). Usa la cache."""
    ruta = config.PLANES_DIR / f"{_clave(item)}.json"
    if ruta.is_file():
        plan = json.loads(ruta.read_text(encoding="utf-8"))
        return {**plan, "ms": 0.0, "cache": True}
    msgs = [{"role": "system", "content": SISTEMA}, {"role": "user", "content": _usuario(item)}]
    r = decoder.generar(msgs, schema=SCHEMA, max_tokens=MAX_TOKENS)
    try:
        salida = json.loads(r.texto)
    except json.JSONDecodeError:
        salida = {}
    consultas = [c.strip() for c in salida.get("consultas") or [] if isinstance(c, str) and c.strip()][:3]
    normas = [n.strip() for n in salida.get("normas") or [] if isinstance(n, str) and n.strip()][:3]
    plan = {"id": item.get("id"), "plan_version": PLAN_VERSION, "consultas": consultas, "normas": normas,
            "normas_resueltas": [[list(ref) for ref in referencias_de(n)] for n in normas],
            "fin": r.fin, "uso": r.uso}
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {**plan, "ms": r.ms, "cache": False}


def recuperar(item: dict, retriever, decoder=None, k: int | None = None) -> tuple[list, dict]:
    """Top-k de un item segun la configuracion (SYNTAX_CONSULTA_OPCIONES, SYNTAX_PLANIFICADOR).

    Con ambos en off es exactamente la recuperacion de e20 (`retriever.retrieve`).
    `item` debe venir ya filtrado (sin legal_basis ni respuestas).
    """
    k = k or config.RETRIEVAL_K
    opciones = config.CONSULTA_OPCIONES == "on"
    consulta = consulta_de(item, sin_meta=opciones)
    kwargs = ({"consulta_lookup": item["pregunta"]} if config.LOOKUP_MODO == "on"
              and config.LOOKUP_FUENTE == "pregunta" else {})
    info: dict = {"consulta": consulta, "plan_ms": 0.0}
    consultas = [(consulta, 1.0)]
    if opciones:
        consultas += [(q, config.PESO_EXTRA) for q in consultas_opciones(item)]
    normas = None
    if config.PLANIFICADOR == "on":
        if decoder is None:
            raise ValueError("SYNTAX_PLANIFICADOR=on requiere el decoder")
        plan = planificar(item, decoder)
        info["plan"] = {kk: plan[kk] for kk in ("consultas", "normas", "normas_resueltas", "cache")}
        info["plan_ms"] = plan["ms"]
        consultas += [(q, config.PESO_EXTRA) for q in plan["consultas"]]
        normas = plan["normas"] if config.PLAN_NORMAS == "on" else None
    t0 = time.perf_counter()
    if len(consultas) == 1 and not normas:
        top = retriever.retrieve(consulta, k=k, modo=config.MODO_RECUPERACION, area=item.get("area"), **kwargs)
    else:
        top = retriever.retrieve_multi(consultas, k=k, modo=config.MODO_RECUPERACION, normas=normas,
                                       area=item.get("area"), peso_normas=config.PESO_EXTRA, **kwargs)
    info["ret_ms"] = (time.perf_counter() - t0) * 1000
    info["n_consultas"] = len(consultas)
    return top, info
