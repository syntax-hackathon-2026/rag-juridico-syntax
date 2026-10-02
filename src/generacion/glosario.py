"""Glosario de normas para el prompt (SYNTAX_GLOSARIO=on): puente nombre <-> numero.

Problema (docs/GENERACION.md, seccion 9): el banco nombra las normas por numero
("Ley 1564 de 2012", "Ley 906 de 2004") y las cabeceras de los pasajes por nombre
("Articulo 626 del Codigo General del Proceso."), o al reves. El decoder no conecta
la opcion con la evidencia y la descarta por "no mencionada en los pasajes" (#58).

Fuente unica: el `titulo` de corpus_manifest.json, que ya trae la equivalencia
("Codigo General del Proceso (Ley 1564 de 2012)", "Ley 270 de 1996 (Estatutaria de la
Administracion de Justicia)"). Nada de alias escritos a mano.

Solo cambia el texto que ve el decoder: pasajes_recuperados.texto sigue literal y las
citas se siguen validando contra los 10 pasajes (los titulos nombran la misma norma
que la cabecera, asi que no habilitan citas nuevas).
"""
from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from indexacion import cabeceras  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

# "ley 1564 de 2012", "decreto ley 663 de 1993", "decreto 1072/2015" (texto ya normalizado)
_NUM_RE = re.compile(r"\b(ley|decreto(?:\s*-?\s*ley)?)\s*(?:n[°ºo]?\.?\s*)?(\d{1,5})\s*(?:de|del|/|-)\s*(\d{4})\b")
_DOC_NORMA = re.compile(r"^(ley|decreto)_(\d+)_(\d{4})$")


def _seguro(titulo: str, canon: tuple) -> bool:
    """El titulo aporta algo (numero, nombre o tema entre parentesis o tras coma) y, si el
    decoder lo copia, no extrae otra norma: "Codigo Civil (Ley 57 de 1887)" daria la cita
    espuria ("ley","57","1887") sin respaldo (ver indexacion/cabeceras.py)."""
    if "(" not in titulo and "," not in titulo:
        return False
    cuerpos = {tuple(b) for b in citations.bodies(citations.extract(titulo))}
    return cuerpos <= {canon} | {tuple(v) for v in cabeceras.variantes(canon)}


def _tipo(raw: str) -> str:
    return "ley" if raw == "ley" else "decreto"


@lru_cache(maxsize=1)
def _indices() -> tuple[dict, dict]:
    """(canonico -> titulo, (tipo, numero) -> [(anio, titulo)]) de las normas del manifest."""
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    por_canon: dict[tuple, str] = {}
    por_numero: dict[tuple, list] = {}
    for d in manifest["documentos"]:
        try:
            canon = tuple(cabeceras.canonico(d["doc_id"]))
        except ValueError:
            continue
        if canon[0] in ("jurisprudencia", "documento"):
            continue
        titulo = d["titulo"].strip()
        if not _seguro(titulo, canon):
            continue
        por_canon.setdefault(canon, titulo)
        if m := _DOC_NORMA.match(d["doc_id"]):
            clave = (m[1], m[2].lstrip("0"), m[3])
        elif m := _NUM_RE.search(citations.norm(titulo)):  # codigos: el numero esta en el titulo
            clave = (_tipo(m[1]), m[2].lstrip("0"), m[3])
        else:
            continue
        entradas = por_numero.setdefault(clave[:2], [])
        if (clave[2], titulo) not in entradas:
            entradas.append((clave[2], titulo))
    for entradas in por_numero.values():
        entradas.sort()
    return por_canon, por_numero


def ficha_pasaje(meta: dict) -> str | None:
    """Titulo de la norma del pasaje si agrega algo a su cabecera (numero, nombre o tema)."""
    titulo = _indices()[0].get(tuple(meta.get("canonico") or ()))
    if not titulo:
        return None
    t = citations.norm(titulo).rstrip(".")
    return None if t in citations.norm(meta.get("cabecera") or "") else titulo


def notas(texto: str) -> list[str]:
    """Equivalencias de las normas que nombra un texto (pregunta u opcion).

    - numero y anio en el corpus con titulo mas informativo -> el titulo;
    - numero en el corpus con otro anio -> aviso de posible errata;
    - codigo por nombre ("Codigo General del Proceso") -> su titulo con el numero.
    """
    _, por_numero = _indices()
    t = citations.norm(texto)
    salida: list[str] = []
    for m in _NUM_RE.finditer(t):
        tipo, numero, anio = _tipo(m[1]), m[2].lstrip("0"), m[3]
        entradas = por_numero.get((tipo, numero))
        if not entradas:
            continue
        exactas = [ti for a, ti in entradas if a == anio]
        citada = f"{tipo.capitalize()} {m[2]} de {anio}"
        if exactas:
            ti = exactas[0]
            if citations.norm(ti).rstrip(".") != f"{tipo} {numero} de {anio}":
                salida.append(f"{citada} = {ti}")
        else:
            otras = "; ".join(ti for _, ti in entradas)
            salida.append(f"no hay {citada} en el corpus; probablemente se refiere a {otras} (mismo número, otro año)")
    por_canon = _indices()[0]
    for cuerpo in sorted(citations.bodies(citations.extract(texto)), key=str):
        if cuerpo[1] is None and cuerpo[0] in citations.CODES:  # codigo nombrado
            ti = por_canon.get(tuple(cuerpo))
            if ti and _NUM_RE.search(citations.norm(ti)) and not any(ti in s for s in salida):
                salida.append(ti)
    return list(dict.fromkeys(salida))
