"""
Sesion 2 — Ejemplo 02: Modelos Open-Source con Ollama
======================================================
Familias open-source destacadas:
  - Meta Llama 3.x  : El mas usado del ecosistema open
  - Mistral / Mixtral: Excelente instruccion y contexto largo
  - Microsoft Phi-3  : Eficiente con pocos parametros
  - Alibaba Qwen 2.5 : Multilingue, fuerte en asiatico
  - Google Gemma 2   : Ligero y de alta calidad

Todos corren LOCALMENTE con Ollama — sin costo, sin nube, sin API key.

Prerequisito:
  ollama serve           (iniciar el servicio)
  ollama pull llama3.2   (descargar modelo)
"""

import os
import time
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "llama3.2")
MODO_SIMULADO = os.getenv("MODO_SIMULADO", "false").lower() == "true"


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def separador(titulo: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def verificar_ollama() -> bool:
    """Comprueba que Ollama esta corriendo y devuelve True/False."""
    try:
        respuesta = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        return respuesta.status_code == 200
    except Exception:
        return False


def listar_modelos_ollama() -> list[dict]:
    """Devuelve los modelos instalados en Ollama."""
    try:
        respuesta = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        datos     = respuesta.json()
        return datos.get("models", [])
    except Exception:
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Cliente Ollama
# ──────────────────────────────────────────────────────────────────────────────

def llamar_ollama(
    prompt    : str,
    modelo    : str = None,
    sistema   : str = "Eres un asistente experto. Responde en espanol de forma concisa.",
    max_tokens: int = 300,
) -> dict:
    """
    Llama al endpoint /api/chat de Ollama.

    Ollama expone dos APIs:
      POST /api/generate  — completado simple (un turno)
      POST /api/chat      — chat con historial (multi-turno)

    Aqui usamos /api/chat para consistencia con los proveedores cloud.
    """
    modelo = modelo or OLLAMA_MODEL

    if MODO_SIMULADO:
        return {
            "modelo"        : modelo,
            "respuesta"     : f"[{modelo} simulado] Los LLMs open-source como Llama y Mistral son modelos de lenguaje libre que pueden ejecutarse localmente sin costo ni dependencias de la nube.",
            "tokens_entrada": len(prompt.split()),
            "tokens_salida" : 38,
            "tiempo_s"      : 0.8,
            "simulado"      : True,
        }

    payload = {
        "model"   : modelo,
        "messages": [
            {"role": "system", "content": sistema},
            {"role": "user",   "content": prompt},
        ],
        "stream" : False,
        "options": {"num_predict": max_tokens},
    }

    try:
        inicio    = time.time()
        respuesta = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json    = payload,
            timeout = 120,
        )
        tiempo = round(time.time() - inicio, 3)

        if respuesta.status_code != 200:
            raise RuntimeError(f"HTTP {respuesta.status_code}: {respuesta.text}")

        datos = respuesta.json()
        return {
            "modelo"        : modelo,
            "respuesta"     : datos["message"]["content"],
            "tokens_entrada": datos.get("prompt_eval_count", 0),
            "tokens_salida" : datos.get("eval_count", 0),
            "tiempo_s"      : tiempo,
            "simulado"      : False,
        }
    except Exception as e:
        print(f"  ERROR Ollama ({modelo}): {e}")
        return {
            "modelo"        : modelo,
            "respuesta"     : "No disponible (Ollama no esta corriendo o el modelo no esta descargado)",
            "tokens_entrada": 0,
            "tokens_salida" : 0,
            "tiempo_s"      : 0,
            "simulado"      : True,
        }


def mostrar_resultado(resultado: dict) -> None:
    sim = " [SIMULADO]" if resultado.get("simulado") else ""
    print(f"\n  Modelo    : {resultado['modelo']}{sim}")
    print(f"  Respuesta : {resultado['respuesta'][:250]}")
    tok_e = resultado.get('tokens_entrada', 0)
    tok_s = resultado.get('tokens_salida', 0)
    if tok_e or tok_s:
        print(f"  Tokens    : {tok_e} entrada / {tok_s} salida")
    print(f"  Tiempo    : {resultado['tiempo_s']}s")


