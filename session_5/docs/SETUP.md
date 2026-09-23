# Guía de instalación y ejecución — Sesión 5

## Requisitos

- Python 3.12
- Node.js 20+ (para Vite 6 / React 18)
- Ubuntu 24.04+ (o cualquier Linux/macOS/WSL2 equivalente)
- (Opcional) Ollama, si desea probar un modelo local — ver `../ollama/GUIA_OLLAMA.md`
- (Opcional) API keys de OpenAI/Anthropic/Google, si desea probar proveedores reales — sin ellas, el sistema corre en modo simulado

## 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env y completar solo las API keys que vaya a usar (puede dejarlas vacías)

uvicorn main:app --reload --port 8000
```

Verificar que está corriendo:

```bash
curl http://localhost:8000/
# {"servicio": "Sesión 5 — Evaluación, Costeo y Ética", "estado": "ok", ...}
```

Documentación interactiva (Swagger UI) generada automáticamente por FastAPI: `http://localhost:8000/docs`.

### Pruebas del backend

```bash
cd backend
pytest -v
```

Deben pasar 12 pruebas de humo que cubren evaluación, costeo, checklist ético y registro.

## 2. Frontend (React 18 + Vite 6)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abrir `http://localhost:5173`. El frontend espera el backend corriendo en `http://localhost:8000` (configurable con la variable `VITE_API_BASE`, ver `frontend/vite.config.js` y `frontend/src/api.js`).

## 3. Flujo recomendado en clase

1. Abrir la pestaña **"1. Evaluar proveedor"**, elegir `ollama` (funciona en modo simulado sin instalar nada) y ejecutar la evaluación. Observar el desglose de puntaje por pregunta, especialmente en las de riesgo alto.
2. Repetir con `openai` (u otro proveedor) para comparar.
3. Ir a **"2. Proyección de costo"**, usar el `costo_total_usd` de una corrida dividido entre 10 (número de ítems del dataset) como "costo por llamada", y proyectar a un volumen de uso hipotético.
4. Completar el **"3. Checklist de ética"** — intencionalmente, marcar una pregunta como "no" para ver cómo el sistema la marca como bloqueante.
5. Revisar **"4. Registro y comparativa"** para ver todas las corridas registradas y la tabla comparativa agregada por proveedor.

## 4. Modo simulado vs. modo real

Todo el flujo anterior funciona sin ninguna API key. Si se agregan credenciales reales en `backend/.env`, las llamadas a `/api/evaluar` usarán el proveedor real automáticamente (ver `backend/proveedores.py`) — no hay ningún cambio de código necesario, solo la variable de entorno correspondiente.

## 5. Estructura del repositorio

```
session_5/
├── README.md                    → esta sesión, resumen y objetivos
├── docs/
│   ├── SETUP.md                 → esta guía
│   └── marco_evaluacion.md      → fundamento teórico de cada decisión de diseño
├── backend/
│   ├── main.py                  → API FastAPI
│   ├── evaluacion.py            → harness de evaluación ligero
│   ├── costeo.py                → cálculo y proyección de costos
│   ├── etica.py                 → checklist de consideraciones éticas
│   ├── registro.py              → registro de corridas (JSON append-only)
│   ├── proveedores.py           → adaptadores OpenAI/Anthropic/Google/Ollama
│   ├── dataset_dorado.json      → dataset mínimo (10 ítems, dominio Tienda Andina)
│   ├── tarifas_ejemplo.json     → tabla de precios de ejemplo (editable)
│   ├── requirements.txt
│   ├── .env.example
│   └── tests/test_evaluacion.py → pruebas de humo (pytest)
├── frontend/
│   ├── src/App.jsx              → dashboard con 4 pestañas
│   ├── src/components/          → un componente por pestaña
│   └── src/api.js               → cliente HTTP hacia el backend
└── ollama/
    └── GUIA_OLLAMA.md           → instalación y uso de un modelo local
```
