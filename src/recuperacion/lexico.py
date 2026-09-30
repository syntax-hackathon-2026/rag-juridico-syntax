"""Tokenizador de BM25, compartido por la construccion del indice y las consultas.

Minusculas y sin tildes (citations.norm, el mismo criterio del evaluador), conserva
los numeros de articulo con puntos o guiones como un solo token ("2.2.1.1.1",
"240-1", "1564") y quita stopwords del espanol. Sin stemming: se prueba despues con
datos (CLAUDE.md, "mirar si el stemming dana"). Cambiar algo aqui obliga a
reconstruir el indice: VERSION queda en indice_info.json.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from citations import norm  # noqa: E402

VERSION = "lex-v1"

_TOKEN = re.compile(r"\d+(?:[.\-]\d+)*[a-z]?|[a-z]+")

# Stopwords del espanol ya normalizadas (sin tildes). No incluye "ley", "articulo",
# "no" ni "sin": en derecho cambian el sentido de la consulta.
STOPWORDS = frozenset("""
a al algo algun alguna algunas alguno algunos ante antes aquel aquella aquellas aquellos aqui
asi aun aunque cada cual cuales cualquier cuando cuanto de del desde donde dos e el ella ellas
ello ellos en entre era eran es esa esas ese eso esos esta estaba estaban estan estar este esto
estos fue fueron ha habia habian han hasta hay la las le les lo los mas me mi mientras muy nos
o otra otras otro otros para pero poco por porque pues que quien quienes se sea sean segun ser
si sido sobre su sus tal tambien tan tanto te tiene tienen toda todas todo todos tu u un una
unas uno unos y ya
""".split())


def tokenizar(texto: str) -> list[str]:
    return [t for t in _TOKEN.findall(norm(texto)) if t not in STOPWORDS]
