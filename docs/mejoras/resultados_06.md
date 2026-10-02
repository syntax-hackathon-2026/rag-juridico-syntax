# Resultados del plan 06: referencias legales como candidato suave

Fecha: 2026-10-01. Rama: `sofi-local`; HEAD de partida `99eead1` (plan 05), arbol inicialmente limpio.

**Decision: prueba de concepto, desactivada por defecto.** La fase 0 encuentra cero fallos de articulo entre las preguntas con referencia explicita y fundamento de articulo evaluable del baseline. El plan establece reducir a prueba de concepto cuando hay menos de tres fallos. Se completaron parser, indice, variantes experimentales, reporte y pruebas posibles; A/B real y keep/revert final bloqueados por ausencia del indice. No se afirma mejora de calidad ni se adopta una variante.

## Fase 0 medida, sin modelo nuevo

Comando reproducible, solo lectura:

```powershell
py -3.13 src/evaluacion/analisis_referencias.py
```

Datos: `data/sample_50.jsonl` (50 items) y `evaluation/retrieval/e01_bge_m3_hibrido.jsonl` (41 preguntas evaluables del baseline). SHA256 del baseline: `8cbd75b2f2b05ff642f30671bb3462b38d8764f11bd9f7146eaa293da13097f9`. La consulta y sus referencias usan exclusivamente pregunta/opciones; los fundamentos y los IDs se cruzan solo en evaluacion.

| Fuente de extraccion | Con cuerpo | Con cuerpo + articulo explicito | Con cuerpo explicito y articulo en GT evaluable | Con articulo explicito y articulo en GT evaluable | Fallos art_hit@10 del subconjunto |
|---|---:|---:|---:|---:|---:|
| Pregunta | 14/50 | 4/50 | 4 | 3 | 0/4 |
| Pregunta + opciones | 15/50 | 4/50 | 4 | 3 | 0/4 |

Los cuatro casos evaluables con norma explicita y articulo en GT son 600 (rank_art=2), 218 (6), 280 (1) y 865 (1). El 280 menciona cuerpo sin articulo explicito. Los cuatro con articulo explicito son 600, 218, 442 y 865; el 442 carece de GT de articulo evaluable, por lo que su rank_art nulo no se considera fallo. El 190 menciona norma pero no tiene fila evaluable en el baseline: se informa como no disponible. Incluir opciones agrega referencia en el 58. Estos conteos no demuestran que toda referencia mencionada sea pertinente: el parser oficial puede asociar citas de las opciones o de contexto.

La fase 0 usa el baseline versionado, no una corrida nueva en esta maquina. Debe repetirse si cambia el indice, la consulta o el baseline.

## Implementacion

