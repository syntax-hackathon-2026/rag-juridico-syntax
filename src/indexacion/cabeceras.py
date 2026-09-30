"""Cuerpo canonico de cada documento y encabezado citable de cada fragmento.

El evaluador da por respaldada una cita solo si `citations.extract()` la encuentra
en el TEXTO de alguno de los 10 primeros pasajes (scripts/evaluate.py,
citas_respaldadas). Un articulo suelto ("ARTICULO 42. Deberes del juez...") no
extrae ninguna norma, asi que cada fragmento empieza con un encabezado del tipo
"Articulo 42 del Codigo General del Proceso." que extrae exactamente el cuerpo
canonico del documento. `cabecera()` lo comprueba con el propio `citations`.

Forma elegida "Articulo N de/del <nombre>." porque:
  - "<nombre>, articulo N" pierde el articulo cuando el nombre sigue ("Constitucion
    Politica de Colombia, articulo 29": la ventana de _articles_near se rompe);
  - "Codigo Civil (Ley 57 de 1887)" agrega un cuerpo espurio ("ley","57","1887").

Canonico de un doc_id, en orden: doc_id que es clave de citations.CODES -> regex sobre
el doc_id (ley_N_AAAA, decreto_N_AAAA, sentencia_<sala>_N_AAAA) -> `canonico` de
data/fuentes_descargadas.json (p. ej. constitucion_politica_1991). El doc_id va
primero porque es la identidad ya verificada: el `canonico` de la semilla arrastra
erratas del banco que fuentes_override.json corrigio en el doc_id (ley_1563_2012
figura como "Decreto 1563 de 2012", decreto_2737_1989 como "Ley 2737 de 1989",
ley_964_2005 como "Ley 964 de 2006").
"""
from __future__ import annotations

import json
import re
import sys
from functools import lru_cache

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
import citations  # noqa: E402

Canonico = tuple  # (cuerpo, numero|None, anio|None)

# Nombre con tildes y genero gramatical ("de la" / "del") de los cuerpos de CODES.
NOMBRES: dict[str, tuple[str, str]] = {
    "constitucion": ("Constitución Política", "la"),
    "codigo_civil": ("Código Civil", "el"),
    "codigo_penal": ("Código Penal", "el"),
    "codigo_procedimiento_penal": ("Código de Procedimiento Penal", "el"),
    "codigo_comercio": ("Código de Comercio", "el"),
    "codigo_sustantivo_trabajo": ("Código Sustantivo del Trabajo", "el"),
    "codigo_procesal_trabajo": ("Código Procesal del Trabajo", "el"),
    "codigo_general_proceso": ("Código General del Proceso", "el"),
    "cpaca": ("Código de Procedimiento Administrativo y de lo Contencioso Administrativo", "el"),
    "estatuto_tributario": ("Estatuto Tributario", "el"),
    "codigo_infancia": ("Código de la Infancia y la Adolescencia", "el"),
    "codigo_nacional_policia": ("Código Nacional de Seguridad y Convivencia Ciudadana", "el"),
    "codigo_disciplinario": ("Código General Disciplinario", "el"),
    "estatuto_consumidor": ("Estatuto del Consumidor", "el"),
    "decision_andina_486": ("Decisión 486 de la Comisión de la Comunidad Andina", "la"),
}
TIPOS_NORMA = {"ley": ("Ley", "la"), "decreto": ("Decreto", "el"),
               "acto_legislativo": ("Acto Legislativo", "el"), "resolucion": ("Resolución", "la")}
CORTES = {
    "C": "Corte Constitucional", "T": "Corte Constitucional", "SU": "Corte Constitucional",
    "SL": "Corte Suprema de Justicia, Sala de Casación Laboral",
    "SP": "Corte Suprema de Justicia, Sala de Casación Penal",
    "SC": "Corte Suprema de Justicia, Sala de Casación Civil",
    "STC": "Corte Suprema de Justicia, Sala de Casación Civil",
    "STL": "Corte Suprema de Justicia, Sala de Casación Laboral",
}

