"""Genera informe/INFORME_TECNICO.docx con el mismo estilo del reporte del viernes.

Reutiliza los helpers de entregas/viernes/build_reporte.py (tipografia, color, tablas).
Las cifras se transcriben de evaluation/experiments.csv, docs/INDEXACION.md y corpus_manifest.json;
revisarlas contra la corrida final antes de exportar el PDF.

Uso (Windows, Word instalado):  python informe/build_informe.py [--pdf]
Dependencias solo de esta herramienta (no van a requirements.txt): python-docx, pymupdf.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "entregas" / "viernes"))
import build_reporte as br  # noqa: E402
from build_reporte import ACENTO, FUENTE, mixto, parrafo, tabla, titulo_seccion  # noqa: E402

MAX_PAGINAS = 3


def item(doc, n, titulo, cuerpo):
    p = parrafo(doc, after=1)
    mixto(p, [(f"{n}. {titulo} ", True), (cuerpo, False)])


def construir(salida: Path):
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.left_margin = s.right_margin = Cm(1.7)
    s.top_margin, s.bottom_margin = Cm(1.2), Cm(1.2)
    doc.styles["Normal"].font.name = FUENTE
    doc.styles["Normal"].font.size = Pt(10)

    parrafo(doc, "Informe técnico — Hackathon 2026", size=16, bold=True, color=ACENTO, after=2)
    p = parrafo(doc, after=0)
    mixto(p, [("Equipo: ", True), (br.EQUIPO, False), ("    Integrantes: ", True), (br.INTEGRANTES, False)])
    p = parrafo(doc, after=0)
    mixto(p, [("Universidad de los Andes · RAG de derecho colombiano con un modelo abierto de 8.000 millones de parámetros", False)])

    # 1. Arquitectura
    titulo_seccion(doc, "1. Arquitectura del sistema")
    p = parrafo(doc, after=2)
    mixto(p, [("Recorrido de una pregunta. ", True), (
        "La pregunta, sus opciones y su área pasan por cinco etapas. Todas son deterministas, incluido el "
        "modelo que redacta, que corre con temperatura 0 y semilla fija.", False)])
    item(doc, 1, "Ingesta e indexación (se hace antes).",
         "Corpus propio de 1.285 documentos (985 sentencias; el resto, normas y tres documentos no normativos) "
         "descargado de fuentes oficiales, convertido a texto limpio y dividido en 185.234 fragmentos. Cada "
         "fragmento empieza con una línea que nombra su norma (\"Artículo 42 del Código General del Proceso.\") "
         "y guarda su norma, artículo, sección y vigencia.")
    item(doc, 2, "Recuperación.",
         "Si la pregunta nombra una norma o una sentencia, sus fragmentos se añaden como candidatos. Después se "
         "combinan una búsqueda por palabras exactas y una por significado, se da prioridad a los documentos del "
         "área de la pregunta, se dejan detrás las sentencias y las normas derogadas y un segundo modelo reordena "
         "los 20 mejores. Los 10 primeros textos son la evidencia entregada.")
    item(doc, 3, "Generación.",
         "Los 5 primeros textos, con un glosario que une el nombre de cada norma con su número, van al modelo, "
         "que redacta según el formato (cerrada, semiabierta o abierta) en un formato de salida fijo.")
    item(doc, 4, "Verificación de citas.",
         "Cada norma citada se comprueba contra los 10 textos de evidencia (sección 4).")
    item(doc, 5, "Interfaz y reproducción.",
         "Una aplicación web (identidad visual de Software Colombia) usa el mismo código de respuesta que el "
         "proceso por lotes. Un solo comando monta el entorno, el índice, el modelo, las preguntas y la evaluación "
         "en una máquina limpia.")

    # 2. Encoder y decoder
    titulo_seccion(doc, "2. Selección de encoder y decoder")
    tabla(doc, [
        ["Componente", "Modelo y motivo de la elección", "Alternativas descartadas"],
        ["Encoder (vectores para comparar significado)",
         "BAAI/bge-m3 (licencia MIT, 1.024 dimensiones). Es multilingüe, admite textos de hasta 8.192 tokens "
         "(hay artículos que superan los 512 de E5), no exige prefijos y su licencia es compatible con la CC-BY-4.0 del corpus.",
         "jina-embeddings-v3 (licencia no comercial); multilingual-e5-large (límite de 512 tokens)"],
        ["Decoder (redacta la respuesta)",
         "Qwen3-8B cuantizado Q8_0, servido con llama.cpp y sin modo de razonamiento. Lo sugiere el enunciado, "
         "cabe en una GPU de 24 GB, y Q8_0 acertó una cerrada más que Q4_K_M.",
         "Qwen3-4B (plan B por velocidad); modo de razonamiento (más lento, sin ganancia)"],
        ["Reranker (reordena candidatos)",
         "BAAI/bge-reranker-v2-m3 (Apache-2.0) sobre los 20 mejores, fusionado con el orden previo. "
         "Subió 0,41 de 50 puntos en la muestra (citación).",
         "Reordenar 40 candidatos o usar solo el orden del reranker: no mejoraron"],
    ], [3.6, 9.2, 4.2], size=9)
    p = parrafo(doc, before=3, after=0)
    mixto(p, [("Configuración de inferencia. ", True), (
        "Cuantización Q8_0, temperatura 0, semilla 0, una sola petición a la vez y sin caché de prompt: dos "
        "corridas con la misma configuración dan entregas idénticas pregunta por pregunta. En una RTX 4090 tarda "
        "unos 4,4 s por pregunta con el corpus anterior y unos 6,6 s con el reranker y el corpus actual (de 1,2 a 1,8 "
        "horas para las 992). En un Mac M1 de 16 GB serían unos 145 s, por eso la corrida final usa las máquinas del campus.", False)])

    # 3. Recuperación
    titulo_seccion(doc, "3. Estrategia de recuperación")
    item(doc, 1, "Segmentación.",
         "Cada artículo es un fragmento (si pasa de 350 palabras se divide por párrafos); las sentencias se dividen "
         "en tramos de unas 350 palabras sin mezclar secciones. La línea inicial con el nombre de la norma es necesaria: "
         "el evaluador solo da por respaldada una cita si la encuentra en el texto de los 10 primeros pasajes.")
    item(doc, 2, "Índice híbrido.",
         "Búsqueda por palabras (BM25, útil para números de artículo y siglas) y por significado (índice FAISS exacto), "
         "fusionadas por posición (RRF). Se recuperan 10 textos.")
    item(doc, 3, "Composición del corpus.",
         "Las sentencias de las ampliaciones solo se recuperan si la pregunta las nombra, porque sin ese filtro "
         "desplazaban a los artículos. El área de la pregunta prioriza sus documentos, porque el corpus está "
         "desbalanceado hacia lo constitucional (935 documentos frente a 39 de mercados).")
    item(doc, 4, "Medición.",
         "En las 41 preguntas de la muestra con documento de referencia (usado solo para evaluar): el documento correcto "
         "está entre los 10 primeros en el 90 % de los casos (MRR 0,75) y la evidencia respalda el 93 % de las citas esperadas. "
         "Cada mejora se midió y se conservó solo si mejoraba; todas están en evaluation/experiments.csv.")

    # 4. Citas y abstención
    titulo_seccion(doc, "4. Verificación de citas y abstención")
    p = parrafo(doc, after=2)
    mixto(p, [("Citas. ", True), (
        "El sistema nunca emite una cita que no esté en los 10 textos recuperados. Tras generar, extrae las normas "
        "del texto con el mismo extractor del evaluador y las compara con la evidencia, sin usar otro modelo. Si hay "
        "una cita sin respaldo, regenera la respuesta una vez; si persiste, elimina la oración con esa cita y, si "
        "un campo obligatorio queda vacío, se abstiene. Al final añade las referencias de los 10 textos, que siempre "
        "están respaldadas.", False)])
    p = parrafo(doc, after=0)
    mixto(p, [("Abstención. ", True), (
        "Se abstiene si no hay textos, si el modelo no entrega un formato válido o si quitar las citas sin respaldo deja "
        "la respuesta vacía. No se ajustó un umbral de confianza: abstenerse vale 0 en exactitud y 0,5 en calibración, y con "
        "50 preguntas un umbral fino se sobreajustaría.", False)])

    # 5. Resultados
    titulo_seccion(doc, "5. Resultados sobre las preguntas de muestra")
    parrafo(doc, "Resultado de python scripts/evaluate.py --split sample (corridas e24_final y e60; evaluation/experiments.csv).",
            size=8.5, italic=True, after=2)
    tabla(doc, [
        ["Componente", "Corpus anterior (e24_final)", "Corpus actual (e60)", "Posibles"],
        ["Exactitud en cerradas", "16,00 (12 de 15)", "13,33 (10 de 15)", "20"],
        ["Calidad de citación", "17,55", "17,55", "20"],
        ["Abstención calibrada", "8,60", "8,14", "10"],
        ["Total automático sin RAGAS", "42,15", "39,02", "50"],
        ["Corrección de texto libre (juez RAGAS)", "13,20 (0,440)", "por medir", "30"],
    ], [7.0, 4.2, 3.6, 2.2], alinear_der=(1, 2, 3), size=9.5)
    p = parrafo(doc, before=3, after=2)
    mixto(p, [("Lectura. ", True), (
        "La citación (recall ponderado 0,878) no cambió entre corridas y ninguna cita queda sin respaldo. La diferencia en "
        "cerradas son dos preguntas de 15 y no se diagnosticó una causa única; con tan pocas preguntas no es una señal "
        "significativa. Las ampliaciones recientes no se miden en la muestra porque sus normas ya estaban: su efecto esperado "
        "está en las 992. El juez de texto libre varía ±0,03 entre corridas (0,43 a 0,46; la referencia es 0,451).", False)])
    p = parrafo(doc, after=0)
    mixto(p, [("Errores más frecuentes. ", True), (
        "(i) Cerradas que exigen doctrina o jurisprudencia fuera del corpus (#128, #647, #671). (ii) Preguntas que no nombran "
        "su norma: el documento correcto entra en el 90 % de los casos, pero el artículo exacto solo en el 58 %; fallan #247, "
        "#679, #239 y #661. (iii) Texto libre con narrativa larga, donde la norma decisiva no llega a los 10 textos "
        "(la Ley 472 de 1998 en #247).", False)])

    # 6. Limitaciones
    titulo_seccion(doc, "6. Limitaciones")
    lim = [
        ("El modelo de 8B no recuerda números de artículo.",
         "Sin razonamiento depende de que la evidencia esté en los textos. Se midieron y descartaron un planificador de consultas "
         "con el mismo modelo, una consulta por opción y prompts alternativos: ninguno mejoró."),
        ("Texto libre cerca de la línea base.",
         "La corrección ronda 0,44 frente a 0,451 y el juez no es determinista: en algunas corridas no da veredicto en 3 o 4 de 35 "
         "respuestas, que cuentan como cero."),
        ("Fuentes ausentes.",
         "Doctrina, circulares de la SIC y de la Superintendencia Financiera, resoluciones administrativas y sentencias de la Corte "
         "Suprema anteriores a 2016 no están en el corpus."),
        ("Áreas de los documentos.",
         "Las de las ampliaciones las propuso un agente y alimentan la prioridad por área; falta la revisión humana completa."),
        ("Muestra pequeña.",
         "Con 50 preguntas, una diferencia de una o dos no es significativa; se decidió por métricas de recuperación y por no "
         "regresión, no por el total."),
        ("Ampliación dirigida por las preguntas.",
         "El sábado se amplió el corpus mirando solo el texto de las preguntas (nunca respuestas ni fundamentos), con autorización "
         "de la organización; nada se programa por número de pregunta."),
    ]
    for i, (t, c) in enumerate(lim, 1):
        item(doc, i, t, c)

    salida.parent.mkdir(parents=True, exist_ok=True)
    doc.save(salida)
    print(f"docx: {salida}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", type=Path, default=HERE / "INFORME_TECNICO.docx")
    ap.add_argument("--pdf", action="store_true", help="exportar a PDF con Word y comprobar el maximo de paginas")
    a = ap.parse_args()
    construir(a.salida)
    if a.pdf:
        pdf = a.salida.with_suffix(".pdf")
        import subprocess
        ps = ("$w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0; "
              "try { $d = $w.Documents.Open('%s', $false, $true); $d.ExportAsFixedFormat('%s', 17); "
              "$d.Close($false) } finally { $w.Quit() }" % (str(a.salida), str(pdf)))
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
        import pymupdf
        n = pymupdf.open(pdf).page_count
        print(f"pdf: {pdf}  paginas = {n}")
        if n > MAX_PAGINAS:
            sys.exit(f"ERROR: el PDF pasa de {MAX_PAGINAS} paginas")


if __name__ == "__main__":
    main()
