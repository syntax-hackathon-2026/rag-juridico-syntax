# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> `AGENTS.md` es una réplica exacta de este archivo para otros agentes (Codex, Gemini, Cursor…). **Editar solo `CLAUDE.md` y regenerar la copia** (ver "Sincronizar AGENTS.md").

# Proyecto

Hackathon LATAM AI Week 2026 (Uniandes): **RAG de derecho colombiano** con un decoder abierto de **≤ 8B parámetros**, `temperature=0`, sobre un **corpus jurídico que construimos nosotros**. El equipo se llama **Syntax**: usar exactamente ese nombre donde las plantillas dicen `<Nombre del equipo>` (`CORPUS.md`, `README.md`, `LICENSE`, campo `equipo` de `corpus_manifest.json`, nombre del comprimido del corpus). Somos 3 (Sofía Morato, Joel David Niño, Santiago Muñoz), mezcla de Windows y Mac, con acceso a máquinas potentes en el campus.

Plazos: **vie 17:00** reporte de avance (PDF de 1 página por correo) · **sáb 09:00** se entregan las 992 preguntas · **sáb 15:00** cierre (repo + enlace público al corpus/índice) y verificación en vivo. Las 992 preguntas deben correr en ~6 h ⇒ objetivo **< 10 s/pregunta** (límite teórico 21,8 s).

Los archivos oficiales viven también en `../Hackathon 2026/` (`enunciado.pdf`, `entregables/`, `Ejemplo de entrega/`). **El código oficial y el schema mandan sobre cualquier documento, incluido este.**

## Comandos

```bash
# Autoevaluar (determinista, sin API): 20 cerradas + 20 citas + 10 abstención
python scripts/evaluate.py --submission entrega.jsonl --split sample

# Con juez de texto libre (30 pts): requiere OPENROUTER_API_KEY (env o scripts/.env, nunca versionar)
pip install -r scripts/requirements-evaluador.txt
python scripts/evaluate.py --submission entrega.jsonl --split sample --ragas
```

```bash
# Validar corpus_manifest.json contra CORPUS_DIR (corpus/ e indice/); --strict para la entrega
python src/validaciones/manifest.py
```

Todavía no existen `run.sh`, `src/main.py` ni tests, y `requirements.txt` está vacío (se llena a medida que se introducen imports; ver "Entorno y dependencias"). Contrato de entrega: `bash run.sh` o `python src/main.py --split sample` debe reconstruir el índice y generar la entrega con un solo comando. Cuando se cree el código, documentar aquí los comandos reales (ingesta, retrieval_eval, main).

## Entorno y dependencias (`src/reproducibilidad/`)

Tres scripts, solo stdlib (corren sin instalar nada, en Windows y Mac):

```bash
python3.11 src/reproducibilidad/preparar_entorno.py      # crea .venv, instala requirements.txt y verifica deps
python3.11 src/reproducibilidad/preparar_entorno.py --evaluador --recrear   # + deps del juez; .venv de cero
python src/reproducibilidad/verificar_deps.py            # exit 1 si un import de src/ no está en requirements.txt o no está fijado
python src/reproducibilidad/verificar_deps.py --fix      # agrega los faltantes ya instalados como paquete==version
python src/reproducibilidad/registrar_entorno.py --salida evaluation/entornos/<experimento>.json   # commit, python, SO, device, paquetes
```

**Regla para todos los agentes: `requirements.txt` crece junto con los imports, nunca después.** Al introducir un import de un paquete de terceros en `src/`:

1. `pip install <paquete>` dentro de `.venv` (activar con `source .venv/bin/activate` en Mac o `.venv\Scripts\activate` en Windows).
2. `python src/reproducibilidad/verificar_deps.py --fix`: agrega `paquete==version` (versión instalada, orden alfabético) a `requirements.txt`. Nunca escribir líneas sin `==`.
3. Si el nombre del import difiere del paquete de pip y no está en el diccionario `ALIAS` de `verificar_deps.py` (p. ej. `fitz`→`pymupdf`, `faiss`→`faiss-cpu`, `sklearn`→`scikit-learn`), agregarlo ahí.
4. Volver a correr `verificar_deps.py` hasta que diga `ok`, y commitear el import y la línea de `requirements.txt` **en el mismo commit**.

