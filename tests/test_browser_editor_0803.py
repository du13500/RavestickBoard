"""Schwenk über großes Bild und Frame-Editor im echten (headless) Chromium mit simulierter API.
Schwenk: Fenster-Positionen, Versatz-Rechnung (Frames/Ende/Versatz), Stoppen/Umlauf, Nutzlast gegen unabhängige Referenz.
Editor: Zeichnen (Stift, Radierer, Füllen, Pipette, Auswahl), Rückgängig/Wiederherstellen, Bildleiste, Zwiebelschicht, Zoom,
Gesten nur im Zeichenfeld, Sperre im Hochformat und bei zu kleinem Feld, Bearbeiten gespeicherter Animationen.
Kleinpaket: Tempo-Hinweis im Programm, gleiche Breite bei klassischem Scrollbalken, Backup-Knöpfe behalten ihre Farbe.
Aufruf: python tests/test_browser_editor_0803.py
Nicht geprüft: iPad/iPhone-Safari, echter Apple Pencil, echte Zwei-Finger-Gesten auf Hardware."""
import io, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
_p = ROOT / 'tests/test_browser_anim_0803.py'
_src = _p.read_text(encoding='utf8')
_head = _src[:_src.index('with sync_playwright() as pw:')]
_ns = {'__file__': str(_p), 'sys': sys, 're': re, 'json': json, 'Path': Path, '__name__': 'anim_base'}
_head = _head.replace('SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None', 'SHOTS = None')
exec(_head, _ns)
check, errors, ref_payload, RGB, grid = _ns['check'], _ns['errors'], _ns['ref_payload'], _ns['RGB'], _ns['grid']
html, base, ANIM_MOCK = _ns['html'], _ns['base'], _ns['ANIM_MOCK']
from PIL import Image
from playwright.sync_api import sync_playwright

def page_with(browser, w, h, touch=True, classic_scroll=False):
    ctx = browser.new_context(viewport={'width': w, 'height': h}, is_mobile=touch, has_touch=touch, accept_downloads=True)
    page = ctx.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append('console:' + m.text) if m.type == 'error' else None)
    page._dlg = lambda d: d.accept(); page.on('dialog', page._dlg)
    first = html.index('<script>'); ph = html[:first] + base + ANIM_MOCK + html[first:]
    page.route('http://rb.test/**', lambda r: r.fulfill(status=200, body=ph, content_type='text/html; charset=utf-8'))
    page.goto('http://rb.test/', wait_until='domcontentloaded')
    page.wait_for_function('!document.documentElement.classList.contains("rb-booting")', timeout=15000)
    page.evaluate("navigate('animations')"); page.wait_for_timeout(250)
    page.evaluate("animShowImport()")
    return ctx, page

def stored_payload(page, idx=-1):
    return bytes(page.evaluate("Array.from(window.__anim.items.at(%d).payload)" % idx))

