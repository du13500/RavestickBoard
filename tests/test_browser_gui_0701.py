"""v0.6.1.10: Oberflaeche in echtem (headless) Chromium mit simulierter API (nur Web, ohne ESP32).
Prueft: Texteditor (Senden/Speichern bleiben bei leeren Feldern gesperrt, Speichern gelb, keine Hinweistexte, Dialog
„Zeichen gestalten“ ohne Senden und mit kurzem Hinweis, Palettenknopf am Laptop groesser), Symbole (Heissluftballon,
Schneeflocke weiss, Tab „Alle Symbole“, Kategorieleiste: Umbruch am Laptop, weiche Raender am Handy, altes Faecher-Zeichen),
Bibliothek-Vorschau (Tempo-Taste Schnecke/Vogel/Hase statt Regler, auch fuer Blocktexte, Unterkante wie die Liste),
Ambiente am Laptop untereinander, „auf der Tafel“ als Flugzeug (Zeile: links der Pfeile; Kachel/Kurzwahl/Ambiente: Punkt),
weich ein- und ausgeblendete Hinweise.
Aufruf: python tests/test_browser_gui_0701.py [Screenshot-Ordner]
Nicht geprueft: echtes Handy/Safari, ESP32."""
import re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
_src = (ROOT / 'tests/test_browser_ui_0701.py').read_text(encoding='utf8')
_ns = {'__file__': str(ROOT / 'tests/test_browser_ui_0701.py'), 'sys': sys, 're': re, 'json': json, 'Path': Path}
exec(_src[:_src.index('with sync_playwright() as pw:')].replace('SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None', 'SHOTS = None'), _ns)
boot, check, fails, html = _ns['boot'], _ns['check'], _ns['fails'], _ns['html']

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    # ====================================================== Handy
    ctx, page, errs = boot(browser, 390, 844, touch=True)
    page.evaluate("navigate('editor');setTab('scroll')"); page.wait_for_timeout(300)
    page.fill('#scrollText', ''); page.wait_for_timeout(400)
    check(page.locator('#sendScroll').is_disabled() and page.locator('#libSaveAs').is_disabled(), 'Lauftext leer: Senden und Speichern gesperrt')
    page.fill('#scrollText', 'Hi'); page.wait_for_timeout(400)
    check(page.locator('#sendScroll').is_enabled() and page.locator('#libSaveAs').is_enabled(), 'Lauftext mit Text: beide frei')
    page.fill('#scrollText', '   '); page.wait_for_timeout(400)
    check(page.locator('#sendScroll').is_disabled() and page.locator('#libSaveAs').is_disabled(), 'nur Leerzeichen zählt als leer')
    page.fill('#scrollText', 'Hi')
    page.evaluate("document.getElementById('scrollLayout').value='1';document.getElementById('scrollLayout').dispatchEvent(new Event('change'))")
    page.fill('#scrollText', ''); page.fill('#scrollLine2', 'unten'); page.wait_for_timeout(400)
    check(page.locator('#sendScroll').is_enabled(), 'zweizeilig: Text nur in Zeile 2 reicht')
    page.evaluate("document.getElementById('scrollLayout').value='3';document.getElementById('scrollLayout').dispatchEvent(new Event('change'))"); page.wait_for_timeout(400)
    check(page.locator('#sendScroll').is_disabled(), 'einzeilig: Text in der (ausgeblendeten) Zeile 2 zählt nicht')
    # Blocktext
    page.evaluate("setTab('pages')"); page.wait_for_timeout(500)
    page.fill('#line1', ''); page.wait_for_timeout(400)
    gate = page.evaluate("['pageShow','v42SendDraftBand','v42SaveBlock'].map(i=>document.getElementById(i).disabled)")
    check(gate == [True, True, True], f'Blocktext leer: Diese Seite senden, Alle Seiten senden, Speichern gesperrt {gate}')
    page.fill('#line1', 'Seite eins'); page.wait_for_timeout(400)
    gate = page.evaluate("['pageShow','v42SendDraftBand','v42SaveBlock'].map(i=>document.getElementById(i).disabled)")
    check(gate == [False, False, False], f'Blocktext mit Text: alle frei {gate}')
    # Farben: Senden gruen, Speichern wie die anderen Speichern-Knoepfe gelb
    cols = page.evaluate("['pageShow','v42SendDraftBand','libSaveAs','v42SaveBlock'].map(i=>getComputedStyle(document.getElementById(i)).backgroundColor)")
    check(cols[0] == cols[1] == 'rgb(61, 220, 151)', f'Senden bleibt grün {cols}')
    check(page.evaluate("document.getElementById('v42SaveBlock').classList.contains('primary')") and page.evaluate("document.getElementById('libSaveAs').classList.contains('primary')") and cols[3] == 'rgb(255, 212, 92)', f'Speichern im Gelb der anderen Speichern-Knöpfe {cols}')
    # keine Hinweistexte unter Speichern/Senden
    check(page.locator('#libEditorInfo').count() == 0 and page.locator('#v42BlockInfo').count() == 0, 'Hinweiselemente unter Speichern/Senden entfernt')
    body = page.inner_text('body')
    check('Ungespeicherter Entwurf' not in body and 'Du kannst diesen Blocktext aktualisieren' not in body and 'Neuer Blocktext, noch nicht' not in body, 'Hinweistexte stehen nicht mehr in der Seite')
    check("libEditorInfo" not in html.replace('libraryEditorIndicator', '') and 'v42BlockInfo' not in html, 'Quelltext ohne die Hinweis-Elemente')
    # Dialog „Zeichen gestalten“
    page.evaluate("setTab('scroll')"); page.fill('#scrollText', 'Hallo'); page.wait_for_timeout(300)
    page.locator('#rbzOpen').click(); page.wait_for_function('!document.getElementById("rbz").classList.contains("hidden")')
    check(page.locator('#rbzSend').count() == 0 and page.locator('#rbzDone').is_visible(), 'Dialog: kein Senden-Knopf, „Fertig“ bleibt')
    page.locator('#rbzMatrix .rbz-cell, #rbzMatrix button, #rbzMatrix span').first.click() if page.locator('#rbzMatrix .rbz-cell, #rbzMatrix button, #rbzMatrix span').count() else None
    check(page.evaluate("RBZ_COLOR_NOTE") == 'Färbt Buchstaben und färbbare Symbole.', 'Dialog: kurzer Farbhinweis')
    page.locator('#rbzDone').click()
    # Symbole
    info = page.evaluate("(()=>{const a=RB_SYM_INFO.get(59),b=RB_SYM_INFO.get(37);return {a:[a.name,a.cat],b:b.name,fan:RB_SYM_BY_CP.get(0x1FAAD),ball:RB_SYM_BY_CP.get(0x1F388),names:SYMBOL_TABLE.map(e=>e[2])}})()")
    check(info['a'] == ['Heißluftballon', 'Fahrzeuge & Weltall'] and info['b'] == 'Schneeflocke weiß' and 'Fächer' not in info['names'], f'Symbolnamen: {info["a"]} {info["b"]}')
    check(info['fan'] == 59 and info['ball'] == 59, 'altes Fächer-Zeichen wird weiter als Heißluftballon gezeichnet, neues Zeichen = Ballon')
    page.evaluate("rbSymTab='';rbSymOpen();document.getElementById('symbolOverlay').classList.remove('hidden')"); page.wait_for_timeout(500)
    tabs = page.evaluate("[...document.querySelectorAll('#symTabs .chip')].map(c=>c.dataset.tab)")
    check(tabs[:3] == ['__recent', '__all', 'Liebe'], f'Tab „Alle Symbole“ zwischen „Zuletzt benutzt“ und „Liebe“: {tabs[:4]}')
    page.locator('#symTabs .chip[data-tab="__all"]').click(); page.wait_for_timeout(200)
    n_all = page.evaluate("document.querySelectorAll('#symbolCategories .symbol-grid button').length")
    check(n_all == page.evaluate("SYMBOL_TABLE.length") and n_all >= 75, f'„Alle Symbole“ zeigt jedes Symbol: {n_all}')
    fade = page.evaluate("(()=>{const r=document.getElementById('symTabs');return {ov:r.scrollWidth>r.clientWidth,r:r.classList.contains('fade-r'),l:r.classList.contains('fade-l'),mask:getComputedStyle(r).maskImage||getComputedStyle(r).webkitMaskImage}})()")
    check(fade['ov'] and fade['r'] and not fade['l'] and 'gradient' in fade['mask'], f'Handy: Leiste scrollt, rechts weich ausgeblendet: {fade}')
    page.evaluate("document.getElementById('symTabs').scrollLeft=120"); page.wait_for_timeout(200)
    fade = page.evaluate("(()=>{const r=document.getElementById('symTabs');return [r.classList.contains('fade-l'),r.classList.contains('fade-r')]})()")
    check(fade[0] and fade[1], f'Handy: nach dem Scrollen beidseitig weich: {fade}')
    page.evaluate("document.getElementById('symTabs').scrollLeft=9999"); page.wait_for_timeout(200)
    fade = page.evaluate("(()=>{const r=document.getElementById('symTabs');return [r.classList.contains('fade-l'),r.classList.contains('fade-r')]})()")
    check(fade[0] and not fade[1], f'Handy: am Ende nur links weich: {fade}')
    check(not errs, f'keine Skriptfehler (Handy): {errs[:3]}'); ctx.close()

    # ====================================================== Laptop
    ctx, page, errs = boot(browser, 1440, 900)
    page.evaluate("navigate('editor');setTab('scroll')"); page.wait_for_timeout(300)
    sv = page.evaluate("(()=>{const b=document.getElementById('rbzOpen'),s=b.querySelector('svg').getBoundingClientRect();return [Math.round(b.getBoundingClientRect().width),Math.round(s.width)]})()")
    check(sv[1] >= 24 and sv[1] / sv[0] > 0.6, f'Palettenknopf am Laptop: Symbol groß genug {sv}')
    page.evaluate("rbSymTab='';rbSymOpen();document.getElementById('symbolOverlay').classList.remove('hidden')"); page.wait_for_timeout(500)
    wr = page.evaluate("(()=>{const r=document.getElementById('symTabs'),cs=getComputedStyle(r);return {wrap:cs.flexWrap,ov:r.scrollWidth<=r.clientWidth+1,rows:new Set([...r.children].map(c=>c.offsetTop)).size,mask:cs.maskImage||cs.webkitMaskImage}})()")
    check(wr['wrap'] == 'wrap' and wr['ov'] and wr['rows'] >= 2 and 'gradient' not in (wr['mask'] or ''), f'Laptop: Kategorien umbrechen statt abgeschnitten zu werden: {wr}')
    if SHOTS: page.screenshot(path=str(SHOTS / 'g01_laptop_symbole.png'))
    page.evaluate("document.getElementById('symbolOverlay').classList.add('hidden')")
    # Bibliothek-Vorschau
    page.evaluate("window.__mock.entries.push({id:60,name:'Block A',kind:'block',mode:0,text:'',line2:'',layout:5,color1:3,color2:0,pages:2});window.__mock.entries.push({id:61,name:'Standbild',kind:'text',mode:1,text:'Still',line2:'',layout:0,color1:3,color2:0})")
    page.evaluate("navigate('library');refreshLibrary()"); page.wait_for_timeout(500)
    check(page.locator('#libPrevTempo').count() == 0 and page.locator('#libPrevSpeed').count() == 1, 'Vorschau: Tempo-Regler weg, Tempo-Taste da')
    page.evaluate("librarySelected=2;libraryNoAuto=false;renderLibrary();libPrevUpdate()"); page.wait_for_timeout(500)
    check(page.locator('#libPrevSpeed').is_visible(), 'Lauftext: Tempo-Taste sichtbar')
    seq = []
    for _ in range(4):
        seq.append(page.evaluate("[document.getElementById('libPrevSpeed').dataset.rbIcon,libPrev.rate]")); page.locator('#libPrevSpeed').click(); page.wait_for_timeout(120)
    check(seq == [['snail', 1], ['bird', 2], ['rabbit', 4], ['snail', 1]], f'Tempo-Taste: Schnecke → Vogel → Hase → Schnecke {seq}')
    check(page.evaluate("[...document.querySelectorAll('#libPrevSpeed svg')].length") == 1, 'Tempo-Taste hat genau ein Symbol')
    check(page.evaluate("document.getElementById('scrollSpeed').value") == page.evaluate("document.querySelector('#rbDock input[data-global=speed]').value"), 'die Taste ändert nicht das Tafeltempo (Regler im Dock unverändert)')
    page.evaluate("librarySelected=60;renderLibrary();libPrevUpdate()"); page.wait_for_timeout(600)
    check(page.locator('#libPrevSpeed').is_visible() and page.evaluate("libPrev.rec&&libPrev.rec.kind") == 'block', 'Blocktext: Tempo-Taste sichtbar')
    page.evaluate("librarySelected=61;renderLibrary();libPrevUpdate()"); page.wait_for_timeout(600)
    check(page.locator('#libPrevSpeed').is_hidden(), 'Standbild: keine Tempo-Taste')
    bt = page.evaluate("(()=>{const l=document.querySelector('#view-library>div').getBoundingClientRect(),p=document.getElementById('libPreview').getBoundingClientRect();return [Math.round(l.bottom),Math.round(p.bottom)]})()")
    check(abs(bt[0] - bt[1]) <= 1, f'Vorschau-Kasten hat dieselbe Unterkante wie die Liste links {bt}')
    # „auf der Tafel“ in der Zeile: Flugzeug links von den Pfeilen
    page.evaluate("librarySelected=1;renderLibrary();rbOn={kind:1,id:1};rbOnApply()"); page.wait_for_timeout(300)
    row = page.evaluate("""(()=>{const r=document.querySelector('#libList .library-row[data-id="1"]'),k=[...r.children].map(e=>e.className.split(' ')[0]||e.tagName),b=r.querySelector(':scope>.rb-on-badge');
      return {kids:k,svg:!!(b&&b.querySelector('svg')),bg:b?getComputedStyle(b).backgroundColor:'',txt:b?b.textContent.trim():'x',on:r.classList.contains('on-board'),vis:b?getComputedStyle(b).display:''}})()""")
    check(row['on'] and row['svg'] and row['txt'] == '' and row['kids'][1] == 'rb-on-badge' and row['vis'] != 'none' and row['bg'] == 'rgba(0, 0, 0, 0)', f'Bibliothek-Zeile: Flugzeug (ohne Pille) direkt links der Pfeile: {row}')
    if SHOTS: page.screenshot(path=str(SHOTS / 'g02_laptop_bibliothek.png'))
    page.evaluate("rbOn={kind:0,id:0};rbOnApply()")
    # Ambiente untereinander
    page.evaluate("navigate('ambience')"); page.wait_for_timeout(300)
    am = page.evaluate("(()=>{const b=[...document.querySelectorAll('#ambienceColors button')].map(e=>e.getBoundingClientRect());return {n:b.length,lefts:new Set(b.map(r=>Math.round(r.left))).size,tops:b.map(r=>Math.round(r.top)),h:Math.round(b[0].height)}})()")
    check(am['n'] == 7 and am['lefts'] == 1 and am['tops'] == sorted(am['tops']) and len(set(am['tops'])) == 7 and am['h'] <= 64, f'Ambiente am Laptop: sieben Farben untereinander in der kleinen Höhe {am}')
    page.evaluate("rbOn={kind:3,id:Number(document.querySelector('#ambienceColors button').dataset.onId)};rbOnApply()")
    dot = page.evaluate("(()=>{const b=document.querySelector('#ambienceColors button.on-board>.rb-on-badge');if(!b)return null;const r=b.getBoundingClientRect(),p=b.parentElement.getBoundingClientRect();return {svg:!!b.querySelector('svg'),top:Math.round(r.top-p.top),right:Math.round(p.right-r.right),w:Math.round(r.width)}})()")
    check(dot and dot['svg'] and dot['top'] <= 10 and dot['right'] <= 12 and dot['w'] == 22, f'Ambiente: Punkt mit Flugzeug oben rechts {dot}')
    page.evaluate("rbOn={kind:0,id:0};rbOnApply()")
    # Kurzwahl: Punkt oben rechts
    page.evaluate("navigate('home');v42Shortcuts=Array.from({length:8},()=>({type:0,id:0,label:''}));v42Shortcuts[0]={type:1,id:1,label:'Text 1'};libShortcutsDraw();rbOn={kind:1,id:1};rbOnApply()"); page.wait_for_timeout(300)
    sk = page.evaluate("(()=>{const t=document.querySelector('.shortcut.on-board');const b=t&&t.querySelector(':scope>.rb-on-badge');if(!b)return null;const r=b.getBoundingClientRect(),p=t.getBoundingClientRect();return {svg:!!b.querySelector('svg'),top:Math.round(r.top-p.top),right:Math.round(p.right-r.right),txt:b.textContent.trim()}})()")
    check(sk and sk['svg'] and sk['txt'] == '' and sk['top'] <= 8 and sk['right'] <= 8, f'Kurzwahl: Punkt mit Flugzeug oben rechts {sk}')
    page.evaluate("rbOn={kind:0,id:0};rbOnApply()")
    # Hinweise weich ein-/ausblenden
    page.evaluate("notify('Probe')"); page.wait_for_timeout(500)
    t1 = page.evaluate("(()=>{const s=document.getElementById('status'),c=getComputedStyle(s);return [s.hidden,c.opacity,c.visibility,c.transitionProperty.includes('opacity'),c.transitionDuration]})()")
    check(t1[0] is False and t1[1] == '1' and t1[2] == 'visible' and t1[3], f'Hinweis wird eingeblendet (Übergang auf Deckkraft) {t1}')
    page.evaluate("document.getElementById('status').hidden=true"); page.wait_for_timeout(60)
    mid = float(page.evaluate("getComputedStyle(document.getElementById('status')).opacity"))
    check(0 < mid < 1, f'Hinweis blendet weich aus (nicht abrupt): Deckkraft nach 60 ms = {mid}')
    page.wait_for_timeout(500)
    t2 = page.evaluate("(()=>{const c=getComputedStyle(document.getElementById('status'));return [c.opacity,c.visibility,c.pointerEvents]})()")
    check(t2 == ['0', 'hidden', 'none'], f'nach dem Ausblenden unsichtbar und ohne Klickfläche {t2}')
    page.evaluate("window.poll=async()=>{}")   # der Status-Abruf würde die Sperre im Test sofort wieder lösen
    page.evaluate("rbTxSet(true)"); page.wait_for_timeout(100)
    mid = float(page.evaluate("getComputedStyle(document.querySelector('.rb-tx-pill')).opacity"))
    check(0 < mid < 1, f'Übertragungs-Pille blendet weich ein: Deckkraft nach 100 ms = {mid}')
    mid = float(page.evaluate("(async()=>{rbTxSet(true);await new Promise(r=>setTimeout(r,600));rbTxSet(false);await new Promise(r=>setTimeout(r,100));return getComputedStyle(document.querySelector('.rb-tx-pill')).opacity})()"))
    check(0 < mid < 1, f'Übertragungs-Pille blendet weich aus: Deckkraft nach 100 ms = {mid}')
    check(not errs, f'keine Skriptfehler (Laptop): {errs[:3]}'); ctx.close()
    browser.close()
print('FAILS:', len(fails))
if not fails: print('PASS Browser 0.6.1.10 (Oberfläche): Texteditor leer gesperrt, Speichern gelb, ohne Hinweistexte, Dialog schlank, Symbole (Heißluftballon, Schneeflocke weiß, Alle Symbole, Kategorieleiste), Bibliothek-Vorschau mit Tempo-Taste, Ambiente untereinander, „auf der Tafel“ als Flugzeug, weiche Hinweise.')
sys.exit(1 if fails else 0)
