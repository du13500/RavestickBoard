"""v0.8.3: Import-Maske und Editor im echten (headless) Chromium mit simulierter API.
Prueft: sichtbarer 1:1-Knopf mit immer sichtbarer Groessenzeile (Schwenk und GIF), Umschalter "Rahmen bewegen / Bahn bewegen" mit
ziehbarem Bahnpunkt (Bahn gerade, Kachelmodus sperrt), allgemeines Rueckgaengig/Wiederherstellen der Import-Maske (Knoepfe, Tastatur,
Verlauf leeren bei neuer Quelle), Zeichen-Editor mit "Duplizieren" und echtem "Neu", Linie/Rechteck/Kreis (Pixelform, Ziehen, ein
Rueckgaengig-Schritt) und die sieben Mischfarben im Ambiente (nur senden, temporaere Animation mit 1 ms).
Aufruf: python tests/test_browser_import_0803.py
Nicht geprueft: echtes iPhone-Safari, Hardware."""
import sys, re, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
_src = (ROOT / 'tests/test_browser_editor_0803.py').read_text(encoding='utf8')
_ns = {'__file__': str(ROOT / 'tests/test_browser_editor_0803.py'), '__name__': 'ed_base', 'sys': sys, 're': re, 'json': json, 'Path': Path}
exec(_src[:_src.index('TMP = Path(')], _ns)
page_with, errors = _ns['page_with'], _ns['errors']
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import random
fails = []
def check(c, msg):
    if not c: fails.append(msg); print('FAIL', msg)
