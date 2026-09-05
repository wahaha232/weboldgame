#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_pics.py - PICS.GRP/PICS.IDX 解出工具 (Phase 2)

Format (verified in Phase 1):
  PICS.IDX : 17 x { uint32 start, uint32 end }   (LE)
  PICS.GRP : concat of pictures; each picture =
             uint16 width | uint16 height | raw 8-bit indexed pixels (w*h)

Usage:
  python extract_pics.py [--pal pal.bin] [--out dir]
Output:
  dumps/pics/pic_NN_WxH.png (default P-mode w/ grayscale palette,
  or with real RGB palette if provided)
Read-only tool. 原始檔案不修改。
"""

import os
import struct
import sys

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\pics"


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
    idx = open(os.path.join(BASE, "PICS.IDX"), "rb").read()
    grp = open(os.path.join(BASE, "PICS.GRP"), "rb").read()
    if not pal:
        pal = _grey_pal()
    else:
        if len(pal) < 768:
            print("[warn] palette < 768 bytes")
    entries = []
    for i in range(0, len(idx), 8):
        entries.append(struct.unpack("<II", idx[i:i + 8]))
    print("pictures:", len(entries), " grp_size:", len(grp))
    for n, (a, b) in enumerate(entries):
        w, h = struct.unpack("<HH", grp[a:a + 4])
        px = grp[a + 4:b]
        if len(px) != w * h:
            print("!! pic%02d size mismatch" % n)
            continue
        from PIL import Image
        im = Image.new("P", (w, h))
        im.putdata(px)
        im.putpalette(pal[:768] if len(pal) >= 768 else _grey_pal())
        fn = os.path.join(outdir, "pic_%02d_%dx%d.png" % (n, w, h))
        im.save(fn)
        print("saved", fn)
    # 原始資料另存(不影響原檔)以便後續重新上色
    open(os.path.join(outdir, "pics_raw.bin"), "wb").write(grp)
    print("raw copy kept at", os.path.join(outdir, "pics_raw.bin"))


if __name__ == "__main__":
    main()
