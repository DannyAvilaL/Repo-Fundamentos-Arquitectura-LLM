"""
Sesion 2 — Ejemplo 04: Casos de Uso Empresariales
===================================================
Demostracion de 6 casos de uso reales con LLMs:

  1. Clasificacion de tickets de soporte
  2. Resumen de documentos legales / contratos
  3. Extraccion de datos estructurados (JSON)
  4. Analisis de sentimiento de feedback
  5. Asistente de codigo
  6. Generacion de reportes ejecutivos

Cada caso usa Ollama (local) o modo simulado.
"""

import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST   = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL", "llama3.2")
MODO_SIMULADO = os.getenv("MODO_SIMULADO", "false").lower() == "true"


# ──────────────────────────────────────────────────────────────────────────────
# Utilidad: llamar LLM
# ──────────────────────────────────────────────────────────────────────────────

def llm(
    prompt    : str,
    sistema   : str = "Eres un asistente empresarial experto. Responde SIEMPRE en espanol.",
    max_tokens: int = 400,
    simulado  : str = "",
) -> str:
    """
    Funcion unificada para llamar al LLM.
    Si Ollama no esta disponible o MODO_SIMULADO=True, devuelve texto simulado.
    """
    if MODO_SIMULADO or simulado:
        return simulado or f"[Simulado] Respuesta para: {prompt[:60]}..."

    try:
        respuesta = httpx.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model"   : OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": sistema},
                    {"role": "user",   "content": prompt},
                ],
                "stream" : False,
                "options": {"num_predict": max_tokens},
            },
            timeout=120,
        )
        return respuesta.json()["message"]["content"]
    except Exception as e:
        print(f"  ADVERTENCIA: Ollama no disponible ({e}). Usando simulacion.")
        return simulado or f"[Simulado] Respuesta para: {prompt[:60]}..."


def titulo(texto: str) -> None:
    print(f"\n{'='*65}")
    print(f"  CASO {texto}")
    print(f"{'='*65}")


# ──────────────────────────────────────────────────────────────────────────────
# CASO 1: Clasificacion de tickets de soporte
# ──────────────────────────────────────────────────────────────────────────────

TICKETS_EJEMPLO = [
    "No puedo acceder a mi cuenta desde ayer por la tarde, cuando ingreso mi contrasena dice 'invalid credentials'",
    "El sistema de facturacion genero un cobro doble en mi tarjeta de credito del mes pasado",
    "Como puedo exportar mis datos a formato Excel?",
    "La aplicacion se cae cada vez que intento subir un archivo mayor a 10MB",
    "Quiero cancelar mi suscripcion y solicitar reembolso del ultimo mes",
]

CATEGORIAS = ["acceso/autenticacion", "facturacion", "consulta/informacion", "bug/error-tecnico", "cancelacion"]

def clasificar_ticket(ticket: str) -> dict:
    """
    Clasifica un ticket de soporte en categoria y prioridad.
    Devuelve JSON estructurado.
    """
    prompt = f"""Clasifica este ticket de soporte tecnico.

Ticket: "{ticket}"

Categorias validas: {', '.join(CATEGORIAS)}
Prioridades: alta, media, baja

Responde SOLO con JSON valido, sin texto adicional:
{{
  "categoria": "...",
  "prioridad": "...",
  "resumen": "...(max 10 palabras)",
  "accion_recomendada": "...(max 15 palabras)"
}}"""

    simulado_map = {
        0: '{{"categoria": "acceso/autenticacion", "prioridad": "alta", "resumen": "Usuario no puede iniciar sesion", "accion_recomendada": "Restablecer credenciales y verificar estado de cuenta"}}',
        1: '{{"categoria": "facturacion", "prioridad": "alta", "resumen": "Cobro duplicado en tarjeta", "accion_recomendada": "Verificar transacciones y procesar reembolso"}}',
        2: '{{"categoria": "consulta/informacion", "prioridad": "baja", "resumen": "Consulta sobre exportacion de datos", "accion_recomendada": "Enviar documentacion de la funcion de exportacion"}}',
        3: '{{"categoria": "bug/error-tecnico", "prioridad": "alta", "resumen": "App se cierra con archivos grandes", "accion_recomendada": "Escalar a equipo tecnico, verificar limite de carga"}}',
        4: '{{"categoria": "cancelacion", "prioridad": "media", "resumen": "Solicitud de cancelacion y reembolso", "accion_recomendada": "Confirmar proceso de cancelacion y politica de reembolso"}}',
    }

    idx = TICKETS_EJEMPLO.index(ticket) if ticket in TICKETS_EJEMPLO else 0
    texto = llm(prompt, max_tokens=150, simulado=simulado_map.get(idx, ""))

    try:
        # Extraer JSON si viene con texto alrededor
        inicio = texto.find("{")
        fin    = texto.rfind("}") + 1
        return json.loads(texto[inicio:fin]) if inicio >= 0 else {"raw": texto}
    except json.JSONDecodeError:
        return {"raw": texto}