Detalles:

- Se escanea todo `src/` con `ast` (también los imports dentro de funciones, como el `import faiss` de `config.verificar_indice()`, que hoy falta declarar). Se ignoran stdlib, `__future__` y módulos locales (`src/*`, `scripts/*`, p. ej. `config`, `citations`).
- Import opcional a propósito (backend alternativo, detección de `torch` en `registrar_entorno.py`): marcar la línea con `# dep: opcional`, cargarlo dentro de la función que lo usa y protegerlo con `importlib.util.find_spec`. No usar el marcador para saltarse una dependencia real del pipeline.
- Deps que no se importan directamente (p. ej. `accelerate`, runtime de `transformers`) se agregan a mano con `==`; `verificar_deps.py` solo las muestra como aviso.
- `scripts/requirements-evaluador.txt` es oficial del jurado: no editarlo. Nuestras deps van solo en `requirements.txt` de la raíz.
- Ruedas de GPU (`torch` con CUDA, `llama-cpp-python` con Metal/CUDA) dependen de la plataforma: fijar la versión en `requirements.txt` y documentar en `README.md` el índice o flag de instalación por plataforma, no mantener archivos de requirements separados por máquina.
- Cada fila de `evaluation/experiments.csv` debe poder enlazar su JSON de `registrar_entorno.py`; la corrida final de las 992 guarda el suyo como prueba de la configuración congelada.

## Contrato de datos (verificado en el código)

- **Entrada**: `data/sample_50.jsonl` = 15 `multiple_choice`, 30 `semi_open`, 5 `open_ended`. Campos `id, formato, area, pregunta, opciones, legal_basis, respuesta_correcta|respuesta_esperada`.
- **`legal_basis` y las respuestas son ground truth de evaluación: nunca se usan en runtime, nunca se hardcodea por `id`.** El test real (992) no las trae.
- **Salida**: una línea JSON por ítem, validada por `schema/submission.schema.json`. Comunes: `id, formato, abstencion, pasajes_recuperados[{doc_id, texto, inicio?, fin?, score?}]`, `latencia_ms?`.
  - `multiple_choice`: `respuesta_correcta` (A–D; `null` si abstiene), `justificacion` (**de aquí se extraen las citas que puntúan**), `descarte_opciones`.
  - `semi_open`: `respuesta` (3–5 oraciones, ≤150 palabras), `palabras_clave`, `referencia_legal`.
  - `open_ended`: `marco_normativo`, `analisis` (5–8 oraciones), `jurisprudencia`, `conclusion`.
- `doc_id` de cada pasaje **debe existir en `corpus_manifest.json`**. `pasajes_recuperados` solo puede ir vacío si `abstencion=true`. `texto` debe ser literal (la verificación en vivo reconstruye la respuesta desde ahí).
- `scripts/common.py`: `read_jsonl`/`write_jsonl` (UTF-8, `\n`), `FLAWED_IDS={374}` excluido de la calificación. `load_bank`/`questions_export.json` son solo del jurado.

## Cómo puntúa realmente (`scripts/evaluate.py`, `scripts/citations.py`)

| Componente | Pts | Detalle que condiciona el diseño |
|---|---:|---|
| Exactitud cerradas | 20 | Abstenerse = 0 aquí. Referencia del baseline: 0,905 |
| Correctness texto libre (RAGAS) | 30 | Juez `z-ai/glm-5.3-flash` vía OpenRouter + encoder local `multilingual-e5-large`. Baseline 0,451. Las abstenciones no se juzgan |
| Citación | 20 | `recall_ponderado − 2 × tasa_sin_respaldo`. Cita correcta **respaldada** = 1; correcta **sin respaldo** = 0,5; cita sin respaldo penaliza el doble |
| Abstención | 10 | Acertar = 1, **abstenerse = 0,5 siempre** (acierte o no), errar = 0. ⇒ solo abstenerse si P(acierto) < ~0,5. Abstenerse en todo es no competitivo |
| Corpus 5 · interfaz 10 · video 3 · reproducibilidad 2 | 20 | Manuales. Interfaz (Streamlit) no es prioridad hasta tener el 80% automático |

