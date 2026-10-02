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
