"""
registro.py
===========
Registro de resultados y comparativas — Sesión 5.

Persistencia deliberadamente simple: un archivo JSON append-only
(`runs_log.json`). Para un PoC, una base de datos completa (Postgres)
es sobre-ingeniería — el objetivo de este módulo es que CADA corrida
quede trazada (qué dataset, qué proveedor, qué resultados, qué costo,
quién aprobó el checklist de ética) para poder compararlas después,
no montar infraestructura de producción.

Si este PoC avanza a producción, el mismo esquema de "run" se puede
migrar a una tabla de Postgres sin cambiar la forma de los datos.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LOG_PATH = Path(__file__).parent / "runs_log.json"


def _leer_log() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        contenido = f.read().strip()
        return json.loads(contenido) if contenido else []


def _escribir_log(runs: list[dict]) -> None:
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=2)


def registrar_corrida(
    proveedor: str,
    modelo: str,
    resumen_evaluacion: dict,
    costo_total_usd: float,
    latencia_promedio_segundos: float,
    checklist_etica: Optional[dict] = None,
    aprobado_por: Optional[str] = None,
) -> dict:
    run = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proveedor": proveedor,
        "modelo": modelo,
        "resumen_evaluacion": resumen_evaluacion,
        "costo_total_usd": costo_total_usd,
        "latencia_promedio_segundos": latencia_promedio_segundos,
        "checklist_etica": checklist_etica,
        "aprobado_por": aprobado_por,
    }
    runs = _leer_log()
    runs.append(run)
    _escribir_log(runs)
    return run


def listar_corridas() -> list[dict]:
    return _leer_log()


def comparativa_por_proveedor() -> list[dict]:
    """Agrupa las corridas registradas por proveedor+modelo y calcula
    promedios — es la vista que alimenta la tabla comparativa del
    frontend ('Registro de resultados y comparativas')."""
    runs = _leer_log()
    agrupado: dict[str, dict] = {}
    for run in runs:
        clave = f"{run['proveedor']}:{run['modelo']}"
        grupo = agrupado.setdefault(
            clave,
            {
                "proveedor": run["proveedor"],
                "modelo": run["modelo"],
                "corridas": 0,
                "suma_puntaje": 0.0,
                "suma_costo_usd": 0.0,
                "suma_latencia_segundos": 0.0,
            },
        )
        grupo["corridas"] += 1
        grupo["suma_puntaje"] += run["resumen_evaluacion"].get("puntaje_promedio", 0.0)
        grupo["suma_costo_usd"] += run.get("costo_total_usd", 0.0)
        grupo["suma_latencia_segundos"] += run.get("latencia_promedio_segundos", 0.0)

    comparativa = []
    for grupo in agrupado.values():
        n = grupo["corridas"]
        comparativa.append(
            {
                "proveedor": grupo["proveedor"],
                "modelo": grupo["modelo"],
                "corridas": n,
                "puntaje_promedio": round(grupo["suma_puntaje"] / n, 3),
                "costo_promedio_usd": round(grupo["suma_costo_usd"] / n, 6),
                "latencia_promedio_segundos": round(grupo["suma_latencia_segundos"] / n, 3),
            }
        )
    # Orden sugerido: mejor puntaje primero, luego menor costo.
    comparativa.sort(key=lambda r: (-r["puntaje_promedio"], r["costo_promedio_usd"]))
    return comparativa