# ──────────────────────────────────────────────────────────────────────────────
# CASO 2: Resumen de documentos legales
# ──────────────────────────────────────────────────────────────────────────────

CONTRATO_EJEMPLO = """
CONTRATO DE SERVICIOS PROFESIONALES

Entre las partes: TechCorp S.A. (en adelante "El Proveedor") con NIT 900.123.456-7,
y Empresa ABC Ltda. (en adelante "El Cliente") con NIT 800.987.654-3.

OBJETO: El Proveedor se compromete a desarrollar un sistema de gestion de inventarios
con las siguientes caracteristicas: modulo de entrada/salida de productos, integracion
con codigo de barras, reportes en tiempo real y dashboard ejecutivo.

PLAZO: 4 meses calendario contados desde la firma del contrato.

VALOR: $45.000.000 COP pagaderos en 3 cuotas: 40% inicio, 30% entrega parcial,
30% entrega final.

GARANTIA: 6 meses de soporte tecnico incluidos. Defectos criticos se atienden en 24h,
los no criticos en 5 dias habiles.

PENALIZACIONES: Por retraso en entrega, 0.5% del valor total por semana de retraso,
con maximo del 10%.

PROPIEDAD INTELECTUAL: El codigo fuente pasa a ser propiedad del Cliente tras el
pago total. El Proveedor conserva el derecho de usar tecnologias y frameworks propios.

CONFIDENCIALIDAD: Ambas partes se comprometen a no divulgar informacion sensible
durante y hasta 2 anos despues de finalizado el contrato.
"""

def resumir_contrato(texto: str) -> str:
    prompt = f"""Analiza este contrato y extrae los puntos mas importantes para un ejecutivo.

CONTRATO:
{texto}

Proporciona un resumen ejecutivo con:
1. Partes involucradas
2. Que se entrega
3. Cuando y cuanto cuesta
4. Riesgos o clausulas importantes
5. Recomendacion (aprobar/revisar/rechazar)

Maximo 200 palabras."""

    simulado = """Resumen Ejecutivo del Contrato:

1. PARTES: TechCorp S.A. (proveedor) y Empresa ABC Ltda. (cliente).

2. ENTREGABLE: Sistema de gestion de inventarios con modulo de productos,
   codigo de barras, reportes y dashboard.

3. TERMINOS ECONOMICOS: $45M COP en 4 meses. Pago en 3 cuotas (40/30/30%).

4. CLAUSULAS IMPORTANTES:
   - Garantia 6 meses con SLA de 24h para criticos
   - Penalizacion 0.5%/semana de retraso (max 10%)
   - IP pasa al cliente solo tras pago total
   - Confidencialidad por 2 anos

5. RECOMENDACION: REVISAR. Verificar que el plazo de 4 meses es realista
   para el alcance definido. Considerar agregar clausula de alcance detallado
   para evitar disputas sobre funcionalidades."""

    return llm(prompt, max_tokens=300, simulado=simulado)


