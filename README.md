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
- Coordinate Encoding Codec
    * Hilbert
    * Geohash
    * H3
    * S2
- Integer Compression Codec
    * LEB128
    * Streamvbyte
- Properties Compression
    * Dictionary
    * RLE
    * Parquet-based?


```
MAGIC
CODEC ENUM
COORDINATE COUNT
COORDINATE SIZE

PROPERTIES_COUNT
PROPERTY 1 OFFSET
PROPERTY 2 OFFSET
PROPERTY 3 OFFSET

COORDINATE BYTES
PROPERTY 1 BYTES
PROPERTY 2 BYTES
PROPERTY 3 BYTES
```