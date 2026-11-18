"""v0.6.1.11: Neues und Korrekturen der Weboberflaeche im echten (headless) Chromium mit simulierter API.
Prueft: JSON-Backup mit Animationen (Export Schema 3, Import mit Wiederverwendung, Kurzwahl Typ 4 umgeschluesselt),
WLAN-Passwort in den Einstellungen (Abfrage, Pruefung im Browser, Speichern, Standard wiederherstellen; kein Passwort im
Backup), Blocktext aus der Bibliothek ueber /api/library/send (Markierung mit ID), Seite duplizieren direkt hinter dem
Original, zusammengefasste Listenabrufe, Live-Einstellung wird nachgeholt (F-040), Bearbeiten erhaelt den Standbild-Modus
(F-036), keine Abfrage beim Seitenstart doppelt.
Aufruf: python tests/test_browser_neu_06111.py
Nicht geprueft: echtes iPhone-Safari, echter ESP32 (WLAN-Neustart, BOOT-Taste)."""
import json, re, sys, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'web/index.html').read_text(encoding='utf8')
src = (ROOT / 'tests/test_browser_06111.py').read_text(encoding='utf8')
asrc = (ROOT / 'tests/test_browser_anim_06111.py').read_text(encoding='utf8')
base = src[src.index("MOCK=r'''") + 9:src.index("'''.replace('%FONT%'")].replace('%FONT%', '{}')
ANIM_MOCK = asrc[asrc.index("ANIM_MOCK = r'''") + 16:asrc.index("</script>'''", asrc.index("ANIM_MOCK = r'''")) + 9]
EXTRA = r'''<script>
(function(){
 const base=window.fetch;
 window.__x={wifiCustom:false,pages:[{line1:'A',line2:'',layout:3,align:1,color1:6,color2:7,duration:7},{line1:'B',line2:'',layout:3,align:1,color1:6,color2:7,duration:7}],shortcuts:Array.from({length:8},()=>({type:0,id:0,label:''}))};
 window.fetch=async function(path,opt={}){
  const full=String(path),p=full.split('?')[0],X=window.__x,m=window.__mock,arg=new URLSearchParams(opt.body||''),q=new URLSearchParams(full.split('?')[1]||'');
  const reply=(obj,status)=>{m.requests.push({path:p,method:opt.method||'GET',data:Object.fromEntries(arg.entries())});const snap=JSON.stringify(obj);return {ok:(status||200)<400,status:status||200,json:async()=>JSON.parse(snap),text:async()=>snap};};
  if(p==='/api/wifi')return reply({ok:true,ssid:'RavestickBoard',custom:X.wifiCustom,min:8,max:63});
  if(p==='/api/wifi/password'){if(arg.get('reset')==='1'){X.wifiCustom=false;return reply({ok:true,message:'Standardpasswort gesetzt.'});}
   const pw=arg.get('pw')||'';if(pw.length<8||pw.length>63||/[^\x20-\x7e]/.test(pw))return reply({ok:false,message:'Passwort ungültig.'},400);X.wifiCustom=true;X.lastPw=pw;return reply({ok:true,message:'Passwort gespeichert.'});}
  if(p==='/api/program')return reply({ok:true,pages:JSON.parse(JSON.stringify(X.pages)),current:0});
  if(p==='/api/program/add'){const c=arg.has('copy')?Number(arg.get('copy')):-1;if(c>=0)X.pages.splice(c+1,0,JSON.parse(JSON.stringify(X.pages[c])));else X.pages.push({line1:'',line2:'',layout:3,align:1,color1:6,color2:7,duration:7});return reply({ok:true,message:'Seite hinzugefügt.'});}
  if(p==='/api/program/set'){const i=Number(arg.get('index'));if(X.pages[i])Object.assign(X.pages[i],{line1:arg.get('line1'),line2:arg.get('line2')});return reply({ok:true,message:'ok'});}
  if(p==='/api/collections/get'){const id=Number(q.get('id'));return reply(Object.assign({ok:true},JSON.parse(JSON.stringify((m.programs||[]).find(x=>x.id===id)||{}))));}
  if(p==='/api/collections/save'){const id=(m.programs||[]).reduce((a,x)=>Math.max(a,x.id),0)+1;(m.programs=m.programs||[]).push({id,name:arg.get('name'),ids:(arg.get('ids')||'').split(',').map(Number),seconds:Number(arg.get('seconds')),playback:Number(arg.get('playback'))});return reply({ok:true,id});}
  if(p==='/api/shortcuts')return reply({ok:true,items:JSON.parse(JSON.stringify(X.shortcuts))});
  if(p==='/api/shortcuts/set'){const i=Number(arg.get('slot'))-1;X.shortcuts[i]={type:Number(arg.get('type')),id:Number(arg.get('id')),label:arg.get('label')||''};return reply({ok:true,message:'Kurzwahl gespeichert.'});}
  if(p==='/api/library/send'||p==='/api/block/send')return reply({ok:true,message:'Wird gesendet.'},202);
  if(p==='/api/block/get'){const id=Number(q.get('id'));const e=m.entries.find(x=>x.id===id);return reply({ok:true,id,name:e?e.name:'',pages:e&&e.pages?e.pages:[]});}
  return base(path,opt);
 };
})();
</script>'''
errors = []
def check(c, msg):
    if not c: errors.append(msg); print('FAIL', msg)
