#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
basedata_analyzer.py - BASEDATA.001 結構分析 (Phase 2)

Verified layout:
  * 檔頭 ~0x540 之前: header(前 ~0x44 bytes 有意義;其餘 0)
  * 城市表:  0x540 起, 39 筆 x 0x30 (48) bytes
      - name 4 bytes(Big5, 一至二字),後接狀態/屬欄位(待解)
  * 人物表:  0xC90 起, 255 筆 x 0x20 (32) bytes
      - 前 8 bytes = 顯示名(Big5, 以 0x20 補位, 最多 4 字)
      - 後 24 bytes = 屬性/資料(值域含大量 0x00-0xFF, 需 runtime 交叉)
Usage: python basedata_analyzer.py [out_dir]
Read-only tool.
"""

import os
import sys

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han\BASEDATA.001"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\basedata"


def cp(o, b):
    try:
        return b[o:o + 2].decode("cp950")
    except Exception:
        return None


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(outdir, exist_ok=True)
    b = open(BASE, "rb").read()
    L = []
    L.append("BASEDATA.001 size=%d (0x%X)" % (len(b), len(b)))
    L.append("header[0:0x44]: %s" % b[0:0x44].hex(" "))
    L.append("")

    # --- city table ---
    L.append("== City table 0x540, 39 x 0x30 ==")
    for n in range(39):
        o = 0x540 + n * 0x30
        nm = b[o:o + 4].decode("cp950", "replace").strip()
        L.append("%2d 0x%04X %-6s %s" % (n, o, nm,
                                          b[o + 4:o + 0x30].hex(" ")))
    open(os.path.join(outdir, "cities.txt"), "w", encoding="utf-8").write(
        "\n".join(L))
    print("cities:", 39)

    # --- character table ---
    L2 = ["== Character table 0xC90, 255 x 0x20 =="]
    recs = []
    for n in range(255):
        o = 0xC90 + n * 0x20
        name = b[o:o + 8].decode("cp950", "replace").strip()
        # also decode at +0/+2 for 1-char alignment names
        nm2 = b[o + 2:o + 8].decode("cp950", "replace").strip()
        if len(name) == 0 and nm2:
            name = nm2
        recs.append((name, b[o:o + 0x20].hex(" ")))
    for n, (name, hexs) in enumerate(recs):
        L2.append("%3d 0x%04X %-14s %s" % (n, 0xC90 + n * 0x20, name, hexs))
    open(os.path.join(outdir, "characters.txt"), "w",
         encoding="utf-8").write("\n".join(L2))
    print("characters:", 255)
    print("output ->", outdir)


if __name__ == "__main__":
    main()
