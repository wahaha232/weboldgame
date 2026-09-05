#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_dosbox_mem.py - 掃描 DOSBox-X 行程記憶體,找已知檔案內容/字串的
runtime 位置,用以推導「file offset ↔ runtime 段」映射。

Usage: python scan_dosbox_mem.py <pid>
Read-only (OpenProcess + VirtualQueryEx + ReadProcessMemory).
"""

import ctypes
import ctypes.wintypes as w
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40 | 0x80

TARGETS = [
    ("basedata.001", b"basedata.001"),
    ("PICS.IDX", b"PICS.IDX"),
    ("SOUND-DRIVER-AD-LIB", b"SOUND-DRIVER-AD-LIB"),
    ("liaodong big5", b"\xbf\xf1\xaa\x46"),
    ("BASEDATA head AC1A", b"\x41\x43\x1a\x00"),
    ("candidate pal start", bytes((2, 2, 2, 4, 4, 4, 6, 6, 6))),
    ("han save head", bytes((0x20, 0x20, 0x20, 0xBC, 0x42))),
]


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", w.DWORD),
                ("__alignment1", w.DWORD),
                ("RegionSize", ctypes.c_size_t),
                ("State", w.DWORD),
                ("Protect", w.DWORD),
                ("Type", w.DWORD),
                ("__alignment2", w.DWORD)]


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    if not h:
        print("OpenProcess failed:", ctypes.get_last_error())
        return
    found = {k: [] for k, _ in TARGETS}
    addr = 0
    mbi = MBI()
    total = 0
    chunks = 0
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr),
                             ctypes.byref(mbi), ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0:
            break
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        if size > 64 * 1024 * 1024:
            size = 64 * 1024 * 1024
        buf = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t(0)
        if not k32.ReadProcessMemory(h, ctypes.c_void_p(mbi.BaseAddress),
                                     buf, size, ctypes.byref(read)):
            continue
        data = buf.raw[:read.value]
        total += len(data)
        chunks += 1
        for name, pat in TARGETS:
            if len(found[name]) >= 6:
                continue
            start = 0
            while True:
                i = data.find(pat, start)
                if i < 0:
                    break
                found[name].append(mbi.BaseAddress + i)
                start = i + 1
    print("scanned bytes:", total, "chunks:", chunks)
    for name, _ in TARGETS:
        print("%-22s -> %s" % (name,
                               [hex(x) for x in found[name][:6]]))
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
