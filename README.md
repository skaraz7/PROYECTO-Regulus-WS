# Sistema Inteligente de Scraping - Supermercados Perú

Sistema completo de scraping y búsqueda inteligente para comparar precios en Metro, Plaza Vea y Tottus.

## 🏗️ Arquitectura del Sistema

### Core Scrapers (`/core/`)
- `metro_scraper.py` - Scraper especializado para Metro
- `plazavea_scraper.py` - Scraper especializado para Plaza Vea  
- `tottus_scraper.py` - Scraper especializado para Tottus

### Componentes Principales
- `scraping_diario.py` - Ejecuta scraping completo diario (1 vez al día)
- `asistente_inteligente.py` - Asistente con IA para consultas de usuarios

### Datos (`/data/`)
- `metro_completo.json` - Base de datos completa de Metro
- `plazavea_completo.json` - Base de datos completa de Plaza Vea
- `tottus_completo.json` - Base de datos completa de Tottus
- `resumen_scraping.json` - Resumen de último scraping

## 🚀 Uso del Sistema

### 1. Scraping Diario (Ejecutar 1 vez al día)
```bash
python scraping_diario.py
```
- Recolecta productos de todas las categorías
- Genera bases de datos JSON actualizadas
- Almacena ~300-500 productos por tienda

### 2. Asistente Inteligente (Uso interactivo)
```bash
python asistente_inteligente.py
```

#### Ejemplos de Consultas:
- "¿Cuál es la pasta de dientes más barata?"
- "Jabón para ropa en Metro"
- "Comparar aceite de cocina en todas las tiendas"
- "Detergente más económico"
- "Leche más cara en Plaza Vea"

## 🧠 Funcionamiento Inteligente

### Flujo de Búsqueda:
1. **Interpretación**: Analiza la consulta del usuario
2. **Búsqueda Local**: Busca primero en bases de datos JSON
3. **Búsqueda Web**: Si no encuentra suficientes resultados, hace scraping en tiempo real
4. **Procesamiento**: Ordena por precio, compara tiendas, etc.
5. **Respuesta**: Muestra resultados formateados

### Tipos de Consulta Soportados:
- **Precio Mínimo**: "más barato", "económico", "menor precio"
- **Precio Máximo**: "más caro", "premium", "mayor precio"  
- **Comparación**: "comparar", "donde comprar", "vs"
- **Búsqueda General**: Cualquier producto

## 📊 Estadísticas Actuales

**Total Productos en BD**: 376
- Metro: 80 productos
- Plaza Vea: 296 productos
- Tottus: 0 productos (requiere ajustes)

**Categorías Cubiertas**:
- Abarrotes
- Limpieza
- Lácteos
- Desayuno
- Cuidado Personal
- Bebidas

## 🔧 Características Técnicas

### Scrapers Core:
- **Anti-detección**: User agents, cookies, scroll humano
- **Robustez**: Múltiples selectores, manejo de errores
- **Eficiencia**: Scraping por categorías, límites configurables

### Asistente IA:
- **NLP Básico**: Extracción de palabras clave, detección de intención
- **Búsqueda Híbrida**: Local primero, web como fallback
- **Respuestas Contextuales**: Ordenamiento inteligente por tipo de consulta

## 🎯 Ventajas del Sistema

1. **Eficiencia**: Scraping diario evita consultas web constantes
2. **Velocidad**: Búsquedas instantáneas en BD local
3. **Completitud**: Fallback a web si no encuentra en BD
4. **Flexibilidad**: Acepta consultas en lenguaje natural
5. **Escalabilidad**: Fácil agregar nuevas tiendas/productos

## 📝 Próximas Mejoras

- [ ] Integración con Gemini API para mejor NLP
- [ ] Corrección de scraper de Tottus
- [ ] Notificaciones de ofertas
- [ ] API REST para integración externa
- [ ] Dashboard web para visualización

## 🛠️ Instalación

```bash
pip install playwright beautifulsoup4
playwright install chromium
```

## 📞 Soporte

Sistema desarrollado para comparación inteligente de precios en supermercados peruanos.
Optimizado para consultas rápidas y scraping eficiente.