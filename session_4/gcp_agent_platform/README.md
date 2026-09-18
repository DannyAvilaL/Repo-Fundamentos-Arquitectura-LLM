# Ejemplo: Agentes en Google Cloud — Gemini Enterprise Agent Platform

> **Nota de nomenclatura (2026):** Google renombró **Vertex AI Agent Builder**
> a **Gemini Enterprise Agent Platform** en mayo de 2026. Si tu consola
> todavía muestra "Vertex AI", los conceptos son equivalentes — solo cambia
> el nombre de marca. El proyecto de GCP, IAM, facturación y modelos Gemini
> subyacentes son los mismos.

Este ejemplo conecta directamente con los temas de la Sesión 4 (estructura
de una llamada API, parámetros, seguridad básica, control de alucinación):
un **agente** no es más que una llamada API envuelta en lógica de decisión
(qué herramienta usar, cuándo escalar, cómo mantenerse dentro del contexto
permitido). Las mismas buenas prácticas aplican — solo cambia quién arma el
prompt final.

Se cubren **tres formas** de crear el mismo agente simple — un asistente de
FAQ para "Tienda Andina" (el mismo caso de estudio usado en los ejemplos de
grounding de esta sesión) — con niveles crecientes de control técnico:

| Parte | Enfoque | Control | Para quién |
|---|---|---|---|
| **3.1** | Consola de GCP (Agent Studio) — sin código | Bajo — instrucciones + data store | Analistas, PMs, prueba de concepto |
| **3.2** | Google ADK (Agent Development Kit) — Python | Alto — tools, orquestación | Desarrolladores, integración con sistemas propios |
| **3.3** | Sin ADK — FastAPI puro + Docker → Cloud Run | Total — cada línea de la llamada API es tuya | Equipos que ya tienen su propio backend y solo necesitan el modelo |

## Estructura

```
gcp_agent_platform/
├── README.md                          ← esta guía
├── 01_agente_consola_gcp.md           ← Parte 3.1: paso a paso en la consola
├── adk_agent/                         ← Parte 3.2: agente con ADK
│   ├── __init__.py
│   ├── agent.py
│   ├── requirements.txt
│   ├── .env.example
│   └── DEPLOY.md
└── sin_adk_docker/                    ← Parte 3.3: agente sin ADK, vía Docker
    ├── main.py
    ├── Dockerfile
    ├── requirements.txt
    ├── .env.example
    └── DEPLOY.md
```

## Prerrequisitos comunes

1. Una cuenta de Google Cloud con facturación habilitada (el tier gratuito
   alcanza para este ejercicio).
2. Un proyecto de GCP creado — anota su `PROJECT_ID`.
3. Habilitar las APIs necesarias:
   ```bash
   gcloud services enable aiplatform.googleapis.com run.googleapis.com \
       artifactregistry.googleapis.com cloudbuild.googleapis.com
   ```
4. Autenticación local (para las Partes 3.2 y 3.3):
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project TU_PROJECT_ID
   ```

## ¿Cuál elegir?

- **¿Quieres validar una idea en minutos, sin tocar código?** → 3.1.
- **¿Tu agente necesita herramientas (tools), memoria de conversación o vas
  a orquestar varios pasos?** → 3.2 (ADK trae todo eso resuelto).
- **¿Ya tienes un backend FastAPI/Flask propio y solo quieres agregarle una
  llamada al modelo, con control total del contenedor y sin adoptar un
  framework de agentes nuevo?** → 3.3.

Ninguna opción es "mejor" en términos absolutos — la elección depende del
control que necesitas versus la velocidad con la que quieres llegar a un
demo funcional. La tabla comparativa completa está en cada guía.
