# Fuentes pendientes del corpus

Lista de verificación de lo que falta por conseguir. Marcar `[x]` cuando el original esté en `data/raw/`, mapeado en `data/mapa_archivos.json` (si es PDF/RTF), parseado a `data_corpus/corpus/<doc_id>.txt` y registrado en `CORPUS.md`.

Estado a 2026-10-01: **213 documentos en el corpus** (167 + 46 de esta lista; ver "Resultado de la incorporación" al final). Estado a 2026-09-29: 167 documentos. Origen de la lista: `data/fuentes_descargadas.json` (semilla) y `data/fuentes_faltantes_sample50.md` (`legal_basis` de `sample_50`).

**Cómo incorporar cada uno** (ver `CLAUDE.md` y `CORPUS.md`, sección 3):

1. Guardar el original en `data/raw/pdf/` o `data/raw/rtf/`.
2. Agregar `"archivo": "doc_id"` en `data/mapa_archivos.json`.
3. Semilla: poner `url` y `fuente` en `data/fuentes_override.json` (clave = `doc_id`). Fuera de la semilla: agregarlo a `_adicionales`.
4. `python src/ingesta/descargar_fuentes.py --solo <doc_id>` y luego `python src/ingesta/parsear_pdf.py --solo <doc_id>` (o `parsear_rtf.py`).
5. `python src/ingesta/descargar_fuentes.py --corpus-md`.

---



## A. Sentencias de la Corte Suprema sin URL (15, de la semilla)

Se descargan a mano (la Relatoría no tiene URL predecible). Ítems = preguntas del banco que las citan.

### Sala Laboral (SL)

- [x] `sentencia_sl_648_2018` — SL-648 de 2018 (2 ítems, Derecho laboral) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sl_1050_2023` — SL-1050 de 2023 (1 ítem, Derecho laboral) [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sl_1730_2020` — SL-1730 de 2020 (1 ítem, Derecho laboral) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sl_1972_2025` — SL-1972 de 2025 (1 ítem, Derecho laboral) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)



### Sala Penal (SP)

- [x] `sentencia_sp_1680_2022` — SP-1680 de 2022 (2 ítems, Derecho penal) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sp_1945_2019` — SP-1945 de 2019 (2 ítems, Derecho penal) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sp_1167_2022` — SP-1167 de 2022 (1 ítem, Derecho penal) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sp_3218_2021` — SP-3218 de 2021 (1 ítem, Derecho penal) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)



### Sala Civil (SC)

- [x] `sentencia_sc_1121_2018` — SC-1121 de 2018 (1 ítem, Derecho civil) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) (word)
- [x] `sentencia_sc_18392_2017` — SC-18392 de 2017 (1 ítem, Comercial y sociedades) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sc_3674_2021` — SC-3674 de 2021 (1 ítem, Comercial y sociedades) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sc_425_2024` — SC-425 de 2024 (1 ítem, Comercial y sociedades); también se incorporó la SC-435 de 2024 (`sentencia_sc_435_2024`) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sc_8453_2016` — SC-8453 de 2016 (1 ítem, Comercial y sociedades) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_sc_3085_2024` — SC-3085 de 2024 (1 ítem, Derecho de familia) - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)



### Otro tipo

- [x] `acuerdo_2_2015` — Acuerdo 02 de 2015 (1 ítem, Derecho constitucional). Falta identificar qué entidad lo expidió; el script no tiene regla para `acuerdo`. - [https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=154021](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=154021)

---



## B. No encontrados en la fuente oficial (6, de la semilla)

La URL que construyó el script no existe. Probar otra fuente o confirmar si la referencia del banco es una errata.

