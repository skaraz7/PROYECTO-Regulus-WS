import json
import os
import re
from datetime import datetime
from core.metro_scraper import MetroScraper
from core.plazavea_scraper import PlazaVeaScraper
from core.tottus_scraper import TottusScraper

class AsistenteInteligente:
    def __init__(self):
        self.data_dir = "data"
        self.base_datos = self.cargar_base_datos()
        
    def cargar_base_datos(self):
        """Carga las bases de datos JSON generadas por el scraping diario"""
        db = {}
        archivos = [
            'metro_completo.json',
            'plazavea_completo.json',
            'tottus_completo.json'
        ]
        
        for archivo in archivos:
            archivo_path = os.path.join(self.data_dir, archivo)
            try:
                if os.path.exists(archivo_path):
                    with open(archivo_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        tienda = data['tienda'].lower().replace(' ', '_')
                        db[tienda] = data
                        print(f"BD cargada: {data['tienda']} - {data['total_productos']} productos")
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")
        
        return db
    
    def interpretar_consulta(self, consulta):
        """Interpreta la consulta del usuario"""
        consulta_lower = consulta.lower()
        
        # Detectar tienda específica
        tienda_detectada = None
        if 'metro' in consulta_lower:
            tienda_detectada = 'metro'
        elif any(palabra in consulta_lower for palabra in ['plaza vea', 'plazavea', 'plaza']):
            tienda_detectada = 'plaza_vea'
        elif 'tottus' in consulta_lower:
            tienda_detectada = 'tottus'
        
        # Detectar tipo de consulta
        if any(palabra in consulta_lower for palabra in ['barato', 'menor precio', 'más barato', 'economico', 'menor']):
            tipo_consulta = 'precio_minimo'
        elif any(palabra in consulta_lower for palabra in ['caro', 'mayor precio', 'más caro', 'premium', 'mayor']):
            tipo_consulta = 'precio_maximo'
        elif any(palabra in consulta_lower for palabra in ['comparar', 'comparacion', 'vs', 'versus', 'donde']):
            tipo_consulta = 'comparacion'
        else:
            tipo_consulta = 'busqueda_general'
        
        # Extraer producto de la consulta (palabras clave después de preposiciones)
        palabras_clave = self._extraer_producto_de_consulta(consulta_lower)
        
        return {
            'producto_keywords': palabras_clave,
            'tienda': tienda_detectada,
            'tipo': tipo_consulta,
            'consulta_original': consulta
        }
    
    def _extraer_producto_de_consulta(self, consulta):
        """Extrae palabras clave del producto de la consulta"""
        # Remover palabras comunes
        palabras_ignorar = {
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'por', 'para',
            'que', 'cual', 'cuales', 'donde', 'como', 'cuando', 'precio', 'precios',
            'barato', 'baratos', 'caro', 'caros', 'mejor', 'mejores', 'mas', 'menos',
            'comparar', 'comparacion', 'buscar', 'encontrar', 'quiero', 'necesito',
            'metro', 'plaza', 'vea', 'tottus', 'tienda', 'tiendas', 'supermercado'
        }
        
        palabras = re.findall(r'\b\w+\b', consulta)
        palabras_filtradas = [p for p in palabras if p not in palabras_ignorar and len(p) > 2]
        
        return palabras_filtradas
    
    def buscar_en_bd(self, interpretacion):
        """Busca en la base de datos local"""
        resultados = []
        palabras_clave = interpretacion['producto_keywords']
        tienda = interpretacion['tienda']
        
        if not palabras_clave:
            return []
        
        # Buscar en tiendas específicas o todas
        tiendas_buscar = [tienda] if tienda else self.base_datos.keys()
        
        for tienda_key in tiendas_buscar:
            if tienda_key in self.base_datos:
                productos = self.base_datos[tienda_key]['productos']
                
                # Buscar productos que contengan las palabras clave
                for producto in productos:
                    nombre_lower = producto['nombre'].lower()
                    if any(palabra in nombre_lower for palabra in palabras_clave):
                        resultados.append(producto)
        
        return resultados
    
    def buscar_en_web(self, interpretacion):
        """Busca en la web cuando no encuentra en BD local"""
        print("Buscando en la web...")
        resultados = []
        palabras_clave = interpretacion['producto_keywords']
        producto_busqueda = ' '.join(palabras_clave[:2])  # Usar las primeras 2 palabras
        
        tienda = interpretacion['tienda']
        
        try:
            if not tienda or tienda == 'metro':
                metro = MetroScraper()
                resultados.extend(metro.buscar_producto(producto_busqueda, 10))
            
            if not tienda or tienda == 'plaza_vea':
                plazavea = PlazaVeaScraper()
                resultados.extend(plazavea.buscar_producto(producto_busqueda, 10))
            
            if not tienda or tienda == 'tottus':
                tottus = TottusScraper()
                resultados.extend(tottus.buscar_producto(producto_busqueda, 10))
                
        except Exception as e:
            print(f"Error en búsqueda web: {e}")
        
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
        print(f"Palabras clave detectadas: {interpretacion['producto_keywords']}")
        
        # Buscar en BD local primero
        resultados = self.buscar_en_bd(interpretacion)
        print(f"Encontrados {len(resultados)} productos en BD local")
        
        # Si no encuentra suficientes resultados, buscar en web
        if len(resultados) < 3:
            print("Pocos resultados en BD local, buscando en web...")
            resultados_web = self.buscar_en_web(interpretacion)
            resultados.extend(resultados_web)
            print(f"Total con búsqueda web: {len(resultados)}")
        
        if resultados:
            # Procesar resultados
            resultados_procesados = self.procesar_resultados(resultados, interpretacion['tipo'])
            self.mostrar_respuesta(interpretacion, resultados_procesados)
            return resultados_procesados
        else:
            print("No se encontraron productos")
            return []
    
    def mostrar_respuesta(self, interpretacion, resultados):
        """Muestra la respuesta formateada"""
        tipo = interpretacion['tipo']
        
        print(f"\nRESULTADOS:")
        
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
    asistente = AsistenteInteligente()
    
    print("=== ASISTENTE INTELIGENTE DE COMPRAS ===")
    print("Escribe 'salir' para terminar")
    print("\nEjemplos de consultas:")
    print("- ¿Cuál es la pasta de dientes más barata?")
    print("- Jabón para ropa en Metro")
    print("- Comparar aceite de cocina")
    print("- Detergente más económico")
    
    while True:
        consulta = input("\n> ").strip()
        
        if consulta.lower() in ['salir', 'exit', 'quit']:
            print("¡Hasta luego!")
            break
        
        if consulta:
            asistente.responder_consulta(consulta)
        else:
            print("Por favor ingresa una consulta válida")

if __name__ == "__main__":
    main()