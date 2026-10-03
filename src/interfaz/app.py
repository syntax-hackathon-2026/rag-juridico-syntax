"""Interfaz grafica del RAG juridico de Syntax (Streamlit), con la estetica de Software Colombia.

    streamlit run src/interfaz/app.py

Capa fina sobre el pipeline: `responder(item, retriever, decoder)` con la configuracion
por defecto (la misma de src/main.py), asi que la misma pregunta da el mismo registro
que la entrega. Dos modos:
  - Consultar: pregunta libre o de ejemplo -> respuesta, citas validadas y los 10 pasajes.
    Necesita data_corpus/indice/ y llama-server (python src/generacion/modelo.py servir).
  - Explorar entrega: abre un .jsonl de entrega (y su traza) sin indice ni decoder.

De los ejemplos de sample_50 solo pasan los campos de runtime (responder.entrada_runtime):
legal_basis y las respuestas nunca se muestran ni se usan.

Estetica de software-colombia.com: turquesa #09ACC4 (hover #0890A8), naranja #FF993B,
texto #32373C, Montserrat, tarjetas blancas con borde turquesa suave y pie turquesa claro.
"""
from __future__ import annotations

import base64
import html
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from common import read_jsonl  # noqa: E402
from evaluate import answer_text  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO = ASSETS / "software_colombia.png"
MODOS = ("Consultar", "Explorar entrega")
FORMATOS = {"multiple_choice": "Selección múltiple", "semi_open": "Semiabierta", "open_ended": "Abierta (caso)"}
CAMPOS_RUNTIME = ("id", "formato", "area", "pregunta", "opciones")  # = responder.CAMPOS_RUNTIME
ETIQUETAS = {
    "justificacion": "Justificación", "respuesta": "Respuesta", "palabras_clave": "Palabras clave",
    "referencia_legal": "Referencia legal", "marco_normativo": "Marco normativo", "analisis": "Análisis",
    "jurisprudencia": "Jurisprudencia", "conclusion": "Conclusión",
}
ORDEN_CAMPOS = {
    "multiple_choice": ("justificacion",),
    "semi_open": ("respuesta", "palabras_clave", "referencia_legal"),
    "open_ended": ("marco_normativo", "analisis", "jurisprudencia", "conclusion"),
}
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
:root {--sc-turquesa: #09ACC4; --sc-turquesa-osc: #0890A8; --sc-naranja: #FF993B;
       --sc-texto: #32373C; --sc-gris: #8A8F94; --sc-borde: rgba(9, 172, 196, .22);}
html, body, p, li, label, input, textarea, button, h1, h2, h3, h4, .stMarkdown, .stCaption {
    font-family: 'Montserrat', sans-serif !important;}
header[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {display: none;}
[data-testid="stMainBlockContainer"], .block-container {max-width: 1240px; padding-top: 0; padding-bottom: 0;}
[data-testid="stMain"] {overflow-x: hidden;}
h1, h2, h3 {color: var(--sc-texto); font-weight: 700 !important;}

/* barra de navegacion */
.st-key-nav {background: #fff; box-shadow: 0 10px 30px -18px rgba(0,0,0,.25); width: 100vw !important;
    max-width: 100vw; margin: 0 0 .5rem calc(50% - 50vw); padding: .6rem calc(50vw - 50% + 1rem);}
.sc-logo img {height: 64px; width: auto;}
.st-key-modo {width: 100% !important;}
.st-key-modo [data-testid="stRadioGroup"] {justify-content: flex-end; gap: 2.4rem;}
.st-key-modo [data-testid="stRadioOption"] > div > div:first-child {display: none;}
.st-key-modo [data-testid="stRadioOption"] {padding-bottom: .35rem; border-bottom: 3px solid transparent; cursor: pointer;}
.st-key-modo [data-testid="stRadioOption"] p {text-transform: uppercase; font-weight: 700; font-size: .85rem;
    letter-spacing: .02em; color: var(--sc-texto);}
.st-key-modo [data-testid="stRadioOption"][data-selected="true"] {border-bottom-color: var(--sc-turquesa);}
.st-key-modo [data-testid="stRadioOption"]:hover p {color: var(--sc-turquesa);}

/* titulo de seccion */
.sc-seccion {text-align: center; margin: 2.2rem 0 1.6rem;}
.sc-kicker {color: var(--sc-turquesa); font-size: .95rem; margin-bottom: .2rem;}
.sc-seccion h1 {font-size: 2.3rem; margin: 0; padding: 0;}
.sc-barra {width: 135px; height: 4px; background: var(--sc-naranja); margin: .7rem auto 1rem;}
.sc-sub {color: var(--sc-gris); font-size: 1.02rem; line-height: 1.75; max-width: 640px; margin: 0 auto;}

/* tarjetas */
[class*="st-key-tarjeta"] {background: #fff; border: 1px solid var(--sc-borde) !important; border-radius: 6px;
    box-shadow: 0 6px 22px -10px rgba(9, 172, 196, .35); padding: 1.4rem 1.6rem;}
.sc-titulo {text-align: center; font-weight: 700; font-size: 1.25rem; color: var(--sc-texto); margin-bottom: .2rem;}
.sc-titulo-sub {text-align: center; font-weight: 400; color: var(--sc-texto); font-size: 1rem;}
.sc-mini {width: 68px; height: 4px; background: var(--sc-turquesa); margin: .7rem auto 1.1rem;}
.sc-campo {font-weight: 700; color: var(--sc-texto); margin: .9rem 0 .2rem;}
.sc-opcion {border-left: 4px solid var(--sc-turquesa); background: rgba(9, 172, 196, .08);
    padding: .8rem 1rem; border-radius: 0 4px 4px 0; color: var(--sc-texto);}
.sc-opcion b {color: var(--sc-turquesa-osc);}
.sc-abstiene {border-left: 4px solid var(--sc-naranja); background: rgba(255, 153, 59, .1);
    padding: .8rem 1rem; border-radius: 0 4px 4px 0;}
.sc-pregunta {color: var(--sc-gris); font-size: 1.02rem; line-height: 1.7; text-align: center; max-width: 900px; margin: 0 auto 1rem;}
.sc-chip {display: inline-block; padding: .2rem .7rem; margin: .2rem .3rem .2rem 0; border-radius: 3px;
    font-size: .8rem; font-weight: 600; color: #fff;}
.sc-ok {background: var(--sc-turquesa);}
.sc-no {background: #D9534F;}
.sc-tag {display: inline-block; padding: .15rem .6rem; margin: .15rem .3rem .15rem 0; border: 1px solid var(--sc-borde);
    border-radius: 3px; font-size: .82rem; color: var(--sc-turquesa-osc);}
[data-testid="stExpander"] details {border: 1px solid var(--sc-borde); border-radius: 4px;}
[data-testid="stExpander"] summary p {font-weight: 600; font-size: .9rem;}
[data-testid="stMetricValue"] {color: var(--sc-turquesa); font-weight: 700;}
[data-testid="stMetricLabel"] p {text-transform: uppercase; font-size: .75rem; letter-spacing: .04em; color: var(--sc-gris);}
.stButton button, .stDownloadButton button, [data-testid="stFileUploader"] button {
    text-transform: uppercase; font-weight: 700; letter-spacing: .03em; border-radius: 3px; padding: .55rem 1.8rem;}

/* pie */
.sc-pie {background: #E6F6F9; margin: 3.5rem calc(50% - 50vw) 0; padding: 3rem calc(50vw - 50% + 1rem) 2.5rem;}
.sc-pie-grid {display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 2rem; max-width: 1240px; margin: 0 auto;}
.sc-pie h4 {text-align: center; font-size: 1.35rem; margin: 0;}
.sc-pie .sc-barra {width: 78px; height: 3px; margin: .6rem auto 1.1rem;}
.sc-pie p, .sc-pie li {color: var(--sc-gris); text-align: center; font-size: .92rem; line-height: 1.9; margin: 0; list-style: none;}
.sc-pie ul {padding: 0; margin: 0;}
.sc-pie a {color: var(--sc-turquesa); text-decoration: none;}
.sc-pie img {height: 88px; display: block; margin: 0 auto 1rem;}
@media (max-width: 800px) {.sc-pie-grid {grid-template-columns: 1fr;}
    .st-key-modo [data-testid="stRadioGroup"] {justify-content: center;}}
</style>
"""


# ---------- recursos (se cargan una vez por proceso) ----------

@st.cache_data
def logo_b64() -> str:
    return base64.b64encode(LOGO.read_bytes()).decode("ascii") if LOGO.is_file() else ""


@st.cache_data
def manifest() -> dict:
    datos = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"titulos": {d["doc_id"]: d.get("titulo") or d["doc_id"] for d in datos["documentos"]},
            "areas": sorted({a for d in datos["documentos"] for a in d.get("areas") or ()}),
            "n_docs": len(datos["documentos"]), "enlace": datos.get("enlace_nube") or ""}


@st.cache_data
def ejemplos() -> list[dict]:
    if not config.SAMPLE_PATH.is_file():
        return []
    return [{k: it[k] for k in CAMPOS_RUNTIME if k in it} for it in read_jsonl(config.SAMPLE_PATH)]


@st.cache_resource(show_spinner="Cargando el índice (BM25 + bge-m3)…")
def recursos():
    """Retriever + decoder. Importes diferidos: el modo Explorar no necesita torch ni faiss."""
    from generacion import modelo
    from generacion.llm import Decoder
    from recuperacion.retriever import cargar
    config.verificar_indice()
    info_llm = modelo.verificar()  # SystemExit con el comando para levantarlo si no responde
    retriever = cargar(cargar_denso=config.MODO_RECUPERACION != "bm25")
    return retriever, Decoder(), info_llm


# ---------- piezas visuales ----------

def md(texto: str) -> None:
    st.markdown(texto, unsafe_allow_html=True)


def seccion(kicker: str, titulo: str, sub: str) -> None:
    md(f'<div class="sc-seccion"><div class="sc-kicker">{kicker}</div><h1>{titulo}</h1>'
       f'<div class="sc-barra"></div><div class="sc-sub">{sub}</div></div>')


def titulo_tarjeta(titulo: str, sub: str = "") -> None:
    md(f'<div class="sc-titulo-sub">{sub}</div>' if sub else "")
    md(f'<div class="sc-titulo">{titulo}</div><div class="sc-mini"></div>')


def navegacion() -> str:
    with st.container(key="nav"):
        izq, der = st.columns([1, 2], vertical_alignment="center")
        b64 = logo_b64()
        izq.markdown(f'<div class="sc-logo"><img src="data:image/png;base64,{b64}" alt="Software Colombia"></div>'
                     if b64 else "**Software Colombia**", unsafe_allow_html=True)
        with der:
            return st.radio("Modo", MODOS, horizontal=True, label_visibility="collapsed", key="modo")


def pie() -> None:
    m = manifest()
    info = {}
    if config.INDICE_INFO_PATH.is_file():
        info = json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8"))
    llm = config.llm_config()
    frag = f"{info['n_fragmentos']:,}".replace(",", ".") + " fragmentos" if info.get("n_fragmentos") else ""
    enlace = (f'<li><a href="{html.escape(m["enlace"])}">Descargar corpus e índice</a></li>'
              if m["enlace"].startswith("http") else "")
    md(_pie_html(logo_b64(), llm, m, frag, enlace))


def _pie_html(b64: str, llm: dict, m: dict, frag: str, enlace: str) -> str:
    n_docs = f"{m['n_docs']:,}".replace(",", ".")
    img = f'<img src="data:image/png;base64,{b64}" alt="Software Colombia">' if b64 else ""
    return f"""<div class="sc-pie"><div class="sc-pie-grid">
<div>{img}<p>Equipo Syntax</p><p>Sofía Morato · Joel David Niño · Santiago Muñoz</p>
<p>Hackathon LATAM AI Week 2026 · Uniandes</p></div>
<div><h4>Nuestro sistema</h4><div class="sc-barra"></div><ul>
<li>Decoder {html.escape(llm['nombre'])} ({html.escape(str(llm.get('cuantizacion', '')))}), temperatura 0</li>
<li>Recuperación híbrida BM25 + bge-m3 + RRF, top-{config.RETRIEVAL_K}</li>
<li>Citas validadas contra los pasajes recuperados</li></ul></div>
<div><h4>Información de interés</h4><div class="sc-barra"></div><ul>
<li>Corpus: {n_docs} documentos{' · ' + frag if frag else ''}</li>
<li>Licencia del corpus CC-BY-4.0</li>{enlace}
<li>Herramienta de apoyo: no constituye asesoría legal</li></ul></div>
</div></div>"""


# ---------- presentacion del resultado ----------

def chips(registro: dict) -> None:
    """Citas de la respuesta (como las extrae el evaluador) y si los 10 pasajes las respaldan."""
    from generacion import citas as v
    perm = v.permitidas([p["texto"] for p in registro.get("pasajes_recuperados") or []])
    cuerpos = sorted(v.cuerpos(answer_text(registro)), key=str)
    if not cuerpos:
        st.caption("La respuesta no cita normas ni sentencias.")
        return
    md("".join(f'<span class="sc-chip {"sc-ok" if c in perm else "sc-no"}">'
               f'{"✓" if c in perm else "✗"} {html.escape(v.nombre(c))}</span>' for c in cuerpos))
    n_mal = sum(c not in perm for c in cuerpos)
    st.caption(f"{len(cuerpos)} citas · {n_mal} sin respaldo en los 10 pasajes recuperados "
               "(mismo criterio de scripts/citations.py que usa el evaluador).")


def respuesta(registro: dict, item: dict | None = None) -> None:
    formato = registro["formato"]
    if registro.get("abstencion"):
        md('<div class="sc-abstiene"><b>El sistema se abstiene:</b> la evidencia recuperada no alcanza '
           'para responder con respaldo.</div>')
    if formato == "multiple_choice" and (letra := registro.get("respuesta_correcta")):
        texto = ((item or {}).get("opciones") or {}).get(letra, "")
        md(f'<div class="sc-opcion"><b>Opción {letra}</b>{": " + html.escape(texto) if texto else ""}</div>')
    for campo in ORDEN_CAMPOS[formato]:
        valor = registro.get(campo)
        if not valor:
            continue
        md(f'<div class="sc-campo">{ETIQUETAS[campo]}</div>')
        if isinstance(valor, list):
            md("".join(f'<span class="sc-tag">{html.escape(str(x))}</span>' for x in valor))
        else:
            st.write(valor)
    if formato == "multiple_choice" and registro.get("descarte_opciones"):
        with st.expander("Descarte de las otras opciones"):
            for letra, motivo in sorted(registro["descarte_opciones"].items()):
                st.markdown(f"**{letra}.** {motivo}")
    md('<div class="sc-campo">Citas</div>')
    chips(registro)


def pasajes(registro: dict, traza: dict | None) -> None:
    titulos = manifest()["titulos"]
    k = (traza or {}).get("generation_k") or config.GENERATION_K
    lista = registro.get("pasajes_recuperados") or []
    titulo_tarjeta("Evidencia recuperada", f"{len(lista)} pasajes literales del corpus")
    st.caption(f"Los {k} primeros (📖) son los que lee el decoder; los 10 cuentan como respaldo de las citas.")
    for i, p in enumerate(lista, 1):
        marca = "📖 " if i <= k else ""
        score = f" · score {p['score']:.4f}" if p.get("score") is not None else ""
        with st.expander(f"{marca}{i}. {titulos.get(p['doc_id'], p['doc_id'])}{score}", expanded=i == 1):
            st.caption(f"doc_id `{p['doc_id']}` · caracteres {p.get('inicio', '?')}–{p.get('fin', '?')}")
            st.text(p["texto"])


def metricas(registro: dict, traza: dict | None) -> None:
    lat = (traza or {}).get("latencia") or {}
    cols = st.columns(3)
    cols[0].metric("Latencia total", f"{registro.get('latencia_ms', 0) / 1000:.1f} s")
    cols[1].metric("Recuperación", f"{lat['ret_ms'] / 1000:.2f} s" if "ret_ms" in lat else "—")
    cols[2].metric("Generación", f"{lat['gen_ms'] / 1000:.1f} s" if "gen_ms" in lat else "—")
    if traza:
        notas = []
        if traza.get("regenerado"):
            notas.append("se regeneró una vez por citas sin respaldo")
        if traza.get("citas_quitadas"):
            notas.append("se quitaron oraciones con citas sin respaldo")
        motivos = (traza.get("abstencion") or {}).get("motivos")
        if motivos:
            notas.append("motivos de abstención: " + ", ".join(motivos))
        if traza.get("errores_schema"):
            notas.append(f"errores de schema: {traza['errores_schema']}")
        if notas:
            st.caption(" · ".join(notas))


def resultado(registro: dict, traza: dict | None, item: dict | None) -> None:
    izq, der = st.columns(2, gap="large")
    with izq, st.container(key="tarjeta_respuesta"):
        titulo_tarjeta("Respuesta", FORMATOS.get(registro["formato"], ""))
        respuesta(registro, item)
        metricas(registro, traza)
        st.download_button("Descargar JSON", json.dumps(registro, ensure_ascii=False, indent=2),
                           file_name=f"respuesta_{registro['id']}.json", mime="application/json", type="primary")
    with der, st.container(key="tarjeta_evidencia"):
        pasajes(registro, traza)


# ---------- modos ----------

def modo_consultar() -> None:
    seccion("RAG de derecho colombiano", "Consulta Jurídica",
            "Respuestas a preguntas de derecho colombiano con normas y jurisprudencia "
            "citadas solo si están respaldadas por el corpus.")
    ej = ejemplos()
    with st.container(key="tarjeta_consulta"):
        etiquetas = ["Escribir una pregunta nueva"] + [
            f"#{e['id']} · {FORMATOS[e['formato']]} · {e['pregunta'][:70]}" for e in ej]
        elegido = st.selectbox("Ejemplo de las preguntas de muestra", range(len(etiquetas)),
                               format_func=lambda i: etiquetas[i])
        base = ej[elegido - 1] if elegido else {}
        clave = f"ej{base.get('id', 0)}"  # widgets nuevos al cambiar de ejemplo

        areas = ["(sin área)"] + manifest()["areas"]
        c1, c2 = st.columns(2)
        formato = c1.selectbox("Formato", list(FORMATOS), format_func=FORMATOS.get, key=f"f{clave}",
                               index=list(FORMATOS).index(base.get("formato", "semi_open")))
        area = c2.selectbox("Área", areas, key=f"a{clave}",
                            index=areas.index(base["area"]) if base.get("area") in areas else 0)
        pregunta = st.text_area("Pregunta", base.get("pregunta", ""), height=130, key=f"p{clave}",
                                placeholder="Ej.: ¿Qué término tiene el demandado para contestar la demanda en el proceso verbal?")
        opciones = {}
        if formato == "multiple_choice":
            previas = base.get("opciones") or {}
            for letra in "ABCD":
                texto = st.text_input(f"Opción {letra}", previas.get(letra, ""), key=f"o{letra}{clave}")
                if texto.strip():
                    opciones[letra] = texto.strip()
        pulsado = st.button("Responder", type="primary", disabled=not pregunta.strip())

    if not pulsado:
        return
    if formato == "multiple_choice" and len(opciones) < 2:
        st.error("Una pregunta de selección múltiple necesita al menos dos opciones.")
        return
    try:
        retriever, decoder, _ = recursos()
    except SystemExit as e:  # sin indice o sin llama-server: el mensaje trae el comando
        st.error(f"No se puede responder en esta máquina:\n\n```\n{e}\n```")
        st.info("El modo **Explorar entrega** funciona sin índice ni decoder.")
        return
    from generacion.responder import responder
    item = {"id": int(base.get("id", 0)), "formato": formato, "pregunta": pregunta.strip()}
    if area != areas[0]:
        item["area"] = area
    if opciones:
        item["opciones"] = opciones
    with st.spinner("Recuperando evidencia y generando con Qwen3-8B…"):
        registro, traza = responder(item, retriever, decoder)
    st.write("")
    resultado(registro, traza, item)


def modo_explorar() -> None:
    seccion("Verificación de resultados", "Explorar Entrega",
            "Revisa cada respuesta de una entrega con su evidencia, sin necesidad del índice ni del decoder.")
    carpetas = sorted((config.ROOT / "evaluation" / "generacion").glob("*/entrega.jsonl"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    locales = sorted(config.ROOT.glob("submissions*.jsonl")) + sorted(config.SALIDAS_DIR.glob("*.jsonl"))
    rutas = locales + carpetas
    with st.container(key="tarjeta_entrega"):
        c1, c2 = st.columns(2)
        ruta = c1.selectbox("Entrega del repositorio", rutas, format_func=lambda p: p.relative_to(config.ROOT).as_posix()) \
            if rutas else None
        subido = c2.file_uploader("…o abrir un archivo .jsonl", type=["jsonl"])
    if subido:
        registros = [json.loads(l) for l in subido.getvalue().decode("utf-8").splitlines() if l.strip()]
        trazas: dict = {}
    elif ruta:
        registros = read_jsonl(ruta)
        cand = [ruta.with_name("trazas.jsonl"), config.TRAZAS_DIR / ruta.name.removeprefix("sample_")]
        trazas = {t["id"]: t for c in cand if c.is_file() for t in read_jsonl(c)}
    else:
        st.info("No hay entregas en el repo: abre un .jsonl.")
        return
    if not registros:
        st.warning("La entrega está vacía.")
        return

    st.write("")
    c = st.columns(3)
    c[0].metric("Registros", len(registros))
    c[1].metric("Abstenciones", sum(bool(r.get("abstencion")) for r in registros))
    lat = [r["latencia_ms"] for r in registros if r.get("latencia_ms")]
    c[2].metric("Latencia media", f"{sum(lat) / len(lat) / 1000:.1f} s" if lat else "—")

    preguntas = {e["id"]: e for e in ejemplos()}
    etiqueta = {r["id"]: f"#{r['id']} · {FORMATOS.get(r['formato'], r['formato'])}"
                + (f" · {preguntas[r['id']]['pregunta'][:80]}" if r["id"] in preguntas else "")
                for r in registros}
    elegido = st.selectbox("Pregunta", [r["id"] for r in registros], format_func=etiqueta.get)
    registro = next(r for r in registros if r["id"] == elegido)
    item = preguntas.get(elegido)
    if item:
        opciones = "".join(f"<br><b>{l}.</b> {html.escape(t)}" for l, t in (item.get("opciones") or {}).items())
        md(f'<div class="sc-pregunta">{html.escape(item["pregunta"])}{opciones}</div>')
    resultado(registro, trazas.get(elegido), item)


def main() -> None:
    st.set_page_config(page_title="Syntax · Consulta jurídica", page_icon=str(LOGO) if LOGO.is_file() else "⚖️",
                       layout="wide", initial_sidebar_state="collapsed")
    md(CSS)
    modo = navegacion()
    if modo == "Consultar":
        modo_consultar()
    else:
        modo_explorar()
    pie()


main()
