# Áreas por asignar en `corpus_manifest.json`

Los 183 documentos de la semilla traen sus `areas` de `data/seed_targets.json` (áreas de las preguntas del banco que los citan). Los 30 documentos de abajo **no están en la semilla** (5 del 2026-09-29 y 25 incorporados el 2026-10-01) (`items_del_banco = 0`; sección `_adicionales` de `data/fuentes_override.json`): sus áreas las propuso un agente, a partir del `area` de la pregunta de `sample_50` que los cita o de la sección de `fuentes_pendientes.md` y hay que confirmarlas.

Mientras tanto, `corpus_manifest.json` los lleva con la propuesta actual (el validador exige `areas` no vacía).

La columna "Áreas en sample_50" es solo evidencia para decidir: el `area` de las preguntas de `data/sample_50.jsonl` cuyo `legal_basis` cita el documento (ground truth de evaluación; no se usa en runtime).

| doc_id | Norma | Áreas propuestas (actuales) | Áreas en sample_50 (preguntas) | Área asignada |
|---|---|---|---|---|
| `codigo_civil` | Código Civil (Ley 57 de 1887) | Derecho civil, Derecho de familia | Derecho civil (358); Derecho de familia (487, 490, 865, 647) | |
| `codigo_comercio` | Código de Comercio (Decreto 410 de 1971) | Derecho comercial y sociedades | Derecho comercial y sociedades (239) | |
| `codigo_penal` | Código Penal (Ley 599 de 2000) | Derecho penal | Derecho penal (600, 280, 1065) | |
| `cpaca` | CPACA (Ley 1437 de 2011) | Derecho administrativo, Derecho procesal | Derecho administrativo (748); Derecho procesal (1089) | |
| `ley_472_1998` | Ley 472 de 1998 (acciones populares y de grupo) | Derecho constitucional, Derecho administrativo | Derecho constitucional (51); Derecho administrativo (247) | |
| `sentencia_c_468_2024` | Sentencia C-468 de 2024 | Derecho constitucional | Derecho constitucional (453) | |
| `sentencia_su_16_2020` | Sentencia SU-016 de 2020 | Derecho constitucional | Derecho constitucional (453) | |
| `sentencia_su_277_2025` | Sentencia SU-277 de 2025 | Derecho administrativo | Derecho administrativo (563) | |
| `sentencia_t_256_2025` | Sentencia T-256 de 2025 | Derecho constitucional | Derecho constitucional (190) | |
| `sentencia_ce_suj_4_005_2020` | Consejo de Estado, Seccion Cuarta, Sentencia de unificacion 2020CE-SUJ-4-005 de 2020 (exp. 21329) | Derecho tributario | Derecho tributario (142) | |
| `auto_supersociedades_2025_01_730337` | Auto 2025-01-730337 de la Superintendencia de Sociedades | Derecho comercial y sociedades | Derecho comercial y sociedades (272) | |
| `sentencia_sc_10291_2017` | Sentencia SC-10291 de 2017 | Derecho civil | Derecho civil (168) | |
| `sentencia_sc_435_2024` | Sentencia SC-435 de 2024 | Derecho comercial y sociedades | — (ampliación, sin pregunta en sample_50) | |
| `sentencia_sc_5288_2021` | Sentencia SC-5288 de 2021 | Derecho comercial y sociedades | Derecho comercial y sociedades (697) | |
| `doctrina_arbanza_grupo_sociedades_2024` | Arbanza, Analisis comparativo de la extension del convenio arbitral a partes no signatarias: Pakistan, Francia y Colombia (2024) | Derecho comercial y sociedades | Derecho comercial y sociedades (697) | |
| `doctrina_ompi_agotamiento_patentes_2012` | OMPI, Seminario Regional (Bogota, 2012), Tema 14: El agotamiento del derecho de patente | Derecho de los mercados | Derecho de los mercados (513) | |
| `codigo_procedimiento_penal` | Codigo de Procedimiento Penal (Ley 906 de 2004) | Derecho penal, Derecho procesal | — (ampliación, sin pregunta en sample_50) | |
| `codigo_procesal_trabajo` | Codigo Procesal del Trabajo y de la Seguridad Social (Decreto 2158 de 1948) | Derecho laboral, Derecho procesal | — (ampliación, sin pregunta en sample_50) | |
| `decreto_1072_2015` | Decreto 1072 de 2015 (Decreto Unico Reglamentario del Sector Trabajo) | Derecho laboral | — (ampliación, sin pregunta en sample_50) | |
| `decreto_1625_2016` | Decreto 1625 de 2016 (Decreto Unico Reglamentario en materia tributaria) | Derecho tributario | — (ampliación, sin pregunta en sample_50) | |
| `decreto_1074_2015` | Decreto 1074 de 2015 (Decreto Unico Reglamentario del Sector Comercio, Industria y Turismo) | Derecho comercial y sociedades, Derecho de los mercados | — (ampliación, sin pregunta en sample_50) | |
| `decreto_1083_2015` | Decreto 1083 de 2015 (Decreto Unico Reglamentario del Sector de Funcion Publica) | Derecho administrativo | — (ampliación, sin pregunta en sample_50) | |
| `acto_legislativo_1_2003` | Acto Legislativo 01 de 2003 (reforma politica) | Derecho constitucional | — (ampliación, sin pregunta en sample_50) | |
| `acto_legislativo_2_2015` | Acto Legislativo 02 de 2015 (equilibrio de poderes) | Derecho constitucional | — (ampliación, sin pregunta en sample_50) | |
| `acto_legislativo_1_2005` | Acto Legislativo 01 de 2005 (adiciona el articulo 48 de la Constitucion, pensiones) | Derecho constitucional, Derecho laboral | — (ampliación, sin pregunta en sample_50) | |
| `ley_100_1993` | Ley 100 de 1993 (Sistema de Seguridad Social Integral) | Derecho laboral | — (ampliación, sin pregunta en sample_50) | |
| `ley_222_1995` | Ley 222 de 1995 (regimen de sociedades) | Derecho comercial y sociedades | — (ampliación, sin pregunta en sample_50) | |
| `ley_1676_2013` | Ley 1676 de 2013 (garantias mobiliarias) | Derecho comercial y sociedades, Derecho civil | — (ampliación, sin pregunta en sample_50) | |
| `decreto_19_2012` | Decreto 19 de 2012 (antitramites) | Derecho administrativo | — (ampliación, sin pregunta en sample_50) | |
| `decreto_1_1984` | Decreto 01 de 1984 (Codigo Contencioso Administrativo anterior al CPACA) | Derecho administrativo, Derecho procesal | — (ampliación, sin pregunta en sample_50) | |

Nombres válidos (exactos, como en el banco): `Derecho constitucional`, `Derecho administrativo`, `Derecho penal`, `Derecho procesal`, `Derecho comercial y sociedades`, `Derecho civil`, `Derecho de familia`, `Derecho tributario`, `Derecho laboral`, `Derecho de los mercados [competencia, consumidor, datos personales y propiedad intelectual]`.

**Cómo aplicar la decisión.** Llenar "Área asignada" y actualizar `areas` del documento en dos sitios: `_adicionales` de `data/fuentes_override.json` (para que `descargar_fuentes.py` lo conserve) y `corpus_manifest.json`. Luego `python src/validaciones/manifest.py`.
