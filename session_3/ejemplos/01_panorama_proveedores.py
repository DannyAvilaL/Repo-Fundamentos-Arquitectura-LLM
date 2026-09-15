"""
Sesión 3 · Ejemplo 1: Panorama de Proveedores de Inferencia
=============================================================

Objetivo: mapear el ecosistema de proveedores que ofrecen acceso a LLMs
mediante API — directos (OpenAI, Anthropic, Google) y a través de
hyperscalers (Azure, Vertex AI / Gemini Enterprise Agent Platform, AWS Bedrock).

Seguridad: NUNCA hardcodear API keys. Siempre os.getenv() + .env
Este script funciona en MODO_SIMULADO si no hay credenciales configuradas.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
console = Console()

MODO_SIMULADO = not any([
    os.getenv("OPENAI_API_KEY"),
    os.getenv("ANTHROPIC_API_KEY"),
    os.getenv("GOOGLE_API_KEY"),
])


# ─── Modelo de datos: Proveedor de inferencia ────────────────────────────────

@dataclass
class Proveedor:
    nombre: str
    tipo: str                    # "directo" | "hyperscaler"
    modelos_destacados: list = field(default_factory=list)
    fortalezas: str = ""
    consideraciones: str = ""
    licenciamiento: str = ""


CATALOGO_PROVEEDORES = [
    Proveedor(
        nombre="OpenAI (directo)",
        tipo="directo",
        modelos_destacados=["GPT-4o", "GPT-4o-mini", "o1", "o3-mini"],
        fortalezas="Ecosistema maduro, function calling robusto, gran comunidad",
        consideraciones="Sin SLA empresarial propio; rate limits por tier de uso",
        licenciamiento="Uso comercial permitido vía API; términos de uso propios de OpenAI",
    ),
    Proveedor(
        nombre="Anthropic (directo)",
        tipo="directo",
        modelos_destacados=["Claude Opus", "Claude Sonnet", "Claude Haiku"],
        fortalezas="Ventanas de contexto largas, fuerte en razonamiento y seguridad",
        consideraciones="Requiere workspace scoping en API keys de organización",
        licenciamiento="Uso comercial permitido vía API; Acceptable Use Policy propia",
    ),
    Proveedor(
        nombre="Google AI Studio (directo)",
        tipo="directo",
        modelos_destacados=["Gemini 2.0/2.5 Flash", "Gemini Pro"],
        fortalezas="Multimodal nativo, contexto muy largo, tier gratuito generoso",
        consideraciones="Cuotas variables por región; features en preview cambian rápido",
        licenciamiento="Términos de Google AI Studio — distintos de Vertex AI",
    ),
    Proveedor(
        nombre="Azure OpenAI Service",
        tipo="hyperscaler",
        modelos_destacados=["GPT-4o", "GPT-4o-mini", "o1"],
        fortalezas="SLA empresarial, cumplimiento (SOC2/HIPAA), integración con Entra ID",
        consideraciones="Requiere aprobación de acceso; despliegue por región limitado",
        licenciamiento="Contrato Enterprise Agreement / CSP de Microsoft; datos no se usan para entrenar",
    ),
    Proveedor(
        nombre="Google Vertex AI / Gemini Enterprise Agent Platform",
        tipo="hyperscaler",
        modelos_destacados=["Gemini 2.0/2.5", "Llama (Model Garden)", "Claude (Model Garden)"],
        fortalezas="Model Garden con modelos de terceros, integración nativa con GCP, ADK para agentes",
        consideraciones="Curva de aprendizaje de IAM/roles de GCP; nombres de producto cambian con frecuencia",
        licenciamiento="Google Cloud Platform Terms of Service + términos específicos por modelo en Model Garden",
    ),
    Proveedor(
        nombre="AWS Bedrock",
        tipo="hyperscaler",
        modelos_destacados=["Claude (Anthropic)", "Llama (Meta)", "Titan", "Mistral"],
        fortalezas="Multi-proveedor en una sola API, Guardrails nativos, integración con IAM/VPC",
        consideraciones="Disponibilidad de modelos varía por región de AWS",
        licenciamiento="AWS Customer Agreement + términos del proveedor del modelo subyacente",
    ),
    Proveedor(
        nombre="Meta Llama (self-hosted / Model Garden)",
        tipo="directo",
        modelos_destacados=["Llama 3.2", "Llama 3.3 70B"],
        fortalezas="Licencia abierta, se puede auto-hospedar (Ollama, vLLM) sin costo por token",
        consideraciones="Requiere infraestructura propia para uso productivo a escala",
        licenciamiento="Llama Community License — uso comercial permitido con restricciones (>700M MAU requiere licencia especial)",
    ),
    Proveedor(
        nombre="Mistral AI",
        tipo="directo",
        modelos_destacados=["Mistral Large", "Mistral Small", "Mixtral 8x7B"],
        fortalezas="Buen balance costo/calidad, modelos abiertos (Apache 2.0) y propietarios",
        consideraciones="Ecosistema de tooling más pequeño que OpenAI/Anthropic",
        licenciamiento="Modelos abiertos bajo Apache 2.0; modelos premium vía API comercial",
    ),
]


def mostrar_panorama():
    """Imprime tabla comparativa del panorama de proveedores."""
    tabla = Table(title="Panorama de Proveedores de Inferencia LLM", show_lines=True)
    tabla.add_column("Proveedor", style="bold cyan")
    tabla.add_column("Tipo")
    tabla.add_column("Modelos destacados")
    tabla.add_column("Fortalezas")

    for p in CATALOGO_PROVEEDORES:
        tabla.add_row(
            p.nombre,
            p.tipo,
            ", ".join(p.modelos_destacados),
            p.fortalezas,
        )
    console.print(tabla)


def mostrar_licenciamiento():
    """Imprime detalle de términos de licenciamiento por proveedor."""
    console.print("\n[bold yellow]Términos clave de licenciamiento/uso[/bold yellow]\n")
    for p in CATALOGO_PROVEEDORES:
        console.print(f"[bold cyan]{p.nombre}[/bold cyan]")
        console.print(f"  Licenciamiento: {p.licenciamiento}")
        console.print(f"  Consideraciones: {p.consideraciones}\n")


def respuesta_simulada(proveedor: str, prompt: str) -> str:
    """Respuesta de ejemplo cuando no hay credenciales configuradas."""
    return (
        f"[MODO_SIMULADO] Respuesta simulada de {proveedor} para: '{prompt[:50]}...' "
        f"Configura las API keys en .env para llamadas reales."
    )


def llamar_openai(prompt: str) -> str:
    """Llamada real a OpenAI si hay API key; si no, modo simulado."""
    if MODO_SIMULADO or not os.getenv("OPENAI_API_KEY"):
        return respuesta_simulada("OpenAI", prompt)

    from openai import OpenAI
    cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    respuesta = cliente.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return respuesta.choices[0].message.content


def llamar_azure_openai(prompt: str) -> str:
    """Llamada real a Azure OpenAI si hay credenciales; si no, modo simulado.

    Azure OpenAI usa el mismo SDK de OpenAI pero con endpoint y auth distintos.
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

    if not (endpoint and api_key):
        return respuesta_simulada("Azure OpenAI", prompt)

    from openai import AzureOpenAI
    cliente = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-08-01-preview",
    )
    respuesta = cliente.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    return respuesta.choices[0].message.content


