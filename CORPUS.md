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
| `auto_supersociedades_2025_01_730337` | Auto 2025-01-730337 de la Superintendencia de Sociedades | Superintendencia de Sociedades (Baranda Virtual) | [enlace](https://servicios.supersociedades.gov.co/barandaVirtual/#!/app/radicaciones#verpdf) | 2026-10-01 | — | 5 | Comercial y sociedades |
| `codigo_civil` | Codigo Civil (Ley 57 de 1887) | Sistema Unico de Informacion de Tramites (SUIT) | [enlace](https://tramites1.suit.gov.co/registro-web/suit_descargar_archivo?A=115930) | 2026-09-29 | 2.680 | 2.856 | Civil, Familia |
| `codigo_comercio` | Codigo de Comercio (Decreto 410 de 1971) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=41102) | 2026-09-29 | 2.032 | 2.072 | Comercial y sociedades |
| `codigo_penal` | Codigo Penal (Ley 599 de 2000) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6388) | 2026-09-29 | 476 | 625 | Penal |
| `codigo_procedimiento_penal` | Codigo de Procedimiento Penal (Ley 906 de 2004) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=14787) | 2026-10-01 | 564 | 625 | Penal, Procesal |
| `codigo_procesal_trabajo` | Codigo Procesal del Trabajo y de la Seguridad Social (Decreto 2158 de 1948) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5259) | 2026-10-01 | 143 | 157 | Laboral, Procesal |
| `cpaca` | Codigo de Procedimiento Administrativo y de lo Contencioso Administrativo (Ley 1437 de 2011) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=41249) | 2026-09-29 | 309 | 369 | Administrativo, Procesal |
| `decreto_1072_2015` | Decreto 1072 de 2015 (Decreto Unico Reglamentario del Sector Trabajo) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=72173) | 2026-10-01 | 1.412 | 1.563 | Laboral |
| `decreto_1074_2015` | Decreto 1074 de 2015 (Decreto Unico Reglamentario del Sector Comercio, Industria y Turismo) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608) | 2026-10-01 | 2.108 | 2.395 | Comercial y sociedades, Mercados |
| `decreto_1083_2015` | Decreto 1083 de 2015 (Decreto Unico Reglamentario del Sector de Funcion Publica) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=62866) | 2026-10-01 | 888 | 970 | Administrativo |
| `decreto_1625_2016` | Decreto 1625 de 2016 (Decreto Unico Reglamentario en materia tributaria) | Normograma de la DIAN | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/decreto_1625_2016.pdf) | 2026-10-01 | 1.545 | 3.549 | Tributario |
| `decreto_19_2012` | Decreto 19 de 2012 (antitramites) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=45322) | 2026-10-01 | 237 | 268 | Administrativo |
| `decreto_1_1984` | Decreto 01 de 1984 (Codigo Contencioso Administrativo anterior al CPACA) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6543) | 2026-10-01 | 245 | 283 | Administrativo, Procesal |
| `doctrina_arbanza_grupo_sociedades_2024` | Arbanza, Analisis comparativo de la extension del convenio arbitral a partes no signatarias: Pakistan, Francia y Colombia (2024) | Arbanza (doctrina) | [enlace](https://arbanza.com/analisis-comparativo-de-la-extension-del-convenio-arbitral-a-partes-no-signatarias-el-caso-de-pakistan-francia-y-colombia/) | 2026-10-01 | — | 14 | Comercial y sociedades |
| `doctrina_ompi_agotamiento_patentes_2012` | OMPI, Seminario Regional (Bogota, 2012), Tema 14: El agotamiento del derecho de patente | Organizacion Mundial de la Propiedad Intelectual (OMPI) | [enlace](https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf) | 2026-10-01 | — | 4 | Mercados |
| `ley_100_1993` | Ley 100 de 1993 (Sistema de Seguridad Social Integral) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=5248) | 2026-10-01 | 289 | 331 | Laboral |
| `ley_1676_2013` | Ley 1676 de 2013 (garantias mobiliarias) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=54297) | 2026-10-01 | 91 | 105 | Civil, Comercial y sociedades |
| `ley_222_1995` | Ley 222 de 1995 (regimen de sociedades) | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=6739) | 2026-10-01 | 242 | 253 | Comercial y sociedades |
| `ley_472_1998` | Ley 472 de 1998, acciones populares y de grupo | Gestor Normativo de Funcion Publica | [enlace](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=188) | 2026-09-29 | 86 | 93 | Administrativo, Constitucional |
| `sentencia_c_468_2024` | Sentencia C-468 de 2024 | Regimen Legal de Bogota (Secretaria Juridica Distrital) | [enlace](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=172537) | 2026-10-01 | — | 65 | Constitucional |
| `sentencia_ce_suj_4_005_2020` | Consejo de Estado, Seccion Cuarta, Sentencia de unificacion 2020CE-SUJ-4-005 de 2020 (exp. 21329) | Normograma de la DIAN | [enlace](https://normograma.dian.gov.co/dian/compilacion/docs/pdf/25000-23-37-000-2013-00443-01(21329)ce-suj-4-005.pdf) | 2026-10-01 | — | 64 | Tributario |
| `sentencia_sc_10291_2017` | Sentencia SC-10291 de 2017 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 26 | Civil |
| `sentencia_sc_435_2024` | Sentencia SC-435 de 2024 | Relatoria de la Corte Suprema de Justicia | [enlace](https://consultajurisprudencial.ramajudicial.gov.co/WebRelatoria/csj/index.xhtml) | 2026-10-01 | — | 46 | Comercial y sociedades |
| `sentencia_sc_5288_2021` | Sentencia SC-5288 de 2021 | Corte Suprema de Justicia | [enlace](https://www.cortesuprema.gov.co/corte/wp-content/uploads/not/civil21/prov/11001-02-03-000-2021-00766-00.pdf) | 2026-10-01 | — | 82 | Comercial y sociedades |
| `sentencia_su_16_2020` | Sentencia SU-016 de 2020 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2020/su016-20.htm) | 2026-10-01 | — | 321 | Constitucional |
| `sentencia_su_277_2025` | Sentencia SU-277 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/su277-25.htm) | 2026-10-01 | — | 173 | Administrativo |
| `sentencia_t_256_2025` | Sentencia T-256 de 2025 | Relatoria de la Corte Constitucional | [enlace](https://www.corteconstitucional.gov.co/relatoria/2025/t-256-25.htm) | 2026-10-01 | — | 256 | Constitucional |

**Objetivos de la semilla sin documento propio (3, 3 erratas).** Las erratas son referencias mal escritas del banco que apuntan a un documento ya incorporado; el resto quedó sin descargar. El detalle está en `data/fuentes_descargadas.json`.

| doc_id | Estado | Motivo |
|---|---|---|
| `ley_11500_2007` | errata | errata de la semilla: es la Ley 1150 de 2007, ya en el corpus como ley_1150_2007 |
| `ley_1150_2005` | errata | errata de la semilla: la Ley 1150 es de 2007, ya en el corpus como ley_1150_2007 |
| `ley_116_2006` | errata | errata de la semilla: probablemente la Ley 1116 de 2006 (insolvencia), ya en el corpus como ley_1116_2006 |

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
   `pdf`, `pdf_escaneado`, `otros`), con pausa de 1 s entre peticiones. Dieciocho
   documentos de mayor impacto no se descargan con el script: sus PDF se obtienen a
   mano del Gestor Normativo de Función Pública, del ICBF, de la SUIT o de RedJurista
   (enlaces en `data/referencias_normativas.md`) para controlar la calidad del dato, y
   el script solo los registra con esa fuente (`data/fuentes_override.json`). Trece son
   objetivos de la semilla (Constitución, CGP, CST, ET, Estatuto del Consumidor, Código
   de la Infancia, Leyes 80/1993, 1116/2006, 1258/2008, 1581/2012 y 2220/2022, Decreto
   2153/1992 y sentencia SL3385 de 2022). Cinco son adicionales a la semilla, tomados de
   las fuentes del `legal_basis` de `sample_50` que la semilla no cubría (Código Civil,
   Código de Comercio, Código Penal, CPACA y Ley 472 de 1998; sección `_adicionales` del
   mismo archivo, con `doc_id` canónicos de `scripts/citations.py`). La URL real, la
   fecha de consulta, el estado y el sha256 de cada descarga quedan en
   `data/fuentes_descargadas.json`, a partir del cual se genera el inventario de la
   sección 1.
2. **Extracción de texto.**
3. **Normalización.**
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

*Fallas concretas del pipeline (OCR, normas derogadas, encoding, artículos
duplicados, etc.) y cómo se resolvieron.*

**Decisiones de diseño relevantes.**

- **Encabezado citable en cada fragmento.** El evaluador considera respaldada una
  cita solo si la encuentra en el texto de alguno de los diez primeros pasajes
  recuperados. Un artículo aislado ("ARTÍCULO 42. Deberes del juez…") no nombra la
  norma a la que pertenece. Por eso cada fragmento empieza con una línea como
  "Artículo 42 del Código General del Proceso." o "Corte Constitucional, Sentencia
  C-355 de 2006.", seguida del texto literal. Se verifica automáticamente que el
  encabezado identifique exactamente la norma del documento, y los 31.127
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
