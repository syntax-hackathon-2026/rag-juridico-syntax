# Pendientes del plan de ampliación del corpus (v3)

Estado al 2026-10-02. Plan original: `docs/INDEXACION.md` sección 13 y `docs/ingesta/fuentes_pendientes.md` ("Ampliación v3"). Corte propuesto: **viernes 22:00**. Lo que no esté medido a esa hora no entra, y el sábado solo se corren preguntas.

## Ya hecho (commit `2327d10`, rama `santiago`)

- **Fase 1, normas**: entraron las 95 leyes y decretos de la lista (primera y segunda ola), más la Decisión Andina 351/1993.
- **Fase 2, sentencias**: 37 hitos y el lote de **242 SU de 2020–2026** (258 encontradas, 16 ya estaban).
- **Pipeline**: descarga, parseo, manifest y segmentación, con un resultado de **588 documentos y 113.519 fragmentos**. El validador da 0 errores, y `hashes_esperados.json` y `CORPUS.md` están actualizados.
- **Medición solo en BM25** (`e04_corpus_v3_bm25`): respaldo@10 baja de 0,927 a 0,866 y doc_hit@10 de 0,805 a 0,707 sobre sample_50.
  - La medición está sesgada en contra, porque todo el gold de sample_50 ya estaba en v2.
  - Del lado de la ganancia, las 15 de 15 SU nombradas en la pregunta llegan al top-10, y 10 de 12 normas e hitos nuevos también.

## 1. Bloqueante: medir el híbrido en la 4090 y decidir KEEP/REVERT

Sin este paso v3 no se puede congelar. Pasos en la 4090, desde la raíz del worktree de la rama:

```powershell
# zip del corpus v3 fuera del repo o en data_corpus\ (no en la raíz: .gitignore no cubre *.zip)
# caché de embeddings v2 en data_corpus\cache_emb\BAAI__bge-m3@5617a9f61b02 (evita recodificar 47.966 fragmentos)
powershell -ExecutionPolicy Bypass -File reproducir.ps1 -Corpus C:\syntax\corpus_v3.zip --hasta indice
.venv\Scripts\python src\evaluacion\retrieval_eval.py --modo bm25 denso hibrido --experimento e04_corpus_v3
```

- [ ] Codificar los ~65.500 fragmentos nuevos (bge-m3, `--batch 64`) y obtener `index.faiss` v3.
- [ ] Correr `retrieval_eval` híbrido (`e04_corpus_v3`) y compararlo con `e03_corpus_v2`: respaldo@10 0,927, doc_hit@10 0,854.
- [ ] Correr el pipeline completo sobre sample (`e04_v3_rtx4090`) para medir la latencia con el índice 2,4 veces más grande. El objetivo es < 10 s por pregunta.
- [ ] **Regla de decisión**:
  - **KEEP v3** si el híbrido no empeora de forma material (≤ 1–2 preguntas de 41, dada la medición sesgada).
  - Si diluye, se puede aplicar la mitigación de la sección 2, o **REVERT parcial** a "v2 + normas + hitos" (respaldo@10 BM25 0,890).
  - Si nada aguanta, **REVERT** a v2. El índice v2 está respaldado en `data_corpus/respaldo_indice_v2/` y `data_corpus/resultado_indice.zip`.
- [ ] Anotar la fila en `evaluation/experiments.csv` y el entorno en `evaluation/entornos/e04_corpus_v3.json`, y completar la sección 13 de `docs/INDEXACION.md`.

## 2. Condicional: mitigación "SU solo si se nombra"

Solo si el híbrido muestra dilución. **No está implementada.**

- [ ] En `src/recuperacion/`, sacar los fragmentos del lote SU 2020–2026 (nota "lote de sentencias de unificacion" en `_adicionales`) de las ramas BM25 y denso, **salvo** que `citations.extract(pregunta)` nombre esa sentencia.
- [ ] Efecto esperado en sample_50: las métricas de "v2 + normas + hitos", conservando las 15 de 15 SU nombradas.
- [ ] Riesgo: las preguntas que tratan el tema de una SU sin nombrarla no la recuperan. Es lo mismo que pasa hoy con v2.
- [ ] Medir otra vez (`e05_…`) antes de dejarla.

