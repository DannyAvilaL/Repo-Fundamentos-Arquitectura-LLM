"""
Sesion 2 — Ejemplo 03: Comparacion de Modelos
==============================================
Benchmark side-by-side entre modelos propietarios y open-source
para las mismas tareas empresariales.

Metricas evaluadas:
  - Calidad de respuesta
  - Velocidad (tokens/segundo)
  - Costo estimado por 1000 llamadas
  - Ventana de contexto disponible

Ejecuta con Ollama corriendo para ver comparacion real.
"""

import os
import time
import httpx
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()

OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODO_SIMULADO = os.getenv("MODO_SIMULADO", "false").lower() == "true"


# ──────────────────────────────────────────────────────────────────────────────
# Definicion de modelos a comparar
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DefinicionModelo:
    nombre      : str
    proveedor   : str
    tipo        : str          # "cloud" | "local"
    contexto_k  : int          # ventana de contexto en miles de tokens
    precio_input: float        # USD por millon de tokens (0 si local)
    precio_output: float
    descripcion : str


MODELOS = [
    DefinicionModelo("gpt-4o-mini",          "OpenAI",    "cloud", 128,  0.15,  0.60, "Economico y rapido — ideal produccion"),
    DefinicionModelo("claude-3-haiku",        "Anthropic", "cloud", 200,  0.25,  1.25, "Ultra rapido, bajo costo, 200K contexto"),
    DefinicionModelo("gemini-1.5-flash",      "Google",    "cloud", 1000, 0.075, 0.30, "El mas economico, 1M contexto"),
    DefinicionModelo("llama3.2",              "Meta",      "local", 128,  0.0,   0.0,  "Open-source, sin costo, 3B params"),
    DefinicionModelo("phi3:mini",             "Microsoft", "local", 128,  0.0,   0.0,  "Ultra eficiente, 3.8B params"),
    DefinicionModelo("mistral",               "Mistral",   "local", 32,   0.0,   0.0,  "7B, excelente calidad instruccion"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Cliente unificado
# ──────────────────────────────────────────────────────────────────────────────

def llamar_modelo(prompt: str, modelo: DefinicionModelo) -> dict:
    """Llama a cualquier modelo con una interfaz unificada."""

    if MODO_SIMULADO:
        # Simulacion con datos representativos
        datos_simulados = {
            "gpt-4o-mini"    : {"tiempo": 0.8, "tokens": 45, "calidad": 8.5},
            "claude-3-haiku" : {"tiempo": 0.6, "tokens": 42, "calidad": 8.8},
            "gemini-1.5-flash":{"tiempo": 0.7, "tokens": 40, "calidad": 8.2},
            "llama3.2"       : {"tiempo": 2.1, "tokens": 38, "calidad": 7.2},
            "phi3:mini"      : {"tiempo": 1.8, "tokens": 35, "calidad": 7.0},
            "mistral"        : {"tiempo": 2.5, "tokens": 41, "calidad": 7.8},
        }
        d = datos_simulados.get(modelo.nombre, {"tiempo": 1.5, "tokens": 40, "calidad": 7.5})
        texto = f"[{modelo.nombre} simulado] Respuesta de ejemplo para la tarea: {prompt[:50]}..."
        return {
            "modelo"   : modelo.nombre,
            "tipo"     : modelo.tipo,
            "texto"    : texto,
            "tiempo_s" : d["tiempo"],
            "tokens_s" : d["tokens"],
            "error"    : None,
            "simulado" : True,
        }

    if modelo.tipo == "local":
        return _llamar_ollama(prompt, modelo)
    else:
        return _llamar_cloud(prompt, modelo)


def _llamar_ollama(prompt: str, modelo: DefinicionModelo) -> dict:
    """Llamada a Ollama para modelos locales."""
    payload = {
        "model"   : modelo.nombre,
        "messages": [
            {"role": "system", "content": "Responde en espanol, de forma concisa y precisa."},
            {"role": "user",   "content": prompt},
        ],
        "stream" : False,
        "options": {"num_predict": 200},
    }
    try:
        inicio    = time.time()
        resp      = httpx.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=120)
        tiempo    = round(time.time() - inicio, 3)
        datos     = resp.json()
        tokens_s  = datos.get("eval_count", 0)
        return {
            "modelo"  : modelo.nombre,
            "tipo"    : "local",
            "texto"   : datos["message"]["content"],
            "tiempo_s": tiempo,
            "tokens_s": round(tokens_s / tiempo, 1) if tiempo > 0 else 0,
            "error"   : None,
            "simulado": False,
        }
    except Exception as e:
        return {"modelo": modelo.nombre, "tipo": "local", "texto": "", "tiempo_s": 0, "tokens_s": 0, "error": str(e), "simulado": True}


def _llamar_cloud(prompt: str, modelo: DefinicionModelo) -> dict:
    """Llamada a modelos en la nube via SDK."""
    try:
        inicio = time.time()

        if modelo.proveedor == "OpenAI":
            from openai import OpenAI
            cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            comp    = cliente.chat.completions.create(
                model    = modelo.nombre,
                messages = [
                    {"role": "system", "content": "Responde en espanol, conciso."},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens = 200,
            )
            texto    = comp.choices[0].message.content
            tokens_s = comp.usage.completion_tokens

        elif modelo.proveedor == "Anthropic":
            import anthropic
            cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            msg     = cliente.messages.create(
                model      = "claude-3-haiku-20240307",
                max_tokens = 200,
                system     = "Responde en espanol, conciso.",
                messages   = [{"role": "user", "content": prompt}],
            )
            texto    = msg.content[0].text
            tokens_s = msg.usage.output_tokens

        elif modelo.proveedor == "Google":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            m_obj    = genai.GenerativeModel(modelo.nombre)
            resp     = m_obj.generate_content(prompt)
            texto    = resp.text
            tokens_s = len(texto.split())

        else:
            raise ValueError(f"Proveedor desconocido: {modelo.proveedor}")

        tiempo = round(time.time() - inicio, 3)
        return {
            "modelo"  : modelo.nombre,
            "tipo"    : "cloud",
            "texto"   : texto,
            "tiempo_s": tiempo,
            "tokens_s": round(tokens_s / tiempo, 1) if tiempo > 0 else 0,
            "error"   : None,
            "simulado": False,
        }
    except Exception as e:
        return {"modelo": modelo.nombre, "tipo": "cloud", "texto": "", "tiempo_s": 0, "tokens_s": 0, "error": str(e), "simulado": True}


# ──────────────────────────────────────────────────────────────────────────────
# Analisis de costos
# ──────────────────────────────────────────────────────────────────────────────

def calcular_costo_mensual(
    modelo      : DefinicionModelo,
    llamadas_dia: int = 1000,
    tokens_prom : int = 500,
) -> dict:
    """
    Calcula el costo mensual estimado para un volumen de uso dado.

    Parametros tipicos empresariales:
      - Chatbot soporte: 1000 conversaciones/dia, 500 tokens promedio
      - Analisis docs  : 200 documentos/dia,     2000 tokens promedio
    """
    if modelo.tipo == "local":
        costo_mensual = 0.0
        infraestructura = "~$7-50/mes (servidor o PC con GPU)"
    else:
        tokens_mes    = llamadas_dia * 30 * tokens_prom
        costo_input   = (tokens_mes / 1_000_000) * modelo.precio_input
        costo_output  = (tokens_mes / 1_000_000) * modelo.precio_output
        costo_mensual = round(costo_input + costo_output, 2)
        infraestructura = "Incluida (sin infraestructura propia)"

    return {
        "modelo"         : modelo.nombre,
        "tipo"           : modelo.tipo,
        "costo_mensual"  : costo_mensual,
        "infraestructura": infraestructura,
        "llamadas_dia"   : llamadas_dia,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSESION 2 — EJEMPLO 03: COMPARACION DE MODELOS")

    tarea = "Resume en 3 puntos clave las ventajas de usar LLMs en atencion al cliente empresarial."

    # ── Benchmark de respuestas ───────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  BENCHMARK DE RESPUESTAS")
    print(f"  Tarea: {tarea}")
    print(f"{'='*60}")

    # Seleccionar modelos para el benchmark (1 por familia)
    modelos_bench = [m for m in MODELOS if m.nombre in ["gpt-4o-mini", "llama3.2", "phi3:mini"]]

    resultados = []
    for modelo in modelos_bench:
        print(f"\n  Consultando {modelo.nombre} ({modelo.tipo})...", end=" ", flush=True)
        res = llamar_modelo(tarea, modelo)
        resultados.append(res)
        sim = "[SIM]" if res.get("simulado") else ""
        print(f"OK {sim} ({res['tiempo_s']}s)")
        print(f"  {res['texto'][:200]}")

    # Tabla comparativa de velocidad
    print(f"\n{'─'*60}")
    print(f"  {'Modelo':<20} {'Tipo':<8} {'Tiempo':<10} {'Tok/s':<8}")
    print(f"{'─'*60}")
    for r in sorted(resultados, key=lambda x: x["tiempo_s"]):
        print(f"  {r['modelo']:<20} {r['tipo']:<8} {r['tiempo_s']:<10} {r['tokens_s']:<8}")

    # ── Analisis de costos ────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  ANALISIS DE COSTOS — 1000 llamadas/dia, 500 tokens promedio")
    print(f"{'='*60}")

    print(f"\n  {'Modelo':<22} {'Tipo':<8} {'Costo/mes':<14} {'Infraestructura'}")
    print(f"  {'─'*80}")
    for modelo in MODELOS:
        analisis = calcular_costo_mensual(modelo, llamadas_dia=1000, tokens_prom=500)
        costo    = f"${analisis['costo_mensual']:.2f}" if analisis["costo_mensual"] > 0 else "GRATIS"
        print(f"  {modelo.nombre:<22} {modelo.tipo:<8} {costo:<14} {analisis['infraestructura']}")

    # ── Tabla de capacidades ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  TABLA DE CAPACIDADES")
    print(f"{'='*60}")

    print(f"\n  {'Modelo':<22} {'Proveedor':<12} {'Contexto':<12} {'Precio Input':<15} {'Tipo'}")
    print(f"  {'─'*80}")
    for m in MODELOS:
        precio = f"${m.precio_input}/MTok" if m.precio_input > 0 else "Gratis"
        print(f"  {m.nombre:<22} {m.proveedor:<12} {m.contexto_k}K tokens{'':<4} {precio:<15} {m.tipo}")

    # ── Recomendaciones ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  GUIA DE SELECCION RAPIDA")
    print(f"{'='*60}")
    print("""
  USAR MODELO CLOUD (propietario) cuando:
    - Necesitas la mejor calidad disponible
    - El volumen es bajo (< 100K tokens/mes)
    - Debes procesar documentos muy largos (>32K tokens)
    - La latencia es critica (< 1s)
    - No tienes infraestructura GPU disponible

  USAR MODELO LOCAL (open-source + Ollama) cuando:
    - Los datos son confidenciales (no pueden salir de la empresa)
    - El volumen es alto (> 10M tokens/mes)
    - Quieres experimentar sin costo
    - Necesitas personalizar / fine-tunear el modelo
    - Tienes restricciones regulatorias (GDPR, HIPAA, etc.)

  HIBRIDO (lo mas comun en empresas):
    - Local para datos sensibles, tareas internas
    - Cloud para tareas que requieren maxima calidad
    """)


if __name__ == "__main__":
    main()
