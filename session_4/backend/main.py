"""
Sesión 4 — Backend FastAPI: Demo Guiada de Llamada API con Buenas Prácticas
===============================================================================

Expone un único endpoint de demostración (/demo/completar) que aplica,
en un solo lugar, todo el contenido de la sesión:
  - Estructura de la llamada (system + user + parámetros)
  - Perfiles de parámetros (preciso / balanceado / creativo)
  - Seguridad básica (validación de input, límites, rate limiting)
  - Control de alucinación opcional (grounding con contexto fijo de demo)
  - Heurística de señales de alerta sobre la respuesta

Seguridad: todas las credenciales se leen con os.getenv() desde .env.
Nunca hardcodear API keys en el código.

Ejecutar:
    uvicorn main:app --reload --port 8000
"""

import os
import re
import time
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    RATE_LIMIT_DISPONIBLE = True
except ImportError:
    RATE_LIMIT_DISPONIBLE = False

load_dotenv()

app = FastAPI(
    title="Sesión 4 — Demo Guiada de Llamada API",
    description="Backend educativo BSG Institute — Fundamentos de Arquitectura LLM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rate limiting básico (Seguridad, Tema 1) ────────────────────────────────
if RATE_LIMIT_DISPONIBLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─── Parámetros y contexto de la demo ────────────────────────────────────────

PERFILES_PARAMETROS = {
    "preciso": {"temperature": 0.0, "max_tokens": 200},
    "balanceado": {"temperature": 0.7, "max_tokens": 300},
    "creativo": {"temperature": 1.2, "max_tokens": 500},
}

SYSTEM_PROMPT_BASE = (
    "Eres un asistente de soporte técnico de Tienda Andina. "
    "Responde de forma breve, profesional y en español."
)

SYSTEM_PROMPT_GROUNDING = (
    "Responde ÚNICAMENTE con información del contexto proporcionado. "
    "Si la respuesta no está en el contexto, dilo explícitamente — no inventes información."
)

CONTEXTO_DEMO = (
    "Política de devoluciones de Tienda Andina: 30 días desde la compra, "
    "con boleta o factura original, producto sin uso y en su empaque original. "
    "Los productos de higiene personal no tienen devolución."
)

MAX_PROMPT_LENGTH = 4000


# ─── Modelos Pydantic ─────────────────────────────────────────────────────────

class SolicitudDemo(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LENGTH)
    perfil_parametros: Literal["preciso", "balanceado", "creativo"] = "preciso"
    usar_grounding: bool = True


class RespuestaDemo(BaseModel):
    respuesta: str
    latencia_seg: float
    simulado: bool
    grounding_activo: bool
    perfil_usado: str
    senales_alerta: list[str] = []
    error: Optional[str] = None


# ─── Seguridad básica (Tema 1) ───────────────────────────────────────────────

def sanitizar_input(texto: str) -> str:
    """Trunca inputs excesivamente largos — evita costos inesperados."""
    return texto[:MAX_PROMPT_LENGTH]


def detectar_senales_alerta(respuesta: str, grounding_activo: bool) -> list[str]:
    """Heurística simple de posible alucinación — no reemplaza revisión humana."""
    senales = []
    if re.search(r'\b\d{1,3}%\b', respuesta) and "contexto" not in respuesta.lower():
        senales.append("Contiene una estadística específica sin referencia a fuente")
    if re.search(r'\b(siempre|nunca|garantizado)\b', respuesta, re.IGNORECASE):
        senales.append("Usa lenguaje absoluto ('siempre', 'nunca', 'garantizado')")
    if not grounding_activo:
        senales.append("Grounding desactivado — la respuesta puede no estar verificada contra una fuente")
    return senales


# ─── Lógica de la llamada (Temas 1, 2 y 3 combinados) ────────────────────────

def respuesta_simulada(prompt: str, grounding: bool) -> str:
    if grounding and "internacional" in prompt.lower():
        return (
            "[MODO_SIMULADO — CON grounding] El contexto no menciona compras internacionales "
            "específicamente. Solo puedo confirmar la política general: 30 días, con boleta, "
            "producto sin uso. Te recomiendo confirmar el caso internacional con soporte."
        )
    if not grounding and "internacional" in prompt.lower():
        return (
            "[MODO_SIMULADO — SIN grounding, ejemplo de alto riesgo] Para compras internacionales "
            "ofrecemos devoluciones en 45 días con envío gratuito. ← esto es un ejemplo de dato inventado."
        )
    return f"[MODO_SIMULADO] Respuesta simulada para: '{prompt[:60]}...'"


async def ejecutar_completado(prompt: str, perfil: str, grounding: bool) -> tuple[str, float, bool]:
    inicio = time.time()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return respuesta_simulada(prompt, grounding), time.time() - inicio, True

    from openai import AsyncOpenAI
    cliente = AsyncOpenAI(api_key=api_key)
    params = PERFILES_PARAMETROS[perfil]

    system_prompt = SYSTEM_PROMPT_BASE
    user_content = prompt
    if grounding:
        system_prompt = SYSTEM_PROMPT_GROUNDING
        user_content = f"Contexto:\n{CONTEXTO_DEMO}\n\nPregunta: {prompt}"

    respuesta = await cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=params["temperature"],
        max_tokens=params["max_tokens"],
    )
    return respuesta.choices[0].message.content, time.time() - inicio, False


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "servicio": "Sesión 4 — Demo Guiada de Llamada API"}


@app.get("/perfiles")
async def listar_perfiles():
    """Expone los perfiles de parámetros disponibles (Tema 1)."""
    return PERFILES_PARAMETROS


demo_completar_decorador = (
    limiter.limit("10/minute") if RATE_LIMIT_DISPONIBLE else (lambda f: f)
)


@app.post("/demo/completar", response_model=RespuestaDemo)
@demo_completar_decorador
async def demo_completar(request: Request, solicitud: SolicitudDemo):
    """
    Endpoint de la demo guiada (ejemplos/05_demo_guiada_endpoint.py).
    Aplica sanitización de input, perfil de parámetros, grounding opcional,
    y heurística de señales de alerta — todo en una sola llamada.
    """
    prompt = sanitizar_input(solicitud.prompt)

    try:
        respuesta, latencia, simulado = await ejecutar_completado(
            prompt, solicitud.perfil_parametros, solicitud.usar_grounding
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al llamar al modelo: {e}")

    senales = detectar_senales_alerta(respuesta, solicitud.usar_grounding)

    return RespuestaDemo(
        respuesta=respuesta,
        latencia_seg=round(latencia, 3),
        simulado=simulado,
        grounding_activo=solicitud.usar_grounding,
        perfil_usado=solicitud.perfil_parametros,
        senales_alerta=senales,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)))
