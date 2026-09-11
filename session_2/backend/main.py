"""
Sesion 2 — Backend FastAPI: Comparador Multi-Modelo
====================================================
API que permite comparar respuestas de modelos propietarios
y open-source desde una unica interfaz REST.

Endpoints:
  GET  /                    Health check
  GET  /modelos             Lista todos los modelos disponibles
  POST /chat                Chat con un modelo especifico
  POST /comparar            Envia el mismo prompt a varios modelos
  GET  /modelos/locales     Modelos disponibles en Ollama

Ejecutar:
  uvicorn main:app --reload --port 8000
"""

import os
import time
import httpx
import asyncio
from typing import Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Configuracion
# ──────────────────────────────────────────────────────────────────────────────

OLLAMA_HOST       = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

MODELOS_CLOUD = {
    "gpt-4o-mini"         : {"proveedor": "openai",    "descripcion": "OpenAI GPT-4o Mini — rapido y economico"},
    "claude-3-haiku"      : {"proveedor": "anthropic", "descripcion": "Anthropic Claude 3 Haiku — ultra rapido"},
    "gpt-4o"              : {"proveedor": "openai",    "descripcion": "OpenAI GPT-4o — mayor capacidad"},
}

MODELOS_LOCALES_DEFAULT = [
    {"nombre": "llama3.2",  "descripcion": "Meta Llama 3.2 3B", "tipo": "local"},
    {"nombre": "phi3:mini", "descripcion": "Microsoft Phi-3 Mini", "tipo": "local"},
    {"nombre": "mistral",   "descripcion": "Mistral 7B",          "tipo": "local"},
]


# ──────────────────────────────────────────────────────────────────────────────
# Modelos Pydantic (request / response)
# ──────────────────────────────────────────────────────────────────────────────

class MensajeChat(BaseModel):
    rol      : str = Field(..., pattern="^(user|assistant|system)$")
    contenido: str

class SolicitudChat(BaseModel):
    modelo   : str
    mensajes : list[MensajeChat]
    sistema  : Optional[str] = "Eres un asistente experto. Responde en espanol."
    max_tokens: int = 300

class RespuestaChat(BaseModel):
    modelo    : str
    proveedor : str
    texto     : str
    tokens    : dict
    tiempo_ms : int
    error     : Optional[str] = None

class SolicitudComparacion(BaseModel):
    prompt  : str
    modelos : list[str] = Field(default=["llama3.2", "gpt-4o-mini"])
    sistema : Optional[str] = "Eres un asistente experto. Responde en espanol de forma concisa."

class RespuestaComparacion(BaseModel):
    prompt     : str
    resultados : list[RespuestaChat]
    tiempo_total_ms: int


# ──────────────────────────────────────────────────────────────────────────────
# App FastAPI
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "Comparador Multi-Modelo LLM",
    description = "Sesion 2 — API para comparar modelos propietarios y open-source",
    version     = "1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:5173", "http://localhost:3000"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers de llamada a modelos
# ──────────────────────────────────────────────────────────────────────────────

