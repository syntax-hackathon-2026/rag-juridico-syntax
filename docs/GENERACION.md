# Generación: estado y contexto

Contexto para quien continúe el RAG después de la recuperación. Resume lo construido el 2026-09-30 (rama `santiago`), las decisiones y su motivo, lo medido y lo que falta. Las reglas generales están en `CLAUDE.md` y la indexación en `docs/INDEXACION.md`; este documento no las repite.

## 1. Estado en una línea

`pregunta → híbrido top-10 → Qwen3-8B (llama.cpp local) → citas validadas ⊆ top-10 → schema → JSONL` funciona de punta a punta sobre `sample_50` (corrida `e02_v0`, sección 6). Es el v0 de `CLAUDE.md`: sin reranker, sin lookup por metadata y con una abstención mínima. Cuello de botella actual: **latencia** (~145 s por pregunta en un Mac M1 de 16 GB con memoria compartida); falta elegir y medir la máquina final.

## 2. Comandos

```bash
# decoder (una vez por máquina)
brew install llama.cpp                                  # Mac; Windows/Linux: binario de GitHub releases (CUDA/CPU)
python src/generacion/modelo.py descargar               # GGUF -> modelos/ (revisión + sha256 fijos)
python src/generacion/modelo.py servir                  # otra terminal; 127.0.0.1:8080
python src/generacion/modelo.py verificar               # responde y sirve el GGUF configurado

# generar
python src/main.py --split sample --limite 5            # humo
python src/main.py --split sample --experimento e02_v0  # sample_50 -> salidas/sample_e02_v0.jsonl (+ trazas)
python src/main.py --split sample --ids 51 60           # regenerar ítems concretos
python src/main.py --split sample --generation-k 7 --experimento e04_k7 --ids ...  # barrido plan 03
python src/main.py --split test                         # sábado: data/test_992.jsonl -> submissions.jsonl

# evaluar y registrar (legal_basis solo aquí)
python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_e02_v0.jsonl --experimento e02_v0 [--ragas]
python src/evaluacion/comparar_entregas.py a.jsonl b.jsonl [--ids ...]   # determinismo / verificación en vivo
```

Variables: `SYNTAX_LLM` (`qwen3-8b-q8` por defecto | `qwen3-8b-q4` | `qwen3-4b-2507-q4`), `SYNTAX_LLM_URL`, `SYNTAX_GENERATION_K` (5), `SYNTAX_CITAR_EVIDENCIA` (`no` | `generacion` | `top10`, por defecto `top10`), `SYNTAX_PENSAR_FORMATOS` (vacío; p. ej. `multiple_choice`) y `SYNTAX_PENSAR_TOKENS` (768), `SYNTAX_FILTRO_CITA` (`todo`) y `SYNTAX_LOOKUP` (`on`) de la recuperación, `SYNTAX_DEVICE` (encoder de la consulta).

`main.py` escribe línea a línea y **se reanuda**: si una corrida se cae, se relanza el mismo comando y salta los ids ya escritos (`--sin-reanudar` empieza de cero). Al final reordena, valida todo contra el schema y sale con 1 si hay errores.

## 3. Archivos

| Archivo | Qué hace |
|---|---|
| `src/generacion/modelo.py` | Descarga y verifica el GGUF; arma y lanza el comando de `llama-server`; comprueba el servidor y registra la build de llama.cpp. |
| `src/generacion/llm.py` | `Decoder.generar(mensajes, schema, max_tokens) -> Respuesta`: cliente HTTP stdlib a `/v1/chat/completions`. Única interfaz con el motor. |
| `src/generacion/prompts.py` | `PROMPT_VERSION = "p-v0"`. Reglas comunes, instrucciones por formato y el JSON Schema de la salida del decoder. |
| `src/generacion/citas.py` | Validación determinista con `scripts/citations.py`: `permitidas(top10)`, `sin_respaldo`, `quitar_oraciones`, `citas_evidencia`. |
| `src/generacion/postproceso.py` | Recortes de longitud, armado del registro y validación con `jsonschema` contra `schema/submission.schema.json`. |
| `src/generacion/abstencion.py` | Regla v0 y señales registradas para calibrar. |
| `src/generacion/responder.py` | `responder(item, retriever, decoder) -> (registro, traza)`: orquesta todo, sin estado global (reutilizable por la interfaz). |
| `src/main.py`, `run.sh` | Comando único. |
| `src/evaluacion/evaluar_entrega.py` | Evaluador oficial + diagnóstico por pregunta + fila en `experiments.csv`. Deja `evaluation/generacion/<exp>/{reporte.json, errores.csv, entrega.jsonl, trazas.jsonl, meta.json}`. |
| `src/evaluacion/comparar_entregas.py` | Compara normas citadas y pasajes por id (criterio de la verificación en vivo). |
| `src/recuperacion/consulta.py` | `consulta_de(item)`: la misma consulta en la medición y en el runtime. |

