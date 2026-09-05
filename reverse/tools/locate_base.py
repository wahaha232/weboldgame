import ctypes
import ctypes.wintypes as w
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40 | 0x80
PALSIG = bytes((2, 2, 2, 4, 4, 4, 6, 6, 6, 8, 8, 8, 10, 10, 10, 12))


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
    b = ctypes.create_string_buffer(size)
    r = ctypes.c_size_t(0)
    if not ctypes.windll.kernel32.ReadProcessMemory(
            h, ctypes.c_void_p(addr), b, size, ctypes.byref(r)):
        return None
    return b.raw[:r.value]


def regions(h):
    out = []
    addr = 0
    mbi = MBI()
    while ctypes.windll.kernel32.VirtualQueryEx(
            h, ctypes.c_void_p(addr), ctypes.byref(mbi),
            ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0 or size > 256 * 1024 * 1024:
            continue
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        out.append((mbi.BaseAddress, size))
    return out


def scan(h, pat, maxhits=8):
    hits = []
    for base, size in regions(h):
        if len(hits) >= maxhits:
            break
        d = read(h, base, size)
        if not d:
            continue
        s = 0
        while True:
            i = d.find(pat, s)
            if i < 0:
                break
            hits.append(base + i)
            s = i + 1
    return hits


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    if not h:
        print("open fail")
        return

    # pass1: find HAN.EXE full image copy R
    R = None
    for hit in scan(h, b"basedata.001", 40):
        c = hit - 0x1A06B
        head = read(h, c, 4)
        if head == b"MZ\x6b\x01":  # HAN.EXE first 4 bytes
            pal = read(h, c + 0x1B40F, 16)
            if pal == PALSIG:
                R = c
                break
    print("R (HAN image copy host) =", hex(R) if R else None)
    if not R:
        k32.CloseHandle(h)
        return

    psp = read(h, R - 0x100, 0x100)
    print("PSP host =", hex(R - 0x100), "first bytes:", psp[:4].hex(" "))
    E = int.from_bytes(psp[0x2C:0x2E], "little")
    par = int.from_bytes(psp[0x16:0x18], "little")
    print("env seg E=%04X parent=%04X" % (E, par))

    # pass2: locate env block host via COMSPEC= (env starts typically with it)
    best = []
    for hit in scan(h, b"COMSPEC=", 30):
        B = hit - E * 16
        # validate B
        ivt = read(h, B, 0x100)
        if not ivt:
            continue
        sc = 0
        for i in range(0, 0x100, 4):
            seg = ivt[i + 2] | (ivt[i + 3] << 8)
            if 0x40 <= seg <= 0x9FFF:
                sc += 1
        bios = read(h, B + 0x400, 0x100)
        best.append((sc, B))
    best.sort(reverse=True)
    print("B candidates:", [(s, hex(b)) for s, b in best[:6]])

    # for top candidates read palette & screen
    for sc, B in best[:4]:
        pal = read(h, B + 0x1BBFE, 1536)
        ok = pal is not None and all(x < 64 for x in pal) and len(set(pal)) > 8
        print("== B=%s sc=%d pal_ok=%s head=%s" %
              (hex(B), sc, ok, pal[:24].hex(" ") if pal else None))
        if not ok:
            continue
        open("palette_runtime_6bit.bin", "wb").write(pal)
        print("  saved palette_runtime_6bit.bin")
        # DS 0x19CB head 256
        ds = read(h, B + 0x19CB0, 256)
        print("  DS0 head:", ds[:32].hex(" ") if ds else None)
        # screen text page B8000
        txt = read(h, B + 0xB8000, 4000)
        if txt:
            lines = []
            for r in range(25):
                line = []
                for c in range(0, 160, 2):
                    ch = txt[r * 160 + c]
                    line.append(chr(ch) if 32 <= ch < 127 else
                                (" " if ch == 0 else "."))
                lines.append("".join(line))
            print("  screen:")
            for ln in lines:
                print("   |%s|" % ln)
        break
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
