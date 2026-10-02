# Resultados del plan 05: reranker

Fecha: 2026-10-01. Rama comprobada antes de editar: `sofi-local`; arbol inicialmente limpio.

Estado: implementacion de la medicion previa completada y probada; medicion real bloqueada. Las fases 1 y 2 siguen pendientes. **No hay decision go/no-go ni keep/revert de calidad.** No se implemento ni activo un reranker sin superar la fase 0 y definir el presupuesto de latencia. La abstencion permanece `off` por defecto. Se conservaron los cambios de los planes 03 y 04; el plan 06 no se implemento.

## Cambios

- `src/evaluacion/retrieval_eval.py`: opcion explicita `--techo-reranker`, solo con `--modo hibrido`. Recupera los primeros 40 del RRF existente (40 candidatos por rama), sin modelo nuevo. El comportamiento habitual sigue usando top-10. MRR se mantiene limitado a top-10 para comparar con el baseline; MRR@40 se informa aparte. Respaldo sigue limitado a los diez primeros textos. Detecta artefactos ausentes antes de escribir resultados o registrar el entorno; nunca reconstruye el indice.
- `src/evaluacion/techo_reranker.py`: art_hit@20/@40, doc_hit@40, MRR@40, distribucion 1-5/6-10/11-20/21-40/fuera, IDs por intervalo y techo en preguntas/pp. Reutiliza los rangos calculados con `citations.extract`, sin llevar ground truth a runtime.
- La corrida real guardara detalle top-40 en `evaluation/retrieval/<exp>_hibrido.jsonl`, resumen en su `.meta.json`, entorno y fila en `experiments.csv`. Las metricas nuevas van en `notas`, conservando las 35 columnas existentes. No se escribio ninguna fila ficticia.
- `tests/test_techo_reranker.py`: pruebas sinteticas de fronteras, denominadores, ausencia de articulos, entrada vacia, criterio de continuacion e integracion del evaluador; un match en rango 11 no altera MRR ni hits/respaldo top-10.
- `docs/INDEXACION.md`: referencia al estado condicionado del plan.

No se cambiaron prompts, generation_k, config de abstencion, retriever de runtime, requirements ni corpus/indice. La carga del retriever en el evaluador es diferida para que la ayuda y comprobacion de artefactos funcionen antes de cargar dependencias de recuperacion.

## Criterios y denominadores

El plan completo establece continuar con **>=4 preguntas o >=8 pp**; el helper respeta ese OR y usa el numero real de preguntas con articulo. Con 19, dos preguntas ya son 10,53 pp. El resumen dice cerrar si <4: hay una discrepancia entre ambos documentos. Se usa el criterio del plan completo y se exponen conteos y pp para que la decision sea revisable. Sin preguntas con articulo no se autoriza continuar. Un techo favorable solo habilita experimentar, no activar por defecto.

Para keep: art_hit@10 mejora >=3 preguntas o >=8 pp, MRR no baja, doc_hit@10 no baja y latencia adicional dentro del presupuesto medido en la maquina final. Si mejora solo @1, hay regresion documental, se excede el presupuesto o empata, gana el baseline sin reranker. Faltan todas estas mediciones; no se afirma ninguna mejora.

## Pruebas ejecutadas

| Comando | Resultado |
|---|---|
| `py -3.13 -m unittest discover -s tests -p test_techo_reranker.py -v` | 5 pruebas pasaron; datos sinteticos |
| `py -3.13 -m pytest tests/test_abstencion.py -q` | 25 pruebas del plan 04 pasaron |
| `py -3.13 src/evaluacion/retrieval_eval.py --help` | Correcto; expone --techo-reranker |
| `py -3.13 src/evaluacion/retrieval_eval.py --modo hibrido --techo-reranker --experimento e05_techo --no-csv` | Bloqueado con error explicito de indice ausente; sin resultados de calidad |
| `py -3.13 src/reproducibilidad/verificar_deps.py` | ok: 9 paquetes usados, declarados y fijados; avisos lxml/pytest sin import directo |
| `git diff --check` | Sin errores de whitespace |

El comando `python` apunta a 3.9.12; `py -3.13` usa el Python 3.13 instalado. No existe `.venv` en este worktree. En 3.13 faltan `sentence_transformers` y `torch`; pytest y numpy estan disponibles. No se instalaron paquetes ni descargaron modelos. Los permisos iniciales dejaron de permitir acceder al worktree; lecturas, escrituras y pruebas posteriores requirieron ejecucion escalada.

## Bloqueos y comandos reproducibles

Ausentes: `data_corpus/indice/chunks.jsonl`, `index.faiss` y `bm25/`. Las trazas existentes del baseline solo tienen top-10 y no permiten reconstruir el rango 11-40. Hay que usar una maquina que ya tenga el indice congelado y bge-m3 cacheado, con dependencias fijadas. No se reconstruyo ni se descargo el indice. Tampoco se comprobo disponibilidad del decoder o credenciales RAGAS; no son necesarias para fase 0 y quedan por comprobar para el A/B final.

En esa maquina (Windows; en Mac usar el Python 3.13 del entorno en lugar de `py -3.13`):

```powershell
$env:SYNTAX_ABSTENCION = "off"
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
py -3.13 src/reproducibilidad/verificar_corpus.py
py -3.13 src/evaluacion/retrieval_eval.py --modo hibrido --experimento e05_sin_rerank
py -3.13 src/evaluacion/retrieval_eval.py --modo hibrido --techo-reranker --experimento e05_techo
```

Los flags offline evitan descargas implicitas del encoder; si falta su cache, la corrida debe fallar. Estos comandos aun no produjeron metricas reales. Revisar conteos, IDs y tipo documental, no solo promedios. Si el techo no cumple, cerrar el plan con esa tabla, sin construir el reranker.

Solo si cumple y hay presupuesto de latencia: verificar licencia y fijar revision real del modelo (Qwen3-Reranker-0.6B primero; BAAI/bge-reranker-v2-m3 como alternativa), implementar backend/interfaz y bandera off, probar texto/retrieval_text y variantes 40/20/fusion de rangos por separado. Las variables `SYNTAX_RERANKER` y `RERANK_N` **todavia no estan implementadas**; los comandos de activacion del plan no deben interpretarse como funcionales en este estado. Falta parametrizar los metadatos reales de retrieval/generacion y la fila de evaluar_entrega cuando exista ese backend.

Despues del A/B de recuperacion: comprobar pertenencia estricta a candidatos, texto/offsets intactos, desempate por chunk_id y dos rankings identicos; medir latencia/memoria en maquina final con batch/dtype/revision fijos. Solo entonces elegir variante y correr generacion completa en dos experimentos distintos, evaluar con `evaluar_entrega.py --ragas` y comparar con `comparar_entregas.py`. Sin decoder, encoder del juez o API key, documentar lo que falte y no declarar RAGAS medido.

## Planes 03 y 04

Mientras el reranker no se adopte, el top-10 runtime no cambia y esta implementacion offline no exige repetir ni recalibrar. Si una variante supera keep/revert y se adopta, repetir el barrido generation_k={3,5,7,10} del plan 03 con retrieval_k=10 fijo: cambia el orden del top-5 que ve el decoder. Recalibrar el plan 04 con nuevas trazas por formato, scores/ranks y sensibilidad +/-20%; mantener abstencion off hasta cumplir su keep >=0,3 puntos netos sin bajar exactitud. Tambien repetir ambos si posteriormente se adopta el plan 06, que no se implemento aqui.

No se hizo commit, push, merge ni cambios en main.
