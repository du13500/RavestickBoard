"""Bildschirmfotos der echten Oberfläche (web/index.html) mit der simulierten API aus den Browsertests.
Für den Vorher/Nachher-Vergleich der Design-Tokens: gleiche Seiten, gleiche Daten, Handy und Laptop.
Aufruf: python tests/design_shots_0800.py <Zielordner>
Nicht geprüft: echtes iPhone/Safari."""
import re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
_src = (ROOT / 'tests/test_browser_ui_0800.py').read_text(encoding='utf8')
_ns = {'__file__': str(ROOT / 'tests/test_browser_ui_0800.py'), 'sys': sys, 're': re, 'json': json, 'Path': Path}
exec(_src[:_src.index('with sync_playwright() as pw:')].replace('SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None', 'SHOTS = None'), _ns)
boot = _ns['boot']
VIEWS = [('home', None), ('editor', "setTab('scroll')"), ('editor-block', "setTab('pages')"), ('library', None),
         ('programs', None), ('ambience', None), ('animations', None), ('settings', None), ('diagnostics', None)]
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    for dev, (w, h, touch) in {'handy': (390, 844, True), 'laptop': (1280, 860, False)}.items():
        ctx, page, errs = boot(browser, w, h, touch=touch)
        page.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important;caret-color:transparent!important}')
        for name, extra in VIEWS:
            page.evaluate(f"navigate('{name.split('-')[0]}')"); page.wait_for_timeout(400)
            if extra: page.evaluate(extra); page.wait_for_timeout(300)
            page.evaluate('window.scrollTo(0,0)'); page.wait_for_timeout(150)
            page.screenshot(path=str(OUT / f'{dev}_{name}.png'), full_page=True)
        if errs: print('Seitenfehler', dev, errs[:3])
        ctx.close()
    browser.close()
print('Bilder:', len(list(OUT.glob('*.png'))))
