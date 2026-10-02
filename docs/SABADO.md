# Sábado 2026-10-03: revisar las preguntas, ajustar fuentes y responder

La organización confirmó (2026-10-02) que, después de recibir las 992 a las 09:00, **podemos revisar las preguntas y ajustar el corpus antes de responder**. Este documento es el guion del día: qué cambia, qué corre cada máquina, comandos exactos y reglas de decisión. Los tiempos medidos están en la sección 6.

## 1. Qué cambia respecto del plan anterior

- **La ampliación se dirige por la demanda, ya no a ciegas.** `citations.extract` sobre `pregunta + opciones` (campos de runtime) dice qué normas y sentencias nombran las preguntas y cuáles faltan en el índice.
  - Con el filtro "solo por cita" y el lookup, un documento nombrado e ingerido llega al top-10 casi siempre (15/15 SU sintéticas, `docs/INDEXACION.md` 13).
  - Sin nombrarlo, no mete ruido.
  - Es la ganancia más barata y segura.
- **El corpus de respaldo es la v4 congelada del viernes**:
  - tag `avance-viernes`;
  - 1.186 documentos y 173.393 fragmentos;
  - zip en `C:\Users\s.munozm234\congelados\avance-viernes\`;
  - `entregas/viernes/CONGELADO.md`.
  - Medido en `sample_50`: 40,59/50 sin juez, 4,2 s por pregunta.
- **El corte del corpus se mueve al sábado a las 10:45.** Lo que se agregue después no entra.
- **Sin ground truth** se decide con dos medidas:
  - **respaldo nombrado@10**: fracción de los cuerpos nombrados en la pregunta que el top-10 respalda, con el mismo criterio del evaluador;
  - **no regresión en `sample_50`**.
  - Las dos son deterministas y gratis. Sin juez RAGAS el sábado.
- **Generación incremental.**
  - El decoder guarda cada respuesta por hash de la petición (`SYNTAX_LLM_CACHE=on`, `salidas/cache_llm/`).
  - Al volver a correr las 992 con el índice final, solo se regeneran las preguntas cuyo prompt cambió (el top-5 que ve el decoder). El resto sale del caché en milisegundos.
  - La entrega sigue siendo exactamente lo que el pipeline produce con el índice publicado.
- **Hasta 3 RTX 4090.** Se reparte por `--particion I/N`; todas usan la misma configuración.
- **Integridad (no cambia).**
  - Solo se leen `id, formato, area, pregunta, opciones` (más `tema`, `sub_tarea` y `complejidad` para conteos).
  - Nada se hardcodea por `id`.
  - Solo entran fuentes públicas normativas o jurisprudenciales, nunca material con respuestas.
  - En `CORPUS.md` se anota que la ampliación del sábado fue dirigida por las preguntas, con la autorización.

## 2. Roles

| Quién | Máquina | Rol |
|---|---|---|
| Santiago | M1 (RTX 4090 de referencia) | corpus: análisis, ingesta, índice, empaquetado, entrega |
| Joel | M2 (RTX 4090) | generación: respaldo y parte 2/3 de la final |
| Sofía | M3 (RTX 4090) | generación: parte 3/3 de la final; README/CORPUS.md |
| Los tres (09:15–10:00) | sus portátiles | triage por área y cola manual |

Reparto del triage (3–4 áreas cada uno, por demanda):

| Persona | Áreas |
|---|---|
| Santiago | constitucional, administrativo, procesal |
| Joel | laboral, penal, tributario |
| Sofía | civil, familia, comercial, mercados |

## 3. Preparación (viernes en la noche)

1. M2 y M3:
   - clonar el repo en la rama `santiago` (después del merge de `santiago-sabado`);
   - descomprimir el zip v4 en `data_corpus/` (corpus/ e indice/), como en `CONGELADO.md`;
   - `python src/reproducibilidad/reproducir.py --hasta decoder` (entorno, verificación de hashes, llama.cpp b11146 y el GGUF verificado).
2. **Determinismo entre máquinas.** En M1, M2 y M3:

   ```
   SYNTAX_LLM_CACHE=off python src/main.py --split sample --experimento det_m<N> --sin-reanudar
   ```

   y comparar con `comparar_entregas.py salidas/sample_det_m1.jsonl salidas/sample_det_m2.jsonl`. **Deben dar 0 diferencias.** Si no:
   - no se reparte la generación: una sola máquina hace las 992 (~70 min a 4,2 s por pregunta);
   - no se copia `cache_llm/` entre máquinas.
3. Confirmar quién tiene el `LICENSE` del corpus (`../LICENSE`, CLAUDE.md) y la carpeta de OneDrive con enlace público.
4. Pedir por correo la confirmación de que se puede ajustar el corpus después de ver las preguntas, para citarla en `CORPUS.md`.

## 4. Cronograma del sábado

Los comandos son de PowerShell en Windows. En bash, `$env:SYNTAX_DEVICE="cuda"` se escribe `SYNTAX_DEVICE=cuda`.

### 09:00 Llegan las preguntas (M1)

```
copy <archivo recibido> data\test_992.jsonl
git add data/test_992.jsonl; git commit -m "Preguntas del test (992)"
```

Mirar qué campos traen (`sub_tarea`, `tema`). Si traen `sub_tarea`, **no se cambian los prompts hoy**: solo se anota.

### 09:05 Análisis (M1, ~5 min) y respaldo (M2 + M3, ~40 min)

M1:

```
$env:SYNTAX_DEVICE="cuda"
python src/evaluacion/analizar_test.py --experimento test_v4 --maquinas 2
```

Deja en `evaluation/test/test_v4/`:
- `nombradas_faltantes.csv`;
- `nombradas_sin_respaldo.csv`;
- `confianza.csv`;
- `triage/<area>.md`;
- `resumen.json`, con el respaldo nombrado@10 de la v4, que es la línea base del día.

Subir `evaluation/test/test_v4/` a la rama para que el equipo vea las hojas de triage.

M2 y M3, **entrega de respaldo con la v4** (el caché se llena aquí y luego se copia a M1):

```
python src/main.py --split test --experimento respaldo_v4 --particion 1/2     # M2
python src/main.py --split test --experimento respaldo_v4 --particion 2/2     # M3
```

### 09:15 Ingesta automática (M1)

```
python src/ingesta/ampliar_desde_citas.py evaluation/test/test_v4/nombradas_faltantes.csv --plan
python src/ingesta/ampliar_desde_citas.py evaluation/test/test_v4/nombradas_faltantes.csv
```

- Baja por regla lo que nombran las preguntas:
  - leyes y decretos del Senado y de los espejos de Avance Jurídico;
  - C, T y SU de la relatoría.
- Parsea y valida: artículos detectados, sentencia completa.
- Registra en `_adicionales`, con las áreas de las preguntas que lo citan; las sentencias van a `solo_por_cita.json`.
- Deja `no_resueltos_<hora>.csv`: es la cola manual.

### 09:15–10:00 Triage y cola manual (personas)

- **Triage.**
  - Cada persona abre `evaluation/test/test_v4/triage/<area>.md` de sus áreas: las 20 preguntas de menor confianza, con el top-3 recuperado.
  - Anota en `lista_<persona>.txt` las normas o sentencias que faltan: temas, nunca respuestas. Una por línea, con el área tras `;`:

    ```
    Ley 1258 de 2008 ; Derecho comercial
    Sentencia T-123 de 2024 ; Derecho constitucional
    ```

  - M1 las ingiere así:

    ```
    python src/ingesta/ampliar_desde_citas.py lista_<persona>.txt --plan
    python src/ingesta/ampliar_desde_citas.py lista_<persona>.txt
    ```

- **Cola manual** (`no_resueltos_*.csv`):
  - **solo lo que nombran ≥ 2 preguntas**, máximo **45 min por persona**;
  - típicamente sentencias de la Corte Suprema (SL, SC, SP, STC), del Consejo de Estado y resoluciones;
  - el PDF va a `data/raw/pdf/` y la fila a `manual.csv` (`doc_id,titulo,fuente,url,areas,archivo`);
  - `doc_id` por convención: `sentencia_sl_1234_2019`;
  - en M1: `python src/ingesta/ampliar_desde_citas.py --manual manual.csv`.
- Todo documento nuevo debe ser una norma o sentencia pública. Una Decisión Andina nueva necesita además su entrada en `cabeceras.DOCUMENTOS`; si no, `generar_manifest` falla.

### 09:50 Entrega de respaldo lista (M2 → M1)

Copiar `salidas/test_respaldo_v4_p*.jsonl` y `salidas/cache_llm/qwen3-8b-q8.jsonl` de M2 y M3 a M1. Concatenar los dos cachés: son JSONL por clave y se pueden unir sin problema.

```
python src/evaluacion/unir_entregas.py salidas/test_respaldo_v4_p1de2.jsonl salidas/test_respaldo_v4_p2de2.jsonl --salida entregas/respaldo_v4.jsonl
```

**Desde aquí siempre hay una entrega válida**, con la v4 y el zip congelado como corpus.

### 10:00–10:45 Reindexar y medir (M1)

```
python src/ingesta/ampliar_desde_citas.py --indexar --batch 64
python src/evaluacion/analizar_test.py --experimento test_v5 --maquinas 3
python src/evaluacion/retrieval_eval.py --modo hibrido --experimento e30_v5_sample --no-csv
```

**KEEP de la ampliación** si se cumplen las dos condiciones:
1. el respaldo nombrado@10 de `test_v5` sube frente a `test_v4`;
2. en `sample_50` doc_hit@10 no pierde más de 1 pregunta frente a `e20` (0,902).

Si no se cumplen: identificar el lote culpable (IDF de BM25 o desplazamiento por área, ver INDEXACION 13), sacarlo de `_adicionales` y volver a indexar. Si no se resuelve a las 10:45, **REVERT**: se entrega la v4.

### 10:45 Congelar el corpus del sábado (M1)

```
python src/reproducibilidad/verificar_corpus.py --actualizar
python src/validaciones/manifest.py
git add corpus_manifest.json data/registros docs/ingesta evaluation/test
git commit -m "Corpus v5: ampliacion dirigida por las preguntas del test"
git push
```

- Copiar `data_corpus/corpus/` y `data_corpus/indice/` a M2 y M3, por red o USB. No se recodifica en cada máquina: el índice tiene que ser bit a bit el mismo.
- En M2 y M3: `git pull`, `python src/reproducibilidad/verificar_corpus.py` en `ok` y reiniciar los procesos que usen el índice.

### 11:00 Corrida final (M1, M2, M3)

Con el caché unido copiado en las tres máquinas, y el mismo experimento en las tres:

```
python src/main.py --split test --experimento final_v5 --particion 1/3     # M1
python src/main.py --split test --experimento final_v5 --particion 2/3     # M2
python src/main.py --split test --experimento final_v5 --particion 3/3     # M3
```

`main.py` marca `(cache)` en las preguntas que no cambiaron. Una caída se reanuda volviendo a lanzar el mismo comando.

### ~11:45 Unir y verificar (M1)

```
python src/evaluacion/unir_entregas.py salidas/test_final_v5_p1de3.jsonl salidas/test_final_v5_p2de3.jsonl salidas/test_final_v5_p3de3.jsonl
python src/reproducibilidad/validar_entrega.py submissions.jsonl --preguntas data/test_992.jsonl
```

Verificación en vivo de prueba: tomar 5 ids al azar y correrlos en **otra** máquina, **sin caché**.

```
$env:SYNTAX_LLM_CACHE="off"; python src/main.py --split test --experimento verif --ids <5 ids>
python src/evaluacion/comparar_entregas.py submissions.jsonl salidas/test_verif.jsonl --ids <5 ids>
```

Debe dar 0 diferencias.

### 12:30 Publicar (M1)

```
python src/reproducibilidad/package_corpus.py --licencia <ruta LICENSE> --nombre Syntax-corpus
```

1. Subir el zip a OneDrive con enlace público y comprobarlo en una ventana privada.
2. Poner el enlace en `enlace_nube` (manifest y README) y correr `python src/validaciones/manifest.py --strict`.
3. Registrar el entorno de la corrida final: `python src/reproducibilidad/registrar_entorno.py --salida evaluation/entornos/final_v5.json`.
4. En `CORPUS.md`: bitácora de la ampliación del sábado, hash del zip y tabla de evolución.
5. PR de `santiago` a `main`.

### 14:30 Entrega (margen de 30 min)

## 5. Reglas de decisión

- **Go/no-go a las 11:15.** Si el corpus del sábado no está congelado y medido, se entrega el respaldo v4 (`entregas/respaldo_v4.jsonl` + zip congelado) y se documenta.
- **KEEP/REVERT de cada lote:** respaldo nombrado@10 sube y `sample_50` no pierde más de 1 pregunta (sección 4, 10:00).
- **Cola manual:** solo lo que nombran ≥ 2 preguntas, 45 min por persona como máximo. Lo que no entra se anota como limitación.
- **Sin juez RAGAS el sábado.**
- **Una sola configuración congelada** para las 992 y la verificación en vivo:
  - defaults de `config.py`, sin variables `SYNTAX_*` salvo `SYNTAX_DEVICE` y `SYNTAX_LLM_CACHE`;
  - el mismo GGUF Q8_0 y llama.cpp b11146 en las tres máquinas.

## 6. Tiempos medidos

Ver la sección "Simulacro" más abajo (se completa el viernes en la noche).
