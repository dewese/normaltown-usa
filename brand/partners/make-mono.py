#!/usr/bin/env python3
"""Turn a partner's square logo into a white-on-soft-black version.

The brand palette is exactly three colors, so third-party logos get flattened to
white marks on the canvas black before they go on the site. Pure standard library
(no Pillow on this machine): the source PNGs are 8-bit RGBA and not interlaced,
which is the only case this handles.

Each pixel's brightness is mapped onto the line between soft-black and white, so
antialiased edges stay smooth instead of turning into jaggies. `dark` and `light`
are the brightness of the two colors in the source you want to become black and
white; run with --report to see what a file actually contains.

    python3 make-mono.py river.png --dark 10 --light 193
"""
import argparse
import struct
import zlib

BLACK = (0x0F, 0x0F, 0x0F)
WHITE = (0xFF, 0xFF, 0xFF)


def read_png(path):
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    pos, idat, hdr = 8, bytearray(), None
    while pos < len(raw):
        (length,) = struct.unpack(">I", raw[pos:pos + 4])
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", data)
        elif kind == b"IDAT":
            idat += data
        pos += 12 + length
    w, h, depth, color, comp, filt, interlace = hdr
    assert (depth, color, interlace) == (8, 6, 0), f"{path}: need 8-bit RGBA, non-interlaced"
    return w, h, unfilter(zlib.decompress(bytes(idat)), w, h)


def unfilter(data, w, h):
    """Undo the per-scanline PNG filters, returning flat RGBA bytes."""
    stride, out, prev, pos = w * 4, bytearray(), bytearray(w * 4), 0
    for _ in range(h):
        ftype = data[pos]
        line = bytearray(data[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        for x in range(stride):
            a = line[x - 4] if x >= 4 else 0
            b = prev[x]
            c = prev[x - 4] if x >= 4 else 0
            if ftype == 1:
                line[x] = (line[x] + a) & 0xFF
            elif ftype == 2:
                line[x] = (line[x] + b) & 0xFF
            elif ftype == 3:
                line[x] = (line[x] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pred) & 0xFF
        out += line
        prev = line
    return out


def write_png(path, w, h, pixels):
    rows = bytearray()
    for y in range(h):
        rows += b"\x00" + pixels[y * w * 4:(y + 1) * w * 4]   # filter type 0

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))

    path.write_bytes(b"\x89PNG\r\n\x1a\n"
                     + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
                     + chunk(b"IEND", b""))


def brightness(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def report(w, h, px):
    seen = {}
    for i in range(0, len(px), 4):
        if px[i + 3] > 8:
            key = round(brightness(px[i], px[i + 1], px[i + 2]) / 8) * 8
            seen[key] = seen.get(key, 0) + 1
    print(f"{w}x{h}, brightness clusters (value: pixels):")
    for k in sorted(seen, key=lambda k: -seen[k])[:8]:
        print(f"  {k:5.0f}: {seen[k]}")


def fill_holes(px, w, h):
    """Paint enclosed transparent areas white.

    Some logos are a solid shape with the mark knocked out of it (CrowdHealth is an
    orange disc with a heart-shaped hole). Flooding transparency in from the border
    tells the outside of the shape apart from the hole inside it, so the hole can
    become the white mark instead of showing the page through.
    """
    outside = bytearray(w * h)
    stack = [(x, y) for x in range(w) for y in (0, h - 1)]
    stack += [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h):
            continue
        i = y * w + x
        if outside[i] or px[i * 4 + 3] != 0:
            continue
        outside[i] = 1
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    out = bytearray(px)
    for i in range(w * h):
        if px[i * 4 + 3] == 0 and not outside[i]:
            out[i * 4:i * 4 + 4] = bytes(WHITE) + b"\xff"
    return out


def monochrome(px, dark, light):
    out = bytearray(px)
    span = max(1.0, light - dark)
    for i in range(0, len(px), 4):
        if px[i + 3] == 0:
            continue
        t = min(1.0, max(0.0, (brightness(px[i], px[i + 1], px[i + 2]) - dark) / span))
        for c in range(3):
            out[i + c] = round(BLACK[c] + (WHITE[c] - BLACK[c]) * t)
    return out


if __name__ == "__main__":
    import pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--dark", type=float, default=0.0)
    ap.add_argument("--light", type=float, default=255.0)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--fill-holes", action="store_true",
                    help="paint enclosed transparent areas white (knocked-out marks)")
    a = ap.parse_args()
    src = pathlib.Path(a.src)
    w, h, px = read_png(src)
    if a.report:
        report(w, h, px)
    else:
        if a.fill_holes:
            px = fill_holes(px, w, h)
        write_png(pathlib.Path(a.out or a.src), w, h, monochrome(px, a.dark, a.light))
        print(f"wrote {a.out or a.src} ({w}x{h})")
