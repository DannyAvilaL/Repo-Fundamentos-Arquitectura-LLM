"""
Sesión 3 · Ejemplo 5: Benchmark Comparativo Multi-Proveedor
===============================================================

Objetivo: ejercicio integrador — enviar el mismo prompt a múltiples
proveedores (los que tengan credenciales configuradas; el resto en
MODO_SIMULADO) y comparar latencia, longitud de respuesta y costo estimado.

Este es el mismo patrón que usa el backend FastAPI de esta sesión,
en versión standalone de terminal para que el alumno entienda la lógica
antes de verla en la API.
"""

import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

PROMPT_PRUEBA = "Enumera 3 factores clave al elegir un proveedor de inferencia LLM para producción."


@dataclass
class ResultadoBenchmark:
    proveedor: str
    latencia_seg: float
    tokens_aprox: int
    costo_estimado_usd: float
    respuesta_preview: str
    simulado: bool


def _estimar_tokens(texto: str) -> int:
    """Estimación simple: ~4 caracteres por token (aproximación en inglés/español)."""
    return max(1, len(texto) // 4)


def _respuesta_simulada(proveedor: str) -> str:
    return (
        f"[MODO_SIMULADO — {proveedor}] 1) Costo por token según volumen esperado. "
        f"2) Cumplimiento y residencia de datos requeridos. 3) SLA de disponibilidad contractual."
    )


def benchmark_openai() -> ResultadoBenchmark:
    inicio = time.time()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ResultadoBenchmark("OpenAI (GPT-4o-mini)", 0.0, 0, 0.0, _respuesta_simulada("OpenAI"), True)

    from openai import OpenAI
    cliente = OpenAI(api_key=api_key)
    resp = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT_PRUEBA}],
        max_tokens=150,
    )
    texto = resp.choices[0].message.content
    latencia = time.time() - inicio
    tokens = resp.usage.total_tokens if resp.usage else _estimar_tokens(texto)
    costo = (tokens / 1_000_000) * 0.60  # aprox blended input/output
    return ResultadoBenchmark("OpenAI (GPT-4o-mini)", latencia, tokens, costo, texto[:150], False)


def benchmark_anthropic() -> ResultadoBenchmark:
    inicio = time.time()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return ResultadoBenchmark("Anthropic (Claude Haiku)", 0.0, 0, 0.0, _respuesta_simulada("Anthropic"), True)

    import anthropic
    cliente = anthropic.Anthropic(api_key=api_key)
    resp = cliente.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=150,
        messages=[{"role": "user", "content": PROMPT_PRUEBA}],
    )
    texto = resp.content[0].text
    latencia = time.time() - inicio
    tokens = resp.usage.input_tokens + resp.usage.output_tokens
    costo = (tokens / 1_000_000) * 0.75  # aprox blended
    return ResultadoBenchmark("Anthropic (Claude Haiku)", latencia, tokens, costo, texto[:150], False)


def benchmark_google() -> ResultadoBenchmark:
    inicio = time.time()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return ResultadoBenchmark("Google (Gemini 2.0 Flash)", 0.0, 0, 0.0, _respuesta_simulada("Google"), True)

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    modelo = genai.GenerativeModel("gemini-2.0-flash")
    resp = modelo.generate_content(PROMPT_PRUEBA)
    texto = resp.text
    latencia = time.time() - inicio
    tokens = _estimar_tokens(PROMPT_PRUEBA + texto)
    costo = (tokens / 1_000_000) * 0.19  # aprox blended
    return ResultadoBenchmark("Google (Gemini 2.0 Flash)", latencia, tokens, costo, texto[:150], False)


def benchmark_ollama() -> ResultadoBenchmark:
    inicio = time.time()
    import httpx
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        tags = httpx.get(f"{host}/api/tags", timeout=2.0)
        modelos = [m["name"] for m in tags.json().get("models", [])]
        if not modelos:
            raise RuntimeError("Sin modelos instalados")
        modelo = modelos[0]
        resp = httpx.post(
            f"{host}/api/chat",
            json={"model": modelo, "messages": [{"role": "user", "content": PROMPT_PRUEBA}], "stream": False},
            timeout=60.0,
        )
        texto = resp.json()["message"]["content"]
        latencia = time.time() - inicio
        return ResultadoBenchmark(f"Ollama local ({modelo})", latencia, _estimar_tokens(texto), 0.0, texto[:150], False)
    except Exception:
        return ResultadoBenchmark("Ollama local", 0.0, 0, 0.0, _respuesta_simulada("Ollama"), True)


def ejecutar_benchmark() -> list:
    console.print(f"[dim]Prompt de prueba: '{PROMPT_PRUEBA}'[/dim]\n")
    return [
        benchmark_openai(),
        benchmark_anthropic(),
        benchmark_google(),
        benchmark_ollama(),
    ]


def mostrar_resultados(resultados: list):
    tabla = Table(title="Benchmark Comparativo Multi-Proveedor", show_lines=True)
    tabla.add_column("Proveedor", style="bold cyan")
    tabla.add_column("Latencia (s)", justify="right")
    tabla.add_column("Tokens aprox.", justify="right")
    tabla.add_column("Costo estimado", justify="right")
    tabla.add_column("Modo")

    for r in resultados:
        modo = "[yellow]SIMULADO[/yellow]" if r.simulado else "[green]REAL[/green]"
        tabla.add_row(
            r.proveedor,
            f"{r.latencia_seg:.2f}" if not r.simulado else "—",
            str(r.tokens_aprox) if not r.simulado else "—",
            f"${r.costo_estimado_usd:.5f}" if not r.simulado else "—",
            modo,
        )
    console.print(tabla)


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 3: Benchmark Comparativo Multi-Proveedor ═══[/bold green]\n")
    resultados = ejecutar_benchmark()
    mostrar_resultados(resultados)
    console.print(
        "\n[dim]Configura las API keys en .env para ver latencias y costos reales. "
        "Ollama requiere 'ollama serve' corriendo localmente.[/dim]"
    )
