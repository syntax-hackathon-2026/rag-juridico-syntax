# Bitácora del corpus — &lt;Nombre del equipo&gt;

> Plantilla basada en `Hackathon 2026/Ejemplo de entrega/CORPUS.md`. Completar cada
> sección a medida que se construye el corpus. Quitar todas las notas en cursiva
> (como esta) antes de la entrega final.

---

## 1. Inventario

*Una fila por documento fuente incorporado al corpus. `doc_id` debe coincidir con
el usado en `corpus_manifest.json` y con la metadata de los fragmentos del
índice. "Fecha de consulta" es la fecha de descarga, para trazabilidad si la
fuente cambia. "Áreas" son las áreas del banco de preguntas (enunciado, sección
4.2) a las que aporta el documento.*

<!-- inventario:inicio (generado por src/ingesta/descargar_fuentes.py --corpus-md) -->

| doc_id | Título | Fuente | URL | Fecha de consulta | Artículos | Fragmentos | Áreas |
|---|---|---|---|---|---:|---:|---|
| `constitucion_politica_1991` | Constitucion Politica de Colombia de 1991 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/constitucion_politica_1991.html) | 2026-09-29 | — | — | Administrativo, Comercial y sociedades, Constitucional, Familia, Laboral, Mercados, Penal, Procesal, Tributario |
| `codigo_general_proceso` | Codigo General del Proceso (Ley 1564 de 2012) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1564_2012.html) | 2026-09-29 | — | — | Civil, Comercial y sociedades, Familia, Mercados, Penal, Procesal, Tributario |
| `codigo_sustantivo_trabajo` | Codigo Sustantivo del Trabajo | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/codigo_sustantivo_trabajo.html) | 2026-09-29 | — | — | Laboral |
| `estatuto_tributario` | Estatuto Tributario (Decreto 624 de 1989) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/estatuto_tributario.html) | 2026-09-29 | — | — | Civil, Constitucional, Tributario |
| `decision_andina_486` | Decision 486 de 2000 de la Comunidad Andina, Regimen Comun sobre Propiedad Industrial | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC486.pdf) | 2026-09-28 | — | — | Comercial y sociedades, Mercados |
| `estatuto_consumidor` | Estatuto del Consumidor (Ley 1480 de 2011) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1480_2011.html) | 2026-09-29 | — | — | Civil, Mercados |
| `ley_80_1993` | Ley 80 de 1993 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0080_1993.html) | 2026-09-29 | — | — | Administrativo, Laboral |
| `ley_2220_2022` | Ley 2220 de 2022 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2220_2022.html) | 2026-09-29 | — | — | Civil, Procesal |
| `decreto_2153_1992` | Decreto 2153 de 1992 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2153_1992.html) | 2026-09-29 | — | — | Mercados |
| `ley_1116_2006` | Ley 1116 de 2006 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1116_2006.html) | 2026-09-29 | — | — | Comercial y sociedades, Procesal |
| `sentencia_c_355_2006` | Sentencia C-355 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/C-355-06.htm) | 2026-09-29 | — | — | Constitucional, Penal |
| `ley_1581_2012` | Ley 1581 de 2012 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html) | 2026-09-29 | — | — | Administrativo, Constitucional, Mercados |
| `codigo_infancia` | Codigo de la Infancia y la Adolescencia (Ley 1098 de 2006) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1098_2006.html) | 2026-09-29 | — | — | Familia |
| `ley_1258_2008` | Ley 1258 de 2008 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1258_2008.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `sentencia_c_207_2019` | Sentencia C-207 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/C-207-19.htm) | 2026-09-29 | — | — | Administrativo |
| `sentencia_sl_3385_2022` | Sentencia SL-3385 de 2022 | Relatoria de la Corte Suprema de Justicia | [enlace](https://www.corteconstitucional.gov.co/relatoria/?q=Sentencia%20SL-3385%20de%202022) | 2026-09-29 | — | — | Laboral |
| `sentencia_t_323_2024` | Sentencia T-323 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-323-24.htm) | 2026-09-29 | — | — | Constitucional |
| `ley_1010_2006` | Ley 1010 de 2006 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1010_2006.html) | 2026-09-29 | — | — | Laboral |
| `ley_1150_2007` | Ley 1150 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1150_2007.html) | 2026-09-29 | — | — | Administrativo |
| `ley_1340_2009` | Ley 1340 de 2009 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1340_2009.html) | 2026-09-29 | — | — | Mercados |
| `ley_153_1887` | Ley 153 de 1887 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0153_1887.htm) | 2026-09-29 | — | — | Civil, Tributario |
| `ley_2437_2024` | Ley 2437 de 2024 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2437_2024.html) | 2026-09-29 | — | — | Civil, Procesal |
| `ley_54_1990` | Ley 54 de 1990 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0054_1990.htm) | 2026-09-29 | — | — | Familia |
| `ley_979_2005` | Ley 979 de 2005 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0979_2005.html) | 2026-09-29 | — | — | Familia |
| `sentencia_c_394_2017` | Sentencia C-394 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-394-17.htm) | 2026-09-28 | — | — | Constitucional, Familia |
| `sentencia_c_55_2022` | Sentencia C-55 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/C-055-22.htm) | 2026-09-28 | — | — | Constitucional, Penal |
| `sentencia_su_315_2025` | Sentencia SU-315 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU315-25.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_t_243_2018` | Sentencia T-243 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/T-243-18.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_t_760_2008` | Sentencia T-760 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/T-760-08.htm) | 2026-09-28 | — | — | Administrativo, Constitucional |
| `ley_1095_2006` | Ley 1095 de 2006 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1095_2006.html) | 2026-09-29 | — | — | Constitucional, Penal |
| `ley_1563_2012` | Ley 1563 de 2012 (Estatuto de Arbitraje Nacional e Internacional) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1563_2012.html) | 2026-09-29 | — | — | Procesal |
| `ley_2141_2021` | Ley 2141 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2141_2021.html) | 2026-09-29 | — | — | Constitucional, Laboral |
| `ley_2452_2025` | Ley 2452 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2452_2025.html) | 2026-09-29 | — | — | Laboral |
| `ley_2466_2025` | Ley 2466 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2466_2025.html) | 2026-09-29 | — | — | Laboral |
| `ley_256_1996` | Ley 256 de 1996 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0256_1996.html) | 2026-09-29 | — | — | Mercados |
| `ley_50_1990` | Ley 50 de 1990 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0050_1990.htm) | 2026-09-29 | — | — | Laboral |
| `sentencia_c_117_2018` | Sentencia C-117 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-117-18.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_127_2011` | Sentencia C-127 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-127-11.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_134_2019` | Sentencia C-134 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/C-134-19.htm) | 2026-09-28 | — | — | Constitucional, Familia |
| `sentencia_c_15_2018` | Sentencia C-15 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-015-18.htm) | 2026-09-28 | — | — | Constitucional, Penal |
| `sentencia_c_164_2022` | Sentencia C-164 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/C-164-22.htm) | 2026-09-28 | — | — | Constitucional, Penal |
| `sentencia_c_259_2015` | Sentencia C-259 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-259-15.htm) | 2026-09-28 | — | — | Administrativo, Procesal |
| `sentencia_c_35_2009` | Sentencia C-35 de 2009 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2009/C-035-09.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_431_2001` | Sentencia C-431 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-431-01.htm) | 2026-09-28 | — | — | Constitucional, Penal |
| `sentencia_c_500_2024` | Sentencia C-500 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/C-500-24.htm) | 2026-09-28 | — | — | Procesal, Tributario |
| `sentencia_c_507_2004` | Sentencia C-507 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-507-04.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_540_2023` | Sentencia C-540 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-540-23.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_582_1999` | Sentencia C-582 de 1999 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1999/C-582-99.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_746_2011` | Sentencia C-746 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-746-11.htm) | 2026-09-28 | — | — | Constitucional, Familia |
| `sentencia_c_748_2011` | Sentencia C-748 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-748-11.htm) | 2026-09-28 | — | — | Civil, Mercados |
| `sentencia_c_94_2021` | Sentencia C-94 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-094-21.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_96_2024` | Sentencia C-96 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/C-096-24.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_su_111_2025` | Sentencia SU-111 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU111-25.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_su_214_2016` | Sentencia SU-214 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/SU214-16.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_547_2017` | Sentencia T-547 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/T-547-17.htm) | 2026-09-28 | — | — | Constitucional, Laboral |
| `codigo_disciplinario` | Codigo General Disciplinario (Ley 1952 de 2019) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1952_2019.html) | 2026-09-29 | — | — | Administrativo |
| `codigo_nacional_policia` | Codigo Nacional de Seguridad y Convivencia Ciudadana (Ley 1801 de 2016) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1801_2016.html) | 2026-09-29 | — | — | Procesal |
| `decreto_1082_2015` | Decreto 1082 de 2015 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1082_2015.htm) | 2026-09-29 | — | — | Administrativo |
| `decreto_1742_2020` | Decreto 1742 de 2020 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_1742_2020.html) | 2026-09-29 | — | — | Tributario |
| `decreto_175_2025` | Decreto 175 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0175_2025.html) | 2026-09-29 | — | — | Tributario |
| `decreto_2067_1991` | Decreto 2067 de 1991 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2067_1991.html) | 2026-09-29 | — | — | Constitucional |
| `decreto_24_2016` | Decreto 24 de 2016 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0024_2016.htm) | 2026-09-29 | — | — | Comercial y sociedades |
| `decreto_2737_1989` | Codigo del Menor (Decreto 2737 de 1989) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/codigo_menor.htm) | 2026-09-29 | — | — | Laboral |
| `decreto_405_2025` | Decreto 405 de 2025 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/decreto_0405_2025.htm) | 2026-09-29 | — | — | Laboral |
| `decreto_4334_2008` | Decreto 4334 de 2008 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4334_2008.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `decreto_4436_2005` | Decreto 4436 de 2005 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_4436_2005.htm) | 2026-09-29 | — | — | Familia |
| `decreto_4886_2011` | Decreto 4886 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4886_2011.html) | 2026-09-29 | — | — | Mercados |
| `decreto_663_1993` | Estatuto Organico del Sistema Financiero (Decreto 663 de 1993) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/estatuto_organico_sistema_financiero.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `decreto_780_2016` | Decreto 780 de 2016 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_0780_2016.htm) | 2026-09-29 | — | — | Penal |
| `decreto_875_2008` | Decreto 875 de 2008 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_0875_2008.htm) | 2026-09-29 | — | — | Laboral |
| `decreto_960_1970` | Decreto 960 de 1970 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0960_1970.html) | 2026-09-29 | — | — | Civil |
| `ley_1151_2007` | Ley 1151 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1151_2007.html) | 2026-09-29 | — | — | Administrativo |
| `ley_137_1994` | Ley 137 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0137_1994.html) | 2026-09-29 | — | — | Tributario |
| `ley_1473_2011` | Ley 1473 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1473_2011.html) | 2026-09-29 | — | — | Tributario |
| `ley_155_1959` | Ley 155 de 1959 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0155_1959.htm) | 2026-09-29 | — | — | Mercados |
| `ley_1562_2012` | Ley 1562 de 2012 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1562_2012.html) | 2026-09-29 | — | — | Laboral |
| `ley_1607_2012` | Ley 1607 de 2012 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1607_2012.html) | 2026-09-29 | — | — | Tributario |
| `ley_160_1994` | Ley 160 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0160_1994.html) | 2026-09-29 | — | — | Civil |
| `ley_1700_2013` | Ley 1700 de 2013 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1700_2013.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `ley_1755_2015` | Ley 1755 de 2015 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1755_2015.html) | 2026-09-29 | — | — | Administrativo |
| `ley_1819_2016` | Ley 1819 de 2016 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1819_2016.html) | 2026-09-29 | — | — | Tributario |
| `ley_1909_2018` | Ley 1909 de 2018 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1909_2018.html) | 2026-09-29 | — | — | Constitucional |
| `ley_2114_2021` | Ley 2114 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2114_2021.html) | 2026-09-29 | — | — | Laboral |
| `ley_2157_2021` | Ley 2157 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2157_2021.html) | 2026-09-29 | — | — | Mercados |
| `ley_2160_2021` | Ley 2160 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2160_2021.html) | 2026-09-29 | — | — | Administrativo |
| `ley_2251_2022` | Ley 2251 de 2022 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2251_2022.html) | 2026-09-29 | — | — | Civil |
| `ley_29_1982` | Ley 29 de 1982 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0029_1982.htm) | 2026-09-29 | — | — | Familia |
| `ley_527_1999` | Ley 527 de 1999 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0527_1999.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `ley_600_2000` | Ley 600 de 2000 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0600_2000.html) | 2026-09-29 | — | — | Penal |
| `ley_640_2001` | Ley 640 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0640_2001.html) | 2026-09-29 | — | — | Mercados |
| `ley_678_2001` | Ley 678 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0678_2001.html) | 2026-09-29 | — | — | Procesal |
| `ley_721_2001` | Ley 721 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0721_2001.html) | 2026-09-29 | — | — | Familia |
| `ley_75_1968` | Ley 75 de 1968 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0075_1968.htm) | 2026-09-29 | — | — | Familia |
| `ley_769_2002` | Ley 769 de 2002 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0769_2002.html) | 2026-09-29 | — | — | Civil |
| `ley_820_2003` | Ley 820 de 2003 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0820_2003.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `ley_964_2005` | Ley 964 de 2005 (Mercado de Valores) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0964_2005.html) | 2026-09-29 | — | — | Comercial y sociedades |
| `sentencia_c_1033_2002` | Sentencia C-1033 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-1033-02.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_106_2018` | Sentencia C-106 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-106-18.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_1189_2000` | Sentencia C-1189 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-1189-00.htm) | 2026-09-28 | — | — | Penal |
| `sentencia_c_131_2018` | Sentencia C-131 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-131-18.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_145_2018` | Sentencia C-145 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-145-18.htm) | 2026-09-28 | — | — | Comercial y sociedades |
| `sentencia_c_145_2020` | Sentencia C-145 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/C-145-20.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_149_1993` | Sentencia C-149 de 1993 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1993/C-149-93.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_170_2004` | Sentencia C-170 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-170-04.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_c_183_2025` | Sentencia C-183 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-183-25.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_c_201_2002` | Sentencia C-201 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-201-02.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_c_225_1995` | Sentencia C-225 de 1995 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1995/C-225-95.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_22_1996` | Sentencia C-22 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-022-96.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_233_2021` | Sentencia C-233 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-233-21.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_239_1997` | Sentencia C-239 de 1997 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1997/C-239-97.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_276_2025` | Sentencia C-276 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-276-25.htm) | 2026-09-28 | — | — | Comercial y sociedades |
| `sentencia_c_332_2025` | Sentencia C-332 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-332-25.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_335_2008` | Sentencia C-335 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/C-335-08.htm) | 2026-09-28 | — | — | Penal |
| `sentencia_c_345_2017` | Sentencia C-345 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-345-17.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_c_389_2023` | Sentencia C-389 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-389-23.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_39_2025` | Sentencia C-39 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-039-25.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_413_1996` | Sentencia C-413 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-413-96.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_459_2023` | Sentencia C-459 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-459-23.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_486_1993` | Sentencia C-486 de 1993 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1993/C-486-93.htm) | 2026-09-28 | — | — | Comercial y sociedades |
| `sentencia_c_4_1998` | Sentencia C-4 de 1998 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1998/C-004-98.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_533_2000` | Sentencia C-533 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-533-00.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_535_2002` | Sentencia C-535 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-535-02.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_c_537_1995` | Sentencia C-537 de 1995 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1995/C-537-95.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_683_2015` | Sentencia C-683 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-683-15.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_700_1999` | Sentencia C-700 de 1999 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1999/C-700-99.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_c_80_2025` | Sentencia C-80 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-080-25.htm) | 2026-09-28 | — | — | Mercados |
| `sentencia_c_891_2012` | Sentencia C-891 de 2012 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2012/C-891-12.htm) | 2026-09-28 | — | — | Tributario |
| `sentencia_c_964_2003` | Sentencia C-964 de 2003 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2003/C-964-03.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_c_985_2010` | Sentencia C-985 de 2010 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2010/C-985-10.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_su_11_2020` | Sentencia SU-11 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU011-20.htm) | 2026-09-28 | — | — | Administrativo |
| `sentencia_su_138_2024` | Sentencia SU-138 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU138-24.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_149_2021` | Sentencia SU-149 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU149-21.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_su_207_2022` | Sentencia SU-207 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU207-22.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_240_2015` | Sentencia SU-240 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU240-15.htm) | 2026-09-28 | — | — | Administrativo |
| `sentencia_su_27_2021` | Sentencia SU-27 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU027-21.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_su_296_2023` | Sentencia SU-296 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU296-23.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_su_380_2021` | Sentencia SU-380 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU380-21.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_396_2024` | Sentencia SU-396 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU396-24.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_su_425_2025` | Sentencia SU-425 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU425-25.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_429_2024` | Sentencia SU-429 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU429-24.htm) | 2026-09-28 | — | — | Penal |
| `sentencia_su_431_2015` | Sentencia SU-431 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU431-15.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_455_2020` | Sentencia SU-455 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU455-20.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_500_2015` | Sentencia SU-500 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU500-15.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_su_566_2015` | Sentencia SU-566 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU566-15.htm) | 2026-09-28 | — | — | Administrativo |
| `sentencia_t_1001_2001` | Sentencia T-1001 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/T-1001-01.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_1059_2001` | Sentencia T-1059 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/T-1059-01.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_t_1096_2008` | Sentencia T-1096 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/T-1096-08.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_145_2016` | Sentencia T-145 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/T-145-16.htm) | 2026-09-28 | — | — | Laboral |
| `sentencia_t_230_2023` | Sentencia T-230 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/T-230-23.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_232_2025` | Sentencia T-232 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-232-25.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_262_2025` | Sentencia T-262 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-262-25.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_26_2025` | Sentencia T-26 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-026-25.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_t_325_2025` | Sentencia T-325 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-325-25.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_350_2025` | Sentencia T-350 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-350-25.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_429_2011` | Sentencia T-429 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/T-429-11.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_445_2024` | Sentencia T-445 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-445-24.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_4_2026` | Sentencia T-4 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-004-26.htm) | 2026-09-28 | — | — | Civil |
| `sentencia_t_67_2025` | Sentencia T-67 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-067-25.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_71_2016` | Sentencia T-71 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/T-071-16.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_77_2025` | Sentencia T-77 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-077-25.htm) | 2026-09-28 | — | — | Familia |
| `sentencia_t_925_2014` | Sentencia T-925 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/T-925-14.htm) | 2026-09-28 | — | — | Constitucional |
| `sentencia_t_970_2014` | Sentencia T-970 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/T-970-14.htm) | 2026-09-28 | — | — | Constitucional |

