"""Orden de los pasajes que ve el decoder cuando la pregunta nombra una sentencia (SYNTAX_SECCION_SENTENCIA).

"¿Cuál es el problema jurídico de la C-039 de 2025?" recupera la sentencia, pero el
top-5 que ve el decoder puede traer la decisión o el índice en vez del problema
jurídico (#946, #190 de sample_50). Si la pregunta nombra una sentencia y pide una
sección, los fragmentos de esa sentencia que la contienen suben al frente **dentro del
top-10**: el conjunto de pasajes no cambia, así que citación y abstención tampoco.

Las secciones vienen de segmentar.py (sintesis | antecedentes | consideraciones |
resuelve | salvamento | aclaracion).
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

# (pista en la pregunta, secciones que la contienen, frase literal que la delata en el fragmento)
PISTAS = [
    (re.compile(r"problema juridico"), ("sintesis", "consideraciones"), "problema juridico"),
    (re.compile(r"antecedentes|hechos|factic"), ("antecedentes",), "hechos"),
    (re.compile(r"decidio|resolvio|decision|resuelve|fallo"), ("resuelve", "sintesis"), None),
    (re.compile(r"fundamento|ratio|subregla|regla|definio|precedente|establecio|considero"),
     ("consideraciones", "sintesis"), None),
]

VOTOS = ("salvamento", "aclaracion")


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


def sentencias_nombradas(pregunta: str) -> set[tuple]:
    return {b for b in citations.bodies(citations.extract(pregunta)) if b and b[0] == "jurisprudencia"}


def reordenar(pregunta: str, top: list) -> tuple[list, dict | None]:
    """Devuelve (top reordenado, info para la traza | None si no cambia nada).

    Prioridad: fragmento de la sentencia nombrada con la frase de la pista (2) > de la
    seccion pedida (1) > resto (0) > salvamentos y aclaraciones de voto (-1), que
    contradicen o matizan la decision mayoritaria (#563, #1015, #946 de sample_50).
    """
    nombradas = sentencias_nombradas(pregunta)
    if not nombradas:
        return top, None
    q = _norm(pregunta)
    pista = next((p for p in PISTAS if p[0].search(q)), None)
    secciones, frase = (pista[1], pista[2]) if pista else ((), None)

    def prioridad(p) -> int:
        if p.meta.get("seccion") in VOTOS:
            return -1
        if not pista or tuple(p.meta.get("canonico") or ()) not in nombradas:
            return 0
        if frase and frase in _norm(p.texto):
            return 2
        return 1 if p.meta.get("seccion") in secciones else 0

    prios = [prioridad(p) for p in top]
    orden = sorted(range(len(top)), key=lambda i: (-prios[i], i))
    if orden == list(range(len(top))):
        return top, None
    nuevo = [top[i] for i in orden]
    return nuevo, {"secciones": list(secciones), "antes": [p.chunk_id for p in top[:5]],
                   "despues": [p.chunk_id for p in nuevo[:5]]}
