# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> `AGENTS.md` es una réplica exacta de este archivo para otros agentes (Codex, Gemini, Cursor…). **Editar solo `CLAUDE.md` y regenerar la copia** (ver "Sincronizar AGENTS.md").

# Proyecto

Hackathon LATAM AI Week 2026 (Uniandes): **RAG de derecho colombiano** con un decoder abierto de **≤ 8B parámetros**, `temperature=0`, sobre un **corpus jurídico que construimos nosotros**. El equipo se llama **Syntax**: usar exactamente ese nombre donde las plantillas dicen `<Nombre del equipo>` (`CORPUS.md`, `README.md`, `LICENSE`, campo `equipo` de `corpus_manifest.json`, nombre del comprimido del corpus). Somos 3 (Sofía Morato, Joel David Niño, Santiago Muñoz), mezcla de Windows y Mac, con acceso a máquinas potentes en el campus.

Plazos: **vie 17:00** reporte de avance (PDF de 1 página por correo) · **sáb 09:00** se entregan las 992 preguntas · **sáb 15:00** cierre (repo + enlace público al corpus/índice) y verificación en vivo. Las 992 preguntas deben correr en ~6 h ⇒ objetivo **< 10 s/pregunta** (límite teórico 21,8 s).

**Estado (2026-10-02, tarde):** RAG de punta a punta en la RTX 4090 con Qwen3-8B Q8_0. **Corpus v4: 1.186 documentos, 173.393 fragmentos** (v3 + 34 normas de las áreas delgadas, Decisiones Andinas 345/391/608, 28 C- de control y 533 tutelas 2025–2026; `docs/INDEXACION.md` 16). Recuperación: filtro `sentencias` (las sentencias nuevas solo se recuperan si la consulta las nombra; las normas sí) + **prioridad por el `area` de la pregunta** (`SYNTAX_AREA_BOOST=2.0`, sección 15): doc_hit@10 0,854 → 0,902, respaldo@10 0,927. Generación `e19_corpus_v4_t`: cerradas 11/15, citación 17,55, abstención 8,37, ~4,0 s/pregunta; con juez 53,53/80 (4 ítems sin veredicto del juez; los juzgados promedian 0,487 ≈ `e13`). Defaults: lookup `on`, `CITAR_EVIDENCIA=top10`, prompt `p-v0` + **glosario de normas** (`SYNTAX_GLOSARIO=on`: título del manifest y equivalencia nombre ↔ número en el prompt; arregla #58), sin thinking. **`e24_final`: cerradas 12/15, 42,15/50 sin juez, 55,35/80 con juez, 4,4 s/pregunta.** Planificador agéntico (query translation + normas del 8B), una consulta por opción y prompt p-v2 de cerradas: medidos y REVERT (`docs/GENERACION.md` 9: el 8B no recuerda números de artículo y la multi-consulta diluye el RRF). Las cerradas que fallan (#128, #647, #671) son de doctrina/corpus. **Las `areas` del manifest afectan la recuperación**: revisar `docs/ingesta/areas_propuestas_v3.csv`. Toda ampliación nueva es automática (sin búsqueda manual) y las sentencias van a `solo_por_cita.json`.

**Sábado (confirmado por la organización el 2026-10-02): se pueden revisar las 992 preguntas y ajustar el corpus antes de responder.** Guion completo, roles, comandos y tiempos medidos en el simulacro: **`docs/SABADO.md`**. La v4 congelada (tag `avance-viernes`, `entregas/viernes/CONGELADO.md`) es el corpus de respaldo. La ampliación del sábado se dirige por las preguntas:
- `src/evaluacion/analizar_test.py`: cuerpos nombrados que faltan, hojas de triage por área y respaldo nombrado@10 (sin ground truth);
- `src/ingesta/ampliar_desde_citas.py`: resolver → descargar → parsear → validar → `--indexar`, ~4 min por ola; lo no resuelto va a la cola manual acotada (≥ 2 preguntas, 45 min por persona);
- caché del decoder por hash de la petición (`SYNTAX_LLM_CACHE=on|off`, `salidas/cache_llm/`): repetir las 992 con el índice nuevo solo regenera lo que cambió; la verificación en vivo corre con `off`;
- `main.py --particion I/N` + `src/evaluacion/unir_entregas.py` para repartir entre máquinas.
- `santiago-cerradas` (2026-10-02, noche): composición del top-10 (`SYNTAX_CUPO_NORMAS`, `SYNTAX_MAX_POR_DOC`) medida y **apagada** (juez 0,4185 vs 0,4401, empate); `src/ingesta/huecos_por_citas.py` (normas que el corpus cita y no tiene) y `src/ingesta/huecos_preguntas.py`; procedimiento de un corpus v5 desde un Mac en `docs/ingesta/corpus_v5_mac.md` (`docs/INDEXACION.md` 17).
- `santiago-metadatos` (2026-10-03): **búsqueda por metadatos activada por defecto** (`docs/INDEXACION.md` 19): `SYNTAX_FACTOR_VOTO=0.5` (salvamentos/aclaraciones detrás), `SYNTAX_ALIAS=on` (nombres de normas desde los títulos del manifest + pocos fijos, `src/recuperacion/alias.py`) y `SYNTAX_CUERPO=boost` (×1,5 a los fragmentos del cuerpo nombrado). doc_hit@1 0,610 → 0,634 y MRR 0,713 → 0,725, sin pérdidas; generación igual. `rama` (búsqueda dentro del documento) REVERT; vigencia neutra (apagada). `src/evaluacion/disparos_metadatos.py` cuenta los disparos en las 992.
- `santiago` (2026-10-03, tarde): **consulta sin la instruccion de lectura activada por defecto** (`SYNTAX_SIN_PREAMBULO=on`, `docs/INDEXACION.md` 22): la busqueda ignora "Habiendo hecho la lectura previa de la Resolucion 368/2014... responda" (bloque #721-#752 del test); #748 de D a A, doc_hit@10 0,878 -> 0,902. Tope por norma (`SYNTAX_MAX_POR_DOC_NORMAS`) medido y REVERT (seccion 21).
- **Hecho**: corpus v2 de 213 documentos → 47.966 fragmentos (seg-v1; índice híbrido BM25 + bge-m3 + RRF v2 medido en `e03_corpus_v2`: respaldo@10 0,927, doc_hit@10 0,854; el denso se codificó en GPU de Kaggle y se armó en local, ver `docs/INDEXACION.md` sección 10). Antes: 167 documentos → 35.105 fragmentos → índice híbrido BM25 + bge-m3 + RRF (`docs/INDEXACION.md`) → generación con Qwen3-8B servido en local por llama.cpp, citas validadas contra el top-10, schema y `evaluate.py` (`docs/GENERACION.md`, corrida `e02_v0`).
- **Falta**: (1) elegir y medir la máquina final (en un Mac M1 de 16 GB el 8B tarda ~145 s por pregunta; para las 992 hay que bajar de ~20 s); (2) iterar según `evaluation/generacion/<exp>/errores.csv`; (3) diagnosticar los 4 fallos de recuperación que quedan (#247, #679, #239, #661; ninguno nombra su norma); revisar y aplicar `docs/ingesta/areas_propuestas_v3.csv`; RAGAS varía ±0,03 entre corridas del juez: no ajustar texto libre con una sola corrida; confirmar las áreas de `docs/ingesta/areas_por_asignar.md`; (4) comando único en contenedor limpio y empaquetado/publicación del corpus; (5) interfaz.

Los archivos oficiales viven también en `../Hackathon 2026/` (`enunciado.pdf`, `entregables/`, `Ejemplo de entrega/`). **El código oficial y el schema mandan sobre cualquier documento, incluido este.**

## Comandos

```bash
# Autoevaluar (determinista, sin API): 20 cerradas + 20 citas + 10 abstención
python scripts/evaluate.py --submission entrega.jsonl --split sample

# Con juez de texto libre (30 pts): requiere OPENROUTER_API_KEY (env o scripts/.env, nunca versionar)
pip install -r scripts/requirements-evaluador.txt
python scripts/evaluate.py --submission entrega.jsonl --split sample --ragas
```

```bash
# Validar corpus_manifest.json contra data_corpus/ (corpus/ e indice/); --strict para la entrega
python src/validaciones/manifest.py
```

```bash
# Descargar las fuentes de data/registros/seed_targets.json a data/raw/ (solo stdlib, idempotente: salta lo que ya está en data/raw/)
python src/ingesta/descargar_fuentes.py                  # --solo <doc_id>... | --limite N | --forzar
python src/ingesta/descargar_fuentes.py --corpus-md      # regenera el inventario de CORPUS.md desde data/registros/fuentes_descargadas.json
```

`data/registros/fuentes_descargadas.json` (versionado) registra por `doc_id` la URL real, fuente, fecha de consulta, estado (`descargado | no_encontrado | sin_resolver | errata | error`) y sha256 de lo descargado. Los originales van en `data/raw/` (**versionada en git**, ~87 MB: es la evidencia de la fuente y evita depender de que los sitios sigan respondiendo; no está en `.gitignore`): HTML en `data/raw/html/<doc_id>/` (todas las partes de la norma), PDF en `data/raw/pdf/` con su entrada en `data/registros/mapa_archivos.json` (el script la agrega), RTF/DOCX manuales en `data/raw/rtf/`. Lo que ya está en `data/raw/` (p. ej. los PDF/RTF bajados a mano de la Constitución, el CGP y las demás normas de alto impacto) no se vuelve a descargar: solo se registra. Resolución de URLs (las de la semilla son de búsqueda): Senado (normas, con sus partes `_prNNN`); si el Senado da 404 (leyes anteriores a 1992, decretos), el mismo nombre de archivo en los espejos de la compilación de Avance Jurídico (`normas.cra.gov.co`, `normativa.colpensiones.gov.co`, `cancilleria.gov.co`); relatoría de la Corte Constitucional (C/T/SU); PDF de la CAN (Decisión 486). **`data/registros/fuentes_override.json`** (versionado, a mano) manda sobre las reglas: corrige erratas de la semilla (p. ej. `decreto_1563_2012` → `ley_1563_2012`, `ley_11500_2007` es `ley_1150_2007`) y da URLs que no siguen patrón; solo URLs verificadas. SUIN-Juriscol ya no se puede raspar (aplicación Angular sin HTML) y la relatoría de la Corte Suprema (SL/SP/SC) no tiene URLs predecibles: esos objetivos quedan `sin_resolver` para descarga manual a `data/raw/pdf/` + `mapa_archivos.json`.

```bash
# Parsear los originales de data/raw/{pdf,rtf,html}/ a texto limpio en data_corpus/corpus/<doc_id>.txt
python src/ingesta/parsear_pdf.py      # PDF (PyMuPDF); los doc_id de OCR_FORZADO por Tesseract spa (brew install tesseract tesseract-lang)
python src/ingesta/parsear_rtf.py      # RTF y DOCX (pandoc: brew install pandoc); --solo <doc_id>... | --forzar
python src/ingesta/parsear_html.py     # data/raw/html/<doc_id>/ (BeautifulSoup + lxml); salta los doc_id que ya tienen .txt (fuente manual PDF/RTF)
```

Los parsers detectan el formato **por contenido, no por extensión** (en `data/raw/rtf/` hay `.rtf` que en realidad son DOCX; algunos PDF traen bytes antes de `%PDF`). El `doc_id` sale de `data/registros/mapa_archivos.json` (archivo original → `doc_id`; agregar ahí cada archivo nuevo, un archivo sin entrada es error y no detiene el lote). Si un `doc_id` tiene fuente nativa (RTF/DOCX) y PDF, se usa la nativa. La limpieza (`src/ingesta/_texto.py`) es solo estructural: NFKC (ligaduras), encabezados/pies repetidos, guiones blandos, saltos de línea dentro de párrafo y tablas de pandoc; el contenido normativo no se reescribe. Salida: párrafos separados por línea en blanco, más `data_corpus/parseo.json` (fuera de `corpus/`, que se publica tal cual) con `archivo_original`, `formato_real`, `metodo_ingesta` y `sha256` del `.txt`, base para generar `corpus_manifest.json`. Un PDF con < 200 caracteres/página se marca como posible escaneado. El OCR está en `parsear_pdf.py`: la lista fija `OCR_FORZADO` (escaneados o con capa OCR ilegible) pasa por Tesseract 5 `spa` a 300 dpi, como binario del sistema vía `subprocess` (igual que pandoc, sin dependencias de pip); se eligió sobre Docling porque las sentencias son prosa a una columna y Docling arrastra torch y modelos de layout sin ganancia. `SIN_ORDENAR` extrae sin ordenar por coordenadas los PDF de diapositivas con texto en capas.

`parsear_html.py` tiene un extractor por fuente, elegido por contenido. **Compilación de Avance Jurídico** (Senado y espejos): une las partes en orden (`<base>.html` y luego `_pr001`, `_pr002`…), toma solo el cuerpo de la norma (`div#aj_data` interno o `div.panel-documento`) y quita el índice de navegación, las cajas "Jurisprudencia Vigencia" (vacías, las llena JavaScript), el pie de Avance Jurídico y la sentencia de control que a veces viene pegada al final tras `<NOTA DEL EDITOR ...>` (Ley 1581/2012: 822k → 33k caracteres). Conserva las notas cortas en línea (`<Artículo modificado por …>`, `<Aparte tachado INEXEQUIBLE>`) y el texto tachado: son hechos de vigencia y así lo publica la fuente. **Relatoría de la Corte Constitucional** (HTML de Word): todo el cuerpo con sus notas al pie. En HTML solo `<br>` es salto de línea (Word parte las líneas del código fuente). Registra en `parseo.json` `extractor`, `n_partes` y `n_articulos_detectados`, y avisa si hay saltos en la numeración de artículos (falta una parte `_prNNN`).

```bash
# Segmentar corpus/*.txt -> data_corpus/indice/chunks.jsonl + resumen_indice.json (sin deps de ML, ~1 min)
python src/indexacion/segmentar.py                          # --solo <doc_id>... (solo tabla) | --mostrar <doc_id> [<art>|w0001]
# Indice: bm25/ + index.faiss (bge-m3, fp32) + indice_info.json; actualiza n_fragmentos/sha256 del manifest
python src/indexacion/construir_indice.py                   # --solo-bm25 (sin encoder) | --batch 64 | --no-manifest
SYNTAX_DEVICE=cuda python src/indexacion/construir_indice.py --batch 64    # campus; cuda|mps|cpu|auto
# Probar y medir la recuperacion (legal_basis solo como evaluacion)
python src/recuperacion/retriever.py "consulta" --modo bm25|denso|hibrido -k 10
python src/evaluacion/retrieval_eval.py --modo bm25 denso hibrido --experimento <nombre>   # --no-csv para no registrar
```

Estado, resultados medidos, problemas conocidos y trampas de la indexación: **`docs/INDEXACION.md`** (leerlo antes de tocar `src/indexacion/` o `src/recuperacion/`).

Segmentación (`src/indexacion/segmentar.py`, versión `seg-v1`):

- **Normas**: un artículo = un fragmento; si pasa de 350 palabras se parte por párrafos (y un párrafo enorme por oraciones) en `#p1..#pN` sin solapamiento. El texto previo al primer artículo va como `#pre#pN` con `articulo=null`. Los encabezados LIBRO/TÍTULO/CAPÍTULO no entran al fragmento: se guardan en `seccion`. **Normas modificatorias**: tras un "…quedará así:" (o un encabezado entre comillas) se entra en modo cita, y los "ARTÍCULO N" transcritos quedan dentro del artículo propio hasta que la numeración vuelve a la de la norma (Ley 1819/2016 art. 10 contiene el art. 247 del ET, no es un "art. 247 de la Ley 1819").
- **Sentencias**: ventanas de ~350 palabras con párrafos enteros, 1 párrafo de solapamiento si es corto, sin cruzar secciones (`sintesis | antecedentes | consideraciones | resuelve | salvamento | aclaracion`).
- **`texto` de cada fragmento = cabecera citable + `"\n"` + `corpus[inicio:fin]` literal**, y va tal cual a `pasajes_recuperados.texto`. Motivo: el evaluador da por respaldada una cita solo si `citations.extract()` la encuentra en el texto del pasaje (`evaluate.citas_respaldadas`), y un artículo suelto no extrae ninguna norma. La cabecera tiene la forma "Artículo 42 del Código General del Proceso." / "Corte Constitucional, Sentencia C-355 de 2006." (`src/indexacion/cabeceras.py`) y se valida con `bodies(extract(cabecera)) == {canonico}`. Otras formas fallan: "Constitución Política de Colombia, artículo 29" pierde el artículo, y "Código Civil (Ley 57 de 1887)" agrega un cuerpo espurio. `retrieval_text` (lo que ven BM25 y el encoder) agrega título, siglas y sección.
- **Cuerpo canónico**: clave de `citations.CODES` → regex del `doc_id` → `canonico` de `fuentes_descargadas.json`. El `doc_id` manda porque la semilla arrastra erratas del banco (`ley_1563_2012` figura como "Decreto 1563 de 2012", `decreto_2737_1989` como "Ley 2737 de 1989", `ley_964_2005` como "Ley 964 de 2006"): la cabecera usa la norma correcta aunque esos ~4 ítems citen la forma errónea.
- Invariantes que se comprueban al segmentar (exit 1 si fallan): `texto` = cabecera + literal, fragmentos de una norma sin solaparse, `chunk_id` únicos. Los artículos detectados (números base: `38A` y `12-1` cuentan con 38 y 12, sin transitorios) se comparan con `n_articulos` del manifest. Ojo: en normas modificatorias el manifest a veces cuenta los artículos transcritos (Ley 50/1990: 171; Ley 80/1993: 86, cuando tiene 81).
- **Determinismo**: los vectores del corpus se calculan una vez (caché en `data_corpus/cache_emb/`, por sha256 del `retrieval_text`) y la consulta se codifica siempre en fp32. Los empates se desempatan por `chunk_id`. `ENCODER_REVISION` fija el commit de `BAAI/bge-m3` en Hugging Face.

```bash
# Decoder local (llama.cpp): brew install llama.cpp | binario de GitHub releases (CUDA/CPU)
python src/generacion/modelo.py descargar       # GGUF a modelos/ (revision + sha256 de config.LLM_MODELOS)
python src/generacion/modelo.py servir          # otra terminal: llama-server en 127.0.0.1:8080 (-np 1, sin mmap, temp 0)
# Generar (se reanuda si se cae) y evaluar
bash run.sh                                     # = python src/main.py --split sample
python src/main.py --split sample --experimento <exp> [--limite N | --ids ...]
python src/main.py --split test                 # sabado: data/test_992.jsonl -> submissions.jsonl
python src/evaluacion/evaluar_entrega.py --entrega salidas/sample_<exp>.jsonl --experimento <exp> [--ragas]
python src/evaluacion/comparar_entregas.py a.jsonl b.jsonl    # determinismo / verificacion en vivo
```

```bash
# Reproduccion en maquina limpia (Windows+NVIDIA / Linux): entorno -> corpus -> indice -> decoder -> preguntas -> evaluar
powershell -ExecutionPolicy Bypass -File reproducir.ps1 -Corpus C:\ruta\corpus   # Windows; instala Python 3.13 si falta
python src/reproducibilidad/reproducir.py --corpus <carpeta|zip>                  # las 6 etapas sobre sample_50
# Modular: una o varias etapas, y que preguntas responder
python src/reproducibilidad/reproducir.py --solo indice [--reindexar]
python src/reproducibilidad/reproducir.py --solo preguntas --split test --rango 100-200   # o --ids 51 60 | --limite N | --particion 2/4 | --entrada <jsonl>
python src/reproducibilidad/reproducir.py --solo evaluar --entrega submissions.jsonl --split test
python src/reproducibilidad/reproducir.py --dry-run --desde preguntas --split test         # plan + prerrequisitos que faltan, sin ejecutar
```

`reproducir.py` (solo stdlib) es el contrato de "contenedor vacio" y **parte de que `data_corpus/corpus/*.txt` ya existe** (reconstruir el corpus con `src/ingesta/` es aparte). Seis etapas modulares (`--solo a,b` | `--desde` | `--hasta` | `--dry-run`): `entorno`, `corpus`, `indice`, `decoder`, `preguntas`, `evaluar`. Una etapa aislada no re-ejecuta las anteriores: comprueba sus prerrequisitos (`.venv`, `.txt`, indice vigente, entrega) y falla diciendo que comando los resuelve; `preguntas` levanta el servidor por su cuenta si no hay uno. Entorno: instala `requirements.txt` **y** `scripts/requirements-evaluador.txt` y comprueba el conjunto (`pip check`, `verificar_deps.py --evaluador`: instalado, en rango e importable). `evaluar` valida el schema siempre (`validar_entrega.py`) y puntua: sample completo con `evaluar_entrega.py`, test con `evaluate.py` solo si estan los archivos del jurado (`answer_key_992.jsonl`, `scoring_subset.json`); el juez de texto libre corre si hay `OPENROUTER_API_KEY` (entorno o `scripts/.env`), con `--ragas` se exige y con `--sin-ragas` se apaga. Crea `.venv`, cambia torch por la rueda CUDA (cu126/cu130 segun el driver; la de PyPI en Windows es CPU), exige los `.txt` identicos al sha256 del manifest, segmenta, comprueba `chunks.jsonl` contra `hashes_esperados.json`, codifica en GPU (`--batch 64`), baja llama.cpp `b11146` a `herramientas/` (en `.gitignore`) y el GGUF verificado, levanta `llama-server`, corre `main.py`, evalua y reporta latencia media y horas proyectadas para 992. En Mac no baja llama.cpp (`brew install llama.cpp`). **Todo cambio de dependencias o pasos del pipeline debe seguir funcionando con este script desde cero.**

Estado, decisiones, latencias medidas y trampas de la generación: **`docs/GENERACION.md`** (leerlo antes de tocar `src/generacion/` o `src/main.py`). Claves:

- `responder(item, retriever, decoder)` (`src/generacion/responder.py`) deja pasar solo `id, formato, pregunta, opciones` (guarda contra el ground truth), recupera el top-10 híbrido, manda los `GENERATION_K=5` primeros al decoder y valida **todo** el texto de la respuesta con `scripts/citations.py` contra los 10 pasajes. Si hay citas sin respaldo, regenera 1 vez, luego quita esas oraciones y, si queda un campo vacío, se abstiene. Después agrega las cabeceras de la evidencia a los campos citables (`CITAR_EVIDENCIA`).
- **Determinismo**: `temperature=0`, `seed=0`, `-np 1`, `cache_prompt=false` y `enable_thinking=false`. Comprobado: dos corridas dan salidas idénticas. La salida del decoder se restringe por JSON Schema (gramática de llama.cpp).
- `SYNTAX_LLM` elige el GGUF (`qwen3-8b-q4` | `qwen3-4b-2507-q4`), `SYNTAX_LLM_URL` el endpoint, `SYNTAX_GENERATION_K` y `SYNTAX_CITAR_EVIDENCIA` los hiperparámetros. Cambiar un texto de `prompts.py` = subir `PROMPT_VERSION`.
- Cada corrida deja `salidas/trazas/<exp>.jsonl` (+ `.meta.json` con GGUF, build de llama.cpp, prompt y sha del índice); `evaluar_entrega.py` las copia, junto con el reporte oficial y `errores.csv` (diagnóstico por pregunta), a `evaluation/generacion/<exp>/` (versionado) y agrega la fila en `experiments.csv`.

Pendiente del contrato de entrega: en un contenedor limpio, `run.sh` aún asume el índice presente y el servidor levantado (ver `docs/GENERACION.md`, sección 7).

## Entorno y dependencias (`src/reproducibilidad/`)

Cuatro scripts, solo stdlib (corren sin instalar nada, en Windows y Mac):

```bash
python3.13 src/reproducibilidad/preparar_entorno.py      # crea .venv, instala requirements.txt y verifica deps
python3.13 src/reproducibilidad/preparar_entorno.py --evaluador --recrear   # + deps del juez; .venv de cero
python src/reproducibilidad/verificar_deps.py            # exit 1 si un import de src/ no está en requirements.txt o no está fijado
python src/reproducibilidad/verificar_deps.py --fix      # agrega los faltantes ya instalados como paquete==version
python src/reproducibilidad/registrar_entorno.py --salida evaluation/entornos/<experimento>.json   # commit, python, SO, device, paquetes
python src/reproducibilidad/verificar_corpus.py   # exit 1 si corpus/ o chunks.jsonl locales difieren de los congelados (--actualizar solo en la máquina de referencia)
```

**Regla para todos los agentes: `requirements.txt` crece junto con los imports, nunca después.** Al introducir un import de un paquete de terceros en `src/`:

1. `pip install <paquete>` dentro de `.venv` (activar con `source .venv/bin/activate` en Mac o `.venv\Scripts\activate` en Windows).
2. `python src/reproducibilidad/verificar_deps.py --fix`: agrega `paquete==version` (versión instalada, orden alfabético) a `requirements.txt`. Nunca escribir líneas sin `==`.
3. Si el nombre del import difiere del paquete de pip y no está en el diccionario `ALIAS` de `verificar_deps.py` (p. ej. `fitz`→`pymupdf`, `faiss`→`faiss-cpu`, `sklearn`→`scikit-learn`), agregarlo ahí.
4. Volver a correr `verificar_deps.py` hasta que diga `ok`, y commitear el import y la línea de `requirements.txt` **en el mismo commit**.

Detalles:

- Se escanea todo `src/` con `ast` (también los imports dentro de funciones, como el `import faiss` de `config.verificar_indice()`, que hoy falta declarar). Se ignoran stdlib, `__future__` y módulos locales (`src/*`, `scripts/*`, p. ej. `config`, `citations`).
- Import opcional a propósito (backend alternativo, detección de `torch` en `registrar_entorno.py`): marcar la línea con `# dep: opcional`, cargarlo dentro de la función que lo usa y protegerlo con `importlib.util.find_spec`. No usar el marcador para saltarse una dependencia real del pipeline.
- Deps que no se importan directamente (p. ej. `accelerate`, runtime de `transformers`) se agregan a mano con `==`; `verificar_deps.py` solo las muestra como aviso.
- `scripts/requirements-evaluador.txt` es oficial del jurado: no editarlo. Nuestras deps van solo en `requirements.txt` de la raíz.
- Ruedas de GPU (`torch` con CUDA, `llama-cpp-python` con Metal/CUDA) dependen de la plataforma: fijar la versión en `requirements.txt` y documentar en `README.md` el índice o flag de instalación por plataforma, no mantener archivos de requirements separados por máquina.
- Cada fila de `evaluation/experiments.csv` debe poder enlazar su JSON de `registrar_entorno.py`; la corrida final de las 992 guarda el suyo como prueba de la configuración congelada.

## Contrato de datos (verificado en el código)

- **Entrada**: `data/sample_50.jsonl` = 15 `multiple_choice`, 30 `semi_open`, 5 `open_ended`. Campos `id, formato, area, pregunta, opciones, legal_basis, respuesta_correcta|respuesta_esperada`.
- **`legal_basis` y las respuestas son ground truth de evaluación: nunca se usan en runtime, nunca se hardcodea por `id`.** El test real (992) no las trae.
- **Salida**: una línea JSON por ítem, validada por `schema/submission.schema.json`. Comunes: `id, formato, abstencion, pasajes_recuperados[{doc_id, texto, inicio?, fin?, score?}]`, `latencia_ms?`.
  - `multiple_choice`: `respuesta_correcta` (A–D; `null` si abstiene), `justificacion` (**de aquí se extraen las citas que puntúan**), `descarte_opciones`.
  - `semi_open`: `respuesta` (3–5 oraciones, ≤150 palabras), `palabras_clave`, `referencia_legal`.
  - `open_ended`: `marco_normativo`, `analisis` (5–8 oraciones), `jurisprudencia`, `conclusion`.
- `doc_id` de cada pasaje **debe existir en `corpus_manifest.json`**. `pasajes_recuperados` solo puede ir vacío si `abstencion=true`. `texto` debe ser literal (la verificación en vivo reconstruye la respuesta desde ahí).
- `scripts/common.py`: `read_jsonl`/`write_jsonl` (UTF-8, `\n`), `FLAWED_IDS={374}` excluido de la calificación. `load_bank`/`questions_export.json` son solo del jurado.

## Cómo puntúa realmente (`scripts/evaluate.py`, `scripts/citations.py`)

| Componente | Pts | Detalle que condiciona el diseño |
|---|---:|---|
| Exactitud cerradas | 20 | Abstenerse = 0 aquí. Referencia del baseline: 0,905 |
| Correctness texto libre (RAGAS) | 30 | Juez `z-ai/glm-5.3-flash` vía OpenRouter + encoder local `multilingual-e5-large`. Baseline 0,451. Las abstenciones no se juzgan |
| Citación | 20 | `recall_ponderado − 2 × tasa_sin_respaldo`. Cita correcta **respaldada** = 1; correcta **sin respaldo** = 0,5; cita sin respaldo penaliza el doble |
| Abstención | 10 | Acertar = 1, **abstenerse = 0,5 siempre** (acierte o no), errar = 0. ⇒ solo abstenerse si P(acierto) < ~0,5. Abstenerse en todo es no competitivo |
| Corpus 5 · interfaz 10 · video 3 · reproducibilidad 2 | 20 | Manuales. Interfaz (Streamlit) no es prioridad hasta tener el 80% automático |

- **Respaldo de una cita = aparece en los primeros 10 `pasajes_recuperados`** (`MAX_PASAJES_EVIDENCIA = 10`). Por eso el top-10 es lo crítico, y **jamás se emite una cita que no esté en esos 10 pasajes** (comparación determinista de tuplas canónicas, sin LLM). Citar de más *desde la evidencia* es gratis.
- `citations.py` normaliza a tuplas: `("ley","1563","2012","41")`, `("codigo_penal",None,None,"404")`, `("jurisprudencia","C-355","2006",None)`. Alias de códigos en `CODES` (CGP, CPACA, CST, ET, Decisión Andina 486…). **El parser de consultas y el formato de las citas de salida deben reutilizar/respetar ese diccionario** (importar `citations.extract`/`norm` en lugar de reescribirlo).
- Solo el ~84% del banco tiene `legal_basis` con citas extraíbles; el resto no puntúa en citación.

## Corpus: qué construir

`data/registros/seed_targets.json` (semilla 20260830) lista **186 documentos objetivo** con `norma`, `canonico`, `items_del_banco`, `areas` y `donde_buscar` (URL). Ojo: **111 de los 186 son sentencias** (C-, T-, SU-, SL-), no legislación. No se puede tratar la jurisprudencia como secundaria; hay que decidir pronto cuánta entra y con qué granularidad (por sentencia completa vs. por fragmento/ratio).

Mayor demanda en el banco: Constitución (90), CGP (65), CST (37), Estatuto Tributario (35), Decisión Andina 486 (23), Estatuto del Consumidor (13), Ley 80/1993 (12)… Ordenar la ingesta por `items_del_banco`, no por comodidad.

Fuentes por orden de ataque: **Secretaría del Senado** (HTML limpio, artículo por artículo) → SUIN-Juriscol → Corte Constitucional (relatoría) → Corte Suprema/Consejo de Estado → DIAN/SIC. Evitar OCR salvo necesidad. Derecho ambiental/internacional no está en el banco.

Modelo de chunk: **un artículo = una unidad** (inciso/parágrafo solo si el artículo es largo), con metadata `chunk_id, doc_id, document_type, document_number, year, article, section, validity, source_url, start_offset, end_offset`. Separar `retrieval_text` (puede llevar encabezado "Ley X de Y, art. N" para mejorar la búsqueda, estilo contextual retrieval con reglas) de `source_text` (literal; es lo que va en `pasajes_recuperados.texto`).

### Estado de las fuentes y listas de trabajo

**Corpus v2 (2026-10-01): 213 documentos** = 183 objetivos de la semilla (los 186 menos 3 erratas, estado `errata`, que apuntan a un `doc_id` ya cubierto, p. ej. `ley_116_2006` → `ley_1116_2006`) + 30 fuera de la semilla en `_adicionales`. Las 15 sentencias de la CSJ, los 6 no encontrados y las fuentes del `legal_basis` de `sample_50` se bajaron a mano (`docs/ingesta/fuentes_pendientes.md`, sección "Resultado de la incorporación"), junto con la ampliación desde `citations.py`: CPP, CPT, DUR 1072/1074/1083/1625, actos legislativos, Leyes 100/1993, 222/1995 y 1676/2013, y Decretos 19/2012 y 01/1984. Erratas nuevas resueltas con override: `ley_1692_2017` → `ley_1692_2013`, `ley_23_1961` → `ley_23_1991`, `sentencia_su_488_2011` → `sentencia_t_488_2011`, `sentencia_t_248_2025` → `sentencia_sp_248_2025`, `sentencia_su_6_1991` → `sentencia_t_6_1992`. Los documentos no normativos (doctrina, auto de Supersociedades, sentencia de unificación del Consejo de Estado) llevan tipo `documento` (`cabeceras.DOCUMENTOS`). Historia: en v1 eran 162 de la semilla más **5 documentos fuera de la semilla** (`codigo_civil`, `codigo_comercio`, `codigo_penal`, `cpaca`, `ley_472_1998`) que aparecen en el `legal_basis` de `sample_50` y que la semilla no cubría (sección `_adicionales` de `fuentes_override.json`, con `doc_id` canónicos de `scripts/citations.py`) ⇒ 167 en el corpus. Dieciocho documentos de alto impacto (Constitución, CGP, CST, ET, Estatuto del Consumidor, los 5 adicionales…) se bajaron a mano en PDF (Gestor Normativo, ICBF, SUIT, RedJurista) para controlar la calidad; el script solo los registra. Sus enlaces están en `docs/ingesta/referencias_normativas.md`.

Archivos de trabajo versionados en `data/` (léelos antes de tocar el corpus):

- **`fuentes_pendientes.md`**: checklist de fuentes. Todo lo que estaba pendiente al 2026-09-29 ya está incorporado (tabla "Resultado de la incorporación", con los `doc_id` definitivos); quedan abiertas solo las decisiones D.4/D.5 (tutelas y autos de la CSJ, circulares y resoluciones). Cada ítem lleva el procedimiento de incorporación; marcar `[x]` al terminar.
- **`areas_por_asignar.md`**: las `areas` de los 30 documentos adicionales las propuso un agente y **falta que una persona las confirme**; al decidir, actualizar `_adicionales` de `fuentes_override.json` y `corpus_manifest.json` y correr el validador.
- **`fuentes_descargadas.json`** (URL/estado/sha256), **`fuentes_override.json`**, **`mapa_archivos.json`**: ver comandos de arriba.

Decidido (2026-10-01): entran los no normativos (ponencia de la OMPI, doctrina de Arbanza y SC5288-2021 para el caso Dow Chemical), y `sentencia_su_6_1991` se resuelve con la T-006 de 1992.

Entregables del corpus: `corpus_manifest.json`, `corpus/`, `indice/` (`index.faiss` + `chunks.jsonl`), `LICENSE`, y la bitácora `CORPUS.md` (plantilla en la raíz, con tabla de evolución del puntaje).

### Licencia del corpus (decidida)

- **CC-BY-4.0**, igual que el ejemplo oficial. Cubre el trabajo de Syntax (selección, limpieza, segmentación, metadatos, encabezados de fragmentos e índice), no los textos normativos y jurisprudenciales, que son de libre reproducción (Ley 23 de 1982, art. 41).
- El archivo ya está escrito en `../LICENSE` (carpeta del proyecto, fuera del repo): encabezado en español con alcance y atribución ("Copyright (c) 2026 Syntax") + texto legal oficial de CC-BY-4.0 sin modificar. Se copia tal cual a la raíz del comprimido del corpus.
- Mantener coherentes: `"licencia": "CC-BY-4.0"` en `corpus_manifest.json`, sección 5 de `CORPUS.md` y columna "Licencia" de `README.md`.
- Implicaciones: no usar encoders con licencia no comercial para el índice publicado (p. ej. `jina-embeddings-v3` es CC-BY-NC-4.0; `bge-m3` y `multilingual-e5-large` son MIT). No incluir doctrina ni textos con derechos de autor. Si se reutiliza un dataset de terceros (p. ej. `justicedao/ipfs_colombia_laws_ir`), verificar que su licencia sea compatible y citarlo.

### Formato de `corpus_manifest.json`

Referencia: `../Hackathon 2026/entregables/sabado/corpus_manifest.ejemplo.json`. **Va versionado en el repo (raíz) y también dentro del comprimido del corpus (`enunciado.pdf`, secc. 9 y 9.3); deben ser el mismo archivo.** `corpus/` e `indice/` no se versionan.

- **Nivel raíz**: `equipo`, `licencia` (el ejemplo usa `CC-BY-4.0`; debe coincidir con `LICENSE`), `fecha_generacion`, `enlace_nube` (el mismo del README, sección "Corpus e índice") y `documentos` (lista, un registro por documento).
- **Campos obligatorios por documento** (enunciado): `doc_id`, `titulo`, `fuente`, `url`, `fecha_consulta`, `areas`.
- **Campos adicionales que trae el ejemplo** (los mantenemos): `n_articulos`, `n_fragmentos`, `metodo_ingesta`, `sha256`.
- **`doc_id`**: `snake_case` en minúsculas, sin tildes, `tipo_numero_año`: `ley_1564_2012`, `sentencia_c_355_2006`. Debe ser idéntico en `CORPUS.md`, en la metadata de cada chunk y en `pasajes_recuperados.doc_id` (el evaluador lo valida contra el manifest). Es estable: no renombrar una vez indexado.
- **`fecha_consulta` / `fecha_generacion`**: ISO `AAAA-MM-DD` (fecha real de descarga, no la de hoy al editar).
- **`areas`**: lista de strings con los nombres exactos de las 10 áreas del banco (`Derecho procesal`, `Derecho civil`, `Derecho constitucional`…, ver `CORPUS.md` sección 2). Un documento puede tener varias.
- **`n_articulos`**: entero para normas; `null` (no `0`) para sentencias u otros documentos sin articulado. **`n_fragmentos`**: entero, debe coincidir con los chunks de ese `doc_id` en `chunks.jsonl`.
- **`metodo_ingesta`**: texto corto con el método real: `"parser HTML + segmentacion por articulo"`, `"extraccion de PDF con OCR + segmentacion por parrafo"`.
- **`sha256`**: hash del **archivo procesado** (el de `corpus/`), no del original descargado; se recalcula si el archivo cambia.
- **Texto**: los valores del ejemplo van en ASCII sin tildes (`Codigo`, `Secretaria`, `indice`). Seguir esa convención en `titulo`, `fuente` y `metodo_ingesta`; solo las URLs y los nombres propios se dejan tal cual. JSON con indentación de 2 espacios, UTF-8, `\n`.
- **Placeholders del ejemplo** (`<URL>`, `2026-XX-XX`, `<hash...>`) son solo de plantilla: ninguno puede quedar en la entrega final.
- **Rutas**: nunca absolutas ni dependientes de la máquina (`/Users/...`, `C:\...`); si se registra una ruta, es relativa a la raíz del corpus.
- **Estado actual (v2, 2026-10-01)**: 213 documentos y 47.966 fragmentos; el validador da 0 errores, y el único aviso es `enlace_nube: "<URL>"`. **Lo genera `python src/ingesta/generar_manifest.py`** (`--revisar` para ver el diff) desde `data/registros/fuentes_descargadas.json` (título, fuente, URL, fecha, áreas), `data_corpus/parseo.json` (método, sha256) y `chunks.jsonl` (`n_fragmentos`). Conserva el `n_articulos` ya registrado y, en los documentos nuevos, lo toma de `resumen_indice.json`. No editarlo a mano: corregir la fuente (override, parseo) y regenerar. Orden para un documento nuevo: parsear → `generar_manifest.py` → `segmentar.py` → `generar_manifest.py` → `construir_indice.py`. Las `areas` de los 5 documentos adicionales son provisionales (ver `docs/ingesta/areas_por_asignar.md`).
- **Edición**: idealmente lo genera un script a partir de `corpus/` para no editarlo a mano; si se edita a mano, una persona a la vez (es un JSON en git y los conflictos de merge son dolorosos).

### Carpeta local del corpus y rutas

El corpus procesado y el índice se generan en `data_corpus/` dentro del repo: una carpeta **local de cada persona**, en `.gitignore`. No hay configuración por máquina ni carpeta compartida; el pipeline la reconstruye desde cero con el comando único, igual que en el contenedor limpio del jurado. `corpus_manifest.json` **no** está ahí: vive versionado en la raíz del repo y se copia al comprimido al empaquetar.

```
data_corpus/                   (en .gitignore)
├── corpus/   un archivo por doc_id: corpus/<doc_id>.<ext>
├── indice/   index.faiss + chunks.jsonl
```

Las fuentes originales **no** viven aquí sino en `data/raw/` (`html/<doc_id>/`, `pdf/`, `rtf/`; en `.gitignore`, fuera de `data_corpus/`). `src/config.py` exporta `RAW_DIR`, `RAW_HTML_DIR`, `raw_html_dir(doc_id)`, `docs_en_raw()` (doc_id con algún original ya en `data/raw/`), `MAPA_ARCHIVOS_PATH` y `PARSEO_PATH`.

- **`src/config.py` es el único lugar donde se definen rutas**: exporta `ROOT`, `MANIFEST_PATH`, `CORPUS_DIR` (= `ROOT / "data_corpus"`), `CORPUS_TEXTOS`, `INDICE_DIR`, `RAW_DIR`, `RAW_HTML_DIR`, `FUENTES_PATH`, `CHUNKS_PATH`, `FAISS_PATH`, `BM25_DIR`, `INDICE_INFO_PATH`, `RESUMEN_INDICE_PATH`, `EMB_CACHE_DIR`, `EXPERIMENTS_CSV`, los parámetros del encoder (`ENCODER_MODEL`, `ENCODER_REVISION`, `ENCODER_MAX_SEQ`), los del decoder y el pipeline (`LLM_MODELOS`/`llm_config()`, `MODELOS_DIR`, `LLM_URL`, `LLM_CTX`, `LLM_SEED`, `MODO_RECUPERACION`, `RETRIEVAL_K`, `GENERATION_K`, `CITAR_EVIDENCIA`, `SALIDAS_DIR`, `TRAZAS_DIR`, `SCHEMA_PATH`, `SAMPLE_PATH`, `TEST_PATH`, `SUBMISSION_PATH`), `DEVICE` (variable de entorno `SYNTAX_DEVICE`: `cuda|mps|cpu|auto`) con `resolver_device()`, más `verificar_indice()` (comprueba que `chunks.jsonl` e `index.faiss` existan y tengan el mismo número de fragmentos; llamarla al arrancar cualquier proceso que use el índice). Los scripts hacen `sys.path.insert(0, str(ROOT / "src")); import config` (como `src/validaciones/*.py`). Nunca escribir rutas a mano ni usar `os.getcwd()`.
- **Un archivo por `doc_id` en `corpus/`**: cada uno ingiere documentos distintos sin pisarse. El `sha256` del manifest es el de ese archivo.
- **Validar antes de subir cambios y antes de entregar**: `python src/validaciones/manifest.py` (formato, `sha256` contra `corpus/`, `n_fragmentos` contra `chunks.jsonl`, `doc_id` de los chunks ⊆ manifest). Con `--strict` (entrega final) los placeholders y archivos ausentes son error.
- **Empaquetado final**: `python src/reproducibilidad/package_corpus.py [--licencia <ruta>]` (verifica con `verificar_corpus.py` y arma `data_corpus/Syntax-corpus-v4.zip`, determinista: ~900 MB, mismo sha256 en cada corrida): `corpus/` + `indice/` (con `bm25/`) + `LICENSE` + copia de `corpus_manifest.json` → subir a OneDrive con enlace público (el enunciado exige lectura pública para cualquiera con el vínculo e índice congelado); anotar el hash del comprimido en `CORPUS.md`.

## Arquitectura

**v0 (primer objetivo, antes de cualquier otra cosa):**
`corpus → BM25 → top-10 → Qwen → validación de schema → evaluate.py`

**Target condicional** (cada pieza entra solo si el análisis de error la justifica):

```
pregunta → parser de referencias legales (determinista) ─ ¿norma+artículo explícitos? → lookup por metadata
        └→ BM25 + BGE-M3 → RRF → 20–40 candidatos → [reranker] → top-10
                → ¿evidencia suficiente? no → abstención
                                          sí → Qwen3-8B → validar citas (⊆ top-10) → validar schema → jsonl
```

Elecciones actuales (revisar con datos, no dogma):
- Encoder `BAAI/bge-m3` (normalizar embeddings, FAISS `IndexFlatIP`); BM25 con `bm25s` (mirar tildes, `art.`/`artículo`, `Ley 1564/2012` vs `de 2012`, siglas; probar si el stemming daña).
- Fusión RRF antes que suma de scores. Hybrid se prueba temprano: en derecho, números de artículo y siglas hacen que BM25 y denso sean complementarios.
- Reranker: `Qwen3-Reranker-0.6B` (candidato; `bge-reranker-v2-m3` como alternativa). Solo si el artículo correcto está en rango 11–40 con frecuencia. Medir latencia y mantener solo si mejora.
- Decoder `Qwen3-8B` (plan B `Qwen3-4B` si la velocidad no alcanza). Un solo decoder hasta que el análisis muestre "retrieval correcto + generación incorrecta".
- `generation_k` (3/5/7/10) es un hiperparámetro a barrer; `retrieved_top_k=10` se mantiene fijo para el juez.
- Prompts separados por formato: `generate_closed / generate_semi_open / generate_open`. Política: no inventar normas, artículos ni sentencias; citar solo lo respaldado por los pasajes.
- Citas inválidas tras generar: regenerar 1 vez → eliminar la cita si no rompe validez → abstenerse.
- Abstención: registrar primero score, rank, margen, acuerdo BM25/denso y coincidencia de referencia exacta; elegir una regla simple sobre esas señales (no ajustar umbrales finos a 50 muestras).

**No construir** (salvo que el análisis de error lo demuestre): agentic RAG, GraphRAG, HyDE, multi-query, query decomposition, fine-tuning, queries sintéticas, vector DB externa, LangChain/LlamaIndex, UI avanzada.

## Método de trabajo (obligatorio para todo el equipo y todos los agentes)

`OBSERVAR → MEDIR → DIAGNOSTICAR → HIPÓTESIS → CAMBIAR UNA COSA → BENCHMARK → KEEP/REVERT`

Antes de añadir una técnica: qué error observado corrige, qué métrica debe mejorar, si hay alternativa más simple, coste en latencia/memoria, si es reversible y si generaliza a 992 (no solo a las 50). Una mejora de 1/50 no es significativa; a igualdad, gana lo más simple, rápido y reproducible.

- **Medir retrieval antes de generar**: `retrieval_eval.py` con Document/Article Hit@1/3/5/10, MRR y latencia, guardado por pregunta (usando `legal_basis` solo aquí, como evaluación).
- **Análisis de error por pregunta** con diagnóstico ∈ {CORPUS, INGESTION, DOCUMENT_RETRIEVAL, ARTICLE_RETRIEVAL, RANKING, GENERATION, CITATION, SCHEMA, UNKNOWN}. El diagnóstico decide el siguiente experimento.
- **`evaluation/experiments.csv`**: una fila por experimento (commit, versión de corpus, retriever/encoder/fusión/reranker, retrieval_k/generation_k, decoder/cuantización/prompt_version, hit@k, MRR, puntajes oficiales, latencias, notas). Compartido y versionado: la memoria humana no cuenta.
- Desempate determinista en rankings; prompt y modelo versionados.

## Equipo, plataformas y cómputo

- **Windows + Mac**: escribir código portable. `pathlib`, sin rutas con `\`, abrir/escribir archivos con `encoding="utf-8"` y `newline="\n"`, sin dependencias de bash en `src/` (el `run.sh` es un envoltorio fino de `python src/main.py`). Fijar versiones en `requirements.txt` (Python 3.13, declarado en la línea `# python: 3.13` de `requirements.txt`; `verificar_deps.py` y `preparar_entorno.py` fallan con otra versión. Para cambiarla, editar esa línea y recrear el entorno).
- **Un solo contrato de dispositivo**: `device = cuda | mps | cpu` por configuración, no por `if platform`. Mac: llama.cpp con Metal (`-DGGML_METAL=ON`, GGUF Q4_K_M). Campus/CUDA: mismo modelo servido por llama.cpp o vLLM. Exponer el decoder siempre tras una interfaz `generate(prompt) -> str` (idealmente endpoint OpenAI-compatible) para que el resto del código no cambie.
- **Las máquinas del campus sirven para lo pesado y paralelizable**: embeddings del corpus completo, construcción de índices, sweeps de retrieval y las corridas largas de las 992. Los Mac sirven para iterar.
- **Cuidado de reproducibilidad entre plataformas**: un GGUF Q4 en Mac y otra cuantización en CUDA no dan la misma salida. Los números de `experiments.csv` deben anotar plataforma y cuantización; **la corrida final de las 992 y la verificación en vivo usan una sola configuración congelada**.
- Índices y modelos pesados **no van al repo** (enlace público en la nube, verificable en ventana privada antes de las 15:00). Rutas y hashes de artefactos se registran en `corpus_manifest.json`.
- Sofía es la desarrolladora principal con tiempo fragmentado: tareas pequeñas, cada una terminable en una sesión, con interfaces claras (`retrieve(query, k) -> list[RetrievedChunk]`).

## Convenciones de repo

- Una **rama personal por integrante** (`santiago`, `sofi`), no una rama por tarea; traer `main` antes de trabajar (`git merge origin/main`) y merge a `main` por PR/cuando se pida. No hacer push directo a `main` ni force-push. Los worktrees de agentes viven en `.claude/worktrees/` y deben tener checked out la rama personal.
- Mensajes de commit en español, sin tildes, con un resumen de una línea y el detalle de decisiones en viñetas (así se ha hecho hasta ahora).
- No versionar `scripts/.env`, modelos, índices ni `__pycache__` (ver `.gitignore`).
- Completar `README.md` (arquitectura, reproducción, resultados, limitaciones) y `CORPUS.md` a medida que avanza el trabajo, no al final; hay que quitar las notas en cursiva de las plantillas.

## Sincronizar AGENTS.md

Después de editar este archivo:

```bash
python -c "import shutil; shutil.copyfile('CLAUDE.md', 'AGENTS.md')"
```

(funciona igual en Windows y Mac; no usar symlinks porque en Windows fallan sin permisos).