- **Respaldo de una cita = aparece en los primeros 10 `pasajes_recuperados`** (`MAX_PASAJES_EVIDENCIA = 10`). Por eso el top-10 es lo crítico, y **jamás se emite una cita que no esté en esos 10 pasajes** (comparación determinista de tuplas canónicas, sin LLM). Citar de más *desde la evidencia* es gratis.
- `citations.py` normaliza a tuplas: `("ley","1563","2012","41")`, `("codigo_penal",None,None,"404")`, `("jurisprudencia","C-355","2006",None)`. Alias de códigos en `CODES` (CGP, CPACA, CST, ET, Decisión Andina 486…). **El parser de consultas y el formato de las citas de salida deben reutilizar/respetar ese diccionario** (importar `citations.extract`/`norm` en lugar de reescribirlo).
- Solo el ~84% del banco tiene `legal_basis` con citas extraíbles; el resto no puntúa en citación.

## Corpus: qué construir

`data/seed_targets.json` (semilla 20260830) lista **186 documentos objetivo** con `norma`, `canonico`, `items_del_banco`, `areas` y `donde_buscar` (URL). Ojo: **111 de los 186 son sentencias** (C-, T-, SU-, SL-), no legislación. No se puede tratar la jurisprudencia como secundaria; hay que decidir pronto cuánta entra y con qué granularidad (por sentencia completa vs. por fragmento/ratio).

Mayor demanda en el banco: Constitución (90), CGP (65), CST (37), Estatuto Tributario (35), Decisión Andina 486 (23), Estatuto del Consumidor (13), Ley 80/1993 (12)… Ordenar la ingesta por `items_del_banco`, no por comodidad.

Fuentes por orden de ataque: **Secretaría del Senado** (HTML limpio, artículo por artículo) → SUIN-Juriscol → Corte Constitucional (relatoría) → Corte Suprema/Consejo de Estado → DIAN/SIC. Evitar OCR salvo necesidad. Derecho ambiental/internacional no está en el banco.

Modelo de chunk: **un artículo = una unidad** (inciso/parágrafo solo si el artículo es largo), con metadata `chunk_id, doc_id, document_type, document_number, year, article, section, validity, source_url, start_offset, end_offset`. Separar `retrieval_text` (puede llevar encabezado "Ley X de Y, art. N" para mejorar la búsqueda, estilo contextual retrieval con reglas) de `source_text` (literal; es lo que va en `pasajes_recuperados.texto`).

Entregables del corpus: `corpus_manifest.json`, `corpus/`, `indice/` (`index.faiss` + `chunks.jsonl`), `LICENSE`, y la bitácora `CORPUS.md` (plantilla en la raíz, con tabla de evolución del puntaje).

### Licencia del corpus (decidida)

- **CC-BY-4.0**, igual que el ejemplo oficial. Cubre el trabajo de Syntax (selección, limpieza, segmentación, metadatos, encabezados de fragmentos e índice), no los textos normativos y jurisprudenciales, que son de libre reproducción (Ley 23 de 1982, art. 41).
- El archivo ya está escrito en `../LICENSE` (carpeta del proyecto, fuera del repo): encabezado en español con alcance y atribución ("Copyright (c) 2026 Syntax") + texto legal oficial de CC-BY-4.0 sin modificar. Se copia tal cual a la raíz del comprimido del corpus.
- Mantener coherentes: `"licencia": "CC-BY-4.0"` en `corpus_manifest.json`, sección 5 de `CORPUS.md` y columna "Licencia" de `README.md`.
- Implicaciones: no usar encoders con licencia no comercial para el índice publicado (p. ej. `jina-embeddings-v3` es CC-BY-NC-4.0; `bge-m3` y `multilingual-e5-large` son MIT). No incluir doctrina ni textos con derechos de autor. Si se reutiliza un dataset de terceros (p. ej. `justicedao/ipfs_colombia_laws_ir`), verificar que su licencia sea compatible y citarlo.

