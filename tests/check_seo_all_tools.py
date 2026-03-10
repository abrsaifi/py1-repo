import json
from playwright.sync_api import sync_playwright, TimeoutError

TOOLS = [
    'jpg-to-png', 'png-to-jpg', 'webp-to-png', 'image-to-pdf',
    'pdf-to-docx', 'docx-to-pdf', 'pdf-to-excel', 'excel-to-pdf',
    'pdf-to-pptx', 'pptx-to-pdf', 'csv-to-excel', 'pdf-to-image',
    'compress-pdf', 'merge-pdf', 'split-pdf', 'mp3-to-wav', 'mp4-to-webm'
]

BASE = 'http://localhost:5176/'

def check(url, page):
    logs = []
    def on_console(msg):
        logs.append({'type': msg.type, 'text': msg.text})
    page.on('console', on_console)
    page.goto(url)
    try:
        page.wait_for_selector('meta[data-seo="true"]', timeout=4000)
    except TimeoutError:
        pass
    title = page.title()
    metas = page.evaluate("Array.from(document.querySelectorAll('meta')).map(m => ({name: m.getAttribute('name'), property: m.getAttribute('property'), content: m.getAttribute('content'), dataset: m.dataset}))")
    jsonld = page.evaluate("(() => { const el = document.getElementById('schema-structured-data'); return el ? el.textContent : null })()")
    return {'url': url, 'title': title, 'meta_tags': metas, 'json_ld': jsonld, 'console': logs}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    results = []
    for slug in TOOLS:
        url = BASE + slug
        try:
            res = check(url, page)
            results.append({'slug': slug, 'ok': True, 'data': res})
        except Exception as e:
            results.append({'slug': slug, 'ok': False, 'error': str(e)})

    print(json.dumps({'results': results}, indent=2))
    browser.close()
