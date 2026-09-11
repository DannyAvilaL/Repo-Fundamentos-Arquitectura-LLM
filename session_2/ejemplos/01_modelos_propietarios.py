"""
Sesion 2 — Ejemplo 01: Modelos Propietarios
============================================
Familias principales de LLMs propietarios:
  - OpenAI   : GPT-4o, GPT-4o-mini
  - Anthropic: Claude 3.5 Sonnet, Claude 3 Haiku
  - Google   : Gemini 1.5 Pro, Gemini 1.5 Flash

Todos siguen el mismo patron de llamada:
  cliente -> modelo -> respuesta de texto

MODO_SIMULADO = True cuando no hay API keys configuradas.
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────────
# Configuracion
# ──────────────────────────────────────────────────────────────────────────────

OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY", "")
MODO_SIMULADO     = os.getenv("MODO_SIMULADO", "false").lower() == "true"

# Si no hay keys, activa modo simulado automaticamente
if not any([OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY]):
    MODO_SIMULADO = True
    print("INFO: No se encontraron API keys. Ejecutando en MODO_SIMULADO.\n")


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def separador(titulo: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def respuesta_simulada(proveedor: str, modelo: str, prompt: str) -> dict:
    """Devuelve una respuesta falsa para demostracion sin costo."""
    respuestas = {
        "openai": f"[GPT-4o simulado] Los LLMs son modelos de lenguaje entrenados con grandes corpus de texto usando arquitecturas Transformer. Tienen capacidades de comprension, generacion y razonamiento en lenguaje natural.",
        "anthropic": f"[Claude simulado] Los LLMs (Large Language Models) son sistemas de IA basados en Transformers entrenados con datos masivos para entender y generar texto con alta coherencia y precision.",
        "google": f"[Gemini simulado] Los modelos de lenguaje extensos utilizan mecanismos de atencion para procesar secuencias de texto y generar respuestas contextualmente relevantes.",
    }
    tiempo = round(0.5 + len(prompt) * 0.001, 3)
    tokens_entrada = len(prompt.split())
    tokens_salida  = 45
    return {
        "proveedor"    : proveedor,
        "modelo"       : modelo,
        "respuesta"    : respuestas.get(proveedor, "[Respuesta simulada]"),
        "tokens_entrada": tokens_entrada,
        "tokens_salida" : tokens_salida,
        "tiempo_s"     : tiempo,
        "simulado"     : True,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Clientes por proveedor
# ──────────────────────────────────────────────────────────────────────────────

def llamar_openai(prompt: str, modelo: str = "gpt-4o-mini") -> dict:
    """
    Llama a la API de OpenAI.
    Documentacion: https://platform.openai.com/docs/api-reference/chat
    """
    if MODO_SIMULADO or not OPENAI_API_KEY:
        return respuesta_simulada("openai", modelo, prompt)

    try:
        from openai import OpenAI

        cliente = OpenAI(api_key=OPENAI_API_KEY)
        inicio  = time.time()

        completion = cliente.chat.completions.create(
            model    = modelo,
            messages = [
                {"role": "system", "content": "Eres un experto en IA y LLMs. Responde en espanol de forma concisa."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens  = 200,
            temperature = 0.7,
        )

        tiempo = round(time.time() - inicio, 3)
        return {
            "proveedor"     : "openai",
            "modelo"        : modelo,
            "respuesta"     : completion.choices[0].message.content,
            "tokens_entrada": completion.usage.prompt_tokens,
            "tokens_salida" : completion.usage.completion_tokens,
            "tiempo_s"      : tiempo,
            "simulado"      : False,
        }
    except Exception as e:
        print(f"  ERROR OpenAI: {e}")
        return respuesta_simulada("openai", modelo, prompt)


def llamar_anthropic(prompt: str, modelo: str = "claude-3-haiku-20240307") -> dict:
    """
    Llama a la API de Anthropic (Claude).
    Documentacion: https://docs.anthropic.com/en/api/messages
    """
    if MODO_SIMULADO or not ANTHROPIC_API_KEY:
        return respuesta_simulada("anthropic", modelo, prompt)

    try:
        import anthropic

        cliente = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        inicio  = time.time()

        mensaje = cliente.messages.create(
            model      = modelo,
            max_tokens = 200,
            system     = "Eres un experto en IA y LLMs. Responde en espanol de forma concisa.",
            messages   = [{"role": "user", "content": prompt}],
        )

        tiempo = round(time.time() - inicio, 3)
        return {
            "proveedor"     : "anthropic",
            "modelo"        : modelo,
            "respuesta"     : mensaje.content[0].text,
            "tokens_entrada": mensaje.usage.input_tokens,
            "tokens_salida" : mensaje.usage.output_tokens,
            "tiempo_s"      : tiempo,
            "simulado"      : False,
        }
    except Exception as e:
        print(f"  ERROR Anthropic: {e}")
        return respuesta_simulada("anthropic", modelo, prompt)


def llamar_google(prompt: str, modelo: str = "gemini-1.5-flash") -> dict:
    """
    Llama a la API de Google Gemini.
    Documentacion: https://ai.google.dev/api/generate-content
    """
    if MODO_SIMULADO or not GOOGLE_API_KEY:
        return respuesta_simulada("google", modelo, prompt)

    try:
        import google.generativeai as genai

        genai.configure(api_key=GOOGLE_API_KEY)
        modelo_obj = genai.GenerativeModel(modelo)
        inicio     = time.time()

        respuesta = modelo_obj.generate_content(
            f"Eres un experto en IA y LLMs. Responde en espanol de forma concisa.\n\n{prompt}",
            generation_config=genai.GenerationConfig(max_output_tokens=200, temperature=0.7),
        )

        tiempo = round(time.time() - inicio, 3)
        return {
            "proveedor"     : "google",
            "modelo"        : modelo,
            "respuesta"     : respuesta.text,
            "tokens_entrada": len(prompt.split()),    # Google no siempre expone esto
            "tokens_salida" : len(respuesta.text.split()),
            "tiempo_s"      : tiempo,
            "simulado"      : False,
        }
    except Exception as e:
        print(f"  ERROR Google: {e}")
        return respuesta_simulada("google", modelo, prompt)


def mostrar_resultado(resultado: dict) -> None:
    sim = " [SIMULADO]" if resultado.get("simulado") else ""
    print(f"\n  Proveedor : {resultado['proveedor'].upper()}{sim}")
    print(f"  Modelo    : {resultado['modelo']}")
    print(f"  Respuesta : {resultado['respuesta'][:200]}...")
    print(f"  Tokens    : {resultado['tokens_entrada']} entrada / {resultado['tokens_salida']} salida")
    print(f"  Tiempo    : {resultado['tiempo_s']}s")


# ──────────────────────────────────────────────────────────────────────────────
# Demo principal
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSESION 2 — EJEMPLO 01: MODELOS PROPIETARIOS")
    print("Comparando OpenAI · Anthropic · Google")

    prompt = "Explica en 3 oraciones que es un LLM y para que sirve en empresas."

    # ── Familia OpenAI ────────────────────────────────────────────────────────
    separador("OpenAI — Familia GPT")
    print("""
  Modelos disponibles:
  - gpt-4o         : El mas capaz, multimodal (texto + imagen)
  - gpt-4o-mini    : Economico, rapido, ideal para produccion
  - o1-preview     : Razonamiento avanzado (cadena de pensamiento)
  - gpt-3.5-turbo  : Legacy, muy economico
    """)

    # Modelos economicos para demo
    for modelo in ["gpt-4o-mini"]:
        resultado = llamar_openai(prompt, modelo)
        mostrar_resultado(resultado)

    # ── Familia Anthropic ─────────────────────────────────────────────────────
    separador("Anthropic — Familia Claude")
    print("""
  Modelos disponibles:
  - claude-3-5-sonnet-20241022  : El mas inteligente de Claude
  - claude-3-5-haiku-20241022   : Rapido y economico
  - claude-3-opus-20240229      : Maximo razonamiento (mas caro)
  - claude-3-haiku-20240307     : Ultra rapido, bajo costo

  Ventaja clave: ventana de contexto de 200K tokens
    """)

    for modelo in ["claude-3-haiku-20240307"]:
        resultado = llamar_anthropic(prompt, modelo)
        mostrar_resultado(resultado)

    # ── Familia Google ────────────────────────────────────────────────────────
    separador("Google — Familia Gemini")
    print("""
  Modelos disponibles:
  - gemini-1.5-pro   : Contexto 1 MILLON de tokens, multimodal
  - gemini-1.5-flash : Rapido y economico
  - gemini-2.0-flash : Ultima generacion (diciembre 2024)

  Ventaja clave: 1M tokens de contexto = documentos enteros
    """)

    for modelo in ["gemini-1.5-flash"]:
        resultado = llamar_google(prompt, modelo)
        mostrar_resultado(resultado)

    # ── Resumen de precios ────────────────────────────────────────────────────
    separador("Tabla Comparativa de Precios (por millon de tokens)")
    print("""
  Modelo                      Input      Output
  ─────────────────────────────────────────────
  GPT-4o                      $2.50      $10.00
  GPT-4o-mini                 $0.15       $0.60
  Claude 3.5 Sonnet           $3.00      $15.00
  Claude 3 Haiku              $0.25       $1.25
  Gemini 1.5 Pro              $1.25       $5.00
  Gemini 1.5 Flash            $0.075      $0.30

  Nota: Precios aproximados. Verificar en sitios oficiales.
  1 token ≈ 0.75 palabras en ingles / 0.6 en espanol
    """)


if __name__ == "__main__":
    main()
