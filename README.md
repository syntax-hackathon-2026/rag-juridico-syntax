
# Syntax — Hackathon 2026

**Integrantes: Sofia Morato, Joel David Niño, Santiago Muñoz**

**Universidad de los Andes**

Sistema de respuesta a preguntas de derecho colombiano con un modelo abierto de
tamaño reducido y un corpus jurídico propio.

## Corpus e índice

| Recurso                              | Enlace    | Tamaño | Licencia |
| ------------------------------------ | --------- | ------- | -------- |
| Corpus procesado e índice vectorial | [OneDrive](https://1drv.ms/u/c/e17f9102812dd361/IQBccApNKKVUR5RKm1ux2I-RAT5JSwWVU1jFBh37iHhFtXg?e=lbmgOi) (`Syntax-corpus-v5c.zip`, sha256 `3164e080…b28f0b`) | 958 MB | CC-BY-4.0 |

El comprimido contiene `LICENSE`, `corpus_manifest.json`, `corpus/` con los
documentos procesados e `indice/` con el índice serializado y los fragmentos.

El enlace permanece activo hasta el 2 de noviembre de 2026 (treinta días después del evento). Corpus v5: 1.285 documentos y 185.234 fragmentos; sha256 completo del comprimido y de `chunks.jsonl` en [`CORPUS.md`](CORPUS.md), sección 6.

## Video

[Video de presentación en YouTube](https://www.youtube.com/watch?v=QfkF2o2-lVs)

## Arquitectura

```
pregunta + opciones + área
   ├─► normas y sentencias nombradas (scripts/citations.py) ─► lookup por metadata
   └─► BM25 + bge-m3 ─► RRF ─► prioridad por área (×2) ─► filtro "solo por cita"
                                   ─► top-10 = pasajes_recuperados
                                   └─► top-5 + glosario de normas ─► Qwen3-8B Q8_0 (llama.cpp, temperatura 0, JSON por gramática)
                                         ─► validar citas ⊆ top-10 ─► citar la evidencia del top-10 ─► validar schema ─► JSONL
```

| Componente               | Elección | Motivo |
| ------------------------ | --------- | ------ |
| Corpus                   | 1.285 documentos (normas, códigos, Decisiones Andinas y sentencias de la Corte Constitucional y la Corte Suprema) → 185.234 fragmentos (v5) | Construido desde la semilla del banco y ampliado por área; detalle y bitácora en [`CORPUS.md`](CORPUS.md) |
| Encoder                  | `BAAI/bge-m3` (revisión fijada, fp32, 1024 dim) | Licencia MIT (compatible con CC-BY-4.0 del corpus), multilingüe, sin prefijos, 8k tokens |
| Decoder                  | `Qwen/Qwen3-8B-GGUF` Q8_0 (sha256 fijado; Q4_K_M para Macs de 16 GB), servido en local por `llama-server` (llama.cpp b11146), sin thinking | Sugerido por el enunciado; el mismo GGUF corre en Mac (Metal), Windows y Linux (CUDA). Temperatura 0, semilla fija, un solo slot y sin caché de prompt para que la salida sea reproducible. Q8_0 acertó una cerrada más que Q4 y cabe en una GPU de 24 GB |
| Segmentación            | Un artículo = un fragmento (partido por párrafos si pasa de 350 palabras); sentencias en ventanas de ~350 palabras por sección | El artículo es la unidad de sentido; cada fragmento lleva una cabecera citable ("Artículo 42 del Código General del Proceso.") para que la cita quede respaldada |
| Recuperación            | Híbrida: BM25 (`bm25s`) + denso (FAISS `IndexFlatIP`) fusionados con RRF (k=60, 40 candidatos por rama); consulta = pregunta + opciones | Los números de artículo y las siglas favorecen a BM25; las paráfrasis, al denso |
| Lookup por metadata      | Si la pregunta nombra una norma (y artículo) o una sentencia, sus fragmentos entran a los candidatos con un bono | Las preguntas que nombran su fuente la recuperan en el top-10 |
| Filtro "solo por cita"   | Las sentencias de las ampliaciones solo se recuperan si la pregunta las nombra | Cada ampliación sin filtro bajó la recuperación: las sentencias largas desplazaban a los artículos |
| Prioridad por área       | El score de los fragmentos cuyo documento es del área de la pregunta se multiplica por 2 | El corpus está desbalanceado (constitucional mucho mayor que mercados o procesal); solo reordena, nunca descarta |
| Glosario de normas       | Bajo cada pasaje va el título de su norma y, si la pregunta nombra una norma por número o por nombre, la equivalencia | El decoder no sabe que "Ley 1564 de 2012" es el CGP; arregla una cerrada sin regresiones |
| Reordenamiento           | `BAAI/bge-reranker-v2-m3` (Apache-2.0) sobre los 20 primeros candidatos, fusionado por RRF con el orden híbrido | Midió +0,41/50 en la muestra (citación) frente al híbrido solo (`e53_rerank_rrf20`, `docs/INDEXACION.md` sección 20); con N=40 o solo el orden del cross-encoder no mejoró |
| Mecanismo de abstención | Se abstiene si no hay pasajes, si el decoder no produce un JSON válido o si quitar las citas sin respaldo deja un campo vacío | Abstenerse da 0 en exactitud y en RAGAS y 0,5 en calibración: solo conviene cuando la probabilidad de acierto es baja |

Toda norma citada se verifica de forma determinista contra los 10 pasajes recuperados con el mismo extractor del evaluador (`scripts/citations.py`): una cita sin respaldo se regenera una vez, luego se elimina su oración y, si eso deja la respuesta incompleta, el sistema se abstiene. Después se agregan a la respuesta las cabeceras citables de los 10 pasajes (`CITAR_EVIDENCIA=top10`), que siempre están respaldadas. Detalle en [`docs/GENERACION.md`](docs/GENERACION.md) y [`docs/INDEXACION.md`](docs/INDEXACION.md).

Probado y descartado con medición (cada uno en `evaluation/experiments.csv`): thinking, `generation_k=10`, prompts alternativos para cerradas y texto libre, una consulta por opción, un planificador de consultas con el mismo 8B y la composición forzada del top-10.

## Reproducción

Un único comando genera la entrega a partir del índice y del decoder local.

```bash
python3.13 src/reproducibilidad/preparar_entorno.py      # .venv + requirements.txt (Python 3.13)

# Decoder: llama.cpp (build usada: 0.5.0, build 11146)
brew install llama.cpp                                   # Mac (Metal)
#   Windows/Linux: binario de https://github.com/ggml-org/llama.cpp/releases (CUDA o CPU), o `winget install llama.cpp`
python src/generacion/modelo.py descargar                # GGUF a modelos/ con sha256 verificado
python src/generacion/modelo.py servir                   # en otra terminal; deja el servidor en 127.0.0.1:8080

bash run.sh                                              # o: python src/main.py --split sample
bash run.sh --split test                                 # 992 preguntas -> submissions.jsonl
```

### Máquina limpia (Windows con GPU NVIDIA, Linux)

Con el repo descargado y los `.txt` del corpus a mano, un solo comando prepara todo y corre las preguntas:

```powershell
# Windows (instala Python 3.13 con winget si falta)
powershell -ExecutionPolicy Bypass -File reproducir.ps1 -Corpus C:\ruta\al\corpus     # carpeta o .zip con los .txt
```
```bash
python3.13 src/reproducibilidad/reproducir.py --corpus /ruta/al/corpus                  # Linux / contenedor con Python 3.13
```

Todo parte de que los `.txt` del corpus ya existen en `data_corpus/corpus/`. Las seis etapas se pueden correr por separado
(`--solo entorno|corpus|indice|decoder|preguntas|evaluar`, varias con coma, o `--desde`/`--hasta`; `--dry-run` muestra el plan y lo que falta):

```bash
python src/reproducibilidad/reproducir.py --solo indice                                  # solo construir el índice
python src/reproducibilidad/reproducir.py --solo preguntas --split test --ids 51 60      # solo responder (o --rango 100-200, --limite N, --particion 2/4, --entrada <jsonl>)
python src/reproducibilidad/reproducir.py --solo evaluar --entrega submissions.jsonl --split test
```

Etapas (cada una se salta si ya está lista): `.venv` + `requirements.txt` y `scripts/requirements-evaluador.txt` (y torch con CUDA en lugar de la rueda CPU de PyPI) →
`.txt` contra el sha256 de `corpus_manifest.json` → segmentar, comprobar que `chunks.jsonl` es idéntico al congelado,
codificar con bge-m3 en GPU y armar BM25 + FAISS → llama.cpp b11146 (se descarga a `herramientas/`) + GGUF con sha256 →
`llama-server` en segundo plano, `src/main.py` (con latencia media y proyección a 992 preguntas) y la evaluación: schema siempre
y puntaje oficial con `evaluate.py` (el juez de texto libre corre solo si hay `OPENROUTER_API_KEY` en el entorno o en `scripts/.env`;
`--ragas` lo exige, `--sin-ragas` lo apaga; con `--split test` el puntaje solo se calcula si están los archivos del jurado).
Opciones: `--reindexar` (borra índice y caché de vectores), `--sin-reanudar` (latencias limpias), `--device cpu`. Requiere driver NVIDIA con CUDA >= 12.6; no instala drivers.

El índice (`data_corpus/indice/`) se reconstruye con `src/indexacion/segmentar.py` + `src/indexacion/construir_indice.py`, o se toma del comprimido publicado (sección "Corpus e índice"). Para volver a parsear los originales de `data/raw/` hacen falta pandoc (RTF/DOCX) y Tesseract con el idioma español (5 sentencias escaneadas): `brew install pandoc tesseract tesseract-lang`. No son necesarios si se parte del `corpus/` publicado. `SYNTAX_LLM` elige el decoder (`qwen3-8b-q8` por defecto; `qwen3-8b-q4` para Macs de 16 GB y `qwen3-4b-2507-q4` como alternativas) y `SYNTAX_LLM_URL` el endpoint.

Requisitos de hardware: GPU con ~10 GB libres para el decoder 8B Q8_0 (~6 GB con Q4_K_M) más ~4 GB para el encoder y el índice. Máquina de referencia: Windows con RTX 4090 (24 GB).

Tiempo medido en la RTX 4090 con Qwen3-8B Q8_0: **~4,4 s por pregunta** (recuperación ~0,6–0,8 s), ~1,2 h para las 992. En un Mac M1 de 16 GB con Q4_K_M, ~145 s por pregunta. Construir el índice desde los `.txt` tomó ~32 min en la 4090 con el corpus v3 (113.519 fragmentos; el v5 tiene 185.234); se evita descargando el índice publicado.

## Resultados sobre las preguntas de muestra

Corrida `e24_final` (configuración por defecto, RTX 4090, Qwen3-8B Q8_0), evaluada con `scripts/evaluate.py --ragas`:

| Componente                               |    Puntos | Posibles |
| ---------------------------------------- | --------: | -------: |
| Exactitud en cerradas (12/15)            |     16,00 |       20 |
| Corrección en texto libre (RAGAS 0,440)  |     13,20 |       30 |
| Calidad de citación                      |     17,55 |       20 |
| Abstención calibrada                     |      8,60 |       10 |
| **Total automático**                     | **55,35** |   **80** |

- Citación: recall ponderado 0,878 y **0 citas sin respaldo** (la validación contra el top-10 lo garantiza).
- El juez de texto libre varía ±0,03 entre corridas sobre la misma entrega: en esta corrida no devolvió veredicto en 3 de 35 ítems (cuentan como cero); repetido por ítem dio 0,457.
- La salida es determinista: dos corridas con la misma configuración dan entregas idénticas (`src/evaluacion/comparar_entregas.py`).
- Evolución: 51,19 (`e05`, corpus v3 y Q8_0) → 54,43 (`e13`, filtro solo por cita, evidencia del top-10 y lookup) → 55,35 (`e24_final`, corpus v4, prioridad por área y glosario). Todas las corridas están en `evaluation/experiments.csv` y `evaluation/generacion/<experimento>/`.

## Interfaz gráfica

Aplicación Streamlit (`src/interfaz/app.py`) sobre el mismo `responder()` que usa `src/main.py`, con la identidad visual de Software Colombia (tema en `.streamlit/config.toml`, logo en `src/interfaz/assets/`). Cómo ejecutarla:

```bash
python src/generacion/modelo.py servir      # otra terminal: llama-server (solo para "Consultar")
streamlit run src/interfaz/app.py           # o: bash interfaz.sh  ->  http://localhost:8501
```

- **Consultar**: pregunta libre o un ejemplo de `sample_50` (solo `id, formato, area, pregunta, opciones`), en los tres formatos. Muestra la respuesta, las citas marcadas como respaldadas o no en los 10 pasajes (mismo criterio de `scripts/citations.py` que usa el evaluador), los 10 pasajes literales con su `doc_id` (señalando los 5 que lee el decoder), la latencia y si hubo regeneración o abstención. El registro se descarga en JSON, en el formato de `submissions.jsonl`. Necesita `data_corpus/indice/` y el decoder; si faltan, la app indica el comando que lo resuelve.
- **Explorar entrega**: abre cualquier `.jsonl` de entrega (`submissions.jsonl`, `evaluation/generacion/<exp>/entrega.jsonl` con su traza) sin índice ni decoder. Sirve para la verificación en vivo.
- Usa la configuración por defecto de `config.py`, así que la misma pregunta da el mismo registro que la corrida por lotes. En la demo se corre con `SYNTAX_LLM_CACHE=off`.

## Limitaciones conocidas

1. **Texto libre**: RAGAS ~0,44–0,46, cerca de la línea base del enunciado (0,451). En los casos con narrativa larga la norma decisiva a veces no llega al top-10 (p. ej. #247: la Ley 472 de 1998), y ningún cambio de prompt probado mejoró el puntaje del juez.
2. **Recuperación sin nombre de la norma**: el documento correcto entra al top-10 en ~90% de las preguntas, pero el artículo exacto solo en ~58% (art_hit@10). Las sentencias de las ampliaciones solo se recuperan si la pregunta las nombra.
3. **Fuentes ausentes**: doctrina (leasing, fintech, modelo de convenio OCDE), circulares de la SIC y de la Superintendencia Financiera, resoluciones administrativas y sentencias de la Corte Suprema anteriores a 2016 no están en el corpus.
4. **Áreas de los documentos**: las de los documentos de las ampliaciones las propuso un agente y afectan la recuperación (prioridad por área); falta la revisión humana completa.
5. **Decoder de 8B sin thinking**: no recuerda números de artículo con fiabilidad, así que el sistema depende de que la evidencia esté en los pasajes; las preguntas que exigen doctrina fuera del corpus fallan.
