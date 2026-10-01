# Resultados del analisis de abstencion - e02_v0

Comando: `python src/evaluacion/analisis_abstencion.py --experimento e02_v0`

Fuentes comprobadas:
- `salidas/trazas/e02_v0.jsonl`: 50 trazas.
- `evaluation/generacion/e02_v0/errores.csv`: 50 filas.
- `evaluation/generacion/e02_v0/entrega.jsonl`: 50 respuestas.
- `data/sample_50.jsonl`: 50 IDs de referencia.
- Modo runtime y hash de config: `{'modo': 'off', 'config_sha256': 'd163a18ba87ab24f0430ef65b46db7b127c374b417e14439f4dfe52edf876232'}`.

## Regla oficial y limites de los datos

La etiqueta de acierto de este analisis replica `score_abstention` en `scripts/evaluate.py`: cerradas calificadas comparan la opcion; semiabiertas y abiertas comparan los cuerpos de citas extraibles en `answer_text` contra `legal_basis`. Las preguntas de texto libre sin citas extraibles se excluyen del denominador oficial. El ID 374 se excluye de exactitud cerrada mediante `FLAWED_IDS`; la logica oficial de abstencion solo lo trata como cerrado si pertenece a `closed_ids`.

`errores.csv.correcta` solo se informa para cerradas; sus vacios en texto libre no son aciertos ni errores. El reporte disponible no contiene puntuaciones RAGAS por ID (el `reporte.json` marca RAGAS pendiente), asi que `ragas_individual` queda como no disponible. `aciertos_cita`, `rank_doc`, `rank_art`, diagnostico y latencia se conservan tal como vienen de `errores.csv`; no sustituyen RAGAS.

La columna `estimacion_componente_abstencion_numerador` usa `0.5 * errores_capturados - 0.5 * aciertos_perdidos`: estima solo el cambio del numerador del componente de abstencion segun la regla oficial. No son puntos totales ni incluye cambios en exactitud, citacion o RAGAS. Los umbrales son candidatos exploratorios; no se selecciona ninguno.

Comprobacion contra el reporte oficial: 43 IDs evaluados, 34 aciertos y 9 errores; coincide con la clasificacion por ID.

## Estado por formato

| Formato | IDs | Evaluables | Aciertos | Errores | Excluidos por falta de cita | Faltan entrega/traza/errores.csv |
|---|---:|---:|---:|---:|---:|---:|
| `multiple_choice` | 15 | 15 | 11 | 4 | 0 | 0 |
| `semi_open` | 30 | 24 | 21 | 3 | 6 | 0 |
| `open_ended` | 5 | 4 | 2 | 2 | 1 | 0 |

IDs individuales, en el orden del banco:

- **multiple_choice** (15): 51=acierto, 58=error, 60=acierto, 128=error, 290=acierto, 308=acierto, 352=acierto, 358=acierto, 487=acierto, 528=acierto, 600=acierto, 617=acierto, 647=error, 671=error, 748=acierto
- **semi_open** (30): 24=excluido_sin_cita_extraible, 79=acierto, 140=acierto, 142=excluido_sin_cita_extraible, 168=excluido_sin_cita_extraible, 190=excluido_sin_cita_extraible, 218=acierto, 239=error, 280=acierto, 442=acierto, 453=acierto, 472=acierto, 490=acierto, 563=error, 589=acierto, 661=acierto, 674=error, 697=excluido_sin_cita_extraible, 857=excluido_sin_cita_extraible, 865=acierto, 879=acierto, 919=acierto, 946=acierto, 960=acierto, 991=acierto, 1005=acierto, 1015=acierto, 1065=acierto, 1073=acierto, 1089=acierto
- **open_ended** (5): 247=error, 253=acierto, 272=acierto, 513=excluido_sin_cita_extraible, 679=error

Excluidos del componente por `legal_basis` sin cita extraible: 24, 142, 168, 190, 513, 697, 857.
IDs `FLAWED_IDS` presentes en la muestra: ninguno.

Faltantes por fuente:
- entrega: ninguno.
- traza: ninguno.
- errores.csv: ninguno.
- RAGAS agregado en `reporte.json`: pendiente (correr con --ragas); no se dispone de veredictos individuales en las fuentes revisadas.

## Sensibilidad de cortes exploratorios

Aplicados solo a las preguntas evaluables por el componente oficial de abstencion del formato indicado. Las perturbaciones multiplican el umbral base por 0.8, 0.9, 1.1 y 1.2 (el signo de la desigualdad no cambia). IDs afectados son los que satisfacen el corte; las señales faltantes se reportan aparte y no se cuentan como afectados.

