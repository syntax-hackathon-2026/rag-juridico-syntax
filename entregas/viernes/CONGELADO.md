# Congelado del avance del viernes (2026-10-02)

Estado exacto con el que se generaron `respuestas_sample.jsonl` y `REPORTE_AVANCE.pdf`. El corpus puede
seguir creciendo en `santiago`/`main`; para reproducir **estas** respuestas se usa el tag y el snapshot de abajo,
no el estado vigente de la rama.

## Qué quedó fijo

| Pieza | Valor |
|---|---|
| Código, manifest y registros | tag git **`avance-viernes`** (la corrida se hizo en el commit `8e57595`; el tag apunta al commit que versiona sus resultados) |
| Corrida | `e20_avance_v4` (`evaluation/generacion/e20_avance_v4/`, entorno en `evaluation/entornos/e20_avance_v4.json`) |
| Respuestas enviadas | `entregas/viernes/respuestas_sample.jsonl`, sha256 `677722f06ee7ef2316df5eeca1762b12e2e835d6a0c0f1332197f8973c1f0d5e` |
| Puntaje (evaluate.py, sin RAGAS) | 40,59/50: cerradas 14,67 (11/15), citación 17,55 (recall 0,878, 0 sin respaldo), abstención 8,37; 0 errores de schema |
| Puntaje con juez (`--ragas`) | 53,17/80: texto libre 12,58/30 (correctness 0,4195; referencia 0,451). El juez `z-ai/glm-5.3-flash` no dio veredicto en 4 de 35 respuestas, que cuentan como cero (0,474 en las 31 juzgadas). El juez no es determinista: las mismas respuestas dieron 0,4314 en `e19_corpus_v4_t_ragas`. Se evaluó después de crear el tag, sobre el mismo `respuestas_sample.jsonl` |
| Corpus | v4: 1.186 documentos, 173.393 fragmentos; `corpus_manifest.json` sha256 `cd1943a03e4eb5c374c9ebe36044e3d4ff7e718e8d666ab3d260b3f4eeeb77cb` |
| `indice/chunks.jsonl` | sha256 `030d9268939055b63ee20a27d9714103e78af93e5c3e2cfa06a70352c3ad7f18` (= `data/registros/hashes_esperados.json`) |
| `indice/index.faiss` | sha256 `4e6d922cd6635b3e99a439c48c895b87d64e5595d2ac18b672356f9235d55e3d` |
| Snapshot corpus + índice | `Syntax-corpus-avance-viernes.zip` (900,5 MB, 1.196 archivos: `corpus/`, `indice/` con `index.faiss` y `bm25/`, `corpus_manifest.json`; sin LICENSE, no es el zip publicable), sha256 `07b95bde068a4415cde055560a6a1c784f7f0fe0abab685bb397ef3c99040d4f`. Copia en la RTX 4090: `C:\Users\s.munozm234\congelados\avance-viernes\` |
| Encoder | `BAAI/bge-m3` revisión `5617a9f61b028005a4858fdac845db406aefb181`, fp32, CUDA |
| Decoder | `Qwen/Qwen3-8B-GGUF` `Qwen3-8B-Q8_0.gguf` (revisión `7c41481f…`, sha256 `408b9555…e883d6`), llama.cpp build 11146 (commit `7fe450e19`), `temperature=0`, `seed=0`, `-np 1` |
| Configuración | valores por defecto de `src/config.py` en el tag, **sin ninguna variable `SYNTAX_*`**: híbrido BM25 + bge-m3 + RRF, lookup `on`, filtro solo por cita `sentencias`, prioridad por área 2,0, `retrieval_k=10`, `generation_k=5`, `CITAR_EVIDENCIA=top10`, prompt `p-v0`, sin thinking, abstención `off` |
| Máquina | Windows 11 + RTX 4090 (24 GB), latencia media 4,2 s/pregunta (incluye ~38 s de calentamiento en la primera) |

Comprobación de determinismo: `e20_avance_v4` es idéntica pregunta por pregunta a `e19_corpus_v4_t`
(misma configuración, otra corrida): `comparar_entregas.py` da 0 ítems con citas, pasajes o redacción distintos.

## Cómo reproducir

Desde un clon del repo, en una carpeta aparte para no tocar el trabajo en curso:

```powershell
git fetch --tags
git worktree add ..\syntax-avance-viernes avance-viernes
cd ..\syntax-avance-viernes
# corpus + indice congelados (asi no se recodifica y index.faiss es bit a bit el mismo)
Expand-Archive C:\Users\s.munozm234\congelados\avance-viernes\Syntax-corpus-avance-viernes.zip $env:TEMP\snap
New-Item -ItemType Directory -Force data_corpus | Out-Null
Move-Item $env:TEMP\snap\Syntax-corpus-avance-viernes\corpus, $env:TEMP\snap\Syntax-corpus-avance-viernes\indice data_corpus\
# entorno, verificacion de hashes, decoder (b11146 + GGUF verificado), 50 preguntas y evaluate.py
python src/reproducibilidad/reproducir.py --experimento repro_avance_viernes --sin-ragas
python src/evaluacion/comparar_entregas.py entregas/viernes/respuestas_sample.jsonl salidas/sample_repro_avance_viernes.jsonl
```

Esperado: la etapa `indice` dice "indice vigente ... se salta la codificacion", el puntaje es 40,59/50 y
`comparar_entregas.py` reporta 0 diferencias. Sin el zip, `reproducir.py --corpus <zip|carpeta>` reconstruye el
índice desde los `.txt` (exige `chunks.jsonl` idéntico al congelado) y vuelve a codificar con bge-m3; en la
misma GPU debería dar el mismo índice, pero solo el zip lo garantiza bit a bit.

El snapshot se regenera desde el tag con
`python src/reproducibilidad/package_corpus.py --sin-licencia --nombre Syntax-corpus-avance-viernes`
(zip determinista: mismo contenido, mismo sha256).
