"""Prompts y JSON Schemas por formato (generate_closed / generate_semi_open / generate_open).

Cambiar cualquier texto de este archivo = subir PROMPT_VERSION (va a experiments.csv
y a cada traza): con temperatura 0 el prompt es parte de la configuracion congelada.

Estructura de los mensajes:
  system: reglas comunes + instrucciones del formato (fijo por formato)
  user:   pasajes [P1]..[Pk] (texto literal del fragmento, con su cabecera citable)
          + pregunta (+ opciones)

El schema se impone por gramatica en llama.cpp y fija el orden de las claves. En
cerradas va `justificacion` antes que `respuesta_correcta`: el modelo razona antes
de elegir la letra.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402

# p-v0: base. p-v2: reglas de decision en cerradas (SYNTAX_PROMPT_MC; docs/GENERACION.md 9).
# "+glosario": fichas y notas de equivalencia de normas (SYNTAX_GLOSARIO, generacion/glosario.py).
# "+tl1": instrucciones de texto libre p-tl1 (SYNTAX_PROMPT_TL; docs/GENERACION.md 10).
PROMPT_VERSION = (config.PROMPT_MC + ("+glosario" if config.GLOSARIO == "on" else "")
                  + ("+tl1" if config.PROMPT_TL == "p-tl1" else ""))

MAX_TOKENS = {"multiple_choice": 700, "semi_open": 450, "open_ended": 1100}

REGLAS = """Eres un abogado colombiano experto. Respondes preguntas de derecho colombiano usando pasajes recuperados de un corpus de normas y sentencias colombianas, numerados [P1], [P2], etc. La primera línea de cada pasaje identifica su fuente, por ejemplo «Artículo 42 del Código General del Proceso.», «Artículo 5 de la Ley 80 de 1993.» o «Corte Constitucional, Sentencia C-355 de 2006.».

Reglas:
1. Fundamenta la respuesta en los pasajes. Si no bastan, usa tu conocimiento jurídico general, pero sin citar normas que no estén en ellos.
2. Cita únicamente normas, artículos y sentencias que aparezcan en los pasajes, escritas como en su primera línea: «artículo 42 del Código General del Proceso», «artículo 88 de la Constitución Política», «Ley 472 de 1998», «Sentencia C-355 de 2006». Nunca cites una norma, un artículo o una sentencia que no esté en los pasajes, aunque la conozcas o la mencione la pregunta.
3. Escribe en español, con lenguaje jurídico preciso y directo. Empieza por la respuesta, sin repetir la pregunta.
4. Devuelve solo el objeto JSON pedido."""

INSTRUCCIONES = {
    "multiple_choice": """Formato: pregunta de selección múltiple con una sola opción correcta.
- "justificacion": de 2 a 4 oraciones que expliquen por qué la opción correcta lo es, citando la norma aplicable de los pasajes.
- "respuesta_correcta": la letra de la opción correcta.
- "descarte_opciones": para cada letra, una oración breve; para las opciones incorrectas, por qué lo son; para la elegida, «Es la opción correcta.».""" + ("" if config.PROMPT_MC == "p-v0" else """
Para elegir:
- Que una opción no aparezca en los pasajes no la hace incorrecta. Si los pasajes no resuelven la pregunta, elige con tu conocimiento del derecho colombiano la opción más exacta.
- «Todas las anteriores», «Ninguna de las anteriores» u opciones que combinan otras («(a) y (b)») solo son correctas si lo es cada opción que abarcan (o ninguna, en el caso de «Ninguna»).
- Si la pregunta exige un cálculo o comparar cifras o plazos, hazlo explícitamente en la justificación antes de elegir."""),
    "semi_open": """Formato: pregunta de respuesta corta.
- "respuesta": de 3 a 5 oraciones y como máximo 120 palabras. La primera oración responde directamente la pregunta. Incluye los requisitos, plazos, autoridades o conceptos concretos que se piden y menciona la norma que lo establece.
- "palabras_clave": de 3 a 6 términos jurídicos clave de la respuesta.
- "referencia_legal": la norma o el artículo principal que fundamenta la respuesta, tomado de los pasajes (por ejemplo «Artículo 1502 del Código Civil»).""",
    "open_ended": """Formato: caso práctico que exige un análisis completo.
- "marco_normativo": las normas aplicables tomadas de los pasajes, con una frase sobre lo que regula cada una.
- "analisis": de 5 a 8 oraciones que apliquen esas normas a los hechos del caso.
- "jurisprudencia": las sentencias de los pasajes que sean pertinentes y la regla que fijan; si los pasajes no traen sentencias pertinentes, escribe «No se recuperó jurisprudencia pertinente para el caso.».
- "conclusion": de 1 a 3 oraciones con la respuesta concreta al caso.""",
}


# p-tl1 (docs/GENERACION.md 10): el juez RAGAS compara afirmaciones con la respuesta esperada,
# que es una linea (que articulo), una enumeracion (requisitos) o un Si/No con la regla. La
# forma uniforme de p-v0 agrega afirmaciones de sobra o deja elementos fuera.
INSTRUCCIONES_TL1 = {
    "semi_open": """Formato: pregunta de respuesta corta.
- "respuesta": como máximo 5 oraciones y 120 palabras. La primera oración responde directamente la pregunta. Ajusta la forma a lo que se pregunta:
  - Si pregunta qué artículo o qué norma regula algo, o pide citar o transcribir una disposición: una o dos oraciones con la norma y su contenido.
  - Si pide requisitos, elementos, causales, condiciones o etapas: enuméralos todos, sin omitir ninguno, en una oración separada por punto y coma.
  - Si pregunta si algo procede, existe, es posible o es verdadero o falso: empieza con «Sí», «No», «Verdadera» o «Falsa» y luego da la regla que lo determina.
  - Si pregunta por una sentencia: di lo que la sentencia plantea o decide (problema jurídico, hechos, regla o decisión), no datos del expediente ni del trámite.
  - Si pide una definición: da la definición legal o doctrinal precisa.
