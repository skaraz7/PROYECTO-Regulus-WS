from playwright.sync_api import sync_playwright
import json, re

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

def _extraer_jsonld(page):
    productos = []
    try:
        scripts = page.locator('script[type="application/ld+json"]').all()
        for s in scripts:
            raw = s.text_content()
            if not raw:
                continue
            data = json.loads(raw)
            arr = data if isinstance(data, list) else [data]
            for d in arr:
                if isinstance(d, dict) and (d.get('@type') == 'Product' or str(d.get('@type','')).lower() == 'product'):
                    name = d.get('name')
                    offers = d.get('offers') or {}
                    if isinstance(offers, list) and offers:
                        offers = offers[0]
                    price = (offers or {}).get('price') or (offers or {}).get('lowPrice')
                    url = d.get('url') or d.get('@id')
                    if name and price:
                        productos.append({'tienda':'Tottus','nombre':name,'precio':f"S/ {price}",'link':url or ''})
                if isinstance(d, dict) and (d.get('@type') == 'ItemList'):
                    for it in d.get('itemListElement', []):
                        item = it.get('item') if isinstance(it, dict) else {}
                        name = (item or {}).get('name')
                        offers = (item or {}).get('offers') or {}
                        price = offers.get('price') or offers.get('lowPrice')
                        url = (item or {}).get('url')
                        if name and price:
                            productos.append({'tienda':'Tottus','nombre':name,'precio':f"S/ {price}",'link':url or ''})
    except Exception:
        pass
    return productos

def buscar_tottus(producto="arroz", max_items=10, categoria_id=None):
    resultados = []
    
    with sync_playwright() as p:
        # Stealth mode avanzado - navegador real
        browser = p.chromium.launch(
            headless=True,  # Cambiar a headless para evitar ventanas
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
            viewport={'width': 1366, 'height': 768},  # Resolución común
            locale='es-PE',
            timezone_id='America/Lima',
            geolocation={'latitude': -12.0464, 'longitude': -77.0428},  # Lima, Perú
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
            // Eliminar webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Fingir plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Fingir idiomas
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-PE', 'es', 'en'],
            });
            
            // Eliminar automation flags
            window.chrome = {
                runtime: {},
            };
            
            // Fingir permisos
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        try:
            print("Tottus: Navegación humanoide iniciada")
            
            # Simular comportamiento humano - ir primero a homepage
            page.goto("https://www.tottus.com.pe", wait_until="load")
            page.wait_for_timeout(3000)
            
            # Movimientos de mouse aleatorios
            import random
            page.mouse.move(random.randint(100, 500), random.randint(100, 400))
            page.wait_for_timeout(1000)
            
            # Aceptar cookies
            _aceptar_cookies(page)
            page.wait_for_timeout(2000)
            
            # Navegar a la categoría especificada
            if categoria_id:
                url_categoria = f"https://www.tottus.com.pe/tottus-pe/lista/{categoria_id}"
                print(f"Tottus: Navegando a categoría {categoria_id}")
            else:
                url_categoria = "https://www.tottus.com.pe/tottus-pe/lista/CATG16815/Arroz"
                print("Tottus: Navegando a categoría arroz por defecto")
            
            page.goto(url_categoria, wait_until="networkidle")
            
            # Simular scroll humano
            for i in range(3):
                page.mouse.wheel(0, random.randint(200, 500))
                page.wait_for_timeout(random.randint(1000, 2000))
            
            current_url = page.url
            print(f"Tottus: URL actual: {current_url}")
            
            # Esperar productos con múltiples intentos
            productos_detectados = False
            for intento in range(3):
                try:
                    page.wait_for_selector("div.vtex-search-result-3-x-galleryItem, .pod, [data-pod], [class*='product']", timeout=10000)
                    productos_detectados = True
                    print(f"Tottus: Productos detectados en intento {intento + 1}")
                    break
                except Exception:
                    print(f"Tottus: Intento {intento + 1} fallido, esperando...")
                    page.wait_for_timeout(5000)
                    page.reload(wait_until="networkidle")
            
            if not productos_detectados:
                print("Tottus: No se detectaron productos después de 3 intentos")
            
            # Extraer datos desde el DOM renderizado
            productos = page.evaluate("""
                () => {
                    const items = []
                    // Probar selectores VTEX
                    let elements = document.querySelectorAll('div.vtex-search-result-3-x-galleryItem')
                    
                    // Si no hay VTEX, probar selectores genéricos
                    if (elements.length === 0) {
                        elements = document.querySelectorAll('[class*="galleryItem"], .pod, [data-pod]')
                    }
                    
                    elements.forEach(prod => {
                        let nombre = ''
                        let precio = ''
                        let link = ''
                        
                        // Intentar extraer nombre
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
                        
                        // Intentar extraer precio
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
                        
                        // Intentar extraer link
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
            
            print(f"Tottus: Extraidos {len(productos)} productos del DOM")
            
            # Guardar en archivo JSON
            with open('tottus_arroz.json', 'w', encoding='utf-8') as f:
                json.dump(productos, f, indent=2, ensure_ascii=False)
            
            # Procesar para compatibilidad con el sistema
            for producto in productos[:max_items]:
                resultados.append({
                    "tienda": "Tottus",
                    "nombre": producto['nombre'],
                    "precio": producto['precio'],
                    "link": producto['link']
                })
            
            # Mostrar validación
            if productos:
                primer_producto = productos[0]
                print(f"Tottus: Primer producto: {primer_producto['nombre']} - {primer_producto['precio']}")
            else:
                print("Tottus: No se encontraron productos")
                
        except Exception as e:
            print(f"Tottus: Error: {e}")
        finally:
            browser.close()
    
    print(f"Tottus: Extraidos {len(resultados)} productos para el sistema")
    return resultados