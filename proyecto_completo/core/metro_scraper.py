from playwright.sync_api import sync_playwright
import json, re
from datetime import datetime

class MetroScraper:
    def __init__(self):
        self.base_url = "https://www.metro.pe"
        self.categorias = {
            # Abarrotes - Todas las subcategorías
            'aceites': '/abarrotes/aceites',
            'arroz': '/abarrotes/arroz',
            'fideos_pastas': '/abarrotes/fideos-pastas-y-salsas',
            'conservas': '/abarrotes/alimentos-en-conserva',
            'chocolateria': '/abarrotes/chocolateria',
            'condimentos': '/abarrotes/condimentos-vinagres-y-comida-instantanea',
            'galletas_snacks': '/abarrotes/galletas-snacks-y-golosinas',
            'menestras': '/abarrotes/menestras',
            'reposteria': '/abarrotes/reposteria',
            # Desayuno - Todas las subcategorías
            'azucar': '/desayuno/azucar-y-edulcorantes',
            'cafe': '/desayuno/cafe-e-infusiones',
            'cereales': '/desayuno/cereales-y-avenas',
            'mermeladas': '/desayuno/mermeladas-y-mieles',
            'modificadores': '/desayuno/modificadores-de-leche',
            'panes': '/desayuno/panes-y-tortillas-empacadas',
            'suplementos': '/desayuno/suplementos-nutricionales-para-adultos',
            # Lácteos - Todas las subcategorías
            'leches': '/lacteos/leches',
            'yogures': '/lacteos/yogures',
            'mantequillas': '/lacteos/mantequillas-y-margarinas',
            'queseria': '/lacteos/la-queseria',
            # Limpieza
            'limpieza': '/limpieza',
            # Carnes y Pescados - Todas las subcategorías
            'aves_huevos': '/carnes-aves-y-pescados/aves-y-huevos',
            'pescados_mariscos': '/carnes-aves-y-pescados/pescados-y-mariscos',
            'res_carnes': '/carnes-aves-y-pescados/res-y-otras-carnes',
            'cerdo': '/carnes-aves-y-pescados/cerdo',
            'hamburguesas_apanados': '/carnes-aves-y-pescados/hamburguesas-y-apanados',
            'premium_carnes': '/carnes-pollos-y-pescados/premium',
            'empanizados_pescados': '/carnes-pollos-y-pescados/empanizados-de-pescados',
            # Frutas y Verduras
            'frutas': '/frutas-y-verduras/frutas',
            'verduras': '/frutas-y-verduras/verduras',
            # Embutidos y Fiambres - Todas las subcategorías
            'embutidos': '/embutidos-y-fiambres/embutidos',
            'fiambres': '/embutidos-y-fiambres/fiambres',
            'delicatessen': '/embutidos-y-fiambres/delicatessen'
        }
    
    def _aceptar_cookies(self, page):
        candidatos = [
            'button:has-text("Aceptar")',
            'button:has-text("Confirmar mis preferencias")',
            '[aria-label*="Aceptar"]',
            'button:has-text("Acepto")',
            '#onetrust-accept-btn-handler'
        ]
        for sel in candidatos:
            try:
                el = page.locator(sel).first
                if el.is_visible():
                    el.click(timeout=3000)
                    break
            except Exception:
                pass
    
    def scraping_general(self, max_items_por_categoria=50):
        """Scraping general de todas las categorías"""
        todos_productos = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            page.set_default_timeout(45000)
            
            for categoria, url_path in self.categorias.items():
                print(f"Scrapeando Metro - {categoria}")
                try:
                    url = f"{self.base_url}{url_path}"
                    page.goto(url, wait_until="load")
                    page.wait_for_timeout(3000)
                    self._aceptar_cookies(page)
                    
                    # Scroll para cargar productos
                    for i in range(5):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1000)
                    
                    # Extraer productos
                    cards = page.locator('[class*="vtex-search-result"] [class*="galleryItem"]')
                    count = min(cards.count(), max_items_por_categoria)
                    
                    for i in range(count):
                        c = cards.nth(i)
                        try:
                            nombre = c.locator('[class*="vtex-product-summary"] [class*="productBrand"]').first.inner_text().strip()
                            precio = c.locator('span[class*="sellingPriceValue"], span[class*="price_sellingPrice"]').first.inner_text().strip()
                            href = c.locator('a[href]').first.get_attribute('href') or ""
                            link = href if href.startswith("http") else f"{self.base_url}{href}"
                            
                            if nombre and precio:
                                todos_productos.append({
                                    "tienda": "Metro",
                                    "categoria": categoria,
                                    "nombre": nombre,
                                    "precio": precio,
                                    "precio_numerico": self._extraer_precio(precio),
                                    "link": link,
                                    "fecha_scraping": datetime.now().isoformat()
                                })
                        except Exception:
                            continue
                            
                except Exception as e:
                    print(f"Error en categoría {categoria}: {e}")
            
            browser.close()
        
        return todos_productos
    
    def buscar_producto(self, producto, max_items=20):
        """Búsqueda específica de un producto"""
        url = f"{self.base_url}/search?_q={producto}"
        resultados = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                page.goto(url, wait_until="load")
                page.wait_for_timeout(3000)
                self._aceptar_cookies(page)
                
                # Scroll
                for i in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                
                cards = page.locator('[class*="vtex-search-result"] [class*="galleryItem"]')
                count = min(cards.count(), max_items)
                
                for i in range(count):
                    c = cards.nth(i)
                    try:
                        nombre = c.locator('[class*="vtex-product-summary"] [class*="productBrand"]').first.inner_text().strip()
                        precio = c.locator('span[class*="sellingPriceValue"]').first.inner_text().strip()
                        href = c.locator('a[href]').first.get_attribute('href') or ""
                        link = href if href.startswith("http") else f"{self.base_url}{href}"
                        
                        if nombre and precio:
                            resultados.append({
                                "tienda": "Metro",
                                "nombre": nombre,
                                "precio": precio,
                                "precio_numerico": self._extraer_precio(precio),
                                "link": link
                            })
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Error buscando {producto}: {e}")
            
            browser.close()
        
        return resultados
    
    def _extraer_precio(self, precio_str):
        if not precio_str:
            return 0
        match = re.search(r'S/\s*(\d+(?:\.\d+)?)', precio_str.replace(',', ''))
        return float(match.group(1)) if match else 0