# Resultados de e02_v0 contra el evaluador oficial (con juez de API)

Primera evaluación completa del RAG v0 sobre `sample_50`, incluyendo el juez de texto libre (`--ragas`).

- **Fecha:** 2026-10-01
- **Corrida evaluada:** `evaluation/generacion/e02_v0/entrega.jsonl` (50 respuestas; diagnóstico por pregunta en `evaluation/generacion/e02_v0/errores.csv`)
- **Comando:** `python scripts/evaluate.py --submission evaluation/generacion/e02_v0/entrega.jsonl --split sample --ragas`
- **Juez:** `z-ai/glm-5.3-flash` (OpenRouter) + encoder local `multilingual-e5-large`

## Configuración de la corrida

| | |
|---|---|
| Decoder | Qwen3-8B Q4_K_M, llama.cpp (build 11146), `temperature=0`, `seed=0` |
| Prompt | `p-v0` |
| Recuperación | híbrida BM25 + bge-m3 + RRF, `retrieval_k=10`, `generation_k=5` |
| Índice | seg-v1, 35.105 fragmentos, 167 documentos |
| Commit | `12e1aab` |
| Máquina | Mac M1 16 GB (encoder en `mps`) |

## Puntaje

**50,66 de 80 puntos automáticos.** Los otros 20 (interfaz, corpus, video y reproducibilidad) son manuales.

| Componente | Resultado | Puntos | Baseline |
|---|---|---:|---:|
| Exactitud cerradas | 11 de 15 (0,733) | 14,67 / 20 | 0,905 |
| Correctness texto libre (RAGAS) | 0,4327 (35 ítems juzgados, 0 fallidos) | 12,98 / 30 | 0,451 |
| Citación | índice 0,7551 | 15,10 / 20 | |
| Abstención | calibración 0,7907 | 7,91 / 10 | |

Validación de schema: 0 errores.

### Citación

- 49 referencias esperadas, 37 acertadas (todas respaldadas en el top-10).
- 111 citas emitidas; 74 no coinciden con el `legal_basis`. Citar de más desde la evidencia no penaliza.
- **0 citas sin respaldo**, así que no hay penalización. La validación contra el top-10 funciona.
- Lo que limita el puntaje es el recall (0,755), que depende de que la recuperación traiga el artículo correcto.

### Abstención

- Nunca nos abstuvimos: 34 respuestas bien y 9 mal.
- Abstenerse vale 0,5 siempre. Las 9 respuestas malas valieron 0.
- Es una oportunidad, pero con 50 muestras no se debe ajustar un umbral fino. Primero hay que registrar señales (score, rank, margen, acuerdo BM25/denso).

## Diagnóstico por pregunta (`errores.csv`)

| Diagnóstico | Cerradas | Semi-abiertas | Abiertas | Total |
|---|---:|---:|---:|---:|
| OK | 8 | 23 | 2 | 33 |
| DOCUMENT_RETRIEVAL | 2 | 1 | 2 | 5 |
| ARTICLE_RETRIEVAL | 1 | 3 | 1 | 5 |
| GENERATION | 4 | 0 | 0 | 4 |
| CITATION | 0 | 2 | 0 | 2 |
| CORPUS | 0 | 1 | 0 | 1 |

Lecturas:

- **Cerradas:** 4 de las 7 falladas son `GENERATION`. La recuperación trajo evidencia útil y el modelo eligió mal (ids 58, 128, 647, 671). Es la mayor brecha frente al baseline (0,733 contra 0,905). El tamaño de `generation_k`, el prompt y el modelo son las palancas.
- **Abiertas:** las 3 falladas son de recuperación (2 de documento, 1 de artículo). Son solo 5 preguntas, así que es una señal débil.
- **Recuperación en general:** 10 de 17 preguntas con error son de recuperación (documento o artículo), contra 4 de generación. Las métricas de recuperación por separado están en `evaluation/experiments.csv` (fila `e01_bge_m3_hibrido`).
- **CORPUS:** 1 caso, probablemente una de las 30 fuentes pendientes (`docs/ingesta/fuentes_pendientes.md`).

## Latencia (el problema más grande para el sábado)

| | Segundos por pregunta |
|---|---:|
| Mediana | 111 |
| Máximo | 535 |
| Cerradas (media) | 131 |
| Semi-abiertas (media) | 94 |
| Abiertas (media) | 259 |

El objetivo es **< 10 s por pregunta** (límite teórico 21,8 s) para correr las 992 en ~6 h. Con este Mac estamos más de 10 veces por encima, así que hay que elegir y medir la máquina final antes de seguir afinando calidad. Hubo 4 respuestas que se regeneraron por citas sin respaldo.

## Qué falta por medir o decidir

1. Medir el mismo `sample_50` en la máquina del campus (CUDA) y con `qwen3-4b-2507-q4` para ver el costo de calidad frente a velocidad. Los intentos de 4B (`e03_4b_q4`) quedaron incompletos.
2. Revisar las 4 cerradas con `GENERATION`: ¿el pasaje correcto estaba en los 5 enviados al decoder, o solo en los 10?
3. Probar `generation_k` (3 / 5 / 7 / 10) manteniendo `retrieval_k=10`.
4. Registrar señales de abstención y proponer una regla simple.
5. Cerrar las fuentes pendientes que afectan al `legal_basis` de `sample_50`.
6. Registrar esta evaluación con `evaluar_entrega.py --ragas` para que quede la fila en `evaluation/experiments.csv`.

## Notas

- Es una sola corrida sobre 50 preguntas: una diferencia de 1 o 2 preguntas no es significativa. El juez de texto libre tampoco es determinista, así que 0,433 contra 0,451 es esencialmente un empate con el baseline.
- La llave de OpenRouter va en `scripts/.env` (ignorado por git). Nunca se versiona.
- Las dependencias del juez se instalan con `pip install -r scripts/requirements-evaluador.txt`. Son del jurado y no van en `requirements.txt`.
