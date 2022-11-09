import json
import geohash
from operator import sub
from itertools import starmap, islice
import gzip

path = "data/example.geojson"

with open(path, 'r') as f:
    geojson = json.load(f)

coordinates = [x['geometry']['coordinates'] for x in geojson]
properties = [x['properties'] for x in geojson]
encoded = [geohash.encode_uint64(x[1], x[0]) for x in coordinates]
indexes = list(range(len(encoded)))
indexes.sort(key=encoded.__getitem__)
encoded.sort()
properties = list(map(properties.__getitem__, indexes))
diff = [encoded[0], *starmap(sub, zip(islice(encoded, 1, None), encoded))]
byts = [x.to_bytes(8, 'little', signed=False).split(b'\x00')[0] for x in diff]
joinedb = b'\x00'.join(byts)

codes = {
    'snappy': len(snappy.compress(joinedb)),
    'zlib': len(zlib.compress(joinedb, -1)),
    'lzma': len(lzma.compress(joinedb)),
    'bz2': len(bz2.compress(joinedb, 6)),
    'gzip': len(gzip.compress(joinedb, 8))
}
