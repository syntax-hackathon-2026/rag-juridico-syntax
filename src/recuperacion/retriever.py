"""Recuperacion sobre data_corpus/indice/: BM25, denso (bge-m3 + FAISS) o hibrido (RRF).

    from recuperacion.retriever import retrieve
    pasajes = retrieve("terminos para contestar la demanda en proceso verbal", k=10, modo="hibrido")

`RetrievedChunk` trae exactamente lo que va a pasajes_recuperados (doc_id, texto,
inicio, fin, score) mas la metadata del fragmento. Rankings deterministas: empates
por chunk_id. La consulta se codifica siempre en fp32 (ver construir_indice.py).

CLI para probar a mano:
    python src/recuperacion/retriever.py "despido sin justa causa indemnizacion" --modo bm25
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from recuperacion import lexico  # noqa: E402
from recuperacion.referencias import IndiceReferencias, cuerpos_de, referencias_de  # noqa: E402

MODOS = ("bm25", "denso", "hibrido")
RRF_K = 60
N_CANDIDATOS = 40


@dataclass
class RetrievedChunk:
    chunk_id: str
    doc_id: str
    texto: str
    inicio: int
    fin: int
    score: float
    rank: int
    meta: dict = field(default_factory=dict)

    def pasaje(self) -> dict:
        """Registro para pasajes_recuperados del schema de entrega."""
        return {"doc_id": self.doc_id, "texto": self.texto, "inicio": self.inicio,
                "fin": self.fin, "score": round(self.score, 6)}


class Retriever:
    def __init__(self, cargar_denso: bool = True):
        with config.CHUNKS_PATH.open(encoding="utf-8") as f:
            self.chunks = [json.loads(l) for l in f if l.strip()]
        for c in self.chunks:  # solo sirve para construir el indice; ahorra memoria junto al decoder
            c.pop("retrieval_text", None)
        self.indice_referencias = IndiceReferencias(self.chunks)
        self.excluidos = self._cargar_filtro()
        import bm25s

        self.bm25 = bm25s.BM25.load(str(config.BM25_DIR))
        self.faiss = None
        self._encoder = None
        self._ultima: tuple[str, np.ndarray] | None = None
        if cargar_denso and config.FAISS_PATH.is_file():
            import faiss

            config.verificar_indice()
            self.faiss = faiss.read_index(str(config.FAISS_PATH))

    # --- filtro "solo por cita" (docs/INDEXACION.md 14) ----------------------------

    def _cargar_filtro(self) -> np.ndarray | None:
        """Mascara de chunks cuyo documento solo se recupera si la consulta lo nombra."""
        if config.FILTRO_CITA == "off":
            return None
        registro = json.loads(config.SOLO_POR_CITA_PATH.read_text(encoding="utf-8"))
        grupos = ("sentencias",) if config.FILTRO_CITA == "sentencias" else ("sentencias", "normas")
        docs = {d for g in grupos for d in registro[g]}
        mascara = np.array([c["doc_id"] in docs for c in self.chunks], dtype=bool)
        return mascara if mascara.any() else None

    def _filtrar(self, buscar, consulta: str, n: int) -> list[tuple[int, float]]:
        """Top-n de una rama sin los chunks excluidos, salvo los de un cuerpo nombrado en la consulta.

        Pide candidatos de mas (x4 cada vez) hasta juntar n o agotar la rama; el orden
        de la rama no cambia, asi que el resultado es determinista.
        """
        if self.excluidos is None:
            return buscar(consulta, n)
        nombrados = cuerpos_de(consulta)
        pedir = n
        while True:
            pares = buscar(consulta, pedir)
            ok = [p for p in pares if not self.excluidos[p[0]]
                  or tuple(self.chunks[p[0]]["canonico"]) in nombrados]
            if len(ok) >= n or len(pares) < pedir or pedir >= len(self.chunks):
                return ok[:n]
            pedir = min(pedir * 4, len(self.chunks))

    # --- ramas --------------------------------------------------------------------

    def buscar_bm25(self, consulta: str, n: int) -> list[tuple[int, float]]:
        tokens = lexico.tokenizar(consulta)
        if not tokens:
            return []
        n = min(n, len(self.chunks))
        idx, scores = self.bm25.retrieve([tokens], k=n, show_progress=False, n_threads=1)
        pares = [(int(i), float(s)) for i, s in zip(idx[0], scores[0]) if s > 0]
        return sorted(pares, key=lambda p: (-p[1], self.chunks[p[0]]["chunk_id"]))

    def _codificar(self, consulta: str) -> np.ndarray:
        if self._ultima is not None and self._ultima[0] == consulta:  # _filtrar repite la busqueda densa
            return self._ultima[1]
        if self._encoder is None:
            from indexacion.construir_indice import cargar_encoder

            self._encoder = cargar_encoder(config.resolver_device())
        v = self._encoder.encode([consulta], normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False).astype(np.float32)
        self._ultima = (consulta, v)
        return v

    def buscar_denso(self, consulta: str, n: int) -> list[tuple[int, float]]:
        if self.faiss is None:
            raise RuntimeError("no hay index.faiss: construir el indice sin --solo-bm25")
        scores, idx = self.faiss.search(self._codificar(consulta), min(n, len(self.chunks)))
        pares = [(int(i), float(s)) for i, s in zip(idx[0], scores[0]) if i >= 0]
        return sorted(pares, key=lambda p: (-p[1], self.chunks[p[0]]["chunk_id"]))

    # --- API ----------------------------------------------------------------------

    def retrieve(self, consulta: str, k: int = 10, modo: str = "hibrido",
                 n_candidatos: int = N_CANDIDATOS,
                 consulta_lookup: str | None = None) -> list[RetrievedChunk]:
        if modo not in MODOS:
            raise ValueError(f"modo {modo!r}; opciones: {MODOS}")
        ranks_rama: dict[str, dict[int, int]] = {}
        if modo == "bm25":
            ranking = self._filtrar(self.buscar_bm25, consulta, k)
        elif modo == "denso":
            ranking = self._filtrar(self.buscar_denso, consulta, k)
        else:
            fusion: dict[int, float] = {}
            for nombre, rama in (("bm25", self._filtrar(self.buscar_bm25, consulta, n_candidatos)),
                                 ("denso", self._filtrar(self.buscar_denso, consulta, n_candidatos))):
                ranks_rama[nombre] = {i: r for r, (i, _) in enumerate(rama, 1)}
                for r, (i, _) in enumerate(rama, 1):
                    fusion[i] = fusion.get(i, 0.0) + 1.0 / (RRF_K + r)
            # Lookup es una rama adicional, nunca un filtro de las ramas originales.
            indices_lookup = []
            if config.LOOKUP_MODO == "on":
                texto_lookup = consulta if consulta_lookup is None else consulta_lookup
                if config.LOOKUP_FUENTE == "pregunta" and consulta_lookup is None:
                    raise ValueError("LOOKUP_FUENTE=pregunta requiere consulta_lookup explicita")
                indices_lookup = self.indice_referencias.buscar(referencias_de(texto_lookup))
                if indices_lookup:
                    ranks_rama["lookup"] = {i: r for r, i in enumerate(indices_lookup, 1)}
                for r, i in enumerate(indices_lookup, 1):
                    if config.LOOKUP_VARIANTE == "a":
                        fusion[i] = fusion.get(i, 0.0) + 1.0 / (RRF_K + r)
                    elif config.LOOKUP_VARIANTE == "b":
                        bonus = config.LOOKUP_BONUS if self.indice_referencias.preferible(i) else 0.0
                        fusion[i] = fusion.get(i, 0.0) + bonus
                    else:
                        fusion.setdefault(i, 0.0)
            ranking = sorted(fusion.items(), key=lambda p: (-p[1], self.chunks[p[0]]["chunk_id"]))
            if indices_lookup and config.LOOKUP_VARIANTE == "c":
                insertar = indices_lookup[:min(config.LOOKUP_M, k)]
                ranking = [(i, fusion[i]) for i in insertar] + [(i, s) for i, s in ranking if i not in insertar]
        salida = []
        for r, (i, s) in enumerate(ranking[:k], 1):
            c = self.chunks[i]
            meta = {kk: c[kk] for kk in ("tipo", "articulo", "parte", "n_partes", "seccion", "vigencia",
                                        "canonico", "cabecera", "url")}
            for nombre, ranks in ranks_rama.items():  # senal de acuerdo BM25/denso (None = fuera de los candidatos)
                meta[f"rank_{nombre}"] = ranks.get(i)
            salida.append(RetrievedChunk(chunk_id=c["chunk_id"], doc_id=c["doc_id"], texto=c["texto"],
                                         inicio=c["inicio"], fin=c["fin"], score=s, rank=r, meta=meta))
        return salida


_RETRIEVER: Retriever | None = None


def cargar(cargar_denso: bool = True) -> Retriever:
    """Retriever unico por proceso (cargar el indice cuesta segundos)."""
    global _RETRIEVER
    if _RETRIEVER is None or (cargar_denso and _RETRIEVER.faiss is None and config.FAISS_PATH.is_file()):
        _RETRIEVER = Retriever(cargar_denso=cargar_denso)  # un retriever creado solo con BM25 no sirve para denso
    return _RETRIEVER


def retrieve(consulta: str, k: int = 10, modo: str = "hibrido") -> list[RetrievedChunk]:
    return cargar(cargar_denso=modo != "bm25").retrieve(consulta, k=k, modo=modo)


if __name__ == "__main__":
    import argparse

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("consulta")
    ap.add_argument("--modo", choices=MODOS, default="hibrido")
    ap.add_argument("-k", type=int, default=10)
    args = ap.parse_args()
    for p in retrieve(args.consulta, k=args.k, modo=args.modo):
        print(f"{p.rank:>2}. {p.score:.4f}  {p.chunk_id}")
        print(f"    {p.texto[:160]!r}")
