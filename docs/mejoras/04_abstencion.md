# Plan 04: abstención por señales

Parte de [`00_resumen.md`](00_resumen.md). Usa las trazas del plan 03 y, si se adopta, se recalibra tras los planes 05 y 06.

## 1. Objetivo y métrica

Convertir respuestas que probablemente fallarían en abstenciones, que valen 0,5 sin importar el resultado (componente de abstención, 10 pts).

- **Regla de puntuación** (`scripts/evaluate.py`): acertar = 1, abstenerse = 0,5, errar = 0. Abstenerse conviene solo si P(acierto) < ~0,5.
- **Cerradas:** abstenerse da 0 en exactitud (20 pts). Por eso la regla es **distinta por formato**.
- **Métrica principal:** puntos netos = exactitud + abstención + RAGAS, con la regla activada frente a desactivada.
- **Control:** número de abstenciones por formato y precisión de la regla (de las que se abstuvo, cuántas habrían fallado).

## 2. Evidencia

`docs/RESULTADOS_e02_v0.md`: nunca nos abstuvimos; 34 respuestas buenas y 9 malas de las 43 en la parte de abstención. Cada mala que se convierta en abstención gana 0,5 pts de numerador; cada buena que se pierda cuesta 0,5.

Hoy `abstencion.decidir(motivos)` (`src/generacion/abstencion.py:46`) solo mira motivos técnicos (`sin_pasajes`, `salida_invalida`, `citas_irreparables`). `senales(consulta, top, perm)` (`abstencion.py:25`) ya calcula y registra en la traza, **sin decidir nada**:

`n_pasajes, score_top1, margen_top1_top2, top1_rank_bm25, top1_rank_denso, frac_en_ambas_ramas, n_cuerpos_top10, n_sentencias_top10, normas_en_pregunta, normas_pregunta_en_evidencia`.

Enganche: `responder.py:151` (`abstencion.decidir(motivos)`).

## 3. Diseño

### 3.1 Fase A: análisis offline (sin tocar la generación)

Script `src/evaluacion/analisis_abstencion.py` (nuevo, solo lectura):

1. Une `salidas/trazas/<exp>.jsonl` (señales) con `evaluation/generacion/<exp>/errores.csv` (acierto por pregunta).
2. Por formato, tabla de cada señal frente a acierto (media de la señal en aciertos vs errores; AUC simple si hay suficientes datos; histograma por cuartiles).
3. Para cada señal candidata, curva «si me abstengo por debajo del umbral u: cuántas malas capturo, cuántas buenas pierdo, puntos netos».
4. Salida: `evaluation/abstencion/<exp>_senales.csv` y un resumen en consola.

Esta fase **no cambia umbrales**; solo dice qué señales separan algo. Si ninguna separa, el plan termina aquí (revertir = no hacer nada).

### 3.2 Fase B: regla simple y configurable

Módulo `src/generacion/abstencion.py` (extender) con una función pura:

```python
def decidir_por_senales(senales: dict, formato: str, config: ReglaAbstencion) -> tuple[bool, list[str]]
```

- Devuelve la decisión y los motivos (`senal_baja:score_top1`, etc.), que se suman a `motivos` y quedan en la traza.
- `ReglaAbstencion` es un dataclass con umbrales por formato, cargado desde un JSON versionado (`config/abstencion.json` o constantes en `config.py`; seguir la convención de `config.py` como único lugar de rutas).
- **Política por formato (decidida):**
  - `multiple_choice`: umbral muy conservador (solo evidencia prácticamente nula, p. ej. la norma citada en la pregunta no aparece en ningún pasaje y el acuerdo BM25/denso es nulo). Abstenerse cuesta exactitud, así que debe ser raro.
  - `semi_open` y `open_ended`: umbral más holgado. Aquí las abstenciones no se juzgan en RAGAS, y una respuesta floja pesa sobre un promedio de 0,43.
- Combinar a lo sumo 2–3 señales con operadores simples (AND/OR). Nada de modelos entrenados con 50 muestras.
- `SYNTAX_ABSTENCION=off|reglas` (por defecto `off`). Con `off` el comportamiento es idéntico a hoy.

### 3.3 Fase C: validación

- Medir sobre `sample_50` y, si es posible, sobre un hold-out: las trazas de los barridos del plan 03 y de otras corridas sirven como datos adicionales (mismas preguntas, distintas condiciones: advertir que no son independientes).
- Reportar sensibilidad: puntos netos al mover el umbral ±10–20 %. Si un umbral solo funciona en un valor exacto, es sobreajuste.

