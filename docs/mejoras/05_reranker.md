# Plan 05: reranker

Parte de [`00_resumen.md`](00_resumen.md). Comparte el punto `Retriever.retrieve` con el plan 06: coordinar el orden de integración.

## 1. Objetivo y métrica

Subir el artículo correcto al top-10 (y al top-5 que ve el decoder) reordenando los candidatos del RRF con un modelo más fino.

- **Métricas de recuperación** (`retrieval_eval.py`): `doc_hit@1/3/5/10`, `art_hit@1/10`, `mrr`, `respaldo@10`.
- **Métricas finales:** citación (el recall depende del top-10), exactitud de cerradas y RAGAS.
- **Coste:** latencia añadida por pregunta y memoria. El presupuesto lo fija el equipo con la máquina final.

## 2. Evidencia y decisión previa (medir antes de construir)

`docs/RESULTADOS_e02_v0.md`: 10 de 17 errores son de recuperación. Fila `e01_bge_m3_hibrido`: `doc_hit@10=0,8537`, `art_hit@10=0,5263` (19 preguntas con artículo; señal ruidosa).

Un reranker solo ayuda si el artículo correcto está en el rango 11–40 de los candidatos con frecuencia. Si ya está en el top-10 o no está en los 40, no sirve. **Esta medición decide si el plan continúa.**

## 3. Diseño

### 3.1 Fase 0: medir el techo (sin modelo nuevo)

Extender `src/evaluacion/retrieval_eval.py` para reportar, sobre los `N_CANDIDATOS=40` del RRF:

- `art_hit@20`, `art_hit@40` y `doc_hit@40`.
- Distribución del rango del artículo correcto: 1–5, 6–10, 11–20, 21–40, fuera.
- «Techo de ganancia» = preguntas con artículo en 11–40.

**Regla de continuación:** seguir si el techo es ≥ 4 preguntas de las 19 con artículo (o ≥ 8 puntos porcentuales de `art_hit@10`). Si no, cerrar el plan con la tabla como justificación.

Si hace falta más señal, calcular lo mismo sobre las 41 preguntas con documento (`doc_hit@40`).

### 3.2 Fase 1: reranker en `Retriever.retrieve`

- Punto de integración: `src/recuperacion/retriever.py`, `retrieve(consulta, k, modo, n_candidatos)` (≈línea 94). Después del RRF y antes de recortar a `k`.
- Nueva clase `Reranker` en `src/recuperacion/reranker.py` con la interfaz `rerank(consulta, candidatos: list[RetrievedChunk]) -> list[RetrievedChunk]`. Detrás de una interfaz, igual que el decoder, para cambiar de modelo sin tocar el resto.
- Entrada del cross-encoder: consulta + `retrieval_text` o `texto` del chunk (probar ambos; el texto con cabecera citable es el que ve el decoder).
- Candidatos de modelo, en orden de prueba:
  1. `Qwen3-Reranker-0.6B`.
  2. `BAAI/bge-reranker-v2-m3` (misma familia que el encoder).
  Verificar la licencia antes de usar (el corpus se publica bajo CC-BY-4.0; evitar modelos no comerciales) y fijar la revisión del modelo en `config.py`, como `ENCODER_REVISION`.
- **Determinismo:** fp32 (o un dtype fijo documentado), desempate por `chunk_id`, sin dropout, mismo batch y orden de entrada. Guardar el score del reranker en `meta["rerank_score"]` y el rank previo en `meta["rank_rrf"]`.
- **Alcance del reordenamiento:** probar tres variantes, una por experimento:
  - (a) reordenar los 40 y quedarse con el top-10;
  - (b) reordenar solo los 20 primeros;
  - (c) combinar el score del reranker con el RRF (fusión de rangos) en lugar de sustituir.
- `Retriever.retrieve` mantiene el contrato actual: devuelve una lista de `RetrievedChunk` ordenada. Con el reranker apagado el resultado es idéntico al de hoy.

### 3.3 Fase 2: parametrizar la evaluación

- `src/evaluacion/retrieval_eval.py:160` y `evaluar_entrega.py:200` escriben `fusion="rrf60"` y `reranker=""` a mano. Cambiar a leer los valores del `Retriever` o de la configuración, para que cada fila de `experiments.csv` quede etiquetada.
- Añadir una columna `latencia_rerank_ms` a la fila, o ponerlo en `notas` si no se quiere tocar el esquema de 35 columnas.

