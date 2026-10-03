"""Consulta de recuperacion a partir de un item: la misma en la medicion y en el runtime.

Solo usa `pregunta` y `opciones` (nunca legal_basis ni respuestas).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

TIPOS = ("pregunta", "pregunta+opciones")

# Opciones que no aportan terminos de busqueda: "Todas las anteriores", "Ninguna de las
# anteriores", "(a) y (b)", "A y C son correctas", "Ninguna es correcta".
_META = re.compile(
    r"^\s*(?:todas|todos|ninguna|ninguno|ambas)\s+(?:de\s+)?(?:las\s+|los\s+)?"
    r"(?:anteriores|opciones|respuestas|son|es)\b.*$"
    r"|^\s*(?:las|los)\s+(?:dos|tres)\s+anteriores\b.*$"
    r"|^\s*\(?[a-d]\)?\s*(?:,\s*\(?[a-d]\)?\s*)*(?:y|e|o)\s*\(?[a-d]\)?\s*(?:son\s+correctas?)?\s*\.?\s*$",
    re.IGNORECASE)


# Instruccion fija de lectura (bloque de la Resolucion 368/2014: #721-#752 del test, #748):
# nombra el documento leido, no el fundamento, y llena el top-10 con ese documento.
# "No." lleva punto, por eso se corta en "responda", no en el primer punto.
_PREAMBULO = re.compile(
    r"^\s*habiendo\s+(?:hecho|realizado)\s+la\s+lectura\s+previa\b.*?\bresponda\b[^.:\n]*[.:]?\s*"
    r"(?:pregunta(?:\s+jur[ií]dica)?\s*[.:]\s*)?",
    re.IGNORECASE | re.DOTALL)


def sin_preambulo(pregunta: str) -> str:
    """Pregunta sin la instruccion de lectura; igual si no la trae o si no queda nada."""
    m = _PREAMBULO.match(pregunta)
    return (pregunta[m.end():].strip() or pregunta) if m else pregunta


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def es_meta(opcion: str) -> bool:
    return bool(_META.match(_sin_tildes(str(opcion)).strip()))


def _opciones(item: dict) -> list[str]:
    ops = item.get("opciones") or {}
    return [str(o) for o in (ops.values() if isinstance(ops, dict) else ops)]


def consulta_de(item: dict, tipo: str = "pregunta+opciones", sin_meta: bool = False) -> str:
    texto = item["pregunta"]
    if config.SIN_PREAMBULO == "on":
        texto = sin_preambulo(texto)
    if tipo == "pregunta+opciones" and item.get("opciones"):
        ops = _opciones(item)
        if sin_meta:
            ops = [o for o in ops if not es_meta(o)]
        texto += "\n" + "\n".join(ops)
    return texto


def consultas_opciones(item: dict) -> list[str]:
    """Una consulta por opcion sustantiva de una cerrada: pregunta + opcion (sin las meta)."""
    if item.get("formato") != "multiple_choice" or not item.get("opciones"):
        return []
    vistas: list[str] = []
    for o in _opciones(item):
        o = o.strip()
        if o and not es_meta(o) and o not in vistas:
            vistas.append(o)
    return [f"{item['pregunta'].strip()}\n{o}" for o in vistas]
