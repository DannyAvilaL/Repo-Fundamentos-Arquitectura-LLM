# Marco teórico: Evaluación, Costeo y Ética en el Uso de LLM

Este documento acompaña el código de `backend/` con el fundamento teórico de cada decisión de diseño, para que el ejemplo no sea solo "código que funciona" sino una aplicación explícita de marcos reconocidos de la industria y la academia.

## 1. Por qué un harness ligero y no un framework de evaluación completo

Frameworks como **HELM** (Liang et al., 2022, "Holistic Evaluation of Language Models", arXiv:2211.09110, Stanford CRFM) evalúan modelos en decenas de escenarios y docenas de métricas (precisión, calibración, robustez, equidad, eficiencia, toxicidad, entre otras). Es el estándar correcto para **comparar modelos base** a nivel de la industria.

Para un **PoC de un caso de uso específico** —como el asistente de soporte de "Tienda Andina"— ese nivel de exhaustividad es prematuro. Lo que un equipo necesita en la primera iteración es un conjunto mínimo, reproducible y barato de señales que respondan tres preguntas concretas:

1. ¿Las respuestas son correctas para *mi* dominio? (no para un benchmark genérico)
2. ¿El modelo reconoce sus límites en las preguntas donde inventar una respuesta es peligroso?
3. ¿Cuánto cuesta y qué tan rápido es, a la escala que yo espero usarlo?

Esa es la filosofía de `evaluacion.py`: tres métricas deterministas y gratuitas (superposición léxica, cautela apropiada, longitud relativa), corridas contra un dataset dorado de 10 ítems curado a mano para el dominio del PoC — no contra un benchmark público que no representa el caso de uso real.

## 2. Métricas ligeras vs. LLM-como-juez

Un enfoque cada vez más común es usar un segundo LLM para puntuar la calidad de una respuesta ("LLM-as-a-judge"). Dos papers fundamentan y también advierten sobre esta técnica:

- **Liu et al., 2023**, "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment" (arXiv:2303.16634, EMNLP 2023) muestra que un LLM con una cadena de razonamiento explícita (chain-of-thought, ver Wei et al. 2022 de la Sesión 2) puede alcanzar mejor correlación con el juicio humano que las métricas léxicas clásicas como BLEU o ROUGE.
- **Zheng et al., 2023**, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (arXiv:2306.05685, NeurIPS 2023) documenta también los sesgos del método: sesgo de posición (el juez tiende a preferir la primera respuesta que ve), sesgo de verbosidad (prefiere respuestas más largas aunque no sean mejores) y sesgo de auto-preferencia (un juez tiende a puntuar mejor las respuestas generadas por un modelo de su misma familia).

**Decisión de diseño de este PoC**: el harness de `evaluacion.py` deja el LLM-como-juez como una extensión **opcional y documentada**, nunca como la única señal. Las tres métricas deterministas siempre se calculan primero porque son gratuitas, reproducibles y no tienen los sesgos anteriores — son el "piso" de confianza antes de añadir una capa de evaluación más cara y más rica, pero también más ruidosa.

Adicionalmente, RAGAS (Es et al., 2023, "Ragas: Automated Evaluation of Retrieval Augmented Generation", arXiv:2309.15217, EACL 2024) formaliza la dimensión de **faithfulness** (fidelidad: ¿la respuesta está sustentada por el contexto/la referencia, o inventa información no soportada?) usando inferencia de lenguaje natural (NLI). La métrica `metrica_cautela_apropiada()` de este PoC es una versión heurística y barata de esa misma idea: en vez de un modelo NLI completo, busca señales léxicas explícitas de cautela ("no tengo acceso a...", "te recomiendo verificar...") en las preguntas marcadas como de alto riesgo de alucinación.

## 3. Costeo: de tokens a decisión de negocio

El objetivo de desempeño de la sesión pide explícitamente "un estimado de costos/tiempos para un PoC simple". `costeo.py` separa dos preguntas que suelen confundirse:

1. **¿Cuánto cuesta una llamada?** — función de tokens de entrada/salida y la tarifa del proveedor (`calcular_costo_llamada`).
2. **¿Cuánto costaría este PoC si lo usan efectivamente los usuarios que esperamos?** — proyección lineal simple a partir de un volumen estimado (`proyectar_costo_poc`).

La proyección es deliberadamente simple (lineal, sin descuentos por volumen) porque en la etapa de PoC el objetivo no es un modelo financiero preciso, sino tener **un número de referencia** para decidir si vale la pena seguir invirtiendo antes de escalar. Esa es también la razón por la que el módulo advierte explícitamente sobre lo que la proyección NO incluye (infraestructura, reintentos, costo de evaluación con LLM-como-juez).

## 4. Ética: de principios abstractos a un checklist accionable

Dos marcos de gobernanza de IA reconocidos fundamentan el checklist de `etica.py`:

- **NIST AI RMF 1.0** (National Institute of Standards and Technology, 2023, "AI Risk Management Framework (AI RMF 1.0)", U.S. Department of Commerce) organiza la gestión de riesgo de IA en cuatro funciones: **Gobernar** (políticas y responsabilidades), **Mapear** (identificar riesgos del contexto específico), **Medir** (cuantificar esos riesgos, que es justo lo que hace `evaluacion.py`) y **Gestionar** (mitigar y monitorear). El checklist de la sesión cubre principalmente Mapear y Gobernar, complementando lo que las métricas cuantitativas ya cubren de Medir.

- **Reglamento de IA de la Unión Europea** (Reglamento (UE) 2024/1689, "AI Act") clasifica los sistemas de IA en cuatro niveles de riesgo (inaceptable, alto, limitado, mínimo). Un asistente de soporte al cliente como el de este PoC normalmente cae en riesgo limitado, lo cual **no significa "sin obligaciones"**: el Reglamento exige transparencia explícita (el usuario debe saber que interactúa con un sistema de IA), que es la primera pregunta del checklist (`transparencia_ia`).

**Decisión de diseño importante**: el checklist no es una casilla de verificación decorativa. `resumen_checklist()` calcula explícitamente si hay ítems marcados "no" y los trata como **bloqueantes** para avanzar el PoC — la ética se trata con el mismo rigor de "pasa/no pasa" que un test automatizado, no como una reflexión opcional al final del proyecto.

## 5. Conexión con la Sesión 4 (seguridad OWASP)

Varias preguntas del dataset dorado (`q07`, `q08`) y del checklist de ética (`limites_alcance`) reutilizan deliberadamente categorías del **OWASP Top 10 para LLM Applications (2025)** vistas en la Sesión 4 — específicamente LLM01 (Prompt Injection), LLM06 (Excessive Agency) y LLM07 (System Prompt Leakage). Esto es intencional: evaluación de calidad, evaluación de seguridad y evaluación ética no son tres actividades separadas en la práctica — un PoC maduro las corre juntas, contra el mismo dataset, en el mismo pipeline, como hace este ejemplo.
