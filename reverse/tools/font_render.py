#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
font_render.py - 字型解碼/輸出 (Phase 2)

Hypotheses under test:
  YING.PAT  : 128 glyphs x 16 bytes = 8x16 bitmap (1 byte/row)
  ZHONG.PAT : 591 glyphs x 32 bytes = 16x16 bitmap (2 bytes/row)
  ZHONG.COD : 591 x 2 bytes (code table - semantic TBD)

Output: dumps/font/ying_8x16.png, dumps/font/zhong_16x16.png (contact sheets)
Usage:  python font_render.py
Read-only tool.
"""

import os

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\font"


def to_img_rows(rows, w, scale=3):
    from PIL import Image
    h = len(rows)
    im = Image.new("L", (w * scale, h * scale), 0)
    pix = im.load()
    for y, row in enumerate(rows):
        for x in range(w):
            v = 255 if ((row >> (w - 1 - x)) & 1) else 0
            for dy in range(scale):
                for dx in range(scale):
                    pix[x * scale + dx, y * scale + dy] = v
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    from PIL import Image

    # ---- YING.PAT 8x16 ----
    ying = open(os.path.join(BASE, "YING.PAT"), "rb").read()
    n = len(ying) // 16
    print("YING.PAT glyphs:", n, "(16B each)")
    cols = 16
    rows_n = (n + cols - 1) // cols
    cell_w, cell_h = 8, 16
    sheet = Image.new("L", (cols * cell_w, rows_n * cell_h), 64)
    for g in range(n):
        rowbytes = ying[g * 16:g * 16 + 16]
        bitrows = [int.from_bytes(rowbytes[y:y + 1], "little") for y in range(16)]
        gl = to_img_rows(bitrows, 8, 1)
        sheet.paste(gl, ((g % cols) * cell_w, (g // cols) * cell_h))
    sheet.save(os.path.join(OUT, "ying_8x16.png"))
    print("saved ying sheet")

    # ---- ZHONG.PAT 16x16 ----
    zhong = open(os.path.join(BASE, "ZHONG.PAT"), "rb").read()
    nz = len(zhong) // 32
    print("ZHONG.PAT glyphs:", nz, "(32B each)")
    cols = 16
    rows_n = (nz + cols - 1) // cols
    cell_w, cell_h = 16, 16
    sheet = Image.new("L", (cols * cell_w, rows_n * cell_h), 64)
    for g in range(nz):
        rowbytes = zhong[g * 32:g * 32 + 32]
        bitrows = []
        for y in range(16):
            hi = rowbytes[y * 2]
            lo = rowbytes[y * 2 + 1]
            bitrows.append((hi << 8) | lo)
        gl = to_img_rows(bitrows, 16, 1)
        sheet.paste(gl, ((g % cols) * cell_w, (g // cols) * cell_h))
    sheet.save(os.path.join(OUT, "zhong_16x16.png"))
    print("saved zhong sheet")

    # ZHONG.COD 資料傾印(head) 供分析
    cod = open(os.path.join(BASE, "ZHONG.COD"), "rb").read()
    with open(os.path.join(OUT, "zhong_cod_analysis.txt"), "w", encoding="utf-8") as f:
        f.write("ZHONG.COD size=%d => %d x uint16\n" % (len(cod), len(cod) // 2))
        for i in range(min(len(cod) // 2, 591)):
            v = int.from_bytes(cod[i * 2:i * 2 + 2], "little")
            f.write("%3d %04X\n" % (i, v))
    print("saved zhong_cod analysis")


if __name__ == "__main__":
    main()
