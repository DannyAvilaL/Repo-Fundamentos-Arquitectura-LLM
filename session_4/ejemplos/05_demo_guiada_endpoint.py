"""
Sesión 4 · Ejemplo 5: Demo Guiada con un Endpoint
=====================================================

Objetivo: ejercicio integrador de cierre de sesión — un cliente de
terminal que consume el backend FastAPI de esta sesión (ver backend/main.py)
paso a paso, mostrando en cada paso qué ocurre: envío del prompt,
aplicación de parámetros, verificación de seguridad, y respuesta final
con las técnicas anti-alucinación activas o no.

Requiere que el backend esté corriendo:
    cd backend && uvicorn main:app --reload --port 8000
"""

import os
import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

load_dotenv()
console = Console()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def verificar_backend() -> bool:
    try:
        r = httpx.get(f"{API_BASE}/health", timeout=3.0)
        return r.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def paso_1_prompt() -> str:
    console.print("\n[bold cyan]Paso 1 — El Prompt[/bold cyan]")
    console.print("[dim]Escribe la pregunta que enviarás al modelo.[/dim]")
    return Prompt.ask("Tu prompt", default="¿Cuál es la política de devoluciones para compras internacionales?")


def paso_2_parametros() -> dict:
    console.print("\n[bold cyan]Paso 2 — Los Parámetros[/bold cyan]")
    perfil = Prompt.ask(
        "Elige un perfil de parámetros",
        choices=["preciso", "balanceado", "creativo"],
        default="preciso",
    )
    return {"perfil": perfil}


def paso_3_grounding() -> bool:
    console.print("\n[bold cyan]Paso 3 — Control de Alucinación[/bold cyan]")
    return Confirm.ask("¿Activar grounding (respuesta basada solo en contexto verificado)?", default=True)


def paso_4_enviar(prompt: str, perfil: str, usar_grounding: bool):
    console.print("\n[bold cyan]Paso 4 — Enviando al Backend[/bold cyan]")
    console.print(f"[dim]POST {API_BASE}/demo/completar[/dim]")

    payload = {
        "prompt": prompt,
        "perfil_parametros": perfil,
        "usar_grounding": usar_grounding,
    }
    try:
        r = httpx.post(f"{API_BASE}/demo/completar", json=payload, timeout=30.0)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        console.print(f"[red]Error HTTP {e.response.status_code}: {e.response.text}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Error de conexión: {e}[/red]")
        return None


def paso_5_mostrar_resultado(resultado: dict):
    console.print("\n[bold cyan]Paso 5 — Resultado[/bold cyan]")
    if resultado is None:
        console.print("[red]No se pudo completar la llamada.[/red]")
        return

    console.print(f"[dim]Modo: {'REAL' if not resultado.get('simulado') else 'SIMULADO'}[/dim]")
    console.print(f"[dim]Grounding activo: {resultado.get('grounding_activo')}[/dim]")
    console.print(f"[dim]Latencia: {resultado.get('latencia_seg', 0):.2f}s[/dim]")
    console.print(f"\n[bold]Respuesta:[/bold]\n{resultado.get('respuesta', '')}")

    if resultado.get("senales_alerta"):
        console.print("\n[yellow]⚠ Señales de alerta detectadas:[/yellow]")
        for s in resultado["senales_alerta"]:
            console.print(f"  • {s}")


def ejecutar_demo_guiada():
    console.print("[bold green]═══ Sesión 4: Demo Guiada con un Endpoint ═══[/bold green]")

    if not verificar_backend():
        console.print(f"\n[red]✗ No se pudo conectar al backend en {API_BASE}[/red]")
        console.print("[dim]Ejecuta primero: cd backend && uvicorn main:app --reload --port 8000[/dim]")
        return

    console.print(f"[green]✓ Backend activo en {API_BASE}[/green]")

    prompt = paso_1_prompt()
    params = paso_2_parametros()
    usar_grounding = paso_3_grounding()
    resultado = paso_4_enviar(prompt, params["perfil"], usar_grounding)
    paso_5_mostrar_resultado(resultado)


if __name__ == "__main__":
    ejecutar_demo_guiada()
