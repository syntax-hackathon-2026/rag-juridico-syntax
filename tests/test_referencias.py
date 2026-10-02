"""Parser e integracion con fixture pequena; no descarga modelos ni usa FAISS."""
import json
import sys
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import config
from recuperacion.referencias import IndiceReferencias, normalizar_articulo, referencias_de
from recuperacion.retriever import Retriever
from evaluacion.analisis_referencias import comparar, fase0
from evaluacion.retrieval_eval import metricas_subconjuntos


@pytest.mark.parametrize("texto, esperado", [
    ("art\u00edculo 29 de la Constituci\u00f3n", [("constitucion", None, None, "29")]),
    ("art. 42 del CGP", [("codigo_general_proceso", None, None, "42")]),
    ("Ley 1564 de 2012, art\u00edculos 13, 15 y 42", [
        ("codigo_general_proceso", None, None, "13"),
        ("codigo_general_proceso", None, None, "15"),
        ("codigo_general_proceso", None, None, "42")]),
    ("Sentencia C-355 de 2006", [("jurisprudencia", "C-355", "2006", None)]),
    ("consulta generica", []),
])
def test_extract_oficial(texto, esperado):
    assert referencias_de(texto) == esperado


@pytest.fixture
def chunks():
    return [json.loads(l) for l in (ROOT / "tests/fixtures/referencias_chunks.jsonl").read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def ret(monkeypatch):
    # Init real construye el indice desde la fixture; solo las ramas ML se simulan.
    monkeypatch.setattr(config, "CHUNKS_PATH", ROOT / "tests/fixtures/referencias_chunks.jsonl")
    monkeypatch.setattr(config, "LOOKUP_MODO", "off")
    monkeypatch.setattr(config, "LOOKUP_FUENTE", "consulta")
    bm25 = SimpleNamespace(BM25=SimpleNamespace(load=lambda _: object()))
    monkeypatch.setitem(sys.modules, "bm25s", bm25)
    r = Retriever(cargar_denso=False)
    monkeypatch.setattr(r, "buscar_bm25", lambda consulta, n: [(3, 3.0), (4, 2.0), (5, 1.0)])
    monkeypatch.setattr(r, "buscar_denso", lambda consulta, n: [(4, 3.0), (3, 2.0), (5, 1.0)])
    return r


@pytest.mark.parametrize("entrada, esperado", [("1o", "1"), ("1\u00b0", "1"), ("38A", "38a"), ("12-1", "12-1"), ("5 A", "5a"), (None, None)])
def test_normalizacion(entrada, esperado):
    assert normalizar_articulo(entrada) == esperado


@pytest.mark.parametrize("articulo, indice", [("1", 3), ("38a", 4), ("12-1", 5)])
def test_indice_normalizado(chunks, articulo, indice):
    assert IndiceReferencias(chunks).buscar([("codigo_civil", None, None, articulo)]) == [indice]


def test_partes_y_vigencia(chunks):
    ix = IndiceReferencias(chunks)
    assert ix.buscar(referencias_de("art. 42 del CGP")) == [1, 0, 2]
    assert not ix.preferible(2)
    assert ix.buscar([("codigo_general_proceso", None, None, "99999")]) == []
    assert ix.buscar(referencias_de("CGP")) == []


def test_modificatoria_no_usa_citas_internas(chunks):
    ix = IndiceReferencias(chunks)
    assert ix.buscar(referencias_de("Articulo 10 de la Ley 1819 de 2016")) == [6]
    assert ix.buscar(referencias_de("Articulo 247 del Estatuto Tributario")) == []


def test_cabeceras_fixture_canonicas(chunks):
    for c in chunks:
        assert {r[:3] for r in referencias_de(c["cabecera"])} == {tuple(c["canonico"])}


def test_canonico_chunks_reales_si_disponibles():
    if not config.CHUNKS_PATH.is_file():
        pytest.skip("Sin chunks.jsonl real; coherencia cubierta solo con fixture")
    with config.CHUNKS_PATH.open(encoding="utf-8") as f:
        for i, linea in enumerate(f):
            if i >= 100:
                break
            c = json.loads(linea)
            assert {r[:3] for r in referencias_de(c["cabecera"])} == {tuple(c["canonico"])}


def test_off_golden_y_sin_ref_identico(ret, monkeypatch):
    base = ret.retrieve("sin referencia", k=10)
    assert [p.chunk_id for p in base] == ["codigo_civil#art_1#p1", "codigo_civil#art_38a#p1", "codigo_civil#art_12-1#p1"]
    assert base[0].score == 1 / 61 + 1 / 62
    assert [p.rank for p in base] == [1, 2, 3]
    snapshot = [asdict(p) for p in base]
    for variante in ("a", "b", "c"):
        monkeypatch.setattr(config, "LOOKUP_MODO", "on")
        monkeypatch.setattr(config, "LOOKUP_VARIANTE", variante)
        assert [asdict(p) for p in ret.retrieve("sin referencia", k=10)] == snapshot
        assert [asdict(p) for p in ret.retrieve("art. 99999 del CGP", k=10)] == snapshot
        assert [asdict(p) for p in ret.retrieve("CGP", k=10)] == snapshot
    monkeypatch.setattr(config, "LOOKUP_MODO", "off")
    assert [asdict(p) for p in ret.retrieve("art. 42 del CGP", k=10)] == snapshot


@pytest.mark.parametrize("variante", ["a", "b", "c"])
def test_candidatos_extra_sin_filtro_y_determinismo(ret, monkeypatch, variante):
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_VARIANTE", variante)
    base = {c["chunk_id"]: c for c in ret.chunks}
    p = ret.retrieve("art. 42 del CGP", k=10)
    assert len(p) == 6
    assert len({c.chunk_id for c in p}) == len(p)
    assert {c.doc_id for c in p} == {"codigo_civil", "codigo_general_proceso"}
    for c in p:
        assert c.texto == base[c.chunk_id]["texto"]
        assert (c.inicio, c.fin) == (base[c.chunk_id]["inicio"], base[c.chunk_id]["fin"])
    assert [asdict(c) for c in p] == [asdict(c) for c in ret.retrieve("art. 42 del CGP", k=10)]
    assert [c.meta["rank_lookup"] for c in p if c.doc_id == "codigo_general_proceso"]
    if variante == "a":
        assert next(c for c in p if c.chunk_id.endswith("#p1") and c.doc_id == "codigo_general_proceso").score == 1 / 61
    if variante == "c":
        assert [c.chunk_id for c in p[:2]] == ["codigo_general_proceso#art_42#p1", "codigo_general_proceso#art_42#p2"]
        assert len(ret.retrieve("art. 42 del CGP", k=1)) == 1


def test_fuente_pregunta_excluye_opciones(ret, monkeypatch):
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_FUENTE", "pregunta")
    with pytest.raises(ValueError, match="consulta_lookup"):
        ret.retrieve("consulta\nart. 42 del CGP")
    p = ret.retrieve("consulta\nart. 42 del CGP", consulta_lookup="consulta")
    assert len(p) == 3
    assert all("rank_lookup" not in c.meta for c in p)


def fila(i, doc, art, exp=True):
    return {"id": i, "referencia": [["constitucion", None, None]], "referencia_articulos": [["constitucion", None, None, "29"]],
            "rank_doc": doc, "rank_art": art, "referencias_explicitas": [["constitucion", None, None, "29"]] if exp else [], "respaldo": float(bool(doc and doc <= 10))}


def test_ab_keep_y_perdidas():
    a = [fila(1, 2, None), fila(2, 2, None), fila(3, 1, 1, False)]
    b = [fila(1, 2, 5), fila(2, 2, 10), fila(3, 1, 1, False)]
    assert comparar(a, b)["keep_segun_conteos"]
    b[-1] = fila(3, 11, 11, False)
    assert not comparar(a, b)["keep_segun_conteos"]
    assert comparar(a, b)["perdidas_art"] == [3]
    with pytest.raises(ValueError):
        comparar(a, b[:-1])


def test_fase0_separa_opciones_y_sin_gt_evaluable():
    items = [{"id": 1, "pregunta": "consulta", "opciones": {"A": "art. 42 del CGP"}},
             {"id": 2, "pregunta": "art. 42 del CGP"}]
    m = fase0(items, [fila(1, 2, None)])
    assert m["pregunta"]["n_con_cuerpo"] == 1
    assert m["pregunta+opciones"]["n_con_cuerpo"] == 2
    assert m["pregunta+opciones"]["ids_fallos_art_con_referencia"] == [1]


def test_subconjuntos_denominadores():
    m = metricas_subconjuntos([fila(1, 1, 1), fila(2, None, None, False)])
    assert m["con_referencia"]["art_hit@10"] == 1
    assert m["sin_referencia"]["doc_hit@10"] == 0
    assert metricas_subconjuntos([])["con_referencia"]["mrr"] is None


def test_responder_no_filtra_ground_truth(monkeypatch):
    from generacion.responder import responder
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_FUENTE", "pregunta")
    monkeypatch.setattr(config, "ABSTENCION_MODO", "off")
    llamadas = []
    class Ret:
        def retrieve(self, query, **kwargs):
            llamadas.append((query, kwargs))
            return []
    class Decoder:
        def generar(self, *args, **kwargs):
            pytest.fail("Sin evidencia no se llama al decoder")
    item = {"id": 99, "formato": "multiple_choice", "pregunta": "art. 42 del CGP",
            "opciones": {"A": "Constitucion"}, "legal_basis": "SECRETO", "respuesta_correcta": "D"}
    _, traza = responder(item, Ret(), Decoder())
    assert traza["lookup"]["config"]["modo"] == "on"
    assert traza["lookup"]["matches_top"] == []
    assert llamadas[0][1]["consulta_lookup"] == item["pregunta"]
    assert "Constitucion" in llamadas[0][0]
    assert "SECRETO" not in llamadas[0][0]
    assert set(llamadas[0][1]) == {"k", "modo", "consulta_lookup"}


def test_evaluacion_fuente_y_guardia_runtime(ret, monkeypatch):
    from evaluacion import retrieval_eval as ev
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_FUENTE", "pregunta")
    monkeypatch.setattr(ev, "cargar", lambda **kwargs: ret)
    item = {"id": 1, "formato": "multiple_choice", "pregunta": "art. 42 del CGP",
            "opciones": {"A": "Articulo 29 de la Constitucion"},
            "legal_basis": "Articulo 7 de la Ley 80 de 1993"}
    met, filas = ev.evaluar("hibrido", [item], "pregunta+opciones", techo=True)
    assert filas[0]["referencias_explicitas"] == [["codigo_general_proceso", None, None, "42"]]
    assert any(cid.startswith("codigo_general_proceso#") for cid, _ in filas[0]["top"])
    assert not any(cid.startswith("constitucion_politica_1991#") for cid, _ in filas[0]["top"])
    assert met["subconjuntos_referencias"]["con_referencia"]["n"] == 1


def test_lookup_metadata(monkeypatch):
    monkeypatch.setattr(config, "LOOKUP_MODO", "off")
    monkeypatch.setattr(config, "LOOKUP_VARIANTE", "a")
    m = config.lookup_metadata()
    assert m["modo"] == "off" and m["variante"] == "a"
    assert m["parser"] == "scripts/citations.py"


def test_control_mrr_resto_impide_keep():
    a = [fila(1, 1, None), fila(2, 1, None), fila(3, 1, 1, False)]
    b = [fila(1, 1, 1), fila(2, 1, 1), fila(3, 2, 2, False)]
    assert not comparar(a, b)["keep_segun_conteos"]


@pytest.mark.parametrize("variante", ["a", "b"])
def test_boost_chunk_existente_sin_duplicados(ret, monkeypatch, variante):
    monkeypatch.setattr(config, "LOOKUP_MODO", "off")
    base = ret.retrieve("Articulo 1 del Codigo Civil", k=10)
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_VARIANTE", variante)
    actual = ret.retrieve("Articulo 1 del Codigo Civil", k=10)
    assert len(actual) == 3
    assert len({p.chunk_id for p in actual}) == 3
    antes = next(p for p in base if p.chunk_id == "codigo_civil#art_1#p1")
    despues = next(p for p in actual if p.chunk_id == antes.chunk_id)
    assert despues.score == antes.score + (1 / 61 if variante == "a" else config.LOOKUP_BONUS)


def test_bonus_no_prioriza_derogado(ret, monkeypatch):
    monkeypatch.setattr(config, "LOOKUP_MODO", "on")
    monkeypatch.setattr(config, "LOOKUP_VARIANTE", "b")
    p = ret.retrieve("art. 42 del CGP", k=10)
    nuevos = [c for c in p if c.doc_id == "codigo_general_proceso"]
    assert [c.meta["vigencia"] for c in nuevos] == ["modificado", "sin_nota", "derogado"]
    assert nuevos[-1].score == 0


def test_fase0_gt_ausente_no_se_cuenta_error():
    m = fase0([{"id": 442, "pregunta": "Articulo 7 de la Ley 80 de 1993"}], [])
    assert m["pregunta"]["ids_fallos_art_con_referencia"] == []
    assert m["pregunta"]["n_evaluables_con_articulo_explicito_y_gt"] == 0
    assert m["pregunta"]["ids_con_referencia_sin_baseline"] == [442]
