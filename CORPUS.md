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

| doc_id | Título | Fuente | URL | Fecha de consulta | Artículos | Fragmentos | Áreas |
|---|---|---|---|---|---:|---:|---|
| | | | | | | | |

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

1. **Descarga.**
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
