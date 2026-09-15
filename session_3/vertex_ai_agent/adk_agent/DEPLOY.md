# Ejecutar y Desplegar el Agente ADK

## 1. Instalación local

```bash
cd session_3/vertex_ai_agent/adk_agent
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # y completa GOOGLE_CLOUD_PROJECT

gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
gcloud services enable aiplatform.googleapis.com
```

## 2. Probar localmente

El ADK trae dos formas de ejecutar un agente en desarrollo:

**Opción A — Interfaz web de desarrollo (recomendada para depurar):**
```bash
adk web
```
Abre `http://localhost:8000` en el navegador, selecciona el agente
`adk_agent` en el panel izquierdo y chatea con él. La UI muestra también
las llamadas a `tools` (`consultar_faq`, `escalar_a_humano`) paso a paso —
muy útil para que los alumnos vean el razonamiento del agente.

**Opción B — Terminal interactiva:**
```bash
adk run adk_agent
```

Prueba con mensajes como:
- *"¿Hasta qué hora abren los sábados?"*
- *"Quiero hacer un reclamo por un producto dañado"* (debería activar `escalar_a_humano`)

## 3. Desplegar a Google Cloud (Cloud Run)

Una vez que el agente funciona localmente, el ADK puede empaquetarlo y
desplegarlo directamente a Cloud Run con un solo comando:

```bash
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  ./adk_agent
```

Este comando:
1. Empaqueta el código del agente + el servidor API del ADK en un contenedor.
2. Construye la imagen con Cloud Build.
3. Despliega un servicio de Cloud Run con autenticación gestionada por IAM.

Al finalizar, la terminal imprime la URL pública (o restringida por IAM,
según configuración) del servicio — ej. `https://adk-agent-xxxxx-uc.a.run.app`.

## 4. Alternativa: desplegar a Agent Runtime

Para cargas de trabajo de agentes más exigentes (escalado automático,
integración nativa con el resto de Gemini Enterprise Agent Platform),
Google ofrece **Agent Runtime** como destino de despliegue administrado,
en vez de Cloud Run genérico. Los pasos de alto nivel:

1. Empaqueta el agente igual que en el paso 3.
2. En la consola de **Gemini Enterprise Agent Platform → Agent Runtime**,
   registra el agente apuntando a tu imagen de contenedor o repositorio.
3. Agent Runtime gestiona el ciclo de vida (versionado, rollback, logs
   centralizados) de forma más integrada que un Cloud Run standalone.

Consulta la documentación oficial vigente en el momento de tu despliegue —
los pasos exactos de la consola cambian con frecuencia:
`https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/adk`

## 5. Verificar el despliegue

```bash
curl -X POST https://TU-SERVICIO-URL/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{"input": "¿Cuál es la política de devoluciones?"}'
```

(El formato exacto del endpoint puede variar según la versión del ADK —
revisa la salida de `adk deploy` para la ruta correcta.)

## 6. Limpieza (evitar costos)

```bash
gcloud run services delete adk-agent --region=$GOOGLE_CLOUD_LOCATION
```

## Comparación de esfuerzo: Parte 3.1 vs 3.2

| Aspecto | 3.1 Consola (Agent Studio) | 3.2 ADK (código) |
|---|---|---|
| Tiempo para un demo funcional | ~10 minutos | ~30-45 minutos |
| Lógica personalizada (tools) | No | Sí — funciones Python arbitrarias |
| Testing automatizado | No | Sí — es código versionable |
| Despliegue a producción | Vía integración nativa | Cloud Run / Agent Runtime, con CI/CD propio |
