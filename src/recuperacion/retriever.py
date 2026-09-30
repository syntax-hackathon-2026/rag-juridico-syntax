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
        import bm25s

        self.bm25 = bm25s.BM25.load(str(config.BM25_DIR))
        self.faiss = None
        self._encoder = None
        if cargar_denso and config.FAISS_PATH.is_file():
            import faiss

            config.verificar_indice()
            self.faiss = faiss.read_index(str(config.FAISS_PATH))

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
        if self._encoder is None:
            from indexacion.construir_indice import cargar_encoder

            self._encoder = cargar_encoder(config.resolver_device())
        v = self._encoder.encode([consulta], normalize_embeddings=True, convert_to_numpy=True,
                                 show_progress_bar=False)
        return v.astype(np.float32)

    def buscar_denso(self, consulta: str, n: int) -> list[tuple[int, float]]:
        if self.faiss is None:
            raise RuntimeError("no hay index.faiss: construir el indice sin --solo-bm25")
        scores, idx = self.faiss.search(self._codificar(consulta), min(n, len(self.chunks)))
        pares = [(int(i), float(s)) for i, s in zip(idx[0], scores[0]) if i >= 0]
        return sorted(pares, key=lambda p: (-p[1], self.chunks[p[0]]["chunk_id"]))

    # --- API ----------------------------------------------------------------------

    def retrieve(self, consulta: str, k: int = 10, modo: str = "hibrido",
                 n_candidatos: int = N_CANDIDATOS) -> list[RetrievedChunk]:
        if modo not in MODOS:
            raise ValueError(f"modo {modo!r}; opciones: {MODOS}")
        if modo == "bm25":
            ranking = self.buscar_bm25(consulta, k)
        elif modo == "denso":
            ranking = self.buscar_denso(consulta, k)
        else:
            fusion: dict[int, float] = {}
            for rama in (self.buscar_bm25(consulta, n_candidatos), self.buscar_denso(consulta, n_candidatos)):
                for r, (i, _) in enumerate(rama, 1):
                    fusion[i] = fusion.get(i, 0.0) + 1.0 / (RRF_K + r)
            ranking = sorted(fusion.items(), key=lambda p: (-p[1], self.chunks[p[0]]["chunk_id"]))
        salida = []
        for r, (i, s) in enumerate(ranking[:k], 1):
            c = self.chunks[i]
            meta = {kk: c[kk] for kk in ("tipo", "articulo", "parte", "n_partes", "seccion", "vigencia",
                                        "canonico", "cabecera", "url")}
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
