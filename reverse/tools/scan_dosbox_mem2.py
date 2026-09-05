import ctypes
import ctypes.wintypes as w
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READABLE = 0x02 | 0x04 | 0x08 | 0x10 | 0x20 | 0x40 | 0x80

TARGETS = [
    ("basedata.001", b"basedata.001"),
    ("BASEDATA.001", b"BASEDATA.001"),
    ("PICS.IDX", b"PICS.IDX"),
    ("PICS.GRP", b"PICS.GRP"),
    ("FACE.GRP", b"FACE.GRP"),
    ("ZHONG.PAT", b"ZHONG.PAT"),
    ("hansave.dat", b"hansave.dat"),
    ("SOUND-DRIVER-AD-LIB", b"SOUND-DRIVER-AD-LIB"),
    ("Sound driver V1.51", b"Sound driver V1.51"),
    ("Bad command or file name", b"Bad command or file name"),
    ("File not found", b"File not found"),
    ("Insufficient memory", b"Insufficient memory"),
    ("not ready reading drive", b"not ready reading drive"),
    ("liaodong BF F1 AA 46", b"\xbf\xf1\xaa\x46"),
    ("BASEDATA AC1A", b"\x41\x43\x1a\x00"),
    ("AUTOEXEC/BAT marker han", b"han"),
    ("play\\r\\n", b"play\r\n"),
    ("C:\\\\HAN", b"C:\\HAN"),
    ("YING.PAT", b"YING.PAT"),
]


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


def main():
    pid = int(sys.argv[1])
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = w.HANDLE
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                        False, pid)
    if not h:
        print("OpenProcess failed")
        return
    found = {k: [] for k, _ in TARGETS}
    ctx = {}
    addr = 0
    mbi = MBI()
    total = 0
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                             ctypes.sizeof(mbi)):
        size = mbi.RegionSize
        addr = addr + size
        if size == 0:
            break
        if mbi.State != MEM_COMMIT or not (mbi.Protect & PAGE_READABLE):
            continue
        buf = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t(0)
        if not k32.ReadProcessMemory(h, ctypes.c_void_p(mbi.BaseAddress),
                                     buf, size, ctypes.byref(read)):
            continue
        data = buf.raw[:read.value]
        total += len(data)
        for name, pat in TARGETS:
            if len(found[name]) >= 8:
                continue
            start = 0
            while True:
                i = data.find(pat, start)
                if i < 0:
                    break
                a = mbi.BaseAddress + i
                found[name].append(a)
                ctx.setdefault(name, data[max(0, i - 32):i + len(pat) + 64])
                start = i + 1
    print("scanned", total)
    for name, _ in TARGETS:
        hits = found[name]
        if hits:
            print("%-22s %d hits first=%s" % (name, len(hits), hex(hits[0])))
            if name in ctx:
                print("    ctx:", ctx[name][:120])
        else:
            print("%-22s 0" % name)
    k32.CloseHandle(h)


if __name__ == "__main__":
    main()
