#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
list_rar.py - RAR4 (magic 52 61 72 21 1A 07 00) archive header parser.
Walks the archive block chain WITHOUT decompressing; lists every file entry
(packed/unpacked size, method, host OS, CRC, name) and detects encryption.

Usage:
    python list_rar.py <archive.rar>

Read-only tool. Phase 1 - File Forensics for 《楚漢之爭》 project.
"""

import struct
import sys

RAR4_MAGIC = b"Rar!\x1a\x07\x00"
HOST_OS = {0: "DOS", 1: "OS/2", 2: "Win32", 3: "Unix", 4: "MacOS", 5: "BeOS"}


def _crc32(block):
    crc = 0xFFFFFFFF
    for b in block:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ (0xEDB88320 if (crc & 1) else 0)
    return crc & 0xFFFFFFFF


def _decode_unicode_name(b):
    """RAR LHD_UNICODE: byte0 = count of bytes XORed against UTF-16 low bytes."""
    try:
        if not b:
            return ""
        xor_len = b[0]
        if xor_len == 0:
            return b.decode("cp437", errors="replace")
        high = (xor_len + 1) // 2
        utf16 = b[1:]
        low = b[1 + high:]
        raw = bytearray()
        for i in range(xor_len):
            raw.append(low[i] ^ utf16[i * 2])
        return raw.decode("utf-16-le", errors="replace")
    except Exception:
        return b.decode("cp437", errors="replace")


def parse(path):
    data = open(path, "rb").read()
    if not data.startswith(RAR4_MAGIC):
        raise SystemExit("Not a RAR4 archive (magic mismatch).")

    print("== RAR4 archive ==")
    print("File         : %s" % path)
    print("Size (bytes) : %d" % len(data))
    print("Magic        : %s" % RAR4_MAGIC.hex(" "))

    off = len(RAR4_MAGIC)
    total = 0
    while off + 7 <= len(data):
        head_type = data[off + 2]
        head_flags = struct.unpack("<H", data[off + 3:off + 5])[0]
        head_size = struct.unpack("<H", data[off + 5:off + 7])[0]
        if head_size < 7:
            print("  [warn] bad head_size=%d at off=%d -> stop" % (head_size, off))
            break
        computed = _crc32(data[off + 2:off + head_size])
        stored = struct.unpack("<H", data[off:off + 2])[0]
        crc_ok = (computed & 0xFFFF) == stored
        label = {0x72: "MAIN", 0x73: "FILE", 0x74: "FILE", 0x77: "SUB",
                 0x78: "NEWSUB", 0x79: "ENDARC"}.get(
                     head_type, "TYPE_0x%02X" % head_type)

        if head_type in (0x73, 0x74):
            pos = off + 7
            pack_size, unp_size, host_os, file_crc, ftime = struct.unpack(
                "<IIBII", data[pos:pos + 17])
            method = data[pos + 18]
            unp_ver = data[pos + 17]
            name_size = struct.unpack("<H", data[pos + 19:pos + 21])[0]
            attr = struct.unpack("<I", data[pos + 21:pos + 25])[0]
            name_bytes = data[pos + 25:pos + 25 + name_size]
            if head_flags & 0x0100:  # LHD_LARGE: 8-byte sizes appended
                pack_size, unp_size = struct.unpack(
                    "<QQ", data[pos + 25:pos + 41])
                name_bytes = data[pos + 41:pos + 41 + name_size]
            name = name_bytes.decode("cp437", errors="replace")
            if head_flags & 0x0200:
                name = _decode_unicode_name(name_bytes)
            flags_s = []
            if head_flags & 0x0001:
                flags_s.append("SPLIT_BEFORE")
            if head_flags & 0x0002:
                flags_s.append("SPLIT_AFTER")
            if head_flags & 0x0004:
                flags_s.append("ENCRYPTED")
            if head_flags & 0x0010:
                flags_s.append("SOLID")
            if head_flags & 0x0100:
                flags_s.append("LARGE")
            method_s = {0x30: "store", 0x31: "fastest", 0x32: "fast",
                        0x33: "normal", 0x34: "good", 0x35: "best"}.get(
                            method, "0x%02X" % method)
            print("  FILE  %-30s packed=%-7d unpacked=%-8d method=%-7s "
                  "crc=%08X os=%s unp_ver=%d attr=%08X flags=%s" %
                  (name[:30], pack_size, unp_size, method_s, file_crc,
                   HOST_OS.get(host_os, "?"), unp_ver, attr,
                   ",".join(flags_s) if flags_s else "-"))
            total += 1
        else:
            print("  %-30s head_size=%-5d crc_ok=%s" % (label, head_size, crc_ok))

        off += head_size
        if head_type in (0x79, 0x7B):
            print("  ENDARC: archive end reached")
            break
    print("== total file entries: %d ==" % total)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python list_rar.py <archive.rar>")
    parse(sys.argv[1])

