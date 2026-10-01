# Resultados plan 03 — `generation_k` y cerradas

- **Rama:** `sofi`
- **Baseline:** `e02_v0` (`evaluation/generacion/e02_v0/`, `generation_k=5`, `p-v0`, híbrido, `retrieval_k=10`)
- **Fecha:** 2026-10-01
- **Commit local al documentar:** ver `git rev-parse --short HEAD` en la rama `sofi`

## 3.1 Clasificación manual (ids 58, 128, 647, 671)

Fuentes: `evaluation/generacion/e02_v0/errores.csv`, `trazas.jsonl`, `entrega.jsonl`, `data/sample_50.jsonl`. Posición del **cuerpo** y del **artículo** (según `legal_basis` + `citations.article_level`) sobre el top-10 de la traza; frontera del decoder: `generation_k=5`.

| id | Esperada | Modelo | `rank_doc` | `rank_art` | Artículo ref. en top-5 | Artículo ref. en 6–10 | Clase | Evidencia breve |
|---:|:---:|:---:|:---:|:---:|---|---|---|
| 58 | A | B | 2 | — | No (solo cuerpos CGP / estatuto en `legal_basis`, sin artículo) | No | **A** | En pos. 2 y 5 hay fragmentos del CGP (`codigo_general_proceso`). El modelo cita el art. 1 del CGP como marco “general” y elige B (Ley 270); no usa la norma que el banco marca (Ley 1564 / estatuto consumidor). La pregunta mezcla SIC y opciones de ley distintas al CGP 2012 — posible ruido del banco, pero con documento de `legal_basis` dentro del top-5. |
| 128 | D | B | 1 | — | No (`legal_basis` solo cuerpo `decreto/663/1993`) | No | **A** | Pos. 1–5 son artículos del Decreto 663/1993. El modelo reconoce compañías de financiamiento y bancos pero omite **Fintech** (opción D). Evidencia suficiente en el prompt; error de lectura / opción. |
| 647 | B | D | 5 | — | No (cuerpo `codigo_civil` en pos. **5**, límite de `k=5`) | No | **A** | El único fragmento del Código Civil está en el rank 5 (`codigo_civil#art_1842`). La justificación apoya D con sentencias T/C (pos. 1–4), no el efecto personal “ayuda” del CC. Con `k=3` se pierde el CC del prompt; con `k=7` no entra otro chunk del CC en 6–10. |
| 671 | C | D | — | — | N/A | N/A | **D** | `legal_basis`: «Doctrina.» → `ref_b` vacío. `diagnosticar()` etiqueta `GENERATION` por la rama `not ref_b`, no porque hubiera evidencia en top-5. No hay referencia evaluable en corpus; la justificación mezcla reglas de desempate de contratación (Decreto 1082). No es palanca de `k` ni de prompt cerrado. |

**Lectura:** 3 casos **A** (58, 128, 647) apuntan a razonamiento / prompt; 671 es **D** y no debe contarse en el barrido de `k`. Ninguno es **B** (artículo correcto solo en 6–10) ni **C** puro (documento ausente del top-10) entre estos cuatro.

### Opciones (id 58) vs recuperación

Pregunta: actuaciones jurisdiccionales ante la SIC. Opción A: «Ley 1564 de 2002» (distinta del CGP Ley 1564/2012). El `legal_basis` del banco no alinea cuerpo con la redacción de la opción correcta — conviene no sobreinterpretar citación en este id.

## 3.2 Determinismo y barrido `generation_k`

### Control `k=5` vs `e02_v0`

No se pudo **regenerar** `e04_k5` en esta máquina (bloqueos abajo). Como control offline:

- `comparar_entregas.py salidas/sample_e02_v0.jsonl salidas/sample_e02_v0.jsonl` → **0 diferencias** en 50 ítems (herramienta OK).
- Tras correr `e04_k5`, usar:

```bash
python src/evaluacion/comparar_entregas.py salidas/sample_e02_v0.jsonl salidas/sample_e04_k5.jsonl \
  --ids 51 58 60 128 290 308 352 358 487 528 600 617 647 671 748
```

Criterio: 0 diferencias en las 15 cerradas si mismo GGUF, índice, `p-v0` y servidor.

### Barrido `{3, 5, 7, 10}` (15 cerradas)

IDs (desde `data/sample_50.jsonl`, `formato=multiple_choice`):

`51 58 60 128 290 308 352 358 487 528 600 617 647 671 748`

Scripts reproducibles (misma máquina que `e02_v0`, decoder servido):

