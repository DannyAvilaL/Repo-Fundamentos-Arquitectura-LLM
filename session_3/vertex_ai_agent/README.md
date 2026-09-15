# Ejemplo: Agentes en Google Cloud (Vertex AI → Gemini Enterprise Agent Platform)

> **Nota de nomenclatura (2026):** Google renombró **Vertex AI Agent Builder** a
> **Gemini Enterprise Agent Platform** en mayo de 2026. Si en tu consola de
> Google Cloud todavía ves "Vertex AI", los conceptos y pasos de esta guía son
> equivalentes — solo cambia el nombre de marca. La plataforma subyacente
> (proyecto de GCP, IAM, facturación, modelos Gemini) es la misma.

Este ejemplo cubre dos formas de crear un agente conversacional simple en
Google Cloud, de menor a mayor control técnico:

| Parte | Enfoque | Para quién |
|---|---|---|
| **3.1** | Consola de Google Cloud (Agent Studio) — sin código | Analistas, PMs, prueba de concepto rápida |
| **3.2** | Google ADK (Agent Development Kit) en Python — código | Desarrolladores, integración en sistemas propios |

## Estructura

```
vertex_ai_agent/
├── README.md                          ← esta guía
├── 01_agente_consola_gcp.md            ← Parte 3.1: paso a paso en la consola
└── adk_agent/                          ← Parte 3.2: agente con ADK
    ├── __init__.py
    ├── agent.py                        ← definición del agente
    ├── requirements.txt
    ├── .env.example
    └── DEPLOY.md                       ← cómo desplegar a Cloud Run / Agent Runtime
```

## Prerrequisitos comunes

1. Una cuenta de Google Cloud con facturación habilitada (el tier gratuito
   alcanza para este ejercicio).
2. Un proyecto de GCP creado — anota su `PROJECT_ID`.
3. Habilitar las APIs necesarias:
   ```bash
   gcloud services enable aiplatform.googleapis.com run.googleapis.com
   ```
4. Autenticación local (para la Parte 3.2):
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project TU_PROJECT_ID
   ```
