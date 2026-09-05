#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_dosbox.py - 對執行中 DOSBox 做讀取:嘗試定位 conventional memory 基底,
再讀取 guest 線性位址內容:
  * 0xB8000 文字畫面(80x25 char+attr)
  * 0x19CB0+0x1F4E 起 1536B(候選調色盤表,6-bit)
  * 0x19CB0 資料段附近取樣
用法: python probe_dosbox.py <pid>
Read-only。
"""

import ctypes
import ctypes.wintypes as w
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40 | 0x80


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", w.DWORD),
                ("__a1", w.DWORD),
                ("RegionSize", ctypes.c_size_t),
                ("State", w.DWORD),
                ("Protect", w.DWORD),
                ("Type", w.DWORD),
                ("__a2", w.DWORD)]


def read(h, addr, size):
    buf = ctypes.create_string_buffer(size)
    rd = ctypes.c_size_t(0)
    if not ctypes.windll.kernel32.ReadProcessMemory(
            h, ctypes.c_void_p(addr), buf, size, ctypes.byref(rd)):
        return None
    return buf.raw[:rd.value]


def ivt_score(b):
    if len(b) < 0x500:
        return -1
    s = 0
    for i in range(0, 0x80, 4):
        off = b[i] | (b[i + 1] << 8)
        seg = b[i + 2] | (b[i + 3] << 8)
        if seg == 0 and off == 0:
            s -= 1
        elif 0x40 <= seg <= 0x9FFF:
            s += 1
    # int 10h vector at 0x40
    s10 = b[0x42] | (b[0x43] << 8)
    if s10 >= 0xC000:
        s += 3
    # int 21h at 0x84
    s21 = b[0x86] | (b[0x87] << 8)
    if 0x40 <= s21 <= 0x9FFF:
        s += 3
    return s


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    if not h:
        print("OpenProcess failed")
        return
    cands = []
    addr = 0
    mbi = MBI()
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                             ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0:
            break
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        if size < 0x50000:
            continue
        data = read(h, mbi.BaseAddress, 0x500)
        if not data:
            continue
        sc = ivt_score(data)
        if sc >= 0:
            cands.append((sc, mbi.BaseAddress))
    cands.sort(reverse=True)
    print("conventional-memory candidates:", [(s, hex(a)) for s, a in cands[:8]])
    # for top candidates check B8000 text & palette segment
    for sc, base in cands[:4]:
        B = base
        text = read(h, B + 0xB8000, 4000)
        pal = read(h, B + 0x19CB0 + 0x1F4E, 1536)
        ds0 = read(h, B + 0x19CB0, 64)
        ok_pal = pal is not None and all(x < 64 for x in pal)
        print("== candidate B=%s sc=%d pal_ok=%s" % (hex(B), sc, ok_pal))
        if pal:
            print("   pal head:", pal[:24].hex(" "))
        if ds0:
            print("   DS0 head:", ds0[:32].hex(" "))
        if text:
            cells = text[:4000]
            rows = []
            for r in range(25):
                line = "".join(chr(cells[r * 160 + c]) if 32 <= cells[r * 160 + c] < 127
                               else (" " if cells[r * 160 + c] == 0 else ".")
                               for c in range(0, 160, 2))
                rows.append(line)
            print("   screen:")
            for ln in rows:
                print("   |%s|" % ln)
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