## 3. Congelar y publicar (después del KEEP/REVERT)

- [ ] Si se revierte o recorta: quitar las entradas de `_adicionales` y regenerar en este orden: parseo → `generar_manifest.py` → `segmentar.py` → `generar_manifest.py` → `construir_indice.py`.
- [ ] `python src/reproducibilidad/verificar_corpus.py --actualizar` en la máquina de referencia, para el `hashes_esperados.json` final.
- [ ] **Empaquetado**: escribir `package_corpus.py`, que todavía no existe.
  - Debe juntar `corpus/`, `indice/` (`index.faiss`, `chunks.jsonl`, `bm25/`, `indice_info.json`), `LICENSE` (`../LICENSE`) y una copia de `corpus_manifest.json` en `Syntax-corpus….zip`.
  - Anotar el sha256 del zip en `CORPUS.md`.
- [ ] Subir el zip a OneDrive con enlace público y verificarlo en una ventana privada.
- [ ] Poner el enlace en `enlace_nube`, que hoy dice `"<URL>"`, y en `README.md`. Después correr `python src/validaciones/manifest.py --strict`, que debe dar 0 errores y 0 avisos.
- [ ] Repartir `index.faiss` y `cache_emb/` v3 a los demás equipos.
- [ ] PR de `santiago` → `main` después de medir: draft ahora o PR normal con el resultado.

## 4. Revisión humana, sin bloquear la medición

- [ ] **Confirmar las `areas` de los 375 documentos nuevos**: las propuso un agente.
  - Las 242 SU van todas como `Derecho constitucional`, lo cual es claramente incompleto: muchas son laborales, pensionales, de salud o de familia.
  - Se corrigen en `_adicionales` de `fuentes_override.json` y luego se regenera con `generar_manifest.py`. Afecta el inventario de `CORPUS.md` y la nota de corpus (5 pts), no el retrieval.
- [ ] Sumar los 375 a `docs/ingesta/areas_por_asignar.md`, que hoy solo lista los 30 adicionales de v2.
- [ ] SU-163/2023: la relatoría solo publica la nota de nulidad (Auto 823/2024). Decidir si se deja (es inofensivo y responde "fue anulada") o se quita.

## 5. Quedó fuera del plan (solo si sobra tiempo antes del corte; si no, documentar como limitación)

- [ ] **Sentencias C- de control de las leyes de la Fase 1**. El plan las incluía en los hitos y no se bajaron, salvo la C-264/2026 de la Ley 2381/2024.
  - Son baratas: el patrón de la relatoría es `relatoria/<año>/C-<nnn>-<aa>.htm`.
  - Prioridad: la C de la Ley 1751/2015 (C-313/14, ya está), y las de Ley 1957/2019, Ley 2213/2022 y Ley 2277/2022.
- [ ] **Decisiones andinas 608/2005 y 345/1993**: no se bajaron.
  - Igual que la 351, `citations.py` no las reconoce, así que irían como `documento` en `cabeceras.DOCUMENTOS` y **no puntúan en citación**, solo en contenido.
- [ ] **Decreto 2555/2010** (financiero): descartado por tamaño.
- [ ] **T- de 2025–2026** (la semilla trae 8). El plan decía que solo entraban si la medición no mostraba dilución, así que depende de la sección 1.
- [ ] **Verificación por norma nueva**: `retriever.py "artículo N de la Ley X de Y" --modo hibrido` con el fragmento esperado en el top-3. Se probó en una muestra de 12 y fallaron la Ley 361/1997 y la C-590/2005 cuando no se nombran. No se hizo en las 95.
- [ ] Cubrir con el lookup por referencia (`SYNTAX_LOOKUP`, apagado por defecto) los documentos nuevos nombrados en la pregunta. Solo vale la pena si el híbrido no los trae por sí mismo.

## Nota de proceso

Los scripts auxiliares de la ampliación (`agregar_v3.py`, `sondear_su.py`, `agregar_su.py`, `shard.py`, `fusionar.py`) vivían en el directorio temporal de la sesión y no están versionados. El procedimiento quedó descrito en `fuentes_pendientes.md`. Si hay que repetir el sondeo de SU, el criterio es que una SU existe si su página de la relatoría carga `/relatoria/encabezado.js`, con nnn = 1..620 por año.
