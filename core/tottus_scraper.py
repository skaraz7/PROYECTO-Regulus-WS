from playwright.sync_api import sync_playwright
import json, re, random
from datetime import datetime

class TottusScraper:
    def __init__(self):
        self.base_url = "https://www.tottus.com.pe"
        # Categorías completas de Tottus - Alimentos y productos básicos
        self.categorias = {
            # Abarrotes
            'arroz': 'CATG16815',
            'sal': 'CATG16816', 
            'aceites': 'CATG16817',
            'pastas': 'CATG16818',
            'condimentos': 'CATG16819',
            'especias': 'CATG16820',
            'salsas_cremas': 'CATG16821',
            'salsas_pasta': 'CATG16822',
            'menestras': 'CATG16823',
            'sopas_bases': 'CATG16824',
            'conservas': 'CATG16825',
            'harina': 'CATG16826',
            # Lácteos y Huevos
            'huevos': 'CATG16750',
            'lacteos': 'CATG16751',
            'yogurt': 'CATG16783',
            'leche': 'CATG17094',
            'leche_condensada': 'CATG17095',
            'queso_crema': 'CATG17096',
            'yogurt_batido': 'CATG35331',
            'yogurt_familiar': 'CATG35330',
            'yogurt_griego': 'CATG35334',
            # Desayuno
            'azucar': 'CATG16808',
            'cafe': 'CATG16809',
            'cereales': 'CATG16810',
            'modificadores_leche': 'CATG16811',
            'panaderia': 'CATG16812',
            'mermeladas': 'CATG16813',
            # Bebidas
            'gaseosas': 'CATG16845',
            'aguas': 'CATG16846',
            'jugos': 'CATG16847',
            'energizantes': 'CATG16848',
            'rehidratantes': 'CATG16849',
            # Limpieza y Cuidado
            'papel_higienico': 'CATG16682',
            'jabones': 'CATG16888',
            'detergentes': 'CATG17770',
            # Snacks y Dulces
            'galletas': 'CATG16769',
            'chocolates': 'CATG16764',
            'snacks': 'CATG16763',
            'frutos_secos': 'CATG16762',
            'caramelos': 'CATG16767',
            # Carnes y Pescados
            'carnes': 'CATG16837',
            'pescados_mariscos': 'CATG16963',
            'embutidos': 'CATG16959',
            'hamburguesas': 'CATG16961',
            # Frutas y Verduras
            'frutas_verduras': 'CATG16839',
            # Congelados
            'productos_congelados': 'CATG16836',
            'helados': 'CATG16789',
            # Bebidas Alcohólicas
            'cervezas': 'CATG16070',
            'vinos': 'CATG16855',
            'licores': 'CATG16857',
            # Mascotas
            'mascotas': 'CATG16835',
            'perros': 'CATG16740',
            'gatos': 'CATG16741'
        }
    
    def _setup_browser(self, p):
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={'width': 1366, 'height': 768},
            locale='es-PE',
            timezone_id='America/Lima'
        )
        
        page = context.new_page()
        
        # Scripts anti-detección
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        return browser, page
    
    def _aceptar_cookies(self, page):
        candidatos = [
            'button:has-text("Aceptar")',
            'button:has-text("Confirmar mis preferencias")',
            '[aria-label*="Aceptar"]'
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
        """Scraping general usando función probada"""
        # Importar y usar la función que sabemos funciona
        from scraper.tottus import buscar_tottus
        
        todos_productos = []
        
        for categoria_nombre, catg_id in self.categorias.items():
            print(f"Scrapeando Tottus - {categoria_nombre}")
            
            try:
                # Usar la función probada
                productos = buscar_tottus("productos", max_items_por_categoria, catg_id)
                
                for producto in productos:
                    producto['categoria'] = categoria_nombre
                    producto['fecha_scraping'] = datetime.now().isoformat()
                    producto['precio_numerico'] = self._extraer_precio(producto['precio'])
                    todos_productos.append(producto)
                    
                print(f"Tottus: {len(productos)} productos de {categoria_nombre}")
                
            except Exception as e:
                print(f"Error en {categoria_nombre}: {e}")
        
        return todos_productos
    
    def buscar_producto(self, producto, max_items=20):
        """Búsqueda específica usando categoría por defecto"""
        # Usar categoría de abarrotes por defecto para búsquedas
        return self._buscar_en_categoria('CATG16815', producto, max_items)
    
    def _buscar_en_categoria(self, categoria_id, producto, max_items):
        """Búsqueda en categoría específica"""
        resultados = []
        
        with sync_playwright() as p:
            browser, page = self._setup_browser(p)
            
            try:
                print("Tottus: Navegación humanoide iniciada")
                page.goto(self.base_url, wait_until="load")
                page.wait_for_timeout(3000)
                page.mouse.move(random.randint(100, 500), random.randint(100, 400))
                self._aceptar_cookies(page)
                page.wait_for_timeout(2000)
                
                url = f"{self.base_url}/tottus-pe/lista/{categoria_id}"
                page.goto(url, wait_until="networkidle")
                
                # Scroll humano
                for i in range(3):
                    page.mouse.wheel(0, random.randint(200, 500))
                    page.wait_for_timeout(random.randint(1000, 2000))
                
                # Esperar productos
                try:
                    page.wait_for_selector("div.vtex-search-result-3-x-galleryItem", timeout=10000)
                except:
                    print("Tottus: No se detectaron productos")
                    return []
                
                # Extraer productos
                productos = page.evaluate("""
                    () => {
                        const items = []
                        let elements = document.querySelectorAll('div.vtex-search-result-3-x-galleryItem')
                        
                        if (elements.length === 0) {
                            elements = document.querySelectorAll('[class*="galleryItem"], .pod, [data-pod]')
                        }
                        
                        elements.forEach(prod => {
                            let nombre = ''
                            let precio = ''
                            let link = ''
                            
                            const nombreSelectors = [
                                'span.vtex-product-summary-2-x-productBrand',
                                '[class*="productBrand"]',
                                '.pod-title'
                            ]
                            for (const sel of nombreSelectors) {
                                const elem = prod.querySelector(sel)
                                if (elem && elem.innerText.trim()) {
                                    nombre = elem.innerText.trim()
                                    break
                                }
                            }
                            
                            const precioSelectors = [
                                'span.vtex-product-price-1-x-sellingPriceValue',
                                '[class*="sellingPrice"]',
                                '[class*="price"]'
                            ]
                            for (const sel of precioSelectors) {
                                const elem = prod.querySelector(sel)
                                if (elem && elem.innerText.includes('S/')) {
                                    precio = elem.innerText.trim()
                                    break
                                }
                            }
                            
                            const linkElem = prod.querySelector('a[href]')
                            if (linkElem) link = linkElem.href
                            
                            if (nombre && precio) {
                                items.push({nombre, precio, link})
                            }
                        })
                        return items
                    }
                """)
                
                for prod in productos[:max_items]:
                    resultados.append({
                        "tienda": "Tottus",
                        "nombre": prod['nombre'],
                        "precio": prod['precio'],
                        "precio_numerico": self._extraer_precio(prod['precio']),
                        "link": prod['link']
                    })
                        
            except Exception as e:
                print(f"Error buscando {producto}: {e}")
            finally:
                browser.close()
        
        return resultados
    
    def _extraer_precio(self, precio_str):
        if not precio_str:
            return 0
        match = re.search(r'S/\s*(\d+(?:\.\d+)?)', precio_str.replace(',', ''))
        return float(match.group(1)) if match else 0