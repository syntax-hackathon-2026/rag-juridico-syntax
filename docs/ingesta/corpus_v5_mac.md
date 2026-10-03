# Corpus v5 desde un Mac: procedimiento

Ampliación automática del corpus v4 (1.186 documentos, 173.393 fragmentos) con las normas que el propio corpus cita y no tiene (`src/ingesta/huecos_por_citas.py`, tabla en `docs/ingesta/huecos_por_citas.md`). Contexto y mediciones: `docs/INDEXACION.md` sección 17. **Regla del equipo: nada se busca a mano**; lo que no se resuelva automáticamente se descarta y se anota en `docs/ingesta/fuentes_pendientes.md` ("Ampliación v5", no resueltos).

Tiempo estimado: ~2 h de reloj (~1 h de máquina). En un Mac el paso caro es el denso de los fragmentos nuevos (MPS; ver paso 6).

## Qué se espera y qué no

- Cubre huecos estructurales para las 992 (Leyes 715/2001, 1122/2007, 1955/2019, 1448/2011, 734/2002, 142/1994, 2294/2023, tratados aprobados por ley…).
- **No** arregla #647, #671 ni #128 de `sample_50` (doctrina) ni trae los decretos del SMLMV ni los convenios de doble imposición: el corpus no los cita por número y no hay regla automática que los encuentre.
- En `sample_50` casi no se puede medir ganancia (sus normas ya están): el KEEP es "no diluye" (mismo criterio que v4, `docs/INDEXACION.md` 16).

## 0. Prerrequisitos en el Mac

```bash
git fetch origin && git checkout santiago && git merge origin/santiago   # trae santiago-cerradas ya fusionada
python3.13 src/reproducibilidad/preparar_entorno.py                     # .venv
source .venv/bin/activate
brew install llama.cpp pandoc tesseract tesseract-lang                   # si faltan
```

`data_corpus/` (índice v4 + `cache_emb/`) no está en git. Opciones, de la más rápida a la más lenta:

1. Descomprimir el zip de OneDrive `data_corpus_v4.zip` (ver "Respaldo" abajo) en la raíz del repo. Con `cache_emb/` el denso solo codifica lo nuevo.
2. Sin el zip: `python src/reproducibilidad/reproducir.py --corpus <zip del corpus publicado> --hasta indice` (parsea y codifica todo: en un Mac son horas; evitarlo).

Verificar: `python src/reproducibilidad/verificar_corpus.py` y `python src/validaciones/manifest.py` (0 errores).

## 1. Lista de candidatos

```bash
python src/ingesta/huecos_por_citas.py --min-docs 10 --limite 120 --json salidas/huecos_v5.json
```

Criterio fijo antes de medir: normas (`tipo=norma`) con **≥ 10 documentos citantes**, sin actos legislativos que ya estén incorporados a la Constitución, tope **80 documentos** (tiempo de indexación) y máximo 400 artículos por norma (las enormes, como un DUR completo, se descartan por tamaño igual que el Decreto 1165/2019 en v4).

## 2. Sondeo y validación de URLs (script por escribir: `src/ingesta/sondear_normas.py`)

Versionarlo esta vez (el de v4 quedó en un temporal). Reutiliza de `src/ingesta/descargar_fuentes.py`: `ESPEJOS_AJ`, `descargar()`, `buscar_en_espejos()`, `es_pagina_valida()` y `partes_senado()`.

Para cada `doc_id` `tipo_N_AAAA`:
1. Probar `<tipo>_<NNNN>_<AAAA>.htm` (número con y sin ceros a 4 dígitos) en los espejos de Avance Jurídico (CRA, Colpensiones, Cancillería, DIAN) y luego en el Senado (`www.secretariasenado.gov.co/senado/basedoc/<tipo>_<NNNN>_<AAAA>.html`).
2. Aceptar solo si el encabezado dice "<tipo> <N> de <AAAA>" y la página trae "ARTÍCULO".
3. Escribir la entrada en `_adicionales` de `data/registros/fuentes_override.json` con `doc_id`, `titulo` (ASCII sin tildes, del encabezado), `fuente`, `url`, `areas` (las 1–3 áreas de `huecos_v5.json`) y `nota: "ampliacion v5 (AAAA-MM-DD): hueco por citas internas, N docs citantes; areas propuestas, falta confirmar"`.
4. Lo que no valida → lista de no resueltos.

## 3. Descarga y parseo

```bash
python src/ingesta/descargar_fuentes.py --solo <doc_id> ...     # baja también las partes _prNNN
python src/ingesta/parsear_html.py                               # salta lo ya parseado
python src/ingesta/generar_manifest.py --revisar && python src/ingesta/generar_manifest.py
```

