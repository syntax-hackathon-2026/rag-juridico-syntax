"""Validacion determinista de citas contra la evidencia (enunciado, paso 4).

Mismo criterio que el evaluador (scripts/evaluate.py, citas_respaldadas): una cita
esta respaldada si su cuerpo normativo aparece en `citations.extract` del texto de
alguno de los 10 primeros pasajes. Se compara a nivel de cuerpo (`citations.bodies`),
que es como puntua `citations.score`. Nada de LLM aqui.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

Cuerpo = tuple  # ("ley", "1563", "2012") | ("codigo_penal", None, None) | ("jurisprudencia", "C-355", "2006")

_ORACION = re.compile(r"(?<=[.;!?])\s+(?=[\"'«(¿¡]?[A-ZÁÉÍÓÚÑ])")


def cuerpos(texto: str) -> set[Cuerpo]:
    return citations.bodies(citations.extract(texto or ""))


def permitidas(textos_pasajes: list[str]) -> set[Cuerpo]:
    """Cuerpos que el evaluador da por respaldados con estos pasajes (usa los 10 primeros)."""
    salida: set[Cuerpo] = set()
    for t in textos_pasajes[:10]:
        salida |= cuerpos(t)
    return salida


def sin_respaldo(texto: str, perm: set[Cuerpo]) -> set[Cuerpo]:
    return cuerpos(texto) - perm


def oraciones(texto: str) -> list[str]:
    return [o for o in _ORACION.split((texto or "").strip()) if o.strip()]


def quitar_oraciones(texto: str, malas: set[Cuerpo]) -> str:
    """Elimina las oraciones que citan alguno de los cuerpos `malas`."""
    return " ".join(o for o in oraciones(texto) if not (cuerpos(o) & malas))


def nombre(c: Cuerpo) -> str:
    """Forma legible de un cuerpo canonico (para el mensaje de correccion al decoder)."""
    tipo, num, anio = c[:3]
    if tipo == "jurisprudencia":
        return f"Sentencia {num} de {anio}"
    if num:
        return f"{tipo.replace('_', ' ').capitalize()} {num} de {anio}"
    return tipo.replace("_", " ")


def citas_evidencia(meta_pasajes: list[dict]) -> list[str]:
    """Cabeceras citables de los pasajes, una por cuerpo normativo, en orden de ranking.

    La cabecera de cada fragmento ("Articulo 42 del Codigo General del Proceso.") se
    valido al segmentar: extrae exactamente su cuerpo canonico (docs/INDEXACION.md 4.1).
    """
    vistos: set[tuple] = set()
    salida = []
    for m in meta_pasajes:
        clave = tuple(m.get("canonico") or ())
        if not clave or clave in vistos or not m.get("cabecera"):
            continue
        vistos.add(clave)
        salida.append(m["cabecera"])
    return salida
