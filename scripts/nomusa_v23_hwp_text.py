"""Plain-text extraction from HWP 5.0 files, including '배포용 문서' (ViewText, AES-128-ECB).
Algorithm follows the public HWP 5.0 spec / pyhwp distdoc implementation."""
from __future__ import annotations
import struct, zlib
import olefile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def _msvc_rand(seed):
    while True:
        seed = (seed * 214013 + 2531011) & 0xFFFFFFFF
        yield (seed >> 16) & 0x7FFF

def _dist_key(payload: bytes) -> bytes:
    seed = struct.unpack_from("<I", payload, 0)[0]
    r = _msvc_rand(seed); s = bytearray(payload); n = 0; key = 0
    for i in range(256):
        if n == 0:
            key = next(r) & 0xFF; n = (next(r) & 0xF) + 1
        if i >= 4: s[i] ^= key
        n -= 1
    off = 4 + (seed & 0xF)
    return bytes(s[off:off + 16])

def _records(data: bytes):
    i = 0
    while i + 4 <= len(data):
        h = struct.unpack_from("<I", data, i)[0]; tag = h & 0x3FF; size = (h >> 20) & 0xFFF; i += 4
        if size == 0xFFF: size = struct.unpack_from("<I", data, i)[0]; i += 4
        yield tag, data[i:i + size]; i += size

def _para_text(t: bytes) -> str:
    s = []; j = 0
    while j + 1 < len(t):
        c = struct.unpack_from("<H", t, j)[0]
        if c in (1,2,3,4,5,6,7,8,9,11,12,14,15,16,17,18,19,20,21,22,23): j += 16; continue
        if c in (10, 13): s.append("\n")
        elif c >= 32: s.append(chr(c))
        j += 2
    return "".join(s)

def hwp_text(path) -> str:
    o = olefile.OleFileIO(str(path))
    flags = o.openstream("FileHeader").read()[36]
    compressed, distributed = flags & 1, flags & 4
    root = "ViewText" if distributed else "BodyText"
    secs = sorted([d for d in o.listdir() if d[0] == root], key=lambda d: int(d[1][7:]))
    out = []
    for d in secs:
        data = o.openstream(d).read()
        if distributed:
            h = struct.unpack_from("<I", data, 0)[0]; size = (h >> 20) & 0xFFF
            key = _dist_key(data[4:4 + size]); body = data[4 + size:]
            body = body[: len(body) // 16 * 16]
            dec = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
            data = dec.update(body) + dec.finalize()
        if compressed:
            data = zlib.decompressobj(-15).decompress(data)
        out.extend(_para_text(p) for tag, p in _records(data) if tag == 67)
    return "\n".join(out)

if __name__ == "__main__":
    import sys; print(hwp_text(sys.argv[1]))
