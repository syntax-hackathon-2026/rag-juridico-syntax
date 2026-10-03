# Bitácora del corpus — Syntax

Corpus jurídico colombiano de **Syntax** (Sofía Morato, Joel David Niño, Santiago Muñoz) para el RAG de la Hackathon LATAM AI Week 2026. Versión congelada: **v5, 1.285 documentos, 185.234 fragmentos** (generada el 2026-10-03).

---

## 1. Inventario

Una fila por documento fuente. `doc_id` coincide con `corpus_manifest.json`, con la metadata de los fragmentos y con `pasajes_recuperados.doc_id`. "Fecha de consulta" es la fecha de descarga. "Áreas" son las del banco de preguntas (enunciado, sección 4.2). La tabla se genera con `src/ingesta/descargar_fuentes.py --corpus-md` desde `data/registros/fuentes_descargadas.json`.

<!-- inventario:inicio (generado por src/ingesta/descargar_fuentes.py --corpus-md) -->

| doc_id | Título | Fuente | URL | Fecha de consulta | Artículos | Fragmentos | Áreas |
|---|---|---|---|---|---:|---:|---|
| `constitucion_politica_1991` | Constitucion Politica de Colombia de 1991 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=4125) | 2026-09-29 | 380 | 667 | Administrativo, Comercial y sociedades, Constitucional, Familia, Laboral, Mercados, Penal, Procesal, Tributario |
| `codigo_general_proceso` | Codigo General del Proceso (Ley 1564 de 2012) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=48425) | 2026-09-29 | 627 | 733 | Civil, Comercial y sociedades, Familia, Mercados, Penal, Procesal, Tributario |
| `codigo_sustantivo_trabajo` | Codigo Sustantivo del Trabajo | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=199983) | 2026-09-29 | 487 | 533 | Laboral |
| `estatuto_tributario` | Estatuto Tributario (Decreto 624 de 1989) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6533) | 2026-09-29 | 932 | 1.458 | Civil, Constitucional, Tributario |
| `decision_andina_486` | Decision 486 de 2000 de la Comunidad Andina, Regimen Comun sobre Propiedad Industrial | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC486.pdf) | 2026-09-28 | 280 | 283 | Comercial y sociedades, Mercados |
| `estatuto_consumidor` | Estatuto del Consumidor (Ley 1480 de 2011) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=44306) | 2026-09-29 | 84 | 106 | Civil, Mercados |
| `ley_80_1993` | Ley 80 de 1993 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=304) | 2026-09-29 | 86 | 121 | Administrativo, Laboral |
| `ley_2220_2022` | Ley 2220 de 2022 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=188766) | 2026-09-29 | 151 | 162 | Civil, Procesal |
| `decreto_2153_1992` | Decreto 2153 de 1992 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=38168) | 2026-09-29 | 59 | 70 | Mercados |
| `ley_1116_2006` | Ley 1116 de 2006 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=22657) | 2026-09-29 | 126 | 147 | Comercial y sociedades, Procesal |
| `sentencia_c_355_2006` | Sentencia C-355 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/C-355-06.htm) | 2026-09-29 | — | 1.057 | Constitucional, Penal |
| `ley_1581_2012` | Ley 1581 de 2012 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981) | 2026-09-29 | 30 | 33 | Administrativo, Constitucional, Mercados |
| `codigo_infancia` | Codigo de la Infancia y la Adolescencia (Ley 1098 de 2006) | Instituto Colombiano de Bienestar Familiar (ICBF) | [enlace](https://www.icbf.gov.co/sites/default/files/codigoinfancialey1098.pdf) | 2026-09-29 | 216 | 239 | Familia |
| `ley_1258_2008` | Ley 1258 de 2008 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=34130) | 2026-09-29 | 46 | 47 | Comercial y sociedades |
| `sentencia_c_207_2019` | Sentencia C-207 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/C-207-19.htm) | 2026-09-29 | — | 307 | Administrativo |
| `sentencia_sl_3385_2022` | Sentencia SL-3385 de 2022 | RedJurista | [enlace](https://www.redjurista.com/appfolders/images/news/CSJ_SCL_SL3385_2022_2022.pdf) | 2026-09-29 | — | 20 | Laboral |
| `sentencia_t_323_2024` | Sentencia T-323 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-323-24.htm) | 2026-09-29 | — | 268 | Constitucional |
| `ley_1010_2006` | Ley 1010 de 2006 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1010_2006.html) | 2026-09-29 | 19 | 24 | Laboral |
| `ley_1150_2007` | Ley 1150 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1150_2007.html) | 2026-09-29 | 32 | 53 | Administrativo |
| `ley_1340_2009` | Ley 1340 de 2009 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1340_2009.html) | 2026-09-29 | 34 | 37 | Mercados |
| `ley_153_1887` | Ley 153 de 1887 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0153_1887.htm) | 2026-09-29 | 327 | 328 | Civil, Tributario |
| `ley_2437_2024` | Ley 2437 de 2024 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2437_2024.html) | 2026-09-29 | 21 | 37 | Civil, Procesal |
| `ley_54_1990` | Ley 54 de 1990 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0054_1990.htm) | 2026-09-29 | 9 | 10 | Familia |
| `ley_979_2005` | Ley 979 de 2005 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0979_2005.html) | 2026-09-29 | 5 | 10 | Familia |
| `sentencia_c_394_2017` | Sentencia C-394 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-394-17.htm) | 2026-09-28 | — | 194 | Constitucional, Familia |
| `sentencia_c_55_2022` | Sentencia C-55 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/C-055-22.htm) | 2026-09-28 | — | 935 | Constitucional, Penal |
| `sentencia_su_315_2025` | Sentencia SU-315 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU315-25.htm) | 2026-09-28 | — | 170 | Civil |
| `sentencia_t_243_2018` | Sentencia T-243 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/T-243-18.htm) | 2026-09-28 | — | 72 | Laboral |
| `sentencia_t_760_2008` | Sentencia T-760 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/T-760-08.htm) | 2026-09-28 | — | 878 | Administrativo, Constitucional |
| `ley_1095_2006` | Ley 1095 de 2006 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1095_2006.html) | 2026-09-29 | 10 | 11 | Constitucional, Penal |
| `ley_1563_2012` | Ley 1563 de 2012 (Estatuto de Arbitraje Nacional e Internacional) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1563_2012.html) | 2026-09-29 | 119 | 128 | Procesal |
| `ley_2141_2021` | Ley 2141 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2141_2021.html) | 2026-09-29 | 3 | 5 | Constitucional, Laboral |
| `ley_2452_2025` | Ley 2452 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2452_2025.html) | 2026-09-29 | 331 | 373 | Laboral |
| `ley_2466_2025` | Ley 2466 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2466_2025.html) | 2026-09-29 | 22 | 87 | Laboral |
| `ley_256_1996` | Ley 256 de 1996 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0256_1996.html) | 2026-09-29 | 33 | 34 | Mercados |
| `ley_50_1990` | Ley 50 de 1990 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0050_1990.htm) | 2026-09-29 | 171 | 131 | Laboral |
| `sentencia_c_117_2018` | Sentencia C-117 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-117-18.htm) | 2026-09-28 | — | 184 | Tributario |
| `sentencia_c_127_2011` | Sentencia C-127 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-127-11.htm) | 2026-09-28 | — | 70 | Constitucional |
| `sentencia_c_134_2019` | Sentencia C-134 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/C-134-19.htm) | 2026-09-28 | — | 43 | Constitucional, Familia |
| `sentencia_c_15_2018` | Sentencia C-15 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-015-18.htm) | 2026-09-28 | — | 140 | Constitucional, Penal |
| `sentencia_c_164_2022` | Sentencia C-164 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/C-164-22.htm) | 2026-09-28 | — | 158 | Constitucional, Penal |
| `sentencia_c_259_2015` | Sentencia C-259 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-259-15.htm) | 2026-09-28 | — | 122 | Administrativo, Procesal |
| `sentencia_c_35_2009` | Sentencia C-35 de 2009 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2009/C-035-09.htm) | 2026-09-28 | — | 70 | Tributario |
| `sentencia_c_431_2001` | Sentencia C-431 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-431-01.htm) | 2026-09-28 | — | 10 | Constitucional, Penal |
| `sentencia_c_500_2024` | Sentencia C-500 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/C-500-24.htm) | 2026-09-28 | — | 91 | Procesal, Tributario |
| `sentencia_c_507_2004` | Sentencia C-507 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-507-04.htm) | 2026-09-28 | — | 256 | Familia |
| `sentencia_c_540_2023` | Sentencia C-540 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-540-23.htm) | 2026-09-28 | — | 98 | Tributario |
| `sentencia_c_582_1999` | Sentencia C-582 de 1999 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1999/C-582-99.htm) | 2026-09-28 | — | 22 | Constitucional |
| `sentencia_c_746_2011` | Sentencia C-746 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-746-11.htm) | 2026-09-28 | — | 29 | Constitucional, Familia |
| `sentencia_c_748_2011` | Sentencia C-748 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-748-11.htm) | 2026-09-28 | — | 520 | Civil, Mercados |
| `sentencia_c_94_2021` | Sentencia C-94 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-094-21.htm) | 2026-09-28 | — | 123 | Constitucional |
| `sentencia_c_96_2024` | Sentencia C-96 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/C-096-24.htm) | 2026-09-28 | — | 164 | Familia |
| `sentencia_sl_648_2018` | Sentencia SL-648 de 2018 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 46 | Laboral |
| `sentencia_sp_1680_2022` | Sentencia SP-1680 de 2022 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 36 | Penal |
| `sentencia_sp_1945_2019` | Sentencia SP-1945 de 2019 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 22 | Penal |
| `sentencia_su_111_2025` | Sentencia SU-111 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU111-25.htm) | 2026-09-28 | — | 176 | Laboral |
| `sentencia_su_214_2016` | Sentencia SU-214 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/SU214-16.htm) | 2026-09-28 | — | 559 | Familia |
| `sentencia_t_547_2017` | Sentencia T-547 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/T-547-17.htm) | 2026-09-28 | — | 75 | Constitucional, Laboral |
| `acuerdo_2_2015` | Acuerdo 02 de 2015 de la Corte Constitucional (Reglamento de la Corte Constitucional) | Regimen Legal de Bogota (Secretaria Juridica Distrital) | [enlace](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=154021) | 2026-10-01 | 113 | 121 | Constitucional |
| `codigo_disciplinario` | Codigo General Disciplinario (Ley 1952 de 2019) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1952_2019.html) | 2026-09-29 | 257 | 299 | Administrativo |
| `codigo_nacional_policia` | Codigo Nacional de Seguridad y Convivencia Ciudadana (Ley 1801 de 2016) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1801_2016.html) | 2026-09-29 | 200 | 315 | Procesal |
| `decreto_1082_2015` | Decreto 1082 de 2015 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1082_2015.htm) | 2026-09-29 | 786 | 920 | Administrativo |
| `decreto_1742_2020` | Decreto 1742 de 2020 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_1742_2020.html) | 2026-09-29 | 80 | 150 | Tributario |
| `decreto_175_2025` | Decreto 175 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0175_2025.html) | 2026-09-29 | 10 | 27 | Tributario |
| `decreto_2067_1991` | Decreto 2067 de 1991 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2067_1991.html) | 2026-09-29 | 54 | 59 | Constitucional |
| `decreto_24_2016` | Decreto 24 de 2016 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0024_2016.htm) | 2026-09-29 | 3 | 7 | Comercial y sociedades |
| `decreto_2737_1989` | Codigo del Menor (Decreto 2737 de 1989) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/codigo_menor.htm) | 2026-09-29 | 354 | 361 | Laboral |
| `decreto_405_2025` | Decreto 405 de 2025 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/decreto_0405_2025.htm) | 2026-09-29 | 7 | 6 | Laboral |
| `decreto_4334_2008` | Decreto 4334 de 2008 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4334_2008.html) | 2026-09-29 | 16 | 20 | Comercial y sociedades |
| `decreto_4436_2005` | Decreto 4436 de 2005 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_4436_2005.htm) | 2026-09-29 | 8 | 10 | Familia |
| `decreto_46_2024` | Decreto 046 de 2024 | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=228530) | 2026-10-01 | 2 | 18 | Comercial y sociedades |
| `decreto_4886_2011` | Decreto 4886 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4886_2011.html) | 2026-09-29 | 29 | 63 | Mercados |
| `decreto_663_1993` | Estatuto Organico del Sistema Financiero (Decreto 663 de 1993) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/estatuto_organico_sistema_financiero.html) | 2026-09-29 | 342 | 631 | Comercial y sociedades |
| `decreto_780_2016` | Decreto 780 de 2016 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_0780_2016.htm) | 2026-09-29 | 2.396 | 2.913 | Penal |
| `decreto_875_2008` | Decreto 875 de 2008 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_0875_2008.htm) | 2026-09-29 | 3 | 3 | Laboral |
| `decreto_960_1970` | Decreto 960 de 1970 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0960_1970.html) | 2026-09-29 | 233 | 236 | Civil |
| `ley_1151_2007` | Ley 1151 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1151_2007.html) | 2026-09-29 | 159 | 259 | Administrativo |
| `ley_137_1994` | Ley 137 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0137_1994.html) | 2026-09-29 | 59 | 66 | Tributario |
| `ley_1473_2011` | Ley 1473 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1473_2011.html) | 2026-09-29 | 16 | 23 | Tributario |
| `ley_155_1959` | Ley 155 de 1959 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0155_1959.htm) | 2026-09-29 | 20 | 22 | Mercados |
| `ley_1562_2012` | Ley 1562 de 2012 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1562_2012.html) | 2026-09-29 | 33 | 46 | Laboral |
| `ley_1607_2012` | Ley 1607 de 2012 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1607_2012.html) | 2026-09-29 | 198 | 315 | Tributario |
| `ley_160_1994` | Ley 160 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0160_1994.html) | 2026-09-29 | 113 | 142 | Civil |
| `ley_1692_2013` | Ley 1692 de 2013 (Convenio Colombia-Portugal para evitar la doble imposicion) | Normograma de la DIAN | [enlace](https://www.dian.gov.co/normatividad/convenios/ConveniosTributacionInternacional/B149.pdf) | 2026-10-01 | 30 | 67 | Tributario |
| `ley_1700_2013` | Ley 1700 de 2013 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1700_2013.html) | 2026-09-29 | 13 | 15 | Comercial y sociedades |
| `ley_1755_2015` | Ley 1755 de 2015 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1755_2015.html) | 2026-09-29 | 2 | 12 | Administrativo |
| `ley_1819_2016` | Ley 1819 de 2016 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1819_2016.html) | 2026-09-29 | 373 | 554 | Tributario |
| `ley_1909_2018` | Ley 1909 de 2018 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1909_2018.html) | 2026-09-29 | 32 | 37 | Constitucional |
| `ley_2114_2021` | Ley 2114 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2114_2021.html) | 2026-09-29 | 6 | 14 | Laboral |
| `ley_2157_2021` | Ley 2157 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2157_2021.html) | 2026-09-29 | 14 | 17 | Mercados |
| `ley_2160_2021` | Ley 2160 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2160_2021.html) | 2026-09-29 | 5 | 10 | Administrativo |
| `ley_2251_2022` | Ley 2251 de 2022 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2251_2022.html) | 2026-09-29 | 24 | 28 | Civil |
| `ley_23_1991` | Ley 23 de 1991 (descongestion de despachos judiciales) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6546) | 2026-10-01 | 105 | 114 | Constitucional |
| `ley_29_1982` | Ley 29 de 1982 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0029_1982.htm) | 2026-09-29 | 11 | 12 | Familia |
| `ley_527_1999` | Ley 527 de 1999 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0527_1999.html) | 2026-09-29 | 47 | 50 | Comercial y sociedades |
| `ley_600_2000` | Ley 600 de 2000 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0600_2000.html) | 2026-09-29 | 557 | 574 | Penal |
| `ley_640_2001` | Ley 640 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0640_2001.html) | 2026-09-29 | 50 | 52 | Mercados |
| `ley_678_2001` | Ley 678 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0678_2001.html) | 2026-09-29 | 30 | 36 | Procesal |
| `ley_721_2001` | Ley 721 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0721_2001.html) | 2026-09-29 | 13 | 14 | Familia |
| `ley_75_1968` | Ley 75 de 1968 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0075_1968.htm) | 2026-09-29 | 67 | 71 | Familia |
| `ley_769_2002` | Ley 769 de 2002 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0769_2002.html) | 2026-09-29 | 169 | 224 | Civil |
| `ley_820_2003` | Ley 820 de 2003 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0820_2003.html) | 2026-09-29 | 43 | 49 | Comercial y sociedades |
| `ley_964_2005` | Ley 964 de 2005 (Mercado de Valores) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0964_2005.html) | 2026-09-29 | 82 | 116 | Comercial y sociedades |
| `sentencia_c_1033_2002` | Sentencia C-1033 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-1033-02.htm) | 2026-09-28 | — | 36 | Familia |
| `sentencia_c_106_2018` | Sentencia C-106 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-106-18.htm) | 2026-09-28 | — | 125 | Constitucional |
| `sentencia_c_1189_2000` | Sentencia C-1189 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-1189-00.htm) | 2026-09-28 | — | 79 | Penal |
| `sentencia_c_131_2018` | Sentencia C-131 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-131-18.htm) | 2026-09-28 | — | 69 | Familia |
| `sentencia_c_145_2018` | Sentencia C-145 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-145-18.htm) | 2026-09-28 | — | 81 | Comercial y sociedades |
| `sentencia_c_145_2020` | Sentencia C-145 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/C-145-20.htm) | 2026-09-28 | — | 306 | Constitucional |
| `sentencia_c_149_1993` | Sentencia C-149 de 1993 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1993/C-149-93.htm) | 2026-09-28 | — | 32 | Constitucional |
| `sentencia_c_170_2004` | Sentencia C-170 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-170-04.htm) | 2026-09-28 | — | 108 | Laboral |
| `sentencia_c_183_2025` | Sentencia C-183 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-183-25.htm) | 2026-09-28 | — | 160 | Civil |
| `sentencia_c_201_2002` | Sentencia C-201 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-201-02.htm) | 2026-09-28 | — | 98 | Laboral |
| `sentencia_c_225_1995` | Sentencia C-225 de 1995 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1995/C-225-95.htm) | 2026-09-28 | — | 124 | Constitucional |
| `sentencia_c_22_1996` | Sentencia C-22 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-022-96.htm) | 2026-09-28 | — | 20 | Constitucional |
| `sentencia_c_233_2021` | Sentencia C-233 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-233-21.htm) | 2026-09-28 | — | 423 | Constitucional |
| `sentencia_c_239_1997` | Sentencia C-239 de 1997 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1997/C-239-97.htm) | 2026-09-28 | — | 209 | Constitucional |
| `sentencia_c_276_2025` | Sentencia C-276 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-276-25.htm) | 2026-09-28 | — | 125 | Comercial y sociedades |
| `sentencia_c_332_2025` | Sentencia C-332 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-332-25.htm) | 2026-09-28 | — | 107 | Constitucional |
| `sentencia_c_335_2008` | Sentencia C-335 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/C-335-08.htm) | 2026-09-28 | — | 90 | Penal |
| `sentencia_c_345_2017` | Sentencia C-345 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-345-17.htm) | 2026-09-28 | — | 113 | Civil |
| `sentencia_c_389_2023` | Sentencia C-389 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-389-23.htm) | 2026-09-28 | — | 79 | Tributario |
| `sentencia_c_39_2025` | Sentencia C-39 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-039-25.htm) | 2026-09-28 | — | 186 | Familia |
| `sentencia_c_413_1996` | Sentencia C-413 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-413-96.htm) | 2026-09-28 | — | 16 | Tributario |
| `sentencia_c_459_2023` | Sentencia C-459 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-459-23.htm) | 2026-09-28 | — | 86 | Constitucional |
| `sentencia_c_486_1993` | Sentencia C-486 de 1993 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1993/C-486-93.htm) | 2026-09-28 | — | 62 | Comercial y sociedades |
| `sentencia_c_4_1998` | Sentencia C-4 de 1998 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1998/C-004-98.htm) | 2026-09-28 | — | 20 | Familia |
| `sentencia_c_533_2000` | Sentencia C-533 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-533-00.htm) | 2026-09-28 | — | 22 | Familia |
| `sentencia_c_535_2002` | Sentencia C-535 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/C-535-02.htm) | 2026-09-28 | — | 26 | Laboral |
| `sentencia_c_537_1995` | Sentencia C-537 de 1995 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1995/C-537-95.htm) | 2026-09-28 | — | 50 | Tributario |
| `sentencia_c_683_2015` | Sentencia C-683 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-683-15.htm) | 2026-09-28 | — | 406 | Familia |
| `sentencia_c_700_1999` | Sentencia C-700 de 1999 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1999/C-700-99.htm) | 2026-09-28 | — | 214 | Constitucional |
| `sentencia_c_80_2025` | Sentencia C-80 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-080-25.htm) | 2026-09-28 | — | 125 | Mercados |
| `sentencia_c_891_2012` | Sentencia C-891 de 2012 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2012/C-891-12.htm) | 2026-09-28 | — | 56 | Tributario |
| `sentencia_c_964_2003` | Sentencia C-964 de 2003 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2003/C-964-03.htm) | 2026-09-28 | — | 70 | Familia |
| `sentencia_c_985_2010` | Sentencia C-985 de 2010 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2010/C-985-10.htm) | 2026-09-28 | — | 78 | Familia |
| `sentencia_sc_1121_2018` | Sentencia SC-1121 de 2018 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 38 | Civil |
| `sentencia_sc_18392_2017` | Sentencia SC-18392 de 2017 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 38 | Comercial y sociedades |
| `sentencia_sc_3085_2024` | Sentencia SC-3085 de 2024 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 95 | Familia |
| `sentencia_sc_3674_2021` | Sentencia SC-3674 de 2021 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 21 | Comercial y sociedades |
| `sentencia_sc_425_2024` | Sentencia SC-425 de 2024 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 75 | Comercial y sociedades |
| `sentencia_sc_8453_2016` | Sentencia SC-8453 de 2016 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 38 | Comercial y sociedades |
| `sentencia_sl_1050_2023` | Sentencia SL-1050 de 2023 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 61 | Laboral |
| `sentencia_sl_1730_2020` | Sentencia SL-1730 de 2020 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 57 | Laboral |
| `sentencia_sl_1972_2025` | Sentencia SL-1972 de 2025 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 42 | Laboral |
| `sentencia_sp_1167_2022` | Sentencia SP-1167 de 2022 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 36 | Penal |
| `sentencia_sp_248_2025` | Sentencia SP-248 de 2025 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 55 | Penal |
| `sentencia_sp_3218_2021` | Sentencia SP-3218 de 2021 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 92 | Penal |
| `sentencia_su_11_2020` | Sentencia SU-11 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU011-20.htm) | 2026-09-28 | — | 120 | Administrativo |
| `sentencia_su_138_2024` | Sentencia SU-138 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU138-24.htm) | 2026-09-28 | — | 211 | Civil |
| `sentencia_su_149_2021` | Sentencia SU-149 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU149-21.htm) | 2026-09-28 | — | 115 | Laboral |
| `sentencia_su_207_2022` | Sentencia SU-207 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU207-22.htm) | 2026-09-28 | — | 134 | Civil |
| `sentencia_su_240_2015` | Sentencia SU-240 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU240-15.htm) | 2026-09-28 | — | 99 | Administrativo |
| `sentencia_su_27_2021` | Sentencia SU-27 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU027-21.htm) | 2026-09-28 | — | 99 | Laboral |
| `sentencia_su_296_2023` | Sentencia SU-296 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU296-23.htm) | 2026-09-28 | — | 150 | Laboral |
| `sentencia_su_380_2021` | Sentencia SU-380 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU380-21.htm) | 2026-09-28 | — | 127 | Civil |
| `sentencia_su_396_2024` | Sentencia SU-396 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU396-24.htm) | 2026-09-28 | — | 177 | Laboral |
| `sentencia_su_425_2025` | Sentencia SU-425 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU425-25.htm) | 2026-09-28 | — | 78 | Civil |
| `sentencia_su_429_2024` | Sentencia SU-429 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU429-24.htm) | 2026-09-28 | — | 259 | Penal |
| `sentencia_su_431_2015` | Sentencia SU-431 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU431-15.htm) | 2026-09-28 | — | 173 | Civil |
| `sentencia_su_455_2020` | Sentencia SU-455 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU455-20.htm) | 2026-09-28 | — | 104 | Civil |
| `sentencia_su_500_2015` | Sentencia SU-500 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU500-15.htm) | 2026-09-28 | — | 220 | Civil |
| `sentencia_su_566_2015` | Sentencia SU-566 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU566-15.htm) | 2026-09-28 | — | 194 | Administrativo |
| `sentencia_t_1001_2001` | Sentencia T-1001 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/T-1001-01.htm) | 2026-09-28 | — | 61 | Constitucional |
| `sentencia_t_1059_2001` | Sentencia T-1059 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/T-1059-01.htm) | 2026-09-28 | — | 41 | Laboral |
| `sentencia_t_1096_2008` | Sentencia T-1096 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/T-1096-08.htm) | 2026-09-28 | — | 62 | Familia |
| `sentencia_t_145_2016` | Sentencia T-145 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/T-145-16.htm) | 2026-09-28 | — | 80 | Laboral |
| `sentencia_t_230_2023` | Sentencia T-230 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/T-230-23.htm) | 2026-09-28 | — | 27 | Constitucional |
| `sentencia_t_232_2025` | Sentencia T-232 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-232-25.htm) | 2026-09-28 | — | 98 | Familia |
| `sentencia_t_262_2025` | Sentencia T-262 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-262-25.htm) | 2026-09-28 | — | 109 | Constitucional |
| `sentencia_t_26_2025` | Sentencia T-26 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-026-25.htm) | 2026-09-28 | — | 145 | Civil |
| `sentencia_t_325_2025` | Sentencia T-325 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-325-25.htm) | 2026-09-28 | — | 74 | Constitucional |
| `sentencia_t_350_2025` | Sentencia T-350 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-350-25.htm) | 2026-09-28 | — | 100 | Familia |
| `sentencia_t_429_2011` | Sentencia T-429 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/T-429-11.htm) | 2026-09-28 | — | 41 | Constitucional |
| `sentencia_t_445_2024` | Sentencia T-445 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-445-24.htm) | 2026-09-28 | — | 138 | Constitucional |
| `sentencia_t_488_2011` | Sentencia T-488 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/T-488-11.htm) | 2026-10-01 | — | 46 | Administrativo |
| `sentencia_t_4_2026` | Sentencia T-4 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-004-26.htm) | 2026-09-28 | — | 105 | Civil |
| `sentencia_t_67_2025` | Sentencia T-67 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-067-25.htm) | 2026-09-28 | — | 190 | Constitucional |
| `sentencia_t_6_1992` | Sentencia T-006 de 1992 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1992/t-006-92.htm) | 2026-10-01 | — | 127 | Administrativo |
| `sentencia_t_71_2016` | Sentencia T-71 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/T-071-16.htm) | 2026-09-28 | — | 89 | Familia |
| `sentencia_t_77_2025` | Sentencia T-77 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-077-25.htm) | 2026-09-28 | — | 74 | Familia |
| `sentencia_t_925_2014` | Sentencia T-925 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/T-925-14.htm) | 2026-09-28 | — | 33 | Constitucional |
| `sentencia_t_970_2014` | Sentencia T-970 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/T-970-14.htm) | 2026-09-28 | — | 106 | Constitucional |
| `acto_legislativo_1_2003` | Acto Legislativo 01 de 2003 (reforma politica) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=8620) | 2026-10-01 | 18 | 21 | Constitucional |
| `acto_legislativo_1_2005` | Acto Legislativo 01 de 2005 (adiciona el articulo 48 de la Constitucion, pensiones) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=17236) | 2026-10-01 | 2 | 6 | Constitucional, Laboral |
| `acto_legislativo_2_2015` | Acto Legislativo 02 de 2015 (equilibrio de poderes) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=66596) | 2026-10-01 | 26 | 34 | Constitucional |
| `acuerdo_1_2025` | Acuerdo 01 de 2025 de la Corte Constitucional (reparto de tutelas) | Normograma de la Cancilleria (compilacion) | [enlace](https://www.cancilleria.gov.co/normograma/compilacion/docs/acuerdo_cconstitucional_0001_2025.htm) | 2026-10-03 | 113 | 126 | Constitucional |
| `auto_supersociedades_2025_01_730337` | Auto 2025-01-730337 de la Superintendencia de Sociedades | Superintendencia de Sociedades (Baranda Virtual) | [enlace](https://servicios.supersociedades.gov.co/barandaVirtual/#!/app/radicaciones#verpdf) | 2026-10-01 | — | 5 | Comercial y sociedades |
| `codigo_civil` | Codigo Civil (Ley 57 de 1887) | Sistema Unico de Informacion de Tramites (SUIT) | [enlace](https://tramites1.suit.gov.co/registro-web/suit_descargar_archivo?A=115930) | 2026-09-29 | 2.680 | 2.856 | Civil, Familia |
| `codigo_comercio` | Codigo de Comercio (Decreto 410 de 1971) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=41102) | 2026-09-29 | 2.032 | 2.072 | Comercial y sociedades |
| `codigo_penal` | Codigo Penal (Ley 599 de 2000) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6388) | 2026-09-29 | 476 | 625 | Penal |
| `codigo_procedimiento_penal` | Codigo de Procedimiento Penal (Ley 906 de 2004) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=14787) | 2026-10-01 | 564 | 625 | Penal, Procesal |
| `codigo_procesal_trabajo` | Codigo Procesal del Trabajo y de la Seguridad Social (Decreto 2158 de 1948) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5259) | 2026-10-01 | 143 | 157 | Laboral, Procesal |
| `cpaca` | Codigo de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=41249) | 2026-09-29 | 309 | 369 | Administrativo, Procesal |
| `decision_andina_345` | Decision 345 de 1993 de la Comunidad Andina, Regimen Comun de Proteccion de los Derechos de los Obtentores de Variedades Vegetales | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC345.pdf) | 2026-10-02 | — | 13 | Mercados |
| `decision_andina_351` | Decision 351 de 1993 de la Comunidad Andina, Regimen Comun sobre Derecho de Autor y Derechos Conexos | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC351.pdf) | 2026-10-02 | — | 20 | Mercados |
| `decision_andina_391` | Decision 391 de 1996 de la Comunidad Andina, Regimen Comun sobre Acceso a los Recursos Geneticos | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC391.pdf) | 2026-10-02 | — | 24 | Mercados |
| `decision_andina_608` | Decision 608 de 2005 de la Comunidad Andina, Normas para la proteccion y promocion de la libre competencia | Comunidad Andina | [enlace](https://www.comunidadandina.org/StaticFiles/DocOf/DEC608.pdf) | 2026-10-02 | — | 18 | Mercados |
| `decreto_1069_2015` | Decreto 1069 de 2015 (Decreto Unico Reglamentario del Sector Justicia y del Derecho) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1069_2015.htm) | 2026-10-02 | 170 | 186 | Constitucional, Procesal |
| `decreto_1072_2015` | Decreto 1072 de 2015 (Decreto Unico Reglamentario del Sector Trabajo) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173) | 2026-10-01 | 1.412 | 1.563 | Laboral |
| `decreto_1074_2015` | Decreto 1074 de 2015 (Decreto Unico Reglamentario del Sector Comercio, Industria y Turismo) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608) | 2026-10-01 | 2.108 | 2.395 | Comercial y sociedades, Mercados |
| `decreto_1083_2015` | Decreto 1083 de 2015 (Decreto Unico Reglamentario del Sector de Funcion Publica) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=62866) | 2026-10-01 | 888 | 970 | Administrativo |
| `decreto_1165_2019` | Decreto 1165 de 2019 (regimen de aduanas) | Normograma CRC | [enlace](https://normograma.crcom.gov.co/crc/compilacion/docs/decreto_1165_2019.htm) | 2026-10-03 | 775 | 1.284 | Tributario |
| `decreto_1260_1970` | Decreto 1260 de 1970 (Estatuto del registro del estado civil de las personas) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1260_1970.htm) | 2026-10-02 | 124 | 125 | Civil, Familia |
| `decreto_1265_1970` | Decreto 1265 de 1970 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_1265_1970.htm) | 2026-10-03 | 22 | 23 | Administrativo, Procesal |
| `decreto_1295_1994` | Decreto 1295 de 1994 (Sistema General de Riesgos Profesionales) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1295_1994.htm) | 2026-10-02 | 98 | 106 | Laboral |
| `decreto_1333_1986` | Decreto 1333 de 1986 (Codigo de Regimen Municipal) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1333_1986.htm) | 2026-10-02 | 386 | 392 | Administrativo, Tributario |
| `decreto_1377_2013` | Decreto 1377 de 2013 (Reglamenta parcialmente la Ley 1581 de 2012 (datos personales)) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_1377_2013.htm) | 2026-10-02 | 28 | 31 | Mercados |
| `decreto_1382_2000` | Decreto 1382 de 2000 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1382_2000.htm) | 2026-10-03 | 6 | 8 | Constitucional |
| `decreto_1400_1970` | Decreto 1400 de 1970 (Codigo de Procedimiento Civil) | Funcion Publica - Gestor Normativo | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6923) | 2026-10-03 | 678 | 757 | Procesal |
| `decreto_1421_1993` | Decreto 1421 de 1993 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_1421_1993.html) | 2026-10-03 | 180 | 196 | Administrativo, Tributario |
| `decreto_1507_2014` | Decreto 1507 de 2014 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_1507_2014.htm) | 2026-10-03 | 6 | 183 | Laboral |
| `decreto_1625_2016` | Decreto 1625 de 2016 (Decreto Unico Reglamentario en materia tributaria) | Normograma de la DIAN | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/decreto_1625_2016.pdf) | 2026-10-01 | 1.545 | 3.549 | Tributario |
| `decreto_1818_1998` | Decreto 1818 de 1998 (Estatuto de los mecanismos alternativos de solucion de conflictos) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/decreto_1818_1998.htm) | 2026-10-02 | 232 | 237 | Procesal |
| `decreto_19_2012` | Decreto 19 de 2012 (antitramites) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=45322) | 2026-10-01 | 237 | 268 | Administrativo |
| `decreto_1_1984` | Decreto 01 de 1984 (Codigo Contencioso Administrativo anterior al CPACA) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6543) | 2026-10-01 | 245 | 283 | Administrativo, Procesal |
| `decreto_2106_2019` | Decreto 2106 de 2019 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2106_2019.html) | 2026-10-03 | 158 | 186 | Administrativo |
| `decreto_2150_1995` | Decreto 2150 de 1995 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2150_1995.html) | 2026-10-03 | 152 | 154 | Administrativo |
| `decreto_2158_1948` | Decreto 2158 de 1948 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_2158_1948.htm) | 2026-10-03 | 1 | 7 | Laboral, Procesal |
| `decreto_216_2021` | Decreto 216 de 2021 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/decreto_0216_2021.htm) | 2026-10-03 | 21 | 37 | Administrativo, Constitucional |
| `decreto_2351_1965` | Decreto 2351 de 1965 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_2351_1965.htm) | 2026-10-03 | 6 | 8 | Laboral |
| `decreto_2591_1991` | Decreto 2591 de 1991 (Reglamento de la accion de tutela) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_2591_1991.html) | 2026-10-02 | 55 | 56 | Constitucional, Procesal |
| `decreto_25_2014` | Decreto 25 de 2014 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0025_2014.html) | 2026-10-03 | 28 | 46 | Administrativo, Constitucional |
| `decreto_262_2000` | Decreto 262 de 2000 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0262_2000.html) | 2026-10-02 | 262 | 301 | Administrativo |
| `decreto_2820_1974` | Decreto 2820 de 1974 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_2820_1974.htm) | 2026-10-03 | 71 | 72 | Civil, Familia |
| `decreto_306_1992` | Decreto 306 de 1992 (Reglamenta el Decreto 2591 de 1991 (accion de tutela)) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0306_1992.htm) | 2026-10-02 | 10 | 11 | Procesal |
| `decreto_333_2021` | Decreto 333 de 2021 (Reglas de reparto de la accion de tutela) | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/decreto_0333_2021.htm) | 2026-10-02 | 4 | 13 | Procesal |
| `decreto_4062_2011` | Decreto 4062 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4062_2011.html) | 2026-10-03 | 34 | 44 | Administrativo |
| `decreto_4065_2011` | Decreto 4065 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_4065_2011.html) | 2026-10-03 | 26 | 35 | Administrativo, Constitucional |
| `decreto_472_2015` | Decreto 472 de 2015 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/decreto_0472_2015.htm) | 2026-10-03 | 15 | 19 | Laboral |
| `decreto_678_2020` | Decreto 678 de 2020 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0678_2020.html) | 2026-10-03 | 10 | 26 | Tributario |
| `decreto_735_2013` | Decreto 735 de 2013 (Efectividad de la garantia de bienes y servicios) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0735_2013.htm) | 2026-10-02 | 25 | 29 | Mercados |
| `decreto_758_1990` | Decreto 758 de 1990 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0758_1990.htm) | 2026-10-02 | 54 | 73 | Laboral |
| `decreto_806_2020` | Decreto 806 de 2020 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/decreto_0806_2020.html) | 2026-10-03 | 16 | 51 | Procesal |
| `decreto_886_2014` | Decreto 886 de 2014 (Registro Nacional de Bases de Datos) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/decreto_0886_2014.htm) | 2026-10-02 | 16 | 18 | Mercados |
| `decreto_920_2023` | Decreto Ley 920 de 2023 (regimen sancionatorio y de decomiso aduanero) | Normograma DIAN | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/decreto_0920_2023.htm) | 2026-10-03 | 155 | 301 | Tributario |
| `doctrina_arbanza_grupo_sociedades_2024` | Arbanza, Analisis comparativo de la extension del convenio arbitral a partes no signatarias: Pakistan, Francia y Colombia (2024) | Arbanza (doctrina) | [enlace](https://arbanza.com/analisis-comparativo-de-la-extension-del-convenio-arbitral-a-partes-no-signatarias-el-caso-de-pakistan-francia-y-colombia/) | 2026-10-01 | — | 14 | Comercial y sociedades |
| `doctrina_ompi_agotamiento_patentes_2012` | OMPI, Seminario Regional (Bogota, 2012), Tema 14: El agotamiento del derecho de patente | Organizacion Mundial de la Propiedad Intelectual (OMPI) | [enlace](https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf) | 2026-10-01 | — | 4 | Mercados |
| `doctrina_unbosque_agencia_comercial_cesantia_2024` | Trabajo de grado Universidad El Bosque - Contrato de agencia comercial y cesantia comercial (2024) | Repositorio Universidad El Bosque (REDCOL) | [enlace](https://redcol.minciencias.gov.co/Record/UNBOSQUE2_4d108bd5eb3d5ba57603313e68fd019b/) | 2026-10-03 | — | 19 | Comercial y sociedades |
| `ley_1004_2005` | Ley 1004 de 2005 (Regimen especial de zonas francas) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1004_2005.html) | 2026-10-02 | 13 | 14 | Tributario |
| `ley_100_1993` | Ley 100 de 1993 (Sistema de Seguridad Social Integral) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5248) | 2026-10-01 | 289 | 331 | Laboral |
| `ley_1032_2006` | Ley 1032 de 2006 (Delitos contra los derechos de autor y la propiedad industrial) | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_1032_2006.htm) | 2026-10-02 | 5 | 6 | Mercados, Penal |
| `ley_1060_2006` | Ley 1060 de 2006 (Impugnacion de la paternidad y la maternidad) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1060_2006.html) | 2026-10-02 | 14 | 15 | Familia |
| `ley_1066_2006` | Ley 1066 de 2006 (Normalizacion de la cartera publica (cobro coactivo)) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1066_2006.htm) | 2026-10-02 | 21 | 27 | Administrativo, Tributario |
| `ley_1111_2006` | Ley 1111 de 2006 (Reforma tributaria de 2006) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1111_2006.htm) | 2026-10-02 | 78 | 140 | Tributario |
| `ley_1122_2007` | Ley 1122 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1122_2007.html) | 2026-10-02 | 46 | 63 | Administrativo, Laboral |
| `ley_1123_2007` | Ley 1123 de 2007 (Codigo Disciplinario del Abogado) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1123_2007.htm) | 2026-10-02 | 112 | 117 | Administrativo, Procesal |
| `ley_1142_2007` | Ley 1142 de 2007 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1142_2007.html) | 2026-10-03 | 56 | 61 | Penal, Procesal |
| `ley_115_1994` | Ley 115 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0115_1994.html) | 2026-10-02 | 222 | 233 | Administrativo, Constitucional |
| `ley_1183_2008` | Ley 1183 de 2008 (Titulacion de la posesion de inmuebles urbanos de estratos 1 y 2) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1183_2008.htm) | 2026-10-02 | 22 | 23 | Civil |
| `ley_1221_2008` | Ley 1221 de 2008 (Teletrabajo) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1221_2008.htm) | 2026-10-02 | 9 | 14 | Laboral |
| `ley_1251_2008` | Ley 1251 de 2008 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1251_2008.html) | 2026-10-02 | 35 | 48 | Constitucional, Familia |
| `ley_1257_2008` | Ley 1257 de 2008 (Violencia y discriminacion contra las mujeres) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1257_2008.htm) | 2026-10-02 | 39 | 47 | Familia, Penal |
| `ley_1266_2008` | Ley 1266 de 2008 (Habeas data financiero) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1266_2008.htm) | 2026-10-02 | 22 | 37 | Mercados |
| `ley_1273_2009` | Ley 1273 de 2009 (Proteccion de la informacion y de los datos (delitos informaticos)) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1273_2009.htm) | 2026-10-02 | 5 | 15 | Mercados, Penal |
| `ley_1276_2009` | Ley 1276 de 2009 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1276_2009.html) | 2026-10-03 | 15 | 18 | Administrativo, Familia |
| `ley_1285_2009` | Ley 1285 de 2009 (Reforma a la Ley Estatutaria de la Administracion de Justicia) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1285_2009.htm) | 2026-10-02 | 28 | 31 | Procesal |
| `ley_12_1991` | Ley 12 de 1991 | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_0012_1991.htm) | 2026-10-02 | 54 | 72 | Constitucional, Familia |
| `ley_1306_2009` | Ley 1306 de 2009 (Proteccion de personas con discapacidad mental) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1306_2009.htm) | 2026-10-02 | 120 | 124 | Civil, Familia |
| `ley_130_1994` | Ley 130 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0130_1994.html) | 2026-10-03 | 54 | 59 | Administrativo, Constitucional |
| `ley_1314_2009` | Ley 1314 de 2009 (Normas de contabilidad e informacion financiera) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1314_2009.htm) | 2026-10-02 | 17 | 22 | Comercial y sociedades |
| `ley_1328_2009` | Ley 1328 de 2009 (Regimen de proteccion al consumidor financiero) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1328_2009.htm) | 2026-10-02 | 101 | 129 | Comercial y sociedades, Mercados |
| `ley_1341_2009` | Ley 1341 de 2009 (Tecnologias de la informacion y las comunicaciones) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1341_2009.htm) | 2026-10-02 | 73 | 126 | Mercados |
| `ley_1346_2009` | Ley 1346 de 2009 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1346_2009.html) | 2026-10-02 | 50 | 68 | Civil, Constitucional |
| `ley_134_1994` | Ley 134 de 1994 (Mecanismos de participacion ciudadana) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0134_1994.html) | 2026-10-02 | 109 | 110 | Constitucional |
| `ley_1361_2009` | Ley 1361 de 2009 (Proteccion integral a la familia) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1361_2009.htm) | 2026-10-02 | 14 | 17 | Familia |
| `ley_136_1994` | Ley 136 de 1994 (Organizacion y funcionamiento de los municipios) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0136_1994.htm) | 2026-10-02 | 203 | 232 | Administrativo |
| `ley_1395_2010` | Ley 1395 de 2010 (Descongestion judicial) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1395_2010.htm) | 2026-10-02 | 122 | 132 | Procesal |
| `ley_1403_2010` | Ley 1403 de 2010 (Remuneracion por comunicacion publica de obras audiovisuales (Ley Fanny Mikey)) | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_1403_2010.htm) | 2026-10-02 | 2 | 4 | Mercados |
| `ley_1429_2010` | Ley 1429 de 2010 (Formalizacion y generacion de empleo) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1429_2010.htm) | 2026-10-02 | 65 | 77 | Comercial y sociedades, Laboral |
| `ley_142_1994` | Ley 142 de 1994 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0142_1994.html) | 2026-10-02 | 189 | 239 | Administrativo, Comercial y sociedades |
| `ley_1430_2010` | Ley 1430 de 2010 (Control tributario y competitividad) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1430_2010.htm) | 2026-10-02 | 67 | 79 | Tributario |
| `ley_1438_2011` | Ley 1438 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1438_2011.html) | 2026-10-02 | 145 | 172 | Administrativo, Laboral |
| `ley_1448_2011` | Ley 1448 de 2011 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1448_2011.html) | 2026-10-02 | 208 | 280 | Administrativo, Constitucional, Penal |
| `ley_1453_2011` | Ley 1453 de 2011 (Seguridad ciudadana) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1453_2011.htm) | 2026-10-02 | 111 | 128 | Penal |
| `ley_1474_2011` | Ley 1474 de 2011 (Estatuto Anticorrupcion) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1474_2011.htm) | 2026-10-02 | 135 | 157 | Administrativo, Penal |
| `ley_1475_2011` | Ley 1475 de 2011 (Partidos y movimientos politicos) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1475_2011.htm) | 2026-10-02 | 55 | 68 | Constitucional |
| `ley_1496_2011` | Ley 1496 de 2011 (Igualdad salarial entre mujeres y hombres) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1496_2011.htm) | 2026-10-02 | 10 | 11 | Laboral |
| `ley_14_1983` | Ley 14 de 1983 (Fortalecimiento de los fiscos de las entidades territoriales) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0014_1983.htm) | 2026-10-02 | 90 | 91 | Tributario |
| `ley_1508_2012` | Ley 1508 de 2012 (Asociaciones Publico Privadas) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1508_2012.htm) | 2026-10-02 | 39 | 47 | Administrativo |
| `ley_1551_2012` | Ley 1551 de 2012 (Modernizacion de la organizacion de los municipios) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1551_2012.htm) | 2026-10-02 | 50 | 71 | Administrativo |
| `ley_1561_2012` | Ley 1561 de 2012 (Proceso verbal especial de titulacion de la posesion) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1561_2012.html) | 2026-10-02 | 27 | 33 | Civil, Procesal |
| `ley_1579_2012` | Ley 1579 de 2012 (Estatuto de registro de instrumentos publicos) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1579_2012.htm) | 2026-10-02 | 104 | 106 | Civil |
| `ley_1609_2013` | Ley 1609 de 2013 (Ley marco de aduanas) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1609_2013.htm) | 2026-10-02 | 7 | 8 | Tributario |
| `ley_1616_2013` | Ley 1616 de 2013 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1616_2013.html) | 2026-10-03 | 44 | 55 | Administrativo, Constitucional |
| `ley_1618_2013` | Ley 1618 de 2013 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1618_2013.html) | 2026-10-02 | 32 | 54 | Administrativo, Constitucional |
| `ley_1648_2013` | Ley 1648 de 2013 (Medidas de observancia de los derechos de propiedad industrial) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1648_2013.htm) | 2026-10-02 | 4 | 5 | Mercados |
| `ley_1676_2013` | Ley 1676 de 2013 (garantias mobiliarias) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=54297) | 2026-10-01 | 91 | 105 | Civil, Comercial y sociedades |
| `ley_16_1972` | Ley 16 de 1972 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0016_1972.htm) | 2026-10-02 | 82 | 84 | Constitucional, Penal |
| `ley_1708_2014` | Ley 1708 de 2014 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1708_2014.html) | 2026-10-03 | 217 | 253 | Penal, Procesal |
| `ley_1709_2014` | Ley 1709 de 2014 (Reforma al Codigo Penitenciario y Carcelario) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1709_2014.htm) | 2026-10-02 | 107 | 129 | Penal |
| `ley_1712_2014` | Ley 1712 de 2014 (Transparencia y acceso a la informacion publica) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1712_2014.html) | 2026-10-02 | 33 | 40 | Administrativo, Constitucional |
| `ley_1735_2014` | Ley 1735 de 2014 (Inclusion financiera) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1735_2014.htm) | 2026-10-02 | 15 | 18 | Comercial y sociedades |
| `ley_1739_2014` | Ley 1739 de 2014 (Reforma tributaria de 2014) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1739_2014.htm) | 2026-10-02 | 77 | 147 | Tributario |
| `ley_1751_2015` | Ley 1751 de 2015 (Estatutaria de salud) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1751_2015.html) | 2026-10-02 | 26 | 33 | Constitucional |
| `ley_1757_2015` | Ley 1757 de 2015 (Estatutaria de participacion democratica) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1757_2015.html) | 2026-10-02 | 112 | 121 | Constitucional |
| `ley_1761_2015` | Ley 1761 de 2015 (Feminicidio (Ley Rosa Elvira Cely)) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1761_2015.html) | 2026-10-02 | 13 | 14 | Penal |
| `ley_1774_2016` | Ley 1774 de 2016 (Animales como seres sintientes y maltrato animal) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1774_2016.html) | 2026-10-02 | 14 | 17 | Civil, Penal |
| `ley_1781_2016` | Ley 1781 de 2016 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1781_2016.html) | 2026-10-03 | 4 | 5 | Administrativo, Procesal |
| `ley_178_1994` | Ley 178 de 1994 (Aprueba el Convenio de Paris para la Proteccion de la Propiedad Industrial) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0178_1994.html) | 2026-10-02 | 30 | 64 | Mercados |
| `ley_181_1995` | Ley 181 de 1995 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0181_1995.html) | 2026-10-03 | 91 | 96 | Administrativo |
| `ley_1820_2016` | Ley 1820 de 2016 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1820_2016.html) | 2026-10-03 | 61 | 72 | Penal, Procesal |
| `ley_1822_2017` | Ley 1822 de 2017 (Licencia de maternidad) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1822_2017.htm) | 2026-10-02 | 3 | 6 | Laboral |
| `ley_1826_2017` | Ley 1826 de 2017 (Procedimiento penal abreviado y acusador privado) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1826_2017.html) | 2026-10-02 | 44 | 49 | Penal, Procesal |
| `ley_1846_2017` | Ley 1846 de 2017 (Jornada nocturna) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1846_2017.htm) | 2026-10-02 | 4 | 5 | Laboral |
| `ley_1878_2018` | Ley 1878 de 2018 (Proceso administrativo de restablecimiento de derechos) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1878_2018.html) | 2026-10-02 | 13 | 22 | Familia |
| `ley_1882_2018` | Ley 1882 de 2018 (Contratacion publica) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1882_2018.html) | 2026-10-02 | 21 | 29 | Administrativo |
| `ley_1901_2018` | Ley 1901 de 2018 (Sociedades Comerciales de Beneficio e Interes Colectivo (BIC)) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1901_2018.html) | 2026-10-02 | 10 | 14 | Comercial y sociedades |
| `ley_190_1995` | Ley 190 de 1995 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0190_1995.html) | 2026-10-03 | 85 | 86 | Administrativo, Penal |
| `ley_1915_2018` | Ley 1915 de 2018 (Derecho de autor y derechos conexos) | Normograma de la DIAN (compilacion Avance Juridico) | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/ley_1915_2018.htm) | 2026-10-02 | 37 | 45 | Mercados |
| `ley_1922_2018` | Ley 1922 de 2018 (Reglas de procedimiento de la JEP) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1922_2018.html) | 2026-10-02 | 76 | 94 | Penal, Procesal |
| `ley_1943_2018` | Ley 1943 de 2018 (Ley de financiamiento) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1943_2018.html) | 2026-10-02 | 122 | 204 | Tributario |
| `ley_1949_2019` | Ley 1949 de 2019 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_1949_2019.html) | 2026-10-02 | 12 | 22 | Administrativo, Laboral |
| `ley_1957_2019` | Ley 1957 de 2019 (Estatutaria de la Administracion de Justicia en la JEP) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_1957_2019.htm) | 2026-10-02 | 159 | 206 | Constitucional, Penal |
| `ley_1978_2019` | Ley 1978 de 2019 (Modernizacion del sector de las Tecnologias de la Informacion y las Comunicaciones) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_1978_2019.htm) | 2026-10-02 | 50 | 79 | Administrativo, Mercados |
| `ley_1996_2019` | Ley 1996 de 2019 (Ejercicio de la capacidad legal de las personas con discapacidad) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_1996_2019.htm) | 2026-10-02 | 63 | 72 | Civil, Familia |
| `ley_1_1976` | Ley 1 de 1976 (Divorcio en el matrimonio civil) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0001_1976.htm) | 2026-10-02 | 32 | 35 | Familia |
| `ley_2010_2019` | Ley 2010 de 2019 (Ley de Crecimiento Economico) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2010_2019.htm) | 2026-10-02 | 160 | 255 | Tributario |
| `ley_2044_2020` | Ley 2044 de 2020 (Saneamiento de predios ocupados por asentamientos humanos ilegales) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2044_2020.html) | 2026-10-02 | 33 | 38 | Civil |
| `ley_2055_2020` | Ley 2055 de 2020 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2055_2020.html) | 2026-10-02 | 41 | 100 | Constitucional, Familia |
| `ley_2069_2020` | Ley 2069 de 2020 (Ley de Emprendimiento) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2069_2020.htm) | 2026-10-02 | 84 | 108 | Comercial y sociedades |
| `ley_2080_2021` | Ley 2080 de 2021 (Reforma del CPACA) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2080_2021.htm) | 2026-10-02 | 87 | 108 | Administrativo, Procesal |
| `ley_2081_2021` | Ley 2081 de 2021 (Imprescriptibilidad de delitos sexuales contra menores) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2081_2021.html) | 2026-10-02 | 2 | 3 | Penal |
| `ley_2088_2021` | Ley 2088 de 2021 (Trabajo en casa) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2088_2021.htm) | 2026-10-02 | 16 | 17 | Laboral |
| `ley_2089_2021` | Ley 2089 de 2021 (Prohibicion del castigo fisico a ninos, ninas y adolescentes) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2089_2021.html) | 2026-10-02 | 7 | 9 | Familia |
| `ley_2094_2021` | Ley 2094 de 2021 (Reforma del Codigo General Disciplinario) | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_2094_2021.htm) | 2026-10-02 | 75 | 81 | Administrativo, Procesal |
| `ley_2097_2021` | Ley 2097 de 2021 (Registro de Deudores Alimentarios Morosos (REDAM)) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2097_2021.htm) | 2026-10-02 | 11 | 13 | Familia |
| `ley_2098_2021` | Ley 2098 de 2021 (Prision perpetua revisable) | Normograma de la DIAN (compilacion Avance Juridico) | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/ley_2098_2021.htm) | 2026-10-02 | 25 | 30 | Penal |
| `ley_2101_2021` | Ley 2101 de 2021 (Reduccion de la jornada laboral) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2101_2021.htm) | 2026-10-02 | 8 | 10 | Laboral |
| `ley_2121_2021` | Ley 2121 de 2021 (Trabajo remoto) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_2121_2021.htm) | 2026-10-02 | 27 | 31 | Laboral |
| `ley_2126_2021` | Ley 2126 de 2021 (Comisarias de familia) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2126_2021.html) | 2026-10-02 | 48 | 62 | Familia |
| `ley_2136_2021` | Ley 2136 de 2021 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2136_2021.html) | 2026-10-03 | 91 | 111 | Administrativo, Constitucional |
| `ley_2155_2021` | Ley 2155 de 2021 (Ley de Inversion Social) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2155_2021.htm) | 2026-10-02 | 65 | 108 | Tributario |
| `ley_2191_2022` | Ley 2191 de 2022 (Desconexion laboral) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2191_2022.htm) | 2026-10-02 | 8 | 9 | Laboral |
| `ley_2195_2022` | Ley 2195 de 2022 (Transparencia, prevencion y lucha contra la corrupcion) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2195_2022.htm) | 2026-10-02 | 69 | 81 | Administrativo |
| `ley_2197_2022` | Ley 2197 de 2022 (Seguridad ciudadana) | Normograma de la DIAN (compilacion Avance Juridico) | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/ley_2197_2022.htm) | 2026-10-02 | 22 | 78 | Penal |
| `ley_21_1982` | Ley 21 de 1982 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0021_1982.htm) | 2026-10-03 | 94 | 157 | Laboral |
| `ley_21_1991` | Ley 21 de 1991 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0021_1991.htm) | 2026-10-03 | 44 | 50 | Constitucional |
| `ley_2213_2022` | Ley 2213 de 2022 (Tecnologias de la informacion en las actuaciones judiciales) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_2213_2022.htm) | 2026-10-02 | 15 | 18 | Procesal |
| `ley_222_1995` | Ley 222 de 1995 (regimen de sociedades) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6739) | 2026-10-01 | 242 | 253 | Comercial y sociedades |
| `ley_223_1995` | Ley 223 de 1995 (Racionalizacion tributaria de 1995) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0223_1995.htm) | 2026-10-02 | 285 | 563 | Tributario |
| `ley_2277_2022` | Ley 2277 de 2022 (Reforma tributaria para la igualdad y la justicia social) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_2277_2022.htm) | 2026-10-02 | 96 | 147 | Tributario |
| `ley_2300_2023` | Ley 2300 de 2023 (Ley Dejen de Fregar (contacto de cobranza)) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_2300_2023.htm) | 2026-10-02 | 10 | 11 | Mercados |
| `ley_2365_2024` | Ley 2365 de 2024 (Acoso sexual en el ambito laboral) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_2365_2024.htm) | 2026-10-02 | 24 | 27 | Laboral |
| `ley_2381_2024` | Ley 2381 de 2024 (Reforma pensional (Sistema de Proteccion Social Integral para la Vejez)) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_2381_2024.htm) | 2026-10-02 | 95 | 140 | Laboral |
| `ley_23_1981` | Ley 23 de 1981 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_0023_1981.htm) | 2026-10-03 | 94 | 96 | Civil, Penal |
| `ley_23_1982` | Ley 23 de 1982 (Derechos de autor) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0023_1982.htm) | 2026-10-02 | 260 | 266 | Mercados |
| `ley_2445_2025` | Ley 2445 de 2025 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2445_2025.html) | 2026-10-03 | 45 | 78 | Procesal |
| `ley_2447_2025` | Ley 2447 de 2025 (Prohibicion del matrimonio infantil y las uniones tempranas) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_2447_2025.html) | 2026-10-02 | 21 | 24 | Familia |
| `ley_248_1995` | Ley 248 de 1995 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0248_1995.html) | 2026-10-02 | 25 | 31 | Constitucional, Penal |
| `ley_24_1992` | Ley 24 de 1992 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0024_1992.html) | 2026-10-03 | 41 | 42 | Administrativo, Constitucional |
| `ley_258_1996` | Ley 258 de 1996 (Afectacion a vivienda familiar) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0258_1996.html) | 2026-10-02 | 13 | 15 | Civil, Familia |
| `ley_25_1992` | Ley 25 de 1992 (Divorcio y efectos civiles del matrimonio religioso) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0025_1992.html) | 2026-10-02 | 15 | 16 | Familia |
| `ley_270_1996` | Ley 270 de 1996 (Estatutaria de la Administracion de Justicia) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0270_1996.htm) | 2026-10-02 | 210 | 264 | Constitucional, Procesal |
| `ley_294_1996` | Ley 294 de 1996 (Violencia intrafamiliar) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0294_1996.html) | 2026-10-02 | 30 | 33 | Familia, Penal |
| `ley_30_1992` | Ley 30 de 1992 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0030_1992.html) | 2026-10-02 | 144 | 154 | Administrativo |
| `ley_319_1996` | Ley 319 de 1996 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0319_1996.html) | 2026-10-03 | 22 | 30 | Constitucional, Laboral |
| `ley_361_1997` | Ley 361 de 1997 (Integracion social de las personas con limitacion (estabilidad reforzada)) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0361_1997.htm) | 2026-10-02 | 73 | 76 | Laboral |
| `ley_383_1997` | Ley 383 de 1997 (Normas para fortalecer la lucha contra la evasion y el contrabando) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0383_1997.htm) | 2026-10-02 | 74 | 78 | Tributario |
| `ley_387_1997` | Ley 387 de 1997 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0387_1997.html) | 2026-10-02 | 34 | 39 | Administrativo, Constitucional |
| `ley_388_1997` | Ley 388 de 1997 (Ley de desarrollo territorial) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0388_1997.htm) | 2026-10-02 | 138 | 179 | Administrativo, Civil |
| `ley_393_1997` | Ley 393 de 1997 (Accion de cumplimiento) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0393_1997.html) | 2026-10-02 | 32 | 33 | Administrativo, Constitucional |
| `ley_397_1997` | Ley 397 de 1997 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0397_1997.html) | 2026-10-03 | 83 | 110 | Administrativo, Constitucional |
| `ley_418_1997` | Ley 418 de 1997 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0418_1997.html) | 2026-10-03 | 131 | 158 | Administrativo, Penal |
| `ley_43_1990` | Ley 43 de 1990 (Profesion de contador publico) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0043_1990.htm) | 2026-10-02 | 75 | 81 | Comercial y sociedades |
| `ley_446_1998` | Ley 446 de 1998 (Descongestion, eficiencia y acceso a la justicia) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0446_1998.htm) | 2026-10-02 | 167 | 187 | Procesal |
| `ley_44_1990` | Ley 44 de 1990 (Impuesto predial unificado) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0044_1990.htm) | 2026-10-02 | 30 | 32 | Tributario |
| `ley_44_1993` | Ley 44 de 1993 (Derechos de autor (modificacion de la Ley 23 de 1982)) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0044_1993.htm) | 2026-10-02 | 70 | 74 | Mercados |
| `ley_45_1936` | Ley 45 de 1936 (Filiacion natural) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0045_1936.htm) | 2026-10-02 | 30 | 32 | Civil, Familia |
| `ley_463_1998` | Ley 463 de 1998 (Aprueba el Tratado de Cooperacion en materia de Patentes (PCT)) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0463_1998.html) | 2026-10-02 | 69 | 308 | Mercados |
| `ley_472_1998` | Ley 472 de 1998, acciones populares y de grupo | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=188) | 2026-09-29 | 86 | 93 | Administrativo, Constitucional |
| `ley_489_1998` | Ley 489 de 1998 (Organizacion y funcionamiento de las entidades del orden nacional) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0489_1998.html) | 2026-10-02 | 121 | 125 | Administrativo |
| `ley_49_1990` | Ley 49 de 1990 (Reforma tributaria de 1990) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0049_1990.htm) | 2026-10-02 | 83 | 95 | Tributario |
| `ley_51_1981` | Ley 51 de 1981 | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0051_1981.htm) | 2026-10-02 | 25 | 32 | Constitucional |
| `ley_550_1999` | Ley 550 de 1999 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0550_1999.html) | 2026-10-03 | 38 | 48 | Comercial y sociedades |
| `ley_565_2000` | Ley 565 de 2000 (Aprueba el Tratado de la OMPI sobre Derecho de Autor (WCT)) | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_0565_2000.htm) | 2026-10-02 | 25 | 54 | Mercados |
| `ley_575_2000` | Ley 575 de 2000 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0575_2000.html) | 2026-10-02 | 14 | 17 | Familia, Penal |
| `ley_57_1887` | Ley 57 de 1887 (Adopta el Codigo Civil de la Nacion) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0057_1887.htm) | 2026-10-02 | 337 | 338 | Civil |
| `ley_590_2000` | Ley 590 de 2000 (Micro, pequenas y medianas empresas) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0590_2000.htm) | 2026-10-02 | 47 | 49 | Comercial y sociedades |
| `ley_5_1992` | Ley 5 de 1992 (Reglamento del Congreso) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0005_1992.htm) | 2026-10-02 | 392 | 510 | Constitucional |
| `ley_60_1993` | Ley 60 de 1993 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0060_1993.html) | 2026-10-03 | 43 | 75 | Administrativo, Tributario |
| `ley_610_2000` | Ley 610 de 2000 (Proceso de responsabilidad fiscal) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0610_2000.html) | 2026-10-02 | 68 | 69 | Administrativo |
| `ley_617_2000` | Ley 617 de 2000 (Racionalizacion del gasto publico territorial) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0617_2000.htm) | 2026-10-02 | 96 | 110 | Administrativo |
| `ley_633_2000` | Ley 633 de 2000 (Reforma tributaria de 2000) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0633_2000.htm) | 2026-10-02 | 146 | 168 | Tributario |
| `ley_65_1993` | Ley 65 de 1993 (Codigo Penitenciario y Carcelario) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0065_1993.htm) | 2026-10-02 | 174 | 213 | Penal |
| `ley_675_2001` | Ley 675 de 2001 (Regimen de propiedad horizontal) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0675_2001.htm) | 2026-10-02 | 87 | 94 | Civil |
| `ley_70_1993` | Ley 70 de 1993 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0070_1993.html) | 2026-10-03 | 68 | 71 | Administrativo, Constitucional |
| `ley_712_2001` | Ley 712 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0712_2001.html) | 2026-10-02 | 55 | 68 | Laboral, Procesal |
| `ley_715_2001` | Ley 715 de 2001 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0715_2001.html) | 2026-10-02 | 113 | 157 | Administrativo, Tributario |
| `ley_734_2002` | Ley 734 de 2002 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0734_2002.html) | 2026-10-02 | 221 | 246 | Administrativo |
| `ley_74_1968` | Ley 74 de 1968 | Normograma de la Cancilleria (compilacion Avance Juridico) | [enlace](https://www.cancilleria.gov.co/sites/default/files/Normograma/docs/ley_0074_1968.htm) | 2026-10-02 | 53 | 165 | Constitucional, Penal |
| `ley_776_2002` | Ley 776 de 2002 (Prestaciones del Sistema General de Riesgos Profesionales) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/compilacion/docs/ley_0776_2002.htm) | 2026-10-02 | 23 | 26 | Laboral |
| `ley_788_2002` | Ley 788 de 2002 (Reforma tributaria de 2002) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0788_2002.htm) | 2026-10-02 | 118 | 143 | Tributario |
| `ley_789_2002` | Ley 789 de 2002 (Reforma laboral de 2002) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0789_2002.htm) | 2026-10-02 | 52 | 94 | Laboral |
| `ley_791_2002` | Ley 791 de 2002 (Reduccion de terminos de prescripcion) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0791_2002.htm) | 2026-10-02 | 13 | 14 | Civil |
| `ley_794_2003` | Ley 794 de 2003 (Reforma del Codigo de Procedimiento Civil) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0794_2003.htm) | 2026-10-02 | 70 | 98 | Procesal |
| `ley_797_2003` | Ley 797 de 2003 (Reforma del Sistema General de Pensiones) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0797_2003.htm) | 2026-10-02 | 25 | 36 | Laboral |
| `ley_860_2003` | Ley 860 de 2003 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0860_2003.html) | 2026-10-02 | 5 | 10 | Laboral |
| `ley_863_2003` | Ley 863 de 2003 (Reforma tributaria de 2003) | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0863_2003.htm) | 2026-10-02 | 69 | 131 | Tributario |
| `ley_890_2004` | Ley 890 de 2004 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0890_2004.html) | 2026-10-03 | 15 | 17 | Penal |
| `ley_909_2004` | Ley 909 de 2004 (Empleo publico y carrera administrativa) | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0909_2004.html) | 2026-10-02 | 58 | 79 | Administrativo, Laboral |
| `ley_90_1946` | Ley 90 de 1946 | Normograma de Colpensiones (compilacion Avance Juridico) | [enlace](https://normativa.colpensiones.gov.co/colpens/docs/ley_0090_1946.htm) | 2026-10-03 | 84 | 125 | Laboral |
| `ley_95_1890` | Ley 95 de 1890 (Reformas civiles) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0095_1890.htm) | 2026-10-02 | 42 | 43 | Civil |
| `ley_962_2005` | Ley 962 de 2005 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0962_2005.html) | 2026-10-02 | 86 | 97 | Administrativo |
| `ley_975_2005` | Ley 975 de 2005 (Justicia y Paz) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0975_2005.htm) | 2026-10-02 | 72 | 102 | Penal |
| `ley_996_2005` | Ley 996 de 2005 (Ley de Garantias Electorales) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0996_2005.htm) | 2026-10-02 | 42 | 47 | Constitucional |
| `ley_99_1993` | Ley 99 de 1993 | Secretaria del Senado | [enlace](http://www.secretariasenado.gov.co/senado/basedoc/ley_0099_1993.html) | 2026-10-02 | 118 | 171 | Administrativo |
| `ley_9_1989` | Ley 9 de 1989 (Ley de reforma urbana) | Normograma de la CRA (compilacion Avance Juridico) | [enlace](https://normas.cra.gov.co/gestor/docs/ley_0009_1989.htm) | 2026-10-02 | 128 | 135 | Administrativo, Civil |
| `providencia_csj_civil_2001_00847_2011` | Corte Suprema de Justicia, Sala de Casacion Civil, sentencia sustitutiva del 19 de octubre de 2011 (exp. 11001-3103-032-2001-00847-01) | Ambito Juridico (texto de la providencia de la Corte Suprema de Justicia) | [enlace](https://ambitojuridico.com/sites/default/files/BancoMedios/Archivos/sent.%2011001310303220010084701-11.doc) | 2026-10-03 | — | 52 | Comercial y sociedades |
| `resolucion_1036_2021` | Resolucion 1036 de 2021 (Ministerio de Ambiente; relleno sanitario El Carrasco) | Ministerio de Ambiente y Desarrollo Sostenible | [enlace](https://www.minambiente.gov.co/wp-content/uploads/2021/10/Resolucion-1036-de-2021.pdf) | 2026-10-03 | 8 | 41 | Administrativo |
| `resolucion_368_2014` | Resolucion 368 de 2014 (Ministerio de Ambiente; relleno sanitario El Carrasco) | Ministerio de Ambiente y Desarrollo Sostenible | [enlace](https://www.minambiente.gov.co/) | 2026-10-03 | 2 | 34 | Administrativo |
| `sentencia_c_1011_2008` | Sentencia C-1011 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/C-1011-08.htm) | 2026-10-02 | — | 623 | Constitucional, Mercados |
| `sentencia_c_1024_2004` | Sentencia C-1024 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-1024-04.htm) | 2026-10-02 | — | 105 | Constitucional, Laboral |
| `sentencia_c_1035_2008` | Sentencia C-1035 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/C-1035-08.htm) | 2026-10-02 | — | 83 | Constitucional, Laboral |
| `sentencia_c_1040_2005` | Sentencia C-1040 de 2005 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2005/C-1040-05.htm) | 2026-10-02 | — | 1.395 | Constitucional |
| `sentencia_c_1064_2001` | Sentencia C-1064 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-1064-01.htm) | 2026-10-02 | — | 192 | Constitucional |
| `sentencia_c_1094_2003` | Sentencia C-1094 de 2003 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2003/C-1094-03.htm) | 2026-10-02 | — | 53 | Constitucional, Laboral |
| `sentencia_c_1153_2005` | Sentencia C-1153 de 2005 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2005/C-1153-05.htm) | 2026-10-02 | — | 586 | Constitucional |
| `sentencia_c_141_2010` | Sentencia C-141 de 2010 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2010/C-141-10.htm) | 2026-10-02 | — | 965 | Constitucional |
| `sentencia_c_146_2021` | Sentencia C-146 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-146-21.htm) | 2026-10-02 | — | 170 | Administrativo, Constitucional, Procesal |
| `sentencia_c_148_2025` | Sentencia C-148 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-148-25.htm) | 2026-10-03 | — | 645 | Tributario |
| `sentencia_c_150_2015` | Sentencia C-150 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-150-15.htm) | 2026-10-02 | — | 770 | Constitucional |
| `sentencia_c_180_1994` | Sentencia C-180 de 1994 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1994/C-180-94.htm) | 2026-10-02 | — | 223 | Constitucional |
| `sentencia_c_221_1994` | Sentencia C-221 de 1994 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1994/C-221-94.htm) | 2026-10-02 | — | 84 | Constitucional, Penal |
| `sentencia_c_251_1996` | Sentencia C-251 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-251-96.htm) | 2026-10-02 | — | 34 | Administrativo, Civil, Constitucional |
| `sentencia_c_264_2026` | Sentencia C-264 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/C-264-26.htm) | 2026-10-02 | — | 398 | Constitucional, Laboral |
| `sentencia_c_294_2021` | Sentencia C-294 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/C-294-21.htm) | 2026-10-02 | — | 463 | Constitucional, Penal |
| `sentencia_c_29_2009` | Sentencia C-029 de 2009 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2009/C-029-09.htm) | 2026-10-02 | — | 303 | Constitucional, Familia |
| `sentencia_c_300_2012` | Sentencia C-300 de 2012 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2012/C-300-12.htm) | 2026-10-02 | — | 134 | Administrativo, Constitucional |
| `sentencia_c_30_2023` | Sentencia C-030 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/C-030-23.htm) | 2026-10-02 | — | 336 | Administrativo, Constitucional, Procesal |
| `sentencia_c_313_2014` | Sentencia C-313 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/C-313-14.htm) | 2026-10-02 | — | 985 | Constitucional |
| `sentencia_c_317_2025` | Sentencia C-317 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/C-317-25.htm) | 2026-10-03 | — | 84 | Constitucional |
| `sentencia_c_319_2006` | Sentencia C-319 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/C-319-06.htm) | 2026-10-02 | — | 119 | Constitucional, Penal |
| `sentencia_c_328_2015` | Sentencia C-328 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-328-15.htm) | 2026-10-02 | — | 67 | Constitucional, Procesal |
| `sentencia_c_348_2004` | Sentencia C-348 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/C-348-04.htm) | 2026-10-02 | — | 37 | Administrativo, Constitucional |
| `sentencia_c_370_2006` | Sentencia C-370 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/C-370-06.htm) | 2026-10-02 | — | 876 | Constitucional, Penal |
| `sentencia_c_37_1996` | Sentencia C-037 de 1996 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1996/C-037-96.htm) | 2026-10-02 | — | 602 | Constitucional, Procesal |
| `sentencia_c_448_2020` | Sentencia C-448 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/C-448-20.htm) | 2026-10-03 | — | 152 | Tributario |
| `sentencia_c_44_2015` | Sentencia C-044 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-044-15.htm) | 2026-10-02 | — | 163 | Constitucional |
| `sentencia_c_458_2015` | Sentencia C-458 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-458-15.htm) | 2026-10-02 | — | 154 | Constitucional, Laboral |
| `sentencia_c_465_2008` | Sentencia C-465 de 2008 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2008/C-465-08.htm) | 2026-10-03 | — | 58 | Laboral |
| `sentencia_c_467_2016` | Sentencia C-467 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/C-467-16.htm) | 2026-10-02 | — | 146 | Civil, Constitucional, Penal |
| `sentencia_c_468_2024` | Sentencia C-468 de 2024 | Regimen Legal de Bogota (Secretaria Juridica Distrital) | [enlace](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=172537) | 2026-10-01 | — | 65 | Constitucional |
| `sentencia_c_481_2019` | Sentencia C-481 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/C-481-19.htm) | 2026-10-02 | — | 281 | Constitucional, Tributario |
| `sentencia_c_490_2011` | Sentencia C-490 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-490-11.htm) | 2026-10-02 | — | 960 | Constitucional |
| `sentencia_c_517_2024` | Sentencia C-517 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/C-517-24.htm) | 2026-10-03 | — | 110 | Constitucional |
| `sentencia_c_531_2000` | Sentencia C-531 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-531-00.htm) | 2026-10-02 | — | 34 | Constitucional, Laboral |
| `sentencia_c_539_2011` | Sentencia C-539 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-539-11.htm) | 2026-10-02 | — | 113 | Administrativo, Constitucional |
| `sentencia_c_540_2001` | Sentencia C-540 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-540-01.htm) | 2026-10-02 | — | 259 | Administrativo, Constitucional |
| `sentencia_c_543_1992` | Sentencia C-543 de 1992 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1992/C-543-92.htm) | 2026-10-02 | — | 170 | Constitucional, Procesal |
| `sentencia_c_551_2003` | Sentencia C-551 de 2003 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2003/C-551-03.htm) | 2026-10-02 | — | 581 | Constitucional |
| `sentencia_c_575_2006` | Sentencia C-575 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/C-575-06.htm) | 2026-10-02 | — | 514 | Constitucional, Penal |
| `sentencia_c_577_2011` | Sentencia C-577 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-577-11.htm) | 2026-10-02 | — | 545 | Constitucional, Familia |
| `sentencia_c_579_2013` | Sentencia C-579 de 2013 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2013/C-579-13.htm) | 2026-10-02 | — | 715 | Constitucional, Penal |
| `sentencia_c_581_2001` | Sentencia C-581 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-581-01.htm) | 2026-10-03 | — | 48 | Penal |
| `sentencia_c_590_2005` | Sentencia C-590 de 2005 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2005/C-590-05.htm) | 2026-10-02 | — | 77 | Constitucional, Procesal |
| `sentencia_c_5_2017` | Sentencia C-005 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-005-17.htm) | 2026-10-02 | — | 130 | Constitucional, Laboral |
| `sentencia_c_634_2011` | Sentencia C-634 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-634-11.htm) | 2026-10-02 | — | 83 | Administrativo, Constitucional |
| `sentencia_c_660_2000` | Sentencia C-660 de 2000 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2000/C-660-00.htm) | 2026-10-02 | — | 24 | Constitucional, Familia |
| `sentencia_c_674_2017` | Sentencia C-674 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/C-674-17.htm) | 2026-10-02 | — | 1.241 | Constitucional, Penal |
| `sentencia_c_694_2015` | Sentencia C-694 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-694-15.htm) | 2026-10-02 | — | 600 | Constitucional, Penal |
| `sentencia_c_71_2015` | Sentencia C-071 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/C-071-15.htm) | 2026-10-02 | — | 352 | Constitucional, Familia |
| `sentencia_c_75_2007` | Sentencia C-075 de 2007 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2007/C-075-07.htm) | 2026-10-02 | — | 161 | Constitucional, Familia |
| `sentencia_c_80_2018` | Sentencia C-080 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/C-080-18.htm) | 2026-10-02 | — | 1.849 | Constitucional, Penal |
| `sentencia_c_821_2005` | Sentencia C-821 de 2005 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2005/C-821-05.htm) | 2026-10-02 | — | 66 | Constitucional, Familia |
| `sentencia_c_824_2011` | Sentencia C-824 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-824-11.htm) | 2026-10-02 | — | 75 | Constitucional, Laboral |
| `sentencia_c_836_2001` | Sentencia C-836 de 2001 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2001/C-836-01.htm) | 2026-10-02 | — | 115 | Constitucional, Procesal |
| `sentencia_c_878_2011` | Sentencia C-878 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/C-878-11.htm) | 2026-10-03 | — | 47 | Tributario |
| `sentencia_c_886_2010` | Sentencia C-886 de 2010 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2010/C-886-10.htm) | 2026-10-02 | — | 142 | Constitucional, Familia, Penal |
| `sentencia_c_957_1999` | Sentencia C-957 de 1999 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1999/C-957-99.htm) | 2026-10-02 | — | 33 | Administrativo, Constitucional |
| `sentencia_ce_suj_4_005_2020` | Consejo de Estado, Seccion Cuarta, Sentencia de unificacion 2020CE-SUJ-4-005 de 2020 (exp. 21329) | Normograma de la DIAN | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/25000-23-37-000-2013-00443-01(21329)ce-suj-4-005.pdf) | 2026-10-01 | — | 64 | Tributario |
| `sentencia_sc_10291_2017` | Sentencia SC-10291 de 2017 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 26 | Civil |
| `sentencia_sc_435_2024` | Sentencia SC-435 de 2024 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 46 | Comercial y sociedades |
| `sentencia_sc_5288_2021` | Sentencia SC-5288 de 2021 | Corte Suprema de Justicia | [enlace](https://www.cortesuprema.gov.co/corte/wp-content/uploads/not/civil21/prov/11001-02-03-000-2021-00766-00.pdf) | 2026-10-01 | — | 82 | Comercial y sociedades |
| `sentencia_sl_3871_2021` | Sentencia SL3871 de 2021 | Relatoria de la Corte Suprema de Justicia - Sala de Casacion Laboral | [enlace](https://www.cortesuprema.gov.co/corte/wp-content/uploads/relatorias/la/bnov2021/SL3871-2021.pdf) | 2026-10-03 | — | 18 | Laboral |
| `sentencia_su_103_2022` | Sentencia SU-103 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU103-22.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_su_107_2024` | Sentencia SU-107 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU107-24.htm) | 2026-10-02 | — | 683 | Constitucional |
| `sentencia_su_108_2020` | Sentencia SU-108 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU108-20.htm) | 2026-10-02 | — | 93 | Constitucional |
| `sentencia_su_109_2022` | Sentencia SU-109 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU109-22.htm) | 2026-10-02 | — | 216 | Constitucional |
| `sentencia_su_111_2020` | Sentencia SU-111 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU111-20.htm) | 2026-10-02 | — | 225 | Constitucional |
| `sentencia_su_114_2023` | Sentencia SU-114 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU114-23.htm) | 2026-10-02 | — | 109 | Constitucional |
| `sentencia_su_118_2026` | Sentencia SU-118 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU118-26.htm) | 2026-10-02 | — | 135 | Constitucional |
| `sentencia_su_121_2022` | Sentencia SU-121 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU121-22.htm) | 2026-10-02 | — | 286 | Constitucional |
| `sentencia_su_122_2022` | Sentencia SU-122 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU122-22.htm) | 2026-10-02 | — | 724 | Constitucional |
| `sentencia_su_123_2018` | Sentencia SU-123 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/SU123-18.htm) | 2026-10-02 | — | 220 | Constitucional |
| `sentencia_su_126_2022` | Sentencia SU-126 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU126-22.htm) | 2026-10-02 | — | 158 | Constitucional |
| `sentencia_su_126_2025` | Sentencia SU-126 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU126-25.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_su_128_2021` | Sentencia SU-128 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU128-21.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_su_128_2024` | Sentencia SU-128 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU128-24.htm) | 2026-10-02 | — | 234 | Constitucional |
| `sentencia_su_129_2021` | Sentencia SU-129 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU129-21.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_su_12_2020` | Sentencia SU-012 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU012-20.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_su_134_2022` | Sentencia SU-134 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU134-22.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_su_136_2022` | Sentencia SU-136 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU136-22.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_su_138_2021` | Sentencia SU-138 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU138-21.htm) | 2026-10-02 | — | 98 | Constitucional |
| `sentencia_su_139_2021` | Sentencia SU-139 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU139-21.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_su_140_2019` | Sentencia SU-140 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/SU140-19.htm) | 2026-10-03 | — | 411 | Laboral |
| `sentencia_su_140_2026` | Sentencia SU-140 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU140-26.htm) | 2026-10-02 | — | 138 | Constitucional |
| `sentencia_su_141_2020` | Sentencia SU-141 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU141-20.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_su_143_2020` | Sentencia SU-143 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU143-20.htm) | 2026-10-02 | — | 165 | Constitucional |
| `sentencia_su_143_2026` | Sentencia SU-143 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU143-26.htm) | 2026-10-02 | — | 159 | Constitucional |
| `sentencia_su_144_2026` | Sentencia SU-144 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU144-26.htm) | 2026-10-02 | — | 108 | Constitucional |
| `sentencia_su_146_2020` | Sentencia SU-146 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU146-20.htm) | 2026-10-02 | — | 205 | Constitucional |
| `sentencia_su_14_2020` | Sentencia SU-014 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU014-20.htm) | 2026-10-02 | — | 136 | Constitucional |
| `sentencia_su_150_2021` | Sentencia SU-150 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU150-21.htm) | 2026-10-02 | — | 604 | Constitucional |
| `sentencia_su_155_2023` | Sentencia SU-155 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU155-23.htm) | 2026-10-02 | — | 104 | Constitucional |
| `sentencia_su_157_2022` | Sentencia SU-157 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU157-22.htm) | 2026-10-02 | — | 338 | Constitucional |
| `sentencia_su_163_2023` | Sentencia SU-163 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU163-23.htm) | 2026-10-02 | — | 1 | Constitucional |
| `sentencia_su_164_2026` | Sentencia SU-164 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU164-26.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_su_165_2022` | Sentencia SU-165 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU165-22.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_su_167_2023` | Sentencia SU-167 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU167-23.htm) | 2026-10-02 | — | 168 | Constitucional |
| `sentencia_su_167_2024` | Sentencia SU-167 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU167-24.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_su_168_2023` | Sentencia SU-168 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU168-23.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_su_169_2024` | Sentencia SU-169 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU169-24.htm) | 2026-10-02 | — | 175 | Constitucional |
| `sentencia_su_16_2020` | Sentencia SU-016 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/su016-20.htm) | 2026-10-01 | — | 321 | Constitucional |
| `sentencia_su_16_2021` | Sentencia SU-016 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU016-21.htm) | 2026-10-02 | — | 331 | Constitucional |
| `sentencia_su_16_2024` | Sentencia SU-016 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU016-24.htm) | 2026-10-02 | — | 131 | Constitucional |
| `sentencia_su_16_2026` | Sentencia SU-016 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU016-26.htm) | 2026-10-02 | — | 194 | Constitucional |
| `sentencia_su_171_2026` | Sentencia SU-171 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU171-26.htm) | 2026-10-02 | — | 142 | Constitucional |
| `sentencia_su_174_2021` | Sentencia SU-174 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU174-21.htm) | 2026-10-02 | — | 102 | Constitucional |
| `sentencia_su_174_2025` | Sentencia SU-174 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU174-25.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_su_175_2025` | Sentencia SU-175 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU175-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_su_176_2025` | Sentencia SU-176 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU176-25.htm) | 2026-10-02 | — | 510 | Constitucional |
| `sentencia_su_179_2021` | Sentencia SU-179 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU179-21.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_su_17_2024` | Sentencia SU-017 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU017-24.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_su_180_2022` | Sentencia SU-180 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU180-22.htm) | 2026-10-02 | — | 341 | Constitucional |
| `sentencia_su_184_2025` | Sentencia SU-184 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU184-25.htm) | 2026-10-02 | — | 1.284 | Constitucional |
| `sentencia_su_18_2024` | Sentencia SU-018 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU018-24.htm) | 2026-10-02 | — | 255 | Constitucional |
| `sentencia_su_18_2025` | Sentencia SU-018 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU018-25.htm) | 2026-10-02 | — | 199 | Constitucional |
| `sentencia_su_18_2026` | Sentencia SU-018 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU018-26.htm) | 2026-10-02 | — | 282 | Constitucional |
| `sentencia_su_190_2021` | Sentencia SU-190 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU190-21.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_su_191_2022` | Sentencia SU-191 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU191-22.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_su_191_2025` | Sentencia SU-191 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU191-25.htm) | 2026-10-02 | — | 277 | Constitucional |
| `sentencia_su_196_2023` | Sentencia SU-196 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU196-23.htm) | 2026-10-02 | — | 237 | Constitucional |
| `sentencia_su_196_2025` | Sentencia SU-196 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU196-25.htm) | 2026-10-02 | — | 143 | Constitucional |
| `sentencia_su_201_2021` | Sentencia SU-201 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU201-21.htm) | 2026-10-02 | — | 140 | Constitucional |
| `sentencia_su_204_2025` | Sentencia SU-204 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU204-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_su_205_2025` | Sentencia SU-205 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU205-25.htm) | 2026-10-02 | — | 155 | Constitucional |
| `sentencia_su_209_2021` | Sentencia SU-209 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU209-21.htm) | 2026-10-02 | — | 115 | Constitucional |
| `sentencia_su_20_2020` | Sentencia SU-020 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU020-20.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_su_20_2022` | Sentencia SU-020 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU020-22.htm) | 2026-10-02 | — | 1.157 | Constitucional |
| `sentencia_su_212_2023` | Sentencia SU-212 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU212-23.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_su_213_2021` | Sentencia SU-213 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU213-21.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_su_213_2022` | Sentencia SU-213 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU213-22.htm) | 2026-10-02 | — | 226 | Constitucional |
| `sentencia_su_213_2023` | Sentencia SU-213 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU213-23.htm) | 2026-10-02 | — | 136 | Constitucional |
| `sentencia_su_213_2024` | Sentencia SU-213 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU213-24.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_su_214_2022` | Sentencia SU-214 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU214-22.htm) | 2026-10-02 | — | 229 | Constitucional |
| `sentencia_su_214_2023` | Sentencia SU-214 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU214-23.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_su_215_2022` | Sentencia SU-215 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU215-22.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_su_216_2022` | Sentencia SU-216 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU216-22.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_218_2024` | Sentencia SU-218 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU218-24.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_su_220_2024` | Sentencia SU-220 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU220-24.htm) | 2026-10-02 | — | 107 | Constitucional |
| `sentencia_su_221_2024` | Sentencia SU-221 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU221-24.htm) | 2026-10-02 | — | 107 | Constitucional |
| `sentencia_su_227_2021` | Sentencia SU-227 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU227-21.htm) | 2026-10-02 | — | 132 | Constitucional |
| `sentencia_su_228_2021` | Sentencia SU-228 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU228-21.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_su_22_2023` | Sentencia SU-022 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU022-23.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_su_236_2022` | Sentencia SU-236 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU236-22.htm) | 2026-10-02 | — | 260 | Constitucional |
| `sentencia_su_237_2019` | Sentencia SU-237 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/SU237-19.htm) | 2026-10-03 | — | 65 | Administrativo |
| `sentencia_su_239_2024` | Sentencia SU-239 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU239-24.htm) | 2026-10-02 | — | 166 | Constitucional |
| `sentencia_su_241_2024` | Sentencia SU-241 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU241-24.htm) | 2026-10-02 | — | 170 | Constitucional |
| `sentencia_su_244_2021` | Sentencia SU-244 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU244-21.htm) | 2026-10-02 | — | 406 | Constitucional |
| `sentencia_su_245_2021` | Sentencia SU-245 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU245-21.htm) | 2026-10-02 | — | 199 | Constitucional |
| `sentencia_su_245_2025` | Sentencia SU-245 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU245-25.htm) | 2026-10-02 | — | 143 | Constitucional |
| `sentencia_su_254_2026` | Sentencia SU-254 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU254-26.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_su_257_2021` | Sentencia SU-257 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU257-21.htm) | 2026-10-02 | — | 387 | Constitucional |
| `sentencia_su_258_2021` | Sentencia SU-258 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU258-21.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_su_259_2021` | Sentencia SU-259 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU259-21.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_su_260_2021` | Sentencia SU-260 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU260-21.htm) | 2026-10-02 | — | 45 | Constitucional |
| `sentencia_su_261_2021` | Sentencia SU-261 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU261-21.htm) | 2026-10-02 | — | 132 | Constitucional |
| `sentencia_su_269_2023` | Sentencia SU-269 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU269-23.htm) | 2026-10-02 | — | 132 | Constitucional |
| `sentencia_su_26_2021` | Sentencia SU-026 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU026-21.htm) | 2026-10-02 | — | 43 | Constitucional |
| `sentencia_su_272_2021` | Sentencia SU-272 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU272-21.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_su_273_2022` | Sentencia SU-273 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU273-22.htm) | 2026-10-02 | — | 153 | Constitucional |
| `sentencia_su_274_2025` | Sentencia SU-274 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU274-25.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_su_275_2025` | Sentencia SU-275 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU275-25.htm) | 2026-10-02 | — | 261 | Constitucional |
| `sentencia_su_277_2025` | Sentencia SU-277 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/su277-25.htm) | 2026-10-01 | — | 173 | Administrativo |
| `sentencia_su_279_2024` | Sentencia SU-279 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU279-24.htm) | 2026-10-02 | — | 234 | Constitucional |
| `sentencia_su_282_2023` | Sentencia SU-282 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU282-23.htm) | 2026-10-02 | — | 108 | Constitucional |
| `sentencia_su_286_2021` | Sentencia SU-286 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU286-21.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_su_287_2024` | Sentencia SU-287 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU287-24.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_su_288_2015` | Sentencia SU-288 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU288-15.htm) | 2026-10-03 | — | 80 | Administrativo, Constitucional |
| `sentencia_su_288_2022` | Sentencia SU-288 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU288-22.htm) | 2026-10-02 | — | 788 | Constitucional |
| `sentencia_su_292_2025` | Sentencia SU-292 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU292-25.htm) | 2026-10-02 | — | 191 | Constitucional |
| `sentencia_su_295_2023` | Sentencia SU-295 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU295-23.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_su_296_2020` | Sentencia SU-296 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU296-20.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_su_297_2021` | Sentencia SU-297 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU297-21.htm) | 2026-10-02 | — | 114 | Constitucional |
| `sentencia_su_297_2023` | Sentencia SU-297 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU297-23.htm) | 2026-10-02 | — | 204 | Constitucional |
| `sentencia_su_297_2025` | Sentencia SU-297 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU297-25.htm) | 2026-10-02 | — | 190 | Constitucional |
| `sentencia_su_299_2022` | Sentencia SU-299 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU299-22.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_su_29_2023` | Sentencia SU-029 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU029-23.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_29_2024` | Sentencia SU-029 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU029-24.htm) | 2026-10-02 | — | 227 | Constitucional |
| `sentencia_su_304_2024` | Sentencia SU-304 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU304-24.htm) | 2026-10-02 | — | 171 | Constitucional |
| `sentencia_su_306_2023` | Sentencia SU-306 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU306-23.htm) | 2026-10-02 | — | 209 | Constitucional |
| `sentencia_su_312_2020` | Sentencia SU-312 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU312-20.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_su_313_2020` | Sentencia SU-313 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU313-20.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_su_316_2021` | Sentencia SU-316 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU316-21.htm) | 2026-10-02 | — | 170 | Constitucional |
| `sentencia_su_316_2023` | Sentencia SU-316 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU316-23.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_su_317_2021` | Sentencia SU-317 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU317-21.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_su_317_2023` | Sentencia SU-317 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU317-23.htm) | 2026-10-02 | — | 162 | Constitucional |
| `sentencia_su_322_2024` | Sentencia SU-322 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU322-24.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_su_326_2022` | Sentencia SU-326 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU326-22.htm) | 2026-10-02 | — | 197 | Constitucional |
| `sentencia_su_328_2025` | Sentencia SU-328 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU328-25.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_su_329_2024` | Sentencia SU-329 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU329-24.htm) | 2026-10-02 | — | 135 | Constitucional |
| `sentencia_su_32_2022` | Sentencia SU-032 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU032-22.htm) | 2026-10-02 | — | 216 | Constitucional |
| `sentencia_su_333_2020` | Sentencia SU-333 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU333-20.htm) | 2026-10-02 | — | 171 | Constitucional |
| `sentencia_su_335_2023` | Sentencia SU-335 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU335-23.htm) | 2026-10-02 | — | 194 | Constitucional |
| `sentencia_su_336_2017` | Sentencia SU-336 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/SU336-17.htm) | 2026-10-03 | — | 244 | Administrativo |
| `sentencia_su_339_2024` | Sentencia SU-339 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU339-24.htm) | 2026-10-02 | — | 158 | Constitucional |
| `sentencia_su_339_2025` | Sentencia SU-339 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU339-25.htm) | 2026-10-02 | — | 140 | Constitucional |
| `sentencia_su_342_2024` | Sentencia SU-342 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU342-24.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_su_345_2024` | Sentencia SU-345 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU345-24.htm) | 2026-10-02 | — | 168 | Constitucional |
| `sentencia_su_347_2022` | Sentencia SU-347 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU347-22.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_347_2023` | Sentencia SU-347 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU347-23.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_su_348_2022` | Sentencia SU-348 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU348-22.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_su_349_2022` | Sentencia SU-349 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU349-22.htm) | 2026-10-02 | — | 155 | Constitucional |
| `sentencia_su_353_2020` | Sentencia SU-353 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU353-20.htm) | 2026-10-02 | — | 149 | Constitucional |
| `sentencia_su_354_2020` | Sentencia SU-354 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU354-20.htm) | 2026-10-02 | — | 189 | Constitucional |
| `sentencia_su_355_2020` | Sentencia SU-355 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU355-20.htm) | 2026-10-02 | — | 324 | Constitucional |
| `sentencia_su_355_2022` | Sentencia SU-355 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU355-22.htm) | 2026-10-02 | — | 149 | Constitucional |
| `sentencia_su_360_2024` | Sentencia SU-360 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU360-24.htm) | 2026-10-02 | — | 206 | Constitucional |
| `sentencia_su_363_2021` | Sentencia SU-363 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU363-21.htm) | 2026-10-02 | — | 155 | Constitucional |
| `sentencia_su_367_2025` | Sentencia SU-367 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU367-25.htm) | 2026-10-02 | — | 328 | Constitucional |
| `sentencia_su_368_2022` | Sentencia SU-368 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU368-22.htm) | 2026-10-02 | — | 194 | Constitucional |
| `sentencia_su_368_2025` | Sentencia SU-368 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU368-25.htm) | 2026-10-02 | — | 169 | Constitucional |
| `sentencia_su_369_2024` | Sentencia SU-369 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU369-24.htm) | 2026-10-02 | — | 148 | Constitucional |
| `sentencia_su_371_2021` | Sentencia SU-371 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU371-21.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_su_381_2024` | Sentencia SU-381 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU381-24.htm) | 2026-10-02 | — | 191 | Constitucional |
| `sentencia_su_382_2024` | Sentencia SU-382 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU382-24.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_su_386_2023` | Sentencia SU-386 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU386-23.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_su_387_2022` | Sentencia SU-387 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU387-22.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_su_388_2021` | Sentencia SU-388 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU388-21.htm) | 2026-10-02 | — | 209 | Constitucional |
| `sentencia_su_388_2022` | Sentencia SU-388 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU388-22.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_su_388_2023` | Sentencia SU-388 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU388-23.htm) | 2026-10-02 | — | 115 | Constitucional |
| `sentencia_su_389_2005` | Sentencia SU-389 de 2005 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2005/SU389-05.htm) | 2026-10-03 | — | 76 | Constitucional |
| `sentencia_su_38_2023` | Sentencia SU-038 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU038-23.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_su_397_2021` | Sentencia SU-397 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU397-21.htm) | 2026-10-02 | — | 267 | Constitucional |
| `sentencia_su_397_2022` | Sentencia SU-397 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU397-22.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_su_39_1997` | Sentencia SU-039 de 1997 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1997/SU039-97.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_su_405_2021` | Sentencia SU-405 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU405-21.htm) | 2026-10-02 | — | 173 | Constitucional |
| `sentencia_su_40_2018` | Sentencia SU-40 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/SU040-18.htm) | 2026-10-03 | — | 86 | Laboral |
| `sentencia_su_40_2026` | Sentencia SU-040 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU040-26.htm) | 2026-10-02 | — | 226 | Constitucional |
| `sentencia_su_411_2020` | Sentencia SU-411 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU411-20.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_su_417_2024` | Sentencia SU-417 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU417-24.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_su_419_2024` | Sentencia SU-419 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU419-24.htm) | 2026-10-02 | — | 313 | Constitucional |
| `sentencia_su_41_2020` | Sentencia SU-041 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU041-20.htm) | 2026-10-02 | — | 254 | Constitucional |
| `sentencia_su_41_2022` | Sentencia SU-041 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU041-22.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_su_424_2021` | Sentencia SU-424 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU424-21.htm) | 2026-10-02 | — | 210 | Constitucional |
| `sentencia_su_426_2025` | Sentencia SU-426 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU426-25.htm) | 2026-10-02 | — | 150 | Constitucional |
| `sentencia_su_428_2023` | Sentencia SU-428 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU428-23.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_su_428_2024` | Sentencia SU-428 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU428-24.htm) | 2026-10-02 | — | 98 | Constitucional |
| `sentencia_su_429_2023` | Sentencia SU-429 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU429-23.htm) | 2026-10-02 | — | 133 | Constitucional |
| `sentencia_su_432_2025` | Sentencia SU-432 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU432-25.htm) | 2026-10-02 | — | 210 | Constitucional |
| `sentencia_su_433_2020` | Sentencia SU-433 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU433-20.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_su_439_2024` | Sentencia SU-439 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU439-24.htm) | 2026-10-02 | — | 93 | Constitucional |
| `sentencia_su_440_2021` | Sentencia SU-440 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU440-21.htm) | 2026-10-02 | — | 142 | Constitucional |
| `sentencia_su_444_2023` | Sentencia SU-444 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU444-23.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_su_444_2025` | Sentencia SU-444 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU444-25.htm) | 2026-10-02 | — | 198 | Constitucional |
| `sentencia_su_446_2022` | Sentencia SU-446 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU446-22.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_su_446_2025` | Sentencia SU-446 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU446-25.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_su_449_2020` | Sentencia SU-449 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU449-20.htm) | 2026-10-02 | — | 258 | Constitucional |
| `sentencia_su_451_2024` | Sentencia SU-451 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU451-24.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_su_452_2024` | Sentencia SU-452 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU452-24.htm) | 2026-10-02 | — | 136 | Constitucional |
| `sentencia_su_453_2020` | Sentencia SU-453 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU453-20.htm) | 2026-10-02 | — | 58 | Constitucional |
| `sentencia_su_454_2020` | Sentencia SU-454 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU454-20.htm) | 2026-10-02 | — | 156 | Constitucional |
| `sentencia_su_454_2025` | Sentencia SU-454 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU454-25.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_461_2020` | Sentencia SU-461 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU461-20.htm) | 2026-10-02 | — | 130 | Constitucional |
| `sentencia_su_462_2020` | Sentencia SU-462 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU462-20.htm) | 2026-10-02 | — | 166 | Constitucional |
| `sentencia_su_466_2025` | Sentencia SU-466 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU466-25.htm) | 2026-10-02 | — | 335 | Constitucional |
| `sentencia_su_471_2023` | Sentencia SU-471 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU471-23.htm) | 2026-10-02 | — | 160 | Constitucional |
| `sentencia_su_474_2020` | Sentencia SU-474 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU474-20.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_su_475_2023` | Sentencia SU-475 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU475-23.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_su_478_2024` | Sentencia SU-478 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU478-24.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_su_47_2026` | Sentencia SU-047 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU047-26.htm) | 2026-10-02 | — | 186 | Constitucional |
| `sentencia_su_480_2025` | Sentencia SU-480 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU480-25.htm) | 2026-10-02 | — | 136 | Constitucional |
| `sentencia_su_484_2024` | Sentencia SU-484 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU484-24.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_su_487_2024` | Sentencia SU-487 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU487-24.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_su_488_2020` | Sentencia SU-488 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU488-20.htm) | 2026-10-02 | — | 124 | Constitucional |
| `sentencia_su_48_2021` | Sentencia SU-048 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU048-21.htm) | 2026-10-02 | — | 51 | Constitucional |
| `sentencia_su_48_2022` | Sentencia SU-048 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU048-22.htm) | 2026-10-02 | — | 123 | Constitucional |
| `sentencia_su_495_2020` | Sentencia SU-495 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU495-20.htm) | 2026-10-02 | — | 127 | Constitucional |
| `sentencia_su_499_2024` | Sentencia SU-499 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU499-24.htm) | 2026-10-02 | — | 158 | Constitucional |
| `sentencia_su_49_2017` | Sentencia SU-049 de 2017 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2017/SU049-17.htm) | 2026-10-02 | — | 88 | Constitucional, Laboral |
| `sentencia_su_49_2024` | Sentencia SU-049 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU049-24.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_su_501_2024` | Sentencia SU-501 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU501-24.htm) | 2026-10-02 | — | 153 | Constitucional |
| `sentencia_su_502_2025` | Sentencia SU-502 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU502-25.htm) | 2026-10-02 | — | 130 | Constitucional |
| `sentencia_su_508_2020` | Sentencia SU-508 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU508-20.htm) | 2026-10-02 | — | 169 | Constitucional |
| `sentencia_su_50_2022` | Sentencia SU-050 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU050-22.htm) | 2026-10-02 | — | 191 | Constitucional |
| `sentencia_su_512_2024` | Sentencia SU-512 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU512-24.htm) | 2026-10-02 | — | 295 | Constitucional |
| `sentencia_su_543_2023` | Sentencia SU-543 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU543-23.htm) | 2026-10-02 | — | 191 | Constitucional |
| `sentencia_su_545_2023` | Sentencia SU-545 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU545-23.htm) | 2026-10-02 | — | 604 | Constitucional |
| `sentencia_su_546_2023` | Sentencia SU-546 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU546-23.htm) | 2026-10-02 | — | 605 | Constitucional |
| `sentencia_su_54_2015` | Sentencia SU-54 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/SU054-15.htm) | 2026-10-03 | — | 159 | Civil |
| `sentencia_su_54_2025` | Sentencia SU-054 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU054-25.htm) | 2026-10-02 | — | 163 | Constitucional |
| `sentencia_su_56_2025` | Sentencia SU-056 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU056-25.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_su_575_2019` | Sentencia SU-575 de 2019 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2019/SU575-19.htm) | 2026-10-03 | — | 116 | Administrativo |
| `sentencia_su_59_2024` | Sentencia SU-059 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU059-24.htm) | 2026-10-02 | — | 222 | Constitucional |
| `sentencia_su_60_2021` | Sentencia SU-060 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU060-21.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_su_60_2024` | Sentencia SU-060 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU060-24.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_su_60_2026` | Sentencia SU-060 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU060-26.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_su_617_2014` | Sentencia SU-617 de 2014 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2014/SU617-14.htm) | 2026-10-02 | — | 148 | Constitucional, Familia |
| `sentencia_su_61_2023` | Sentencia SU-061 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU061-23.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_su_62_2023` | Sentencia SU-062 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU062-23.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_su_63_2023` | Sentencia SU-063 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU063-23.htm) | 2026-10-02 | — | 109 | Constitucional |
| `sentencia_su_63_2025` | Sentencia SU-063 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU063-25.htm) | 2026-10-02 | — | 142 | Constitucional |
| `sentencia_su_65_2026` | Sentencia SU-065 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU065-26.htm) | 2026-10-02 | — | 109 | Constitucional |
| `sentencia_su_66_2026` | Sentencia SU-066 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU066-26.htm) | 2026-10-02 | — | 248 | Constitucional |
| `sentencia_su_67_2022` | Sentencia SU-067 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU067-22.htm) | 2026-10-02 | — | 165 | Constitucional |
| `sentencia_su_67_2023` | Sentencia SU-067 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU067-23.htm) | 2026-10-02 | — | 210 | Constitucional |
| `sentencia_su_68_2022` | Sentencia SU-068 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU068-22.htm) | 2026-10-02 | — | 151 | Constitucional |
| `sentencia_su_68_2023` | Sentencia SU-068 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU068-23.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_su_68_2026` | Sentencia SU-068 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU068-26.htm) | 2026-10-02 | — | 141 | Constitucional |
| `sentencia_su_6_2023` | Sentencia SU-006 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU006-23.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_su_70_2025` | Sentencia SU-070 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU070-25.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_su_71_2022` | Sentencia SU-071 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU071-22.htm) | 2026-10-02 | — | 103 | Constitucional |
| `sentencia_su_72_2024` | Sentencia SU-072 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU072-24.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_su_73_2020` | Sentencia SU-073 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU073-20.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_su_73_2021` | Sentencia SU-073 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU073-21.htm) | 2026-10-02 | — | 236 | Constitucional |
| `sentencia_su_74_2020` | Sentencia SU-074 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU074-20.htm) | 2026-10-02 | — | 339 | Constitucional |
| `sentencia_su_74_2022` | Sentencia SU-074 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU074-22.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_su_75_2018` | Sentencia SU-075 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/SU075-18.htm) | 2026-10-02 | — | 293 | Constitucional, Laboral |
| `sentencia_su_76_2022` | Sentencia SU-076 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU076-22.htm) | 2026-10-02 | — | 152 | Constitucional |
| `sentencia_su_7_2023` | Sentencia SU-007 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU007-23.htm) | 2026-10-02 | — | 100 | Constitucional |
| `sentencia_su_80_2020` | Sentencia SU-080 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU080-20.htm) | 2026-10-02 | — | 102 | Constitucional |
| `sentencia_su_81_2020` | Sentencia SU-081 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/SU081-20.htm) | 2026-10-02 | — | 438 | Constitucional |
| `sentencia_su_81_2024` | Sentencia SU-081 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU081-24.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_82_2022` | Sentencia SU-082 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU082-22.htm) | 2026-10-02 | — | 162 | Constitucional |
| `sentencia_su_82_2026` | Sentencia SU-082 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/SU082-26.htm) | 2026-10-02 | — | 408 | Constitucional |
| `sentencia_su_86_2022` | Sentencia SU-086 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU086-22.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_su_87_2022` | Sentencia SU-087 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/SU087-22.htm) | 2026-10-02 | — | 81 | Constitucional, Laboral |
| `sentencia_su_87_2025` | Sentencia SU-087 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU087-25.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_su_88_2024` | Sentencia SU-088 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/SU088-24.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_su_88_2025` | Sentencia SU-088 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/SU088-25.htm) | 2026-10-02 | — | 304 | Constitucional |
| `sentencia_su_91_2023` | Sentencia SU-091 de 2023 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2023/SU091-23.htm) | 2026-10-02 | — | 357 | Constitucional |
| `sentencia_su_92_2021` | Sentencia SU-092 de 2021 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2021/SU092-21.htm) | 2026-10-02 | — | 453 | Constitucional |
| `sentencia_t_102_2026` | Sentencia T-102 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-102-26.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_t_103_2026` | Sentencia T-103 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-103-26.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_t_104_2025` | Sentencia T-104 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-104-25.htm) | 2026-10-02 | — | 195 | Constitucional |
| `sentencia_t_104_2026` | Sentencia T-104 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-104-26.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_105_2025` | Sentencia T-105 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-105-25.htm) | 2026-10-02 | — | 264 | Constitucional |
| `sentencia_t_105_2026` | Sentencia T-105 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-105-26.htm) | 2026-10-02 | — | 108 | Constitucional |
| `sentencia_t_106_2025` | Sentencia T-106 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-106-25.htm) | 2026-10-02 | — | 473 | Constitucional |
| `sentencia_t_106_2026` | Sentencia T-106 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-106-26.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_107_2025` | Sentencia T-107 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-107-25.htm) | 2026-10-02 | — | 115 | Constitucional |
| `sentencia_t_107_2026` | Sentencia T-107 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-107-26.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_108_2025` | Sentencia T-108 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-108-25.htm) | 2026-10-02 | — | 65 | Constitucional |
| `sentencia_t_108_2026` | Sentencia T-108 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-108-26.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_t_109_2025` | Sentencia T-109 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-109-25.htm) | 2026-10-02 | — | 30 | Constitucional |
| `sentencia_t_109_2026` | Sentencia T-109 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-109-26.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_10_2025` | Sentencia T-010 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-010-25.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_t_10_2026` | Sentencia T-010 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-010-26.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_110_2026` | Sentencia T-110 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-110-26.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_111_2026` | Sentencia T-111 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-111-26.htm) | 2026-10-02 | — | 42 | Constitucional |
| `sentencia_t_112_2026` | Sentencia T-112 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-112-26.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_113_2025` | Sentencia T-113 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-113-25.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_113_2026` | Sentencia T-113 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-113-26.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_t_114_2025` | Sentencia T-114 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-114-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_115_2025` | Sentencia T-115 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-115-25.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_t_116_2025` | Sentencia T-116 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-116-25.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_t_117_2025` | Sentencia T-117 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-117-25.htm) | 2026-10-02 | — | 45 | Constitucional |
| `sentencia_t_118_2025` | Sentencia T-118 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-118-25.htm) | 2026-10-02 | — | 34 | Constitucional |
| `sentencia_t_119_2026` | Sentencia T-119 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-119-26.htm) | 2026-10-02 | — | 188 | Constitucional |
| `sentencia_t_11_2025` | Sentencia T-011 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-011-25.htm) | 2026-10-02 | — | 123 | Constitucional |
| `sentencia_t_11_2026` | Sentencia T-011 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-011-26.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_t_120_2025` | Sentencia T-120 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-120-25.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_122_2025` | Sentencia T-122 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-122-25.htm) | 2026-10-02 | — | 45 | Constitucional |
| `sentencia_t_122_2026` | Sentencia T-122 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-122-26.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_123_2025` | Sentencia T-123 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-123-25.htm) | 2026-10-02 | — | 31 | Constitucional |
| `sentencia_t_123_2026` | Sentencia T-123 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-123-26.htm) | 2026-10-02 | — | 52 | Constitucional |
| `sentencia_t_124_2025` | Sentencia T-124 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-124-25.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_124_2026` | Sentencia T-124 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-124-26.htm) | 2026-10-02 | — | 155 | Constitucional |
| `sentencia_t_125_2025` | Sentencia T-125 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-125-25.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_125_2026` | Sentencia T-125 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-125-26.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_126_2026` | Sentencia T-126 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-126-26.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_127_2026` | Sentencia T-127 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-127-26.htm) | 2026-10-02 | — | 177 | Constitucional |
| `sentencia_t_128_2026` | Sentencia T-128 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-128-26.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_129_2011` | Sentencia T-129 de 2011 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2011/T-129-11.htm) | 2026-10-02 | — | 217 | Constitucional |
| `sentencia_t_12_2025` | Sentencia T-012 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-012-25.htm) | 2026-10-02 | — | 146 | Constitucional |
| `sentencia_t_12_2026` | Sentencia T-012 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-012-26.htm) | 2026-10-02 | — | 93 | Constitucional |
| `sentencia_t_131_2025` | Sentencia T-131 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-131-25.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_t_131_2026` | Sentencia T-131 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-131-26.htm) | 2026-10-02 | — | 131 | Constitucional |
| `sentencia_t_132_2025` | Sentencia T-132 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-132-25.htm) | 2026-10-02 | — | 135 | Constitucional |
| `sentencia_t_132_2026` | Sentencia T-132 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-132-26.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_133_2025` | Sentencia T-133 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-133-25.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_133_2026` | Sentencia T-133 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-133-26.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_134_2025` | Sentencia T-134 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-134-25.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_134_2026` | Sentencia T-134 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-134-26.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_135_2025` | Sentencia T-135 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-135-25.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_135_2026` | Sentencia T-135 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-135-26.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_136_2025` | Sentencia T-136 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-136-25.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_t_136_2026` | Sentencia T-136 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-136-26.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_137_2025` | Sentencia T-137 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-137-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_137_2026` | Sentencia T-137 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-137-26.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_138_2026` | Sentencia T-138 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-138-26.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_t_139_2025` | Sentencia T-139 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-139-25.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_13_2025` | Sentencia T-013 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-013-25.htm) | 2026-10-02 | — | 167 | Constitucional |
| `sentencia_t_13_2026` | Sentencia T-013 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-013-26.htm) | 2026-10-02 | — | 58 | Constitucional |
| `sentencia_t_140_2025` | Sentencia T-140 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-140-25.htm) | 2026-10-02 | — | 45 | Constitucional |
| `sentencia_t_141_2025` | Sentencia T-141 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-141-25.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_141_2026` | Sentencia T-141 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-141-26.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_144_2025` | Sentencia T-144 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-144-25.htm) | 2026-10-02 | — | 201 | Constitucional |
| `sentencia_t_145_2025` | Sentencia T-145 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-145-25.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_t_145_2026` | Sentencia T-145 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-145-26.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_146_2025` | Sentencia T-146 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-146-25.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_t_146_2026` | Sentencia T-146 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-146-26.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_147_2025` | Sentencia T-147 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-147-25.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_147_2026` | Sentencia T-147 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-147-26.htm) | 2026-10-02 | — | 159 | Constitucional |
| `sentencia_t_148_2026` | Sentencia T-148 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-148-26.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_t_149_2025` | Sentencia T-149 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-149-25.htm) | 2026-10-02 | — | 288 | Constitucional |
| `sentencia_t_149_2026` | Sentencia T-149 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-149-26.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_14_2025` | Sentencia T-014 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-014-25.htm) | 2026-10-02 | — | 215 | Constitucional |
| `sentencia_t_14_2026` | Sentencia T-014 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-014-26.htm) | 2026-10-02 | — | 130 | Constitucional |
| `sentencia_t_150_2025` | Sentencia T-150 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-150-25.htm) | 2026-10-02 | — | 43 | Constitucional |
| `sentencia_t_150_2026` | Sentencia T-150 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-150-26.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_151_2025` | Sentencia T-151 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-151-25.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_151_2026` | Sentencia T-151 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-151-26.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_152_2025` | Sentencia T-152 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-152-25.htm) | 2026-10-02 | — | 93 | Constitucional |
| `sentencia_t_152_2026` | Sentencia T-152 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-152-26.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_153_1998` | Sentencia T-153 de 1998 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1998/T-153-98.htm) | 2026-10-02 | — | 145 | Constitucional, Penal |
| `sentencia_t_153_2025` | Sentencia T-153 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-153-25.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_t_153_2026` | Sentencia T-153 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-153-26.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_t_154_2026` | Sentencia T-154 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-154-26.htm) | 2026-10-02 | — | 40 | Constitucional |
| `sentencia_t_155_2025` | Sentencia T-155 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-155-25.htm) | 2026-10-02 | — | 90 | Constitucional |
| `sentencia_t_155_2026` | Sentencia T-155 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-155-26.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_t_156_2025` | Sentencia T-156 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-156-25.htm) | 2026-10-02 | — | 245 | Constitucional |
| `sentencia_t_156_2026` | Sentencia T-156 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-156-26.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_157_2025` | Sentencia T-157 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-157-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_157_2026` | Sentencia T-157 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-157-26.htm) | 2026-10-02 | — | 124 | Constitucional |
| `sentencia_t_158_2025` | Sentencia T-158 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-158-25.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_158_2026` | Sentencia T-158 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-158-26.htm) | 2026-10-02 | — | 223 | Constitucional |
| `sentencia_t_159_2025` | Sentencia T-159 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-159-25.htm) | 2026-10-02 | — | 103 | Constitucional |
| `sentencia_t_159_2026` | Sentencia T-159 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-159-26.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_15_2025` | Sentencia T-015 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-015-25.htm) | 2026-10-02 | — | 89 | Constitucional |
| `sentencia_t_160_2025` | Sentencia T-160 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-160-25.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_160_2026` | Sentencia T-160 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-160-26.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_161_2025` | Sentencia T-161 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-161-25.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_161_2026` | Sentencia T-161 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-161-26.htm) | 2026-10-02 | — | 65 | Constitucional |
| `sentencia_t_162_2025` | Sentencia T-162 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-162-25.htm) | 2026-10-02 | — | 38 | Constitucional |
| `sentencia_t_162_2026` | Sentencia T-162 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-162-26.htm) | 2026-10-02 | — | 88 | Constitucional |
| `sentencia_t_163_2025` | Sentencia T-163 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-163-25.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_163_2026` | Sentencia T-163 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-163-26.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_164_2025` | Sentencia T-164 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-164-25.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_165_2025` | Sentencia T-165 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-165-25.htm) | 2026-10-02 | — | 89 | Constitucional |
| `sentencia_t_166_2025` | Sentencia T-166 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-166-25.htm) | 2026-10-02 | — | 46 | Constitucional |
| `sentencia_t_167_2025` | Sentencia T-167 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-167-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_168_2025` | Sentencia T-168 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-168-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_169_2025` | Sentencia T-169 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-169-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_16_2025` | Sentencia T-016 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-016-25.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_170_2025` | Sentencia T-170 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-170-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_171_2025` | Sentencia T-171 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-171-25.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_172_2025` | Sentencia T-172 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-172-25.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_173_2025` | Sentencia T-173 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-173-25.htm) | 2026-10-02 | — | 69 | Constitucional |
| `sentencia_t_173_2026` | Sentencia T-173 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-173-26.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_t_174_2026` | Sentencia T-174 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-174-26.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_t_175_2026` | Sentencia T-175 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-175-26.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_176_2026` | Sentencia T-176 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-176-26.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_177_2025` | Sentencia T-177 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-177-25.htm) | 2026-10-02 | — | 28 | Constitucional |
| `sentencia_t_177_2026` | Sentencia T-177 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-177-26.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_178_2025` | Sentencia T-178 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-178-25.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_t_178_2026` | Sentencia T-178 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-178-26.htm) | 2026-10-02 | — | 35 | Constitucional |
| `sentencia_t_179_2025` | Sentencia T-179 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-179-25.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_t_179_2026` | Sentencia T-179 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-179-26.htm) | 2026-10-02 | — | 109 | Constitucional |
| `sentencia_t_17_2025` | Sentencia T-017 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-017-25.htm) | 2026-10-02 | — | 140 | Constitucional |
| `sentencia_t_180_2026` | Sentencia T-180 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-180-26.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_181_2026` | Sentencia T-181 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-181-26.htm) | 2026-10-02 | — | 25 | Constitucional |
| `sentencia_t_182_2026` | Sentencia T-182 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-182-26.htm) | 2026-10-02 | — | 114 | Constitucional |
| `sentencia_t_183_2026` | Sentencia T-183 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-183-26.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_184_2026` | Sentencia T-184 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-184-26.htm) | 2026-10-02 | — | 143 | Constitucional |
| `sentencia_t_185_2025` | Sentencia T-185 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-185-25.htm) | 2026-10-02 | — | 88 | Constitucional |
| `sentencia_t_185_2026` | Sentencia T-185 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-185-26.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_186_2025` | Sentencia T-186 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-186-25.htm) | 2026-10-02 | — | 35 | Constitucional |
| `sentencia_t_186_2026` | Sentencia T-186 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-186-26.htm) | 2026-10-02 | — | 138 | Constitucional |
| `sentencia_t_187_2025` | Sentencia T-187 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-187-25.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_187_2026` | Sentencia T-187 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-187-26.htm) | 2026-10-02 | — | 46 | Constitucional |
| `sentencia_t_188_2025` | Sentencia T-188 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-188-25.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_t_188_2026` | Sentencia T-188 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-188-26.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_189_2025` | Sentencia T-189 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-189-25.htm) | 2026-10-02 | — | 148 | Constitucional |
| `sentencia_t_189_2026` | Sentencia T-189 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-189-26.htm) | 2026-10-02 | — | 22 | Constitucional |
| `sentencia_t_190_2025` | Sentencia T-190 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-190-25.htm) | 2026-10-02 | — | 28 | Constitucional |
| `sentencia_t_190_2026` | Sentencia T-190 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-190-26.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_193_2025` | Sentencia T-193 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-193-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_193_2026` | Sentencia T-193 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-193-26.htm) | 2026-10-02 | — | 99 | Constitucional |
| `sentencia_t_194_2025` | Sentencia T-194 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-194-25.htm) | 2026-10-02 | — | 106 | Constitucional |
| `sentencia_t_195_2025` | Sentencia T-195 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-195-25.htm) | 2026-10-02 | — | 56 | Constitucional |
| `sentencia_t_198_2026` | Sentencia T-198 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-198-26.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_199_2025` | Sentencia T-199 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-199-25.htm) | 2026-10-02 | — | 391 | Constitucional |
| `sentencia_t_199_2026` | Sentencia T-199 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-199-26.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_t_19_2025` | Sentencia T-019 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-019-25.htm) | 2026-10-02 | — | 106 | Constitucional |
| `sentencia_t_19_2026` | Sentencia T-019 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-019-26.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_1_2025` | Sentencia T-001 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-001-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_1_2026` | Sentencia T-001 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-001-26.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_200_2025` | Sentencia T-200 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-200-25.htm) | 2026-10-02 | — | 90 | Constitucional |
| `sentencia_t_200_2026` | Sentencia T-200 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-200-26.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_201_2025` | Sentencia T-201 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-201-25.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_201_2026` | Sentencia T-201 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-201-26.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_202_2018` | Sentencia T-202 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/T-202-18.htm) | 2026-10-03 | — | 112 | Familia |
| `sentencia_t_202_2024` | Sentencia T-202 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-202-24.htm) | 2026-10-03 | — | 181 | Laboral, Penal |
| `sentencia_t_202_2025` | Sentencia T-202 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-202-25.htm) | 2026-10-02 | — | 140 | Constitucional |
| `sentencia_t_202_2026` | Sentencia T-202 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-202-26.htm) | 2026-10-02 | — | 189 | Constitucional |
| `sentencia_t_203_2025` | Sentencia T-203 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-203-25.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_203_2026` | Sentencia T-203 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-203-26.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_204_2026` | Sentencia T-204 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-204-26.htm) | 2026-10-02 | — | 123 | Constitucional |
| `sentencia_t_205_2026` | Sentencia T-205 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-205-26.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_206_2026` | Sentencia T-206 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-206-26.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_207_2026` | Sentencia T-207 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-207-26.htm) | 2026-10-02 | — | 141 | Constitucional |
| `sentencia_t_208_2026` | Sentencia T-208 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-208-26.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_20_2025` | Sentencia T-020 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-020-25.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_t_210_2025` | Sentencia T-210 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-210-25.htm) | 2026-10-02 | — | 115 | Constitucional |
| `sentencia_t_211_2025` | Sentencia T-211 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-211-25.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_212_2025` | Sentencia T-212 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-212-25.htm) | 2026-10-02 | — | 114 | Constitucional |
| `sentencia_t_213_2025` | Sentencia T-213 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-213-25.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_213_2026` | Sentencia T-213 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-213-26.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_214_2025` | Sentencia T-214 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-214-25.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_214_2026` | Sentencia T-214 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-214-26.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_t_215_2026` | Sentencia T-215 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-215-26.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_t_216_2026` | Sentencia T-216 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-216-26.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_21_2025` | Sentencia T-021 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-021-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_222_2026` | Sentencia T-222 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-222-26.htm) | 2026-10-02 | — | 107 | Constitucional |
| `sentencia_t_223_2026` | Sentencia T-223 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-223-26.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_t_224_2026` | Sentencia T-224 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-224-26.htm) | 2026-10-02 | — | 133 | Constitucional |
| `sentencia_t_225_2026` | Sentencia T-225 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-225-26.htm) | 2026-10-02 | — | 58 | Constitucional |
| `sentencia_t_226_2025` | Sentencia T-226 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-226-25.htm) | 2026-10-02 | — | 211 | Constitucional |
| `sentencia_t_226_2026` | Sentencia T-226 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-226-26.htm) | 2026-10-02 | — | 181 | Constitucional |
| `sentencia_t_227_2025` | Sentencia T-227 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-227-25.htm) | 2026-10-02 | — | 184 | Constitucional |
| `sentencia_t_227_2026` | Sentencia T-227 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-227-26.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_228_2025` | Sentencia T-228 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-228-25.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_t_228_2026` | Sentencia T-228 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-228-26.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_t_229_2025` | Sentencia T-229 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-229-25.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_229_2026` | Sentencia T-229 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-229-26.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_22_2025` | Sentencia T-022 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-022-25.htm) | 2026-10-02 | — | 35 | Constitucional |
| `sentencia_t_22_2026` | Sentencia T-022 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-022-26.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_230_2025` | Sentencia T-230 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-230-25.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_230_2026` | Sentencia T-230 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-230-26.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_231_2026` | Sentencia T-231 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-231-26.htm) | 2026-10-02 | — | 273 | Constitucional |
| `sentencia_t_232_2026` | Sentencia T-232 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-232-26.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_233_2025` | Sentencia T-233 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-233-25.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_t_233_2026` | Sentencia T-233 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-233-26.htm) | 2026-10-02 | — | 20 | Constitucional |
| `sentencia_t_234_2025` | Sentencia T-234 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-234-25.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_234_2026` | Sentencia T-234 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-234-26.htm) | 2026-10-02 | — | 158 | Constitucional |
| `sentencia_t_235_2025` | Sentencia T-235 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-235-25.htm) | 2026-10-02 | — | 163 | Constitucional |
| `sentencia_t_235_2026` | Sentencia T-235 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-235-26.htm) | 2026-10-02 | — | 26 | Constitucional |
| `sentencia_t_236_2025` | Sentencia T-236 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-236-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_236_2026` | Sentencia T-236 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-236-26.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_t_237_2025` | Sentencia T-237 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-237-25.htm) | 2026-10-02 | — | 69 | Constitucional |
| `sentencia_t_237_2026` | Sentencia T-237 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-237-26.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_238_2025` | Sentencia T-238 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-238-25.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_238_2026` | Sentencia T-238 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-238-26.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_239_2025` | Sentencia T-239 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-239-25.htm) | 2026-10-02 | — | 109 | Constitucional |
| `sentencia_t_239_2026` | Sentencia T-239 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-239-26.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_23_2025` | Sentencia T-023 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-023-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_23_2026` | Sentencia T-023 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-023-26.htm) | 2026-10-02 | — | 47 | Constitucional |
| `sentencia_t_240_2026` | Sentencia T-240 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-240-26.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_241_2025` | Sentencia T-241 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-241-25.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_t_241_2026` | Sentencia T-241 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-241-26.htm) | 2026-10-02 | — | 145 | Constitucional |
| `sentencia_t_242_2025` | Sentencia T-242 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-242-25.htm) | 2026-10-02 | — | 148 | Constitucional |
| `sentencia_t_242_2026` | Sentencia T-242 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-242-26.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_243_2026` | Sentencia T-243 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-243-26.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_t_244_2026` | Sentencia T-244 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-244-26.htm) | 2026-10-02 | — | 89 | Constitucional |
| `sentencia_t_245_2026` | Sentencia T-245 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-245-26.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_246_2026` | Sentencia T-246 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-246-26.htm) | 2026-10-02 | — | 118 | Constitucional |
| `sentencia_t_247_2026` | Sentencia T-247 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-247-26.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_t_248_2026` | Sentencia T-248 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-248-26.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_249_2026` | Sentencia T-249 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-249-26.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_24_2025` | Sentencia T-024 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-024-25.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_t_24_2026` | Sentencia T-024 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-024-26.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_251_2025` | Sentencia T-251 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-251-25.htm) | 2026-10-02 | — | 318 | Constitucional |
| `sentencia_t_254_2006` | Sentencia T-254 de 2006 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2006/T-254-06.htm) | 2026-10-03 | — | 69 | Civil |
| `sentencia_t_256_2025` | Sentencia T-256 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/t-256-25.htm) | 2026-10-01 | — | 256 | Constitucional |
| `sentencia_t_257_2025` | Sentencia T-257 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-257-25.htm) | 2026-10-02 | — | 156 | Constitucional |
| `sentencia_t_258_2025` | Sentencia T-258 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-258-25.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_t_258_2026` | Sentencia T-258 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-258-26.htm) | 2026-10-02 | — | 244 | Constitucional |
| `sentencia_t_259_2025` | Sentencia T-259 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-259-25.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_25_2004` | Sentencia T-025 de 2004 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2004/T-025-04.htm) | 2026-10-02 | — | 271 | Constitucional |
| `sentencia_t_25_2026` | Sentencia T-025 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-025-26.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_260_2025` | Sentencia T-260 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-260-25.htm) | 2026-10-02 | — | 42 | Constitucional |
| `sentencia_t_260_2026` | Sentencia T-260 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-260-26.htm) | 2026-10-02 | — | 123 | Constitucional |
| `sentencia_t_261_2025` | Sentencia T-261 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-261-25.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_t_263_2025` | Sentencia T-263 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-263-25.htm) | 2026-10-02 | — | 42 | Constitucional |
| `sentencia_t_263_2026` | Sentencia T-263 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-263-26.htm) | 2026-10-02 | — | 27 | Constitucional |
| `sentencia_t_268_2026` | Sentencia T-268 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-268-26.htm) | 2026-10-02 | — | 152 | Constitucional |
| `sentencia_t_270_2025` | Sentencia T-270 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-270-25.htm) | 2026-10-02 | — | 85 | Constitucional |
| `sentencia_t_271_2025` | Sentencia T-271 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-271-25.htm) | 2026-10-02 | — | 159 | Constitucional |
| `sentencia_t_272_2025` | Sentencia T-272 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-272-25.htm) | 2026-10-02 | — | 56 | Constitucional |
| `sentencia_t_275_2026` | Sentencia T-275 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-275-26.htm) | 2026-10-02 | — | 126 | Constitucional |
| `sentencia_t_277_2018` | Sentencia T-277 de 2018 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2018/T-277-18.htm) | 2026-10-03 | — | 99 | Constitucional |
| `sentencia_t_277_2026` | Sentencia T-277 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-277-26.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_278_2026` | Sentencia T-278 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-278-26.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_t_279_2025` | Sentencia T-279 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-279-25.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_279_2026` | Sentencia T-279 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-279-26.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_27_2025` | Sentencia T-027 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-027-25.htm) | 2026-10-02 | — | 98 | Constitucional |
| `sentencia_t_280_2025` | Sentencia T-280 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-280-25.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_280_2026` | Sentencia T-280 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-280-26.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_281_2025` | Sentencia T-281 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-281-25.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_281_2026` | Sentencia T-281 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-281-26.htm) | 2026-10-02 | — | 189 | Constitucional |
| `sentencia_t_282_2025` | Sentencia T-282 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-282-25.htm) | 2026-10-02 | — | 34 | Constitucional |
| `sentencia_t_282_2026` | Sentencia T-282 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-282-26.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_t_283_2025` | Sentencia T-283 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-283-25.htm) | 2026-10-02 | — | 54 | Constitucional |
| `sentencia_t_284_2025` | Sentencia T-284 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-284-25.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_284_2026` | Sentencia T-284 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-284-26.htm) | 2026-10-02 | — | 134 | Constitucional |
| `sentencia_t_285_2025` | Sentencia T-285 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-285-25.htm) | 2026-10-02 | — | 69 | Constitucional |
| `sentencia_t_285_2026` | Sentencia T-285 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-285-26.htm) | 2026-10-02 | — | 121 | Constitucional |
| `sentencia_t_286_2025` | Sentencia T-286 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-286-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_287_2022` | Sentencia T-287 de 2022 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2022/T-287-22.htm) | 2026-10-03 | — | 70 | Constitucional |
| `sentencia_t_287_2025` | Sentencia T-287 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-287-25.htm) | 2026-10-02 | — | 105 | Constitucional |
| `sentencia_t_287_2026` | Sentencia T-287 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-287-26.htm) | 2026-10-02 | — | 26 | Constitucional |
| `sentencia_t_288_2025` | Sentencia T-288 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-288-25.htm) | 2026-10-02 | — | 134 | Constitucional |
| `sentencia_t_288_2026` | Sentencia T-288 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-288-26.htm) | 2026-10-02 | — | 98 | Constitucional |
| `sentencia_t_289_2025` | Sentencia T-289 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-289-25.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_28_2025` | Sentencia T-028 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-028-25.htm) | 2026-10-02 | — | 119 | Constitucional |
| `sentencia_t_290_2025` | Sentencia T-290 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-290-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_291_2025` | Sentencia T-291 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-291-25.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_293_2025` | Sentencia T-293 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-293-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_294_2025` | Sentencia T-294 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-294-25.htm) | 2026-10-02 | — | 51 | Constitucional |
| `sentencia_t_295_2025` | Sentencia T-295 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-295-25.htm) | 2026-10-02 | — | 51 | Constitucional |
| `sentencia_t_296_2025` | Sentencia T-296 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-296-25.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_t_299_2025` | Sentencia T-299 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-299-25.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_29_2025` | Sentencia T-029 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-029-25.htm) | 2026-10-02 | — | 105 | Constitucional |
| `sentencia_t_2_1992` | Sentencia T-002 de 1992 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1992/T-002-92.htm) | 2026-10-02 | — | 27 | Constitucional |
| `sentencia_t_2_2025` | Sentencia T-002 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-002-25.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_2_2026` | Sentencia T-002 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-002-26.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_300_2025` | Sentencia T-300 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-300-25.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_301_2025` | Sentencia T-301 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-301-25.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_301_2026` | Sentencia T-301 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-301-26.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_t_302_2025` | Sentencia T-302 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-302-25.htm) | 2026-10-02 | — | 230 | Constitucional |
| `sentencia_t_302_2026` | Sentencia T-302 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-302-26.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_t_303_2025` | Sentencia T-303 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-303-25.htm) | 2026-10-02 | — | 121 | Constitucional |
| `sentencia_t_303_2026` | Sentencia T-303 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-303-26.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_304_2025` | Sentencia T-304 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-304-25.htm) | 2026-10-02 | — | 32 | Constitucional |
| `sentencia_t_304_2026` | Sentencia T-304 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-304-26.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_t_305_2025` | Sentencia T-305 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-305-25.htm) | 2026-10-02 | — | 100 | Constitucional |
| `sentencia_t_306_2025` | Sentencia T-306 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-306-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_307_2025` | Sentencia T-307 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-307-25.htm) | 2026-10-02 | — | 64 | Constitucional |
| `sentencia_t_308_2025` | Sentencia T-308 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-308-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_309_2025` | Sentencia T-309 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-309-25.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_t_30_2025` | Sentencia T-030 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-030-25.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_t_310_2025` | Sentencia T-310 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-310-25.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_311_2025` | Sentencia T-311 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-311-25.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_t_312_2025` | Sentencia T-312 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-312-25.htm) | 2026-10-02 | — | 29 | Constitucional |
| `sentencia_t_313_2025` | Sentencia T-313 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-313-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_314_2025` | Sentencia T-314 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-314-25.htm) | 2026-10-02 | — | 104 | Constitucional |
| `sentencia_t_318_2025` | Sentencia T-318 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-318-25.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_319_2025` | Sentencia T-319 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-319-25.htm) | 2026-10-02 | — | 92 | Constitucional |
| `sentencia_t_31_2026` | Sentencia T-031 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-031-26.htm) | 2026-10-02 | — | 125 | Constitucional |
| `sentencia_t_320_2025` | Sentencia T-320 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-320-25.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_321_2025` | Sentencia T-321 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-321-25.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_322_2025` | Sentencia T-322 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-322-25.htm) | 2026-10-02 | — | 27 | Constitucional |
| `sentencia_t_324_2025` | Sentencia T-324 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-324-25.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_329_2025` | Sentencia T-329 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-329-25.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_32_2026` | Sentencia T-032 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-032-26.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_330_2025` | Sentencia T-330 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-330-25.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_t_331_2025` | Sentencia T-331 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-331-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_333_2025` | Sentencia T-333 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-333-25.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_334_2025` | Sentencia T-334 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-334-25.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_t_335_2025` | Sentencia T-335 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-335-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_336_2025` | Sentencia T-336 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-336-25.htm) | 2026-10-02 | — | 37 | Constitucional |
| `sentencia_t_337_2025` | Sentencia T-337 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-337-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_33_2025` | Sentencia T-033 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-033-25.htm) | 2026-10-02 | — | 34 | Constitucional |
| `sentencia_t_341_2025` | Sentencia T-341 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-341-25.htm) | 2026-10-02 | — | 103 | Constitucional |
| `sentencia_t_342_2025` | Sentencia T-342 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-342-25.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_343_2025` | Sentencia T-343 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-343-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_344_2025` | Sentencia T-344 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-344-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_345_2025` | Sentencia T-345 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-345-25.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_346_2025` | Sentencia T-346 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-346-25.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_t_347_2025` | Sentencia T-347 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-347-25.htm) | 2026-10-02 | — | 104 | Constitucional |
| `sentencia_t_348_2025` | Sentencia T-348 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-348-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_349_2025` | Sentencia T-349 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-349-25.htm) | 2026-10-02 | — | 144 | Constitucional |
| `sentencia_t_34_2025` | Sentencia T-034 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-034-25.htm) | 2026-10-02 | — | 46 | Constitucional |
| `sentencia_t_351_2025` | Sentencia T-351 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-351-25.htm) | 2026-10-02 | — | 151 | Constitucional |
| `sentencia_t_352_2025` | Sentencia T-352 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-352-25.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_353_2025` | Sentencia T-353 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-353-25.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_t_354_2025` | Sentencia T-354 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-354-25.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_355_2025` | Sentencia T-355 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-355-25.htm) | 2026-10-02 | — | 110 | Constitucional |
| `sentencia_t_356_2025` | Sentencia T-356 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-356-25.htm) | 2026-10-02 | — | 89 | Constitucional |
| `sentencia_t_357_2025` | Sentencia T-357 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-357-25.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_358_2025` | Sentencia T-358 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-358-25.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_359_2025` | Sentencia T-359 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-359-25.htm) | 2026-10-02 | — | 126 | Constitucional |
| `sentencia_t_35_2025` | Sentencia T-035 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-035-25.htm) | 2026-10-02 | — | 33 | Constitucional |
| `sentencia_t_360_2025` | Sentencia T-360 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-360-25.htm) | 2026-10-02 | — | 72 | Constitucional |
| `sentencia_t_361_2025` | Sentencia T-361 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-361-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_362_2025` | Sentencia T-362 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-362-25.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_t_363_2025` | Sentencia T-363 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-363-25.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_370_2025` | Sentencia T-370 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-370-25.htm) | 2026-10-02 | — | 28 | Constitucional |
| `sentencia_t_371_2025` | Sentencia T-371 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-371-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_372_2025` | Sentencia T-372 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-372-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_373_2025` | Sentencia T-373 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-373-25.htm) | 2026-10-02 | — | 112 | Constitucional |
| `sentencia_t_375_2025` | Sentencia T-375 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-375-25.htm) | 2026-10-02 | — | 169 | Constitucional |
| `sentencia_t_376_2025` | Sentencia T-376 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-376-25.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_377_2025` | Sentencia T-377 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-377-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_378_2025` | Sentencia T-378 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-378-25.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_379_2025` | Sentencia T-379 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-379-25.htm) | 2026-10-02 | — | 49 | Constitucional |
| `sentencia_t_380_2025` | Sentencia T-380 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-380-25.htm) | 2026-10-02 | — | 54 | Constitucional |
| `sentencia_t_386_2025` | Sentencia T-386 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-386-25.htm) | 2026-10-02 | — | 84 | Constitucional |
| `sentencia_t_387_2025` | Sentencia T-387 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-387-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_388_2013` | Sentencia T-388 de 2013 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2013/T-388-13.htm) | 2026-10-02 | — | 1.265 | Constitucional, Penal |
| `sentencia_t_388_2025` | Sentencia T-388 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-388-25.htm) | 2026-10-02 | — | 140 | Constitucional |
| `sentencia_t_389_2025` | Sentencia T-389 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-389-25.htm) | 2026-10-02 | — | 103 | Constitucional |
| `sentencia_t_390_2025` | Sentencia T-390 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-390-25.htm) | 2026-10-02 | — | 357 | Constitucional |
| `sentencia_t_391_2025` | Sentencia T-391 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-391-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_392_2025` | Sentencia T-392 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-392-25.htm) | 2026-10-02 | — | 51 | Constitucional |
| `sentencia_t_393_2025` | Sentencia T-393 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-393-25.htm) | 2026-10-02 | — | 72 | Constitucional |
| `sentencia_t_394_2025` | Sentencia T-394 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-394-25.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_395_2025` | Sentencia T-395 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-395-25.htm) | 2026-10-02 | — | 165 | Constitucional |
| `sentencia_t_396_2025` | Sentencia T-396 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-396-25.htm) | 2026-10-02 | — | 153 | Constitucional |
| `sentencia_t_397_2025` | Sentencia T-397 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-397-25.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_t_398_2025` | Sentencia T-398 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-398-25.htm) | 2026-10-02 | — | 35 | Constitucional |
| `sentencia_t_399_2025` | Sentencia T-399 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-399-25.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_3_2025` | Sentencia T-003 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-003-25.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_3_2026` | Sentencia T-003 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-003-26.htm) | 2026-10-02 | — | 114 | Constitucional |
| `sentencia_t_400_2025` | Sentencia T-400 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-400-25.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_401_2025` | Sentencia T-401 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-401-25.htm) | 2026-10-02 | — | 53 | Constitucional |
| `sentencia_t_402_2025` | Sentencia T-402 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-402-25.htm) | 2026-10-02 | — | 65 | Constitucional |
| `sentencia_t_403_2025` | Sentencia T-403 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-403-25.htm) | 2026-10-02 | — | 138 | Constitucional |
| `sentencia_t_404_2025` | Sentencia T-404 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-404-25.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_406_1992` | Sentencia T-406 de 1992 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/1992/T-406-92.htm) | 2026-10-02 | — | 52 | Constitucional |
| `sentencia_t_406_2025` | Sentencia T-406 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-406-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_408_2025` | Sentencia T-408 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-408-25.htm) | 2026-10-02 | — | 40 | Constitucional |
| `sentencia_t_40_2025` | Sentencia T-040 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-040-25.htm) | 2026-10-02 | — | 115 | Constitucional |
| `sentencia_t_414_2025` | Sentencia T-414 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-414-25.htm) | 2026-10-02 | — | 69 | Constitucional |
| `sentencia_t_415_2025` | Sentencia T-415 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-415-25.htm) | 2026-10-02 | — | 142 | Constitucional |
| `sentencia_t_416_2025` | Sentencia T-416 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-416-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_418_2025` | Sentencia T-418 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-418-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_419_2025` | Sentencia T-419 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-419-25.htm) | 2026-10-02 | — | 56 | Constitucional |
| `sentencia_t_41_2025` | Sentencia T-041 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-041-25.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_t_41_2026` | Sentencia T-041 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-041-26.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_420_2025` | Sentencia T-420 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-420-25.htm) | 2026-10-02 | — | 333 | Constitucional |
| `sentencia_t_421_2025` | Sentencia T-421 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-421-25.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_422_2025` | Sentencia T-422 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-422-25.htm) | 2026-10-02 | — | 34 | Constitucional |
| `sentencia_t_423_2025` | Sentencia T-423 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-423-25.htm) | 2026-10-02 | — | 69 | Constitucional |
| `sentencia_t_426_2003` | Sentencia T-426 de 2003 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2003/T-426-03.htm) | 2026-10-03 | — | 28 | Constitucional |
| `sentencia_t_42_2025` | Sentencia T-042 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-042-25.htm) | 2026-10-02 | — | 129 | Constitucional |
| `sentencia_t_42_2026` | Sentencia T-042 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-042-26.htm) | 2026-10-02 | — | 105 | Constitucional |
| `sentencia_t_430_2025` | Sentencia T-430 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-430-25.htm) | 2026-10-02 | — | 43 | Constitucional |
| `sentencia_t_433_2025` | Sentencia T-433 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-433-25.htm) | 2026-10-02 | — | 73 | Constitucional |
| `sentencia_t_434_2025` | Sentencia T-434 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-434-25.htm) | 2026-10-02 | — | 98 | Constitucional |
| `sentencia_t_435_2025` | Sentencia T-435 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-435-25.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_t_436_2025` | Sentencia T-436 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-436-25.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_437_2025` | Sentencia T-437 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-437-25.htm) | 2026-10-02 | — | 93 | Constitucional |
| `sentencia_t_438_2025` | Sentencia T-438 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-438-25.htm) | 2026-10-02 | — | 124 | Constitucional |
| `sentencia_t_439_2025` | Sentencia T-439 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-439-25.htm) | 2026-10-02 | — | 152 | Constitucional |
| `sentencia_t_43_2025` | Sentencia T-043 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-043-25.htm) | 2026-10-02 | — | 42 | Constitucional |
| `sentencia_t_43_2026` | Sentencia T-043 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-043-26.htm) | 2026-10-02 | — | 149 | Constitucional |
| `sentencia_t_440_2025` | Sentencia T-440 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-440-25.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_t_441_2025` | Sentencia T-441 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-441-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_442_2025` | Sentencia T-442 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-442-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_449_2025` | Sentencia T-449 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-449-25.htm) | 2026-10-02 | — | 78 | Constitucional |
| `sentencia_t_44_2025` | Sentencia T-044 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-044-25.htm) | 2026-10-02 | — | 37 | Constitucional |
| `sentencia_t_44_2026` | Sentencia T-044 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-044-26.htm) | 2026-10-02 | — | 130 | Constitucional |
| `sentencia_t_450_2025` | Sentencia T-450 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-450-25.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_t_451_2025` | Sentencia T-451 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-451-25.htm) | 2026-10-02 | — | 77 | Constitucional |
| `sentencia_t_452_2025` | Sentencia T-452 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-452-25.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_t_453_2025` | Sentencia T-453 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-453-25.htm) | 2026-10-02 | — | 83 | Constitucional |
| `sentencia_t_455_2025` | Sentencia T-455 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-455-25.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_456_2024` | Sentencia T-456 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-456-24.htm) | 2026-10-03 | — | 79 | Laboral |
| `sentencia_t_456_2025` | Sentencia T-456 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-456-25.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_457_2025` | Sentencia T-457 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-457-25.htm) | 2026-10-02 | — | 72 | Constitucional |
| `sentencia_t_458_2025` | Sentencia T-458 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-458-25.htm) | 2026-10-02 | — | 74 | Constitucional |
| `sentencia_t_459_2025` | Sentencia T-459 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-459-25.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_t_45_2025` | Sentencia T-045 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-045-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_460_2025` | Sentencia T-460 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-460-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_461_2025` | Sentencia T-461 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-461-25.htm) | 2026-10-02 | — | 58 | Constitucional |
| `sentencia_t_462_2025` | Sentencia T-462 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-462-25.htm) | 2026-10-02 | — | 111 | Constitucional |
| `sentencia_t_463_2025` | Sentencia T-463 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-463-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_469_2025` | Sentencia T-469 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-469-25.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_46_2025` | Sentencia T-046 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-046-25.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_46_2026` | Sentencia T-046 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-046-26.htm) | 2026-10-02 | — | 59 | Constitucional |
| `sentencia_t_470_2025` | Sentencia T-470 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-470-25.htm) | 2026-10-02 | — | 54 | Constitucional |
| `sentencia_t_471_2025` | Sentencia T-471 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-471-25.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_t_472_2025` | Sentencia T-472 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-472-25.htm) | 2026-10-02 | — | 170 | Constitucional |
| `sentencia_t_473_2025` | Sentencia T-473 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-473-25.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_474_2025` | Sentencia T-474 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-474-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_475_2025` | Sentencia T-475 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-475-25.htm) | 2026-10-02 | — | 131 | Constitucional |
| `sentencia_t_476_2025` | Sentencia T-476 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-476-25.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_t_47_2025` | Sentencia T-047 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-047-25.htm) | 2026-10-02 | — | 63 | Constitucional |
| `sentencia_t_481_2025` | Sentencia T-481 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-481-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_482_2025` | Sentencia T-482 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-482-25.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_483_2025` | Sentencia T-483 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-483-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_484_2025` | Sentencia T-484 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-484-25.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_485_2025` | Sentencia T-485 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-485-25.htm) | 2026-10-02 | — | 90 | Constitucional |
| `sentencia_t_486_2025` | Sentencia T-486 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-486-25.htm) | 2026-10-02 | — | 80 | Constitucional |
| `sentencia_t_487_2025` | Sentencia T-487 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-487-25.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_488_2025` | Sentencia T-488 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-488-25.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_489_2025` | Sentencia T-489 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-489-25.htm) | 2026-10-02 | — | 147 | Constitucional |
| `sentencia_t_48_2025` | Sentencia T-048 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-048-25.htm) | 2026-10-02 | — | 24 | Constitucional |
| `sentencia_t_490_2025` | Sentencia T-490 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-490-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_491_2025` | Sentencia T-491 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-491-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_496_2025` | Sentencia T-496 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-496-25.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_497_2025` | Sentencia T-497 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-497-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_498_2025` | Sentencia T-498 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-498-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_499_2025` | Sentencia T-499 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-499-25.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_t_49_2025` | Sentencia T-049 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-049-25.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_t_4_2016` | Sentencia T-4 de 2016 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2016/T-004-16.htm) | 2026-10-03 | — | 25 | Familia |
| `sentencia_t_4_2025` | Sentencia T-004 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-004-25.htm) | 2026-10-02 | — | 94 | Constitucional |
| `sentencia_t_500_2025` | Sentencia T-500 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-500-25.htm) | 2026-10-02 | — | 141 | Constitucional |
| `sentencia_t_501_2025` | Sentencia T-501 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-501-25.htm) | 2026-10-02 | — | 105 | Constitucional |
| `sentencia_t_507_2025` | Sentencia T-507 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-507-25.htm) | 2026-10-02 | — | 120 | Constitucional |
| `sentencia_t_508_2025` | Sentencia T-508 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-508-25.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_509_2025` | Sentencia T-509 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-509-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_50_2025` | Sentencia T-050 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-050-25.htm) | 2026-10-02 | — | 225 | Constitucional |
| `sentencia_t_510_2025` | Sentencia T-510 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-510-25.htm) | 2026-10-02 | — | 194 | Constitucional |
| `sentencia_t_511_2025` | Sentencia T-511 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-511-25.htm) | 2026-10-02 | — | 50 | Constitucional |
| `sentencia_t_512_2025` | Sentencia T-512 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-512-25.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_513_2025` | Sentencia T-513 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-513-25.htm) | 2026-10-02 | — | 104 | Constitucional |
| `sentencia_t_514_2025` | Sentencia T-514 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-514-25.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_515_2025` | Sentencia T-515 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-515-25.htm) | 2026-10-02 | — | 128 | Constitucional |
| `sentencia_t_516_2025` | Sentencia T-516 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-516-25.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_t_517_2025` | Sentencia T-517 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-517-25.htm) | 2026-10-02 | — | 145 | Constitucional |
| `sentencia_t_518_2025` | Sentencia T-518 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-518-25.htm) | 2026-10-02 | — | 139 | Constitucional |
| `sentencia_t_519_2025` | Sentencia T-519 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-519-25.htm) | 2026-10-02 | — | 30 | Constitucional |
| `sentencia_t_51_2026` | Sentencia T-051 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-051-26.htm) | 2026-10-02 | — | 112 | Constitucional |
| `sentencia_t_520_2025` | Sentencia T-520 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-520-25.htm) | 2026-10-02 | — | 182 | Constitucional |
| `sentencia_t_521_2025` | Sentencia T-521 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-521-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_522_2025` | Sentencia T-522 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-522-25.htm) | 2026-10-02 | — | 124 | Constitucional |
| `sentencia_t_523_2025` | Sentencia T-523 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-523-25.htm) | 2026-10-02 | — | 116 | Constitucional |
| `sentencia_t_524_2025` | Sentencia T-524 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-524-25.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_525_2025` | Sentencia T-525 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-525-25.htm) | 2026-10-02 | — | 227 | Constitucional |
| `sentencia_t_526_2025` | Sentencia T-526 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-526-25.htm) | 2026-10-02 | — | 101 | Constitucional |
| `sentencia_t_527_2025` | Sentencia T-527 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-527-25.htm) | 2026-10-02 | — | 108 | Constitucional |
| `sentencia_t_528_2025` | Sentencia T-528 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-528-25.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_529_2025` | Sentencia T-529 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-529-25.htm) | 2026-10-02 | — | 99 | Constitucional |
| `sentencia_t_52_2026` | Sentencia T-052 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-052-26.htm) | 2026-10-02 | — | 114 | Constitucional |
| `sentencia_t_53_2025` | Sentencia T-053 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-053-25.htm) | 2026-10-02 | — | 23 | Constitucional |
| `sentencia_t_53_2026` | Sentencia T-053 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-053-26.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_54_2026` | Sentencia T-054 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-054-26.htm) | 2026-10-02 | — | 133 | Constitucional |
| `sentencia_t_55_2026` | Sentencia T-055 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-055-26.htm) | 2026-10-02 | — | 82 | Constitucional |
| `sentencia_t_56_2026` | Sentencia T-056 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-056-26.htm) | 2026-10-02 | — | 91 | Constitucional |
| `sentencia_t_57_2025` | Sentencia T-057 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-057-25.htm) | 2026-10-02 | — | 165 | Constitucional |
| `sentencia_t_57_2026` | Sentencia T-057 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-057-26.htm) | 2026-10-02 | — | 37 | Constitucional |
| `sentencia_t_58_2025` | Sentencia T-058 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-058-25.htm) | 2026-10-02 | — | 100 | Constitucional |
| `sentencia_t_58_2026` | Sentencia T-058 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-058-26.htm) | 2026-10-02 | — | 44 | Constitucional |
| `sentencia_t_59_2025` | Sentencia T-059 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-059-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_59_2026` | Sentencia T-059 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-059-26.htm) | 2026-10-02 | — | 148 | Constitucional |
| `sentencia_t_5_2025` | Sentencia T-005 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-005-25.htm) | 2026-10-02 | — | 39 | Constitucional |
| `sentencia_t_60_2025` | Sentencia T-060 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-060-25.htm) | 2026-10-02 | — | 208 | Constitucional |
| `sentencia_t_617_2010` | Sentencia T-617 de 2010 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2010/T-617-10.htm) | 2026-10-03 | — | 170 | Constitucional |
| `sentencia_t_61_2025` | Sentencia T-061 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-061-25.htm) | 2026-10-02 | — | 52 | Constitucional |
| `sentencia_t_61_2026` | Sentencia T-061 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-061-26.htm) | 2026-10-02 | — | 112 | Constitucional |
| `sentencia_t_62_2025` | Sentencia T-062 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-062-25.htm) | 2026-10-02 | — | 68 | Constitucional |
| `sentencia_t_64_2025` | Sentencia T-064 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-064-25.htm) | 2026-10-02 | — | 55 | Constitucional |
| `sentencia_t_65_2025` | Sentencia T-065 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-065-25.htm) | 2026-10-02 | — | 75 | Constitucional |
| `sentencia_t_66_2025` | Sentencia T-066 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-066-25.htm) | 2026-10-02 | — | 90 | Constitucional |
| `sentencia_t_68_2025` | Sentencia T-068 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-068-25.htm) | 2026-10-02 | — | 29 | Constitucional |
| `sentencia_t_69_2026` | Sentencia T-069 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-069-26.htm) | 2026-10-02 | — | 76 | Constitucional |
| `sentencia_t_6_2025` | Sentencia T-006 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-006-25.htm) | 2026-10-02 | — | 62 | Constitucional |
| `sentencia_t_70_2026` | Sentencia T-070 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-070-26.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_71_2026` | Sentencia T-071 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-071-26.htm) | 2026-10-02 | — | 42 | Constitucional |
| `sentencia_t_72_2026` | Sentencia T-072 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-072-26.htm) | 2026-10-02 | — | 144 | Constitucional |
| `sentencia_t_73_2025` | Sentencia T-073 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-073-25.htm) | 2026-10-02 | — | 100 | Constitucional |
| `sentencia_t_74_2025` | Sentencia T-074 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-074-25.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_t_75_2025` | Sentencia T-075 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-075-25.htm) | 2026-10-02 | — | 61 | Constitucional |
| `sentencia_t_762_2015` | Sentencia T-762 de 2015 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2015/T-762-15.htm) | 2026-10-02 | — | 344 | Constitucional, Penal |
| `sentencia_t_76_2026` | Sentencia T-076 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-076-26.htm) | 2026-10-02 | — | 79 | Constitucional |
| `sentencia_t_77_2026` | Sentencia T-077 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-077-26.htm) | 2026-10-02 | — | 122 | Constitucional |
| `sentencia_t_78_2025` | Sentencia T-078 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-078-25.htm) | 2026-10-02 | — | 205 | Constitucional |
| `sentencia_t_78_2026` | Sentencia T-078 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-078-26.htm) | 2026-10-02 | — | 130 | Constitucional |
| `sentencia_t_79_2024` | Sentencia T-79 de 2024 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2024/T-079-24.htm) | 2026-10-03 | — | 31 | Constitucional |
| `sentencia_t_7_2025` | Sentencia T-007 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-007-25.htm) | 2026-10-02 | — | 96 | Constitucional |
| `sentencia_t_81_2025` | Sentencia T-081 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-081-25.htm) | 2026-10-02 | — | 121 | Constitucional |
| `sentencia_t_82_2025` | Sentencia T-082 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-082-25.htm) | 2026-10-02 | — | 186 | Constitucional |
| `sentencia_t_83_2025` | Sentencia T-083 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-083-25.htm) | 2026-10-02 | — | 105 | Constitucional |
| `sentencia_t_83_2026` | Sentencia T-083 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-083-26.htm) | 2026-10-02 | — | 97 | Constitucional |
| `sentencia_t_84_2025` | Sentencia T-084 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-084-25.htm) | 2026-10-02 | — | 103 | Constitucional |
| `sentencia_t_84_2026` | Sentencia T-084 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-084-26.htm) | 2026-10-02 | — | 172 | Constitucional |
| `sentencia_t_85_2025` | Sentencia T-085 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-085-25.htm) | 2026-10-02 | — | 70 | Constitucional |
| `sentencia_t_86_2026` | Sentencia T-086 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-086-26.htm) | 2026-10-02 | — | 209 | Constitucional |
| `sentencia_t_87_2026` | Sentencia T-087 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-087-26.htm) | 2026-10-02 | — | 71 | Constitucional |
| `sentencia_t_881_2002` | Sentencia T-881 de 2002 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2002/T-881-02.htm) | 2026-10-02 | — | 95 | Constitucional |
| `sentencia_t_88_2026` | Sentencia T-088 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-088-26.htm) | 2026-10-02 | — | 89 | Constitucional |
| `sentencia_t_89_2025` | Sentencia T-089 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-089-25.htm) | 2026-10-02 | — | 67 | Constitucional |
| `sentencia_t_89_2026` | Sentencia T-089 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-089-26.htm) | 2026-10-02 | — | 113 | Constitucional |
| `sentencia_t_8_2025` | Sentencia T-008 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-008-25.htm) | 2026-10-02 | — | 88 | Constitucional |
| `sentencia_t_8_2026` | Sentencia T-008 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-008-26.htm) | 2026-10-02 | — | 173 | Constitucional |
| `sentencia_t_90_2025` | Sentencia T-090 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-090-25.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_90_2026` | Sentencia T-090 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-090-26.htm) | 2026-10-02 | — | 72 | Constitucional |
| `sentencia_t_91_2025` | Sentencia T-091 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-091-25.htm) | 2026-10-02 | — | 48 | Constitucional |
| `sentencia_t_91_2026` | Sentencia T-091 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-091-26.htm) | 2026-10-02 | — | 221 | Constitucional |
| `sentencia_t_92_2025` | Sentencia T-092 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-092-25.htm) | 2026-10-02 | — | 87 | Constitucional |
| `sentencia_t_92_2026` | Sentencia T-092 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-092-26.htm) | 2026-10-02 | — | 86 | Constitucional |
| `sentencia_t_93_2025` | Sentencia T-093 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-093-25.htm) | 2026-10-02 | — | 66 | Constitucional |
| `sentencia_t_93_2026` | Sentencia T-093 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-093-26.htm) | 2026-10-02 | — | 88 | Constitucional |
| `sentencia_t_94_2025` | Sentencia T-094 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-094-25.htm) | 2026-10-02 | — | 104 | Constitucional |
| `sentencia_t_94_2026` | Sentencia T-094 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-094-26.htm) | 2026-10-02 | — | 117 | Constitucional |
| `sentencia_t_95_2025` | Sentencia T-095 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-095-25.htm) | 2026-10-02 | — | 60 | Constitucional |
| `sentencia_t_95_2026` | Sentencia T-095 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-095-26.htm) | 2026-10-02 | — | 65 | Constitucional |
| `sentencia_t_96_2025` | Sentencia T-096 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-096-25.htm) | 2026-10-02 | — | 57 | Constitucional |
| `sentencia_t_96_2026` | Sentencia T-096 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-096-26.htm) | 2026-10-02 | — | 41 | Constitucional |
| `sentencia_t_9_2025` | Sentencia T-009 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/T-009-25.htm) | 2026-10-02 | — | 81 | Constitucional |
| `sentencia_t_9_2026` | Sentencia T-009 de 2026 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2026/T-009-26.htm) | 2026-10-02 | — | 102 | Constitucional |

**Objetivos de la semilla sin documento propio (21, 3 erratas).** Las erratas son referencias mal escritas del banco que apuntan a un documento ya incorporado; el resto quedó sin descargar. El detalle está en `data/registros/fuentes_descargadas.json`.

| doc_id | Estado | Motivo |
|---|---|---|
| `ley_11500_2007` | errata | errata de la semilla: es la Ley 1150 de 2007, ya en el corpus como ley_1150_2007 |
| `ley_1150_2005` | errata | errata de la semilla: la Ley 1150 es de 2007, ya en el corpus como ley_1150_2007 |
| `ley_116_2006` | errata | errata de la semilla: probablemente la Ley 1116 de 2006 (insolvencia), ya en el corpus como ley_1116_2006 |
| `decreto_1066_2015` | error | ampliacion v5: descartado por tamano (1167 articulos > 400) |
| `decreto_1067_2015` | error | ampliacion v5: descartado por tamano (457 articulos > 400) |
| `decreto_1075_2015` | error | ampliacion v5: descartado por tamano (2084 articulos > 400) |
| `decreto_1076_2015` | error | ampliacion v5: descartado por tamano (2146 articulos > 400) |
| `decreto_1077_2015` | error | ampliacion v5: descartado por tamano (1977 articulos > 400) |
| `decreto_1084_2015` | error | ampliacion v5: descartado por tamano (592 articulos > 400) |
| `decreto_1833_2016` | error | ampliacion v5: descartado por tamano (1792 articulos > 400) |
| `ley_1450_2011` | error | ampliacion v5: retirado tras r40_corpus_v5 (Plan Nacional de Desarrollo 2010-2014: ley omnibus que satura el top-10; 276 articulos) |
| `ley_1753_2015` | error | ampliacion v5: retirado tras r40_corpus_v5 (Plan Nacional de Desarrollo 2014-2018: ley omnibus que satura el top-10; 268 articulos) |
| `ley_1955_2019` | error | ampliacion v5: retirado tras r40_corpus_v5 (Plan Nacional de Desarrollo 2018-2022: ley omnibus que satura el top-10; 406 articulos) |
| `ley_2294_2023` | error | ampliacion v5: retirado tras r40_corpus_v5 (Plan Nacional de Desarrollo 2022-2026: ley omnibus que satura el top-10; 500 articulos) |
| `decreto_100_1980` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/decreto_0100_1980.html no existe en Secretaria del Senado |
| `decreto_1421_2017` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/decreto_1421_2017.html no existe en Secretaria del Senado |
| `decreto_2700_1991` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/decreto_2700_1991.html no existe en Secretaria del Senado |
| `decreto_3030_2022` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/decreto_3030_2022.html no existe en Secretaria del Senado |
| `ley_1264_2012` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/ley_1264_2012.html no existe en Secretaria del Senado |
| `ley_2568_2021` | no_encontrado | http://www.secretariasenado.gov.co/senado/basedoc/ley_2568_2021.html no existe en Secretaria del Senado |
| `sentencia_su_279_2019` | no_encontrado | https://www.corteconstitucional.gov.co/relatoria/2019/SU279-19.htm no existe en Relatoria de la Corte Constitucional |

<!-- inventario:fin -->

**Totales**

| Métrica | Valor |
|---|---:|
| Documentos incorporados | 1.285 (985 sentencias, 300 normas y documentos no normativos) |
| Artículos indexados | 40.494 (291 documentos con articulado) |
| Fragmentos en el índice | 185.234 |
| Tamaño del corpus procesado | 262 MB (1.285 archivos `.txt`) |
| Tamaño del índice vectorial | 1,5 GB sin comprimir: `index.faiss` 759 MB, `chunks.jsonl` 747 MB, `bm25/` 168 MB |

## 2. Criterio de selección

La selección se dirigió por la **demanda del banco** (enunciado, sección 4.2) y no por comodidad. Se partió de la semilla `data/registros/seed_targets.json` (186 objetivos ordenados por ítems del banco: Constitución, CGP, CST, Estatuto Tributario, Decisión Andina 486…), se agregaron las fuentes que la semilla no cubría (códigos Civil, de Comercio y Penal, CPACA, Ley 472 de 1998) y después se amplió con ampliaciones **automáticas** (sin búsqueda manual): normas de las áreas con menos cobertura, Decisiones Andinas, sentencias C- de control, tutelas 2025–2026 y las normas que el propio corpus cita y no tenía. El sábado, con la autorización de la organización, la ampliación se dirigió además por los cuerpos normativos que nombran las preguntas (solo `pregunta` y `opciones`, nunca respuestas ni `legal_basis`).

Un documento puede tener varias áreas. Las cifras son las del manifest v5.

| Área | Ítems en el banco | Documentos incorporados | Fragmentos | Cobertura estimada |
|---|---:|---:|---:|---|
| Derecho constitucional | 134 | 935 | 128.160 | Alta: Constitución, sentencias C-, T- y SU, tutelas 2025–2026. Es el área sobrerrepresentada, por eso la recuperación aplica prioridad por área. |
| Derecho administrativo | 124 | 92 | 14.228 | Buena en normas (CPACA, Leyes 80 y 1150, decretos únicos reglamentarios); sin doctrina ni circulares. |
| Derecho penal | 123 | 65 | 20.490 | Buena: Código Penal, CPP, leyes especiales y sentencias de control. |
| Derecho procesal | 111 | 48 | 8.499 | Media: CGP, CPACA, CPT, arbitraje y conciliación. |
| Derecho comercial y sociedades | 104 | 40 | 9.051 | Media: Código de Comercio y leyes societarias y de insolvencia; sin doctrina. |
| Derecho civil | 102 | 50 | 10.771 | Media: Código Civil, Ley 153, Estatuto del Consumidor y sentencias de la CSJ. |
| Derecho de familia | 93 | 62 | 10.138 | Buena: Código de la Infancia, uniones maritales y sentencias de control. |
| Derecho tributario | 92 | 50 | 14.631 | Buena en el Estatuto Tributario y el DUR 1625; sin doctrina de la DIAN ni modelo de convenio de la OCDE. |
| Derecho laboral | 87 | 81 | 9.899 | Buena: CST, Ley 50/1990, reformas de 2025, DUR 1072 y sentencias de la CSJ. |
| Derecho de los mercados | 72 | 39 | 7.160 | Media: Decisión 486, Estatuto del Consumidor, Ley 1581 y competencia; sin circulares de la SIC. |

**Documentos descartados.**

- **Cuatro Planes Nacionales de Desarrollo** (Leyes 2294/2023, 1955/2019, 1753/2015 y 1450/2011): leyes ómnibus que tocan cualquier tema y desplazaban a la norma correcta del top-10 (`docs/INDEXACION.md`, sección 18).
- **Siete decretos únicos reglamentarios** de más de 400 artículos, por tamaño y ruido de recuperación (`docs/ingesta/fuentes_pendientes.md`, "Ampliación v5").
- **Doctrina con derechos de autor**: no se incluye (licencia CC-BY-4.0 del corpus). Solo entran los documentos no normativos decididos el 2026-10-01.
- **Circulares y resoluciones administrativas** (SIC, Superintendencia Financiera) y sentencias de la Corte Suprema anteriores a 2016: no hay URLs predecibles ni descarga automática; quedan como limitación.

## 3. Método de ingesta y limpieza

1. **Descarga.** `src/ingesta/descargar_fuentes.py` (solo biblioteca estándar de
   Python) recorre los 186 objetivos de `data/registros/seed_targets.json` en orden de ítems
   del banco. Como la semilla solo trae URLs de búsqueda, cada objetivo se resuelve
   con reglas deterministas a la URL del documento: normas en la Secretaría del
   Senado (`basedoc/ley_NNNN_AAAA.html` más todas sus partes `_prNNN.html`),
   sentencias C/T/SU en la relatoría de la Corte Constitucional
   (`relatoria/AAAA/C-NNN-AA.htm`) y la Decisión Andina 486 en el PDF oficial de la
   Comunidad Andina. Los originales se guardan sin modificar en
   `data/raw_sources/<tipo>/<doc_id>/`, clasificados por tipo de archivo (`html`,
   `pdf`, `pdf_escaneado`, `otros`), con pausa de 1 s entre peticiones. Dieciocho
   documentos de mayor impacto no se descargan con el script: sus PDF se obtienen a
   mano del Gestor Normativo de Función Pública, del ICBF, de la SUIT o de RedJurista
   (enlaces en `docs/ingesta/referencias_normativas.md`) para controlar la calidad del dato, y
   el script solo los registra con esa fuente (`data/registros/fuentes_override.json`). Trece son
   objetivos de la semilla (Constitución, CGP, CST, ET, Estatuto del Consumidor, Código
   de la Infancia, Leyes 80/1993, 1116/2006, 1258/2008, 1581/2012 y 2220/2022, Decreto
   2153/1992 y sentencia SL3385 de 2022). Cinco son adicionales a la semilla, tomados de
   las fuentes del `legal_basis` de `sample_50` que la semilla no cubría (Código Civil,
   Código de Comercio, Código Penal, CPACA y Ley 472 de 1998; sección `_adicionales` del
   mismo archivo, con `doc_id` canónicos de `scripts/citations.py`). La URL real, la
   fecha de consulta, el estado y el sha256 de cada descarga quedan en
   `data/registros/fuentes_descargadas.json`, a partir del cual se genera el inventario de la
   sección 1.
2. **Extracción de texto.** `src/ingesta/parsear_html.py` (BeautifulSoup + lxml, un extractor por fuente: compilación de Avance Jurídico, relatoría de la Corte Constitucional), `parsear_pdf.py` (PyMuPDF; Tesseract 5 `spa` para los escaneados) y `parsear_rtf.py` (pandoc, RTF y DOCX). Si un documento tiene fuente nativa (RTF/DOCX) y PDF, se usa la nativa. El formato se detecta por contenido, no por extensión.
3. **Normalización.** `src/ingesta/_texto.py`, solo estructural: NFKC (ligaduras), encabezados y pies repetidos, guiones blandos, saltos de línea dentro de párrafo y tablas de pandoc. El contenido normativo no se reescribe; las notas de vigencia en línea (`<Artículo modificado por …>`, texto tachado) se conservan porque son hechos de la fuente.
4. **Segmentación.** `src/indexacion/segmentar.py` (versión `seg-v1`). En las normas
   (Constitución, códigos, leyes, decretos y Decisión 486) cada artículo es un fragmento.
   Los artículos de más de 350 palabras se parten por párrafos (incisos, parágrafos,
   numerales) en partes sin solapamiento, y el texto anterior al primer artículo forma
   su propio fragmento. Los encabezados se reconocen en todas sus variantes
   (`ARTÍCULO 1o.`, `Artículo 1°.`, `Artículo 1.-`, `ARTÍCULO 12-1.`, `ARTÍCULO 2.2.1.1.1.`,
   `ARTÍCULO TRANSITORIO 3.`). En las normas modificatorias, los artículos transcritos
   tras un "…quedará así:" se quedan dentro del artículo que los introduce. Las
   sentencias se parten en ventanas de ~350 palabras con párrafos completos, sin cruzar
   secciones (síntesis, antecedentes, consideraciones, resuelve, salvamento, aclaración).
   El conteo de artículos detectados se contrasta con `n_articulos` del manifest:
   coincide exactamente en la Constitución (380), el CGP (627), el CST (487), el ET
   (932), el Código Civil (2680), el Código de Comercio (2032) y la Decisión 486 (280).
5. **Extracción de metadatos.** Cada fragmento registra `doc_id`, tipo de norma,
   número, año, artículo, parte, ruta LIBRO/TÍTULO/CAPÍTULO, una señal de vigencia
   tomada de las notas en línea de la fuente (`modificado`, `derogado`, `inexequible`,
   `sin_nota`), la tupla canónica de la norma en el formato de `scripts/citations.py`,
   los offsets `inicio`/`fin` en `corpus/<doc_id>.txt` y la URL de origen.
6. **Indexación.** `src/indexacion/construir_indice.py`: índice léxico BM25 (`bm25s`,
   tokenizador sin tildes que conserva números de artículo como `2.2.1.1` o `240-1`) e
   índice denso con `BAAI/bge-m3` (licencia MIT, 1024 dimensiones, revisión fijada)
   en un `faiss.IndexFlatIP` exacto con vectores normalizados. La recuperación híbrida
   combina ambos por Reciprocal Rank Fusion.

**Problemas encontrados.**

- **Erratas de la semilla**: referencias mal escritas del banco (`decreto_1563_2012` es la Ley 1563 de 2012; `ley_11500_2007` es la Ley 1150 de 2007; `ley_1692_2017`, `ley_23_1961`…). Se corrigen en `data/registros/fuentes_override.json` y el corpus usa la identificación correcta.
- **Fuentes sin descarga automática**: SUIN-Juriscol es una aplicación Angular sin HTML y la relatoría de la Corte Suprema no tiene URLs predecibles. Esos documentos se bajaron a mano (PDF/RTF) y se registraron en `data/registros/mapa_archivos.json`; el resto de la ampliación fue automática.
- **PDF escaneados**: cinco sentencias y algunos PDF con capa OCR ilegible pasan por Tesseract 5 en español a 300 dpi (`OCR_FORZADO`). Se descartó Docling porque las sentencias son prosa a una columna y arrastra modelos de layout sin ganancia.
- **Formato real distinto de la extensión**: hay `.rtf` que son DOCX y PDF con bytes antes de `%PDF`; los parsers detectan el formato por contenido.
- **Normas modificatorias**: los artículos transcritos tras un "…quedará así:" no son artículos de la norma que los transcribe; se mantienen dentro del artículo que los introduce.
- **Ruido de las sentencias largas**: sin filtro desplazaban a los artículos. Las sentencias de las ampliaciones solo se recuperan si la pregunta las nombra (`solo_por_cita.json`) y las sentencias y normas derogadas van detrás de la norma vigente.
- **Leyes ómnibus**: los Planes Nacionales de Desarrollo bajaban la recuperación y se retiraron (sección 2).

**Decisiones de diseño relevantes.**

- **Encabezado citable en cada fragmento.** El evaluador considera respaldada una
  cita solo si la encuentra en el texto de alguno de los diez primeros pasajes
  recuperados. Un artículo aislado ("ARTÍCULO 42. Deberes del juez…") no nombra la
  norma a la que pertenece. Por eso cada fragmento empieza con una línea como
  "Artículo 42 del Código General del Proceso." o "Corte Constitucional, Sentencia
  C-355 de 2006.", seguida del texto literal. Se verifica automáticamente que el
  encabezado identifique exactamente la norma del documento, y los 185.234
  fragmentos quedan respaldados por su propia norma.
- **Encoder.** De los encoders sugeridos en el enunciado se descartó
  `jina-embeddings-v3` porque su licencia (CC-BY-NC-4.0) es incompatible con la
  CC-BY-4.0 del corpus publicado. Entre `bge-m3` y `multilingual-e5-large` se eligió
  `bge-m3`: admite textos de hasta 8192 tokens, y hay artículos del ET y del CST que
  superan los 512 de E5. Además no necesita los prefijos `query:`/`passage:`.
- **Identidad correcta sobre la semilla.** Tres objetivos de la semilla llegan con
  una norma mal citada en el propio banco ("Decreto 1563 de 2012", "Ley 2737 de 1989",
  "Ley 964 de 2006"). El corpus usa la identificación correcta (Ley 1563 de 2012,
  Decreto 2737 de 1989, Ley 964 de 2005).

- **Recuperación sobre el índice (no cambia el corpus).** Filtro "solo por cita" para las sentencias de las ampliaciones, prioridad ×2 por el área de la pregunta, metadatos (alias de normas desde los títulos del manifest, ×1,5 al cuerpo nombrado, sentencias y derogados detrás de la norma) y reranker `BAAI/bge-reranker-v2-m3` sobre los 20 primeros candidatos fusionado por RRF. Cada una se midió y se mantuvo solo si mejoraba (`docs/INDEXACION.md`, secciones 14–24).
- **Corpus v5 congelado.** El índice (`indice_info.json`, sha256 de `chunks.jsonl`) y los `.txt` (sha256 del manifest) no se modifican después de la entrega; la verificación en vivo corre con la caché del decoder apagada.

## 4. Evolución del puntaje

Autoevaluación con `scripts/evaluate.py` sobre `data/sample_50.jsonl` (Qwen3-8B, temperatura 0). Total sobre 50 puntos, sin juez de texto libre. El detalle por corrida está en `evaluation/experiments.csv`.

| Fecha | Documentos | Fragmentos | Cerradas /20 | Citación /20 | Abstención /10 | Total /50 | Qué cambió |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-10-02 | 588 | 113.519 | 14,67 | 14,69 | 7,67 | 37,03 | `e05`: corpus v3, Qwen3-8B Q8_0 |
| 2026-10-02 | 588 | 113.519 | 14,67 | 16,33 | 8,37 | 39,37 | `e13`: filtro solo por cita, evidencia del top-10 y lookup por metadata |
| 2026-10-02 | 1.186 | 173.393 | 14,67 | 17,55 | 8,37 | 40,59 | `e19`/`e20`: corpus v4 (áreas delgadas, C- de control, tutelas) y prioridad por área |
| 2026-10-02 | 1.186 | 173.393 | 16,00 | 17,55 | 8,60 | 42,15 | `e24_final`: glosario de normas en el prompt |
| 2026-10-03 | 1.247 | 179.226 | 16,00 | 17,55 | 8,60 | 42,15 | `e41`: corpus v5 (61 normas que el corpus cita y no tenía), sin Planes de Desarrollo |
| 2026-10-03 | 1.284 | 185.215 | 13,33 | 17,55 | 8,14 | 39,02 | `e60`: v5 con reranker y metadatos activados (corrida de muestra anterior al congelado final) |

**Lectura de la curva.**

- El salto de citación (14,69 a 17,55) vino del filtro solo por cita, el lookup por metadata y agregar las cabeceras citables del top-10; ninguna corrida tiene citas sin respaldo.
- Las cerradas pasaron de 11 a 12 de 15 con el glosario de normas (#58). Las corridas v5 con reranker bajan a 10 de 15 en la muestra; con 15 cerradas una pregunta vale 1,33 puntos y no se diagnosticó una causa única, así que el resultado se reporta tal cual.
- Las ampliaciones v5 no se miden en `sample_50` (sus normas ya estaban); su ganancia esperada es en las 992. En recuperación, doc_hit@1 subió de 0,610 (v4) a 0,659 y MRR de 0,717 a 0,747 con los metadatos, los factores de sentencia y derogada y la consulta sin la instrucción de lectura (`docs/INDEXACION.md`, secciones 19–24).
- El juez de texto libre varía ±0,03 entre corridas: RAGAS 0,43–0,46, cerca de la línea base (0,451).

## 5. Licencia

El corpus procesado y el índice se publican bajo **CC-BY-4.0** (archivo `LICENSE` en la raíz del comprimido). La licencia cubre el trabajo de Syntax (selección, limpieza, segmentación, metadatos, encabezados de fragmentos e índice), no los textos normativos y jurisprudenciales, que son de libre reproducción (Ley 23 de 1982, art. 41). Los modelos usados son compatibles: `BAAI/bge-m3` (MIT), `BAAI/bge-reranker-v2-m3` (Apache-2.0) y Qwen3-8B (Apache-2.0).

## 6. Enlace al corpus e índice

Coincide con el de `README.md` ("Corpus e índice") y con `enlace_nube` de `corpus_manifest.json`.

| Recurso | Enlace | Tamaño | Vigencia |
|---|---|---|---|
| Corpus procesado e índice (v5) | [OneDrive](https://1drv.ms/u/c/e17f9102812dd361/IQBccApNKKVUR5RKm1ux2I-RAT5JSwWVU1jFBh37iHhFtXg?e=lbmgOi) | 958 MB (958.473.787 bytes) | Hasta el 2026-11-02 |

- sha256 del comprimido (`Syntax-corpus-v5c.zip`): `3164e08008e40ee6ebfa4f30a7966483b15dc45483dd2ecb25c63b67e6b28f0b`.
- sha256 de `indice/chunks.jsonl`: `9159bd3529dc59c41a7074e50e4f9e7cbf194b0ca958ff718c6c16d86454f85d` (185.234 fragmentos; `indice_info.json`).
- Encoder `BAAI/bge-m3`, revisión `5617a9f61b028005a4858fdac845db406aefb181`, fp32.
- La ampliación del sábado fue dirigida por las preguntas del test (solo `pregunta` y `opciones`), con la autorización de la organización del 2026-10-02.
