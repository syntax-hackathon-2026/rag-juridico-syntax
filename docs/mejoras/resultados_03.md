# Resultados plan 03 — `generation_k` y cerradas

- **Rama:** `sofi`
- **Baseline:** `e02_v0` (`evaluation/generacion/e02_v0/`, `generation_k=5`, `p-v0`, híbrido, `retrieval_k=10`)
- **Fecha:** 2026-10-01
- **Estado:** preparación realizada; clasificación pendiente de confirmar y experimentos sin ejecutar.
- **Commit:** consultar `git rev-parse --short HEAD` en la rama `sofi`.

## 3.1 Revisión de los casos 58, 128, 647 y 671

Fuentes utilizadas en el análisis inicial:

- `evaluation/generacion/e02_v0/errores.csv`
- `evaluation/generacion/e02_v0/trazas.jsonl`
- `evaluation/generacion/e02_v0/entrega.jsonl`
- `data/sample_50.jsonl`

Las observaciones siguientes proceden del análisis inicial y requieren confirmar los pasajes concretos. Encontrar el cuerpo normativo correcto en el top-5 no demuestra que el fragmento pertinente estuviera disponible para el decoder.

Clasificaciones del plan:

- **A:** evidencia pertinente presente; error de razonamiento del modelo.
- **B:** evidencia pertinente únicamente en posiciones 6–10.
- **C:** evidencia pertinente ausente del top-10.
- **D:** pregunta ambigua o defectuosa, con justificación documentada.

| ID | Esperada | Modelo | `rank_doc` reportado | Clasificación provisional | Observación inicial y verificación pendiente |
|---:|:---:|:---:|---:|---|---|
| 58 | A | B | 2 | Pendiente; posible A o D | Se reportan fragmentos del CGP en posiciones 2 y 5. La opción A menciona «Ley 1564 de 2002», mientras el análisis identifica el CGP como Ley 1564/2012. Verificar la pregunta original, sus opciones y si los pasajes resuelven la pregunta antes de atribuir el fallo al modelo o al banco. |
| 128 | D | B | 1 | Pendiente; posible A | Se reportan artículos del Decreto 663/1993 en posiciones 1–5. Falta identificar el pasaje que permite resolver las opciones, incluida la referencia a Fintech. La presencia del decreto por sí sola no demuestra evidencia suficiente. |
| 647 | B | D | 5 | Pendiente; posible A o C | Se reporta `codigo_civil#art_1842` en posición 5. Verificar si su contenido respalda la respuesta esperada. Que pertenezca al Código Civil no basta para considerarlo pertinente. |
| 671 | C | D | — | Pendiente | El análisis reporta `legal_basis = «Doctrina.»` y ausencia de referencia extraíble. Esto no demuestra que la pregunta sea defectuosa ni que la evidencia esté ausente. Revisar pregunta, opciones y pasajes recuperados. |

**Lectura provisional:** aún no hay casos A confirmados mediante pasajes concretos documentados. No corresponde concluir que el prompt sea la causa principal ni descartar problemas de recuperación.

El caso **671 permanece entre los 15 IDs del barrido**. La ausencia de una cita extraíble no justifica excluirlo de la exactitud de preguntas cerradas.

### Verificación pendiente

Para cada caso:

1. Identificar el pasaje que respalda la respuesta esperada.
2. Registrar su posición en el top-10, si está presente.
3. Comprobar si fue enviado al decoder con `k=5`.
4. Documentar por qué permite resolver la pregunta.
5. Asignar A/B/C/D solamente cuando haya evidencia suficiente.

`legal_basis` se utiliza exclusivamente para evaluación; no debe incorporarse al prompt ni a la lógica de ejecución.

## 3.2 Control y barrido de `generation_k`

### Control `k=5` frente a `e02_v0`

No se pudo regenerar `e04_k5` en este entorno por falta del índice y del decoder.

El análisis inicial reporta esta comparación:

```bash
python src/evaluacion/comparar_entregas.py \
  salidas/sample_e02_v0.jsonl \
  salidas/sample_e02_v0.jsonl