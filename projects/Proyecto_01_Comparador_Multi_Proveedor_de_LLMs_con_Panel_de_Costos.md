**PROYECTO FINAL · OPCIÓN 1 de 10**

**Comparador Multi-Proveedor de LLMs con Panel de Costos**

*Decisiones de arquitectura basadas en datos propios, no en tablas teóricas*

Fundamentos de Arquitectura LLM · Proyecto Final

**1. Contexto y motivación**

Toda organización que empieza a integrar LLMs enfrenta la misma pregunta a nivel ejecutivo: ¿qué proveedor usamos? En la Sesión 3 del curso se revisó una tabla comparativa teórica de proveedores (OpenAI, Anthropic, Google, Meta, Mistral, Azure, Vertex AI, AWS Bedrock, Ollama). Ese conocimiento es necesario pero insuficiente: un arquitecto de soluciones que llega a un comité técnico con «según la documentación, este proveedor debería ser más barato» pierde credibilidad frente a uno que llega con «medí 50 llamadas reales sobre nuestra propia carga de trabajo y este proveedor costó 34% menos con una caída de calidad de solo 2 puntos en nuestra rubrica interna».

Este proyecto convierte al estudiante en la persona que genera esa segunda frase. El objetivo no es demostrar que se sabe llamar a tres SDKs distintos —eso ya se dominó en la Sesión 2—, sino construir la herramienta que una organización real usaría internamente antes de firmar un contrato anual con un proveedor de inferencia.

**2. Objetivos de aprendizaje**

- Diseñar un experimento de comparación de proveedores que sea reproducible: mismos prompts, mismos parámetros de generación, mismas condiciones de red, para que la comparación sea justa y no esté sesgada por variables no controladas.

- Implementar llamadas concurrentes a múltiples proveedores sin que la latencia de uno bloquee la medición de los demás (orquestación asíncrona).

- Traducir la documentación de precios de cada proveedor (que suele venir en USD por millón de tokens, con tokens de entrada y salida facturados distinto) a un cálculo de costo real por llamada.

- Presentar hallazgos de manera que un tomador de decisiones no técnico pueda entenderlos en menos de dos minutos.

**3. Planteamiento del problema**

El estudiante debe construir una herramienta (no un script de un solo uso) que reciba un conjunto de prompts de prueba representativos de un caso de uso real (el estudiante elige el dominio: atención al cliente, generación de reportes, clasificación de documentos, etc.), los envíe a al menos tres proveedores distintos bajo las mismas condiciones, y produzca un panel comparativo con métricas cuantitativas de calidad, costo y latencia, más una recomendación final.

**4. Alcance funcional (qué debe hacer el sistema)**

- Backend en FastAPI con un endpoint que reciba un prompt y un conjunto de proveedores a comparar, y devuelva las respuestas de todos ellos junto con sus métricas.

- Integración con al menos 3 proveedores distintos, de los cuales al menos uno debe ser un modelo local vía Ollama (para que la comparación incluya la opción self-hosted, no solo APIs gestionadas).

- Cálculo de costo estimado por llamada, usando las tarifas públicas vigentes de cada proveedor (documentadas con fecha de consulta, porque cambian).

- Medición de latencia end-to-end (desde que se envía la solicitud hasta que se recibe la respuesta completa) y, si el proveedor lo permite, tiempo hasta el primer token (relevante para experiencia de usuario en streaming).

- Un panel visual (frontend en React) que muestre, para un mismo prompt, las respuestas de los distintos proveedores lado a lado con sus métricas.

- Un mecanismo de «juicio de calidad»: puede ser manual (el estudiante puntúa cada respuesta de 1 a 5 según un rubro que él mismo defina) o asistido (usar un LLM como evaluador, declarando explícitamente el sesgo potencial de esa metodología en la documentación).

**5. Requisitos no funcionales**

- El sistema debe seguir funcionando (en MODO_SIMULADO) si falta la API key de alguno de los proveedores, sin que la aplicación completa se caiga.

- Las llamadas a distintos proveedores deben ejecutarse en paralelo, no en secuencia —de lo contrario, comparar 3 proveedores toma 3 veces más tiempo del necesario y la medición de latencia individual pierde sentido si hay contención de recursos compartidos.

- Ninguna API key debe quedar hardcodeada en el código ni subida al repositorio.

**6. Arquitectura sugerida**

