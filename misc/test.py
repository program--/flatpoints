import json
import geohash
from operator import sub
from itertools import starmap, islice

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


new_obj = {
    "points": diff,
    "properties": properties
}

with open('data/example.flatpoi', 'w') as f:
    json.dump(new_obj, f)
