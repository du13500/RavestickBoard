"""Baut das Lieferpaket als ZIP aus einer festen Dateiliste statt aus dem ganzen Ordner.
Hinein kommen nur Dateien, die git kennt (versioniert oder neu und nicht ignoriert), und unter firmware/ nur der
angegebene Firmware-Ordner. So geraten keine lokalen Dateien (Diagnosen, Exporte, Zwischenstände) ins Paket.
Aufruf: python tools/zip_paket.py <Firmware-Ordner, z. B. RavestickBoard_v0_7_1> <Ziel.zip>"""
import subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPERRE = ('__pycache__/', '.DS_Store', 'Thumbs.db', '.env', 'secrets.h', 'config.local.h')
ENDUNG_SPERRE = ('.bin', '.elf', '.map', '.log', '.tmp', '.bak', '.pyc')


def dateiliste(fw):
    git = lambda *a: subprocess.run(['git', '-C', str(ROOT), *a], check=True, capture_output=True, text=True).stdout.splitlines()
    namen = set(git('ls-files')) | set(git('ls-files', '--others', '--exclude-standard'))
    out = []
    for n in sorted(namen):
        if not (ROOT / n).is_file():
            continue                                   # gelöscht, aber noch im Index
        if n.startswith('firmware/') and not n.startswith(f'firmware/{fw}/'):
            continue
        if any(s in n for s in SPERRE) or n.endswith(ENDUNG_SPERRE):
            continue
        out.append(n)
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    fw, ziel = sys.argv[1], Path(sys.argv[2])
    if not (ROOT / 'firmware' / fw).is_dir():
        sys.exit(f'Firmware-Ordner fehlt: firmware/{fw}')
    liste = dateiliste(fw)
    if not any(n.startswith(f'firmware/{fw}/') and n.endswith('.ino') for n in liste):
        sys.exit('Im Firmware-Ordner liegt kein Sketch (.ino).')
    with zipfile.ZipFile(ziel, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in liste:
            z.write(ROOT / n, n)
    print(f'{len(liste)} Dateien -> {ziel}')


if __name__ == '__main__':
    main()
