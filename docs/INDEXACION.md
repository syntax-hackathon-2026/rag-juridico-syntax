# Segmentación e indexación del corpus: estado y contexto

Contexto para agentes y personas que continúen el trabajo de recuperación. Resume lo construido el 2026-09-29 (rama `sofi`), las decisiones de diseño y su motivo, los resultados medidos y lo que falta. Las reglas generales del proyecto están en `CLAUDE.md`; este documento no las repite.

## 1. Estado en una línea

**Corpus v2 (2026-10-02): 213 documentos → 47.966 fragmentos, con BM25 + bge-m3 + RRF construidos y medidos (`e03_corpus_v2`, sección 10).** `index.faiss` (IndexFlatIP, fp32) se codificó en una T4 de Kaggle (CUDA) y se armó en local desde la caché con `SYNTAX_DEVICE=cpu`; es idéntico byte a byte al de Kaggle. Mejor `respaldo@10` en híbrido: 0,927 (v1: 0,907). Antes (v1): 167 documentos → 35.105 fragmentos (`e01_bge_m3`, Colab T4). `construir_indice.py --particion I/N` permite repartir la codificación entre varias máquinas; ver `notebooks/indice_denso_colab.ipynb` y `notebooks/indice_denso_kaggle.ipynb`. El generador (Qwen), `src/main.py` y `run.sh` están descritos en `docs/GENERACION.md`.

## 2. Pipeline y comandos

```bash
# 0. corpus local (data_corpus/ está en .gitignore; cada persona lo regenera)
python src/ingesta/parsear_pdf.py && python src/ingesta/parsear_rtf.py && python src/ingesta/parsear_html.py

# 1. segmentar: corpus/*.txt -> data_corpus/indice/chunks.jsonl + resumen_indice.json  (~1 min, sin deps de ML)
python src/indexacion/segmentar.py
python src/indexacion/segmentar.py --solo codigo_civil ley_80_1993          # solo imprime la tabla, no escribe
python src/indexacion/segmentar.py --mostrar codigo_general_proceso 42      # ver los fragmentos de un artículo
python src/indexacion/segmentar.py --mostrar sentencia_c_355_2006 w0001     # ver una ventana de sentencia

# 2. índice: bm25/ + index.faiss + indice_info.json, y actualiza corpus_manifest.json
python src/indexacion/construir_indice.py --solo-bm25                       # sin encoder (lo que está construido hoy)
SYNTAX_DEVICE=cuda python src/indexacion/construir_indice.py --batch 64     # con GPU (campus)

# 3. probar y medir
python src/recuperacion/retriever.py "deberes del juez" --modo bm25|denso|hibrido -k 10
python src/evaluacion/retrieval_eval.py --modo bm25 denso hibrido --experimento e01_bge_m3
```

Todo usa rutas de `src/config.py`. En Windows, si una consola da error de codificación: `PYTHONIOENCODING=utf-8`.

## 3. Archivos nuevos

| Archivo | Qué hace |
|---|---|
| `src/indexacion/cabeceras.py` | Cuerpo canónico de cada `doc_id` (tupla en formato de `scripts/citations.py`) y encabezado citable de cada fragmento, validado con `citations.extract`. |
| `src/indexacion/segmentar.py` | Segmentador de normas (por artículo) y sentencias (ventanas). Comprueba invariantes y escribe `chunks.jsonl` + `resumen_indice.json`. |
| `src/indexacion/construir_indice.py` | BM25 (`bm25s`), embeddings `bge-m3` con caché, `faiss.IndexFlatIP`, `indice_info.json` y actualización del manifest. |
| `src/recuperacion/lexico.py` | Tokenizador de BM25 compartido por indexación y consulta (`lex-v1`). |
| `src/recuperacion/retriever.py` | `retrieve(query, k, modo) -> list[RetrievedChunk]`; modos `bm25`, `denso`, `hibrido` (RRF k=60 sobre 40 candidatos por rama). `RetrievedChunk.pasaje()` devuelve el registro listo para `pasajes_recuperados`. |
| `src/evaluacion/retrieval_eval.py` | Métricas de recuperación sobre `sample_50` (usa `legal_basis` solo para evaluar). Escribe `evaluation/retrieval/*.jsonl`, `evaluation/experiments.csv` y `evaluation/entornos/*.json`. |

Modificados: `src/config.py` (rutas del índice, `ENCODER_*`, `DEVICE`/`resolver_device()`, `FUENTES_PATH`), `src/ingesta/_texto.py` (toma `FUENTES_PATH` de config), `requirements.txt`, `CLAUDE.md`/`AGENTS.md`, `CORPUS.md` (sección 3, pasos 4–6 y decisiones), `corpus_manifest.json` (`n_fragmentos`, `sha256`).

## 4. Decisiones de diseño y por qué

### 4.1 Encabezado citable dentro de `texto` (la decisión más importante)

El evaluador calcula el respaldo con `citations.extract(pasaje["texto"])` sobre los 10 primeros pasajes (`scripts/evaluate.py`, `citas_respaldadas`). **No mira el `doc_id`.** Un artículo suelto ("ARTÍCULO 42. Deberes del juez…") no extrae ninguna norma, así que ninguna cita quedaría respaldada. Por eso:

```
texto = cabecera + "\n" + corpus[inicio:fin]      # corpus = data_corpus/corpus/<doc_id>.txt
```

- Cabecera de norma: `Artículo 42 del Código General del Proceso.`, `Artículo 5 de la Ley 80 de 1993.`, `Artículo 2.2.1.1 del Decreto 1082 de 2015.`. Antes del primer artículo: `<Nombre>, encabezado y disposiciones iniciales.`
- Cabecera de sentencia: `Corte Constitucional, Sentencia C-355 de 2006.` o `Corte Suprema de Justicia, Sala de Casación Laboral, Sentencia SL-3385 de 2022.`
- Se valida que `bodies(extract(cabecera)) == {canonico}`: la cabecera extrae exactamente la norma del documento y nada más. Otras formas probadas fallan:
  - "Constitución Política de Colombia, artículo 29" pierde el artículo (la ventana de `_articles_near` se rompe con "de colombia").
  - "Código Civil (Ley 57 de 1887)" agrega un cuerpo espurio `("ley","57","1887")`.
- La puntuación de citas compara a **nivel de cuerpo** (`citations.bodies` descarta el artículo). Aun así, la cabecera lleva el artículo para la validación de citas en generación.
- Verificado con el evaluador oficial: **0 de 31.127** fragmentos quedan sin respaldo de su propio cuerpo.
- **Para quien construya la generación:** `pasajes_recuperados[i].texto` debe ser `chunk["texto"]` tal cual, sin recortar la cabecera, y `inicio`/`fin` son offsets del cuerpo literal en `corpus/<doc_id>.txt`.

### 4.2 Cuerpo canónico por documento

Orden (`cabeceras.canonico`): `doc_id` que es clave de `citations.CODES` (`codigo_civil`, `cpaca`, `codigo_general_proceso`…) → regex del `doc_id` (`ley_N_AAAA`, `decreto_N_AAAA`, `sentencia_<sala>_N_AAAA`; una ley con alias de código en `citations._ALIAS_NUM` usa el alias) → `canonico` de `data/registros/fuentes_descargadas.json` (p. ej. `constitucion_politica_1991`). El `doc_id` va primero porque el `canonico` de la semilla arrastra **erratas del propio banco**, que `fuentes_override.json` corrigió en el `doc_id`:

| doc_id | La semilla/banco dice | Norma correcta (la que usa la cabecera) |
|---|---|---|
| `ley_1563_2012` | Decreto 1563 de 2012 (2 ítems) | Ley 1563 de 2012 |
| `decreto_2737_1989` | Ley 2737 de 1989 (1 ítem) | Decreto 2737 de 1989 |
| `ley_964_2005` | Ley 964 de 2006 (1 ítem) | Ley 964 de 2005 |

Esos ~4 ítems pueden perder citación si su `legal_basis` usa la forma errónea. Se decidió no citar normas inexistentes. En el corpus v2 se agregan cinco erratas más, resueltas a mano (`fuentes_override.json`):

| doc_id | La semilla/banco dice | Documento incorporado |
|---|---|---|
| `ley_1692_2013` | Ley 1692 de 2017 | Ley 1692 de 2013 (convenio Colombia-Portugal, doble imposición) |
| `ley_23_1991` | Ley 23 de 1961 | Ley 23 de 1991 (descongestión judicial) |
| `sentencia_t_488_2011` | SU-488 de 2011 | T-488 de 2011 |
| `sentencia_sp_248_2025` | T-248 de 2025 (área penal) | SP248-2025, Sala Penal de la Corte Suprema |
| `sentencia_t_6_1992` | SU-6 de 1991 (no hubo SU en 1991) | T-006 de 1992, respaldo elegido a mano |

**Ceros a la izquierda.** `citations` compara el número como texto: "Decreto 046 de 2024" da `("decreto","046","2024")` y no coincide con `"46"`. Si la semilla trae la misma norma con ceros, `canonico()` conserva esa forma (`decreto_46_2024` → `046`, `acuerdo_2_2015` → `02`). Además, `cabeceras.variantes()` hace que la cabecera nombre también las otras formas usuales, así respalda la cita escrita de cualquiera de ellas: "Artículo 1 del Acto Legislativo 1 de 2005 (Acto Legislativo 01 de 2005)." Solo afecta a normas de un dígito o con ceros en la semilla, y ninguna de ellas estaba en v1.

