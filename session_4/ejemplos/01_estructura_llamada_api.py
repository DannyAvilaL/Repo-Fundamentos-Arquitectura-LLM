"""
Sesión 4 · Ejemplo 1: Estructura de una Llamada API
======================================================

Objetivo: descomponer una llamada a un LLM en sus 3 componentes —
prompt, parámetros, seguridad básica — y mostrar cómo cada uno afecta
el resultado, el costo y el riesgo de la llamada.

Seguridad: NUNCA hardcodear API keys. Siempre os.getenv() + .env
Este script funciona en MODO_SIMULADO si no hay credenciales configuradas.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

MODO_SIMULADO = not os.getenv("OPENAI_API_KEY")


# ─── 1. EL PROMPT ─────────────────────────────────────────────────────────
# El prompt tiene normalmente dos partes lógicas, aunque la API las trate
# como mensajes separados:
#   - system: el rol/instrucciones permanentes del asistente
#   - user: la solicitud puntual de este turno

SYSTEM_PROMPT = (
    "Eres un asistente de soporte técnico de una empresa de software. "
    "Responde de forma breve, profesional y en español. "
    "Si no sabes la respuesta, dilo explícitamente — no inventes información."
)


# ─── 2. LOS PARÁMETROS ─────────────────────────────────────────────────────
# Cada parámetro cambia el comportamiento del modelo de forma distinta.
# Ninguno de estos "arregla" un mal prompt — pero un buen prompt con
# parámetros mal elegidos también puede fallar.

@dataclass
class ParametrosLlamada:
    temperature: float = 0.7   # 0 = determinista, 2 = máxima aleatoriedad
    max_tokens: int = 300      # techo de tokens de salida (controla costo)
    top_p: float = 1.0         # muestreo por núcleo — alternativa a temperature
    frequency_penalty: float = 0.0  # penaliza repetir las mismas palabras
    presence_penalty: float = 0.0   # penaliza repetir los mismos temas


PERFILES_PARAMETROS = {
    "preciso": ParametrosLlamada(temperature=0.0, max_tokens=200),
    "balanceado": ParametrosLlamada(temperature=0.7, max_tokens=300),
    "creativo": ParametrosLlamada(temperature=1.2, max_tokens=500),
}


def mostrar_perfiles():
    tabla = Table(title="Perfiles de Parámetros — Cuándo Usar Cada Uno")
    tabla.add_column("Perfil", style="bold cyan")
    tabla.add_column("temperature", justify="right")
    tabla.add_column("max_tokens", justify="right")
    tabla.add_column("Caso de uso recomendado")

    casos = {
        "preciso": "Clasificación, extracción de datos, código, respuestas factuales",
        "balanceado": "Chatbots conversacionales, soporte al cliente",
        "creativo": "Brainstorming, generación de variantes, copywriting",
    }
    for nombre, p in PERFILES_PARAMETROS.items():
        tabla.add_row(nombre, str(p.temperature), str(p.max_tokens), casos[nombre])
    console.print(tabla)


# ─── 3. SEGURIDAD BÁSICA ───────────────────────────────────────────────────
# Antes de enviar CUALQUIER llamada real, hay 4 verificaciones mínimas
# que todo desarrollador debería aplicar.

def verificar_api_key_presente(nombre_var: str) -> bool:
    """Regla 1: la API key existe y no está vacía."""
    valor = os.getenv(nombre_var)
    return bool(valor and valor.strip())


def verificar_api_key_no_hardcodeada(ruta_archivo: str) -> bool:
    """
    Regla 2: la API key no está escrita literalmente en el código fuente.
    Este chequeo es solo educativo — en la práctica se usa un linter de
    secretos (ej. gitleaks, truffleHog) en el pipeline de CI.
    """
    patrones_sospechosos = ["sk-", "sk-ant-", "AIza"]
    try:
        with open(ruta_archivo, encoding="utf-8") as f:
            contenido = f.read()
        for patron in patrones_sospechosos:
            if patron in contenido:
                return False
        return True
    except FileNotFoundError:
        return True


def sanitizar_input_usuario(texto: str, max_longitud: int = 4000) -> str:
    """
    Regla 3: nunca confiar en el input del usuario sin límites.
    Trunca el prompt para evitar costos inesperados o abuso del endpoint.
    """
    if len(texto) > max_longitud:
        console.print(f"[yellow]⚠ Input truncado de {len(texto)} a {max_longitud} caracteres[/yellow]")
        return texto[:max_longitud]
    return texto


def validar_longitud_respuesta_esperada(max_tokens: int, limite_razonable: int = 4000) -> bool:
    """Regla 4: max_tokens dentro de un rango razonable evita facturas sorpresa."""
    return 0 < max_tokens <= limite_razonable


def checklist_seguridad_basica(prompt_usuario: str, params: ParametrosLlamada) -> dict:
    resultados = {
        "API key presente (OPENAI_API_KEY)": verificar_api_key_presente("OPENAI_API_KEY"),
        "API key no hardcodeada en este archivo": verificar_api_key_no_hardcodeada(__file__),
        "Input del usuario dentro de límite razonable": len(prompt_usuario) <= 4000,
        "max_tokens dentro de rango razonable": validar_longitud_respuesta_esperada(params.max_tokens),
    }
    return resultados


def mostrar_checklist(resultados: dict):
    tabla = Table(title="Checklist de Seguridad Básica — Pre-Vuelo")
    tabla.add_column("Verificación")
    tabla.add_column("Estado", justify="center")
    for verificacion, ok in resultados.items():
        estado = "[green]✓ OK[/green]" if ok else "[red]✗ FALLA[/red]"
        tabla.add_row(verificacion, estado)
    console.print(tabla)


# ─── 4. LA LLAMADA COMPLETA ────────────────────────────────────────────────

def respuesta_simulada(prompt: str) -> str:
    return (
        f"[MODO_SIMULADO] Respuesta simulada para: '{prompt[:60]}...' "
        f"Configura OPENAI_API_KEY en .env para una llamada real."
    )


def ejecutar_llamada(prompt_usuario: str, params: ParametrosLlamada) -> str:
    """Ensambla y ejecuta la llamada completa: prompt + parámetros + seguridad."""
    prompt_usuario = sanitizar_input_usuario(prompt_usuario)

    resultados_seguridad = checklist_seguridad_basica(prompt_usuario, params)
    if not all(resultados_seguridad.values()):
        console.print("[red]⚠ Checklist de seguridad falló — revisa antes de continuar[/red]")
        mostrar_checklist(resultados_seguridad)

    if MODO_SIMULADO:
        return respuesta_simulada(prompt_usuario)

    from openai import OpenAI
    cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_usuario},
        ],
        temperature=params.temperature,
        max_tokens=params.max_tokens,
        top_p=params.top_p,
        frequency_penalty=params.frequency_penalty,
        presence_penalty=params.presence_penalty,
    )
    return respuesta.choices[0].message.content


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 4: Estructura de una Llamada API ═══[/bold green]\n")

    if MODO_SIMULADO:
        console.print("[yellow]⚠ MODO_SIMULADO activo — configura OPENAI_API_KEY en .env para llamadas reales[/yellow]\n")

    mostrar_perfiles()

    prompt_prueba = "¿Cómo restablezco mi contraseña si no tengo acceso a mi correo de recuperación?"
    params = PERFILES_PARAMETROS["preciso"]

    console.print(f"\n[bold]Prompt de prueba:[/bold] {prompt_prueba}")
    resultados_seguridad = checklist_seguridad_basica(prompt_prueba, params)
    mostrar_checklist(resultados_seguridad)

    console.print("\n[bold]Respuesta:[/bold]")
    console.print(ejecutar_llamada(prompt_prueba, params))