## 4. Archivos

| Archivo | Cambio |
|---|---|
| `src/recuperacion/reranker.py` | Nuevo: interfaz y backend(s) |
| `src/recuperacion/retriever.py` | Llamada opcional al reranker en `retrieve` |
| `src/config.py` | `SYNTAX_RERANKER`, `RERANKER_MODEL`, `RERANKER_REVISION`, `RERANK_N` |
| `src/evaluacion/retrieval_eval.py` | Métricas hasta 40 y columnas `fusion`/`reranker` reales |
| `src/evaluacion/evaluar_entrega.py` | Etiquetar el reranker en `experiments.csv` |
| `requirements.txt` | Solo si el modelo exige un paquete nuevo (regla de CLAUDE.md: mismo commit) |
| `docs/INDEXACION.md` | Sección con los resultados |

## 5. Cómo activarlo y revertirlo

`SYNTAX_RERANKER=off|<nombre>`; por defecto `off`. Registrar el modelo y su revisión en `.meta.json`. Los modelos pesados no van al repo (se descargan, como el GGUF y bge-m3).

## 6. Pruebas (A/B de calidad; no se plantea pytest en este plan)

```bash
python src/evaluacion/retrieval_eval.py --modo hibrido --experimento e05_sin_rerank
SYNTAX_RERANKER=<modelo> python src/evaluacion/retrieval_eval.py --modo hibrido --experimento e05_rerank_a
```

- Comparar `art_hit@10`, `mrr`, `respaldo@10` y el detalle por pregunta (`evaluation/retrieval/<exp>_<modo>.jsonl`): cuáles suben, cuáles bajan.
- Una vez elegida la variante, correr generación completa y `evaluar_entrega.py --ragas`.
- Determinismo: dos corridas del reranker sobre las mismas consultas deben dar el mismo orden (comparar con `comparar_entregas.py` sobre la entrega final).
- Verificación puntual de seguridad: ningún chunk que el reranker devuelva puede estar fuera de los candidatos del RRF (los `pasajes_recuperados` siguen validando contra el manifest).

## 7. Criterio keep/revert

- **Keep** si `art_hit@10` sube ≥ 3 preguntas de las 19 (o ≥ 8 pp) **y** `mrr` no baja, **y** la latencia añadida cabe en el presupuesto.
- **Revert** si solo mejora `art_hit@1` sin tocar `@10` (no cambia la citación), si baja `doc_hit@10`, o si la latencia no cabe.
- A igualdad, gana lo más simple: sin reranker.

## 8. Riesgos y trampas

- Con 19 preguntas con artículo, la métrica de artículo es ruidosa. Mirar también `doc_hit` y `mrr` sobre las 41 con documento.
- Un cross-encoder sobre 40 pasajes de ~350 palabras es caro en CPU/MPS: medirlo en la máquina final, no en el Mac.
- Las sentencias (111 de 186 documentos) se segmentan en ventanas largas; el reranker puede favorecerlas sobre un artículo corto. Revisar el efecto por tipo de documento.
- `texto` = cabecera + literal. El evaluador valida las citas contra `texto`; el reranker no debe modificarlo.
- No reentrenar ni afinar el reranker (CLAUDE.md: no fine-tuning).
- Interacción con el plan 06: el lookup determinista puede resolver los casos fáciles; medir el reranker con y sin él.

## 9. Dependencias

- Fase 0 es independiente. Fases 1–2 conviene hacerlas después de decidir el presupuesto de latencia.
- Tras adoptarlo, repetir el barrido de `generation_k` del plan 03 y recalibrar la abstención del plan 04.
- Coordinar con el plan 06 el orden dentro de `retrieve`: lookup (candidatos extra) → RRF → reranker → recorte.

## 10. Tareas

- [ ] Fase 0: métricas `@20`/`@40` y distribución de rangos; decisión go/no-go.
- [ ] Elegir y fijar el modelo (licencia, revisión); descargar.
- [ ] Interfaz `Reranker` y backend; flag y config.
- [ ] Integrar en `retrieve` con el contrato actual intacto.
- [ ] Parametrizar `fusion`/`reranker` en las evaluaciones.
- [ ] A/B de las tres variantes (a/b/c) y elección.
- [ ] Prueba de determinismo y de latencia en la máquina final.
- [ ] Documentar en `docs/INDEXACION.md` y registrar filas en `experiments.csv`.
