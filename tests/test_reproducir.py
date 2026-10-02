"""Logica pura de src/reproducibilidad/reproducir.py: etapas, seleccion de preguntas, comandos y juez.

Sin GPU, sin red y sin tocar el entorno: solo funciones puras y --dry-run.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location("reproducir", ROOT / "src" / "reproducibilidad" / "reproducir.py")
rp = importlib.util.module_from_spec(_spec)
sys.modules["reproducir"] = rp
_spec.loader.exec_module(rp)


def args(*argv: str):
    return rp.crear_parser().parse_args(list(argv))


def escribir(ruta: Path, items: list[dict]) -> Path:
    ruta.write_text("\n".join(json.dumps(i) for i in items) + "\n", encoding="utf-8")
    return ruta


def q(i: int, formato: str = "semi_open") -> dict:
    return {"id": i, "formato": formato, "pregunta": f"pregunta {i}"}


# --- etapas -------------------------------------------------------------------------------

def test_todas_por_defecto():
    assert rp.resolver_etapas() == rp.ETAPAS


@pytest.mark.parametrize("solo, esperado", [
    ("indice", ["indice"]),
    ("evaluar,corpus", ["corpus", "evaluar"]),  # siempre en orden canonico
    (" preguntas , evaluar ", ["preguntas", "evaluar"]),
])
def test_solo(solo, esperado):
    assert rp.resolver_etapas(solo=solo) == esperado


@pytest.mark.parametrize("desde, hasta, esperado", [
    (None, "indice", ["entorno", "corpus", "indice"]),
    ("preguntas", None, ["preguntas", "evaluar"]),
    ("corpus", "decoder", ["corpus", "indice", "decoder"]),
    ("evaluar", "evaluar", ["evaluar"]),
])
def test_desde_hasta(desde, hasta, esperado):
    assert rp.resolver_etapas(desde=desde, hasta=hasta) == esperado


@pytest.mark.parametrize("kw", [
    {"solo": "indice", "hasta": "indice"},
    {"solo": "indice", "desde": "corpus"},
    {"solo": "nada"},
    {"solo": ""},
    {"desde": "evaluar", "hasta": "corpus"},
])
def test_etapas_invalidas(kw):
    with pytest.raises(ValueError):
        rp.resolver_etapas(**kw)


# --- seleccion de preguntas ---------------------------------------------------------------

def test_rango():
    assert rp.parsear_rango("100-200") == (100, 200)
    assert rp.parsear_rango(" 5 - 5 ") == (5, 5)
    for malo in ("200-100", "a-b", "10", "1-2-3", ""):
        with pytest.raises(ValueError):
            rp.parsear_rango(malo)


def test_seleccion_ids_rango_y_ninguna():
    items = [q(i) for i in (1, 5, 7, 9, 12)]
    assert rp.seleccion(args(), items) is None
    assert rp.seleccion(args("--ids", "9", "1", "9"), items) == [9, 1]
    assert rp.seleccion(args("--rango", "5-9"), items) == [5, 7, 9]  # solo los que existen
    with pytest.raises(ValueError, match="no estan"):
        rp.seleccion(args("--ids", "1", "2"), items)
    with pytest.raises(ValueError, match="ningun id"):
        rp.seleccion(args("--rango", "100-200"), items)
    with pytest.raises(ValueError, match="excluyentes"):
        rp.seleccion(args("--ids", "1", "--rango", "1-5"), items)


def test_hay_seleccion():
    assert not rp.hay_seleccion(args())
    for extra in (["--ids", "1"], ["--rango", "1-2"], ["--limite", "3"], ["--particion", "1/2"]):
        assert rp.hay_seleccion(args(*extra))


def test_leer_preguntas(tmp_path):
    ok = escribir(tmp_path / "ok.jsonl", [q(1, "multiple_choice"), q(2, "open_ended")])
    assert [i["id"] for i in rp.leer_preguntas(ok)] == [1, 2]
    with pytest.raises(ValueError, match="No existe"):
        rp.leer_preguntas(tmp_path / "nada.jsonl")
    with pytest.raises(ValueError, match="repetido"):
        rp.leer_preguntas(escribir(tmp_path / "dup.jsonl", [q(1), q(1)]))
    with pytest.raises(ValueError, match="formato"):
        rp.leer_preguntas(escribir(tmp_path / "fmt.jsonl", [{"id": 1, "formato": "otro", "pregunta": "x"}]))
    with pytest.raises(ValueError, match="id"):
        rp.leer_preguntas(escribir(tmp_path / "sinid.jsonl", [{"formato": "semi_open", "pregunta": "x"}]))
    (tmp_path / "roto.jsonl").write_text("{no es json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="JSON invalido"):
        rp.leer_preguntas(tmp_path / "roto.jsonl")
    (tmp_path / "vacio.jsonl").write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no tiene preguntas"):
        rp.leer_preguntas(tmp_path / "vacio.jsonl")


def test_sample_50_es_valido():
    assert len(rp.leer_preguntas(rp.config.SAMPLE_PATH)) == 50


# --- rutas y comandos ---------------------------------------------------------------------

def test_ruta_entrega():
    assert rp.ruta_entrega(args("--split", "test")) == rp.config.SUBMISSION_PATH
    assert rp.ruta_entrega(args("--split", "test", "--ids", "1")).name == "test_windows_rtx4090.jsonl"
    assert rp.ruta_entrega(args("--split", "sample", "--experimento", "x")).name == "sample_x.jsonl"
    assert rp.ruta_entrega(args("--entrega", "otra.jsonl")) == Path("otra.jsonl")


def test_comando_main():
    a = args("--split", "test", "--entrada", "q.jsonl", "--limite", "5", "--particion", "2/3",
             "--experimento", "e", "--sin-reanudar")
    cmd = [str(c) for c in rp.comando_main(a, "py", None, Path("s.jsonl"))]
    assert cmd == ["py", "src/main.py", "--split", "test", "--experimento", "e", "--salida", "s.jsonl",
                   "--entrada", "q.jsonl", "--limite", "5", "--particion", "2/3", "--sin-reanudar"]
    cmd = [str(c) for c in rp.comando_main(args(), "py", [51, 60], Path("s.jsonl"))]
    assert cmd[-3:] == ["--ids", "51", "60"][-3:] and "--ids" in cmd and "--entrada" not in cmd


# --- evaluar ------------------------------------------------------------------------------

def test_juez(tmp_path):
    assert rp.llave_juez({"OPENROUTER_API_KEY": "sk-x"}, tmp_path / "no.env")
    assert not rp.llave_juez({"OPENROUTER_API_KEY": "  "}, tmp_path / "no.env")
    env = tmp_path / ".env"
    env.write_text("# c\nexport OPENROUTER_API_KEY='sk-y'\n", encoding="utf-8")
    assert rp.llave_juez({}, env)
    env.write_text("OPENROUTER_API_KEY=\nOTRA=1\n", encoding="utf-8")
    assert not rp.llave_juez({}, env)

    assert rp.usar_juez(args(), True)[0] is True
    assert rp.usar_juez(args(), False)[0] is False  # sin llave: se omite con aviso, no falla
    assert "OPENROUTER_API_KEY" in rp.usar_juez(args(), False)[1]
    assert rp.usar_juez(args("--sin-ragas"), True)[0] is False
    assert rp.usar_juez(args("--ragas"), True)[0] is True
    with pytest.raises(ValueError, match="falta OPENROUTER_API_KEY"):
        rp.usar_juez(args("--ragas"), False)
    with pytest.raises(ValueError, match="excluyentes"):
        rp.usar_juez(args("--ragas", "--sin-ragas"), True)


def test_comandos_evaluar_sample_completo():
    a = args("--experimento", "e", "--no-csv")
    cmds = rp.comandos_evaluar(a, "py", Path("s.jsonl"), juez=True)
    assert [c[1][1] for c in cmds] == ["src/reproducibilidad/validar_entrega.py", "src/evaluacion/evaluar_entrega.py"]
    ev = [str(x) for x in cmds[1][1]]
    assert "--ragas" in ev and "--no-csv" in ev and ev[ev.index("--corrida") + 1] == "e"
    assert "--preguntas" in [str(x) for x in cmds[0][1]]  # sin subconjunto: exige todos los ids


def test_comandos_evaluar_subconjunto_solo_schema():
    cmds = rp.comandos_evaluar(args("--ids", "51"), "py", Path("s.jsonl"), juez=False)
    assert len(cmds) == 1 and "--preguntas" not in [str(x) for x in cmds[0][1]]
    assert len(rp.comandos_evaluar(args("--entrada", "otra.jsonl"), "py", Path("s.jsonl"), juez=False)) == 1


def test_comandos_evaluar_test(monkeypatch):
    a = args("--split", "test")
    monkeypatch.setattr(rp, "jurado_test_presente", lambda: False)
    assert len(rp.comandos_evaluar(a, "py", Path("s.jsonl"), juez=False)) == 1  # sin clave: solo schema
    monkeypatch.setattr(rp, "jurado_test_presente", lambda: True)
    cmds = rp.comandos_evaluar(a, "py", Path("s.jsonl"), juez=True)
    ev = [str(x) for x in cmds[1][1]]
    assert ev[1] == "scripts/evaluate.py" and ev[ev.index("--split") + 1] == "test" and "--ragas" in ev


# --- validar_entrega ----------------------------------------------------------------------

def test_validar_entrega_detecta_problemas():
    pytest.importorskip("jsonschema")
    sys.path.insert(0, str(ROOT / "src" / "reproducibilidad"))
    from validar_entrega import validar_entrega

    reg = {"id": 1, "formato": "semi_open", "abstencion": True, "pasajes_recuperados": [],
           "respuesta": "", "palabras_clave": [], "referencia_legal": ""}
    res = validar_entrega([reg, dict(reg)], {"ley_1564_2012"}, {1, 2})
    assert any("repetido" in g for g in res["globales"]) and any("faltan" in g for g in res["globales"])
    malo = {**reg, "id": 3, "abstencion": False,
            "pasajes_recuperados": [{"doc_id": "no_existe", "texto": "x"}]}
    res = validar_entrega([malo], {"ley_1564_2012"})
    assert 3 in res["errores"]


# --- dry-run de punta a punta -------------------------------------------------------------

def test_dry_run_no_ejecuta(capsys, monkeypatch):
    llamadas = []
    monkeypatch.setattr(rp.subprocess, "run", lambda *a, **k: llamadas.append(a) or pytest.fail("no debe ejecutar"))
    monkeypatch.setattr(rp, "gpu_nvidia", lambda: None)
    monkeypatch.setattr(rp, "indice_al_dia", lambda: True)
    monkeypatch.setattr(rp, "venv_py", lambda: Path(sys.executable))
    codigo = rp.main(["--dry-run", "--solo", "preguntas,evaluar", "--rango", "51-60", "--sin-ragas"])
    salida = capsys.readouterr().out
    assert codigo == 0 and not llamadas
    assert "prerrequisitos: ok" in salida and "src/main.py" in salida and "--ids" in salida


def test_dry_run_reporta_prerrequisitos(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(rp, "gpu_nvidia", lambda: None)
    monkeypatch.setattr(rp, "indice_al_dia", lambda: False)
    codigo = rp.main(["--dry-run", "--solo", "preguntas", "--entrada", str(tmp_path / "no.jsonl")])
    salida = capsys.readouterr().out
    assert codigo == 1 and "--solo indice" in salida and "No existe" in salida
