"""Compress a Tripo GLB and wrap it as a .js file so the game runs from a double-click.

Usage:
    python tools/wrap_model.py <input.glb> [--id saifman] [--max 1024]

Writes models/<id>.glb (textures shrunk to --max px) and models/<id>.js, which sets
window.SAIFMAN_MODELS[id] to the base64 GLB. Needs Pillow (pip install pillow).
"""
import argparse
import base64
import io
import json
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def read_glb(data):
    magic, version, _ = struct.unpack_from('<III', data, 0)
    if magic != 0x46546C67 or version != 2:
        raise SystemExit('Not a glTF 2.0 binary (.glb) file')
    off, doc, binary = 12, None, b''
    while off < len(data):
        length, kind = struct.unpack_from('<II', data, off)
        chunk = data[off + 8: off + 8 + length]
        if kind == 0x4E4F534A:
            doc = json.loads(chunk.decode('utf-8'))
        elif kind == 0x004E4942:
            binary = chunk
        off += 8 + length
    return doc, binary


def write_glb(doc, binary):
    js = json.dumps(doc, separators=(',', ':')).encode('utf-8')
    js += b' ' * (-len(js) % 4)
    binary += b'\0' * (-len(binary) % 4)
    total = 12 + 8 + len(js) + 8 + len(binary)
    return (struct.pack('<III', 0x46546C67, 2, total)
            + struct.pack('<II', len(js), 0x4E4F534A) + js
            + struct.pack('<II', len(binary), 0x004E4942) + binary)


def shrink(raw, max_px):
    img = Image.open(io.BytesIO(raw))
    img.load()
    if max(img.size) > max_px:
        img.thumbnail((max_px, max_px), Image.LANCZOS)
    out = io.BytesIO()
    has_alpha = img.mode in ('RGBA', 'LA') and img.getchannel('A').getextrema()[0] < 255
    if has_alpha:
        img.save(out, 'PNG', optimize=True)
        return out.getvalue(), 'image/png'
    img.convert('RGB').save(out, 'JPEG', quality=85, optimize=True)
    return out.getvalue(), 'image/jpeg'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('--id', default='saifman')
    ap.add_argument('--max', type=int, default=1024)
    args = ap.parse_args()

    src = Path(args.input).read_bytes()
    doc, binary = read_glb(src)
    views = doc.get('bufferViews', [])

    # new bytes for every bufferView (images re-encoded, the rest copied)
    chunks = [binary[v.get('byteOffset', 0): v.get('byteOffset', 0) + v['byteLength']] for v in views]
    for im in doc.get('images', []):
        if 'bufferView' in im:
            chunks[im['bufferView']], im['mimeType'] = shrink(chunks[im['bufferView']], args.max)

    out = bytearray()
    for v, data in zip(views, chunks):
        out += b'\0' * (-len(out) % 4)
        v['byteOffset'], v['byteLength'] = len(out), len(data)
        out += data
    if doc.get('buffers'):
        doc['buffers'][0]['byteLength'] = len(out)

    glb = write_glb(doc, bytes(out))
    models = ROOT / 'models'
    models.mkdir(exist_ok=True)
    (models / f'{args.id}.glb').write_bytes(glb)
    clips = [a.get('name', '?') for a in doc.get('animations', [])]
    (models / f'{args.id}.js').write_text(
        f'/* {args.id} 3D model (Tripo, clips: {", ".join(clips) or "none"}), embedded so the game also runs from a double-click. */\n'
        f'(window.SAIFMAN_MODELS = window.SAIFMAN_MODELS || {{}})["{args.id}"] = "{base64.b64encode(glb).decode()}";\n',
        encoding='utf-8')
    print(f'{len(src) / 1e6:.1f} MB -> {len(glb) / 1e6:.1f} MB, clips: {clips}')
    print(f'wrote models/{args.id}.glb and models/{args.id}.js')


if __name__ == '__main__':
    main()
