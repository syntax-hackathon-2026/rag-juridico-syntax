# Áreas por asignar en `corpus_manifest.json`

Los 162 documentos de la semilla traen sus `areas` de `data/seed_targets.json` (áreas de las preguntas del banco que los citan). Los 5 documentos de abajo **no están en la semilla** (`items_del_banco = 0`; sección `_adicionales` de `data/fuentes_override.json`): sus áreas las propuso un agente y hay que confirmarlas.

Mientras tanto, `corpus_manifest.json` los lleva con la propuesta actual (el validador exige `areas` no vacía).

La columna "Áreas en sample_50" es solo evidencia para decidir: el `area` de las preguntas de `data/sample_50.jsonl` cuyo `legal_basis` cita el documento (ground truth de evaluación; no se usa en runtime).

| doc_id | Norma | Áreas propuestas (actuales) | Áreas en sample_50 (preguntas) | Área asignada |
|---|---|---|---|---|
| `codigo_civil` | Código Civil (Ley 57 de 1887) | Derecho civil, Derecho de familia | Derecho civil (358); Derecho de familia (487, 490, 865, 647) | |
| `codigo_comercio` | Código de Comercio (Decreto 410 de 1971) | Derecho comercial y sociedades | Derecho comercial y sociedades (239) | |
| `codigo_penal` | Código Penal (Ley 599 de 2000) | Derecho penal | Derecho penal (600, 280, 1065) | |
| `cpaca` | CPACA (Ley 1437 de 2011) | Derecho administrativo, Derecho procesal | Derecho administrativo (748); Derecho procesal (1089) | |
| `ley_472_1998` | Ley 472 de 1998 (acciones populares y de grupo) | Derecho constitucional, Derecho administrativo | Derecho constitucional (51); Derecho administrativo (247) | |

Nombres válidos (exactos, como en el banco): `Derecho constitucional`, `Derecho administrativo`, `Derecho penal`, `Derecho procesal`, `Derecho comercial y sociedades`, `Derecho civil`, `Derecho de familia`, `Derecho tributario`, `Derecho laboral`, `Derecho de los mercados [competencia, consumidor, datos personales y propiedad intelectual]`.

**Cómo aplicar la decisión.** Llenar "Área asignada" y actualizar `areas` del documento en dos sitios: `_adicionales` de `data/fuentes_override.json` (para que `descargar_fuentes.py` lo conserve) y `corpus_manifest.json`. Luego `python src/validaciones/manifest.py`.
