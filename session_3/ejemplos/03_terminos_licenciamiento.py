"""
Sesión 3 · Ejemplo 3: Términos Clave de Licenciamiento y Uso
================================================================

Objetivo: familiarizar a los alumnos con los términos legales/contractuales
más relevantes al integrar LLMs de terceros en un proyecto empresarial.

Este script es una guía de referencia ejecutable — no reemplaza asesoría
legal. Antes de integrar cualquier proveedor en producción, revisar los
Términos de Servicio (ToS) y el Acuerdo de Procesamiento de Datos (DPA)
vigentes en la fecha de implementación.
"""

from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

console = Console()


@dataclass
class TerminoLicenciamiento:
    concepto: str
    definicion: str
    ejemplo_proveedor: str


CONCEPTOS_CLAVE = [
    TerminoLicenciamiento(
        "Uso de datos para entrenamiento",
        "Si el proveedor puede usar tus prompts/respuestas para reentrenar sus modelos. "
        "La mayoría de las APIs empresariales (no las versiones de consumo gratuito) excluyen esto por defecto.",
        "OpenAI API / Azure OpenAI: NO se usan datos de API para entrenar. "
        "ChatGPT gratuito: SÍ, salvo que desactives el historial.",
    ),
    TerminoLicenciamiento(
        "Retención de datos",
        "Cuánto tiempo el proveedor conserva tus prompts/respuestas en sus servidores y con qué propósito (abuse monitoring).",
        "OpenAI: hasta 30 días para monitoreo de abuso, salvo Zero Data Retention (ZDR) aprobado.",
    ),
    TerminoLicenciamiento(
        "Licencia del modelo (open-weight)",
        "Bajo qué términos puedes usar, modificar y redistribuir un modelo de pesos abiertos.",
        "Llama Community License: uso comercial permitido, pero empresas con >700M usuarios mensuales "
        "activos requieren licencia especial de Meta. Mistral (algunos modelos): Apache 2.0, sin restricciones.",
    ),
    TerminoLicenciamiento(
        "Propiedad de las salidas (outputs)",
        "Quién es dueño del contenido generado por el modelo y si puedes usarlo comercialmente.",
        "OpenAI y Anthropic: el usuario es dueño de los outputs generados vía API, sujeto a cumplir los ToS.",
    ),
    TerminoLicenciamiento(
        "Acceptable Use Policy (AUP)",
        "Usos prohibidos explícitamente (ej. armas, vigilancia masiva, desinformación, contenido para menores).",
        "Todos los proveedores mayores (OpenAI, Anthropic, Google) publican una AUP; violarla puede resultar "
        "en suspensión de cuenta sin reembolso.",
    ),
    TerminoLicenciamiento(
        "SLA (Service Level Agreement) contractual",
        "Compromiso formal y penalizable de disponibilidad — distinto del 'uptime histórico' informal.",
        "Solo los hyperscalers (Azure, AWS Bedrock, Vertex AI) ofrecen SLA contractual con créditos "
        "de servicio. Las APIs directas (OpenAI, Anthropic) no ofrecen SLA formal por defecto.",
    ),
    TerminoLicenciamiento(
        "Residencia y soberanía de datos",
        "En qué región geográfica se procesan y almacenan los datos — crítico para GDPR, LGPD, leyes locales.",
        "Azure OpenAI y Vertex AI permiten fijar la región de despliegue. OpenAI/Anthropic directos "
        "procesan primariamente en EE.UU. salvo acuerdos empresariales específicos.",
    ),
    TerminoLicenciamiento(
        "DPA (Data Processing Agreement)",
        "Documento legal requerido para cumplimiento GDPR/LGPD cuando el proveedor procesa datos "
        "personales en tu nombre.",
        "Disponible bajo solicitud en todos los proveedores empresariales (OpenAI Enterprise, "
        "Anthropic, Azure, AWS, Google Cloud).",
    ),
]


def mostrar_terminos():
    tabla = Table(title="Términos Clave de Licenciamiento/Uso de LLMs", show_lines=True)
    tabla.add_column("Concepto", style="bold cyan", no_wrap=True)
    tabla.add_column("Definición")
    tabla.add_column("Ejemplo por proveedor")

    for t in CONCEPTOS_CLAVE:
        tabla.add_row(t.concepto, t.definicion, t.ejemplo_proveedor)
    console.print(tabla)


def checklist_due_diligence():
    """Checklist práctico antes de integrar un proveedor de LLM en un proyecto empresarial."""
    console.print("\n[bold yellow]Checklist de Due Diligence antes de integrar un proveedor[/bold yellow]\n")
    items = [
        "¿Los datos de entrada/salida se usan para reentrenar el modelo? (verificar ToS)",
        "¿Existe un DPA disponible si procesas datos personales?",
        "¿En qué región se procesan y almacenan los datos?",
        "¿Hay SLA contractual o es solo 'mejor esfuerzo'?",
        "¿La licencia del modelo permite el volumen de usuarios que proyectas?",
        "¿Qué política de retención aplica a tus prompts?",
        "¿El proveedor permite Zero Data Retention (ZDR) si tu industria lo requiere (salud, finanzas)?",
        "¿Existe un canal de soporte empresarial con tiempos de respuesta garantizados?",
    ]
    for i, item in enumerate(items, 1):
        console.print(f"  {i}. [ ] {item}")


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 3: Términos de Licenciamiento y Uso ═══[/bold green]\n")
    mostrar_terminos()
    checklist_due_diligence()
    console.print(
        "\n[dim]⚠ Este contenido es educativo, no constituye asesoría legal. "
        "Verifica siempre los términos vigentes con el equipo legal antes de producción.[/dim]"
    )
