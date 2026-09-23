**PROYECTO FINAL · OPCIÓN 8 de 10**

**Framework de Evaluación de Proveedores para un Caso de Negocio**

*De los criterios legales de la Sesión 3 a una recomendación ejecutiva real*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

La Sesión 3 cubrió los términos legales y contractuales que un arquitecto de soluciones debe revisar antes de integrar un proveedor de LLM en un proyecto empresarial: DPA, residencia de datos, AUP, SLA, retención de datos, licenciamiento de modelos open-weight. La mayoría de los ejercicios técnicos del curso, sin embargo, se enfocan en calidad y costo técnico, dejando estos criterios contractuales como conocimiento declarativo.

Este proyecto los convierte en la base de una decisión de negocio real: dado un caso de uso empresarial con requisitos regulatorios o contractuales específicos, el estudiante debe producir el tipo de documento que un comité de arquitectura o de compliance esperaría ver antes de aprobar la integración de un proveedor externo de IA.

**2. Objetivos de aprendizaje**

- Aplicar los criterios legales/contractuales de la Sesión 3 (DPA, residencia de datos, AUP, SLA) a un caso de negocio concreto, no de forma abstracta.

- Combinar evidencia técnica propia (no solo documentación de marketing del proveedor) con criterios contractuales en una única recomendación.

- Practicar la comunicación ejecutiva: producir una recomendación que un tomador de decisiones no técnico pueda usar para actuar.

**3. Planteamiento del problema**

Elegir un caso de uso empresarial con requisitos regulatorios o de confidencialidad explícitos (ej. un banco procesando reclamos de clientes con datos personales, una aseguradora de salud analizando historiales clínicos, una firma legal procesando contratos confidenciales), comparar al menos 3 a 4 proveedores de LLM en criterios técnicos Y contractuales relevantes a ese caso, y producir una recomendación final justificada dirigida a un comité de decisión.

**4. Alcance funcional (qué debe hacer el sistema)**

- Definición explícita del caso de negocio elegido, incluyendo qué tipo de datos maneja y qué requisitos regulatorios o contractuales aplican (aunque sean simplificados/ficticios, deben ser realistas: GDPR, LGPD, HIPAA, secreto profesional, etc., según corresponda).

- Una matriz de comparación de al menos 3-4 proveedores con mínimo 6 criterios, combinando al menos 3 técnicos (calidad, costo, latencia) y al menos 3 contractuales/legales (DPA disponible, residencia de datos configurable, AUP compatible con el caso de uso, SLA formal).

- Al menos una prueba técnica propia (no solo lectura de documentación) que aporte evidencia real a la columna de calidad de la matriz —por ejemplo, correr el mismo conjunto de prompts representativos del caso de uso contra los proveedores comparados.

- Una recomendación final por escrito, dirigida explícitamente a un lector ejecutivo, que declare un proveedor ganador (o descarte a todos y explique por qué) con la justificación basada en la matriz.

**5. Requisitos no funcionales**

- La información contractual usada (DPA, SLA, políticas de retención) debe citarse desde fuentes verificables (documentación oficial del proveedor), no de memoria ni de la tabla genérica del curso.

- El documento final debe ser legible por alguien sin formación técnica profunda — el lenguaje técnico debe explicarse, no asumirse.

**6. Arquitectura sugerida**

- Un componente de prueba técnica (puede ser un script simple que llame a los proveedores comparados con el mismo conjunto de prompts del dominio elegido).

- Un documento/matriz de comparación (tabla estructurada, puede vivir en el mismo informe).

- Un informe final en formato ejecutivo (resumen, matriz, recomendación, riesgos).

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Definir el caso de negocio y los requisitos regulatorios/contractuales aplicables, investigando qué exige realmente ese tipo de industria (aunque sea de forma simplificada).

2.  Fase 2 — Investigar y documentar, con fuentes citables, los términos contractuales relevantes de cada proveedor comparado (DPA, residencia de datos, AUP, SLA).

3.  Fase 3 — Construir y correr la prueba técnica propia sobre los proveedores comparados, usando prompts representativos del caso de uso.

4.  Fase 4 — Consolidar la matriz de comparación combinando los hallazgos técnicos y contractuales.

5.  Fase 5 — Redactar la recomendación final en formato ejecutivo.

**8. Entregables**

- El informe final (matriz de comparación + recomendación justificada), en un formato legible para un público ejecutivo.

- El código o registro de la prueba técnica propia usada como evidencia.

- Las fuentes citadas para cada afirmación contractual (enlaces a documentación oficial de cada proveedor).

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                                  | **Peso**    | **Qué se evalúa**                                                                                                                                            |
|-------------------------------------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código (prueba técnica)**                                   | **30 pts**  | La prueba técnica es real, reproducible, y sus resultados alimentan efectivamente la matriz de comparación.                                                  |
| **Seguridad y arquitectura**                                                  | **20 pts**  | Manejo seguro de credenciales en la prueba técnica; consideración explícita de cómo cada proveedor manejaría datos sensibles del caso de uso elegido.        |
| **Matriz de comparación + recomendación justificada (entregable específico)** | **25 pts**  | La matriz combina criterios técnicos y contractuales con fuentes verificables; la recomendación final es específica al caso de negocio elegido, no genérica. |
| **Documentación**                                                             | **10 pts**  | El informe está escrito en un formato claro y ejecutivo, citando fuentes para cada afirmación contractual.                                                   |
| **Video (máx. 30 min)**                                                       | **15 pts**  | Debe explicarse la recomendación final como si se presentara ante un comité de decisión real.                                                                |
| **Total**                                                                     | **100 pts** | *Calificación máxima del proyecto*                                                                                                                           |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué caso de negocio eligieron y qué requisitos regulatorios/contractuales aplican?

2.  Muestren la matriz de comparación completa y expliquen cómo obtuvieron cada dato (técnico y contractual).

3.  ¿Cuál es la recomendación final y qué riesgo específico del proveedor NO elegido la descartó?

4.  Presenten la recomendación como si estuvieran frente a un comité ejecutivo real, no como una exposición técnica interna.

**11. Errores comunes a evitar**

- Citar términos contractuales de memoria («creo que Azure permite fijar la región») en vez de verificarlos en la documentación oficial vigente.

- Presentar la matriz de comparación sin llegar a una recomendación final concreta — dejar la decisión «abierta» no es aceptable para este entregable.

- Ignorar el criterio contractual más relevante para el caso de uso elegido (ej. evaluar un caso de salud sin mencionar retención de datos o confidencialidad explícitamente).

**12. Definición de "terminado" (checklist final)**

- La matriz de comparación cubre al menos 6 criterios verificables sobre al menos 3 proveedores.

- Existe una prueba técnica propia, no solo información de documentación.

- El informe concluye con una recomendación final explícita y justificada.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
