# Parte 3.1 — Crear un Agente desde la Consola de Google Cloud (sin código)

Objetivo: crear un agente conversacional simple — el asistente de FAQ de
"Tienda Andina" que usamos en los ejemplos de grounding de esta sesión —
usando únicamente la interfaz web de Google Cloud, sin escribir código.
Esto corresponde a **Agent Studio**, dentro de lo que hoy se llama
**Gemini Enterprise Agent Platform** (antes Vertex AI Agent Builder /
Vertex AI Search & Conversation).

## Paso 1 — Acceder a la consola

1. Ve a [console.cloud.google.com](https://console.cloud.google.com).
2. Selecciona tu proyecto (o crea uno nuevo) en el selector superior.
3. En el buscador superior escribe **"Agent Studio"** o **"Gemini
   Enterprise Agent Platform"** y entra a la sección. Si tu consola aún
   muestra el nombre anterior, busca **"Vertex AI Agent Builder"** — es la
   misma pantalla.

## Paso 2 — Habilitar las APIs necesarias

Si es la primera vez que usas la plataforma, la consola te pedirá habilitar:
- `Vertex AI API`
- `Discovery Engine API` (motor de agentes/búsqueda)

Haz clic en **"Habilitar"** cuando aparezca el aviso. Puedes verificarlo con:
```bash
gcloud services list --enabled | grep -E "aiplatform|discoveryengine"
```

## Paso 3 — Crear un nuevo agente

1. Dentro de **Agent Studio**, haz clic en **"Crear agente"** (Create agent).
2. Completa los campos básicos:
   - **Nombre del agente**: `asistente-tienda-andina`
   - **Idioma predeterminado**: Español
   - **Región**: `us-central1` (o la región más cercana disponible)
3. Selecciona el modelo base — por defecto usará un modelo de la familia
   **Gemini** (ej. Gemini 2.0 Flash).

## Paso 4 — Definir el comportamiento (Instructions)

Aquí es donde los conceptos de la Sesión 4 se vuelven visibles: las
**Instructions** de un agente en la consola cumplen el mismo rol que el
`system_prompt` que armamos a mano en `ejemplos/01_estructura_llamada_api.py`
— es el mismo componente, solo que la consola te da un campo de texto en
vez de una variable de Python.

En el panel de configuración, sección **"Instrucciones"**, escribe:

```
Eres el asistente virtual de "Tienda Andina". Tu objetivo es responder
preguntas frecuentes sobre horarios, métodos de pago y política de
devoluciones. Responde ÚNICAMENTE con base en la información del Data
Store — si la pregunta no está cubierta, di explícitamente que no lo
sabes y ofrece escalar a un agente humano. No inventes datos ni políticas
que no estén en la fuente. Sé breve, amable y siempre en español.
```

Nota la instrucción explícita de "no inventes datos que no estén en la
fuente" — es la misma técnica anti-alucinación de *grounding* vista en
`ejemplos/03_control_alucinacion.py`, aplicada aquí como configuración de
consola en vez de código.

## Paso 5 — Agregar una fuente de conocimiento (Data Store)

1. En la pestaña **"Data Stores"**, haz clic en **"Agregar fuente de datos"**.
2. Puedes subir un PDF/documento con las FAQs, o pegar texto directo:
   ```
   Horario: Lunes a sábado, 9:00 a 20:00.
   Métodos de pago: Tarjeta de crédito/débito, transferencia, efectivo en tienda.
   Devoluciones: Hasta 30 días con boleta, producto sin uso.
   ```
3. Asocia esa fuente de datos al agente — esto habilita respuestas basadas
   en RAG (Retrieval-Augmented Generation) sin necesidad de reentrenar nada.
   Es el mismo `CONTEXTO_DEMO` que ve el endpoint `/demo/completar` del
   backend cuando `usar_grounding=true`, aquí gestionado por la plataforma.

## Paso 6 — Ajustar parámetros de generación (si la consola lo expone)

Algunas versiones de Agent Studio permiten ajustar `temperature` y
`max output tokens` en una sección avanzada de configuración del modelo.
Para un asistente de FAQ que debe apegarse a hechos, usa una
**temperature baja (0.0–0.3)** — el mismo perfil "preciso" que definimos
en `PERFILES_PARAMETROS` en el backend. Si la consola no expone estos
controles directamente, el comportamiento por defecto de Gemini para
agentes de este tipo ya tiende a ser conservador.

## Paso 7 — Probar el agente (Preview)

1. Usa el panel **"Vista previa"** (Preview) a la derecha de la pantalla.
2. Escribe una pregunta de prueba: *"¿Hasta qué hora están abiertos los
   sábados?"*
3. Verifica que la respuesta use la información del Data Store.
4. Prueba también una pregunta **fuera de contexto** (ej. "¿tienen
   sucursal en Madrid?") y confirma que el agente admite no saberlo, en
   vez de inventar una respuesta — esto es la prueba de alucinación más
   simple que existe y aplica igual aquí que en código.

## Paso 8 — Publicar / Integrar

Desde la pestaña **"Integraciones"** puedes:
- Generar un **widget embebible** para un sitio web (`<script>` snippet).
- Exponer un **endpoint de API REST** para consumir el agente desde tu
  propio backend — el mismo patrón de "llamada API con buenas prácticas"
  de esta sesión, solo que ahora el otro lado de la llamada es tu agente.
- Conectarlo a **Dialogflow CX** para flujos conversacionales más complejos.

Para este curso, basta con dejarlo en modo *Preview* — no es necesario
publicarlo públicamente para fines de aprendizaje.

## Costos y limpieza

- Los Data Stores y el uso del modelo se facturan por consumo (tokens +
  almacenamiento del índice de búsqueda).
- Para evitar cargos después del ejercicio, **elimina el agente y el Data
  Store** desde la consola, o borra el proyecto de prueba completo:
  ```bash
  gcloud projects delete TU_PROJECT_ID
  ```

## Comparación rápida con las Partes 3.2 y 3.3

| | 3.1 Consola (Agent Studio) | 3.2 ADK (código) | 3.3 Sin ADK + Docker |
|---|---|---|---|
| Requiere programar | No | Sí (Python) | Sí (Python) |
| Control sobre la llamada API cruda | No — la plataforma la arma | Parcial — el ADK la arma por ti | Total — la escribes tú |
| Ideal para | Prototipo rápido, no-developers | Producción, tools, orquestación | Backends existentes que solo agregan un modelo |
| Versionado en Git | No nativo | Sí — es código | Sí — es código |