Revisar en la salida de `parsear_html.py` los avisos de saltos en la numeración (falta una parte `_prNNN`): esa norma se descarta o se rebaja.

## 4. Segmentar y registros

```bash
python src/indexacion/segmentar.py           # exit 1 si falla un invariante
python src/ingesta/generar_manifest.py       # n_fragmentos
python src/indexacion/solo_por_cita.py       # las normas nuevas NO van al registro (se recuperan sin nombrarlas)
python src/validaciones/manifest.py
```

Comprobar que los fragmentos de v4 no cambian: los `chunk_id` y `texto` previos deben ser idénticos (comparar contra una copia de `chunks.jsonl` v4 guardada antes de empezar).

## 5. Áreas

Las `areas` son propuestas por el detector (áreas de los documentos que citan). Como el retriever prioriza por área (`SYNTAX_AREA_BOOST=2.0`), una área mal puesta mueve la recuperación: revisar al menos las 20 primeras y anotarlas en `docs/ingesta/areas_propuestas_v3.csv`.

## 6. Índice (Mac)

```bash
SYNTAX_DEVICE=mps python src/indexacion/construir_indice.py --batch 16
```

La caché `data_corpus/cache_emb/` (por sha256 del `retrieval_text`) hace que solo se codifiquen los fragmentos nuevos. Referencia: 80 normas ≈ 10–20 mil fragmentos; en un M1 de 16 GB bge-m3 rinde ~5–15 fragmentos/s con MPS ⇒ **20–60 min**. Cerrar otras aplicaciones (memoria). Si no cabe, hacer este paso mañana en la 4090 (`SYNTAX_DEVICE=cuda --batch 64`, minutos) con el mismo `chunks.jsonl`.

**Ojo de reproducibilidad**: los vectores de MPS y de CUDA pueden diferir en los últimos decimales. El índice publicado y la corrida final deben salir de **una sola** máquina: si se codifica en el Mac, publicar ese `index.faiss` + `cache_emb/` y no recodificar en la 4090 (o al revés).

## 7. Medir y decidir

```bash
python src/evaluacion/retrieval_eval.py --modo hibrido --experimento r40_corpus_v5
python src/main.py --split sample --experimento e40_corpus_v5          # requiere llama-server (python src/generacion/modelo.py servir)
python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_e40_corpus_v5.jsonl --experimento e40_corpus_v5
```

KEEP si `doc_hit@10` ≥ 0,902, `respaldo@10` ≥ 0,927 (pérdida ≤ 1 pregunta de 41) y cerradas ≥ 12/15. En un Mac la generación del 8B es lenta (~145 s/pregunta en un M1): medir solo recuperación ahí y dejar la generación para la 4090.

## Respaldo de lo no versionado (zip a OneDrive, privado)

El índice v4 vigente estaba en el worktree `mejoras-mc` de la 4090 y la caché de embeddings en el checkout principal. `data_corpus_v4.zip` (~2,7 GB sin comprimir) junta:

| Contenido | Origen en la 4090 | Tamaño |
|---|---|---:|
| `data_corpus/corpus/` (1.186 `.txt`) | `.claude/worktrees/mejoras-mc/data_corpus/corpus` | 248 MB |
| `data_corpus/indice/` (`chunks.jsonl`, `bm25/`, `index.faiss`, `indice_info.json`, `resumen_indice.json`) | `.claude/worktrees/mejoras-mc/data_corpus/indice` | 1,5 GB |
| `data_corpus/parseo.json` | `.claude/worktrees/mejoras-mc/data_corpus/parseo.json` | 0,6 MB |
| `data_corpus/cache_emb/` (vectores bge-m3 por sha256) | `rag-juridico-santiago/data_corpus/cache_emb` | 722 MB |

No hace falta respaldar: `.venv/` (se recrea), `modelos/*.gguf` (`python src/generacion/modelo.py descargar` los baja verificados por sha256), `herramientas/llama.cpp` (lo baja `reproducir.py`; en Mac, brew). **`scripts/.env` tiene la clave del juez: no va en el zip de OneDrive**; copiarla a mano o crearla de nuevo.

## 8. Cerrar

- `python src/reproducibilidad/verificar_corpus.py --actualizar` **solo en la máquina de referencia** (regenera `hashes_esperados.json`).
- `docs/INDEXACION.md`: sección 18 con la tabla v4 → v5. `docs/ingesta/fuentes_pendientes.md`: "Ampliación v5" con entradas y no resueltos. Estado en `CLAUDE.md` y `python -c "import shutil; shutil.copyfile('CLAUDE.md', 'AGENTS.md')"`.
- Commit en `santiago` (mensaje en español sin tildes) y nuevo zip del corpus/índice para la publicación.
