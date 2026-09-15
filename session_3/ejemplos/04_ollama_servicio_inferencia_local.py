"""
Sesión 3 · Ejemplo 4: Ollama como Servicio de Inferencia Local
==================================================================

Objetivo: mostrar Ollama como una alternativa de "proveedor de inferencia"
que corre en la máquina del alumno — útil para pruebas sin costo, sin
credenciales, y como punto de comparación de disponibilidad/latencia
frente a proveedores cloud.

Requiere Ollama instalado y corriendo (ver docs/SETUP.md). Si Ollama no
está disponible, el script cae a MODO_SIMULADO automáticamente.
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
    """Verifica si el servicio de Ollama está corriendo y accesible."""
    try:
        respuesta = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        return respuesta.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def listar_modelos_ollama() -> list:
    """Lista los modelos instalados localmente en Ollama."""
    try:
        respuesta = httpx.get(f"{OLLAMA_HOST}/api/tags", timeout=3.0)
        respuesta.raise_for_status()
        return [m["name"] for m in respuesta.json().get("models", [])]
    except Exception:
        return []


def consultar_ollama(modelo: str, prompt: str) -> tuple:
    """Envía un prompt a Ollama y mide latencia. Retorna (respuesta, latencia_seg)."""
    inicio = time.time()
    try:
        respuesta = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": modelo,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60.0,
        )
        respuesta.raise_for_status()
        contenido = respuesta.json()["message"]["content"]
        latencia = time.time() - inicio
        return contenido, latencia
    except Exception as e:
        return f"[ERROR] {e}", time.time() - inicio


def medir_disponibilidad(intentos: int = 5) -> dict:
    """
    Mide disponibilidad práctica de Ollama con N intentos de health-check.
    Sirve como ejercicio comparativo: los alumnos pueden hacer lo mismo
    contra un endpoint cloud y comparar consistencia de latencia.
    """
    resultados = []
    for i in range(intentos):
        inicio = time.time()
        ok = verificar_ollama()
        latencia_ms = (time.time() - inicio) * 1000
        resultados.append({"intento": i + 1, "disponible": ok, "latencia_ms": round(latencia_ms, 1)})
    return resultados


def mostrar_disponibilidad(resultados: list):
    tabla = Table(title=f"Disponibilidad Ollama local ({OLLAMA_HOST})")
    tabla.add_column("Intento", justify="center")
    tabla.add_column("Disponible", justify="center")
    tabla.add_column("Latencia (ms)", justify="right")

    exitosos = sum(1 for r in resultados if r["disponible"])
    for r in resultados:
        estado = "✅" if r["disponible"] else "❌"
        tabla.add_row(str(r["intento"]), estado, str(r["latencia_ms"]))

    console.print(tabla)
    console.print(f"\nDisponibilidad observada: {exitosos}/{len(resultados)} "
                  f"({exitosos/len(resultados)*100:.0f}%)")


def mostrar_compatibilidad_openai():
    """Demuestra que Ollama expone una API compatible con el SDK de OpenAI."""
    console.print("\n[bold yellow]Compatibilidad con SDK de OpenAI[/bold yellow]")
    console.print(
        "Ollama expone un endpoint compatible en /v1/, lo que permite reutilizar "
        "el SDK oficial de OpenAI apuntando a tu servidor local:\n"
    )
    console.print("""[dim]
from openai import OpenAI

cliente = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # cualquier valor no vacío — Ollama no valida esta key
)

respuesta = cliente.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Hola"}],
)
print(respuesta.choices[0].message.content)
[/dim]""")


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 3: Ollama como Servicio de Inferencia Local ═══[/bold green]\n")

    if not verificar_ollama():
        console.print(f"[yellow]⚠ Ollama no detectado en {OLLAMA_HOST} — MODO_SIMULADO[/yellow]")
        console.print("[dim]Instala Ollama y ejecuta 'ollama serve' para probar en vivo. Ver docs/SETUP.md[/dim]\n")
        mostrar_compatibilidad_openai()
    else:
        modelos = listar_modelos_ollama()
        console.print(f"[green]✅ Ollama activo. Modelos instalados: {modelos or 'ninguno — ejecuta ollama pull llama3.2:3b'}[/green]\n")

        console.print("[bold]Midiendo disponibilidad (5 health-checks)...[/bold]")
        resultados = medir_disponibilidad()
        mostrar_disponibilidad(resultados)

        if modelos:
            console.print(f"\n[bold]Consultando modelo '{modelos[0]}'...[/bold]")
            respuesta, latencia = consultar_ollama(modelos[0], "¿Qué es un servicio de inferencia de LLM?")
            console.print(f"Respuesta ({latencia:.2f}s): {respuesta[:300]}")

        mostrar_compatibilidad_openai()
