# Fuentes pendientes del corpus

Lista de verificación de lo que falta por conseguir. Marcar `[x]` cuando el original esté en `data/raw/`, mapeado en `data/registros/mapa_archivos.json` (si es PDF/RTF), parseado a `data_corpus/corpus/<doc_id>.txt` y registrado en `CORPUS.md`.

Estado a 2026-10-01: **213 documentos en el corpus** (167 + 46 de esta lista; ver "Resultado de la incorporación" al final). Estado a 2026-09-29: 167 documentos. Origen de la lista: `data/registros/fuentes_descargadas.json` (semilla) y `data/fuentes_faltantes_sample50.md` (`legal_basis` de `sample_50`).

**Cómo incorporar cada uno** (ver `CLAUDE.md` y `CORPUS.md`, sección 3):

1. Guardar el original en `data/raw/pdf/` o `data/raw/rtf/`.
2. Agregar `"archivo": "doc_id"` en `data/registros/mapa_archivos.json`.
3. Semilla: poner `url` y `fuente` en `data/registros/fuentes_override.json` (clave = `doc_id`). Fuera de la semilla: agregarlo a `_adicionales`.
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

Salen de la comparación del `legal_basis` de `sample_50` contra la semilla (antes `data/fuentes_faltantes_sample50.md`, ya eliminado; está en el historial de git). Los ítems A.1 a A.5 de esa comparación (Código Civil, Código de Comercio, Código Penal, CPACA y Ley 472 de 1998) **ya están incorporados**.

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

Las áreas de los 25 documentos nuevos fuera de la semilla son provisionales: ver `docs/ingesta/areas_por_asignar.md`.

## Ampliación v3 (2026-10-02)

Plan: `docs/INDEXACION.md` sección 13. Todo va en `_adicionales` de `fuentes_override.json` con la nota "ampliacion v3"; **las áreas las propuso un agente y falta que una persona las confirme** (las SU del lote van todas como `Derecho constitucional`).

- **Normas (95)**, por área: tutela (Decreto 2591/1991), Ley 270/1996, 393/1997, 1751/2015, 134/1994, 1757/2015, 5/1992, 1712/2014, DUR 1069/2015, 1475/2011, 996/2005; administrativo (489/1998, 909/2004, 1474/2011, 610/2000, 2080/2021, 1882/2018, 2195/2022, 1508/2012, 136/1994, 617/2000, 1551/2012); penal (1257/2008, 1761/2015, 1826/2017, 65/1993, 1709/2014, 1453/2011, 2197/2022, 975/2005, 1957/2019, 1922/2018, 1774/2016, 1273/2009, 2081/2021, 2098/2021); procesal (2213/2022, 1285/2009, 446/1998, 1395/2010); civil (1996/2019, 675/2001, 1579/2012, 791/2002, 258/1996, 1561/2012, 1306/2009); familia (1060/2006, 294/1996, 2126/2021, 2447/2025, 1878/2018, 2089/2021, 1/1976, 25/1992, 2097/2021, 1361/2009); laboral (2381/2024, 789/2002, 361/1997, 2101/2021, 797/2003, 776/2002, Decreto 1295/1994, 1822/2017, 1221/2008, 2088/2021, 2121/2021, 2191/2022, 2365/2024, 1496/2011, 1846/2017); comercial (2069/2020, 1901/2018, 1314/2009, 43/1990, 590/2000, 1429/2010, 1735/2014); tributario (2277/2022, 2010/2019, 2155/2021, 1066/2006, Decreto 1333/1986, 14/1983, 1430/2010, 44/1990, 788/2002); mercados (1266/2008, 1328/2009, 23/1982, 2300/2023, 44/1993, 1915/2018, 1341/2009).
- **Decisión Andina 351/1993** (derecho de autor): PDF de la CAN; tipo `documento` en `cabeceras.DOCUMENTOS` porque `citations.py` no reconoce "Decisión 351".
- **Hitos (37)**: T-406/92, T-002/92, C-543/92, C-221/94, SU-039/97, T-153/98, C-836/01, C-1064/01, T-881/02, C-551/03, T-025/04, C-590/05, C-1040/05, C-370/06, C-075/07, C-029/09, C-141/10, C-577/11, C-634/11, C-539/11, T-129/11, C-579/13, T-388/13, C-313/14, SU-617/14, C-071/15, T-762/15, SU-049/17, C-005/17, C-674/17, C-080/18, SU-123/18, SU-075/18, C-481/19, C-294/21, SU-087/22 y C-264/2026 (control de la reforma pensional, Ley 2381/2024).
- **Lote SU 2020–2026 (242 nuevas)**: se sondeó `relatoria/<año>/SU<nnn>-<aa>.htm` para nnn = 1..620 (la página genérica de la relatoría no carga `encabezado.js`). Se encontraron 258 (34, 41, 43, 40, 47, 37 y 16 por año); las otras 16 ya estaban. La SU-163/2023 fue anulada (Auto 823/2024) y la relatoría solo publica la nota de nulidad.

