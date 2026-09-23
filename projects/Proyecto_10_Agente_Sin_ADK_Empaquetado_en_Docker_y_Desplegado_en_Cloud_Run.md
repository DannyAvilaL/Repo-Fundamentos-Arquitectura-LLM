**PROYECTO FINAL · OPCIÓN 10 de 10**

**Agente Sin ADK, Empaquetado en Docker y Desplegado en Cloud Run**

*Construir a mano lo que un framework de agentes hace por ti*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

La Parte 3.3 del ejercicio guiado de agentes en Google Cloud mostró cómo construir un agente sin adoptar el framework ADK: un servicio FastAPI plano, con lógica de decisión propia expresada como código Python ordinario, empaquetado en un Dockerfile escrito a mano y desplegado con \`gcloud run deploy\` en vez de \`adk deploy\`. Ese camino existe porque, en la práctica profesional, muchos equipos ya tienen un backend propio y no quieren adoptar un framework de agentes completo solo para agregar una decisión simple respaldada por un LLM.

Este proyecto lleva ese patrón a un caso de uso original, con énfasis explícito en las prácticas de seguridad de contenedores vistas en el curso: usuario no-root dentro del contenedor, secretos gestionados fuera del código y fuera de las variables de entorno en texto plano, y un Dockerfile que el propio estudiante entiende línea por línea, no uno generado automáticamente.

**2. Objetivos de aprendizaje**

- Entender, construyendo el equivalente mínimo a mano, qué resuelve realmente un framework de agentes como el ADK (y por lo tanto, cuándo vale la pena adoptarlo y cuándo no).

- Escribir un \`Dockerfile\` propio siguiendo prácticas de seguridad de contenedores de nivel producción.

- Completar el ciclo completo de despliegue a Google Cloud Run con gestión adecuada de secretos.

**3. Planteamiento del problema**

Construir un servicio FastAPI propio (sin usar el framework ADK) que tome decisiones de negocio simples apoyándose en un LLM para un caso de uso original, empaquetarlo en un \`Dockerfile\` escrito por el estudiante siguiendo prácticas de seguridad de contenedores, y desplegarlo en Google Cloud Run con el secreto/API key gestionado a través de Secret Manager, nunca como variable de entorno en texto plano.

**4. Alcance funcional (qué debe hacer el sistema)**

- Un servicio FastAPI con lógica de decisión propia (por ejemplo, un endpoint que reciba una solicitud y decida, usando el LLM, cómo clasificarla o a qué flujo enviarla — análogo a la lógica de \`decidir_accion()\` del ejemplo del curso, pero para un caso de uso distinto).

- Un \`Dockerfile\` propio (no autogenerado por una herramienta) que siga prácticas de seguridad de contenedores: imagen base mínima, usuario no-root, sin secretos copiados dentro de la imagen.

- Despliegue funcional en Google Cloud Run, accesible mediante una URL pública o protegida por IAM.

- Gestión del secreto/API key exclusivamente vía Google Secret Manager, referenciado en el despliegue (\`--set-secrets\`), nunca como variable de entorno en texto plano ni copiado dentro del contenedor.

**5. Requisitos no funcionales**

- El contenedor debe escuchar en el puerto que Cloud Run inyecta dinámicamente (variable \`PORT\`), nunca un puerto fijo asumido.

- El servicio debe responder de forma controlada ante una solicitud mal formada, sin exponer trazas de error internas al cliente.

**6. Arquitectura sugerida**

- FastAPI puro (sin ADK) como framework del servicio.

- Un \`Dockerfile\` escrito a mano: imagen base \`python:3.12-slim\` o equivalente, instalación de dependencias, creación explícita de un usuario no-root, y \`CMD\` que arranca el servicio.

- Google Secret Manager para el secreto/API key, referenciado en el comando de despliegue de Cloud Run.

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Diseñar el caso de uso y la lógica de decisión propia (qué condiciones activan qué rama de comportamiento).

2.  Fase 2 — Implementar y probar el servicio FastAPI localmente, sin Docker aún.

3.  Fase 3 — Escribir el \`Dockerfile\` propio y probar la imagen localmente (\`docker build\` + \`docker run\`) antes de intentar el despliegue en la nube.

4.  Fase 4 — Crear el secreto en Google Secret Manager y desplegar a Cloud Run referenciándolo, nunca copiándolo en texto plano.

5.  Fase 5 — Verificar el servicio desplegado con una llamada real y confirmar que el secreto nunca aparece expuesto (ni en logs, ni en la configuración visible del servicio).

**8. Entregables**

- Repositorio con el servicio FastAPI y el \`Dockerfile\` propio.

- Evidencia del despliegue funcional en Cloud Run (URL, capturas de verificación).

- Evidencia de que el secreto se gestiona vía Secret Manager (comando de creación del secreto y de despliegue referenciándolo, sin exponer el valor real).

- Video explicativo de máximo 30 minutos.

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                                                                                 | **Peso**    | **Qué se evalúa**                                                                                                                                                            |
|--------------------------------------------------------------------------------------------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                                                                                   | **30 pts**  | El servicio responde correctamente y la lógica de decisión propia funciona de forma consistente para el caso de uso elegido.                                                 |
| **Seguridad y arquitectura**                                                                                 | **20 pts**  | El \`Dockerfile\` sigue prácticas de seguridad de contenedores (usuario no-root, imagen mínima); el puerto se lee dinámicamente de la variable de entorno \`PORT\`.          |
| **Contenedor propio desplegado en Cloud Run con secretos gestionados correctamente (entregable específico)** | **25 pts**  | El despliegue en Cloud Run es real y verificable; el secreto se gestiona exclusivamente vía Secret Manager, nunca en texto plano en ningún punto del pipeline de despliegue. |
| **Documentación**                                                                                            | **10 pts**  | El \`Dockerfile\` y las decisiones de seguridad de contenedores están explicadas, no solo presentes.                                                                         |
| **Video (máx. 30 min)**                                                                                      | **15 pts**  | Debe mostrarse el servicio YA DESPLEGADO respondiendo en vivo, y explicarse cómo el secreto llega al contenedor sin exponerse.                                               |
| **Total**                                                                                                    | **100 pts** | *Calificación máxima del proyecto*                                                                                                                                           |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué caso de uso eligieron y cómo funciona la lógica de decisión propia del servicio?

2.  Recorran el \`Dockerfile\` línea por línea explicando cada decisión de seguridad tomada.

3.  Demuestren el servicio YA DESPLEGADO en Cloud Run respondiendo a una llamada real.

4.  Expliquen cómo el secreto llega al servicio en producción sin quedar expuesto en ningún momento del proceso.

**11. Errores comunes a evitar**

- Copiar el archivo \`.env\` con el secreto real dentro de la imagen de Docker — queda embebido permanentemente en la imagen, incluso si luego se borra del contenedor en ejecución.

- Asumir un puerto fijo (ej. 8080 hardcodeado) en vez de leer la variable \`PORT\` que Cloud Run inyecta dinámicamente, lo cual puede causar que el despliegue falle silenciosamente.

- Ejecutar el proceso principal como usuario root dentro del contenedor —contradice directamente la práctica de seguridad de contenedores exigida por este proyecto.

- Usar \`--set-env-vars\` para pasar el secreto en el despliegue en vez de \`--set-secrets\` con Secret Manager — técnicamente funciona, pero expone el secreto en la configuración visible del servicio.

**12. Definición de "terminado" (checklist final)**

- El servicio está desplegado en Cloud Run y responde correctamente a una llamada real al momento de grabar el video.

- El \`Dockerfile\` usa un usuario no-root y lee el puerto dinámicamente.

- El secreto se gestiona vía Secret Manager, verificable en el comando de despliegue usado.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
