"""
Sesión 4 · Ejemplo 2: Técnicas Introductorias de Prompting
==============================================================

Objetivo: mostrar, con el MISMO caso de uso, cómo distintas técnicas de
prompting cambian la calidad y consistencia de la respuesta. No requiere
credenciales — cada técnica se presenta con su prompt de ejemplo y una
explicación de cuándo usarla.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

MODO_SIMULADO = not os.getenv("OPENAI_API_KEY")

CASO_DE_USO = "Clasificar un ticket de soporte: 'La app se cierra sola cada vez que subo una foto de perfil.'"


@dataclass
class TecnicaPrompting:
    nombre: str
    descripcion: str
    prompt_ejemplo: str
    cuando_usarla: str


TECNICAS = [
    TecnicaPrompting(
        nombre="Zero-shot",
        descripcion="Se le pide la tarea directamente, sin ejemplos.",
        prompt_ejemplo=(
            "Clasifica este ticket de soporte en una categoría: bug, pregunta, "
            "solicitud de feature. Ticket: 'La app se cierra sola cada vez que "
            "subo una foto de perfil.'"
        ),
        cuando_usarla="Tareas simples y bien definidas donde el modelo ya 'sabe' el formato esperado.",
    ),
    TecnicaPrompting(
        nombre="Few-shot",
        descripcion="Se incluyen 2-3 ejemplos de entrada/salida antes de la tarea real.",
        prompt_ejemplo=(
            "Ejemplo 1 → Ticket: 'No puedo iniciar sesión' → Categoría: bug\n"
            "Ejemplo 2 → Ticket: '¿Tienen plan anual?' → Categoría: pregunta\n"
            "Ejemplo 3 → Ticket: 'Sería bueno tener modo oscuro' → Categoría: solicitud de feature\n\n"
            "Ticket: 'La app se cierra sola cada vez que subo una foto de perfil.' → Categoría:"
        ),
        cuando_usarla="Cuando el formato de salida es específico de tu negocio y zero-shot es inconsistente.",
    ),
    TecnicaPrompting(
        nombre="Chain-of-Thought (CoT)",
        descripcion="Se le pide al modelo razonar paso a paso antes de dar la respuesta final.",
        prompt_ejemplo=(
            "Analiza este ticket paso a paso antes de clasificarlo:\n"
            "1. ¿Qué está describiendo el usuario?\n"
            "2. ¿Es un comportamiento inesperado del sistema (bug), una duda (pregunta), "
            "o algo que no existe todavía (feature)?\n"
            "3. Da tu clasificación final.\n\n"
            "Ticket: 'La app se cierra sola cada vez que subo una foto de perfil.'"
        ),
        cuando_usarla="Tareas que requieren razonamiento (matemáticas, lógica, decisiones con criterios múltiples).",
    ),
    TecnicaPrompting(
        nombre="Role Prompting",
        descripcion="Se le asigna un rol/persona específico en el system prompt.",
        prompt_ejemplo=(
            "System: Eres un ingeniero de soporte técnico senior con 10 años de experiencia "
            "clasificando bugs de aplicaciones móviles. Eres extremadamente preciso.\n"
            "User: Clasifica: 'La app se cierra sola cada vez que subo una foto de perfil.'"
        ),
        cuando_usarla="Cuando quieres un tono o nivel de expertise consistente en todas las respuestas.",
    ),
    TecnicaPrompting(
        nombre="Structured Output (JSON forzado)",
        descripcion="Se pide explícitamente un formato estructurado, idealmente con response_format.",
        prompt_ejemplo=(
            "Clasifica el ticket y responde ÚNICAMENTE con JSON válido en este formato: "
            '{"categoria": "bug|pregunta|feature", "prioridad": "alta|media|baja", '
            '"confianza": 0.0-1.0}\n\n'
            "Ticket: 'La app se cierra sola cada vez que subo una foto de perfil.'"
        ),
        cuando_usarla="Cuando la respuesta se va a procesar programáticamente (como en el backend de esta sesión).",
    ),
]


def mostrar_tecnicas():
    for t in TECNICAS:
        console.print(Panel(
            f"[dim]{t.descripcion}[/dim]\n\n"
            f"[bold]Prompt de ejemplo:[/bold]\n{t.prompt_ejemplo}\n\n"
            f"[bold yellow]Cuándo usarla:[/bold yellow] {t.cuando_usarla}",
            title=f"[bold cyan]{t.nombre}[/bold cyan]",
            expand=False,
        ))


def respuesta_simulada(tecnica: str) -> str:
    ejemplos = {
        "Zero-shot": "bug",
        "Few-shot": "bug",
        "Chain-of-Thought (CoT)": (
            "1. El usuario describe un cierre inesperado de la app.\n"
            "2. Es un comportamiento anómalo del sistema → bug.\n"
            "3. Categoría final: bug."
        ),
        "Role Prompting": "Clasificación: bug (crash reproducible al subir imagen — prioridad alta).",
        "Structured Output (JSON forzado)": '{"categoria": "bug", "prioridad": "alta", "confianza": 0.95}',
    }
    return f"[MODO_SIMULADO] {ejemplos.get(tecnica, 'respuesta simulada')}"


def probar_tecnica(tecnica: TecnicaPrompting) -> str:
    if MODO_SIMULADO:
        return respuesta_simulada(tecnica.nombre)

    from openai import OpenAI
    cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    mensajes = [{"role": "user", "content": tecnica.prompt_ejemplo}]
    if tecnica.nombre == "Role Prompting":
        mensajes = [
            {"role": "system", "content": "Eres un ingeniero de soporte técnico senior con 10 años de experiencia clasificando bugs de aplicaciones móviles. Eres extremadamente preciso."},
            {"role": "user", "content": "Clasifica: 'La app se cierra sola cada vez que subo una foto de perfil.'"},
        ]
    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini", messages=mensajes, temperature=0.2, max_tokens=200,
    )
    return respuesta.choices[0].message.content


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 4: Técnicas de Prompting ═══[/bold green]\n")
    console.print(f"[dim]Caso de uso constante: {CASO_DE_USO}[/dim]\n")

    if MODO_SIMULADO:
        console.print("[yellow]⚠ MODO_SIMULADO activo[/yellow]\n")

    mostrar_tecnicas()

    console.print("\n[bold green]═══ Resultados comparativos ═══[/bold green]\n")
    for t in TECNICAS:
        resultado = probar_tecnica(t)
        console.print(f"[bold cyan]{t.nombre}:[/bold cyan] {resultado}\n")