- `src/recuperacion/referencias.py`: `referencias_de(consulta)` devuelve referencias unicas y deterministas, reutilizando `citations.extract`, `bodies` y `article_level`. No cambia regex legales, CODES ni el evaluador oficial. Comparte la normalizacion previa de `_art` con el evaluador: 1o/1 grado, 38A, 12-1, letras y espacios. `generacion/citas.py.cuerpos` ya usa la misma funcion oficial; no se le agrego dependencia de recuperacion ni se cambio su comportamiento.
- `IndiceReferencias` se construye una vez en `Retriever.__init__` desde canonico/articulo de los chunks. Resuelve todas las partes y no usa citas dentro del texto; una norma modificatoria sigue identificandose por su canonico propio. Ordena la rama lookup por senal de vigencia y chunk_id: derogado/inexequible despues de los demas. Las senales no se reinterpretan como dictamen de vigencia.
- `Retriever.retrieve`: integracion solo en hibrido, sin filtros duros. (a) agrega rama RRF con contribucion 1/(60+rank_lookup); (b) suma bonus fijo, conservando el candidato antiguo pero sin bonus cuando existe alternativa sin senal derogado/inexequible; (c) inserta hasta m candidatos de articulo en cabeza, sin duplicados y respetando k. Todas las partes entran como candidatos, aunque el recorte top-k puede excluir algunas. Las ramas originales nunca se filtran. Se registra rank_lookup cuando hay matches.
- No hay lookup para cuerpo sin articulo. El boost opcional de documento/anio/tipo se omite, dada la escasa senal de la fase 0. Mencionar solo norma o sentencia devuelve la referencia oficial pero conserva el ranking actual.
- `src/config.py`: `SYNTAX_LOOKUP=off|on`, `SYNTAX_LOOKUP_VARIANTE=a|b|c`, `SYNTAX_LOOKUP_FUENTE=consulta|pregunta`, `SYNTAX_LOOKUP_BONUS=0.005`, `SYNTAX_LOOKUP_M=2`. Se validan valores; defaults experimentales sin seleccionar por calidad. No se modificaron los parametros de los planes 03/04, ni se implemento backend de reranker.
- Fuente `consulta` usa el mismo texto que BM25/denso; `pregunta` mantiene la consulta pregunta+opciones para esas ramas y envia pregunta separada al lookup mediante `consulta_lookup`. `responder` y `retrieval_eval` pasan esa entrada solo si lookup esta on y fuente=pregunta; nunca envian legal_basis, respuestas esperadas o id al lookup. Una llamada directa a retrieve en ese modo debe proporcionar consulta_lookup para evitar extraer opciones accidentalmente.
- `retrieval_eval.py`: referencias explicitas por pregunta, subconjuntos con/sin referencia y denominadores separados, art_hit@10, respaldo@10 y control doc_hit/MRR. Se preservan metricas top-40 y archivo meta del plan 05. Cada corrida genera .meta.json con lookup/fuente/variante/parametros; CSV conserva 35 columnas y registra configuracion y subconjuntos en notas. `--techo-reranker` requiere lookup off para seguir midiendo RRF puro. El tiempo de las referencias de diagnostico se excluye de la latencia de recuperacion.
- `src/main.py` agrega lookup a meta.retrieval; `evaluar_entrega.py` usa esa meta, no la configuracion de la maquina que evalua, para registrar lookup en notas del CSV. Solo con lookup on, las trazas agregan una seccion lookup con configuracion y matches_top (chunk_id/rank_lookup); apagado conserva los campos anteriores.
- `analisis_referencias.py --comparar` informa ganancias de articulo en referencias explicitas, perdida de cualquier acierto documental/articulo y control MRR en el resto. Exige IDs unicos, iguales y mismos fundamentos. Calcula keep de conteos sin cambiar flags. No valida automaticamente la pertinencia juridica ni reemplaza la inspeccion de los pasajes.

## Pruebas y controles ejecutados

| Comprobacion | Resultado |
|---|---|
| `py -3.13 -m pytest tests -q` | 63 pasaron, 1 omitida |
| Pruebas nuevas del parser y fixture | Ejemplos oficiales, listas de articulos, canonicos de cabeceras, normalizacion, partes, articulo ausente, modificatorias, vigencia, variantes a/b/c, scores, no duplicados/filtros, igualdad sin referencias, textos/offsets intactos y determinismo |
| Guardia de runtime y fuente | Pregunta separada de opciones, ground truth no pasa al lookup; reporte del subconjunto coherente |
| Regresion planes 04/05 | Sus 25 y 5 pruebas siguen pasando, sin editarlas |
| Comparacion sintetica contra el retriever de HEAD 99eead1 | 27 comparaciones exactas de todos los campos de RetrievedChunk: 3 modos, k=1/10/40, 3 consultas, lookup off |
| Fase 0 offline | Conteos de la tabla, con parser oficial y baseline versionado |
| A/B real baseline y variantes a/b/c | Los cuatro intentos terminan con exit 2: falta chunks.jsonl/BM25; sin escritura de metricas ni filas ficticias |
| `py -3.13 src/reproducibilidad/verificar_deps.py` | ok: nueve paquetes usados declarados y fijados; sin deps nuevas |
| `git diff --check` | Sin errores de whitespace |

La prueba omitida compara cabeceras de una muestra de chunks reales; falta chunks.jsonl. La fixture de ocho chunks es sintetica, identifica sus URLs como example.invalid y no es corpus para publicacion. Se probaron dos rankings identicos con ramas simuladas; no se midio determinismo del encoder real, generacion ni latencia de la maquina final. Los tiempos de pytest no son latencias de retrieval.

