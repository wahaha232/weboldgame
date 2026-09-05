#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hex_dump.py - simple hex dump generator (offset : hex : ascii).

Usage:
    python hex_dump.py <file> <start_hex_or_dec> <length> [out_file]
    e.g. python hex_dump.py HAN.EXE 0 256
         python hex_dump.py PICS.GRP 0x0 0x80 dump.txt
Read-only tool. Phase 1 - File Forensics.
"""

import sys


def dump(path, start, length):
    with open(path, "rb") as f:
        f.seek(start)
        data = f.read(length)
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hexs = " ".join("%02X" % x for x in chunk)
        hexs = hexs.ljust(47)
        asc = "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)
        lines.append("%08X  %s  %s" % (start + i, hexs, asc))
    return "\n".join(lines), len(data)


def _parse_num(s):
    return int(s, 16) if s.lower().startswith("0x") else int(s)


if __name__ == "__main__":
    if len(sys.argv) not in (4, 5):
        raise SystemExit("usage: hex_dump.py <file> <start> <length> [out]")
    p = sys.argv[1]
    st = _parse_num(sys.argv[2])
    ln = _parse_num(sys.argv[3])
    text, got = dump(p, st, ln)
    print("== %s @0x%X len=%d (read %d bytes) ==" % (p, st, ln, got))
    print(text)
    if len(sys.argv) == 5:
        with open(sys.argv[4], "w", encoding="utf-8") as f:
            f.write("== %s @0x%X len=%d (read %d bytes) ==\n%s\n"
                    % (p, st, ln, got, text))
        print("saved -> %s" % sys.argv[4])
