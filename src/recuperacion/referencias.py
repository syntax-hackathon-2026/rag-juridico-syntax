"""Referencias oficiales y lookup de metadata; sin regex legales alternativas."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
sys.path.insert(0, str(config.ROOT / "scripts"))
import citations

Ref = tuple[str, str | None, str | None, str | None]


def normalizar_articulo(a: str | None) -> str | None:
    """Misma normalizacion de articulos del evaluador, compartida por lookup."""
    if a is None:
        return None
    a = re.sub(r"[\u00b0\u00ba]", "", a.lower()).replace(" ", "")
    return re.sub(r"^(\d+)o$", r"\1", a)


def referencias_de(consulta: str) -> list[Ref]:
    """Extraccion oficial; lista unica y estable incluso con None en las tuplas."""
    refs = citations.extract(consulta or "")
    articulos = citations.article_level(refs)
    cuerpos_con_articulo = citations.bodies(articulos)
    salida = {(r[0], r[1], r[2], normalizar_articulo(r[3])) for r in articulos}
    salida.update((*c, None) for c in citations.bodies(refs) - cuerpos_con_articulo)
    return sorted(salida, key=str)


class IndiceReferencias:
    """canonico propio del chunk + articulo -> todas sus partes, una vez por carga.

    No inspecciona citas dentro del texto: una norma modificatoria conserva su
    identidad. Vigencia es solo una senal de la fuente, no una conclusion legal.
    """
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.por_articulo: dict[tuple, list[int]] = {}
        for i, c in enumerate(chunks):
            a = normalizar_articulo(c.get("articulo"))
            if a is not None:
                self.por_articulo.setdefault((*c["canonico"], a), []).append(i)
        for indices in self.por_articulo.values():
            indices.sort(key=self.prioridad)

    def prioridad(self, i: int) -> tuple:
        c = self.chunks[i]
        return (c.get("vigencia") in {"derogado", "inexequible"}, c["chunk_id"])

    def buscar(self, refs: list[Ref]) -> list[int]:
        encontrados = {i for ref in refs if ref[3] is not None
                       for i in self.por_articulo.get(tuple(ref), [])}
        return sorted(encontrados, key=self.prioridad)

    def preferible(self, i: int) -> bool:
        c = self.chunks[i]
        clave = (*c["canonico"], normalizar_articulo(c.get("articulo")))
        return not (self.prioridad(i)[0] and any(not self.prioridad(j)[0]
                    for j in self.por_articulo.get(clave, [])))