- [x] `decreto_46_2024` — Decreto 46 de 2024 (1 ítem, Comercial y sociedades). No está en el Senado; probar Gestor Normativo o SUIN-Juriscol. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=228530](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=228530)
- [x] `ley_1692_2013` — Ley 1692 de 2013 (1 ítem, Tributario). No está en el Senado; - [https://www.dian.gov.co/normatividad/convenios/ConveniosTributacionInternacional/B149.pdf](https://www.dian.gov.co/normatividad/convenios/ConveniosTributacionInternacional/B149.pdf)
- [x] `ley_23_1991` — Ley 23 de 1991 (1 ítem, Constitucional). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6546](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6546)
- [x] `sentencia_su_488_2011` — SU-488 de 2011 (1 ítem, Administrativo). Probar `SU-488-11.htm` u otro formato de URL en la Relatoría. - [https://www.corteconstitucional.gov.co/relatoria/2011/T-488-11.htm](https://www.corteconstitucional.gov.co/relatoria/2011/T-488-11.htm) (rtf)
- [x] `sentencia_t_248_2025` — T-248 de 2025 (1 ítem, Penal). Probar otro formato de URL en la Relatoría. es SP-248 de 2025 de la Corte suprema - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml)
- [x] `sentencia_su_6_1991` — SU-6 de 1991 (1 ítem, Administrativo). La Corte no emitió SU en 1991; probablemente errata. Decidir: identificar la sentencia real o descartar. Respaldo escogido: sentencia t-06 de 1992 [https://www.corteconstitucional.gov.co/relatoria/1992/t-006-92.htm](https://www.corteconstitucional.gov.co/relatoria/1992/t-006-92.htm) (rtf)

---



## C. Fuentes del `legal_basis` de `sample_50` fuera de la semilla

Servidas por `data/fuentes_faltantes_sample50.md`. Los ítems A.1 a A.5 de ese documento (Código Civil, Código de Comercio, Código Penal, CPACA y Ley 472 de 1998) **ya están incorporados**.

### Corte Constitucional

- [x] `sentencia_c_468_2024` — C-468 de 2024 (pregunta 453). - [https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=172537](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=172537) 
- [x] `sentencia_su_16_2020` — SU-016 de 2020 (pregunta 453). [https://www.corteconstitucional.gov.co/relatoria/2020/su016-20.htm](https://www.corteconstitucional.gov.co/relatoria/2020/su016-20.htm) (rtf)
- [x] `sentencia_su_277_2025` — SU-277 de 2025 (pregunta 563). [https://www.corteconstitucional.gov.co/relatoria/2025/su277-25.htm](https://www.corteconstitucional.gov.co/relatoria/2025/su277-25.htm)  (rtf)
- [x] T-256 de 2025 (pregunta 190). [https://www.corteconstitucional.gov.co/relatoria/2025/t-256-25.htm](https://www.corteconstitucional.gov.co/relatoria/2025/t-256-25.htm)  (rtf)



### Otras cortes y autoridades

- [x] Consejo de Estado, sentencia de unificación 2020CE-SUJ-4-005 del 26-nov-2020, exp. 21329 (pregunta 142, tributario). Buscar en la relatoría del Consejo de Estado o en SUIN-Juriscol. [https://normograma.dian.gov.co/dian/compilacion/docs/pdf/25000-23-37-000-2013-00443-01(21329)ce-suj-4-005.pdf](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/25000-23-37-000-2013-00443-01(21329)ce-suj-4-005.pdf)
- [x] Auto de Supersociedades No. 2025-01-730337 (pregunta 272). Complementa la Ley 1116 de 2006. Buscar en supersociedades.gov.co. - [https://servicios.supersociedades.gov.co/barandaVirtual/#!/app/radicaciones#verpdf](https://servicios.supersociedades.gov.co/barandaVirtual/#!/app/radicaciones#verpdf)
- [x] Sentencia de la Sala Civil de la CSJ del 18-jul-2017, SC10291-2017(pregunta 168). - [https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) 



### No normativos (decidir si valen la pena)

- [x] WIPO, `wipo_ip_bog_12_ref_u14b_aleman.pdf` (pregunta 513). [https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf](https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf). Es una ponencia, no una norma: decidir si se incluye. incluido, link no cambia
- [x] Caso Dow Chemical (laudo CCI, 1982) (pregunta 697). Sin fuente oficial, probablemente doctrina de arbitraje internacional: decidir si se incluye. doctrina arbanza [https://arbanza.com/analisis-comparativo-de-la-extension-del-convenio-arbitral-a-partes-no-signatarias-el-caso-de-pakistan-francia-y-colombia/](https://arbanza.com/analisis-comparativo-de-la-extension-del-convenio-arbitral-a-partes-no-signatarias-el-caso-de-pakistan-francia-y-colombia/) y sentencia corte [https://www.cortesuprema.gov.co/corte/wp-content/uploads/not/civil21/prov/11001-02-03-000-2021-00766-00.pdf](https://www.cortesuprema.gov.co/corte/wp-content/uploads/not/civil21/prov/11001-02-03-000-2021-00766-00.pdf)

---



## D. Ampliación propuesta desde `scripts/citations.py` (cobertura del test)

Origen: cruce de los cuerpos que reconocen `CODES`, `_ALIAS_NUM` y `NORM_TYPES` contra el corpus (2026-10-01). La semilla ya cubre las citas del banco; esto es una apuesta de cobertura para preguntas del test (992) que la semilla no vio, **no** una corrección de errores medidos. Los `doc_id` son propuestos (estables una vez indexados). Ingerir en el orden de prioridad.

### D.1 Prioridad alta (códigos que `citations.py` reconoce y no están en el corpus)

- [x] `codigo_procedimiento_penal` (antes propuesto `ley_906_2004`) — Ley 906 de 2004, Código de Procedimiento Penal (alias `codigo_procedimiento_penal`, `cpp`). Hoy solo está `ley_600_2000` (procedimiento penal anterior). Derecho penal. Senado. [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=14787](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=14787)
- [x] `codigo_procesal_trabajo` (antes propuesto `decreto_2158_1948`) — Decreto-ley 2158 de 1948, Código Procesal del Trabajo y de la Seguridad Social (alias `codigo_procesal_trabajo`, `cpts`). Complemento procesal del CST (37 ítems). Derecho laboral. Compilación Avance Jurídico (Senado). Revisar que `citations.py` y la cabecera (`cabeceras.py`) usen el cuerpo `codigo_procesal_trabajo`. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5259](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5259)



### D.2 Decretos únicos reglamentarios (`NORM_TYPES["decreto"]`; archivos grandes, segmentar por artículo)

- [x] `decreto_1072_2015` — DUR del Sector Trabajo (laboral). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173)
- [x] `decreto_1625_2016` — DUR en materia tributaria (acompaña al ET). [https://normograma.dian.gov.co/dian/compilacion/docs/pdf/decreto_1625_2016.pdf](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/decreto_1625_2016.pdf)
- [x] `decreto_1074_2015` — DUR del Sector Comercio, Industria y Turismo (comercial y mercados). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608)
- [x] `decreto_1083_2015` — DUR del Sector de Función Pública (administrativo). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=62866](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=62866)



### D.3 Actos legislativos (`NORM_TYPES["acto_legislativo"]`; ninguno en el corpus, textos cortos)

- [x] `acto_legislativo_1_2003` — reforma política. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=8620](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=8620)
- [x] `acto_legislativo_2_2015` — equilibrio de poderes. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=66596](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=66596)
- [x] `acto_legislativo_1_2005` — pensiones. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=17236](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=17236) (corregida: antes repetía la URL del Acto Legislativo 02 de 2015)

Verificar primero que el extractor de `citations.py` y el `doc_id`/cabecera (`cabeceras.py`) soporten el cuerpo `acto_legislativo`.

### D.4 Sentencias de salas no representadas (`_SENT_RE`: `stc|stl|ac|au`)

- [ ] Decidir si entran tutelas de la Corte Suprema (`STC`, `STL`) y autos de unificación (`AU`); hoy solo hay SL y Corte Constitucional. Sin candidatos concretos: salen de las preguntas del test (sábado) o de `items_del_banco`.



### D.5 Resoluciones y circulares (`NORM_TYPES["resolucion"|"circular"]`; decidir granularidad antes de ingerir)

- [ ] Circular Básica Jurídica de la SIC (consumidor y competencia).
- [ ] Circular Básica Jurídica de la Superintendencia Financiera.
- [ ] Resoluciones DIAN de alto uso (identificar cuáles).



### D.6 Códigos que `citations.py` no reconoce con alias propio (hoy se leen como `("ley", número, año, …)`; si se ingieren, agregarlos a `CODES`/`_ALIAS_NUM`)

- [x] `ley_100_1993` — sistema de seguridad social (laboral). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5248](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5248)
- [x] `ley_222_1995` — sociedades (comercial). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6739](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6739)
- [x] `ley_1676_2013` — garantías mobiliarias (comercial). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=54297](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=54297)
- [x] `decreto_19_2012` — antitrámites. - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=45322](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=45322)
- [x] `decreto_1_1984` — CCA anterior al CPACA (transición, administrativo). - [https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6543](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6543)

