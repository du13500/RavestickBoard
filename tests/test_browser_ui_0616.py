"""v0.6.1.5/0.6.1.6: Neue Bedienung in der Weboberflaeche, in echtem (headless) Chromium mit simulierter API.
Prueft: Mehrfachauswahl zum Loeschen in Bibliothek und Programmen (Strg/Umschalt-Klick, Strg+A, Esc, Entf; nur Loeschen aktiv;
eine Rueckfrage; Fehlerbericht), Wiederholung lesender Anfragen bei 503 "Speicher knapp" (nicht bei schreibenden), Meldung
bei fehlgeschlagenem Sendeauftrag, sichtbar gesperrter Tempo-Regler, Seitenleiste und breite Darstellung ab 1000 px,
Menue unter der Banane, Bedienfeld so breit wie der Inhalt.
0.6.1.6: Sperre waehrend einer Uebertragung (Status busy, 409 busy, keine schreibenden Anfragen, Hinweis auf dem Bedienfeld
ohne es zu vergroessern), Schrift mit Wiederholung, Rahmen (fensterhoch, Bedienfeld unten buendig und so breit wie die
Flaechen) auf iPhone SE, Handy und Laptop, Ambiente-Farben, lange Namen, Namen aus Dateinamen, beschaedigte Programme im
Kurzwahl-Dialog, Blocktext-Kopf.
Aufruf: python tests/test_browser_ui_0616.py [Screenshot-Ordner]"""
import re, sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
html = (ROOT / 'web/index.html').read_text(encoding='utf8')
src = (ROOT / 'tests/test_browser_0616.py').read_text(encoding='utf8')
MOCK = src[src.index("MOCK=r'''") + 9:src.index("</script>'''") + 9]
ino = next((ROOT / 'firmware').glob('RavestickBoard_v0_6_1_6/*.ino')).read_text(encoding='utf8')
blk = ino[ino.index('static const Glyph FONT[] = {'):]; blk = blk[:blk.index('};')]
font = {}
for m in re.finditer(r"\{\s*(?:'(\\?.)'|(0x[0-9A-Fa-f]+|\d+))\s*,\s*\{([^}]*)\}\s*\}", blk):
    ch, num, rows = m.groups(); font[ord(ch[-1]) if ch else int(num, 0)] = [int(x) for x in rows.split(',')]
MOCK = MOCK.replace('%FONT%', json.dumps(font))
# Zusatz zur Attrappe: Loeschen wirkt wirklich, einzelne Pfade koennen 503/500/409 liefern.
EXTRA = r'''<script>
(function(){
 const base=window.fetch;
 if(window.__preRules)window.__mock.rules=window.__preRules;   // 0.6.1.6: Regeln schon beim Laden (Schrift)
 window.fetch=async function(path,opt={}){
  const full=String(path),p=full.split('?')[0],m=window.__mock,arg=new URLSearchParams(opt.body||'');
  const reply=(obj,status)=>{const snap=JSON.stringify(obj);return {ok:status<400,status,json:async()=>JSON.parse(snap),text:async()=>snap};};
  const rule=(m.rules||[]).find(r=>r.path===p&&r.n>0&&(!r.id||String(r.id)===arg.get('id')));
  if(rule){rule.n--;m.requests.push({path:p,method:opt.method||'GET',data:Object.fromEntries(arg.entries()),failed:rule.status});
   return reply(rule.body||{ok:false,message:rule.message||'Speicher knapp, bitte gleich noch einmal versuchen.'},rule.status);}
  if(p==='/api/library/delete'){m.requests.push({path:p,method:'POST',data:Object.fromEntries(arg.entries())});m.entries=m.entries.filter(e=>e.id!==Number(arg.get('id')));return reply({ok:true,message:'ok'},200);}
  if(p==='/api/collections/delete'){m.requests.push({path:p,method:'POST',data:Object.fromEntries(arg.entries())});m.programs=(m.programs||[]).filter(e=>e.id!==Number(arg.get('id')));return reply({ok:true,message:'ok'},200);}
  return base(path,opt);
 };
})();
</script>'''
page_html = html.replace('<script>', MOCK + EXTRA + '<script>', 1)
fails = []
def check(ok, label):
    if not ok: fails.append(label); print('FAIL', label)
SEED = """()=>{const m=window.__mock;m.entries=[];for(let i=1;i<=6;i++)m.entries.push({id:i,name:'Text '+i,text:'T'+i,line2:'',layout:0,color1:3,color2:0,mode:i%2,kind:'text'});m.nextId=7;
 m.programs=[1,2,3,4].map(i=>({id:i,name:'Programm '+i,count:2,playback:0,ids:[i,i+1]}));m.rules=[];}"""
