# Plan 06: parser de referencias legales y metadata como candidato suave

Parte de [`00_resumen.md`](00_resumen.md). Comparte `Retriever.retrieve` con el plan 05.

## 1. Objetivo y métrica

Cuando la pregunta nombra una norma y/o un artículo («artículo 29 de la Constitución», «art. 42 del CGP», «Ley 1564 de 2012»), traer ese fragmento directamente al conjunto de candidatos, sin depender de que BM25 o bge-m3 lo encuentren.

- **Métrica principal:** `art_hit@10` y `respaldo@10` en las preguntas que mencionan norma o artículo (subconjunto).
- **Control:** que no baje `doc_hit@10`/`mrr` en el resto (el lookup no debe desplazar aciertos).
- **Impacto esperado:** acotado, porque solo ayuda a las preguntas con referencia explícita. Medirlo antes de invertir (Fase 0).

## 2. Evidencia

`CLAUDE.md` plantea un «parser de referencias legales (determinista)» con lookup por metadata en la arquitectura objetivo. `abstencion.senales` ya calcula `normas_en_pregunta` con las funciones de `scripts/citations.py`, así que la extracción en la consulta existe. Falta usarla para recuperar.

## 3. Diseño

### 3.1 Fase 0: medir cuántas preguntas se benefician

Script sobre `sample_50` (solo lectura): para cada pregunta, `extract(pregunta + opciones)` y contar cuántas dan (a) un cuerpo (norma) y (b) un cuerpo + artículo. Cruzar con `art_hit@10` actual para ver cuántas de ellas hoy **fallan**. Si son pocas (< 3), el plan se reduce a una prueba de concepto.

### 3.2 Fase 1: extracción reutilizando el parser oficial

- Usar `citations.extract(texto)` (`scripts/citations.py:115`), `bodies()` y `article_level()`. **No reescribir** el diccionario `CODES` ni las regex (regla de CLAUDE.md).
- Envolverlo en `src/recuperacion/referencias.py` (nuevo) con una función `referencias_de(consulta) -> list[Ref]`, donde `Ref = (cuerpo, numero, anio, articulo)`.
- `src/generacion/citas.py:25` ya tiene `cuerpos()`; ver si se puede compartir en lugar de duplicar.

### 3.3 Fase 2: índice `(canonico, articulo) → chunks`

- Construir una sola vez en `Retriever.__init__` a partir de `meta["canonico"]` y `meta["articulo"]` (ya presentes en `meta`).
- Normalizar el artículo igual que `_art()` de `retrieval_eval.py:56` (hay valores como `'1o'`, `'38A'`, `'12-1'`).
- Las normas partidas (`#p1..#pN`) devuelven **todas** las partes del artículo; las modificatorias pueden tener artículos transcritos con el mismo número: usar `canonico` del `doc_id` propio, no del texto citado dentro (trampa documentada en `docs/INDEXACION.md`).
- Considerar `meta["vigencia"]`: si hay un fragmento `derogado` o `inexequible`, mantenerlo pero no darle prioridad sobre el vigente cuando haya ambos.

### 3.4 Fase 3: integración como candidato, nunca filtro duro

Dentro de `Retriever.retrieve` (`retriever.py:94`, fusión en ≈109), tres variantes, una por experimento:

- (a) **Candidato extra al RRF:** los chunks del lookup entran como una tercera «rama» con rank fijo bajo (p. ej. 1..n), fusionados por RRF.
- (b) **Boost suave:** se les suma un bonus fijo al score RRF.
- (c) **Inserción garantizada:** se insertan en el top-`m` (p. ej. posiciones 1–2) si la referencia es de nivel artículo.

No se implementa filtro duro por área o por norma: el corpus no tiene campo `area` y un error de extracción haría desaparecer la respuesta correcta.

Si la pregunta nombra solo la norma (sin artículo), no hay lookup por artículo; se puede usar como boost suave a los chunks de ese `doc_id`.

### 3.5 Metadata como señal secundaria (opcional)

Idea ligada al «filtro por metadata»: `tipo` (`constitucion|codigo|ley|decreto|decision|sentencia`) y `anio` sí están en el chunk. Posible boost suave si la pregunta nombra una sentencia («Sentencia C-355 de 2006») o un año. Solo si la Fase 0 muestra casos concretos; se descarta si el beneficio es marginal.

## 4. Archivos

