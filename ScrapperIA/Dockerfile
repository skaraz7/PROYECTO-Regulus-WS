FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del SO necesarias para Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxss1 \
    libasound2 \
    libgbm1 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    wget \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Instalar navegadores de Playwright (con deps)
RUN python -m playwright install --with-deps chromium

# Copiar código
COPY . .

# Puerto que Render asigna por env $PORT
EXPOSE $PORT

# Ejecutar con gunicorn - Render inyectará $PORT automáticamente
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120