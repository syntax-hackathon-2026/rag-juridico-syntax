# Plan de mejoras para las cerradas (sábado 2026-10-03)

Plan de trabajo para la noche del viernes y la mañana del sábado. Nada de esto está implementado; cada propuesta va detrás de un flag `SYNTAX_MC_*` apagado hasta medirla.

## Contexto

Las cerradas valen 20 pts y en el test son **289 ítems puntuados**. Cada acierto suma ≈ 0,069 pts en exactitud y ≈ 0,011 pts en abstención (≈ 880 ítems), así que **+10 cerradas ≈ +0,8 pts**. En `sample_50` vamos 12/15 (`e24_final`). Presupuesto: **5–10 s por cerrada en total**.

### Lo que ya se probó (no repetir)

| Intento | Resultado |
|---|---|
| p-v1 «conocimiento propio, analizar cada opción» (`e09`) | 10/15: arregla #647, rompe #308 y #528 |
| Thinking 768 / 1536 (`e10`, `e10b`) | 10 y 9/15; 10–15 s/cerrada (fuera de presupuesto) |
| generation_k = 10 (`e11`) | mismas letras |
| p-v2: reglas de decisión y opciones meta (`e23`) | mismas letras |
| Una consulta por opción, fusionada en el RRF | doc_hit@10 0,902 → 0,878 |
| Planificador agéntico | el 8B inventa artículos; doc_hit@10 ≈ 0,81 |
| Glosario nombre ↔ número (`e22`, KEEP) | arregla #58: 12/15 |

En 12 corridas, #128, #647 y #671 fallan casi siempre igual; votar entre las variantes medidas no pasa de 12/15. La recuperación de las cerradas está saturada en la muestra (doc_hit@10 = 1,0): lo que queda es **decisión** y **doctrina fuera del corpus**.

### Hallazgos

