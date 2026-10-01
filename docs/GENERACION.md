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

Variables: `SYNTAX_LLM` (`qwen3-8b-q4` | `qwen3-4b-2507-q4`), `SYNTAX_LLM_URL`, `SYNTAX_GENERATION_K` (5), `SYNTAX_CITAR_EVIDENCIA` (`no` | `generacion` | `top10`), `SYNTAX_DEVICE` (encoder de la consulta).

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
- `enable_thinking=false` por plantilla (`--jinja`): el thinking multiplica los tokens y la latencia.
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

## 6. Resultados `e02_v0` (sample_50)

_Se completa al terminar la corrida._

## 7. Pendientes

1. **Máquina final**: medir la latencia en las candidatas (GPU NVIDIA del equipo o del campus). La corrida de las 992 y la verificación en vivo del sábado deben usar la misma máquina y la misma configuración (sección 4.2).
2. **Contenedor limpio** (2 pts de reproducibilidad): `run.sh` asume el servidor levantado y el índice presente. Falta `asegurar_indice()` (descargar el comprimido publicado o reconstruir) y decidir entre llama-cpp-python in-process o descargar el binario de llama.cpp.
3. Iteraciones según el análisis de error (`evaluation/generacion/<exp>/errores.csv`): barrido de `generation_k` y de `CITAR_EVIDENCIA`, lookup por metadata cuando la pregunta nombra norma y artículo, cuota por tipo de documento (las sentencias desplazan artículos), reranker, thinking solo en cerradas, calibración de la abstención.
4. Interfaz Streamlit sobre `responder()`.

## 8. Trampas

- En esta build de llama.cpp **`--no-mmap` ya no existe**: es `--load-mode none` (`llama-server --help | grep load-mode`).
- `llama-server` con mmap en un Mac con poca memoria libre se vuelve 5 veces más lento sin avisar: mirar `vm.swapusage` y los `timings` de la traza (`prompt_per_second`, `predicted_per_second`).
- Con temperatura 0 un reintento idéntico devuelve lo mismo: reintentar solo cambiando algo (más tokens, un mensaje de corrección).
- `sorted()` sobre tuplas de `citations` con `None` falla (`str` vs `None`): usar `key=str`.
- `evaluate.py` cuenta como error de validación cada ítem del split que falte: en humos con `--limite` es normal.