## 4. Decisiones y por qué

### 4.1 Decoder local con llama.cpp

- **Qwen3-8B Q4_K_M del repo oficial** `Qwen/Qwen3-8B-GGUF`, con revisión y sha256 fijados en `config.LLM_MODELOS`. El mismo archivo corre en Mac (Metal), Windows y Linux (CUDA), así que los resultados de dos máquinas se pueden comparar si comparten la build de llama.cpp.
- **`llama-server` por HTTP en `localhost`**. Todo corre en local; "servidor" es solo un proceso aparte. El pipeline habla con él a través de una interfaz única, y la interfaz gráfica puede reutilizar el mismo proceso. El backend in-process (llama-cpp-python) queda para cuando se resuelva el contenedor limpio (sección 7).
- **Plan B `qwen3-4b-2507-q4`** (`unsloth/Qwen3-4B-Instruct-2507-GGUF`; Qwen no publica un GGUF oficial del 2507). Es un modelo sin thinking.

### 4.2 Determinismo (temperatura 0 y verificación en vivo)

- `temperature=0` (greedy), `seed=0`, un solo slot (`-np 1`: el batching entre peticiones cambia la numérica) y **`cache_prompt=false`**, porque la documentación de llama-server advierte que reutilizar la caché KV puede dar logits distintos según el tamaño de lote. Cuesta reprocesar el prefijo en cada pregunta.
- `enable_thinking=false` por plantilla (`--jinja`): el thinking multiplica los tokens y la latencia, y en las cerradas no mejoró (sección 6, `e10`). Se puede activar por formato con `SYNTAX_PENSAR_FORMATOS`: llama-server separa el razonamiento en `reasoning_content` (va solo a la traza), aplica la gramática del schema después y respeta el tope `thinking_budget_tokens` por petición (`reasoning_budget` lo ignora).
- **Medido**: dos corridas de los mismos 3 ítems (una con mmap y otra sin mmap) dan **salidas idénticas** en redacción, citas y pasajes (`comparar_entregas.py`: 0 diferencias).
- Congelar para la entrega: GGUF + sha256, build de llama.cpp (hoy `0.5.0, build 11146`; se registra en `meta.json` de cada corrida), `PROMPT_VERSION`, `GENERATION_K`, `CITAR_EVIDENCIA` y el índice (`sha256_chunks`).

### 4.3 Salida estructurada por gramática

El JSON Schema de cada formato va como `response_format` y llama.cpp lo convierte en gramática: la salida siempre parsea y las claves salen en el orden del schema. En cerradas el orden es `justificacion → respuesta_correcta → descarte_opciones`, así el modelo razona antes de elegir la letra. `descarte_opciones` pide las cuatro letras (la elegida con «Es la opción correcta.») y el postproceso quita la elegida. Si la salida se corta por longitud, hay un reintento con 1,6 veces los tokens. Repetir la misma llamada no sirve: con temperatura 0 da lo mismo.

### 4.4 Citas (paso 4 del enunciado)