def boot(pw_browser, w, h, touch=False, pre=None):
    ctx = pw_browser.new_context(viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    page = ctx.new_page(); errs = []
    if pre: page.add_init_script('window.__preRules=' + json.dumps(pre))
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
    page.route('http://rb.test/**', lambda r: r.fulfill(status=200, body=page_html, content_type='text/html; charset=utf-8'))
    page.goto('http://rb.test/', wait_until='domcontentloaded')
    page.wait_for_function('!document.documentElement.classList.contains("rb-booting")', timeout=15000)
    page.evaluate(SEED + '' if not pre else SEED.replace('m.rules=[];','')); page.evaluate("async()=>{await refreshLibrary();await v42RefreshPrograms();}")
    return ctx, page, errs
def reqs(page, path): return [r for r in page.evaluate('__mock.requests') if r['path'] == path]
def toast(page): return page.evaluate("document.getElementById('status').hidden?'':document.getElementById('status').textContent")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    # ============================================================ Laptop 1440 x 900
    ctx, page, errs = boot(browser, 1440, 900)
    # ---- Seitenleiste und Breite
    g = page.evaluate("""()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)]};
      return {menu:r(document.getElementById('mainMenu')),menuShown:getComputedStyle(document.getElementById('mainMenu')).display,main:r(document.getElementById('appShell')),
       dock:r(document.getElementById('rbDock')),header:r(document.querySelector('.app-header')),banana:getComputedStyle(document.getElementById('bananaMenu')).pointerEvents,
       cols:getComputedStyle(document.getElementById('shortcutGrid')).gridTemplateColumns.split(' ').length,over:document.documentElement.scrollWidth>window.innerWidth,
       tiles:[...document.querySelectorAll('.shortcut')].map(e=>Math.round(e.getBoundingClientRect().top))}}""")
    check(g['menuShown'] == 'flex' and g['menu'][0] == 0 and g['menu'][2] == 232 and g['menu'][3] == 900, f'Seitenleiste fest links, volle Hoehe: {g["menu"]} {g["menuShown"]}')
    check(g['header'][0] == 0 and g['header'][2] == 232 and g['banana'] == 'none', f'Kopf mit Logo und Version sitzt in der Seitenleiste, Banane ohne Funktion: {g["header"]} {g["banana"]}')
    check(g['main'][0] >= 256 and g['main'][2] == 1120, f'Kurzwahl nutzt 1120 px rechts der Seitenleiste: {g["main"]}')
    check(g['cols'] == 4 and len(set(g['tiles'])) == 2, f'Kurzwahl: vier Kacheln je Zeile, zwei Zeilen: {g["cols"]} {sorted(set(g["tiles"]))}')
    check(g['dock'][0] == g['main'][0] and g['dock'][2] == g['main'][2], f'Bedienfeld so breit wie der Inhalt: {g["dock"]} / {g["main"]}')
    check(not g['over'], 'kein seitliches Ueberlaufen bei 1440 px')
    if SHOTS: page.screenshot(path=str(SHOTS / 'u01_laptop_kurzwahl.png'))
    page.locator('#mainMenu [data-nav="library"]').click(); page.wait_for_timeout(200)
    g2 = page.evaluate("""()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.width)]};return {view:document.body.dataset.rbView,menu:getComputedStyle(document.getElementById('mainMenu')).display,
      main:r(document.getElementById('appShell')),dock:r(document.getElementById('rbDock')),cur:document.querySelector('#mainMenu [data-nav].current').dataset.nav}}""")
    check(g2['view'] == 'library' and g2['menu'] == 'flex' and g2['cur'] == 'library', f'Klick in der Seitenleiste wechselt die Ansicht, Leiste bleibt: {g2}')
    check(g2['main'][1] == 860 and g2['dock'] == g2['main'], f'Bibliothek 860 px breit, Bedienfeld gleich: {g2}')
    for v in ['programs', 'animations', 'editor', 'ambience', 'settings', 'diagnostics']:
        page.evaluate(f"navigate('{v}')"); page.wait_for_timeout(120)
        check(page.evaluate("document.documentElement.scrollWidth<=window.innerWidth"), f'Ansicht {v}: kein seitliches Ueberlaufen')
    surf = page.evaluate("""()=>{navigate('library');const c=s=>getComputedStyle(document.querySelector(s)).backgroundColor;return [c('#view-library .panel'),c('#rbDock')]}""")
    check(surf[0] == surf[1] == 'rgb(29, 34, 46)', f'Karte und Bedienfeld haben dieselbe Flaechenfarbe: {surf}')

    # ---- Mehrfachauswahl Bibliothek
    page.evaluate("navigate('library')"); page.wait_for_timeout(150)
    picks = page.locator('#libList .lib-pick')
    def lib_state():
        return page.evaluate("""()=>({multi:[...rbMulti.lib].sort((a,b)=>a-b),single:librarySelected,bar:document.getElementById('libMultiBar').hidden?'':document.getElementById('libMultiBar').textContent,
          dis:Object.fromEntries(['libOpen','libSend','libDuplicate','libRename','libDelete'].map(i=>[i,document.getElementById(i).disabled])),
          rows:[...document.querySelectorAll('#libList .library-row.multi')].map(r=>Number(r.dataset.id)),arrows:[...document.querySelectorAll('#libList .library-row button:not(.lib-pick)')].every(b=>b.disabled)})""")
    page.evaluate("librarySelected=0;libraryNoAuto=true;renderLibrary()")
    picks.nth(0).click(); s = lib_state()
    check(s['multi'] == [] and s['single'] == 1 and not any(s['dis'].values()) and s['bar'] == '', f'Einzelklick wie bisher: {s}')
    picks.nth(2).click(modifiers=['Control']); s = lib_state()
    check(s['multi'] == [1, 3] and s['single'] == 0 and s['rows'] == [1, 3], f'Strg-Klick nimmt dazu, die Einzelauswahl gehoert dazu: {s}')
    check(s['dis'] == {'libOpen': True, 'libSend': True, 'libDuplicate': True, 'libRename': True, 'libDelete': False} and s['arrows'], f'ab zwei markierten Eintraegen ist nur Loeschen bedienbar, Pfeile gesperrt: {s["dis"]}')
    check('2 Einträge ausgewählt' in s['bar'], f'Hinweiszeile nennt die Anzahl: {s["bar"]}')
    if SHOTS: page.screenshot(path=str(SHOTS / 'u02_bibliothek_mehrfach.png'))
    picks.nth(4).click(modifiers=['Shift']); s = lib_state()
    check(s['multi'] == [3, 4, 5], f'Umschalt-Klick waehlt den Bereich ab dem zuletzt angeklickten Eintrag: {s["multi"]}')
    picks.nth(0).click(modifiers=['Control', 'Shift']); s = lib_state()
    check(s['multi'] == [1, 2, 3, 4, 5], f'Strg+Umschalt erweitert um den Bereich: {s["multi"]}')
    for i in (0, 1, 3, 4): picks.nth(i).click(modifiers=['Control'])
    s = lib_state()
    check(s['multi'] == [] and s['single'] == 3 and not any(s['dis'].values()) and s['bar'] == '', f'bleibt ein Eintrag uebrig, gilt wieder die Einzelauswahl: {s}')
    page.keyboard.press('Control+a'); s = lib_state()
    check(s['multi'] == [1, 2, 3, 4, 5, 6] and '6 Einträge' in s['bar'], f'Strg+A waehlt alle: {s["multi"]}')
    page.keyboard.press('Escape'); s = lib_state()
    check(s['multi'] == [] and s['single'] == 0 and s['dis']['libDelete'], f'Esc hebt die Auswahl auf: {s}')
    picks.nth(1).click(); picks.nth(3).click(modifiers=['Control']); picks.nth(5).click(); s = lib_state()
    check(s['multi'] == [] and s['single'] == 6, f'Klick ohne Taste beendet die Mehrfachauswahl: {s}')
    page.locator('#libMultiBar').evaluate("e=>e.hidden") or check(False, 'Hinweiszeile muss ohne Mehrfachauswahl verborgen sein')
    # Schaltflaeche "Auswahl aufheben"
    picks.nth(0).click(); picks.nth(1).click(modifiers=['Shift']); page.locator('#libMultiBar button').click(); s = lib_state()
    check(s['multi'] == [] and s['bar'] == '', 'Schaltflaeche „Auswahl aufheben“ wirkt')
    # Eingabefelder: Strg+A im Textfeld gehoert dem Feld
    page.evaluate("navigate('editor')"); page.fill('#scrollText', 'abc'); page.focus('#scrollText'); page.keyboard.press('Control+a'); page.evaluate("navigate('library')")
    check(lib_state()['multi'] == [], 'Strg+A in einem Textfeld markiert keine Listeneintraege')
    # Loeschen: eine Rueckfrage mit Anzahl, Namen, Abhaengigkeiten; Abbrechen laesst alles stehen
    page.evaluate("v42Shortcuts=[{type:1,id:2,label:'x'},{type:0,id:0,label:''},{type:1,id:5,label:'y'},{type:0,id:0,label:''},{type:0,id:0,label:''},{type:0,id:0,label:''},{type:0,id:0,label:''},{type:0,id:0,label:''}]")
    page.evaluate("window.__confirms=[];window.confirm=m=>{window.__confirms.push(m);return false};0")
    picks.nth(1).click(); picks.nth(2).click(modifiers=['Control']); picks.nth(4).click(modifiers=['Control'])
    page.locator('#libDelete').click(); page.wait_for_timeout(150)
    c = page.evaluate('__confirms'); 
    check(len(c) == 1 and c[0].startswith('3 Bibliothekseinträge wirklich löschen?') and all(f'• Text {i}' in c[0] for i in (2, 3, 5)), f'eine Rueckfrage mit Anzahl und Namen: {c}')
    check('Programme: Programm 1, Programm 2, Programm 3, Programm 4' in c[0] and 'Kurzwahlen: 1, 3' in c[0] and 'nicht rückgängig' in c[0], f'Rueckfrage nennt Programme und Kurzwahlen: {c}')
    check(len(reqs(page, '/api/library/delete')) == 0 and lib_state()['multi'] == [2, 3, 5], 'Abbrechen: nichts geloescht, Auswahl bleibt')
    page.keyboard.press('Delete'); page.wait_for_timeout(150)
    check(len(page.evaluate('__confirms')) == 2 and len(reqs(page, '/api/library/delete')) == 0, 'Entf loest dieselbe Rueckfrage aus')
    page.evaluate("window.confirm=m=>{window.__confirms.push(m);return true};0")
    page.locator('#libDelete').click(); page.wait_for_function("document.querySelectorAll('#libList .library-row').length===3", timeout=8000)
    d = [r['data']['id'] for r in reqs(page, '/api/library/delete')]
    check(d == ['2', '3', '5'] and page.evaluate("libraryItems.map(x=>x.id)") == [1, 4, 6], f'drei Eintraege nacheinander geloescht: {d}')
    check(toast(page) == '3 Bibliothekseinträge gelöscht.' and lib_state()['multi'] == [] and lib_state()['single'] == 0, f'Meldung und leere Auswahl danach: {toast(page)!r}')
    # Fehler bei einem Eintrag: Bericht, die uebrigen sind geloescht
    page.evaluate("window.__mock.rules=[{path:'/api/library/delete',id:4,n:1,status:500,message:'Schreibfehler'}]")
    page.keyboard.press('Control+a'); page.keyboard.press('Delete'); page.wait_for_function("document.querySelectorAll('#libList .library-row').length===1", timeout=8000)
    check(toast(page).startswith('2 von 3 gelöscht. Fehler bei: Text 4 (Schreibfehler)'), f'Fehlerbericht nennt den Eintrag: {toast(page)!r}')
    check(page.evaluate("document.getElementById('status').classList.contains('toast-error')"), 'Fehlerbericht als Fehlermeldung dargestellt')
    # beschaeftigt (409): Abbruch nach dem ersten Fehlschlag
    page.evaluate(SEED); page.evaluate("async()=>{await refreshLibrary()}")
    n0 = len(reqs(page, '/api/library/delete'))
    page.evaluate("window.__mock.rules=[{path:'/api/library/delete',n:99,status:409,message:'Der Controller ist beschaeftigt.'}]")
    page.keyboard.press('Control+a'); page.keyboard.press('Delete'); page.wait_for_function("document.getElementById('status').textContent.includes('von 6')", timeout=8000)
    check(len(reqs(page, '/api/library/delete')) == n0 + 1 and toast(page).startswith('0 von 6 gelöscht.'), f'bei „beschaeftigt“ wird nach dem ersten Versuch abgebrochen: {toast(page)!r}')
    page.evaluate("window.__mock.rules=[]")

    # ---- Mehrfachauswahl Programme
    page.evaluate("navigate('programs')"); page.wait_for_timeout(200)
    pp = page.locator('#v42Programs .lib-pick')
    def prog_state():
        return page.evaluate("""()=>({multi:[...rbMulti.prog].sort((a,b)=>a-b),single:v42ProgramId,bar:document.getElementById('progMultiBar').hidden?'':document.getElementById('progMultiBar').textContent,
          dis:Object.fromEntries(['v42NewProgram','v43ProgEdit','v42RunProgram','v42DeleteProgram'].map(i=>[i,document.getElementById(i).disabled]))})""")
    pp.nth(0).click(); page.wait_for_function("v42ProgramId===1"); pp.nth(2).click(modifiers=['Shift']); page.wait_for_timeout(150); s = prog_state()
    check(s['multi'] == [1, 2, 3] and s['single'] == 0 and '3 Programme ausgewählt' in s['bar'], f'Programme: Bereich mit Umschalt-Klick: {s}')
    check(s['dis'] == {'v42NewProgram': True, 'v43ProgEdit': True, 'v42RunProgram': True, 'v42DeleteProgram': False}, f'Programme: nur Loeschen bedienbar: {s["dis"]}')
    page.evaluate("window.__confirms=[];v42Shortcuts[1]={type:2,id:2,label:'P'};0")
    page.locator('#v42DeleteProgram').click(); page.wait_for_function("document.querySelectorAll('#v42Programs .library-row').length===1", timeout=8000)
    c = page.evaluate('__confirms')
    check(len(c) == 1 and c[0].startswith('3 Programme wirklich löschen?') and 'Zugeordnet: Kurzwahl 2.' in c[0] and 'Bibliothekseinträge bleiben' in c[0], f'Programme: Rueckfrage: {c}')
    check([r['data']['id'] for r in reqs(page, '/api/collections/delete')] == ['1', '2', '3'] and toast(page) == '3 Programme gelöscht.', f'Programme geloescht: {toast(page)!r}')
    s = prog_state(); check(s['multi'] == [] and not s['dis']['v42NewProgram'], 'Programme: danach wieder normal')

    # ---- Wiederholung bei 503 (nur lesend)
    n0 = len(reqs(page, '/api/library'))
    page.evaluate("window.__mock.rules=[{path:'/api/library',n:2,status:503}]")
    r = page.evaluate("(async()=>{const t0=Date.now();try{const j=await api('/api/library');return {ok:!!j.items,ms:Date.now()-t0}}catch(e){return {err:e.message}}})()")
    check(r.get('ok') and r['ms'] >= 850 and len(reqs(page, '/api/library')) == n0 + 3, f'503 beim Lesen: zweimal gewartet, dann Erfolg: {r}')
    page.evaluate("window.__mock.rules=[{path:'/api/library',n:999,status:503}]"); n0 = len(reqs(page, '/api/library'))
    r = page.evaluate("(async()=>{try{await api('/api/library');return {}}catch(e){return {err:e.message,status:e.status}}})()")
    check(r.get('status') == 503 and 'Speicher knapp' in r.get('err', '') and len(reqs(page, '/api/library')) == n0 + 9, f'dauerhaft 503: neun Versuche, dann Fehler: {r} {len(reqs(page, "/api/library")) - n0}')
    page.evaluate("window.__mock.rules=[{path:'/api/library/save',n:5,status:503}]"); n0 = len(reqs(page, '/api/library/save'))
    r = page.evaluate("(async()=>{try{await api('/api/library/save',{name:'x'});return {}}catch(e){return {err:e.message,status:e.status}}})()")
    check(r.get('status') == 503 and len(reqs(page, '/api/library/save')) == n0 + 1, f'schreibende Anfrage wird nicht wiederholt: {r}')
    page.evaluate("window.__mock.rules=[{path:'/api/library',n:5,status:404,message:'weg'}]"); n0 = len(reqs(page, '/api/library'))
    r = page.evaluate("(async()=>{try{await api('/api/library');return {}}catch(e){return {err:e.message,status:e.status}}})()")
    check(r.get('status') == 404 and len(reqs(page, '/api/library')) == n0 + 1, f'andere Fehler werden nicht wiederholt: {r}')
    page.evaluate("window.__mock.rules=[]")

    # ---- Meldung bei fehlgeschlagenem Sendeauftrag (D10)
    page.evaluate("document.getElementById('status').hidden=true;window.__mock.status={state:'sending',message:'läuft'};rbJobWatch=false")
    page.evaluate("(async()=>{rbBleJobStart();rbBusy=0;await poll();})()"); check(toast(page) == '', 'waehrend des Sendens keine Meldung')
    page.evaluate("window.__mock.status={state:'error',message:'Tafel lehnt Paket 1 von 241 ab: Code 0x04 (Datenlaenge zu gross).'}")
    page.evaluate("(async()=>{rbBusy=0;await poll();})()")
    check(toast(page) == 'Fehler: Tafel lehnt Paket 1 von 241 ab: Code 0x04 (Datenlaenge zu gross).', f'fehlgeschlagener Auftrag wird gemeldet: {toast(page)!r}')
    page.evaluate("document.getElementById('status').hidden=true"); page.evaluate("(async()=>{rbBusy=0;await poll();})()")
    check(toast(page) == '', 'die Meldung kommt nur einmal')
    page.evaluate("window.__mock.status={state:'ok',message:'Text gesendet.'}"); page.evaluate("(async()=>{rbBleJobStart();rbBusy=0;await poll();})()")
    check(toast(page) == '' and page.evaluate('rbJobWatch') is False, 'erfolgreicher Auftrag: keine Fehlermeldung')
    page.evaluate("window.__mock.status={state:'error',message:'alt'}"); page.evaluate("(async()=>{rbBusy=0;await poll();})()")
    check(toast(page) == '', 'ein Fehler ohne eigenen Auftrag (anderes Geraet, Programm) wird nicht als Meldung gezeigt')

    # ---- Tempo-Regler sichtbar gesperrt
    page.evaluate("window.__mock.status={state:'idle',message:'Bereit',animActive:true}"); page.evaluate("(async()=>{rbBusy=0;await poll();})()")
    o = page.evaluate("""()=>{const i=document.querySelector('#rbDock input[data-global="speed"]');return {dis:i.disabled,op:getComputedStyle(i.closest('.pixel-range')).opacity,
      bright:getComputedStyle(document.querySelector('#rbDock input[data-global="brightness"]').closest('.pixel-range')).opacity}}""")
    check(o['dis'] and abs(float(o['op']) - 0.42) < 0.01 and float(o['bright']) == 1, f'gesperrter Tempo-Regler ist abgeblendet, Helligkeit nicht: {o}')
    page.evaluate("window.__mock.status={state:'idle',message:'Bereit',animActive:false}"); page.evaluate("(async()=>{rbBusy=0;await poll();})()")
    check(float(page.evaluate("getComputedStyle(document.querySelector('#rbDock input[data-global=\"speed\"]').closest('.pixel-range')).opacity")) == 1, 'frei: wieder voll sichtbar')
    check(not errs, f'keine Skriptfehler (Laptop): {errs[:3]}')
    ctx.close()

    # ============================================================ mittlere Breite 900: Menue unter der Banane
    ctx, page, errs = boot(browser, 900, 800)
    page.locator('#bananaMenu').click(); page.wait_for_timeout(200)
    g = page.evaluate("""()=>{const r=e=>e.getBoundingClientRect();const p=r(document.querySelector('.menu-panel')),b=r(document.getElementById('bananaMenu')),m=r(document.getElementById('appShell'));
      return {panel:Math.round(p.left),banana:Math.round(b.left),main:Math.round(m.left),radius:getComputedStyle(document.querySelector('.menu-panel')).borderTopLeftRadius,side:getComputedStyle(document.getElementById('mainMenu')).position}}""")
    check(abs(g['panel'] - g['banana']) <= 1 and g['radius'] == '16px', f'Menue oeffnet buendig unter der Banane, rundum abgerundet: {g}')
    if SHOTS: page.screenshot(path=str(SHOTS / 'u03_menue_900.png'))
    page.mouse.click(850, 700); page.wait_for_timeout(150)
    check(page.evaluate("document.getElementById('mainMenu').classList.contains('hidden')"), 'Klick daneben schliesst das Menue')
    d = page.evaluate("()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.width)]};return [r(document.getElementById('appShell')),r(document.getElementById('rbDock'))]}")
    check(d[0] == d[1] and d[0][1] == 720, f'Bedienfeld 720 px wie der Inhalt (vorher 694): {d}')
    check(not errs, f'keine Skriptfehler (900 px): {errs[:3]}'); ctx.close()

    # ============================================================ Handy 390: wie bisher
    ctx, page, errs = boot(browser, 390, 844, touch=True)
    g = page.evaluate("""()=>({menu:document.getElementById('mainMenu').classList.contains('hidden'),cols:getComputedStyle(document.getElementById('shortcutGrid')).gridTemplateColumns.split(' ').length,
      header:getComputedStyle(document.querySelector('.app-header')).position,over:document.documentElement.scrollWidth>window.innerWidth})""")
    check(g['menu'] and g['cols'] == 2 and g['header'] == 'sticky' and not g['over'], f'Handy: Menue zu, zwei Kacheln je Zeile, Kopf oben: {g}')
    page.locator('#bananaMenu').tap(); page.wait_for_timeout(200)
    check(page.evaluate("Math.round(document.querySelector('.menu-panel').getBoundingClientRect().left)") == 12, 'Handy: Menue 12 px vom linken Rand')
    page.evaluate("showMenu(false);navigate('library')"); page.wait_for_timeout(150)
    lp = page.locator('#libList .lib-pick'); lp.nth(0).tap(); lp.nth(2).tap(); page.wait_for_timeout(100)
    check(page.evaluate("[...rbMulti.lib].length") == 0 and page.evaluate("librarySelected") == 3 and page.evaluate("document.getElementById('libMultiBar').hidden"), 'Handy: Tippen waehlt immer nur einen Eintrag, keine Mehrfachauswahl')
    if SHOTS: page.screenshot(path=str(SHOTS / 'u04_handy_bibliothek.png'))
    check(not errs, f'keine Skriptfehler (Handy): {errs[:3]}'); ctx.close()

    # ============================================================ 0.6.1.6
    GEO = """()=>{const r=e=>e?e.getBoundingClientRect():null;const d=r(document.getElementById('rbDock'));
      const v=document.querySelector('.app-view:not(.hidden)');const p=v?[...v.querySelectorAll('.inner-panel,.panel')].find(e=>e.offsetParent&&e.getBoundingClientRect().height>40):null;const pr=r(p);
      return {ih:innerHeight,iw:innerWidth,sh:document.scrollingElement.scrollHeight,db:Math.round(d.bottom),dt:Math.round(d.top),dl:Math.round(d.left),dw:Math.round(d.width),dh:Math.round(d.height),
        pl:pr?Math.round(pr.left):null,pw:pr?Math.round(pr.width):null,frame:document.body.classList.contains('rb-frame'),over:document.documentElement.scrollWidth>innerWidth}}"""
    # ---- iPhone SE 375 x 667: Rahmen, Ambiente, Dock-Tasten
    ctx, page, errs = boot(browser, 375, 667, touch=True)
    for v in ['home', 'library', 'ambience', 'programs', 'animations']:
        page.evaluate(f"showMenu(false);navigate('{v}')"); page.wait_for_timeout(250)
        g = page.evaluate(GEO)
        check(g['frame'] and g['sh'] <= g['ih'] + 1 and abs(g['db'] - g['ih']) <= 1 and not g['over'], f'SE {v}: fensterhoch, Bedienfeld unten buendig: {g}')
        check(g['pl'] is None or (abs(g['dl'] - g['pl']) <= 1 and abs(g['dw'] - g['pw']) <= 1), f'SE {v}: Bedienfeld so breit wie die Flaeche: {g}')
        if SHOTS: page.screenshot(path=str(SHOTS / f'x_se_{v}.png'))
    page.evaluate("navigate('ambience')"); page.wait_for_timeout(200)
    a = page.evaluate("""()=>{const b=[...document.querySelectorAll('#ambienceColors button')];const d=document.getElementById('rbDock').getBoundingClientRect();
      const w=b[b.length-1].getBoundingClientRect();const box=document.getElementById('ambienceColors').getBoundingClientRect();return {n:b.length,last:Math.round(w.bottom),boxb:Math.round(box.bottom),dock:Math.round(d.top),minh:Math.round(Math.min(...b.map(x=>x.getBoundingClientRect().height)))}}""")
    check(a['n'] == 7 and a['minh'] >= 33 and a['boxb'] <= a['dock'] + 1, f'SE Ambiente: sieben Farben, Mindesthoehe, Feld endet ueber dem Bedienfeld: {a}')
    k = page.evaluate("[...document.querySelectorAll('.rb-dock-actions button.v43-force-btn')].filter(b=>b.offsetParent).map(b=>{const r=b.getBoundingClientRect();return [Math.round(r.width),Math.round(r.top)]})")
    check(k and all(w == 30 for w, t in k) and len(set(t for w, t in k)) == 1, f'SE: Dock-Tasten 30 px in einer Reihe: {k}')
    # Blocktext-Kopf
    page.evaluate("navigate('editor');setTab('pages')"); page.wait_for_timeout(300)
    check(page.text_content('#rbBlockHead').strip() == 'Blocktext · Seite 1 von 40', 'Blocktext-Kopf: ' + page.text_content('#rbBlockHead'))
    page.evaluate("navigate('editor');setTab('scroll')"); page.wait_for_timeout(200)
    g = page.evaluate(GEO); check(not g['frame'], f'Texteditor scrollt normal (kein Rahmen): {g}')
    # ---- Sperre waehrend einer Uebertragung (das ANDERE Geraet: nur der Status meldet busy)
    page.evaluate("navigate('library')"); page.wait_for_timeout(200)
    h0 = page.evaluate(GEO)['dh']
    page.evaluate("window.__mock.status={state:'sending',busy:true,message:'Übertragung läuft …'};rbPollPending=false;rbBusy=0;rbTxPolledAt=0;poll()"); page.wait_for_timeout(400)
    t = page.evaluate("""()=>({tx:document.documentElement.classList.contains('rb-tx'),pill:getComputedStyle(document.querySelector('.rb-tx-pill')).display,text:document.querySelector('.rb-tx-pill').textContent,
       h:Math.round(document.getElementById('rbDock').getBoundingClientRect().height),pe:getComputedStyle(document.getElementById('libSend')).pointerEvents,
       range:getComputedStyle(document.querySelector('#rbDock input[type=range]')).pointerEvents})""")
    check(t['tx'] and t['pill'] == 'flex' and 'Übertragung läuft' in t['text'] and abs(t['h'] - h0) <= 1 and t['pe'] == 'none' and t['range'] == 'none', f'Sperre: Hinweis auf dem Bedienfeld, gleiche Hoehe, Knoepfe gesperrt: {t} (vorher {h0})')
    if SHOTS: page.screenshot(path=str(SHOTS / 'x_se_uebertragung.png'))
    n0 = len(page.evaluate('__mock.requests'))
    r = page.evaluate("async()=>{try{await api('/api/text',{text:'x'});return 'ok'}catch(e){return e.status+' '+e.message}}")
    check(r.startswith('409') and len(page.evaluate('__mock.requests')) == n0, f'Sperre: schreibende Anfrage geht nicht raus: {r}')
    page.evaluate("navigate('programs')"); page.wait_for_timeout(200)
    check(page.evaluate("document.body.dataset.rbView") == 'programs', 'Sperre: Seiten wechseln geht')
    page.evaluate("window.__mock.status={state:'idle'};rbPollPending=false;rbBusy=0;rbTxPolledAt=0;poll()"); page.wait_for_timeout(400)
    check(not page.evaluate("document.documentElement.classList.contains('rb-tx')"), 'Sperre endet mit dem Status')
    # 409 busy auf eine lesende Anfrage: warten, wiederholen, danach Liste da
    page.evaluate("window.__mock.status={state:'sending',busy:true};window.__mock.rules=[{path:'/api/library',n:2,status:409,body:{ok:false,busy:true,message:'Übertragung läuft.'}}]")
    page.evaluate("window.__lr=null;refreshLibrary().then(()=>window.__lr='ok',e=>window.__lr='err '+e.message)"); page.wait_for_timeout(600)
    check(page.evaluate("document.documentElement.classList.contains('rb-tx')"), '409 busy: Sperre an, waehrend gewartet wird ' + str(page.evaluate("[window.__lr,rbTxOn,JSON.stringify(__mock.requests.slice(-3))]")))
    page.evaluate("window.__mock.status={state:'idle'}"); page.wait_for_function("window.__lr!==null", timeout=8000)
    check(page.evaluate("window.__lr") == 'ok' and len(reqs(page, '/api/library')) >= 2, 'lesende Anfrage nach 409 busy wiederholt und erfolgreich: ' + str(page.evaluate("window.__lr")))
    page.evaluate("window.__mock.status={state:'idle'};rbPollPending=false;rbBusy=0;rbTxPolledAt=0;poll()"); page.wait_for_timeout(300)
    # „sending“ nur zweimal HINTEREINANDER sperrt (kurze Steuerbefehle); ein normaler Status dazwischen setzt zurueck
    page.evaluate("rbTxFromStatus({state:'sending'});rbTxFromStatus({state:'idle'});rbTxFromStatus({state:'sending'})")
    check(not page.evaluate("rbTxOn"), 'kurze Auftraege mit Pause dazwischen sperren nicht')
    page.evaluate("rbTxFromStatus({state:'sending'})"); check(page.evaluate("rbTxOn"), 'zweimal hintereinander sending sperrt')
    page.evaluate("rbTxFromStatus({state:'idle'})"); check(not page.evaluate("rbTxOn"), 'idle hebt auf')
    # Kurzwahl-Dialog: beschaedigtes Programm ausgegraut
    page.evaluate("window.__mock.programs=[{id:1,name:'Gut',count:2,missing:0,ids:[1,2]},{id:2,name:'Kaputt',count:2,missing:1,ids:[1,99]}];navigate('home');v42OpenShortcut(2)"); page.wait_for_function("!document.getElementById('v42ShortcutDialog').classList.contains('hidden')"); page.wait_for_timeout(300)
    page.evaluate("[...document.querySelectorAll('#v42Sources button')].find(b=>b.textContent.trim()==='Programme').click()"); page.wait_for_timeout(200)
    o = page.evaluate("[...document.querySelectorAll('#v42ShortcutTarget option')].map(o=>[o.textContent,o.disabled])")
    check(['Kaputt (beschädigt)', True] in o and ['Gut', False] in o, f'Kurzwahl: beschaedigtes Programm ausgegraut: {o}')
    page.evaluate("window.__mock.rules=[{path:'/api/shortcuts/set',n:1,status:500,message:'Schreibfehler'}];document.getElementById('v42ShortcutTarget').value='1';document.getElementById('v42ShortcutTarget').dispatchEvent(new Event('change'));document.getElementById('v42ShortcutSave').click()"); page.wait_for_timeout(400)
    check('Schreibfehler' in page.inner_text('#v42ShortcutMsg') and not page.evaluate("document.getElementById('v42ShortcutDialog').classList.contains('hidden')"), 'Kurzwahl: Meldung steht im Dialog')
    page.evaluate("document.getElementById('v42ShortcutDialog').classList.add('hidden')")
    # Namen aus Dateinamen
    nn = page.evaluate("[rbNiceName('party_time-loop.gif'),rbNiceName('IMG_20241103.gif'),rbNiceName('giphy.gif'),rbNiceName('herzschlag.txt')]")
    check(nn[0] == 'Party time loop' and nn[1].startswith('Animation ') and nn[2].startswith('Animation ') and nn[3] == 'Herzschlag', f'Namen aus Dateinamen: {nn}')
    # lange Namen: weich ausgeblendet, beim Auswaehlen einmal durchlaufen
    page.evaluate("window.__mock.entries.push({id:50,name:'Ein sehr langer Name für die Festivaltafel am Abend',text:'x',line2:'',layout:0,color1:3,color2:0,mode:0,kind:'text'});navigate('library');refreshLibrary()"); page.wait_for_timeout(500)
    ln = page.locator('#libList .library-row').filter(has_text='Ein sehr langer').locator('.lib-name')
    st = ln.evaluate("e=>({fits:e.classList.contains('rb-fits'),mask:getComputedStyle(e).webkitMaskImage||getComputedStyle(e).maskImage,title:e.title})")
    check(not st['fits'] and 'gradient' in st['mask'] and st['title'].startswith('Ein sehr langer'), f'langer Name: Verlauf statt Punkte, Tooltip: {st}')
    page.locator('#libList .library-row').filter(has_text='Ein sehr langer').locator('.lib-pick').tap(); page.wait_for_timeout(300)
    check(ln.evaluate("e=>e.classList.contains('rb-run')"), 'langer Name laeuft beim Auswaehlen einmal durch')
    check(not errs, f'keine Skriptfehler (SE 0.6.1.6): {errs[:3]}'); ctx.close()
    # ---- Schrift mit Wiederholung: /api/font antwortet anfangs 12x mit 503
    ctx, page, errs = boot(browser, 390, 844, touch=True, pre=[{'path': '/api/font', 'n': 12, 'status': 503}])
    check(not page.evaluate("fontReady"), 'Schrift: zunaechst nicht da (503)')
    page.wait_for_function("fontReady===true", timeout=20000)
    check(page.evaluate("fontReady") and len(reqs(page, '/api/font')) >= 13, 'Schrift: nach 503 im Hintergrund nachgeladen, Vorschau geht wieder')
    check(not [e for e in errs if 'font' not in e.lower()], f'keine Skriptfehler (Schrift): {errs[:3]}'); ctx.close()
    # ---- Laptop 1440 x 900: Rahmen
    ctx, page, errs = boot(browser, 1440, 900)
    for v in ['home', 'library', 'animations']:
        page.evaluate(f"navigate('{v}')"); page.wait_for_timeout(250); g = page.evaluate(GEO)
        check(g['frame'] and g['sh'] <= g['ih'] + 1 and abs(g['db'] - g['ih']) <= 1 and (g['pl'] is None or (abs(g['dl'] - g['pl']) <= 1 and abs(g['dw'] - g['pw']) <= 1)), f'Laptop {v}: Rahmen {g}')
        if SHOTS: page.screenshot(path=str(SHOTS / f'x_laptop_{v}.png'))
    check(not errs, f'keine Skriptfehler (Laptop 0.6.1.6): {errs[:3]}'); ctx.close()
    browser.close()
print('FAILS:', len(fails))
if not fails: print('PASS Browser 0.6.1.6: Sperre waehrend Uebertragung, Schrift mit Wiederholung, Rahmen (SE/Handy/Laptop), Ambiente, Dock-Tasten, lange Namen, Dateinamen, Kurzwahl beschaedigt, Blocktext-Kopf | 0.6.1.5: Mehrfachauswahl (Bibliothek, Programme), 503-Wiederholung, Auftragsfehler-Meldung, Tempo-Sperre, Seitenleiste, Menue, Bedienfeldbreite')
sys.exit(1 if fails else 0)
