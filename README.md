# Schema

```
{
    "points": [], # 64-bit Integer Array
    "properties": {
        "index": {...}
        "dictionary": {...}
    }
}
```

### Considerations
- Coordinate Encoding Codec: Geohash using Hilbert Curves
- Integer Compression Codec
    * LEB128
    * Streamvbyte
- Properties Compression
    * Dictionary
    * RLE
    * Parquet-based?


```
MAGIC

!! Header
COORDINATE COUNT
PROPERTIES COUNT
PROPERTIES NAMES (array of null-terminated strings)
PROPERTIES TYPES (array of enumerators)

!!! Offsets
COORDINATES OFFSET
PROPERTY 1 OFFSET
PROPERTY 2 OFFSET
PROPERTY 3 OFFSET

!! Data
COORDINATE BYTES
PROPERTY 1 BYTES
PROPERTY 2 BYTES
PROPERTY 3 BYTES
```