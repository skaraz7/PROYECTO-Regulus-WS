# API de Scraping - Supermercados Perú

API REST para búsquedas en tiempo real de productos en Metro, Plaza Vea y Tottus.

> **Nota**: Esta API realiza scraping en tiempo real por cada consulta. Para scraping masivo diario y asistente inteligente, ver el proyecto completo en el repositorio principal.

## 🚀 Deployment en Render

### 1. Conectar Repositorio
- Fork este repositorio
- Conectar con Render desde GitHub

### 2. Configuración en Render
- **Build Command**: `pip install -r requirements.txt && playwright install chromium`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
- **Environment**: Python 3.11

## 📡 Endpoints

### GET /health
Health check del servicio
```
GET /health
Response: "ok"
```

### GET /scrape
Búsqueda directa de productos
```
GET /scrape?product=arroz&stores=metro,plazavea&max=5

Parameters:
- product: Producto a buscar (default: "arroz")
- stores: Tiendas separadas por coma (default: "metro,plazavea,tottus")
- max: Máximo productos por tienda (default: 10)

Response:
{
  "product": "arroz",
  "stores": ["metro", "plazavea"],
  "count": 8,
  "items": [...]
}
```

### POST /chat
Consultas en lenguaje natural con IA
```
POST /chat
Content-Type: application/json

{
  "message": "arroz más barato",
  "max": 5
}

Response:
{
  "message": "arroz más barato",
  "interpretation": {
    "product": ["arroz"],
    "store": null,
    "query_type": "precio_minimo"
  },
  "response": "El arroz más barato es: Arroz Superior por S/ 3.50 en Metro",
  "count": 5,
  "products": [...]
}
```

#### Ejemplos de consultas IA:
- "¿Cuál es la pasta de dientes más barata?"
- "Aceite de cocina más caro"
- "Comparar detergente en todas las tiendas"
- "Leche en Metro"
- "Arroz económico"

## 🛠️ Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# Ejecutar aplicación
python app.py
```

## 🏪 Tiendas Soportadas
- **Metro**: metro.pe
- **Plaza Vea**: plazavea.com.pe  
- **Tottus**: tottus.com.pe