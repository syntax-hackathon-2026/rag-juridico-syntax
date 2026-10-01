"""Analisis de señales para abstencion (Fase A del Plan 04).

Genera:
 - evaluation/abstencion/<exp>_senales.csv  (por-item, señales aplanadas)
 - evaluation/abstencion/<exp>_umbral_candidatos.csv (curvas por percentil)

Uso: python src/evaluacion/analisis_abstencion.py --experimento e02_v0

Reglas y convenciones:
 - Une salidas/trazas/<exp>.jsonl con evaluation/generacion/<exp>/errores.csv por id.
 - No asumimos que una pregunta ausente de errores.csv es un acierto: queda marcada como "missing_error".
 - "Exclusiones" en este análisis se consideran los items con diagnostico en
   ("SCHEMA","ABSTENCION","CORPUS") porque no aportan señales comparables
   para calibrar abstencion offline.
 - Para cada señal numerica se calcula la media en aciertos/errores y una curva
   de simulacion para percentiles [5,10,20,30,40,50,60,70,80,90,95].

"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

import config

PERCENTILES = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95]


def read_jsonl(path: Path) -> list[dict]:
    out = []
    if not path.is_file():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def read_errors_csv(path: Path) -> dict:
    if not path.is_file():
        return {}
    out = {}
    with path.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                idv = int(row.get("id"))
            except Exception:
                continue
            out[idv] = row
    return out


def flatten_senales(senales: dict) -> dict:
    """Convierte el dict de senales a valores simples serializables."""
    out = {}
    for k, v in (senales or {}).items():
        if isinstance(v, (list, dict)):
            out[k] = json.dumps(v, ensure_ascii=False)
        else:
            out[k] = v
    return out


def is_numeric(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def percentile_thresholds(values: list[float], percents: list[int]) -> list[float]:
    if not values:
        return []
    vals = sorted(values)
    n = len(vals)
    out = []
    for p in percents:
        # linear interpolation
        k = (p / 100) * (n - 1)
        lo = math.floor(k)
        hi = math.ceil(k)
        if lo == hi:
            out.append(vals[int(k)])
        else:
            w = k - lo
            out.append(vals[lo] * (1 - w) + vals[hi] * w)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experimento", default="e02_v0")
    ap.add_argument("--outdir", default=str(config.EVALUATION_DIR / "abstencion"))
    args = ap.parse_args()

    exp = args.experimento
    traces_path = config.TRAZAS_DIR / f"{exp}.jsonl"
    errors_path = config.EVALUATION_DIR / "generacion" / exp / "errores.csv"
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    missing = []
    if not traces_path.is_file():
        missing.append(str(traces_path))
    if not errors_path.is_file():
        missing.append(str(errors_path))
    if missing:
        print("Faltan archivos necesarios:")
        for m in missing:
            print(" -", m)
        return 2

    trazas = {t["id"]: t for t in read_jsonl(traces_path)}
    errores = read_errors_csv(errors_path)

    # union ids
    ids = sorted(set(list(trazas.keys()) + list(errores.keys())))

    # collect all senal keys
    senal_keys = set()
    for t in trazas.values():
        s = t.get("senales") or {}
        senal_keys |= set(s.keys())

    senal_keys = sorted(senal_keys)

    # write per-item signals
    senales_csv_path = outdir / f"{exp}_senales.csv"
    campos = ["id", "formato", "trace_exists", "error_exists", "diagnostico", "correcta", "abstencion"] + senal_keys
    with senales_csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(campos)
        for idv in ids:
            t = trazas.get(idv)
            e = errores.get(idv)
            formato = (e.get("formato") if e else (t.get("formato") if t else ""))
            row = [idv, formato, bool(t), bool(e), (e.get("diagnostico") if e else ""), None, None]
            if e and e.get("correcta") != "":
                try:
                    row[5] = int(e.get("correcta"))
                except Exception:
                    row[5] = ""
            else:
                row[5] = ""
            if e is not None:
                row[6] = e.get("abstencion")
            else:
                row[6] = ""
            s = flatten_senales((t or {}).get("senales") or {})
            for k in senal_keys:
                row.append(s.get(k, ""))
            w.writerow(row)

    print(f"Wrote per-item signals to {senales_csv_path}")

    # Now per-format analysis
    merged = []
    for idv in ids:
        t = trazas.get(idv)
        e = errores.get(idv)
        formato = (e.get("formato") if e else (t.get("formato") if t else None))
        correcta = None
        if e and e.get("correcta") != "":
            try:
                correcta = int(e.get("correcta"))
            except Exception:
                correcta = None
        sen = (t or {}).get("senales") or {}
        diagnostico = e.get("diagnostico") if e else None
        merged.append({"id": idv, "formato": formato, "correcta": correcta, "senales": sen, "diagnostico": diagnostico, "trace_exists": bool(t), "error_exists": bool(e)})

    # classify
    aciertos = [m for m in merged if m["correcta"] == 1 and m["trace_exists"]]
    errores_list = [m for m in merged if m["correcta"] == 0 and m["trace_exists"]]
    # exclusiones: diagnostico in SCHEMA, ABSTENCION, CORPUS
    exclusiones = [m for m in merged if (m["diagnostico"] or "") in ("SCHEMA", "ABSTENCION", "CORPUS")]
    faltantes_traza = [m for m in merged if not m["trace_exists"]]
    faltantes_error = [m for m in merged if not m["error_exists"]]

    print(f"Total ids union: {len(ids)}")
    print(f"Aciertos (correcta==1 && trace): {len(aciertos)}")
    print(f"Errores (correcta==0 && trace): {len(errores_list)}")
    print(f"Exclusiones (diagnostico in SCHEMA/ABSTENCION/CORPUS): {len(exclusiones)}")
    print(f"Faltantes traza: {len(faltantes_traza)}, faltantes error: {len(faltantes_error)}")

    # signals to analyse (numeric ones only)
    numeric_keys = []
    sample_items = [m for m in merged if m["senales"]]
    if sample_items:
        for k in senal_keys:
            vals = []
            for it in sample_items:
                v = it["senales"].get(k)
                if isinstance(v, (int, float)):
                    vals.append(v)
                else:
                    # try parse numeric strings
                    try:
                        if v is None or v == "":
                            continue
                        nv = float(v)
                        vals.append(nv)
                    except Exception:
                        continue
            if vals:
                numeric_keys.append(k)

    print(f"Numeric signal keys detected: {numeric_keys}")

    # prepare per-format CSV of threshold candidates
    umbral_rows = []
    for formato in sorted({m["formato"] for m in merged if m["formato"]}):
        fmt_items = [m for m in merged if m["formato"] == formato and m["trace_exists"] and m["correcta"] in (0, 1)]
        if not fmt_items:
            continue
        n_err = sum(1 for m in fmt_items if m["correcta"] == 0)
        n_ok = sum(1 for m in fmt_items if m["correcta"] == 1)
        for key in numeric_keys:
            # collect values
            vals_err = [float(m["senales"].get(key)) for m in fmt_items if (m["correcta"] == 0 and m["senales"].get(key) is not None and str(m["senales"].get(key)) != "")]
            vals_ok = [float(m["senales"].get(key)) for m in fmt_items if (m["correcta"] == 1 and m["senales"].get(key) is not None and str(m["senales"].get(key)) != "")]
            vals_all = [float(m["senales"].get(key)) for m in fmt_items if m["senales"].get(key) is not None and str(m["senales"].get(key)) != ""]
            if not vals_all:
                continue
            mean_ok = mean(vals_ok) if vals_ok else None
            mean_err = mean(vals_err) if vals_err else None
            # decide direction: if mean_ok > mean_err => higher is better, so abstain when value < thresh
            if mean_ok is None or mean_err is None:
                direction = "unknown"
            else:
                direction = "higher_better" if mean_ok > mean_err else "lower_better"
            thresholds = percentile_thresholds(vals_all, PERCENTILES)
            for p, thr in zip(PERCENTILES, thresholds):
                if direction == "higher_better":
                    # abstain when value < thr
                    err_cap = sum(1 for v in vals_err if v < thr)
                    ok_lost = sum(1 for v in vals_ok if v < thr)
                elif direction == "lower_better":
                    err_cap = sum(1 for v in vals_err if v > thr)
                    ok_lost = sum(1 for v in vals_ok if v > thr)
                else:
                    # try both and record the best orientation by net gain
                    err_cap_h = sum(1 for v in vals_err if v < thr)
                    ok_lost_h = sum(1 for v in vals_ok if v < thr)
                    ng_h = 0.5 * (err_cap_h - ok_lost_h)
                    err_cap_l = sum(1 for v in vals_err if v > thr)
                    ok_lost_l = sum(1 for v in vals_ok if v > thr)
                    ng_l = 0.5 * (err_cap_l - ok_lost_l)
                    if ng_h >= ng_l:
                        direction = "higher_better"
                        err_cap, ok_lost = err_cap_h, ok_lost_h
                    else:
                        direction = "lower_better"
                        err_cap, ok_lost = err_cap_l, ok_lost_l
                net_gain = 0.5 * (err_cap - ok_lost)
                umbral_rows.append({
                    "experimento": exp,
                    "formato": formato,
                    "senal": key,
                    "percentil": p,
                    "threshold": thr,
                    "direction": direction,
                    "errors_captured": err_cap,
                    "corrects_lost": ok_lost,
                    "net_gain": net_gain,
                    "n_errors": n_err,
                    "n_corrects": n_ok,
                    "n_samples": len(fmt_items),
                })

    umbral_csv = outdir / f"{exp}_umbral_candidatos.csv"
    if umbral_rows:
        with umbral_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(umbral_rows[0].keys()), lineterminator="\n")
            w.writeheader()
            for r in umbral_rows:
                w.writerow(r)
        print(f"Wrote threshold candidates to {umbral_csv}")
    else:
        print("No numeric signals found or no labeled items to analyse; no threshold CSV written.")

    # write a short summary file in docs/mejoras/resultados_04.md
    summary_path = Path("docs") / "mejoras" / "resultados_04.md"
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(f"# Resultados analisis abstencion - {exp}\n\n")
        f.write(f"Comando ejecutado: python src/evaluacion/analisis_abstencion.py --experimento {exp}\n\n")
        f.write(f"Archivos leidos:\n - {traces_path}\n - {errors_path}\n\n")
        f.write(f"Total ids union: {len(ids)}\n")
        f.write(f"Aciertos (correcta==1 && trace): {len(aciertos)}\n")
        f.write(f"Errores (correcta==0 && trace): {len(errores_list)}\n")
        f.write(f"Exclusiones (diagnostico in SCHEMA/ABSTENCION/CORPUS): {len(exclusiones)}\n")
        f.write(f"Faltantes traza: {len(faltantes_traza)}, faltantes error: {len(faltantes_error)}\n\n")
        if umbral_rows:
            f.write(f"Se generaron {len(umbral_rows)} filas de candidatos de umbrales en {umbral_csv}\n")
            f.write(f"Se genero el CSV por-item en {senales_csv_path}\n")
        else:
            f.write("No se generaron candidatos de umbral (falta de datos numericos o items etiquetados).\n")
        f.write("\nPendientes:\n - Revisar definicion exacta de 'exclusiones' con el equipo (aqui se usaron SCHEMA/ABSTENCION/CORPUS).\n - Elegir a lo sumo 2-3 señales por formato para la Fase B.\n - Ejecutar A/B sobre sample_50 con las reglas propuestas.\n")

    print(f"Summary written to {summary_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
