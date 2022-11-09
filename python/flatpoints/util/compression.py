from io import BytesIO


def leb128_encode(x: list[int]) -> bytes:
    return b"".join([leb128_single_encode(i) for i in x])


def leb128_decode(b: bytes) -> list[int]:
    pos = 0
    tot = len(b)
    ret = []
    while pos != tot:
        buf = leb128_single_decode(b[pos:])
        ret.append(buf[0])
        pos += buf[1]
    return ret


def leb128_single_encode(x: int) -> bytes:
    buf = b''
    while True:
        w = x & 0x7f
        x >>= 7
        if x:
            buf += bytes((w | 0x80, ))
        else:
            buf += bytes((w, ))
            break
    return buf


def leb128_single_decode(b: bytes | BytesIO) -> (int, int):
    if isinstance(b, bytes):
        return leb128_single_decode(BytesIO(b))
    else:
        shift = 0
        ret = 0
        while True:
            i = _ro(b)
            ret |= (i & 0x7f) << shift
            shift += 7
            if not (i & 0x80):
                break
    return (ret, int(shift / 7))


def _ro(stream: BytesIO) -> int:
    c = stream.read(1)
    if c == b'':
        raise EOFError("Unexpected EOF")
    return ord(c)
