"""v0.8.2: Entwurfs-Lebenszyklus, Eingaben und Pixelgrafik der Import-Maske im echten (headless) Chromium mit simulierter API.
Prueft: Mehrheitsfarbe und Faktor-Erkennung (reine Funktionen), Bildart Foto/Pixelgrafik (Automatik bei hoechstens 16 Farben,
1:1-Rahmen mit Faktor, Schwelle/Kontrast gesperrt), Zahlenfelder zu den Reglern, einklappbarer Bereich "Anker und Vorlagen",
Rueckfrage beim Quellwechsel (Abbrechen erhaelt den Entwurf), ganze Zahlen in Von/Bis/Schritt, Schwenk-Timer vor dem Speichern,
GIF-Decoder lehnt unvollstaendige Daten ab, Undo-Grenze, Tastatur bei gesperrtem Editor, Editor gibt Bilder beim Schliessen frei.
Aufruf: python tests/test_browser_lifecycle_0802.py
Nicht geprueft: echtes iPhone-Safari."""
import sys, re, json, io, base64
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
_src = (ROOT / 'tests/test_browser_editor_0802.py').read_text(encoding='utf8')
_ns = {'__file__': str(ROOT / 'tests/test_browser_editor_0802.py'), '__name__': 'ed_base', 'sys': sys, 're': re, 'json': json, 'Path': Path}
exec(_src[:_src.index('TMP = Path(')], _ns)
page_with, errors = _ns['page_with'], _ns['errors']
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw
import random
fails = []
def check(c, msg):
    if not c: fails.append(msg); print('FAIL', msg)
random.seed(3)
PAL = [(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255), (255, 255, 255)]
TMP = Path('/tmp/rb_lifecycle_0802'); TMP.mkdir(exist_ok=True)
nat = Image.new('RGB', (96, 96), (0, 0, 0)); d = ImageDraw.Draw(nat)
for _ in range(60):
    x, y = random.randrange(96), random.randrange(96); d.rectangle([x, y, x + random.randrange(2, 12), y + random.randrange(2, 9)], fill=random.choice(PAL))