# ──────────────────────────────────────────────────────────────────────────────
# CASO 3: Extraccion de datos estructurados
# ──────────────────────────────────────────────────────────────────────────────

FACTURA_TEXTO = """
Recibo del restaurante El Buen Sabor
Fecha: 15 de marzo de 2025
Mesa: 7 - Mesero: Carlos Rodriguez

  2x Bandeja Paisa           $28.000
  1x Ajiaco Santafereno      $22.000
  3x Limonada Natural         $9.000
  1x Postre del dia           $8.000

Subtotal:                    $67.000
Descuento empleado (15%):   -$10.050
IVA (19%):                  $12.730
TOTAL:                       $69.680

Metodo de pago: Tarjeta Debito
Propina voluntaria (incluida): $7.000
"""

def extraer_datos_factura(texto: str) -> dict:
    prompt = f"""Extrae los datos de esta factura y devuelve SOLO JSON valido.

FACTURA:
{texto}

JSON esperado:
{{
  "establecimiento": "...",
  "fecha": "YYYY-MM-DD",
  "items": [
    {{"descripcion": "...", "cantidad": 0, "precio_unitario": 0, "subtotal": 0}}
  ],
  "subtotal": 0,
  "descuento": 0,
  "iva": 0,
  "total": 0,
  "metodo_pago": "...",
  "propina": 0
}}"""

    simulado = json.dumps({
        "establecimiento": "El Buen Sabor",
        "fecha"          : "2025-03-15",
        "items": [
            {"descripcion": "Bandeja Paisa",       "cantidad": 2, "precio_unitario": 14000, "subtotal": 28000},
            {"descripcion": "Ajiaco Santafereno",  "cantidad": 1, "precio_unitario": 22000, "subtotal": 22000},
            {"descripcion": "Limonada Natural",    "cantidad": 3, "precio_unitario": 3000,  "subtotal": 9000},
            {"descripcion": "Postre del dia",      "cantidad": 1, "precio_unitario": 8000,  "subtotal": 8000},
        ],
        "subtotal"   : 67000,
        "descuento"  : 10050,
        "iva"        : 12730,
        "total"      : 69680,
        "metodo_pago": "Tarjeta Debito",
        "propina"    : 7000,
    }, ensure_ascii=False, indent=2)

    texto_resp = llm(prompt, max_tokens=400, simulado=simulado)
    try:
        i = texto_resp.find("{")
        f = texto_resp.rfind("}") + 1
        return json.loads(texto_resp[i:f])
    except Exception:
        return {"raw": texto_resp}


# ──────────────────────────────────────────────────────────────────────────────
# CASO 4: Analisis de sentimiento
# ──────────────────────────────────────────────────────────────────────────────

REVIEWS_EJEMPLO = [
    "Excelente servicio, el equipo de soporte resolvio mi problema en menos de una hora. Definitivamente lo recomiendo.",
    "El producto tiene bugs que reportamos hace 3 meses y todavia no los han solucionado. Muy decepcionante.",
    "Funciona bien para lo basico, pero le faltan algunas funciones avanzadas que necesitamos.",
    "La interfaz es intuitiva y el precio es justo para lo que ofrece.",
]

