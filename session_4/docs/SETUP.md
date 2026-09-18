# Guía de Instalación — Sesión 4

## 1. Requisitos previos

- Python 3.12
- Node.js 18+ (para el frontend React 18 + Vite 6)
- Git
- Ubuntu 24.04+ recomendado (también funciona en macOS/Windows con WSL2)
- (Opcional) Una API key de OpenAI o de Google AI Studio si quieres probar
  llamadas reales — todos los ejemplos funcionan sin ellas en MODO_SIMULADO.
- (Opcional) Cuenta de Google Cloud con facturación habilitada, solo para
  el ejercicio de agentes en `gcp_agent_platform/` (el tier gratuito
  alcanza para las tres partes).

## 2. Entorno Python

```bash
cd session_4
python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Configurar API keys (opcional)

Copia el archivo de ejemplo y complétalo. Puedes dejarlo en blanco — el
código detecta automáticamente la ausencia de la key y cae a MODO_SIMULADO:

```bash
cp backend/.env.example backend/.env
```

- OpenAI: crea una key en [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Google AI Studio (para `gcp_agent_platform/sin_adk_docker`): crea una
  key en [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

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

Luego ejecuta `python ejemplos/04_ollama_pruebas_locales.py` para practicar
las mismas técnicas de prompting y grounding contra un modelo 100% local —
sin costo y sin depender de conectividad a un proveedor externo.

## 5. Backend FastAPI

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Verifica en `http://localhost:8000/health`.

El backend incluye rate limiting (`slowapi`) en el endpoint principal —
si no está instalado, el servidor sigue funcionando sin ese límite
(revisa la consola al arrancar por un aviso al respecto).

## 6. Frontend React 18 + Vite 6

```bash
cd frontend
npm install
npm run dev
```
Abre `http://localhost:5173`. El proxy de Vite ya reenvía `/api/*` al
backend en `:8000`, quitando el prefijo `/api` automáticamente — si vas a
reutilizar este `vite.config.js` en otro proyecto, revisa esa línea de
`rewrite` antes de asumir que el backend usa el mismo prefijo.

## 7. Ejercicio de agentes en Google Cloud (Partes 3.1, 3.2 y 3.3)

Ver `gcp_agent_platform/README.md` — requiere una cuenta de Google Cloud
con facturación habilitada.

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
gcloud services enable aiplatform.googleapis.com run.googleapis.com \
    artifactregistry.googleapis.com cloudbuild.googleapis.com
```

Para la Parte 3.2 (ADK), instala adicionalmente:
```bash
cd gcp_agent_platform/adk_agent
pip install -r requirements.txt
```

Para la Parte 3.3 (sin ADK, vía Docker), necesitas Docker instalado
localmente además del SDK de `gcloud`:
```bash
cd gcp_agent_platform/sin_adk_docker
pip install -r requirements.txt   # para probar sin Docker primero
docker build -t agente-tienda-andina:local .
```

## Troubleshooting común

| Problema | Causa probable | Solución |
|---|---|---|
| `Connection refused` en Ollama | El servicio no está corriendo | `ollama serve` en otra terminal |
| `404 Not Found` al llamar `/api/...` desde el frontend | El backend no está corriendo, o el proxy de Vite no reescribe el prefijo | Verifica uvicorn en `:8000` y la línea `rewrite` en `vite.config.js` |
| `ModuleNotFoundError: slowapi` | Paquete opcional no instalado | `pip install slowapi` (el backend sigue funcionando sin rate limiting mientras tanto) |
| `403 Forbidden` en Vertex AI / Gemini | API no habilitada o falta autenticación | `gcloud services enable aiplatform.googleapis.com` + `gcloud auth application-default login` |
| `ModuleNotFoundError: google.adk` | Paquete no instalado | `pip install google-adk` |
| `docker: command not found` | Docker no instalado (solo afecta la Parte 3.3) | Instala Docker Desktop o Docker Engine para tu SO |
| Respuesta siempre en `MODO_SIMULADO` | Falta la API key correspondiente en `.env` | Completa `OPENAI_API_KEY` (backend) o `GOOGLE_API_KEY` (`sin_adk_docker`) |
