import ctypes
import ctypes.wintypes as w
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40 | 0x80
PAL_GUEST = 0x1BBFE  # 0x19CB0 + 0x1F4E


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


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    if not h:
        print("open fail")
        return
    runs = []
    addr = 0
    mbi = MBI()
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                             ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0 or size > 128 * 1024 * 1024:
            continue
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        data = read(h, mbi.BaseAddress, size)
        if not data:
            continue
        run = []
        best = []
        for i, x in enumerate(data):
            if x < 64:
                if not run:
                    run = [i]
                else:
                    run.append(i)
            else:
                if len(run) >= 700:
                    best.append((mbi.BaseAddress + run[0], len(run)))
                run = []
        if len(run) >= 700:
            best.append((mbi.BaseAddress + run[0], len(run)))
        runs.extend(best)
    runs.sort(key=lambda r: -r[1])
    print("runs of <64 (>=700):", [(hex(a), n) for a, n in runs[:12]])
    for a, n in runs[:12]:
        B = a - PAL_GUEST
        pal = read(h, a, 1536)
        tail = read(h, a + 1536 - 48, 48)
        head = pal[:48]
        ok = (n >= 1536)
        print("B guess %s run_len %d ok_full_1536=%s head=%s" %
              (hex(B), n, ok, head.hex(" ")))
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
