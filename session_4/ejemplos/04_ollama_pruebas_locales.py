"""
Sesión 4 · Ejemplo 4: Pruebas Locales con Ollama
====================================================

Objetivo: que el alumno pueda practicar TODO el contenido de esta sesión
(estructura de llamada, prompting, control de alucinación) sin necesitar
ninguna API key — usando un modelo corriendo en su propia máquina.

Requiere Ollama instalado y corriendo (ver docs/SETUP.md). Si Ollama no
está disponible, cae a MODO_SIMULADO automáticamente.
"""

import os
import time
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def verificar_ollama() -> bool:
    try:
        r = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def listar_modelos() -> list:
    try:
        r = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        r.raise_for_status()
        return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


def llamar_ollama(modelo: str, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> tuple:
    """Misma estructura de llamada del ejemplo 1 (system + user + parámetros), pero local."""
    inicio = time.time()
    try:
        r = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "options": {"temperature": temperature},
                "stream": False,
            },
            timeout=60.0,
        )
        r.raise_for_status()
        contenido = r.json()["message"]["content"]
        return contenido, time.time() - inicio
    except Exception as e:
        return f"[ERROR] {e}", time.time() - inicio


def practicar_prompting_local(modelo: str):
    """Reutiliza las técnicas del ejemplo 2, pero ejecutadas 100% en local."""
    console.print("\n[bold]Práctica: Chain-of-Thought en local[/bold]")
    prompt_cot = (
        "Analiza este ticket paso a paso antes de clasificarlo:\n"
        "1. ¿Qué está describiendo el usuario?\n"
        "2. ¿Es un bug, una pregunta, o una solicitud de feature?\n"
        "3. Da tu clasificación final.\n\n"
        "Ticket: 'La app se cierra sola cada vez que subo una foto de perfil.'"
    )
    respuesta, latencia = llamar_ollama(
        modelo,
        "Eres un asistente de soporte técnico preciso y breve.",
        prompt_cot,
        temperature=0.2,
    )
    console.print(f"[dim]Latencia: {latencia:.2f}s[/dim]")
    console.print(respuesta)


def practicar_grounding_local(modelo: str):
    """Reutiliza la demo de grounding del ejemplo 3, pero ejecutada en local."""
    console.print("\n[bold]Práctica: Grounding (control de alucinación) en local[/bold]")
    contexto = (
        "Política de devoluciones de Tienda Andina: 30 días desde la compra, "
        "con boleta original, producto sin uso. Productos de higiene personal no aplican."
    )
    pregunta = "¿Cuál es la política de devoluciones para compras internacionales?"

    respuesta, latencia = llamar_ollama(
        modelo,
        "Responde ÚNICAMENTE con información del contexto dado. Si la respuesta no está en el contexto, dilo explícitamente.",
        f"Contexto:\n{contexto}\n\nPregunta: {pregunta}",
        temperature=0.0,
    )
    console.print(f"[dim]Latencia: {latencia:.2f}s[/dim]")
    console.print(respuesta)


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 4: Pruebas Locales con Ollama ═══[/bold green]\n")

    if not verificar_ollama():
        console.print(f"[yellow]⚠ Ollama no detectado en {OLLAMA_HOST} — instala y ejecuta 'ollama serve'.[/yellow]")
        console.print("[dim]Ver docs/SETUP.md para instrucciones. Sin Ollama, usa los ejemplos 1-3 con OPENAI_API_KEY o en MODO_SIMULADO.[/dim]")
    else:
        modelos = listar_modelos()
        if not modelos:
            console.print("[yellow]⚠ Ollama está corriendo pero no tiene modelos instalados.[/yellow]")
            console.print("[dim]Ejecuta: ollama pull llama3.2:3b[/dim]")
        else:
            modelo = modelos[0]
            console.print(f"[green]✅ Ollama activo. Usando modelo: {modelo}[/green]")
            practicar_prompting_local(modelo)
            practicar_grounding_local(modelo)
