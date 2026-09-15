"""
Sesión 3 — Backend FastAPI: Comparador Multi-Proveedor de Inferencia
========================================================================

Expone endpoints para comparar proveedores de inferencia LLM en paralelo:
OpenAI, Anthropic, Google (directo), Azure OpenAI, AWS Bedrock, Vertex AI
y Ollama (local). Cada proveedor cae a MODO_SIMULADO si no hay credenciales.

Seguridad: todas las credenciales se leen con os.getenv() desde .env.
Nunca hardcodear API keys en el código.

Ejecutar:
    uvicorn main:app --reload --port 8000
"""

import os
import time
import asyncio
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Sesión 3 — Comparador de Proveedores de Inferencia",
    description="Backend educativo BSG Institute — Fundamentos de Arquitectura LLM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


# ─── Modelos Pydantic ─────────────────────────────────────────────────────────

class SolicitudComparacion(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    proveedores: list[str] = Field(
        default=["openai", "anthropic", "google", "azure", "bedrock", "vertex", "ollama"]
    )


class ResultadoProveedor(BaseModel):
    proveedor: str
    respuesta: str
    latencia_seg: float
    simulado: bool
    costo_estimado_usd: Optional[float] = None
    error: Optional[str] = None


class RespuestaComparacion(BaseModel):
    prompt: str
    resultados: list[ResultadoProveedor]
    proveedor_mas_rapido: Optional[str] = None


class InfoProveedor(BaseModel):
    id: str
    nombre: str
    tipo: str
    configurado: bool


# ─── Catálogo de proveedores ──────────────────────────────────────────────────

def _configurado(*env_vars: str) -> bool:
    return all(os.getenv(v) for v in env_vars)


def obtener_catalogo_proveedores() -> list[InfoProveedor]:
    return [
        InfoProveedor(id="openai", nombre="OpenAI (GPT-4o-mini)", tipo="directo",
                      configurado=_configurado("OPENAI_API_KEY")),
        InfoProveedor(id="anthropic", nombre="Anthropic (Claude Haiku)", tipo="directo",
                      configurado=_configurado("ANTHROPIC_API_KEY")),
        InfoProveedor(id="google", nombre="Google AI Studio (Gemini Flash)", tipo="directo",
                      configurado=_configurado("GOOGLE_API_KEY")),
        InfoProveedor(id="azure", nombre="Azure OpenAI Service", tipo="hyperscaler",
                      configurado=_configurado("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY")),
        InfoProveedor(id="bedrock", nombre="AWS Bedrock (Claude)", tipo="hyperscaler",
                      configurado=_configurado("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")),
        InfoProveedor(id="vertex", nombre="Vertex AI / Gemini Enterprise Agent Platform", tipo="hyperscaler",
                      configurado=_configurado("GOOGLE_CLOUD_PROJECT")),
        InfoProveedor(id="ollama", nombre="Ollama (local)", tipo="self-hosted", configurado=True),
    ]


# ─── Llamadas por proveedor (todas async, con fallback simulado) ────────────

async def _simulado(nombre: str, inicio: float) -> ResultadoProveedor:
    await asyncio.sleep(0.15)  # simula latencia de red para que la demo se vea realista
    return ResultadoProveedor(
        proveedor=nombre,
        respuesta=f"[MODO_SIMULADO] Configura las credenciales de {nombre} en .env para ver una respuesta real.",
        latencia_seg=round(time.time() - inicio, 3),
        simulado=True,
    )


async def llamar_openai(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    if not os.getenv("OPENAI_API_KEY"):
        return await _simulado("OpenAI", inicio)
    try:
        from openai import AsyncOpenAI
        cliente = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = await cliente.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=200,
        )
        tokens = resp.usage.total_tokens if resp.usage else 0
        return ResultadoProveedor(
            proveedor="OpenAI", respuesta=resp.choices[0].message.content,
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
            costo_estimado_usd=round((tokens / 1_000_000) * 0.60, 6),
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="OpenAI", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_anthropic(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    if not os.getenv("ANTHROPIC_API_KEY"):
        return await _simulado("Anthropic", inicio)
    try:
        import anthropic
        cliente = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = await cliente.messages.create(
            model="claude-3-haiku-20240307", max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        tokens = resp.usage.input_tokens + resp.usage.output_tokens
        return ResultadoProveedor(
            proveedor="Anthropic", respuesta=resp.content[0].text,
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
            costo_estimado_usd=round((tokens / 1_000_000) * 0.75, 6),
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="Anthropic", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_google(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    if not os.getenv("GOOGLE_API_KEY"):
        return await _simulado("Google AI Studio", inicio)
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        modelo = genai.GenerativeModel("gemini-2.0-flash")
        resp = await asyncio.to_thread(modelo.generate_content, prompt)
        return ResultadoProveedor(
            proveedor="Google AI Studio", respuesta=resp.text,
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="Google AI Studio", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_azure(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not (endpoint and api_key):
        return await _simulado("Azure OpenAI", inicio)
    try:
        from openai import AsyncAzureOpenAI
        cliente = AsyncAzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version="2024-08-01-preview")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        resp = await cliente.chat.completions.create(
            model=deployment, messages=[{"role": "user", "content": prompt}], max_tokens=200,
        )
        return ResultadoProveedor(
            proveedor="Azure OpenAI", respuesta=resp.choices[0].message.content,
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="Azure OpenAI", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_bedrock(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        return await _simulado("AWS Bedrock", inicio)
    try:
        import boto3, json
        cliente = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        cuerpo = {"anthropic_version": "bedrock-2023-05-31", "max_tokens": 200,
                  "messages": [{"role": "user", "content": prompt}]}
        resp = await asyncio.to_thread(
            cliente.invoke_model, modelId="anthropic.claude-3-haiku-20240307-v1:0", body=json.dumps(cuerpo),
        )
        resultado = json.loads(resp["body"].read())
        return ResultadoProveedor(
            proveedor="AWS Bedrock", respuesta=resultado["content"][0]["text"],
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="AWS Bedrock", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_vertex(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return await _simulado("Vertex AI", inicio)
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=project_id, location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
        modelo = GenerativeModel("gemini-2.0-flash")
        resp = await asyncio.to_thread(modelo.generate_content, prompt)
        return ResultadoProveedor(
            proveedor="Vertex AI", respuesta=resp.text,
            latencia_seg=round(time.time() - inicio, 3), simulado=False,
        )
    except Exception as e:
        return ResultadoProveedor(proveedor="Vertex AI", respuesta="", latencia_seg=round(time.time() - inicio, 3),
                                   simulado=False, error=str(e))


async def llamar_ollama(prompt: str) -> ResultadoProveedor:
    inicio = time.time()
    try:
        async with httpx.AsyncClient(timeout=30.0) as cliente:
            tags = await cliente.get(f"{OLLAMA_HOST}/api/tags")
            modelos = [m["name"] for m in tags.json().get("models", [])]
            if not modelos:
                raise RuntimeError("Ollama sin modelos instalados — ejecuta: ollama pull llama3.2:3b")
            resp = await cliente.post(
                f"{OLLAMA_HOST}/api/chat",
                json={"model": modelos[0], "messages": [{"role": "user", "content": prompt}], "stream": False},
            )
            contenido = resp.json()["message"]["content"]
            return ResultadoProveedor(
                proveedor=f"Ollama ({modelos[0]})", respuesta=contenido,
                latencia_seg=round(time.time() - inicio, 3), simulado=False, costo_estimado_usd=0.0,
            )
    except Exception as e:
        return ResultadoProveedor(proveedor="Ollama (local)", respuesta="",
                                   latencia_seg=round(time.time() - inicio, 3), simulado=True,
                                   error=f"Ollama no disponible: {e}")


PROVEEDORES_FN = {
    "openai": llamar_openai,
    "anthropic": llamar_anthropic,
    "google": llamar_google,
    "azure": llamar_azure,
    "bedrock": llamar_bedrock,
    "vertex": llamar_vertex,
    "ollama": llamar_ollama,
}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "servicio": "Sesión 3 — Comparador de Proveedores"}


@app.get("/proveedores", response_model=list[InfoProveedor])
async def listar_proveedores():
    """Lista los proveedores disponibles y si tienen credenciales configuradas."""
    return obtener_catalogo_proveedores()


@app.post("/comparar", response_model=RespuestaComparacion)
async def comparar_proveedores(solicitud: SolicitudComparacion):
    """Envía el mismo prompt a todos los proveedores solicitados EN PARALELO."""
    tareas = []
    for pid in solicitud.proveedores:
        fn = PROVEEDORES_FN.get(pid)
        if fn is None:
            raise HTTPException(status_code=400, detail=f"Proveedor desconocido: {pid}")
        tareas.append(fn(solicitud.prompt))

    resultados = await asyncio.gather(*tareas)

    reales = [r for r in resultados if not r.simulado and not r.error]
    mas_rapido = min(reales, key=lambda r: r.latencia_seg).proveedor if reales else None

    return RespuestaComparacion(prompt=solicitud.prompt, resultados=resultados, proveedor_mas_rapido=mas_rapido)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)))