_RE_NORMA = re.compile(r"^(ley|decreto|acto_legislativo|resolucion)_(\d+)_(\d{4})$")
_RE_SENTENCIA = re.compile(r"^sentencia_([a-z]{1,3})_(\d+)_(\d{4})$")


@lru_cache(maxsize=1)
def _fuentes() -> dict[str, dict]:
    if not config.FUENTES_PATH.is_file():
        return {}
    datos = json.loads(config.FUENTES_PATH.read_text(encoding="utf-8"))
    return {d["doc_id"]: d for d in datos["documentos"]}


def canonico(doc_id: str) -> Canonico:
    """Tupla canonica (formato de citations) del cuerpo normativo de un documento."""
    if doc_id in citations.CODES:
        return (doc_id, None, None)
    if m := _RE_NORMA.match(doc_id):
        # una ley que citations trata como codigo (ley_1564_2012 -> codigo_general_proceso)
        alias = citations._ALIAS_NUM.get((m[1], m[2]))
        return (alias, None, None) if alias else (m[1], m[2], m[3])
    if m := _RE_SENTENCIA.match(doc_id):
        return ("jurisprudencia", f"{m[1].upper()}-{int(m[2])}", m[3])
    c = _fuentes().get(doc_id, {}).get("canonico")
    if c:
        return tuple(c)
    raise ValueError(f"{doc_id}: no se puede deducir el cuerpo canonico; agregar 'canonico' "
                     f"en {config.FUENTES_PATH.name} o usar un doc_id tipo ley_N_AAAA")


def tipo(canon: Canonico) -> str:
    cuerpo = canon[0]
    if cuerpo == "jurisprudencia":
        return "sentencia"
    if cuerpo == "constitucion":
        return "constitucion"
    if cuerpo == "decision_andina_486":
        return "decision"
    if cuerpo in citations.CODES:
        return "codigo"
    return cuerpo  # ley | decreto | ...


def nombre(canon: Canonico) -> tuple[str, str]:
    """(nombre legible, articulo 'la'/'el') del cuerpo, p. ej. ('Ley 80 de 1993', 'la')."""
    cuerpo, numero, anio = canon
    if cuerpo in NOMBRES:
        return NOMBRES[cuerpo]
    if cuerpo in TIPOS_NORMA:
        t, art = TIPOS_NORMA[cuerpo]
        return f"{t} {numero} de {anio}", art
    raise ValueError(f"cuerpo sin nombre legible: {canon}")


def _con_articulo(art: str, nom: str) -> str:
    return f"del {nom}" if art == "el" else f"de la {nom}"


@lru_cache(maxsize=None)
def cabecera(canon: Canonico, articulo: str | None = None) -> str:
    """Encabezado citable de un fragmento; falla si no extrae exactamente `canon`."""
    if canon[0] == "jurisprudencia":
        sala, anio = canon[1].split("-")[0], canon[2]
        corte = CORTES.get(sala, "Corte")
        texto = f"{corte}, Sentencia {canon[1]} de {anio}."
    else:
        nom, art = nombre(canon)
        if articulo is None:
            texto = f"{nom}, encabezado y disposiciones iniciales."
        elif articulo.upper().startswith("TRANSITORIO"):
            texto = f"Artículo {articulo.lower()} {_con_articulo(art, nom)}."
        else:
            texto = f"Artículo {articulo} {_con_articulo(art, nom)}."
    extraidos = citations.bodies(citations.extract(texto))
    if extraidos != {tuple(canon)}:
        raise AssertionError(f"la cabecera {texto!r} extrae {extraidos}, se esperaba {{{canon}}}")
    return texto


def siglas(canon: Canonico) -> list[str]:
    """Abreviaturas usuales del cuerpo (CGP, CST, ET...) para el texto de busqueda."""
    variantes = citations.CODES.get(canon[0], ())
    return sorted({v.replace(".", "").upper() for v in variantes
                   if len(v.replace(".", "")) <= 6 and " " not in v})