| Archivo | Cambio |
|---|---|
| `src/recuperacion/referencias.py` | Nuevo: `referencias_de`, normalización |
| `src/recuperacion/retriever.py` | Índice en `__init__` y lookup en `retrieve` |
| `src/config.py` | `SYNTAX_LOOKUP=off|on`, variante e hiperparámetros |
| `tests/test_referencias.py` | Nuevo (pytest) |
| `requirements.txt` | `pytest==<version>` si aún no está (plan 04 puede haberlo añadido) |
| `src/evaluacion/retrieval_eval.py` | Reporte del subconjunto con referencia explícita |
| `docs/INDEXACION.md` | Sección con resultados |

## 5. Cómo activarlo y revertirlo

`SYNTAX_LOOKUP=off|on`, por defecto `off`. Con `off` el resultado debe ser bit a bit idéntico al actual. Registrar la variante en las filas de `experiments.csv` y en `.meta.json`.

## 6. Pruebas

### 6.1 Unitarias (pytest)

- Extracción: «artículo 29 de la Constitución» → `(constitucion, None, None, "29")`; «art. 42 del CGP» → `codigo_general_proceso`; «Ley 1564 de 2012, artículos 13, 15 y 42» → lista de tres referencias; «Sentencia C-355 de 2006» → referencia de jurisprudencia sin artículo.
- Cuerpos canónicos: los de `extract` coinciden con `meta["canonico"]` para una muestra de chunks reales.
- Índice: `'1o'`, `'38A'`, `'12-1'` se resuelven; un artículo inexistente devuelve lista vacía, sin error.
- Consulta sin referencias → el retriever devuelve exactamente lo mismo que con `SYNTAX_LOOKUP=off`.
- Determinismo y desempate por `chunk_id`.

Las pruebas de índice usan un `chunks.jsonl` pequeño de fixture, no el índice completo, para correr en segundos.

### 6.2 A/B de calidad

```bash
python src/evaluacion/retrieval_eval.py --modo hibrido --experimento e06_sin_lookup
SYNTAX_LOOKUP=on python src/evaluacion/retrieval_eval.py --modo hibrido --experimento e06_lookup_a
```

Comparar por pregunta (`evaluation/retrieval/<exp>_hibrido.jsonl`): qué preguntas mejoran, cuáles se desplazan. Reportar el subconjunto con referencia explícita por separado del total.

## 7. Criterio keep/revert

- **Keep** si `art_hit@10` sube en al menos 2 preguntas con referencia explícita **y** ningún acierto previo sale del top-10.
- **Revert** si desplaza aciertos o si el beneficio es nulo (la Fase 0 ya habrá avisado).
- Elegir la variante más simple que cumpla: (a) antes que (c).

## 8. Riesgos y trampas

- Extracción errónea (p. ej. «artículo 5» de otra norma citada de pasada en una opción): por eso es candidato extra y no filtro.
- Mencionar la norma en las **opciones** de una cerrada no significa que sea la respuesta: la consulta incluye pregunta + opciones. Probar extraer solo de la pregunta frente a pregunta + opciones.
- Normas con erratas en la semilla (`ley_1563_2012`, `decreto_2737_1989`, `ley_964_2005`): el cuerpo canónico lo manda el `doc_id`, no el texto de la pregunta.
- Artículos modificados: el texto vigente y el original pueden coexistir; revisar `vigencia`.
- Nunca usar `legal_basis` ni los `id` en la lógica (ground truth).
- Ahorro de latencia: es una consulta a un diccionario, no añade coste apreciable.

## 9. Dependencias

- Independiente del plan 03. Comparte `retrieve` con el plan 05: orden acordado lookup → RRF → reranker → recorte.
- Ya hay `abstencion.senales()` que usa `normas_en_pregunta`; si se mejora la extracción, mejora esa señal sin cambios extra (relación con el plan 04).

## 10. Tareas

- [ ] Fase 0: contar preguntas con referencia explícita y cuántas fallan hoy.
- [ ] `referencias.py` reutilizando `citations.extract`.
- [ ] Índice `(canonico, articulo)` en `Retriever.__init__` y normalización.
- [ ] Pruebas unitarias con fixture pequeña.
- [ ] Integración variante (a), flag `SYNTAX_LOOKUP`.
- [ ] A/B de (a), (b) y (c); elección.
- [ ] Reporte del subconjunto en `retrieval_eval.py` y documentación.
