from playwright.sync_api import sync_playwright
import json, re
import random

def _aceptar_cookies(page):
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

def buscar_tottus(producto="arroz", max_items=10, categoria_id=None):
    resultados = []
    
    with sync_playwright() as p:
        # Stealth mode avanzado - navegador real
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--disable-plugins-discovery'
            ]
        )
        
        # Fingerprints humanos
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768},
            locale='es-PE',
            timezone_id='America/Lima',
            geolocation={'latitude': -12.0464, 'longitude': -77.0428},
            permissions=['geolocation'],
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-PE,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        page = context.new_page()
        
        # Inyectar scripts anti-detección
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-PE', 'es', 'en'],
            });
            
            window.chrome = {
                runtime: {},
            };
            
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        try:
            # Simular comportamiento humano - ir primero a homepage
            page.goto("https://www.tottus.com.pe", wait_until="load")
            page.wait_for_timeout(3000)
            
            # Movimientos de mouse aleatorios
            page.mouse.move(random.randint(100, 500), random.randint(100, 400))
            page.wait_for_timeout(1000)
            
            # Aceptar cookies
            _aceptar_cookies(page)
            page.wait_for_timeout(2000)
            
            # Navegar a la categoría especificada
            if categoria_id:
                url_categoria = f"https://www.tottus.com.pe/tottus-pe/lista/{categoria_id}"
            else:
                url_categoria = "https://www.tottus.com.pe/tottus-pe/lista/CATG16815/Arroz"
            
            page.goto(url_categoria, wait_until="networkidle")
            
            # Simular scroll humano
            for i in range(3):
                page.mouse.wheel(0, random.randint(200, 500))
                page.wait_for_timeout(random.randint(1000, 2000))
            
            # Esperar productos con múltiples intentos
            productos_detectados = False
            for intento in range(3):
                try:
                    page.wait_for_selector("div.vtex-search-result-3-x-galleryItem, .pod, [data-pod], [class*='product']", timeout=10000)
                    productos_detectados = True
                    break
                except Exception:
                    page.wait_for_timeout(5000)
                    page.reload(wait_until="networkidle")
            
            # Extraer datos desde el DOM renderizado
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
                            '.pod-title',
                            '.pod-subTitle'
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
                            '[class*="price"]',
                            '.copy10'
                        ]
                        for (const sel of precioSelectors) {
                            const elem = prod.querySelector(sel)
                            if (elem && elem.innerText.includes('S/')) {
                                precio = elem.innerText.trim()
                                break
                            }
                        }
                        
                        const linkSelectors = [
                            'a.vtex-product-summary-2-x-clearLink',
                            'a[href]'
                        ]
                        for (const sel of linkSelectors) {
                            const elem = prod.querySelector(sel)
                            if (elem && elem.href) {
                                link = elem.href
                                break
                            }
                        }
                        
                        if (nombre && precio) {
                            items.push({nombre, precio, link})
                        }
                    })
                    return items
                }
            """)
            
            # Procesar para compatibilidad con el sistema
            for producto in productos[:max_items]:
                resultados.append({
                    "tienda": "Tottus",
                    "nombre": producto['nombre'],
                    "precio": producto['precio'],
                    "link": producto['link']
                })
                
        except Exception as e:
            print(f"Tottus: Error: {e}")
        finally:
            browser.close()
    
    return resultados