"""
Sesion 2 — Ejemplo 05: API Gestionada vs Self-Hosted
=====================================================
Analisis completo de las dos modalidades de consumo de LLMs:

  API GESTIONADA (Cloud):
    - OpenAI, Anthropic, Google
    - Sin infraestructura, pago por uso
    - SLA garantizado, actualizaciones automaticas

  SELF-HOSTED (Ollama / vLLM / llama.cpp):
    - Modelo corre en tu servidor o PC
    - Costo fijo de infraestructura
    - Control total, datos nunca salen de tu red

Este ejemplo simula una decision empresarial real comparando ambas opciones.
"""

import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

MODO_SIMULADO = os.getenv("MODO_SIMULADO", "false").lower() == "true"


# ──────────────────────────────────────────────────────────────────────────────
# Modelo de datos
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class EscenarioEmpresa:
    nombre           : str
    tokens_mes       : int          # tokens procesados por mes
    datos_sensibles  : bool         # si los datos son confidenciales
    equipo_devops    : bool         # si tienen equipo para mantener infraestructura
    presupuesto_usd  : float        # presupuesto mensual disponible para IA
    latencia_max_ms  : int          # latencia maxima tolerable en ms
    disponibilidad   : float        # uptime requerido (0.0-1.0)


@dataclass
class OpcionDeployment:
    nombre           : str
    tipo             : str          # "cloud" | "local"
    costo_fijo_mes   : float        # USD/mes de infraestructura
    costo_por_mtoken : float        # USD por millon de tokens (0 si local)
    latencia_p50_ms  : int          # latencia mediana en ms
    latencia_p99_ms  : int          # latencia p99 en ms
    uptime           : float        # SLA como decimal
    setup_dias       : int          # dias para llegar a produccion
    pros             : list
    contras          : list


