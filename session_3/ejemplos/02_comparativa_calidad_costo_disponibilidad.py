"""
Sesión 3 · Ejemplo 2: Comparativa de Calidad, Costo y Disponibilidad
=======================================================================

Objetivo: dar a los alumnos un marco cuantitativo simple para comparar
proveedores en 3 ejes: calidad (benchmark proxy), costo (USD por millón
de tokens) y disponibilidad (SLA / uptime declarado).

No requiere credenciales — usa datos de referencia públicos actualizados
manualmente. Los precios cambian con frecuencia: siempre verificar en la
página oficial del proveedor antes de usar en producción.
"""

from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class ModeloInferencia:
    proveedor: str
    modelo: str
    precio_input_mtok: float   # USD por millón de tokens de entrada
    precio_output_mtok: float  # USD por millón de tokens de salida
    calidad_relativa: int      # 1-10, proxy simplificado (no un benchmark oficial)
    sla_uptime: str
    contexto_k: int            # tamaño de ventana de contexto en miles de tokens


# Precios de referencia (actualizar antes de usar en clase — cambian seguido)
CATALOGO = [
    ModeloInferencia("OpenAI", "GPT-4o", 2.50, 10.00, 9, "99.9% (histórico, sin SLA contractual directo)", 128),
    ModeloInferencia("OpenAI", "GPT-4o-mini", 0.15, 0.60, 7, "99.9% (histórico, sin SLA contractual directo)", 128),
    ModeloInferencia("Anthropic", "Claude Sonnet", 3.00, 15.00, 9, "99.9% (histórico, sin SLA contractual directo)", 200),
    ModeloInferencia("Anthropic", "Claude Haiku", 0.25, 1.25, 6, "99.9% (histórico, sin SLA contractual directo)", 200),
    ModeloInferencia("Google", "Gemini 2.0 Flash", 0.075, 0.30, 8, "99.9% (histórico, sin SLA contractual directo)", 1000),
    ModeloInferencia("Azure OpenAI", "GPT-4o (Azure)", 2.50, 10.00, 9, "99.9% SLA contractual (Enterprise Agreement)", 128),
    ModeloInferencia("AWS Bedrock", "Claude Sonnet (Bedrock)", 3.00, 15.00, 9, "99.9% SLA contractual (AWS)", 200),
    ModeloInferencia("Vertex AI", "Gemini 2.0 Flash (Vertex)", 0.075, 0.30, 8, "99.9% SLA contractual (GCP)", 1000),
    ModeloInferencia("Ollama (local)", "Llama 3.2 3B", 0.0, 0.0, 5, "Depende de tu propia infraestructura", 128),
]


def calcular_costo_estimado(modelo: ModeloInferencia, tokens_input: int, tokens_output: int) -> float:
    """Costo estimado en USD para un volumen de tokens dado."""
    costo_input = (tokens_input / 1_000_000) * modelo.precio_input_mtok
    costo_output = (tokens_output / 1_000_000) * modelo.precio_output_mtok
    return round(costo_input + costo_output, 4)


def mostrar_comparativa():
    tabla = Table(title="Comparativa: Calidad · Costo · Disponibilidad", show_lines=True)
    tabla.add_column("Proveedor", style="bold cyan")
    tabla.add_column("Modelo")
    tabla.add_column("$/MTok in", justify="right")
    tabla.add_column("$/MTok out", justify="right")
    tabla.add_column("Calidad (1-10)", justify="center")
    tabla.add_column("Contexto (K tokens)", justify="right")
    tabla.add_column("Disponibilidad / SLA")

    for m in CATALOGO:
        tabla.add_row(
            m.proveedor, m.modelo,
            f"${m.precio_input_mtok:.3f}",
            f"${m.precio_output_mtok:.3f}",
            str(m.calidad_relativa),
            str(m.contexto_k),
            m.sla_uptime,
        )
    console.print(tabla)


def mostrar_costo_por_volumen(tokens_input=1_000_000, tokens_output=250_000):
    """Simula el costo mensual para un volumen de uso típico de una app empresarial."""
    tabla = Table(title=f"Costo estimado: {tokens_input:,} tokens input + {tokens_output:,} tokens output / mes")
    tabla.add_column("Proveedor · Modelo", style="bold cyan")
    tabla.add_column("Costo mensual estimado (USD)", justify="right")

    resultados = []
    for m in CATALOGO:
        costo = calcular_costo_estimado(m, tokens_input, tokens_output)
        resultados.append((f"{m.proveedor} · {m.modelo}", costo))

    resultados.sort(key=lambda x: x[1])
    for nombre, costo in resultados:
        tabla.add_row(nombre, f"${costo:,.2f}")

    console.print(tabla)


def criterios_seleccion():
    """Marco de decisión simple para elegir proveedor según prioridad del proyecto."""
    console.print("\n[bold yellow]Marco de selección rápida[/bold yellow]\n")
    criterios = [
        ("Máxima calidad, presupuesto flexible", "GPT-4o / Claude Sonnet (directo o vía hyperscaler)"),
        ("Costo mínimo, calidad aceptable", "Gemini 2.0 Flash / GPT-4o-mini / Claude Haiku"),
        ("Cumplimiento empresarial (SOC2/HIPAA)", "Azure OpenAI / AWS Bedrock / Vertex AI"),
        ("Multi-proveedor en una sola integración", "AWS Bedrock (Model Access) o Vertex AI Model Garden"),
        ("Cero costo por token, control total de datos", "Ollama self-hosted (Llama, Mistral, Phi)"),
        ("Contexto muy largo (>500K tokens)", "Gemini 2.0/2.5 (directo o Vertex AI)"),
    ]
    for necesidad, recomendacion in criterios:
        console.print(f"  • [bold]{necesidad}[/bold] → {recomendacion}")


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 3: Comparativa de Proveedores ═══[/bold green]\n")
    mostrar_comparativa()
    print()
    mostrar_costo_por_volumen()
    criterios_seleccion()
