"""Interfaz grafica del RAG juridico de Syntax (Streamlit), con la marca de Software Colombia.

    streamlit run src/interfaz/app.py

Capa fina sobre el pipeline: `responder(item, retriever, decoder)` con la configuracion
por defecto (la misma de src/main.py), asi que la misma pregunta da el mismo registro
que la entrega. Dos modos:
  - Consultar: pregunta libre o de ejemplo -> respuesta, citas validadas y los 10 pasajes.
    Necesita data_corpus/indice/ y llama-server (python src/generacion/modelo.py servir).
  - Explorar entrega: abre un .jsonl de entrega (y su traza) sin indice ni decoder.

De los ejemplos de sample_50 solo pasan los campos de runtime (responder.entrada_runtime):
legal_basis y las respuestas nunca se muestran ni se usan.
"""
from __future__ import annotations

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
.sx-banda {border-left: 6px solid var(--primary-color, #0B4F8A); padding: .4rem 1rem; margin-bottom: 1rem;}
.sx-banda h1 {margin: 0; font-size: 1.9rem;}
.sx-banda p {margin: 0; opacity: .75;}
.sx-chip {display: inline-block; padding: .15rem .6rem; margin: .15rem .25rem .15rem 0;
          border-radius: 999px; font-size: .85rem; border: 1px solid;}
.sx-ok {background: rgba(22, 163, 74, .12); border-color: rgba(22, 163, 74, .6);}
.sx-no {background: rgba(220, 38, 38, .12); border-color: rgba(220, 38, 38, .6);}
.sx-pie {opacity: .65; font-size: .8rem; margin-top: 2rem; border-top: 1px solid rgba(128,128,128,.3);
         padding-top: .6rem;}
</style>
"""


# ---------- recursos (se cargan una vez por proceso) ----------

def _logo() -> Path | None:
    for nombre in ("software_colombia.svg", "software_colombia.png"):
        if (ASSETS / nombre).is_file():
            return ASSETS / nombre
    return None


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


# ---------- presentacion ----------

def chips(registro: dict) -> None:
    """Citas de la respuesta (como las extrae el evaluador) y si los 10 pasajes las respaldan."""
    from generacion import citas as v
    perm = v.permitidas([p["texto"] for p in registro.get("pasajes_recuperados") or []])
    cuerpos = sorted(v.cuerpos(answer_text(registro)), key=str)
    if not cuerpos:
        st.caption("La respuesta no cita normas ni sentencias.")
        return
    html_chips = "".join(
        f'<span class="sx-chip {"sx-ok" if c in perm else "sx-no"}">'
        f'{"✓" if c in perm else "✗"} {html.escape(v.nombre(c))}</span>' for c in cuerpos)
    n_mal = sum(c not in perm for c in cuerpos)
    st.markdown(html_chips, unsafe_allow_html=True)
    st.caption(f"{len(cuerpos)} citas · {n_mal} sin respaldo en los 10 pasajes recuperados "
               "(se validan con scripts/citations.py, el mismo criterio del evaluador).")


def respuesta(registro: dict, item: dict | None = None) -> None:
    formato = registro["formato"]
    if registro.get("abstencion"):
        st.warning("El sistema **se abstiene**: la evidencia recuperada no alcanza para responder con respaldo.")
    if formato == "multiple_choice":
        letra = registro.get("respuesta_correcta")
        opciones = (item or {}).get("opciones") or {}
        if letra:
            st.success(f"**Opción {letra}**" + (f": {opciones[letra]}" if letra in opciones else ""))
    for campo in ORDEN_CAMPOS[formato]:
        valor = registro.get(campo)
        if not valor:
            continue
        st.markdown(f"**{ETIQUETAS[campo]}**")
        if isinstance(valor, list):
            st.markdown(" · ".join(f"`{x}`" for x in valor))
        else:
            st.write(valor)
    if formato == "multiple_choice" and registro.get("descarte_opciones"):
        with st.expander("Descarte de las otras opciones"):
            for letra, motivo in sorted(registro["descarte_opciones"].items()):
                st.markdown(f"**{letra}.** {motivo}")
    st.markdown("**Citas**")
    chips(registro)


def pasajes(registro: dict, traza: dict | None) -> None:
    titulos = manifest()["titulos"]
    k = (traza or {}).get("generation_k") or config.GENERATION_K
    lista = registro.get("pasajes_recuperados") or []
    st.subheader(f"Evidencia: {len(lista)} pasajes recuperados")
    st.caption(f"Texto literal del corpus. Los {k} primeros son los que lee el decoder; "
               "los 10 cuentan como respaldo de las citas.")
    for i, p in enumerate(lista, 1):
        marca = "📖 " if i <= k else ""
        score = f" · score {p['score']:.4f}" if p.get("score") is not None else ""
        with st.expander(f"{marca}{i}. {titulos.get(p['doc_id'], p['doc_id'])}{score}", expanded=i == 1):
            st.caption(f"doc_id `{p['doc_id']}` · caracteres {p.get('inicio', '?')}–{p.get('fin', '?')}")
            st.text(p["texto"])


def metricas(registro: dict, traza: dict | None) -> None:
    lat = (traza or {}).get("latencia") or {}
    cols = st.columns(4)
    cols[0].metric("Latencia total", f"{registro.get('latencia_ms', 0) / 1000:.1f} s")
    cols[1].metric("Recuperación", f"{lat['ret_ms'] / 1000:.2f} s" if "ret_ms" in lat else "—")
    cols[2].metric("Generación", f"{lat['gen_ms'] / 1000:.1f} s" if "gen_ms" in lat else "—")
    cols[3].metric("Llamadas al decoder", lat.get("n_llamadas", "—"))
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
    izq, der = st.columns([1, 1], gap="large")
    with izq:
        st.subheader("Respuesta")
        respuesta(registro, item)
        metricas(registro, traza)
        st.download_button("Descargar registro (JSON)", json.dumps(registro, ensure_ascii=False, indent=2),
                           file_name=f"respuesta_{registro['id']}.json", mime="application/json")
    with der:
        pasajes(registro, traza)


# ---------- modos ----------

def modo_consultar() -> None:
    ej = ejemplos()
    with st.sidebar:
        st.markdown("**Ejemplo de `sample_50`**")
        etiquetas = ["—"] + [f"#{e['id']} · {FORMATOS[e['formato']]} · {e['pregunta'][:50]}" for e in ej]
        elegido = st.selectbox("Cargar ejemplo", range(len(etiquetas)), format_func=lambda i: etiquetas[i],
                               label_visibility="collapsed")
    base = ej[elegido - 1] if elegido else {}
    clave = f"ej{base.get('id', 0)}"  # widgets nuevos al cambiar de ejemplo

    areas = ["(sin área)"] + manifest()["areas"]
    c1, c2 = st.columns(2)
    formato = c1.selectbox("Formato", list(FORMATOS), format_func=FORMATOS.get, key=f"f{clave}",
                           index=list(FORMATOS).index(base.get("formato", "semi_open")))
    area = c2.selectbox("Área", areas, key=f"a{clave}",
                        index=areas.index(base["area"]) if base.get("area") in areas else 0)
    pregunta = st.text_area("Pregunta", base.get("pregunta", ""), height=140, key=f"p{clave}",
                            placeholder="Ej.: ¿Qué término tiene el demandado para contestar la demanda en el proceso verbal?")
    opciones = {}
    if formato == "multiple_choice":
        previas = base.get("opciones") or {}
        for letra in "ABCD":
            texto = st.text_input(f"Opción {letra}", previas.get(letra, ""), key=f"o{letra}{clave}")
            if texto.strip():
                opciones[letra] = texto.strip()

    if not st.button("Responder", type="primary", disabled=not pregunta.strip()):
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
    resultado(registro, traza, item)


def modo_explorar() -> None:
    carpetas = sorted((config.ROOT / "evaluation" / "generacion").glob("*/entrega.jsonl"),
                      key=lambda p: p.stat().st_mtime, reverse=True)
    locales = sorted(config.ROOT.glob("submissions*.jsonl")) + sorted(config.SALIDAS_DIR.glob("*.jsonl"))
    rutas = locales + carpetas
    with st.sidebar:
        subido = st.file_uploader("Abrir una entrega (.jsonl)", type=["jsonl"])
        ruta = None
        if rutas and not subido:
            ruta = st.selectbox("…o elegir una del repo", rutas,
                                format_func=lambda p: p.relative_to(config.ROOT).as_posix())
    if subido:
        registros = [json.loads(l) for l in subido.getvalue().decode("utf-8").splitlines() if l.strip()]
        trazas: dict = {}
    elif ruta:
        registros = read_jsonl(ruta)
        cand = [ruta.with_name("trazas.jsonl"), config.TRAZAS_DIR / ruta.name.removeprefix("sample_")]
        trazas = {t["id"]: t for c in cand if c.is_file() for t in read_jsonl(c)}
    else:
        st.info("No hay entregas en el repo: sube un .jsonl desde la barra lateral.")
        return
    if not registros:
        st.warning("La entrega está vacía.")
        return

    n_abst = sum(bool(r.get("abstencion")) for r in registros)
    c = st.columns(3)
    c[0].metric("Registros", len(registros))
    c[1].metric("Abstenciones", n_abst)
    lat = [r["latencia_ms"] for r in registros if r.get("latencia_ms")]
    c[2].metric("Latencia media", f"{sum(lat) / len(lat) / 1000:.1f} s" if lat else "—")

    preguntas = {e["id"]: e for e in ejemplos()}
    etiqueta = {r["id"]: f"#{r['id']} · {FORMATOS.get(r['formato'], r['formato'])}"
                + (f" · {preguntas[r['id']]['pregunta'][:60]}" if r["id"] in preguntas else "")
                for r in registros}
    elegido = st.selectbox("Pregunta", [r["id"] for r in registros], format_func=etiqueta.get)
    registro = next(r for r in registros if r["id"] == elegido)
    item = preguntas.get(elegido)
    if item:
        st.markdown(f"> {item['pregunta']}")
        for letra, texto in (item.get("opciones") or {}).items():
            st.markdown(f"> **{letra}.** {texto}")
    resultado(registro, trazas.get(elegido), item)


def acerca() -> None:
    m = manifest()
    with st.sidebar.expander("Configuración del sistema"):
        info = {}
        if config.INDICE_INFO_PATH.is_file():
            info = json.loads(config.INDICE_INFO_PATH.read_text(encoding="utf-8"))
        llm = config.llm_config()
        st.markdown(
            f"- Decoder: `{llm['nombre']}` ({llm.get('cuantizacion', '')}), temperature 0\n"
            f"- Recuperación: {config.MODO_RECUPERACION} (BM25 + bge-m3 + RRF), top-{config.RETRIEVAL_K}\n"
            f"- Corpus: {m['n_docs']} documentos"
            + (f", {info['n_fragmentos']:,} fragmentos".replace(",", ".") if info.get("n_fragmentos") else "")
            + "\n- Licencia del corpus: CC-BY-4.0")
        if m["enlace"].startswith("http"):
            st.markdown(f"[Descargar corpus e índice]({m['enlace']})")


def main() -> None:
    logo = _logo()
    st.set_page_config(page_title="Syntax · RAG jurídico", page_icon=str(logo) if logo else "⚖️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    if logo:
        st.logo(str(logo), size="large")
    st.markdown('<div class="sx-banda"><h1>Syntax · RAG de derecho colombiano</h1>'
                '<p>con Software Colombia</p></div>', unsafe_allow_html=True)
    modo = st.sidebar.radio("Modo", ["Consultar", "Explorar entrega"])
    acerca()
    if modo == "Consultar":
        modo_consultar()
    else:
        modo_explorar()
    st.markdown('<div class="sx-pie">Equipo Syntax: Sofía Morato, Joel David Niño, Santiago Muñoz · '
                'Hackathon LATAM AI Week 2026 (Uniandes) · Herramienta de apoyo: no constituye asesoría legal.'
                '</div>', unsafe_allow_html=True)


main()