- Usa solo los pasajes que tratan la figura o institución por la que se pregunta. Si los pasajes tratan otra figura u otro tipo de contrato, ignóralos y responde con tu conocimiento del derecho colombiano, sin citar normas.
- En "respuesta" menciona solo la norma principal. No agregues normas, sentencias ni datos que la pregunta no pide.
- "palabras_clave": de 3 a 6 términos jurídicos clave de la respuesta.
- "referencia_legal": la norma o el artículo principal que fundamenta la respuesta y, si aplica, otras normas pertinentes de los pasajes (por ejemplo «Artículo 1502 del Código Civil»).""",
    "open_ended": """Formato: caso práctico que exige un análisis completo.
- "marco_normativo": las normas aplicables tomadas de los pasajes, separadas por punto y coma, cada una con una frase breve sobre lo que regula.
- "analisis": de 5 a 8 oraciones. La primera oración responde directamente cada pregunta del caso (qué acción procede, quién responde, si es posible o no). Luego aplica las normas a los hechos.
- "jurisprudencia": las sentencias de los pasajes que sean pertinentes y la regla que fijan; si los pasajes no traen sentencias pertinentes, escribe «No se recuperó jurisprudencia pertinente para el caso.».
- "conclusion": de 1 a 3 oraciones que respondan cada pregunta planteada en el caso.""",
}


def instrucciones(formato: str) -> str:
    if config.PROMPT_TL == "p-tl1" and formato in INSTRUCCIONES_TL1:
        return INSTRUCCIONES_TL1[formato]
    return INSTRUCCIONES[formato]

def _texto(maximo: int) -> dict:
    return {"type": "string", "minLength": 1, "maxLength": maximo}


def schema(formato: str, letras: list[str] | None = None) -> dict:
    """JSON Schema de la salida del decoder para un formato (no el de la entrega)."""
    if formato == "multiple_choice":
        letras = letras or ["A", "B", "C", "D"]
        props = {
            "justificacion": _texto(1200),
            "respuesta_correcta": {"type": "string", "enum": letras},
            "descarte_opciones": {"type": "object", "properties": {l: _texto(300) for l in letras},
                                  "required": letras, "additionalProperties": False},
        }
    elif formato == "semi_open":
        props = {
            "respuesta": _texto(1000),
            "palabras_clave": {"type": "array", "items": _texto(60), "minItems": 3, "maxItems": 6},
            "referencia_legal": _texto(300),
        }
    elif formato == "open_ended":
        props = {
            "marco_normativo": _texto(1200),
            "analisis": _texto(1800),
            "jurisprudencia": _texto(800),
            "conclusion": _texto(600),
        }
    else:
        raise ValueError(f"formato desconocido: {formato!r}")
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def letras_de(item: dict) -> list[str]:
    ops = item.get("opciones") or {}
    letras = sorted(ops) if isinstance(ops, dict) else ["A", "B", "C", "D"][:len(ops)]
    return [l for l in letras if l in ("A", "B", "C", "D")] or ["A", "B", "C", "D"]


def _con_ficha(texto: str, ficha: str | None) -> str:
    """Inserta la ficha del glosario tras la cabecera (primera linea) del pasaje."""
    if not ficha:
        return texto
    cabecera, _, resto = texto.partition("\n")
    return f"{cabecera}\n(Norma: {ficha})\n{resto}"


def _nota(texto: str) -> str:
    from generacion import glosario

    ns = glosario.notas(texto)
    return f" [nota: {'; '.join(ns)}]" if ns else ""


def mensajes(item: dict, pasajes: list[str], metas: list[dict] | None = None) -> list[dict]:
    """Mensajes de chat para el decoder. `pasajes`: texto literal de cada fragmento.

    Con `metas` (SYNTAX_GLOSARIO=on) cada pasaje lleva la ficha de su norma, y la pregunta
    y las opciones, notas de equivalencia nombre <-> numero (generacion/glosario.py).
    """
    if metas is not None:
        from generacion import glosario

        pasajes = [_con_ficha(t.strip(), glosario.ficha_pasaje(m)) for t, m in zip(pasajes, metas)]
    nota = _nota if metas is not None else (lambda _t: "")
    bloques = "\n\n".join(f"[P{i}] {t.strip()}" for i, t in enumerate(pasajes, 1))
    usuario = f"Pasajes:\n\n{bloques}\n\nPregunta: {item['pregunta'].strip()}{nota(item['pregunta'])}"
    ops = item.get("opciones")
    if ops:
        pares = ops.items() if isinstance(ops, dict) else zip("ABCD", ops)
        usuario += "\n\nOpciones:\n" + "\n".join(f"{l}. {str(t).strip()}{nota(str(t))}" for l, t in pares)
    return [{"role": "system", "content": REGLAS + "\n\n" + instrucciones(item["formato"])},
            {"role": "user", "content": usuario}]


def correccion(no_respaldadas: list[str], permitidas: list[str]) -> str:
    """Mensaje para regenerar cuando la respuesta cita normas ausentes de los pasajes."""
    return ("Tu respuesta cita normas que no están en los pasajes: " + "; ".join(no_respaldadas) + ". "
            "Reescribe el objeto JSON completo sin citarlas. Solo puedes citar estas fuentes: "
            + " ".join(permitidas))