Sin evidencia en el banco de que aparezcan; baja prioridad hasta tener las preguntas del test.

---



## Orden de ataque sugerido

1. Sección C, Corte Constitucional: C-468/2024, SU-016/2020, SU-277/2025 (faltan en `sample_50`, URL directa).
2. D.1: Ley 906/2004 y Decreto-ley 2158/1948.
3. D.2: Decretos 1072/2015 y 1625/2016.
4. A: SL-648/2018, SP-1680/2022, SP-1945/2019 (2 ítems cada una).
5. D.3: actos legislativos.
6. Resto.



## Sin acción (referencia)

- **Erratas de la semilla ya cubiertas** (no hay nada que descargar): `ley_11500_2007` y `ley_1150_2005` → `ley_1150_2007`; `ley_116_2006` → `ley_1116_2006`.
- **Preguntas sin fuente normativa**: 24 (`legal_basis` vacío), 671 y 857 (solo «Doctrina»).



## Conteo

| Bloque | Pendientes (2026-09-29) | Pendientes hoy |
|---|---:|---:|
| A. Corte Suprema y acuerdo sin URL | 15 | 0 |
| B. No encontrados | 6 | 0 |
| C. Fuera de la semilla (sample_50) | 9 | 0 |
| D. Ampliación propuesta desde `citations.py` | 18 | 4 (D.4 y D.5: decisiones abiertas, sin candidatos) |
| **Total** | **48** | **4** |

