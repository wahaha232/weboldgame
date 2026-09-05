#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sound_analyzer.py - SONGS.IDX/SONGS.GRP/STANDARD.BNK 分析 (Phase 2)

Verified (2026):
  * SONGS.IDX = 3 x uint32 LE = 各歌曲起點 (0x0000, 0x196D, 0x267E);
    歌曲長 = 下一起點/EOF 差值,三首恰蓋滿 SONGS.GRP。
  * SONGS.GRP 內每首歌為 AdLib 多軌樂譜:
      header "\\roll\\default"; 文字標記 Tempo / "Voix  n" / "Timbre  n" /
      "Volume  n" / "Pitch  n"; 樂器名取自 STANDARD.BNK(trumpet1, piano1,
      bdrum1, snare1, tom1, cymbal1, hihat1); 內含 IEEE float(例 00 00 80 3F = 1.0)。
Usage: python sound_analyzer.py [out_dir]
Read-only tool.
"""

import os
import re
import struct
import sys

BASE = r"D:\VS CODE\PROJECT\hanwebgame\reverse\extracted\han"
OUT = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\sound"


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else OUT
    os.makedirs(outdir, exist_ok=True)
    idx = open(os.path.join(BASE, "SONGS.IDX"), "rb").read()
    grp = open(os.path.join(BASE, "SONGS.GRP"), "rb").read()
    bnk = open(os.path.join(BASE, "STANDARD.BNK"), "rb").read()
    L = []
    L.append("SONGS.IDX size=%d" % len(idx))
    starts = [struct.unpack("<I", idx[i:i + 4])[0] for i in range(0, len(idx), 4)]
    L.append("song starts: %s" % ["0x%04X" % s for s in starts])
    L.append("SONGS.GRP size = 0x%04X" % len(grp))
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(grp)
        L.append("song %d: [0x%04X, 0x%04X) len=%d" % (i, s, e, e - s))

    def findstr(from_o, to_o, pat):
        o = grp.find(pat, from_o, to_o)
        return o

    L.append("")
    for si, s in enumerate(starts):
        e = starts[si + 1] if si + 1 < len(starts) else len(grp)
        seg = grp[s:e]
        L.append("=" * 20)
        L.append("SONG %d  off 0x%04X len %d" % (si, s, e - s))
        # markers
        L.append("  header bytes: %s" % seg[0:16].hex(" "))
        for m in re.finditer(rb"Voix  \d+", seg):
            L.append("    @%04X %s" % (s + m.start(), m.group().decode()))
        # instrument names used in song (strings appearing near 'Timbre')
        used = {}
        for m in re.finditer(rb"[a-z0-9]{4,9}", seg):
            name = m.group().decode()
            if name in ("trumpet1", "piano1", "bdrum1", "snare1", "tom1",
                        "cymbal1", "hihat1", "drum1"):
                used.setdefault(name, []).append(s + m.start())
        for n, offs in used.items():
            L.append("  inst %-9s at %s" % (n, [hex(x) for x in offs]))
        # tempo marker
        t = seg.find(b"Tempo")
        if t >= 0:
            L.append("  'Tempo' @%04X  tail: %s" % (s + t, seg[t:t + 32].hex(" ")))
    # BNK names & count
    names = re.findall(rb"[A-Z]{4,8}1", bnk)
    L.append("")
    L.append("STANDARD.BNK name fields found: %s"
             % [n.decode() for n in names])
    open(os.path.join(outdir, "songs_overview.txt"), "w",
         encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