**Documentos no normativos** (`cabeceras.DOCUMENTOS`): la sentencia de unificación del Consejo de Estado 2020CE-SUJ-4-005, el auto 2025-01-730337 de Supersociedades y la doctrina de la OMPI y de Arbanza. `citations` no extrae ninguna cita de ellos. Tienen `canonico = ("documento", doc_id, None)` y `tipo = "documento"`; la cabecera es su nombre legible (se comprueba que no extraiga ninguna cita) y se segmentan en ventanas, como las sentencias (`segmentar.EN_VENTANAS`).

### 4.3 Unidad de fragmento

- **Normas**: un artículo = un fragmento (`chunk_id` `<doc_id>#art_<N>#p1`). Si pasa de 350 palabras se parte por párrafos en `#p1..#pN` sin solapamiento (un párrafo de más de 450 palabras se parte por oraciones). El texto anterior al primer artículo va en `<doc_id>#pre#pN`. Los encabezados LIBRO/TÍTULO/CAPÍTULO/SECCIÓN no entran al texto: se guardan en `seccion`. Un id de artículo repetido (el ET repite "ARTÍCULO 1", el del decreto y el del estatuto; la Constitución tiene transitorios de varios actos legislativos) recibe el sufijo `~2`.
- **Sentencias**: ventanas de ~350 palabras con párrafos enteros (`<doc_id>#w0001`…), 1 párrafo de solapamiento si tiene ≤ 120 palabras, sin cruzar secciones: `sintesis | antecedentes | consideraciones | resuelve | salvamento | aclaracion`. Salvamento y aclaración solo se detectan como "… de voto" (evita "2. Aclaración previa" y la firma "CON SALVAMENTO DE VOTO").
- Formatos de encabezado de artículo reconocidos: `ARTÍCULO 1o.`, `Artículo 1°.`, `ARTÍCULO 1 ORIGEN…` (sin puntuación), `Artículo 1.-`, `ARTÍCULO 12-1.`, `ARTÍCULO 5A.`, `ARTÍCULO 2.2.1.1.1.`, `ARTÍCULO TRANSITORIO 3.`, `14 bis`. Después del número exige puntuación o espacio + mayúscula, así que "Artículo 42 del Código…" en una nota no abre un artículo.

### 4.4 Normas modificatorias (modo cita)

Una ley que reforma otra transcribe artículos ajenos: "ARTÍCULO 10. Modifíquese el artículo 247 del Estatuto Tributario, el cual quedará así: Artículo 247. …". Sin tratamiento, el 247 quedaría como "Artículo 247 de la Ley 1819 de 2016", una cita falsa. Regla:

- Se entra en modo cita si el párrafo previo termina en `:`, si algún párrafo del artículo actual termina en la fórmula de reforma (`quedará así:`, `el siguiente texto:`… aunque haya un subtítulo en medio, caso Ley 1755/2015), o si el encabezado empieza con comillas. Un encabezado entre comillas nunca abre artículo, **ni siquiera antes del primero** (la Ley 600/2000 cita "Artículo 235" de la Constitución en su preámbulo).
- Se sale cuando la numeración vuelve a la propia: número base entre el último y +2 (letras y `-N` comparten base), reinicio en 1 (transitorios, decreto que adopta un código) o, en decretos únicos, cualquier número decimal mayor, aunque cambie de nivel (`2.2.1.4 → 2.2.1.5`, `1.2.1.9.1.3 → 1.2.1.10.1`; antes se exigía el mismo nivel y el DUR 1625/2016 se quedaba atascado en modo cita).
- Un encabezado "ARTÍCULO N DEL ESTATUTO TRIBUTARIO." / "ARTÍCULO 428 LITERAL F) DEL ESTATUTO…" (nombre de otra norma pegado al número, sin puntuación) es una transcripción y no abre artículo (`_DE_OTRA_NORMA`). Solo aparece en el DUR tributario de la DIAN. Antes, un "ARTÍCULO 19-4 DEL ESTATUTO TRIBUTARIO" se tomaba como artículo propio y 2.598 fragmentos del 1625 quedaban dentro de él.
- En el DUR 1625/2016 de la DIAN, las versiones anteriores de cada artículo (plazos de años pasados, con numeración más baja) quedan dentro del artículo vigente, igual que las cajas de "legislación anterior" del Senado. Las tablas del PDF salen con el texto desordenado.

### 4.5 Encoder e índice

- `BAAI/bge-m3`, licencia MIT, revisión fijada `5617a9f61b028005a4858fdac845db406aefb181` (verificada en Hugging Face), 1024 dimensiones, `max_seq_length=1024`, vectores normalizados y `faiss.IndexFlatIP` exacto (el enunciado, B.3, recomienda índice exacto a esta escala). Se descartó `jina-embeddings-v3` (CC-BY-NC, incompatible con nuestra CC-BY-4.0). `multilingual-e5-large` queda como experimento si el denso sale flojo: tope de 512 tokens y exige prefijos `query:`/`passage:`.
- **Determinismo**: el índice y la consulta van siempre en fp32, y los empates se desempatan por `chunk_id`. Caché de embeddings en `data_corpus/cache_emb/<modelo>@<rev>/*.npz` con clave sha256 del `retrieval_text`: al agregar documentos solo se codifican los nuevos, y una corrida interrumpida retoma. `--solo-bm25` borra un `index.faiss` viejo para que no quede desalineado.
- BM25 (`bm25s` 0.3.11, lucene, k1=1.5, b=0.75) sobre `retrieval_text` = `texto` + título del manifest + siglas (`CGP`, `CST`, `ET`…) + sección. Tokenizador `lex-v1`: sin tildes (`citations.norm`), conserva `2.2.1.1`, `240-1` y `1564`, stopwords en español sin "no", "sin" ni "ley", sin stemming.

### 4.6 Manifest

`construir_indice.py` (salvo `--no-manifest`) reescribe en cada build `n_fragmentos` por documento y en la raíz, y `sha256` si el `.txt` cambió. **No toca `n_articulos`** ni agrega o borra documentos. Para agregar o quitar documentos está `python src/ingesta/generar_manifest.py` (`--revisar` muestra el diff sin escribir). Lo regenera desde `data/registros/fuentes_descargadas.json` (título, fuente, URL, fecha, áreas), `data_corpus/parseo.json` (método, sha256) y `chunks.jsonl` (`n_fragmentos`). Conserva el `n_articulos` ya registrado; en documentos nuevos lo toma de `articulos_base` de `resumen_indice.json`. Orden para un documento nuevo: parsear → `generar_manifest.py` (títulos para el `retrieval_text`) → `segmentar.py` → `generar_manifest.py` → `construir_indice.py`. Formato: `json.dumps(indent=2, ensure_ascii=False)` + `\n`, igual que el archivo original. `python src/validaciones/manifest.py` da 0 errores; solo queda el placeholder `enlace_nube`.

## 5. Registro de `chunks.jsonl`

```json
{"chunk_id": "codigo_general_proceso#art_42#p1", "doc_id": "codigo_general_proceso", "tipo": "codigo",
 "numero": "1564", "anio": "2012", "articulo": "42", "parte": 1, "n_partes": 2,
 "seccion": "LIBRO PRIMERO SUJETOS DEL PROCESO / TÍTULO III DEBERES Y PODERES DE LOS JUECES",
 "vigencia": "sin_nota", "canonico": ["codigo_general_proceso", null, null],
 "cabecera": "Artículo 42 del Código General del Proceso.", "inicio": 52615, "fin": 54829,
 "texto": "Artículo 42 del Código General del Proceso.\nArtículo 42. Deberes del juez. …",
 "retrieval_text": "… | Codigo General del Proceso (Ley 1564 de 2012) | CGP | LIBRO PRIMERO …",
 "url": "…", "fuente": "…", "n_palabras": 349}
```

- `tipo`: `constitucion | codigo | ley | decreto | decision | sentencia`. En los códigos, `numero`/`anio` son los de la norma que los adopta (salen del título del manifest).
- `vigencia`: señal por regex sobre las notas en línea de los primeros 300 caracteres (`inexequible | derogado | modificado | sin_nota`; `null` en sentencias y preámbulos). **No es verdad jurídica.**
- Invariantes comprobadas al segmentar (exit 1 si fallan): `texto == cabecera + "\n" + corpus[inicio:fin]`; fragmentos de una norma sin solaparse; `chunk_id` únicos en todo el corpus.

## 6. Resultados

**Segmentación** (`seg-v1`): 31.127 fragmentos, 0 errores. Artículos detectados (números base, sin transitorios) frente a `n_articulos` del manifest: exactos en Constitución 380, CGP 627, CST 487, ET 932, Código Civil 2680, Código de Comercio 2032, Decisión 486 280, Decreto 1082 786, Ley 1755 2; Código Penal 475/476, Decreto 780 2380/2396. Secciones de sentencias: consideraciones 5265, antecedentes 2890, aclaración 693, resuelve 688, síntesis 540, salvamento 390.

**Recuperación, `e00_bm25_seg_v1`** (sample_50, 41 preguntas con fundamento extraíble, 19 a nivel de artículo, consulta = pregunta + opciones):

| doc_hit@1 | doc_hit@3 | doc_hit@5 | doc_hit@10 | MRR | respaldo@10 | art_hit@1 | art_hit@10 | latencia |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0,488 | 0,683 | 0,707 | 0,805 | 0,594 | 0,833 | 0,211 | 0,421 | 6 ms |

`respaldo@10` es la fracción de normas de referencia que el evaluador daría por respaldadas con esos 10 pasajes: el techo de los 20 pts de citación. Fallos de doc_hit@10 (8), por diagnóstico:

