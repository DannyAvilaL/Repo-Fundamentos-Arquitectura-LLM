"""
etica.py
========
Checklist estructurado de consideraciones éticas básicas para un PoC de
LLM — Sesión 5.

No pretende ser una auditoría de cumplimiento legal completa. Es una
herramienta de PoC: un conjunto mínimo de preguntas SÍ/NO/PARCIAL que el
equipo debe responder de forma explícita y guardar junto con cada corrida
de evaluación, para que la decisión de "avanzar o no" quede documentada
y no dependa de la memoria de una reunión.

Las categorías del checklist están mapeadas a dos marcos regulatorios/de
gobernanza reales, para que el estudiante entienda que esto no es una
lista inventada sino una simplificación de estándares reconocidos:

- NIST AI Risk Management Framework 1.0 (NIST, 2023, "AI Risk Management
  Framework (AI RMF 1.0)", U.S. Department of Commerce) — que organiza la
  gestión de riesgo de IA en cuatro funciones: GOBERNAR, MAPEAR, MEDIR y
  GESTIONAR. Este checklist cubre principalmente MAPEAR (identificar
  riesgos) y MEDIR (con las métricas de evaluacion.py).

- Reglamento de IA de la Unión Europea (Reglamento (UE) 2024/1689, "AI
  Act"), que clasifica los sistemas de IA en cuatro niveles de riesgo
  (inaceptable, alto, limitado, mínimo) según su caso de uso. Un asistente
  de soporte al cliente como "Tienda Andina" normalmente cae en riesgo
  limitado/mínimo, pero SOLO si se cumplen obligaciones básicas de
  transparencia (el usuario debe saber que habla con un sistema de IA).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Respuesta = Literal["si", "no", "parcial", "no_aplica"]


@dataclass
class ItemChecklist:
    id: str
    pregunta: str
    marco_referencia: str
    respuesta: Respuesta
    justificacion: str = ""


PREGUNTAS_CHECKLIST = [
    {
        "id": "transparencia_ia",
        "pregunta": "¿El usuario sabe explícitamente que está hablando con un sistema de IA y no con una persona?",
        "marco_referencia": "EU AI Act — obligación de transparencia para sistemas de riesgo limitado",
    },
    {
        "id": "escalamiento_humano",
        "pregunta": "¿Existe una ruta clara y visible para escalar a un humano cuando el sistema no puede o no debe responder?",
        "marco_referencia": "NIST AI RMF — función GESTIONAR (supervisión humana)",
    },
    {
        "id": "datos_sensibles",
        "pregunta": "¿El PoC evita solicitar o almacenar datos personales sensibles (salud, datos de pago completos, identificación) más allá de lo estrictamente necesario?",
        "marco_referencia": "NIST AI RMF — función MAPEAR (identificación de riesgos de privacidad)",
    },
    {
        "id": "sesgo_evaluado",
        "pregunta": "¿El dataset dorado incluye preguntas diseñadas para detectar respuestas sesgadas o discriminatorias, y se revisaron los resultados?",
        "marco_referencia": "NIST AI RMF — función MEDIR (equidad y sesgo)",
    },
    {
        "id": "limites_alcance",
        "pregunta": "¿El sistema tiene instrucciones y pruebas explícitas para rechazar solicitudes fuera de su alcance declarado?",
        "marco_referencia": "OWASP LLM06 (Excessive Agency, visto en Sesión 4) + NIST AI RMF GOBERNAR",
    },
    {
        "id": "registro_decisiones",
        "pregunta": "¿Cada corrida de evaluación queda registrada (fecha, dataset, resultados, quién la aprobó) para trazabilidad futura?",
        "marco_referencia": "NIST AI RMF — función GOBERNAR (documentación y trazabilidad)",
    },
    {
        "id": "plan_reentrenamiento",
        "pregunta": "¿Existe un plan mínimo para re-evaluar el sistema si el proveedor cambia de modelo (deprecation) o si el dataset dorado se queda desactualizado?",
        "marco_referencia": "NIST AI RMF — función GESTIONAR (monitoreo continuo)",
    },
]


def validar_checklist(respuestas: dict[str, dict]) -> list[ItemChecklist]:
    """Valida y normaliza las respuestas recibidas del frontend contra las
    preguntas oficiales del checklist. Lanza ValueError si falta una
    pregunta obligatoria o si la respuesta no es uno de los valores
    permitidos."""
    items = []
    ids_validos = {p["id"] for p in PREGUNTAS_CHECKLIST}
    for pregunta in PREGUNTAS_CHECKLIST:
        entrada = respuestas.get(pregunta["id"])
        if entrada is None:
            raise ValueError(f"Falta responder la pregunta obligatoria: '{pregunta['id']}'")
        respuesta = entrada.get("respuesta")
        if respuesta not in ("si", "no", "parcial", "no_aplica"):
            raise ValueError(
                f"Respuesta inválida para '{pregunta['id']}': debe ser si/no/parcial/no_aplica"
            )
        items.append(
            ItemChecklist(
                id=pregunta["id"],
                pregunta=pregunta["pregunta"],
                marco_referencia=pregunta["marco_referencia"],
                respuesta=respuesta,
                justificacion=entrada.get("justificacion", ""),
            )
        )
    extra = set(respuestas.keys()) - ids_validos
    if extra:
        raise ValueError(f"IDs de pregunta desconocidos: {extra}")
    return items


def resumen_checklist(items: list[ItemChecklist]) -> dict:
    conteo = {"si": 0, "no": 0, "parcial": 0, "no_aplica": 0}
    for item in items:
        conteo[item.respuesta] += 1
    bloqueantes = [i for i in items if i.respuesta == "no"]
    listo_para_avanzar = len(bloqueantes) == 0
    return {
        "conteo": conteo,
        "items_bloqueantes": [i.id for i in bloqueantes],
        "listo_para_avanzar": listo_para_avanzar,
        "recomendacion": (
            "El PoC NO debería avanzar a producción hasta resolver los ítems marcados 'no'."
            if not listo_para_avanzar
            else "No hay bloqueantes éticos identificados en este checklist mínimo — igual se recomienda revisión humana antes de producción."
        ),
        "generado_en": datetime.now(timezone.utc).isoformat(),
    }
