"""
Parte 3.3 — Agente simple SIN el ADK de Google, publicado vía Docker
====================================================================

Objetivo: el mismo asistente de FAQ de "Tienda Andina" (Partes 3.1 y 3.2),
pero sin adoptar el framework ADK — un servicio FastAPI plano que llama
directamente al modelo Gemini. Es exactamente el mismo patrón usado en
`backend/main.py` de esta sesión, aplicado a un caso de "agente": un
endpoint que arma un prompt con contexto (grounding), controla parámetros
y decide, con lógica simple de Python, cuándo escalar a un humano.

Cuándo elegir esto sobre el ADK (Parte 3.2):
- Ya tienes un backend propio y no quieres agregar una dependencia de
  framework nueva solo para un agente simple.
- Necesitas control total sobre el Dockerfile, el runtime y cómo se
  empaqueta el servicio (por ejemplo, para cumplir un estándar interno
  de contenedores de tu empresa).
- El agente no necesita orquestación multi-paso compleja — una función
  Python si/entonces alcanza.

Seguridad: la API key de Gemini se lee con os.getenv() desde una variable
de entorno / archivo .env — nunca hardcodeada en el código.
"""

import os
import re
import time
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

try:
    import google.generativeai as genai

    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    GEMINI_DISPONIBLE = bool(GEMINI_API_KEY)
    if GEMINI_DISPONIBLE:
        genai.configure(api_key=GEMINI_API_KEY)
except ImportError:
    GEMINI_DISPONIBLE = False


app = FastAPI(
    title="Agente Tienda Andina — Sin ADK",
    description="Parte 3.3: agente de FAQ construido con FastAPI puro, sin el ADK de Google.",
    version="1.0.0",
)

# ─── "Base de conocimiento" del agente (mismo contexto que Partes 3.1 y 3.2) ──

FAQ_TIENDA = {
    "horario": "Lunes a sábado, de 9:00 a 20:00. Domingos cerrado.",
    "pagos": "Aceptamos tarjeta de crédito/débito, transferencia bancaria y efectivo en tienda.",
    "devoluciones": "Hasta 30 días desde la compra, con boleta y producto sin uso.",
    "envios": "Envíos a todo el país en 2-5 días hábiles. Gratis en compras sobre $50.000.",
}

CONTEXTO_FAQ = "\n".join(f"- {tema.capitalize()}: {resp}" for tema, resp in FAQ_TIENDA.items())

SYSTEM_PROMPT = (
    "Eres el asistente virtual de 'Tienda Andina'. Responde ÚNICAMENTE con "
    "base en el siguiente contexto verificado. Si la pregunta no está "
    "cubierta por el contexto, responde exactamente: "
    "'No tengo esa información — un agente humano dará seguimiento por correo.' "
    "No inventes datos. Sé breve, amable y responde siempre en español.\n\n"
    f"Contexto verificado:\n{CONTEXTO_FAQ}"
)

# Mismo concepto de perfiles de parámetros que en backend/main.py —
# un agente de FAQ usa el perfil "preciso" por defecto.
PARAMETROS_AGENTE = {"temperature": 0.1, "max_output_tokens": 512, "top_p": 0.9}

PATRON_ESCALAMIENTO = re.compile(
    r"\b(reclamo|urgente|dañado|roto|queja|estafa|fraude)\b", re.IGNORECASE
)


class SolicitudAgente(BaseModel):
    mensaje: str


class RespuestaAgente(BaseModel):
    respuesta: str
    accion: Literal["responder_faq", "escalar_a_humano"]
    latencia_seg: float
    simulado: bool


def decidir_accion(mensaje: str) -> str:
    """Lógica simple de decisión — el reemplazo casero del 'tool routing'
    que el ADK hace automáticamente. Para un agente de una sola tool, un
    if/else explícito es más fácil de leer y depurar que adoptar un
    framework completo."""
    if PATRON_ESCALAMIENTO.search(mensaje):
        return "escalar_a_humano"
    return "responder_faq"


def respuesta_simulada(mensaje: str, accion: str) -> str:
    if accion == "escalar_a_humano":
        return (
            "Solicitud registrada para seguimiento humano. "
            "Te contactaremos por correo en 24h. [MODO_SIMULADO — sin GOOGLE_API_KEY]"
        )
    return (
        "[MODO_SIMULADO — sin GOOGLE_API_KEY] Esta es una respuesta simulada. "
        "Con una API key real, el modelo respondería usando el contexto de la FAQ."
    )


@app.get("/health")
async def health():
    return {"status": "ok", "gemini_configurado": GEMINI_DISPONIBLE}


@app.post("/agente/consultar", response_model=RespuestaAgente)
async def consultar_agente(solicitud: SolicitudAgente):
    inicio = time.perf_counter()
    accion = decidir_accion(solicitud.mensaje)

    if accion == "escalar_a_humano":
        respuesta = (
            "Entiendo que esto requiere atención personalizada. "
            "He registrado tu solicitud — un agente humano te contactará por correo en 24h."
        )
        return RespuestaAgente(
            respuesta=respuesta,
            accion=accion,
            latencia_seg=round(time.perf_counter() - inicio, 3),
            simulado=False,
        )

    if not GEMINI_DISPONIBLE:
        respuesta = respuesta_simulada(solicitud.mensaje, accion)
        return RespuestaAgente(
            respuesta=respuesta,
            accion=accion,
            latencia_seg=round(time.perf_counter() - inicio, 3),
            simulado=True,
        )

    modelo = genai.GenerativeModel(
        model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        system_instruction=SYSTEM_PROMPT,
    )
    resultado = modelo.generate_content(
        solicitud.mensaje,
        generation_config=PARAMETROS_AGENTE,
    )
    return RespuestaAgente(
        respuesta=resultado.text,
        accion=accion,
        latencia_seg=round(time.perf_counter() - inicio, 3),
        simulado=False,
    )


if __name__ == "__main__":
    import uvicorn

    puerto = int(os.getenv("PORT", "8080"))  # Cloud Run inyecta PORT
    uvicorn.run(app, host="0.0.0.0", port=puerto)