## Bloqueos y comandos pendientes para el equipo

Faltan corpus/indice locales, BM25/FAISS/chunks.jsonl y en el Python 3.13 disponible no estan torch ni sentence-transformers. Hay pytest y numpy; no existe .venv en este worktree. No se descargaron modelos ni se reconstruyo el indice. La fase 0 no requiere modelos, decoder o credenciales. La generacion y RAGAS siguen pendientes de comprobar decoder, dependencias del juez y credenciales; no se usaron.

En una maquina que ya tenga el corpus/indice congelado y bge-m3 cacheado, activar el entorno Python 3.13 con requirements.txt fijado. Usar `python` del entorno (en Windows sin activar entorno, `py -3.13`):

```powershell
$env:SYNTAX_ABSTENCION = "off"
$env:SYNTAX_RERANKER = "off"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
python src/reproducibilidad/verificar_corpus.py
python src/evaluacion/analisis_referencias.py

foreach ($taskFuente in @("consulta", "pregunta")) {
    $env:SYNTAX_LOOKUP_FUENTE = $taskFuente
    $env:SYNTAX_LOOKUP = "off"
    python src/evaluacion/retrieval_eval.py --modo hibrido --experimento "e06_sin_lookup_$taskFuente"
    foreach ($taskVariante in @("a", "b", "c")) {
        $env:SYNTAX_LOOKUP = "on"
        $env:SYNTAX_LOOKUP_VARIANTE = $taskVariante
        python src/evaluacion/retrieval_eval.py --modo hibrido --experimento "e06_lookup_${taskVariante}_$taskFuente"
        python src/evaluacion/analisis_referencias.py --baseline "evaluation/retrieval/e06_sin_lookup_${taskFuente}_hibrido.jsonl" --comparar "evaluation/retrieval/e06_lookup_${taskVariante}_${taskFuente}_hibrido.jsonl"
    }
}
$env:SYNTAX_LOOKUP = "off"
```

Los flags offline impiden descargar implicitamente el encoder: cache ausente implica fallo. Cada comparacion conserva pregunta+opciones para las ramas originales; solo cambia la fuente del lookup. Un cambio por experimento, con bonus/m fijos. Revisar el detalle por ID, las regresiones y referencias no pertinentes introducidas por las opciones. La seccion de comandos no representa corridas realizadas.

**Keep:** al menos dos ganancias de art_hit@10 con referencia explicita y ningun acierto previo de documento/articulo fuera del top-10, sin bajar doc_hit/MRR del resto. **Revert:** ganancias nulas o perdida de aciertos. A igualdad gana off; entre variantes que cumplan, preferir la mas simple (a antes de c). La fase 0 actual no ofrece dos fallos de articulo explicito para recuperar: no se espera justificar keep sobre este baseline. Si las nuevas medidas muestran lo mismo, cerrar como prueba de concepto. El reordenamiento top-5 puede ayudar o perjudicar generacion aunque @10 no cambie; no cumple por si solo el criterio del plan.

La insercion (c) puede desplazar evidencia y hacer que el score del primer candidato sea menor que el del segundo; no se habilita por defecto. Vigencia solo prioriza la rama lookup: no se suprime evidencia antigua ni se reordena por fuerza una rama semantica que ya la favorecia. Mantener estas limitaciones al revisar el A/B.

Si se adopta lookup tras cumplir keep, repetir el barrido generation_k del plan 03 y recalibrar el plan 04 con nuevas trazas y sensibilidad por formato, manteniendo abstencion off hasta su propio criterio keep. Mientras lookup este off, no se requiere repetirlos por esta prueba de concepto. La medicion del techo del plan 05 conserva lookup off; si despues se decide combinarlos, medir la combinacion por separado.

No se hizo commit, push, merge ni cambios en main. Los problemas de acceso al worktree en el sandbox requirieron ejecucion escalada para leer, editar y probar dentro de esta rama.
