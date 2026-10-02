"""Un item -> un registro de la entrega (y su traza). Sin estado global: lo usan
src/main.py y, mas adelante, la interfaz.

    registro, traza = responder(item, retriever, decoder)

Pasos (v0, CLAUDE.md "Arquitectura"):
  1. lista blanca del item: id, formato, pregunta, opciones (legal_basis y las
     respuestas nunca pasan de aqui).
  2. consulta = pregunta + opciones (la misma que mide retrieval_eval.py).
  3. top-10 hibrido -> pasajes_recuperados; los GENERATION_K primeros al decoder.
  4. JSON por gramatica; si se corta por longitud, un reintento con mas tokens.
  5. citas sin respaldo en los 10 pasajes -> regenerar 1 vez -> quitar esas
     oraciones -> si queda un campo vacio, abstenerse.
  6. agregar las cabeceras de la evidencia a los campos citables (CITAR_EVIDENCIA).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from generacion import abstencion, citas, postproceso, prompts  # noqa: E402
from recuperacion.consulta import consulta_de  # noqa: E402

sys.path.insert(0, str(config.ROOT / "scripts"))
from evaluate import answer_text  # noqa: E402

CAMPOS_RUNTIME = ("id", "formato", "pregunta", "opciones")
ETIQUETA_EVIDENCIA = "Fuentes consultadas:"


def entrada_runtime(item: dict) -> dict:
    """Lo unico del item que ve el sistema. El test real no trae mas que esto."""
    return {k: item[k] for k in CAMPOS_RUNTIME if k in item}


def _textos(campos: dict) -> str:
    """Todo el texto de la respuesta (tambien descarte_opciones y palabras_clave)."""
    partes = []
    for v in campos.values():
        if isinstance(v, dict):
            partes += [str(x) for x in v.values()]
        elif isinstance(v, list):
            partes += [str(x) for x in v]
        elif v:
            partes.append(str(v))
    return "\n".join(partes)


def _quitar(campos: dict, malas: set) -> dict:
    salida = {}
    for k, v in campos.items():
        if k == "respuesta_correcta":
            salida[k] = v
        elif isinstance(v, dict):
            salida[k] = {l: citas.quitar_oraciones(t, malas) or "Opción descartada." for l, t in v.items()}
        elif isinstance(v, list):
            salida[k] = [t for t in v if not (citas.cuerpos(t) & malas)]
        else:
            salida[k] = citas.quitar_oraciones(v, malas)
    return salida


def _agregar_evidencia(formato: str, campos: dict, cabeceras: list[str]) -> dict:
    if not cabeceras:
        return campos
    campo = {"multiple_choice": "justificacion", "semi_open": "referencia_legal",
             "open_ended": "marco_normativo"}[formato]
    base = campos[campo].rstrip()
    if base and not base.endswith((".", ";", ":")):
        base += "."
    return {**campos, campo: f"{base} {ETIQUETA_EVIDENCIA} {' '.join(cabeceras)}".strip()}


def _generar_json(decoder, msgs: list[dict], esquema: dict, max_tokens: int, llamadas: list,
                  pensar: bool = False) -> dict | None:
    for tokens in (max_tokens, int(max_tokens * 1.6)):
        r = decoder.generar(msgs, schema=esquema, max_tokens=tokens, pensar=pensar)
        llamada = {"ms": r.ms, "fin": r.fin, "uso": r.uso, "tiempos": r.tiempos, "texto": r.texto}
        if r.razonamiento:
            llamada["razonamiento"] = r.razonamiento
        llamadas.append(llamada)
        try:
            salida = json.loads(r.texto)
            if isinstance(salida, dict):
                return salida
        except json.JSONDecodeError:
            pass
        if r.fin != "length":  # a temperatura 0, repetir la misma llamada da lo mismo
            return None
    return None


def responder(item: dict, retriever, decoder, generation_k: int | None = None,
              regla_abstencion: abstencion.ReglaAbstencion | None = None) -> tuple[dict, dict]:
    t0 = time.perf_counter()
    generation_k = generation_k or config.GENERATION_K
    item = entrada_runtime(item)
    formato = item["formato"]
    pensar = formato in config.PENSAR_FORMATOS
    consulta = consulta_de(item)

    kwargs_lookup = ({"consulta_lookup": item["pregunta"]} if config.LOOKUP_MODO == "on"
                     and config.LOOKUP_FUENTE == "pregunta" else {})
    top = retriever.retrieve(consulta, k=config.RETRIEVAL_K, modo=config.MODO_RECUPERACION, **kwargs_lookup)
    ms_ret = (time.perf_counter() - t0) * 1000
    perm = citas.permitidas([p.texto for p in top])
    llamadas: list[dict] = []
    traza: dict = {"id": item["id"], "formato": formato, "prompt_version": prompts.PROMPT_VERSION,
                   "generation_k": generation_k, "pensar": pensar, "top": [[p.chunk_id, round(p.score, 6)] for p in top],
                   "senales": abstencion.senales(consulta, top, perm), "llamadas": llamadas}
    if config.LOOKUP_MODO == "on":
        traza["lookup"] = {
            "config": config.lookup_metadata(),
            "matches_top": [[p.chunk_id, p.meta["rank_lookup"]] for p in top
                            if p.meta.get("rank_lookup") is not None],
        }
    motivos: list[str] = []
    campos: dict | None = None

    if not top:
        motivos.append("sin_pasajes")
    else:
        gen = top[:generation_k]
        letras = prompts.letras_de(item)
        esquema = prompts.schema(formato, letras)
        msgs = prompts.mensajes(item, [p.texto for p in gen])
        salida = _generar_json(decoder, msgs, esquema, prompts.MAX_TOKENS[formato], llamadas, pensar)
        if salida is None:
            motivos.append("salida_invalida")
        else:
            campos = postproceso.normalizar(formato, salida, letras)
            malas = citas.sin_respaldo(_textos(campos), perm)
            if malas:
                traza["citas_sin_respaldo"] = sorted(map(list, malas), key=str)
                corr = prompts.correccion([citas.nombre(c) for c in sorted(malas, key=str)],
                                          citas.citas_evidencia([p.meta for p in top]))
                msgs2 = msgs + [{"role": "assistant", "content": llamadas[-1]["texto"]},
                                {"role": "user", "content": corr}]
                salida2 = _generar_json(decoder, msgs2, esquema, prompts.MAX_TOKENS[formato], llamadas, pensar)
                traza["regenerado"] = True
                if salida2 is not None:
                    campos2 = postproceso.normalizar(formato, salida2, letras)
                    if not postproceso.faltantes(formato, campos2):
                        campos = campos2
                malas = citas.sin_respaldo(_textos(campos), perm)
                if malas:
                    traza["citas_quitadas"] = sorted(map(list, malas), key=str)
                    campos = _quitar(campos, malas)
                    if citas.sin_respaldo(_textos(campos), perm):
                        motivos.append("citas_irreparables")
            if not motivos and postproceso.faltantes(formato, campos):
                motivos.append("citas_irreparables" if traza.get("citas_quitadas") else "salida_invalida")
            if not motivos and config.CITAR_EVIDENCIA != "no":
                base = gen if config.CITAR_EVIDENCIA == "generacion" else top
                cabeceras = citas.citas_evidencia([p.meta for p in base])
                completos = _agregar_evidencia(formato, campos, cabeceras)
                if not citas.sin_respaldo(_textos(completos), perm):  # nunca deberia fallar; por si acaso
                    campos = completos
                    traza["citas_agregadas"] = cabeceras

    if config.ABSTENCION_MODO == "reglas":
        regla = regla_abstencion or abstencion.cargar_regla(config.ABSTENCION_CONFIG_PATH)
        _, motivos_senales = abstencion.decidir_por_senales(
            traza["senales"], formato, regla
        )
        motivos.extend(motivos_senales)
    abst = abstencion.decidir(motivos)
    if abst:
        campos = postproceso.vacios(formato)
    traza["abstencion"] = {"abstiene": abst, "motivos": motivos}
    ms_total = (time.perf_counter() - t0) * 1000
    reg = postproceso.registro(item["id"], formato, campos, abst, [p.pasaje() for p in top], int(round(ms_total)))
    traza["citas_respuesta"] = sorted(map(list, citas.cuerpos(answer_text(reg))), key=str)
    traza["latencia"] = {"ret_ms": round(ms_ret, 1), "gen_ms": round(sum(l["ms"] for l in llamadas), 1),
                         "total_ms": round(ms_total, 1), "n_llamadas": len(llamadas)}
    traza["errores_schema"] = postproceso.validar(reg)
    return reg, traza