OPCIONES = [
    OpcionDeployment(
        nombre           = "OpenAI GPT-4o-mini",
        tipo             = "cloud",
        costo_fijo_mes   = 0.0,
        costo_por_mtoken = 0.375,   # promedio input+output
        latencia_p50_ms  = 800,
        latencia_p99_ms  = 3000,
        uptime           = 0.9995,
        setup_dias       = 1,
        pros             = [
            "Sin infraestructura",
            "Siempre ultima version",
            "SLA 99.95% garantizado",
            "Soporte enterprise disponible",
        ],
        contras          = [
            "Datos salen de tu red",
            "Costo variable (puede dispararse)",
            "Dependencia del proveedor",
            "Latencia variable",
        ],
    ),
    OpcionDeployment(
        nombre           = "Ollama + Llama3.2 (PC local)",
        tipo             = "local",
        costo_fijo_mes   = 15.0,    # electricidad aprox
        costo_por_mtoken = 0.0,
        latencia_p50_ms  = 2500,
        latencia_p99_ms  = 6000,
        uptime           = 0.95,    # depende de tu PC
        setup_dias       = 1,
        pros             = [
            "Gratis despues del setup",
            "Datos nunca salen de tu equipo",
            "Funciona sin internet",
            "Perfecto para desarrollo y pruebas",
        ],
        contras          = [
            "Calidad menor a GPT-4o",
            "Lento sin GPU dedicada",
            "Debes mantener el servicio",
            "Sin SLA garantizado",
        ],
    ),
    OpcionDeployment(
        nombre           = "Ollama + Llama3.1 (Servidor GPU)",
        tipo             = "local",
        costo_fijo_mes   = 350.0,   # servidor con GPU A100 cloud
        costo_por_mtoken = 0.0,
        latencia_p50_ms  = 400,
        latencia_p99_ms  = 1200,
        uptime           = 0.99,
        setup_dias       = 7,
        pros             = [
            "Alta velocidad (GPU dedicada)",
            "Datos privados",
            "Costo fijo predecible",
            "Escalable horizontalmente",
        ],
        contras          = [
            "Inversion inicial alta",
            "Requiere equipo DevOps",
            "Mantenimiento continuo",
            "Actualizaciones manuales",
        ],
    ),
    OpcionDeployment(
        nombre           = "Anthropic Claude Haiku",
        tipo             = "cloud",
        costo_fijo_mes   = 0.0,
        costo_por_mtoken = 0.75,
        latencia_p50_ms  = 600,
        latencia_p99_ms  = 2500,
        uptime           = 0.9999,
        setup_dias       = 1,
        pros             = [
            "El mas rapido del mercado",
            "200K tokens de contexto",
            "SLA 99.99%",
            "Muy economico para su calidad",
        ],
        contras          = [
            "Datos en servidores Anthropic",
            "Costo acumula con volumen",
            "Dependencia del proveedor",
        ],
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Motor de analisis
# ──────────────────────────────────────────────────────────────────────────────

def calcular_costo_total(opcion: OpcionDeployment, tokens_mes: int) -> float:
    """Calcula costo total mensual de una opcion para un volumen dado."""
    costo_tokens = (tokens_mes / 1_000_000) * opcion.costo_por_mtoken
    return opcion.costo_fijo_mes + costo_tokens


def puntaje_opcion(opcion: OpcionDeployment, empresa: EscenarioEmpresa) -> float:
    """
    Calcula un puntaje de 0-100 para una opcion dado el perfil de la empresa.
    Criterios ponderados:
      - Costo         (30%)
      - Privacidad    (25%)
      - Latencia      (20%)
      - Disponibilidad(15%)
      - Facilidad     (10%)
    """
    costo_total = calcular_costo_total(opcion, empresa.tokens_mes)

    # Costo: mas barato = mejor puntaje (normalizado)
    costo_max  = empresa.presupuesto_usd * 2
    puntaje_costo = max(0, 1 - (costo_total / costo_max)) * 30

    # Privacidad: si datos son sensibles, local gana mucho
    if empresa.datos_sensibles:
        puntaje_privacidad = 25.0 if opcion.tipo == "local" else 5.0
    else:
        puntaje_privacidad = 20.0  # neutral si no son sensibles

    # Latencia: menor latencia = mayor puntaje
    lat_ratio = min(1, empresa.latencia_max_ms / opcion.latencia_p50_ms)
    puntaje_latencia = lat_ratio * 20

    # Disponibilidad
    puntaje_disponibilidad = (opcion.uptime / empresa.disponibilidad) * 15
    puntaje_disponibilidad = min(15, puntaje_disponibilidad)

    # Facilidad de setup
    puntaje_facilidad = max(0, 10 - opcion.setup_dias) if not empresa.equipo_devops else 10
    if not empresa.equipo_devops and opcion.tipo == "local" and opcion.setup_dias > 1:
        puntaje_facilidad = 2

    return round(puntaje_costo + puntaje_privacidad + puntaje_latencia + puntaje_disponibilidad + puntaje_facilidad, 1)


def recomendar(empresa: EscenarioEmpresa) -> None:
    """Analiza el perfil de la empresa y recomienda la mejor opcion."""
    print(f"\n  Empresa         : {empresa.nombre}")
    print(f"  Volumen         : {empresa.tokens_mes:,} tokens/mes")
    print(f"  Datos sensibles : {'Si' if empresa.datos_sensibles else 'No'}")
    print(f"  Equipo DevOps   : {'Si' if empresa.equipo_devops else 'No'}")
    print(f"  Presupuesto     : ${empresa.presupuesto_usd:,.0f}/mes")
    print(f"  Latencia max    : {empresa.latencia_max_ms}ms")

    print(f"\n  {'Opcion':<35} {'Costo/mes':<14} {'Latencia':<12} {'Uptime':<10} {'Puntaje'}")
    print(f"  {'─'*80}")

    resultados = []
    for opcion in OPCIONES:
        costo   = calcular_costo_total(opcion, empresa.tokens_mes)
        puntaje = puntaje_opcion(opcion, empresa)
        resultados.append((opcion, costo, puntaje))
        print(f"  {opcion.nombre:<35} ${costo:<13,.2f} {opcion.latencia_p50_ms}ms{'':<7} {opcion.uptime*100:.2f}%{'':<3} {puntaje}/100")

    ganador = max(resultados, key=lambda x: x[2])
    print(f"\n  RECOMENDACION: {ganador[0].nombre}")
    print(f"  Puntaje: {ganador[2]}/100 | Costo estimado: ${ganador[1]:,.2f}/mes")


# ──────────────────────────────────────────────────────────────────────────────
# Escenarios de ejemplo
# ──────────────────────────────────────────────────────────────────────────────

ESCENARIOS = [
    EscenarioEmpresa(
        nombre           = "Startup EdTech — Chatbot de tutoria",
        tokens_mes       = 2_000_000,
        datos_sensibles  = False,
        equipo_devops    = False,
        presupuesto_usd  = 300.0,
        latencia_max_ms  = 2000,
        disponibilidad   = 0.99,
    ),
    EscenarioEmpresa(
        nombre           = "Banco Regional — Analisis de credito",
        tokens_mes       = 50_000_000,
        datos_sensibles  = True,
        equipo_devops    = True,
        presupuesto_usd  = 5000.0,
        latencia_max_ms  = 3000,
        disponibilidad   = 0.9999,
    ),
    EscenarioEmpresa(
        nombre           = "Clinica — Resumen de historiales",
        tokens_mes       = 5_000_000,
        datos_sensibles  = True,
        equipo_devops    = False,
        presupuesto_usd  = 500.0,
        latencia_max_ms  = 5000,
        disponibilidad   = 0.99,
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\nSESION 2 — EJEMPLO 05: API GESTIONADA VS SELF-HOSTED")

    # Comparativa de opciones
    print(f"\n{'='*65}")
    print("  OPCIONES DISPONIBLES")
    print(f"{'='*65}")

    for opcion in OPCIONES:
        tipo_label = "CLOUD" if opcion.tipo == "cloud" else "LOCAL"
        print(f"\n  [{tipo_label}] {opcion.nombre}")
        print(f"    Costo fijo : ${opcion.costo_fijo_mes}/mes")
        if opcion.costo_por_mtoken > 0:
            print(f"    Costo uso  : ${opcion.costo_por_mtoken}/MTok")
        print(f"    Latencia   : {opcion.latencia_p50_ms}ms (p50) / {opcion.latencia_p99_ms}ms (p99)")
        print(f"    Setup      : {opcion.setup_dias} dia(s)")
        print(f"    Pros       : {' | '.join(opcion.pros[:2])}")

    # Analisis por escenario
    print(f"\n{'='*65}")
    print("  RECOMENDACIONES POR ESCENARIO EMPRESARIAL")
    print(f"{'='*65}")

    for escenario in ESCENARIOS:
        recomendar(escenario)
        print()

    # Tabla de decision rapida
    print(f"\n{'='*65}")
    print("  TABLA DE DECISION RAPIDA")
    print(f"{'='*65}")
    print("""
  Situacion                              Recomendacion
  ──────────────────────────────────────────────────────────
  Datos confidenciales (HIPAA, GDPR)     Self-Hosted (Ollama)
  Volumen < 5M tokens/mes                API Cloud
  Volumen > 50M tokens/mes               Self-Hosted con GPU
  Sin equipo DevOps                      API Cloud
  Latencia < 1 segundo critica           API Cloud (Claude Haiku)
  Prototipo / desarrollo                 Ollama local
  Produccion con SLA 99.99%              API Cloud enterprise
  Regulacion financiera / bancaria       Self-Hosted
  Startup con presupuesto limitado       Ollama local + API cloud para produccion

  PATRON MAS COMUN EN EMPRESAS:
    Desarrollo  : Ollama local (gratis, rapido de probar)
    Staging     : Ollama en servidor (replica produccion sin costo)
    Produccion  : API Cloud para calidad o Self-Hosted para privacidad
    """)


if __name__ == "__main__":
    main()
