from playwright.sync_api import sync_playwright
import json, re

def _aceptar_cookies(page):
    # Plaza Vea tiene muro de cookies agresivo
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
    # Intento con getByRole como sugiere ChatGPT
    try:
        page.get_by_role('button', name=re.compile(r'Aceptar|Confirmar mis preferencias', re.I)).click(timeout=3000)
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
                        productos.append({'tienda':'Plaza Vea','nombre':name,'precio':f"S/ {price}",'link':url or ''})
                if isinstance(d, dict) and (d.get('@type') == 'ItemList'):
                    for it in d.get('itemListElement', []):
                        item = it.get('item') if isinstance(it, dict) else {}
                        name = (item or {}).get('name')
                        offers = (item or {}).get('offers') or {}
                        price = offers.get('price') or offers.get('lowPrice')
                        url = (item or {}).get('url')
                        if name and price:
                            productos.append({'tienda':'Plaza Vea','nombre':name,'precio':f"S/ {price}",'link':url or ''})
    except Exception:
        pass
    return productos

def buscar_plazavea(producto="arroz", max_items=10, categoria_url=None):
    if categoria_url:
        url = categoria_url
    elif producto.lower() == "arroz":
        url = "https://www.plazavea.com.pe/abarrotes/arroz"
    else:
        url = f"https://www.plazavea.com.pe/search?_q={producto}"
    
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
            page.wait_for_timeout(5000)
            # Manejo agresivo de cookies para Plaza Vea
            _aceptar_cookies(page)
            page.wait_for_timeout(3000)
            _aceptar_cookies(page)  # Segundo intento
            # Scroll para cargar productos
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
        except Exception as e:
            print(f"Error cargando Plaza Vea: {e}")

        # Plaza Vea usa estructura diferente a VTEX
        cards = page.locator('.Showcase.ga-product-item')
        count = cards.count()
        for i in range(min(count, max_items)):
            c = cards.nth(i)
            try:
                nombre = c.locator('.Showcase__name').first.inner_text().strip()
            except Exception:
                nombre = ""
            try:
                precio = c.locator('.Showcase__salePrice .price').first.inner_text().strip()
            except Exception:
                precio = ""
            link = ""
            try:
                href = c.locator('.Showcase__link').first.get_attribute('href') or ""
                link = href if href.startswith("http") else f"https://www.plazavea.com.pe{href}"
            except Exception:
                pass

            if nombre and (precio or "S/" in precio):
                resultados.append({"tienda":"Plaza Vea","nombre":nombre,"precio":precio or "", "link":link})

        if not resultados:
            resultados = _extraer_jsonld(page)

        browser.close()
    return resultados