### Formato de `corpus_manifest.json`

Referencia: `../Hackathon 2026/entregables/sabado/corpus_manifest.ejemplo.json`. **Va versionado en el repo (raíz) y también dentro del comprimido del corpus (`enunciado.pdf`, secc. 9 y 9.3); deben ser el mismo archivo.** `corpus/` e `indice/` no se versionan.

- **Nivel raíz**: `equipo`, `licencia` (el ejemplo usa `CC-BY-4.0`; debe coincidir con `LICENSE`), `fecha_generacion`, `enlace_nube` (el mismo del README, sección "Corpus e índice") y `documentos` (lista, un registro por documento).
- **Campos obligatorios por documento** (enunciado): `doc_id`, `titulo`, `fuente`, `url`, `fecha_consulta`, `areas`.
- **Campos adicionales que trae el ejemplo** (los mantenemos): `n_articulos`, `n_fragmentos`, `metodo_ingesta`, `sha256`.
- **`doc_id`**: `snake_case` en minúsculas, sin tildes, `tipo_numero_año`: `ley_1564_2012`, `sentencia_c_355_2006`. Debe ser idéntico en `CORPUS.md`, en la metadata de cada chunk y en `pasajes_recuperados.doc_id` (el evaluador lo valida contra el manifest). Es estable: no renombrar una vez indexado.
- **`fecha_consulta` / `fecha_generacion`**: ISO `AAAA-MM-DD` (fecha real de descarga, no la de hoy al editar).
- **`areas`**: lista de strings con los nombres exactos de las 10 áreas del banco (`Derecho procesal`, `Derecho civil`, `Derecho constitucional`…, ver `CORPUS.md` sección 2). Un documento puede tener varias.
- **`n_articulos`**: entero para normas; `null` (no `0`) para sentencias u otros documentos sin articulado. **`n_fragmentos`**: entero, debe coincidir con los chunks de ese `doc_id` en `chunks.jsonl`.
- **`metodo_ingesta`**: texto corto con el método real: `"parser HTML + segmentacion por articulo"`, `"extraccion de PDF con OCR + segmentacion por parrafo"`.
- **`sha256`**: hash del **archivo procesado** (el de `corpus/`), no del original descargado; se recalcula si el archivo cambia.
- **Texto**: los valores del ejemplo van en ASCII sin tildes (`Codigo`, `Secretaria`, `indice`). Seguir esa convención en `titulo`, `fuente` y `metodo_ingesta`; solo las URLs y los nombres propios se dejan tal cual. JSON con indentación de 2 espacios, UTF-8, `\n`.
- **Placeholders del ejemplo** (`<URL>`, `2026-XX-XX`, `<hash...>`) son solo de plantilla: ninguno puede quedar en la entrega final.
- **Rutas**: nunca absolutas ni dependientes de la máquina (`/Users/...`, `C:\...`); si se registra una ruta, es relativa a la raíz del corpus.
- **Edición**: idealmente lo genera un script a partir de `corpus/` para no editarlo a mano; si se edita a mano, una persona a la vez (es un JSON en git y los conflictos de merge son dolorosos).

### Carpeta externa (OneDrive) y rutas

El corpus procesado y el índice viven **fuera del repo**, en una carpeta sincronizada de OneDrive cuya ruta cambia por máquina (2 Windows + 1 Mac). `corpus_manifest.json` **no** está ahí: vive versionado en la raíz del repo y se copia al comprimido al empaquetar.

```
<CORPUS_DIR>/                  (OneDrive; "mantener siempre en este dispositivo")
├── corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
├── indice/   index.faiss + chunks.jsonl
└── raw/      descargas originales (opcional, regenerable)
```

