"""Herramientas del sabado: cache del decoder, doc_id propuesto y areas de la ingesta dirigida."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evaluacion.analizar_test import doc_id_propuesto  # noqa: E402
from generacion.llm import CacheRespuestas, Respuesta  # noqa: E402
from ingesta.ampliar_desde_citas import normalizar_areas  # noqa: E402


def test_cache_clave_estable_y_persistente(tmp_path):
    ruta = tmp_path / "cache.jsonl"
    c = CacheRespuestas(ruta, "gguf|b1")
    a = c.clave({"messages": [{"role": "user", "content": "hola"}], "temperature": 0.0})
    b = c.clave({"temperature": 0.0, "messages": [{"role": "user", "content": "hola"}]})
    assert a == b  # el orden de las claves no cambia el hash
    assert a != CacheRespuestas(ruta, "gguf|b2").clave({"temperature": 0.0, "messages": [
        {"role": "user", "content": "hola"}]})  # otra build -> otra clave
    assert c.leer(a) is None
    c.guardar(a, Respuesta(texto='{"x": 1}', fin="stop", uso={"n": 3}, tiempos={}, ms=1234.5))
    r = CacheRespuestas(ruta, "gguf|b1").leer(a)  # se relee del disco
    assert r is not None and r.cache and r.texto == '{"x": 1}' and r.ms == 1234.5


def test_doc_id_propuesto():
    assert doc_id_propuesto(("ley", "0080", "1993")) == ("ley_80_1993", True)
    assert doc_id_propuesto(("decreto", "1377", "2013")) == ("decreto_1377_2013", True)
    assert doc_id_propuesto(("jurisprudencia", "SU-214", "2016")) == ("sentencia_su_214_2016", True)
    assert doc_id_propuesto(("jurisprudencia", "C-355", "2006")) == ("sentencia_c_355_2006", True)
    assert doc_id_propuesto(("jurisprudencia", "SL-1234", "2019")) == ("sentencia_sl_1234_2019", False)
    assert doc_id_propuesto(("resolucion", "368", "2014")) == ("resolucion_368_2014", False)
    assert doc_id_propuesto(("codigo_civil", None, None)) == (None, False)


def test_normalizar_areas():
    conocidas = {"Derecho civil", "Derecho constitucional", "Derecho comercial y sociedades"}
    assert normalizar_areas(["derecho civil"], conocidas) == (["Derecho civil"], [])
    assert normalizar_areas(["Derecho comercial"], conocidas) == (["Derecho comercial y sociedades"], [])
    assert normalizar_areas(["Derecho c"], conocidas) == ([], ["Derecho c"])  # ambigua
    assert normalizar_areas(["Derecho minero"], conocidas) == ([], ["Derecho minero"])
