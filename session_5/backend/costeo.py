"""
costeo.py
=========
Módulo de estimación de costos para un PoC — Sesión 5.

Objetivo de desempeño de la sesión: "Diseñar [...] un estimado de
costos/tiempos para un PoC simple con LLM". Este módulo traduce tokens
de entrada/salida en costo real por llamada, y proyecta ese costo a
escala (por ejemplo, "¿cuánto costaría este PoC si lo usan 500 usuarios,
10 veces al mes cada uno?").

IMPORTANTE (a remarcar en la sesión): estas tarifas son de ejemplo y
DEBEN actualizarse contra la documentación de pricing vigente del
proveedor antes de tomar una decisión real — los precios de LLMs
cambian con frecuencia. Por eso cada tarifa incluye un campo
`fecha_referencia` y el archivo entero es un JSON editable, no una
constante enterrada en el código (mismo principio que se usó para las
tablas de precios de la Sesión 1/3).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

TARIFAS_PATH = Path(__file__).parent / "tarifas_ejemplo.json"


@dataclass
class EstimacionCosto:
    proveedor: str
    modelo: str
    tokens_entrada: int
    tokens_salida: int
    costo_entrada_usd: float
    costo_salida_usd: float
    costo_total_usd: float
    fecha_referencia_tarifa: str
    nota: str


def _cargar_tarifas() -> dict:
    with open(TARIFAS_PATH, encoding="utf-8") as f:
        return json.load(f)


def calcular_costo_llamada(
    proveedor: str,
    modelo: str,
    tokens_entrada: int,
    tokens_salida: int,
) -> EstimacionCosto:
    tarifas = _cargar_tarifas()
    clave = f"{proveedor}:{modelo}"
    tarifa = tarifas.get(clave) or tarifas.get(f"{proveedor}:__default__")
    if tarifa is None:
        return EstimacionCosto(
            proveedor=proveedor,
            modelo=modelo,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida,
            costo_entrada_usd=0.0,
            costo_salida_usd=0.0,
            costo_total_usd=0.0,
            fecha_referencia_tarifa="N/A",
            nota=f"Sin tarifa registrada para '{clave}' en tarifas_ejemplo.json — costo reportado como 0.",
        )
    # Tarifas expresadas en USD por cada 1,000,000 de tokens (convención de
    # la mayoría de los proveedores en su documentación de pricing).
    costo_entrada = (tokens_entrada / 1_000_000) * tarifa["usd_por_millon_entrada"]
    costo_salida = (tokens_salida / 1_000_000) * tarifa["usd_por_millon_salida"]
    return EstimacionCosto(
        proveedor=proveedor,
        modelo=modelo,
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
        costo_entrada_usd=round(costo_entrada, 8),
        costo_salida_usd=round(costo_salida, 8),
        costo_total_usd=round(costo_entrada + costo_salida, 8),
        fecha_referencia_tarifa=tarifa.get("fecha_referencia", "sin fecha"),
        nota=tarifa.get("nota", ""),
    )


def proyectar_costo_poc(
    costo_por_llamada_usd: float,
    usuarios_estimados: int,
    llamadas_por_usuario_mes: int,
) -> dict:
    """Proyecta el costo mensual y anual de un PoC dado un costo promedio
    por llamada y un volumen esperado de uso."""
    llamadas_mes = usuarios_estimados * llamadas_por_usuario_mes
    costo_mes = llamadas_mes * costo_por_llamada_usd
    return {
        "usuarios_estimados": usuarios_estimados,
        "llamadas_por_usuario_mes": llamadas_por_usuario_mes,
        "llamadas_totales_mes": llamadas_mes,
        "costo_estimado_mes_usd": round(costo_mes, 2),
        "costo_estimado_anio_usd": round(costo_mes * 12, 2),
        "advertencia": (
            "Proyección lineal simple para un PoC — no incluye descuentos por volumen, "
            "costos de infraestructura (Cloud Run, base de datos, etc.), reintentos por "
            "fallos, ni el costo de las llamadas de evaluación con LLM-como-juez si se activa."
        ),
    }
