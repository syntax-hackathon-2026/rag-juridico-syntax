"""Analisis offline de señales de abstencion (Fase A del Plan 04).

Uso: python src/evaluacion/analisis_abstencion.py --experimento e02_v0

La etiqueta de acierto reproduce score_abstention de scripts/evaluate.py:
opcion exacta para cerradas calificadas y solapamiento de cuerpos de citas para
texto libre. Las preguntas de texto libre sin citas extraibles se excluyen del
componente, como hace el evaluador. No se infiere acierto de errores.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import citations  # noqa: E402
import config  # noqa: E402
from common import FLAWED_IDS, read_jsonl  # noqa: E402
from evaluate import answer_text  # noqa: E402
from generacion.abstencion import (  # noqa: E402
    ReglaAbstencion,
    cargar_regla,
    decidir_por_senales,
)

PERCENTILES = (5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95)
FORMATS = ("multiple_choice", "semi_open", "open_ended")
SENSITIVITY_CANDIDATES = (
    ("semi_open: top1_rank_denso > 18.5", "semi_open",
     "top1_rank_denso", ">", 18.5),
    ("open_ended: frac_en_ambas_ramas < 0.74", "open_ended",
     "frac_en_ambas_ramas", "<", 0.74),
    ("open_ended: score_top1 < 0.03164", "open_ended",
     "score_top1", "<", 0.03164),
)
SIGNAL_SUMMARY_FIELDS = (
    "experimento", "tipo_fila", "formato", "senal", "grupo", "n", "media",
    "auc_error_mayor", "cuartil", "q25", "q50", "q75", "n_aciertos",
    "n_errores", "percentil", "umbral", "abstener_si", "errores_capturados",
    "aciertos_perdidos", "estimacion_componente_abstencion_numerador",
    "n_senales_faltantes",
)


def read_jsonl_by_id(path: Path) -> dict[int, dict]:
    rows = read_jsonl(path)
    indexed = {}
    for row in rows:
        qid = row.get("id")
        if not isinstance(qid, int):
            raise ValueError(f"{path}: id ausente o no entero")
        if qid in indexed:
            raise ValueError(f"{path}: id duplicado {qid}")
        indexed[qid] = row
    return indexed


def read_errors(path: Path) -> dict[int, dict[str, str]]:
    indexed = {}
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise ValueError(f"{path}: falta columna id")
        for row in reader:
            try:
                qid = int(row["id"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path}: id invalido {row.get('id')!r}") from exc
            if qid in indexed:
                raise ValueError(f"{path}: id duplicado {qid}")
            indexed[qid] = row
    return indexed


def quantile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("No se puede calcular un cuantil sin valores")
    position = (percentile / 100) * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def numeric_value(value: object) -> float | None:
    if isinstance(value, bool) or value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def auc_error_higher(errors: list[float], correct: list[float]) -> float | None:
    """Empirical AUC with errors as positives; ties count as one half."""
    if len(errors) < 2 or len(correct) < 2:
        return None
    wins = sum((error > ok) + 0.5 * (error == ok)
               for error in errors for ok in correct)
    return wins / (len(errors) * len(correct))


def evaluator_label(item: dict, submission: dict | None, reference: set,
                    closed_scored: bool) -> tuple[str, bool | None]:
    """Per-item classification matching evaluate.score_abstention."""
    if not closed_scored and not reference:
        return "excluido_sin_cita_extraible", None
    if submission is None:
        return "error_sin_entrega", False
    if closed_scored:
        correct = (submission.get("respuesta_correcta")
                   == item.get("respuesta_correcta"))
    else:
        cited = citations.extract(answer_text(submission))
        correct = bool(citations.bodies(reference) & citations.bodies(cited))
    return ("acierto" if correct else "error"), correct


def threshold_sensitivity(rows: list[dict]) -> tuple[list[dict], dict[str, set[int]]]:
    """Apply specified cutoffs and multiplicative +/-10%/+/-20% perturbations."""
    scenarios = []
    base_ids = {}
    for name, fmt, signal, operator, base_threshold in SENSITIVITY_CANDIDATES:
        format_rows = [row for row in rows if row["formato"] == fmt
                       and row["acierto_segun_componente_abstencion"] != ""]
        for variation, factor in (
            ("-20%", 0.8), ("-10%", 0.9), ("base", 1.0),
            ("+10%", 1.1), ("+20%", 1.2),
        ):
            threshold = base_threshold * factor
            missing_rows = [
                row for row in format_rows
                if numeric_value(row.get(signal)) is None
            ]
            affected = {
                row["id"] for row in format_rows
                if (value := numeric_value(row.get(signal))) is not None
                and (value > threshold if operator == ">"
                     else value < threshold)
            }
            captured = sum(
                row["id"] in affected and row["acierto_segun_componente_abstencion"] == 0
                for row in format_rows
            )
            lost = sum(
                row["id"] in affected and row["acierto_segun_componente_abstencion"] == 1
                for row in format_rows
            )
            scenarios.append({
                "candidate": name,
                "variation": variation,
                "format": fmt,
                "signal": signal,
                "operator": operator,
                "threshold": threshold,
                "affected_ids": affected,
                "captured_errors": captured,
                "lost_correct": lost,
                "missing_ids": {row["id"] for row in missing_rows},
            })
            if variation == "base":
                base_ids[name] = affected
    return scenarios, base_ids


def simular_regla(rows: list[dict], regla: ReglaAbstencion) -> dict:
    """Replays signal rules on saved traces and scores official abstention only."""
    eligible = [row for row in rows
                if row["acierto_segun_componente_abstencion"] != ""]
    newly_abstained = set()
    missing_signals = set()
    counts = Counter()
    by_format = defaultdict(list)
    for row in eligible:
        if row["formato"] == "semi_open" and regla.semi_open_top1_rank_denso_mayor_que is not None:
            if numeric_value(row.get("top1_rank_denso")) is None:
                missing_signals.add(row["id"])
        elif row["formato"] == "open_ended" and regla.open_ended_frac_en_ambas_ramas_menor_que is not None:
            if numeric_value(row.get("frac_en_ambas_ramas")) is None:
                missing_signals.add(row["id"])
        decision, _ = decidir_por_senales(row, row["formato"], regla)
        already_abstained = row["abstencion"] == 1
        abstained = already_abstained or decision
        if decision and not already_abstained:
            newly_abstained.add(row["id"])
            by_format[row["formato"]].append(row["id"])
        correct = row["acierto_segun_componente_abstencion"] == 1
        if abstained and not correct:
            counts["abstuvo_bien"] += 1
        elif abstained:
            counts["abstuvo_de_mas"] += 1
        elif correct:
            counts["respondio_bien"] += 1
        else:
            counts["respondio_mal"] += 1
    total = len(eligible)
    numerator = counts["respondio_bien"] + 0.5 * (
        counts["abstuvo_bien"] + counts["abstuvo_de_mas"]
    )
    calibration = numerator / total if total else 0.0
    return {
        "eligible": total,
        "new_ids": newly_abstained,
        "missing_signal_ids": missing_signals,
        "new_ids_by_format": dict(by_format),
        "captured_errors": counts["abstuvo_bien"],
        "lost_correct": counts["abstuvo_de_mas"],
        "responded_correct": counts["respondio_bien"],
        "responded_error": counts["respondio_mal"],
        "component_points": round(10 * calibration, 2),
        "calibration": calibration,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experimento", default="e02_v0")
    parser.add_argument("--outdir", type=Path, default=config.EVALUATION_DIR / "abstencion")
    args = parser.parse_args()

    exp = args.experimento
    trace_path = config.TRAZAS_DIR / f"{exp}.jsonl"
    experiment_dir = config.EVALUATION_DIR / "generacion" / exp
    errors_path = experiment_dir / "errores.csv"
    submission_path = experiment_dir / "entrega.jsonl"
    report_path = experiment_dir / "reporte.json"
    required = (trace_path, errors_path, submission_path, config.SAMPLE_PATH)
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("Faltan archivos necesarios:")
        for path in missing:
            print(f" - {path}")
        return 2

    bank = read_jsonl(config.SAMPLE_PATH)
    bank_by_id = {item["id"]: item for item in bank}
    if len(bank_by_id) != len(bank):
        raise ValueError(f"{config.SAMPLE_PATH}: IDs duplicados")
    traces = read_jsonl_by_id(trace_path)
    errors = read_errors(errors_path)
    submissions = read_jsonl_by_id(submission_path)
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}

    args.outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for qid, item in sorted(bank_by_id.items()):
        fmt = item["formato"]
        trace = traces.get(qid)
        error = errors.get(qid)
        submission = submissions.get(qid)
        reference = citations.extract(item.get("legal_basis") or "")
        closed_scored = fmt == "multiple_choice" and qid not in FLAWED_IDS
        label, correct = evaluator_label(item, submission, reference, closed_scored)
        abstained = bool(submission and submission.get("abstencion"))
        trace_signals = (trace or {}).get("senales") or {}
        rows.append({
            "id": qid,
            "formato": fmt,
            "estado_componente_abstencion": label,
            "acierto_segun_componente_abstencion": (
                "" if correct is None else int(correct)
            ),
            "abstencion": int(abstained) if submission is not None else "",
            "exactitud_cerrada_evaluable": int(closed_scored),
            "referencias_extraibles": len(reference),
            "traza_disponible": int(trace is not None),
            "errores_csv_disponible": int(error is not None),
            "entrega_disponible": int(submission is not None),
            "diagnostico": (error or {}).get("diagnostico", ""),
            "correcta_csv_cerradas": (error or {}).get("correcta", ""),
            "rank_doc": (error or {}).get("rank_doc", ""),
            "rank_art": (error or {}).get("rank_art", ""),
            "aciertos_cita": (error or {}).get("aciertos_cita", ""),
            "sin_respaldo": (error or {}).get("sin_respaldo", ""),
            "latencia_s": (error or {}).get("latencia_s", ""),
            "ragas_individual": (
                "no_disponible" if fmt != "multiple_choice" else "no_aplica"
            ),
            **trace_signals,
        })

    per_item_path = args.outdir / f"{exp}_senales.csv"
    fixed_fields = [
        "id", "formato", "estado_componente_abstencion",
        "acierto_segun_componente_abstencion", "abstencion",
        "exactitud_cerrada_evaluable", "referencias_extraibles",
        "traza_disponible", "errores_csv_disponible", "entrega_disponible",
        "diagnostico", "correcta_csv_cerradas", "rank_doc", "rank_art",
        "aciertos_cita", "sin_respaldo", "latencia_s", "ragas_individual",
    ]
    signal_fields = sorted({
        key for row in rows for key in row
        if key not in fixed_fields
    })
    fields = fixed_fields + signal_fields
    with per_item_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # Per-format signal statistics and threshold curves. Only items eligible
    # for the official abstention component are labeled/scored.
    summary_rows = []
    labeled_by_format = defaultdict(list)
    for row in rows:
        if row["acierto_segun_componente_abstencion"] != "":
            labeled_by_format[row["formato"]].append(row)

    for fmt in FORMATS:
        fmt_rows = labeled_by_format[fmt]
        correct_rows = [row for row in fmt_rows
                        if row["acierto_segun_componente_abstencion"] == 1]
        error_rows = [row for row in fmt_rows
                      if row["acierto_segun_componente_abstencion"] == 0]
        for signal in signal_fields:
            correct_values = [
                value for row in correct_rows
                if (value := numeric_value(row.get(signal))) is not None
            ]
            error_values = [
                value for row in error_rows
                if (value := numeric_value(row.get(signal))) is not None
            ]
            auc = auc_error_higher(error_values, correct_values)
            values_by_group = {}
            all_values = []
            for group, group_rows in (("acierto", correct_rows), ("error", error_rows)):
                signal_values = correct_values if group == "acierto" else error_values
                values_by_group[group] = signal_values
                all_values.extend(signal_values)
                summary_rows.append({
                    "experimento": exp, "tipo_fila": "media", "formato": fmt,
                    "senal": signal, "grupo": group, "n": len(signal_values),
                    "media": mean(signal_values) if signal_values else "",
                    "auc_error_mayor": auc if auc is not None else "",
                    "n_aciertos": len(correct_rows), "n_errores": len(error_rows),
                    "n_senales_faltantes": len(group_rows) - len(signal_values),
                })
            combined = correct_values + error_values
            if combined:
                q25, q50, q75 = (quantile(combined, q) for q in (25, 50, 75))
                quartile_counts = Counter()
                for row in fmt_rows:
                    value = numeric_value(row.get(signal))
                    if value is None:
                        continue
                    group = ("acierto" if row["acierto_segun_componente_abstencion"] == 1
                             else "error")
                    quartile = (1 if value <= q25 else 2 if value <= q50
                                else 3 if value <= q75 else 4)
                    quartile_counts[(quartile, group)] += 1
                for quartile in range(1, 5):
                    summary_rows.append({
                        "experimento": exp, "tipo_fila": "cuartil", "formato": fmt,
                        "senal": signal, "grupo": "todos",
                        "auc_error_mayor": auc, "cuartil": quartile,
                        "q25": q25, "q50": q50, "q75": q75,
                        "n_aciertos": quartile_counts[(quartile, "acierto")],
                        "n_errores": quartile_counts[(quartile, "error")],
                    })
            if not combined:
                continue
            for percentile in PERCENTILES:
                threshold = quantile(combined, percentile)
                for direction in ("<", ">"):
                    captured = sum(v < threshold if direction == "<" else v > threshold
                                   for v in error_values)
                    lost = sum(v < threshold if direction == "<" else v > threshold
                               for v in correct_values)
                    summary_rows.append({
                        "experimento": exp,
                        "tipo_fila": "umbral_candidato",
                        "formato": fmt,
                        "senal": signal,
                        "grupo": "todos",
                        "auc_error_mayor": auc,
                        "n_aciertos": len(correct_rows),
                        "n_errores": len(error_rows),
                        "percentil": percentile,
                        "umbral": threshold,
                        "abstener_si": direction,
                        "errores_capturados": captured,
                        "aciertos_perdidos": lost,
                        "estimacion_componente_abstencion_numerador":
                            0.5 * captured - 0.5 * lost,
                        "n_senales_faltantes": len(fmt_rows) - len(combined),
                    })

    candidates_path = args.outdir / f"{exp}_umbral_candidatos.csv"
    with candidates_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=SIGNAL_SUMMARY_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    official_check = Counter()
    for row in rows:
        correct = row["acierto_segun_componente_abstencion"]
        if correct == "":
            continue
        abstained = row["abstencion"] == 1
        if abstained and correct == 0:
            official_check["abstuvo_bien"] += 1
        elif abstained:
            official_check["abstuvo_de_mas"] += 1
        elif correct == 1:
            official_check["respondio_bien"] += 1
        else:
            official_check["respondio_mal"] += 1
    if report.get("abstencion"):
        official_result = report["abstencion"]
        for key in ("items_evaluados", "abstuvo_bien", "abstuvo_de_mas",
                    "respondio_bien", "respondio_mal"):
            calculated = (
                sum(official_check.values()) if key == "items_evaluados"
                else official_check[key]
            )
            if calculated != official_result.get(key):
                raise ValueError(
                    "La clasificacion por ID no coincide con "
                    f"reporte.json ({key}: {calculated} != {official_result.get(key)})"
                )

    sensitivity_rows, candidate_base_ids = threshold_sensitivity(rows)
    base_rule = cargar_regla(config.ABSTENCION_CONFIG_PATH)
    simulation_rule_sets = [("sin reglas (base observada)", ReglaAbstencion())]
    simulation_rule_sets.append(("reglas experimentales (base)", base_rule))
    sensitivity_variants = {}
    for factor, label in ((0.8, "-20%"), (1.2, "+20%")):
        semi_variant = replace(
            base_rule,
            semi_open_top1_rank_denso_mayor_que=(
                base_rule.semi_open_top1_rank_denso_mayor_que * factor
            ),
        )
        open_variant = replace(
            base_rule,
            open_ended_frac_en_ambas_ramas_menor_que=(
                base_rule.open_ended_frac_en_ambas_ramas_menor_que * factor
            ),
        )
        both_variant = replace(
            base_rule,
            semi_open_top1_rank_denso_mayor_que=(
                base_rule.semi_open_top1_rank_denso_mayor_que * factor
            ),
            open_ended_frac_en_ambas_ramas_menor_que=(
                base_rule.open_ended_frac_en_ambas_ramas_menor_que * factor
            ),
        )
        simulation_rule_sets.extend([
            (f"solo semi_open {label}", semi_variant),
            (f"solo open_ended {label}", open_variant),
            (f"ambos formatos {label}", both_variant),
        ])
    simulations = [
        (name, simular_regla(rows, rule))
        for name, rule in simulation_rule_sets
    ]
    baseline_points = simulations[0][1]["component_points"]
    if report.get("abstencion") and baseline_points != report["abstencion"].get("puntos"):
        raise ValueError(
            "La simulacion sin reglas no coincide con el reporte oficial de abstencion"
        )

    # The official report, per-format counts, and item-level status lists make
    # clear which items were scored, excluded, or lack a source/metric.
    lines = [
        f"# Resultados del analisis de abstencion - {exp}",
        "",
        "Comando: `python src/evaluacion/analisis_abstencion.py "
        f"--experimento {exp}`",
        "",
        "Fuentes comprobadas:",
        f"- `salidas/trazas/{exp}.jsonl`: {len(traces)} trazas.",
        f"- `evaluation/generacion/{exp}/errores.csv`: {len(errors)} filas.",
        f"- `evaluation/generacion/{exp}/entrega.jsonl`: {len(submissions)} respuestas.",
        f"- `data/sample_50.jsonl`: {len(bank_by_id)} IDs de referencia.",
        f"- Modo runtime y hash de config: `{config.abstencion_metadata()}`.",
        "",
        "## Regla oficial y limites de los datos",
        "",
        "La etiqueta de acierto de este analisis replica `score_abstention` en "
        "`scripts/evaluate.py`: cerradas calificadas comparan la opcion; "
        "semiabiertas y abiertas comparan los cuerpos de citas extraibles en "
        "`answer_text` contra `legal_basis`. Las preguntas de texto libre sin "
        "citas extraibles se excluyen del denominador oficial. El ID 374 se "
        "excluye de exactitud cerrada mediante `FLAWED_IDS`; la logica oficial "
        "de abstencion solo lo trata como cerrado si pertenece a `closed_ids`.",
        "",
        "`errores.csv.correcta` solo se informa para cerradas; sus vacios en "
        "texto libre no son aciertos ni errores. El reporte disponible no "
        "contiene puntuaciones RAGAS por ID (el `reporte.json` marca RAGAS "
        "pendiente), asi que `ragas_individual` queda como no disponible. "
        "`aciertos_cita`, `rank_doc`, `rank_art`, diagnostico y latencia se "
        "conservan tal como vienen de `errores.csv`; no sustituyen RAGAS.",
        "",
        "La columna `estimacion_componente_abstencion_numerador` usa "
        "`0.5 * errores_capturados - 0.5 * aciertos_perdidos`: estima solo "
        "el cambio del numerador del componente de abstencion segun la regla "
        "oficial. No son puntos totales ni incluye cambios en exactitud, "
        "citacion o RAGAS. Los umbrales son candidatos exploratorios; no se "
        "selecciona ninguno.",
        "",
    ]
    if report.get("abstencion"):
        result = report["abstencion"]
        lines.extend([
            "Comprobacion contra el reporte oficial: "
            f"{result['items_evaluados']} IDs evaluados, "
            f"{result['respondio_bien']} aciertos y "
            f"{result['respondio_mal']} errores; coincide con la clasificacion "
            "por ID.",
            "",
        ])
    lines.extend([
        "## Estado por formato",
        "",
        "| Formato | IDs | Evaluables | Aciertos | Errores | Excluidos por falta de cita | Faltan entrega/traza/errores.csv |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for fmt in FORMATS:
        format_rows = [row for row in rows if row["formato"] == fmt]
        labels = Counter(row["estado_componente_abstencion"] for row in format_rows)
        evaluated = sum(labels[label] for label in ("acierto", "error", "error_sin_entrega"))
        missing_rows = [
            row for row in format_rows
            if not (row["entrega_disponible"] and row["traza_disponible"]
                    and row["errores_csv_disponible"])
        ]
        lines.append(
            f"| `{fmt}` | {len(format_rows)} | {evaluated} | {labels['acierto']} | "
            f"{labels['error'] + labels['error_sin_entrega']} | "
            f"{labels['excluido_sin_cita_extraible']} | {len(missing_rows)} |"
        )
    lines.extend(["", "IDs individuales, en el orden del banco:", ""])
    for fmt in FORMATS:
        format_rows = [row for row in rows if row["formato"] == fmt]
        items = ", ".join(
            f"{row['id']}={row['estado_componente_abstencion']}"
            for row in format_rows
        )
        lines.extend([f"- **{fmt}** ({len(format_rows)}): {items}"])

    excluded_ids = [str(row["id"]) for row in rows
                    if row["estado_componente_abstencion"] == "excluido_sin_cita_extraible"]
    flawed_ids_in_sample = [str(row["id"]) for row in rows
                            if row["id"] in FLAWED_IDS]
    missing_by_source = {
        label: [str(row["id"]) for row in rows if not row[key]]
        for label, key in (
            ("entrega", "entrega_disponible"),
            ("traza", "traza_disponible"),
            ("errores.csv", "errores_csv_disponible"),
        )
    }
    lines.extend([
        "",
        f"Excluidos del componente por `legal_basis` sin cita extraible: "
        f"{', '.join(excluded_ids) if excluded_ids else 'ninguno'}.",
        f"IDs `FLAWED_IDS` presentes en la muestra: "
        f"{', '.join(flawed_ids_in_sample) if flawed_ids_in_sample else 'ninguno'}.",
        "",
        "Faltantes por fuente:",
    ])
    for source, ids in missing_by_source.items():
        lines.append(f"- {source}: {', '.join(ids) if ids else 'ninguno'}.")
    if report:
        ragas = report.get("correccion_ragas", {})
        lines.append(
            f"- RAGAS agregado en `reporte.json`: "
            f"{ragas.get('estado', 'no hay seccion')}; no se dispone de "
            "veredictos individuales en las fuentes revisadas."
        )
    lines.extend([
        "",
        "## Sensibilidad de cortes exploratorios",
        "",
        "Aplicados solo a las preguntas evaluables por el componente oficial "
        "de abstencion del formato indicado. Las perturbaciones multiplican el "
        "umbral base por 0.8, 0.9, 1.1 y 1.2 (el signo de la desigualdad no "
        "cambia). IDs afectados son los que satisfacen el corte; las señales "
        "faltantes se reportan aparte y no se cuentan como afectados.",
        "",
        "| Candidato | Variacion | Umbral | IDs afectados | Errores capturados | Aciertos perdidos | Señal faltante (IDs) |",
        "|---|---:|---:|---|---:|---:|---|",
    ])
    for scenario in sensitivity_rows:
        ids_text = ", ".join(map(str, sorted(scenario["affected_ids"]))) or "ninguno"
        missing_text = ", ".join(map(str, sorted(scenario["missing_ids"]))) or "ninguno"
        lines.append(
            f"| `{scenario['candidate']}` | {scenario['variation']} | "
            f"{scenario['threshold']:.8g} | {ids_text} | "
            f"{scenario['captured_errors']} | {scenario['lost_correct']} | "
            f"{missing_text} |"
        )
    lines.extend([
        "",
        "### Solapamiento entre candidatos base",
        "",
        "Interseccion de IDs afectados (cada candidato se evalua solo en su "
        "formato elegible; un ID de otro formato no pertenece a su conjunto):",
        "",
        "| Candidatos | IDs compartidos |",
        "|---|---|",
    ])
    base_candidates = list(candidate_base_ids.items())
    for first_index, (first, first_ids) in enumerate(base_candidates):
        for second, second_ids in base_candidates[first_index + 1:]:
            overlap = sorted(first_ids & second_ids)
            lines.append(
                f"| `{first}` ∩ `{second}` | "
                f"{', '.join(map(str, overlap)) if overlap else 'ninguno'} |"
            )
    all_overlap = set.intersection(*(ids for _, ids in base_candidates)) if base_candidates else set()
    lines.append(
        f"| Los tres candidatos | "
        f"{', '.join(map(str, sorted(all_overlap))) if all_overlap else 'ninguno'} |"
    )
    lines.extend([
        "",
        "Estos resultados son descriptivos sobre la misma muestra usada para "
        "proponer los cortes. No son validacion independiente ni justifican "
        "elegir una regla definitiva; las preguntas y escenarios no constituyen "
        "muestras independientes. La etiqueta de error en texto libre sigue "
        "siendo la coincidencia de citas del componente oficial, no un veredicto "
        "RAGAS individual, que no esta disponible.",
    ])
    lines.extend([
        "",
        "## Simulacion offline de las reglas experimentales",
        "",
        "Reaplicacion determinista a las senales ya guardadas. `sin reglas` usa "
        "las abstenciones de la entrega existente; las variantes usan la "
        "configuracion versionada, manteniendo sin reglas nuevas a "
        "`multiple_choice`. La metrica de la tabla es solo el componente oficial "
        "de abstencion; no estima puntos totales ni RAGAS.",
        "",
        "| Escenario | Nuevas abstenciones (IDs por formato) | Errores capturados | Aciertos perdidos | Señales faltantes | Puntos componente abstencion | Cambio vs base |",
        "|---|---|---:|---:|---|---:|---:|",
    ])
    for name, simulation in simulations:
        ids_by_format = "; ".join(
            f"{fmt}: {', '.join(map(str, sorted(ids)))}"
            for fmt, ids in sorted(simulation["new_ids_by_format"].items())
        ) or "ninguna"
        missing_ids = ", ".join(map(str, sorted(simulation["missing_signal_ids"]))) or "ninguna"
        delta = round(simulation["component_points"] - baseline_points, 2)
        lines.append(
            f"| {name} | {ids_by_format} | {simulation['captured_errors']} | "
            f"{simulation['lost_correct']} | {missing_ids} | "
            f"{simulation['component_points']:.2f} | {delta:+.2f} |"
        )
    base_simulation = simulations[1][1]
    extreme_simulations = [
        result for name, result in simulations
        if name.startswith("ambos formatos ") and name != "ambos formatos base"
    ]
    sensitivity_component_ok = all(
        result["component_points"] > baseline_points for result in extreme_simulations
    )
    if sensitivity_component_ok:
        sensitivity_note = (
            "En los extremos conjuntos ±20%, la estimacion del componente de "
            "abstencion sigue por encima de la base observada."
        )
    else:
        sensitivity_note = (
            "La sensibilidad conjunta ±20% falla: al menos un extremo no mejora "
            "el componente oficial frente a la base observada."
        )
    lines.extend([
        "",
        sensitivity_note,
        f"En la configuracion base se capturan {base_simulation['captured_errors']} "
        f"errores y se pierden {base_simulation['lost_correct']} aciertos. "
        "La sensibilidad y el tamaño de la muestra no constituyen validacion "
        "independiente; aunque el componente aislado sea positivo, faltan "
        "veredictos RAGAS por ID para estimar el efecto total. Por ello este "
        "resultado no recomienda activar las reglas.",
    ])
    lines.extend([
        "",
        "## Salidas y pendientes",
        "",
        f"- CSV por ID y formato: `{per_item_path.relative_to(ROOT).as_posix()}`.",
        f"- Medias, AUC (solo con al menos dos casos por clase), conteos por "
        f"cuartil y curvas de candidatos: `{candidates_path.relative_to(ROOT).as_posix()}`.",
        "- Configuracion experimental de Fase B: `config/abstencion.json`; "
        "multiple_choice no tiene reglas nuevas.",
        "- RAGAS individual requeriria conservar/exportar el resultado por pregunta "
        "del juez; no se puede reconstruir del puntaje agregado.",
        "- Fase B implementada con activacion opt-in; `SYNTAX_ABSTENCION=off` "
        "sigue siendo el default. No se valido como regla de produccion.",
        "- No se modificaron prompts ni la generacion del decoder.",
    ])
    results_path = ROOT / "docs" / "mejoras" / "resultados_04.md"
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    counts = Counter(row["estado_componente_abstencion"] for row in rows)
    print(f"IDs sample: {len(rows)}")
    for fmt in FORMATS:
        labels = Counter(row["estado_componente_abstencion"] for row in rows
                         if row["formato"] == fmt)
        print(f"{fmt}: {dict(labels)}")
    print(f"Salidas: {per_item_path}; {candidates_path}; {results_path}")
    print(f"Estado total: {dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