def llamar_bedrock(prompt: str) -> str:
    """Llamada real a AWS Bedrock (Claude) si hay credenciales; si no, modo simulado."""
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        return respuesta_simulada("AWS Bedrock (Claude)", prompt)

    try:
        import boto3
    except ImportError:
        return "[ERROR] Falta el paquete 'boto3'. Instálalo con: pip install boto3"
    import json

    cliente = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
    cuerpo = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    }
    respuesta = cliente.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(cuerpo),
    )
    resultado = json.loads(respuesta["body"].read())
    return resultado["content"][0]["text"]


def llamar_vertex_ai(prompt: str) -> str:
    """Llamada real a Vertex AI / Gemini Enterprise Agent Platform si hay credenciales."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        return respuesta_simulada("Vertex AI (Gemini)", prompt)

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
    except ImportError:
        return "[ERROR] Falta el paquete 'google-cloud-aiplatform'. Instálalo con: pip install google-cloud-aiplatform"

    vertexai.init(project=project_id, location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    modelo = GenerativeModel("gemini-2.0-flash")
    respuesta = modelo.generate_content(prompt)
    return respuesta.text


if __name__ == "__main__":
    console.print("[bold green]═══ Sesión 3: Panorama de Proveedores de Inferencia ═══[/bold green]\n")

    if MODO_SIMULADO:
        console.print("[yellow]⚠ MODO_SIMULADO activo — no se detectaron API keys en .env[/yellow]\n")

    mostrar_panorama()
    mostrar_licenciamiento()

    console.print("[bold green]═══ Prueba de llamadas por proveedor ═══[/bold green]\n")
    prompt_prueba = "Explica en una oración qué es la inferencia en el contexto de LLMs."

    console.print(f"OpenAI:        {llamar_openai(prompt_prueba)}")
    console.print(f"Azure OpenAI:  {llamar_azure_openai(prompt_prueba)}")
    console.print(f"AWS Bedrock:   {llamar_bedrock(prompt_prueba)}")
    console.print(f"Vertex AI:     {llamar_vertex_ai(prompt_prueba)}")