- CORPUS: #563 (SU-277/2025 no está en el corpus).
- DOCUMENT_RETRIEVAL: #60, #647, #748, #247, #679, #239, #661. En casi todos, ventanas de sentencias desplazan al artículo (juez natural → T-323/2024 en lugar de CGP/Constitución; legalidad tributaria → sentencias C en lugar de la Constitución). Hipótesis a medir: denso/híbrido; después, una penalización o cuota por tipo de documento.

## 7. Problemas conocidos y pendientes

1. **Índice denso: resuelto para v2 (2026-10-02, sección 10).** En CPU de portátil el corpus completo llevaría muchas horas (más de 10 minutos por 512 fragmentos); se codifica en GPU (`SYNTAX_DEVICE=cuda`) y se trae `cache_emb/` + `index.faiss`. Cada cambio de corpus obliga a repetirlo, aunque la caché (por sha256 del `retrieval_text`) limita la codificación a los fragmentos nuevos.
2. **Los parsers no dan el mismo texto en todas las máquinas (causa probable, sin confirmar: `lxml`/libxml2 con HTML de Word muy anidado).** Diagnosticado el 2026-09-30: 33 documentos (31 sentencias HTML de la relatoría y 2 vía pandoc) daban un texto distinto en Windows. Comparado con el HTML original, el `corpus/` de Mac es completo (`sentencia_c_55_2022`: 242.776 palabras contra 240.988 del HTML) y el de Windows estaba truncado (159 fragmentos, ~25 % del texto). El manifest se regeneró con el corpus de Mac (35.105 fragmentos). Medidas para que sea replicable:
   - `parsear_html.py` mide la **completitud** de cada sentencia (palabras extraídas / palabras del HTML crudo contadas por regex, sin `lxml`) y avisa por debajo de 0,85 (medido: 0,945–0,995). Un parseo truncado ya no pasa en silencio.
   - `python src/reproducibilidad/verificar_corpus.py` compara el `sha256` de cada `corpus/*.txt` con el manifest y el de `chunks.jsonl` con `data/registros/hashes_esperados.json`. exit 1 = esa máquina no reproduce el corpus congelado.
   - La entrega no depende de re-parsear: el jurado parte del `corpus/` publicado (más el manifest con sus `sha256`). Segmentar e indexar sí son deterministas (dos corridas dan el mismo `chunks.jsonl`). Solo una máquina debe generar `corpus/`, y todas las demás deben descargarlo o pasar `verificar_corpus.py`.
   - `construir_indice.py` reescribe `sha256`/`n_fragmentos` del manifest: correr `verificar_corpus.py` **antes** de aceptar ese cambio, o una divergencia de corpus queda oculta.
3. **`n_articulos` del manifest inflado en normas modificatorias** (cuenta artículos transcritos): Ley 80/1993 dice 86 y tiene 81; Ley 50/1990, 171 contra 117; Decreto 405/2025, 7 contra 2; Ley 2466/2025 22 contra 70 detectados (aquí el manifest trae el conteo del índice de navegación). Código de Policía: 200 contra 243 reales. Conviene que quien mantiene el manifest revise esos valores.
4. **Error residual del modo cita**: Ley 1607/2012 detecta 212 artículos contra 198; ~14 artículos del ET transcritos quedan como propios. Menor, porque la cita sigue siendo correcta a nivel de cuerpo (Ley 1607).
5. 11 sentencias no tienen sección `resuelve` detectada (p. ej. `sentencia_c_55_2022` no trae el título RESUELVE en el HTML). Las notas al pie de la relatoría quedan etiquetadas con la última sección.
6. Pendiente del plan: `run.sh`/`src/main.py` (el comando único debe decidir si reconstruye embeddings, que es lento en CPU, o descarga el índice publicado), generación con Qwen, abstención y empaquetado del corpus.
7. Entorno de esta corrida: Python 3.13 (ya es la versión oficial del proyecto, ver `# python:` en `requirements.txt`), `torch==2.14.0` CPU, pandoc 3.12 (winget). Versiones fijadas en `requirements.txt`; `verificar_deps.py` da ok.

## 8. Trampas encontradas (para no repetirlas)

- En Git Bash de Windows, un `cat > archivo` sin heredoc (o `python -` con heredoc vacío) se queda esperando stdin y cuelga la herramienta: usar `< /dev/null` o escribir el script a un archivo.
- Salida de Python redirigida a archivo: usar `python -u` o `PYTHONUNBUFFERED=1`, o el log queda vacío hasta el final.
- `citations.extract` es lento en volumen (~10 min sobre 31k textos): no llamarlo por fragmento en caliente; `cabeceras.cabecera` está cacheada con `lru_cache`.
- Al insertar lógica dentro de un `if/elif/else` con Edit, verificar que no quede entre el `elif` y el `else`: así ocurrió un bug que duplicó todo el CGP en el preámbulo. La comprobación de "sin solapamiento" ahora lo detecta.

## 9. Índice denso: resultados `e01_bge_m3` (2026-09-30)

Corpus de 35.105 fragmentos (seg-v1), mismo `sample_50` y consulta = pregunta + opciones. Denso: bge-m3 fp32 (Colab T4) + `IndexFlatIP`; híbrido: RRF k=60 sobre 40 candidatos por rama.

| modo | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@1 | art_hit@10 | latencia |
|---|---:|---:|---:|---:|---:|---:|---:|
| bm25 | 0,439 | 0,780 | 0,563 | 0,833 | 0,158 | 0,421 | 1 ms |
| denso | 0,585 | 0,854 | 0,672 | 0,870 | 0,211 | 0,526 | 395 ms |
| hibrido | 0,512 | 0,854 | 0,643 | 0,907 | 0,263 | 0,526 | 76 ms |

- El híbrido da el mejor `respaldo@10` (0,907), que es el techo de los 20 pts de citación; el denso, el mejor MRR y doc_hit@1. Diferencias de 1–2 preguntas de 41: no son concluyentes.
- Sin el cuerpo en el top-10 en híbrido: #60, #748, #247, #679, #563, #661 (#563 es de CORPUS). BM25 fallaba además en #600, #647 y #239, que el híbrido resuelve; el resto sigue pendiente de diagnóstico.
- Bug corregido: `retriever.cargar()` reutilizaba un retriever creado solo con BM25 y fallaba en `denso`.
- La latencia del denso incluye cargar el encoder en la primera consulta.

## 10. Corpus v2: `e03_corpus_v2_bm25` (2026-10-01)

+46 documentos (ver `docs/ingesta/fuentes_pendientes.md`): 14 sentencias SC/SL/SP de la semilla, más SP248-2025, SC10291-2017, SC435-2024 y SC5288-2021; las de la Corte Constitucional C-468/2024, SU-016/2020, SU-277/2025, T-256/2025, T-488/2011 y T-006/1992; Acuerdo 02/2015; Decreto 046/2024; Leyes 1692/2013, 23/1991, 100/1993, 222/1995 y 1676/2013; CPP (`codigo_procedimiento_penal`, Ley 906/2004); CPT (`codigo_procesal_trabajo`, Decreto 2158/1948); DUR 1072/2015, 1074/2015, 1083/2015 y 1625/2016; Decretos 19/2012 y 01/1984; Actos Legislativos 01/2003, 01/2005 y 02/2015; y los 4 documentos no normativos.

OCR: SL648-2018 y SP1945-2019 (escaneados) y SC10291-2017, SC18392-2017 y SC8453-2016 (capa OCR ilegible) pasan por Tesseract 5.5.3 `spa` a 300 dpi (`parsear_pdf.OCR_FORZADO`). La ponencia de la OMPI se extrae sin ordenar por coordenadas (`SIN_ORDENAR`), porque son diapositivas con texto en capas.

| modo (sample_50, 41 con fundamento) | doc_hit@1 | doc_hit@3 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 |
|---|---:|---:|---:|---:|---:|---:|
| bm25 v1 (`e01`) | 0,439 | 0,683 | 0,780 | 0,563 | 0,833 | 0,421 |
| bm25 v2 (`e03`) | 0,390 | 0,634 | 0,805 | 0,530 | **0,927** | 0,368 |

- Gana el respaldo@10 (+4 preguntas): #453 (SU-016, C-468), #563 (SU-277), #60, #748 y #239.
- Baja la precisión arriba del ranking, por desplazamiento léxico: el DUR 1625 adelanta al EOSF en #128 y el DUR 1074 al Estatuto del Consumidor en #674; SC435-2024 y SC3085-2024 pasan por delante del CGP y el Código Civil en #589 y #490; el art. 101 del Acuerdo 02/2015 ("8:00 a.m. a 5:00 p.m.") pasa delante del CST en #1073. Son diferencias de 1–2 preguntas de 41, sin cambio en el código del retriever. Hay que medirlo de nuevo en híbrido cuando esté el denso.
- **Índice denso v2 (2026-10-02).** Codificado en una T4 de Kaggle (`notebooks/indice_denso_kaggle.ipynb`; la caché de v1, también CUDA, se reutilizó y solo se codificaron los fragmentos nuevos). Integrado en local con `SYNTAX_DEVICE=cpu python src/indexacion/construir_indice.py` (todo desde caché, ~20 s para BM25). Comprobado: sha256 de `chunks.jsonl` igual al de `indice_info.json` del zip, `index.faiss` con 47.966 vectores de dimensión 1024 (idéntico byte a byte al de Kaggle), la caché cubre todos los fragmentos (47.947 claves únicas por textos repetidos) y `manifest.py` da 0 errores. `indice_info.json` registra `device: cpu` (la máquina que armó el índice); los vectores son de CUDA.

