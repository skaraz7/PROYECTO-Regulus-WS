from core.metro_scraper import MetroScraper
from core.plazavea_scraper import PlazaVeaScraper
from core.tottus_scraper import TottusScraper

def mostrar_categorias_configuradas():
    print("CATEGORIAS CONFIGURADAS PARA SCRAPING COMPLETO")
    print("=" * 60)
    
    # Metro
    metro = MetroScraper()
    print(f"\nMETRO - {len(metro.categorias)} categorías:")
    for i, (cat, url) in enumerate(metro.categorias.items(), 1):
        print(f"{i:2d}. {cat}: {url}")
    
    # Plaza Vea
    pv = PlazaVeaScraper()
    print(f"\nPLAZA VEA - {len(pv.categorias)} categorías:")
    for i, (cat, url) in enumerate(pv.categorias.items(), 1):
        print(f"{i:2d}. {cat}: {url}")
    
    # Tottus
    tottus = TottusScraper()
    print(f"\nTOTTUS - {len(tottus.categorias)} categorías:")
    for i, (cat, catg_id) in enumerate(tottus.categorias.items(), 1):
        print(f"{i:2d}. {cat}: {catg_id}")
    
    total_categorias = len(metro.categorias) + len(pv.categorias) + len(tottus.categorias)
    print(f"\nTOTAL CATEGORIAS: {total_categorias}")
    print("Estimado de productos: ~5,000-10,000 productos")

if __name__ == "__main__":
    mostrar_categorias_configuradas()