async def llamar_ollama(
    mensajes  : list[dict],
    modelo    : str,
    sistema   : str,
    max_tokens: int,
) -> RespuestaChat:
    """Llama a Ollama de forma asincrona."""
    inicio = time.time()

    msgs_completos = [{"role": "system", "content": sistema}]
    for m in mensajes:
        msgs_completos.append({"role": m["rol"], "content": m["contenido"]})

    try:
        async with httpx.AsyncClient(timeout=120) as cliente:
            resp = await cliente.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model"   : modelo,
                    "messages": msgs_completos,
                    "stream"  : False,
                    "options" : {"num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            datos = resp.json()

        tiempo_ms = int((time.time() - inicio) * 1000)
        return RespuestaChat(
            modelo    = modelo,
            proveedor = "ollama/local",
            texto     = datos["message"]["content"],
            tokens    = {
                "entrada": datos.get("prompt_eval_count", 0),
                "salida" : datos.get("eval_count", 0),
            },
            tiempo_ms = tiempo_ms,
        )
    except Exception as e:
        return RespuestaChat(
            modelo    = modelo,
            proveedor = "ollama/local",
            texto     = "",
            tokens    = {"entrada": 0, "salida": 0},
            tiempo_ms = int((time.time() - inicio) * 1000),
            error     = str(e),
        )


async def llamar_openai(
    mensajes  : list[dict],
    modelo    : str,
    sistema   : str,
    max_tokens: int,
) -> RespuestaChat:
    """Llama a OpenAI de forma asincrona."""
    if not OPENAI_API_KEY:
        return RespuestaChat(
            modelo="gpt-4o-mini", proveedor="openai", texto="",
            tokens={"entrada":0,"salida":0}, tiempo_ms=0,
            error="OPENAI_API_KEY no configurada",
        )
    inicio = time.time()
    try:
        from openai import AsyncOpenAI
        cliente = AsyncOpenAI(api_key=OPENAI_API_KEY)

        msgs_completos = [{"role": "system", "content": sistema}]
        for m in mensajes:
            msgs_completos.append({"role": m["rol"], "content": m["contenido"]})

        comp = await cliente.chat.completions.create(
            model      = modelo,
            messages   = msgs_completos,
            max_tokens = max_tokens,
        )
        tiempo_ms = int((time.time() - inicio) * 1000)
        return RespuestaChat(
            modelo    = modelo,
            proveedor = "openai",
            texto     = comp.choices[0].message.content,
            tokens    = {
                "entrada": comp.usage.prompt_tokens,
                "salida" : comp.usage.completion_tokens,
            },
            tiempo_ms = tiempo_ms,
        )
    except Exception as e:
        return RespuestaChat(
            modelo=modelo, proveedor="openai", texto="",
            tokens={"entrada":0,"salida":0}, tiempo_ms=0, error=str(e),
        )


async def llamar_anthropic(
    mensajes  : list[dict],
    modelo    : str,
    sistema   : str,
    max_tokens: int,
) -> RespuestaChat:
    """Llama a Anthropic de forma asincrona."""
    if not ANTHROPIC_API_KEY:
        return RespuestaChat(
            modelo=modelo, proveedor="anthropic", texto="",
            tokens={"entrada":0,"salida":0}, tiempo_ms=0,
            error="ANTHROPIC_API_KEY no configurada",
        )
    inicio = time.time()
    try:
        import anthropic
        cliente = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

        msgs_anthropic = [{"role": m["rol"], "content": m["contenido"]} for m in mensajes]
        modelo_real    = "claude-3-haiku-20240307" if "haiku" in modelo else modelo

        msg = await cliente.messages.create(
            model      = modelo_real,
            max_tokens = max_tokens,
            system     = sistema,
            messages   = msgs_anthropic,
        )
        tiempo_ms = int((time.time() - inicio) * 1000)
        return RespuestaChat(
            modelo    = modelo,
            proveedor = "anthropic",
            texto     = msg.content[0].text,
            tokens    = {
                "entrada": msg.usage.input_tokens,
                "salida" : msg.usage.output_tokens,
            },
            tiempo_ms = tiempo_ms,
        )
    except Exception as e:
        return RespuestaChat(
            modelo=modelo, proveedor="anthropic", texto="",
            tokens={"entrada":0,"salida":0}, tiempo_ms=0, error=str(e),
        )


async def llamar_modelo(sol: SolicitudChat) -> RespuestaChat:
    """Enruta la llamada al proveedor correcto."""
    modelo = sol.modelo.lower()

    if any(x in modelo for x in ["gpt", "o1", "o3"]):
        return await llamar_openai(
            [{"rol": m.rol, "contenido": m.contenido} for m in sol.mensajes],
            sol.modelo, sol.sistema, sol.max_tokens,
        )
    elif "claude" in modelo or "haiku" in modelo or "sonnet" in modelo:
        return await llamar_anthropic(
            [{"rol": m.rol, "contenido": m.contenido} for m in sol.mensajes],
            sol.modelo, sol.sistema, sol.max_tokens,
        )
    else:
        # Asumir Ollama para cualquier otro modelo
        return await llamar_ollama(
            [{"rol": m.rol, "contenido": m.contenido} for m in sol.mensajes],
            sol.modelo, sol.sistema, sol.max_tokens,
        )


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def health():
    return {
        "status"  : "ok",
        "servicio": "Comparador Multi-Modelo LLM",
        "version" : "1.0.0",
        "sesion"  : "Sesion 2 — Tipos de modelos",
    }


@app.get("/modelos")
async def listar_modelos():
    """Devuelve todos los modelos disponibles (cloud + local)."""
    cloud = [
        {
            "nombre"     : nombre,
            "tipo"       : "cloud",
            "proveedor"  : info["proveedor"],
            "descripcion": info["descripcion"],
            "disponible" : bool(OPENAI_API_KEY if "gpt" in nombre else ANTHROPIC_API_KEY),
        }
        for nombre, info in MODELOS_CLOUD.items()
    ]

    # Consultar Ollama
    locales = []
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            resp = await c.get(f"{OLLAMA_HOST}/api/tags")
            if resp.status_code == 200:
                for m in resp.json().get("models", []):
                    locales.append({
                        "nombre"     : m["name"],
                        "tipo"       : "local",
                        "proveedor"  : "ollama",
                        "descripcion": f"Modelo local — {m.get('size', 0) // 1024**3}GB",
                        "disponible" : True,
                    })
    except Exception:
        locales = [{**m, "disponible": False} for m in MODELOS_LOCALES_DEFAULT]

    return {"cloud": cloud, "local": locales, "total": len(cloud) + len(locales)}


@app.get("/modelos/locales")
async def modelos_ollama():
    """Lista modelos instalados en Ollama."""
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            resp = await c.get(f"{OLLAMA_HOST}/api/tags")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible: {e}")


@app.post("/chat", response_model=RespuestaChat)
async def chat(solicitud: SolicitudChat):
    """Envia un mensaje a un modelo especifico."""
    return await llamar_modelo(solicitud)


@app.post("/comparar", response_model=RespuestaComparacion)
async def comparar(solicitud: SolicitudComparacion):
    """
    Envia el mismo prompt a varios modelos en paralelo y devuelve
    todas las respuestas para comparacion side-by-side.
    """
    inicio = time.time()

    # Crear tareas paralelas para todos los modelos
    tareas = [
        llamar_modelo(SolicitudChat(
            modelo   = modelo,
            mensajes = [MensajeChat(rol="user", contenido=solicitud.prompt)],
            sistema  = solicitud.sistema,
        ))
        for modelo in solicitud.modelos
    ]

    # Ejecutar en paralelo (asyncio.gather)
    resultados = await asyncio.gather(*tareas)

    tiempo_total = int((time.time() - inicio) * 1000)
    return RespuestaComparacion(
        prompt          = solicitud.prompt,
        resultados      = list(resultados),
        tiempo_total_ms = tiempo_total,
    )
