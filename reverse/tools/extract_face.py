#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_face.py - FACE.GRP 頭像解出工具 (Phase 2)

Verified structure (Phase 2):
  FACE.GRP = 78 portraits, each =
             uint16 width(=48) | uint16 height(=48) | raw 8-bit indexed (48*48)
  180,024 bytes = 78 * (4 + 2304)  -> exact.

Usage:
  python extract_face.py [--pal pal.bin] [--out dir]
Output: dumps/face/face_YY.png 及 dumps/face/faces_grid.png
Read-only tool.
"""

import os
import struct
import sys

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\face"


def _grey_pal():
    return bytes(v for i in range(256) for v in (i, i, i))


def main():
    args = sys.argv[1:]
    pal = None
    outdir = OUT
    for i, a in enumerate(args):
        if a == "--pal":
            pal = open(args[i + 1], "rb").read()
        elif a == "--out":
            outdir = args[i + 1]
    os.makedirs(outdir, exist_ok=True)
    data = open(os.path.join(BASE, "FACE.GRP"), "rb").read()
    if not pal:
        pal = _grey_pal()
    nfaces = 0
    off = 0
    from PIL import Image
    frames = []
    while off + 4 <= len(data):
        w, h = struct.unpack("<HH", data[off:off + 4])
        need = 4 + w * h
        if off + need > len(data):
            break
        px = data[off + 4:off + need]
        frames.append((off, w, h, px))
        off += need
    print("parsed faces:", len(frames))
    for n, (o, w, h, px) in enumerate(frames):
        im = Image.new("P", (w, h))
        im.putdata(px)
        im.putpalette(pal[:768] if len(pal) >= 768 else _grey_pal())
        fn = os.path.join(outdir, "face_%02d.png" % n)
        im.save(fn)
        # keep full color frame in memory for the grid
        im = im.convert("RGB")
        frames[n] = (o, w, h, px, im)
    # contact sheet 13 x 6
    cols, rows = 13, 6
    cw, ch = 48, 48
    sheet = Image.new("RGB", (cols * cw, rows * ch), (40, 40, 48))
    for n, (o, w, h, px, im) in enumerate(frames):
        x = (n % cols) * cw
        y = (n // cols) * ch
        sheet.paste(im, (x, y))
    sheet.save(os.path.join(outdir, "faces_grid.png"))
    print("saved", len(frames), "faces + grid")
    open(os.path.join(outdir, "face_raw.bin"), "wb").write(data)


if __name__ == "__main__":
    main()