| modo (sample_50, 41 con fundamento, v2) | doc_hit@1 | doc_hit@3 | doc_hit@10 | MRR | respaldo@10 | art_hit@1 | art_hit@10 | latencia |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bm25 | 0,390 | 0,634 | 0,805 | 0,530 | 0,927 | 0,158 | 0,368 | 2 ms |
| denso | 0,488 | 0,707 | 0,829 | 0,614 | 0,878 | 0,158 | 0,526 | 500 ms |
| **hibrido** (RRF k=60) | 0,488 | 0,732 | 0,854 | 0,619 | **0,927** | 0,263 | 0,526 | 100 ms |

- **Frente a v1 (`e01`)**: el híbrido sube de 0,907 a 0,927 en respaldo@10 y se mantiene en doc_hit@10 (0,854); baja doc_hit@1 (0,512 → 0,488) y MRR (0,643 → 0,619) por el desplazamiento léxico descrito arriba. El denso también baja (doc_hit@1 0,585 → 0,488; MRR 0,672 → 0,614). Todo son diferencias de 1–3 preguntas de 41: no concluyentes.
- **Sin el cuerpo de referencia en el top-10 (híbrido)**: #60, #748, #247, #679, #239, #661. Respecto a v1 se resuelve #563 (SU-277/2025, ahora en el corpus) y reaparece #239, que el híbrido de v1 resolvía (regresión por el desplazamiento de las sentencias nuevas). El denso falla en #58 y #1073 (y no en #60).
- Resultados por pregunta en `evaluation/retrieval/e03_corpus_v2_{bm25,denso,hibrido}.jsonl`; entorno en `evaluation/entornos/e03_corpus_v2.json`.
- Siguiente: diagnosticar los 6 fallos del híbrido (DOCUMENT_RETRIEVAL por ventanas de sentencias) antes de añadir un reranker o una cuota por tipo de documento.
## 11. Plan 05: medicion previa del reranker (2026-10-01)

Disponible `retrieval_eval.py --modo hibrido --techo-reranker --experimento e05_techo`: mide top-40 RRF, art_hit@20/@40, doc_hit@40 y distribucion del articulo correcto. Conserva MRR/top-10 del baseline; el resumen adicional va en `.meta.json` y notas del CSV. No modifica el runtime ni activa un reranker. La medicion real esta bloqueada por falta del indice local; fases del modelo condicionadas al techo y presupuesto del plan. Ver [resultados y comandos del plan 05](mejoras/resultados_05.md).

## 12. Plan 06: lookup experimental (2026-10-01)

`SYNTAX_LOOKUP=off` por defecto. La prueba de concepto usa `citations.extract` y un indice canonico/articulo desde chunks.jsonl; anade candidatos sin filtrar BM25/denso. Variantes `SYNTAX_LOOKUP_VARIANTE=a|b|c`: rama RRF, bonus fijo e insercion de hasta m articulos; fuente `SYNTAX_LOOKUP_FUENTE=consulta|pregunta`. No se aplica a BM25/denso por separado ni a menciones de cuerpo sin articulo. Los textos y offsets siguen intactos.

Fase 0 sobre sample_50 y e01_bge_m3_hibrido: 14 preguntas con cuerpo explicito (15 incluyendo opciones), cuatro con articulo explicito y cero fallos art_hit@10 entre los cuatro casos con cuerpo explicito y GT de articulo evaluable. Se conserva como prueba de concepto, sin activar ni seleccionar variante por calidad. A/B real pendiente por falta de indice local. `analisis_referencias.py` reproduce el conteo; retrieval_eval informa subconjuntos y registra lookup en meta/notas del CSV. Ver [resultados, pruebas y comandos del plan 06](mejoras/resultados_06.md).

## 13. Corpus v3: `e04_corpus_v3` (2026-10-02)

+375 documentos (ver `docs/ingesta/fuentes_pendientes.md`, sección "Ampliación v3"): 95 leyes/decretos de alto impacto por área, la Decisión Andina 351, 37 sentencias hito de la Corte Constitucional y el **lote de las 242 SU de 2020–2026** que faltaban (258 encontradas sondeando la relatoría, `SU<nnn>-<aa>.htm`). Total: 588 documentos y **113.519 fragmentos** (v2: 47.966). Nuevos: lote SU 42.430, hitos 15.391 (C-080/18, C-674/17 y T-388/13 superan los 2 M de caracteres por los salvamentos) y normas 7.732.

Motivo (análisis del `legal_basis` de sample_50 contra la semilla): 16 de 49 menciones no estaban en la semilla, 13 eran códigos (ya en v2) y 3 eran sentencias (SU-016/2020, C-468/2024, SU-277/2025, dos de ellas SU recientes). Extrapolado a las 992, faltan unas 60 preguntas cuya fuente es una sentencia que no estaba en el corpus, y cerca de 9 de 30 semiabiertas nombran la sentencia en la pregunta. Las SU están sobrerrepresentadas en el banco (18 % de las sentencias de la semilla).

BM25 en sample_50 (41 preguntas con fundamento), variantes armadas filtrando `chunks.jsonl`:

| variante | fragmentos | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 |
|---|---:|---:|---:|---:|---:|
| v2 (`e03`) | 47.966 | 0,390 | 0,805 | 0,530 | 0,927 |
| v2 + normas | 55.698 | 0,366 | 0,732 | 0,485 | 0,902 |
| v2 + normas + hitos | 71.089 | 0,366 | 0,732 | 0,478 | 0,890 |
| **v3 completo** (`e04`) | 113.519 | 0,317 | 0,707 | 0,427 | 0,866 |

- **La medición está sesgada en contra de ampliar**: todo el `legal_basis` de sample_50 ya está en v2, así que aquí solo se ve el desplazamiento léxico y nunca la ganancia. Cada escalón son 1–3 preguntas de 41. Sin el cuerpo en el top-10 (v3): #60, #290, #352, #600, #647, #748, #247, #679, #218, #239, #661, #1005; frente a v2 entran #290, #352, #600, #647, #218 y #1005, sobre todo códigos (Penal, Civil, Constitución) desplazados por las leyes nuevas.
- **Lado de la ganancia** (preguntas sintéticas, BM25 v3): 15/15 SU del lote nombradas en la pregunta ("¿problema jurídico de la sentencia SU-nnn de aaaa?", "¿antecedentes fácticos…?") traen su documento al top-10; 10/12 preguntas sobre normas/hitos nuevos lo traen (la mayoría en el rank 1; fallan Ley 361/1997 y C-590/2005 sin nombrarlas).
- **Híbrido medido en la RTX 4090** (`e04_corpus_v3`, denso codificado con `construir_indice.py --batch 64`; índice denso v2 respaldado en `data_corpus/respaldo_indice_v2/`):

