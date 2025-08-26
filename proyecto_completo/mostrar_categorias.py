import json
import os

def mostrar_todas_las_categorias():
    print("=" * 60)
    print("CATEGORIAS DISPONIBLES POR TIENDA")
    print("=" * 60)
    
    # Metro - desde archivo JSON
    print("\n1. METRO:")
    if os.path.exists('metro_categories_from_html.json'):
        with open('metro_categories_from_html.json', 'r', encoding='utf-8') as f:
            metro_cats = json.load(f)
        
        for categoria, subcategorias in metro_cats.items():
            print(f"  {categoria}:")
            for sub in subcategorias:
                print(f"    - {sub['name']}: {sub['url']}")
    
    # Plaza Vea - desde archivo JSON
    print("\n2. PLAZA VEA:")
    if os.path.exists('plazavea_categorias.json'):
        with open('plazavea_categorias.json', 'r', encoding='utf-8') as f:
            pv_cats = json.load(f)
        
        for cat in pv_cats:
            print(f"  - {cat['nombre']}: {cat['url']}")
    
    # Tottus - desde archivo TXT
    print("\n3. TOTTUS:")
    if os.path.exists('tottus_categories.txt'):
        with open('tottus_categories.txt', 'r', encoding='utf-8') as f:
            tottus_cats = f.read()
        print("  Categorías extraídas:")
        lines = tottus_cats.split('\n')[:20]  # Mostrar solo las primeras 20
        for line in lines:
            if line.strip():
                print(f"  - {line.strip()}")
        print("  ... (y más)")
    
    # Categorías válidas de Tottus
    if os.path.exists('valid_categories.json'):
        with open('valid_categories.json', 'r', encoding='utf-8') as f:
            valid_cats = json.load(f)
        
        print("\n  Categorías válidas de Tottus:")
        for cat_id, info in list(valid_cats.items())[:10]:
            print(f"  - {cat_id}: {info}")
        print(f"  ... Total: {len(valid_cats)} categorías")
    
    # Categorías actualmente configuradas en scrapers
    print("\n" + "=" * 60)
    print("CATEGORIAS CONFIGURADAS EN SCRAPERS")
    print("=" * 60)
    
    print("\nMETRO (core/metro_scraper.py):")
    from core.metro_scraper import MetroScraper
    metro = MetroScraper()
    for cat, url in metro.categorias.items():
        print(f"  - {cat}: https://www.metro.pe{url}")
    
    print("\nPLAZA VEA (core/plazavea_scraper.py):")
    from core.plazavea_scraper import PlazaVeaScraper
    pv = PlazaVeaScraper()
    for cat, url in pv.categorias.items():
        print(f"  - {cat}: https://www.plazavea.com.pe{url}")
    
    print("\nTOTTUS (core/tottus_scraper.py):")
    from core.tottus_scraper import TottusScraper
    tottus = TottusScraper()
    for cat, cat_id in tottus.categorias.items():
        print(f"  - {cat}: CATG{cat_id} (solo abarrotes configurado)")

if __name__ == "__main__":
    mostrar_todas_las_categorias()