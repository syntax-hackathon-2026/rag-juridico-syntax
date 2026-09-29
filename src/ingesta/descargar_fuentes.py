"""Descarga el contenido original de las fuentes de data/seed_targets.json.

Los `donde_buscar` de la semilla son URLs de busqueda (`?q=...`), no del
documento. Este script resuelve cada objetivo a la URL real del documento con
reglas deterministas y guarda las paginas tal cual llegan (sin limpiar; la
limpieza es de src/ingesta/parsear_html.py):

  - Codigos, leyes y decretos -> Secretaria del Senado (`basedoc/ley_0080_1993.html`).
    Las normas largas estan partidas en `<base>_pr001.html`, `_pr002.html`...;
    se descargan todas las partes hasta el primer 404.
    Lo que no esta en el Senado (leyes anteriores a 1992, decretos) se busca con el
    mismo nombre en los espejos de la compilacion de Avance Juridico de otras
    entidades (normas.cra.gov.co, normativa.colpensiones.gov.co, cancilleria.gov.co), en ese orden.
  - Decision Andina 486 -> PDF oficial de la Comunidad Andina.
  - Sentencias C-, T-, SU- -> Relatoria de la Corte Constitucional
    (`relatoria/2006/C-355-06.htm`; las SU van sin guion: `SU214-16.htm`). La relatoria responde 200 con una pagina
    generica cuando la sentencia no existe; se detecta por contenido.
  - data/fuentes_override.json (versionado, editado a mano) manda sobre las reglas:
    corrige erratas de la semilla y da la URL real de lo que no sigue un patron
    (normas que no estan en el Senado, sentencias de la Corte Suprema, etc.).
  - Lo que ya esta en data/raw/ (descargas manuales en pdf/ o rtf/ mapeadas en
    data/mapa_archivos.json, o una carpeta html/<doc_id>/) no se vuelve a bajar:
    solo se registra.
  - Lo que no tiene regla ni override queda `sin_resolver` con la URL de busqueda
    de la semilla.

Salidas:
  - data/raw/html/<doc_id>/<archivo original>   paginas HTML (todas las partes)
  - data/raw/pdf/<archivo original>             PDF, con su entrada en data/mapa_archivos.json
  - data/fuentes_descargadas.json               (versionado: doc_id, url, fecha de
    consulta, estado, sha256 de lo descargado); es la fuente para CORPUS.md y
    corpus_manifest.json.

Solo stdlib. Es idempotente: salta lo ya descargado salvo con --forzar.

Uso:
    python src/ingesta/descargar_fuentes.py                    # todo
    python src/ingesta/descargar_fuentes.py --solo ley_80_1993 sentencia_c_355_2006
    python src/ingesta/descargar_fuentes.py --limite 10        # los 10 con mas items del banco
    python src/ingesta/descargar_fuentes.py --corpus-md        # solo regenera el inventario de CORPUS.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import config  # noqa: E402

SEED_PATH = ROOT / "data" / "seed_targets.json"
REGISTRO_PATH = ROOT / "data" / "fuentes_descargadas.json"
OVERRIDE_PATH = ROOT / "data" / "fuentes_override.json"
CORPUS_MD_PATH = ROOT / "CORPUS.md"

SENADO = "http://www.secretariasenado.gov.co/senado/basedoc/"
RELATORIA_CC = "https://www.corteconstitucional.gov.co/relatoria/"
USER_AGENT = "Mozilla/5.0 (compatible; rag-juridico-syntax/0.1; hackathon LATAM AI Week)"
PAUSA_S = 1.0          # cortesia con los servidores publicos
MAX_PARTES = 300       # tope de paginas _prNNN por norma
REINTENTOS = 3
TIMEOUT_S = 120        # el Senado y la relatoria tardan; las sentencias pesan varios MB

FUENTE_SENADO = "Secretaria del Senado"
FUENTE_CC = "Relatoria de la Corte Constitucional"
FUENTE_CAN = "Comunidad Andina"
FUENTE_CSJ = "Relatoria de la Corte Suprema de Justicia"
FUENTE_SUIN = "SUIN-Juriscol"
FUENTE_EVA = "Gestor Normativo de Funcion Publica"
# espejos de la compilacion de Avance Juridico (mismo nombre de archivo que el Senado, .htm)
ESPEJOS_AJ = [
    ("Normograma de la CRA (compilacion Avance Juridico)", "https://normas.cra.gov.co/gestor/docs/"),
    ("Normograma de Colpensiones (compilacion Avance Juridico)", "https://normativa.colpensiones.gov.co/colpens/docs/"),
    ("Normograma de Colpensiones (compilacion Avance Juridico)",
     "https://normativa.colpensiones.gov.co/compilacion/docs/"),
    ("Normograma de la Cancilleria (compilacion Avance Juridico)",
     "https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/"),
]

# canonico de citations.py -> (doc_id, titulo, archivo en Senado o URL absoluta)
CODIGOS = {
    "constitucion": ("constitucion_politica_1991", "Constitucion Politica de Colombia de 1991",
                     "constitucion_politica_1991.html"),
    "codigo_general_proceso": ("codigo_general_proceso", "Codigo General del Proceso (Ley 1564 de 2012)",
                               "ley_1564_2012.html"),
    "codigo_sustantivo_trabajo": ("codigo_sustantivo_trabajo", "Codigo Sustantivo del Trabajo",
                                  "codigo_sustantivo_trabajo.html"),
    "estatuto_tributario": ("estatuto_tributario", "Estatuto Tributario (Decreto 624 de 1989)",
                            "estatuto_tributario.html"),
    "decision_andina_486": ("decision_andina_486", "Decision 486 de 2000 de la Comunidad Andina, "
                            "Regimen Comun sobre Propiedad Industrial",
                            "https://www.comunidadandina.org/StaticFiles/DocOf/DEC486.pdf"),
    "estatuto_consumidor": ("estatuto_consumidor", "Estatuto del Consumidor (Ley 1480 de 2011)",
                            "ley_1480_2011.html"),
    "codigo_infancia": ("codigo_infancia", "Codigo de la Infancia y la Adolescencia (Ley 1098 de 2006)",
                        "ley_1098_2006.html"),
    "codigo_disciplinario": ("codigo_disciplinario", "Codigo General Disciplinario (Ley 1952 de 2019)",
                             "ley_1952_2019.html"),
    "codigo_nacional_policia": ("codigo_nacional_policia", "Codigo Nacional de Seguridad y Convivencia "
                                "Ciudadana (Ley 1801 de 2016)", "ley_1801_2016.html"),
}
PREFIJOS_CC = {"C", "T", "SU"}
PREFIJOS_CSJ = {"SL", "SP", "SC"}


@dataclass
class Objetivo:
    doc_id: str
    titulo: str
    fuente: str
    url: str                  # URL del documento (o de busqueda si sin_resolver)
    areas: list[str]
    items_del_banco: int
    canonico: list
    estado: str = "pendiente"  # descargado | no_encontrado | sin_resolver | errata | error
    tipo_fuente: str | None = None  # html | pdf | rtf (carpeta de data/raw/)
    fecha_consulta: str | None = None
    archivos: list[str] = field(default_factory=list)
    bytes: int = 0
    sha256: str | None = None  # del contenido original concatenado (no del procesado)
    nota: str = ""


def cargar_overrides() -> dict[str, dict]:
    if not OVERRIDE_PATH.is_file():
        return {}
    datos = json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
    return {k: v for k, v in datos.items() if not k.startswith("_")}


def resolver(entrada: dict, overrides: dict[str, dict] | None = None) -> Objetivo:
    """Traduce una entrada de la semilla a doc_id, titulo, fuente y URL del documento."""
    obj = _resolver_por_regla(entrada)
    ov = (overrides or {}).get(obj.doc_id)
    if ov:
        # el override puede corregir el doc_id (errata de la semilla) y la fuente/URL
        for campo in ("doc_id", "titulo", "fuente", "url", "estado"):
            if ov.get(campo):
                setattr(obj, campo, ov[campo])
        if obj.estado == "sin_resolver" and ov.get("url"):
            obj.estado = "pendiente"
        obj.nota = ov.get("nota", "")
    return obj


def _resolver_por_regla(entrada: dict) -> Objetivo:
    tipo, numero, anio = entrada["canonico"]
    base = dict(areas=entrada["areas"], items_del_banco=entrada["items_del_banco"],
                canonico=entrada["canonico"])
    if tipo in CODIGOS:
        doc_id, titulo, destino = CODIGOS[tipo]
        if destino.startswith("http"):
            return Objetivo(doc_id, titulo, FUENTE_CAN, destino, **base)
        return Objetivo(doc_id, titulo, FUENTE_SENADO, SENADO + destino, **base)
    if tipo in ("ley", "decreto"):
        n = int(numero)
        doc_id = f"{tipo}_{n}_{anio}"
        titulo = f"{tipo.capitalize()} {n} de {anio}"
        return Objetivo(doc_id, titulo, FUENTE_SENADO, f"{SENADO}{tipo}_{n:04d}_{anio}.html", **base)
    if tipo == "jurisprudencia":
        prefijo, n = numero.split("-")
        doc_id = f"sentencia_{prefijo.lower()}_{int(n)}_{anio}"
        titulo = f"Sentencia {prefijo}-{int(n)} de {anio}"
        if prefijo in PREFIJOS_CC:
            guion = "" if prefijo == "SU" else "-"  # la relatoria publica SU214-16.htm, C-355-06.htm
            url = f"{RELATORIA_CC}{anio}/{prefijo}{guion}{int(n):03d}-{str(anio)[2:]}.htm"
            return Objetivo(doc_id, titulo, FUENTE_CC, url, **base)
        fuente = FUENTE_CSJ if prefijo in PREFIJOS_CSJ else entrada["donde_buscar"]
        return Objetivo(doc_id, titulo, fuente, entrada["donde_buscar"], estado="sin_resolver",
                        nota="Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json", **base)
    doc_id = f"{tipo}_{int(numero)}_{anio}"
    return Objetivo(doc_id, entrada["norma"], FUENTE_SUIN, entrada["donde_buscar"], estado="sin_resolver",
                    nota=f"tipo '{tipo}' sin regla de resolucion; agregar a data/fuentes_override.json", **base)


def descargar(url: str) -> bytes | None:
    """GET con reintentos. Devuelve None si la pagina no existe (404)."""
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for intento in range(1, REINTENTOS + 1):
        try:
            with urllib.request.urlopen(peticion, timeout=TIMEOUT_S) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if intento == REINTENTOS:
                raise
        except (urllib.error.URLError, TimeoutError):
            if intento == REINTENTOS:
                raise
        time.sleep(PAUSA_S * 2 ** intento)
    return None


def es_sentencia_cc(contenido: bytes) -> bool:
    # Las sentencias reales cargan el encabezado de la relatoria; la pagina generica no.
    return b"/relatoria/encabezado.js" in contenido


def es_pagina_valida(obj: Objetivo, contenido: bytes) -> bool:
    """Descarta las paginas de error que responden 200 (relatoria, gestor de Funcion Publica)."""
    if obj.fuente == FUENTE_CC:
        return es_sentencia_cc(contenido)
    if obj.fuente == FUENTE_EVA:
        return b"<title>No disponible" not in contenido
    return True


def partes_senado(url: str) -> list[str]:
    """URLs de las partes siguientes de una norma del Senado o un espejo: <base>_pr001.html, ..."""
    raiz, ext = url.rsplit(".", 1)
    return [f"{raiz}_pr{i:03d}.{ext}" for i in range(1, MAX_PARTES + 1)]


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _leer_mapa() -> dict[str, str]:
    if not config.MAPA_ARCHIVOS_PATH.is_file():
        return {}
    return json.loads(config.MAPA_ARCHIVOS_PATH.read_text(encoding="utf-8"))


def _guardar_mapa(mapa: dict[str, str]) -> None:
    ordenado = dict(sorted(mapa.items(), key=lambda kv: kv[0].lower()))
    config.MAPA_ARCHIVOS_PATH.write_text(json.dumps(ordenado, ensure_ascii=False, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")


def _archivos_en_raw(doc_id: str) -> list[Path]:
    """Originales de un doc_id en data/raw/: carpeta html/<doc_id>/ o PDF/RTF del mapa."""
    carpeta = config.raw_html_dir(doc_id)
    if carpeta.is_dir():
        html = sorted(f for f in carpeta.iterdir() if f.is_file() and not f.name.startswith("."))
        if html:
            return html
    nombres = {_nfc(n) for n, d in _leer_mapa().items() if d == doc_id}
    return sorted(f for sub in ("pdf", "rtf") for f in (config.RAW_DIR / sub).glob("*")
                  if _nfc(f.name) in nombres)


def registrar_existentes(obj: Objetivo, archivos: list[Path]) -> None:
    """Registra en el objetivo los originales que ya estan en data/raw/."""
    h = hashlib.sha256()
    for f in archivos:
        h.update(f.read_bytes())
    obj.estado = "descargado"
    obj.tipo_fuente = archivos[0].parent.name if archivos[0].parent.parent == config.RAW_DIR else "html"
    obj.archivos = [_nfc(f.name) for f in archivos]
    obj.bytes = sum(f.stat().st_size for f in archivos)
    obj.sha256 = h.hexdigest()
    obj.fecha_consulta = dt.date.fromtimestamp(max(f.stat().st_mtime for f in archivos)).isoformat()


def _nombre_archivo(url: str, contenido: bytes) -> str:
    """Nombre del original: el de la URL, o <doc_id>.pdf/.html si la URL no trae uno usable."""
    nombre = urllib.parse.unquote(urllib.parse.urlparse(url).path.rsplit("/", 1)[-1])
    nombre = re.sub(r"[^\w.\-]", "_", nombre)
    es_pdf = contenido[:1024].find(b"%PDF-") >= 0
    ext = ".pdf" if es_pdf else ".html"
    if not nombre or "." not in nombre or (es_pdf and not nombre.lower().endswith(".pdf")):
        return ""
    return nombre if nombre.lower().endswith((".pdf", ".html", ".htm")) else nombre + ext


def guardar_pdf(obj: Objetivo, url: str, contenido: bytes) -> Path:
    nombre = _nombre_archivo(url, contenido) or f"{obj.doc_id}.pdf"
    destino = config.RAW_DIR / "pdf" / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    mapa = _leer_mapa()
    previo = mapa.get(nombre)
    if previo and previo != obj.doc_id:
        raise RuntimeError(f"{nombre} ya esta mapeado a {previo} en mapa_archivos.json")
    mapa[nombre] = obj.doc_id
    _guardar_mapa(mapa)
    return destino


def procesar(obj: Objetivo, forzar: bool) -> None:
    existentes = _archivos_en_raw(obj.doc_id)
    if existentes and (not forzar or obj.estado in ("sin_resolver", "no_encontrado", "errata")):
        registrar_existentes(obj, existentes)  # descarga manual o previa: solo se registra
        obj.nota = "ya estaba en data/raw/ (usar --forzar para repetir)"
        return
    if obj.estado in ("sin_resolver", "no_encontrado", "errata"):
        return

    contenido = descargar(obj.url)
    time.sleep(PAUSA_S)
    if contenido is None and obj.fuente == FUENTE_SENADO:
        contenido = buscar_en_espejos(obj)
    if contenido is None or not es_pagina_valida(obj, contenido):
        obj.estado = "no_encontrado"
        obj.nota = f"{obj.url} no existe en {obj.fuente}"
        return

    if contenido[:1024].find(b"%PDF-") >= 0:
        destino = guardar_pdf(obj, obj.url, contenido)
        registrar_existentes(obj, [destino])
        obj.fecha_consulta = dt.date.today().isoformat()
        return

    paginas = [(obj.url, contenido)]
    if obj.fuente == FUENTE_SENADO or obj.fuente in {f for f, _ in ESPEJOS_AJ}:
        for url in partes_senado(obj.url):
            parte = descargar(url)
            time.sleep(PAUSA_S)
            if parte is None:
                break
            paginas.append((url, parte))

    guardar_html(obj, paginas)


def buscar_en_espejos(obj: Objetivo) -> bytes | None:
    """Norma ausente del Senado: la busca en los espejos; si aparece, cambia fuente y URL."""
    nombre = obj.url.rsplit("/", 1)[-1].removesuffix(".html") + ".htm"
    for fuente, base in ESPEJOS_AJ:
        contenido = descargar(base + nombre)
        time.sleep(PAUSA_S)
        if contenido is not None:
            obj.fuente, obj.url = fuente, base + nombre
            return contenido
    return None


def guardar_html(obj: Objetivo, paginas: list[tuple[str, bytes]]) -> None:
    carpeta = config.raw_html_dir(obj.doc_id)
    if carpeta.is_dir():  # --forzar: reemplaza la version previa
        for viejo in carpeta.iterdir():
            viejo.unlink()
    carpeta.mkdir(parents=True, exist_ok=True)
    for i, (url, datos) in enumerate(paginas):
        nombre = _nombre_archivo(url, datos) or f"{obj.doc_id}_{i:03d}.html"
        (carpeta / nombre).write_bytes(datos)
    registrar_existentes(obj, sorted(f for f in carpeta.iterdir() if f.is_file()))
    obj.fecha_consulta = dt.date.today().isoformat()


def cargar_registro() -> dict[str, dict]:
    if not REGISTRO_PATH.is_file():
        return {}
    with REGISTRO_PATH.open(encoding="utf-8") as f:
        return {d["doc_id"]: d for d in json.load(f)["documentos"]}


def guardar_registro(registro: dict[str, dict]) -> None:
    docs = sorted(registro.values(), key=lambda d: (-d["items_del_banco"], d["doc_id"]))
    salida = {"semilla": SEED_PATH.relative_to(ROOT).as_posix(), "documentos": docs}
    with REGISTRO_PATH.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
        f.write("\n")


# --- Inventario de CORPUS.md -------------------------------------------------

INICIO_INV = "<!-- inventario:inicio (generado por src/ingesta/descargar_fuentes.py --corpus-md) -->"
FIN_INV = "<!-- inventario:fin -->"


def area_corta(area: str) -> str:
    return area.split(" [")[0].removeprefix("Derecho ").removeprefix("de los ").removeprefix("de ").capitalize()


def tabla_inventario(registro: dict[str, dict]) -> str:
    filas = [
        "| doc_id | Título | Fuente | URL | Fecha de consulta | Artículos | Fragmentos | Áreas |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for d in sorted(registro.values(), key=lambda d: (-d["items_del_banco"], d["doc_id"])):
        if d["estado"] != "descargado":
            continue
        areas = ", ".join(sorted({area_corta(a) for a in d["areas"]}))
        filas.append(f"| `{d['doc_id']}` | {d['titulo']} | {d['fuente']} | [enlace]({d['url']}) "
                     f"| {d['fecha_consulta']} | — | — | {areas} |")
    pendientes = [d for d in registro.values() if d["estado"] != "descargado"]
    lineas = [INICIO_INV, "", *filas, ""]
    if pendientes:
        lineas += [f"**Pendientes de descarga ({len(pendientes)}).** Objetivos de "
                   "`data/seed_targets.json` que el script no pudo descargar; el detalle "
                   "está en `data/fuentes_descargadas.json`.", "",
                   "| doc_id | Estado | Motivo |", "|---|---|---|"]
        for d in sorted(pendientes, key=lambda d: (d["estado"], -d["items_del_banco"], d["doc_id"])):
            lineas.append(f"| `{d['doc_id']}` | {d['estado']} | {d['nota']} |")
        lineas.append("")
    lineas.append(FIN_INV)
    return "\n".join(lineas)


def actualizar_corpus_md(registro: dict[str, dict]) -> None:
    texto = CORPUS_MD_PATH.read_text(encoding="utf-8")
    bloque = tabla_inventario(registro)
    if INICIO_INV in texto:
        antes, resto = texto.split(INICIO_INV, 1)
        _, despues = resto.split(FIN_INV, 1)
        texto = antes + bloque + despues
    else:
        # Primera vez: reemplaza la tabla vacia de la plantilla en la seccion 1.
        vacia = ("| doc_id | Título | Fuente | URL | Fecha de consulta | Artículos | Fragmentos | Áreas |\n"
                 "|---|---|---|---|---|---:|---:|---|\n| | | | | | | | |")
        if vacia not in texto:
            raise SystemExit("No encuentro la tabla de inventario de CORPUS.md ni los marcadores.")
        texto = texto.replace(vacia, bloque, 1)
    with CORPUS_MD_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--solo", nargs="+", metavar="DOC_ID", help="descargar solo estos doc_id")
    ap.add_argument("--limite", type=int, help="solo los N objetivos con mas items del banco")
    ap.add_argument("--forzar", action="store_true", help="volver a descargar lo ya descargado")
    ap.add_argument("--corpus-md", action="store_true",
                    help="no descargar; regenerar el inventario de CORPUS.md desde el registro")
    args = ap.parse_args()

    registro = cargar_registro()
    if args.corpus_md:
        actualizar_corpus_md(registro)
        print(f"CORPUS.md actualizado ({sum(d['estado'] == 'descargado' for d in registro.values())} documentos)")
        return 0

    with SEED_PATH.open(encoding="utf-8") as f:
        semilla = json.load(f)["documentos"]
    overrides = cargar_overrides()
    objetivos = sorted((resolver(e, overrides) for e in semilla), key=lambda o: (-o.items_del_banco, o.doc_id))
    if not (args.solo or args.limite):
        # un override puede renombrar un doc_id (errata de la semilla): se borra la clave vieja
        vigentes = {o.doc_id for o in objetivos}
        registro = {k: v for k, v in registro.items() if k in vigentes}
    if args.solo:
        objetivos = [o for o in objetivos if o.doc_id in set(args.solo)]
    if args.limite:
        objetivos = objetivos[: args.limite]

    for i, obj in enumerate(objetivos, 1):
        previo = registro.get(obj.doc_id)
        try:
            procesar(obj, args.forzar)
        except Exception as e:  # noqa: BLE001 - se registra y se sigue con el resto
            obj.estado, obj.nota = "error", f"{type(e).__name__}: {e}"
        if previo and previo.get("sha256") == obj.sha256 and previo.get("fecha_consulta"):
            obj.fecha_consulta = previo["fecha_consulta"]  # mismo contenido: fecha real de la descarga
        registro[obj.doc_id] = asdict(obj)
        guardar_registro(registro)  # tras cada documento: una interrupcion no pierde lo hecho
        print(f"[{i}/{len(objetivos)}] {obj.estado:<13} {obj.doc_id:<32} "
              f"{len(obj.archivos)} arch. {obj.bytes / 1e6:.1f} MB {obj.nota}", flush=True)

    resumen: dict[str, int] = {}
    for d in registro.values():
        resumen[d["estado"]] = resumen.get(d["estado"], 0) + 1
    print("Resumen:", ", ".join(f"{k}={v}" for k, v in sorted(resumen.items())))
    print(f"Registro: {REGISTRO_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
