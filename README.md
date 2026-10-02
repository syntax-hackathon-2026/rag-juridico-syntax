
# Syntax — Hackathon 2026

**Integrantes: Sofia Morato, Joel David Niño, Santiago Muñoz**

**Universidad de los Andes**

Sistema de respuesta a preguntas de derecho colombiano con un modelo abierto de
tamaño reducido y un corpus jurídico propio.

## Corpus e índice

<!-- OBLIGATORIO. El jurado descarga desde aquí. Verificar el enlace desde una
     sesión privada del navegador antes de las 15:00. -->

| Recurso                              | Enlace    | Tamaño | Licencia |
| ------------------------------------ | --------- | ------- | -------- |
| Corpus procesado e índice vectorial | `<URL>` |         |          |

El comprimido contiene `LICENSE`, `corpus_manifest.json`, `corpus/` con los
documentos procesados e `indice/` con el índice serializado y los fragmentos.

El enlace permanece activo hasta el `<fecha, treinta días después del evento>`.

## Arquitectura

```
pregunta (+ opciones) ─► BM25 + bge-m3 ─► RRF ─► top-10 = pasajes_recuperados
                                               └─► top-5 ─► Qwen3-8B (llama.cpp, temperatura 0, JSON por gramática)
                                                          ─► validar citas ⊆ top-10 ─► validar schema ─► JSONL
```

| Componente               | Elección | Motivo |
| ------------------------ | --------- | ------ |
| Encoder                  | `BAAI/bge-m3` (revisión fijada, fp32, 1024 dim) | Licencia MIT (compatible con CC-BY-4.0 del corpus), multilingüe, sin prefijos, 8k tokens |
| Decoder                  | `Qwen/Qwen3-8B-GGUF` Q4_K_M (sha256 fijado), servido en local por `llama-server` (llama.cpp) | Sugerido por el enunciado; el mismo GGUF corre en Mac (Metal), Windows y Linux (CUDA). Temperatura 0, semilla fija, un solo slot y sin caché de prompt para que la salida sea reproducible |
| Segmentación            | Un artículo = un fragmento (partido por párrafos si pasa de 350 palabras); sentencias en ventanas de ~350 palabras por sección | El artículo es la unidad de sentido; cada fragmento lleva una cabecera citable ("Artículo 42 del Código General del Proceso.") para que la cita quede respaldada |
| Recuperación            | Híbrida: BM25 (`bm25s`) + denso (FAISS `IndexFlatIP`) fusionados con RRF (k=60, 40 candidatos por rama) | Los números de artículo y las siglas favorecen a BM25; las paráfrasis, al denso. Mejor respaldo@10 medido (0,927 en el corpus v2) |
| Reordenamiento           | Ninguno (v0) | Solo entra si el análisis de error muestra el artículo correcto en los rangos 11–40 |
| Mecanismo de abstención | Regla v0: se abstiene si no hay pasajes, si el decoder no produce un JSON válido o si quitar las citas sin respaldo deja un campo vacío | Abstenerse da 0 en exactitud y en RAGAS; se registran señales (score, margen, acuerdo BM25/denso) para calibrar una regla con datos |

Toda norma citada se verifica de forma determinista contra los 10 pasajes recuperados con el mismo extractor del evaluador (`scripts/citations.py`): una cita sin respaldo se regenera una vez, luego se elimina su oración y, si eso deja la respuesta incompleta, el sistema se abstiene. Detalle en [`docs/GENERACION.md`](docs/GENERACION.md) y [`docs/INDEXACION.md`](docs/INDEXACION.md).

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

El índice (`data_corpus/indice/`) se reconstruye con `src/indexacion/segmentar.py` + `src/indexacion/construir_indice.py`, o se toma del comprimido publicado (sección "Corpus e índice"). Para volver a parsear los originales de `data/raw/` hacen falta pandoc (RTF/DOCX) y Tesseract con el idioma español (5 sentencias escaneadas): `brew install pandoc tesseract tesseract-lang`. No son necesarios si se parte del `corpus/` publicado. `SYNTAX_LLM` elige el decoder (`qwen3-8b-q4` por defecto; `qwen3-4b-2507-q4` como alternativa) y `SYNTAX_LLM_URL` el endpoint.

Requisitos de hardware: ~6 GB de memoria para el decoder (8B Q4) más ~4 GB para el encoder y el índice. Con GPU (Metal/CUDA) y memoria libre suficiente.

Tiempo estimado sobre las 50 preguntas de muestra: en un Mac M1 de 16 GB con otras aplicaciones abiertas, ~145 s por pregunta (~2 h). En una GPU dedicada se espera bastante menos; está pendiente medirlo en la máquina final.

## Resultados sobre las preguntas de muestra

| Componente            | Puntos | Posibles |
| --------------------- | -----: | -------: |
| Exactitud en cerradas |        |       20 |
| Calidad de citación  |        |       20 |
| Abstención calibrada |        |       10 |

## Interfaz gráfica

Cómo ejecutarla:

```bash
```

## Limitaciones conocidas

1. 

2. 

3.