| modo (41 preguntas) | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 |
|---|---:|---:|---:|---:|---:|
| híbrido v2 (`e03`) | 0,488 | 0,854 | 0,619 | 0,927 | 0,526 |
| denso v3 | 0,415 | 0,780 | 0,536 | 0,866 | 0,474 |
| **híbrido v3** | 0,390 | 0,780 | 0,515 | 0,890 | 0,421 |

  El híbrido también diluye: −0,07 en doc_hit@10 y −0,10 en MRR frente a v2. En generación (`e05_q8_rtx4090`) las sentencias nuevas copan el top-10 de las cerradas (8 de 10 en #51, 9 de 10 en #748, que pasa de A a D) aunque ninguna cerrada del sample nombra una sentencia. Decisión: **no revertir; filtrar** (sección 14).
- Mitigación posible si el híbrido también diluye: dejar el lote de SU recuperable **solo cuando la pregunta lo nombra** (filtrar sus fragmentos de las ramas BM25/denso salvo cita explícita de esa sentencia con `citations.extract`). En sample_50 daría las métricas de "v2 + normas + hitos" y conservaría los 15/15 de sentencias nombradas.

## 14. Filtro "solo por cita" (`e06`, 2026-10-02)

Los 375 documentos nuevos de v3 (279 sentencias = 242 SU + 37 hitos, y 96 normas) quedan en el corpus y en el manifest, pero **solo se recuperan si la consulta los nombra**: `retriever._filtrar` los quita de las ramas BM25 y densa salvo que `citations.extract` de la consulta (pregunta + opciones) encuentre su cuerpo canónico (`referencias.cuerpos_de`, la misma tupla que `canonico` en `chunks.jsonl`). Se filtra en cada rama antes del RRF, pidiendo candidatos de más (x4 cada vez) hasta completar 40; el orden de la rama no cambia y el resultado es determinista. El índice no se reconstruye.

- Registro versionado `data/registros/solo_por_cita.json` (grupos `sentencias` y `normas`), generado por `python src/indexacion/solo_por_cita.py` a partir del manifest de `e8e7e58` (corpus v2). No editar a mano; si se agregan documentos que deban recuperarse siempre (p. ej. un código), regenerar con otra `--base` o sacarlos del registro con el script.
- `SYNTAX_FILTRO_CITA=off|sentencias|todo`. Por defecto `todo` hasta `e15`; desde la sección 15 es `sentencias` (las normas nuevas vuelven a recuperarse sin nombrarlas, compensadas por la prioridad por área).

| híbrido (41 preguntas) | doc_hit@1 | doc_hit@3 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 |
|---|---:|---:|---:|---:|---:|---:|
| v2 (`e03`) | 0,488 | 0,732 | 0,854 | 0,619 | 0,927 | 0,526 |
| v3 sin filtro (`e04`) | 0,390 | 0,585 | 0,780 | 0,515 | 0,890 | 0,421 |
| v3 filtro `sentencias` (`e06`) | 0,488 | 0,659 | 0,829 | 0,593 | 0,927 | 0,474 |
| **v3 filtro `todo` (`e06b`)** | 0,488 | 0,707 | 0,854 | 0,613 | 0,927 | 0,526 |

- `todo` recupera las métricas de v2 y conserva las sentencias nombradas (919, 946, 563, 453, 140, 991 y 1015 en rank 1–2). Las normas nuevas también desplazaban (solo `sentencias` se queda en 0,829). Cerradas: #51 y #290 vuelven al rank 1, #352 al 4 y #58 pasa del 9 al 3.
- Consulta solo `pregunta` (`e07_consulta_pregunta`, con filtro): peor en cerradas (MRR 0,603 → 0,456; #51 al 7, #128 al 8, #352 fuera). Se mantiene `pregunta+opciones`.
- Latencia: el filtro hace una búsqueda densa extra con la consulta ya codificada (caché de la última consulta en `_codificar`); ~110 ms/consulta en caliente en la 4090. El promedio de `retrieval_eval` (~650 ms) incluye la carga del encoder.
- **Lookup por metadata (plan 06, variante a) activado por defecto** (`e12_lookup_filtro`, con filtro): doc_hit@1 0,488 → 0,537, MRR 0,613 → 0,638, art_hit@1 0,263 → 0,368; doc_hit@10 y respaldo@10 sin cambio. En generación (`e13_lookup`) cambia solo #600 (sigue correcta, norma al rank 1) y #218.
- Pendientes sin cambio: #60, #748, #247, #679, #239 y #661 siguen sin su cuerpo en el top-10 (ninguna nombra la norma; el lookup no las alcanza).

## 15. Prioridad por área de la pregunta (`e15`, `e16`, 2026-10-02)

El banco trae `area` en cada pregunta (las 992 tienen la estructura de sample_50) y la oferta del corpus está desbalanceada: constitucional tiene 340 documentos (315 sentencias) y mercados 25, procesal 28, tributario 31 y civil 35, con una demanda de ~99 preguntas por área. `area` no es ground truth (es metadata del enunciado), así que entra en `responder.CAMPOS_RUNTIME` y llega al retriever.

- `retriever.retrieve(..., area=...)`: en el híbrido, después del RRF y del lookup, el score de los fragmentos cuyo documento lleva esa área en `corpus_manifest.json` se multiplica por `SYNTAX_AREA_BOOST`. Solo reordena los candidatos de las ramas; nunca descarta (las preguntas cuyo fundamento es de otra área, p. ej. #679 constitucional → Ley 1581, siguen igual). `area=None` o factor 1.0 = sin cambio (comprobado: con 1.0 reproduce `e12` pregunta por pregunta). `meta["area_match"]` queda en la traza.
- Consecuencia: **las `areas` del manifest ahora afectan la recuperación**, no solo la nota del corpus. Propuestas para los documentos de v3/v4 en `docs/ingesta/areas_propuestas_v3.csv` (léxico por área; falta revisión humana).

| híbrido (41 preguntas) | filtro | boost | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 |
|---|---|---:|---:|---:|---:|---:|---:|
| `e12_lookup_filtro` (base) | todo | 1,0 | 0,537 | 0,854 | 0,638 | 0,927 | 0,526 |
| `e15_area115` / `130` / `150` | todo | 1,15–1,5 | 0,585 | 0,878 | 0,690–0,697 | 0,927 | 0,526 |
| `e15_normasv3_area100` | sentencias | 1,0 | 0,537 | 0,854 | 0,630 | 0,927 | 0,526 |
| `e15_normasv3_area150` | sentencias | 1,5 | 0,610 | 0,878 | 0,706 | 0,927 | 0,526 |
| **`e15_normasv3_area200`** | **sentencias** | **2,0** | **0,610** | **0,902** | **0,718** | **0,939** | **0,579** |
| `e15_normasv3_area250` / `300` | sentencias | 2,5–3,0 | 0,610 | 0,902 | 0,727 | 0,939 | 0,579 |
| `e15_sinfiltro_area150` | off | 1,5 | 0,537 | 0,829 | 0,643 | 0,927 | 0,474 |

- **Por defecto: `SYNTAX_FILTRO_CITA=sentencias` y `SYNTAX_AREA_BOOST=2.0`.** Arregla #748 (CPACA, rank 5) y #60 (CGP, rank 7); #58, #79, #674, #879, #960 suben. Solo #647 baja (4 → 5). Fallan #247, #679, #239 y #661. 2,0 es el punto donde se estancan los aciertos; 2,5–3,0 solo suben el MRR y arriesgan las preguntas de otra área.
- Con la prioridad por área, las 96 normas de v3 pueden recuperarse sin nombrarlas sin perder nada (era la condición para ampliar las áreas delgadas). Las sentencias siguen filtradas: sin filtro, ni con boost 1,5 se recupera v2 (`e15_sinfiltro_area150`).
- Generación (`e16_area200`, sin juez): cerradas 0,733 (= `e13`), **citación 16,33 → 17,55**, abstención 8,37 (=). La latencia medida (11,8 s/pregunta) no es comparable: otra sesión codificaba el corpus completo en la misma 4090 durante la corrida.

## 16. Corpus v4: áreas delgadas, C- de control y lote T 2025–2026 (`e17`, `e18`, 2026-10-02)

Ampliación automática (procedimiento y lista de descartes en `docs/ingesta/fuentes_pendientes.md`, "Ampliación v4"): **+65 documentos** (34 normas de mercados, tributario, procesal y civil; Decisiones Andinas 345, 391 y 608; 28 sentencias C- de control) y **+533 tutelas de 2025–2026** (lote sondeado en la relatoría). Total: **1.186 documentos y 173.393 fragmentos**. Los 113.519 fragmentos de v3 no cambian (comprobado byte a byte). Las sentencias nuevas (C- y T-) entran a `solo_por_cita.json` (840 sentencias y 133 normas en el registro); las normas nuevas se recuperan sin nombrarlas (filtro `sentencias`, sección 15).

Documentos por área (un documento cuenta en cada una de sus áreas; "recuperables" = sin las sentencias solo por cita):

| Área | v3 | v4 | v4 recuperables sin nombrar | fragmentos recuperables |
|---|---:|---:|---:|---:|
| Constitucional | 340 | 901 | 61 | 11.402 |
| Laboral | 56 | 62 | 51 | 6.635 |
| Familia | 49 | 54 | 46 | 7.933 |
| Administrativo | 40 | 52 | 43 | 8.614 |
| Civil | 35 | 45 | 43 | 10.127 |
| Tributario | 31 | 41 | 40 | 11.467 |
| Mercados | 25 | 39 | 38 | 6.537 |
| Penal | 45 | 51 | 37 | 10.438 |
| Comercial | 36 | 36 | 36 | 8.693 |
| Procesal | 28 | 38 | 31 | 5.587 |

| híbrido (41 preguntas, filtro `sentencias`, área ×2,0) | fragmentos | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 | ms/consulta |
|---|---:|---:|---:|---:|---:|---:|---:|
| v3 (`e15_normasv3_area200`) | 113.519 | 0,610 | 0,902 | 0,718 | 0,939 | 0,579 | — |
| **v4 (`e17_corpus_v4`)** | 124.302 | 0,610 | 0,902 | 0,718 | 0,939 | 0,579 | 729 |
| **v4 + T (`e18_corpus_v4_t`)** | 173.393 | 0,610 | 0,902 | 0,717 | 0,927 | 0,579 | 1.153 |

- **v4 no diluye nada** en sample_50 (idéntico a v3 pregunta por pregunta). Sondeo de ganancia sobre las 37 normas/decisiones nuevas: 34/34 artículos nombrados ("¿Qué establece el artículo N de la Ley X de Y?") en el top-3 (todos en el rank 1) y 37/37 documentos en el top-10 consultando solo el tema con su área (optimista: el tema sale del título).
- **Lote T**: 25/25 tutelas nombradas (muestra fija, semilla 0) en el top-10. Costo: aunque las T no entran al top-10 sin nombrarlas, **cambian las estadísticas de BM25** (IDF y longitud media se calculan con todo el índice), y eso reordena un poco el top-10 de varias preguntas: #51 pierde medio punto de respaldo (sale un pasaje de la T-262/2025 que traía su cita) y #748 pasa del rank 5 al 6. Es −1/2 pregunta de 41, dentro de la regla KEEP fijada antes de medir (≤ 1 pregunta). Latencia de recuperación +0,4 s/consulta (más candidatos filtrados en `_filtrar`). **KEEP**. Si hiciera falta recortar, la alternativa es construir BM25 sin las sentencias solo por cita (quedarían recuperables por la rama densa y el lookup).
- Parseo: `parsear_html.py` reintenta con `html.parser` cuando lxml trunca una sentencia (10 C- en Windows). Ningún `.txt` previo cambia.
- **Generación con el corpus final** (`e19_corpus_v4_t`, Qwen3-8B Q8_0 en la 4090, GPU sin otra carga): cerradas 0,733 (= `e13`), citación **17,55** (`e13`: 16,33), abstención 8,37 (=), 0 errores de schema, **4,0 s/pregunta** (recuperación 610 ms). Única corrida con juez de la ola (`e19_corpus_v4_t_ragas`, presupuesto de API): RAGAS 0,4314 y total **53,53/80**, pero el juez **no devolvió veredicto en 4 de 35 ítems** (cuentan como cero). Los 31 juzgados promedian 0,487 frente a 0,5019 de `e13`, dentro del ruido del juez (±0,03, `docs/GENERACION.md` 6). Cambiaron 21 de las 35 respuestas de texto libre (otra evidencia). No se gastó una segunda corrida con juez: no hay reversión que confirmar.


## 17. Composición del top-10 y huecos de fuente de las cerradas (`c00`–`c02`, 2026-10-02)

Base: `e24_final` (cerradas 12/15). `c00_base` la reproduce con 0 diferencias (`comparar_entregas.py`). Las tres cerradas que fallan desde `e13` son #128, #647 y #671. Rank de su fragmento clave en los 40 candidatos por rama, con la consulta pregunta + opciones y el área:

| id | fragmento clave | fusión | BM25 | denso | top-10 (normas/sentencias) |
|---|---|---:|---:|---:|---|
| #647 | `codigo_civil#art_176#p1` ("socorrerse y ayudarse mutuamente") | 17 | — | 11 | 4 / 6 |
| #671 | `ley_1692_2013#art_4` (residente de ambos Estados) | — | — | — | 10 / 0 |
| #128 | `decreto_663_1993#art_24#p1` (leasing de las compañías de financiamiento) | 46 | 37 | — | 10 / 0 |

En las 50 preguntas, 184 de los 500 puestos del top-10 son ventanas de sentencias.

**Composición del top-k** (`retriever._componer`, apagada por defecto): `SYNTAX_CUPO_NORMAS=n` garantiza al menos n fragmentos de normas en el top-k, cambiando las sentencias peor ubicadas por las mejores normas que siguen en la fusión. `SYNTAX_MAX_POR_DOC=m` permite como máximo m ventanas de una misma sentencia. Solo reordena candidatos de la fusión.

| híbrido (41 con fundamento) | doc_hit@10 | MRR | respaldo@10 | art_hit@10 | cambios |
|---|---:|---:|---:|---:|---|
| base | 0,902 | 0,717 | 0,927 | 0,579 | — |
| cupo 4–7 | 0,927 | 0,720 | 0,919–0,927 | 0,579 | +#661 |
| máx. 2 por sentencia | 0,902 | 0,722 | 0,927 | 0,579 | #60: Constitución art. 29 del rank 7 al 4 |
| **cupo 6 + máx. 2** | **0,927** | **0,724** | 0,927 | 0,579 | +#661, sin pérdidas |

| generación (sin juez) | cerradas | citación | abstención | s/pregunta |
|---|---:|---:|---:|---:|
| `c00_base` | 12/15 | 17,55 | 8,60 | 4,06 |
| `c01_cupo6m2` | 12/15 | 17,55 | 8,60 | 3,81 |
| `c02_cupo6m2_k10` (`GENERATION_K=10`) | 11/15 (pierde #528) | 17,96 | 8,60 | 4,51 |

- **c01: neutra en lo determinista**. Cambia los pasajes de 21 de las 50 respuestas. **Juez (`c01_cupo6m2_ragas`): RAGAS 0,4185** frente a 0,4401 de `e24_final` (3 ítems sin veredicto en ambas), total 54,70/80 frente a 55,35. Criterio fijado antes de medir: KEEP ≥ 0,440, REVERT < 0,41, en medio empate ⇒ gana lo más simple. **Queda apagada** (`SYNTAX_CUPO_NORMAS=0`, `SYNTAX_MAX_POR_DOC=0`).
- **c02: REVERT**. Con k=10 el modelo ve el art. 176 en #647 y aun así elige D. En #528 inventa "SMLMV ≈ 1.000.000 COP" y pasa de C a B.
- **Las tres cerradas no se arreglan con recuperación ni con generación**:
  - #647: el art. 176 iguala socorro y ayuda. La distinción "ayuda = apoyo intelectual, moral y afectivo" es doctrina y ningún fragmento del corpus la trae (búsqueda de "socorro" + "ayuda" + "moral/afectivo": 5 pasajes, ninguno la define).
  - #671: "reglas de desempate" no aparece en ninguna norma tributaria. La regla (art. 4 de los convenios) no entra a los 40 candidatos.
  - #128: "Fintech" no aparece junto a "leasing" en ninguna norma del corpus.
  - Además #528 depende del SMLMV del año, que ningún documento del corpus trae.

**Herramientas de huecos de fuente** (solo stdlib + `citations.py`, no descargan nada):

- `src/ingesta/huecos_por_citas.py`: normas que el propio corpus cita y que no están en el corpus, ordenadas por documentos citantes (47 s con multiprocessing). Tabla en `docs/ingesta/huecos_por_citas.md`: 1.006 cuerpos con ≥ 3 documentos citantes. Arriba están Leyes 715/2001, 1122/2007, 1955/2019, 1448/2011, 734/2002, 142/1994, la Ley 2294/2023 (PND) y los tratados aprobados por ley (PIDCP Ley 74/1968, CADH Ley 16/1972, OIT Ley 21/1991). Ni los convenios de doble imposición ni los decretos del SMLMV aparecen: el corpus no los cita por número.
- `src/ingesta/huecos_preguntas.py`: sobre un lote de preguntas (solo `pregunta` y `opciones`), lista las normas nombradas que no están, los artículos nombrados ausentes y los términos con df < 3 en BM25, por área. En `sample_50` encuentra la Ley 2294/2023 (#218) y la Resolución 368/2014 (#748). Los términos raros son sobre todo erratas del banco. Para el sábado: `--entrada data/test_992.jsonl --md salidas/huecos_test.md`.


## 18. Corpus v5: huecos que el propio corpus cita (`r40`, `r41`, `e41`, 2026-10-03)

Ampliación automática de v4 (procedimiento `docs/ingesta/corpus_v5_mac.md`, lista y descartes en `docs/ingesta/fuentes_pendientes.md` "Ampliación v5"): detector `huecos_por_citas.py` (≥ 10 documentos citantes, sin actos legislativos, 80 primeros) y `ampliar_desde_citas.py`. Se bajaron 72 normas; 7 decretos únicos reglamentarios se descartaron por tamaño (> 400 artículos) y 3 decretos no existen en el Senado. Los 173.393 fragmentos de v4 no cambian (mismos `chunk_id`, `texto` y orden). Las áreas de las normas nuevas se revisaron por materia (`areas_propuestas_v3.csv`, `aprobado` pendiente).

| híbrido (41 preguntas, filtro `sentencias`, área ×2,0) | fragmentos | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@10 |
|---|---:|---:|---:|---:|---:|---:|
| v4 + T (`e18_corpus_v4_t`) | 173.393 | 0,610 | 0,902 | 0,717 | 0,927 | 0,579 |
| v5 con 65 normas (`r40_corpus_v5`, MPS) | 180.817 | 0,585 | **0,878** | 0,691 | 0,927 | 0,526 |
| v5 sin PND, 61 normas (`r41_corpus_v5_sin_pnd`, CUDA) | 179.226 | 0,610 | **0,902** | 0,717 | 0,927 | 0,579 |

- **No cumple KEEP** (`doc_hit@10` ≥ 0,902). De las 41 preguntas, 39 conservan su rank; cambian dos. **#218** (rank 1 → fuera): nombra el art. 32 de la Ley 2294/2023 y el art. 313 de la Constitución (el fundamento es la Constitución); con la Ley 2294 en el corpus los 10 puestos del top-10 son de esa ley y sale el art. 313. **#748**: CPACA del rank 6 al 9 por fragmentos de las Leyes 1448/2011, 1753/2015 y 2294/2023.
- **Decisión**: retirar los 4 Planes Nacionales de Desarrollo (Leyes 2294/2023, 1955/2019, 1753/2015 y 1450/2011), leyes ómnibus que tocan cualquier tema. El corpus queda en **61 normas nuevas, 1.247 documentos y 179.226 fragmentos** (+5.833 sobre v4; v4 idéntico). Medido de nuevo en la 4090 (`r41`, abajo).
- Latencia de recuperación en un M1 con MPS: 500 ms/consulta.

**`r41` / `e41` en la RTX 4090 (v5 sin PND).** Corpus regenerado en Windows desde `data/raw/html` (`parsear_html.py --solo` con las 61 normas): los 1.247 `.txt` son idénticos al sha256 del manifest generado en el Mac, la segmentación da los mismos 179.226 fragmentos y los 173.393 de v4 son idénticos (`chunk_id`, `texto` y `retrieval_text`). Índice con `SYNTAX_DEVICE=cuda --batch 64`: 173.507 vectores de `cache_emb/` (CUDA) y 5.719 codificados (~40 s); `sha256_chunks` `6f1d931e…`. Todos los vectores son de CUDA (una sola máquina, como pide `corpus_v5_mac.md` paso 6).

- **Recuperación: cumple KEEP** (tabla de arriba): las cifras son las de v4 y fallan las mismas 4 (#247, #679, #239 y #661). De las 41 preguntas, 21 cambian algo dentro del top-10 (sobre todo por las estadísticas de BM25), pero el rank del documento de referencia solo cambia en **#748** (CPACA 6 → 7; con los PND bajaba a 9). En 9 preguntas entra alguna norma nueva al top-10 sin sacar la referencia (Ley 142/1994 en #218 y #290; Leyes 1142/2007 y 1708/2014 en #600).
- **Generación `e41_corpus_v5_sin_pnd`** (sample_50, misma configuración que `e24_final`, solo cambia el índice; `SYNTAX_LLM_CACHE=off`):

| | cerradas | citación | abstención | RAGAS | total /80 | s/pregunta |
|---|---:|---:|---:|---:|---:|---:|
| `e24_final` (v4) | 12/15 (16,0) | 17,55 | 8,60 | 0,4401 (3 sin veredicto = 0) | 55,35 | 4,4 |
| `e41_corpus_v5_sin_pnd` | 12/15 (16,0) | 17,55 | 8,60 | 0,4483 (0 sin veredicto) | **55,60** | 4,7 |

- La subida de RAGAS no es del corpus: `e24_final` tuvo 3 ítems sin veredicto del juez (cuentan 0). Juez pareado (`juez_por_item.py`, `evaluation/juez/j5_e41_corpus_v5.csv` vs `j1_e24_final.csv`) en los 10 ítems de texto libre que cambian: −0,030, mejoran 1, empeoran 3 ⇒ empate. Lo domina **#280** (0,98 → 0,53) con dos respuestas equivalentes (art. 64 del Código Penal, mismos requisitos): ruido del juez; sin #280, +0,016. **#960** mejora (+0,25).
- **Decisión: KEEP del v5 sin PND** con la regla de `corpus_v5_mac.md` paso 7 (`doc_hit@10` ≥ 0,902, `respaldo@10` ≥ 0,927, cerradas ≥ 12/15). En `sample_50` no se mide ganancia (sus normas ya estaban): no diluye. La ganancia esperada es en las 992.

## 19. Búsqueda por metadatos (`r42`–`r49`, `e25`, 2026-10-03)

Señales que ya estaban en `chunks.jsonl` y en el manifest pero que la recuperación no usaba. Todo en runtime (el índice no cambia), solo en el híbrido y con flags que **reordenan o suman candidatos, nunca filtran**. Desempate por `chunk_id`. Con todo apagado se reproduce `r41` pregunta por pregunta (`r41b_reproduce`: 0/41 top-10 distintos).

- **`SYNTAX_FACTOR_VOTO`**: multiplica el score de las ventanas `salvamento`/`aclaracion` (~18.000, votos disidentes que suelen decir lo contrario de la decisión), salvo que la consulta pida el voto (`salvamento|aclaracion de voto|disident|voto particular`).
- **`SYNTAX_FACTOR_VIGENCIA`**: lo mismo para los fragmentos `derogado` (3.669), salvo que la consulta hable de vigencia o de derogatoria. `inexequible` no se toca: el aparte tachado convive con el texto vigente.
- **`SYNTAX_CUERPO=boost|rama`**: si la consulta nombra un cuerpo que está en el corpus, `boost` multiplica por `SYNTAX_CUERPO_BOOST` (1,5) los candidatos de ese documento; `rama` agrega BM25 (`weight_mask` de bm25s) y denso (vectores del documento reconstruidos de FAISS) **restringidos a ese documento**, como dos ramas RRF de peso `SYNTAX_CUERPO_PESO`. Antes, los cuerpos nombrados sin artículo (11 de las 15 preguntas de sample_50 que nombran algo) solo servían para el filtro de sentencias.
- **`SYNTAX_ALIAS=on`** (`src/recuperacion/alias.py`): nombres que `citations.py` no reconoce. Automáticos desde el `titulo` del manifest: el nombre entre paréntesis o el que va antes de "(", si empieza por Codigo/Estatuto/Regimen/Reglamento/Convenio/Decreto Unico o tiene ≥ 4 palabras de contenido; se descarta el que apunta a más de un documento (87 nombres en v5). Fijos, pocos: la Constitución como "artículo N superior / de la Carta / norma superior" (con el artículo, que entra al lookup), "EOSF" y "Estatuto (General) de Contratación" → Ley 80/1993. Solo sirve para recuperar: no toca las citas emitidas. `python src/recuperacion/alias.py` lista los nombres para revisarlos. Ojo: "Constitución" a secas y "Carta Política" ya los reconoce `citations.py`, y el "Superior" de #60 es "Consejo Superior".
- `meta["disparos"]` (y `disparos` en `evaluation/retrieval/*.jsonl`) registra qué regla se activó. `python src/evaluacion/disparos_metadatos.py --entrada <jsonl> [--mostrar nombres|cuerpo]` cuenta los disparos de un lote sin índice ni modelos. En sample_50, el 32 % dispara la regla de cuerpo y el alias agrega #290.

Regla KEEP fijada antes de medir: doc_hit@10 y respaldo@10 ≥ base, y **ninguna pregunta pierde su cuerpo del top-10**; desempatan MRR, doc_hit@1 y art_hit@10.

| híbrido (41 con fundamento) | índice | doc_hit@1 | doc_hit@10 | MRR | respaldo@10 | art_hit@1 | top-10 distintos | cambios de rank del cuerpo |
|---|---|---:|---:|---:|---:|---:|---:|---|
| base `r41` | v5 sin PND | 0,610 | 0,902 | 0,717 | 0,927 | 0,368 | — | — |
| `r42_voto05` (= `voto025`) | v5 sin PND | 0,634 | 0,902 | 0,729 | 0,927 | 0,368 | 12 | #1015 2 → 1 |
| `r44_vigencia07` | v5 sin PND | 0,610 | 0,902 | 0,717 | 0,927 | 0,368 | 3 | ninguno |
| `r43_cuerpo_boost` (alias) | v5 sin PND | 0,634 | 0,902 | 0,729 | 0,927 | 0,368 | 10 | #272 2 → 1, #1015 2 → 1, #563 1 → 2 |
| base `r46_base_ola1` | ola 1 (181.662) | 0,610 | 0,878 | 0,713 | 0,927 | 0,368 | — | frente a `r41`: **#748 7 → fuera**, #589 art 4 → 9 |
| `r47_cuerpo_rama` (alias) | ola 1 | 0,610 | 0,878 | 0,704 | 0,927 | 0,316 | 14 | #563 **1 → 8**, #290 1 → 2, #272 y #1015 2 → 1 |
| **`r48_voto_boost`** (voto 0,5 + alias + boost) | ola 1 | **0,634** | 0,878 | **0,725** | 0,927 | 0,368 | 16 | #272 2 → 1, #1015 2 → 1, #563 1 → 2 |

- **KEEP: voto 0,5 + alias + boost.** Sin pérdidas y con mejor rank arriba. #563 (nombra la T-760/2008, fundamento SU-277/2025) baja al 2 sin salir del top-10: era el riesgo previsto.
- **REVERT: `rama`.** La búsqueda dentro del documento nombrado empuja demasiado los fragmentos de ese documento (#563 al 8). Queda disponible por flag.
- **Vigencia: neutra** (3 top-10 distintos, ninguna métrica cambia). Queda apagada: a igualdad, gana lo más simple.
- La pérdida de #748 en la ola 1 viene del corpus nuevo, no de los metadatos (pasa igual con todo apagado).
- **Generación en sample** (índice de la ola 1, Qwen3-8B Q8_0, sin juez): `e25_base` y `e25_metadatos` dan **lo mismo** (cerradas 10/15, citación 17,14, abstención 8,14, 38,61/50, 0 errores de schema, 4,1 s/pregunta; recuperación 711 → 727 ms). Queda activado por defecto porque mejora el ranking sin costo: `SYNTAX_FACTOR_VOTO=0.5`, `SYNTAX_ALIAS=on`, `SYNTAX_CUERPO=boost`. Los defaults reproducen `r48`.
- **Aviso sobre la ola 1** (no son los metadatos): frente a `e24_final` (12/15) se pierden dos cerradas. **#528** (C → B) cita el Decreto 1400/1970 (el Código de Procedimiento Civil derogado, que ahora compite con el CGP) y **#748** (A → D) se queda sin el CPACA porque la Resolución 368/2014, que nombra la pregunta, ocupa el top-10.
- Pendiente para las 992: `disparos_metadatos.py --entrada data/test_992.jsonl --mostrar nombres` (revisar a mano que los alias no se equivoquen de norma) y `analizar_test.py` para el respaldo nombrado@10.

## 20. Reranker cross-encoder (`r50`–`r55`, `e50`, `e53`, 2026-10-03)

`BAAI/bge-reranker-v2-m3` (Apache-2.0, revisión `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`) vía `sentence_transformers.CrossEncoder`, fp32, `max_length=512`. En `retriever.retrieve` (solo híbrido), después de la fusión con área, metadatos y lookup, y antes de `_componer`: puntúa (consulta, `texto` = cabecera + literal) de los `SYNTAX_RERANK_N` primeros y reordena solo ese tramo. `SYNTAX_RERANK_MODO=rrf` funde el rango de la fusión con el del cross-encoder (1/(60+r) + 1/(60+r_ce)); `puro` usa solo el cross-encoder. Los fragmentos del lookup quedan fijos en su puesto. `pasajes_recuperados.score` sigue siendo el de la fusión. Empates: score redondeado a 1e-5 y `chunk_id`. `reproducir.py` (etapa `decoder`) baja los pesos en la revisión fijada.

Techo previo (fase 0, sin lookup, índice v5 sin PND): art_hit@10 0,579 → @40 0,632 (+1 pregunta), doc_hit@10 0,878 → @40 0,951. No llegaba a la puerta del plan 05 (≥ 4 preguntas); se implementó igual para buscar la ganancia en el orden dentro del top-10 (lo que ve el decoder con `GENERATION_K=5`).

| híbrido, índice ola 1 (181.662) | doc_hit@10 | MRR | respaldo@10 | art_hit@10 | ret. ms | cambios del cuerpo/artículo |
|---|---:|---:|---:|---:|---:|---|
| base `r50` (= `r48`) | 0,878 | 0,725 | 0,927 | 0,579 | 1.173 | — |
| rrf N=40 `r51` | 0,829 | 0,699 | 0,939 | 0,579 | 1.714 | **#647 5 → fuera, #1073 7 → fuera** |
| puro N=40 `r52` | 0,829 | 0,637 | 0,915 | 0,632 | 1.241 | mismas pérdidas, #748 pierde respaldo |
| **rrf N=20 `r53`** | **0,878** | 0,700 | **0,939** | 0,579 | 1.234 | #51 respaldo 0,5 → 1; art #352 4 → 3, #358 9 → 6, #589 9 → 4; doc #58 y #79 1 → 4, #647 5 → 9 |
| puro N=20 `r54` | 0,829 | 0,659 | 0,939 | 0,579 | 1.513 | #647 fuera, #1073 fuera |
| rrf N=15 `r55` | 0,878 | 0,702 | 0,939 | 0,579 | 1.418 | ≈ N=20 |

Generación en sample (mismo índice, Qwen3-8B Q8_0, sin juez):

| | cerradas | citación | abstención | total /50 | s/pregunta |
|---|---:|---:|---:|---:|---:|
| `e50_base` (= `e25_metadatos`) | 10/15 | 17,14 | 8,14 | 38,61 | 4,5 |
| **`e53_rerank_rrf20`** | 10/15 | **17,55** | 8,14 | **39,02** | 4,6 |

- **KEEP: rrf N=20, activado por defecto.** No saca ningún cuerpo del top-10, sube respaldo@10 y citación (+0,41/50), y cuesta +0,1 s/pregunta. N=40 y `puro` dejan subir candidatos de la cola que desplazan documentos buenos.
- Cambian los pasajes de las 50 respuestas (todo reordenamiento cuenta). **Juez** (las dos entregas en paralelo, mismo índice; regla fijada antes: REVERT si cae más de 0,03): `e50_base_ragas` 0,4503 → `e53_rerank_rrf20_ragas` **0,4565** (+0,006, dentro del ruido ±0,03), total **52,12 → 52,72/80**. Sin ítems sin veredicto. No baja: se mantiene KEEP.
- Medido sobre el índice de la ola 1. Tras congelar el índice del sábado hay que repetir `r50`/`r53` y el determinismo (dos corridas con `SYNTAX_LLM_CACHE=off` → `comparar_entregas.py` = 0 diferencias, también entre máquinas) antes de la corrida final. Apagar con `SYNTAX_RERANKER=off`.

## 21. Parámetros de la fusión (`f00`–`f06`, 2026-10-03)

`RRF_K`, candidatos por rama y peso de cada rama estaban fijos (60, 40, 1:1) y nunca se habían medido. Quedan como variables de entorno con esos mismos valores por defecto: `SYNTAX_RRF_K`, `SYNTAX_N_CANDIDATOS`, `SYNTAX_PESO_BM25`, `SYNTAX_PESO_DENSO`. Índice v5 congelado (185.215 fragmentos), reranker rrf N=20 y metadatos activados, 41 preguntas con fundamento. Regla KEEP fijada antes: doc_hit@10 y respaldo@10 ≥ base, ningún cuerpo sale del top-10, sube MRR o art_hit.

| variante | doc_hit@1 | doc_hit@10 | MRR | art_hit@10 | respaldo@10 | cambios |
|---|---:|---:|---:|---:|---:|---|
| base `f00` (k 60, 40 cand.) | 0,634 | 0,878 | 0,700 | 0,579 | 0,939 | — (= `r53`) |
| `f01_k20` | 0,634 | 0,878 | 0,706 | 0,579 | 0,939 | art #589 4 → 3, #1089 6 → 4; doc #58 4 → 2, #647 9 → 10 |
| `f02_k100` | 0,634 | 0,878 | 0,699 | 0,579 | 0,939 | ±1 puesto en 3 preguntas |
| `f03_cand100` | 0,659 | 0,829 | 0,711 | 0,579 | 0,939 | **#647 y #1073 fuera** |
| `f04_cand200` | 0,659 | 0,829 | 0,715 | 0,526 | 0,951 | #647 y #1073 fuera, art #358 fuera |
| `f05_denso15` | 0,634 | 0,854 | 0,703 | 0,579 | 0,927 | #1073 fuera, respaldo #51 1 → 0,5 |
| `f06_bm2515` | 0,659 | 0,854 | 0,723 | 0,526 | 0,939 | #647 fuera, art #358 y #589 fuera |

- **Se mantienen los valores de siempre.** Más candidatos o más peso a una rama sube el rank 1 pero deja entrar candidatos de la cola que el boost de área (×2) empuja sobre el documento bueno (el mismo patrón del reranker N=40). `k=20` cumple la regla, pero la ganancia es de 2 artículos en 41 y deja #647 en el borde (puesto 10). No justifica cambiar la configuración congelada horas antes de la corrida final.
- Conclusión: con el corpus congelado, la recuperación está en su techo de runtime. Los fallos que quedan (#247, #679, #239, #661) no nombran su norma y los fallos de artículo son de ranking dentro del documento correcto.
## 22. Sentencias y derogados detrás de la norma (`r60`–`r64`, 2026-10-03)

Diagnóstico sobre el v5 congelado (`r60_base`, con reranker rrf20): de las 15 preguntas cuyo cuerpo no queda en el top-1, en 6 lo ocupa una ventana de sentencia en una pregunta conceptual que no nombra ninguna (#60 T-323/2024, #647 T-1096/2008, #661 C-389/2023, #490, #617, #352). El 72 % de los fragmentos (133.626 de 185.215) son sentencias. En otras dos (#589, #528) compite el Decreto 1400/1970 (el CPC, derogado entero por el CGP), que casi no tiene fragmentos marcados `derogado`, así que `SYNTAX_FACTOR_VIGENCIA` no lo toca.

Dos factores en runtime, del mismo tipo que `FACTOR_VOTO` (multiplican el score de la fusión antes del reranker, no filtran), **activados por defecto en 0,5** (apagar con `=1.0`):

- `SYNTAX_FACTOR_SENTENCIA`: ventanas `tipo == sentencia`, salvo que la consulta nombre una sentencia (`citations.py`/alias) o diga `sentencia|jurisprudenc|precedente|subregla|ratio decidendi|providencia|fallo`. En el test se activa en 778 de 992 preguntas. Disparo `factor_sentencia`.
- `SYNTAX_FACTOR_DEROGADA`: documentos derogados enteros (`config.DOCS_DEROGADOS`: Decreto 1400/1970, Decreto 01/1984 y Decreto 2737/1989), salvo que la consulta los nombre o hable de vigencia.

| híbrido (41 con fundamento) | doc_hit@1 | doc_hit@3 | doc_hit@10 | MRR | respaldo@10 | art_hit@1 | art_hit@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `r60_base` | 0,634 | 0,732 | 0,878 | 0,700 | 0,939 | 0,368 | 0,579 |
| `r61_sent07` | 0,659 | 0,780 | 0,878 | 0,732 | 0,927 | 0,421 | 0,579 |
| `r62_sent05` | 0,659 | 0,805 | 0,878 | 0,738 | 0,927 | 0,421 | 0,579 |
| `r63_derog05` | 0,610 | 0,732 | 0,878 | 0,692 | 0,939 | 0,368 | 0,579 |
| **`r64_sent05_derog05`** | **0,659** | **0,805** | 0,878 | **0,742** | 0,927 | **0,421** | 0,579 |

- `r64` sube 8 preguntas (#60 8 → 2, #647 9 → 2, #352 3 → 1 con el artículo, #617 2 → 1, #490 5 → 3, #589 3 → 2 y art. 4 → 2, #1089 art. 6 → 5) y ningún cuerpo sale del top-10.
- Pierde **#51**: respaldo 1 → 0,5, porque el art. 88 de la Constitución solo estaba respaldado por una ventana de la SU-429/2024 que lo cita, y el factor la saca del top-10. Además #879 baja de 1 a 2 (sin sentencias en su top-10: es reacomodo del reranker rrf).
- No cumple la regla KEEP de la sección 19 (respaldo@10 0,939 → 0,927), así que se midió la generación.

Generación en sample (Qwen3-8B Q8_0, servidor compartido con otra sesión: las latencias absolutas no son comparables):

| | cerradas | citación | abstención | total /50 | schema | recuperación ms |
|---|---:|---:|---:|---:|---:|---:|
| `e60_base` (= `e53`) | 10/15 | 17,55 | 8,14 | 39,02 | 0 | 1.417 |
| `e64_sent05_derog05` | 10/15 | 17,55 | 8,14 | 39,02 | 0 | 1.355 |

- **Empate en lo determinista.** La pérdida de respaldo de #51 no cuesta puntos: la cita perdida es la SU-429/2024, que no está en el `legal_basis`; la Ley 472 sigue citada. #1065 deja de citar la C-015/2018 (tampoco puntuaba) y #168 agrega la Ley 57/1887.
- Las cerradas que suben de rank (#60, #352, #617, #647) no cambian de respuesta. En #647 el diagnóstico pasa de RANKING a GENERATION: el Código Civil ya está en el puesto 2 y el modelo igual se equivoca (doctrina, sección 17).
- **KEEP, activado por defecto** (decisión del equipo, 2026-10-03): mejor ranking a igual puntaje determinista. Sin juez: el texto libre cambia en las preguntas reordenadas. `r65_defaults` reproduce `r64` (0/50 top-10 distintos).