- **Configuración por persona**: copiar `.env.example` a `.env` (raíz, no se versiona) y poner `CORPUS_DIR=<ruta local>` sin comillas ni escapes (`C:\Users\ana\OneDrive\rag-corpus` en Windows). Precedencia: variable de entorno > `.env` > `<repo>/data_corpus` (por defecto; ignorado por git, es lo que ve un contenedor limpio).
- **`src/config.py` es el único lugar donde se definen rutas**: exporta `ROOT`, `MANIFEST_PATH`, `CORPUS_DIR`, `CORPUS_TEXTOS`, `INDICE_DIR`, `RAW_DIR`, `CHUNKS_PATH`, `FAISS_PATH`, más `exigir_corpus_dir()` y `verificar_indice()` (comprueba que `chunks.jsonl` e `index.faiss` existan y tengan el mismo número de fragmentos; llamarla al arrancar cualquier proceso que use el índice). Los scripts hacen `sys.path.insert(0, str(ROOT / "src")); import config` (como `src/validaciones/*.py`). Nunca escribir rutas a mano ni usar `os.getcwd()`.
- **Un archivo por `doc_id` en `corpus/`**: cada uno ingiere documentos distintos sin pisarse. El `sha256` del manifest es el de ese archivo.
- **Una sola persona reconstruye `indice/`** y avisa antes: `index.faiss` es binario y OneDrive crea copias en conflicto si dos lo escriben. Si aparecen archivos tipo `index-<PC>.faiss`, hay un conflicto: no usarlos, resolver entre el equipo.
- **Validar antes de subir cambios y antes de entregar**: `python src/validaciones/manifest.py` (formato, `sha256` contra `corpus/`, `n_fragmentos` contra `chunks.jsonl`, `doc_id` de los chunks ⊆ manifest). Con `--strict` (entrega final) los placeholders y archivos ausentes son error.
- **Empaquetado final** (aún por hacer, `package_corpus.py`): `corpus/` + `indice/` + `LICENSE` + copia de `corpus_manifest.json` → comprimido `Syntax-corpus...` a un enlace público **aparte** de la carpeta de trabajo (el enunciado exige lectura pública para cualquiera con el vínculo e índice congelado); anotar el hash del comprimido en `CORPUS.md`.

## Arquitectura

**v0 (primer objetivo, antes de cualquier otra cosa):**
`corpus → BM25 → top-10 → Qwen → validación de schema → evaluate.py`

**Target condicional** (cada pieza entra solo si el análisis de error la justifica):

```
pregunta → parser de referencias legales (determinista) ─ ¿norma+artículo explícitos? → lookup por metadata
        └→ BM25 + BGE-M3 → RRF → 20–40 candidatos → [reranker] → top-10
                → ¿evidencia suficiente? no → abstención
                                          sí → Qwen3-8B → validar citas (⊆ top-10) → validar schema → jsonl
```

Elecciones actuales (revisar con datos, no dogma):
- Encoder `BAAI/bge-m3` (normalizar embeddings, FAISS `IndexFlatIP`); BM25 con `bm25s` (mirar tildes, `art.`/`artículo`, `Ley 1564/2012` vs `de 2012`, siglas; probar si el stemming daña).
- Fusión RRF antes que suma de scores. Hybrid se prueba temprano: en derecho, números de artículo y siglas hacen que BM25 y denso sean complementarios.
- Reranker: `Qwen3-Reranker-0.6B` (candidato; `bge-reranker-v2-m3` como alternativa). Solo si el artículo correcto está en rango 11–40 con frecuencia. Medir latencia y mantener solo si mejora.
- Decoder `Qwen3-8B` (plan B `Qwen3-4B` si la velocidad no alcanza). Un solo decoder hasta que el análisis muestre "retrieval correcto + generación incorrecta".
- `generation_k` (3/5/7/10) es un hiperparámetro a barrer; `retrieved_top_k=10` se mantiene fijo para el juez.
- Prompts separados por formato: `generate_closed / generate_semi_open / generate_open`. Política: no inventar normas, artículos ni sentencias; citar solo lo respaldado por los pasajes.
- Citas inválidas tras generar: regenerar 1 vez → eliminar la cita si no rompe validez → abstenerse.
- Abstención: registrar primero score, rank, margen, acuerdo BM25/denso y coincidencia de referencia exacta; elegir una regla simple sobre esas señales (no ajustar umbrales finos a 50 muestras).