Fuentes: el Senado tardaba ~20 s por página y cortaba conexiones en paralelo, así que 68 normas se bajaron de los espejos de Avance Jurídico (CRA, Colpensiones y DIAN, que se agregó a `ESPEJOS_AJ`) y 27 del Senado. Parseo: nueva regla en `parsear_html.py` que corta el oficio de remisión de la Corte ("Corte Constitucional" / "Secretaría General") pegado tras las leyes estatutarias (Ley 1712/2014 traía la C-274/13 entera: 720k → 36k caracteres); no cambia ningún `.txt` de v2.

## Ampliación v4 (2026-10-02): áreas delgadas, de forma automática

Motivo: la demanda del banco es de ~99 preguntas por área, pero mercados (25 documentos), procesal (28), tributario (31) y civil (35) tenían pocos documentos frente a constitucional (340). Desde `e15` el retriever prioriza los documentos del área de la pregunta (`docs/INDEXACION.md` 15), así que las normas nuevas de esas áreas pueden recuperarse sin nombrarlas sin diluir las demás. **Regla del equipo: nada se busca a mano.** Lo que no se resuelve con reglas automáticas se descarta y queda en la lista de abajo.

Procedimiento (scripts auxiliares en el directorio temporal de la sesión, no versionados; el criterio queda aquí):

1. **Normas**: para cada candidato `tipo_N_AAAA` se prueba `<tipo>_<NNNN>_<AAAA>.htm` en los espejos de Avance Jurídico (`ESPEJOS_AJ`: CRA, Colpensiones, Cancillería, DIAN) y luego en el Senado. Se acepta solo si la página dice "<tipo> <N> de <AAAA>" en el encabezado y trae artículos. Entradas en `_adicionales` con la nota "ampliacion v4" y luego `descargar_fuentes.py --solo` (bajas también las partes `_prNNN`).
2. **Decisiones Andinas** 345/1993, 391/1996 y 608/2005: PDF de la CAN con el mismo patrón que la 486 (`DocOf/DEC<N>.pdf`). Tipo `documento` en `cabeceras.DOCUMENTOS` (no puntúan en citación: `citations.py` no reconoce "Decisión N").
3. **Sentencias C- de control**: las notas de vigencia de la compilación no traen el número de la sentencia (las cajas las llena JavaScript), así que se toman las C- **co-citadas** en el mismo párrafo con cada ley de v3/v4 dentro de las sentencias del corpus (≥ 3 menciones, hasta 3 por ley, tope 40, sin las que ya estaban) y se bajan de `relatoria/<año>/C-<nnn>-<aa>.htm` (el descargador valida `encabezado.js`). Entran al registro `solo_por_cita.json` (solo se recuperan si la pregunta las nombra).
4. Parseo, `generar_manifest.py`, `segmentar.py`, `generar_manifest.py`, `solo_por_cita.py`, `construir_indice.py`.

Entraron **65 documentos** (corpus de 653 documentos y 124.302 fragmentos; los 113.519 fragmentos de v3 no cambian):

