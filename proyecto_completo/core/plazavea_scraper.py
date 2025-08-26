from playwright.sync_api import sync_playwright
import json, re
from datetime import datetime

class PlazaVeaScraper:
    def __init__(self):
        self.base_url = "https://www.plazavea.com.pe"
        self.categorias = {
            'abarrotes': '/abarrotes',
            'arroz': '/abarrotes/arroz',
            'aceites': '/abarrotes/aceites',
            'limpieza': '/limpieza',
            'jabones': '/limpieza/jabones',
            'lacteos': '/lacteos-y-huevos',
            'desayuno': '/desayuno',
            'cuidado_personal': '/cuidado-personal',
            'bebidas': '/bebidas',
            'frutas_verduras': '/frutas-y-verduras',
            'carnes_pollos': '/carnes-y-pollos'
        }
    
    def _aceptar_cookies(self, page):
        candidatos = [
            'button:has-text("Aceptar")',
            'button:has-text("Confirmar mis preferencias")',
            'button:has-text("Acepto")',
            '#onetrust-accept-btn-handler',
            '[aria-label*="Aceptar"]'
        ]
        for sel in candidatos:
            try:
                el = page.locator(sel).first
                if el.is_visible():
                    el.click(timeout=5000)
                    page.wait_for_timeout(1000)
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
                print(f"Scrapeando Plaza Vea - {categoria}")
                try:
                    url = f"{self.base_url}{url_path}"
                    page.goto(url, wait_until="load")
                    page.wait_for_timeout(5000)
                    self._aceptar_cookies(page)
                    page.wait_for_timeout(3000)
                    
                    # Scroll para cargar productos
                    for i in range(5):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(1000)
                    
                    # Extraer productos
                    cards = page.locator('.Showcase.ga-product-item')
                    count = min(cards.count(), max_items_por_categoria)
                    
                    for i in range(count):
                        c = cards.nth(i)
                        try:
                            nombre = c.locator('.Showcase__name').first.inner_text().strip()
                            precio = c.locator('.Showcase__salePrice .price').first.inner_text().strip()
                            href = c.locator('.Showcase__link').first.get_attribute('href') or ""
                            link = href if href.startswith("http") else f"{self.base_url}{href}"
                            
                            if nombre and precio:
                                todos_productos.append({
                                    "tienda": "Plaza Vea",
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
                page.wait_for_timeout(5000)
                self._aceptar_cookies(page)
                
                # Scroll
                for i in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                
                cards = page.locator('.Showcase.ga-product-item')
                count = min(cards.count(), max_items)
                
                for i in range(count):
                    c = cards.nth(i)
                    try:
                        nombre = c.locator('.Showcase__name').first.inner_text().strip()
                        precio = c.locator('.Showcase__salePrice .price').first.inner_text().strip()
                        href = c.locator('.Showcase__link').first.get_attribute('href') or ""
                        link = href if href.startswith("http") else f"{self.base_url}{href}"
                        
                        if nombre and precio:
                            resultados.append({
                                "tienda": "Plaza Vea",
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