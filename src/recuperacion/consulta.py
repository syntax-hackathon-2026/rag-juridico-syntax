"""Consulta de recuperacion a partir de un item: la misma en la medicion y en el runtime.

Solo usa `pregunta` y `opciones` (nunca legal_basis ni respuestas).
"""
from __future__ import annotations

TIPOS = ("pregunta", "pregunta+opciones")


def consulta_de(item: dict, tipo: str = "pregunta+opciones") -> str:
    texto = item["pregunta"]
    if tipo == "pregunta+opciones" and item.get("opciones"):
        ops = item["opciones"]
        texto += "\n" + "\n".join(ops.values() if isinstance(ops, dict) else ops)
    return texto