## 4. Archivos

| Archivo | Cambio |
|---|---|
| `src/evaluacion/analisis_abstencion.py` | Nuevo (fase A) |
| `src/generacion/abstencion.py` | `decidir_por_senales` + dataclass de reglas |
| `src/generacion/responder.py` | ~línea 151: pasar `senales` y `formato` y sumar motivos |
| `src/config.py` | `SYNTAX_ABSTENCION`, ruta de la config de umbrales |
| `tests/test_abstencion.py` | Nuevo (pytest) |
| `requirements.txt` | `pytest==<version>` (ver `verificar_deps.py`) |
| `evaluation/abstencion/` | Salidas del análisis |

## 5. Cómo activarlo y revertirlo

`SYNTAX_ABSTENCION=reglas` activa; sin definir (o `off`) queda como hoy. Las trazas guardan los motivos, y el `.meta.json` debe registrar el valor de la bandera y el hash del archivo de umbrales.

## 6. Pruebas

### 6.1 Unitarias (pytest)

- Dadas señales sintéticas, la decisión es la esperada para cada formato.
- Cerradas **no** se abstienen con señales moderadamente débiles que sí abstienen en semi-abiertas.
- Determinismo: mismas señales → misma decisión y mismos motivos en el mismo orden.
- Señales faltantes o `None` (p. ej. `top1_rank_bm25=None`) no lanzan excepción y no provocan abstención por sí mismas.
- Con `SYNTAX_ABSTENCION=off`, `decidir` devuelve exactamente lo que devuelve hoy.

Para añadir `pytest`: `pip install pytest` en `.venv`, `python src/reproducibilidad/verificar_deps.py --fix`, y commitear el import y la línea de `requirements.txt` juntos (regla de CLAUDE.md).

### 6.2 A/B de calidad

Re-ejecutar `evaluar_entrega.py` sobre las mismas respuestas con la regla activada (no hace falta volver a generar: se puede reaplicar la regla a las trazas guardadas, que contienen las señales) y comparar puntos netos. Luego una corrida real con la regla para confirmar que la integración no altera otra cosa (`comparar_entregas.py` sobre las preguntas que no abstienen).

## 7. Criterio keep/revert

- **Keep** si los puntos netos suben ≥ 0,3 pts (unas 6 abstenciones útiles netas sobre 50 equivalen a ~0,6 pts de abstención) **y** la exactitud de cerradas no baja, **y** la mejora es estable a ±20 % del umbral.
- **Revert** si ninguna señal separa aciertos de errores o si la regla solo ayuda con un umbral exacto.
- No ajustar umbrales finos a 50 muestras (CLAUDE.md).

## 8. Riesgos y trampas

- Sobreajuste con pocas muestras: preferir reglas con sentido jurídico («la norma nombrada en la pregunta no aparece en los pasajes») a umbrales numéricos opacos.
- Abstenerse en una cerrada es 0 en exactitud: no hacerlo salvo evidencia casi nula.
- El comportamiento de la abstención debe ser **determinista**: nada de muestreo.
- Una abstención exige `pasajes_recuperados` coherentes; `postproceso.vacios(formato)` ya produce los campos vacíos válidos. Comprobar con el schema.
- `legal_basis` y las respuestas correctas son solo para el análisis offline; la regla en runtime usa únicamente señales de la recuperación.
- Cuidado con la expectativa: abstenerse en todo no es competitivo.

## 9. Dependencias

- Recomendado después del plan 03 (más trazas). Si el plan 05 o 06 se adopta, **recalibrar**: cambian los scores y los ranks.
- Comparte `responder.py` con el plan 03 (solo si se toca el prompt) y no toca `retriever.py`.

## 10. Tareas

- [ ] Instalar y fijar `pytest` (ver arriba).
- [ ] Fase A: `analisis_abstencion.py` y tabla de señales por formato.
- [ ] Decidir con el equipo qué señales entran (máximo 3) a partir de la tabla.
- [ ] Fase B: `decidir_por_senales`, dataclass y config; `SYNTAX_ABSTENCION`.
- [ ] Pruebas unitarias.
- [ ] Fase C: A/B reaplicando la regla a las trazas; análisis de sensibilidad.
- [ ] Corrida real con la regla y registro en `experiments.csv`; actualizar `docs/GENERACION.md` sección de abstención.