| Candidato | Variacion | Umbral | IDs afectados | Errores capturados | Aciertos perdidos | Señal faltante (IDs) |
|---|---:|---:|---|---:|---:|---|
| `semi_open: top1_rank_denso > 18.5` | -20% | 14.8 | 239, 674 | 2 | 0 | 1073 |
| `semi_open: top1_rank_denso > 18.5` | -10% | 16.65 | 239, 674 | 2 | 0 | 1073 |
| `semi_open: top1_rank_denso > 18.5` | base | 18.5 | 239, 674 | 2 | 0 | 1073 |
| `semi_open: top1_rank_denso > 18.5` | +10% | 20.35 | 239 | 1 | 0 | 1073 |
| `semi_open: top1_rank_denso > 18.5` | +20% | 22.2 | 239 | 1 | 0 | 1073 |
| `open_ended: frac_en_ambas_ramas < 0.74` | -20% | 0.592 | 247 | 1 | 0 | ninguno |
| `open_ended: frac_en_ambas_ramas < 0.74` | -10% | 0.666 | 247 | 1 | 0 | ninguno |
| `open_ended: frac_en_ambas_ramas < 0.74` | base | 0.74 | 247, 679 | 2 | 0 | ninguno |
| `open_ended: frac_en_ambas_ramas < 0.74` | +10% | 0.814 | 247, 679 | 2 | 0 | ninguno |
| `open_ended: frac_en_ambas_ramas < 0.74` | +20% | 0.888 | 247, 679 | 2 | 0 | ninguno |
| `open_ended: score_top1 < 0.03164` | -20% | 0.025312 | 247 | 1 | 0 | ninguno |
| `open_ended: score_top1 < 0.03164` | -10% | 0.028476 | 247 | 1 | 0 | ninguno |
| `open_ended: score_top1 < 0.03164` | base | 0.03164 | 247, 679 | 2 | 0 | ninguno |
| `open_ended: score_top1 < 0.03164` | +10% | 0.034804 | 247, 253, 272, 679 | 2 | 2 | ninguno |
| `open_ended: score_top1 < 0.03164` | +20% | 0.037968 | 247, 253, 272, 679 | 2 | 2 | ninguno |

### Solapamiento entre candidatos base

Interseccion de IDs afectados (cada candidato se evalua solo en su formato elegible; un ID de otro formato no pertenece a su conjunto):

| Candidatos | IDs compartidos |
|---|---|
| `semi_open: top1_rank_denso > 18.5` ∩ `open_ended: frac_en_ambas_ramas < 0.74` | ninguno |
| `semi_open: top1_rank_denso > 18.5` ∩ `open_ended: score_top1 < 0.03164` | ninguno |
| `open_ended: frac_en_ambas_ramas < 0.74` ∩ `open_ended: score_top1 < 0.03164` | 247, 679 |
| Los tres candidatos | ninguno |

Estos resultados son descriptivos sobre la misma muestra usada para proponer los cortes. No son validacion independiente ni justifican elegir una regla definitiva; las preguntas y escenarios no constituyen muestras independientes. La etiqueta de error en texto libre sigue siendo la coincidencia de citas del componente oficial, no un veredicto RAGAS individual, que no esta disponible.

## Simulacion offline de las reglas experimentales

Reaplicacion determinista a las senales ya guardadas. `sin reglas` usa las abstenciones de la entrega existente; las variantes usan la configuracion versionada, manteniendo sin reglas nuevas a `multiple_choice`. La metrica de la tabla es solo el componente oficial de abstencion; no estima puntos totales ni RAGAS.

| Escenario | Nuevas abstenciones (IDs por formato) | Errores capturados | Aciertos perdidos | Señales faltantes | Puntos componente abstencion | Cambio vs base |
|---|---|---:|---:|---|---:|---:|
| sin reglas (base observada) | ninguna | 0 | 0 | ninguna | 7.91 | +0.00 |
| reglas experimentales (base) | open_ended: 247, 679; semi_open: 239, 674 | 4 | 0 | 1073 | 8.37 | +0.46 |
| solo semi_open -20% | open_ended: 247, 679; semi_open: 239, 674 | 4 | 0 | 1073 | 8.37 | +0.46 |
| solo open_ended -20% | open_ended: 247; semi_open: 239, 674 | 3 | 0 | 1073 | 8.26 | +0.35 |
| ambos formatos -20% | open_ended: 247; semi_open: 239, 674 | 3 | 0 | 1073 | 8.26 | +0.35 |
| solo semi_open +20% | open_ended: 247, 679; semi_open: 239 | 3 | 0 | 1073 | 8.26 | +0.35 |
| solo open_ended +20% | open_ended: 247, 679; semi_open: 239, 674 | 4 | 0 | 1073 | 8.37 | +0.46 |
| ambos formatos +20% | open_ended: 247, 679; semi_open: 239 | 3 | 0 | 1073 | 8.26 | +0.35 |

En los extremos conjuntos ±20%, la estimacion del componente de abstencion sigue por encima de la base observada.
En la configuracion base se capturan 4 errores y se pierden 0 aciertos. La sensibilidad y el tamaño de la muestra no constituyen validacion independiente; aunque el componente aislado sea positivo, faltan veredictos RAGAS por ID para estimar el efecto total. Por ello este resultado no recomienda activar las reglas.

## Salidas y pendientes

- CSV por ID y formato: `evaluation/abstencion/e02_v0_senales.csv`.
- Medias, AUC (solo con al menos dos casos por clase), conteos por cuartil y curvas de candidatos: `evaluation/abstencion/e02_v0_umbral_candidatos.csv`.
- Configuracion experimental de Fase B: `config/abstencion.json`; multiple_choice no tiene reglas nuevas.
- RAGAS individual requeriria conservar/exportar el resultado por pregunta del juez; no se puede reconstruir del puntaje agregado.
- Fase B implementada con activacion opt-in; `SYNTAX_ABSTENCION=off` sigue siendo el default. No se valido como regla de produccion.
- No se modificaron prompts ni la generacion del decoder.
