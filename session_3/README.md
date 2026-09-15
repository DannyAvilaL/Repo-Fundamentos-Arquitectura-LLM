# Sesión 3 — Proveedores y Servicios de Inferencia

**Curso:** Fundamentos de Arquitectura LLM · BSG Institute
**Capítulo 2:** Ecosistema y Operación Básica de LLM
**Tema:** Proveedores y servicios de inferencia

## Contenido de la sesión

1. **Panorama de proveedores** — OpenAI, Anthropic, Meta, Mistral, Azure,
   Vertex AI (Gemini Enterprise Agent Platform), AWS Bedrock.
2. **Comparativa básica** — calidad, costo y disponibilidad.
3. **Términos clave de licenciamiento/uso** — qué revisar antes de integrar
   un proveedor en un proyecto empresarial.
4. **Práctica con agentes en Google Cloud** — crear un agente simple desde
   la consola (sin código) y con el Google ADK (con código), en la sección
   `vertex_ai_agent/`.

## Estructura del repositorio

```
session_3/
├── README.md                    ← este archivo
├── requirements.txt              ← dependencias generales de la sesión
├── docs/
│   └── SETUP.md                  ← guía de instalación paso a paso
├── ejemplos/
│   ├── 01_panorama_proveedores.py
│   ├── 02_comparativa_calidad_costo_disponibilidad.py
│   ├── 03_terminos_licenciamiento.py
│   ├── 04_ollama_servicio_inferencia_local.py
│   └── 05_benchmark_multiproveedor.py
├── backend/                      ← API FastAPI: comparador multi-proveedor
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                     ← UI React: comparador visual
│   └── src/App.jsx
└── vertex_ai_agent/               ← Ejercicio 3: agentes en Google Cloud
    ├── README.md
    ├── 01_agente_consola_gcp.md   ← Parte 3.1: consola (sin código)
    └── adk_agent/                 ← Parte 3.2: Google ADK (con código)
        ├── agent.py
        └── DEPLOY.md
```

## Tabla de proveedores cubiertos

| Proveedor | Tipo | Modelos destacados | Licenciamiento |
|---|---|---|---|
| OpenAI | Directo | GPT-4o, GPT-4o-mini, o1 | Términos de uso propios |
| Anthropic | Directo | Claude Opus/Sonnet/Haiku | Acceptable Use Policy propia |
| Google AI Studio | Directo | Gemini 2.0/2.5 Flash/Pro | Términos de Google AI Studio |
| Meta Llama | Directo / self-host | Llama 3.2, 3.3 | Llama Community License (open-weight) |
| Mistral AI | Directo | Mistral Large/Small, Mixtral | Apache 2.0 (modelos abiertos) + comercial |
| Azure OpenAI | Hyperscaler | GPT-4o, o1 | Enterprise Agreement Microsoft |
| Vertex AI / Gemini Enterprise Agent Platform | Hyperscaler | Gemini, Model Garden (Llama, Claude) | GCP ToS + términos por modelo |
| AWS Bedrock | Hyperscaler | Claude, Llama, Titan, Mistral | AWS Customer Agreement |
| Ollama | Self-hosted | Llama, Mistral, Phi, Qwen | Licencia del modelo subyacente |

> **Nota de nomenclatura:** Google renombró Vertex AI Agent Builder a
> **Gemini Enterprise Agent Platform** en mayo de 2026. Ambos nombres
> aparecen en este material según el contexto — la plataforma es la misma.

## Quick Start

```bash
# 1. Clonar y entrar al repo
cd session_3

# 2. Entorno Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar credenciales (opcional — todo funciona en MODO_SIMULADO sin ellas)
cp backend/.env.example backend/.env
# edita backend/.env con tus API keys

# 4. Ejecutar ejemplos standalone
python ejemplos/01_panorama_proveedores.py
python ejemplos/02_comparativa_calidad_costo_disponibilidad.py
python ejemplos/03_terminos_licenciamiento.py
python ejemplos/04_ollama_servicio_inferencia_local.py
python ejemplos/05_benchmark_multiproveedor.py

# 5. Backend + Frontend (comparador visual)
cd backend && uvicorn main:app --reload --port 8000 &
cd ../frontend && npm install && npm run dev

# 6. Ejercicio de agentes en Google Cloud
# Ver vertex_ai_agent/README.md para la guía completa (Partes 3.1 y 3.2)
```

Ver `docs/SETUP.md` para instrucciones detalladas de instalación de Ollama,
configuración de credenciales por proveedor, y troubleshooting común.

## Seguridad

Todas las credenciales se leen exclusivamente vía `os.getenv()` desde
archivos `.env` (nunca incluidos en el repositorio — ver `.gitignore`).
Ningún ejemplo de este repositorio hardcodea API keys.

## Casos de uso empresariales de este contenido

- Definir criterios objetivos de selección de proveedor para un RFP interno.
- Evaluar riesgo de vendor lock-in al elegir hyperscaler vs API directa.
- Preparar un checklist de compliance (DPA, residencia de datos) antes de
  una integración con datos sensibles.
- Prototipar rápidamente un agente conversacional sin escribir código,
  y luego migrarlo a una implementación con ADK cuando se necesite lógica
  de negocio personalizada.