1. `permitidas(top10)` = cuerpos de `citations.extract` sobre el texto de los 10 pasajes. Es exactamente `evaluate.citas_respaldadas`.
2. Todo el texto de la respuesta (también `descarte_opciones` y `palabras_clave`) se valida contra ese conjunto **a nivel de cuerpo**, que es como puntúa el evaluador.
3. Si hay citas sin respaldo: se regenera 1 vez con la lista de fuentes permitidas; si persisten, se quitan las oraciones que las contienen; si eso deja vacío un campo obligatorio, el sistema se abstiene.
4. **`CITAR_EVIDENCIA=generacion`**: se agregan las cabeceras de los pasajes que vio el decoder ("Fuentes consultadas: Artículo 46 de la Ley 472 de 1998. …"), una por cuerpo. Van en `justificacion` en cerradas, en `referencia_legal` en semiabiertas (no va al juez RAGAS) y en `marco_normativo` en abiertas. Motivo: el evaluador puntúa por cuerpo; una cita correcta y respaldada vale 1, y una no pertinente pero respaldada vale 0 **sin penalización**. Todas son normas efectivamente recuperadas. Es un experimento: comparar `no`, `generacion` y `top10`.

Límite conocido: la validación es a nivel de cuerpo. Si el modelo cita "artículo 58 de la Constitución" y en los pasajes solo está el artículo 2, la cita pasa. El evaluador tampoco lo distingue, pero el enunciado pide que el artículo citado figure en los pasajes. Endurecerlo a nivel de artículo es una iteración posible.

### 4.5 Abstención

Regla v0 (`abstencion.py`): solo se abstiene por `sin_pasajes`, `salida_invalida` o `citas_irreparables`. Abstenerse da 0,5 en el componente de 10 pts, pero 0 en exactitud, en RAGAS (las abstenciones cuentan como cero) y en citación. Cada traza registra señales para calibrar después: score y margen top1–top2, ranks de BM25 y denso del top-1, fracción del top-10 presente en ambas ramas, cuerpos distintos, sentencias en el top-10 y normas nombradas en la pregunta que aparecen en la evidencia.

### 4.6 Guarda contra el ground truth

`responder.entrada_runtime()` deja pasar solo `id, formato, pregunta, opciones`. `legal_basis` y las respuestas solo se leen en `src/evaluacion/`.

## 5. Latencia medida (Mac M1, 16 GB, 7 núcleos de GPU, 2026-09-30)

Los mismos 3 ítems (51 cerrada, 24 semiabierta, 247 abierta) y `generation_k=5` (~2.200–2.900 tokens de prompt):

| Configuración | prefill | generación | s por pregunta |
|---|---:|---:|---:|
| 8B Q4_K_M, mmap (defecto) | 13 tok/s | 2,2 tok/s | 94–375 |
| 8B Q4_K_M, `--load-mode none` | 38 tok/s | 4,8 tok/s | 83–206 (media 145) |
| 4B-2507 Q4_K_M, `--load-mode none` | 60 tok/s | 7 tok/s | 67–158 (media 111) |

- El M1 debería dar ~12 tok/s de generación con un 8B Q4; aquí rinde menos porque la máquina tiene ~6–7 GB en swap (el encoder en el proceso de Python ocupa ~4 GB, más Cursor, Zoom y el navegador). Con mmap, macOS desalojaba páginas del modelo: de ahí `--load-mode none` (antes `--no-mmap`) en `modelo.py`.
- El 4B no resuelve el problema en esta máquina: es solo ~1,3 veces más rápido y escribe más tokens.
- **Para las 992 hay que llegar a menos de ~20 s por pregunta**: hace falta una GPU dedicada (NVIDIA con ≥ 8 GB, o un Mac con más memoria libre). Medir allí con `main.py --limite 10` antes del sábado. Palancas sin cambiar de modelo: `generation_k=3` (reduce el prefill ~35 %), descartes más cortos en cerradas (la generación domina en las abiertas) y cerrar las demás aplicaciones.

## 6. Resultados (sample_50, RTX 4090, Qwen3-8B)

| corrida | cambio | cerradas | RAGAS | citación | abstención | total /80 |
|---|---|---:|---:|---:|---:|---:|
| `e02_v0` | corpus v1, Q4, Mac | 11/15 | — | 15,10 | 7,91 | — |
| `e04_v3_rtx4090` | corpus v3, Q4 | 10/15 | — | 14,69 | 7,44 | — |
| `e05_q8_rtx4090` | Q8_0 | 11/15 | 0,472 | 14,69 | 7,67 | 51,19 |
| `e08_filtro` | filtro solo por cita (`todo`) | 11/15 | 0,462 | 14,69 | 7,67 | 50,90 |
| `e08b_top10` | + `CITAR_EVIDENCIA=top10` | 11/15 | 0,466 | **16,33** | **8,37** | 53,34 |
| `e13_lookup` | + lookup variante a | 11/15 | 0,502 | 16,33 | 8,37 | **54,43** |
| `e14_final` | defaults, sin variables | idéntica a `e13` (determinismo) | | | | |