def analizar_sentimiento_batch(reviews: list[str]) -> list[dict]:
    """Analiza multiples reviews de una vez (batch processing)."""
    reviews_numeradas = "\n".join([f"{i+1}. {r}" for i, r in enumerate(reviews)])

    prompt = f"""Analiza el sentimiento de cada review. Devuelve SOLO JSON valido.

REVIEWS:
{reviews_numeradas}

Formato esperado (array):
[
  {{
    "id": 1,
    "sentimiento": "positivo|negativo|neutro",
    "puntuacion": 1-5,
    "temas_mencionados": ["tema1", "tema2"],
    "accion_requerida": "urgente|monitorear|ninguna"
  }}
]"""

    simulado = json.dumps([
        {"id": 1, "sentimiento": "positivo", "puntuacion": 5, "temas_mencionados": ["soporte", "velocidad"], "accion_requerida": "ninguna"},
        {"id": 2, "sentimiento": "negativo", "puntuacion": 1, "temas_mencionados": ["bugs", "tiempo-respuesta"], "accion_requerida": "urgente"},
        {"id": 3, "sentimiento": "neutro",   "puntuacion": 3, "temas_mencionados": ["funcionalidad", "precio"], "accion_requerida": "monitorear"},
        {"id": 4, "sentimiento": "positivo", "puntuacion": 4, "temas_mencionados": ["interfaz", "precio"], "accion_requerida": "ninguna"},
    ], ensure_ascii=False, indent=2)

    texto_resp = llm(prompt, max_tokens=500, simulado=simulado)
    try:
        i = texto_resp.find("[")
        f = texto_resp.rfind("]") + 1
        return json.loads(texto_resp[i:f])
    except Exception:
        return [{"raw": texto_resp}]


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSESION 2 — EJEMPLO 04: CASOS DE USO EMPRESARIALES")

    # CASO 1
    titulo("1: CLASIFICACION DE TICKETS DE SOPORTE")
    print(f"\n  Modelo: {OLLAMA_MODEL} | Procesando {len(TICKETS_EJEMPLO)} tickets...")
    for ticket in TICKETS_EJEMPLO:
        resultado = clasificar_ticket(ticket)
        print(f"\n  Ticket : {ticket[:60]}...")
        print(f"  Categ  : {resultado.get('categoria', '?')}")
        print(f"  Prior  : {resultado.get('prioridad', '?')}")
        print(f"  Accion : {resultado.get('accion_recomendada', '?')}")

    # CASO 2
    titulo("2: RESUMEN DE CONTRATO LEGAL")
    print("\n  Analizando contrato de servicios...")
    resumen = resumir_contrato(CONTRATO_EJEMPLO)
    print(f"\n{resumen}")

    # CASO 3
    titulo("3: EXTRACCION DE DATOS ESTRUCTURADOS (FACTURA)")
    print("\n  Extrayendo datos de factura de restaurante...")
    datos = extraer_datos_factura(FACTURA_TEXTO)
    if "items" in datos:
        print(f"\n  Establecimiento: {datos.get('establecimiento')}")
        print(f"  Fecha          : {datos.get('fecha')}")
        print(f"  Items          : {len(datos.get('items', []))}")
        print(f"  Total          : ${datos.get('total', 0):,}")
        print(f"  Pago           : {datos.get('metodo_pago')}")
    else:
        print(f"\n  {datos}")

    # CASO 4
    titulo("4: ANALISIS DE SENTIMIENTO — BATCH REVIEWS")
    print(f"\n  Analizando {len(REVIEWS_EJEMPLO)} reviews de clientes...")
    resultados = analizar_sentimiento_batch(REVIEWS_EJEMPLO)
    emojis = {"positivo": "✓", "negativo": "✗", "neutro": "~"}
    for r, review in zip(resultados, REVIEWS_EJEMPLO):
        emoji = emojis.get(r.get("sentimiento", ""), "?")
        print(f"\n  {emoji} [{r.get('puntuacion', '?')}/5] {review[:55]}...")
        print(f"    Sentimiento: {r.get('sentimiento')} | Accion: {r.get('accion_requerida')}")
        temas = r.get('temas_mencionados', [])
        if temas:
            print(f"    Temas: {', '.join(temas)}")

    # Resumen
    print(f"\n{'='*65}")
    print("  RESUMEN DE CASOS DE USO VISTOS:")
    print("""
  1. Clasificacion de tickets  — Reduce tiempo de triaje 70%
  2. Resumen documentos        — Analiza contratos en segundos
  3. Extraccion estructurada   — JSON desde texto no estructurado
  4. Analisis de sentimiento   — Monitoreo automatico de feedback

  Todos estos casos pueden ejecutarse con modelos LOCALES (Ollama)
  para datos confidenciales, sin costo de API y sin salir de la red.
    """)


if __name__ == "__main__":
    main()
