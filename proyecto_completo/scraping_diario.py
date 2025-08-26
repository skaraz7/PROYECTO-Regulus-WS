import json
import os
from datetime import datetime
from core.metro_scraper import MetroScraper
from core.plazavea_scraper import PlazaVeaScraper
from core.tottus_scraper import TottusScraper

class ScrapingDiario:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Crear directorio data si no existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def ejecutar_scraping_completo(self):
        """Ejecuta scraping completo de todas las tiendas"""
        print("=" * 60)
        print("INICIANDO SCRAPING DIARIO COMPLETO")
        print("=" * 60)
        
        resultados = {}
        
        # Metro
        print("\n1. SCRAPING METRO...")
        try:
            metro = MetroScraper()
            productos_metro = metro.scraping_general(max_items_por_categoria=100)
            
            data_metro = {
                "tienda": "Metro",
                "fecha_actualizacion": datetime.now().isoformat(),
                "total_productos": len(productos_metro),
                "productos": productos_metro
            }
            
            with open(f"{self.data_dir}/metro_completo.json", 'w', encoding='utf-8') as f:
                json.dump(data_metro, f, indent=2, ensure_ascii=False)
            
            resultados["metro"] = len(productos_metro)
            print(f"Metro: {len(productos_metro)} productos guardados")
            
        except Exception as e:
            print(f"Error en Metro: {e}")
            resultados["metro"] = 0
        
        # Plaza Vea
        print("\n2. SCRAPING PLAZA VEA...")
        try:
            plazavea = PlazaVeaScraper()
            productos_pv = plazavea.scraping_general(max_items_por_categoria=100)
            
            data_pv = {
                "tienda": "Plaza Vea",
                "fecha_actualizacion": datetime.now().isoformat(),
                "total_productos": len(productos_pv),
                "productos": productos_pv
            }
            
            with open(f"{self.data_dir}/plazavea_completo.json", 'w', encoding='utf-8') as f:
                json.dump(data_pv, f, indent=2, ensure_ascii=False)
            
            resultados["plazavea"] = len(productos_pv)
            print(f"Plaza Vea: {len(productos_pv)} productos guardados")
            
        except Exception as e:
            print(f"Error en Plaza Vea: {e}")
            resultados["plazavea"] = 0
        
        # Tottus
        print("\n3. SCRAPING TOTTUS...")
        try:
            tottus = TottusScraper()
            productos_tottus = tottus.scraping_general(max_items_por_categoria=100)
            
            data_tottus = {
                "tienda": "Tottus",
                "fecha_actualizacion": datetime.now().isoformat(),
                "total_productos": len(productos_tottus),
                "productos": productos_tottus
            }
            
            with open(f"{self.data_dir}/tottus_completo.json", 'w', encoding='utf-8') as f:
                json.dump(data_tottus, f, indent=2, ensure_ascii=False)
            
            resultados["tottus"] = len(productos_tottus)
            print(f"Tottus: {len(productos_tottus)} productos guardados")
            
        except Exception as e:
            print(f"Error en Tottus: {e}")
            resultados["tottus"] = 0
        
        # Resumen final
        total_productos = sum(resultados.values())
        
        resumen = {
            "fecha_scraping": datetime.now().isoformat(),
            "resultados": resultados,
            "total_productos": total_productos
        }
        
        with open(f"{self.data_dir}/resumen_scraping.json", 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SCRAPING DIARIO COMPLETADO")
        print(f"Total productos recolectados: {total_productos}")
        print(f"Metro: {resultados.get('metro', 0)}")
        print(f"Plaza Vea: {resultados.get('plazavea', 0)}")
        print(f"Tottus: {resultados.get('tottus', 0)}")
        print("=" * 60)
        
        return resultados

def main():
    scraper = ScrapingDiario()
    scraper.ejecutar_scraping_completo()

if __name__ == "__main__":
    main()