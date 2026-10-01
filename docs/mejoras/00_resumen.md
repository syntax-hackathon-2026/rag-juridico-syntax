# Planes de mejora del RAG: resumen

Origen: `docs/RESULTADOS_e02_v0.md` (50,66/80 sobre `sample_50`). Cuatro planes independientes, escritos para que cada integrante tome uno. La latencia y la elección de máquina quedan fuera: el equipo las prueba aparte. Por eso no existe un plan 02.

| Plan | Qué ataca | Evidencia | Pruebas |
|---|---|---|---|
| [03 `generation_k` y cerradas](03_generation_k_cerradas.md) | Exactitud de cerradas (0,733 vs 0,905) | 4 de 7 cerradas falladas son `GENERATION` | A/B por id |
| [04 Abstención](04_abstencion.md) | Respuestas malas que valdrían 0,5 si se abstuviera | 0 abstenciones, 9 malas de 43 | pytest + A/B |
| [05 Reranker](05_reranker.md) | Artículo correcto fuera del top-10 | 10 de 17 errores son de recuperación | A/B de recuperación |
| [06 Parser de referencias](06_parser_referencias.md) | Preguntas que nombran norma o artículo y no se recuperan | Parser ya existe en `citations.py` | pytest + A/B |

## Qué propone cada plan

### 03: barrido de `generation_k` y revisión de cerradas
1. Clasificar a mano los 4 casos `GENERATION` (ids 58, 128, 647, 671): evidencia en el top-5, en 6–10, ausente, o pregunta defectuosa.
2. Barrer `generation_k ∈ {3, 5, 7, 10}` con `retrieval_k=10` fijo, solo en las 15 cerradas, tras comprobar que repetir `k=5` reproduce `e02_v0`.
3. Si hay casos de razonamiento erróneo, una única variante de prompt para cerradas (`p-v1`).
- **Keep:** ≥ 2 cerradas más, con tendencia en `k` vecinos, sin bajar citación.

### 04: abstención por señales
1. **Fase A:** análisis offline de las señales que la traza ya guarda (`score_top1`, margen, ranks BM25/denso, `frac_en_ambas_ramas`, `normas_pregunta_en_evidencia`) contra el acierto, por formato.
2. **Fase B:** regla simple con umbrales **por formato**: cerradas casi nunca (abstenerse da 0 en exactitud), texto libre más holgado. Bandera `SYNTAX_ABSTENCION`.
3. **Fase C:** validar reaplicando la regla a las trazas y medir sensibilidad al umbral.
- **Keep:** ≥ 0,3 pts netos, sin bajar exactitud, estable a ±20 % del umbral.

### 05: reranker
1. **Fase 0:** medir cuántas veces el artículo correcto está en el rango 11–40. Si el techo es bajo (< 4 de 19), se cierra el plan.
2. Interfaz `Reranker` (`Qwen3-Reranker-0.6B` o `bge-reranker-v2-m3`), integrada en `Retriever.retrieve` tras el RRF y antes del recorte a `k`, determinista y con bandera `SYNTAX_RERANKER`.
3. Tres variantes de alcance (40, 20, fusión de rangos) y parametrización de `fusion`/`reranker` en las evaluaciones.
- **Keep:** `art_hit@10` +3 preguntas, `mrr` no baja, latencia dentro del presupuesto.

### 06: parser de referencias
1. **Fase 0:** contar cuántas preguntas nombran norma o artículo y cuántas fallan hoy.
2. Reutilizar `citations.extract` (no reescribir `CODES`) y un índice `(canonico, articulo)` en el retriever.
3. Integrar como **candidato extra** o boost suave, nunca filtro duro (el corpus no tiene campo `area` y un error ocultaría la respuesta). Bandera `SYNTAX_LOOKUP`.
- **Keep:** +2 preguntas con referencia explícita sin sacar aciertos del top-10.

## Orden recomendado y dependencias

```
03 ──► 04 ──► (recalibrar 04 si se adopta 05 o 06)
 └──────────► 05 ◄──► 06      (ambos tocan Retriever.retrieve)
```

- **03 primero:** barato, sin código, y sus trazas dan datos para el plan 04.
- **05 y 06 son paralelos** pero tocan el mismo punto. Orden de composición dentro de `retrieve`: lookup (06) → RRF → reranker (05) → recorte. Cada uno con su bandera, apagada por defecto.
- **Tras adoptar 05 o 06:** repetir el barrido de `k` (03) y recalibrar la abstención (04), porque cambian el top-5 y los scores.
- La latencia disponible (decidida fuera de estos planes) condiciona 03 (`k` alto) y 05 (coste del reranker).

## Reglas comunes a todos los planes

- Método del repo: observar → medir → diagnosticar → un cambio → benchmark → keep/revert. **Un cambio por experimento.**
- Cada cambio entra con una bandera `SYNTAX_*` apagada por defecto; apagada, el comportamiento es idéntico al actual.
- Cada corrida registra fila en `evaluation/experiments.csv` y deja trazas + `.meta.json`.
- Cambiar un texto de `prompts.py` implica subir `PROMPT_VERSION`.
- `legal_basis`, respuestas esperadas e `id` son ground truth: solo para evaluación, nunca en runtime.
- Con 50 preguntas, 1–2 de diferencia no es significativo; a igualdad, gana lo más simple.
- Dependencias nuevas (p. ej. `pytest`, un modelo) van en `requirements.txt` con `==` en el mismo commit que el import (`verificar_deps.py --fix`).
- Determinismo: desempate por `chunk_id`, fp32, y comprobar con `comparar_entregas.py`.
- Windows + Mac: `pathlib`, UTF-8, sin dependencias de bash en `src/`.

## Nota para quien tome un plan

Cada plan termina con una lista de tareas de ≤ 1 sesión. Al cerrarlo, dejar un `resultados_NN.md` junto a su plan con la tabla de resultados y la decisión keep/revert, y actualizar `docs/GENERACION.md` o `docs/INDEXACION.md` si cambia el comportamiento por defecto.
