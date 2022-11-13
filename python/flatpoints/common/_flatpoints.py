from ._header import header
from ._properties import properties, property
from flatpoints.util import hilbert, compression
from itertools import starmap, islice
from operator import sub
from io import FileIO
import json

class flatpoints():
    _header: header = header()
    _properties: properties = properties()
    _data: bytes = bytes()

    def __init__(self, file: FileIO | str):
        try:
            self.from_fps(file)
        except RuntimeError:
            try:
                self.from_json(file)
            except:
                raise RuntimeError('file is not parseable to flatpoints')

    def __str__(self):
        return f'{str(self._header)}\n{str(self._properties)}'

    def __len__(self):
        return len(self._data)

    def shape(self) -> (int, int):
        return (self._header._ccount, len(self._properties))

    def from_fps(self, file: FileIO | str):
        if isinstance(file, str):
            filedata = open(file, 'r')
        else:
            filedata = file

        self._header.from_file(filedata)
        self._data = filedata.read(self._header._offsets[0] - self._header._sod)
        self._properties = properties()
        self._properties._data = {}
        self._properties._size = 0
        for index, key, ptype in zip(range(self._header._pcount), self._header._pnames, self._header._ptypes):
            if index != self._header._pcount -1:
                pdata = filedata.read(self._header._offsets[index + 1] - self._header._offsets[index] - 1)
            else:
                pdata = filedata.readall()

            self._properties._data[key] = property(pdata, ptype)
            self._properties._size += len(self._properties._data[key])

        if isinstance(file, str):
            filedata.close()
        
        return self

    def from_json(self, file: FileIO | str):
        if isinstance(file, str):
            _file = open(file, 'r')
            filedata = json.load(_file)
            _file.close()
        else:
            filedata = json.load(file)

        # Parse Coordinates
        x = []
        y = []
        for d in filedata:
            pt = d['geometry']['coordinates']
            x.append(pt[0])
            y.append(pt[1])
        h = hilbert.encode(hilbert.MAX_N, x, y, hilbert.WORLD)
        index = list(range(len(h)))
        index.sort(key=h.__getitem__)
        h.sort()
        hdiff = [h[0], *starmap(sub, zip(islice(h, 1, None), h))]
        self._data = compression.leb128_encode(hdiff)

        # Parse Properties
        self._properties.from_geojson(filedata, index)

        # Initialize header
        self._header._ccount  = len(x)
        self._header._pcount  = len(self._properties)
        self._header._pnames  = list(self._properties.keys())
        self._header._ptypes  = self._properties.types()
        self._header._sod     = len(self._header) + 1
        self._header._offsets = self._properties.to_bytes()[1]
        self._header._offsets = [offset + len(self._header) + len(self._data) for offset in self._header._offsets]
        return self

    def to_bytes(self) -> bytes:
        res = self._header.to_bytes()
        res += self._data
        res += self._properties.to_bytes()[0]
        return res

    def to_file(self, file: FileIO | str) -> int:
        if isinstance(file, str):
            filedata = open(file, 'wb')
        else:
            filedata = file

        res = filedata.write(self.to_bytes())

        if isinstance(file, str):
            filedata.close()

        return res
