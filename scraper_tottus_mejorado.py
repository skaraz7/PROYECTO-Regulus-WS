from scraper.tottus import buscar_tottus
import json
from datetime import datetime

def scraper_tottus_productos():
    """Scraper mejorado de Tottus usando el sistema existente"""
    
    # Mapeo de productos a categorías de Tottus
    productos_categorias = {
        'arroz': 'CATG16815',  # Categoría de arroz
        'azucar': None,  # Buscar en general
        'papel_higienico': None,  # Buscar en general
        'leche': None,  # Buscar en general
        'detergentes': None,  # Buscar en general
        'yogures': None  # Buscar en general
    }
    
    todos_productos = {}
    
    for producto, categoria_id in productos_categorias.items():
        print(f"\n=== Scrapeando {producto.upper()} en TOTTUS ===")
        try:
            # Usar el scraper existente
            resultados = buscar_tottus(producto, 30, categoria_id)
            
            # Filtrar productos usando nombres completos (Tottus tiene nombres genéricos)
            if producto == 'arroz':
                # Para arroz, todos los productos de la categoría son válidos
                filtrados = resultados
            elif producto == 'azucar':
                filtrados = [r for r in resultados if any(palabra in r['nombre'].lower() 
                           for palabra in ['azucar', 'azúcar', 'sugar'])]
            elif producto == 'papel_higienico':
                filtrados = [r for r in resultados if any(palabra in r['nombre'].lower() 
                           for palabra in ['papel', 'higienico', 'higiénico', 'tissue'])]
            elif producto == 'leche':
                filtrados = [r for r in resultados if 'leche' in r['nombre'].lower()]
            elif producto == 'detergentes':
                filtrados = [r for r in resultados if any(palabra in r['nombre'].lower() 
                           for palabra in ['detergente', 'ariel', 'ace', 'bolivar'])]
            elif producto == 'yogures':
                filtrados = [r for r in resultados if any(palabra in r['nombre'].lower() 
                           for palabra in ['yogur', 'yogurt'])]
            else:
                filtrados = resultados
            
            # Si no hay filtrados específicos, usar todos los resultados
            if not filtrados and resultados:
                print(f"No se encontraron productos específicos, usando todos los resultados")
                filtrados = resultados
            
            # Agregar metadata
            for item in filtrados:
                item['categoria'] = producto
                item['fecha_scraping'] = datetime.now().isoformat()
                item['precio_numerico'] = extraer_precio(item['precio'])
            
            todos_productos[producto] = filtrados
            print(f"Encontrados {len(filtrados)} productos de {producto}")
            
        except Exception as e:
            print(f"Error scrapeando {producto}: {e}")
            todos_productos[producto] = []
    
    # Guardar en JSON
    with open('tottus_productos_completo.json', 'w', encoding='utf-8') as f:
        json.dump({
            'tienda': 'Tottus',
            'fecha_actualizacion': datetime.now().isoformat(),
            'total_productos': sum(len(prods) for prods in todos_productos.values()),
            'productos': todos_productos
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nTOTTUS: {sum(len(prods) for prods in todos_productos.values())} productos guardados")
    return todos_productos

def extraer_precio(precio_str):
    """Extrae precio numérico"""
    import re
    if not precio_str:
        return 0
    match = re.search(r'S/\s*(\d+(?:\.\d+)?)', precio_str.replace(',', ''))
    return float(match.group(1)) if match else 0

if __name__ == "__main__":
    scraper_tottus_productos()