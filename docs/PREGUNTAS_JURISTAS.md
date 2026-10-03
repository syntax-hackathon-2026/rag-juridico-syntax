# Preguntas para los juristas autores del banco

Preparadas el 2026-10-02 a partir del enunciado, los entregables y `data/sample_50.jsonl`.
Son preguntas sobre **criterios**, no sobre el contenido del conjunto ciego (ver "Integridad").

## Lo que el enunciado ya responde (no gastar tiempo)

- **El temario es público**: áreas, pesos y catálogo de sub-tareas de las semiabiertas (§4.2).
- **Citas**: una cita pertinente pero distinta de la referencia, y respaldada, no se penaliza (§6.1).
- **Abstención**: se declara cuando el corpus no da fundamento suficiente (§5, paso 4).
- **Verificación en vivo**: el jurado elige 2 o 3 preguntas ya entregadas y las regenera (§7). No hay preguntas nuevas.
- **Volumen del test**: 289 cerradas y 250 de texto libre estratificadas, con un solo juez (`z-ai/glm-5.3-flash`).

## Integridad

No preguntar qué normas pesan más en las 992 ni qué preguntas saldrán en la verificación en vivo: es pedir contenido del conjunto ciego. El enunciado dice que la lista de fuentes es deliberadamente no exhaustiva y que cerrar esa brecha es el trabajo de la semana. Indexar material con respuestas descalifica (§3.2 y §8): **nada de lo que nos digan en la charla debe entrar al índice.**

## Hallazgo en la muestra

Los ítems de `sample_50.jsonl` traen `tema`, `complejidad` y `sub_tarea` (las 30 semiabiertas; cerradas y abiertas vienen con `null`). `CLAUDE.md` (sección "Contrato de datos") no lo menciona. Si el test también los trae, se podrían enrutar prompts por sub-tarea.

Sub-tareas en la muestra (30 semiabiertas): Problema jurídico 6, Definición básica 6, Requisitos legales 4, Precedente jurisprudencial 3, Fundamento jurídico central 2, Existencia normativa 2, Reproducción literal 2, y 1 cada una de Antecedentes fácticos, Conflicto normativo, Elemento esencial, Jerarquía legal y Distinción conceptual.

## Preguntas

### A. Estructura del test (lo que más cambia el diseño)

1. **¿Las 992 traen `tema`, `complejidad` y `sub_tarea` como la muestra?** Si no los traen, ¿las semiabiertas siguen plantillas de redacción reconocibles por sub-tarea?
2. **¿Cuál es la estratificación de los 250 ítems de texto libre?** Por área, por complejidad, por formato o por otro criterio.
3. **"Existencia normativa" y "Jerarquía legal" (#79, #563):** la respuesta puede ser "sí existe, la Ley 1010" o "no existe". ¿Hay casos de normas inexistentes o de premisas falsas donde la respuesta correcta sea negarlas?

### B. Respuestas de texto libre (30 pts)

4. **"Reproducción literal" (#442, #865):** ¿la respuesta esperada es el texto exacto del artículo vigente? ¿Es correcto citar el artículo completo con su numeración y sus incisos?
5. **Sub-tareas de jurisprudencia** (precedente, problema jurídico, ratio decidendi, antecedentes fácticos, sentido del fallo): ¿esperan el contenido de una sentencia concreta o el criterio general de la Corte? #453 pide "el principal precedente" y su `legal_basis` lista tres sentencias.
6. **"Conflicto normativo":** ¿qué criterio esperan que se aplique (jerarquía, especialidad, temporalidad)? ¿Se espera citar las reglas de la Ley 153 de 1887 o basta el razonamiento?
7. **Abiertas casuísticas:** ¿qué pesa más al calificar el análisis: el problema jurídico, la norma aplicable o la conclusión? ¿Un error en la conclusión con buen marco normativo es aceptable?
8. **Referencias que no son norma** (doctrina en #857, documento de la OMPI en #513, auto de Supersociedades en #272): ¿cuántas preguntas se apoyan en fuentes así y cómo se espera que se respondan?

### C. Citación (20 pts)

9. **¿Qué cuenta como "norma del fundamento de referencia"?** ¿Solo el artículo, o también el código o la ley que lo contiene? Hay `legal_basis` vagos o de baja calidad (#24 no tiene, #442 solo dice "Código Sustantivo del Trabajo", #1065 cita el art. 20 del Código Penal para una pregunta de contratación). ¿Cómo se evaluó eso?
10. **Vigencia:** ¿contra qué fecha se valida la vigencia (la de redacción del banco o la actual)? ¿Hay preguntas sobre normas derogadas o modificadas?
11. **Compilaciones:** cuando un decreto único reglamentario (DUR) compila un decreto, ¿cuál se considera la fuente correcta?

### D. Cerradas (20 pts) y abstención (10 pts)

12. **¿Cuántas cerradas dependen de jurisprudencia y no del texto de una norma?** ¿Qué errores típicos buscan los distractores (excepción contra regla, plazos cercanos, norma derogada)?
13. **¿Qué preguntas del banco consideran "no respondibles" con fuentes públicas?** ¿Hay otras como el id 374 (marcado defectuoso) que debamos tratar con cuidado?

### E. Corpus

14. **Cobertura por área:** el banco no cubre derecho ambiental ni internacional. ¿Entra el derecho comunitario andino (Decisión 486) dentro de "mercados"? ¿Qué otras fuentes de ese tipo hay?
15. **Las 6 preguntas de la muestra donde el híbrido no recuperó la fuente** (#60, #748, #247, #679, #239, #661): ¿qué fuente tenían en mente los autores? Es sobre la muestra, no sobre el test.

## Si solo hay tiempo para cinco

**1** (campos de sub-tarea en el test), **2** (estratificación), **3** (normas inexistentes y premisas falsas, que define cuándo abstenerse), **4** (reproducción literal) y **5** (jurisprudencia: contenido concreto o criterio general).