1. **Con 15 ítems no se decide nada** (1 pregunta = 6,7 pp).
2. **Latencia medida de una cerrada en `e24`: ~4 s**. El prefill (~2.500 tokens) tarda solo **~0,2 s**; la escritura (~300 tokens a ~90 tok/s) se lleva **~3,4 s**. Consecuencia: **una llamada de 1 token cuesta ~0,25 s**. Leer probabilidades de letras es casi gratis; escribir texto es caro.
3. **No se usan logprobs**: no sabemos qué tan seguro está el modelo de cada letra.
4. **Un solo prompt mezcla decidir y redactar con citas restringidas**: «no cites lo que no está en los pasajes» empuja a elegir la opción que aparece en ellos (#58; #671 cae en «Todas las anteriores»).
5. **`descarte_opciones` no puntúa** (las citas que cuentan salen de `justificacion`, y las cabeceras de evidencia se agregan solas). Es casi la mitad de los tokens que se escriben: recortarlo libera ~1,5 s para la decisión.
6. **Riesgo latente**: en cerradas, `responder.py` se abstiene si las citas no se reparan, y la regeneración puede cambiar la letra. Abstenerse en una cerrada solo compensa con P(acierto) < ~7 %, o sea nunca. No ocurrió en la muestra, pero con 289 puede ocurrir.

---

## Propuestas (dentro de 5–10 s por cerrada)

Todas son deterministas, así que la verificación en vivo sigue funcionando.

### P1. Logprobs de la letra (base de todo lo demás; ~0 s)

- `llm.py`: `logprobs: true, top_logprobs: 5` en `/v1/chat/completions`. Para llamadas de una letra, `/completion` con `n_probs` y la gramática del enum.
- **Verificar** que con la gramática JSON activa el token de la letra trae probabilidades útiles.
- Guardar P(A..D) y el margen en la traza; tabular confianza contra acierto.

### P2. Separar decidir de redactar (≈ igual que hoy)

- **Llamada 1 «decidir»**: análisis breve por opción (V/F + ≤ 15 palabras) y luego la letra, sin la restricción de citas: «los pasajes son evidencia, no la lista cerrada de lo verdadero». ~120 tokens ≈ 1,4 s.
- **Llamada 2 «redactar»** con la letra fija (enum de una sola letra): `justificacion` con las reglas actuales y `descarte_opciones` corto (una frase de ≤ 12 palabras por opción). ~180 tokens ≈ 2 s.
- Total ≈ 3,5–4 s, similar a hoy, y la decisión ya no compite con las citas.

### P3. Puntuación de letras con 1 token + votantes baratos (~0,25 s cada uno)

Con P1 resuelto, cada votante es una llamada de un token:
- **Rotación de opciones** (PriDe): 2–4 órdenes cíclicos reetiquetados; la probabilidad vuelve a su opción original y se suma. Corrige el sesgo de posición del 8B. Las preguntas con opciones meta que se refieren por letra no se rotan.
- **Closed-book** (sin pasajes, ~0,05 s de prefill): conocimiento paramétrico. Fue el único que acertó #671 (`e05`) y ayuda en doctrina que no está en el corpus.
- **Verificación por opción** «¿la opción X es correcta? Sí/No» con P(Sí): 4 llamadas ≈ 1 s. Las opciones meta («Todas», «Ninguna», «(a) y (b)», detectadas por regex) se puntúan por regla: Todas = mín(P), Ninguna = mín(1−P), combinación = mín de las abarcadas. Ataca #671 y #647.
- Combinar con suma de log-probabilidades y pesos simples, sin ajuste fino. La letra ganadora pasa a la llamada «redactar» (P2).
- Costo total de P3: ~1,5–2,5 s. **Con P2, cabe en ~6–7 s por cerrada.**

### P4. Cascada acotada (opcional, solo si P1 la justifica)

- Si el margen del ensamble es bajo (p. ej. < 0,2), una llamada «decidir» extra con otro orden de pasajes o con evidencia por opción (P5).
- Thinking queda **fuera**: a ~90 tok/s, incluso 256 tokens son +3 s. Solo se podría si afecta a menos del ~15 % de las cerradas y el promedio queda ≤ 10 s.

### P5. Evidencia por opción solo para el decoder (~0,1–0,3 s de recuperación)

- El top-10 puntuado no cambia. Para «decidir», agregar el mejor fragmento de `retrieve(pregunta + opción)` de cada opción al final de `pasajes_recuperados` (posición 11 en adelante: no cuenta para el respaldo y queda visible para la verificación en vivo; el schema no limita la lista).
- Unos 4 fragmentos más ≈ +0,1 s de prefill. Ataca #647 (C.C. art. 176 en el corpus pero fuera del top-10).
- Medir antes con `retrieval_eval`: ¿el artículo correcto aparece en el top-2 de la opción correcta?

### P6. Guardas (sin costo; KEEP directo si la muestra sale idéntica)

- Cerradas: **no abstenerse nunca**. Con citas irreparables, se quitan las oraciones y queda «Fuentes consultadas…». Con salida inválida, una llamada de solo letra.
- **Fijar la letra** en la regeneración por citas (enum de una sola letra).

### P7. Calculadoras deterministas (0 s)

- Cuantías del CGP art. 25 con la tabla de SMLMV por año, días hábiles y porcentajes. Se detectan por regex y se inyecta una línea `[cálculo: …]`.
- Solo si `analizar_test.py` muestra ≥ 5 cerradas numéricas en las 289 el sábado a las 09:00.

### P8. Calibración por lote sin etiquetas (0 s)

- Con las P(letra) de las 289 (solo campos de runtime), estimar el sesgo medio por letra y corregirlo. Vector congelado en config para que la verificación en vivo regenere igual.
- Solo si P1 muestra un sesgo claro de letra.

### P9. Orden de pasajes y "sándwich" (~0 s)

- Pasaje de mayor score al final, junto a la pregunta, y repetir la pregunta y las opciones después de los pasajes.

### P10. A/B de decoder ≤ 8B (solo si sobra tiempo)

- `qwen3-4b-2507` ya está en `config.LLM_MODELOS` y escribe más rápido (cabe mejor en el presupuesto). Un decoder distinto por formato puede chocar con el enunciado: preguntar a la organización.

### Descartado

Thinking general (latencia), reranker para cerradas (recuperación saturada en la muestra), few-shot con ítems del banco y datos sintéticos.

---

## Orden de ejecución

**Viernes en la noche (rama `santiago-mejoras-mc`):**
1. P6 guardas: las 15 cerradas deben salir idénticas.
2. P1 logprobs: tabla de confianza en las 15.
3. P2 → P3 (rotación + closed-book + verificación por opción) → P5, midiendo cada uno solo (método de `CLAUDE.md`: cambiar una cosa).

**Sábado 09:00–10:45:**
4. Con `analizar_test.py`, contar en las 289 las opciones meta, las numéricas y las doctrinales; activar solo lo que aplique (P7, P8).
5. KEEP si no pierde ninguna de las 12 cerradas que hoy acierta y la latencia media de las cerradas es ≤ 10 s.
6. Congelar flags y `PROMPT_VERSION`, registrar en `experiments.csv` y verificar determinismo entre máquinas con los flags nuevos.

## Archivos

- `src/generacion/llm.py`: logprobs y llamadas de 1 token.
- `src/generacion/responder.py`: guardas, ruta de cerradas con decidir/votar/redactar y letra fija.
- `src/generacion/prompts.py`: prompts y schemas nuevos; subir `PROMPT_VERSION`.
- Nuevo `src/generacion/cerradas.py`: opciones meta, rotaciones, agregación y calculadoras.
- `src/config.py`: flags `SYNTAX_MC_*`.

## Verificación

- `python src/main.py --split sample --ids 51 58 60 128 290 308 352 358 487 528 600 617 647 671 748 --experimento eXX` + `evaluar_entrega.py`: sin regresión.
- Latencia media por cerrada (objetivo ≤ 10 s, idealmente ~6–7 s).
- `comparar_entregas.py`: determinismo entre dos corridas y entre M1 y M2; `validar_entrega.py` con los pasajes 11 en adelante.
