**PROYECTO FINAL · OPCIÓN 5 de 10**

**Agente Conversacional en Google Cloud (Agent Platform)**

*Del ejercicio guiado del curso a un agente propio, desplegado en la nube*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

El curso desarrolló un ejercicio completo de agentes en Google Cloud en tres variantes (consola sin código, Google ADK, y sin ADK vía Docker), todas resolviendo el mismo caso de uso ficticio de FAQ de «Tienda Andina». Ese ejercicio enseña el mecánica de cada camino, pero un agente que repite exactamente el mismo caso de uso no demuestra que el estudiante entendió cómo diseñar un agente para un problema nuevo.

Este proyecto exige dar el salto de «reproduje el ejemplo» a «diseñé un agente para un problema que el curso nunca resolvió», con al menos una herramienta (tool) propia que el agente pueda invocar, y con evidencia de que efectivamente corre en Google Cloud, no solo en la máquina local del estudiante.

**2. Objetivos de aprendizaje**

- Diseñar la lógica de un agente para un caso de uso original: qué herramientas necesita, cuándo debe usarlas, y qué debe hacer cuando la pregunta está fuera de su dominio de competencia.

- Implementar al menos una tool/función propia (no copiada de \`consultar_faq\`/\`escalar_a_humano\`) que realice una acción real o simulada relevante al caso de uso elegido.

- Completar el ciclo de vida completo de un agente: desarrollo local → despliegue en la nube → verificación de que el servicio desplegado responde correctamente.

**3. Planteamiento del problema**

Diseñar y construir un agente conversacional para un caso de uso original (el estudiante elige el dominio: agendamiento de citas, consulta de estado de pedidos, triage de solicitudes internas de TI, etc.), usando el Google ADK o la consola de Agent Studio, con al menos una herramienta personalizada, y desplegarlo de forma verificable en Google Cloud (Cloud Run o Agent Runtime).

**4. Alcance funcional (qué debe hacer el sistema)**

- Definición clara del caso de uso y de las instrucciones (system prompt / instruction) del agente.

- Al menos una tool/función propia, con su propia lógica de negocio (puede ser simulada, ej. «consultar el estado de un pedido» contra un diccionario en memoria, siempre que la función represente una acción real que el agente podría tomar en producción).

- Manejo explícito del caso en que la pregunta del usuario está fuera del dominio del agente (análogo a la herramienta \`escalar_a_humano\` del curso, pero adaptada al nuevo caso de uso).

- Despliegue funcional en Google Cloud con evidencia verificable (URL del servicio accesible, o capturas del comando de verificación de \`gcloud\`).

**5. Requisitos no funcionales**

- Las credenciales de Google Cloud deben manejarse vía Application Default Credentials o variables de entorno, nunca hardcodeadas.

- El agente debe manejar con gracia una pregunta ambigua o mal formulada, sin fallar de forma abrupta.

**6. Arquitectura sugerida**

- Google ADK (recomendado para mayor control) o Agent Studio (vía consola, para quien priorice velocidad de prototipado) como framework base.

- Al menos una \`FunctionTool\` (o equivalente en Agent Studio) con lógica propia.

- Despliegue vía \`adk deploy cloud_run\` (si se usa ADK) o la ruta de publicación de Agent Studio.

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Elegir el caso de uso y diseñar en papel (antes de programar) qué tools necesita el agente y cuándo debe invocarlas.

2.  Fase 2 — Implementar y probar el agente localmente (\`adk web\` o \`adk run\`), iterando sobre las instrucciones hasta que el comportamiento sea consistente.

3.  Fase 3 — Implementar la tool propia y verificar que el agente la invoca en el momento correcto, no antes ni después.

4.  Fase 4 — Desplegar a Google Cloud y verificar el servicio desplegado con una llamada real (no solo confiar en que el despliegue «parece» exitoso).

5.  Fase 5 — Probar casos límite: preguntas fuera de dominio, preguntas ambiguas, múltiples turnos de conversación si aplica.

**8. Entregables**

- Repositorio con el código del agente (o la configuración exportada, si se usó Agent Studio).

- Evidencia del despliegue en GCP (URL, capturas de \`gcloud run services describe\` o similar).

- Documentación del diseño: qué tools tiene el agente, cuándo las usa, y cómo maneja preguntas fuera de dominio.

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                                      | **Peso**    | **Qué se evalúa**                                                                                                                              |
|-----------------------------------------------------------------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                                                        | **30 pts**  | El agente responde correctamente a la mayoría de las consultas del dominio elegido; la tool propia funciona de forma confiable.                |
| **Seguridad y arquitectura**                                                      | **20 pts**  | Credenciales manejadas correctamente; el agente no expone información sensible ni instrucciones internas al usuario.                           |
| **Agente con tool propia, desplegado y accesible en GCP (entregable específico)** | **25 pts**  | La tool es original y relevante al caso de uso; el despliegue en GCP es verificable y funcional al momento de la entrega, no solo documentado. |
| **Documentación**                                                                 | **10 pts**  | El diseño del agente (instrucciones, tools, límites) está documentado con claridad.                                                            |
| **Video (máx. 30 min)**                                                           | **15 pts**  | Debe mostrarse una conversación en vivo con el agente YA DESPLEGADO en GCP, no solo corriendo localmente.                                      |
| **Total**                                                                         | **100 pts** | *Calificación máxima del proyecto*                                                                                                             |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué caso de uso eligieron y por qué justifica un agente (en vez de un simple endpoint de pregunta-respuesta)?

2.  Expliquen la tool propia: qué hace, cuándo el agente decide invocarla.

3.  Demuestren una conversación en vivo contra el agente YA DESPLEGADO en GCP.

4.  Muestren qué pasa cuando le hacen una pregunta fuera del dominio del agente.

**11. Errores comunes a evitar**

- Probar únicamente en local (\`adk web\`) y nunca verificar realmente que el despliegue en GCP funciona con una llamada externa.

- Reciclar exactamente el caso de uso de «Tienda Andina» cambiando solo los nombres — no demuestra diseño original.

- Diseñar una tool tan genérica (ej. «responder cualquier cosa») que en realidad el agente nunca necesita decidir cuándo usarla, lo cual no demuestra comprensión del patrón de decisión del agente.

**12. Definición de "terminado" (checklist final)**

- El agente está desplegado en GCP y responde a una llamada real al momento de grabar el video.

- La tool propia se invoca correctamente en al menos un caso demostrado en vivo.

- El agente maneja sin fallar al menos una pregunta fuera de su dominio.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
