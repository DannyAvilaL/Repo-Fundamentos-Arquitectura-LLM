"""
Sesión 4 · Ejemplo 3: Control de Alucinación
================================================

Objetivo: mostrar 5 técnicas prácticas para reducir alucinaciones — el
modelo inventando información que suena plausible pero es falsa — y
un patrón de auto-verificación aplicable en producción.

No requiere credenciales para ver las técnicas; la demo con llamada real
requiere OPENAI_API_KEY.
"""

import os
import re
from dataclasses import dataclass
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
console = Console()

MODO_SIMULADO = not os.getenv("OPENAI_API_KEY")


@dataclass
class TecnicaAntiAlucinacion:
    nombre: str
    descripcion: str
    ejemplo: str
    limitacion: str


TECNICAS = [
    TecnicaAntiAlucinacion(
        nombre="1. Permitir 'No lo sé'",
        descripcion="Instruir explícitamente al modelo a admitir cuando no tiene la información, "
                    "en vez de forzarlo (implícitamente) a siempre dar una respuesta.",
        ejemplo='System: "Si no tienes información suficiente para responder con certeza, '
                'di explícitamente \'No tengo información suficiente\' en vez de adivinar."',
        limitacion="El modelo puede subestimar o sobrestimar su propia certeza — no es infalible.",
    ),
    TecnicaAntiAlucinacion(
        nombre="2. Grounding con contexto (RAG)",
        descripcion="En vez de confiar en el conocimiento interno del modelo, se le da el contexto "
                    "relevante en el prompt y se le pide responder SOLO con base en ese contexto.",
        ejemplo='"Responde ÚNICAMENTE con información del siguiente documento. Si la respuesta '
                'no está en el documento, di que no está disponible.\\n\\nDocumento: [...]"',
        limitacion="Requiere tener el contexto correcto disponible — no resuelve preguntas fuera de ese dominio.",
    ),
    TecnicaAntiAlucinacion(
        nombre="3. Pedir citas/fuentes",
        descripcion="Solicitar que cada afirmación factual venga acompañada de su fuente dentro "
                    "del contexto proporcionado — facilita verificar después.",
        ejemplo='"Para cada dato que menciones, indica entre corchetes de qué parte del documento '
                'lo obtuviste, ej: [Sección 2, párrafo 3]."',
        limitacion="El modelo puede inventar también la cita — siempre verificar que la fuente citada exista.",
    ),
    TecnicaAntiAlucinacion(
        nombre="4. Temperature baja para hechos",
        descripcion="Usar temperature=0 o cercano a 0 en tareas factuales reduce (no elimina) "
                    "la tendencia a generar variaciones creativas de la verdad.",
        ejemplo="temperature=0.0 en vez de 0.7-1.0 para preguntas de hechos, cálculos, citas legales.",
        limitacion="Temperature baja no impide alucinaciones — solo reduce variabilidad, no aumenta veracidad.",
    ),
    TecnicaAntiAlucinacion(
        nombre="5. Segunda pasada de auto-verificación",
        descripcion="Pedir al modelo que revise su propia respuesta anterior buscando afirmaciones "
                    "no verificables o inconsistentes, en una segunda llamada.",
        ejemplo='"Revisa la siguiente respuesta y marca cualquier afirmación que no puedas verificar '
                'con el contexto dado: [respuesta anterior]"',
        limitacion="Duplica el costo y la latencia — usar solo en casos de alto riesgo (legal, médico, financiero).",
    ),
]


def mostrar_tecnicas():
    for t in TECNICAS:
        console.print(Panel(
            f"[dim]{t.descripcion}[/dim]\n\n"
            f"[bold]Ejemplo:[/bold] {t.ejemplo}\n\n"
            f"[bold yellow]Limitación:[/bold yellow] {t.limitacion}",
            title=f"[bold cyan]{t.nombre}[/bold cyan]",
            expand=False,
        ))


# ─── Demo: mismo prompt CON y SIN grounding ────────────────────────────────

