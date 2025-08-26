FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar repositorios y instalar dependencias básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalar Playwright y navegadores
RUN python -m playwright install chromium
RUN python -m playwright install-deps chromium || true

# Copiar código
COPY . .

# Puerto que Render asigna por env $PORT
EXPOSE $PORT

# Ejecutar con gunicorn - Render inyectará $PORT automáticamente
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120