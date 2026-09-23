"""
evaluacion.py
=============
Harness de evaluación LIGERO para un PoC de LLM — Sesión 5.

Filosofía (a explicar en la sesión): un PoC no necesita un framework de
evaluación industrial completo como HELM (Liang et al., 2022,
arXiv:2211.09110) el primer día. Necesita un conjunto MÍNIMO de métricas
reproducibles, corridas contra un dataset dorado pequeño (10-30 ítems),
que le permitan a un equipo responder tres preguntas antes de escalar:
¿es lo bastante correcto?, ¿es lo bastante seguro?, ¿cuánto cuesta y
qué tan rápido es?

Métricas implementadas (todas sin dependencias pesadas — nada de
instalar un stack de NLP completo para un PoC):

1. Coincidencia por palabras clave (proxy ligero de superposición léxica,
   en el espíritu de ROUGE-L pero sin la dependencia `rouge-score`):
   mide qué fracción de las palabras significativas de la respuesta de
   referencia aparecen en la respuesta del modelo.

2. Detección heurística de cautela ("hedging"): para preguntas marcadas
   como `riesgo_alucinacion: alto` en el dataset dorado, se penaliza una
   respuesta que suena 100% segura sin ningún matiz cuando la referencia
   exige cautela (por ejemplo, "no tengo acceso en tiempo real a...").
   Esto opera como un proxy barato de faithfulness/groundedness, la
   dimensión que RAGAS mide de forma más rigurosa con NLI (Es et al.,
   2023, "Ragas: Automated Evaluation of Retrieval Augmented Generation",
   arXiv:2309.15217, EACL 2024) y que HELM reporta en su categoría de
   "robustness" (Liang et al., 2022).

3. Longitud relativa: respuestas desproporcionadamente cortas o largas
   frente a la referencia suelen indicar respuestas evasivas o
   verborrágicas — una señal barata de calidad que no requiere otro LLM.

4. (Opcional, deshabilitado por defecto) LLM-como-juez: usar un segundo
   LLM para puntuar 1-5 la corrección/fidelidad de la respuesta frente a
   la referencia. Esta técnica está documentada en G-Eval (Liu et al.,
   2023, "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment",
   arXiv:2303.16634, EMNLP 2023) y en Zheng et al. (2023, "Judging
   LLM-as-a-Judge with MT-Bench and Chatbot Arena", arXiv:2306.05685,
   NeurIPS 2023). Ambos papers documentan sesgos conocidos del método
   (sesgo de posición, sesgo de verbosidad, sesgo de auto-preferencia
   cuando el juez y el evaluado son el mismo proveedor) — por eso en
   este harness es OPCIONAL y nunca es la única señal: se combina
   siempre con las métricas 1-3, que son deterministas y gratuitas.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
    "al", "a", "en", "y", "o", "que", "es", "son", "por", "para", "con",
    "sin", "su", "sus", "se", "no", "sí", "si", "lo", "le", "les", "ya",
    "muy", "más", "menos", "como", "pero", "esto", "esta", "este", "esos",
}

FRASES_CAUTELA = [
    "no tengo acceso", "no puedo confirmar", "no tengo información",
    "te recomiendo verificar", "consulta con", "no dispongo de",
    "en tiempo real no", "no puedo garantizar", "sujeto a confirmación",
    "según el banco", "puede variar", "consultar la ficha",
]


def _tokenizar(texto: str) -> set[str]:
    palabras = re.findall(r"[a-záéíóúñ0-9]+", texto.lower())
    return {p for p in palabras if p not in STOPWORDS_ES and len(p) > 2}


@dataclass
class ResultadoMetrica:
    nombre: str
    puntaje: float  # 0.0 - 1.0
    detalle: str


@dataclass
class ResultadoEvaluacionItem:
    item_id: str
    categoria: str
    riesgo_alucinacion: str
    pregunta: str
    respuesta_modelo: str
    metricas: list[ResultadoMetrica] = field(default_factory=list)
    puntaje_compuesto: float = 0.0

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "categoria": self.categoria,
            "riesgo_alucinacion": self.riesgo_alucinacion,
            "pregunta": self.pregunta,
            "respuesta_modelo": self.respuesta_modelo,
            "metricas": [
                {"nombre": m.nombre, "puntaje": m.puntaje, "detalle": m.detalle}
                for m in self.metricas
            ],
            "puntaje_compuesto": self.puntaje_compuesto,
        }


def metrica_superposicion_lexica(respuesta: str, referencia: str) -> ResultadoMetrica:
    tokens_ref = _tokenizar(referencia)
    tokens_resp = _tokenizar(respuesta)
    if not tokens_ref:
        return ResultadoMetrica("superposicion_lexica", 0.0, "referencia vacía")
    interseccion = tokens_ref & tokens_resp
    puntaje = len(interseccion) / len(tokens_ref)
    return ResultadoMetrica(
        "superposicion_lexica",
        round(min(puntaje, 1.0), 3),
        f"{len(interseccion)}/{len(tokens_ref)} palabras clave de la referencia presentes en la respuesta",
    )


def metrica_cautela_apropiada(respuesta: str, riesgo_alucinacion: str) -> ResultadoMetrica:
    respuesta_lower = respuesta.lower()
    tiene_cautela = any(frase in respuesta_lower for frase in FRASES_CAUTELA)
    if riesgo_alucinacion != "alto":
        # No es un ítem de alto riesgo: no se exige cautela, puntaje neutro.
        return ResultadoMetrica(
            "cautela_apropiada", 1.0, "ítem de riesgo bajo/medio, no se exige lenguaje de cautela"
        )
    if tiene_cautela:
        return ResultadoMetrica(
            "cautela_apropiada", 1.0, "la respuesta reconoce apropiadamente sus límites (buena señal de faithfulness)"
        )
    return ResultadoMetrica(
        "cautela_apropiada",
        0.0,
        "ítem de alto riesgo de alucinación SIN lenguaje de cautela — posible respuesta inventada con exceso de confianza",
    )


def metrica_longitud_relativa(respuesta: str, referencia: str) -> ResultadoMetrica:
    len_resp, len_ref = len(respuesta.strip()), len(referencia.strip())
    if len_ref == 0:
        return ResultadoMetrica("longitud_relativa", 0.0, "referencia vacía")
    ratio = len_resp / len_ref
    if 0.4 <= ratio <= 2.5:
        puntaje = 1.0
    elif ratio < 0.4:
        puntaje = round(ratio / 0.4, 3)
    else:
        puntaje = round(max(0.0, 1 - (ratio - 2.5) / 5), 3)
    return ResultadoMetrica(
        "longitud_relativa",
        puntaje,
        f"respuesta {len_resp} caracteres vs. referencia {len_ref} caracteres (ratio {ratio:.2f})",
    )


PESOS_DEFECTO = {
    "superposicion_lexica": 0.45,
    "cautela_apropiada": 0.40,
    "longitud_relativa": 0.15,
}


def evaluar_item(
    item_id: str,
    categoria: str,
    riesgo_alucinacion: str,
    pregunta: str,
    respuesta_modelo: str,
    referencia: str,
    pesos: Optional[dict[str, float]] = None,
) -> ResultadoEvaluacionItem:
    pesos = pesos or PESOS_DEFECTO
    metricas = [
        metrica_superposicion_lexica(respuesta_modelo, referencia),
        metrica_cautela_apropiada(respuesta_modelo, riesgo_alucinacion),
        metrica_longitud_relativa(respuesta_modelo, referencia),
    ]
    puntaje_compuesto = sum(pesos.get(m.nombre, 0) * m.puntaje for m in metricas)
    resultado = ResultadoEvaluacionItem(
        item_id=item_id,
        categoria=categoria,
        riesgo_alucinacion=riesgo_alucinacion,
        pregunta=pregunta,
        respuesta_modelo=respuesta_modelo,
        metricas=metricas,
        puntaje_compuesto=round(puntaje_compuesto, 3),
    )
    return resultado


def resumen_corrida(resultados: list[ResultadoEvaluacionItem]) -> dict:
    if not resultados:
        return {"puntaje_promedio": 0.0, "items_evaluados": 0}
    promedio = sum(r.puntaje_compuesto for r in resultados) / len(resultados)
    riesgo_alto = [r for r in resultados if r.riesgo_alucinacion == "alto"]
    promedio_riesgo_alto = (
        sum(r.puntaje_compuesto for r in riesgo_alto) / len(riesgo_alto)
        if riesgo_alto
        else None
    )
    return {
        "items_evaluados": len(resultados),
        "puntaje_promedio": round(promedio, 3),
        "items_riesgo_alto": len(riesgo_alto),
        "puntaje_promedio_riesgo_alto": (
            round(promedio_riesgo_alto, 3) if promedio_riesgo_alto is not None else None
        ),
        "advertencia_riesgo_alto": (
            "El puntaje en ítems de alto riesgo de alucinación es la señal más importante "
            "para decidir si el PoC puede avanzar — un promedio general alto puede esconder "
            "fallas graves concentradas justo en las preguntas más sensibles."
        ),
    }
