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
                # Product directo
                if isinstance(d, dict) and (d.get('@type') == 'Product' or str(d.get('@type','')).lower() == 'product'):
                    name = d.get('name')
                    offers = d.get('offers') or {}
                    if isinstance(offers, list) and offers:
                        offers = offers[0]
                    price = (offers or {}).get('price') or (offers or {}).get('lowPrice')
                    url = d.get('url') or d.get('@id')
                    if name and price:
                        productos.append({'tienda':'Metro','nombre':name,'precio':f"S/ {price}",'link':url or ''})
                # ItemList con items
                if isinstance(d, dict) and (d.get('@type') == 'ItemList'):
                    for it in d.get('itemListElement', []):
                        item = it.get('item') if isinstance(it, dict) else {}
                        name = (item or {}).get('name')
                        offers = (item or {}).get('offers') or {}
                        price = offers.get('price') or offers.get('lowPrice')
                        url = (item or {}).get('url')
                        if name and price:
                            productos.append({'tienda':'Metro','nombre':name,'precio':f"S/ {price}",'link':url or ''})
    except Exception:
        pass
    return productos

def buscar_metro(producto="arroz", max_items=10, categoria_url=None):
    if categoria_url:
        url = categoria_url
        print(f"Metro: Usando categoria especifica: {url}")
    elif producto.lower() == "arroz":
        url = "https://www.metro.pe/abarrotes/arroz"
    else:
        url = f"https://www.metro.pe/search?_q={producto}"
    resultados = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(45000)
        try:
            page.goto(url, wait_until="load")
            page.wait_for_timeout(3000)
            _aceptar_cookies(page)
            # Scroll para cargar productos
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error cargando Metro: {e}")

        # VTEX: cards de resultados
        cards = page.locator('[class*="vtex-search-result"] [class*="galleryItem"]')
        count = cards.count()
        print(f"Metro: Encontrados {count} elementos")
        for i in range(min(count, max_items)):
            c = cards.nth(i)
            try:
                nombre = c.locator('[class*="vtex-product-summary"] [class*="productBrand"]').first.inner_text().strip()
            except Exception:
                nombre = ""
            try:
                precio = c.locator('span[class*="sellingPriceValue"], span[class*="price_sellingPrice"]').first.inner_text().strip()
            except Exception:
                precio = ""
            link = ""
            try:
                href = c.locator('a[href]').first.get_attribute('href') or ""
                link = href if href.startswith("http") else f"https://www.metro.pe{href}"
            except Exception:
                pass

            if nombre and (precio or "S/" in precio):
                resultados.append({"tienda":"Metro","nombre":nombre,"precio":precio or "", "link":link})

        # Fallback JSON-LD si no hubo DOM
        if not resultados:
            resultados = _extraer_jsonld(page)

        browser.close()
    return resultados