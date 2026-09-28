"""Descarga el contenido original de las fuentes de data/seed_targets.json.

Los `donde_buscar` de la semilla son URLs de busqueda (`?q=...`), no del
documento. Este script resuelve cada objetivo a la URL real del documento con
reglas deterministas y guarda las paginas tal cual llegan (sin limpiar):

  - Codigos, leyes y decretos -> Secretaria del Senado (`basedoc/ley_0080_1993.html`).
    Las normas largas estan partidas en `<base>_pr001.html`, `_pr002.html`...;
    se descargan todas las partes hasta el primer 404.
  - Decision Andina 486 -> PDF oficial de la Comunidad Andina.
  - Sentencias C-, T-, SU- -> Relatoria de la Corte Constitucional
    (`relatoria/2006/C-355-06.htm`; las SU van sin guion: `SU214-16.htm`). La relatoria responde 200 con una pagina
    generica cuando la sentencia no existe; se detecta por contenido.
  - Sentencias de la Corte Suprema (SL, SP, SC), acuerdos y normas que solo estan
    en SUIN-Juriscol (aplicacion Angular sin URL estable) quedan `sin_resolver`
    con la URL de busqueda de la semilla, para descarga manual.

Salidas:
  - data_corpus/raw/<doc_id>/<archivo original>   (local, en .gitignore)
  - data/fuentes_descargadas.json                  (versionado: doc_id, url,
    fecha de consulta, estado, sha256 de lo descargado); es la fuente para
    CORPUS.md y corpus_manifest.json.

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
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import config  # noqa: E402

SEED_PATH = ROOT / "data" / "seed_targets.json"
REGISTRO_PATH = ROOT / "data" / "fuentes_descargadas.json"
CORPUS_MD_PATH = ROOT / "CORPUS.md"

SENADO = "http://www.secretariasenado.gov.co/senado/basedoc/"
RELATORIA_CC = "https://www.corteconstitucional.gov.co/relatoria/"
USER_AGENT = "Mozilla/5.0 (compatible; rag-juridico-syntax/0.1; hackathon LATAM AI Week)"
PAUSA_S = 1.0          # cortesia con los servidores publicos
MAX_PARTES = 300       # tope de paginas _prNNN por norma
REINTENTOS = 3

FUENTE_SENADO = "Secretaria del Senado"
FUENTE_CC = "Relatoria de la Corte Constitucional"
FUENTE_CAN = "Comunidad Andina"
FUENTE_CSJ = "Relatoria de la Corte Suprema de Justicia"
FUENTE_SUIN = "SUIN-Juriscol"

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
    estado: str = "pendiente"  # descargado | no_encontrado | sin_resolver | error
    fecha_consulta: str | None = None
    archivos: list[str] = field(default_factory=list)
    bytes: int = 0
    sha256: str | None = None  # del contenido original concatenado (no del procesado)
    nota: str = ""


def resolver(entrada: dict) -> Objetivo:
    """Traduce una entrada de la semilla a doc_id, titulo, fuente y URL del documento."""
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
                        nota="Corte Suprema: sin URL predecible; descargar a mano", **base)
    doc_id = f"{tipo}_{int(numero)}_{anio}"
    return Objetivo(doc_id, entrada["norma"], FUENTE_SUIN, entrada["donde_buscar"], estado="sin_resolver",
                    nota=f"tipo '{tipo}' sin regla de resolucion", **base)


def descargar(url: str) -> bytes | None:
    """GET con reintentos. Devuelve None si la pagina no existe (404)."""
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for intento in range(1, REINTENTOS + 1):
        try:
            with urllib.request.urlopen(peticion, timeout=60) as r:
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


def partes_senado(url: str) -> list[str]:
    """URLs de las partes siguientes de una norma del Senado: <base>_pr001.html, ..."""
    raiz = url.removesuffix(".html")
    return [f"{raiz}_pr{i:03d}.html" for i in range(1, MAX_PARTES + 1)]


def procesar(obj: Objetivo, forzar: bool) -> None:
    carpeta = config.RAW_DIR / obj.doc_id
    if obj.estado == "sin_resolver":
        return
    if carpeta.is_dir() and any(carpeta.iterdir()) and not forzar:
        obj.estado = "descargado"
        obj.nota = "ya estaba descargado (usar --forzar para repetir)"
        return

    contenido = descargar(obj.url)
    time.sleep(PAUSA_S)
    if contenido is None or (obj.fuente == FUENTE_CC and not es_sentencia_cc(contenido)):
        obj.estado = "no_encontrado"
        obj.nota = f"{obj.url} no existe en {obj.fuente}"
        return

    paginas = [(obj.url, contenido)]
    if obj.fuente == FUENTE_SENADO:
        for url in partes_senado(obj.url):
            parte = descargar(url)
            time.sleep(PAUSA_S)
            if parte is None:
                break
            paginas.append((url, parte))

    carpeta.mkdir(parents=True, exist_ok=True)
    for viejo in carpeta.iterdir():
        viejo.unlink()
    h = hashlib.sha256()
    for url, datos in paginas:
        nombre = url.rsplit("/", 1)[-1]
        (carpeta / nombre).write_bytes(datos)
        h.update(datos)
    obj.estado = "descargado"
    obj.fecha_consulta = dt.date.today().isoformat()
    obj.archivos = [url.rsplit("/", 1)[-1] for url, _ in paginas]
    obj.bytes = sum(len(d) for _, d in paginas)
    obj.sha256 = h.hexdigest()
    obj.nota = ""


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
    objetivos = sorted((resolver(e) for e in semilla), key=lambda o: (-o.items_del_banco, o.doc_id))
    if args.solo:
        objetivos = [o for o in objetivos if o.doc_id in set(args.solo)]
    if args.limite:
        objetivos = objetivos[: args.limite]

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for i, obj in enumerate(objetivos, 1):
        previo = registro.get(obj.doc_id)
        try:
            procesar(obj, args.forzar)
        except Exception as e:  # noqa: BLE001 - se registra y se sigue con el resto
            obj.estado, obj.nota = "error", f"{type(e).__name__}: {e}"
        if obj.nota.startswith("ya estaba") and previo:
            obj = Objetivo(**{**previo, "nota": ""})
        registro[obj.doc_id] = asdict(obj)
        guardar_registro(registro)  # tras cada documento: una interrupcion no pierde lo hecho
        print(f"[{i}/{len(objetivos)}] {obj.estado:<13} {obj.doc_id:<32} "
              f"{len(obj.archivos)} arch. {obj.bytes / 1e6:.1f} MB {obj.nota}")

    resumen: dict[str, int] = {}
    for d in registro.values():
        resumen[d["estado"]] = resumen.get(d["estado"], 0) + 1
    print("Resumen:", ", ".join(f"{k}={v}" for k, v in sorted(resumen.items())))
    print(f"Registro: {REGISTRO_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
