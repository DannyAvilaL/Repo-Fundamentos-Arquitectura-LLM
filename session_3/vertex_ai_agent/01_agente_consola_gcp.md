# Parte 3.1 — Crear un Agente desde la Consola de Google Cloud (sin código)

Objetivo: crear un agente conversacional simple — un asistente de FAQ para
una tienda ficticia — usando únicamente la interfaz web de Google Cloud,
sin escribir código. Esto corresponde a **Agent Studio**, dentro de lo que
hoy se llama **Gemini Enterprise Agent Platform** (antes Vertex AI Agent
Builder / Vertex AI Search & Conversation).

## Paso 1 — Acceder a la consola

1. Ve a [console.cloud.google.com](https://console.cloud.google.com).
2. Selecciona tu proyecto (o crea uno nuevo) en el selector superior.
3. En el buscador superior escribe **"Agent Studio"** o **"Gemini Enterprise Agent Platform"**
   y entra a la sección. Si tu consola aún muestra el nombre anterior, busca
   **"Vertex AI Agent Builder"** — es la misma pantalla.

## Paso 2 — Habilitar las APIs necesarias

Si es la primera vez que usas la plataforma, la consola te pedirá habilitar:
- `Vertex AI API`
- `Discovery Engine API` (motor de agentes/búsqueda)

Haz clic en **"Habilitar"** cuando aparezca el aviso. Puedes verificarlo también con:
```bash
gcloud services list --enabled | grep -E "aiplatform|discoveryengine"
```

## Paso 3 — Crear un nuevo agente

1. Dentro de **Agent Studio**, haz clic en **"Crear agente"** (Create agent).
2. Completa los campos básicos:
   - **Nombre del agente**: `asistente-tienda-demo`
   - **Idioma predeterminado**: Español
   - **Región**: `us-central1` (o la región más cercana disponible)
3. Selecciona el modelo base — por defecto usará un modelo de la familia
   **Gemini** (ej. Gemini 2.0 Flash), optimizado para baja latencia en agentes.

## Paso 4 — Definir el comportamiento (Goal / Instructions)

En el panel de configuración del agente, en la sección **"Instrucciones"**
(Instructions / Goal), escribe algo como:

```
Eres el asistente virtual de "Tienda Andina". Tu objetivo es responder
preguntas frecuentes sobre horarios, métodos de pago y política de
devoluciones. Sé breve, amable y siempre en español. Si no sabes la
respuesta, indica que un agente humano dará seguimiento por correo.
```

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

## Paso 6 — Probar el agente (Preview)

1. Usa el panel **"Vista previa"** (Preview) a la derecha de la pantalla.
2. Escribe una pregunta de prueba: *"¿Hasta qué hora están abiertos los sábados?"*
3. Verifica que la respuesta use la información del Data Store que cargaste.

## Paso 7 — Publicar / Integrar

Desde la pestaña **"Integraciones"** puedes:
- Generar un **widget embebible** para un sitio web (`<script>` snippet).
- Exponer un **endpoint de API REST** para consumir el agente desde tu propio backend.
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

## Comparación rápida con la Parte 3.2

| | Consola (Agent Studio) | ADK (código) |
|---|---|---|
| Requiere programar | No | Sí (Python) |
| Control de lógica interna | Limitado (instrucciones + data store) | Total (tools, orquestación, multi-agente) |
| Ideal para | Prototipo rápido, no-developers | Producción, integración con sistemas propios |
| Versionado en Git | No nativo | Sí — es código |
