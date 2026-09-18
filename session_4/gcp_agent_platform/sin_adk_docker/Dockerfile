# Parte 3.3 — Dockerfile propio, sin que el ADK lo genere por ti.
# Base: Python 3.12 slim sobre Debian — compatible con Ubuntu 24.04+ en CI/CD.
FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema mínimas (certificados para HTTPS saliente hacia la API de Gemini)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Cloud Run inyecta la variable PORT en tiempo de ejecución — el contenedor
# debe escuchar en ese puerto, nunca asumir uno fijo. main.py ya lo lee
# con os.getenv("PORT", "8080").
ENV PORT=8080
EXPOSE 8080

# Usuario no-root — buena práctica de seguridad básica para contenedores en producción.
RUN useradd --create-home appuser
USER appuser

CMD ["python", "main.py"]
