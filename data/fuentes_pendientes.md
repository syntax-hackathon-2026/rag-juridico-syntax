# Fuentes pendientes del corpus

Lista de verificación de lo que falta por conseguir. Marcar `[x]` cuando el original esté en `data/raw/`, mapeado en `data/mapa_archivos.json` (si es PDF/RTF), parseado a `data_corpus/corpus/<doc_id>.txt` y registrado en `CORPUS.md`.

Estado a 2026-09-29: 167 documentos en el corpus. Origen de la lista: `data/fuentes_descargadas.json` (semilla) y `data/fuentes_faltantes_sample50.md` (`legal_basis` de `sample_50`).

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

- [ ] `sentencia_sl_648_2018` — SL-648 de 2018 (2 ítems, Derecho laboral)
- [ ] `sentencia_sl_1050_2023` — SL-1050 de 2023 (1 ítem, Derecho laboral)
- [ ] `sentencia_sl_1730_2020` — SL-1730 de 2020 (1 ítem, Derecho laboral)
- [ ] `sentencia_sl_1972_2025` — SL-1972 de 2025 (1 ítem, Derecho laboral)

### Sala Penal (SP)

- [ ] `sentencia_sp_1680_2022` — SP-1680 de 2022 (2 ítems, Derecho penal)
- [ ] `sentencia_sp_1945_2019` — SP-1945 de 2019 (2 ítems, Derecho penal)
- [ ] `sentencia_sp_1167_2022` — SP-1167 de 2022 (1 ítem, Derecho penal)
- [ ] `sentencia_sp_3218_2021` — SP-3218 de 2021 (1 ítem, Derecho penal)

### Sala Civil (SC)

- [ ] `sentencia_sc_1121_2018` — SC-1121 de 2018 (1 ítem, Derecho civil)
- [ ] `sentencia_sc_18392_2017` — SC-18392 de 2017 (1 ítem, Comercial y sociedades)
- [ ] `sentencia_sc_3674_2021` — SC-3674 de 2021 (1 ítem, Comercial y sociedades)
- [ ] `sentencia_sc_425_2024` — SC-425 de 2024 (1 ítem, Comercial y sociedades)
- [ ] `sentencia_sc_8453_2016` — SC-8453 de 2016 (1 ítem, Comercial y sociedades)
- [ ] `sentencia_sc_3085_2024` — SC-3085 de 2024 (1 ítem, Derecho de familia)

### Otro tipo

- [ ] `acuerdo_2_2015` — Acuerdo 02 de 2015 (1 ítem, Derecho constitucional). Falta identificar qué entidad lo expidió; el script no tiene regla para `acuerdo`.

---

## B. No encontrados en la fuente oficial (6, de la semilla)

La URL que construyó el script no existe. Probar otra fuente o confirmar si la referencia del banco es una errata.

- [ ] `decreto_46_2024` — Decreto 46 de 2024 (1 ítem, Comercial y sociedades). No está en el Senado; probar Gestor Normativo o SUIN-Juriscol.
- [ ] `ley_1692_2017` — Ley 1692 de 2017 (1 ítem, Tributario). No está en el Senado; verificar el número (¿errata?).
- [ ] `ley_23_1961` — Ley 23 de 1961 (1 ítem, Constitucional). No está en el Senado; probar SUIN-Juriscol.
- [ ] `sentencia_su_488_2011` — SU-488 de 2011 (1 ítem, Administrativo). Probar `SU-488-11.htm` u otro formato de URL en la Relatoría.
- [ ] `sentencia_t_248_2025` — T-248 de 2025 (1 ítem, Penal). Probar otro formato de URL en la Relatoría.
- [ ] `sentencia_su_6_1991` — SU-6 de 1991 (1 ítem, Administrativo). La Corte no emitió SU en 1991; probablemente errata. Decidir: identificar la sentencia real o descartar.

---

## C. Fuentes del `legal_basis` de `sample_50` fuera de la semilla

Servidas por `data/fuentes_faltantes_sample50.md`. Los ítems A.1 a A.5 de ese documento (Código Civil, Código de Comercio, Código Penal, CPACA y Ley 472 de 1998) **ya están incorporados**.

### Corte Constitucional

- [ ] `sentencia_c_468_2024` — C-468 de 2024 (pregunta 453). https://www.corteconstitucional.gov.co/relatoria/2024/C-468-24.htm
- [ ] `sentencia_su_16_2020` — SU-016 de 2020 (pregunta 453). https://www.corteconstitucional.gov.co/relatoria/2020/SU016-20.htm (la semilla trae SU-11/2020, no esta)
- [ ] `sentencia_su_277_2025` — SU-277 de 2025 (pregunta 563). https://www.corteconstitucional.gov.co/relatoria/2025/SU277-25.htm
- [ ] T-256 (pregunta 190). Ambigua: hay T-256 en varios años. Resolver el año con el enunciado de la pregunta antes de descargar.

### Otras cortes y autoridades

- [ ] Consejo de Estado, sentencia de unificación 2020CE-SUJ-4-005 del 26-nov-2020, exp. 21329 (pregunta 142, tributario). Buscar en la relatoría del Consejo de Estado o en SUIN-Juriscol.
- [ ] Auto de Supersociedades No. 2025-01-730337 (pregunta 272). Complementa la Ley 1116 de 2006. Buscar en supersociedades.gov.co.
- [ ] Sentencia de la Sala Civil de la CSJ del 18-jul-2017, sin radicado (pregunta 168). Identificar el radicado; verificar si es `SC-18392-2017` o `SC-8453-2016` (A, Sala Civil) antes de descargar dos veces.

### No normativos (decidir si valen la pena)

- [ ] WIPO, `wipo_ip_bog_12_ref_u14b_aleman.pdf` (pregunta 513). https://www.wipo.int/edocs/mdocs/mdocs/en/wipo_ip_bog_12/wipo_ip_bog_12_ref_u14b_aleman.pdf. Es una ponencia, no una norma: decidir si se incluye.
- [ ] Caso Dow Chemical (laudo CCI, 1982) (pregunta 697). Sin fuente oficial, probablemente doctrina de arbitraje internacional: decidir si se incluye.

---

## Sin acción (referencia)

- **Erratas de la semilla ya cubiertas** (no hay nada que descargar): `ley_11500_2007` y `ley_1150_2005` → `ley_1150_2007`; `ley_116_2006` → `ley_1116_2006`.
- **Preguntas sin fuente normativa**: 24 (`legal_basis` vacío), 671 y 857 (solo «Doctrina»).

## Conteo

| Bloque | Pendientes |
|---|---:|
| A. Corte Suprema y acuerdo sin URL | 15 |
| B. No encontrados | 6 |
| C. Fuera de la semilla (sample_50) | 9 |
| **Total** | **30** |
