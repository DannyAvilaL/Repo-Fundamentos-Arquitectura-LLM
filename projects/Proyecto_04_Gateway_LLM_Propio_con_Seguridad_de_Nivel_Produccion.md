**PROYECTO FINAL · OPCIÓN 4 de 10**

**Gateway LLM Propio con Seguridad de Nivel Producción**

*El marco OWASP Top 10 para LLMs, aplicado —no solo citado*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

La Sesión 4 introdujo el OWASP Top 10 para LLM Applications (2025) como el estándar de la industria para auditar la seguridad de sistemas con modelos de lenguaje, y lo mapeó explícitamente a tres decisiones concretas de la arquitectura del curso: manejo de API keys (LLM02), rate limiting (LLM10) y sanitización de input (LLM01). Ese mapeo, sin embargo, se hizo sobre un backend ya construido por el equipo docente.

Este proyecto le pide al estudiante hacer el ejercicio inverso y completo: diseñar un backend propio pensando desde el inicio en el marco OWASP, no parchándolo después. Un gateway LLM es, en esencia, la puerta de entrada única entre las aplicaciones de una organización y los proveedores de modelos — es exactamente el tipo de componente donde una falla de seguridad tiene el mayor radio de impacto.

**2. Objetivos de aprendizaje**

- Aplicar de forma proactiva, no reactiva, al menos 3 mitigaciones del marco OWASP Top 10 para LLMs.

- Entender la diferencia entre una mitigación «de papel» (existe en la documentación) y una mitigación real (puede demostrarse en vivo que funciona, provocando la condición que debería bloquear).

- Diseñar logging que sea útil para auditoría sin convertirse, él mismo, en una fuga de datos sensibles.

**3. Planteamiento del problema**

Construir un backend FastAPI que funcione como gateway único hacia uno o más proveedores de LLM, implementando de forma demostrable al menos tres mitigaciones de seguridad mapeadas explícitamente a categorías del OWASP Top 10 para LLMs, con evidencia reproducible de que cada mitigación efectivamente detiene el ataque o mal uso que pretende prevenir.

**4. Alcance funcional (qué debe hacer el sistema)**

- Un único punto de entrada (endpoint) por el cual toda llamada a un LLM debe pasar —ninguna otra parte del sistema llama directamente al proveedor.

- Rate limiting configurado y verificable (LLM10 — Unbounded Consumption): debe poder demostrarse una solicitud rechazada por exceder el límite.

- Sanitización de input antes de que llegue al prompt (LLM01 — Prompt Injection): debe existir al menos un caso de prueba de un input malicioso o manipulador que sea neutralizado o rechazado.

- Manejo seguro de credenciales (LLM02 — Sensitive Information Disclosure): ninguna API key en el código ni en los logs.

- Una cuarta mitigación a elección del estudiante, tomada del resto del listado OWASP (por ejemplo, LLM07 System Prompt Leakage: verificar que el system prompt nunca se filtra en la respuesta, o LLM05 Improper Output Handling: nunca ejecutar o interpretar directamente código que el modelo genere).

**5. Requisitos no funcionales**

- El logging debe registrar metadatos útiles para auditoría (timestamp, endpoint, resultado, latencia) sin registrar el contenido completo del prompt del usuario ni ninguna API key.

- El sistema debe degradarse de forma controlada (mensajes de error claros) ante fallos del proveedor upstream, no exponer trazas de error internas al cliente.

**6. Arquitectura sugerida**

- FastAPI como capa de gateway, con middleware o dependencias para rate limiting (ej. \`slowapi\`) y sanitización.

- Un módulo de sanitización de input separado, testeable de forma aislada con casos de prueba específicos.

- Un módulo de logging estructurado (JSON) que explícitamente excluya campos sensibles antes de escribir cualquier registro.

- Documento de mapeo OWASP → mitigación → evidencia, como parte central de la entrega (no un apéndice).

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Elegir las 3-4 categorías OWASP a cubrir y diseñar, para cada una, el caso de prueba que demostrará que la mitigación funciona ANTES de implementarla (esto obliga a pensar como atacante primero).

2.  Fase 2 — Implementar el gateway básico (sin mitigaciones aún) y confirmar que los casos de prueba diseñados en la Fase 1 efectivamente fallan/pasan sin protección (línea base).

3.  Fase 3 — Implementar cada mitigación una por una, reconfirmando el caso de prueba correspondiente después de cada una.

4.  Fase 4 — Implementar el logging estructurado seguro.

5.  Fase 5 — Redactar el documento de mapeo OWASP → mitigación → evidencia.

**8. Entregables**

- Repositorio con el gateway funcional.

- Documento de mapeo explícito: cada categoría OWASP cubierta, la mitigación implementada, y cómo reproducir la evidencia de que funciona.

- Casos de prueba (scripts o pasos manuales documentados) que demuestren cada mitigación en acción, incluyendo el comportamiento SIN la mitigación como línea base de comparación.

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                               | **Peso**    | **Qué se evalúa**                                                                                                                |
|----------------------------------------------------------------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                                                 | **30 pts**  | El gateway funciona como punto único de entrada; el código de cada mitigación está claramente separado y es legible.             |
| **Seguridad y arquitectura**                                               | **20 pts**  | Manejo de credenciales impecable; degradación controlada ante fallos upstream; logging sin datos sensibles.                      |
| **Mapeo OWASP + mitigaciones demostradas en vivo (entregable específico)** | **25 pts**  | Cada mitigación tiene evidencia reproducible (antes/después); el mapeo a categorías OWASP es correcto y específico, no genérico. |
| **Documentación**                                                          | **10 pts**  | El documento de mapeo es claro, completo y permite a un tercero reproducir la evidencia.                                         |
| **Video (máx. 30 min)**                                                    | **15 pts**  | Debe mostrarse en vivo al menos una mitigación siendo burlada SIN protección y luego bloqueada CON protección activada.          |
| **Total**                                                                  | **100 pts** | *Calificación máxima del proyecto*                                                                                               |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué 3-4 categorías OWASP eligieron cubrir y por qué son las más relevantes para un gateway LLM?

2.  Para cada mitigación: muestren el ataque/mal uso SIN protección (línea base) y luego el mismo caso CON la protección activa.

3.  ¿Qué decidieron NO registrar en los logs y por qué esa decisión es correcta desde el punto de vista de seguridad?

4.  Si tuvieran que agregar una quinta mitigación con más tiempo, ¿cuál sería y por qué?

**11. Errores comunes a evitar**

- Implementar una mitigación pero nunca probarla contra el ataque real que debería detener —queda «de papel», no demostrada.

- Confundir rate limiting por IP con rate limiting por usuario/API key — en un gateway real, la segunda es casi siempre la relevante.

- Registrar el prompt completo del usuario en los logs «por si acaso es útil para depurar», lo cual convierte el propio sistema de logging en una fuga de datos sensibles (exactamente lo que OWASP LLM02 advierte).

**12. Definición de "terminado" (checklist final)**

- Cada mitigación elegida tiene un caso de prueba reproducible que demuestra el comportamiento ANTES y DESPUÉS de aplicarla.

- El documento de mapeo OWASP existe y es específico, no una lista genérica copiada de la documentación oficial.

- Ninguna API key ni dato sensible aparece en el código fuente, en el historial de git, ni en los logs generados durante las pruebas.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
