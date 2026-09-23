"""
Pruebas mínimas de humo (smoke tests) para el harness de evaluación,
costeo, ética y registro de la Sesión 5. No pretenden ser una suite de
cobertura completa — son las pruebas mínimas que un PoC debería tener
para confiar en su propio pipeline de medición.

Ejecutar con:  pytest -v   (desde la carpeta backend/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import costeo
import etica
import evaluacion
import registro


def test_metrica_superposicion_lexica_respuesta_correcta():
    resultado = evaluacion.metrica_superposicion_lexica(
        "Sí, aceptamos devoluciones dentro de los 30 días con etiquetas originales.",
        "Sí, Tienda Andina acepta devoluciones dentro de los 30 días calendario.",
    )
    assert resultado.puntaje > 0.35


def test_metrica_superposicion_lexica_respuesta_irrelevante():
    resultado = evaluacion.metrica_superposicion_lexica(
        "El clima hoy está soleado en Lima.",
        "Sí, Tienda Andina acepta devoluciones dentro de los 30 días calendario.",
    )
    assert resultado.puntaje < 0.3


def test_metrica_cautela_apropiada_detecta_ausencia_de_cautela():
    resultado = evaluacion.metrica_cautela_apropiada(
        "Tu pedido llega mañana a las 3pm sin falta.", riesgo_alucinacion="alto"
    )
    assert resultado.puntaje == 0.0


def test_metrica_cautela_apropiada_reconoce_cautela():
    resultado = evaluacion.metrica_cautela_apropiada(
        "No tengo acceso en tiempo real al estado de tu pedido, te recomiendo verificar en el portal de seguimiento.",
        riesgo_alucinacion="alto",
    )
    assert resultado.puntaje == 1.0


def test_evaluar_item_produce_puntaje_compuesto_en_rango():
    resultado = evaluacion.evaluar_item(
        item_id="q_test",
        categoria="test",
        riesgo_alucinacion="alto",
        pregunta="¿Puedo devolver un producto usado?",
        respuesta_modelo="No tengo acceso en tiempo real a tu caso específico, pero en general se aceptan devoluciones dentro de 30 días sin uso.",
        referencia="Sí, dentro de 30 días calendario, sin uso y con etiquetas originales.",
    )
    assert 0.0 <= resultado.puntaje_compuesto <= 1.0


def test_costeo_calcula_costo_no_negativo():
    estimacion = costeo.calcular_costo_llamada("openai", "gpt-4o-mini", 1000, 500)
    assert estimacion.costo_total_usd >= 0


def test_costeo_proveedor_desconocido_no_falla():
    estimacion = costeo.calcular_costo_llamada("proveedor_inexistente", "modelo-x", 100, 100)
    assert estimacion.costo_total_usd == 0.0


def test_proyeccion_costo_poc():
    proyeccion = costeo.proyectar_costo_poc(
        costo_por_llamada_usd=0.002, usuarios_estimados=500, llamadas_por_usuario_mes=10
    )
    assert proyeccion["llamadas_totales_mes"] == 5000
    assert proyeccion["costo_estimado_mes_usd"] == 10.0


def test_checklist_valida_respuestas_completas():
    respuestas = {
        p["id"]: {"respuesta": "si", "justificacion": "cubierto"}
        for p in etica.PREGUNTAS_CHECKLIST
    }
    items = etica.validar_checklist(respuestas)
    resumen = etica.resumen_checklist(items)
    assert resumen["listo_para_avanzar"] is True


def test_checklist_detecta_bloqueantes():
    respuestas = {
        p["id"]: {"respuesta": "si", "justificacion": "cubierto"}
        for p in etica.PREGUNTAS_CHECKLIST
    }
    respuestas["transparencia_ia"]["respuesta"] = "no"
    items = etica.validar_checklist(respuestas)
    resumen = etica.resumen_checklist(items)
    assert resumen["listo_para_avanzar"] is False
    assert "transparencia_ia" in resumen["items_bloqueantes"]


def test_checklist_falla_si_falta_pregunta():
    import pytest

    respuestas = {p["id"]: {"respuesta": "si"} for p in etica.PREGUNTAS_CHECKLIST[:-1]}
    with pytest.raises(ValueError):
        etica.validar_checklist(respuestas)


def test_registro_y_comparativa(tmp_path, monkeypatch):
    log_temporal = tmp_path / "runs_log_test.json"
    monkeypatch.setattr(registro, "LOG_PATH", log_temporal)

    registro.registrar_corrida(
        proveedor="openai",
        modelo="gpt-4o-mini",
        resumen_evaluacion={"puntaje_promedio": 0.8},
        costo_total_usd=0.01,
        latencia_promedio_segundos=1.2,
    )
    registro.registrar_corrida(
        proveedor="ollama",
        modelo="llama3.2",
        resumen_evaluacion={"puntaje_promedio": 0.7},
        costo_total_usd=0.0,
        latencia_promedio_segundos=2.5,
    )

    corridas = registro.listar_corridas()
    assert len(corridas) == 2

    comparativa = registro.comparativa_por_proveedor()
    assert len(comparativa) == 2
    assert comparativa[0]["puntaje_promedio"] >= comparativa[1]["puntaje_promedio"]
