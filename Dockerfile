FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias completas para Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg \
    libglib2.0-0 libgobject-2.0-0 \
    libnss3 libnssutil3 libsmime3 libnspr4 \
    libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libexpat1 libxcb1 \
    libxkbcommon0 libatspi2.0-0 libx11-6 \
    libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalar solo Playwright sin dependencias del sistema
RUN python -m playwright install chromium --force

# Copiar código
COPY . .

# Puerto que Render asigna
EXPOSE $PORT

# Ejecutar aplicación
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120