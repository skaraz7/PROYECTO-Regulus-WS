FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar requirements e instalar Python packages
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Playwright ya está instalado en la imagen base

# Copiar código
COPY . .

# Puerto que Render asigna
EXPOSE $PORT

# Ejecutar aplicación
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120