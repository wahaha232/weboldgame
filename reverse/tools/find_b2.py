import ctypes
import ctypes.wintypes as w
import sys, os

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
    b = ctypes.create_string_buffer(size)
    r = ctypes.c_size_t(0)
    if not ctypes.windll.kernel32.ReadProcessMemory(
            h, ctypes.c_void_p(addr), b, size, ctypes.byref(r)):
        return None
    return b.raw[:r.value]


def ivt_score(data):
    if len(data) < 0x400:
        return -1
    s = 0
    for i in range(0, 0x400, 4):
        seg = data[i + 2] | (data[i + 3] << 8)
        if 0x40 <= seg <= 0x9FFF:
            s += 1
    return s


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    cands = []
    addr = 0
    mbi = MBI()
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                             ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0 or size > 256 * 1024 * 1024:
            continue
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        d = read(h, mbi.BaseAddress, size)
        if not d:
            continue
        s = 0
        while True:
            i = d.find(b"\x80\x02", s)
            if i < 0:
                break
            B = mbi.BaseAddress + i - 0x413
            if B < 0:
                s = i + 1
                continue
            ivt = read(h, B, 0x400)
            if ivt:
                sc = ivt_score(ivt)
                if sc > 30:
                    cands.append((sc, B))
            s = i + 1
    cands.sort(reverse=True)
    print("B candidates (bios-640k marker):", [(sc, hex(B)) for sc, B in cands[:6]])

    outdir = r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\screen"
    os.makedirs(outdir, exist_ok=True)
    # palette A (6-bit scaled to 8bit): reuse file
    palA = open(r"D:\VS CODE\PROJECT\hanwebgame\reverse\dumps\pics\palA_8bit.bin", "rb").read()
    for sc, B in cands[:3]:
        print("== candidate B=%s sc=%d" % (hex(B), sc))
        # text screen
        txt = read(h, B + 0xB8000, 4000)
        gfx = read(h, B + 0xA0000, 0xFA00)
        # check text rows
        if txt:
            lines = []
            for r in range(25):
                ln = "".join(chr(txt[r * 160 + c]) if 32 <= txt[r * 160 + c] < 127 else
                             (" " if txt[r * 160 + c] == 0 else ".")
                             for c in range(0, 160, 2))
                lines.append(ln)
            nonempty = sum(1 for l in lines if l.strip(" ."))
            print("  text nonempty rows:", nonempty)
            for l in lines:
                if l.strip(" ."):
                    print("   |%s|" % l)
        if gfx:
            from PIL import Image
            im = Image.new("P", (320, 200))
            im.putdata(gfx[:0xFA00])
            im.putpalette(palA[:768])
            fn = os.path.join(outdir, "screen_vga_%s.png" % hex(B))
            im.save(fn)
            print("  saved", fn)
        break
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
