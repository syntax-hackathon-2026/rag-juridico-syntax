# Guion del video — Syntax (Hackathon 2026)

Máximo 5 minutos (entregable 7, 3 puntos manuales). Duración objetivo: ≈ 4:30.
Se sube a la nube (OneDrive/Drive, acceso público) y se enlaza desde el `README`. No se versiona en el repositorio.

> Las cifras salen de la corrida `e24_final` (`README.md`, `CLAUDE.md`). Si el sábado cambia el corpus y se regeneran las respuestas, actualizarlas antes de grabar.

## Guion

| Tiempo | Pantalla | Quién | Texto |
|---|---|---|---|
| **0:00–0:20** Gancho | Título "Syntax · Uniandes". Luego la interfaz abierta (estética Software Colombia, turquesa/naranja) | Sofía | "Las preguntas de derecho colombiano exigen citar la norma exacta, y un modelo pequeño inventa artículos con facilidad. Syntax es un RAG con un modelo abierto de 8B parámetros, un corpus jurídico que construimos nosotros y citas verificadas." |
| **0:20–1:10** Corpus | `CORPUS.md` y una tabla con 1.186 documentos y 173.393 fragmentos | Joel | "Construimos el corpus desde la semilla del banco. Lo ampliamos con códigos, Decisiones Andinas, sentencias C- y SU de la Corte Constitucional y sentencias de la Corte Suprema. La ingesta es automática y rastreable: `corpus_manifest.json` guarda la URL, la fecha y el sha256 de cada fuente. Se publica bajo CC-BY-4.0." |
| **1:10–2:10** Arquitectura | Diagrama del README (pregunta → BM25 + bge-m3 → RRF → prioridad por área → top-10 → Qwen3-8B → validación de citas) | Santiago | "Un artículo es un fragmento, con cabecera citable. La recuperación es híbrida: BM25 sirve para números de artículo y siglas, y bge-m3 para paráfrasis. Se fusionan con RRF y las normas nombradas se buscan por metadatos. Qwen3-8B Q8_0 corre local con llama.cpp, temperatura 0 y JSON por gramática. Cada norma citada se comprueba contra los 10 pasajes recuperados: si no está respaldada, se regenera, se elimina o el sistema se abstiene." |
| **2:10–3:40** Demo en vivo | Interfaz, modo "Consultar" | Santiago maneja, Sofía narra | Tres casos (abajo). Mostrar respuesta, citas validadas y los 10 pasajes. |
| **3:40–4:20** Resultados y límites | Tabla de la corrida `e24_final` | Joel | "En las preguntas de muestra: cerradas 12/15, citación 17,55/20 con cero citas sin respaldo, 55,35/80 automático con el juez RAGAS, y unos 4,4 s por pregunta en una RTX 4090. Probamos y descartamos thinking, un planificador agéntico y una consulta por opción; todo está medido en `experiments.csv`. Limitaciones: el 8B no recuerda números de artículo, las cerradas que fallan son de doctrina que el corpus no cubre, y el juez de texto libre varía ±0,03 entre corridas." |
| **4:20–4:40** Cierre | `README`, sección "Corpus e índice", comando único de reproducción | Todos | "La entrega se reproduce con un solo comando (`reproducir.ps1` o `reproducir.py`) y el corpus y el índice están en un enlace público. Somos Syntax: Sofía Morato, Joel Niño y Santiago Muñoz." |

## Los tres casos de la demo (2:10–3:40)

Usar preguntas de `data/sample_50.jsonl`, no del test. Ensayarlas antes con el decoder ya levantado.

1. **Cerrada que acierta** (≈30 s): se ve la opción elegida, la justificación con la cita y que los pasajes recuperados contienen el artículo.
2. **Pregunta abierta o de caso** (≈40 s): se ven marco normativo, análisis, jurisprudencia y conclusión, con la cita respaldada por el top-10.
3. **Abstención** (≈20 s): una pregunta sin evidencia suficiente. Muestra por qué el sistema se abstiene en vez de inventar.

## Cómo grabarlo

- **Antes:** levantar `llama-server` (`python src/generacion/modelo.py servir`) y la interfaz (`bash interfaz.sh`). En la RTX 4090 la respuesta tarda ~4 s; en un Mac M1 de 16 GB, ~145 s. Si se graba en Mac, usar respuestas precargadas o el modo "Explorar entrega", que no necesita índice ni decoder.
- **Grabación:** pantalla completa a 1080p (OBS o grabadora de Windows) con voz sobre la pantalla. Mejor grabar cada bloque por separado y unirlos.
- **Comprobaciones:** dura menos de 5:00; no se ve `OPENROUTER_API_KEY` ni `scripts/.env`; no se muestran `legal_basis` ni respuestas oficiales.
- **Entrega:** subir a OneDrive/Drive con acceso público, enlazar en el `README` y abrir el enlace desde una sesión privada del navegador antes de las 15:00.

## Pendientes

- Grabar con el estado final: después de congelar el índice del sábado.
- Revisar en el enunciado en PDF si el video debe cubrir algo más (los materiales consultados no lo especifican).
- El informe técnico valora identificar las limitaciones por encima de presentar el sistema como infalible; mantener ese tono en el bloque 3:40–4:20.
