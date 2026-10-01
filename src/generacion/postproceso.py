"""Salida del decoder -> registro de la entrega (schema/submission.schema.json).

Recortes deterministas de longitud (enunciado, paso 3): semiabierta de 3 a 5
oraciones y maximo 150 palabras; `analisis` de 5 a 8 oraciones. Se recorta por
oracion entera, nunca a mitad de una cita.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from generacion.citas import oraciones  # noqa: E402

CAMPOS = {
    "multiple_choice": ("respuesta_correcta", "justificacion", "descarte_opciones"),
    "semi_open": ("respuesta", "palabras_clave", "referencia_legal"),
    "open_ended": ("marco_normativo", "analisis", "jurisprudencia", "conclusion"),
}
MAX_PALABRAS_SEMI = 150
MAX_ORACIONES_SEMI = 5
MAX_ORACIONES_ANALISIS = 8


def recortar(texto: str, max_oraciones: int, max_palabras: int | None = None) -> str:
    salida: list[str] = []
    palabras = 0
    for o in oraciones(texto)[:max_oraciones]:
        n = len(o.split())
        if max_palabras is not None and salida and palabras + n > max_palabras:
            break
        salida.append(o)
        palabras += n
    texto = " ".join(salida)
    if max_palabras is not None and len(texto.split()) > max_palabras:  # una sola oracion enorme
        texto = " ".join(texto.split()[:max_palabras])
    return texto


def normalizar(formato: str, salida: dict, letras: list[str]) -> dict:
    """Campos del formato a partir del JSON del decoder, con limites de longitud."""
    if formato == "multiple_choice":
        letra = salida.get("respuesta_correcta")
        descarte = {l: str(v).strip() for l, v in (salida.get("descarte_opciones") or {}).items()
                    if l in letras and l != letra}
        return {"respuesta_correcta": letra if letra in letras else None,
                "justificacion": str(salida.get("justificacion") or "").strip(),
                "descarte_opciones": descarte}
    if formato == "semi_open":
        claves = [str(p).strip() for p in salida.get("palabras_clave") or [] if str(p).strip()]
        return {"respuesta": recortar(str(salida.get("respuesta") or ""), MAX_ORACIONES_SEMI, MAX_PALABRAS_SEMI),
                "palabras_clave": list(dict.fromkeys(claves)),
                "referencia_legal": str(salida.get("referencia_legal") or "").strip()}
    campos = {k: str(salida.get(k) or "").strip() for k in CAMPOS["open_ended"]}
    campos["analisis"] = recortar(campos["analisis"], MAX_ORACIONES_ANALISIS)
    return campos


def vacios(formato: str) -> dict:
    """Campos de un item abstenido (como el ejemplo oficial del enunciado, anexo A)."""
    if formato == "multiple_choice":
        return {"respuesta_correcta": None, "justificacion": "", "descarte_opciones": {}}
    if formato == "semi_open":
        return {"respuesta": "", "palabras_clave": [], "referencia_legal": ""}
    return {k: "" for k in CAMPOS["open_ended"]}


def faltantes(formato: str, campos: dict) -> list[str]:
    """Campos obligatorios vacios (mismo criterio que evaluate.validate)."""
    return [k for k in CAMPOS[formato] if campos.get(k) in (None, "", [], {})]


def registro(item_id: int, formato: str, campos: dict, abstencion: bool, pasajes: list[dict],
             latencia_ms: int) -> dict:
    return {"id": item_id, "formato": formato, "abstencion": abstencion, **campos,
            "pasajes_recuperados": pasajes, "latencia_ms": latencia_ms}


@lru_cache(maxsize=1)
def _validador():
    import jsonschema

    esquema = json.loads(config.SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(esquema)


def validar(reg: dict) -> list[str]:
    """Errores contra el schema oficial.

    Unica excepcion: cerrada con abstencion=true y respuesta_correcta=null, que la
    descripcion del schema admite aunque su enum no lo incluya.
    """
    r = dict(reg)
    if r.get("abstencion") and r.get("formato") == "multiple_choice" and r.get("respuesta_correcta") is None:
        r["respuesta_correcta"] = "A"
    errores = [f"{'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}" for e in _validador().iter_errors(r)]
    if not r.get("abstencion") and not r.get("pasajes_recuperados"):
        errores.append("pasajes_recuperados vacio sin abstencion")
    if not r.get("abstencion"):
        errores += [f"campo vacio: {k}" for k in faltantes(r["formato"], r)]
    return errores