- Windows: `salidas/correr_e04_cerradas.ps1`
- Mac/Linux: `salidas/correr_e04_cerradas.sh`

Equivalente manual:

```bash
python src/generacion/modelo.py servir   # otra terminal
for k in 3 5 7 10; do
  python src/main.py --split sample --experimento e04_k${k} --generation-k ${k} \
    --ids 51 58 60 128 290 308 352 358 487 528 600 617 647 671 748 --sin-reanudar
  python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_e04_k${k}.jsonl --experimento e04_k${k}
done
```

### Tabla de métricas del barrido

| Experimento | `generation_k` | Exactitud cerradas | Citación (pts) | `regenerado` | Latencia media cerradas | Notas |
|---|---:|---:|---:|---:|---:|---|
| e02_v0 | 5 | 11/15 (0,733) | 15,10 | 4 (total corrida) | ~131 s | baseline |
| e04_k3 | 3 | *pendiente* | *pendiente* | *pendiente* | *pendiente* | |
| e04_k5 | 5 | *pendiente* | *pendiente* | *pendiente* | *pendiente* | control |
| e04_k7 | 7 | *pendiente* | *pendiente* | *pendiente* | *pendiente* | |
| e04_k10 | 10 | *pendiente* | *pendiente* | *pendiente* | *pendiente* | revisar `uso` en trazas vs `LLM_CTX=8192` |

Rellenar filas desde `evaluation/generacion/e04_k*/reporte.json` y `errores.csv`; registrar en `evaluation/experiments.csv` vía `evaluar_entrega.py`.

### Cambios por id (plantilla)

Comparar con `comparar_entregas.py` y `errores.csv` entre `e02_v0` y cada `e04_k*`. Anotar solo cerradas con cambio de letra o abstención.

## 3.3 Prompt `p-v1` (condicional)

Hay **tres casos A** (58, 128, 647) donde convendría forzar citar el pasaje que sostiene la opción y descartar las demás con razón breve (`prompts.py` + `PROMPT_VERSION` → `p-v1`).

**Decisión:** no implementar `p-v1` hasta completar el barrido de `k` con el mismo decoder: primero aislar si `k` mueve 647 (frontera en rank 5) o los demás. Si tras el barrido la exactitud sigue ≤ baseline+1, entonces un solo experimento `e04_k*_pv1` sobre las 15 cerradas.

## Decisión keep / revert (provisional)

| Palanca | Decisión | Motivo |
|---|---|---|
| `generation_k` | **Mantener 5** (default) | Barrido no ejecutado aquí; sin evidencia de ≥2 cerradas ganadas con tendencia en `k` vecinos. |
| `p-v0` | **Mantener** | Sin A/B de prompt. |
| `docs/GENERACION.md` | **Sin cambio** | Default sigue siendo 5. |

Tras ejecutar el barrido en entorno con índice + GPU/Mac campus:

1. Si algún `k` cumple criterio del plan (≥2 cerradas vs `k=5`, citación estable, latencia OK) → actualizar `SYNTAX_GENERATION_K` / `GENERACION.md` y correr las 50 con ese `k` + `--ragas`.
2. Si no → cerrar plan 03 con default 5 y opcionalmente abrir `p-v1`.

## Bloqueos en este entorno (2026-10-01)

| Recurso | Estado |
|---|---|
| `data_corpus/indice/index.faiss` | **Ausente** — `config.verificar_indice()` falla; hay que reconstruir índice (`segmentar.py`, `construir_indice.py`) o copiar el corpus publicado del equipo. |
| Decoder `127.0.0.1:8080` | **No responde** — levantar con `python src/generacion/modelo.py servir` y GGUF en `modelos/`. |
| Juez RAGAS | No requerido para el barrido de cerradas; sí para la corrida final de 50 tras elegir `k`. |

## Tareas del plan 03

- [x] 3.1 Tabla A/B/C/D con posición en top-10
- [x] Scripts + comando reproducible para barrido y control `k=5`
- [x] `--generation-k` en `main.py` (alternativa a variable de entorno)
- [ ] Repetir `e04_k5` y comparar con `e02_v0` (determinismo)
- [ ] Correr `k ∈ {3, 7, 10}` + evaluar y filas en `experiments.csv`
- [ ] Decidir `k` candidato; corrida 50 + `--ragas` si aplica
- [ ] (Condicional) `p-v1` y A/B
- [x] Este documento; `GENERACION.md` sin cambio de default hasta tener números