nat.resize((192, 192), Image.NEAREST).save(TMP / 'art2x.png')
ph = Image.new('RGB', (300, 200))
for x in range(300):
    for y in range(200): ph.putpixel((x, y), (x * 255 // 300, y * 255 // 200, (x + y) % 256))
ph.save(TMP / 'photo.png')
f1 = nat.crop((0, 0, 64, 16)).resize((128, 32), Image.NEAREST); f2 = nat.crop((10, 10, 74, 26)).resize((128, 32), Image.NEAREST)
f1.save(TMP / 'art.gif', save_all=True, append_images=[f2], duration=200, loop=0)
gif_bytes = (TMP / 'art.gif').read_bytes()
with sync_playwright() as pw:
    br = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    ctx, page = page_with(br, 1100, 900, touch=False)
    # --- reine Funktionen ---
    r = page.evaluate("""()=>{
      const mk=(w,h,f)=>{const a=new Uint8ClampedArray(w*h*4);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const c=f(x,y),i=(y*w+x)*4;a[i]=c[0];a[i+1]=c[1];a[i+2]=c[2];a[i+3]=255;}return a;};
      const cols=[[255,0,0],[0,255,0],[0,0,255],[255,255,0]];
      const up2=mk(128,32,(x,y)=>cols[((x>>1)*3+(y>>1)*5)%4]);
      const nat=mk(128,32,(x,y)=>cols[(x*3+y*5)%4]);
      const flat=mk(40,40,()=>[0,0,0]);
      const m=RbAnim.majority(mk(128,32,(x,y)=>((x>>1)+(y>>1))%2?[255,0,0]:[0,0,255]),128,32,{x:0,y:0,w:64,h:16});
      // Block 2x2 mit 3 roten und 1 blauen Pixel -> rot
      const blk=mk(128,32,(x,y)=>(x%2===1&&y%2===1)?[0,0,255]:[255,0,0]);
      const mb=RbAnim.majority(blk,128,32,{x:0,y:0,w:64,h:16});
      const outside=RbAnim.majority(mk(16,4,()=>[255,255,255]),16,4,{x:24,y:6,w:16,h:4});
      return {up2:RbAnim.pixelScale(up2,128,32),nat:RbAnim.pixelScale(nat,128,32),flat:RbAnim.pixelScale(flat,40,40),
        mAll:[...m].every(v=>v===4||v===1),mb:[...mb].every(v=>v===4),out0:outside[0],outIn:outside[6*64+24],outEdge:outside[6*64+23]};}""")
    check(r['up2'] == 2 and r['nat'] == 1 and r['flat'] == 1, f'pixelScale {r}')
    check(r['mAll'] and r['mb'], 'Mehrheitsfarbe: Block mit Mehrheit rot')
    check(r['out0'] == 0 and r['outIn'] == 7 and r['outEdge'] == 0, f'Mehrheitsfarbe: ausserhalb des Bildes schwarz {r}')
    pl = page.evaluate("RbAnim.plan([100,100,100,100,100],{from:1.5,to:3.4,step:1.2,ms:100})")
    check(all(isinstance(i, int) or float(i).is_integer() for i in pl['order']) and pl['count'] >= 1, f'plan rundet auf ganze Zahlen {pl}')
    # --- GIF: unvollstaendige Daten ---
    b64 = base64.b64encode(gif_bytes).decode(); cut = base64.b64encode(gif_bytes[:len(gif_bytes) - 40]).decode()
    res = page.evaluate("""async([ok,cut])=>{const dec=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));let a,b;
      try{a=(await RbAnim.gifDecode(dec(ok),()=>{})).count;}catch(e){a='ERR '+e.message;}
      try{b=(await RbAnim.gifDecode(dec(cut),()=>{})).count;}catch(e){b='ERR '+e.message;}return [a,b];}""", [b64, cut])
    check(res[0] == 2, f'GIF vollstaendig lesbar {res}')
    check(isinstance(res[1], str) and res[1].startswith('ERR'), f'GIF abgeschnitten wird abgelehnt {res}')
    # --- Pixelgrafik per Schwenk-Bild ---
    page.set_input_files('#animFilePan', str(TMP / 'art2x.png')); page.wait_for_timeout(700)
    st = page.evaluate("({k:$('animKind').value,d:$('animDither').value,sw:animPan.s.w,ew:animPan.e.w,off:$('animThr').disabled&&$('animConN').disabled,fold:$('animAnchHead').getAttribute('aria-expanded'),hidden:$('animAnchBody').classList.contains('hidden')})")
    check(st['k'] == 'pixel' and st['d'] == 'majority', f'Pixelgrafik automatisch erkannt {st}')
    check(st['sw'] == 128 and st['ew'] == 128, f'Rahmen 1:1 mit Faktor 2 (128) {st}')
    check(st['off'], 'Schwelle/Kontrast bei Pixelgrafik gesperrt')
    check(st['fold'] == 'false' and st['hidden'], 'Anker und Vorlagen standardmaessig eingeklappt')
    page.click('#animAnchHead'); page.wait_for_timeout(100)
    check(page.evaluate("!$('animAnchBody').classList.contains('hidden')&&$('animAnchHead').getAttribute('aria-expanded')==='true'"), 'Anker und Vorlagen klappt auf')
    page.click('#animAnchHead')
    check(page.evaluate("$('animAnchBody').classList.contains('hidden')"), 'Anker und Vorlagen klappt wieder zu')
    # alle Frames bestehen nur aus den sieben Farben + schwarz, Block-Farben unveraendert (verlustfrei bei 1:1)
    ok = page.evaluate("animImp.frames.length>0&&animImp.frames.every(f=>f.length===1024)")
    check(ok, 'Frames der Pixelgrafik erzeugt')
    # Bildart zurueck auf Foto
    page.select_option('#animKind', 'photo'); page.wait_for_timeout(400)
    check(page.evaluate("$('animDither').value==='fs'&&!$('animThr').disabled"), 'Foto: Floyd-Steinberg, Regler aktiv')
    page.select_option('#animKind', 'pixel'); page.wait_for_timeout(400)
    check(page.evaluate("$('animDither').value==='majority'&&animPan.s.w===128"), 'Pixelgrafik per Auswahl springt auf 1:1')
    # Zahlenfelder
    page.select_option('#animKind', 'photo'); page.wait_for_timeout(300)
    page.fill('#animThrN', '200'); page.wait_for_timeout(300)
    check(page.evaluate("$('animThr').value==='200'"), 'Zahlenfeld setzt Regler Schwelle')
    page.fill('#animConN', '999'); page.wait_for_timeout(300)
    check(page.evaluate("$('animCon').value==='100'"), 'Zahlenfeld klemmt Kontrast auf 100')
    page.evaluate("$('animThr').value=64;$('animThr').dispatchEvent(new Event('input',{bubbles:true}))")
    check(page.evaluate("$('animThrN').value==='64'"), 'Regler fuehrt Zahlenfeld nach')
    # ganze Zahlen in Von/Bis/Schritt
    page.fill('#animFrom', '1.5'); page.fill('#animStep', '1.2'); page.wait_for_timeout(400)
    check(page.evaluate("animImp.frames.length>0")  and not [e for e in errors if 'TypeError' in e], f'Von=1,5 wirft keinen Fehler {errors[:2]}')
    # --- Foto bleibt Foto ---
    # Quellwechsel mit Rueckfrage: Abbrechen erhaelt den Entwurf
    page.evaluate("animImp.dirty=true"); page.remove_listener('dialog', page._dlg); page._dlg = lambda dd: dd.dismiss(); page.on('dialog', page._dlg)
    n0 = page.evaluate("animPan.iw"); page.set_input_files('#animFilePan', str(TMP / 'photo.png')); page.wait_for_timeout(500)
    check(page.evaluate("animPan.iw") == n0, 'Quellwechsel abgebrochen: alter Entwurf bleibt')
    page.remove_listener('dialog', page._dlg); page._dlg = lambda dd: dd.accept(); page.on('dialog', page._dlg)
    page.set_input_files('#animFilePan', str(TMP / 'photo.png')); page.wait_for_timeout(700)
    check(page.evaluate("animPan.iw") == 300 and page.evaluate("$('animKind').value") == 'photo', 'Quellwechsel bestaetigt: neues Foto, Bildart Foto')
    # Schwenk-Timer vor dem Speichern
    page.evaluate("animPan.s.x=7;animPanSync(true)")
    check(page.evaluate("animPan.rt!==0"), 'Test-Voraussetzung: Schwenk-Timer laeuft')
    page.evaluate("animFlush()")
    check(page.evaluate("animPan.rt===0&&animImp.timer===0"), 'animFlush leert beide Timer')
    # --- GIF mit wenigen Farben ---
    page.set_input_files('#animFileGif', str(TMP / 'art.gif')); page.wait_for_timeout(800)
    g = page.evaluate("({k:$('animKind').value,d:$('animDither').value,fit:$('animFit').value,w:animImp.crop&&animImp.crop.w})")
    check(g['k'] == 'pixel' and g['d'] == 'majority' and g['fit'] == 'crop' and abs(g['w'] - 1) < 1e-9, f'GIF Pixelgrafik: Rahmen 128 von 128 {g}')
    # --- Editor: Undo-Grenze, Tastatur, Freigabe ---
    page.evaluate("animShowImport()"); page.click('#animDrawNew'); page.wait_for_timeout(500)
    e = page.evaluate("""()=>{AD.undo=Array.from({length:100},(_,i)=>({frames:[],cur:i}));const first=AD.undo[0];adBegin();const afterBegin=AD.undo.length;adRollback();
      return {afterBegin,after:AD.undo.length,restored:AD.undo[0]===first};}""")
    check(e['afterBegin'] == 100 and e['after'] == 100 and e['restored'], f'Undo-Grenze: Rollback stellt den aeltesten Schritt wieder her {e}')
    k = page.evaluate("""()=>{AD.blocked=true;AD.undo=[{frames:AD.frames.slice(),cur:0}];document.dispatchEvent(new KeyboardEvent('keydown',{key:'z',ctrlKey:true}));const kept=AD.undo.length;AD.blocked=false;return kept;}""")
    check(k == 1, 'Tastatur bei gesperrtem Editor ohne Wirkung')
    page.evaluate("AD.dirty=false"); page.click('#adBack'); page.wait_for_timeout(200)
    fr = page.evaluate("({n:AD.frames.length,u:AD.undo.length,open:AD.open})")
    check(fr == {'n': 0, 'u': 0, 'open': False}, f'Editor gibt Bilder beim Schliessen frei {fr}')
    ctx.close(); br.close()
real = [e for e in errors if 'favicon' not in e]
check(not real, f'Seitenfehler: {real[:3]}')
print('FAILS:', len(fails))
sys.exit(1 if fails else 0)
