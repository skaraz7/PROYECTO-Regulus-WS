import json
import os
import re
from datetime import datetime
# import google.generativeai as genai  # Comentado por ahora

class SistemaInteligenteScraper:
    def __init__(self):
        # Configurar Gemini (necesitas tu API key)
        # genai.configure(api_key="TU_API_KEY_AQUI")
        # self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.productos_db = self.cargar_base_datos()
        
    def cargar_base_datos(self):
        """Carga todas las bases de datos JSON"""
        db = {}
        archivos = [
            'metro_productos_completo.json',
            'plazavea_productos_completo.json', 
            'tottus_productos_completo.json'
        ]
        
        for archivo in archivos:
            try:
                if os.path.exists(archivo):
                    with open(archivo, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tienda = data['tienda'].lower().replace(' ', '_')
                        db[tienda] = data
                        print(f"Cargada BD: {data['tienda']} - {data['total_productos']} productos")
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")
        
        return db
    
    def interpretar_consulta(self, consulta):
        """Interpreta la consulta del usuario usando reglas simples"""
        consulta_lower = consulta.lower()
        
        # Mapeo de productos
        productos_map = {
            'arroz': ['arroz', 'rice'],
            'azucar': ['azucar', 'azúcar', 'sugar', 'endulzante'],
            'papel_higienico': ['papel', 'higienico', 'higiénico', 'tissue', 'papel higienico'],
            'leche': ['leche', 'milk'],
            'detergentes': ['detergente', 'detergentes', 'jabon', 'limpieza'],
            'yogures': ['yogur', 'yogurt', 'yogures']
        }
        
        # Mapeo de tiendas
        tiendas_map = {
            'metro': ['metro'],
            'plaza_vea': ['plaza vea', 'plazavea', 'plaza'],
            'tottus': ['tottus']
        }
        
        # Detectar producto
        producto_detectado = None
        for producto, keywords in productos_map.items():
            if any(keyword in consulta_lower for keyword in keywords):
                producto_detectado = producto
                break
        
        # Detectar tienda
        tienda_detectada = None
        for tienda, keywords in tiendas_map.items():
            if any(keyword in consulta_lower for keyword in keywords):
                tienda_detectada = tienda
                break
        
        # Detectar tipo de consulta
        if any(palabra in consulta_lower for palabra in ['barato', 'menor precio', 'más barato', 'economico']):
            tipo_consulta = 'precio_minimo'
        elif any(palabra in consulta_lower for palabra in ['caro', 'mayor precio', 'más caro', 'premium']):
            tipo_consulta = 'precio_maximo'
        elif any(palabra in consulta_lower for palabra in ['comparar', 'comparacion', 'vs', 'versus']):
            tipo_consulta = 'comparacion'
        else:
            tipo_consulta = 'busqueda_general'
        
        return {
            'producto': producto_detectado,
            'tienda': tienda_detectada,
            'tipo': tipo_consulta,
            'consulta_original': consulta
        }
    
    def buscar_en_bd(self, interpretacion):
        """Busca en la base de datos local"""
        resultados = []
        producto = interpretacion['producto']
        tienda = interpretacion['tienda']
        
        if not producto:
            return []
        
        # Buscar en tiendas específicas o todas
        tiendas_buscar = [tienda] if tienda else self.productos_db.keys()
        
        for tienda_key in tiendas_buscar:
            if tienda_key in self.productos_db:
                tienda_data = self.productos_db[tienda_key]
                if producto in tienda_data['productos']:
                    productos_tienda = tienda_data['productos'][producto]
                    resultados.extend(productos_tienda)
        
        return resultados
    
    def procesar_resultados(self, resultados, tipo_consulta):
        """Procesa los resultados según el tipo de consulta"""
        if not resultados:
            return []
        
        # Filtrar productos con precio válido
        productos_validos = [r for r in resultados if r.get('precio_numerico', 0) > 0]
        
        if tipo_consulta == 'precio_minimo':
            return sorted(productos_validos, key=lambda x: x['precio_numerico'])[:5]
        elif tipo_consulta == 'precio_maximo':
            return sorted(productos_validos, key=lambda x: x['precio_numerico'], reverse=True)[:5]
        elif tipo_consulta == 'comparacion':
            # Agrupar por tienda y mostrar el mejor de cada una
            por_tienda = {}
            for prod in productos_validos:
                tienda = prod['tienda']
                if tienda not in por_tienda or prod['precio_numerico'] < por_tienda[tienda]['precio_numerico']:
                    por_tienda[tienda] = prod
            return list(por_tienda.values())
        else:
            return productos_validos[:10]
    
    def responder_consulta(self, consulta):
        """Responde a una consulta del usuario"""
        print(f"\nProcesando: '{consulta}'")
        
        # Interpretar consulta
        interpretacion = self.interpretar_consulta(consulta)
        print(f"Interpretación: {interpretacion}")
        
        # Buscar en BD local
        resultados = self.buscar_en_bd(interpretacion)
        print(f"Encontrados {len(resultados)} productos en BD local")
        
        if resultados:
            # Procesar resultados
            resultados_procesados = self.procesar_resultados(resultados, interpretacion['tipo'])
            
            # Mostrar respuesta
            self.mostrar_respuesta(interpretacion, resultados_procesados)
            return resultados_procesados
        else:
            print("No se encontraron productos en BD local")
            print("Seria necesario hacer scraping web...")
            return []
    
    def mostrar_respuesta(self, interpretacion, resultados):
        """Muestra la respuesta formateada"""
        producto = interpretacion['producto']
        tipo = interpretacion['tipo']
        
        print(f"\nRESULTADOS PARA {producto.upper()}:")
        
        if tipo == 'precio_minimo':
            print("PRODUCTOS MAS BARATOS:")
        elif tipo == 'precio_maximo':
            print("PRODUCTOS MAS CAROS:")
        elif tipo == 'comparacion':
            print("COMPARACION POR TIENDA:")
        else:
            print("PRODUCTOS ENCONTRADOS:")
        
        for i, prod in enumerate(resultados, 1):
            precio = prod.get('precio', 'N/A')
            tienda = prod.get('tienda', 'N/A')
            nombre = prod.get('nombre', 'N/A')
            print(f"{i}. {nombre} - {precio} ({tienda})")

def main():
    sistema = SistemaInteligenteScraper()
    
    # Ejemplos de consultas
    consultas_ejemplo = [
        "¿Cuál es el arroz más barato?",
        "Quiero comparar precios de leche en todas las tiendas",
        "¿Dónde encuentro azúcar en Metro?",
        "Papel higiénico más económico",
        "Yogures en Plaza Vea"
    ]
    
    print("=== SISTEMA INTELIGENTE DE SCRAPING ===")
    print("Base de datos cargada. Ejemplos de consultas:")
    
    for consulta in consultas_ejemplo:
        sistema.responder_consulta(consulta)
        print("-" * 50)

if __name__ == "__main__":
    main()