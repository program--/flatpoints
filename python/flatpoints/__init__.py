from flatpoints.common.header import Header
from flatpoints.util import hilbert
from flatpoints.util import compression
from operator import sub
from itertools import starmap, islice
import json

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

    def __str__(self) -> str:
        # TODO
        pass

    def __len__(self) -> int:
        return self.header.coordinates_count

    def __getitem__(self, key) -> flatpoints | dict['x': float, 'y': float, 'properties': dict]:
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

    def _dumps_prop_intX(self, prop: list[int], length: int, signed: bool):
        return b''.join([x.to_bytes(length, 'little', signed) for x in prop])

    def _dumps_prop_int64(self, prop: list[int]) -> bytes:
        return self._dumps_prop_intX(prop, 8, True)

    def _dumps_prop_int32(self, prop: list[int]) -> bytes:
        return self._dumps_prop_intX(prop, 4, True)

    def _dumps_prop_uint64(self, prop: list[int]) -> bytes:
        return self._dumps_prop_intX(prop, 8, False)

    def _dumps_prop_uint32(self, prop: list[int]) -> bytes:
        return self._dumps_prop_intX(prop, 4, False)

    def _dumps_prop_bool(self, prop: list[bool]) -> bytes:
        # TODO: Handle NULL case
        return self._dumps_prop_intX(prop, 1, False)

    def _dumps_prop_float32(self, prop: list[float]) -> bytes:
        pass

    def _dumps_prop_float64(self, prop: list[float]) -> bytes:
        pass
