# Arquitectura del Sistema

## 📁 Estructura para Deployment (Render)

```
PROYECTO-Regulus-WS/
├─ scraper/
│  ├─ metro.py          # Scraper Metro (adaptado del original)
│  ├─ plazavea.py       # Scraper Plaza Vea (adaptado del original)  
│  └─ tottus.py         # Scraper Tottus (adaptado del original)
├─ app.py               # API Flask para búsquedas en tiempo real
├─ requirements.txt     # Dependencias para deployment
├─ Dockerfile          # Configuración para contenedores
├─ .gitignore          # Archivos a ignorar
└─ README.md           # Documentación de la API
```

## 🔄 Diferencias con el Sistema Completo

### API REST (Esta estructura)
- **Propósito**: Búsquedas individuales en tiempo real
- **Uso**: `GET /scrape?product=arroz&stores=metro,plazavea&max=5`
- **Deployment**: Render, Heroku, Railway, etc.
- **Scrapers**: Adaptados de los originales, optimizados para respuestas rápidas

### Sistema Completo (Estructura original)
- **Propósito**: Scraping masivo diario + Asistente inteligente
- **Componentes**:
  - `scraping_diario.py` - Recolecta 300-500 productos por tienda diariamente
  - `asistente_inteligente.py` - IA para consultas en lenguaje natural
  - `core/` - Scrapers con 97 categorías configuradas
  - `data/` - Bases de datos JSON locales
- **Uso**: Ejecutar localmente o en servidor dedicado

## 🚀 Casos de Uso

### Usar API REST cuando:
- Necesitas integración con otras aplicaciones
- Quieres búsquedas ocasionales de productos específicos
- Requieres deployment en la nube
- Prefieres arquitectura stateless

### Usar Sistema Completo cuando:
- Necesitas análisis masivo de productos
- Quieres consultas en lenguaje natural ("pasta de dientes más barata")
- Requieres bases de datos locales actualizadas
- Prefieres velocidad de respuesta (búsqueda local primero)

## 🔧 Configuración de Deployment

### Render
1. **Build Command**: `pip install -r requirements.txt && playwright install --with-deps chromium`
2. **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
3. **Environment**: Python 3.11

### Variables de Entorno
- `PORT`: Puerto asignado automáticamente por Render
- Playwright se instala con dependencias del sistema incluidas

## 📊 Rendimiento Esperado

### API REST
- **Tiempo de respuesta**: 10-30 segundos por consulta
- **Productos por consulta**: 5-30 productos
- **Tiendas simultáneas**: 1-3 tiendas por request

### Sistema Completo  
- **Scraping diario**: 1-2 horas para ~1,500 productos
- **Consultas locales**: < 1 segundo
- **Cobertura**: 97 categorías across 3 tiendas