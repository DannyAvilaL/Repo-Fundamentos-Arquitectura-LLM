# Sesión 2 — Tipos de Modelos y Escenarios de Aplicación

**Curso:** Fundamentos de Arquitectura LLM  
**Capítulo:** 1 — Conceptos Fundamentales de LLM  
**Duración:** 3 horas  
**Nivel:** Intermedio — profesionales de TI y desarrollo de software

---

## Objetivos de Aprendizaje

Al finalizar esta sesión el participante podrá:

- Distinguir entre modelos **propietarios** (OpenAI, Anthropic, Google) y **open-source** (Llama, Mistral, Phi, Qwen)
- Evaluar los criterios clave para elegir entre **API gestionada** y **self-hosted** con Ollama
- Identificar los **casos de uso empresariales** más comunes para LLMs
- Ejecutar un modelo localmente con Ollama y comparar su respuesta con APIs en la nube

---

## Estructura del Repositorio

```
session_2/
├── README.md                    ← Este archivo
├── ejemplos/
│   ├── 01_modelos_propietarios.py   ← OpenAI, Anthropic, Google APIs
│   ├── 02_modelos_opensource.py     ← Ollama + Llama/Mistral/Phi local
│   ├── 03_comparacion_modelos.py    ← Benchmark side-by-side
│   ├── 04_casos_uso_empresarial.py  ← Clasificacion, resumen, extraccion
│   └── 05_api_vs_selfhosted.py      ← Analisis de costos y latencia
├── backend/
│   └── main.py                  ← FastAPI: proxy multi-modelo
├── frontend/
│   ├── src/App.jsx              ← React: comparador de modelos
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
└── docs/
    └── SETUP.md                 ← Guia de instalacion completa
```

---

## Inicio Rapido

### 1. Instalar dependencias Python

```bash
cd session_2
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp ../.env.example .env
# Edita .env con tus API keys
```

### 3. Instalar y levantar Ollama (para modelos locales)

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows: descarga desde https://ollama.com/download

# Descargar modelos para la sesion
ollama pull llama3.2          # 2GB — recomendado
ollama pull mistral           # 4GB — opcional
ollama pull phi3:mini         # 2.3GB — ligero

# Verificar que Ollama esta corriendo
ollama serve                  # si no inicio automaticamente
curl http://localhost:11434/api/tags
```

### 4. Ejecutar ejemplos

```bash
# Modelos propietarios (requiere API keys en .env)
python ejemplos/01_modelos_propietarios.py

# Modelos open-source local (requiere Ollama corriendo)
python ejemplos/02_modelos_opensource.py

# Comparacion entre modelos
python ejemplos/03_comparacion_modelos.py

# Casos de uso empresariales
python ejemplos/04_casos_uso_empresarial.py

# Analisis API vs self-hosted
python ejemplos/05_api_vs_selfhosted.py
```

### 5. Levantar el demo full-stack

```bash
# Terminal 1 — Backend FastAPI
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend React
cd frontend
npm install
npm run dev
# Abrir http://localhost:5173
```

---

## Familias de Modelos Cubiertos

### Propietarios (API Gestionada)

| Proveedor | Modelo | Contexto | Precio Input |
|-----------|--------|----------|--------------|
| OpenAI | GPT-4o | 128K tokens | $2.50/MTok |
| OpenAI | GPT-4o-mini | 128K tokens | $0.15/MTok |
| Anthropic | Claude 3.5 Sonnet | 200K tokens | $3.00/MTok |
| Anthropic | Claude 3 Haiku | 200K tokens | $0.25/MTok |
| Google | Gemini 1.5 Pro | 1M tokens | $1.25/MTok |
| Google | Gemini 1.5 Flash | 1M tokens | $0.075/MTok |

### Open-Source (Self-Hosted con Ollama)

| Modelo | Familia | Parametros | RAM minima |
|--------|---------|------------|------------|
| llama3.2 | Meta Llama | 3B | 4GB |
| llama3.1 | Meta Llama | 8B | 8GB |
| mistral | Mistral AI | 7B | 8GB |
| phi3:mini | Microsoft Phi | 3.8B | 4GB |
| qwen2.5 | Alibaba Qwen | 7B | 8GB |
| gemma2 | Google Gemma | 9B | 10GB |

---

## Casos de Uso Empresariales

1. **Clasificacion de tickets de soporte** — Categorizar y priorizar solicitudes entrantes
2. **Resumen de documentos legales** — Extraer puntos clave de contratos
3. **Extraccion de datos estructurados** — JSON desde texto libre
4. **Asistente de codigo** — Generacion y revision de codigo
5. **Analisis de sentimiento** — Feedback de clientes a escala
6. **Chatbot RAG corporativo** — Q&A sobre documentacion interna

---

## Recursos Adicionales

- [Ollama Models Library](https://ollama.com/library)
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic Claude Models](https://www.anthropic.com/claude)
- [Google AI Studio](https://aistudio.google.com)
- [Open LLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard)
- [LM Studio](https://lmstudio.ai) — alternativa grafica a Ollama