# ──────────────────────────────────────────────────────────────────────────────
# Demo principal
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSESION 2 — EJEMPLO 02: MODELOS OPEN-SOURCE CON OLLAMA")

    # ── Estado de Ollama ──────────────────────────────────────────────────────
    separador("Estado de Ollama")
    ollama_ok = verificar_ollama()

    if ollama_ok:
        print(f"\n  Ollama corriendo en {OLLAMA_HOST}")
        modelos = listar_modelos_ollama()
        if modelos:
            print(f"\n  Modelos instalados ({len(modelos)}):")
            for m in modelos:
                tamano = m.get("size", 0) // (1024**3)
                print(f"    - {m['name']}  ({tamano}GB)")
        else:
            print("\n  Sin modelos instalados. Ejecuta: ollama pull llama3.2")
            MODO_SIMULADO = True
    else:
        print(f"\n  Ollama NO disponible en {OLLAMA_HOST}")
        print("  Ejecutando en MODO SIMULADO.\n")
        print("  Para habilitar modelos reales:")
        print("    1. Instalar: curl -fsSL https://ollama.com/install.sh | sh")
        print("    2. Descargar: ollama pull llama3.2")
        print("    3. Volver a ejecutar este script")

    # ── Catalogo de familias ──────────────────────────────────────────────────
    separador("Familias Open-Source Destacadas")
    print("""
  FAMILIA META LLAMA 3.x
  ─────────────────────
  llama3.2      3B  2GB   Liviano, rapido, ideal para aula
  llama3.1      8B  5GB   Mejor calidad general
  llama3.1     70B  40GB  Calidad near-GPT4 (requiere GPU)

  FAMILIA MISTRAL
  ───────────────
  mistral       7B  4GB   Instruccion excelente, ingles/frances
  mixtral      8x7B 26GB  Mixture of Experts, muy capaz

  FAMILIA MICROSOFT PHI
  ─────────────────────
  phi3:mini    3.8B 2.3GB Eficiente, sorprendentemente bueno
  phi3:medium   14B 8GB   Alta calidad con bajo costo

  FAMILIA ALIBABA QWEN
  ────────────────────
  qwen2.5       7B  5GB   Multilingue, excelente en espanol/chino
  qwen2.5-coder 7B  5GB   Especializado en codigo

  FAMILIA GOOGLE GEMMA
  ────────────────────
  gemma2        9B  6GB   Alta calidad, open weights
  gemma2:2b     2B  1.7GB Ultra liviano
    """)

    # ── Demo: Llama 3.2 ───────────────────────────────────────────────────────
    separador("Demo: Meta Llama 3.2 (3B)")

    prompts_demo = [
        "Que es un LLM? Responde en 2 oraciones.",
        "Escribe un ejemplo de JSON con datos de un cliente.",
    ]

    for prompt in prompts_demo:
        print(f"\n  Prompt: {prompt}")
        resultado = llamar_ollama(prompt, modelo="llama3.2")
        mostrar_resultado(resultado)

    # ── Demo: Diferentes modelos ──────────────────────────────────────────────
    separador("Comparacion de Velocidad: Modelos Pequenos")

    prompt_bench = "Lista 3 ventajas de los LLMs en empresas."
    modelos_bench = ["llama3.2", "phi3:mini"]

    print(f"\n  Prompt: {prompt_bench}\n")
    resultados = []
    for modelo in modelos_bench:
        res = llamar_ollama(prompt_bench, modelo=modelo)
        resultados.append(res)
        mostrar_resultado(res)

    # Ranking por velocidad
    resultados_ok = [r for r in resultados if not r.get("simulado") and r["tiempo_s"] > 0]
    if resultados_ok:
        print("\n  Ranking por velocidad:")
        for i, r in enumerate(sorted(resultados_ok, key=lambda x: x["tiempo_s"]), 1):
            tok_s = r.get("tokens_salida", 0)
            tps = round(tok_s / r["tiempo_s"], 1) if r["tiempo_s"] > 0 else 0
            print(f"    {i}. {r['modelo']}: {r['tiempo_s']}s  ({tps} tok/s)")

    # ── API compatible OpenAI ─────────────────────────────────────────────────
    separador("Ollama = Compatible con API de OpenAI")
    print("""
  Ollama expone exactamente la misma API que OpenAI.
  Esto significa que puedes usar el SDK de OpenAI apuntando a Ollama:

  from openai import OpenAI

  cliente = OpenAI(
      base_url = "http://localhost:11434/v1",
      api_key  = "ollama",              # cualquier string, no se valida
  )

  respuesta = cliente.chat.completions.create(
      model    = "llama3.2",
      messages = [{"role": "user", "content": "Hola!"}]
  )
  print(respuesta.choices[0].message.content)

  Con esto, puedes cambiar entre Ollama y OpenAI cambiando
  solo base_url y api_key. EL MISMO CODIGO funciona para ambos.
    """)

    # Demo real con SDK OpenAI apuntando a Ollama
    try:
        from openai import OpenAI
        cliente_ollama = OpenAI(
            base_url = f"{OLLAMA_HOST}/v1",
            api_key  = "ollama",
        )
        if ollama_ok and not MODO_SIMULADO:
            print("  Probando SDK OpenAI -> Ollama...")
            comp = cliente_ollama.chat.completions.create(
                model    = "llama3.2",
                messages = [{"role": "user", "content": "Di 'Hola desde Ollama' en una sola linea."}],
                max_tokens = 30,
            )
            print(f"  Respuesta: {comp.choices[0].message.content}")
        else:
            print("  [SIMULADO] SDK OpenAI -> Ollama: 'Hola desde Ollama via API compatible!'")
    except ImportError:
        print("  (openai no instalado — pip install openai)")


if __name__ == "__main__":
    main()
