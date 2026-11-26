#!/usr/bin/env python3
"""Erzeugt vorschau.gif aus allen Text-Rastern eines Ordners (64x16, Frames durch --- getrennt)."""
import sys, os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1] if len(sys.argv) > 1 else '.'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(SRC, 'vorschau.gif')

# (Datei, Anzeigename, ms je Frame)
ITEMS = [
 ('herzschlag.txt', 'Herzschlag', 45),
 ('equalizer.txt', 'Equalizer bunt', 60),
 ('regenbogenwelle.txt', 'Regenbogenwelle', 50),
 ('sternenhimmel.txt', 'Sternenhimmel', 90),
 ('rave_blinkt.txt', 'RAVE blinkt', 140),
 ('pfeile_rechts.txt', 'Pfeile nach rechts', 40),
 ('pfeile_links.txt', 'Pfeile nach links', 40),
 ('lagerfeuer.txt', 'Lagerfeuer', 70),
 ('smileys.txt', 'Smileys', 130),
 ('dvd_logo.txt', 'DVD-Logo', 60),
 ('dvd_logo_ecke_unten_rechts.txt', 'DVD-Logo Ecke unten rechts', 60),
 ('dvd_logo_ohne_ecke.txt', 'DVD-Logo ohne Ecke', 60),
 ('Alien Dance.txt', 'Alien Dance', 130),
 ('Taxi sign.txt', 'Taxi sign', 250),
 ('UFO.txt', 'UFO', 120),
 ('Tunnel.txt', 'Tunnel', 80),
 ('schnelle Katze.txt', 'Schnelle Katze', 80),
 ('tanzende_banane.txt', 'Tanzende Banane', 130),
 ('TEST_ANDERE.txt', 'TEST andere', 500),
 ('TEST_ORANGE.txt', 'TEST orange', 500),
]
STEP_MS = 40          # Dauer je GIF-Bild (wie in der bisherigen Vorschau)
TOTAL_MS = 9360       # Schleifenlaenge der Vorschau (234 Bilder; Alien Dance passt genau)
COLS = 2

BG = (17, 20, 28); PANEL = (5, 8, 13); OFF = (24, 28, 38); TXT = (230, 234, 242)
COL = {'.': OFF, 'R': (255, 0, 0), 'G': (0, 255, 0), 'B': (0, 0, 255),
       'C': (0, 255, 255), 'M': (255, 0, 255), 'Y': (255, 255, 0), 'W': (255, 255, 255)}
KEYS = '.RGBCMYW'
PAL = np.array([COL[k] for k in KEYS], dtype=np.uint8)

def load(fn):
    t = open(os.path.join(SRC, fn), encoding='utf-8').read().replace('\r\n', '\n').strip('\n')
    frames = []
    for b in t.split('\n---\n'):
        ls = b.split('\n')
        assert len(ls) == 16 and all(len(l) == 64 and re.fullmatch('[.RGBCMYW]+', l) for l in ls), fn
        frames.append(np.array([[KEYS.index(c) for c in l] for l in ls], dtype=np.uint8))
    return frames

anims = [(name, ms, load(fn)) for fn, name, ms in ITEMS]
rows = (len(anims) + COLS - 1) // COLS
W = 11 + COLS * 326 + (COLS - 1) * 8 + 11
H = 33 + (rows - 1) * 116 + 86 + 11

# LED-Muster: 4x4 ohne Ecken + 1 px Luecke (5x5 Raster)
tile = np.zeros((5, 5), dtype=bool)
tile[:4, :4] = True
for cy, cx in ((0, 0), (0, 3), (3, 0), (3, 3)):
    tile[cy, cx] = False
MASK = np.tile(tile, (16, 64))   # (80, 320)

font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 14)
font13 = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 13)
base = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(base)
pos = []
for i, (name, ms, fr) in enumerate(anims):
    r, c = divmod(i, COLS)
    x0 = 11 + c * 334
    y0 = 33 + r * 116
    pos.append((x0, y0))
    title = f'{name}  ·  {len(fr)} Frames · {ms} ms'
    f = font
    if d.textlength(title, font=f) > 318:      # lange Titel verkleinern, damit sie nicht in die Nachbarspalte ragen
        f = font13
    d.text((x0 + 3, y0 - 5), title, font=f, fill=TXT, anchor='ls')
    d.rounded_rectangle([x0, y0, x0 + 325, y0 + 85], radius=5, fill=PANEL)
base_arr = np.array(base)

def render(t_ms):
    img = base_arr.copy()
    for (name, ms, fr), (x0, y0) in zip(anims, pos):
        g = fr[(t_ms // ms) % len(fr)]
        rgb = PAL[g]                                  # (16,64,3)
        big = np.repeat(np.repeat(rgb, 5, axis=0), 5, axis=1)   # (80,320,3)
        area = img[y0 + 3:y0 + 83, x0 + 3:x0 + 323]
        area[MASK] = big[MASK]
    return Image.fromarray(img)

# feste Palette: Hintergrund->Text-Verlauf (Kantenglaettung), Panel, LED aus, 7 LED-Farben
cols = [tuple(int(BG[i] + (TXT[i] - BG[i]) * k / 23) for i in range(3)) for k in range(24)]
cols += [PANEL] + [COL[k] for k in KEYS]
flat = [v for c in cols for v in c]
flat += [0] * (768 - len(flat))
pal_img = Image.new('P', (1, 1))
pal_img.putpalette(flat)

n = TOTAL_MS // STEP_MS
frames = [render(k * STEP_MS).quantize(palette=pal_img, dither=Image.Dither.NONE) for k in range(n)]
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=STEP_MS, loop=0, optimize=True)
print(OUT, (W, H), n, 'Bilder', round(os.path.getsize(OUT) / 1e6, 2), 'MB')
frames[0].convert('RGB').save('/home/claude/prev_f0.png')
render(30 * STEP_MS).save('/home/claude/prev_f30.png')
render(120 * STEP_MS).save('/home/claude/prev_f120.png')
