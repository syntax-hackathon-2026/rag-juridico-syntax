"""Abstencion: regla v0 y senales para calibrarla despues.

Por que casi nunca se abstiene (scripts/evaluate.py): abstenerse vale 0,5 en el
componente de abstencion (10 pts), pero 0 en exactitud de cerradas y 0 en RAGAS (las
abstenciones no se juzgan y cuentan como cero), y 0 en citacion. Con respaldo@10 ~0,9
responder es casi siempre mejor. La regla v0 solo se abstiene cuando no hay nada que
entregar con garantias:

  - sin_pasajes:          la recuperacion no devolvio nada.
  - salida_invalida:      el decoder no produjo un JSON util tras reintentar.
  - citas_irreparables:   quitar las citas sin respaldo deja vacio un campo obligatorio.

Las senales se registran en cada traza para elegir despues una regla simple con
datos (CLAUDE.md: no ajustar umbrales finos a 50 muestras).
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generacion import citas  # noqa: E402


@dataclass(frozen=True)
class ReglaAbstencion:
    semi_open_top1_rank_denso_mayor_que: float | None = None
    open_ended_frac_en_ambas_ramas_menor_que: float | None = None


def cargar_regla(path: Path) -> ReglaAbstencion:
    """Carga y valida la configuración versionada de reglas de abstención."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"version", "formatos"}:
        raise ValueError(f"Configuracion de abstencion invalida: {path}")
    if data["version"] != 1:
        raise ValueError(f"Version de configuracion de abstencion no soportada: {data['version']!r}")
    formatos = data["formatos"]
    if not isinstance(formatos, dict) or set(formatos) != {
        "multiple_choice", "semi_open", "open_ended"
    }:
        raise ValueError(f"Formatos invalidos en configuracion de abstencion: {path}")

    closed = formatos["multiple_choice"]
    if closed != {}:
        raise ValueError("Las reglas por senales para multiple_choice deben permanecer vacias")

    def threshold(formato: str, key: str, *, minimum: float | None = None,
                  maximum: float | None = None) -> float:
        config = formatos[formato]
        if not isinstance(config, dict) or set(config) != {key}:
            raise ValueError(
                f"Configuracion invalida para {formato}: se esperaba solo {key}"
            )
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Umbral invalido para {formato}.{key}: {value!r}")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"Umbral no finito para {formato}.{key}: {value!r}")
        if minimum is not None and value < minimum:
            raise ValueError(f"Umbral fuera de rango para {formato}.{key}: {value!r}")
        if maximum is not None and value > maximum:
            raise ValueError(f"Umbral fuera de rango para {formato}.{key}: {value!r}")
        return value

    return ReglaAbstencion(
        semi_open_top1_rank_denso_mayor_que=threshold(
            "semi_open", "top1_rank_denso_mayor_que", minimum=0
        ),
        open_ended_frac_en_ambas_ramas_menor_que=threshold(
            "open_ended", "frac_en_ambas_ramas_menor_que",
            minimum=0, maximum=1,
        ),
    )


def _numero(senales: dict, nombre: str) -> float | None:
    valor = senales.get(nombre)
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    valor = float(valor)
    return valor if math.isfinite(valor) else None


def decidir_por_senales(
    senales: dict, formato: str, config: ReglaAbstencion
) -> tuple[bool, list[str]]:
    """Aplica únicamente las reglas configuradas; entradas ausentes no activan."""
    if formato not in {"multiple_choice", "semi_open", "open_ended"}:
        raise ValueError(f"Formato no soportado para abstencion: {formato!r}")
    if not isinstance(senales, dict):
        senales = {}

    motivos = []
    if formato == "semi_open" and config.semi_open_top1_rank_denso_mayor_que is not None:
        rank = _numero(senales, "top1_rank_denso")
        if rank is not None and rank > config.semi_open_top1_rank_denso_mayor_que:
            motivos.append("senal_umbral:top1_rank_denso")
    elif formato == "open_ended" and config.open_ended_frac_en_ambas_ramas_menor_que is not None:
        overlap = _numero(senales, "frac_en_ambas_ramas")
        if overlap is not None and overlap < config.open_ended_frac_en_ambas_ramas_menor_que:
            motivos.append("senal_umbral:frac_en_ambas_ramas")
    return bool(motivos), motivos


def senales(consulta: str, top: list, perm: set) -> dict:
    """Senales de suficiencia de la evidencia. `top`: RetrievedChunk del top-10."""
    if not top:
        return {"n_pasajes": 0}
    scores = [p.score for p in top]
    en_ambas = [p for p in top if p.meta.get("rank_bm25") and p.meta.get("rank_denso")]
    explicitas = citas.cuerpos(consulta)
    return {
        "n_pasajes": len(top),
        "score_top1": round(scores[0], 6),
        "margen_top1_top2": round(scores[0] - scores[1], 6) if len(scores) > 1 else None,
        "top1_rank_bm25": top[0].meta.get("rank_bm25"),
        "top1_rank_denso": top[0].meta.get("rank_denso"),
        "frac_en_ambas_ramas": round(len(en_ambas) / len(top), 3),
        "n_cuerpos_top10": len({tuple(p.meta.get("canonico") or ()) for p in top}),
        "n_sentencias_top10": sum(p.meta.get("tipo") == "sentencia" for p in top),
        "normas_en_pregunta": sorted(map(list, explicitas), key=str),
        "normas_pregunta_en_evidencia": len(explicitas & perm),
    }


def decidir(motivos: list[str]) -> bool:
    return bool(motivos)
