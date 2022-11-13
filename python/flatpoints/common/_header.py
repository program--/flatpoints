from ._ftype import ftype
from io import BytesIO, FileIO
import struct

class header:
    _sod: int = 0
    _ccount: int = 0
    _pcount: int = 0
    _pnames: list[str] = []
    _ptypes: list[ftype] = []
    _offsets: list[int] = []

    def __str__(self):
        cstr = "coordinates" if self._ccount != 1 else "coordinate"
        pstr = "properties" if self._pcount != 1 else "property"
        return f'\033[1;95m<header>\033[0m\n- {self._ccount} {cstr}\n- {self._pcount} {pstr}'

    def __len__(self):
        ns = b''.join([f'{nm}\0'.encode() for nm in self._pnames])
        return (8 * 3) + len(ns) + len(self._ptypes) + (len(self._offsets) * 8)

    def from_file(self, file: FileIO | str | bytes | BytesIO):
        if isinstance(file, str):
            filedata = open(file, 'rb')
        elif isinstance(file, bytes):
            filedata = BytesIO(file)
        else:
            filedata = file

        # Check Magic
        magic = 'FPS'
        if filedata.read(3).decode('utf-8') != magic:
            if isinstance(file, str):
                filedata.close()
            raise RuntimeError('File is not a flatpoints file')
        
        self._sod = struct.unpack('<Q', filedata.read(8))
        self._ccount = struct.unpack('<Q', filedata.read(8))
        self._pcount = struct.unpack('<Q', filedata.read(8))
        self._ptypes = [ftype(struct.unpack('<B', filedata.read(1))) for _ in range(self._pcount)]
        
        # TODO: Make this faster
        self._pnames = []
        _nulls = 0
        while _nulls != self._pcount:
            c = filedata.read(1).decode('utf-8')
            if c == chr(0):
                _nulls += 1
            self._pnames.append(c)
        self._pnames = "".join(self._pnames).split(chr(0))
        self._pnames.pop()

        self.offsets = [struct.unpack('<Q', filedata.read(8)) for _ in range(self._pcount)]
        
        return self

    def to_bytes(self) -> bytes:
        res = b'FPS'
        res += struct.pack('<Q', self._sod)
        res += struct.pack('<Q', self._ccount)
        res += struct.pack('<Q', self._pcount)
        res += b''.join([struct.pack('<B', pt) for pt in self._ptypes])
        res += b''.join([f'{nm}\0'.encode() for nm in self._pnames])
        res += b''.join([struct.pack('<Q', offset) for offset in self._offsets])
        return res
