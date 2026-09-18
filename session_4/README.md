# Sesión 4 — Ejecución de Llamadas API con Buenas Prácticas

**Curso:** Fundamentos de Arquitectura LLM · BSG Institute
**Capítulo 2:** Ecosistema y Operación Básica de LLM
**Tema:** Ejecución de llamadas API con buenas prácticas

## Contenido de la sesión

1. **Estructura de una llamada API** — prompt, parámetros de generación
   (`temperature`, `max_tokens`, `top_p`, etc.) y seguridad básica (manejo
   de API keys, validación de input).
2. **Técnicas introductorias de prompting y control de alucinación** —
   zero-shot, few-shot, chain-of-thought, role prompting, structured
   output; y cómo reducir respuestas inventadas (grounding, citas, "no lo
   sé", temperature baja, auto-verificación).
3. **Demostración guiada con un endpoint** — un flujo end-to-end (backend
   FastAPI + frontend React) donde el estudiante arma una llamada real
   paso a paso: prompt → parámetros → grounding → envío → resultado.
4. **Práctica con agentes en Google Cloud (Agent Platform)** — crear el
   mismo agente simple de tres formas distintas: consola (sin código),
   Google ADK (con código) y sin ADK vía Docker — sección
   `gcp_agent_platform/`.

## Estructura del repositorio

```
session_4/
├── README.md                    ← este archivo
├── requirements.txt              ← dependencias generales de la sesión
├── docs/
│   └── SETUP.md                  ← guía de instalación paso a paso
├── ejemplos/
│   ├── 01_estructura_llamada_api.py
│   ├── 02_tecnicas_prompting.py
│   ├── 03_control_alucinacion.py
│   ├── 04_ollama_pruebas_locales.py
│   └── 05_demo_guiada_endpoint.py
├── backend/                      ← API FastAPI: endpoint de demo guiada
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                     ← UI React 18 + Vite 6: wizard de 5 pasos
│   └── src/App.jsx
└── gcp_agent_platform/            ← Ejercicio: agentes en Google Cloud (3 partes)
    ├── README.md
    ├── 01_agente_consola_gcp.md   ← Parte 3.1: consola (sin código)
    ├── adk_agent/                 ← Parte 3.2: Google ADK (con código)
    │   ├── agent.py
    │   └── DEPLOY.md
    └── sin_adk_docker/            ← Parte 3.3: sin ADK, vía Docker
        ├── main.py
        ├── Dockerfile
        └── DEPLOY.md
```

## Stack técnico de esta sesión

| Componente | Versión / herramienta |
|---|---|
| Python | 3.12 |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 + Vite 6 |
| Base de datos | Ninguna — no se necesita persistencia para estos ejercicios |
| Sistema operativo de referencia | Ubuntu 24.04+ (también funciona en macOS/Windows con WSL2) |
| Inferencia local | Ollama |

## Quick Start

```bash
# 1. Entrar al repo
cd session_4

# 2. Entorno Python 3.12
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar credenciales (opcional — todo funciona en MODO_SIMULADO sin ellas)
cp backend/.env.example backend/.env
# edita backend/.env con tu OPENAI_API_KEY (o deja en blanco para modo simulado)

# 4. Ejecutar ejemplos standalone
python ejemplos/01_estructura_llamada_api.py
python ejemplos/02_tecnicas_prompting.py
python ejemplos/03_control_alucinacion.py
python ejemplos/04_ollama_pruebas_locales.py
python ejemplos/05_demo_guiada_endpoint.py   # requiere el backend corriendo (paso 5)

# 5. Backend + Frontend (demo guiada)
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000 &
cd ../frontend && npm install && npm run dev

# 6. Ejercicio de agentes en Google Cloud
# Ver gcp_agent_platform/README.md para la guía completa (Partes 3.1, 3.2 y 3.3)
```

Ver `docs/SETUP.md` para instrucciones detalladas de instalación de Ollama,
configuración de credenciales, y troubleshooting común.

## Seguridad

Todas las credenciales se leen exclusivamente vía `os.getenv()` desde
archivos `.env` (nunca incluidos en el repositorio — ver `.gitignore`).
Ningún ejemplo de este repositorio hardcodea API keys. El backend incluye
además `slowapi` para *rate limiting* básico en el endpoint de demo,
sanitización de input y límites de longitud de prompt — las tres son
buenas prácticas de seguridad básica cubiertas en esta sesión.

## Casos de uso empresariales de este contenido

- Diseñar un checklist de seguridad mínimo antes de exponer cualquier
  endpoint que envuelva una llamada a un LLM (rate limiting, sanitización
  de input, nunca exponer la API key al cliente).
- Elegir el perfil de parámetros correcto según el caso de uso — no es lo
  mismo clasificar tickets de soporte (temperature baja) que generar
  copys creativos (temperature alta).
- Establecer un protocolo de verificación anti-alucinación antes de
  desplegar un asistente que responda con datos internos de la empresa.
- Decidir, para un agente conversacional interno, si conviene un
  prototipo rápido sin código, adoptar un framework de agentes (ADK), o
  integrar el modelo directamente en un backend ya existente.
