# Guía de Instalación — Sesión 3

## 1. Requisitos previos

- Python 3.10+
- Node.js 18+ (para el frontend React)
- Git
- (Opcional) Cuenta de Google Cloud, AWS o Azure si quieres probar los
  hyperscalers con credenciales reales — todos los ejemplos funcionan sin
  ellas en MODO_SIMULADO.

## 2. Entorno Python

```bash
cd session_3
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configurar API keys (opcional)

Copia el archivo de ejemplo y complétalo con las credenciales que tengas
disponibles. Puedes dejar en blanco las que no uses — el código detecta
automáticamente su ausencia y cae a MODO_SIMULADO:

```bash
cp backend/.env.example backend/.env
```

### 3.1 OpenAI / Anthropic / Google AI Studio (directos)

- OpenAI: crea una key en [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Anthropic: crea una key en [console.anthropic.com](https://console.anthropic.com) —
  **importante**: si tu organización usa múltiples workspaces, genera la key
  desde dentro de un workspace específico (no desde la key de administrador),
  o incluirás el error `anthropic-workspace-id` al hacer llamadas.
- Google AI Studio: crea una key en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 3.2 Azure OpenAI Service

1. Crea un recurso "Azure OpenAI" desde el portal de Azure.
2. Despliega un modelo (ej. `gpt-4o-mini`) — anota el nombre del *deployment*.
3. Copia el endpoint y la key desde "Keys and Endpoint" en el recurso.

### 3.3 AWS Bedrock

1. En la consola de AWS, ve a **Bedrock → Model access** y solicita acceso
   a los modelos que quieras usar (ej. Claude de Anthropic).
2. Crea credenciales de IAM con permiso `bedrock:InvokeModel`.
3. Configura `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION`.

### 3.4 Vertex AI / Gemini Enterprise Agent Platform

```bash
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```
Luego define `GOOGLE_CLOUD_PROJECT` y `GOOGLE_CLOUD_LOCATION` en tu `.env`.
No necesitas una API key — la autenticación es vía Application Default Credentials.

## 4. Instalar Ollama (inferencia local, recomendado para clase)

```bash
# Linux / macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: descargar instalador desde https://ollama.com/download

# Descargar un modelo liviano (~2GB)
ollama pull llama3.2:3b

# Iniciar el servicio (si no arranca automáticamente)
ollama serve
```

Verifica que esté corriendo:
```bash
curl http://localhost:11434/api/tags
```

## 5. Backend FastAPI

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Verifica en `http://localhost:8000/health`.

## 6. Frontend React

```bash
cd frontend
npm install
npm run dev
```
Abre `http://localhost:5173`.

## 7. Ejercicio de agentes en Google Cloud (Parte 3.1 y 3.2)

Ver `vertex_ai_agent/README.md` — requiere una cuenta de Google Cloud con
facturación habilitada (el tier gratuito cubre el ejercicio completo).

Para la Parte 3.2 (ADK), instala adicionalmente:
```bash
cd vertex_ai_agent/adk_agent
pip install -r requirements.txt
```

## Troubleshooting común

| Problema | Causa probable | Solución |
|---|---|---|
| `Connection refused` en Ollama | El servicio no está corriendo | `ollama serve` en otra terminal |
| `anthropic-workspace-id` header error | API key de administrador, no de workspace | Genera la key desde dentro de un workspace en console.anthropic.com |
| `403 Forbidden` en Vertex AI | API no habilitada o falta autenticación | `gcloud services enable aiplatform.googleapis.com` + `gcloud auth application-default login` |
| CORS error en el frontend | Backend no corriendo o puerto distinto | Verifica que uvicorn esté en :8000 y el proxy de Vite apunte ahí |
| `ModuleNotFoundError: google.adk` | Paquete no instalado | `pip install google-adk` |
