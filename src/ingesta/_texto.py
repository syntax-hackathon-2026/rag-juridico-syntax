"""Utilidades compartidas por los parsers de src/ingesta/parsear_*.py.

- detectar_formato: tipo real de un archivo por sus primeros bytes (no por extension).
- resolver_doc_id: nombre de archivo original -> doc_id (data/mapa_archivos.json).
- limpiar_paginas / limpiar_texto: limpieza estructural del texto extraido.
- guardar_documento: escribe corpus/<doc_id>.txt y actualiza data_corpus/parseo.json.

La limpieza es solo estructural (encabezados, ligaduras, saltos de linea): no
reescribe el contenido normativo, porque el texto de los fragmentos debe ser fiel.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import config  # noqa: E402

FUENTES_PATH = config.ROOT / "data" / "fuentes_descargadas.json"

# --- deteccion de formato -------------------------------------------------

def detectar_formato(ruta: Path) -> str | None:
    """'pdf' | 'rtf' | 'docx' segun los primeros bytes; None si no se reconoce."""
    with ruta.open("rb") as f:
        cabecera = f.read(1024)
    # el estandar PDF admite bytes previos: el marcador puede estar en los primeros 1024
    if b"%PDF-" in cabecera:
        return "pdf"
    inicio = cabecera.lstrip(b"\xef\xbb\xbf \t\r\n")
    if inicio.startswith(b"{\\rtf"):
        return "rtf"
    if inicio.startswith(b"PK\x03\x04"):
        return "docx"  # ZIP: se asume OOXML (Word); pandoc falla si no lo es
    return None


def archivos_de_formato(formatos: set[str], dirs: list[Path]) -> list[tuple[Path, str]]:
    """Archivos en `dirs` cuyo formato REAL esta en `formatos` (ignora la carpeta)."""
    hallados = []
    for d in dirs:
        if not d.is_dir():
            continue
        for ruta in sorted(d.iterdir()):
            if not ruta.is_file() or ruta.name.startswith("."):
                continue
            fmt = detectar_formato(ruta)
            if fmt in formatos:
                hallados.append((ruta, fmt))
    return hallados


# --- doc_id y metadatos ---------------------------------------------------

def _mapa() -> dict[str, str]:
    if not config.MAPA_ARCHIVOS_PATH.is_file():
        return {}
    return json.loads(config.MAPA_ARCHIVOS_PATH.read_text(encoding="utf-8"))


def resolver_doc_id(nombre: str) -> str:
    """doc_id de un archivo original. Falla (no inventa) si no se puede resolver."""
    # macOS puede entregar nombres en NFD; el mapa se escribe en NFC
    nombre = unicodedata.normalize("NFC", nombre)
    mapa = {unicodedata.normalize("NFC", k): v for k, v in _mapa().items()}
    if nombre in mapa:
        return mapa[nombre]
    stem = Path(nombre).stem
    m = re.fullmatch(r"(ley|decreto)_(\d+)_de_(\d{4})", stem, re.I)
    if m:
        return f"{m[1].lower()}_{int(m[2])}_{m[3]}"
    m = re.fullmatch(r"([ctsu]{1,2})-(\d+)-(\d{2})", stem, re.I)
    if m:
        anio = int(m[3])
        anio += 2000 if anio < 50 else 1900
        return f"sentencia_{m[1].lower()}_{int(m[2])}_{anio}"
    raise ValueError(
        f"no se pudo resolver el doc_id de {nombre!r}: agregarlo a "
        f"{config.MAPA_ARCHIVOS_PATH.relative_to(config.ROOT)}"
    )


def metadatos(doc_id: str) -> dict:
    """titulo/fuente/url/areas de fuentes_descargadas.json ({} si el doc_id no esta)."""
    if not FUENTES_PATH.is_file():
        return {}
    for d in json.loads(FUENTES_PATH.read_text(encoding="utf-8"))["documentos"]:
        if d["doc_id"] == doc_id:
            return {k: d.get(k) for k in ("titulo", "fuente", "url", "areas")}
    return {}


# --- limpieza -------------------------------------------------------------

# Estructura que NO debe fusionarse con la linea anterior (la necesita la
# segmentacion por articulo): articulos, titulos, paragrafos, enumeraciones, notas.
_ESTRUCTURA = re.compile(
    r"^(ART[IÍ]CULO|Art[ií]culo|CAP[IÍ]TULO|Cap[ií]tulo|T[IÍ]TULO|T[ií]tulo|SECCI[OÓ]N|"
    r"Secci[oó]n|LIBRO|Libro|PAR[AÁ]GRAFO|Par[aá]grafo|TRANSITORIO|Transitorio|"
    r"\(?[a-zñ]{1,2}\)|\d+[\.\)°º]|[IVXL]+\.|\((Ver|Derogad|Adicionad|Modificad|Declarad|"
    r"Vigencia|Nota|Texto|Inciso|Subrogad|Sustituid)|Nota)"
)
_TERMINAL = re.compile(r"[.:;?!][\"”»')\]]*$")
_HTML_RESIDUO = re.compile(r'"?(PAR[ÁA]GRAFO)\s*-?(\d*)\.p\d*">')
_AVISO_PORTAL = re.compile(
    r"^Los datos publicados tienen prop[oó]sitos exclusivamente informativos\..*no se hace responsable de la vigencia",
    re.I,
)
_BORDE_TABLA = re.compile(r"^[\s|+\-=:]+$")
_RUIDO_FIJO = {"departamento administrativo de la función pública", "eva - gestor normativo"}
_VENTANA_ENCABEZADO = 3
_VENTANA_PIE = 5
_FRACCION_REPETIDA = 0.3


def _normalizar_linea(s: str) -> str:
    """Clave para detectar lineas repetidas: sin espacios extra y con numeros enmascarados."""
    return re.sub(r"\d+", "#", re.sub(r"\s+", " ", s)).strip().lower()


def _quitar_encabezados_y_pies(paginas: list[list[str]]) -> list[list[str]]:
    """Elimina lineas que se repiten en los bordes de >=30 % de las paginas."""
    n = len(paginas)
    cuenta: Counter[str] = Counter()
    for lineas in paginas:
        bordes = lineas[:_VENTANA_ENCABEZADO] + lineas[-_VENTANA_PIE:]
        cuenta.update({_normalizar_linea(l) for l in bordes if l.strip()})
    repetidas = {k for k, c in cuenta.items() if n >= 4 and c / n >= _FRACCION_REPETIDA}
    repetidas |= _RUIDO_FIJO
    salida = []
    for lineas in paginas:
        ultimo = len(lineas) - _VENTANA_PIE
        salida.append([
            l for i, l in enumerate(lineas)
            if not ((i < _VENTANA_ENCABEZADO or i >= ultimo) and _normalizar_linea(l) in repetidas)
            and _normalizar_linea(l) not in _RUIDO_FIJO
        ])
    return salida


def limpiar_texto(texto: str) -> str:
    """Limpieza que aplica a cualquier origen: ligaduras, guiones blandos, residuos HTML."""
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n").replace(" ", " ")
    texto = _HTML_RESIDUO.sub(lambda m: f"{m[1]} {m[2]}. ".replace("  ", " "), texto)
    texto = texto.replace("\u00ad", "")
    lineas = []
    for l in texto.split("\n"):
        l = re.sub(r"[ \t]{2,}", " ", l.rstrip())  # texto justificado deja espacios dobles
        if _AVISO_PORTAL.match(l.strip()):
            continue
        if l.lstrip().startswith(("|", "+")):  # tablas de pandoc: sin bordes ni relleno
            if _BORDE_TABLA.match(l):
                continue
            l = re.sub(r"\s{2,}", " ", l).strip()
            l = re.sub(r"(\| ?)+\|?$", "|", l) if set(l) <= set("| ") else l
        lineas.append(l)
    texto = "\n".join(lineas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip() + "\n"


def limpiar_paginas(paginas: list[str]) -> str:
    """Texto por pagina -> texto corrido: quita encabezados/pies, une lineas partidas.

    Parrafos separados por una linea en blanco. Solo se une una linea con la
    anterior si esta no termina en puntuacion final y la nueva empieza en
    minuscula y no es estructura (articulo, literal, paragrafo...). Ante la duda
    se deja el salto: separar de mas es inocuo, unir de mas altera el texto.
    """
    paginas_l = []
    for p in paginas:
        p = unicodedata.normalize("NFKC", p).replace(" ", " ")
        paginas_l.append([l.strip() for l in p.split("\n") if l.strip()])
    lineas = [l for pag in _quitar_encabezados_y_pies(paginas_l) for l in pag]

    parrafos: list[str] = []
    for l in lineas:
        if parrafos:
            prev = parrafos[-1]
            if prev.endswith(("­", "-")) and l[:1].islower() and not _ESTRUCTURA.match(l):
                # palabra cortada por guion de fin de linea
                parrafos[-1] = prev[:-1] + l
                continue
            if (not _TERMINAL.search(prev) and l[:1].islower()
                    and not _ESTRUCTURA.match(l)):
                parrafos[-1] = f"{prev} {l}"
                continue
        parrafos.append(l)
    texto = "\n\n".join(parrafos).replace("­", "")
    return limpiar_texto(texto)


# --- salida y registro ----------------------------------------------------

def sha256_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _leer_parseo() -> dict:
    if config.PARSEO_PATH.is_file():
        return json.loads(config.PARSEO_PATH.read_text(encoding="utf-8"))
    return {}


def guardar_documento(doc_id: str, texto: str, info: dict) -> Path:
    """Escribe corpus/<doc_id>.txt y registra `info` (+ sha256 del .txt) en parseo.json."""
    config.CORPUS_TEXTOS.mkdir(parents=True, exist_ok=True)
    destino = config.CORPUS_TEXTOS / f"{doc_id}.txt"
    destino.write_text(texto, encoding="utf-8", newline="\n")
    registro = _leer_parseo()
    registro[doc_id] = {
        **metadatos(doc_id),
        **info,
        "archivo_corpus": f"{destino.parent.name}/{destino.name}",
        "n_chars": len(texto),
        "sha256": sha256_texto(texto),
    }
    config.PARSEO_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.PARSEO_PATH.write_text(
        json.dumps(dict(sorted(registro.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destino


# --- CLI comun ------------------------------------------------------------

def ejecutar_cli(descripcion: str, formatos: set[str], extraer) -> int:
    """Recorre data/raw/{pdf,rtf}, extrae los archivos de `formatos` y los guarda.

    `extraer(ruta, formato) -> (texto_limpio, info)`; `info` debe traer
    `metodo_ingesta`. Devuelve el codigo de salida (0 = todo bien).
    """
    import argparse

    ap = argparse.ArgumentParser(description=descripcion)
    ap.add_argument("--input-dir", type=Path, action="append",
                    help="carpeta con originales (repetible); por defecto data/raw/pdf y data/raw/rtf")
    ap.add_argument("--solo", nargs="+", metavar="DOC_ID", help="procesar solo estos doc_id")
    ap.add_argument("--forzar", action="store_true", help="regenerar aunque ya exista corpus/<doc_id>.txt")
    args = ap.parse_args()

    dirs = args.input_dir or [config.RAW_DIR / "pdf", config.RAW_DIR / "rtf"]
    archivos = archivos_de_formato(formatos, dirs)
    if not archivos:
        print(f"No hay archivos {sorted(formatos)} en {[str(d) for d in dirs]}")
        return 1

    # Si un doc_id tiene varias fuentes en distintos formatos, gana la nativa
    # (RTF/DOCX) sobre el PDF: el PDF es una impresion de la misma sentencia.
    preferidas: dict[str, Path] = {}
    for ruta, fmt in archivos_de_formato({"rtf", "docx", "pdf"}, dirs):
        try:
            d = resolver_doc_id(ruta.name)
        except ValueError:
            continue
        if fmt != "pdf":
            preferidas.setdefault(d, ruta)

    vistos: dict[str, Path] = {}
    errores, avisos, hechos, saltados = 0, 0, 0, 0
    for ruta, fmt in archivos:
        try:
            doc_id = resolver_doc_id(ruta.name)
        except ValueError as e:
            print(f"ERROR {ruta.name}: {e}")
            errores += 1
            continue
        if args.solo and doc_id not in args.solo:
            continue
        if fmt == "pdf" and doc_id in preferidas:
            print(f"- {ruta.name}: se omite, {doc_id} se genera desde {preferidas[doc_id].name} (fuente nativa)")
            continue
        if doc_id in vistos:
            print(f"AVISO {ruta.name}: mismo doc_id ({doc_id}) que {vistos[doc_id].name}; se omite")
            avisos += 1
            continue
        vistos[doc_id] = ruta
        destino = config.CORPUS_TEXTOS / f"{doc_id}.txt"
        if destino.is_file() and not args.forzar:
            print(f"= {doc_id} (ya existe; --forzar para regenerar)")
            saltados += 1
            continue
        try:
            texto, info = extraer(ruta, fmt)
        except Exception as e:  # un documento roto no debe tumbar el resto
            print(f"ERROR {ruta.name}: {e}")
            errores += 1
            continue
        info = {
            "archivo_original": f"{ruta.parent.name}/{ruta.name}",
            "formato_real": fmt,
            # carpeta en la que deberia estar segun su formato real (DOCX va con RTF)
            "ubicacion_esperada": "pdf" if fmt == "pdf" else "rtf",
            **info,
        }
        guardar_documento(doc_id, texto, info)
        aviso = f"  AVISO: {info['aviso']}" if info.get("aviso") else ""
        avisos += bool(info.get("aviso"))
        print(f"+ {doc_id:<32} {fmt:<5} {len(texto):>9,} chars{aviso}")
        hechos += 1

    print(f"\n{hechos} escritos, {saltados} ya existian, {avisos} avisos, {errores} errores")
    return 1 if errores or avisos else 0
