#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_save.py - HANSAVE.DAT 存檔初步分析 (Phase 2)

State: 此為 Phase 2 初版。HANSAVE 版型尚未完全解出(需多個不同存檔比對)。
本工具輸出:
  * 開頭 0x800 文字/結構化視圖
  * 重複出現的郡縣名位置清單(提供區塊週期性線索)
Usage: python parse_save.py [out_dir]
Read-only tool.
"""

import os
import re
import sys

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han\HANSAVE.DAT"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\save"

CITIES = ["遼東", "遼西", "北平", "漁陽", "上谷", "雁門", "九原", "鉅鹿",
          "太原", "北地", "琅琊", "邯鄲", "上黨", "河東", "內史", "隴西",
          "九江", "泗水", "三川", "會稽", "穎川", "南陽", "漢中", "閩中",
          "黔中", "南海", "桂林"]


def dec_window(b, a, z):
    out, i = [], a
    while i < z:
        c = b[i]
        if 0x20 <= c < 0x7F:
            out.append(chr(c))
            i += 1
        elif 0x81 <= c <= 0xFE and i + 1 < z:
            try:
                out.append(bytes(b[i:i + 2]).decode("cp950"))
                i += 2
            except Exception:
                out.append("?")
                i += 1
        else:
            out.append(".")
            i += 1
    return "".join(out)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(outdir, exist_ok=True)
    b = open(BASE, "rb").read()
    L = ["HANSAVE.DAT size=%d (0x%X)" % (len(b), len(b))]
    L.append("== head decode ==")
    t = dec_window(b, 0, 0x300)
    for i in range(0, len(t), 110):
        L.append("%04X %s" % (i, t[i:i + 110]))
    L.append("")
    L.append("== 重複出現的城市名 ==")
    for city in CITIES:
        enc = city.encode("cp950")
        hits = []
        s = 0
        while True:
            j = b.find(enc, s)
            if j < 0:
                break
            hits.append(j)
            s = j + 1
        L.append("%-4s %s" % (city, ", ".join("0x%04X" % x for x in hits)))
    open(os.path.join(outdir, "save_overview.txt"), "w",
         encoding="utf-8").write("\n".join(L))
    print("wrote", os.path.join(outdir, "save_overview.txt"))


if __name__ == "__main__":
    main()
