# Sesión 5 — Evaluación, Costeo y Ética en el Uso de LLM

**Curso:** Fundamentos de Arquitectura LLM · Capítulo 2: Ecosistema y Operación Básica de LLM
**Objetivo de desempeño de la sesión:** Diseñar una evaluación inicial y un estimado de costos/tiempos para un PoC simple con LLM, incluyendo consideraciones éticas básicas.

## Temas cubiertos

1. **Calidad y seguridad: qué medir en un PoC.**
2. **Métodos de evaluación ligeros y dataset mínimo.**
3. **Registro de resultados y comparativas.**

## Qué construye este repositorio

Un PoC completo, ejecutable de punta a punta, que aplica los tres temas de la sesión sobre el mismo dominio usado en sesiones anteriores del curso ("Tienda Andina", un asistente de soporte de e-commerce):

- Un **harness de evaluación ligero** (`backend/evaluacion.py`) que corre un dataset dorado de 10 preguntas contra cualquier proveedor de LLM y calcula tres métricas deterministas: superposición léxica con la respuesta de referencia, cautela apropiada en preguntas de alto riesgo de alucinación, y longitud relativa.
- Un **módulo de costeo** (`backend/costeo.py`) que calcula el costo real de cada corrida y proyecta el costo mensual/anual del PoC a escala.
- Un **checklist de ética** (`backend/etica.py`) de 7 preguntas mapeadas explícitamente a NIST AI RMF 1.0 y al Reglamento de IA de la Unión Europea, que bloquea el avance del PoC si hay respuestas "no" sin resolver.
- Un **registro de resultados** (`backend/registro.py`) que guarda cada corrida y genera una tabla comparativa por proveedor/modelo — la base para decidir con datos, no con impresiones, qué proveedor usar.
- Un **dashboard en React** (`frontend/`) con cuatro pestañas, una por cada pieza anterior.
- Una **guía de Ollama** (`ollama/GUIA_OLLAMA.md`) para que cualquier estudiante corra todo el ejercicio con un modelo local, sin gastar dinero ni necesitar credenciales.

Ver `docs/marco_evaluacion.md` para el fundamento teórico completo (con citas verificables) de cada decisión de diseño, y `docs/SETUP.md` para instrucciones paso a paso de instalación y ejecución.

## Por qué está diseñado así (resumen para el estudiante)

Un PoC no se evalúa con el mismo rigor que un modelo en producción, pero tampoco se debe avanzar a producción sin evaluarlo en absoluto. Este ejemplo está deliberadamente en el punto medio: usa métricas ligeras y gratuitas en vez de un framework de evaluación industrial completo (como HELM), pero esas métricas no son arbitrarias — cada una está justificada por un paper o marco reconocido (RAGAS, G-Eval, NIST AI RMF, EU AI Act), citado explícitamente en `docs/marco_evaluacion.md`. La idea que debe quedar clara al final de la sesión es que **"ligero" no significa "sin rigor"**: significa elegir deliberadamente qué medir primero, con qué costo, y documentar por qué.

## Stack técnico

- Python 3.12 + FastAPI (backend)
- React 18 + Vite 6 (frontend)
- Ollama (modelo local opcional, sin costo de API)
- Sin base de datos: registro en JSON append-only, suficiente para el volumen de un PoC (ver `docs/SETUP.md` si se desea migrar a Postgres en el futuro)
- Todas las credenciales vía variables de entorno (`.env`), nunca hardcodeadas

## Inicio rápido

```bash
# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
uvicorn main:app --reload --port 8000

# Frontend (en otra terminal)
cd frontend && npm install && npm run dev
```

Ver `docs/SETUP.md` para el detalle completo, incluyendo el flujo recomendado para usar en clase.
