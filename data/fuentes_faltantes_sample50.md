# Fuentes del `legal_basis` (sample_50) que NO cubre `seed_targets.json`

Comparación de `data/sample_50.jsonl` (50 preguntas) contra los `canonico` de `data/seed_targets.json`.
Pendientes para agregar al corpus. `legal_basis` es ground truth de evaluación: sirve para planear qué ingerir, no se usa en runtime.

## Resumen

- 50 preguntas: 3 no tienen fuente normativa (24, 671, 857), 21 tienen al menos una fuente faltante, el resto queda cubierto por el seed.
- Faltantes: 5 normas, 4 sentencias de Corte Constitucional, 3 documentos de otras cortes/autoridades, 2 documentos no normativos.
- Hallazgo: el seed no incluye Código Civil, Código de Comercio, Código Penal ni CPACA (aparecen en 11 de las 50 preguntas). Tampoco la Ley 472 de 1998.

## A. Normas (códigos y leyes) — prioridad alta

| # | doc_id propuesto | Norma | Preguntas (id: artículo citado) | Dónde buscar |
|---|---|---|---|---|
| 1 | `codigo_civil` | Código Civil (Ley 57 de 1887) | 358: art. 946; 487: art. 1820; 490: art. 1796; 865: art. 113; 647: sin artículo | http://www.secretariasenado.gov.co/senado/basedoc/codigo_civil.html |
| 2 | `codigo_comercio` | Código de Comercio (Decreto 410 de 1971) | 239: arts. 1324, 1325, 822, 871 (y 16) | http://www.secretariasenado.gov.co/senado/basedoc/codigo_comercio.html |
| 3 | `codigo_penal` | Código Penal (Ley 599 de 2000) | 600: art. 241; 280: art. 64; 1065: art. 20 | http://www.secretariasenado.gov.co/senado/basedoc/ley_0599_2000.html |
| 4 | `cpaca` | CPACA (Ley 1437 de 2011) | 748: sin artículo; 1089: art. 246 | http://www.secretariasenado.gov.co/senado/basedoc/ley_1437_2011.html |
| 5 | `ley_472_1998` | Ley 472 de 1998 (acciones populares y de grupo) | 51: arts. 3 y 46; 247: sin artículo | http://www.secretariasenado.gov.co/senado/basedoc/ley_0472_1998.html |

Notas:
- En la 239 el "artículo 16" va sin código (podría ser Código Civil o Constitución); revisar el enunciado.
- Q748 y Q1089 dicen solo "CPACA"/"art. 246 del CPACA": basta con ingerir el código completo.

## B. Jurisprudencia — Corte Constitucional (no está en el seed)

| # | Sentencia | Pregunta | Dónde buscar | Observación |
|---|---|---|---|---|
| 6 | C-468 de 2024 | 453 | https://www.corteconstitucional.gov.co/relatoria/2024/C-468-24.htm | Citada junto a C-332/2025 (cubierta) y SU-016/2020 |
| 7 | SU-016 de 2020 | 453 | https://www.corteconstitucional.gov.co/relatoria/2020/SU016-20.htm | El seed tiene SU-11/2020, no esta |
| 8 | SU-277 de 2025 | 563 | https://www.corteconstitucional.gov.co/relatoria/2025/SU277-25.htm | El seed tiene otras SU de 2025 (111, 315, 425), no esta |
| 9 | T-256 (año no indicado) | 190 | Buscar en https://www.corteconstitucional.gov.co/relatoria/ | Ambigua: hay T-256 en varios años. Resolver con el enunciado/tema de la pregunta 190 antes de ingerir |

## C. Jurisprudencia — otras cortes

| # | Documento | Pregunta | Observación |
|---|---|---|---|
| 10 | Consejo de Estado, Sentencia de unificación 2020CE-SUJ-4-005 del 26-nov-2020, exp. 21329 | 142 | Sección Cuarta (tributario). Buscar en relatoria del Consejo de Estado / SUIN-Juriscol |
| 11 | Auto Supersociedades No. 2025-01-730337 | 272 | Complementa Ley 1116 de 2006 (cubierta). Buscar en supersociedades.gov.co |
| 12 | Sentencia CSJ Sala Civil del 18-jul-2017 (sin radicado) | 168 | Ambigua: el seed tiene SC-18392/2017 y SC-8453/2016, pero no se ha verificado que ninguna sea la del 18-jul-2017. Identificar el radicado |

## D. Documentos no normativos / externos

| # | Documento | Pregunta | Observación |
|---|---|---|---|
| 13 | WIPO, `wipo_ip_bog_12_ref_u14b_aleman.pdf` | 513 | https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf — ponencia, decidir si vale la pena |
| 14 | Caso francés Dow Chemical (laudo arbitral CCI, 1982) | 697 | Sin fuente oficial; probablemente doctrina de arbitraje internacional |

## E. Preguntas sin fuente normativa (nada que ingerir)

- 24: `legal_basis` = None
- 671: "Doctrina."
- 857: "Doctrina."

## F. Preguntas cubiertas por el seed (verificación)

| Pregunta | Fuente citada | Cubierta por |
|---|---|---|
| 51, 60, 218, 661, 1005, 1073 | Constitución | `constitucion` |
| 60, 528, 589, 879 | Código General del Proceso | `codigo_general_proceso` |
| 58 | "Ley 1564 de 2002 (El Estatuto del Consumidor)" | Error del `legal_basis` (Ley 1564 es el CGP, de 2012; el Estatuto del Consumidor es Ley 1480 de 2011). Ambas están en el seed |
| 674 | Estatuto del Consumidor, arts. 3, 23, 24 | `estatuto_consumidor` |
| 128 | Decreto Ley 663 de 1993 | `decreto 663/1993` |
| 290, 308 | Ley 1150 de 2007 | `ley 1150/2007` |
| 352 | Decreto 2067 de 1991 | `decreto 2067/1991` |
| 617, 442, 1073, 253 | Código Sustantivo del Trabajo | `codigo_sustantivo_trabajo` |
| 253 | SL3385-2022; Ley 1562 de 2012 | `SL-3385/2022`; `ley 1562/2012` |
| 272 | Ley 1116 de 2006 | `ley 1116/2006` |
| 679 | Ley 1581 de 2012 | `ley 1581/2012` |
| 79 | Ley 1010 de 2006 | `ley 1010/2006` |
| 140 | C-145 de 2018 | `C-145/2018` |
| 453 | C-332 de 2025 | `C-332/2025` |
| 472 | Ley 1340 de 2009 | `ley 1340/2009` |
| 919 | SU-455 de 2020 | `SU-455/2020` |
| 946 | C-039 de 2025 | `C-39/2025` |
| 960 | Decreto 2153/1992, art. 45 | `decreto 2153/1992` |
| 991, 661 | C-891 de 2012 (en 661 escrito "C-89112") | `C-891/2012` |
| 1015 | C-355 de 2006 | `C-355/2006` |

## Orden sugerido de ingesta

1. `codigo_civil`, `codigo_comercio`, `codigo_penal`, `cpaca` (códigos completos, de mayor peso: 11 preguntas de la muestra).
2. `ley_472_1998`.
3. Sentencias C-468/2024, SU-016/2020, SU-277/2025.
4. Resolver ambigüedades (T-256, sentencia Sala Civil 18-jul-2017) y luego ingerir.
5. Sentencia de unificación CE 2020CE-SUJ-4-005 y auto Supersociedades (opcionales).
6. Documentos no normativos (WIPO, Dow Chemical) solo si sobra tiempo.