def src_image(path):   # 160 x 16: senkrechte Streifen in den acht Farben, je 4 Pixel breit; Zeile 0 zusätzlich weiß
    im = Image.new('RGB', (160, 16))
    for x in range(160):
        c = RGB[1 + (x // 4) % 7]
        for y in range(16): im.putpixel((x, y), c)
    im.save(path); return im
def color_idx(rgb): return RGB.index(rgb)
def expected_window(im, x0, y0=0, wrap=False):
    g = [[0] * 64 for _ in range(16)]
    for y in range(16):
        for x in range(64):
            sx, sy = x0 + x, y0 + y
            if wrap: sx %= im.width; sy %= im.height
            if 0 <= sx < im.width and 0 <= sy < im.height: g[y][x] = color_idx(im.getpixel((sx, sy)))
    return g

TMP = Path('/tmp/rb_editor_test'); TMP.mkdir(exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])

    # ================= Schwenk mit zwei Rahmen (Handy hochkant) =================
    ctx, page = page_with(browser, 390, 844)
    im = src_image(TMP / 'streifen.png')
    check(page.locator('#animFilePan').count() == 1 and page.locator('label[for=animFilePan]').is_visible(), 'Kachel „Schwenk / Einzelbilder“ sichtbar')
    check(page.locator('#animFileStrip').count() == 0 and page.locator('#animStripOpts').count() == 0, 'Quadratische Sprite-Sheets: Kachel und Eingabe entfernt')
    check(page.locator('#animDrawNew').is_visible(), 'Kachel „Neu zeichnen“ sichtbar')
    tiles = page.evaluate("[...document.querySelectorAll('.anim-src-grid .anim-src')].map(e=>e.textContent.trim())")
    check(tiles == ['GIF importieren', 'Schwenk / Einzelbilder', 'Text-Raster', 'Neu zeichnen'], f'vier Kacheln: {tiles}')
    cols = page.evaluate("getComputedStyle(document.querySelector('.anim-src-grid')).gridTemplateColumns.split(' ').length")
    check(cols == 2, f'Handy: Kacheln 2 × 2 ({cols} Spalten)')
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(400)
    check(page.locator('#animCropBlock').is_hidden() and page.locator('#animFitWrap').is_hidden(), 'Schwenk: Ausschnitt-Rahmen und Voreinstellung ausgeblendet')
    check('160 × 16' in page.locator('#animPanSize').inner_text(), f'Bildgröße angezeigt: {page.locator("#animPanSize").inner_text()}')
    st = page.evaluate("({n:animPan.n,s:animPan.s,e:animPan.e,src:animImp.sources.length,dither:$('animDither').value,lock:animPan.lock})")
    check(st['n'] == 79 and st['e']['x'] == 96 and st['e']['y'] == 0 and st['s']['w'] == 64 and st['e']['w'] == 64 and st['src'] == 79 and st['lock'], f'Vorgabe: Rahmen 64 breit, 79 Frames, Ende 96/0 ({st})')
    check(abs(page.evaluate("parseFloat($('animPanDx').value)") - 96 / 78) < 0.01, 'Versatz aus Frames und Ende angezeigt (1,23)')
    check(st['dither'] == 'majority', 'wenige Farben: Pixelgrafik (Mehrheitsfarbe) voreingestellt')
    page.fill('#animPanN', '5'); page.wait_for_timeout(300)
    st = page.evaluate("({n:animPan.n,pos:[0,1,2,3,4].map(k=>animPanFrame(k).x),src:animImp.sources.length,shown:$('animPanDx').value})")
    check(st['n'] == 5 and st['src'] == 5 and st['shown'] == '24' and st['pos'] == [0, 24, 48, 72, 96], f'5 Frames: Versatz 24 ({st})')
    page.fill('#animPanDx', '10'); page.wait_for_timeout(300)
    st = page.evaluate("({n:animPan.n,ex:animPan.e.x,shown:$('animPanEx').value})")
    check(st['n'] == 5 and st['ex'] == 40 and st['shown'] == '40', f'Versatz 10: Ende 40 ({st})')
    page.fill('#animPanEx', '500'); page.wait_for_timeout(300)
    st = page.evaluate("({ex:animPan.e.x,shown:$('animPanEx').value})")
    check(st['ex'] == 128, f'T06 Rahmen darf über den Rand, die Mitte bleibt im Bild (Ende X 128, Rest schwarz) {st}')
    page.dispatch_event('#animPanEx', 'change')
    check(page.input_value('#animPanEx') == '128', 'Feld zeigt nach dem Verlassen den gültigen Wert')
    page.fill('#animPanEx', '96'); page.wait_for_timeout(500)
    info = page.locator('#animInfo').inner_text()
    check(info.startswith('5 Frames'), f'Info: {info}')
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    want = ref_payload([expected_window(im, x) for x in (0, 24, 48, 72, 96)], 100)
    check(stored_payload(page) == want, 'Schwenk: gespeicherte Nutzlast = unabhängige Referenz (5 Fenster)')
    ctx.close()

    # Frame über den Rand: schwarz außerhalb (Referenz); Zoom mit zwei verschieden großen Rahmen
    ctx, page = page_with(browser, 390, 844)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000)
    page.fill('#animPanN', '3'); page.fill('#animPanSx', '-20'); page.fill('#animPanEx', '0'); page.wait_for_timeout(400)
    st = page.evaluate("({sx:animPan.s.x,pos:[0,1,2].map(k=>animPanFrame(k).x)})")
    check(st['sx'] == -20 and st['pos'] == [-20, -10, 0], f'Start-Rahmen 20 Pixel links über dem Bild ({st})')
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    want = ref_payload([expected_window(im, x) for x in (-20, -10, 0)], 100)
    check(stored_payload(page) == want, 'Rahmen über dem Rand: außerhalb des Bildes schwarz (Referenz)')
    ctx.close()
    ctx, page = page_with(browser, 390, 844)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000)
    page.fill('#animPanSw', '32'); page.wait_for_timeout(300)
    check(page.evaluate("animPan.e.w") == 32 and page.evaluate("animPan.s.w") == 32, 'Größe gleich: Ändern des Start-Rahmens zieht den Ende-Rahmen mit')
    page.uncheck('#animPanLock'); page.fill('#animPanEw', '64'); page.wait_for_timeout(300)
    st = page.evaluate("({s:animPan.s.w,e:animPan.e.w,w:[0,animPan.n-1].map(k=>animPanFrame(k).w),mid:animPanFrame(40).w})")
    check(st['s'] == 32 and st['e'] == 64 and abs(st['w'][0] - 32) < 1e-9 and abs(st['w'][1] - 64) < 1e-9 and 32 < st['mid'] < 64, f'unterschiedlich große Rahmen = Zoom, Breite geometrisch ({st})')
    check('Größenänderung je Frame' in page.locator('#animPanInfo').inner_text() and 'herauszoomen' in page.locator('#animPanInfo').inner_text(), page.locator('#animPanInfo').inner_text())
    page.select_option('#animPanWrap', 'wrap'); page.wait_for_timeout(200)
    check(page.locator('#animPanSeam').is_disabled() and 'gleich groß' in page.locator('#animPanSeamWhy').inner_text(), 'nahtlose Schleife bei ungleichen Rahmen gesperrt, mit Begründung')
    page.check('#animPanLock'); page.wait_for_timeout(200)
    check(page.locator('#animPanSeam').is_enabled(), 'Größe gleich wieder an: Knopf frei')
    ctx.close()

    # Rahmen ziehen mit der Maus (Laptop)
    ctx, page = page_with(browser, 1280, 800, touch=False)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(400)
    page.evaluate("document.getElementById('animPanView').scrollIntoView()")
    def pan_px(ix, iy):
        r = page.evaluate("(()=>{const g=animPan.geoNow,b=document.getElementById('animPanView').getBoundingClientRect();return {x:b.left+(%s-g.x0)*g.k,y:b.top+(%s-g.y0)*g.k}})()" % (ix, iy))
        return r['x'], r['y']
    ex0 = page.evaluate("animPan.e.x")
    x0, y0 = pan_px(ex0 + 32, 8); x1, y1 = pan_px(ex0 + 32 - 40, 8)
    page.mouse.move(x0, y0); page.mouse.down(); page.mouse.move(x1, y1, steps=6); page.mouse.up(); page.wait_for_timeout(400)
    ex1 = page.evaluate("animPan.e.x")
    check(abs((ex0 - ex1) - 40) < 3 and page.evaluate("animPan.act") == 'e', f'Ende-Rahmen mit der Maus verschoben ({ex0} -> {ex1})')
    check(abs(page.evaluate("animPan.s.x")) < 1e-9, 'Start-Rahmen blieb stehen')
    check(abs(page.evaluate("parseFloat($('animPanEx').value)") - ex1) < 0.02, 'Feld „Ende X“ folgt dem Rahmen')
    w0 = page.evaluate("animPan.s.w"); sx, sy = pan_px(page.evaluate("animPan.s.x") + w0, 0 + 16)
    page.mouse.move(sx, sy); page.mouse.down(); page.mouse.move(sx + page.evaluate("animPanGeo().k*20"), sy + 1, steps=5); page.mouse.up(); page.wait_for_timeout(300)
    st = page.evaluate("({s:animPan.s.w,e:animPan.e.w})")
    check(st['s'] > w0 and abs(st['s'] - st['e']) < 1e-9, f'Ecke ziehen ändert die Größe, bei „Größe gleich“ folgt der andere Rahmen ({w0} -> {st})')
    page.mouse.move(pan_px(10, 8)[0], pan_px(10, 8)[1]); wb = page.evaluate("animPan.s.w"); page.mouse.wheel(0, 120); page.wait_for_timeout(200)
    check(page.evaluate("animPan.s.w") > wb or page.evaluate("animPan.e.w") > wb, 'Mausrad ändert die Rahmengröße')
    # Anker und Vorlagen (eingeklappt beim Start, ab 0.8.2)
    check(page.locator('#animAnchBody').is_hidden(), 'Anker und Vorlagen starten eingeklappt'); page.click('#animAnchHead')
    page.locator('#animAnchE button').nth(8).click(); page.wait_for_timeout(200)
    st = page.evaluate("({x:animPan.e.x,y:animPan.e.y,w:animPan.e.w,iw:animPan.iw,ih:animPan.ih})")
    check(abs(st['x'] - (st['iw'] - st['w'])) < 1e-6 and abs(st['y'] - (st['ih'] - st['w'] / 4)) < 1e-6, f'Anker unten rechts setzt den Ende-Rahmen ({st})')
    page.locator('#animPanPresets [data-pre="rl"]').click(); page.wait_for_timeout(200)
    st = page.evaluate("({sx:animPan.s.x,ex:animPan.e.x,w:animPan.s.w})")
    check(st['sx'] > st['ex'] and abs(st['ex']) < 1e-6, f'Vorlage „Rechts → Links“: Start rechts, Ende links ({st})')
    page.locator('#animPanPresets [data-pre="one"]').click(); page.wait_for_timeout(200)
    check(page.evaluate("[animPan.s.w,animPan.e.w]") == [64, 64], 'Vorlage „Rahmen 1:1“')
    page.locator('#animPanPresets [data-pre="all"]').click(); page.wait_for_timeout(200)
    check(page.evaluate("[animPan.n,animPan.e.x]") == [79, 96], 'Vorlage „Ganzes Bild durchlaufen“')
    # Kachelmodus
    page.check('#animPanTile'); page.wait_for_timeout(300)
    st = page.evaluate("({lockDis:$('animPanLock').disabled,wrapDis:$('animPanWrap').disabled,n:animPan.n,w:animPan.s.w,ex:animPan.e.x})")
    check(st['lockDis'] and st['wrapDis'] and st['n'] == 2 and st['ex'] == 64, f'Kachelmodus: Rahmen gleich groß, Schritt = Rahmenbreite, 160/64 = 2 ganze Kacheln ({st})')
    ctx.close()

    # Umlauf
    ctx, page = page_with(browser, 390, 844)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000)
    page.select_option('#animPanWrap', 'wrap'); page.fill('#animPanN', '4'); page.wait_for_timeout(300)
    check(page.locator('#animPanSeam').is_visible(), 'Umlauf: Knopf „nahtlose Schleife“ sichtbar')
    page.locator('#animPanSeam').click(); page.wait_for_timeout(400)
    st = page.evaluate("({pos:[0,1,2,3].map(k=>animPanFrame(k).x)})")
    check(st['pos'] == [0, 40, 80, 120], f'nahtlos: Versatz = 160/4 ({st})')
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    want = ref_payload([expected_window(im, x, 0, True) for x in (0, 40, 80, 120)], 100)
    check(stored_payload(page) == want, 'Umlauf: Nutzlast = Referenz (Fenster läuft über den Bildrand zurück an den Anfang)')
    ctx.close()

    # Hochformat-Bild: senkrechter Schwenk
    ctx, page = page_with(browser, 390, 844)
    tall = Image.new('RGB', (64, 48))
    for y in range(48):
        for x in range(64): tall.putpixel((x, y), RGB[1 + (y // 4) % 7])
    tall.save(TMP / 'hoch.png')
    page.set_input_files('#animFilePan', str(TMP / 'hoch.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(300)
    st = page.evaluate("({ex:animPan.e.x,ey:animPan.e.y,n:animPan.n})")
    check(st['ex'] == 0 and st['ey'] == 32 and st['n'] == 33, f'Hochformat: senkrechter Schwenk (Ende 0/32, 33 Frames) {st}')
    ctx.close()

    # T02 Speichern übernimmt die zuletzt getippte Zeit, auch wenn die Neuberechnung noch aussteht
    ctx, page = page_with(browser, 390, 844)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(400)
    page.fill('#animPanN', '3'); page.wait_for_timeout(300)
    page.evaluate("(()=>{const m=$('animMs');m.value='37';m.dispatchEvent(new Event('input'));$('animSave').click();})()")
    page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    want = ref_payload([expected_window(im, x) for x in (0, 48, 96)], 37)
    check(stored_payload(page) == want, 'T02 Speichern direkt nach Zeitänderung: neue Zeit (37 ms) wird gespeichert, nicht die alte')
    ctx.close()

    # Rückfrage beim Verwerfen
    ctx, page = page_with(browser, 390, 844)
    msgs = []
    page.remove_listener('dialog', page._dlg)
    answer = {'ok': False}
    def on_dialog(d): msgs.append(d.message); (d.accept() if answer['ok'] else d.dismiss())
    page.on('dialog', on_dialog)
    page.locator('#animImpBack').click(); page.wait_for_timeout(300)
    check(not msgs and page.locator('#animListPane').is_visible(), 'nichts geändert: Zurück ohne Rückfrage')
    page.evaluate("animShowImport()"); page.wait_for_timeout(200)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(300)
    page.locator('#animImpBack').click(); page.wait_for_timeout(300)
    check(len(msgs) == 1 and 'nicht gespeichert' in msgs[0] and page.locator('#animImportPane').is_visible(), f'geladenes Bild, nicht gespeichert: Rückfrage, Abbrechen bleibt in der Maske ({msgs})')
    page.evaluate("navigate('settings')"); page.wait_for_timeout(300)
    check(len(msgs) == 2 and page.evaluate("activeView") == 'animations', 'Menü: Seitenwechsel fragt ebenfalls nach und bleibt bei Abbrechen')
    answer['ok'] = True
    page.locator('#animImpBack').click(); page.wait_for_timeout(300)
    check(len(msgs) == 3 and page.locator('#animListPane').is_visible(), 'Verwerfen bestätigt: zurück zur Liste')
    page.evaluate("animShowImport()"); page.wait_for_timeout(200)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(300)
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000); page.wait_for_timeout(300)
    check(len(msgs) == 3 and page.locator('#animListPane').is_visible(), 'Speichern: keine Rückfrage, Liste sichtbar')
    page.evaluate("animUI.selected=window.__anim.items[0].id;animGridSync&&animGridSync()"); page.locator('#animEdit').click(); page.wait_for_selector('#animEditFrames:not(.hidden)', timeout=6000); page.wait_for_timeout(300)
    page.locator('#animImpBack').click(); page.wait_for_timeout(300)
    check(len(msgs) == 3, 'Bearbeiten geöffnet, nichts geändert: keine Rückfrage')
    page.locator('#animEdit').click(); page.wait_for_selector('#animEditFrames:not(.hidden)', timeout=6000); page.wait_for_timeout(300)
    page.fill('#animMs', '77'); answer['ok'] = False
    page.locator('#animSendOnly').click(); page.wait_for_timeout(500)
    page.locator('#animImpBack').click(); page.wait_for_timeout(300)
    check(len(msgs) == 4 and page.locator('#animImportPane').is_visible(), 'Nur senden setzt „geändert“ nicht zurück: Rückfrage bleibt')
    ctx.close()

    # ================= Editor (Handy quer) =================
    ctx, page = page_with(browser, 844, 390)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)', timeout=3000); page.wait_for_timeout(400)
    st = page.evaluate("({blocked:AD.blocked,base:AD.base,n:AD.frames.length,lock:document.documentElement.classList.contains('ad-lock')})")
    check(not st['blocked'] and st['base'] >= 10 and st['n'] == 2 and st['lock'], f'Editor offen, nicht gesperrt ({st})')
    check(page.evaluate("getComputedStyle(document.getElementById('adCanvas')).touchAction") == 'none', 'Zeichenfeld: touch-action none')
    box = page.locator('#adCanvas').bounding_box()
    def cell_xy(cx, cy):
        g = page.evaluate("({ox:AD.ox,oy:AD.oy,c:AD.base*AD.zoom})")
        return box['x'] + g['ox'] + (cx + .5) * g['c'], box['y'] + g['oy'] + (cy + .5) * g['c']
    page.locator('#adColors [data-c="4"]').click()
    x0, y0 = cell_xy(2, 3); x1, y1 = cell_xy(10, 3)
    page.mouse.move(x0, y0); page.mouse.down(); page.mouse.move(x1, y1, steps=6); page.mouse.up()
    row = page.evaluate("Array.from(AD.frames[0].slice(3*64,4*64))")
    check(row[2:11] == [4] * 9 and row[1] == 0 and row[11] == 0, f'Stift zeichnet eine Linie in Rot: {row[:14]}')
    page.locator('[data-tool=eraser]').click(); xe, ye = cell_xy(5, 3)
    page.mouse.click(xe, ye)
    check(page.evaluate("AD.frames[0][3*64+5]") == 0, 'Radierer löscht ein Pixel')
    page.locator('#adUndo').click(); check(page.evaluate("AD.frames[0][3*64+5]") == 4, 'Rückgängig stellt das Pixel wieder her')
    page.locator('#adRedo').click(); check(page.evaluate("AD.frames[0][3*64+5]") == 0, 'Wiederherstellen löscht es erneut')
    page.locator('#adUndo').click()
    # Füllen: Rechteck umranden und füllen
    page.locator('#adColors [data-c="6"]').click(); page.locator('[data-tool=fill]').click(); xf, yf = cell_xy(30, 8); page.mouse.click(xf, yf)
    filled = page.evaluate("AD.frames[0].filter(v=>v===6).length")
    check(filled == 64 * 16 - 9, f'Füllen füllt alles außer der roten Linie ({filled})')
    page.locator('#adUndo').click(); check(page.evaluate("AD.frames[0].filter(v=>v===6).length") == 0, 'Rückgängig nimmt die Füllung zurück')
    # Pipette
    page.locator('[data-tool=pipette]').click(); xp, yp = cell_xy(7, 3); page.mouse.click(xp, yp)
    check(page.evaluate("AD.color") == 4 and page.evaluate("AD.tool") == 'pen', 'Pipette nimmt Rot und wechselt zum Stift')
    # Bildleiste: neues Bild = Kopie, Verschieben, Löschen
    page.locator('#adAdd').click()
    st = page.evaluate("({n:AD.frames.length,cur:AD.cur,same:AD.frames[1].join()===AD.frames[0].join(),thumbs:document.querySelectorAll('#adStrip .ad-th').length})")
    check(st['n'] == 3 and st['cur'] == 1 and st['same'] and st['thumbs'] == 3, f'neues Bild ist eine Kopie des aktuellen ({st})')
    page.locator('[data-tool=eraser]').click(); xe, ye = cell_xy(2, 3); page.mouse.click(xe, ye)
    page.locator('#adLeft').click()
    st = page.evaluate("({cur:AD.cur,a:AD.frames[0][3*64+2],b:AD.frames[1][3*64+2],n:AD.frames.length})")
    check(st['cur'] == 0 and st['a'] == 4 and st['b'] == 0, f'Pfeil links wählt nur das vorige Frame, nichts wird verschoben ({st})')
    check(page.locator('#adCount').inner_text() == 'Bild 1/3', f'Anzeige Bild n/m folgt: {page.locator("#adCount").inner_text()}')
    page.locator('#adRight').click(); check(page.evaluate("AD.cur") == 2 - 1, 'Pfeil rechts: nächstes Frame')
    page.locator('#adMoveMode').click()
    check(page.evaluate("AD.move") is True and page.locator('#adMoveMode').get_attribute('aria-pressed') == 'true' and page.evaluate("getComputedStyle($('adLeft')).backgroundColor") == page.evaluate("getComputedStyle($('adDone')).backgroundColor"), 'Verschieben an: Schalter gedrückt, Pfeile gelb')
    page.locator('#adLeft').click()
    st = page.evaluate("({cur:AD.cur,a:AD.frames[0][3*64+2],b:AD.frames[1][3*64+2]})")
    check(st['cur'] == 0 and st['a'] == 0 and st['b'] == 4, f'im Verschieben-Modus schiebt der Pfeil das Frame nach links ({st})')
    page.locator('#adMoveMode').click(); check(page.evaluate("AD.move") is False, 'Verschieben wieder aus')
    page.locator('#adDel').click(); check(page.evaluate("AD.frames.length") == 2, 'Bild gelöscht')
    check(page.evaluate("AD.frames.length") == 2 and page.locator('#adDel').is_disabled(), 'Mindestens zwei Bilder bleiben (Löschen gesperrt)')
    # Auswahl verschieben
    page.locator('[data-tool=select]').click()
    a = cell_xy(2, 3); b = cell_xy(4, 3)
    page.mouse.move(*a); page.mouse.down(); page.mouse.move(*b, steps=4); page.mouse.up()
    sel = page.evaluate("AD.sel")
    check(sel and sel['w'] == 3 and sel['h'] == 1, f'Auswahl aufgezogen {sel}')
    c0 = cell_xy(3, 3); c1 = cell_xy(3, 8)
    page.mouse.move(*c0); page.mouse.down(); page.mouse.move(*c1, steps=5); page.mouse.up()
    st = page.evaluate("({old:Array.from(AD.frames[AD.cur].slice(3*64+2,3*64+5)),neu:Array.from(AD.frames[AD.cur].slice(8*64+2,8*64+5)),flt:!!AD.flt})")
    check(st['flt'] is False and st['neu'] == [4, 4, 4] and st['old'] == [0, 0, 0], f'Auswahl verschoben ({st})')
    page.locator('#adUndo').click(); check(page.evaluate("AD.frames[AD.cur][8*64+2]") == 0 and page.evaluate("AD.frames[AD.cur][3*64+3]") == 4, 'Rückgängig macht das Verschieben in einem Schritt rückgängig')
    # Spiegeln (ganzes Bild)
    page.locator('[data-tool=pen]').click()
    page.locator('#adMore').click(); page.locator('#adFlipH').click()
    check(page.evaluate("AD.frames[AD.cur][3*64+63-2]") == 4, 'Spiegeln links/rechts')
    page.locator('#adUndo').click()
    # Zwiebelschicht
    if page.locator('#adOnion').is_hidden(): page.locator('#adMore').click()
    page.locator('#adOnion').click()
    check(page.evaluate("AD.onion") is True and page.locator('#adOnion').get_attribute('aria-pressed') == 'true', 'Zwiebelschicht an')
    # Zoom
    z0 = page.evaluate("AD.zoom"); page.locator('#adZoomIn').click(); z1 = page.evaluate("AD.zoom")
    check(z1 > z0 and page.locator('#adZoomTxt').inner_text() == '150 %', f'Zoom +: {z0} -> {z1} {page.locator("#adZoomTxt").inner_text()}')
    zmax = page.evaluate("adZoomMax()"); check(page.evaluate("AD.base*adZoomMax()") <= 60.001, f'Zoomgrenze: Pixel höchstens 60 px groß ({zmax})')
    vv = page.evaluate("window.visualViewport?visualViewport.scale:1"); check(vv == 1, 'Seite selbst nicht gezoomt')
    page.locator('#adZoomOut').click(); check(page.evaluate("AD.zoom") == 1, 'Zoom − zurück auf 100 %')
    # Fertig -> Rückgabe an die Maske und Speichern
    page.locator('#adDone').click(); page.wait_for_timeout(300)
    check(page.locator('#animDraw').is_hidden() and not page.evaluate("document.documentElement.classList.contains('ad-lock')"), 'Editor geschlossen, Seiten-Scroll wieder frei')
    n = page.evaluate("animImp.stored.length"); check(n == 2, f'zwei Bilder übernommen ({n})')
    page.fill('#animName', 'Test Zeichnung'); page.wait_for_timeout(300)
    expect = page.evaluate("animImp.stored.map(f=>Array.from(f))")
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    g = [[[f[y * 64 + x] for x in range(64)] for y in range(16)] for f in expect]
    check(stored_payload(page) == ref_payload(g, 100), 'gezeichnete Animation: Nutzlast = Referenz der Editor-Frames')
    # Bearbeiten der gespeicherten Animation
    page.evaluate("animShowList('editor')"); page.wait_for_timeout(500)
    page.evaluate("animUI.selected=window.__anim.items[0].id;animGridSync&&animGridSync()")
    page.locator('#animEdit').click(); page.wait_for_selector('#animEditFrames:not(.hidden)', timeout=6000)
    page.locator('#animEditFrames').click(); page.wait_for_selector('#animDraw:not(.hidden)', timeout=3000); page.wait_for_timeout(300)
    check(page.evaluate("AD.frames.length") == 2 and page.evaluate("Array.from(AD.frames[0]).join()") == ','.join(map(str, expect[0])), 'gespeicherte Animation im Editor geöffnet (Bilder stimmen)')
    box = page.locator('#adCanvas').bounding_box(); page.locator('#adColors [data-c="2"]').click()
    px, py = cell_xy(40, 12); page.mouse.click(px, py)
    page.locator('#adDone').click(); page.wait_for_timeout(300)
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items[0].payload.length>0&&window.__anim.items.length===1", timeout=8000); page.wait_for_timeout(500)
    after = stored_payload(page, 0)
    exp2 = [[row[:] for row in gg] for gg in g]; exp2[0][12][40] = 2
    check(after == ref_payload(exp2, 100), 'bearbeitete Animation überschreibt die gespeicherte (ein Pixel grün)')
    ctx.close()

    # ================= Zwei-Finger-Zoom nur im Feld =================
    ctx, page = page_with(browser, 844, 390)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    cdp = ctx.new_cdp_session(page); box = page.locator('#adCanvas').bounding_box()
    cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    pts = lambda d: [{'x': cx - d, 'y': cy, 'id': 1}, {'x': cx + d, 'y': cy, 'id': 2}]
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': pts(40)})
    for d in (60, 90, 130, 180): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': pts(d)})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
    page.wait_for_timeout(200)
    st = page.evaluate("({z:AD.zoom,vv:window.visualViewport?visualViewport.scale:1,sx:window.scrollX,sy:window.scrollY,painted:AD.frames[0].some(v=>v)})")
    check(st['z'] > 1.5, f'Zwei-Finger-Pinch zoomt das Zeichenfeld ({st})')
    check(st['vv'] == 1 and st['sy'] == 0, f'Seite wurde nicht gezoomt oder gescrollt ({st})')
    check(not st['painted'], 'Pinch malt keine Pixel')
    # Ein Finger zeichnet
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': cx, 'y': cy, 'id': 1}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': cx + 60, 'y': cy, 'id': 1}]})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); page.wait_for_timeout(100)
    check(page.evaluate("AD.frames[0].some(v=>v)"), 'ein Finger zeichnet')
    ctx.close()

    # ================= Sperren =================
    ctx, page = page_with(browser, 390, 844)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    check(page.evaluate("AD.blocked") is True and page.locator('#adBlock').is_visible() and 'Querformat' in page.locator('#adBlockText').inner_text(), 'Hochformat: Hinweis „ins Querformat drehen“')
    check(page.locator('#adTools').is_hidden() and page.locator('#adBack').is_visible(), 'gesperrt: Werkzeuge weg, Zurück bleibt')
    page.set_viewport_size({'width': 844, 'height': 390}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is False and page.locator('#adTools').is_visible(), 'Drehen hebt die Sperre auf')
    page.set_viewport_size({'width': 380, 'height': 300}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is True and 'zu klein' in page.locator('#adBlockText').inner_text(), 'Querformat, aber zu klein: Hinweis „zu klein“')
    page.set_viewport_size({'width': 844, 'height': 340}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is False, 'Handy im Safari-Tab (844×340): noch benutzbar')
    page.set_viewport_size({'width': 430, 'height': 932}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is True and 'Querformat' in page.locator('#adBlockText').inner_text(), 'breites Handy (430 × 932) hochkant: gesperrt, Hinweis „Querformat“')
    page.set_viewport_size({'width': 820, 'height': 1180}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is False and page.evaluate("AD.base") >= 6 and page.locator('#adTools').is_visible(), 'iPad hochkant (820 × 1180): Editor offen')
    page.set_viewport_size({'width': 844, 'height': 340}); page.wait_for_timeout(500)
    page.locator('#adBack').click(); page.wait_for_timeout(300)
    check(page.locator('#animDraw').is_hidden() and page.locator('#animSourcePick').is_visible(), 'Zurück ohne Änderung: zur Quellenwahl')
    ctx.close()

    # ================= Review-Fälle (T01–T12) =================
    # T01 Auswahl über den Rand: Leeren und Spiegeln treffen nur Pixel auf der Zeichenfläche, nie die Nachbarzeile
    ctx, page = page_with(browser, 844, 390)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    st = page.evaluate("(()=>{AD.frames[0].fill(4);AD.sel={x:60,y:0,w:10,h:2};adClear();const f=AD.frames[0];return {in:[f[60],f[63],f[64+60],f[64+63]],wrap:[f[64],f[65],f[2*64],f[2]]}})()")
    check(st['in'] == [0, 0, 0, 0] and st['wrap'] == [4, 4, 4, 4], f'T01 Leeren mit Auswahl über dem rechten Rand trifft nur sichtbare Pixel ({st})')
    st = page.evaluate("(()=>{const f=AD.frames[0];f.fill(0);for(let x=0;x<64;x++)f[2*64+x]=1+(x%7);AD.sel={x:-5,y:2,w:10,h:1};const before=Array.from(f.slice(1*64,2*64)).join()+'|'+Array.from(f.slice(3*64,4*64)).join();adFlip(true);const g=AD.frames[0];return {sameNeighbours:before===Array.from(g.slice(1*64,2*64)).join()+'|'+Array.from(g.slice(3*64,4*64)).join(),sel:AD.sel}})()")
    check(st['sameNeighbours'], f'T01 Spiegeln mit Auswahl über dem linken Rand lässt die Nachbarzeilen unberührt ({st})')
    st = page.evaluate("(()=>{AD.frames[0].fill(0);AD.sel={x:-3,y:14,w:5,h:5};AD.undo=[];AD.redo=[];adLift();return {flt:AD.flt&&[AD.flt.x,AD.flt.y,AD.flt.w,AD.flt.h],sel:AD.sel}})()")
    check(st['flt'] == [0, 14, 2, 2], f'T01 Anheben schneidet die Auswahl auf die Fläche zu ({st})')
    # T01 (Fortsetzung) Auswahl aus dem Bild geschoben und abgelegt: danach nur noch der sichtbare Teil
    st = page.evaluate("(()=>{adCommitFloat();return {sel:AD.sel}})()")
    check(st['sel'] is None or (st['sel']['x'] >= 0 and st['sel']['y'] >= 0 and st['sel']['x'] + st['sel']['w'] <= 64 and st['sel']['y'] + st['sel']['h'] <= 16), f'T01 Auswahl nach dem Ablegen liegt in der Fläche ({st})')
    # T04 Redo bleibt, wenn ein Strich nichts ändert
    page.locator('[data-tool=pen]').click(); page.locator('#adColors [data-c="4"]').click()
    box = page.locator('#adCanvas').bounding_box()
    def cxy(cx, cy):
        g = page.evaluate("({ox:AD.ox,oy:AD.oy,c:AD.base*AD.zoom})")
        return box['x'] + g['ox'] + (cx + .5) * g['c'], box['y'] + g['oy'] + (cy + .5) * g['c']
    page.evaluate("(()=>{AD.sel=null;AD.frames[0].fill(0);AD.undo=[];AD.redo=[];AD.dirty=false;adUiSync();})()")
    page.mouse.click(*cxy(10, 5)); page.locator('#adUndo').click()
    check(page.evaluate("AD.redo.length") == 1, 'T04 vorbereitet: ein Schritt zum Wiederherstellen')
    page.locator('[data-tool=eraser]').click(); page.mouse.click(*cxy(20, 9))   # leeres Pixel radieren: ändert nichts
    check(page.evaluate("AD.redo.length") == 1 and page.locator('#adRedo').is_enabled(), 'T04 wirkungsloser Strich behält „Wiederherstellen“')
    page.locator('[data-tool=pen]').click(); page.mouse.click(*cxy(11, 5))
    check(page.evaluate("AD.redo.length") == 0, 'T04 echte Änderung leert „Wiederherstellen“')
    # T04 (Fortsetzung) „geändert“ nur bei echter Änderung: Antippen ohne Wirkung, Leeren/Spiegeln leerer Bilder
    page.evaluate("(()=>{AD.frames[0].fill(0);AD.undo=[];AD.redo=[];AD.dirty=false;})()")
    page.locator('[data-tool=eraser]').click(); page.mouse.click(*cxy(3, 3)); page.locator('#adMore').click(); page.locator('#adClear').click(); page.locator('#adFlipH').click()
    check(page.evaluate("AD.dirty") is False and page.evaluate("AD.undo.length") == 0, 'T04 nichts geändert: kein „geändert“, kein Verlauf')
    ctx.close()
    # T03 Fertig ohne Änderung merkt keine Änderung; außerdem Von/Bis/Schritt/Rückwärts/Hin-und-zurück bleiben
    ctx, page = page_with(browser, 844, 390)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    page.locator('#adDone').click(); page.wait_for_timeout(300)
    check(page.evaluate("animImp.dirty") is False, 'T03 Editor ohne Änderung verlassen: Maske bleibt „unverändert“')
    page.evaluate("(()=>{$('animPing').checked=true;$('animRev').checked=true;$('animStep').value='1';$('animFrom').value='2';})()")
    page.locator('#animEditFrames').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    page.locator('#adAdd').click(); page.locator('#adDone').click(); page.wait_for_timeout(300)
    st = page.evaluate("({ping:$('animPing').checked,rev:$('animRev').checked,from:$('animFrom').value,to:$('animTo').value,dirty:animImp.dirty})")
    check(st['ping'] and st['rev'] and st['from'] == '2' and st['to'] == '3' and st['dirty'], f'T03 Hin-und-zurück, Rückwärts und Von bleiben; Bis wächst mit der neuen Frame-Zahl ({st})')
    ctx.close()
    # T08 Werkzeugleiste: schmales Querformat (667 × 375) ohne Überlappung, seltene Werkzeuge unter „Mehr“
    ctx, page = page_with(browser, 667, 375)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(400)
    st = page.evaluate("""(()=>{const bx=e=>{const r=e.getBoundingClientRect();return [r.left,r.right,r.top,r.bottom]};
      const els=[...document.querySelectorAll('#adTools > *, #adColors > *')].filter(e=>e.offsetParent);let over=0;
      for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){const a=bx(els[i]),b=bx(els[j]);if(a[0]<b[1]-0.5&&b[0]<a[1]-0.5&&a[2]<b[3]-0.5&&b[2]<a[3]-0.5)over++;}
      const right=Math.max(...els.map(e=>bx(e)[1]));
      return {compact:AD.compact,over,right,vw:innerWidth,panInMore:!!$('adMorePanel').querySelector('[data-tool=pan]'),zoomInMore:!!$('adMorePanel').querySelector('#adZoomIn')}})()""")
    check(st['compact'] and st['over'] == 0 and st['right'] <= st['vw'] and st['panInMore'] and st['zoomInMore'], f'T08 667 × 375: nichts überlappt, nichts ragt hinaus, Ansicht/Zoom unter „Mehr“ ({st})')
    page.locator('#adMore').click(); page.locator('#adMorePanel [data-tool=pan]').click()
    check(page.evaluate("AD.tool") == 'pan', 'T08 Werkzeug „Ansicht“ aus „Mehr“ wählbar')
    page.set_viewport_size({'width': 1024, 'height': 700}); page.wait_for_timeout(500)
    st = page.evaluate("({large:AD.large,compact:AD.compact,panBack:!!$('adTools').querySelector('[data-tool=pan]'),lbl:getComputedStyle(document.querySelector('#adTools [data-tool=pen]'),'::after').content,h:document.querySelector('#adTools [data-tool=pen]').getBoundingClientRect().height,cw:document.querySelector('#adColors button').getBoundingClientRect().width})")
    check(st['large'] and not st['compact'] and st['panBack'] and 'Stift' in st['lbl'] and st['h'] >= 56 and st['cw'] >= 44, f'T08 iPad/Laptop: große, beschriftete Flächen, Werkzeuge zurück in der Leiste ({st})')
    ctx.close()
    # T08 (Fortsetzung) Sperre nach der echten Zeichenfläche: 700 × 360 reicht, 380 × 300 nicht
    ctx, page = page_with(browser, 700, 360)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(400)
    check(page.evaluate("AD.blocked") is False and page.evaluate("AD.base") >= 6, f'T08 700 × 360 benutzbar ({page.evaluate("AD.base")})')
    page.set_viewport_size({'width': 380, 'height': 300}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is True, 'T08 380 × 300 zu klein')
    page.set_viewport_size({'width': 700, 'height': 360}); page.wait_for_timeout(500)
    check(page.evaluate("AD.blocked") is False, 'T08 zurück auf 700 × 360: Sperre löst sich ohne Flackern')
    ctx.close()
    # T07 große Bilder: Hinweis auf Verkleinerung, Zwischenspeicher frei; T09 spät fertig werdendes Laden wird verworfen
    ctx, page = page_with(browser, 1280, 800, touch=False)
    Image.new('RGB', (5000, 16), (255, 0, 0)).save(TMP / 'sehrbreit.png')
    page.set_input_files('#animFilePan', str(TMP / 'sehrbreit.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=8000); page.wait_for_timeout(400)
    st = page.evaluate("({iw:animPan.iw,ow:animPan.ow,note:$('animSrcInfo').textContent+' '+$('animPanSize').textContent})")
    check(st['iw'] == 4096 and st['ow'] == 5000 and 'verkleinert' in st['note'].lower() and '4096' in st['note'], f'T07 5000 Pixel breit: auf 4096 verkleinert, mit Hinweis ({st})')
    page.evaluate("animShowList('editor')"); page.wait_for_timeout(300)
    check(page.evaluate("animPan.img===null&&animImp.sources.length===0"), 'T12 nach dem Verlassen sind Bild und Fenster freigegeben')
    page.evaluate("animShowImport()")
    Image.new('RGB', (4000, 3000), (0, 255, 0)).save(TMP / 'gross.png')
    page.set_input_files('#animFilePan', str(TMP / 'gross.png')); page.evaluate("animReset()"); page.wait_for_timeout(2500)
    check(page.evaluate("animPan.img===null") and page.locator('#animPanOpts').is_hidden(), 'T09 später fertig werdendes Laden einer verworfenen Datei ändert nichts')
    ctx.close()
    # Zahlenfeld: begrenzter Wert wird beim Verlassen zurückgeschrieben (siehe oben); Gleichheitsfall Start = Ende bleibt benutzbar
    ctx, page = page_with(browser, 844, 390)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000)
    page.click('#animAnchHead'); page.locator('#animPanPresets [data-pre="one"]').click(); page.fill('#animPanN', '2'); page.fill('#animPanEx', '0'); page.wait_for_timeout(300)
    check('alle Frames sehen gleich aus' in page.locator('#animPanInfo').inner_text(), 'Start = Ende: Hinweis „alle Frames sehen gleich aus“')
    ctx.close()

    # T05 Zwei-Finger-Zoom nach Undo lässt „Wiederherstellen“ unberührt
    ctx, page = page_with(browser, 844, 390)
    page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(300)
    box = page.locator('#adCanvas').bounding_box(); page.locator('#adColors [data-c="4"]').click()
    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2); page.locator('#adUndo').click()
    cdp = ctx.new_cdp_session(page); cx, cy = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    pts = lambda d: [{'x': cx - d, 'y': cy, 'id': 1}, {'x': cx + d, 'y': cy, 'id': 2}]
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': pts(40)})
    for d in (60, 90, 130): cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': pts(d)})
    cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); page.wait_for_timeout(200)
    check(page.evaluate("AD.zoom") > 1.3 and page.evaluate("AD.redo.length") == 1 and page.locator('#adRedo').is_enabled(), 'T05 Pinch nach Undo: Zoom wirkt, „Wiederherstellen“ bleibt')
    page.locator('#adRedo').click(); check(page.evaluate("AD.frames[0].some(v=>v===4)"), 'T05 Wiederherstellen bringt den Strich zurück')
    ctx.close()
    # T08 Editor bei 667, 740, 844 und 932 Pixeln Breite
    for w_, h_ in ((667, 375), (740, 360), (844, 390), (932, 430)):
        ctx, page = page_with(browser, w_, h_)
        page.locator('#animDrawNew').click(); page.wait_for_selector('#animDraw:not(.hidden)'); page.wait_for_timeout(400)
        st = page.evaluate("""(()=>{const bx=e=>{const r=e.getBoundingClientRect();return [r.left,r.right,r.top,r.bottom]};
          const els=[...document.querySelectorAll('#adTools > *, #adColors > *, .ad-top > *')].filter(e=>e.offsetParent&&!e.matches('.ad-strip'));let over=0;
          for(let i=0;i<els.length;i++)for(let j=i+1;j<els.length;j++){const a=bx(els[i]),b=bx(els[j]);if(a[0]<b[1]-0.5&&b[0]<a[1]-0.5&&a[2]<b[3]-0.5&&b[2]<a[3]-0.5)over++;}
          return {over,right:Math.max(...els.map(e=>bx(e)[1])),vw:innerWidth,blocked:AD.blocked,compact:AD.compact}})()""")
        check(st['over'] == 0 and st['right'] <= st['vw'] + 0.5 and not st['blocked'], f'T08 {w_} × {h_}: Leiste ohne Überlappung, nichts abgeschnitten ({st})')
        ctx.close()
    # T12 mehrfach große Bilder importieren und wieder verlassen: kein Rest bleibt hängen
    ctx, page = page_with(browser, 1280, 800, touch=False)
    Image.new('RGB', (3000, 2000), (0, 0, 255)).save(TMP / 'gross2.png')
    for i in range(3):
        page.evaluate("animShowImport()"); page.set_input_files('#animFilePan', str(TMP / 'gross2.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=10000); page.wait_for_timeout(300)
        page.evaluate("animImp.dirty=false;animShowList('editor')"); page.wait_for_timeout(200)
    check(page.evaluate("animPan.img===null&&animImp.sources.length===0&&animImp.frames===null"), 'T12 dreimal großes Bild geladen und verlassen: nichts bleibt im Speicher')
    ctx.close()

    # ================= Kleinpaket =================
    ctx, page = page_with(browser, 390, 844)
    page.evaluate("programRunning=true;document.querySelectorAll('input[data-global=\"speed\"],#scrollSpeed').forEach(x=>{x.closest('.pixel-range').classList.toggle('rb-fixed',true)})")
    after = page.evaluate("getComputedStyle(document.querySelector('.rb-dock-speed b'),'::after').content")
    check('fest 80' in after, f'Tempo im Programm: „fest 80“ am Regler ({after})')
    ctx.close()
    b2 = pw.chromium.launch(headless=True, ignore_default_args=['--hide-scrollbars'], args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-features=OverlayScrollbar'])
    ctx = b2.new_context(viewport={'width': 1280, 'height': 700})
    page = ctx.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    first = html.index('<script>'); ph = html[:first] + base + ANIM_MOCK + html[first:]
    page.route('http://rb.test/**', lambda r: r.fulfill(status=200, body=ph, content_type='text/html; charset=utf-8'))
    page.goto('http://rb.test/', wait_until='domcontentloaded'); page.wait_for_function('!document.documentElement.classList.contains("rb-booting")', timeout=15000)
    lefts = {}
    for v, extra in (('programs', None), ('animations', None), ('ambience', None), ('settings', None), ('diagnostics', None), ('editor', "setTab('scroll')")):
        page.evaluate(f"navigate('{v}')"); page.wait_for_timeout(250)
        if extra: page.evaluate(extra); page.wait_for_timeout(150)
        lefts[v] = page.evaluate("(()=>{const e=[...document.querySelectorAll('.app-view')].find(e=>!e.classList.contains('hidden'));const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.width)]})()")
    check(len({tuple(x) for x in lefts.values()}) == 1, f'Laptop: alle Ansichten gleich breit und gleich eingerückt, auch mit klassischem Scrollbalken ({lefts})')
    ctx.close(); b2.close()
    browser.close()

print('FEHLER:' if errors else 'Alle Prüfungen bestanden.', *errors, sep='\n' if errors else ' ')
sys.exit(1 if errors else 0)
