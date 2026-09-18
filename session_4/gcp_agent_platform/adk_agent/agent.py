"""
Parte 3.2 — Agente simple con Google ADK (Agent Development Kit)
====================================================================

Objetivo: mismo caso de uso que la Parte 3.1 (asistente de FAQ de
"Tienda Andina"), pero construido en código con el ADK de Google —
control total sobre lógica, herramientas (tools), parámetros del modelo
y orquestación.

El ADK es agnóstico de dónde corre: puedes ejecutarlo localmente con
'adk web' o 'adk run', y desplegarlo a Cloud Run o Agent Runtime dentro
de Gemini Enterprise Agent Platform (ver DEPLOY.md).

Buenas prácticas de Sesión 4 aplicadas aquí:
- Seguridad: las credenciales de GCP se resuelven vía Application Default
  Credentials (gcloud auth application-default login) o variables de
  entorno GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION — nunca hardcodeadas.
- Parámetros: generate_content_config fija una temperature baja, apropiada
  para un agente de FAQ que no debe "creatividad" en sus respuestas.
- Control de alucinación: la instrucción exige admitir cuando no sabe algo
  y usar la tool de escalamiento en vez de inventar una respuesta.
"""

import os
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.genai import types


# ─── Herramientas (tools) del agente ──────────────────────────────────────────

FAQ_TIENDA = {
    "horario": "Lunes a sábado, de 9:00 a 20:00. Domingos cerrado.",
    "pagos": "Aceptamos tarjeta de crédito/débito, transferencia bancaria y efectivo en tienda.",
    "devoluciones": "Hasta 30 días desde la compra, con boleta y producto sin uso.",
    "envios": "Envíos a todo el país en 2-5 días hábiles. Gratis en compras sobre $50.000.",
}


def consultar_faq(tema: str) -> str:
    """Consulta la base de preguntas frecuentes de la tienda.

    Esta es la fuente de verdad del agente (equivalente al CONTEXTO_DEMO
    usado en el backend de la demo guiada) — el modelo NO debe responder
    sobre estos temas sin pasar por esta función.

    Args:
        tema: uno de 'horario', 'pagos', 'devoluciones', 'envios'.

    Returns:
        La respuesta de la FAQ, o un mensaje indicando que no existe esa entrada.
    """
    tema_normalizado = tema.lower().strip()
    if tema_normalizado in FAQ_TIENDA:
        return FAQ_TIENDA[tema_normalizado]
    return (
        f"No tengo información sobre '{tema}'. Temas disponibles: "
        f"{', '.join(FAQ_TIENDA.keys())}. Un agente humano puede ayudarte con esto."
    )


def escalar_a_humano(motivo: str) -> str:
    """Registra una solicitud de escalamiento a un agente humano.

    El agente debe llamar a esta tool en vez de intentar responder algo
    que no está en la FAQ — es la implementación en código de la técnica
    "permitir decir 'no lo sé'" de ejemplos/03_control_alucinacion.py.

    Args:
        motivo: breve descripción de por qué el cliente necesita un humano.

    Returns:
        Confirmación del escalamiento (en este demo, simulado — en producción
        esto podría crear un ticket en un sistema de soporte real).
    """
    # En producción: aquí iría una llamada a un sistema de tickets (Zendesk, etc.)
    return f"Solicitud registrada para seguimiento humano. Motivo: {motivo}. Te contactaremos por correo en 24h."


herramienta_faq = FunctionTool(func=consultar_faq)
herramienta_escalamiento = FunctionTool(func=escalar_a_humano)


# ─── Parámetros de la llamada (mismo concepto que PERFILES_PARAMETROS) ───────
# Un agente de FAQ necesita respuestas consistentes y poco "creativas":
# usamos el equivalente al perfil "preciso" de la Sesión 4.

CONFIG_GENERACION = types.GenerateContentConfig(
    temperature=0.1,
    max_output_tokens=512,
    top_p=0.9,
)


# ─── Definición del agente ────────────────────────────────────────────────────

root_agent = Agent(
    name="asistente_tienda_andina",
    model=os.getenv("ADK_MODEL", "gemini-2.0-flash"),
    description="Asistente virtual de FAQ para Tienda Andina",
    instruction=(
        "Eres el asistente virtual de 'Tienda Andina'. Responde preguntas sobre "
        "horarios, métodos de pago, devoluciones y envíos usando SIEMPRE la "
        "herramienta consultar_faq — nunca respondas estos temas de memoria. "
        "Si el cliente tiene un problema que la FAQ no resuelve (un reclamo, un "
        "pedido específico, algo urgente, o cualquier pregunta fuera de estos "
        "cuatro temas), usa la herramienta escalar_a_humano en vez de inventar "
        "una respuesta. Sé breve, amable y responde siempre en español."
    ),
    tools=[herramienta_faq, herramienta_escalamiento],
    generate_content_config=CONFIG_GENERACION,
)
