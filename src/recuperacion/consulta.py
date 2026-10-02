"""Consulta de recuperacion a partir de un item: la misma en la medicion y en el runtime.

Solo usa `pregunta` y `opciones` (nunca legal_basis ni respuestas).
"""
from __future__ import annotations

import re
import unicodedata

TIPOS = ("pregunta", "pregunta+opciones")

# Opciones que no aportan terminos de busqueda: "Todas las anteriores", "Ninguna de las
# anteriores", "(a) y (b)", "A y C son correctas", "Ninguna es correcta".
_META = re.compile(
    r"^\s*(?:todas|todos|ninguna|ninguno|ambas)\s+(?:de\s+)?(?:las\s+|los\s+)?"
    r"(?:anteriores|opciones|respuestas|son|es)\b.*$"
    r"|^\s*(?:las|los)\s+(?:dos|tres)\s+anteriores\b.*$"
    r"|^\s*\(?[a-d]\)?\s*(?:,\s*\(?[a-d]\)?\s*)*(?:y|e|o)\s*\(?[a-d]\)?\s*(?:son\s+correctas?)?\s*\.?\s*$",
    re.IGNORECASE)


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def es_meta(opcion: str) -> bool:
    return bool(_META.match(_sin_tildes(str(opcion)).strip()))


def _opciones(item: dict) -> list[str]:
    ops = item.get("opciones") or {}
    return [str(o) for o in (ops.values() if isinstance(ops, dict) else ops)]


def consulta_de(item: dict, tipo: str = "pregunta+opciones", sin_meta: bool = False) -> str:
    texto = item["pregunta"]
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
