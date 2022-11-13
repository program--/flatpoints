from ._ftype import ftype, get_ftype
from io import FileIO
from typing import Dict, Callable
import json
import gzip

class property:
    _data: bytes = bytes()
    type: ftype

    def __init__(self, property_data: bytes | list, property_type: ftype | int = 0):
        self.type = ftype(property_type) if isinstance(property_type, int) else property_type
        self._data = property_data if isinstance(property_data, bytes) else self.type.dump(property_data)

    def __len__(self):
        return len(self._data)

    def __str__(self):
        strdata = f'{self._data[:10]}...{self._data[-10:]}' if len(self._data) > 30 else f'{self._data}'
        return f'<property: [{self.type.name}]>\n{strdata}'

    def __repr__(self):
        return f'property({self._data}, {self.type.value})'

    def __getitem__(self, key):
        if isinstance(key, str):
            raise KeyError('property indexing only accepts integers or slices')
        return self._data[key]

    def to_bytes(self) -> bytes:
        return self._data

    def write(self, file: FileIO) -> int:
        if file.closed:
            raise RuntimeError('file is closed')
        return file.write(self._data)


class properties:
    _data: Dict[str, property]
    _size: int

    def __str__(self):
        res = ['\033[1;95m<properties>\033[0m']
        keys = list(self.keys())
        kpad = max([len(key) for key in keys[:5]])
        for key in keys[:5]:
            size = len(self._data[key])
            sstr = 'byte' if size == 1 else 'bytes'
            tstr = f"<{self._data[key].type.name.lower()}>"

            res.append(f'- \033[92m{tstr:<8}\033[0m {key:<{kpad}} : {size:,} {sstr}')

        if len(keys) > 5:
            remaining_bytes = sum([len(self._data[key]) for key in keys[5:]])
            rstr = 'byte' if remaining_bytes == 1 else 'bytes'
            res.append(f'\033[90m…{len(keys) - 5} more w/ {remaining_bytes:,} {rstr}\033[0m')

        return '\n'.join(res)

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            raise KeyError('properties indexing only accepts strings')
        return self._data[key]

    def __len__(self):
        return len(self.keys())

    def size(self) -> int:
        return self._size

    def types(self) -> list[ftype]:
        return [self._data[key].type for key in self.keys()]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()

    def to_bytes(self, compressor: Callable = gzip.compress, *args, **kwargs) -> (bytes, list[int]):
        res = b''
        offsets: list[int] = []
        current_offset = 1
        for index, prop in zip(range(len(self)), self.values()):
            current_data = compressor(prop.to_bytes(), *args, **kwargs)
            offsets.append(current_offset)
            current_offset += len(current_data)
            res += current_data

        return (res, offsets)

    def from_geojson(self, file: FileIO | str | bytes | list[dict], sort_index: list[int] | None = None):
        if isinstance(file, FileIO):
            # `file` is a file stream
            if file.closed:
                raise RuntimeError('file is closed')
            geojson = json.loads(file.readall())
        elif isinstance(file, (str, bytes)):
            # `file` is a geojson string/bytes
            geojson = json.loads(file)
        elif isinstance(file, list):
            # `file` is already in-memory
            geojson = file

        # Load properties as AOS
        origin: list[dict] = [feature['properties'] for feature in geojson]
        if sort_index is not None:
            if len(sort_index) != len(origin):
                raise RuntimeError('geojson and `sort_index` have different lengths')
            origin = list(map(origin.__getitem__, sort_index))

        # Get all keys, some properties may not have entire keylist
        keys = [set(p.keys()) for p in origin]
        keys = list(keys[0].union(*keys))
        keys.sort()
        
        # Organize properties/types into SOA-like
        props = {}
        types = {}
        for key in keys:
            props[key] = []
            types[key] = None

        for p in origin:
            for key in keys:
                try:
                    prop = p[key]
                except KeyError:
                    prop = None
                if prop is not None and types[key] is None:
                    types[key] = get_ftype(prop)
                props[key].append(prop)

        # Convert to property class
        self._data = {}
        _size = []
        for key in keys:
            if types[key] is None and len(props[key]) == 0:
                continue
            self._data[key] = property(props[key], types[key])
            _size.append(len(self._data[key]))
        self._size = sum(_size)
        return self