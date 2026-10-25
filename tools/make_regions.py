"""Turn the Stitch region art into art/regions.js (data URIs, so the game runs from a double-click).

Usage:
    python tools/make_regions.py

Reads   ../الصور  و الشخصيات/المناطق/<city folder>/*/screen.png
Writes  art/regions.js  ->  window.SAIFMAN_REGIONS[id] = { street, sky, skyTop, horizon }
  street : the runner street scene (lobby card picture)
  sky    : the skyline panorama with its flat bottom strip cropped off (3D backdrop)
Needs Pillow (pip install pillow).
"""
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT.parent / 'الصور  و الشخصيات' / 'المناطق'

# game id -> source folder
CITIES = {
    'riyadh': 'الرياض جديد',
    'jeddah': 'جده مدينة',
    'dammam': 'مدينة الدمام',
    'makkah': 'مكة',
    'alula': 'العلا',
    'jazan': 'جازان',
    'madinah': 'المدينة المنورة',
    'abha': 'ابها 2',
    'tabuk': 'تبوك',
    'neom': 'نيوم',
}


def find(folder, *keys):
    for p in sorted((SRC / folder).glob('*/screen.png')):
        if any(k in p.parent.name for k in keys):
            return p
    raise SystemExit(f'missing image in {folder}: {keys}')


def horizon_row(img):
    """Rows at the bottom of the panoramas are a flat band; return the first row of that band."""
    g = img.convert('L')
    w, h = g.size
    std = [ImageStat.Stat(g.crop((0, y, w, y + 1))).stddev[0] for y in range(h)]
    y = h - 1
    while y > h * 0.5 and std[y] < 14:      # walk up through the flat band (and its edge lines)
        y -= 1
    # skip thin rule lines between band and art
    while y > h * 0.5 and min(std[y - 3:y + 1]) < 14:
        y -= 1
    return y + 1


def data_uri(img, width, quality):
    img = img.convert('RGB')
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def hex_color(img, box):
    r, g, b = [round(v) for v in ImageStat.Stat(img.convert('RGB').crop(box)).mean]
    return f'#{r:02x}{g:02x}{b:02x}'


def main():
    out = {}
    for cid, folder in CITIES.items():
        street = Image.open(find(folder, 'street'))
        sky = Image.open(find(folder, 'skyline', 'panoramic'))
        cut = horizon_row(sky)
        sky = sky.crop((0, 0, sky.width, cut))
        out[cid] = {
            'street': data_uri(street, 720, 78),
            'sky': data_uri(sky, 1376, 82),
            'skyTop': hex_color(sky, (0, 0, sky.width, 12)),
            'horizon': hex_color(sky, (0, round(cut * 0.55), sky.width, round(cut * 0.62))),
            'aspect': round(sky.width / sky.height, 4),
        }
        print(f'{cid:7s} sky cut at {cut}/{768}  aspect {out[cid]["aspect"]}  top {out[cid]["skyTop"]}  horizon {out[cid]["horizon"]}')
    art = ROOT / 'art'
    art.mkdir(exist_ok=True)
    (art / 'regions.js').write_text(
        '/* SAiFMaN region art (Stitch), made by tools/make_regions.py. */\n'
        f'window.SAIFMAN_REGIONS = {json.dumps(out)};\n', encoding='utf-8')
    print(f'wrote art/regions.js ({(art / "regions.js").stat().st_size / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