**No construir** (salvo que el análisis de error lo demuestre): agentic RAG, GraphRAG, HyDE, multi-query, query decomposition, fine-tuning, queries sintéticas, vector DB externa, LangChain/LlamaIndex, UI avanzada.

## Método de trabajo (obligatorio para todo el equipo y todos los agentes)

`OBSERVAR → MEDIR → DIAGNOSTICAR → HIPÓTESIS → CAMBIAR UNA COSA → BENCHMARK → KEEP/REVERT`

Antes de añadir una técnica: qué error observado corrige, qué métrica debe mejorar, si hay alternativa más simple, coste en latencia/memoria, si es reversible y si generaliza a 992 (no solo a las 50). Una mejora de 1/50 no es significativa; a igualdad, gana lo más simple, rápido y reproducible.

- **Medir retrieval antes de generar**: `retrieval_eval.py` con Document/Article Hit@1/3/5/10, MRR y latencia, guardado por pregunta (usando `legal_basis` solo aquí, como evaluación).
- **Análisis de error por pregunta** con diagnóstico ∈ {CORPUS, INGESTION, DOCUMENT_RETRIEVAL, ARTICLE_RETRIEVAL, RANKING, GENERATION, CITATION, SCHEMA, UNKNOWN}. El diagnóstico decide el siguiente experimento.
- **`evaluation/experiments.csv`**: una fila por experimento (commit, versión de corpus, retriever/encoder/fusión/reranker, retrieval_k/generation_k, decoder/cuantización/prompt_version, hit@k, MRR, puntajes oficiales, latencias, notas). Compartido y versionado: la memoria humana no cuenta.
- Desempate determinista en rankings; prompt y modelo versionados.

## Equipo, plataformas y cómputo

- **Windows + Mac**: escribir código portable. `pathlib`, sin rutas con `\`, abrir/escribir archivos con `encoding="utf-8"` y `newline="\n"`, sin dependencias de bash en `src/` (el `run.sh` es un envoltorio fino de `python src/main.py`). Fijar versiones en `requirements.txt` (Python 3.11 objetivo; el repo trae `.pyc` de 3.14 de los scripts oficiales, que corren en ambas).
- **Un solo contrato de dispositivo**: `device = cuda | mps | cpu` por configuración, no por `if platform`. Mac: llama.cpp con Metal (`-DGGML_METAL=ON`, GGUF Q4_K_M). Campus/CUDA: mismo modelo servido por llama.cpp o vLLM. Exponer el decoder siempre tras una interfaz `generate(prompt) -> str` (idealmente endpoint OpenAI-compatible) para que el resto del código no cambie.
- **Las máquinas del campus sirven para lo pesado y paralelizable**: embeddings del corpus completo, construcción de índices, sweeps de retrieval y las corridas largas de las 992. Los Mac sirven para iterar.
- **Cuidado de reproducibilidad entre plataformas**: un GGUF Q4 en Mac y otra cuantización en CUDA no dan la misma salida. Los números de `experiments.csv` deben anotar plataforma y cuantización; **la corrida final de las 992 y la verificación en vivo usan una sola configuración congelada**.
- Índices y modelos pesados **no van al repo** (enlace público en la nube, verificable en ventana privada antes de las 15:00). Rutas y hashes de artefactos se registran en `corpus_manifest.json`.
- Sofía es la desarrolladora principal con tiempo fragmentado: tareas pequeñas, cada una terminable en una sesión, con interfaces claras (`retrieve(query, k) -> list[RetrievedChunk]`).

## Convenciones de repo

- Trabajar en ramas por persona/tarea y PR a `main`; no hacer push directo a `main` ni force-push.
- No versionar `scripts/.env`, modelos, índices ni `__pycache__` (ver `.gitignore`).
- Completar `README.md` (arquitectura, reproducción, resultados, limitaciones) y `CORPUS.md` a medida que avanza el trabajo, no al final; hay que quitar las notas en cursiva de las plantillas.

## Sincronizar AGENTS.md

Después de editar este archivo:

```bash
python -c "import shutil; shutil.copyfile('CLAUDE.md', 'AGENTS.md')"
```

(funciona igual en Windows y Mac; no usar symlinks porque en Windows fallan sin permisos).