**Pendientes de descarga (24).** Objetivos de `data/seed_targets.json` que el script no pudo descargar; el detalle está en `data/fuentes_descargadas.json`.

| doc_id | Estado | Motivo |
|---|---|---|
| `ley_11500_2007` | errata | errata de la semilla: es la Ley 1150 de 2007, ya en el corpus como ley_1150_2007 |
| `ley_1150_2005` | errata | errata de la semilla: la Ley 1150 es de 2007, ya en el corpus como ley_1150_2007 |
| `ley_116_2006` | errata | errata de la semilla: probablemente la Ley 1116 de 2006 (insolvencia), ya en el corpus como ley_1116_2006 |
| `decreto_46_2024` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/decreto_0046_2024.html no existe en Secretaria del Senado |
| `ley_1692_2017` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/ley_1692_2017.html no existe en Secretaria del Senado |
| `ley_23_1961` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/ley_0023_1961.html no existe en Secretaria del Senado |
| `sentencia_su_488_2011` | no_encontrado | https://www.corteconstitucional.gov.co/relatoria/2011/SU488-11.htm no existe en Relatoria de la Corte Constitucional |
| `sentencia_su_6_1991` | no_encontrado | no existen sentencias SU de 1991 (la Corte empezo en 1992); referencia de la semilla probablemente erronea |
| `sentencia_t_248_2025` | no_encontrado | https://www.corteconstitucional.gov.co/relatoria/2025/T-248-25.htm no existe en Relatoria de la Corte Constitucional |
| `sentencia_sl_648_2018` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sp_1680_2022` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sp_1945_2019` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `acuerdo_2_2015` | sin_resolver | tipo 'acuerdo' sin regla de resolucion; agregar a data/fuentes_override.json |
| `sentencia_sc_1121_2018` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sc_18392_2017` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sc_3085_2024` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sc_3674_2021` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sc_425_2024` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sc_8453_2016` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sl_1050_2023` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sl_1730_2020` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sl_1972_2025` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sp_1167_2022` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |
| `sentencia_sp_3218_2021` | sin_resolver | Corte Suprema: sin URL predecible; agregar a data/fuentes_override.json |

<!-- inventario:fin -->

**Totales**

*Agregados de la tabla anterior. Recalcular en cada actualización del corpus.*

| Métrica | Valor |
|---|---:|
| Documentos incorporados | |
| Artículos indexados | |
| Fragmentos en el índice | |
| Tamaño del corpus procesado | |
| Tamaño del índice vectorial | |

## 2. Criterio de selección

*Justificar por qué se priorizaron estas fuentes/áreas frente a la composición
del banco de preguntas (enunciado, sección 4.2). Debe explicar el criterio, no
solo describir lo incorporado.*

| Área | Ítems en el banco | Documentos incorporados | Cobertura estimada |
|---|---:|---:|---|
| Derecho constitucional | 134 | | |
| Derecho administrativo | 124 | | |
| Derecho penal | 123 | | |
| Derecho procesal | 111 | | |
| Derecho comercial y sociedades | 104 | | |
| Derecho civil | 102 | | |
| Derecho de familia | 93 | | |
| Derecho tributario | 92 | | |
| Derecho laboral | 87 | | |
| Derecho de los mercados | 72 | | |

**Documentos descartados.**

*Qué se consideró incorporar y no se incluyó, y por qué (volumen, redundancia,
prioridad de tiempo frente al banco, etc.).*

## 3. Método de ingesta y limpieza

*Describir el pipeline real usado, con las herramientas específicas de cada
paso (ver el ejemplo para el nivel de detalle esperado por el jurado).*

1. **Descarga.** `src/ingesta/descargar_fuentes.py` (solo biblioteca estándar de
   Python) recorre los 186 objetivos de `data/seed_targets.json` en orden de ítems
   del banco. Como la semilla solo trae URLs de búsqueda, cada objetivo se resuelve
   con reglas deterministas a la URL del documento: normas en la Secretaría del
   Senado (`basedoc/ley_NNNN_AAAA.html` más todas sus partes `_prNNN.html`),
   sentencias C/T/SU en la relatoría de la Corte Constitucional
   (`relatoria/AAAA/C-NNN-AA.htm`) y la Decisión Andina 486 en el PDF oficial de la
   Comunidad Andina. Los originales se guardan sin modificar en
   `data/raw_sources/<tipo>/<doc_id>/`, clasificados por tipo de archivo (`html`,
   `pdf`, `pdf_escaneado`, `otros`), con pausa de 1 s entre peticiones. Los
   documentos de mayor impacto (Constitución y Código General del Proceso) no se
   descargan con el script: sus PDF se obtienen a mano para controlar la calidad
   del dato, y el script solo los registra. La URL real, la
   fecha de consulta, el estado y el sha256 de cada descarga quedan en
   `data/fuentes_descargadas.json`, a partir del cual se genera el inventario de la
   sección 1.
2. **Extracción de texto.**
3. **Normalización.**
4. **Segmentación.**
5. **Extracción de metadatos.**
6. **Indexación.**

**Problemas encontrados.**

*Fallas concretas del pipeline (OCR, normas derogadas, encoding, artículos
duplicados, etc.) y cómo se resolvieron.*

**Decisiones de diseño relevantes.**

*Cualquier decisión no obvia (p. ej. qué información lleva el encabezado de
cada fragmento) y por qué afecta el puntaje de citación/recuperación.*

## 4. Evolución del puntaje

*Una fila por corrida de autoevaluación con `scripts/evaluate.py` contra
`data/sample_50.jsonl`, en orden cronológico. Sirve para mostrarle al jurado
qué cambios del corpus movieron qué métrica.*

| Fecha | Documentos | Fragmentos | Cerradas /20 | Citación /20 | Abstención /10 | Total /50 | Qué cambió |
|---|---:|---:|---:|---:|---:|---:|---|
| | | | | | | | |

**Lectura de la curva.**

*Interpretar los saltos o estancamientos de la tabla anterior: qué cambio del
corpus o del pipeline explica cada variación.*

## 5. Licencia

*Bajo qué licencia se publica el corpus procesado. Los textos normativos
colombianos suelen ser de dominio público; la licencia cubre el trabajo de
procesamiento (segmentación, limpieza, extracción de metadatos) del equipo.*

## 6. Enlace al corpus e índice

*Debe coincidir con el enlace declarado en `README.md`, sección "Corpus e
índice". El comprimido debe contener `LICENSE`, `corpus_manifest.json`,
`corpus/` e `indice/` (`index.faiss` + `chunks.jsonl`). Verificar que el
enlace sea público y esté vigente antes de la entrega (ver `enunciado.pdf`).*

| Recurso | Enlace | Tamaño | Vigencia |
|---|---|---|---|
| | | | |