def reqs(page, path): return [r for r in page.evaluate('__mock.requests') if r['path'] == path]
def toast(page): return page.evaluate("document.getElementById('status').hidden?'':document.getElementById('status').textContent")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    page = ctx.new_page(); page.on('pageerror', lambda e: errors.append(str(e)))
    first = html.index('<script>')
    page_html = html[:first] + base + ANIM_MOCK + EXTRA + html[first:]
    page.route('http://rb.test/**', lambda r: r.fulfill(status=200, body=page_html, content_type='text/html; charset=utf-8'))
    page.goto('http://rb.test/', wait_until='domcontentloaded')
    page.wait_for_function('!document.documentElement.classList.contains("rb-booting")', timeout=15000)
    page.wait_for_timeout(1500)

    # ---- Seitenstart: jede Liste genau einmal --------------------------------------------------------------------
    counts = {p: len(reqs(page, p)) for p in ['/api/shortcuts', '/api/collections', '/api/library', '/api/anim/list']}
    check(all(v == 1 for v in counts.values()), f'Seitenstart: jede Liste einmal {counts}')

    # ---- Daten anlegen ------------------------------------------------------------------------------------------
    page.evaluate("""()=>{const m=window.__mock;m.entries=[
      {id:1,name:'Hallo',text:'Hallo',line2:'',layout:0,color1:3,color2:3,mode:2,kind:'text',favorite:0},
      {id:2,name:'Stand',text:'Stand',line2:'',layout:0,color1:4,color2:4,mode:1,kind:'text',favorite:0},
      {id:3,name:'Block',text:'[Blockfolge]',line2:'',layout:5,color1:7,color2:7,mode:1,kind:'block',favorite:0,pages:[{line1:'X',line2:'',layout:3,align:1,color1:6,color2:7,duration:7}]}];m.nextId=4;
      m.programs=[{id:1,name:'Prog',count:2,ids:[1,2],seconds:20,playback:0}];
      const A=window.__anim;const mk=(n,c)=>{const fr=[];for(let k=0;k<n;k++){const px=new Uint8Array(64*16);for(let x=0;x<64;x++)px[k*4%64*16+0]=c;px[k]=c;fr.push(px);}return fr;};
      for(const [name,n,c,ms] of [['Funken',5,2,80],['Welle',9,4,120]]){const payload=RbAnim.buildPayload(mk(n,c),ms);A.items.push({id:A.nextId++,name,frames:n,ms,payload,crc:RbAnim.crc32(payload)});}
      window.__x.shortcuts[2]={type:4,id:2,label:''};window.__x.shortcuts[0]={type:1,id:1,label:''};}""")
    page.evaluate("async()=>{await refreshLibrary();await v42RefreshPrograms();await animLoad();await v42RefreshShortcuts();}")

    # ---- Backup-Export mit Animationen ----------------------------------------------------------------------------
    page.evaluate("""()=>{window.__blobs=[];const o=URL.createObjectURL;URL.createObjectURL=b=>{window.__blobs.push(b);return o.call(URL,b);};
      HTMLAnchorElement.prototype.click=function(){};}""")
    page.evaluate("navigate('settings')"); page.wait_for_timeout(300)
    page.locator('#libExport').click()
    page.wait_for_function("document.getElementById('status').textContent.includes('Backup erstellt')", timeout=15000)
    t = toast(page)
    check('3 Bibliothekseinträge' in t and '1 Programme' in t and '2 Animationen' in t and 'Vollständig' not in t, f'Meldung nennt, was drin ist: {t!r}')
    backup_txt = page.evaluate("window.__blobs.at(-1).text()")
    bk = json.loads(backup_txt)
    check(bk['schema'] == 3 and len(bk['animations']) == 2 and bk['firmware'].startswith('0.6.1.11'), f"Schema 3, 2 Animationen, Version {bk.get('firmware')}")
    same = page.evaluate("""(an)=>an.every(a=>{const x=window.__anim.items.find(y=>y.id===a.id);const d=RbAnim.b64uDec(a.data);
      return x&&d.length===x.payload.length&&d.every((v,i)=>v===x.payload[i])&&a.frames===x.frames&&a.ms===x.ms&&a.name===x.name&&a.crc===(x.crc>>>0).toString(16).padStart(8,'0')})""", bk['animations'])
    check(same, 'Nutzlast, Name, Bilder, Zeit und Prüfsumme jeder Animation stimmen')
    check('pw' not in backup_txt.lower().replace('pw":', 'X') and 'Banane1248' not in backup_txt and 'wifi' not in backup_txt.lower(), 'kein WLAN-Passwort im Backup')
    check(page.inner_text('#libExport').strip() != '' and 'Backup:' not in page.inner_text('#libExport'), 'Knopf zeigt danach wieder seinen Text')

    # ---- Import in eine leere Animationsliste: neu anlegen, Kurzwahl Typ 4 auf neue ID -----------------------------
    page.evaluate("""()=>{const A=window.__anim;window.__oldIds=A.items.map(x=>x.id);A.items=[];A.nextId=50;
      window.__x.shortcuts=Array.from({length:8},()=>({type:0,id:0,label:''}));window.confirm=()=>true;}""")
    page.evaluate("async()=>{await animLoad();await v42RefreshShortcuts();}")
    page.set_input_files('#libImport', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup_txt.encode('utf8')}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Kurzwahlen übernommen')", timeout=20000)
    t = toast(page)
    check('2 neue Animationen' in t, f'Import legt 2 Animationen an: {t!r}')
    items = page.evaluate("window.__anim.items.map(x=>({id:x.id,name:x.name,frames:x.frames,ms:x.ms,n:x.payload.length}))")
    check(sorted(i['name'] for i in items) == ['Funken', 'Welle'] and all(i['id'] >= 50 for i in items), f'importierte Animationen {items}')
    sc = page.evaluate("window.__x.shortcuts[2]")
    welle_new = next((i['id'] for i in items if i['name'] == 'Welle'), None)
    check(sc['type'] == 4 and sc['id'] == welle_new, f'Kurzwahl Typ 4 zeigt auf die neue ID {sc} (Welle={welle_new})')
    # nochmal importieren: nichts doppelt
    n_put = len(reqs(page, '/api/anim/put'))
    page.set_input_files('#libImport', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup_txt.encode('utf8')}])
    page.wait_for_function("document.getElementById('status').textContent.includes('2 vorhandene;')||document.getElementById('status').textContent.includes('0 neue Animationen')", timeout=20000)
    t = toast(page)
    check('0 neue Animationen, 2 vorhandene' in t and len(reqs(page, '/api/anim/put')) == n_put and page.evaluate("window.__anim.items.length") == 2, f'zweiter Import erkennt die Animationen wieder: {t!r}')
    # beschaedigte Animation im Backup: klare Meldung, Rest bleibt
    bad = json.loads(backup_txt); bad['animations'][1]['crc'] = '00000000'
    page.evaluate("()=>{window.__anim.items=[];window.__anim.nextId=70;}"); page.evaluate("animLoad()")
    page.set_input_files('#libImport', files=[{'name': 'b.json', 'mimeType': 'application/json', 'buffer': json.dumps(bad).encode()}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Kurzwahlen übernommen')", timeout=20000)
    t = toast(page)
    check('1 neue Animationen' in t and 'Prüfsumme' in t, f'falsche Prüfsumme wird gemeldet, die erste ist übernommen: {t!r}')
    # altes Schema 2 (ohne Animationen) wird weiter angenommen
    old = json.loads(backup_txt); old['schema'] = 2; old.pop('animations')
    page.set_input_files('#libImport', files=[{'name': 'alt.json', 'mimeType': 'application/json', 'buffer': json.dumps(old).encode()}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Kurzwahlen übernommen')", timeout=20000)
    check('Unbekanntes' not in toast(page), 'Schema 2 wird weiter gelesen')

    # ---- WLAN-Passwort -----------------------------------------------------------------------------------------
    page.evaluate("navigate('home')"); n0 = len(reqs(page, '/api/wifi')); page.evaluate("navigate('settings')"); page.wait_for_timeout(300)
    check(len(reqs(page, '/api/wifi')) == n0 + 1, 'Einstellungen fragen /api/wifi ab')
    check('Standardpasswort' in page.inner_text('#rbWifiState') and page.locator('#rbWifiReset').is_hidden(), 'Standard aktiv: Hinweis, kein Zurücksetzen-Knopf')
    check(page.get_attribute('#rbWifiPw', 'type') == 'password', 'Feld verdeckt')
    page.locator('#rbWifiShow').check(); check(page.get_attribute('#rbWifiPw', 'type') == 'text', 'Anzeigen schaltet auf Klartext')
    n_post = len(reqs(page, '/api/wifi/password'))
    check(page.get_attribute('#rbWifiPw', 'maxlength') == '63', 'Feld nimmt höchstens 63 Zeichen an')
    for bad_pw, why in [('kurz', 'zu kurz'), ('Bananenbrot€123', 'Sonderzeichen außerhalb ASCII')]:
        page.fill('#rbWifiPw', bad_pw); page.locator('#rbWifiSave').click(); page.wait_for_timeout(150)
        check(len(reqs(page, '/api/wifi/password')) == n_post and 'Fehler' in toast(page), f'{why}: nichts gesendet, Fehlermeldung')
    page.evaluate("window.__conf=[];window.confirm=m=>{window.__conf.push(m);return true};0")
    page.fill('#rbWifiPw', 'Festival2026!'); page.locator('#rbWifiSave').click(); page.wait_for_timeout(300)
    r = reqs(page, '/api/wifi/password')
    check(len(r) == n_post + 1 and r[-1]['data'] == {'pw': 'Festival2026!'}, f'gültiges Passwort wird gesendet {r[-1:]}')
    check(any('BOOT-Taste' in c for c in page.evaluate('window.__conf')), 'Rückfrage erklärt den Notweg über die BOOT-Taste')
    check(page.input_value('#rbWifiPw') == '' and 'eigenes Passwort' in page.inner_text('#rbWifiState') and page.locator('#rbWifiReset').is_visible(), 'danach: Feld leer, eigenes Passwort aktiv, Zurücksetzen sichtbar')
    page.locator('#rbWifiReset').click(); page.wait_for_timeout(300)
    check(reqs(page, '/api/wifi/password')[-1]['data'] == {'reset': '1'} and 'Standardpasswort' in page.inner_text('#rbWifiState'), 'Standard wiederherstellen')
    page.evaluate("window.confirm=()=>false;0"); n_post = len(reqs(page, '/api/wifi/password'))
    page.fill('#rbWifiPw', 'Festival2026!'); page.locator('#rbWifiSave').click(); page.wait_for_timeout(200)
    check(len(reqs(page, '/api/wifi/password')) == n_post, 'Abbrechen in der Rückfrage sendet nichts')
    page.evaluate("window.confirm=()=>true;0")

    # ---- Blocktext aus der Bibliothek ueber library/send (E7) -----------------------------------------------------
    page.evaluate("navigate('library')"); page.wait_for_timeout(300)
    page.evaluate("()=>{librarySelected=3;renderLibrary();}"); page.wait_for_timeout(100)
    page.locator('#libSend').click(); page.wait_for_timeout(300)
    check(len(reqs(page, '/api/library/send')) >= 1 and reqs(page, '/api/library/send')[-1]['data'].get('id') == '3' and not reqs(page, '/api/block/send'),
          'Blocktext wird über /api/library/send mit ID gesendet')

    # ---- Seite duplizieren: Kopie direkt hinter dem Original ------------------------------------------------------
    page.evaluate("navigate('editor');setTab('pages')"); page.wait_for_timeout(200)
    page.evaluate("async()=>{await refreshPages();selected=0;await refreshPages();}"); page.wait_for_timeout(200)
    page.locator('#pageCopy').click(); page.wait_for_timeout(400)
    lines = page.evaluate("window.__x.pages.map(p=>p.line1)"); sel = page.evaluate("selected")
    check(lines[:3] == ['A', 'A', 'B'] and sel == 1, f'Kopie von Seite 1 steht als Seite 2, Auswahl auf der Kopie: {lines} sel={sel}')

    # ---- Listen-Abrufe zusammenfassen ---------------------------------------------------------------------------
    page.evaluate("window.__mock.listDelay=600"); n = len(reqs(page, '/api/library'))
    page.evaluate("()=>{window.__p=Promise.all([refreshLibrary(true),refreshLibrary(true)]);}"); page.wait_for_timeout(900)
    check(len(reqs(page, '/api/library')) == n + 1, 'zweimal „abwarten“ ergibt einen Abruf')
    n = len(reqs(page, '/api/library'))
    page.evaluate("()=>{refreshLibrary();refreshLibrary();refreshLibrary();}"); page.wait_for_timeout(2200)
    check(len(reqs(page, '/api/library')) == n + 2, f'drei Auffrischungen während eines Abrufs: genau ein Nachzügler ({len(reqs(page, "/api/library")) - n})')
    page.evaluate("window.__mock.listDelay=0")

    # ---- Live-Einstellung wird nachgeholt (F-040) ------------------------------------------------------------------
    page.evaluate("()=>{window.__mock.status={state:'sending'};queueLive('brightness',{value:'37'});}")
    page.wait_for_timeout(7500)
    check(not any(r['data'].get('value') == '37' for r in reqs(page, '/api/brightness')) and 'nachgeholt' in toast(page), f'während Übertragung: nichts gesendet, Hinweis {toast(page)!r}')
    page.evaluate("window.__mock.status={}"); page.wait_for_timeout(1500)
    check(any(r['data'].get('value') == '37' for r in reqs(page, '/api/brightness')), 'danach wird der Wert nachgeholt')

    # ---- Bearbeiten erhaelt den Standbild-Modus (F-036) ------------------------------------------------------------
    page.evaluate("async()=>{await refreshLibrary();libraryEditorId=2;libraryCurrentRecord=null;const t=document.getElementById('scrollText');t.value='Stand';t.dispatchEvent(new Event('input'));}")
    page.wait_for_timeout(200); page.evaluate("v43SaveScrollUpdate()"); page.wait_for_timeout(400)
    sv = [r for r in reqs(page, '/api/library/save') if r['data'].get('id') == '2']
    check(sv and sv[-1]['data'].get('mode') == '1', f'Standbild bleibt Standbild beim Überschreiben {sv[-1:]}')

    check(not [e for e in errors if not e.startswith('console:')], f'keine Skriptfehler {errors[:3]}')
    browser.close()

print('FAILS:', len(errors))
if not errors:
    print('PASS Browser 0.6.1.11: Backup mit Animationen (Export/Import/Wiederverwendung/Kurzwahl 4/Prüfsumme/Schema 2), WLAN-Passwort, Blocktext über library/send, Seite duplizieren dahinter, zusammengefasste Abrufe, Live-Wert nachgeholt, Standbild bleibt, Seitenstart ohne Doppelabrufe')
sys.exit(1 if errors else 0)