- Backend: FastAPI + \`asyncio.gather()\` (o equivalente) para paralelizar las llamadas a proveedores.

- Clientes de proveedor: un adaptador por proveedor detrás de una interfaz común (por ejemplo, una clase abstracta \`ProveedorLLM\` con un método \`generar(prompt, parametros)\`), para que agregar un cuarto proveedor no obligue a reescribir el orquestador.

- Frontend: React 18 + Vite, con una tabla o grid comparativo y, opcionalmente, un gráfico de barras de costo/latencia por proveedor.

- Persistencia mínima: puede ser tan simple como un archivo JSON o CSV donde se acumulan los resultados de cada corrida, para poder graficar tendencias a lo largo de varias ejecuciones.

**7. Plan de trabajo sugerido (5 fases)**

1.  Fase 1 — Diseño del experimento: definir el dominio del caso de uso, escribir al menos 10 prompts de prueba representativos, y decidir la metodología de evaluación de calidad antes de escribir una sola línea de código de integración.

2.  Fase 2 — Adaptadores de proveedor: implementar el cliente de cada proveedor de forma aislada y probarlo individualmente antes de integrarlo al orquestador.

3.  Fase 3 — Orquestación y medición: implementar las llamadas paralelas, el cálculo de costo y la captura de latencia.

4.  Fase 4 — Panel visual: construir el frontend que consume el backend y presenta los resultados de forma clara.

5.  Fase 5 — Corrida completa y análisis: ejecutar el set completo de prompts de prueba contra todos los proveedores y redactar las conclusiones.

**8. Entregables**

- Repositorio de código completo (backend + frontend) con README explicando cómo ejecutarlo.

- El conjunto de prompts de prueba usados, documentado junto con la justificación de por qué son representativos del dominio elegido.

- Un informe corto (puede ir en el README o como documento separado) con la tabla comparativa final y la recomendación de proveedor, justificada con los datos obtenidos.

- Video explicativo de máximo 30 minutos (ver guía más abajo).

**9. Rúbrica de evaluación (100 puntos)**

| **Criterio**                                     | **Peso**    | **Qué se evalúa**                                                                                                                                                                                                                                                          |
|--------------------------------------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Funcionalidad y código**                       | **30 pts**  | La herramienta corre de punta a punta siguiendo el README; las llamadas a proveedores son verdaderamente paralelas (demostrable midiendo el tiempo total vs. la suma de tiempos individuales); el código separa claramente el adaptador de cada proveedor del orquestador. |
| **Seguridad y arquitectura**                     | **20 pts**  | API keys vía variables de entorno; manejo explícito de fallos de un proveedor sin tumbar la comparación completa; parámetros de generación (temperature, max_tokens) fijados explícitamente e idénticos entre proveedores para que la comparación sea justa.               |
| **Panel de comparación (entregable específico)** | **25 pts**  | El panel muestra al menos 5 métricas por proveedor (calidad, costo, latencia, tokens, y una cuarta a elección); los datos de costo usan tarifas reales vigentes con fecha de consulta citada; la metodología de evaluación de calidad está explícita y es defendible.      |
| **Documentación**                                | **10 pts**  | El README explica no solo cómo correr el proyecto, sino las decisiones de diseño: por qué esos proveedores, por qué esa metodología de evaluación.                                                                                                                         |
| **Video (máx. 30 min)**                          | **15 pts**  | Ver desglose general del curso; además, debe mostrarse una corrida real en vivo, no una grabación pre-hecha editada para ocultar fallos.                                                                                                                                   |
| **Total**                                        | **100 pts** | *Calificación máxima del proyecto*                                                                                                                                                                                                                                         |

*La distribución de pesos sigue el estándar del curso: funcionalidad/código 30 pts, seguridad y arquitectura 20 pts, entregable específico del proyecto 25 pts, documentación 10 pts, video explicativo 15 pts.*

**10. Guía para el video (máx. 30 minutos)**

El video debe responder explícitamente estas preguntas, en cualquier orden, mostrando la aplicación funcionando en vivo:

1.  ¿Qué caso de uso eligieron y por qué los prompts de prueba lo representan bien?

2.  ¿Por qué esos 3 (o más) proveedores específicos, y no otros?

3.  Muestren una corrida completa en vivo: prompt entra, tres respuestas salen, se comparan las métricas.

4.  ¿Cuál fue el hallazgo más sorprendente? (Casi siempre hay uno — un proveedor «barato» que resultó lento, o uno «caro» que fue consistentemente mejor en un tipo de tarea específico.)

5.  Si tuvieran que recomendar UN proveedor a una empresa real con este caso de uso, ¿cuál sería y por qué?

**11. Errores comunes a evitar**

- Comparar proveedores con parámetros de generación distintos (ej. temperature=0 en uno y temperature=0.7 en otro) — invalida la comparación de calidad por completo.

- Medir latencia con llamadas secuenciales y atribuir la lentitud al proveedor cuando en realidad es contención de red o rate limiting propio.

- Usar precios de memoria o de una búsqueda genérica sin verificar la tarifa vigente y específica del modelo exacto usado (los proveedores tienen decenas de modelos con precios distintos).

- Evaluar calidad de forma puramente subjetiva («me pareció mejor») sin una rubrica explícita que otra persona pueda replicar.

**12. Definición de "terminado" (checklist final)**

- El panel corre con al menos 3 proveedores reales (no todos en MODO_SIMULADO) al momento de la entrega.

- El cálculo de costo coincide, dentro de un margen razonable, con lo que efectivamente facturó el proveedor (verificable en el dashboard de facturación si se usó una cuenta real).

- Existe una recomendación final escrita, no solo datos crudos.

BSG · Fundamentos de Arquitectura LLM · Proyecto Final
