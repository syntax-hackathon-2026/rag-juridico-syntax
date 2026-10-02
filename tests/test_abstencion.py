from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import config  # noqa: E402
from generacion import abstencion  # noqa: E402
from generacion.responder import responder  # noqa: E402
import generacion.responder as responder_module  # noqa: E402


@pytest.fixture
def regla():
    return abstencion.ReglaAbstencion(
        semi_open_top1_rank_denso_mayor_que=18.5,
        open_ended_frac_en_ambas_ramas_menor_que=0.74,
    )


@pytest.mark.parametrize(
    ("formato", "senales", "expected"),
    [
        ("multiple_choice", {"top1_rank_denso": 100, "frac_en_ambas_ramas": 0}, (False, [])),
        ("semi_open", {"top1_rank_denso": 18.6}, (True, ["senal_umbral:top1_rank_denso"])),
        ("semi_open", {"top1_rank_denso": 18.5}, (False, [])),
        ("open_ended", {"frac_en_ambas_ramas": 0.73}, (True, ["senal_umbral:frac_en_ambas_ramas"])),
        ("open_ended", {"frac_en_ambas_ramas": 0.74}, (False, [])),
    ],
)
def test_decisiones_por_formato(regla, formato, senales, expected):
    assert abstencion.decidir_por_senales(senales, formato, regla) == expected


def test_decidir_por_senales_es_determinista(regla):
    senales = {"top1_rank_denso": 19}
    primera = abstencion.decidir_por_senales(senales, "semi_open", regla)
    segunda = abstencion.decidir_por_senales(senales, "semi_open", regla)
    assert primera == segunda == (True, ["senal_umbral:top1_rank_denso"])


@pytest.mark.parametrize("senales", [
    None,
    {},
    {"top1_rank_denso": None, "frac_en_ambas_ramas": None},
    {"top1_rank_denso": "19", "frac_en_ambas_ramas": float("nan")},
])
@pytest.mark.parametrize("formato", ["multiple_choice", "semi_open", "open_ended"])
def test_senales_faltantes_o_invalidas_no_abstienen(regla, formato, senales):
    assert abstencion.decidir_por_senales(senales, formato, regla) == (False, [])


def test_carga_regla_versionada():
    regla = abstencion.cargar_regla(config.ABSTENCION_CONFIG_PATH)
    assert regla == abstencion.ReglaAbstencion(18.5, 0.74)


def test_metadata_registra_modo_y_hash_de_configuracion(monkeypatch):
    monkeypatch.setattr(config, "ABSTENCION_MODO", "off")
    metadata = config.abstencion_metadata()
    expected_hash = hashlib.sha256(
        config.ABSTENCION_CONFIG_PATH.read_bytes()
    ).hexdigest()

    assert metadata == {"modo": "off", "config_sha256": expected_hash}


class RetrieverSinPasajes:
    def retrieve(self, query, *, k, modo, area=None):
        return []


class DecoderNoUsado:
    def generar(self, *args, **kwargs):
        pytest.fail("No se debe llamar al decoder si no hay pasajes")


class ChunkPrueba:
    score = 0.02
    chunk_id = "doc#chunk"
    texto = "Texto de evidencia sin citas."
    meta = {}

    def pasaje(self):
        return {"doc_id": "doc", "texto": self.texto, "score": self.score}


class RetrieverConPasaje:
    def retrieve(self, query, *, k, modo, area=None):
        return [ChunkPrueba()]


@pytest.mark.parametrize("modo", ["off", "reglas"])
def test_abstencion_tecnica_se_conserva_y_salida_es_valida(monkeypatch, modo, regla):
    monkeypatch.setattr(config, "ABSTENCION_MODO", modo)
    item = {
        "id": 7,
        "formato": "multiple_choice",
        "pregunta": "Pregunta de prueba sin evidencia.",
        "opciones": {"A": "Una", "B": "Dos"},
    }
    registro, traza = responder(
        item, RetrieverSinPasajes(), DecoderNoUsado(), regla_abstencion=regla
    )

    assert registro["abstencion"] is True
    assert registro["pasajes_recuperados"] == []
    assert traza["abstencion"] == {"abstiene": True, "motivos": ["sin_pasajes"]}
    assert traza["errores_schema"] == []


@pytest.mark.parametrize(
    ("modo", "expected_abstention", "expected_reasons"),
    [
        ("off", False, []),
        ("reglas", True, ["senal_umbral:top1_rank_denso"]),
    ],
)
def test_integracion_de_senales_sin_alterar_modo_off(
    monkeypatch, regla, modo, expected_abstention, expected_reasons
):
    monkeypatch.setattr(config, "ABSTENCION_MODO", modo)
    monkeypatch.setattr(config, "CITAR_EVIDENCIA", "no")
    monkeypatch.setattr(
        abstencion, "senales", lambda *args: {"top1_rank_denso": 19}
    )
    monkeypatch.setattr(
        responder_module,
        "_generar_json",
        lambda *args: {
            "respuesta": "Respuesta clara y suficientemente concreta.",
            "palabras_clave": ["regla", "prueba", "plazo"],
            "referencia_legal": "Norma aplicable.",
        },
    )
    item = {
        "id": 9,
        "formato": "semi_open",
        "pregunta": "Pregunta de prueba.",
    }

    registro, traza = responder(
        item, RetrieverConPasaje(), DecoderNoUsado(), regla_abstencion=regla
    )

    assert registro["abstencion"] is expected_abstention
    assert traza["abstencion"]["motivos"] == expected_reasons
    assert traza["errores_schema"] == []
    assert len(registro["pasajes_recuperados"]) == 1


def test_off_no_invoca_la_regla_de_senales(monkeypatch):
    monkeypatch.setattr(config, "ABSTENCION_MODO", "off")

    def unexpected(*args, **kwargs):
        pytest.fail("modo off no debe evaluar señales para decidir abstención")

    monkeypatch.setattr(abstencion, "decidir_por_senales", unexpected)
    item = {
        "id": 8,
        "formato": "multiple_choice",
        "pregunta": "Pregunta de prueba sin evidencia.",
        "opciones": {"A": "Una", "B": "Dos"},
    }
    registro, traza = responder(item, RetrieverSinPasajes(), DecoderNoUsado())

    assert registro["abstencion"] is abstencion.decidir(["sin_pasajes"])
    assert traza["abstencion"]["motivos"] == ["sin_pasajes"]
