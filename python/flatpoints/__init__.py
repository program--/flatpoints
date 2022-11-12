from flatpoints.common.header import Header
from flatpoints.util import hilbert
from flatpoints.util import compression
from operator import sub
from itertools import starmap, islice
import json
import struct
import gzip

# TODO: Get bytesize of properties
# TODO: Calculate SOD / Offsets


class flatpoints():
    header: Header = Header()
    data: bytes = bytes()
    properties: dict = {}

    def _get_type(self, obj: object) -> int:
        typeclass = type(obj)
        if typeclass is int:
            if obj < 0:
                return 1 if obj.bit_length() < 33 else 2
            else:
                return 3 if obj.bit_length() < 33 else 4
        elif typeclass is float:
            return 6
        elif typeclass is str:
            return 7
        elif typeclass is bool:
            return 8
        else:
            return 0

    # Magic Methods

    def __init__(self, filepath: str):
        with open(filepath, 'r') as file:
            geojson = json.load(file)

        self.header.coordinates_count = len(geojson)
        self._parse(geojson)
        self._init_header()
        self.dumps()

    def __str__(self) -> str:
        # TODO
        pass

    def __len__(self) -> int:
        return self.header.coordinates_count

    def __getitem__(self, key):
        if isinstance(key, int):
            x, y = hilbert.decode(
                hilbert.MAX_N, [compression.leb128_decode(self.data)[key]], hilbert.WORLD)
            x = x[0]
            y = y[0]

            props = {}
            for k in self.properties.keys():
                props[k] = self.properties[k][key]

            return {
                'x': x,
                'y': y,
                'properties': props
            }
        elif isinstance(key, slice):
            nfps = flatpoints()
            new_data = compression.leb128_decode(self.data)[key]
            new_header = Header()
            new_header.coordinates_count = len(new_data)
            new_header.properties_count = self.header.properties_count
            new_header.properties_names = self.header.properties_names
            new_header.properties_types = self.header.properties_types
            nfps.header = new_header
            nfps.properties = {k: v[key] for k, v in self.properties}
            nfps.data = compression.leb128_encode(new_data)
            return nfps
        else:
            raise TypeError(
                'flatpoints indices must be integers or slices, not str')

        pass

    # Public

    def dumps(self) -> bytes:
        ret = b''
        prop_bytes = b''
        current_offset = 1
        for i in range(len(self.header.properties_names)):
            prop_name = self.header.properties_names[i]
            prop_type = self.header.properties_types[i]

            if prop_type == 1:
                _dumps = self._dumps_prop_int32
            elif prop_type == 2:
                _dumps = self._dumps_prop_int64
            elif prop_type == 3:
                _dumps = self._dumps_prop_uint32
            elif prop_type == 4:
                _dumps = self._dumps_prop_uint64
            elif prop_type == 5:
                _dumps = self._dumps_prop_float32
            elif prop_type == 6:
                _dumps = self._dumps_prop_float64
            elif prop_type == 7:
                _dumps = self._dumps_prop_str
            elif prop_type == 8:
                _dumps = self._dumps_prop_bool
            else:
                raise TypeError(
                    f'Failed to interpret property {prop_name} type')

            current_bytes = _dumps(self.properties[prop_name])
            current_bytes = gzip.compress(current_bytes, 6)
            self.header.offsets.append(current_offset)
            current_offset += len(current_bytes)
            prop_bytes += current_bytes

        header_size = len(self.header)
        coords_size = len(self.data)
        self.header.start_of_data = header_size + 1
        self.header.offsets = [offset + header_size +
                               coords_size for offset in self.header.offsets]

        ret += self.header.dumps()
        ret += self.data
        ret += prop_bytes
        return ret

    def dump(self, filepath: str) -> int:
        bytes_written = 0
        with open(filepath, 'wb') as file:
            bytes_written = file.write(self.dumps())
        return bytes_written

    # Private

    def _parse(self, data: dict):
        x = []
        y = []
        self.properties = [x['properties'] for x in data]
        for d in data:
            pt = d['geometry']['coordinates']
            x.append(pt[0])
            y.append(pt[1])

        # Encode
        h = hilbert.encode(hilbert.MAX_N, x, y, hilbert.WORLD)
        indexes = list(range(len(h)))
        indexes.sort(key=h.__getitem__)
        h.sort()
        self.properties = list(map(self.properties.__getitem__, indexes))
        hdiff = [h[0], *starmap(sub, zip(islice(h, 1, None), h))]

        # Compress
        self.data = compression.leb128_encode(hdiff)

    def _init_header(self):
        keys = [set(x.keys()) for x in self.properties]
        keys = list(keys[0].union(*keys))
        keys.sort()

        self.header.properties_count = len(keys)
        self.header.properties_names = keys

        # Initialize vectorized properties list
        props = {}
        types = {}
        for key in keys:
            props[key] = []
            types[key] = None

        for propset in self.properties:
            for propname in keys:
                try:
                    prop = propset[propname]
                except KeyError:
                    prop = None

                if prop is not None and types[propname] is None:
                    # if the property exists for this feature and the type doesn't exist
                    # then, get it and set it in the types dict
                    types[propname] = self._get_type(propset[propname])

                props[propname].append(prop)

        self.properties = props
        self.header.properties_types = [types[nm] for nm in keys]

    # Dump methods

    def _dumps_prop_str(self, prop: list[str]) -> bytes:
        return b''.join([f'{x}\0'.encode('utf-8') for x in prop])

    def _dumps_prop_c(self, format: str, prop: list[any]) -> bytes:
        return struct.pack(f'={len(prop)}{format}', *prop)

    def _dumps_prop_int64(self, prop: list[int]) -> bytes:
        return self._dumps_prop_c('q', prop)

    def _dumps_prop_int32(self, prop: list[int]) -> bytes:
        return self._dumps_prop_c('l', prop)

    def _dumps_prop_uint64(self, prop: list[int]) -> bytes:
        return self._dumps_prop_c('Q', prop)

    def _dumps_prop_uint32(self, prop: list[int]) -> bytes:
        return self._dumps_prop_c('L', prop)

    def _dumps_prop_bool(self, prop: list[bool]) -> bytes:
        return self._dumps_prop_c('?', prop)

    def _dumps_prop_float32(self, prop: list[float]) -> bytes:
        return self._dumps_prop_c('f', prop)

    def _dumps_prop_float64(self, prop: list[float]) -> bytes:
        return self._dumps_prop_c('d', prop)
