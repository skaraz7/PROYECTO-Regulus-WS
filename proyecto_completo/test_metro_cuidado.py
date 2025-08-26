from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    print("Probando Metro - Cuidado Personal...")
    page.goto('https://www.metro.pe/cuidado-personal', wait_until='load')
    page.wait_for_timeout(3000)
    
    # Probar diferentes selectores
    selectors = [
        '[class*="vtex-search-result"] [class*="galleryItem"]',
        '[class*="galleryItem"]',
        '.vtex-search-result-3-x-galleryItem'
    ]
    
    for selector in selectors:
        cards = page.locator(selector)
        count = cards.count()
        print(f"Selector '{selector}': {count} productos")
        if count > 0:
            break
    
    browser.close()