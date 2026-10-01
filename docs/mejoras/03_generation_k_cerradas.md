# Plan 03: barrido de `generation_k` y revisión de las cerradas con `GENERATION`

Parte de [`00_resumen.md`](00_resumen.md). Independiente de los planes 05 y 06; su salida (trazas) alimenta el plan 04.

## 1. Objetivo y métrica

Cerrar la brecha de exactitud en preguntas cerradas (0,733 con `e02_v0` frente a 0,905 del baseline), que vale hasta ~3,4 pts de los 20.

- **Métrica principal:** exactitud de cerradas (`evaluate.py`), sobre las 15 de `sample_50`.
- **Métricas de control (no deben empeorar):** citación (recall ponderado, 0 citas sin respaldo), RAGAS de texto libre, `regenerado` (cuántas respuestas se regeneran por citas sin respaldo).
- **Variable de coste:** tokens del prompt y latencia por pregunta. El presupuesto de latencia lo fija el equipo aparte; este plan solo reporta el coste de cada `k`.

## 2. Evidencia

`docs/RESULTADOS_e02_v0.md`: 4 de las 7 cerradas falladas son `GENERATION` (ids 58, 128, 647, 671). El diagnóstico lo asigna `diagnosticar()` (`src/evaluacion/evaluar_entrega.py:51`) cuando `rank_doc <= generation_k`. Eso significa que el documento correcto estaba en el top-5 enviado al decoder, pero **no** implica que el artículo correcto estuviera: `rank_doc` es por documento. Primera tarea: separar esos casos.

## 3. Diseño

### 3.1 Revisión manual de los 4 casos (sin código nuevo)

Para cada id, usando `evaluation/generacion/e02_v0/errores.csv` y `trazas.jsonl`:

1. ¿El artículo correcto (según `legal_basis`, solo como evaluación) estaba en `top[:5]`, en `top[5:10]` o fuera?
2. ¿La opción elegida contradice un pasaje presente, o el pasaje no resuelve la pregunta?
3. Clasificar cada caso: `A` (evidencia presente y el modelo razonó mal), `B` (evidencia solo en 6–10), `C` (evidencia ausente, es retrieval), `D` (pregunta ambigua o del banco defectuoso).

Registrar la tabla en el propio MD de resultados del experimento. Define si el barrido de `k` o el prompt es la palanca.

### 3.2 Barrido de `generation_k`

- Valores: `k ∈ {3, 5, 7, 10}`, con `retrieval_k=10` fijo. Se controla con `SYNTAX_GENERATION_K` (`src/config.py:94`); `main.py` no lo recibe por CLI.
- Una corrida por valor, mismo prompt (`p-v0`), mismo decoder y misma máquina. Nombre de experimento: `e04_k3`, `e04_k5` (repetición de control), `e04_k7`, `e04_k10`. Si ya existe otra serie `e04_*`, usar el siguiente número libre.
- Solo se barren **cerradas** (`--ids` con las 15 cerradas) para ahorrar tiempo; las demás se corren únicamente con el `k` candidato final.
- Trampa: `diagnosticar()` lee `traza["generation_k"]`, así que la frontera `GENERATION`/`RANKING` se mueve con `k`. Comparar errores por id, no por categoría.
- Con `k=10` los pasajes del prompt cubren los 10 de evidencia; comprobar que no se supera `LLM_CTX=8192` (ver `uso` en las trazas).

### 3.3 Variante de prompt para cerradas (solo si 3.1 muestra casos `A`)

- Cambiar `INSTRUCCIONES["multiple_choice"]` en `src/generacion/prompts.py` para pedir: (a) citar el pasaje que respalda la opción elegida; (b) descartar cada opción restante con una razón breve. El `schema()` ya pone `justificacion` antes de `respuesta_correcta`, así que el razonamiento precede a la letra.
- Subir `PROMPT_VERSION` (`p-v0` → `p-v1`). Cambiar un texto sin subirla rompe la trazabilidad.
- Una sola variante a la vez. Si hay dos ideas, dos experimentos.