- **Mercados (10)**: Decretos 1377/2013, 886/2014 y 735/2013; Leyes 178/1994, 463/1998, 565/2000, 1032/2006, 1403/2010, 1648/2013 y 1978/2019; Decisiones Andinas 345, 391 y 608.
- **Tributario (10)**: Leyes 1943/2018, 1739/2014, 1111/2006, 863/2003, 633/2000, 223/1995, 383/1997, 49/1990, 1004/2005 y 1609/2013.
- **Procesal (6)**: Ley 794/2003, Decretos 306/1992, 333/2021 y 1818/1998, Leyes 1123/2007 y 2094/2021.
- **Civil (8)**: Decreto 1260/1970, Leyes 1183/2008, 2044/2020, 9/1989, 388/1997, 57/1887, 95/1890 y 45/1936.
- **C- de control (28)**: C-030/23 y C-146/21 (Ley 2094/2021), C-037/96 y C-328/15 (Ley 270/1996), C-490/11 (Ley 1475/2011), C-1011/08 (Ley 1266/2008), C-180/94 y C-150/15 (Ley 134/1994), C-1153/05 (Ley 996/2005), C-300/12 (Ley 1508/2012), C-1024/04, C-1094/03 y C-1035/08 (Ley 797/2003), C-531/00, C-458/15 y C-824/11 (Ley 361/1997), C-319/06, C-575/06 y C-694/15 (Ley 975/2005), C-044/15 (Ley 5/1992), C-821/05 y C-660/00 (Ley 25/1992), C-348/04 y C-540/01 (Ley 617/2000), C-467/16 (Ley 1774/2016), C-957/99 (Ley 489/1998), C-886/10 (Ley 294/1996), C-251/96 (Ley 9/1989).

**No resueltos (descartados, sin búsqueda manual)**:

- Decreto 920/2023 (régimen sancionatorio aduanero): la página del Senado existe pero el encabezado no valida como "Decreto 920 de 2023".
- Decreto 1400/1970 (CPC): no está en el Senado ni en los espejos.
- Decreto 1165/2019 (régimen de aduanas): resuelto, pero descartado por tamaño (la primera página sola pesa 1,9 MB, ~800 artículos).
- C- de las Leyes 1957/2019, 2213/2022 y 2277/2022 (prioritarias en el plan): ninguna co-citada con esas leyes en el corpus (≥ 3 menciones).

Parseo: 10 sentencias C- salían truncadas en Windows (lxml/libxml2, `docs/INDEXACION.md` 8.2: completitud 15–60 %). `parsear_html.py` ahora reintenta con `html.parser` (stdlib) **solo** cuando la completitud baja de 0,85 y se queda con el texto más completo (0,975–0,984 en las 10; `parser_html` en `parseo.json`). Ningún `.txt` previo cambia. `data_corpus/parseo.json` de esta máquina venía del zip (solo `.txt`), así que las 588 entradas previas se reconstruyeron desde el manifest, verificando el sha256 de cada `.txt` (0 diferencias).

Áreas: las de las normas son las del plan; las de las C- son constitucional + las de la ley controlada. Propuestas de revisión para v3 y v4 en `docs/ingesta/areas_propuestas_v3.csv` (léxico por área; columna `aprobado` para la revisión humana).

**Lote T 2025–2026 (Fase 4, 533 sentencias)**: sondeo de `relatoria/<año>/T-<nnn>-<aa>.htm` (válida si carga `/relatoria/encabezado.js`; se para tras 80 números seguidos sin sentencia): 352 de 2025 y 181 de 2026 (hasta la T-304/26), más las 9 que ya estaban por la semilla. El HTML se guardó directo en `data/raw/html/sentencia_t_<n>_<año>/` (238 MB) y `descargar_fuentes.py --solo` solo lo registró. Todas van como `Derecho constitucional` (área por defecto, propuesta de revisión en `areas_propuestas_v3.csv`) y **solo se recuperan si la pregunta las nombra** (`solo_por_cita.json`). Medición en `docs/INDEXACION.md` 16.

