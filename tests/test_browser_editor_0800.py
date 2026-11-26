"""Schwenk über großes Bild und Frame-Editor im echten (headless) Chromium mit simulierter API.
Schwenk: Fenster-Positionen, Versatz-Rechnung (Frames/Ende/Versatz), Stoppen/Umlauf, Nutzlast gegen unabhängige Referenz.
Editor: Zeichnen (Stift, Radierer, Füllen, Pipette, Auswahl), Rückgängig/Wiederherstellen, Bildleiste, Zwiebelschicht, Zoom,
Gesten nur im Zeichenfeld, Sperre im Hochformat und bei zu kleinem Feld, Bearbeiten gespeicherter Animationen.
Kleinpaket: Tempo-Hinweis im Programm, gleiche Breite bei klassischem Scrollbalken, Backup-Knöpfe behalten ihre Farbe.
Aufruf: python tests/test_browser_editor_0800.py
Nicht geprüft: iPad/iPhone-Safari, echter Apple Pencil, echte Zwei-Finger-Gesten auf Hardware."""
import io, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
_p = ROOT / 'tests/test_browser_anim_0800.py'
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
    page.on('dialog', lambda d: d.accept())
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

    # ================= Schwenk (Handy hochkant) =================
    ctx, page = page_with(browser, 390, 844)
    im = src_image(TMP / 'streifen.png')
    check(page.locator('#animFilePan').count() == 1 and page.locator('label[for=animFilePan]').is_visible(), 'Kachel „Schwenk über großes Bild“ sichtbar')
    check(page.locator('#animDrawNew').is_visible(), 'Kachel „Neu zeichnen“ sichtbar')
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(400)
    check(page.locator('#animCropBlock').is_hidden() and page.locator('#animFitWrap').is_hidden(), 'Schwenk: Ausschnitt-Rahmen und Voreinstellung ausgeblendet')
    check(page.locator('#animPanSize').inner_text().startswith('160 × 16'), f'Bildgröße angezeigt: {page.locator("#animPanSize").inner_text()}')
    st = page.evaluate("({n:animPan.n,ex:animPan.ex,ey:animPan.ey,dx:animPan.dx,wrap:animPan.wrap,src:animImp.sources.length,dither:$('animDither').value})")
    check(st['n'] == 79 and st['ex'] == 96 and st['ey'] == 0 and st['src'] == 79, f'Vorgabe: 79 Frames, Ende 96/0 ({st})')
    check(abs(st['dx'] - 96 / 78) < 1e-9, f'Versatz aus Frames und Ende: {st["dx"]}')
    check(st['dither'] == 'thresh', 'wenige Farben: Schwelle voreingestellt')
    # Frames ändern -> Ende bleibt, Versatz wird angepasst und angezeigt
    page.fill('#animPanN', '5'); page.wait_for_timeout(300)
    st = page.evaluate("({n:animPan.n,dx:animPan.dx,ex:animPan.ex,pos:[0,1,2,3,4].map(k=>animPanPos(k)),src:animImp.sources.length,shown:$('animPanDx').value})")
    check(st['n'] == 5 and st['dx'] == 24 and st['ex'] == 96 and st['src'] == 5 and st['shown'] == '24', f'5 Frames: Versatz 24 ({st})')
    check([p[0] for p in st['pos']] == [0, 24, 48, 72, 96], f'Positionen {st["pos"]}')
    # Versatz ändern -> Ende wandert, Frames bleiben
    page.fill('#animPanDx', '10'); page.wait_for_timeout(300)
    st = page.evaluate("({n:animPan.n,ex:animPan.ex,shown:$('animPanEx').value})")
    check(st['n'] == 5 and st['ex'] == 40 and st['shown'] == '40', f'Versatz 10: Ende 40 ({st})')
    # Ende ändern -> Versatz wird gerechnet; Stoppen begrenzt auf das Bildende
    page.fill('#animPanEx', '500'); page.wait_for_timeout(300)
    st = page.evaluate("({ex:animPan.ex,dx:animPan.dx})")
    check(st['ex'] == 96 and st['dx'] == 24, f'Ende wird im Stopp-Modus auf das Bildende begrenzt ({st})')
    # Nutzlast: 5 Frames, Fenster bei 0/24/48/72/96, Schwelle, 100 ms
    page.fill('#animPanEx', '96'); page.wait_for_timeout(500)
    info = page.locator('#animInfo').inner_text()
    check(info.startswith('5 Frames'), f'Info: {info}')
    page.locator('#animSave').click(); page.wait_for_function("window.__anim.items.length===1", timeout=8000)
    want = ref_payload([expected_window(im, x) for x in (0, 24, 48, 72, 96)], 100)
    check(stored_payload(page) == want, 'Schwenk: gespeicherte Nutzlast = unabhängige Referenz (5 Fenster)')
    ctx.close()

    # Umlauf
    ctx, page = page_with(browser, 390, 844)
    page.set_input_files('#animFilePan', str(TMP / 'streifen.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000)
    page.select_option('#animPanWrap', 'wrap'); page.fill('#animPanN', '4'); page.wait_for_timeout(300)
    check(page.locator('#animPanSeam').is_visible(), 'Umlauf: Knopf „nahtlose Schleife“ sichtbar')
    page.locator('#animPanSeam').click(); page.wait_for_timeout(400)
    st = page.evaluate("({dx:animPan.dx,pos:[0,1,2,3].map(k=>animPanPos(k))})")
    check(st['dx'] == 40 and [p[0] for p in st['pos']] == [0, 40, 80, 120], f'nahtlos: Versatz = 160/4 ({st})')
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
    st = page.evaluate("({ex:animPan.ex,ey:animPan.ey,n:animPan.n})")
    check(st['ex'] == 0 and st['ey'] == 32 and st['n'] == 33, f'Hochformat: senkrechter Schwenk (Ende 0/32, 33 Frames) {st}')
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
    st = page.evaluate("({cur:AD.cur,a:AD.frames[0][3*64+2],b:AD.frames[1][3*64+2]})")
    check(st['cur'] == 0 and st['a'] == 0 and st['b'] == 4, f'Bild nach links geschoben ({st})')
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
