"""Pruebas sinteticas offline; no son resultados A/B."""
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evaluacion.techo_reranker import metricas_techo


class TechoTests(unittest.TestCase):
    def filas(self, ranks):
        return [{"id": i, "rank_art": r, "rank_doc": r, "referencia_articulos": ["art"]}
                for i, r in enumerate(ranks)]

    def test_fronteras(self):
        m = metricas_techo(self.filas([1, 5, 6, 10, 11, 20, 21, 40, None]))
        self.assertEqual(m["distribucion_rank_art"],
                         {"1-5": 2, "6-10": 2, "11-20": 2, "21-40": 2, "fuera": 1})
        self.assertEqual(m["techo_ganancia_preguntas"], 4)
        self.assertEqual(m["art_hit@20"], 6 / 9)
        self.assertEqual(m["art_hit@40"], 8 / 9)
        self.assertTrue(m["continuacion_fase1"])

    def test_criterio_or(self):
        self.assertFalse(metricas_techo(self.filas([11] + [None] * 18))["continuacion_fase1"])
        self.assertTrue(metricas_techo(self.filas([11, 40] + [None] * 17))["continuacion_fase1"])

    def test_sin_articulos(self):
        m = metricas_techo([{"id": 1, "rank_doc": 40, "referencia_articulos": []}])
        self.assertIsNone(m["art_hit@40"])
        self.assertFalse(m["continuacion_fase1"])
        self.assertEqual(m["doc_hit@40"], 1)
        self.assertEqual(m["mrr@40"], 1 / 40)

    def test_evaluacion_top40_conserva_top10(self):
        from evaluacion import retrieval_eval as ev
        legal = "Articulo 7 de la Ley 80 de 1993."
        ref = ev.citations.extract(legal)
        canonico = next(iter(ev.citations.bodies(ref)))
        articulo = next(iter(ev.citations.article_level(ref)))[3]
        chunks = [SimpleNamespace(chunk_id=str(i), score=0.01,
                  texto=legal if i == 11 else "Sin cita",
                  meta={"canonico": canonico if i == 11 else ("ley", "999", "2000"),
                        "articulo": articulo if i == 11 else "1"}) for i in range(1, 41)]
        class Ret:
            def retrieve(self, consulta, k, modo):
                return chunks[:k]
        items = [{"id": 1, "formato": "semi_open", "pregunta": "consulta", "legal_basis": legal}]
        with patch.object(ev, "cargar", return_value=Ret()):
            base, _ = ev.evaluar("hibrido", items, "pregunta")
            techo, filas = ev.evaluar("hibrido", items, "pregunta", techo=True)
        for nombre in ("doc_hit@10", "art_hit@10", "mrr", "respaldo@10"):
            self.assertEqual(base[nombre], techo[nombre])
        self.assertEqual(techo["art_hit@20"], 1)
        self.assertEqual(techo["techo_ganancia_preguntas"], 1)
        self.assertEqual(filas[0]["rank_art"], 11)
        self.assertEqual(len(filas[0]["top"]), 40)
        self.assertEqual(chunks[10].texto, legal)

    def test_vacio(self):
        with self.assertRaises(ValueError):
            metricas_techo([])


if __name__ == "__main__":
    unittest.main()