Experimentos solo de cerradas (`--ids` de las 15; REVERT):

| corrida | cambio | cerradas | efecto |
|---|---|---:|---|
| `e09_prompt_mc` | prompt p-v1: elegir con conocimiento propio, analizar cada opción antes de la letra | 10/15 | arregla 647; rompe 308 y 528 |
| `e10_thinking_mc` | thinking, tope 768 | 10/15 | arregla 647; rompe 528 y 748; ~10 s/cerrada |
| `e10b_thinking_mc_1536` | thinking, tope 1536 | 9/15 | rompe 528 y 748; ~15 s/cerrada |
| `e11_genk10_mc` | generation_k=10 | 11/15 | mismas 15 letras |

- **Cerradas**: lo que se podía arreglar era recuperación. Con v3, las sentencias nuevas copaban el top-10 (#748 pasaba de A a D); con el filtro, #748 vuelve a A y #51, #290 y #352 recuperan su norma arriba. El neto en el sample es 0 porque #671 (doctrina pura, sin norma en el corpus) cambia de C a B con otros pasajes. Fallos que quedan: #58 (el banco da por correcta «Ley 1564 de 2002», errata del CGP), #128 (fintech: opinión, no norma), #647 (definición doctrinal de «ayuda» del C.C. art. 176) y #671. Prompt, thinking y k no los resuelven sin romper otras: con 15 cerradas, 1 pregunta = 6,7 puntos y las variaciones están en el ruido.
- **RAGAS no es reproducible entre corridas**: `e08b` y `e13` difieren en solo 2 respuestas (#600, cerrada, y #218), pero RAGAS pasa de 0,466 a 0,502. El juez (OpenRouter) agrega ruido de ±0,02–0,04 en 35 ítems: no ajustar prompts de texto libre con una sola corrida del juez.
- **`CITAR_EVIDENCIA=top10`**: recupera las citas de #674, #879 y #1073 (cuerpo en ranks 7–9 que el decoder no veía) y, con ellas, su acierto en abstención. Sin costo en RAGAS.
- Latencia media 4,3 s/pregunta (recuperación ~0,1 s en caliente): ~1,2 h para 992.

Corridas del 2026-10-02 (noche, corpus v4, rama `santiago-agentico`; sección 9):

| corrida | cambio | cerradas | RAGAS | citación | abstención | total |
|---|---|---:|---:|---:|---:|---:|
| `e21_base` | e20 rehecha (0 diferencias) | 11/15 | — | 17,55 | 8,37 | 40,59/50 |
| `e22_glosario` | glosario de normas en el prompt | **12/15** | — | 17,55 | 8,60 | **42,15/50** |
| `e23_prompt_mc` | + reglas de decisión p-v2 (REVERT) | 12/15 (mismas letras) | — | 17,55 | 8,60 | 42,15/50 |
| `e24_final` | defaults (glosario on), idéntica a e22 | 12/15 | 0,440 | 17,55 | 8,60 | **55,35/80** |

## 9. Cerradas y recuperación agéntica (2026-10-02)

**Diagnóstico.** Las cerradas estaban fijas en 11/15 desde `e05`, aunque la recuperación mejoró. En las cerradas la recuperación ya es casi perfecta (`r21_base`: doc_hit@10 = 1,0 y art_hit@10 = 0,86 en las 13 con `legal_basis`), así que los fallos están en la generación. Fallaban siempre las mismas cuatro:
- **#58**: la opción correcta es «Ley 1564 de 2002», errata del CGP. El CGP estaba en el top-1, pero su cabecera no dice «Ley 1564» y el decoder descartaba la opción por «no mencionada en los pasajes».
- **#128** (fintech) y **#671** (regla de desempate de los CDI): doctrina que no está en el corpus.
- **#647**: definición doctrinal de «ayuda» (C.C. art. 176, que sí está en el corpus pero no llega al top-10).

**Glosario (KEEP, `SYNTAX_GLOSARIO=on` por defecto, `generacion/glosario.py`).**
- Debajo de la cabecera de cada pasaje va la línea `(Norma: <titulo del manifest>)`. Las normas que nombran la pregunta y las opciones llevan `[nota: ...]`: la equivalencia nombre ↔ número o, si el número existe con otro año, el aviso «probablemente se refiere a …».
- Solo se usan títulos que aportan algo (paréntesis o coma) y que, si el decoder los copia, no extraen otra norma: «Codigo Civil (Ley 57 de 1887)» queda fuera porque daría una cita espuria.
- `pasajes_recuperados.texto` no cambia.
- Arregla #58 sin regresiones; `prompt_version` pasa a `p-v0+glosario`.

**Probado y descartado (REVERT, flags apagados):**
- **Reglas de decisión p-v2** (`SYNTAX_PROMPT_MC=p-v2`): «ausencia en los pasajes ≠ falsedad», opciones meta, cálculo explícito. Mismas 15 letras.
- **Una consulta por opción** (`SYNTAX_CONSULTA_OPCIONES=on`, `recuperacion/consulta.py` + `Retriever.retrieve_multi`): doc_hit@10 baja de 0,902 a 0,878 (pierde #748), con peso 1 y con 0,5. No gana ningún artículo.
- **Planificador** (`SYNTAX_PLANIFICADOR=on`, `generacion/planificador.py`): una llamada corta al 8B que reformula la consulta y propone normas con artículo para el lookup.
  - Con ejemplos reales en el prompt (plan-v1), el 8B los copia en casi todas las preguntas: «artículo 25 del CGP» en 16 de 41. Sin ejemplos (plan-v2), acierta el artículo en solo 3 de 39 planes, y los artículos inventados arrastran documentos equivocados (doc_hit@10 0,805, respaldo@10 0,866).
  - Solo con las reformulaciones (`SYNTAX_PLAN_NORMAS=off`), doc_hit@10 queda en 0,805–0,829, peor que la línea base (0,902).
  - El aparente +3,6 puntos de respaldo de plan-v1 era un artefacto: los artículos copiados meten cuerpos populares (CGP, Constitución) en el top-10.
  - **Conclusión: Qwen3-8B sin thinking no recuerda números de artículo con fiabilidad, y la multi-consulta diluye el RRF.** No volver a intentarlo sin otra señal, como un reranker o el thinking solo en el planificador.
- Lo que queda en cerradas es para la revisión del corpus: doctrina sobre leasing y fintech, modelo de convenio OCDE (regla de desempate), el decreto anual del SMLMV (cuantías, #528) y el art. 176 del C.C. para #647.

## 10. Texto libre (2026-10-02, noche)

**Diagnóstico.** El texto libre vale 30 puntos y es el componente más lejos del máximo: RAGAS 0,42–0,46 con el corpus v4, y el prompt seguía en `p-v0`. Juez por ítem sobre `e24_final` (**J1**, `evaluation/juez/j1_e24_final.csv`): 0,4573, y esta vez **ningún ítem sin veredicto**. En la corrida anterior de la misma entrega hubo 3 (0,4401). Los ítems sin veredicto son ruido intermitente del juez, no un patrón del texto. Lo peor puntuado, por patrón:
- casos con narrativa (#513 0,21, #247 0,22, #1073 0,22, #679 0,32), donde falta la norma decisiva o el razonamiento;
- sentencias nombradas con la sección equivocada en el top-5 (#190 0,21, #946 0,38);
- forma (#490 0,32, #24 0,36): enumeraciones incompletas, o anclaje a pasajes de otra figura.

**Flags (todos apagados por defecto, `src/config.py`):**
- `SYNTAX_PROMPT_TL=p-tl1` (`prompts.INSTRUCCIONES_TL1`; `prompt_version` suma `+tl1`). En semi_open:
  - la forma depende de la pregunta: una línea si pregunta qué artículo; la enumeración completa en una oración con punto y coma si pide requisitos; «Sí»/«No» primero en las de procedencia o verdadero/falso;
  - se ignoran los pasajes de otra figura;
  - en `respuesta` va solo la norma principal; las demás, en `referencia_legal`, que el juez no ve.
  - En open_ended, `analisis` empieza con la respuesta directa. Las cerradas no cambian, así que su caché del decoder sigue valiendo.
- `SYNTAX_SECCION_SENTENCIA=on` (`generacion/seleccion.py`). Si la pregunta nombra una sentencia:
  - sus fragmentos de la sección pedida suben dentro del top-10 (problema jurídico → síntesis/consideraciones, con preferencia por el texto que trae la frase; hechos → antecedentes; decisión → resuelve);
  - los salvamentos y las aclaraciones de voto bajan al final, porque en #563 y #1015 ocupaban el top-5;
  - solo cambia lo que ve el decoder: el top-10 de la entrega, la citación y la abstención no se tocan.
- `SYNTAX_PENSAR_CASOS=40`: thinking (`PENSAR_TOKENS`) en el texto libre cuya pregunta tiene ≥ 40 palabras (10 de 35 en sample_50).

**Método.** `main.py --replay-trazas evaluation/generacion/e24_final/trazas.jsonl` (`recuperacion/fijo.py`) repite el top-10 de `e24_final` con el texto y la metadata reales de `chunks.jsonl` del índice v4 (mismo `sha256_chunks`), sin cargar bge-m3 ni FAISS junto al decoder. Fidelidad comprobada: el pipeline completo en el Mac sobre #280 y #589 salió entero del caché que había llenado el replay, es decir, con peticiones idénticas. Brazos en el Mac con Q4 (`salidas/run_noche.sh`):

| brazo | flags |
|---|---|
| A | `p-v0` |
| B | `p-tl1` |
| C | B + `SECCION_SENTENCIA=on` |
| D | B + `PENSAR_CASOS=40` |

El juez (J2 = A, J3 = B, C y D en una corrida) se pasa solo sobre los ítems cuyo texto difiere, y la comparación es pareada por ítem (`juez_por_item.py comparar`).

Regla fijada antes de medir:
- **KEEP** si la media pareada es ≥ +0,03 y los ítems que mejoran (> +0,02) superan en ≥ 2 a los que empeoran;
- la citación y la abstención no bajan;
- empate ⇒ REVERT.

B se compara contra A; C y D, contra B.

**Resultados (Mac, Q4, replay de `e24_final`, 2026-10-03).** Parte determinista idéntica en todos los brazos: cerradas 16,0, citación 17,55, abstención 8,60, 0 errores. Juez: J2 (A), J3 (B, C y D) y J4 (E), en `evaluation/juez/`.

| comparación | ítems | media pareada | mejoran / empeoran | decisión |
|---|---:|---:|---:|---|
| B (`p-tl1`) vs A (`p-v0`) | 35 | −0,025 | 12 / 16 | **REVERT** |
| C (B + sección) vs B | 7 que cambian | +0,081 | 5 / 1 | pasa, pero sobre un prompt descartado |
| D (B + thinking en casos) vs B | 10 que cambian | +0,003 | 5 / 4 | **REVERT** (#1005: 0,60 → 0,22) |
| E (`p-v0` + sección) vs A | 7 que cambian | −0,002 | 1 / 3 | **REVERT** |

- **`p-tl1` empeora.** Las respuestas más cortas y sin normas secundarias pierden afirmaciones que el juez sí contaba como verdaderos positivos. La hipótesis de los falsos positivos no se sostuvo.
- **La sección de sentencia solo ayudaba a reparar lo que `p-tl1` había roto.** Con `p-v0`, el resultado es neutro: #946 sube de 0,43 a 0,76, pero #140 baja de 0,57 a 0,36.
- **El thinking en casos es neutro en promedio** y duplica la latencia de esos ítems.
- **Ningún flag se activa.** La configuración de la entrega sigue siendo la de `e24_final`. Las 4 corridas del juez quedan como línea base por ítem para lo que venga.
- Lo que sigue para el texto libre ya no es de prompt: es de recuperación en los casos con narrativa (#247: la Ley 472 no llega al top-10) y de corpus.

**Confirmación en la 4090:** no hace falta, porque ningún flag salió KEEP.

**Confirmación en la 4090 (sábado temprano, M1).** Se activan solo los flags KEEP:

```
git pull
$env:SYNTAX_PROMPT_TL="p-tl1"; $env:SYNTAX_SECCION_SENTENCIA="on"     # los que hayan salido KEEP
python src/main.py --split sample --experimento e25_tl --sin-reanudar
python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_e25_tl.jsonl --experimento e25_tl
python src/evaluacion/comparar_entregas.py evaluation/generacion/e24_final/entrega.jsonl salidas/sample_e25_tl.jsonl
python src/evaluacion/juez_por_item.py juzgar --experimento j4_e25_tl --entrega e25=salidas/sample_e25_tl.jsonl --solo-cambiados-vs evaluation/generacion/e24_final/entrega.jsonl
python src/evaluacion/juez_por_item.py comparar evaluation/juez/j1_e24_final.csv:e24 evaluation/juez/j4_e25_tl.csv:e25
```

- Parte determinista: cerradas 12/15, citación 17,55 y abstención 8,60 iguales a `e24_final`.
- Juez: la misma regla de arriba.
- Si pasa, los flags KEEP pasan a ser el valor por defecto en `config.py` **antes de la corrida final de las 11:00** (`docs/SABADO.md` §4). La entrega de respaldo de las 09:05 puede salir con los valores anteriores: es solo respaldo.

## 7. Pendientes

1. **Máquina final**: medir la latencia en las candidatas (GPU NVIDIA del equipo o del campus). La corrida de las 992 y la verificación en vivo del sábado deben usar la misma máquina y la misma configuración (sección 4.2).
2. **Contenedor limpio** (2 pts de reproducibilidad): `reproducir.py` ya encadena entorno → corpus → índice → decoder (binario de llama.cpp b11146) → preguntas → evaluar, por etapas (`--solo/--desde/--hasta`) y con selección de preguntas (`--entrada/--ids/--rango/--limite/--particion`); `run.sh` sigue asumiendo el índice presente y el servidor levantado. Verificado en la RTX 4090 (2026-10-02, desde un `.venv` y un `herramientas/` nuevos, a partir de los 588 `.txt`): `--solo entorno` (torch cu126, `pip check` limpio) 2,9 min, `--solo indice` (bge-m3, 113.519 fragmentos) 32 min, y `--desde preguntas` sobre sample_50 con llama.cpp b11146 y Qwen3-8B Q8_0 recién descargados (sha256 verificado): 37,03/50 sin juez (igual a `e05_q8_rtx4090`), 12,6 s/pregunta (~3,5 h para 992) y entrega idéntica a la de `e05` (`comparar_entregas.py`: 0 diferencias en citas, pasajes y redacción). Pendiente: descargar el índice publicado en vez de reconstruirlo (32 min), y bajar la latencia por debajo de 10 s/pregunta.
3. Iteraciones según el análisis de error (`evaluation/generacion/<exp>/errores.csv`): barrido de `generation_k` y de `CITAR_EVIDENCIA`, lookup por metadata cuando la pregunta nombra norma y artículo, cuota por tipo de documento (las sentencias desplazan artículos), reranker, thinking solo en cerradas, calibración de la abstención.
4. Interfaz Streamlit sobre `responder()`.

## 8. Trampas

- En esta build de llama.cpp **`--no-mmap` ya no existe**: es `--load-mode none` (`llama-server --help | grep load-mode`).
- `llama-server` con mmap en un Mac con poca memoria libre se vuelve 5 veces más lento sin avisar: mirar `vm.swapusage` y los `timings` de la traza (`prompt_per_second`, `predicted_per_second`).
- Con temperatura 0 un reintento idéntico devuelve lo mismo: reintentar solo cambiando algo (más tokens, un mensaje de corrección).
- `sorted()` sobre tuplas de `citations` con `None` falla (`str` vs `None`): usar `key=str`.
- `evaluate.py` cuenta como error de validación cada ítem del split que falte: en humos con `--limite` es normal.
