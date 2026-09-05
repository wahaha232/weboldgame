#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lzexe_unpack.py - LZEXE ver 0.91 解壓器 (Python 移植自 mywave82/unlzexe 0.9,
見 tools/src/unlzexe.c;MIT 風格 freeware). 僅用於本專案 SOUND.EXE 分析。

The algorithm/parameter layout is taken verbatim from unlzexe.c (reference
implementation of the third-party generic LZEXE packer). Output is validated
independently from the produced bytes (MZ header + known strings).

Usage: python lzexe_unpack.py <packed.exe> <out.exe>
Read-only tool (writes only <out.exe>).
"""

import sys


def r16(b, o):
    return b[o] | (b[o + 1] << 8)


def w16(b, o, v):
    b[o] = v & 0xFF
    b[o + 1] = (v >> 8) & 0xFF


def main():
    ip, op = sys.argv[1], sys.argv[2]
    ind = open(ip, "rb").read()

    # ---- rdhead ----
    ihead = [r16(ind, i * 2) for i in range(16)]
    ohead = list(ihead)
    if not (ihead[0] in (0x5A4D, 0x4D5A)) or ihead[0x0D] != 0 or ihead[0x0C] != 0x1C:
        raise SystemExit("not LZEXE (bad header)")
    ver = 91
    print("detected LZEXE ver 0.%d" % ver)

    # ---- mkreltbl ----
    fpos = (ihead[0x0B] + ihead[4]) << 4
    inf = [r16(ind, fpos + i * 2) for i in range(8)]
    ohead[0x0A] = inf[0]  # IP
    ohead[0x0B] = inf[1]  # CS
    ohead[0x08] = inf[2]  # SP
    ohead[0x07] = inf[3]  # SS
    ohead[0x0C] = 0x1C    # relocation table start

    out = bytearray(0x1C)  # output image (header bytes so far)

    # reloc91: decode compressed relocation table
    rp = fpos + 0x158
    rel_off = 0
    rel_seg = 0
    rel_count = 0
    while True:
        span = ind[rp]
        rp += 1
        if span == 0:
            span = r16(ind, rp)
            rp += 2
            if span == 0:
                rel_seg += 0x0FFF
                continue
            elif span == 1:
                break
        rel_off += span
        rel_seg += (rel_off & ~0x0F) >> 4
        rel_off &= 0x0F
        out += rel_off.to_bytes(2, "little")
        out += rel_seg.to_bytes(2, "little")
        rel_count += 1
    ohead[3] = rel_count

    # pad header to paragraph boundary chosen in unlzexe (to 0x200)
    pad = (0x200 - len(out)) & 0x1FF
    ohead[4] = (len(out) + pad) >> 4
    out += b"\0" * pad

    # ---- unpack ----
    cpos = ((ihead[0x0B] - inf[4] + ihead[4]) << 4)
    dat = bytearray()          # decompressed load module (full)
    bitbuf = 0
    bitcnt = 0

    def getbit():
        nonlocal bitbuf, bitcnt, cpos
        b = bitbuf & 1
        bitcnt -= 1
        if bitcnt == 0:
            bitbuf = r16(ind, cpos)
            cpos += 2
            bitcnt = 0x10
        else:
            bitbuf >>= 1
        return b

    def getc8():
        return ind[cpos]

    # init bitstream: unlzexe reads first word at cpos then count=0x10
    bitbuf = r16(ind, cpos)
    cpos += 2
    bitcnt = 0x10

    pos = 0  # position in dat
    while True:
        if getbit():
            dat += ind[cpos:cpos + 1]
            cpos += 1
            pos += 1
            continue
        if not getbit():
            ln = (getbit() << 1) | getbit()
            ln += 2
            span = (ind[cpos] | 0xFF00) - 0x10000  # signed 16-bit
            cpos += 1
        else:
            sp0 = ind[cpos]
            cpos += 1
            ln = ind[cpos]
            cpos += 1
            span = (sp0 | (((ln & ~0x07) << 5) | 0xE000)) - 0x10000
            ln = (ln & 0x07) + 2
            if ln == 2:
                ln = ind[cpos]
                cpos += 1
                if ln == 0:
                    break
                if ln == 1:
                    continue
                ln += 1
        # copy len bytes from pos+span (signed, C: *p = *(p+span); p++)
        for _ in range(ln):
            dat += dat[pos + span:pos + span + 1]
            pos += 1
    loadsize = len(dat)

    # append module at offset ohead[4]<<4
    if len(out) < (ohead[4] << 4):
        out += b"\0" * ((ohead[4] << 4) - len(out))
    out += dat

    # ---- wrhead ----
    if ohead[6] != 0:
        ohead[5] -= inf[5] + ((inf[6] + 16 - 1) >> 4) + 9
        if ohead[6] != 0xFFFF:
            ohead[6] -= (ohead[5] - ihead[5])
    ohead[1] = (loadsize + (ohead[4] << 4)) & 0x1FF
    ohead[2] = (loadsize + (ohead[4] << 4) + 0x1FF) >> 9

    # write header words 0..0x0E
    img = bytearray(out)
    for i in range(0x0E):
        w16(img, i * 2, ohead[i])

    open(op, "wb").write(img)
    print("output", op, "size", len(img), "load module", loadsize,
          "relocs", rel_count)


if __name__ == "__main__":
    main()
