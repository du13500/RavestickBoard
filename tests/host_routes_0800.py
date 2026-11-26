"""Hält die festen Routen für Kurzbefehle fest (docs/KURZBEFEHLE.md, Block ROUTEN-ANFANG/-ENDE):
Jede Route ist im Sketch mit der Methode registriert, der Handler liest die genannten Felder, Lauftext hat
Standardwerte für fehlende Felder. Ändert jemand Pfad, Methode oder Feldnamen, schlägt der Test fehl.
Aufruf: python tests/host_routes_0800.py"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / 'firmware/RavestickBoard_v0_8_0'
src = '\n'.join(p.read_text(encoding='utf-8') for p in sorted(FW.glob('*.ino')) + sorted(FW.glob('*.h')) if 'WebUI' not in p.name)
doc = (ROOT / 'docs/KURZBEFEHLE.md').read_text(encoding='utf-8')
fails = []
def check(ok, msg):
    if not ok: fails.append(msg); print('FAIL', msg)
blk = doc[doc.index('<!-- ROUTEN-ANFANG -->'):doc.index('<!-- ROUTEN-ENDE -->')]
rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in blk.splitlines() if l.startswith('| ') and not l.startswith('| Methode') and not l.startswith('|---')]
check(len(rows) == 4, f'vier feste Routen dokumentiert ({len(rows)})')
def body(fn):
    m = re.search(r'\bvoid\s+' + re.escape(fn) + r'\s*\(\s*\)\s*\{', src)
    if not m: return ''
    i = m.end(); d = 1
    while d and i < len(src):
        d += {'{': 1, '}': -1}.get(src[i], 0); i += 1
    return src[m.start():i]
for meth, path, req, opt in rows:
    m = re.search(r'httpRoute\("' + re.escape(path) + r'",\s*HTTP_(GET|POST),\s*(\w+)\)', src)
    check(m is not None, f'{path} ist registriert')
    if not m: continue
    check(m.group(1) == meth, f'{path}: Methode {meth} ({m.group(1)})')
    b = body(m.group(2)); check(bool(b), f'{path}: Handler {m.group(2)} gefunden')
    fields = [f.strip() for f in (req + ',' + opt).split(',') if f.strip()]
    for f in fields:
        reads = f'web.arg("{f}")' in b or f'web.hasArg("{f}")' in b
        if not reads and f == 'id': reads = 'rb61RequestId()' in b and 'web.arg("id")' in src[src.index('static uint32_t rb61RequestId()'):][:400]
        check(reads, f'{path}: Handler liest Feld {f}')
# Lauftext: Standardwerte, wenn nur "text" kommt
qt = body('queueText')
check('web.hasArg("color") ? web.arg("color").toInt() : 7' in qt, 'Lauftext: Farbe fehlt -> 7 (weiß)')
check('web.hasArg("mode") ? web.arg("mode") : String("scroll")' in qt, 'Lauftext: Modus fehlt -> scroll')
check('web.hasArg("layout") ? constrain(web.arg("layout").toInt(), 0, 4) : 3' in qt, 'Lauftext: Schrift fehlt -> 3 (Original - Normal)')
# Kurzwahl 1..8, Animation-ID 1..9999
check(re.search(r'RB42_SHORTCUT_COUNT\s*=\s*8\b', src) is not None and 'slot<1||slot>RB42_SHORTCUT_COUNT' in body('v042RunShortcut'), 'Kurzwahl: slot 1 bis 8')
rid = src[src.index('static uint32_t rb61RequestId()'):][:400]
check('v.length() > 4' in rid, 'Animation: id hoechstens 4 Ziffern')
# Doku nennt die Farben wie die Oberflaeche
web = (ROOT / 'web/index.html').read_text(encoding='utf-8')
pairs = dict(re.findall(r"\['(Rot|Gelb|Grün|Cyan|Blau|Magenta|Weiß)',(\d)\]", web))
for name, code in pairs.items():
    check(f'{code} {name}' in doc, f'Doku: Farbe {code} = {name}')
check(len(pairs) == 7, f'sieben Farben in der Oberflaeche gefunden ({len(pairs)})')
print('FAILS:', len(fails))
sys.exit(1 if fails else 0)
