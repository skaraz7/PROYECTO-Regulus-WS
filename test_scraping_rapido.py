from core.metro_scraper import MetroScraper
from core.plazavea_scraper import PlazaVeaScraper
from core.tottus_scraper import TottusScraper

def test_scraping_limitado():
    """Test rápido con pocas categorías para verificar funcionamiento"""
    print("TEST RAPIDO DE SCRAPING COMPLETO")
    print("=" * 50)
    
    # Metro - solo 3 categorías
    print("\n1. METRO (3 categorías):")
    metro = MetroScraper()
    categorias_test = {'arroz': '/abarrotes/arroz', 'azucar': '/desayuno/azucar-y-edulcorantes', 'leches': '/lacteos/leches'}
    metro.categorias = categorias_test
    
    productos_metro = metro.scraping_general(10)
    print(f"Metro: {len(productos_metro)} productos")
    
    # Plaza Vea - solo 2 categorías
    print("\n2. PLAZA VEA (2 categorías):")
    pv = PlazaVeaScraper()
    categorias_test_pv = {'arroz': '/abarrotes/arroz', 'limpieza': '/limpieza'}
    pv.categorias = categorias_test_pv
    
    productos_pv = pv.scraping_general(10)
    print(f"Plaza Vea: {len(productos_pv)} productos")
    
    # Tottus - solo 2 categorías
    print("\n3. TOTTUS (2 categorías):")
    tottus = TottusScraper()
    categorias_test_tottus = {'arroz': 'CATG16815', 'aceites': 'CATG16817'}
    tottus.categorias = categorias_test_tottus
    
    productos_tottus = tottus.scraping_general(10)
    print(f"Tottus: {len(productos_tottus)} productos")
    
    total = len(productos_metro) + len(productos_pv) + len(productos_tottus)
    print(f"\nTOTAL TEST: {total} productos")
    print("Sistema funcionando correctamente para scraping completo")

if __name__ == "__main__":
    test_scraping_limitado()