"""v0.6.1.11 und v0.7.1: Neues und Korrekturen der Weboberflaeche im echten (headless) Chromium mit simulierter API.
Prueft: JSON-Backup mit Animationen (Export Schema 3, Import mit Wiederverwendung, Kurzwahl Typ 4 umgeschluesselt),
WLAN-Passwort in den Einstellungen (Abfrage, Pruefung im Browser, Speichern, Standard wiederherstellen; kein Passwort im
Backup), Blocktext aus der Bibliothek ueber /api/library/send (Markierung mit ID), Seite duplizieren direkt hinter dem
Original, zusammengefasste Listenabrufe, Live-Einstellung wird nachgeholt (F-040), Bearbeiten erhaelt den Standbild-Modus
(F-036), keine Abfrage beim Seitenstart doppelt.
v0.7.2: Export mit Auswahl (Abhaengigkeiten kommen mit), Standardpasswort im Klartext, WLAN-Puffer/Sicherheit,
Senden waehrend Programm (409 retry, automatisch nachgesendet), Upload-Kennung, Animations-ID sichtbar,
Design-Tokens (Eingaberand, ein Gruenton), Importfortschritt.
Aufruf: python tests/test_browser_neu_0802.py
Nicht geprueft: echtes iPhone-Safari, echter ESP32 (WLAN-Neustart, BOOT-Taste)."""
import json, re, sys, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'web/index.html').read_text(encoding='utf8')
src = (ROOT / 'tests/test_browser_0802.py').read_text(encoding='utf8')
asrc = (ROOT / 'tests/test_browser_anim_0802.py').read_text(encoding='utf8')
base = src[src.index("MOCK=r'''") + 9:src.index("'''.replace('%FONT%'")].replace('%FONT%', '{}')
ANIM_MOCK = asrc[asrc.index("ANIM_MOCK = r'''") + 16:asrc.index("</script>'''", asrc.index("ANIM_MOCK = r'''")) + 9]
EXTRA = r'''<script>
(function(){
 const base=window.fetch;
 window.__x={wifiCustom:false,pages:[{line1:'A',line2:'',layout:3,align:1,color1:6,color2:7,duration:7},{line1:'B',line2:'',layout:3,align:1,color1:6,color2:7,duration:7}],shortcuts:Array.from({length:8},()=>({type:0,id:0,label:''}))};
 window.fetch=async function(path,opt={}){
  const full=String(path),p=full.split('?')[0],X=window.__x,m=window.__mock,arg=new URLSearchParams(opt.body||''),q=new URLSearchParams(full.split('?')[1]||'');
  const reply=(obj,status)=>{m.requests.push({path:p,method:opt.method||'GET',data:Object.fromEntries(arg.entries())});const snap=JSON.stringify(obj);return {ok:(status||200)<400,status:status||200,json:async()=>JSON.parse(snap),text:async()=>snap};};
  if(p==='/api/wifi')return reply({ok:true,ssid:'RavestickBoard',custom:X.wifiCustom,min:8,max:63,standard:'Banane1248!',buf:X.buf??1,bufActive:X.bufActive??1,rxDynamic:(X.bufActive??1)?8:32,sec:X.sec??0,secActive:X.secActive??0});
  if(p==='/api/wifi/settings'){if(arg.has('buf'))X.buf=Number(arg.get('buf'));if(arg.has('sec'))X.sec=Number(arg.get('sec'));return reply({ok:true,message:arg.get('restart')==='1'?'Gespeichert. Der ESP32 startet gleich neu.':'Gespeichert. Wirkt nach dem nächsten Neustart.'});}
  if(p==='/api/text'&&X.progBusy>0){X.progBusy--;return reply({ok:false,busy:true,retry:true,message:'Das Programm endet nach dem laufenden Schritt.'},409);}
  if(p==='/api/text')return reply({ok:true,message:'Text angenommen.'},202);
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
    page.wait_for_selector('#rbExportDialog .rb-export-opt', timeout=5000)
    check(page.evaluate("[...document.querySelectorAll('.rb-export-opt input')].every(c=>c.checked)") and page.evaluate("document.activeElement&&document.activeElement.id")=='rbExp_library', 'Export-Dialog: alles vorausgewählt, Fokus auf der ersten Wahl')
    page.locator('#rbExportDialog button.primary').click()
    page.wait_for_function("document.getElementById('status').textContent.includes('Backup erstellt')", timeout=15000)
    t = toast(page)
    check('3 Bibliothekseinträge' in t and '1 Programme' in t and '2 Animationen' in t and 'Vollständig' not in t, f'Meldung nennt, was drin ist: {t!r}')
    backup_txt = page.evaluate("window.__blobs.at(-1).text()")
    bk = json.loads(backup_txt)
    check(bk['schema'] == 3 and len(bk['animations']) == 2 and bk['firmware'].startswith('0.8.2'), f"Schema 3, 2 Animationen, Version {bk.get('firmware')}")
    same = page.evaluate("""(an)=>an.every(a=>{const x=window.__anim.items.find(y=>y.id===a.id);const d=RbAnim.b64uDec(a.data);
      return x&&d.length===x.payload.length&&d.every((v,i)=>v===x.payload[i])&&a.frames===x.frames&&a.ms===x.ms&&a.name===x.name&&a.crc===(x.crc>>>0).toString(16).padStart(8,'0')})""", bk['animations'])
    check(same, 'Nutzlast, Name, Bilder, Zeit und Prüfsumme jeder Animation stimmen')
    check('pw' not in backup_txt.lower().replace('pw":', 'X') and 'Banane1248' not in backup_txt and 'wifi' not in backup_txt.lower(), 'kein WLAN-Passwort im Backup')
    check(page.inner_text('#libExport').strip() != '' and 'Backup:' not in page.inner_text('#libExport'), 'Knopf zeigt danach wieder seinen Text')

    # ---- Import in eine leere Animationsliste: neu anlegen, Kurzwahl Typ 4 auf neue ID -----------------------------
    page.evaluate("""()=>{const A=window.__anim;window.__oldIds=A.items.map(x=>x.id);A.items=[];A.nextId=50;
      window.__x.shortcuts=Array.from({length:8},()=>({type:0,id:0,label:''}));window.confirm=()=>true;}""")
    page.evaluate("async()=>{await animLoad();await v42RefreshShortcuts();}")
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup_txt.encode('utf8')}])
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
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup_txt.encode('utf8')}])
    page.wait_for_function("document.getElementById('status').textContent.includes('2 vorhandene;')||document.getElementById('status').textContent.includes('0 neue Animationen')", timeout=20000)
    t = toast(page)
    check('0 neue Animationen, 2 vorhandene' in t and len(reqs(page, '/api/anim/put')) == n_put and page.evaluate("window.__anim.items.length") == 2, f'zweiter Import erkennt die Animationen wieder: {t!r}')
    # v0.7.1 (F3): vorhandene Animationen aus aelteren Dateien ohne Pruefsumme (rev 00000000) werden ueber die Nutzlast erkannt
    page.evaluate("()=>{for(const x of window.__anim.items)x.crc=0;}"); page.evaluate("animLoad()"); page.wait_for_timeout(300)
    n_put = len(reqs(page, '/api/anim/put')); n_get = len(reqs(page, '/api/anim/get'))
    page.evaluate("()=>{window.__prog=[];const o=window.rbImportProgress;window.rbImportProgress=t=>{window.__prog.push(t);o(t);};const st=document.getElementById('status');st.textContent='';st.hidden=true;}")
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': backup_txt.encode('utf8')}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Import fertig')", timeout=20000)
    t = toast(page)
    check('0 neue Animationen, 2 vorhandene' in t and len(reqs(page, '/api/anim/put')) == n_put and len(reqs(page, '/api/anim/get')) > n_get, f'Animationen ohne Pruefsumme nicht doppelt angelegt: {t!r}')
    prog = page.evaluate('window.__prog')
    check(any(str(x).startswith('Animation 1 von') for x in prog) and prog[-1] is None and 'Import:' not in page.inner_text('label[for="libImport"]'), f'Importfortschritt im Knopf, danach wieder die Beschriftung {prog} | {page.inner_text("label[for=libImport]")!r}')
    page.evaluate("()=>{for(const x of window.__anim.items)x.crc=RbAnim.crc32(x.payload);}")
    # beschaedigte Animation im Backup: klare Meldung, Rest bleibt
    bad = json.loads(backup_txt); bad['animations'][1]['crc'] = '00000000'
    page.evaluate("()=>{window.__anim.items=[];window.__anim.nextId=70;}"); page.evaluate("animLoad()")
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'b.json', 'mimeType': 'application/json', 'buffer': json.dumps(bad).encode()}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Kurzwahlen übernommen')", timeout=20000)
    t = toast(page)
    check('1 neue Animationen' in t and 'Prüfsumme' in t, f'falsche Prüfsumme wird gemeldet, die erste ist übernommen: {t!r}')
    # altes Schema 2 (ohne Animationen) wird weiter angenommen
    old = json.loads(backup_txt); old['schema'] = 2; old.pop('animations')
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'alt.json', 'mimeType': 'application/json', 'buffer': json.dumps(old).encode()}])
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


    # ---- v0.7.1: Export mit Auswahl -------------------------------------------------------------------------------
    page.evaluate("()=>{const m=window.__mock;m.entries=[{id:1,name:'Hallo',text:'Hallo',line2:'',layout:0,color1:3,color2:3,mode:2,kind:'text'},{id:2,name:'Stand',text:'Stand',line2:'',layout:0,color1:4,color2:4,mode:1,kind:'text'},{id:5,name:'Allein',text:'Allein',line2:'',layout:0,color1:4,color2:4,mode:1,kind:'text'}];m.programs=[{id:1,name:'Prog',count:1,ids:[2],seconds:20,playback:0}];window.__x.shortcuts=Array.from({length:8},()=>({type:0,id:0,label:''}));window.__x.shortcuts[0]={type:1,id:1,label:''};window.__x.shortcuts[1]={type:4,id:window.__anim.items[0].id,label:''};}")
    page.evaluate("async()=>{await refreshLibrary();await v42RefreshPrograms();await animLoad();await v42RefreshShortcuts();}")
    page.evaluate("navigate('settings')"); page.wait_for_timeout(200)
    def export_with(keys):
        n = page.evaluate("window.__blobs.length")
        page.locator('#libExport').click(); page.wait_for_selector('#rbExportDialog .rb-export-opt', timeout=5000)
        for k in ('library', 'programs', 'animations', 'shortcuts'):
            page.locator('#rbExp_' + k).set_checked(k in keys)
        page.locator('#rbExportDialog button.primary').click()
        page.wait_for_function(f"window.__blobs.length>{n}", timeout=15000)
        return json.loads(page.evaluate("window.__blobs.at(-1).text()"))
    bk = export_with({'programs'})
    check([i['id'] for i in bk['items']] == [2] and [c['id'] for c in bk['collections']] == [1] and bk['animations'] == [] and bk['shortcuts'] == [] and bk['scope']['programs'] and not bk['scope']['library'],
          f"nur Programme: der benoetigte Eintrag kommt mit, sonst nichts {[i['id'] for i in bk['items']]}")
    bk = export_with({'shortcuts'})
    aid = page.evaluate("window.__anim.items[0].id")
    check(sorted(i['id'] for i in bk['items']) == [1] and [a['id'] for a in bk['animations']] == [aid] and bk['collections'] == [] and len(bk['shortcuts']) == 8,
          f"nur Kurzwahlen: Ziele (Eintrag 1, Animation {aid}) kommen mit {[i['id'] for i in bk['items']]} {[a['id'] for a in bk['animations']]}")
    bk = export_with({'library'})
    check(sorted(i['id'] for i in bk['items']) == [1, 2, 5] and bk['collections'] == [] and bk['animations'] == [] and bk['shortcuts'] == [], 'nur Bibliothek')
    n = page.evaluate("window.__blobs.length"); page.locator('#libExport').click(); page.wait_for_selector('#rbExportDialog', timeout=5000)
    for k in ('library', 'programs', 'animations', 'shortcuts'): page.locator('#rbExp_' + k).set_checked(False)
    check(page.locator('#rbExportDialog button.primary').is_disabled(), 'nichts gewählt: Exportieren gesperrt')
    page.keyboard.press('Escape'); page.wait_for_timeout(200)
    check(page.locator('#rbExportDialog').count() == 0 and page.evaluate("window.__blobs.length") == n and 'Backup:' not in page.inner_text('#libExport'), 'Escape schließt ohne Export')
    # Import einer Teilsicherung (nur Bibliothek) laeuft durch
    page.evaluate("()=>{const st=document.getElementById('status');st.textContent='';st.hidden=true;}"); page.set_input_files('#libImport', files=[{'name': 'teil.json', 'mimeType': 'application/json', 'buffer': json.dumps(bk).encode()}])
    page.wait_for_function("document.getElementById('status').textContent.includes('Import fertig')", timeout=20000)
    check('0 neue Einträge, 3 vorhandene' in toast(page) and '0 Kurzwahlen' in toast(page), f'Teilsicherung importiert: {toast(page)!r}')

    # ---- v0.7.1: Standardpasswort im Klartext, WLAN-Puffer und Sicherheit -----------------------------------------
    page.evaluate("navigate('home')"); page.evaluate("navigate('settings')"); page.wait_for_timeout(400)
    check(page.inner_text('#rbWifiState .rb-wifi-std') == 'Banane1248!' and page.evaluate("getComputedStyle(document.querySelector('#rbWifiState .rb-wifi-std')).fontWeight") in ('700', '800', '900'),
          'Standardpasswort steht hervorgehoben im Klartext')
    check(page.input_value('#rbWifiBuf') == '1' and page.input_value('#rbWifiSec') == '0' and 'begrenzte Puffer (8 Empfangspuffer)' in page.inner_text('#rbWifiTechState'), 'WLAN-Technik: aktuelle Werte angezeigt')
    page.evaluate("window.__conf=[];window.confirm=m=>{window.__conf.push(m);return false};0")
    page.select_option('#rbWifiBuf', '0'); page.locator('#rbWifiTechSave').click(); page.wait_for_timeout(500)
    r = reqs(page, '/api/wifi/settings')
    check(r and r[-1]['data'] == {'buf': '0'} and any('Neustart' in c for c in page.evaluate('window.__conf')), f'Puffer umstellen ohne sofortigen Neustart {r[-1:]}')
    check('Nach dem nächsten Neustart: Arduino-Standard' in page.inner_text('#rbWifiTechState'), 'Hinweis: wirkt nach dem Neustart')
    page.evaluate("window.__conf=[];window.confirm=m=>{window.__conf.push(m);return true};0")
    page.select_option('#rbWifiSec', '1'); page.locator('#rbWifiTechSave').click(); page.wait_for_timeout(500)
    r = reqs(page, '/api/wifi/settings')
    check(r[-1]['data'].get('sec') == '1' and any('BOOT-Taste' in c for c in page.evaluate('window.__conf')), f'WPA3 einschalten mit Rueckfrage und BOOT-Hinweis {r[-1:]}')
    page.evaluate("window.__x.buf=1;window.__x.sec=0;window.confirm=()=>true;0")

    # ---- v0.7.1: Senden waehrend Programm (D2) ---------------------------------------------------------------------
    page.evaluate("navigate('editor');setTab('scroll')"); page.wait_for_timeout(300)
    page.fill('#scrollText', 'Mitten rein'); page.wait_for_timeout(300)
    page.evaluate("()=>{window.__mock.status={programPlaying:true,state:'idle'};window.__x.progBusy=1;}"); page.wait_for_function("rbProgOn", timeout=8000)
    d = page.evaluate("({prog:rbProgOn,tx:document.documentElement.classList.contains('rb-tx'),dis:document.getElementById('sendScroll').disabled,aria:document.getElementById('sendScroll').getAttribute('aria-disabled')})")
    check(d['prog'] and page.locator('#sendScroll').is_enabled(), f'Programm läuft: Senden bleibt frei {d}')
    n_text = len(reqs(page, '/api/text'))
    page.locator('#sendScroll').click(); page.wait_for_timeout(400)
    check('Programm wird beendet' in toast(page), f'Hinweis, dass das Programm endet {toast(page)!r}')
    page.evaluate("window.__mock.status={state:'idle'}")
    page.wait_for_function(f"window.__mock.requests.filter(r=>r.path==='/api/text').length>={n_text + 2}", timeout=15000)
    t = reqs(page, '/api/text')[-2:]
    check(len(t) == 2 and t[0]['data'] == t[1]['data'], 'derselbe Inhalt wird nach dem Programmende noch einmal gesendet')

    # ---- v0.7.1: Upload-Kennung, Animations-ID sichtbar ------------------------------------------------------------
    page.wait_for_function("!document.documentElement.classList.contains('rb-tx')", timeout=15000)
    page.evaluate("()=>{window.__mock.requests.length=0;}")
    payload_ok = page.evaluate("""async()=>{const fr=[new Uint8Array(1024),new Uint8Array(1024)];fr[0][5]=2;fr[1][9]=3;
      const pl=RbAnim.buildPayload(fr,100);return await animUploadPayload(pl,{name:'Kennung',frames:2,ms:100});}""")
    puts = reqs(page, '/api/anim/put')
    ups = {r['data'].get('up') for r in puts}
    check(payload_ok and puts and len(ups) == 1 and None not in ups and all(len(u) <= 8 for u in ups), f'jedes Stück trägt dieselbe Kennung {ups}')
    page.evaluate("navigate('animations');animShowList('editor')"); page.wait_for_timeout(600)
    rows = page.evaluate("[...document.querySelectorAll('#animList .anim-row small')].map(e=>e.textContent)")
    check(rows and not any('ID' in r for r in rows), f'keine ID in der Zeile (0.7.2) {rows[:2]}')

    # ---- v0.7.1: Design-Tokens -----------------------------------------------------------------------------------
    st = page.evaluate("""()=>{const r=getComputedStyle(document.documentElement),i=document.createElement('input');i.type='text';document.body.append(i);
      const b=getComputedStyle(i).borderTopColor;i.remove();return {border:b,send:r.getPropertyValue('--rb-send').trim(),on:r.getPropertyValue('--rb-on').trim(),acc:r.getPropertyValue('--rb-accent').trim()};}""")
    check(st['border'] == 'rgb(102, 116, 138)', f"Eingaberand #66748a {st['border']}")
    check(st['send'] == '#3ddc97' and st['on'] in ('#3ddc97', 'var(--rb-send)'), f"ein Grünton für Senden und „auf der Tafel“ {st}")
    css = html[html.index('<style>'):html.index('</style>')]
    for old in ('#ffd35c', '#ffcf52', '#ffcc50', '#4fd37a', '#111820', '#121820'):
        check(old not in css.lower(), f'Fast-Duplikat {old} entfernt')

    # ---- v0.7.1: Kurzwahl ohne Erfolgsmeldung, Palette, Programm-Maske, Kurzwahl-Fenster ------------------------------
    page.evaluate("navigate('home')"); page.wait_for_timeout(300)
    page.evaluate("()=>{window.__toasts=[];const n=window.notify;window.notify=(m)=>{window.__toasts.push(String(m));return n?n(m):undefined;};v42Shortcuts[0]={type:1,id:1,label:'Test'};}")
    n0 = len(reqs(page, '/api/shortcuts/run'))
    page.evaluate("document.querySelector('.shortcut[data-shortcut=\"1\"]').click()"); page.wait_for_timeout(500)
    check(len(reqs(page, '/api/shortcuts/run')) == n0 + 1, 'Kurzwahl ruft /api/shortcuts/run auf')
    check(page.evaluate('window.__toasts').__len__() == 0, f'keine Erfolgsmeldung beim Antippen {page.evaluate("window.__toasts")}')
    page.evaluate("navigate('editor');setTab('scroll')"); page.wait_for_timeout(300)
    page.evaluate("()=>{const s=document.getElementById('scrollLayout');s.value='1';s.dispatchEvent(new Event('change'));}"); page.wait_for_timeout(400)
    xs = page.evaluate("()=>{const a=[...document.querySelectorAll('#scrollColors .swatch')].map(e=>Math.round(e.getBoundingClientRect().left)),b=[...document.querySelectorAll('#scrollColors2 .swatch')].map(e=>Math.round(e.getBoundingClientRect().left));return {a,b};}")
    check(len(xs['b']) >= 7 and xs['a'][:len(xs['b'])] == xs['b'], f'Farbpunkte beider Zeilen stehen untereinander {xs}')
    page.evaluate("navigate('programs')"); page.wait_for_timeout(300)
    page.evaluate("v43ProgShowEdit(true)"); page.wait_for_timeout(200)
    check(page.evaluate("getComputedStyle(document.querySelector('.rb-dock')).display") == 'none', 'Programm-Maske ohne unteres Bedienfeld')
    page.evaluate("v43ProgShowEdit(false)"); page.wait_for_timeout(200)
    check(page.evaluate("getComputedStyle(document.querySelector('.rb-dock')).display") != 'none', 'Bedienfeld kommt in der Programmliste zurück')
    page.evaluate("navigate('home')"); page.wait_for_timeout(300)
    page.evaluate("()=>{const b=document.querySelector('.shortcut[data-shortcut=\"2\"]');b.focus();window.__opener=b;document.getElementById('v42ShortcutDialog').classList.remove('hidden');}"); page.wait_for_timeout(200)
    inside = page.evaluate("document.getElementById('v42ShortcutDialog').contains(document.activeElement)")
    check(inside, 'Fokus liegt nach dem Öffnen im Kurzwahl-Fenster')
    page.keyboard.press('Escape'); page.wait_for_timeout(200)
    check(page.evaluate("document.getElementById('v42ShortcutDialog').classList.contains('hidden')") and page.evaluate('document.activeElement===window.__opener'), 'Escape schließt das Kurzwahl-Fenster, Fokus kehrt zurück')

    # ---- v0.7.2: Überschrift Ambiente, Arbeitsanzeige am Backup, Hinweis aus der Programm-Maske ---------------------
    def h2pos(view):
        page.evaluate(f"navigate('{view}')"); page.wait_for_timeout(350)
        return page.evaluate("(v)=>{const h=document.getElementById('view-'+v).querySelector('h2').getBoundingClientRect();return [Math.round(h.x),Math.round(h.y)];}", view)
    for w, hh in ((390, 844), (1280, 860)):
        page.set_viewport_size({'width': w, 'height': hh}); page.wait_for_timeout(300)
        pl, pp, pa = h2pos('library'), h2pos('programs'), h2pos('ambience')
        # Am Laptop sitzt die Bibliothek wegen der Vorschau-Spalte weiter links; Ambiente richtet sich nach Programme und Animationen
        check(pa == pp and (pa == pl or w > 600), f'Überschrift Ambiente sitzt wie Bibliothek und Programme bei {w} px: {pl} {pp} {pa}')
    page.set_viewport_size({'width': 390, 'height': 844}); page.wait_for_timeout(300)
    check('Blocktexte sind bei Tempo 60' not in html and not page.evaluate("document.body.innerText.includes('bei Tempo 60–90 kalibriert')"), 'Kalibrierhinweis steht nicht mehr in der Programm-Maske')
    page.evaluate("navigate('settings')"); page.wait_for_timeout(300)
    for sel in ('#libExport', 'label[for=libImport]'):
        st = page.evaluate("(s)=>{const e=document.querySelector(s);e.classList.add('rb-working');const a=getComputedStyle(e,'::after'),c=getComputedStyle(e);const r={bar:a.animationName,bg:c.backgroundColor,pos:c.position};e.classList.remove('rb-working');return r;}", sel)
        check(st['bar'] == 'rbWorkBar' and st['bg'] != 'rgb(255, 212, 92)' and st['pos'] == 'relative', f'{sel}: Arbeitsanzeige (Laufbalken, Knopf nicht gelb) {st}')
        st2 = page.evaluate("(s)=>getComputedStyle(document.querySelector(s),'::after').animationName", sel)
        check(st2 != 'rbWorkBar', f'{sel}: ohne Arbeit keine Anzeige {st2}')
    page.evaluate("()=>{window.__bkSeen=null;const old=window.v42Backup;window.v42Backup=async(cb,sel)=>{window.__bkSeen=document.getElementById('libExport').classList.contains('rb-working');return old(cb,sel);};}")
    n = page.evaluate("window.__blobs.length"); page.locator('#libExport').click(); page.wait_for_selector('#rbExportDialog .rb-export-opt', timeout=5000)
    page.locator('#rbExportDialog button.primary').click(); page.wait_for_function(f"window.__blobs.length>{n}", timeout=15000); page.wait_for_timeout(300)
    check(page.evaluate('window.__bkSeen') is True, 'Export: Arbeitsanzeige ist aktiv, während das Backup entsteht')
    check(not page.evaluate("document.getElementById('libExport').classList.contains('rb-working')") and not page.evaluate("document.querySelector('label[for=libImport]').classList.contains('rb-working')"), 'Export: Arbeitsanzeige danach weg')

    check(not [e for e in errors if not e.startswith('console:')], f'keine Skriptfehler {errors[:3]}')
    browser.close()

print('FAILS:', len(errors))
if not errors:
    print('PASS Browser 0.6.1.11/0.7.2: Export mit Auswahl, WLAN-Klartext und -Technik, Senden während Programm, Upload-Kennung, ID, Tokens; Backup mit Animationen (Export/Import/Wiederverwendung/Kurzwahl 4/Prüfsumme/Schema 2), WLAN-Passwort, Blocktext über library/send, Seite duplizieren dahinter, zusammengefasste Abrufe, Live-Wert nachgeholt, Standbild bleibt, Seitenstart ohne Doppelabrufe')
sys.exit(1 if errors else 0)
