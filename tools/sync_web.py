#!/usr/bin/env python3
"""Reproducible WebUI gzip/ETag; run from repo root or anywhere."""
from pathlib import Path
import gzip, hashlib, json
ROOT=Path(__file__).resolve().parents[1]

def newest_firmware_dir(root):
    """Neuester Ordner firmware/RavestickBoard_v0_6_* (nach Versionsnummer, nicht alphabetisch).
    Mit --fw <Ordnername> laesst sich ein bestimmter Ordner waehlen."""
    import sys, re
    if '--fw' in sys.argv:
        return root / 'firmware' / sys.argv[sys.argv.index('--fw') + 1]
    best = None
    for d in (root / 'firmware').glob('RavestickBoard_v*'):
        m = re.fullmatch(r'RavestickBoard_v(\d+(?:_\d+)*)', d.name)
        if not m or not d.is_dir():
            continue
        key = tuple(int(x) for x in m.group(1).split('_'))
        if best is None or key > best[0]:
            best = (key, d)
    if best is None:
        raise SystemExit('Kein Firmware-Ordner gefunden.')
    return best[1]
html=(ROOT/'web/index.html').read_text(encoding='utf8').rstrip('\n')
raw=('\n'+html+'\n').encode('utf8')
gz=gzip.compress(raw,compresslevel=9,mtime=0)
lines=['  '+', '.join(f'0x{b:02x}' for b in gz[i:i+16])+',' for i in range(0,len(gz),16)]
header='#pragma once\n// v0.6.0.0: gzip-9 HTML in PROGMEM, generated reproducibly from web/index.html.\n// Do not edit this header directly; regenerate from the checked-in HTML source.\nstatic const uint8_t PAGE_HTML_GZIP[] PROGMEM = {\n'+'\n'.join(lines)+'\n};\nstatic constexpr size_t PAGE_HTML_GZIP_LEN = sizeof(PAGE_HTML_GZIP);\n'
header+='static constexpr char PAGE_HTML_ETAG[] = '+json.dumps('"'+hashlib.sha256(raw).hexdigest()[:24]+'"')+';\n'
p=newest_firmware_dir(ROOT)/'RavestickBoard_WebUI.h'   # 0.6.1.11: neuester Ordner statt festem Pfad
p.write_text(header,encoding='utf8')
print(f'{p.parent.name}: HTML={len(raw)} B gzip={len(gz)} B ETag={hashlib.sha256(raw).hexdigest()[:24]}')
