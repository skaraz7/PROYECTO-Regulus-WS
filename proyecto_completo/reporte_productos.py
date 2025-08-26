import json
import os

def generar_reporte():
    archivos = [
        ('data/metro_completo.json', 'Metro'),
        ('data/plazavea_completo.json', 'Plaza Vea'), 
        ('data/tottus_completo.json', 'Tottus')
    ]
    
    print("=" * 60)
    print("REPORTE DETALLADO DE PRODUCTOS POR CATEGORIA")
    print("=" * 60)
    
    total_general = 0
    
    for archivo, tienda_nombre in archivos:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            print(f"\n{tienda_nombre.upper()}:")
            print(f"Total productos: {data['total_productos']}")
            print(f"Fecha actualización: {data['fecha_actualizacion']}")
            
            # Contar por categoría
            categorias_count = {}
            for producto in data['productos']:
                categoria = producto.get('categoria', 'sin_categoria')
                categorias_count[categoria] = categorias_count.get(categoria, 0) + 1
            
            print("Por categoría:")
            for categoria, count in sorted(categorias_count.items()):
                print(f"  - {categoria}: {count} productos")
            
            total_general += data['total_productos']
        else:
            print(f"\n{tienda_nombre.upper()}: Archivo no encontrado")
    
    print(f"\nTOTAL GENERAL: {total_general} productos")
    print("=" * 60)

if __name__ == "__main__":
    generar_reporte()