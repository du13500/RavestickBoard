from pathlib import Path
from bs4 import BeautifulSoup
import re,subprocess,gzip,hashlib,sys
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
h=(root/'web/index.html').read_text()
ino=(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v0_6_1_7.ino').read_text()
header=(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_WebUI.h').read_text()
assert 'FW_VERSION[] = "0.6.1.7-dev"' in ino
assert 'out.reserve(11000)' not in ino and 'json.reserve(5000)' not in ino
# --- v0.4.3.3: RAM-Experiment (Messung + Versuchsschalter) ---
assert ino.count('= ESP.getSketchSize();')==1 and ino.count('ESP.getSketchSize();')==1   # Aufruf nur einmal, in setup()
assert 'sketchSizeCached = ESP.getSketchSize();' in ino
assert ino.count('BLEDevice::init("")')==1 and 'static bool bleEnsureInit()' in ino
assert '#define RB_AP_MAX_CLIENTS 2' in ino and '#define RB_LAZY_BLE_INIT 0' in ino   # ab 0.4.5.0: höchstens zwei WLAN-Geräte
# --- v0.4.5.1: Vor-Scan, Status, Systemmin-Zuordnung ---
assert '#define RB_PRESCAN 1' in ino and '#define RB_PRESCAN_S 3' in ino and '#include <strings.h>' in ino
assert ino.count('bleScanForSign()')==2                     # Definition + ein Aufruf (nur vor NEUEM Verbindungsaufbau)
assert 'if (!reused && bleScanForSign() == 0)' in ino       # nur "nicht gesehen" bricht ab; "ohne Aussage" (-1) verbindet wie bisher
assert 'scan->start(RB_PRESCAN_S);' in ino and 'scan->start(RB_PRESCAN_S, false)' not in ino   # kein Ueberladungs-Risiko
assert ino.index('bleScanForSign() == 0') < ino.index('++diagnostics.bleAttempts;')   # Fehlscans zaehlen nicht als Verbindungsversuche
assert ino.index('rbPhase("ble_scan");') < ino.index('scan->start(RB_PRESCAN_S);')
assert '\\"bleLink\\":%s,\\"bleLast\\":%u' in ino and 'BLE Vor-Scans:' in ino and 'zuletzt beendete Anfrage:' in ino
assert 'id="rbBle"' in h and "'bluetooth-searching'" in h and "'bluetooth-off'" in h and "'bluetooth-connected'" in h
assert 'WiFi.softAP(WIFI_SSID, WIFI_PASSWORD, 1, 0, RB_AP_MAX_CLIENTS)' in ino
assert 'WiFi.onEvent(wifiEventMark);' in ino and ino.count('wifiEventDrain();')==1
for lbl in ['"Start"','"Nach Sketch-Groesse"','"Nach BLE-Init"','"Nach NVS-Seiten"','"Nach LittleFS-Bibliothek"','"Nach Programmen"','"Nach WLAN-AP"']:
    assert 'bootRamMark('+lbl+')' in ino or lbl in ino, lbl
assert 'START-AUFTEILUNG' in ino and 'WLAN-EREIGNISSE' in ino
assert 'if (!bleEnsureInit())' in ino   # BLE-Auftrag stellt BLE bei Bedarf sicher
assert '0.4.3.2-dev' not in h and '0.4.3.2-dev' not in ino
# --- v0.4.4.0: Abmelden vor Waechter-Neustart und Test-Ausloeser ---
assert '#include <esp_wifi.h>' in ino
assert '#define RB_DEAUTH_BEFORE_RESTART 1' in ino and '#define RB_TEST_HANG 1' in ino
assert ino.count('esp_wifi_deauth_sta(0);')==1                      # alle Geraete (aid 0)
assert ino.index('esp_wifi_deauth_sta(0);')<ino.index('      abort();')   # erst abmelden, dann abort
assert ino.index('rbCrumb.magic = RB_CRUMB_MAGIC;\n#if RB_DEAUTH_BEFORE_RESTART')>0   # Spur steht vor dem Abmelden
assert 'httpRoute("/api/test/hang", HTTP_GET, onTestHang);' in ino
assert ino.count('for (;;) delay(100);')==1 and 'rbPhase("test_hang");' in ino
assert 'web.arg("deauth") != "0"' in ino
assert 'Geraete vorher abgemeldet' in ino and 'Geraete NICHT abgemeldet' in ino
assert 'Abmelden vor Waechter-Neustart' in ino and '\\"hangDeauth\\"' in ino
assert 'static char rbPrevText[200]' in ino
assert '/api/test/hang' not in h                                      # kein Knopf in der Oberflaeche
# --- v0.4.4.0: Farbe und Schrift pro Zeichen (Stilmarken U+0090..U+009C) ---
v042=(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v042.h').read_text()
assert ino.index('struct TextStyle {')<ino.index('bool runJob(Job job')          # Struktur vor dem ersten Funktionsprototyp (Arduino-sicher)
assert 'static inline bool styleApply(TextStyle &st, uint32_t cp)' in ino and 'static const uint8_t RB_STYLE_FONT_LAYOUT[4] = {3, 4, 0, 2};' in ino
assert ino.count('if (styleApply(st, raw)) continue;')==3                          # measureText, drawInlineUtf8, drawInlineUtf8Window
assert ino.count('drawToken(cp, st.layout,')==2 and 'static void drawToken(' in ino # gemeinsamer Maler, keine drei Kopien mehr
assert 'if (cp >= 0x90 && cp <= 0x9C) continue;' in ino                             # Blockseiten ignorieren Marken
assert 'st.layout == layout ? top : styleTop(st.layout)' in ino                     # ohne Schriftmarke bleibt die Oberkante des Aufrufers
assert 'if (st.baseLayout != 1) st.layout = RB_STYLE_FONT_LAYOUT[cp - 0x98];' in ino   # Zweizeilig Mini: Schriftmarken ignoriert
assert 'xC2\\x90\\xC2\\x9C' in v042                                                    # Programmgruppen: Stil an der Nahtstelle zuruecksetzen
for ident in ['rbz','rbzMatrix','rbzGrids','rbzCount','rbzChips','rbzFlowApply','rbzSend','rbzDone','rbzUndo','rbzRedo','rbUndo','rbRedo']:
    assert h.count('id="'+ident+'"')==1,ident
for gone in ['rbStyleUndo','rbzFont"','rbzCycleFont','rbUndoSnap']:
    assert gone not in h,gone
for fn in ['function rbSync(','function rbEncode(','function rbDecode(','function rbDrawStyled(','function rbzOpen(','function rbGlobalColor(','function rbGlobalFontReset(']:
    assert h.count(fn)==1,fn
assert "text:rbEncode('a'),line2:layout===1?rbEncode('b'):''" in h                    # Senden codiert
assert "text:rbEncode('a'),line2:layout===1?rbEncode('b'):'',layout,color1:scrollColor" in h   # Bibliothek speichert codiert
assert 'rbDecode(data.text' in h and 'rbPlain(item.text)' in h
assert h.count('#sendScroll,#libSend,#v42SendDraftBand,#v42RunProgram,#pageShow,#rbzSend,#animSend,#animSaveSend,#animSendOnly{background:var(--rb-send)!important')==1
assert '--rb-send:#3ddc97' in h
# --- v0.4.5.0: Programm-Reihenfolge, Eingabefeld, Verlauf, Startbildschirm ---
assert 'rb44ProgramOrder' in v042 and 'v044MoveCollection' in v042
assert 'httpRoute("/api/collections/move", HTTP_POST, v044MoveCollection);' in ino
assert 'RB44_PROGRAM_ORDER_FILE = "/rb-lib/porder.bin"' in v042
assert v042.index('uint8_t rb44ProgramOrder(')<v042.index('void v042ListCollections()')<v042.index('void v044MoveCollection()')
assert "rbQueueMove('/api/collections/move',id,to" in h and "rbQueueMove('/api/library/move',id,to" in h
assert 'async function rbLoadLists()' in h and "setTimeout(rbLoadLists,150)" in h and 'rbFresh' in h and 'document.hidden||(rbBusy>0' in h
assert '<textarea' in h and h.count('class="rb-ta"')==2 and h.count('class="rb-grip"')==2    # nur Lauftext, Zeile 1 und 2
assert ".rb-dock-modes .v43-force-btn:not([data-mode='scroll']):not([data-mode='static']){display:none}" in h   # v0.4.5.0: Startbildschirm reduziert
assert h.index('id="homePowerOn"')<h.index('id="homePowerOff"')
assert "body[data-rb-view='ambience'] .rb-dock-modes{display:none}" in h
assert 'const RB_HIST_MAX=60' in h and 'function rbRedo()' in h and 'function rbWireFields()' in h
assert 'erase:rbz.sel[' in h                                                                  # Wischen-Entmarkieren
# --- v0.4.3.3: Hang-Waechter und Absturzspur ---
assert '#define RB_HANG_RESTART_MS 25000UL' in ino
assert 'RTC_NOINIT_ATTR RbCrumb rbCrumb;' in ino and 'rbCrumbBoot();' in ino
assert 'if (beat && gap > RB_HANG_RESTART_MS)' in ino and 'abort();' in ino
assert ino.count('rbBeat = millis();')==1                       # Lebenszeichen in loop()
for ph in ['"tx_write"','"tx_wait_notify"','"ble_connect"','"ble_getService"','"ble_regNotify"','"ble_getMTU"','"ble_disconnect"','"web_handler"','"idle"']:
    assert 'rbPhase('+ph in ino or ph in ino, ph
assert ino.count('rbPhase("ble_regNotify");')==2
assert 'rbPhase(ramStageLabel(stage));' in ino                   # alle RAM-Marken setzen auch die Phase
assert 'Absturzspur Vorlauf' in ino and '\\"prevRun\\"' in ino and '[VORLAUF]' in ino
# Reihenfolge: Spur-Definitionen stehen vor erster Nutzung
assert ino.index('static void rbPhase(')<ino.index('void ramTraceMark(')<ino.index('static void httpSampleTimer(')
assert 'diagnosticReportStream();' in ino and 'RbDiagnosticStream json;' in ino
assert 'httpLargestMinDrop' in ino and 'httpLowestUnattributedSystemMin' in ino
assert 'Promise.all([fetch(\'/api/diagnostics' not in h
assert h.count('refreshDiagnostics();')==1, h.count('refreshDiagnostics();')
assert h.count('fetch(\'/api/diagnostics.txt\'')==1
assert 'v42NewBlock:\'flame-kindling\'' in h
assert 'let reportCache' in h
assert 'grid-template-columns:minmax(0,1fr);grid-template-rows:repeat(7,' in h
s=BeautifulSoup(h,'html.parser')
assert set(b.get_text(' ',strip=True) for b in s.select('#view-ambience .ambience-colors button'))==set()  # dynamic
assert [b.get('id') for b in s.select('#pageShow,#v42SendDraftBand,#v42SaveBlock')]==['pageShow','v42SendDraftBand','v42SaveBlock']
assert len(s.select_one('#pageShow').parent.find_all('button',recursive=False))==4
assert s.select_one('#libRename')['data-rb-icon']=='text-cursor-input'
assert s.select_one('#v42NewBlock')['data-rb-icon']=='flame-kindling'
for v in ['0.4.3-dev','0.4.2.5.1-dev']:
 assert v not in h
# gzip: reconstruct compressed payload and compare exact bytes with HTML input
array=header.split('PAGE_HTML_GZIP[] PROGMEM = {',1)[1].split('};',1)[0]
gz=bytes(int(c,16) for c in re.findall(r'0x[0-9a-f]{2}',array))
raw=gzip.decompress(gz);assert raw==('\n'+h.rstrip('\n')+'\n').encode('utf-8')
assert hashlib.sha256(raw).hexdigest()[:24] in header
js='\n'.join(tag.get_text() for tag in s.select('script:not([src])'))
js_tmp=Path('/tmp/rb0450_script.js'); js_tmp.write_text(js)
subprocess.run(['node','--check',str(js_tmp)],check=True)
mock='''<script>
window.__req=[];
window.fetch=async(p,opt={})=>{p=String(p).split('?')[0];__req.push(p);
let r={ok:true};
if(p==='/api/font')r={ok:true};
if(p==='/api/program')r={ok:true,pages:[{line1:'',line2:'',layout:3,align:1,color1:6,color2:7,duration:7}],current:0};
if(p==='/api/library')r={ready:true,items:[],shortcuts:[],used:0,total:100000};
if(p==='/api/collections')r={ok:true,items:[]};
if(p==='/api/shortcuts')r={ok:true,items:Array.from({length:8},()=>({type:0,id:0,label:''}))};
if(p==='/api/status')r={state:'idle',message:'Bereit',brightness:80,speed:80,powerKnown:true,powerOn:true};
if(p==='/api/diagnostics')r={version:'0.6.1.1-dev',uptime:'1 min',reset:'USB',freeHeap:42000,minHeap:30000,maxBlock:25000,appAvailable:500000,wifiClients:1,bleSuccess:0,errors:0,jobsOK:0,jobsFailed:0,pageShows:0,recent:'Ein Ereignis',lastError:'Keiner'};
return {ok:true,status:200,json:async()=>r,text:async()=>p===' /api/diagnostics.txt'?'Bericht':'Bericht'};
};</script>'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for size in [(390,844),(375,667),(430,932)]:
  context=browser.new_context(viewport={'width':size[0],'height':size[1]},is_mobile=True,has_touch=True)
  page=context.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  page.set_content(h.replace('<script>',mock+'<script>',1),wait_until='domcontentloaded')
  page.wait_for_function('!document.documentElement.classList.contains("rb-booting")',timeout=15000)
  # Ambience view: 7 buttons in one column
  page.evaluate("navigate('ambience')")
  names=page.locator('#ambienceColors button').all_text_contents()
  assert names==['Rot','Gelb','Grün','Cyan','Blau','Magenta','Weiß'],names
  rects=[page.locator('#ambienceColors button').nth(i).bounding_box() for i in range(7)]
  assert all(abs(rects[i]['x']-rects[0]['x'])<2 for i in range(7)),rects
  assert all(rects[i+1]['y']>rects[i]['y']+rects[i]['height']-1 for i in range(6)),rects
  # test unique diagnostics JSON only once on navigation
  page.evaluate("navigate('diagnostics')")
  page.wait_for_timeout(200)
  paths=page.evaluate('__req');assert paths.count('/api/diagnostics')==1,paths
  assert '/api/diagnostics.txt' not in paths,paths
  page.locator('#diagReload').click();page.wait_for_timeout(100)
  assert page.evaluate("__req.filter(x=>x==='/api/diagnostics').length")==2
  # block controls disabled single page, after adding page changed
  page.evaluate("navigate('editor');setTab('pages')")
  assert page.locator('#pageDelete').is_disabled()
  assert page.locator('#v42NewBlock').is_disabled()
  assert page.locator('#pageDelete').get_attribute('data-rb-icon')=='trash-off'
  page.evaluate("pages.push(samplePage());renderSelected()")
  assert page.locator('#pageDelete').is_enabled()
  assert page.locator('#v42NewBlock').is_enabled()
  assert page.locator('#v42NewBlock').get_attribute('data-rb-icon')=='flame-kindling'
  assert len(page.locator('#pageShow').locator('xpath=..').locator('button').all())==4
  assert not errors,errors
  if size==(390,844):
   page.screenshot(path='/tmp/RavestickBoard_v0.4.5.0_Browser_Test.png',full_page=True)
  context.close()
 browser.close()

# v0.4.6.0: Verträge für Blockseiten mit Zeichenstilen und Bluetooth-Übertragungszeichen
_ino=next((root/'firmware').glob('RavestickBoard_v0_6_1_7/*.ino')).read_text(encoding='utf8')
_h=next((root/'firmware').glob('RavestickBoard_v0_6_1_7/RavestickBoard_v042.h')).read_text(encoding='utf8')
_web=(root/'web/index.html').read_text(encoding='utf8')
for need in ['rbLineHasMarks','rbPageLineWidth','rbPageLineChars','rbPageDrawLine']:
    assert need in _ino,need
assert 'rbPageLineWidth' in _h and 'rbPageDrawLine' in _h,'Kachel-Renderer der Seiten nutzt die Stilmarken nicht'
for need in ['RBSX','rbPageLoad','rbPageStore','rbzOpenPage','rbPageBaseColor','rbBleJobStart','RB_BLE_LINK_AFTER_MS','rbPageLinePx']:
    assert need in _web,need
assert "r.status===202){rbBleJobStart();" in _web,'202 startet die Übertragungsanzeige nicht'
assert "xfer:['bluetooth-connected'" in _web

# v0.5.0.0: Tafelverwaltung – keine Adresse mehr im Code, Speicher im NVS, Routen, Status
_addr='ff:00:'+'00:03'   # Adresse der Entwicklungstafel darf nirgends mehr im Code stehen
assert 'SIGN_ADDRESS' not in _ino and _addr not in _ino and _addr not in _web and _addr not in _h, 'Tafeladresse steht noch im Code'
assert 'FW_VERSION[] = "0.6.1.7-dev"' in _ino
for need in ['struct SignRef','signLoad();','p.begin("rbsign", false)','/api/sign/scan','/api/sign/save','/api/sign/use','/api/sign/back','\\"signKind\\":%u','Keine Tafel eingerichtet','RB_SIGN_SCAN_S']:
    assert need in _ino,need
assert _ino.index('struct SignRef')<_ino.index('uint8_t pendingLayout'),'SignRef muss vor den automatischen Prototypen stehen'
assert _ino.count('BLEAddress address{String(signActive.addr)};')==1 and 'strcasecmp(dev.getAddress().toString().c_str(), signActive.addr)' in _ino
assert 'rbSignChip' not in _web and 'rb-sign-chip' not in _web,'Kopfzeilen-Chip ist entfallen'
for need in ['rbSignLoad','rbSignScan','rbSignQuality',"'signal-zero'","'antenna'",'user-scalable=no','gesturestart']:
    assert need in _web,need
# --- v0.6.0.0: Animationstest (Opcode 0x04) und Antwortcodes ---
assert 'enum Job : uint8_t { NONE, TEXT, BRIGHTNESS, PAGE, SPEED, MODE, POWER, AMBIENCE, BAND, ANIM };' in ino
assert 'static constexpr uint8_t  RB_ANIM_OPCODE = 0x04;' in ino and 'static constexpr uint8_t  ANIM_MAX_FRAMES = 79;' in ino
assert 'raw[p++] = rb60AnimActive ? RB_ANIM_OPCODE : 0x02;' in ino
assert 'void copyPayloadSlice(size_t offset, size_t length, uint8_t *dest) {\n  if (rb60AnimActive) { rb60CopyAnimSlice(offset, length, dest); return; }' in ino
assert 'rb60AnimActive = false;' in ino[ino.index('struct RenderBufferCleanup'):ino.index('struct RenderBufferCleanup')+700]   # Aufraeumen auf jedem Weg
assert ino.index('static size_t rb60PrepareAnim')<ino.index('size_t makeChunk(')            # Block steht vor seinen Nutzern
assert 'httpRoute("/api/anim/test", HTTP_POST, queueAnimTest);' in ino
assert ino.count('void queueAnimTest()')==1 and ino.count('if (!reserveJob()) return;')>=4
q=ino[ino.index('void queueAnimTest()'):ino.index('// ---- v0.4.5.1: Vor-Scan')]
assert 'autoProgram = false; rb42ProgramPlaying = false;' in q and 'nextJob = ANIM;' in q and 'ms > 2000' in q and 'n > maxFrames' in q
assert 'maxFrames = pattern == ANIM_LIMIT ? ANIM_TEST_OVER_LIMIT : ANIM_MAX_FRAMES' in q       # 80 Frames nur im Grenztest
r=ino[ino.index('bool runJob('):ino.index('static void onHomePage()')]
assert 'job != ANIM && !sendSimple(c, 0x06, actualMode)' in r and 'if (job != ANIM && (job == BAND ||' in r   # kein Modus/Tempo VOR der Animation
assert '(job == TEXT || job == BAND || job == BRIGHTNESS || job == AMBIENCE) && !sendSimple(c, 0x08' in r  # Helligkeit bleibt unveraendert
assert r.index('ramTraceMark(RT_TX_END')<r.index('job == ANIM && mode != 0x00 && !sendSimple(c, 0x06, mode)')   # Modus erst NACH dem Upload
assert 'rb60AckStrict = (job == ANIM);' in r and 'job == ANIM && rb60LastAck == 0x06' in r and 'attempt < (job == ANIM ? 3 : 1)' in r
assert 'if (!ok && (job==TEXT || job==BAND || job==PAGE || job==AMBIENCE) &&' in ino   # kein automatischer Wiederholungsversuch fuer ANIM
sp=ino[ino.index('bool sendPacket('):ino.index('bool sendSimple(')]
assert 'if (rb60AckStrict) return false;' in sp and 'ackStatus != 0' in sp and sp.index('rb60ParseAck')<sp.index('rbTxDelay(60, "tx_after_ack");')
assert 'static int rb60ParseAck(' in ino and 'ackNak' in ino and '\\"ackOk\\"' in ino and 'Antwortcodes der Tafel:' in ino
on=ino[ino.index('void onNotify('):ino.index('bool sendPacket(')]
assert on.index('rb60AckLength = (uint8_t)length;')<on.index('++notifyCount;')      # erst kopieren, dann zaehlen
for need in ['id="rbAnimTestSection"','data-anim="colors"','data-anim="bar" data-n="16"','data-anim="limit" data-n="79"','data-anim="limit" data-n="80"','id="rbAnimMs"',"api('/api/anim/test'"]:
    assert need in h,need
assert 'id="rbAnimMode"' not in h, 'Anzeigemodus-Auswahl ist ab 0.6.0.2/0.6.1.0 entfallen'
# --- v0.6.1.0: Animationen als eigener Bereich (Dateien in LittleFS, Import im Browser) ---
anim_h=(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_Anim.h').read_text(encoding='utf-8')
assert ino.index('#include "RavestickBoard_Library.h"')<ino.index('#include "RavestickBoard_v042.h"')<ino.index('#include "RavestickBoard_Anim.h"')   # Anim.h braucht rb42ProgramPlaying aus v042.h (Compile-Fehler 0.6.1.0)
assert ino.index('rb61AnimBegin();')>ino.index('libraryBegin();')
for rt in ['list','get','put','send','rename','delete','move']:
    assert f'httpRoute("/api/anim/{rt}",' in ino or f'httpRouteGuarded("/api/anim/{rt}",' in ino, rt   # list seit 0.6.1.5 mit Heap-Schutz
assert 'ANIM_FILE = 4' in ino and 'rb61PendingAnimId' in ino and '\\"animActive\\":%s' in ino and 'rb61LastKind = 2' in ino
assert 'static_assert(sizeof(Rb61AnimHeader) == RB61_META_BYTES' in anim_h and 'RB61_META_BYTES = 448' in ino
for need in ['RB61_MAX_ANIMS','RB61_FREE_RESERVE','rb61B64Decode','rb61CleanName','rb61PrepareAnimFile','rb61AnimBegin']:
    assert need in anim_h, need
assert '.tmp' in anim_h and 'rename(' in anim_h          # Hochladen: temporaere Datei, dann umbenennen
assert 'rbAnimMode' not in h and 'view-animations' in h and "'image-play'" in h and "'film'" not in h and 'data-rb-icon="image-play"' in h and 'rbAnimActive' in h
for need in ['RbAnim','animImp','Auf 79 Bilder verteilen','animRasterText']:
    assert need in h, need
assert 'rb61Reply' in anim_h

# --- v0.6.1.2: Ausschnitt-Rahmen, Nur senden (temporaere Datei), Kurzwahl Typ 4, Senden mint, kein Duplizieren in der Oberflaeche ---
for need in ['id="animCrop"','id="animSendOnly"','id="animCropSmaller"','id="animCropBigger"','cropFor','cropRect','clampCrop',"animSaveImport('sendOnly')","temp:'1'",'animLoad','Animation fehlt']:
    assert need in h, need
for gone in ['id="animOffsets"','id="animOx"','id="animOy"','id="animDuplicate"','/api/anim/duplicate','Animationen folgen später','Animationen (zukünftig)']:
    assert gone not in h, gone
assert '#animSend,#animSaveSend,#animSendOnly{background:var(--rb-send)!important' in h      # Senden-Knoepfe mint wie in der Bibliothek
assert 'touch-action:none' in h and 'pointerdown' in h and 'setPointerCapture' in h
assert 'RB61_TEMP_ID = 60000' in anim_h and 'RB61_TEMP_PATH' in anim_h and 'void rb61DropTemp()' in anim_h
assert 'bool rb61AnimExists(uint32_t id)' in anim_h and 'bool rb61QueueAnim(uint32_t id)' in anim_h
assert ino.index('void rb61DropTemp();')<ino.index('rb61DropTemp();',ino.index('void rb61DropTemp();')+10)          # Vorwaertsdeklaration vor erster Verwendung
v42_h=(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v042.h').read_text(encoding='utf-8')
assert 'rb61AnimExists' in v42_h and 'rb61QueueAnim' in v42_h and 'type>4' in v42_h.replace(' ','') or 'type > 4' in v42_h
assert 'bool rb61AnimExists(uint32_t id);' in ino and 'bool rb61QueueAnim(uint32_t id);' in ino
for need in ['id="animEdit"','id="animSaveCopy"','id="animSourcePick"','id="animPixelOpts"','animEditOpen','animImp.stored',"replace:String(replaceId)","animSaveImport('copy')"]:
    assert need in h, need
assert 'uint16_t replaceId' in anim_h and 'web.arg("replace")' in anim_h and 'Animation ersetzt, ID=' in anim_h
assert anim_h.index('bool rb61AnimExists(uint32_t id);')<anim_h.index('web.arg("replace")')                  # Vorwaertsdeklaration vor der ersten Verwendung
print('PASS: 0.6.1.2 (Ausschnitt-Rahmen, Nur senden, Kurzwahl Animationen, mint, Icon image-play).')

# --- v0.6.1.3: Aufraeum-Build nach dem Code-Review (CRC, Lesefehler, Ersetzen, Stapel); die Kurzwahl-Regel beim Loeschen wurde in 0.6.1.4 geaendert ---
assert 'httpRoute("/api/anim/duplicate"' not in ino and 'onAnimDuplicate' not in anim_h, 'Duplizieren ist entfernt (N6)'
assert 'uint8_t crc[4];' in anim_h and 'RB61_FLAG_CRC' in anim_h and 'rb61FileCrc' in anim_h and 'rb61Crc32Update' in anim_h
assert 'crc:String(RbAnim.crc32(payload))' in h and 'function crc32(' in h
fin=anim_h[anim_h.index('// Abschluss: Nutzlastkopf'):anim_h.index('// POST /api/anim/rename')]
assert fin.index('rb61FileCrc')<fin.index('LittleFS.rename(RB61_TMP')     # Pruefsumme vor dem Umbenennen der fertigen Datei
pp=anim_h[anim_h.index('static size_t rb61PrepareAnimFile'):]
assert 'rb61FileCrc(rb61AnimFile' in pp and pp.index('rb61FileCrc')<pp.index('rb60AnimActive = true;') and 'rb61ReadFailed = false;' in pp   # geprueft, bevor irgendetwas gesendet wird
# M1: Lesefehler -> Abbruch statt Nullen
assert 'rb61AnimFile.read(dest, length) == (int)length)) rb61ReadFailed = true;' in ino
_pre=r.index('if (job == ANIM && rb61ReadFailed) {')                                   # nach der MTU-Vorabpruefung ...
assert r.index('Bluetooth-MTU zu klein für die Textpakete')<_pre<r.index('rawBrightness'), 'Lesefehler in der Vorabpruefung'
_loop=r.index('const size_t rawN = makeChunk(i, payloadLen, raw);')                   # ... und in der Sendeschleife, vor dem Rahmen
assert r.index('rb61ReadFailed',_loop)<r.index('framePacket(raw, rawN, frame)',_loop), 'Lesefehler in der Sendeschleife vor dem Senden'
# M3: Ersetzen ueber .bak, Wiederherstellung beim Start
rp=anim_h[anim_h.index('if (rb61Up.replaceId) {'):anim_h.index('const uint32_t id = rb61NewId();')]
assert '".bak"' in rp and rp.index('LittleFS.rename(target, bak)')<rp.index('LittleFS.rename(RB61_TMP, target)',rp.index('LittleFS.rename(target, bak)')) and 'LittleFS.remove(rb61Path(' not in rp
assert 'rb61RecoverBackups();' in anim_h[anim_h.index('static void rb61AnimBegin()'):anim_h.index('void rb61DropTemp()')]
# N1: Reste vor der Platzpruefung entfernen
_np=anim_h[anim_h.index('const long replaceArg'):anim_h.index('File f = LittleFS.open(RB61_TMP, "w");')]
assert _np.index('LittleFS.remove(RB61_TMP)')<_np.index('rb61FreeFor(')
# N10 + M5
assert '"Animation startet"' in ino
assert 'uxTaskGetStackHighWaterMark(nullptr)' in ino and '\\"minStack\\"' in ino and 'Kleinster freier Stapel' in ino and 'Stapel min=' in ino
assert 'v0.4.2.4.1' not in v42_h[:300] and 'v0.4.2.1-dev' not in (root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_Library.h').read_text(encoding='utf-8')[:200]
print('PASS: 0.6.1.3 (CRC-32, Lesefehler-Abbruch, Ersetzen ueber .bak, Reste vor Platzpruefung, Stapelanzeige).')
# --- v0.6.1.4: Abruf in Teilen mit Heap-Schutz, kleinste freie ID, Loeschen ohne Kurzwahl-Eingriff, gesperrte Anzeige-Tasten ---
assert 'rb61DetachShortcuts' not in anim_h and 'next.types[i] == 4' not in anim_h, 'Loeschen leert keine Kurzwahlen mehr (ADR-2026-11-04-J)'
_dl=anim_h[anim_h.index('void onAnimDelete()'):anim_h.index('bool rb61AnimExists(uint32_t id) {')]
assert 'LittleFS.remove(path)' in _dl and 'rb42Write' not in _dl and 'rb42Shortcuts' not in _dl
assert 'static uint32_t rb61NewId()' in anim_h and 'rb61IdReferenced' in anim_h
_ni=anim_h[anim_h.index('static uint32_t rb61NewId()'):anim_h.index('static uint32_t rb61NewId()')+900]
assert 'rb42ShortcutsDamaged' in _ni and 'LittleFS.exists(rb61Path(id))' in _ni and 'rb61IdReferenced(id)' in _ni and '9999' in _ni
assert 'const uint32_t id = rb61NewId();' in anim_h and 'Keine freie Animations-ID mehr.' in anim_h
_g=anim_h[anim_h.index('void onAnimGet()'):anim_h.index('// POST /api/anim/put')]
assert _g.index('heapNow < RB61_GET_MIN_HEAP')<_g.index('LittleFS.open') and '503' in _g and 'Speicher knapp' in _g
assert '\\"total\\":' in _g and '\\"off\\":' in _g and '\\"n\\":' in _g and 'f.seek(RB61_META_BYTES + off)' in _g
assert 'uint8_t raw[RB61_GET_RAW]' in _g and 'char text[RB61_GET_RAW / 3 * 4 + 4]' in _g and 'rb61B64Decode' not in _g and 'String data' not in _g   # keine grossen Stapelpuffer, keine String-Sammlung
assert 'async function animFetchPayload(id,progress)' in h and h.count("/api/anim/get?id=")==1 and h.count('animFetchPayload(')>=3
assert 'Speicher knapp' in h   # Grenzen seit 0.6.1.5 siehe unten
assert ".v43-force-btn[data-mode]').forEach(x=>{" in h and 'x.disabled=rbAnimActive' in h and '.v43-force-btn:disabled' in h
assert 'Die Kachel zeigt danach' in h and 'Diese Kurzwahl wird dabei geleert.' not in h
assert 'animEditHint' not in h and 'überschreibt diese Animation' not in h and 'legt die Animation nur vorübergehend' not in h, 'Hinweistexte der Bearbeitungsansicht entfallen (Z2)'
print('PASS: 0.6.1.4 (Abruf in Teilen + Heap-Schutz, kleinste freie ID, Loeschen ohne Kurzwahl-Eingriff, gesperrte Anzeige-Tasten).')
# --- v0.6.1.5: Heap-Schutz (Abruf 1200 B als eine Antwort, Block-Pruefung, Listen-503, Warteseite), Modus nach Animation,
#     Reihenfolge der Animationen, WLAN-Name, Mehrfachauswahl, Rueckwaerts, Seitenleiste ---
assert 'RB61_GET_MAX = 1200' in anim_h and 'RB61_GET_MIN_HEAP = 24000UL' in anim_h and 'RB61_GET_MIN_BLOCK = 10000UL' in anim_h and 'RB61_GET_RAW = 300' in anim_h
_g=anim_h[anim_h.index('void onAnimGet()'):anim_h.index('// POST /api/anim/move')]
assert 'ESP.getMaxAllocHeap() < RB61_GET_MIN_BLOCK' in _g and 'out.reserve(' in _g and '\\"heap\\":' in _g
assert 'web.sendContent' not in _g and 'JsonChunkWriter' not in _g, 'Abruf antwortet in einem Stueck mit bekannter Laenge'
assert _g.index('f.close();   // Datei zu')<_g.index('web.send(200, "application/json; charset=utf-8", out)')
assert 'RB61_ORDER[] = "/rb-anim/order.bin"' in anim_h and 'void onAnimMove()' in anim_h and 'httpRoute("/api/anim/move", HTTP_POST, onAnimMove);' in ino
_l=anim_h[anim_h.index('void onAnimList()'):anim_h.index('void onAnimGet()')]
assert 'rb61ApplyOrder(ids, n);' in _l
assert 'rb61OrderSync((uint16_t)id);' in anim_h and 'rb61OrderSync(0);' in anim_h
assert 'WIFI_SSID[] = "RavestickBoard";' in ino and 'WIFI_PASSWORD[] = "Banane1248!";' in ino and 'CoolLED1248"' not in ino.replace('bis 0.6.1.4: "CoolLED1248"','')
assert '"RavestickBoard | Diagnose\\n"' in ino and 'RavestickBoard for CoolLED1248' not in ino
assert 'static void httpRouteGuarded(' in ino and 'RB_HTTP_MIN_HEAP = 20000UL' in ino and 'RB_PAGE_MIN_HEAP = 22000UL' in ino
for _r in ['/api/library','/api/library/get','/api/collections','/api/collections/get','/api/shortcuts','/api/anim/list','/api/program','/api/font','/api/sign','/api/block/get']:
    assert f'httpRouteGuarded("{_r}", ' in ino, _r
for _r in ['/api/status','/api/diagnostics','/api/diagnostics.txt','/api/ram.txt','/api/http.txt']:
    assert f'httpRouteGuarded("{_r}"' not in ino, _r + ' muss auch bei knappem Heap erreichbar bleiben'
_hp=ino[ino.index('static void onHomePage()'):ino.index('static void onHomePage()')+700]
assert 'RB_PAGE_MIN_HEAP' in _hp and 'web.hasArg("force")' in _hp and 'RB_WAIT_PAGE' in _hp and 'If-None-Match' in _hp
assert 'http-equiv=\\"refresh\\"' in ino and '/?force=1' in ino
assert 'HTTP-Anfragen wegen knappem Heap vertagt (503): ' in ino
_tx=ino[ino.index('ramTraceMark(RT_TX_END, (uint16_t)payloadLen);'):]
assert _tx.index('if (job != ANIM && rb61LastKind != 1) {')<_tx.index('[STREAM] Fertig'), 'Modus nach den Daten erneut setzen (H2/J14)'
assert 'sendSimple(c, 0x06, actualMode);' in _tx[:900]
# Weboberflaeche
assert '<title>RavestickBoard · v0.6.1.7-dev</title>' in h and 'for CoolLEDX ·' not in h
assert 'const ANIM_GET_LEN=1200' in h and "'&len='+ANIM_GET_LEN,null,true" in h and 'ANIM_GET_PAUSE_LOW_MS' in h
assert 'const RB_503_TRIES=8' in h and 'e.status!==503||data||noRetry' in h, 'nur lesende Anfragen werden bei 503 wiederholt'
assert "if(opt.reverse)order.reverse();" in h and h.index('if(opt.reverse)order.reverse();')<h.index('if(opt.ping&&order.length>2)')
assert 'id="animRev"' in h and "reverse:$('animRev').checked" in h
assert "$('animRasterText').value='';" in h
assert 'const RB_MULTI={' in h and 'async function rbMultiDelete(kind)' in h and h.count("if(rbMultiOn(")>=3
for _id in ['libMultiBar','progMultiBar','animMultiBar']:
    assert f'id="{_id}"' in h, _id
assert "rbQueueMove('/api/anim/move',id,to,animRefresh)" in h
assert 'let rbJobWatch=false' in h and "if(d.state==='error')notify(" in h, 'Meldung bei fehlgeschlagenem Sendeauftrag (D10)'
assert '.pixel-range:has(input:disabled){opacity:.42}' in h
assert '@media(min-width:1000px){' in h and '.menu-backdrop{padding-left:max(12px,calc((100vw - 720px)/2))}' in h
print('PASS: 0.6.1.5 (Abruf 1200 B in einem Stueck + Block-Pruefung, Listen-503, Warteseite, Modus nach Animation, Reihenfolge, WLAN-Name, Mehrfachauswahl, Rueckwaerts, Seitenleiste).')
# --- v0.6.1.6: Antworten waehrend einer Uebertragung, Rahmen, 40 Seiten, Schrift mit Wiederholung, Bedienpunkte ---
assert '#define RB_WEB_DURING_BLE 1' in ino and 'RB_TX_WEB_EVERY_MS = 250UL' in ino and 'static volatile bool rbTxActive = false;' in ino
_r=ino[ino.index('static void rbTxReply('):ino.index('static void rbServeWebDuringTx(')]
assert 'strcmp(path, "/api/status") == 0' in _r and '\\"busy\\":true' in _r and 'web.send(409,' in _r and 'RB_TX_WAIT_PAGE' in _r and 'web.send(503,' in _r
_sv=ino[ino.index('static void rbServeWebDuringTx('):ino.index('static void rbTxDelay(')]
assert 'uxTaskGetStackHighWaterMark' in _sv and 'web.handleClient();' in _sv and 'if (!rbTxActive) return;' in _sv and '#if RB_WEB_DURING_BLE' in _sv
_hr=ino[ino.index('static void httpRoute('):ino.index('static void httpRoute(')+900]
assert 'if (rbTxActive) rbTxReply(path); else handler();' in _hr and 'if (rbTxActive) rbTxReply(path);' in ino[ino.index('static void httpRouteGuarded('):ino.index('static void httpRouteGuarded(')+600]
assert 'if (rbTxActive) rbTxReply("?");' in ino, 'auch unbekannte Pfade antworten waehrend einer Uebertragung mit 409'
_lp=ino[ino.index('rbTxActive = rbTxLongJob(job);'):ino.index('rbTxActive = false;',ino.index('rbTxActive = rbTxLongJob(job);'))]
assert 'runJob(job' in _lp and 'rbTxDelay(400, "job_retry");' in _lp, 'Sperre umfasst Auftrag und Wiederholung'
assert ino.count('web.on(')==2, 'alle Routen laufen ueber httpRoute/httpRouteGuarded (Sperre greift ueberall)'
assert 'rbServeWebDuringTx("tx_wait_notify")' in ino and 'rbTxDelay(60, "tx_after_ack");' in ino and 'rbTxDelay(650, "ble_after_connect");' in ino
assert 'Webantworten in Übertragungen: ' in ino and '"stackBefore\\":' in ino.replace('\\"stackBefore\\":','"stackBefore\\":') or 'stackBefore' in ino
assert 'PAGE_LIMIT = 40' in ino and 'RB42_PAGES = 40' in v42_h and 'RB42_PAGES_V1 = 25' in v42_h and 'static bool rb42ReadBlockV1File(' in v42_h
assert 'if (layout == 2) align = 1;' not in ino, 'Mini einzeilig: links/mittig/rechts'
for _w in ['Datenlänge zu groß','Übertragung fehlgeschlagen']:
    assert _w in ino, _w
for _old in ['Datenlaenge zu gross','"Blockfolge gespeichert','Ungültige Blockfolge']:
    assert _old not in ino+v42_h, _old
# Weboberflaeche
assert 'MAX_PAGES=40' in h and 'id="rbBlockHead"' in h and 'Blocktext · Seite ${selected+1} von ${MAX_PAGES}' in h
assert 'Blockanzeige' not in h and 'Neue Blockfolge' not in h and 'Diese Seite anzeigen“ sendet nur' not in h
assert 'var rbTxOn=false' in h and 'function rbTxSet(on)' in h and "html.rb-tx .rb-tx-pill{display:flex;position:absolute" in h and 'Übertragung läuft …' in h
assert "if(data&&rbTxOn&&path!=='/api/status')" in h and 'RB_TX_TRIES=90' in h
assert 'function rbFrameSync()' in h and 'body.rb-frame #appShell{position:fixed' in h and 'border-radius:17px 17px 0 0!important' in h
assert '@media(max-width:399px)' in h and 'width:30px!important;height:30px!important' in h
assert 'async function rbFontInit()' in h and 'rbFontInit();' in h and "fetch('/api/font')" not in h, 'Schrift mit Wiederholung (Befund iPhone SE)'
assert 'function rbNiceName(raw)' in h and 'function rbNameRun(el)' in h and '@keyframes rbNameRun' in h
assert 'GIF importieren' in h and 'Einzelbilder aus einem Bild' in h and '>Bildstreifen<' not in h
assert "' (beschädigt)'" in h and 'id="v42ShortcutMsg"' in h and "$('animSaveCopy').onclick=async()=>{" in h and "' (Kopie)'" in h
assert 'Eine gesendete Animation ersetzt den Inhalt der Tafel' not in h, 'Hinweistext steht jetzt in der Doku'
assert '#libDelete:not(:disabled),#animDelete:not(:disabled),#v42DeleteProgram:not(:disabled){background:#512d35' in h
# Beispiel-Animationen
_ad=root/'assets/animationen'
for _n in ['herzschlag','equalizer','regenbogenwelle','sternenhimmel','rave_blinkt','pfeile_rechts','pfeile_links','lagerfeuer','smileys']:
    _t=(_ad/f'{_n}.txt').read_text(encoding='utf8'); _fr=_t.strip('\n').split('\n---\n')
    assert 2<=len(_fr)<=79 and all(len(f.split('\n'))==16 and all(len(r)==64 and set(r)<=set('.BGCRMYW') for r in f.split('\n')) for f in _fr), _n
assert (_ad/'LIESMICH.md').exists() and (root/'tools/beispiel_animationen.py').exists()
print('PASS: 0.6.1.6 (Antworten waehrend Uebertragung + Sperre, Rahmen, 40 Seiten mit alten Blockdateien, Schrift mit Wiederholung, Namen, Umlaute, Beispiel-Animationen).')
# --- v0.6.1.7: Rahmen fest, Sperre nur bei Datenuebertragungen, sparsame Exporte, Neustart-Meldung, Icons, Backup-Signal ---
assert 'static bool rbTxLongJob(Job j) { return j == TEXT || j == PAGE || j == AMBIENCE || j == BAND || j == ANIM; }' in ino
assert 'rbTxActive = rbTxLongJob(job);' in ino and 'rbTxActive = true;' not in ino
assert 'struct RbExportOut {' in ino and 'RB_EXPORT_MIN_HEAP = 14000UL' in ino and 'web.sendContent(buf, n)' in ino
for _fn,_nx in [('static void onHttpTraceDownload() {','\n}\n'),('void onRamTraceDownload() {','\n}\n')]:
    _b=ino[ino.index(_fn):ino.index(_nx,ino.index(_fn))]
    assert 'RbExportOut out;' in _b and _b.count('web.sendContent(')==1 and 'out.flush();' in _b, _fn   # nur noch das abschliessende leere Stueck
assert '{ rbExportWaitHeap(); web.sendContent(buffer); buffer = ""; }' in ino
assert '#include <esp_random.h>' in ino and 'rbBootId = esp_random() | 1UL;' in ino
assert '\\"boot\\":%lu,\\"up\\":%lu,\\"restart\\":\\"%s\\",\\"restartPhase\\":\\"%s\\"' in ino and 'strncpy(rbRestartKind, "crash"' in ino
assert ino.index('static uint32_t rbBootId')<ino.index('static void rbCrumbBoot()')
# Weboberflaeche
assert "html.rb-frame-doc,html.rb-frame-doc body{height:100%;overflow:hidden!important;overscroll-behavior:none}" in h
assert "body.rb-frame #appShell{position:fixed;top:0;bottom:0;left:12px;right:12px" in h and 'padding-top:env(safe-area-inset-top,0px)' in h
assert "document.documentElement.classList.toggle('rb-frame-doc',framed)" in h
assert "function rbTxFromStatus(d){\n if(d.busy){" in h and "d.state==='sending'||d.state==='queued'" not in h[h.index('function rbTxFromStatus'):h.index('function rbTxFromStatus')+300]
assert 'Date.now()-rbTxPolledAt<900' in h and 'setInterval(()=>{if(rbTxOn||rbDown)poll();},1000);' in h
assert 'const RB_DOWN_AFTER_MS=6000;' in h and 'function rbBootCheck(d)' in h and "'ESP32 antwortet nicht …'" in h and "ac.abort(),4000" in h
assert "'tower-control':'<path" in h and "'blend':'<circle cx=\"15\" cy=\"9\" r=\"7\"/><circle cx=\"9\" cy=\"15\" r=\"7\"/>'" in h
assert 'id="powerOff" type="button" data-rb-icon="eye-closed" data-rb-only="1"' in h and 'id="symbolClose" type="button" title="Schließen" data-rb-icon="x"' in h
assert "b.dataset.rbIcon=it.mine?'tower-control':'blend'" in h and "b.dataset.rbIcon='save';b.textContent='Als meine Tafel speichern'" in h
assert 'libAssign' not in h and 'libSlot' not in h and '"/api/library/shortcut"' in ino, 'Belegen/Freigeben entfernt, Route bleibt fuer alte Backups'
assert "label.textContent='Backup wird erstellt …'" in h
print('PASS: 0.6.1.7 (Rahmen fest, Sperre nur bei Datenuebertragungen, Status 1 s, sparsame Exporte, Neustart-Meldung, Icons, Backup-Signal, Belegen/Freigeben entfernt).')
# --- Dokumentation: Version und Reihenfolge ---
import re as _re
VER='0.6.1.7'
readme=(root/'README.md').read_text(encoding='utf-8')
assert f'version-v{VER.replace(".", ".")}--dev' in readme and 'version-v0.6.1.7--dev-' in readme
assert 'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v0_6_1_7.ino' in readme and 'RavestickBoard_v0_5_0_1' not in readme
assert readme.index('<h1')<readme.index('> **Aktueller Entwicklungskandidat: v0.6.1.7-dev')   # Banner unter Kopf, GIF, Foto und Titel
assert readme.index('board-gif.gif')<readme.index('totem.jpg')<readme.index('<h1')
assert '## Aktuell: v0.6.1.7-dev' in readme and '**Teststand v0.6.1.7' in readme and 'RavestickBoard_Anim.h' in readme
changelog=(root/'CHANGELOG.md').read_text(encoding='utf-8')
assert changelog.index('## v0.6.1.7-dev')<changelog.index('## v0.6.1.6-dev')<changelog.index('## v0.6.1.5-dev')<changelog.index('## v0.6.1.4-dev')<changelog.index('## v0.6.1.3-dev')<changelog.index('## v0.6.1.2-dev')<changelog.index('## v0.6.1.1-dev')<changelog.index('## v0.6.1.0-dev')<changelog.index('## v0.6.0.2-dev')<changelog.index('## v0.6.0.1-dev')<changelog.index('## v0.6.0.0-dev')<changelog.index('## v0.5.0.1-dev')
vg=(root/'VERSIONSGESCHICHTE.md').read_text(encoding='utf-8')
assert '| v0.6.0.2-dev |' in vg and '| v0.6.1.0-dev |' in vg and '| v0.6.1.1-dev |' in vg and '| v0.6.1.2-dev |' in vg and '| v0.6.1.3-dev |' in vg and '| v0.6.1.4-dev |' in vg and '| v0.6.1.5-dev |' in vg and '| v0.6.1.6-dev |' in vg and '| v0.6.1.7-dev |' in vg and 'Offene Punkte (Stand v0.6.1.7-dev)' in vg
assert (root/'docs/TESTPLAN_v0.6.1.7.md').exists() and 'TESTPLAN_v0.6.1.7.md' in readme and not (root/'docs/TESTPLAN_v0.6.1.6.md').exists() and (root/'docs/archive/TESTPLAN_v0.6.1.6.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.5.md').exists() and (root/'docs/archive/TESTPLAN_v0.6.1.5.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.4.md').exists() and (root/'docs/archive/TESTPLAN_v0.6.1.4.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.3.md').exists() and (root/'docs/archive/TESTPLAN_v0.6.1.3.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.2.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.1.md').exists() and not (root/'docs/TESTPLAN_v0.6.1.0.md').exists() and not (root/'docs/TESTPLAN_v0.6.0.2.md').exists() and not (root/'docs/TESTPLAN_v0.6.0.1.md').exists() and not (root/'docs/TESTPLAN_v0.6.0.0.md').exists()
assert readme.count('<h1')==1
assert 'WLAN `RavestickBoard`' in readme and 'WLAN `CoolLED1248`' not in readme.split('## Kurz zurückgeblickt')[0]
for name in ['docs/ROADMAP.md','docs/TECHNIK.md','docs/DIAGNOSE.md','docs/QUELLEN_UND_LIZENZEN.md','docs/ENTSCHEIDUNGEN.md','THIRD_PARTY_NOTICES.md','tests/README.md']:
    assert '0.6.1.7' in (root/name).read_text(encoding='utf-8'), name
# keine Tafeladresse, keine E-Mail-Adresse, keine Zugangsdaten in Dokumenten
_mac=_re.compile(r'\b[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}\b')
_mail=_re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}')
for f in list(root.glob('*.md'))+list((root/'docs').glob('*.md'))+list((root/'tests').glob('*.md')):
    t=f.read_text(encoding='utf-8')
    assert not _mac.search(t.replace('aa:bb:cc:dd:ee:ff','').replace('c0:ff:ee:00:00:01','')), f   # beide sind ausgedachte Platzhalter
    assert not [m for m in _mail.findall(t) if not m.endswith('@users.noreply.github.com') and m!='noreply@anthropic.com'], f   # keine E-Mail-Adresse ausser noreply
print('PASS: Dokumentation (Version, Banner unter Titel, Installationspfad, Verweise, keine Adressen).')
# --- v0.6.0.1: Frame-Nummer im Muster ---
assert 'static bool rb60NumberPixel(' in ino and 'RB60_DIGITS[10][5]' in ino
assert ino.index('static bool rb60NumberPixel(')<ino.index('static uint8_t rb60AnimColor(')            # Nummer vor Muster
assert 'rb60NumberPixel((uint8_t)(f + 1), col, row)' in ino                                          # 1-basiert
assert '(pattern == ANIM_COLORS ? 700 : pattern == ANIM_BAR ? 60 : 300)' in ino                       # Grenztest lesbar
assert 'Grenze 300 ms' in h and 'seine Nummer' in h
# --- v0.6.0.2: Reihenfolge fuer die automatischen Arduino-Prototypen ---
import importlib.util as _iu
_spec=_iu.spec_from_file_location('arduino_prototypes', root/'tests/arduino_prototypes.py'); _ap=_iu.module_from_spec(_spec); _spec.loader.exec_module(_ap)
_probs=_ap.check(ino)
assert not _probs, 'Typ in Funktionssignatur vor der ersten Funktion nicht definiert (Arduino-Prototypen): '+'; '.join(_probs[:3])
_first_fn=min(ino.index(x) for x in ('static void rbPhase(', 'const char *ramStageLabel('))
assert ino.index('enum RamStage')<ino.index('static void rbPhase(')              # in 0.6.0.1 stand eine Funktion davor
assert ino.index('static bool rb60NumberPixel(')>ino.index('static void rbPhase(')   # Animationsfunktionen hinter den Typen
import importlib.util as _iu2
_s2=_iu2.spec_from_file_location('decl_order', root/'tests/decl_order.py'); _do=_iu2.module_from_spec(_s2); _s2.loader.exec_module(_do)
_dp=_do.check(root/'firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v0_6_1_7.ino')
assert not _dp, 'Name vor seiner Deklaration benutzt (Reihenfolge der Einbindungen): '+'; '.join(_dp[:3])
print('PASS: Deklarationsreihenfolge des zusammengesetzten Sketchs (decl_order).')
print('PASS: Prototyp-Reihenfolge (kein Typ in einer Signatur vor seiner Definition).')
print('PASS: Animationstest-Invarianten (Opcode, Aufraeumen, Modus nach Upload, Status nur im Test strikt, Route, Testbereich).')
print('PASS: Tafelverwaltung-Invarianten (keine Adresse im Code), JS parse, gzip/ETag, firmware version, Stilmarken-Verträge, JSON diagnostics only once, 7 one-column colors, disabled/active block actions, 3 mobile viewports.')
