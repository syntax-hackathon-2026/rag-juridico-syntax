"""Nombres de normas que citations.py no reconoce (SYNTAX_ALIAS=on), solo para recuperar.

Nunca toca las citas que se emiten ni pasajes_recuperados: sirve para que el retriever
sepa que la consulta nombra un cuerpo ("Estatuto Organico del Sistema Financiero",
"Estatuto de contratacion", "articulo 29 superior") y busque dentro de el.

Fuentes:
- automaticos: el `titulo` de corpus_manifest.json, el nombre entre parentesis o antes
  de "(" ("Estatuto Organico del Sistema Financiero (Decreto 663 de 1993)",
  "Ley 1474 de 2011 (Estatuto Anticorrupcion)"). Un nombre que apunta a mas de un
  documento se descarta;
- fijos (pocos, decididos por el equipo): la Constitucion como "norma superior",
  "articulo N superior" o "de la Carta"; EOSF; Estatuto (General) de Contratacion.
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
from recuperacion.lexico import STOPWORDS  # noqa: E402
from recuperacion.referencias import Ref, normalizar_articulo  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from citations import norm  # noqa: E402

CONSTITUCION = ("constitucion", None, None)
_INICIO = ("codigo ", "estatuto ", "regimen ", "reglamento ", "convenio ", "decreto unico ")
_PAREN = re.compile(r"\(([^()]*)\)")
_NUMERO = re.compile(r"\b(ley|decreto|acuerdo|resolucion|acto legislativo)\b.*\d")

# Constitucion por perifrasis: "articulo 29 superior", "articulos 13 y 29 de la Carta"
_ART_CONST = re.compile(
    r"\barticulos?\s+((?:\d+[a-z]?\s*(?:,|y|e)?\s*)+)\s*(?:de\s+la\s+)?(?:superior|carta(?:\s+politica)?)\b")
_CONST = re.compile(r"\b(?:norma|texto|ordenamiento)\s+superior\b|\bcarta\s+(?:fundamental|magna)\b"
                    r"|\bley\s+fundamental\b")
_FIJOS = (  # (regex sobre texto normalizado, doc_id)
    (re.compile(r"\beosf\b"), "decreto_663_1993"),
    (re.compile(r"\bestatuto\s+(?:general\s+)?de\s+(?:la\s+)?contratacion(?:\s+(?:estatal|publica|"
                r"de\s+la\s+administracion\s+publica))?\b"), "ley_80_1993"),
)


def _contenido(nombre: str) -> int:
    return sum(t not in STOPWORDS for t in re.findall(r"[a-z]+", nombre))


def _candidatos(titulo: str) -> list[str]:
    t = norm(titulo)
    salida = [m.strip(" .,") for m in _PAREN.findall(t)]
    if "(" in t:
        salida.append(t.split("(")[0].strip(" .,"))
    buenos = []
    for n in salida:
        if _NUMERO.search(n) or not n:
            continue  # "ley 1564 de 2012": eso ya lo extrae citations.py
        if (n.startswith(_INICIO) and _contenido(n) >= 2) or _contenido(n) >= 4:
            buenos.append(n)
    return buenos


@lru_cache(maxsize=1)
def _tablas() -> tuple[list[tuple[re.Pattern, tuple]], dict[str, tuple]]:
    """([(patron del nombre, canonico)], doc_id -> canonico) desde el manifest."""
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    canon_doc: dict[str, tuple] = {}
    por_nombre: dict[str, set] = {}
    for d in manifest["documentos"]:
        try:
            canon = tuple(cabeceras.canonico(d["doc_id"]))
        except ValueError:
            continue
        canon_doc[d["doc_id"]] = canon
        if canon[0] in ("jurisprudencia", "documento"):
            continue
        for n in _candidatos(d["titulo"]):
            por_nombre.setdefault(n, set()).add(canon)
    patrones = [(re.compile(r"\b" + re.escape(n).replace(r"\ ", r"\s+") + r"\b"), next(iter(cs)))
                for n, cs in sorted(por_nombre.items()) if len(cs) == 1]
    for patron, doc_id in _FIJOS:
        if doc_id in canon_doc:
            patrones.append((patron, canon_doc[doc_id]))
    return patrones, canon_doc


def cuerpos_alias(consulta: str) -> set[tuple]:
    t = norm(consulta)
    cuerpos = {canon for patron, canon in _tablas()[0] if patron.search(t)}
    if _ART_CONST.search(t) or _CONST.search(t):
        cuerpos.add(CONSTITUCION)
    return cuerpos


def referencias_alias(consulta: str) -> list[Ref]:
    """Articulos de la Constitucion nombrados por perifrasis, para el lookup."""
    refs = set()
    for m in _ART_CONST.finditer(norm(consulta)):
        for a in re.findall(r"\d+[a-z]?", m[1]):
            refs.add((*CONSTITUCION, normalizar_articulo(a)))
    return sorted(refs, key=str)


def nombres() -> list[str]:
    """Para revisar a mano: patron -> canonico."""
    return [f"{p.pattern}  ->  {c}" for p, c in _tablas()[0]]


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    if len(sys.argv) > 1:
        texto = " ".join(sys.argv[1:])
        print(sorted(cuerpos_alias(texto), key=str), referencias_alias(texto))
    else:
        print("\n".join(nombres()))
