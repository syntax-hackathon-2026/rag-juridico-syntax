"""HTML -> texto limpio en data_corpus/corpus/<doc_id>.txt.

    python src/ingesta/parsear_html.py [--input-dir DIR] [--solo DOC_ID ...] [--forzar]

Lee data/raw/html/<doc_id>/ (lo que baja src/ingesta/descargar_fuentes.py): el nombre
de la carpeta es el doc_id. Un extractor por fuente, elegido por el contenido:

  - Compilacion de Avance Juridico (Secretaria del Senado y sus espejos en otras
    entidades, p. ej. normas.cra.gov.co): une las partes (<base>.html, <base>_pr001.html, ...) en
    orden y toma solo el cuerpo de la norma. Quita el indice de navegacion, las cajas
    "Jurisprudencia Vigencia" (vacias, las llena JavaScript), el pie de Avance
    Juridico y la sentencia de control que a veces viene pegada al final tras
    `<NOTA DEL EDITOR ...>`. Conserva las notas cortas en linea (`<Articulo
    modificado por ...>`, `<Aparte tachado INEXEQUIBLE>`): son hechos de vigencia.
  - Relatoria de la Corte Constitucional (HTML exportado de Word): todo el cuerpo,
    incluidas las notas al pie (son parte de la sentencia).
  - Cualquier otra pagina: el contenedor con mas texto, sin navegacion ni scripts.

Un bloque (p, h*, li, fila de tabla) = un parrafo, separados por linea en blanco; al
final se aplica la misma limpieza que a los PDF/RTF (_texto.limpiar_texto). Si el
doc_id ya tiene corpus/<doc_id>.txt (p. ej. de un PDF/RTF manual) se salta salvo
con --forzar.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bs4 import BeautifulSoup, Tag  # noqa: E402

import _texto  # noqa: E402
from _texto import config  # noqa: E402

METODO = "parser HTML (BeautifulSoup) + limpieza de navegacion y notas editoriales"
MIN_CHARS = 2000

_BLOQUES = ("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "pre", "blockquote")
_ESPACIOS = re.compile(r"[ \t\r\n\f\v ]+")
_BR = "\x00"
_ARTICULO = re.compile(r"^ART[IÍ]CULO\s+(\d+)", re.I)
_PARTE_SENADO = re.compile(r"_pr(\d{3})\.html?$", re.I)
_CORTE_SENADO = re.compile(
    r"^(<\s*NOTA DEL EDITOR|Las notas de vigencia, concordancias, notas del editor|"
    r"Disposiciones analizadas por Avance Jur[ií]dico)", re.I)
_NAV_SENADO = re.compile(r"^(Anterior\s*\|\s*Siguiente|Inicio|Artículo)$", re.I)
_SENTENCIA_PEGADA = re.compile(r"^SENTENCIA\s+[CTSU]{1,2}\s*-\s*\d", re.I)


# --- lectura ------------------------------------------------------------------

def decodificar(datos: bytes) -> str:
    """Bytes -> str segun el <meta charset>; ISO-8859-1 se lee como cp1252 (superconjunto)."""
    m = re.search(rb'charset=["\']?([\w-]+)', datos[:4096], re.I)
    declarado = m[1].decode("ascii").lower() if m else ""
    if declarado in ("iso-8859-1", "latin-1", "latin1", "windows-1252", "cp1252"):
        return datos.decode("cp1252", errors="replace")
    try:
        return datos.decode(declarado or "utf-8")
    except (LookupError, UnicodeDecodeError):
        try:
            return datos.decode("utf-8")
        except UnicodeDecodeError:
            return datos.decode("cp1252", errors="replace")


def ordenar_partes(archivos: list[Path]) -> list[Path]:
    """Pagina base primero y luego _pr001, _pr002... (el orden alfabetico las invierte)."""
    def clave(f: Path) -> tuple[int, str]:
        m = _PARTE_SENADO.search(f.name)
        return (int(m[1]) if m else 0, f.name)
    return sorted(archivos, key=clave)


def detectar_fuente(html: str) -> str:
    if 'id="aj_data"' in html or 'class="bookmarkaj"' in html:
        return "avance_juridico"
    if "/relatoria/encabezado.js" in html or "corteconstitucional" in html[:5000].lower():
        return "relatoria_cc"
    return "generico"


# --- bloques -> parrafos --------------------------------------------------------

def _texto_bloque(el: Tag) -> str:
    if el.name == "tr":
        celdas = [_ESPACIOS.sub(" ", c.get_text(" ")).strip() for c in el.find_all(["td", "th"])]
        return " | ".join(c for c in celdas if c)
    # en HTML los saltos del codigo fuente son espacio (Word corta las lineas a ~75
    # columnas); solo <br> es salto real
    for br in el.find_all("br"):
        br.replace_with(_BR)
    lineas = [_ESPACIOS.sub(" ", l).strip() for l in el.get_text("").split(_BR)]
    return "\n".join(l for l in lineas if l)


def parrafos(raiz: Tag) -> list[str]:
    """Texto de los bloques de `raiz` en orden de documento, sin repetir bloques anidados."""
    salida = []
    for el in raiz.find_all(_BLOQUES):
        if el.find_parent(_BLOQUES) is not None:  # p dentro de li/tr/p: ya lo cubre el padre
            continue
        texto = _texto_bloque(el)
        if texto:
            salida.append(texto)
    return salida


def _quitar(raiz: Tag, *selectores: str) -> None:
    for sel in selectores:
        for el in raiz.select(sel):
            el.decompose()


# --- extractores por fuente ------------------------------------------------------

def extraer_avance_juridico(html: str) -> list[str]:
    sopa = BeautifulSoup(html, "lxml")
    cuerpos = sopa.find_all("div", id="aj_data")
    # Senado: el aj_data interno trae solo la norma; espejo de la CRA: div.panel-documento
    raiz = cuerpos[-1] if cuerpos else (sopa.find("div", class_="panel-documento") or sopa.body)
    _quitar(raiz, "script", "style", "#selector_aj", "#imprimir", "#logo_aj", "#update_date",
            "a.hlk_inicio", "a.caja_vja_encabezado", "table[class^=caja_vja]", "select")
    bloques = []
    for p in parrafos(raiz):
        if _CORTE_SENADO.match(p):
            # la sentencia de control pegada empieza con "SENTENCIA C-748-11." justo antes
            while bloques and _SENTENCIA_PEGADA.match(bloques[-1]):
                bloques.pop()
            break
        if _NAV_SENADO.match(p):
            continue
        bloques.append(p)
    return bloques


def extraer_relatoria_cc(html: str) -> list[str]:
    sopa = BeautifulSoup(html, "lxml")
    raiz = sopa.find("div", class_="amplia") or sopa.body or sopa
    _quitar(raiz, "script", "style")
    return parrafos(raiz)


def extraer_generico(html: str) -> list[str]:
    sopa = BeautifulSoup(html, "lxml")
    _quitar(sopa, "script", "style", "noscript", "nav", "header", "footer", "form", "iframe", "select")
    candidatos = sopa.find_all(["main", "article", "div", "td", "body"])
    if not candidatos:
        return parrafos(sopa)
    # el contenedor mas profundo que concentra el grueso del texto (>= 80 % del maximo)
    largo = {id(c): len(c.get_text(" ", strip=True)) for c in candidatos}
    maximo = max(largo.values())
    grandes = [c for c in candidatos if largo[id(c)] >= 0.8 * maximo]
    raiz = min(grandes, key=lambda c: largo[id(c)])
    return parrafos(raiz)


EXTRACTORES = {"avance_juridico": extraer_avance_juridico, "relatoria_cc": extraer_relatoria_cc, "generico": extraer_generico}


# --- documento -------------------------------------------------------------------

def articulos_detectados(bloques: list[str]) -> list[int]:
    return [int(m[1]) for b in bloques if (m := _ARTICULO.match(b))]


def extraer_documento(carpeta: Path) -> tuple[str, dict]:
    archivos = ordenar_partes([f for f in carpeta.iterdir()
                               if f.is_file() and f.suffix.lower() in (".html", ".htm")])
    if not archivos:
        raise RuntimeError("carpeta sin archivos .html/.htm")
    paginas = [decodificar(f.read_bytes()) for f in archivos]
    fuente = detectar_fuente(paginas[0])
    bloques = [b for html in paginas for b in EXTRACTORES[fuente](html)]
    texto = _texto.limpiar_texto("\n\n".join(bloques))

    arts = articulos_detectados(bloques)
    info = {
        "metodo_ingesta": METODO,
        "extractor": fuente,
        "n_partes": len(archivos),
        "n_articulos_detectados": len(arts),
    }
    avisos = []
    if len(texto) < MIN_CHARS:
        avisos.append(f"texto muy corto ({len(texto)} chars)")
    if fuente == "avance_juridico":
        if not arts:
            avisos.append("norma sin articulos detectados")
        else:
            # la numeracion admite repeticiones (2o. y 2A, articulos transitorios) pero no huecos grandes
            saltos = [(a, b) for a, b in zip(arts, arts[1:]) if b > a + 5]
            if saltos:
                avisos.append(f"saltos en la numeracion de articulos: {saltos[:3]} (falta una parte _prNNN?)")
    if avisos:
        info["aviso"] = "; ".join(avisos)
    return texto, info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input-dir", type=Path, default=config.RAW_HTML_DIR,
                    help="carpeta con una subcarpeta por doc_id (por defecto data/raw/html)")
    ap.add_argument("--solo", nargs="+", metavar="DOC_ID", help="procesar solo estos doc_id")
    ap.add_argument("--forzar", action="store_true", help="regenerar aunque ya exista corpus/<doc_id>.txt")
    args = ap.parse_args()

    carpetas = sorted(d for d in args.input_dir.iterdir() if d.is_dir()) if args.input_dir.is_dir() else []
    if args.solo:
        carpetas = [d for d in carpetas if d.name in set(args.solo)]
    if not carpetas:
        print(f"No hay carpetas <doc_id>/ en {args.input_dir}")
        return 1

    errores, avisos, hechos, saltados = 0, 0, 0, 0
    for carpeta in carpetas:
        doc_id = carpeta.name
        destino = config.CORPUS_TEXTOS / f"{doc_id}.txt"
        if destino.is_file() and not args.forzar:
            print(f"= {doc_id} (ya existe; --forzar para regenerar)")
            saltados += 1
            continue
        try:
            texto, info = extraer_documento(carpeta)
        except Exception as e:  # un documento roto no debe tumbar el resto
            print(f"ERROR {doc_id}: {e}")
            errores += 1
            continue
        info = {"archivo_original": f"html/{doc_id}/", "formato_real": "html",
                "ubicacion_esperada": "html", **info}
        _texto.guardar_documento(doc_id, texto, info)
        aviso = f"  AVISO: {info['aviso']}" if info.get("aviso") else ""
        avisos += bool(info.get("aviso"))
        print(f"+ {doc_id:<32} {info['extractor']:<12} {len(texto):>9,} chars "
              f"{info['n_articulos_detectados']:>4} arts{aviso}")
        hechos += 1

    print(f"\n{hechos} escritos, {saltados} ya existian, {avisos} avisos, {errores} errores")
    return 1 if errores or avisos else 0


if __name__ == "__main__":
    raise SystemExit(main())