## Resultado de la incorporación (2026-10-01)

Los 46 documentos nuevos están en `data/raw/`, mapeados en `mapa_archivos.json`, registrados en `fuentes_override.json` (semilla) o en `_adicionales` (fuera de la semilla), parseados, segmentados y en `corpus_manifest.json` y `CORPUS.md`. `doc_id` definitivos y casos especiales:

| Ítem de la lista | `doc_id` | Nota |
|---|---|---|
| SL-648/2018, SP-1945/2019 | `sentencia_sl_648_2018`, `sentencia_sp_1945_2019` | PDF escaneado: OCR con Tesseract (`parsear_pdf.OCR_FORZADO`) |
| SC-10291/2017, SC-18392/2017, SC-8453/2016 | `sentencia_sc_10291_2017`, `sentencia_sc_18392_2017`, `sentencia_sc_8453_2016` | capa OCR del PDF ilegible: OCR con Tesseract |
| SC-1121/2018 | `sentencia_sc_1121_2018` | DOCX movido de `data/raw/word/` a `data/raw/rtf/` (los parsers detectan el formato por contenido) |
| Sentencias CSJ (A) | `sentencia_<sala>_<n>_<año>` | URL = consulta de la Relatoría (no hay URL por documento); el archivo original queda en la `nota` |
| `ley_1692_2013` | `ley_1692_2013` | errata de la semilla (`ley_1692_2017`) |
| `ley_23_1991` | `ley_23_1991` | errata de la semilla (`ley_23_1961`) |
| `sentencia_su_488_2011` | `sentencia_t_488_2011` | errata de la semilla |
| `sentencia_t_248_2025` | `sentencia_sp_248_2025` | errata de la semilla: es de la Sala Penal de la CSJ |
| `sentencia_su_6_1991` | `sentencia_t_6_1992` | errata de la semilla; respaldo elegido a mano |
| SU-016/2020 | `sentencia_su_16_2020` | desde el RTF de la relatoría (el PDF de Sisjur se descartó) |
| CE 2020CE-SUJ-4-005 | `sentencia_ce_suj_4_005_2020` | tipo `documento`: `citations` no extrae una cita del Consejo de Estado |
| Auto Supersociedades | `auto_supersociedades_2025_01_730337` | tipo `documento`; la Baranda Virtual no da URL directa |
| SC10291-2017 (pregunta 168) | `sentencia_sc_10291_2017` | |
| WIPO | `doctrina_ompi_agotamiento_patentes_2012` | tipo `documento`; extracción sin ordenar (diapositivas en capas) |
| Dow Chemical | `doctrina_arbanza_grupo_sociedades_2024` + `sentencia_sc_5288_2021` | Arbanza = tipo `documento` |
| Decreto 046/2024, Acuerdo 02/2015, actos legislativos, Decreto 01/1984 | `decreto_46_2024`, `acuerdo_2_2015`, `acto_legislativo_*`, `decreto_1_1984` | la cabecera nombra ambas formas del número ("Decreto 046 de 2024 (Decreto 46 de 2024)") para respaldar la cita escrita de cualquiera de las dos |

Las áreas de los 25 documentos nuevos fuera de la semilla son provisionales: ver `data/areas_por_asignar.md`.
