# Ejecutar y Desplegar el Agente Sin ADK (Docker → Cloud Run)

A diferencia de la Parte 3.2, aquí **tú** escribes y controlas el
`Dockerfile` — el ADK no genera nada por ti. Esto da control total, a
cambio de más pasos manuales.

## 1. Probar localmente sin Docker

```bash
cd session_4/gcp_agent_platform/sin_adk_docker
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # y completa GOOGLE_API_KEY (opcional — corre en MODO_SIMULADO sin ella)

python main.py
# o: uvicorn main:app --reload --port 8080
```

Prueba con:
```bash
curl -X POST http://localhost:8080/agente/consultar \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Hasta qué hora abren los sábados?"}'

curl -X POST http://localhost:8080/agente/consultar \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Quiero hacer un reclamo por un producto dañado"}'
```

La segunda solicitud debería devolver `"accion": "escalar_a_humano"` sin
siquiera llamar al modelo — la misma lógica de decisión simple que
reemplaza el "tool routing" automático del ADK.

## 2. Construir y probar la imagen Docker localmente

```bash
docker build -t agente-tienda-andina:local .
docker run --rm -p 8080:8080 --env-file .env agente-tienda-andina:local
```

Verifica con el mismo `curl` de arriba, apuntando a `localhost:8080`.

## 3. Publicar la imagen en Artifact Registry

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev

gcloud artifacts repositories create agentes-demo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Imágenes de agentes de la Sesión 4"

docker tag agente-tienda-andina:local \
  us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/agentes-demo/agente-tienda-andina:v1

docker push \
  us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/agentes-demo/agente-tienda-andina:v1
```

## 4. Desplegar a Cloud Run

```bash
gcloud run deploy agente-tienda-andina \
  --image=us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/agentes-demo/agente-tienda-andina:v1 \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_MODEL=gemini-2.0-flash" \
  --set-secrets="GOOGLE_API_KEY=agente-gemini-key:latest"
```

Nota de seguridad: la API key **no** se pasa con `--set-env-vars` en
producción — se referencia desde **Secret Manager** con `--set-secrets`.
Crear el secreto primero:
```bash
echo -n "tu-api-key-real" | gcloud secrets create agente-gemini-key --data-file=-
gcloud secrets add-iam-policy-binding agente-gemini-key \
  --member="serviceAccount:$(gcloud run services describe agente-tienda-andina --region=us-central1 --format='value(spec.template.spec.serviceAccountName)')" \
  --role="roles/secretmanager.secretAccessor"
```

Alternativamente, sin gestionar el `Dockerfile` manualmente en cada paso,
`gcloud run deploy --source .` construye la imagen con Cloud Build y
despliega en un solo comando — pero entonces pierdes el control explícito
sobre el `Dockerfile` que es el punto de esta Parte 3.3.

## 5. Verificar el despliegue

```bash
SERVICE_URL=$(gcloud run services describe agente-tienda-andina --region=us-central1 --format='value(status.url)')

curl -X POST "$SERVICE_URL/agente/consultar" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{"mensaje": "¿Cuál es la política de devoluciones?"}'
```

## 6. Limpieza (evitar costos)

```bash
gcloud run services delete agente-tienda-andina --region=us-central1
gcloud artifacts repositories delete agentes-demo --location=us-central1
gcloud secrets delete agente-gemini-key
```

## Resumen: 3.1 vs 3.2 vs 3.3

| Aspecto | 3.1 Consola | 3.2 ADK | 3.3 Sin ADK + Docker |
|---|---|---|---|
| Escribes el `Dockerfile` | N/A | No — el ADK lo genera | Sí — línea por línea |
| Dependencia de framework | Ninguna (plataforma) | `google-adk` | Ninguna — solo FastAPI + SDK de Gemini |
| Encaja en un backend existente | N/A | Requiere adoptar el ADK | Se agrega como un endpoint más |
| Curva de aprendizaje | Muy baja | Media (API propia del ADK) | Baja si ya sabes FastAPI/Docker |
| Mejor para | Prototipos, no-developers | Agentes con tools/orquestación compleja | Equipos con backend propio y CI/CD de contenedores ya establecido |
