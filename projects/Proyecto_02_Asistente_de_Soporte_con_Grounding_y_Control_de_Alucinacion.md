**PROYECTO FINAL · OPCIÓN 2 de 10**

**Asistente de Soporte con Grounding y Control de Alucinación**

*De la teoría anti-alucinación de la Sesión 4 a un sistema propio y defendible*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

La Sesión 4 presentó dos casos reales con consecuencias legales: un abogado sancionado por citar jurisprudencia inventada por ChatGPT (Mata v. Avianca), y una aerolínea declarada responsable por la información falsa que dio su propio chatbot (Moffatt v. Air Canada). Ambos casos comparten un patrón: un sistema conversacional respondió con confianza sobre algo que no sabía con certeza, y nadie en el diseño del sistema había construido un mecanismo para evitarlo.

Este proyecto le pide al estudiante que construya ese mecanismo —no como un ejercicio teórico, sino como un sistema que un negocio real podría desplegar sin exponerse al mismo riesgo. El ejemplo de «Tienda Andina» visto en clase es el punto de partida conceptual, no el entregable: el proyecto exige un dominio de conocimiento propio, distinto al del curso.

**2. Objetivos de aprendizaje**

- Implementar grounding real (inyección de contexto verificado en el prompt) y demostrar, con evidencia, cómo cambia el comportamiento del modelo con y sin él.

- Diseñar un mecanismo propio de detección de posibles alucinaciones en la salida del modelo (más allá de copiar la heurística de regex vista en clase).

- Entender los límites de estas técnicas: el grounding reduce el riesgo de alucinación, pero no lo elimina —el proyecto debe reflejar esa honestidad técnica en su documentación.

**3. Planteamiento del problema**

Construir un chatbot de atención al cliente para un negocio (real o ficticio, pero con una base de conocimiento propia y sustancial, mínimo 10 preguntas/respuestas distintas a los ejemplos del curso) que responda Únicamente con base en información verificada, admita explícitamente cuando no sabe algo, y marque sus propias respuestas cuando detecte señales de posible invención.

**4. Alcance funcional (qué debe hacer el sistema)**

- Una base de conocimiento propia (puede ser un documento de texto, un JSON estructurado, o varios archivos) con información verificable sobre el negocio elegido.

- Un endpoint que reciba una pregunta del usuario y responda usando únicamente el contexto de esa base de conocimiento, inyectado explícitamente en el prompt.

- Un modo de comparación: la misma pregunta debe poder enviarse CON grounding y SIN grounding, para que el efecto sea observable y demostrable, no solo afirmado.

- Una heurística propia (puede ser basada en reglas, en un segundo paso de verificación con el mismo modelo, o en ambas) que marque respuestas sospechosas de contener información no verificada.

- Manejo explícito del caso «pregunta fuera de la base de conocimiento»: el sistema debe admitir que no sabe, nunca inventar.

**5. Requisitos no funcionales**

- La base de conocimiento no debe estar hardcodeada dentro del prompt de sistema como texto fijo si supera cierto tamaño —debe cargarse dinámicamente desde un archivo o fuente externa.

- El sistema debe responder en un tiempo razonable aún con la base de conocimiento cargada (evitar inyectar documentos completos de cientos de páginas sin ninguna forma de búsqueda/filtrado previo).

**6. Arquitectura sugerida**

- Backend FastAPI con al menos dos rutas o un parámetro que alterne entre modo «con grounding» y «sin grounding» para la misma pregunta.

- Un módulo de «recuperación» simple: no es obligatorio implementar una base vectorial completa (aunque se valora si se hace), pero sí debe existir alguna lógica que decida qué parte de la base de conocimiento es relevante para la pregunta, en vez de inyectar siempre todo el documento.

- Un módulo de post-procesamiento que aplique la heurística anti-alucinación sobre la respuesta antes de devolverla al usuario.

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Curar la base de conocimiento: elegir el dominio y redactar información verificable y consistente (evitar contradicciones internas, que confundirían tanto al modelo como a la evaluación).

2.  Fase 2 — Implementar el modo sin grounding y documentar sus fallos típicos (esto es evidencia, no un paso desechable).

3.  Fase 3 — Implementar el modo con grounding y comparar respuesta por respuesta contra el modo anterior.

4.  Fase 4 — Diseñar y probar la heurística anti-alucinación propia contra casos diseñados deliberadamente para engañarla.

5.  Fase 5 — Documentar los límites encontrados: ¿qué tipo de pregunta sigue siendo riesgosa incluso con grounding?

**8. Entregables**

- Repositorio con backend funcional y la base de conocimiento propia incluida.

- Un documento comparativo (tabla o lista) con al menos 5 pares de preguntas mostrando la respuesta CON y SIN grounding.

- Documentación de la heurística anti-alucinación implementada y de sus casos de prueba (incluidos los que la engañaron, si los hubo — admitir limitaciones suma, no resta).

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                        | **Peso**    | **Qué se evalúa**                                                                                                                                                                     |
|---------------------------------------------------------------------|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                                          | **30 pts**  | El sistema responde correctamente en ambos modos (con/sin grounding); el manejo de preguntas fuera de dominio es robusto y consistente.                                               |
| **Seguridad y arquitectura**                                        | **20 pts**  | API keys seguras; separación clara entre el módulo de recuperación de contexto y el de generación; límites de longitud de respuesta configurados.                                     |
| **Grounding + heurística anti-alucinación (entregable específico)** | **25 pts**  | El efecto del grounding es demostrable con evidencia real, no solo afirmado; la heurística propia va más allá de copiar el ejemplo de clase y fue probada contra casos adversariales. |
| **Documentación**                                                   | **10 pts**  | Se documentan honestamente los límites del sistema, no solo sus éxitos.                                                                                                               |
| **Video (máx. 30 min)**                                             | **15 pts**  | Debe incluir la demostración en vivo del contraste con/sin grounding, no solo una descripción verbal de que existe.                                                                   |
| **Total**                                                           | **100 pts** | *Calificación máxima del proyecto*                                                                                                                                                    |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué negocio eligieron y por qué la base de conocimiento es representativa de un caso real?

2.  Demuestren en vivo la MISMA pregunta con y sin grounding — la diferencia debe ser visible.

3.  Expliquen cómo funciona su heurística anti-alucinación con un ejemplo real que haya disparado la alerta.

4.  ¿Encontraron algún caso donde el sistema falló a pesar del grounding? ¿Qué aprendieron de eso?

**11. Errores comunes a evitar**

- Inyectar toda la base de conocimiento en cada llamada sin ningún filtrado, lo cual funciona en la demo pero no escala y no demuestra comprensión real del patrón RAG.

- Diseñar la base de conocimiento tan simple que el modelo «adivina» la respuesta correcta incluso sin grounding, haciendo que la comparación no muestre diferencia alguna.

- Confundir «el modelo dijo que no sabe» con «el modelo realmente no tenía la información» — a veces el modelo admite ignorancia por instrucción del prompt incluso cuando sí tenía datos relevantes disponibles; esto también debe observarse y documentarse.

**12. Definición de "terminado" (checklist final)**

- Existe al menos un ejemplo documentado y reproducible donde el modo sin grounding inventó información falsa de forma convincente.

- La heurística anti-alucinación detecta correctamente al menos ese caso.

- El sistema nunca responde con información fuera de la base de conocimiento sin marcarla o admitir incertidumbre.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
