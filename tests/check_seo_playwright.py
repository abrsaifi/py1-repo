import json
from playwright.sync_api import sync_playwright, TimeoutError

URL = 'http://localhost:5173/jpg-to-png'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    logs = []
    def on_console(msg):
        logs.append({'type': msg.type, 'text': msg.text})
    page.on('console', on_console)
    page.goto(URL)
    try:
        page.wait_for_selector('meta[data-seo="true"]', timeout=5000)
    except TimeoutError:
        # proceed anyway
        pass

    title = page.title()

    metas = page.evaluate("Array.from(document.querySelectorAll('meta')).map(m => ({name: m.getAttribute('name'), property: m.getAttribute('property'), content: m.getAttribute('content'), dataset: m.dataset}))")

    jsonld = page.evaluate("(() => { const el = document.getElementById('schema-structured-data'); return el ? el.textContent : null })()")

    result = {
        'url': URL,
        'title': title,
        'meta_tags': metas,
        'json_ld': jsonld
    }

    output = {'result': result, 'console': logs}
    print(json.dumps(output, indent=2))

    browser.close()
