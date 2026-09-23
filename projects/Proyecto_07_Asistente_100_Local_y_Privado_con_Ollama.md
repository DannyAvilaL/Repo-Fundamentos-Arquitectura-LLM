**PROYECTO FINAL · OPCIÓN 7 de 10**

**Asistente 100% Local y Privado con Ollama**

*Cuándo self-hosted es la decisión correcta —demostrado, no solo argumentado*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

La Sesión 2 comparó API gestionada vs. self-hosted en términos generales: control de datos, costo a escala, y ausencia de mantenimiento de infraestructura como criterios a favor de cada opción. Pero en la práctica profesional, la decisión de usar exclusivamente modelos locales casi siempre surge de un requisito no negociable: datos que legalmente o contractualmente no pueden salir de la infraestructura de la organización (información de recursos humanos, historiales médicos, contratos legales, secretos comerciales).

Este proyecto le pide al estudiante construir una aplicación que sea, por diseño, incapaz de enviar datos a un tercero —no porque se configuró para no hacerlo, sino porque arquitectónicamente no tiene ninguna dependencia de red externa una vez que el modelo está descargado—, y respaldar con métricas propias, no solo con la tabla del curso, si esa decisión tiene sentido de costo/desempeño.

**2. Objetivos de aprendizaje**

- Construir una aplicación funcional cuya única dependencia de inferencia sea un modelo local vía Ollama, sin ninguna llamada a una API externa.

- Medir, con datos propios, el costo y la latencia reales de la solución local, y compararlos contra una API gestionada equivalente.

- Argumentar, con esos datos y con el criterio de control de datos, si la decisión self-hosted es la correcta para el caso de uso elegido —incluso si la conclusión honesta terminara siendo que NO lo es.

**3. Planteamiento del problema**

Elegir un caso de uso con datos sensibles (el estudiante puede usar datos ficticios que simulen la sensibilidad real: CVs, notas clínicas simuladas, contratos internos, evaluaciones de desempeño), construir una aplicación que lo resuelva usando únicamente un modelo local vía Ollama, demostrar que funciona sin conexión a internet, y presentar un análisis propio de costo/latencia comparado contra al menos una API gestionada equivalente.

**4. Alcance funcional (qué debe hacer el sistema)**

- Una aplicación funcional (puede ser CLI, backend con API, o con frontend simple) que resuelva un problema real usando exclusivamente un modelo servido por Ollama.

- Verificación demostrable de que la aplicación funciona sin conexión a internet una vez descargado el modelo (por ejemplo, desconectando la red durante la demo).

- Medición propia de latencia (tiempo de respuesta) del modelo local para el caso de uso elegido, en el hardware real del estudiante.

- Medición o estimación propia del costo equivalente de resolver el mismo volumen de trabajo con una API gestionada comparable, y comparación directa contra el costo (amortizado o de oportunidad) de la solución local.

- Una sección de análisis que justifique explícitamente, con los datos obtenidos, si self-hosted fue la decisión correcta para ese caso de uso.

**5. Requisitos no funcionales**

- El modelo local elegido debe ser viable en hardware de consumo razonable (documentar los requisitos de RAM/GPU usados).

- La aplicación no debe tener ninguna dependencia oculta de red (ej. una llamada de telemetría de alguna librería) que contradiga la premisa de «cero salida de datos» — esto debe verificarse explícitamente, no asumirse.

**6. Arquitectura sugerida**

- Ollama como servidor de inferencia local, con el modelo elegido descargado previamente (\`ollama pull\`).

- Cliente de la aplicación que consuma la API local de Ollama (\`http://localhost:11434\`), nunca un endpoint externo.

- Un módulo de medición de latencia/throughput instrumentado directamente en el código, no estimado a ojo.

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Elegir el caso de uso sensible y el modelo local adecuado (balance entre calidad y requisitos de hardware disponibles).

2.  Fase 2 — Construir la aplicación funcional básica contra Ollama.

3.  Fase 3 — Verificar explícitamente la ausencia de dependencias de red (ej. correr con el adaptador de red desactivado y confirmar que sigue funcionando).

4.  Fase 4 — Instrumentar la medición de latencia y volumen de uso propio del caso de uso elegido.

5.  Fase 5 — Calcular el costo equivalente en una API gestionada para el mismo volumen, y escribir el análisis comparativo final.

**8. Entregables**

- Repositorio con la aplicación funcional.

- Evidencia de que funciona sin conexión a internet (descripción del procedimiento usado para verificarlo, o captura/grabación).

- El análisis de costo/latencia con números propios, no solo estimaciones teóricas.

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                                                | **Peso**    | **Qué se evalúa**                                                                                                                                              |
|---------------------------------------------------------------------------------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                                                                  | **30 pts**  | La aplicación resuelve el caso de uso elegido de forma útil y funciona exclusivamente contra el modelo local.                                                  |
| **Seguridad y arquitectura**                                                                | **20 pts**  | Se verifica explícitamente la ausencia de dependencias de red externas; el diseño refleja consciencia del requisito de confidencialidad de los datos.          |
| **Funciona 100% local + análisis costo/latencia con datos propios (entregable específico)** | **25 pts**  | La demostración sin conexión a internet es real y verificable; el análisis de costo/latencia usa mediciones propias, no cifras copiadas de la tabla del curso. |
| **Documentación**                                                                           | **10 pts**  | Se documentan los requisitos de hardware usados y el proceso de instalación del modelo local.                                                                  |
| **Video (máx. 30 min)**                                                                     | **15 pts**  | Debe incluir la demostración en vivo de funcionamiento sin conexión a internet.                                                                                |
| **Total**                                                                                   | **100 pts** | *Calificación máxima del proyecto*                                                                                                                             |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué caso de uso sensible eligieron y por qué justifica exigir una solución 100% local?

2.  Demuestren en vivo que la aplicación sigue funcionando sin conexión a internet.

3.  Muestren los números de su análisis de costo/latencia: ¿cuánto cuesta y cuánto tarda la solución local versus la API gestionada equivalente, para el mismo volumen?

4.  Con esos números en mano, ¿sigue siendo self-hosted la decisión correcta, o el análisis los sorprendió?

**11. Errores comunes a evitar**

- Afirmar que la aplicación es «privada» sin verificar realmente que ninguna librería o dependencia hace una llamada de red oculta (telemetría, verificación de actualización, etc.).

- Comparar el costo de la API gestionada usando el precio de un modelo mucho más pequeño o mucho más grande que el modelo local elegido — la comparación debe ser entre modelos de capacidad similar.

- Ignorar el costo de oportunidad del hardware/tiempo humano de mantenimiento en el análisis de costo del self-hosted, presentando solo el costo de electricidad como si fuera el costo total.

**12. Definición de "terminado" (checklist final)**

- La aplicación resuelve el caso de uso elegido usando exclusivamente Ollama.

- Existe evidencia verificable de funcionamiento sin conexión a internet.

- El análisis de costo/latencia usa mediciones propias y llega a una conclusión explícita y justificada.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