random.seed(5)
PAL = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255), (255, 255, 255)]
TMP = Path('/tmp/rb_import_0803'); TMP.mkdir(exist_ok=True)
ph = Image.new('RGB', (300, 200))
for x in range(300):
    for y in range(200): ph.putpixel((x, y), (x * 255 // 300, y * 255 // 200, (x + y) % 256))
ph.save(TMP / 'photo.png')
nat = Image.new('RGB', (96, 96), (0, 0, 0)); d = ImageDraw.Draw(nat)
for _ in range(60):
    x, y = random.randrange(96), random.randrange(96); d.rectangle([x, y, x + random.randrange(2, 12), y + random.randrange(2, 9)], fill=random.choice(PAL))
nat.resize((192, 192), Image.NEAREST).save(TMP / 'art2x.png')
f1 = nat.crop((0, 0, 64, 16)).resize((128, 32), Image.NEAREST); f2 = nat.crop((10, 10, 74, 26)).resize((128, 32), Image.NEAREST)
f1.save(TMP / 'art.gif', save_all=True, append_images=[f2], duration=200, loop=0)

with sync_playwright() as pw:
    br = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx, page = page_with(br, 1100, 1000, touch=False)

    # ================= Schwenk: 1:1, Bahn, Rueckgaengig =================
    page.set_input_files('#animFilePan', str(TMP / 'photo.png')); page.wait_for_selector('#animPanOpts:not(.hidden)', timeout=5000); page.wait_for_timeout(600)
    check(page.locator('#animOneBtn').is_visible() and page.locator('#animOneBtn').inner_text().strip() == '1:1', '1:1-Knopf sichtbar')
    t = page.locator('#animOneInfo').inner_text()
    check('Rahmen 300 × 75 Bildpixel' in t and '1:1 wären 64 × 16' in t, f'Groessenzeile bei Foto, Rahmen nicht 1:1: {t!r}')
    page.click('#animOneBtn'); page.wait_for_timeout(400)
    check(page.evaluate("animPan.s.w===64&&animPan.e.w===64"), 'Knopf 1:1 stellt beide Rahmen auf 64 Bildpixel')
    t = page.locator('#animOneInfo').inner_text()
    check(t == 'Rahmen 64 × 16 Bildpixel = 1:1', f'Zeile zeigt "= 1:1" auch bei Faktor 1: {t!r}')
    # Rahmen unterschiedlich gross machen, Zeile nennt beide
    page.evaluate("animPan.lock=false;animPan.s={x:10,y:10,w:64};animPan.e={x:0,y:0,w:256};animPanSync();"); page.wait_for_timeout(400)
    t = page.locator('#animOneInfo').inner_text()
    check('Start 64 × 16' in t and 'Ende 256 × 64' in t, f'Zeile nennt Start und Ende: {t!r}')
    # Bahn: gerade zuerst, Mitte liegt auf der Verbindungslinie
    mid = page.evaluate("animPanCenter(.5)"); sm = page.evaluate("animPanStraightMid()")
    check(abs(mid[0] - sm[0]) < 1e-9 and abs(mid[1] - sm[1]) < 1e-9, 'ohne Biegung liegt die Mitte auf der Geraden')
    check(page.locator('#animPanModeFrame').get_attribute('aria-pressed') == 'true' and page.locator('#animPanBendReset').is_disabled(), 'Start: Rahmen bewegen, Bahn-Reset gesperrt')
    page.click('#animPanModeBend'); page.wait_for_timeout(100)
    check(page.evaluate("animPan.bendOn") and page.locator('#animPanModeBend').get_attribute('aria-pressed') == 'true', 'Bahn bewegen eingeschaltet')
    # Ziehen auf dem Bild setzt den Bahnpunkt
    box = page.locator('#animPanView').bounding_box(); g = page.evaluate("animPanGeo()")
    tx, ty = 60.0, 120.0   # Bildkoordinaten
    px = box['x'] + (tx - g['x0']) / g['vw'] * box['width']; py = box['y'] + (ty - g['y0']) / g['vh'] * box['height']
    page.mouse.move(box['x'] + 5, box['y'] + 5); page.mouse.down(); page.mouse.move(px, py, steps=6); page.mouse.up(); page.wait_for_timeout(400)
    mid = page.evaluate("animPanCenter(.5)")
    check(abs(mid[0] - tx) < 2.5 and abs(mid[1] - ty) < 2.5, f'Bahnpunkt folgt dem Zeiger: {mid}')
    sw = page.evaluate("({s:{...animPan.s},e:{...animPan.e}})")
    check(sw['s'] == {'x': 10, 'y': 10, 'w': 64} and sw['e'] == {'x': 0, 'y': 0, 'w': 256}, f'Im Bahn-Modus bleiben die Rahmen unveraendert {sw}')
    st = page.evaluate("({b:animPanBent(),dis:$('animPanBendReset').disabled,info:$('animPanInfo').textContent.includes('gebogen'),f1:animPanFrame(1).x})")
    check(st['b'] and not st['dis'] and st['info'], f'Bahn gebogen, Reset aktiv, Info nennt es {st}')
    # die Frames laufen jetzt wirklich auf der Kurve: Mitte von Frame k ist animPanCenter
    n = page.evaluate("animPan.n"); k = n // 2; fr = page.evaluate("[animPanFrame(%d),animPanCenter(%d/(animPan.n-1))]" % (k, k))
    check(abs(fr[0]['x'] + fr[0]['w'] / 2 - fr[1][0]) < 1e-6 and abs(fr[0]['y'] + fr[0]['w'] / 8 - fr[1][1]) < 1e-6, 'Frame-Mitte liegt auf der gebogenen Bahn')
    # Rueckgaengig: Biegung weg, wieder her
    check(page.evaluate("AH.h.length>=2&&!$('animImpUndo').disabled"), 'Rueckgaengig-Knopf aktiv nach der Biegung')
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(not page.evaluate("animPanBent()"), 'Rueckgaengig nimmt die Biegung zurueck')
    check(not page.locator('#animImpRedo').is_disabled(), 'Wiederherstellen aktiv')
    page.click('#animImpRedo'); page.wait_for_timeout(300)
    check(page.evaluate("animPanBent()"), 'Wiederherstellen bringt die Biegung zurueck')
    # Tastatur
    page.evaluate("document.activeElement&&document.activeElement.blur()")
    page.keyboard.press('Control+z'); page.wait_for_timeout(300)
    check(not page.evaluate("animPanBent()"), 'Strg+Z macht rueckgaengig')
    page.keyboard.press('Control+Shift+Z'); page.wait_for_timeout(300)
    check(page.evaluate("animPanBent()"), 'Strg+Umschalt+Z stellt wieder her')
    # Bahn wieder gerade (ein eigener Schritt)
    page.click('#animPanBendReset'); page.wait_for_timeout(300)
    check(not page.evaluate("animPanBent()") and page.locator('#animPanBendReset').is_disabled(), 'Bahn wieder gerade')
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(page.evaluate("animPanBent()"), 'Rueckgaengig stellt die Biegung nach "gerade" wieder her')
    # Zahlenfeld (change) ist ein Schritt: Anzahl Frames
    page.fill('#animPanN', '9'); page.press('#animPanN', 'Tab'); page.wait_for_timeout(300)
    check(page.evaluate("animPan.n")==9, 'Frames auf 9')
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(page.evaluate("animPan.n")!=9, 'Rueckgaengig: Frameanzahl zurueck')
    # Kachelmodus sperrt die Bahn
    page.click('#animPanModeFrame'); page.check('#animPanTile'); page.wait_for_timeout(300)
    check(page.locator('#animPanModeBend').is_disabled() and not page.evaluate("animPanBent()"), 'Kachelmodus: Bahn gesperrt und gerade')
    page.uncheck('#animPanTile'); page.wait_for_timeout(200)
    # Voreinstellung setzt die Biegung zurueck
    page.evaluate("animPan.bend={x:30,y:10};animPanSync()"); page.click('#animAnchHead'); page.click('#animPanPresets button[data-pre=lr]'); page.wait_for_timeout(300)
    check(not page.evaluate("animPanBent()"), 'Vorlage "Links -> Rechts" setzt die Bahn gerade')
    # Neue Quelle leert den Verlauf
    page.set_input_files('#animFilePan', str(TMP / 'art2x.png')); page.wait_for_timeout(800)
    check(page.evaluate("AH.h.length")==1 and page.locator('#animImpUndo').is_disabled(), 'Neue Quelle: Verlauf geleert, Rueckgaengig gesperrt')
    st = page.evaluate("({sw:animPan.s.w,k:$('animKind').value})")
    check(st['sw'] == 128 and st['k'] == 'pixel', f'Pixelgrafik 2x: Rahmen 128 {st}')
    check(page.locator('#animOneInfo').inner_text() == 'Rahmen 128 × 32 Bildpixel = 1:1', f'Zeile: {page.locator("#animOneInfo").inner_text()!r}')
    page.evaluate("animPanSetW('s',300);animPanSetW('e',300);animPanSync()"); page.wait_for_timeout(300)
    check('1:1 wären 128 × 32' in page.locator('#animOneInfo').inner_text(), 'Zeile nennt die 1:1-Groesse, wenn der Rahmen abweicht')
    page.click('#animOneBtn'); page.wait_for_timeout(300)
    check(page.evaluate("animPan.s.w===128&&animPan.e.w===128"), 'Knopf 1:1 stellt den erkannten Faktor (128) ein')

    # ================= GIF: 1:1 und Rueckgaengig fuer den Ausschnitt =================
    page.set_input_files('#animFileGif', str(TMP / 'art.gif')); page.wait_for_timeout(900)
    check(page.locator('#animOneInfo').inner_text() == 'Rahmen 128 × 32 Bildpixel = 1:1', f'GIF: Zeile {page.locator("#animOneInfo").inner_text()!r}')
    page.evaluate("animCropSet({cx:.5,cy:.5,w:.5})"); page.wait_for_timeout(300); page.evaluate("animHistCommit()")
    check(page.evaluate("animImp.crop.w")<0.6 and 'wären 128 × 32' in page.locator('#animOneInfo').inner_text(), 'GIF: Ausschnitt veraendert, Zeile nennt 1:1')
    page.click('#animOneBtn'); page.wait_for_timeout(300)
    check(abs(page.evaluate("animImp.crop.w")-1)<1e-9 and page.locator('#animOneInfo').inner_text()=='Rahmen 128 × 32 Bildpixel = 1:1', 'GIF: Knopf 1:1 setzt den Ausschnitt')
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(abs(page.evaluate("animImp.crop.w")-0.5)<1e-9, 'GIF: Rueckgaengig stellt den Ausschnitt wieder her')
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(abs(page.evaluate("animImp.crop.w")-1)<1e-9, 'GIF: zweites Rueckgaengig bis zum Anfang')
    check(page.locator('#animImpUndo').is_disabled(), 'Rueckgaengig am Anfang des Verlaufs gesperrt')
    # Bildart ist Teil des Verlaufs
    page.select_option('#animKind', 'photo'); page.wait_for_timeout(300); page.evaluate("animHistCommit()")
    page.click('#animImpUndo'); page.wait_for_timeout(300)
    check(page.evaluate("$('animDither').value")=='majority', 'Rueckgaengig stellt die Bildart zurueck')

    # ================= Zeichen-Editor =================
    page.evaluate("animShowImport()"); page.click('#animDrawNew'); page.wait_for_timeout(500)
    check(page.locator('#adNew').is_visible() and page.locator('#adAdd').is_visible(), 'Neu und Duplizieren sichtbar')
    check(page.locator('#adAdd').get_attribute('title') == 'Aktuelles Bild duplizieren' and page.locator('#adNew').get_attribute('title').startswith('Neues leeres Bild'), 'Beschriftungen')
    page.evaluate("AD.frames[AD.cur][5]=4;AD.frames[AD.cur][70]=2;adRebuildStrip();adDraw()")
    n0 = page.evaluate("AD.frames.length")
    page.click('#adAdd'); page.wait_for_timeout(150)
    r = page.evaluate("({n:AD.frames.length,cur:AD.cur,same:AD.frames[AD.cur][5]===4&&AD.frames[AD.cur][70]===2})")
    check(r['n'] == n0 + 1 and r['same'], f'Duplizieren kopiert das aktuelle Bild {r}')
    page.click('#adNew'); page.wait_for_timeout(150)
    r = page.evaluate("({n:AD.frames.length,cur:AD.cur,empty:AD.frames[AD.cur].every(v=>v===0),prev:AD.frames[AD.cur-1][5]})")
    check(r['n'] == n0 + 2 and r['empty'] and r['prev'] == 4, f'Neu legt ein leeres Bild hinter dem aktuellen an {r}')
    page.click('#adUndo'); page.wait_for_timeout(100)
    check(page.evaluate("AD.frames.length")==n0 + 1, 'Rueckgaengig nimmt das neue Bild zurueck')
    # Formpixel (reine Funktion)
    cnt = page.evaluate("""()=>{
      const run=(kind,ax,ay,bx,by,fill)=>{const f=new Uint8Array(1024);AD.frames[AD.cur]=f;adShapePx(kind,ax,ay,bx,by,3,fill);return [...f].map((v,i)=>v?[i%64,(i/64)|0]:null).filter(Boolean);};
      const sym=(pts,x0,y0,x1,y1)=>{const S=new Set(pts.map(p=>p.join(',')));return pts.every(([x,y])=>S.has((x0+x1-x)+','+y)&&S.has(x+','+(y0+y1-y)));};
      const rO=run('rect',2,2,5,4,false),rF=run('rect',2,2,5,4,true),ln=run('line',0,0,5,0,false),ln2=run('line',5,3,0,0,false);
      const eO=run('ellipse',10,2,18,8,false),eF=run('ellipse',10,2,18,8,true),c1=run('ellipse',3,3,3,3,false),eR=run('ellipse',0,0,15,0,false);
      return {rO:rO.length,rF:rF.length,ln:ln.length,ln2:ln2.length,eOsym:sym(eO,10,2,18,8),eFsym:sym(eF,10,2,18,8),eOn:eO.length,eFn:eF.length,hollow:!eO.some(p=>p[0]===14&&p[1]===5),c1:c1.length,eR:eR.length,
        ext:[Math.min(...eO.map(p=>p[0])),Math.max(...eO.map(p=>p[0])),Math.min(...eO.map(p=>p[1])),Math.max(...eO.map(p=>p[1]))]};}""")
    check(cnt['rO'] == 10 and cnt['rF'] == 12, f'Rechteck 4x3: Rand 10, gefuellt 12 ({cnt})')
    check(cnt['ln'] == 6 and cnt['ln2'] == 6, f'Linie waagerecht 6 Pixel, schraeg 6 Pixel ({cnt})')
    check(cnt['eOsym'] and cnt['eFsym'] and cnt['hollow'] and cnt['eFn'] > cnt['eOn'] > 12, f'Kreis/Ellipse symmetrisch, innen hohl, gefuellt groesser ({cnt})')
    check(cnt['ext'] == [10, 18, 2, 8], f'Ellipse fuellt das aufgezogene Feld ganz aus {cnt["ext"]}')
    check(cnt['c1'] == 1 and cnt['eR'] == 16, f'Entartete Faelle: Punkt 1, flache Ellipse 16 ({cnt})')
    # Ziehen mit der Maus: Rechteck ueber "Mehr"
    page.evaluate("AD.frames[AD.cur]=new Uint8Array(1024);AD.undo=[];AD.redo=[];adDraw();adUiSync()")
    page.click('#adMore'); page.wait_for_timeout(100)
    check(page.locator('[data-tool=rect]').is_visible() and page.locator('[data-tool=line]').is_visible() and page.locator('[data-tool=ellipse]').is_visible(), 'Formwerkzeuge unter "Mehr" sichtbar')
    page.click('[data-tool=rect]'); page.wait_for_timeout(100)
    check(page.evaluate("AD.tool")=='rect' and page.locator('#adMore').evaluate("e=>e.classList.contains('on')"), 'Rechteck gewaehlt, "Mehr" zeigt aktives Werkzeug')
    def cell_xy(cx, cy):
        r = page.locator('#adCanvas').bounding_box(); c = page.evaluate("adCellSize()"); o = page.evaluate("[AD.ox,AD.oy]")
        return r['x'] + o[0] + (cx + .5) * c, r['y'] + o[1] + (cy + .5) * c
    x0, y0 = cell_xy(3, 3); x1, y1 = cell_xy(9, 6)
    page.mouse.move(x0, y0); page.mouse.down(); page.mouse.move(x1, y1, steps=8)
    mid_state = page.evaluate("[AD.frames[AD.cur][3*64+3],AD.frames[AD.cur][6*64+9],AD.frames[AD.cur][4*64+5]]")
    page.mouse.up(); page.wait_for_timeout(150)
    col = page.evaluate("AD.color"); fin = page.evaluate("[AD.frames[AD.cur][3*64+3],AD.frames[AD.cur][6*64+9],AD.frames[AD.cur][4*64+5],AD.undo.length]")
    check(mid_state[0] == col and mid_state[1] == col and mid_state[2] == 0, f'Vorschau beim Ziehen zeigt das Rechteck {mid_state}')
    check(fin[0] == col and fin[1] == col and fin[2] == 0 and fin[3] == 1, f'Rechteck bleibt, innen leer, genau ein Rueckgaengig-Schritt {fin}')
    page.click('#adUndo'); page.wait_for_timeout(100)
    check(page.evaluate("AD.frames[AD.cur].every(v=>v===0)"), 'Ein Rueckgaengig entfernt das ganze Rechteck')
    # Gefuellt, Kreis
    page.click('#adMore'); page.click('#adShapeFill'); page.click('[data-tool=ellipse]'); page.wait_for_timeout(100)
    check(page.evaluate("AD.fill&&AD.tool")=='ellipse', 'Fuellung an, Kreis gewaehlt')
    x0, y0 = cell_xy(20, 2); x1, y1 = cell_xy(28, 8)
    page.mouse.move(x0, y0); page.mouse.down(); page.mouse.move(x1, y1, steps=8); page.mouse.up(); page.wait_for_timeout(150)
    ok = page.evaluate("[AD.frames[AD.cur][5*64+24],AD.frames[AD.cur][2*64+20],AD.undo.length]")
    check(ok[0] == page.evaluate("AD.color") and ok[1] == 0 and ok[2] == 1, f'Gefuellter Kreis: Mitte gesetzt, Ecke des Feldes leer {ok}')
    # Linie, Zug zurueck zum Start ohne Wirkung -> kein Schritt
    page.click('#adMore'); page.click('[data-tool=line]'); page.wait_for_timeout(100)
    un = page.evaluate("AD.undo.length"); x0, y0 = cell_xy(40, 5)
    page.mouse.move(x0, y0); page.mouse.down(); page.mouse.up(); page.wait_for_timeout(100)
    check(page.evaluate("AD.frames[AD.cur][5*64+40]")==page.evaluate("AD.color"), 'Antippen mit der Linie setzt einen Punkt')
    check(page.evaluate("AD.undo.length")==un+1, 'Punkt ist ein Rueckgaengig-Schritt')
    page.evaluate("AD.dirty=false"); page.click('#adBack'); page.wait_for_timeout(200)

    # ================= Ambiente: Mischfarben =================
    page.evaluate("navigate('ambience')"); page.wait_for_timeout(300)
    names = page.evaluate("[...document.querySelectorAll('#ambienceColors button')].map(b=>b.textContent.trim())")
    check(names == ['Rot', 'Gelb', 'Grün', 'Cyan', 'Blau', 'Magenta', 'Weiß', 'Orange', 'Rot-Orange', 'Limette', 'Himmelblau', 'Hellblau', 'Hellrosa', 'Mint'], f'Ambiente: sieben Farben und sieben Mischfarben {names}')
    page.evaluate("window.__mock.requests.length=0")
    page.click('#ambienceColors button:has-text("Rot-Orange")'); page.wait_for_timeout(600)
    rq = page.evaluate("window.__mock.requests.map(r=>({p:r.path,d:r.data}))")
    puts = [r for r in rq if r['p'] == '/api/anim/put']; snd = [r for r in rq if r['p'] == '/api/anim/send']
    check(len(puts) == 1 and puts[0]['d'].get('temp') == '1' and puts[0]['d'].get('frames') == '3' and puts[0]['d'].get('ms') == '1', f'Rot-Orange: temporaere Animation, 3 Bilder, 1 ms {puts[:1]}')
    check(len(snd) == 1 and snd[0]['d'].get('temp') == '1', f'Rot-Orange: danach senden {snd}')
    pay = page.evaluate("Array.from(window.__anim.lastTemp?window.__anim.lastTemp.payload:[])") if page.evaluate("!!window.__anim.lastTemp") else None
    if pay:
        fr = page.evaluate("RbAnim.unpackPayload(window.__anim.lastTemp.payload).frames.map(f=>[...new Set(f)])")
        check(fr == [[4], [4], [6]], f'Rot-Orange besteht aus Rot, Rot, Gelb {fr}')
    page.evaluate("window.__mock.requests.length=0")
    page.click('#ambienceColors button:has-text("Mint")'); page.wait_for_timeout(600)
    rq = page.evaluate("window.__mock.requests.map(r=>({p:r.path,d:r.data}))")
    check(any(r['p'] == '/api/anim/put' and r['d'].get('frames') == '2' for r in rq), 'Mint: zwei Bilder')
    page.evaluate("window.__mock.requests.length=0")
    page.click('#ambienceColors button:has-text("Weiß")'); page.wait_for_timeout(400)
    rq = page.evaluate("window.__mock.requests.map(r=>r.path)")
    check('/api/ambience' in rq and '/api/anim/put' not in rq, f'Volle Farben gehen unveraendert ueber /api/ambience {rq}')
    ctx.close(); br.close()
real = [e for e in errors if 'favicon' not in e]
check(not real, f'Seitenfehler: {real[:3]}')
print('FAILS:', len(fails))
sys.exit(1 if fails else 0)
