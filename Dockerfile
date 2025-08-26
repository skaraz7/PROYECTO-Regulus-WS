FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Evitar buffering en logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Instalar Chromium (necesario para Playwright)
RUN playwright install --with-deps chromium

# Copiar el resto del código
COPY . .

# Render ignora EXPOSE, pero puedes dejarlo fijo
EXPOSE 8000

# Ejecutar con gunicorn (Render inyecta $PORT automáticamente)
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120