## 4. Archivos

| Archivo | Cambio |
|---|---|
| `src/generacion/prompts.py` | Solo en 3.3: instrucción de cerradas y `PROMPT_VERSION` |
| `src/main.py` | Opcional: flag `--generation-k` que sobreescriba la variable (hoy solo por entorno) |
| `salidas/correr_e04_k*.sh` | Opcional: scripts de corrida, al estilo de `correr_e02_v0.sh` |
| `evaluation/experiments.csv` | Una fila por corrida (`evaluar_entrega.py`) |
| `docs/mejoras/resultados_03.md` | Nuevo: tabla de los 4 casos y del barrido |

No hay cambios en `retriever.py` ni en `abstencion.py`.

## 5. Cómo activarlo y revertirlo

- `k`: `SYNTAX_GENERATION_K=<n>`. Revertir = no definir la variable (queda 5).
- Prompt: la versión vive en el código; revertir = volver a `p-v0` por git. Las trazas guardan `prompt_version`.

## 6. Pruebas (A/B de calidad; no hay pytest en este plan)

```bash
export SYNTAX_GENERATION_K=7
python src/main.py --split sample --experimento e04_k7 --ids <15 cerradas>
python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_e04_k7.jsonl --experimento e04_k7
python src/evaluacion/comparar_entregas.py salidas/sample_e02_v0.jsonl salidas/sample_e04_k7.jsonl
```

- `comparar_entregas.py` sirve para verificar que repetir `k=5` reproduce `e02_v0` (determinismo) antes de interpretar diferencias.
- Reportar por id qué cerradas cambian de respuesta y en qué sentido (acierto→error, error→acierto).

## 7. Criterio keep/revert

- **Keep** un `k` distinto de 5 si: (a) gana ≥ 2 cerradas respecto de `k=5` y el sentido se mantiene en al menos dos valores vecinos de `k` (señal de tendencia, no de ruido); (b) citación no baja; (c) la latencia añadida cabe en el presupuesto del equipo.
- **Keep** el prompt nuevo solo si mejora con el `k` elegido y no empeora semi-abiertas/abiertas (el cambio es solo en cerradas, pero verificar `ragas`).
- Si ninguna variante supera 1 pregunta de diferencia: dejar `k=5` y `p-v0` (a igualdad gana lo más simple).
- Con 15 cerradas una diferencia de 1–2 no es significativa; no concluir de un solo `k`.

## 8. Riesgos y trampas

- `k` alto añade ruido: el modelo pequeño puede distraerse con pasajes irrelevantes.
- `k` alto sube el contexto y la latencia (el decoder es el cuello de botella).
- Cerradas con `legal_basis` sin cita extraíble no puntúan en citación; no usarlas para juzgar citación.
- El id 374 está excluido de la calificación (`FLAWED_IDS`); no contarlo.
- `legal_basis` es solo evaluación: nunca entra al prompt ni a ninguna lógica de runtime.

## 9. Dependencias

- Ninguna previa. Conviene correr antes que el plan 04: las trazas de estos barridos dan más señales para calibrar la abstención.
- Si el plan 05 (reranker) se adopta, repetir el barrido de `k` al final, porque el top-5 cambia.

## 10. Tareas (cada una cabe en una sesión)

- [ ] 3.1: tabla de los 4 casos (A/B/C/D) con la posición del artículo correcto en el top-10.
- [ ] Verificar determinismo: repetir `k=5` y comparar con `e02_v0` (`comparar_entregas.py`).
- [ ] Correr `k=3, 7, 10` sobre las 15 cerradas y registrar filas en `experiments.csv`.
- [ ] Decidir `k` candidato; correrlo sobre las 50 y evaluar con `--ragas`.
- [ ] (Condicional) variante de prompt `p-v1` para cerradas y su A/B.
- [ ] Documentar resultado en `docs/mejoras/resultados_03.md` y actualizar `docs/GENERACION.md` si cambia el valor por defecto.
