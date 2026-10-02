"""Genera REPORTE_AVANCE.docx (y el PDF con Word) del entregable del viernes.

Todas las cifras se leen de los artefactos del repo; nada se transcribe a mano:
  - evaluation/generacion/<exp>/reporte.json   (salida de scripts/evaluate.py)
  - evaluation/experiments.csv                 (fecha, encoder, decoder, k, latencia)
  - corpus_manifest.json                       (documentos, areas, fuentes)

Uso (Windows, Word instalado):
  python build_reporte.py --reporte <.../reporte.json> --experiments-csv <.../experiments.csv> --pdf

Dependencias solo de esta herramienta (no van a requirements.txt): python-docx, pymupdf.
El texto editable a mano (observaciones, abstencion, riesgos) esta en las constantes de abajo
y tambien se puede retocar directamente en el .docx antes de exportar el PDF.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

EQUIPO = "Syntax"
INTEGRANTES = "Sofía Morato, Joel David Niño y Santiago Muñoz"
ACENTO = RGBColor(0x1F, 0x3A, 0x5F)
GRIS = "EEF1F5"
FUENTE = "Calibri"
TZ_LOCAL = timezone(timedelta(hours=-5))

AREAS_BANCO = [
    "Derecho constitucional", "Derecho laboral", "Derecho de familia", "Derecho penal",
    "Derecho administrativo", "Derecho comercial y sociedades", "Derecho civil",
    "Derecho tributario", "Derecho procesal",
    "Derecho de los mercados [competencia, consumidor, datos personales y propiedad intelectual]",
]

# Texto editable (se revisa contra la configuracion congelada).
ABSTENCION = (
    "Validación de citas contra el top-10; si quedan campos vacíos tras regenerar, se abstiene. "
    "Regla por señales (score, margen, acuerdo BM25/denso) en evaluación."
)
RIESGOS = [
    ("Tiempo de las 992 preguntas (≈6 h).",
     "{lat_txt} Se congela una sola máquina y configuración para la corrida final y la verificación "
     "en vivo; un Mac M1 tarda ~145 s por pregunta."),
    ("Recuperación a nivel de artículo, cerradas y dependencia del campo área.",
     "En muestra, art_hit@10 ≈ 0,4–0,6 y cerradas {acc} frente a la referencia 0,905. "
     "{area_txt}Se prueban reranker y generation_k, un cambio por experimento."),
    ("Abstención sin calibrar.",
     "{mal} respuestas incorrectas que valdrían 0,5 si se abstuviera; se evalúa una regla simple por "
     "formato, sin sobreajustar a 50 preguntas."),
    ("Entrega del corpus y reproducibilidad.",
     "Falta el empaquetado, el enlace público verificado en ventana privada y la prueba en contenedor "
     "limpio (reproducir.py); la interfaz sigue pendiente."),
]


def num(x: float, dec: int = 2) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


# ---------------------------------------------------------------- datos

def cargar(reporte: Path, csv_path: Path):
    rep = json.loads(reporte.read_text(encoding="utf-8"))
    exp = reporte.parent.name
    with csv_path.open(encoding="utf-8", newline="") as f:
        filas = [r for r in csv.DictReader(f) if r["experimento"] == exp]
    if not filas:
        sys.exit(f"experimento {exp!r} no esta en {csv_path}")
    fila = filas[-1]
    if rep["validacion"]["errores"] != 0:
        sys.exit(f"{exp}: el reporte tiene errores de validacion; no es una corrida completa")
    manifest = json.loads((ROOT / "corpus_manifest.json").read_text(encoding="utf-8"))
    return rep, fila, exp, manifest


def fuentes(manifest) -> str:
    c = Counter()
    for d in manifest["documentos"]:
        f = d["fuente"]
        if "Corte Constitucional" in f:
            c["Relatoría de la Corte Constitucional"] += 1
        elif "Corte Suprema" in f:
            c["Relatoría de la Corte Suprema de Justicia"] += 1
        elif "Senado" in f:
            c["Secretaría del Senado"] += 1
        elif "Avance Juridico" in f:
            c["normogramas (CRA, Colpensiones, DIAN; compilación Avance Jurídico)"] += 1
        elif "Funcion Publica" in f:
            c["Gestor Normativo de Función Pública"] += 1
        elif "Comunidad Andina" in f:
            c["Comunidad Andina"] += 1
        elif "DIAN" in f:
            c["normograma de la DIAN"] += 1
        else:
            c["otras (Régimen Legal de Bogotá, ICBF, RedJurista)"] += 1
    return "; ".join(f"{k} ({v})" for k, v in c.most_common())


# ---------------------------------------------------------------- docx helpers

def fuente(run, size=10, bold=False, color=None, italic=False):
    run.font.name = FUENTE
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def parrafo(doc_or_cell, texto="", size=10, bold=False, color=None, before=0, after=2,
            align=None, italic=False):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), 1.0
    if align:
        p.alignment = align
    if texto:
        fuente(p.add_run(texto), size, bold, color, italic)
    return p


def mixto(p, partes, size=10):
    """partes: lista de (texto, negrita)."""
    for t, b in partes:
        fuente(p.add_run(t), size, b)


def titulo_seccion(doc, texto):
    p = parrafo(doc, texto, size=11, bold=True, color=ACENTO, before=7, after=2)
    pPr = p._p.get_or_add_pPr()
    borde = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "1F3A5F")):
        b.set(qn(f"w:{k}"), v)
    borde.append(b)
    pPr.append(borde)
    return p


def sombrear(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hex_)
    tcPr.append(sh)


def bordes(table):
    tblPr = table._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for lado in ("top", "bottom", "insideH"):
        e = OxmlElement(f"w:{lado}")
        for k, v in (("val", "single"), ("sz", "4"), ("space", "0"), ("color", "B8C0CC")):
            e.set(qn(f"w:{k}"), v)
        b.append(e)
    tblPr.append(b)


def tabla(doc, filas, anchos, encabezado=True, alinear_der=(), negrita_ultima=False, size=9.5):
    t = doc.add_table(rows=len(filas), cols=len(anchos))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    bordes(t)
    for i, fila in enumerate(filas):
        for j, txt in enumerate(fila):
            c = t.cell(i, j)
            c.width = Cm(anchos[j])
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            if j in alinear_der:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            es_enc = encabezado and i == 0
            es_tot = negrita_ultima and i == len(filas) - 1
            fuente(p.add_run(txt), size, bold=es_enc or es_tot,
                   color=ACENTO if es_enc else None)
            if es_enc or es_tot:
                sombrear(c, GRIS)
    return t


# ---------------------------------------------------------------- documento

def construir(rep, fila, exp, manifest, salida: Path, commit: str | None = None,
              lat_sin_carga: float | None = None):
    cer, cit, abst = rep["cerradas"], rep["citas"], rep["abstencion"]
    pts = (cer["puntos"], cit["puntos"], abst["puntos"])
    total = round(sum(pts), 2)
    fecha_utc = datetime.fromisoformat(fila["fecha"])
    fecha = fecha_utc.astimezone(TZ_LOCAL).strftime("%Y-%m-%d")
    docs = manifest["documentos"]
    n_frag = sum(d["n_fragmentos"] or 0 for d in docs)
    cobertas = [a for a in AREAS_BANCO if any(a in d["areas"] for d in docs)]
    sin = [a for a in AREAS_BANCO if a not in cobertas]
    lat = float(fila["latencia_total_ms"]) / 1000
    import re
    m_area = re.search(r"area_boost=([0-9.]+)", fila["notas"])
    boost = float(m_area.group(1)) if m_area else 1.0
    if lat <= 10:
        lat_txt = f"{num(lat, 1)} s/pregunta en la RTX 4090 cumplen el objetivo (<10 s)."
    elif lat_sin_carga:
        lat_txt = (f"{num(lat, 1)} s/pregunta con la GPU compartida con otros experimentos "
                   f"({num(lat_sin_carga, 1)} s sin carga, e14); el objetivo es <10 s y falta medirlo en máquina dedicada.")
    else:
        lat_txt = f"{num(lat, 1)} s/pregunta en la RTX 4090; el objetivo es <10 s."
    area_txt = ("La prioridad por área usa el campo «area» de la pregunta (presente en la muestra); "
                "si las 992 no lo traen, el puntaje será el de la recuperación sin ese refuerzo. "
                if boost > 1 else "")


    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.7)
    s.top_margin, s.bottom_margin = Cm(1.4), Cm(1.4)
    doc.styles["Normal"].font.name = FUENTE
    doc.styles["Normal"].font.size = Pt(10)

    parrafo(doc, "Reporte de avance — Hackathon 2026", size=16, bold=True, color=ACENTO, after=2)
    p = parrafo(doc, after=0)
    mixto(p, [("Equipo: ", True), (EQUIPO, False), ("    Integrantes: ", True), (INTEGRANTES, False)])
    p = parrafo(doc, after=0)
    mixto(p, [("Fecha de la medición: ", True), (fecha, False),
              (f"    Corrida: {exp} (commit {commit or fila['commit'].split('+')[0]})", False)], size=9)

    # 1. Puntaje
    titulo_seccion(doc, "1. Puntaje sobre las preguntas de muestra")
    parrafo(doc, "Resultado de python scripts/evaluate.py --submission <archivo> --split sample.",
            size=8.5, italic=True, after=2)
    tabla(doc, [
        ["Componente", "Puntos obtenidos", "Puntos posibles"],
        ["Exactitud en cerradas", num(pts[0]), "20"],
        ["Calidad de citación", num(pts[1]), "20"],
        ["Abstención calibrada", num(pts[2]), "10"],
        ["Total automático sin RAGAS", num(total), "50"],
    ], [8.0, 4.5, 4.5], alinear_der=(1, 2), negrita_ultima=True)
    p = parrafo(doc, before=3, after=0)
    mixto(p, [("Observaciones. ", True), (
        f"Cerradas {cer['aciertos']}/{cer['n']} ({num(cer['accuracy'], 3)}; referencia del baseline "
        f"{num(cer['referencia'], 3)}). Citación: recall ponderado {num(cit['recall_citas_ponderado'], 3)} "
        f"y {cit['citas_sin_respaldo']} citas sin respaldo en {cit['n_citadas']} emitidas. "
        f"Abstención: {abst['abstuvo_bien'] + abst['abstuvo_de_mas']} abstenciones; "
        f"{abst['respondio_bien']} de {abst['items_evaluados']} respondidas bien. "
        "Con 50 preguntas, una diferencia de 1–2 aciertos no es significativa.", False)])
    ragas = rep.get("correccion_ragas", {})
    if ragas.get("puntos") is not None:
        parrafo(doc, f"Referencia adicional con juez RAGAS: correctness {num(ragas['correctness'], 3)} "
                     f"({num(ragas['puntos'])}/30)" + (f"; medido en {ragas['origen']}" if ragas.get("origen") else "") + ".",
                size=8.5, italic=True, after=0)

    # 2. Corpus
    titulo_seccion(doc, "2. Estado del corpus")
    tabla(doc, [
        ["Métrica", "Valor"],
        ["Documentos incorporados", miles(len(docs))],
        ["Fragmentos indexados", miles(n_frag)],
        ["Áreas del banco con cobertura", f"{len(cobertas)} de {len(AREAS_BANCO)}"],
        ["Áreas del banco sin cobertura", "ninguna" if not sin else "; ".join(sin)],
    ], [8.0, 9.0])
    cnt = Counter(a for d in docs for a in d["areas"])
    top = ", ".join(f"{k.split(' [')[0].replace('Derecho ', '').replace('de los ', '')} {v}"
                    for k, v in cnt.most_common())
    p = parrafo(doc, before=3, after=0)
    mixto(p, [("Fuentes consultadas. ", True), (fuentes(manifest) + ".", False)])
    p = parrafo(doc, after=0)
    mixto(p, [("Documentos por área ", True),
              (f"(un documento puede tener varias): {top}. El corpus tiene desbalance hacia "
               "constitucional (sentencias de la Corte); las áreas de 30 documentos adicionales "
               "son provisionales.", False)])

    # 3. Arquitectura
    titulo_seccion(doc, "3. Arquitectura actual")
    tabla(doc, [
        ["Componente", "Elección"],
        ["Encoder", f"{fila['encoder']} (fp32, FAISS IndexFlatIP, vectores normalizados)"],
        ["Decoder", f"Qwen3-8B, cuantización {fila['cuantizacion']} con llama.cpp; temperature=0, seed=0, "
                    "salida restringida por JSON Schema"],
        ["Estrategia de recuperación",
         f"Híbrida: BM25 (bm25s) + denso, fusión RRF (k=60)"
         + (", más búsqueda por referencia explícita (norma/artículo detectados con citations.py) como candidato extra"
            if '"modo": "on"' in fila["notas"] else "")
         + (f"; prioridad por área del banco (factor {num(boost, 1)}, reordena sin filtrar)" if boost > 1 else "")
         + f"; top-{fila['retrieval_k']} como evidencia, {fila['generation_k']} pasajes al decoder; "
         f"citas validadas contra el top-{fila['retrieval_k']}"],
        ["Segmentación del corpus", f"{fila['version_segmentador']}: un artículo = un fragmento (≤350 palabras, "
                                    "partido por párrafos); sentencias en ventanas de ~350 palabras por sección"],
        ["Mecanismo de abstención", ABSTENCION],
    ], [4.6, 12.4])

    # 4. Riesgos
    titulo_seccion(doc, "4. Riesgos identificados")
    for i, (titulo, cuerpo) in enumerate(RIESGOS, 1):
        p = parrafo(doc, after=1)
        mixto(p, [(f"{i}. {titulo} ", True),
                  (cuerpo.format(lat_txt=lat_txt, area_txt=area_txt, acc=num(cer["accuracy"], 3),
                                 mal=abst["respondio_mal"]), False)])

    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(salida)
    print(f"docx: {salida}  total sin RAGAS = {total} ({exp}, {fecha})")


def exportar_pdf(docx: Path, pdf: Path):
    ps = (
        "$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0; "
        "try { $d = $w.Documents.Open('%s', $false, $true); "
        "$d.ExportAsFixedFormat('%s', 17); $d.Close($false) } finally { $w.Quit() }"
        % (str(docx).replace("'", "''"), str(pdf).replace("'", "''"))
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    import pymupdf  # dep de la herramienta
    n = pymupdf.open(pdf).page_count
    print(f"pdf: {pdf}  paginas = {n}")
    if n != 1:
        sys.exit("ERROR: el PDF no ocupa una pagina; ajustar texto o margenes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reporte", required=True, type=Path)
    ap.add_argument("--experiments-csv", required=True, type=Path)
    ap.add_argument("--salida", type=Path, default=HERE / "REPORTE_AVANCE.docx")
    ap.add_argument("--commit", help="commit a mostrar (por defecto el de experiments.csv)")
    ap.add_argument("--lat-sin-carga", type=float, help="latencia (s) medida sin otros procesos en la GPU")
    ap.add_argument("--pdf", action="store_true", help="exportar a PDF con Word y comprobar 1 pagina")
    a = ap.parse_args()
    rep, fila, exp, manifest = cargar(a.reporte, a.experiments_csv)
    construir(rep, fila, exp, manifest, a.salida, a.commit, a.lat_sin_carga)
    if a.pdf:
        exportar_pdf(a.salida, a.salida.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
