"""Segmenta data_corpus/corpus/<doc_id>.txt en fragmentos -> data_corpus/indice/chunks.jsonl.

    python src/indexacion/segmentar.py                    # todo el corpus
    python src/indexacion/segmentar.py --solo ley_80_1993 codigo_civil   # solo imprime la tabla
    python src/indexacion/segmentar.py --mostrar codigo_general_proceso 42

Unidad de fragmento:
  - Normas (constitucion, codigos, leyes, decretos, Decision 486): un articulo = un
    fragmento; si pasa de MAX_PALABRAS se parte por parrafos (y un parrafo enorme por
    oraciones) en partes 1/n, 2/n... sin solapamiento. El texto previo al primer
    articulo va como fragmento(s) con articulo=null.
  - Sentencias: ventanas de ~MAX_PALABRAS con parrafos enteros, 1 parrafo de
    solapamiento si es corto, sin cruzar secciones (sintesis, antecedentes,
    consideraciones, resuelve, salvamento, aclaracion).

Cada fragmento lleva `texto = cabecera + "\\n" + corpus[inicio:fin]`: la cabecera
citable (ver cabeceras.py) seguida del texto literal. Eso va tal cual a
pasajes_recuperados.texto. `retrieval_text` agrega titulo, siglas y seccion para la
busqueda. La invariante se comprueba al escribir y el script sale con 1 si falla.

Los articulos detectados (numeros base: 38A y 12-1 cuentan con 38 y 12; sin
transitorios) se comparan con `n_articulos` del manifest; una diferencia > 5 % queda
como aviso en la tabla y en resumen_indice.json. El manifest no es infalible: en
normas modificatorias a veces cuenta los articulos transcritos (Ley 50/1990).

Normas modificatorias: tras un parrafo que termina en ":" ("...quedara asi:") o un
encabezado entre comillas se entra en modo cita; los "ARTICULO N" transcritos quedan
dentro del articulo propio hasta que la numeracion vuelve a la de la norma.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cabeceras  # noqa: E402
from cabeceras import config, citations  # noqa: E402

VERSION = "seg-v1"
MAX_PALABRAS = 350  # objetivo por fragmento
MAX_DURO = 450  # un parrafo mas largo que esto se parte por oraciones
SOLAPE_MAX = 120  # palabras maximas del parrafo que se repite entre ventanas de sentencia
TOLERANCIA_ARTICULOS = 0.05

# --- deteccion -----------------------------------------------------------------

# "ARTICULO 1o. X", "Articulo 1°. X", "ARTICULO 1 ORIGEN", "Articulo 1.- X",
# "ARTICULO 1.1.1.1. X", "ARTICULO 12-1. X", "ARTICULO 5A. X", "ARTICULO TRANSITORIO 3."
# Despues del numero: puntuacion, fin, o espacio + mayuscula (asi "Articulo 42 del
# Codigo..." al inicio de un parrafo de notas no cuenta como encabezado).
_ARTICULO = re.compile(
    r"""^(?P<comilla>[“"«'‘])?\s*(?:ART[IÍ]CULO|Art[ií]culo)\s+
    (?P<num>TRANSITORIO(?:\s+\d+)?
      |\d+(?:\.\d+)*(?:-\d+)?(?:[A-Z]|\s[A-Z](?=\.))?(?:\s+[Bb][Ii][Ss])?)
    (?:\s*[°ºo](?![a-záéíóúñ]))?
    (?=\s*(?:[.\-–:,;]|$)|\s+[A-ZÁÉÍÓÚÑ<])""",
    re.X,
)
_ENCABEZADO_SECCION = re.compile(
    r"^(LIBRO|PARTE|T[IÍ]TULO|CAP[IÍ]TULO|SECCI[OÓ]N|Libro|Parte|T[ií]tulo|Cap[ií]tulo|Secci[oó]n)"
    r"(\s+([IVXLCDM]+|\d+|[A-ZÁÉÍÓÚ][a-záéíóúA-ZÁÉÍÓÚ]+))?\.?\s*[.:\-–]?"
)
_NIVELES = {"libro": 0, "parte": 1, "titulo": 2, "capitulo": 3, "seccion": 4}
# "...el cual quedara asi:", "...con el siguiente texto:" al final de un parrafo
_FORMULA_REFORMA = re.compile(
    r"(?i)(quedar[aá]n?\s+as[ií]|(el|los)\s+siguientes?\s*(texto|art[ií]culos?)?|as[ií])\s*:\s*[\"”»']?\s*$")
_ORACION = re.compile(r"(?<=[.;:])\s+(?=[A-ZÁÉÍÓÚÑ0-9“\"(¿¡-])")

_SECCIONES_SENTENCIA = [
    # "SALVAMENTO DE VOTO DEL MAGISTRADO...", no la anotacion de firma "CON SALVAMENTO DE VOTO"
    # ni un subtitulo como "2. Aclaracion previa"
    ("salvamento", re.compile(r"^salvamento (parcial )?de voto")),
    ("aclaracion", re.compile(r"^aclaracion (parcial )?de voto")),
    ("resuelve", re.compile(r"^(resuelve|decide|(\w+\.\s*)?decision\b|(\w+\.\s*)?fallo\b)")),
    ("consideraciones", re.compile(
        r"^((\w+\.\s*)?consideraciones|(\w+\.\s*)?fundamentos( juridicos)?\b|"
        r"(\w+\.\s*)?consideraciones y fundamentos)")),
    ("antecedentes", re.compile(
        r"^((\w+\.\s*)?(antecedentes|norma demandada|texto de la norma|la demanda|demanda\b|"
        r"intervenciones|concepto del? (la )?(procurador|procuradora|ministerio publico)|"
        r"hechos|pruebas|actuacion|decisiones? (judiciales )?objeto de revision|"
        r"sentencias? objeto de revision|la sentencia impugnada|el recurso))")),
]


# --- estructuras -----------------------------------------------------------------

@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    tipo: str
    numero: str | None
    anio: str | None
    articulo: str | None
    parte: int
    n_partes: int
    seccion: str | None
    vigencia: str | None
    canonico: list
    cabecera: str
    inicio: int
    fin: int
    texto: str
    retrieval_text: str
    url: str | None
    fuente: str | None
    n_palabras: int


@dataclass
class Meta:
    doc_id: str
    canon: tuple
    tipo: str
    numero: str | None
    anio: str | None
    titulo: str
    url: str | None
    fuente: str | None
    siglas: list[str] = field(default_factory=list)


# --- utilidades de texto ----------------------------------------------------------

def parrafos(texto: str) -> list[tuple[int, int]]:
    """Spans (inicio, fin) de los parrafos: bloques separados por linea en blanco, sin bordes."""
    spans = []
    for m in re.finditer(r"(?:[^\n]|\n(?![ \t]*\n))+", texto):
        seg = m.group()
        if not seg.strip():
            continue
        ini = m.start() + (len(seg) - len(seg.lstrip()))
        spans.append((ini, m.start() + len(seg.rstrip())))
    return spans


def palabras(texto: str, span: tuple[int, int]) -> int:
    return len(texto[span[0]:span[1]].split())


def unidades(texto: str, spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Parrafos, partiendo por oraciones (y en ultimo caso por palabras) los muy largos."""
    salida = []
    for s, e in spans:
        if palabras(texto, (s, e)) <= MAX_DURO:
            salida.append((s, e))
            continue
        cortes = [s] + [s + m.end() for m in _ORACION.finditer(texto[s:e])] + [e]
        for a, b in zip(cortes, cortes[1:]):
            b_limpio = a + len(texto[a:b].rstrip())
            if b_limpio <= a:
                continue
            if palabras(texto, (a, b_limpio)) <= MAX_DURO:
                salida.append((a, b_limpio))
                continue
            # oracion gigantesca (tablas): ventanas de MAX_PALABRAS palabras
            toks = list(re.finditer(r"\S+", texto[a:b_limpio]))
            for i in range(0, len(toks), MAX_PALABRAS):
                grupo = toks[i:i + MAX_PALABRAS]
                salida.append((a + grupo[0].start(), a + grupo[-1].end()))
    return salida


def empaquetar(texto: str, units: list[tuple[int, int]], solape: bool = False) -> list[tuple[int, int]]:
    """Agrupa unidades consecutivas en spans de hasta MAX_PALABRAS palabras."""
    grupos: list[list[tuple[int, int]]] = []
    actual: list[tuple[int, int]] = []
    n = 0
    for u in units:
        w = palabras(texto, u)
        if actual and n + w > MAX_PALABRAS:
            grupos.append(actual)
            ultimo = actual[-1]
            if solape and len(actual) > 1 and palabras(texto, ultimo) <= SOLAPE_MAX:
                actual, n = [ultimo], palabras(texto, ultimo)
            else:
                actual, n = [], 0
        actual.append(u)
        n += w
    if actual:
        grupos.append(actual)
    return [(g[0][0], g[-1][1]) for g in grupos]


def vigencia(cuerpo: str) -> str:
    """Senal de vigencia a partir de las notas en linea del inicio del articulo (no es verdad juridica)."""
    inicio = cuerpo[:300]
    if re.search(r"INEXEQUIBLE", inicio):
        return "inexequible"
    if re.search(r"(?i)\bderogad[oa]s?\b", inicio):
        return "derogado"
    if re.search(r"(?i)\b(modificad|subrogad|adicionad|sustituid)[oa]s?\b", inicio):
        return "modificado"
    return "sin_nota"


def _id_articulo(num: str) -> str:
    num = re.sub(r"\s+", " ", num.strip())
    num = re.sub(r"(?i)\s+bis$", " bis", num)
    return num.upper() if num.upper().startswith("TRANSITORIO") else num


def _clave(art_id: str) -> tuple[int, ...] | None:
    """Numeros del articulo para comparar secuencias: '12-1' -> (12,), '2.2.1.4' -> (2, 2, 1, 4)."""
    if art_id.startswith("TRANSITORIO"):
        return None
    base = re.match(r"\d+(?:\.\d+)*", art_id)
    return tuple(int(x) for x in base[0].split(".")) if base else None


def _retoma_numeracion(art_id: str, ultimo: str | None) -> bool:
    """En modo cita: el encabezado es el siguiente articulo propio de la norma.

    Tras un "...quedara asi:" la norma modificatoria transcribe articulos ajenos
    (Ley 1819/2016 art. 1 -> arts. 329-340 del ET). Se sale del modo cita cuando la
    numeracion vuelve a la propia: mismo numero base o hasta 2 mas (letras y -N
    comparten base) en articulos simples, o un numero mayor al mismo nivel en los
    decretos unicos (2.2.1.4 -> 2.2.1.5).
    """
    clave, previa = _clave(art_id), (_clave(ultimo) if ultimo else None)
    if clave is None or previa is None:
        return art_id.startswith("TRANSITORIO") or previa is None
    if clave == (1,):
        return True  # la norma reinicia su numeracion (disposiciones transitorias, decreto que adopta un codigo)
    if len(clave) == 1 and len(previa) == 1:
        return previa[0] <= clave[0] <= previa[0] + 2
    return len(clave) == len(previa) and clave > previa


# --- metadatos ---------------------------------------------------------------------

def cargar_manifest() -> dict[str, dict]:
    if not config.MANIFEST_PATH.is_file() or not config.MANIFEST_PATH.stat().st_size:
        return {}
    return {d["doc_id"]: d for d in json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["documentos"]}


def meta_de(doc_id: str, manifest: dict[str, dict]) -> Meta:
    canon = cabeceras.canonico(doc_id)
    t = cabeceras.tipo(canon)
    m = manifest.get(doc_id, {})
    titulo = m.get("titulo") or doc_id
    numero, anio = canon[1], canon[2]
    if t in ("codigo", "constitucion", "decision"):
        # el numero de la norma que adopta el codigo, del titulo "Codigo Civil (Ley 57 de 1887)"
        if mt := re.search(r"(?i)\b(?:ley|decreto(?: ley)?)\s+(\d+)\s+de\s+(\d{4})", titulo):
            numero, anio = mt[1], mt[2]
    return Meta(doc_id=doc_id, canon=canon, tipo=t, numero=numero, anio=anio, titulo=titulo,
                url=m.get("url"), fuente=m.get("fuente"), siglas=cabeceras.siglas(canon))


def _chunk(meta: Meta, texto: str, span: tuple[int, int], articulo: str | None, parte: int,
           n_partes: int, seccion: str | None, vig: str | None, chunk_id: str) -> Chunk:
    cab = cabeceras.cabecera(meta.canon, articulo)
    literal = texto[span[0]:span[1]]
    completo = f"{cab}\n{literal}"
    extras = [meta.titulo] + meta.siglas + ([seccion] if seccion else [])
    return Chunk(
        chunk_id=chunk_id, doc_id=meta.doc_id, tipo=meta.tipo, numero=meta.numero, anio=meta.anio,
        articulo=articulo, parte=parte, n_partes=n_partes, seccion=seccion, vigencia=vig,
        canonico=list(meta.canon), cabecera=cab, inicio=span[0], fin=span[1], texto=completo,
        retrieval_text=completo + "\n" + " | ".join(extras), url=meta.url, fuente=meta.fuente,
        n_palabras=len(literal.split()),
    )


# --- normas --------------------------------------------------------------------------

def _es_encabezado_seccion(t: str) -> str | None:
    """Nivel ('libro', 'titulo'...) si el parrafo es un encabezado de estructura."""
    if len(t.split()) > 20 or "\n" in t.strip():
        return None
    m = _ENCABEZADO_SECCION.match(t)
    if not m:
        return None
    nivel = citations.norm(m[1])
    resto = t[m.end():].strip()
    # "Titulo valor ..." en prosa: exige numeral/ordinal o que el resto sea corto y en mayusculas
    if not m[2] and resto and not resto.isupper():
        return None
    return nivel


def segmentar_norma(texto: str, meta: Meta) -> tuple[list[Chunk], dict]:
    spans = parrafos(texto)
    ruta: list[str | None] = [None] * len(_NIVELES)
    articulos: list[dict] = []  # {id, spans, seccion}
    preambulo: list[tuple[int, int]] = []
    ultimo_encabezado: int | None = None  # nivel del encabezado previo (para su nombre)
    en_cita = False  # dentro de articulos transcritos por una norma modificatoria
    for s, e in spans:
        t = texto[s:e]
        m = _ARTICULO.match(t)
        nivel = None if m else _es_encabezado_seccion(t)
        if nivel is not None:
            i = _NIVELES[nivel]
            ruta[i] = re.sub(r"\s+", " ", t.strip())
            ruta[i + 1:] = [None] * (len(ruta) - i - 1)
            ultimo_encabezado = i
            continue
        if (ultimo_encabezado is not None and not m and len(t.split()) <= 15
                and t.strip().upper() == t.strip() and re.search(r"[A-ZÁÉÍÓÚ]", t)):
            ruta[ultimo_encabezado] = f"{ruta[ultimo_encabezado]} {t.strip()}"  # nombre del titulo/capitulo
            ultimo_encabezado = None
            continue
        ultimo_encabezado = None
        if m and m["comilla"]:
            # un encabezado entre comillas es siempre transcrito, tambien antes del primer articulo
            m = None
            en_cita = bool(articulos)
        if m and articulos:
            previo = texto[articulos[-1]["spans"][-1][0]:articulos[-1]["spans"][-1][1]]
            # articulo citado por una norma modificatoria ("...quedara asi: Articulo 247. ..."),
            # aunque entre la formula y la transcripcion haya un subtitulo (Ley 1755/2015)
            if previo.rstrip(" \"”»'’").endswith(":") or articulos[-1]["reforma"]:
                en_cita = True
            if en_cita:
                if _retoma_numeracion(_id_articulo(m["num"]), articulos[-1]["id"]):
                    en_cita = False
                else:
                    m = None
        if m:
            articulos.append({"id": _id_articulo(m["num"]), "spans": [(s, e)], "reforma": False,
                              "seccion": " / ".join(r for r in ruta if r) or None})
        elif articulos:
            articulos[-1]["spans"].append((s, e))
        else:
            preambulo.append((s, e))
        if articulos and not en_cita and _FORMULA_REFORMA.search(t):
            articulos[-1]["reforma"] = True

    chunks: list[Chunk] = []
    if preambulo:
        partes = empaquetar(texto, unidades(texto, preambulo))
        for i, sp in enumerate(partes, 1):
            chunks.append(_chunk(meta, texto, sp, None, i, len(partes), None, None,
                                 f"{meta.doc_id}#pre#p{i}"))
    for art in articulos:
        cuerpo = texto[art["spans"][0][0]:art["spans"][-1][1]]
        vig = vigencia(cuerpo)
        partes = empaquetar(texto, unidades(texto, art["spans"]))
        base = f"{meta.doc_id}#art_{art['id'].replace(' ', '_')}"
        for i, sp in enumerate(partes, 1):
            chunks.append(_chunk(meta, texto, sp, art["id"], i, len(partes), art["seccion"], vig,
                                 f"{base}#p{i}"))
    ids = [a["id"] for a in articulos]
    # numeros base (sin letras ni -N, sin transitorios): lo que cuenta n_articulos del manifest
    bases = {c for i in ids if (c := _clave(i)) is not None}
    info = {"articulos_detectados": len(set(ids)), "articulos_base": len(bases),
            "articulos_repetidos": len(ids) - len(set(ids))}
    return chunks, info


# --- sentencias --------------------------------------------------------------------

def _seccion_sentencia(t: str) -> str | None:
    if len(t.split()) > 15:
        return None
    n = citations.norm(t).strip(" .:-")
    n = re.sub(r"^[ivxlc]+\s*[.\-)]\s*|^\d+\s*[.\-)]\s*|^[a-z]\s*[.)]\s*", "", n)
    for nombre, patron in _SECCIONES_SENTENCIA:
        if patron.match(n):
            return nombre
    return None


def segmentar_sentencia(texto: str, meta: Meta) -> tuple[list[Chunk], dict]:
    spans = parrafos(texto)
    bloques: list[tuple[str, list[tuple[int, int]]]] = [("sintesis", [])]
    for s, e in spans:
        sec = _seccion_sentencia(texto[s:e])
        if sec and sec != bloques[-1][0]:
            bloques.append((sec, []))
        bloques[-1][1].append((s, e))
    ventanas: list[tuple[str, tuple[int, int]]] = []
    for sec, sp in bloques:
        if sp:
            ventanas += [(sec, v) for v in empaquetar(texto, unidades(texto, sp), solape=True)]
    chunks = [_chunk(meta, texto, v, None, i, len(ventanas), sec, None, f"{meta.doc_id}#w{i:04d}")
              for i, (sec, v) in enumerate(ventanas, 1)]
    secciones = sorted({sec for sec, _ in ventanas})
    return chunks, {"secciones": secciones}


# --- documento y corpus -----------------------------------------------------------------

def segmentar_documento(doc_id: str, manifest: dict[str, dict]) -> tuple[list[Chunk], dict]:
    ruta = config.CORPUS_TEXTOS / f"{doc_id}.txt"
    texto = ruta.read_text(encoding="utf-8")
    meta = meta_de(doc_id, manifest)
    if meta.tipo == "sentencia":
        chunks, info = segmentar_sentencia(texto, meta)
    else:
        chunks, info = segmentar_norma(texto, meta)
    # unicidad de chunk_id (p. ej. el ET repite "ARTICULO 1": el del decreto y el del estatuto)
    vistos: dict[str, int] = {}
    for c in chunks:
        if c.chunk_id in vistos:
            vistos[c.chunk_id] += 1
            c.chunk_id = f"{c.chunk_id}~{vistos[c.chunk_id]}"
        else:
            vistos[c.chunk_id] = 1
    # invariante: texto = cabecera + literal del corpus
    for c in chunks:
        if c.texto != f"{c.cabecera}\n{texto[c.inicio:c.fin]}" or c.fin <= c.inicio:
            raise AssertionError(f"{c.chunk_id}: texto no coincide con corpus[{c.inicio}:{c.fin}]")
    # en normas cada caracter pertenece a lo sumo a un fragmento (en sentencias se solapan a proposito)
    if meta.tipo != "sentencia":
        orden = sorted(chunks, key=lambda c: c.inicio)
        for a, b in zip(orden, orden[1:]):
            if b.inicio < a.fin:
                raise AssertionError(f"{a.chunk_id} y {b.chunk_id} se solapan ({b.inicio} < {a.fin})")
    avisos = []
    esperado = manifest.get(doc_id, {}).get("n_articulos")
    if meta.tipo != "sentencia" and isinstance(esperado, int) and esperado:
        det = info["articulos_base"]
        if abs(det - esperado) / esperado > TOLERANCIA_ARTICULOS:
            avisos.append(f"articulos base detectados {det} vs manifest {esperado}")
    if doc_id not in manifest:
        avisos.append("doc_id ausente de corpus_manifest.json")
    resumen = {
        "tipo": meta.tipo,
        "n_fragmentos": len(chunks),
        "n_articulos_manifest": esperado,
        **info,
        "max_palabras": max((c.n_palabras for c in chunks), default=0),
        "sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
        "avisos": avisos,
    }
    return chunks, resumen


def escribir(chunks: list[Chunk], resumen: dict[str, dict]) -> None:
    config.INDICE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = config.CHUNKS_PATH.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
    tmp.replace(config.CHUNKS_PATH)
    config.RESUMEN_INDICE_PATH.write_text(
        json.dumps({"version_segmentador": VERSION, "documentos": resumen}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--solo", nargs="+", metavar="DOC_ID",
                    help="segmentar solo estos doc_id (solo imprime; no escribe chunks.jsonl)")
    ap.add_argument("--mostrar", nargs="+", metavar=("DOC_ID", "ARTICULO"),
                    help="imprime los fragmentos de un doc_id (y de un articulo o ventana wNNNN)")
    args = ap.parse_args()

    manifest = cargar_manifest()
    if not manifest:
        print(f"AVISO: {config.MANIFEST_PATH.name} vacio o ausente; sin titulos ni n_articulos de referencia")
    docs = sorted(p.stem for p in config.CORPUS_TEXTOS.glob("*.txt"))
    if not docs:
        print(f"No hay textos en {config.CORPUS_TEXTOS}; correr los parsers de src/ingesta/")
        return 1

    if args.mostrar:
        doc_id = args.mostrar[0]
        chunks, _ = segmentar_documento(doc_id, manifest)
        sel = args.mostrar[1] if len(args.mostrar) > 1 else None
        for c in chunks:
            if sel is None or c.articulo == sel or c.chunk_id.endswith(f"#{sel}"):
                print(f"--- {c.chunk_id}  [{c.inicio}:{c.fin}] {c.n_palabras} palabras  "
                      f"seccion={c.seccion} vigencia={c.vigencia}")
                print(c.texto)
        return 0

    objetivo = [d for d in docs if not args.solo or d in args.solo]
    todos: list[Chunk] = []
    resumen: dict[str, dict] = {}
    errores = 0
    for doc_id in objetivo:
        try:
            chunks, res = segmentar_documento(doc_id, manifest)
        except (AssertionError, ValueError) as e:
            print(f"ERROR {doc_id}: {e}")
            errores += 1
            continue
        todos += chunks
        resumen[doc_id] = res
        ref = res["n_articulos_manifest"]
        arts = f"{res.get('articulos_base', '-'):>5}/{ref if ref is not None else '-':<5}"
        aviso = f"  AVISO: {'; '.join(res['avisos'])}" if res["avisos"] else ""
        print(f"{doc_id:<34} {res['tipo']:<12} {res['n_fragmentos']:>6} frag  arts {arts} "
              f"max {res['max_palabras']:>4} pal{aviso}")

    n_avisos = sum(bool(r["avisos"]) for r in resumen.values())
    print(f"\n{len(resumen)} documentos, {len(todos)} fragmentos, {n_avisos} con avisos, {errores} errores")
    if args.solo:
        print("(--solo: no se escribe chunks.jsonl)")
        return 1 if errores else 0
    if errores:
        print("No se escribe chunks.jsonl hasta corregir los errores.")
        return 1
    escribir(todos, resumen)
    print(f"Escrito {config.CHUNKS_PATH.relative_to(config.ROOT)} y {config.RESUMEN_INDICE_PATH.name}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # consolas Windows cp1252
    except AttributeError:
        pass
    raise SystemExit(main())
