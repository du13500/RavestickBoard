#!/usr/bin/env python3
"""Symbol-Daten (ab 0.6.1.8) aus assets/symbole_0618.txt neu bauen.

Aufruf (Repo-Wurzel):  python tools/generate_assets.py  &&  python tools/sync_web.py

Was passiert:
  * Die 16x16-Sprites (128 Byte je Sprite, zwei Pixel pro Byte, hoeherer Halbbyte = gerades x)
    stehen gepackt in web/index.html (RB_ASSET_DATA.symbols, Base64) und in der Firmware
    (RB_SYMBOLS_PACKED in RavestickBoard_Assets.h). Beide Kopien muessen identisch sein.
  * Sprites, die in assets/symbole_0618.txt stehen, werden ersetzt bzw. angehaengt
    (Nummern ab 64). Alle anderen Nummern bleiben aus dem Bestand in web/index.html.
  * Weniger als 16 Zeilen: senkrecht mittig (Rest nach unten), Zeilen rechts mit '.' aufgefuellt.
  * BLANK_SLOTS sind verworfene Nummern: bleiben als leere Plaetze reserviert.
Die Schrift-Daten (RB_FONT_*, RB_ASSET_DATA.normal/bold) werden nicht angefasst.
Es werden keine Dateien aus dem Netz geladen.
"""
from __future__ import annotations
import base64, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / 'firmware' / 'RavestickBoard_v0_6_1_8' / 'RavestickBoard_Assets.h'
SRC = ROOT / 'assets' / 'symbole_0618.txt'
WEB = ROOT / 'web' / 'index.html'
PAL = {'.': 0, 'B': 1, 'G': 2, 'C': 3, 'R': 4, 'M': 5, 'Y': 6, 'W': 7}
BLANK_SLOTS = (48, 51, 52, 53, 56, 57, 58)
BYTES = 128


def parse(path: Path) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    cur = None
    for line in path.read_text(encoding='utf8').split('\n'):
        if line.startswith('@ '):
            cur = int(line.split()[1])
            if cur in out:
                raise SystemExit(f'Nummer {cur} doppelt')
            out[cur] = []
            continue
        if line.startswith('#') or not line.strip():
            continue
        if cur is None or not set(line) <= set(PAL):
            raise SystemExit(f'Ungueltige Zeile bei {cur}: {line!r}')
        out[cur].append(line)
    return out


def pack(rows: list[str]) -> bytes:
    if not 1 <= len(rows) <= 16 or max(map(len, rows)) > 16:
        raise SystemExit(f'Matrix zu gross: {len(rows)} Zeilen')
    top = (16 - len(rows)) // 2
    grid = [['.'] * 16 for _ in range(16)]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            grid[top + y][x] = ch
    data = bytearray()
    for row in grid:
        for x in range(0, 16, 2):
            data.append((PAL[row[x]] << 4) | PAL[row[x + 1]])
    return bytes(data)


def main() -> None:
    html = WEB.read_text(encoding='utf8')
    m = re.search(r'const RB_ASSET_DATA = (\{.*?\});\n', html)
    if not m:
        raise SystemExit('RB_ASSET_DATA fehlt in web/index.html')
    data = json.loads(m.group(1))
    base = bytearray(base64.b64decode(data['symbols']))
    if len(base) % BYTES:
        raise SystemExit('Symbolblock hat falsche Laenge')
    mats = parse(SRC)
    count = max(max(mats), len(base) // BYTES - 1) + 1
    if sorted(n for n in mats if n >= 64) != list(range(64, count)):
        raise SystemExit('Nummern ab 64 muessen lueckenlos sein')
    base.extend(bytes(BYTES * (count - len(base) // BYTES)))
    for n, rows in mats.items():
        base[n * BYTES:(n + 1) * BYTES] = pack(rows)
    for n in BLANK_SLOTS:
        base[n * BYTES:(n + 1) * BYTES] = bytes(BYTES)
    data['symbols'] = base64.b64encode(bytes(base)).decode()
    out = 'const RB_ASSET_DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n'
    html = html[:m.start()] + out.rstrip('\n') + '\n' + html[m.end():]
    html = re.sub(r'const RB_SYMBOL_COUNT=\d+;', f'const RB_SYMBOL_COUNT={count};', html, count=1)
    WEB.write_text(html, encoding='utf8')

    asset = FW.read_text(encoding='utf8')
    lines = ['static const uint8_t RB_SYMBOLS_PACKED[] PROGMEM = {']
    for i in range(0, len(base), 24):
        lines.append('  ' + ', '.join('0x%02X' % b for b in base[i:i + 24]) + ',')
    lines.append('};')
    asset, n1 = re.subn(r'static const uint8_t RB_SYMBOLS_PACKED\[\] PROGMEM = \{.*?\n\};',
                        lambda _: '\n'.join(lines), asset, count=1, flags=re.S)
    asset, n2 = re.subn(r'RB_SYMBOL_COUNT = \d+;', f'RB_SYMBOL_COUNT = {count};', asset, count=1)
    if n1 != 1 or n2 != 1:
        raise SystemExit('Assets.h: Symbolblock nicht gefunden')
    FW.write_text(asset, encoding='utf8')
    print(f'{count} Sprites ({len(base)} Byte) in web/index.html und {FW.name} geschrieben.')


if __name__ == '__main__':
    sys.exit(main())
