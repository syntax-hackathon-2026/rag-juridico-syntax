"""Flags de texto libre (docs/GENERACION.md 10): apagados no cambian nada; encendidos hacen lo esperado."""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import config  # noqa: E402
from generacion import prompts, responder, seleccion  # noqa: E402
from recuperacion.retriever import RetrievedChunk  # noqa: E402

ITEM_SEMI = {"id": 1, "formato": "semi_open", "pregunta": "¿Qué requisitos tiene la lesión enorme?"}


def _hash(msgs) -> str:
    return hashlib.sha256(json.dumps(msgs, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def test_flags_apagados_por_defecto():
    assert config.PROMPT_TL == "p-v0" and config.SECCION_SENTENCIA == "off" and config.PENSAR_CASOS == 0
    assert "+tl1" not in prompts.PROMPT_VERSION
    for f in ("multiple_choice", "semi_open", "open_ended"):
        assert prompts.instrucciones(f) == prompts.INSTRUCCIONES[f]


def test_p_tl1_solo_cambia_texto_libre(monkeypatch):
    base = _hash(prompts.mensajes(ITEM_SEMI, ["Artículo 1947 del Código Civil.\ntexto"]))
    mc = {"id": 2, "formato": "multiple_choice", "pregunta": "¿?", "opciones": {"A": "a", "B": "b"}}
    base_mc = _hash(prompts.mensajes(mc, ["P"]))
    monkeypatch.setattr(config, "PROMPT_TL", "p-tl1")
    assert _hash(prompts.mensajes(ITEM_SEMI, ["Artículo 1947 del Código Civil.\ntexto"])) != base
    assert _hash(prompts.mensajes(mc, ["P"])) == base_mc  # la cache de las cerradas sigue valiendo
    assert "+tl1" in importlib.reload(prompts).PROMPT_VERSION
    monkeypatch.setattr(config, "PROMPT_TL", "p-v0")
    importlib.reload(prompts)


def _chunk(cid, canonico, seccion, texto="x"):
    return RetrievedChunk(chunk_id=cid, doc_id=cid.split("#")[0], texto=texto, inicio=0, fin=1, score=0.0,
                          rank=0, meta={"canonico": canonico, "seccion": seccion})


def test_reordena_solo_la_sentencia_nombrada():
    c39 = ["jurisprudencia", "C-39", "2025"]
    top = [_chunk("s#w9", c39, "resuelve"), _chunk("ley#a1", ["ley", "1", "2000", "1"], None),
           _chunk("s#w2", c39, "consideraciones", "2.1. Problema jurídico. ¿Las normas..."),
           _chunk("otra#w1", ["jurisprudencia", "T-1", "2020"], "consideraciones", "problema jurídico")]
    nuevo, info = seleccion.reordenar("¿Cuál es el problema jurídico de la sentencia C-039 de 2025?", top)
    assert [p.chunk_id for p in nuevo] == ["s#w2", "s#w9", "ley#a1", "otra#w1"] or \
        [p.chunk_id for p in nuevo][0] == "s#w2"
    assert info and sorted(p.chunk_id for p in nuevo) == sorted(p.chunk_id for p in top)  # mismo conjunto
    assert seleccion.reordenar("¿Qué es la lesión enorme?", top) == (top, None)  # sin sentencia nombrada
    assert seleccion.reordenar("¿Qué dice la sentencia C-039 de 2025?", top) == (top, None)  # sin pista ni votos
    voto = [_chunk("s#w8", c39, "salvamento", "problema jurídico"), top[0]]
    nuevo, _ = seleccion.reordenar("¿Qué dice la sentencia C-039 de 2025?", voto)
    assert [p.chunk_id for p in nuevo] == ["s#w9", "s#w8"]  # el salvamento baja aun sin pista


def test_pensar_caso(monkeypatch):
    largo = {"formato": "semi_open", "pregunta": "palabra " * 50}
    assert not responder.pensar_caso(largo)
    monkeypatch.setattr(config, "PENSAR_CASOS", 40)
    assert responder.pensar_caso(largo)
    assert not responder.pensar_caso({"formato": "semi_open", "pregunta": "corta"})
    assert not responder.pensar_caso({"formato": "multiple_choice", "pregunta": "palabra " * 50})


def test_retriever_fijo_repite_la_traza(tmp_path):
    from recuperacion.fijo import RetrieverFijo

    chunks = tmp_path / "chunks.jsonl"
    filas = [{"chunk_id": f"d#a{i}", "doc_id": "d", "texto": f"t{i}", "inicio": i, "fin": i + 1,
              "seccion": None, "canonico": ["ley", "1", "2000", str(i)], "cabecera": f"c{i}"} for i in range(3)]
    chunks.write_text("".join(json.dumps(f) + "\n" for f in filas), encoding="utf-8")
    trazas = tmp_path / "t.jsonl"
    trazas.write_text(json.dumps({"id": 7, "top": [["d#a2", 0.5], ["d#a0", 0.4]]}) + "\n", encoding="utf-8")
    r = RetrieverFijo(trazas, chunks)
    r.fijar(7)
    top = r.retrieve("cualquier consulta", k=10, area="x")
    assert [(p.chunk_id, p.score, p.texto, p.meta["cabecera"]) for p in top] == [("d#a2", 0.5, "t2", "c2"),
                                                                                  ("d#a0", 0.4, "t0", "c0")]
