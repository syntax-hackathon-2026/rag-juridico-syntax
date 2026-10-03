"""Retriever que repite el top-10 de una corrida anterior (main.py --replay-trazas).

Sirve para probar cambios de generacion (prompt, seleccion de pasajes, thinking)
sobre exactamente los mismos pasajes de otra maquina, sin cargar bge-m3 ni FAISS
junto al decoder (en el Mac de 16 GB eso provoca swap). Los fragmentos salen de
data_corpus/indice/chunks.jsonl con su texto y metadata reales, en el orden y con el
score de la traza. El indice local debe ser el mismo de la corrida (sha256_chunks).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from recuperacion.retriever import RetrievedChunk  # noqa: E402

CAMPOS_META = ("tipo", "articulo", "parte", "n_partes", "seccion", "vigencia", "canonico", "cabecera", "url")


class RetrieverFijo:
    def __init__(self, trazas: Path, chunks: Path | None = None):
        self.tops: dict[int, list[tuple[str, float]]] = {}
        for linea in trazas.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                t = json.loads(linea)
                self.tops[t["id"]] = [(cid, s) for cid, s in t["top"]]
        faltan = {cid for top in self.tops.values() for cid, _ in top}
        self.chunks: dict[str, dict] = {}
        with (chunks or config.CHUNKS_PATH).open(encoding="utf-8") as f:
            for linea in f:
                # filtro barato antes de parsear: el chunk_id va al principio de cada linea
                cid = linea[14:linea.find('"', 14)]
                if cid in faltan:
                    self.chunks[cid] = json.loads(linea)
        if faltan - set(self.chunks):
            raise SystemExit(f"{len(faltan - set(self.chunks))} chunk_id de la traza no estan en el indice local "
                             f"(otro indice?): {sorted(faltan - set(self.chunks))[:3]}")
        self.actual: int | None = None

    def fijar(self, item_id: int) -> None:
        if item_id not in self.tops:
            raise SystemExit(f"id {item_id} no esta en las trazas del replay")
        self.actual = item_id

    def retrieve(self, consulta: str, k: int = 10, **_kw) -> list[RetrievedChunk]:
        salida = []
        for r, (cid, s) in enumerate(self.tops[self.actual][:k], 1):
            c = self.chunks[cid]
            salida.append(RetrievedChunk(chunk_id=cid, doc_id=c["doc_id"], texto=c["texto"], inicio=c["inicio"],
                                         fin=c["fin"], score=s, rank=r, meta={kk: c.get(kk) for kk in CAMPOS_META}))
        return salida
