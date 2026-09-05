#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inventory.py - Phase 1 File Forensics inventory generator.

For every file under a given directory, this tool records:
  - filename / extension / size
  - SHA-256, MD5, CRC32
  - first 64 bytes HEX
  - ASCII strings (printable runs >= 4 chars)
  - Big5(CP950)/Chinese strings (CJK runs >= 2 chars)
  - MZ executable check (magic + minimal header sanity)

Output : markdown file (default target reverse/reports/file_inventory.md)
Usage  : python inventory.py <files_dir> <out_md>
Read-only with respect to the game files.
"""

import hashlib
import os
import re
import struct
import sys
import zlib

MIN_ASCII = 4
MIN_CJK = 2
MAX_ASCII = 60
MAX_CJK = 80
MAX_STR_LEN = 200


def sha256(b): return hashlib.sha256(b).hexdigest()
def md5(b): return hashlib.md5(b).hexdigest()
def crc32(b): return "%08X" % (zlib.crc32(b) & 0xFFFFFFFF)


def ascii_strings(b):
    found = re.findall(rb"[\x20-\x7e]{%d,}" % MIN_ASCII, b)
    seen, out = set(), []
    for s in found:
        t = s.decode("latin1")
        if t in seen:
            continue
        seen.add(t)
        out.append(t[:MAX_STR_LEN])
    return out[:MAX_ASCII]


def big5_strings(b):
    text = b.decode("cp950", errors="replace")
    out = []
    for m in re.finditer(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]{2,}", text):
        s = m.group(0)
        if "\ufffd" in s:
            continue
        out.append(s[:MAX_STR_LEN])
    return out[:MAX_CJK]


def first64_hex(b):
    return b[:64].hex(" ").upper()


def mz_check(b):
    if b[:2] != b"MZ":
        return None, None
    if len(b) < 0x40:
        return "invalid(too short)", None
    hdr_paras = struct.unpack("<H", b[8:10])[0]
    if hdr_paras == 0 or hdr_paras * 16 > len(b):
        return "MZ(invalid header size)", None
    info = {
        "e_cblp": struct.unpack("<H", b[2:4])[0],
        "e_cp": struct.unpack("<H", b[4:6])[0],
        "e_crlc": struct.unpack("<H", b[6:8])[0],
        "e_cparhdr": hdr_paras,
        "e_minalloc": struct.unpack("<H", b[10:12])[0],
        "e_maxalloc": struct.unpack("<H", b[12:14])[0],
        "e_ss": struct.unpack("<H", b[14:16])[0],
        "e_sp": struct.unpack("<H", b[16:18])[0],
        "e_csum": struct.unpack("<H", b[18:20])[0],
        "e_ip": struct.unpack("<H", b[20:22])[0],
        "e_cs": struct.unpack("<H", b[22:24])[0],
        "e_lfarlc": struct.unpack("<H", b[24:26])[0],
        "e_ovno": struct.unpack("<H", b[26:28])[0],
        "e_lfanew": struct.unpack("<i", b[0x3C:0x40])[0],
    }
    return "MZ/DOS-EXE(valid header)", info


def _looks_text(b, sample=2048):
    s = b[:sample]
    try:
        s.decode("ascii")
        return True
    except UnicodeDecodeError:
        pass
    nonprint = sum(1 for x in s if x < 9 or (13 < x < 32) or x > 126)
    return nonprint < len(s) * 0.15


def scan_dir(root):
    entries = []
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, root)
            with open(p, "rb") as fh:
                entries.append((rel, fh.read()))
    return entries


def rel_hex_dump(b, n=64):
    h = b[:n].hex(" ").upper()
    return [h[i:i + 48] for i in range(0, len(h), 48)]


def main():
    root, out_md = sys.argv[1], sys.argv[2]
    L = []
    L.append("# 檔案 Inventory — 《楚漢之爭》原始 DOS 檔案 (Phase 1 FILE FORENSICS)\n")
    L.append("> 產出工具: `reverse/tools/inventory.py` | 資料來源: `reverse/extracted/`")
    L.append("> 所有判讀僅為 binary evidence 之初步觀察；正式結論標記於 hypotheses/。\n")
    rows = []
    for rel, b in scan_dir(root):
        mz_res, mz_info = mz_check(b)
        rows.append((rel, b, mz_res, mz_info))

    L.append("## 總表\n")
    L.append("| 檔案 | 大小 | SHA-256 | MD5 | CRC32 | MZ |")
    L.append("|---|---|---|---|---|---|")
    for rel, b, mz_res, _ in rows:
        L.append("| `%s` | %d | `%s` | `%s` | `%s` | %s |"
                 % (rel.replace("|", "/"), len(b), sha256(b), md5(b),
                    crc32(b), mz_res if mz_res else "否"))
    L.append("")

    for rel, b, mz_res, mz_info in rows:
        ext = rel.rsplit(".", 1)[-1].upper() if "." in rel else "(無)"
        L.append("---\n")
        L.append("## %s\n" % rel)
        L.append("- 副檔名: `%s` | 大小: %d bytes" % (ext, len(b)))
        L.append("- SHA-256: `%s`" % sha256(b))
        L.append("- MD5: `%s`" % md5(b))
        L.append("- CRC32: `%s`" % crc32(b))
        L.append("- 前 64 bytes HEX:\n")
        for seg in rel_hex_dump(b):
            L.append("  `%s`" % seg)
        L.append("")
        if mz_res:
            L.append("- MZ 檢查: **%s**" % mz_res)
            if mz_info:
                L.append("  - `e_cblp=%d e_cp=%d reloc_items=%d header_paras=%d "
                         "minalloc=%d maxalloc=%d SS=%04X SP=%04X IP=%04X "
                         "CS=%04X lfarlc=%04X ovno=%d e_lfanew=%s`" % (
                             mz_info["e_cblp"], mz_info["e_cp"],
                             mz_info["e_crlc"], mz_info["e_cparhdr"],
                             mz_info["e_minalloc"], mz_info["e_maxalloc"],
                             mz_info["e_ss"], mz_info["e_sp"], mz_info["e_ip"],
                             mz_info["e_cs"], mz_info["e_lfarlc"],
                             mz_info["e_ovno"], mz_info["e_lfanew"]))
        else:
            L.append("- MZ 檢查: 否 (前2 bytes = `%s`)" % b[:2].hex().upper())
        a_s = ascii_strings(b)
        c_s = big5_strings(b)
        if a_s:
            L.append("- ASCII strings (%d 筆, 顯示前 %d):"
                     % (len(a_s), min(len(a_s), MAX_ASCII)))
            for s in a_s[:MAX_ASCII]:
                L.append("  - `%s`" % s.replace("`", "'"))
        else:
            L.append("- ASCII strings: (無)")
        if c_s:
            L.append("- Big5/中文 strings (%d 筆, 顯示前 %d):"
                     % (len(c_s), min(len(c_s), MAX_CJK)))
            for s in c_s[:MAX_CJK]:
                L.append("  - `%s`" % s.replace("`", "'"))
        else:
            L.append("- Big5/中文 strings: (無)")
        L.append("")

    os.makedirs(os.path.dirname(out_md), exist_ok=True)
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("Wrote %s (%d files)" % (out_md, len(rows)))


if __name__ == "__main__":
    main()