CONTEXTO_REAL = """
Política de devoluciones de Tienda Andina:
- Plazo: 30 días desde la compra.
- Requisito: boleta o factura original.
- Condición: producto sin uso, en su empaque original.
- Excepción: productos de higiene personal no tienen devolución.
"""

PREGUNTA_TRAMPA = "¿Cuál es la política de devoluciones para compras internacionales?"


def respuesta_sin_grounding_simulada() -> str:
    return (
        "[MODO_SIMULADO — SIN grounding, respuesta típica de alto riesgo] "
        "Para compras internacionales, Tienda Andina ofrece devoluciones dentro de 45 días "
        "con envío gratuito de retorno. ← ESTO ES INVENTADO, no está en el contexto real."
    )


def respuesta_con_grounding_simulada() -> str:
    return (
        "[MODO_SIMULADO — CON grounding] La política proporcionada no menciona compras "
        "internacionales específicamente. Solo puedo confirmar la política general: 30 días, "
        "con boleta, producto sin uso. Te recomiendo confirmar el caso internacional con soporte."
    )


def demo_grounding():
    console.print("\n[bold green]═══ Demo: mismo prompt CON y SIN grounding ═══[/bold green]\n")
    console.print(f"[dim]Pregunta trampa (la respuesta NO está en el contexto): {PREGUNTA_TRAMPA}[/dim]\n")

    if MODO_SIMULADO:
        console.print("[red]SIN grounding:[/red]", respuesta_sin_grounding_simulada())
        console.print("\n[green]CON grounding:[/green]", respuesta_con_grounding_simulada())
        return

    from openai import OpenAI
    cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Sin grounding: el modelo responde de memoria, sin contexto real
    resp_sin = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PREGUNTA_TRAMPA}],
        temperature=0.7, max_tokens=150,
    )
    console.print("[red]SIN grounding:[/red]", resp_sin.choices[0].message.content)

    # Con grounding: se le da el contexto real y se le exige ceñirse a él
    resp_con = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Responde ÚNICAMENTE con información del contexto dado. Si la respuesta no está en el contexto, dilo explícitamente."},
            {"role": "user", "content": f"Contexto:\n{CONTEXTO_REAL}\n\nPregunta: {PREGUNTA_TRAMPA}"},
        ],
        temperature=0.0, max_tokens=150,
    )
    console.print("\n[green]CON grounding:[/green]", resp_con.choices[0].message.content)


def detectar_senales_alerta(respuesta: str) -> list:
    """
    Heurística simple (NO infalible) para marcar posibles señales de
    alucinación en una respuesta — útil como capa adicional, no como
    reemplazo de verificación humana en casos de alto riesgo.
    """
    senales = []
    if re.search(r'\b\d{1,3}%\b', respuesta) and "contexto" not in respuesta.lower():
        senales.append("Contiene una estadística específica sin referencia a fuente/contexto")
    if re.search(r'\b(siempre|nunca|garantizado|100%)\b', respuesta, re.IGNORECASE):
        senales.append("Usa lenguaje absoluto ('siempre', 'nunca', 'garantizado') — verificar")
    if len(respuesta) > 50 and "no tengo información" not in respuesta.lower() and "no está" not in respuesta.lower():
        pass  # respuesta normal, sin alerta adicional
    return senales


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 4: Control de Alucinación ═══[/bold green]\n")

    if MODO_SIMULADO:
        console.print("[yellow]⚠ MODO_SIMULADO activo[/yellow]\n")

    mostrar_tecnicas()
    demo_grounding()

    console.print("\n[bold green]═══ Heurística de señales de alerta ═══[/bold green]")
    ejemplo_respuesta = "Nuestro producto tiene 99% de satisfacción garantizada y siempre funciona."
    senales = detectar_senales_alerta(ejemplo_respuesta)
    console.print(f"\nRespuesta analizada: '{ejemplo_respuesta}'")
    for s in senales:
        console.print(f"  [yellow]⚠ {s}[/yellow]")
