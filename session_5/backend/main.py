"""
main.py
=======
Backend FastAPI de la Sesión 5 — Evaluación, Costeo y Ética en el Uso de LLM.

Endpoints:
- GET  /api/dataset            → devuelve el dataset dorado (10 ítems, dominio Tienda Andina)
- POST /api/evaluar             → corre el dataset dorado completo contra un proveedor y registra la corrida
- POST /api/costeo/proyeccion   → proyecta costo mensual/anual dado un costo por llamada y volumen esperado
- GET  /api/checklist/preguntas → devuelve las preguntas del checklist ético
- POST /api/checklist/validar   → valida y resume un checklist de ética respondido
- GET  /api/registro            → lista todas las corridas registradas
- GET  /api/registro/comparativa→ comparativa agregada por proveedor/modelo (para el dashboard React)

Sigue las mismas prácticas de las sesiones anteriores del curso:
- Todas las credenciales vía variables de entorno (ver .env.example), nunca hardcodeadas.
- Rate limiting con slowapi para simular una condición mínima de producción.
- CORS abierto solo al origen del frontend de desarrollo (Vite).
- Modo simulado automático si no hay API key (ver proveedores.py) — el PoC completo
  se puede ejecutar y evaluar sin gastar un centavo ni tener credenciales.
"""
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import costeo
import etica
import evaluacion
import proveedores
import registro
import json
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "dataset_dorado.json"

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Sesión 5 — Evaluación, Costeo y Ética en el Uso de LLM",
    description="API de soporte para el PoC de evaluación ligera de la Sesión 5 (Fundamentos de Arquitectura LLM).",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origenes_permitidos = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cargar_dataset() -> dict:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Modelos Pydantic
# ---------------------------------------------------------------------------
class SolicitudEvaluar(BaseModel):
    proveedor: str = Field(..., description="openai | anthropic | google | ollama")
    modelo: Optional[str] = Field(None, description="Modelo específico; si se omite, usa el default del proveedor")
    aprobado_por: Optional[str] = Field(None, description="Nombre de quien aprueba/registra esta corrida")


class SolicitudProyeccionCosto(BaseModel):
    costo_por_llamada_usd: float = Field(..., ge=0)
    usuarios_estimados: int = Field(..., gt=0)
    llamadas_por_usuario_mes: int = Field(..., gt=0)


class SolicitudChecklist(BaseModel):
    respuestas: dict[str, dict]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def raiz():
    return {
        "servicio": "Sesión 5 — Evaluación, Costeo y Ética",
        "estado": "ok",
        "documentacion": "/docs",
    }


@app.get("/api/dataset")
@limiter.limit("30/minute")
def obtener_dataset(request: Request):
    return _cargar_dataset()


@app.post("/api/evaluar")
@limiter.limit("10/minute")
def evaluar(request: Request, solicitud: SolicitudEvaluar):
    if solicitud.proveedor not in proveedores.PROVEEDORES:
        raise HTTPException(
            status_code=400,
            detail=f"Proveedor '{solicitud.proveedor}' no soportado. Use uno de: {list(proveedores.PROVEEDORES)}",
        )
    dataset = _cargar_dataset()
    resultados = []
    tokens_entrada_total = 0
    tokens_salida_total = 0
    latencias = []
    costo_total = 0.0
    modelo_usado = solicitud.modelo

    for item in dataset["items"]:
        respuesta = proveedores.invocar(solicitud.proveedor, item["pregunta"], solicitud.modelo)
        modelo_usado = respuesta.modelo
        resultado_item = evaluacion.evaluar_item(
            item_id=item["id"],
            categoria=item["categoria"],
            riesgo_alucinacion=item["riesgo_alucinacion"],
            pregunta=item["pregunta"],
            respuesta_modelo=respuesta.texto,
            referencia=item["referencia"],
        )
        resultados.append(resultado_item)
        tokens_entrada_total += respuesta.tokens_entrada
        tokens_salida_total += respuesta.tokens_salida
        latencias.append(respuesta.latencia_segundos)

        estimacion = costeo.calcular_costo_llamada(
            solicitud.proveedor, respuesta.modelo, respuesta.tokens_entrada, respuesta.tokens_salida
        )
        costo_total += estimacion.costo_total_usd

    resumen = evaluacion.resumen_corrida(resultados)
    latencia_promedio = round(sum(latencias) / len(latencias), 4) if latencias else 0.0

    run_registrado = registro.registrar_corrida(
        proveedor=solicitud.proveedor,
        modelo=modelo_usado or "desconocido",
        resumen_evaluacion=resumen,
        costo_total_usd=round(costo_total, 6),
        latencia_promedio_segundos=latencia_promedio,
        checklist_etica=None,
        aprobado_por=solicitud.aprobado_por,
    )

    return {
        "run": run_registrado,
        "detalle_items": [r.to_dict() for r in resultados],
        "tokens_entrada_total": tokens_entrada_total,
        "tokens_salida_total": tokens_salida_total,
    }


@app.post("/api/costeo/proyeccion")
@limiter.limit("30/minute")
def proyectar_costo(request: Request, solicitud: SolicitudProyeccionCosto):
    return costeo.proyectar_costo_poc(
        solicitud.costo_por_llamada_usd,
        solicitud.usuarios_estimados,
        solicitud.llamadas_por_usuario_mes,
    )


@app.get("/api/checklist/preguntas")
@limiter.limit("30/minute")
def preguntas_checklist(request: Request):
    return {"preguntas": etica.PREGUNTAS_CHECKLIST}


@app.post("/api/checklist/validar")
@limiter.limit("30/minute")
def validar_checklist(request: Request, solicitud: SolicitudChecklist):
    try:
        items = etica.validar_checklist(solicitud.respuestas)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    resumen = etica.resumen_checklist(items)
    return {
        "items": [item.__dict__ for item in items],
        "resumen": resumen,
    }


@app.get("/api/registro")
@limiter.limit("30/minute")
def obtener_registro(request: Request):
    return {"corridas": registro.listar_corridas()}


@app.get("/api/registro/comparativa")
@limiter.limit("30/minute")
def obtener_comparativa(request: Request):
    return {"comparativa": registro.comparativa_por_proveedor()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
