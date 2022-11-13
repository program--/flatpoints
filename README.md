# flatpoints

**flatpoints** is an in-development data format for representing coordinates, particularly [*points of interest*](https://en.wikipedia.org/wiki/Point_of_interest), as a compressed list of integers (i.e. an [inverted list](https://en.wikipedia.org/wiki/Inverted_index)).

> **Note**: this library is currently in active development, so its API and the underlying data format are subject to change at any moment.

## Format

Section             | Description          | Bytes
------------------- | -------------------- | ------
Header (Attributes) | Magic Number         | 3 Bytes
Header (Attributes) | Start of Data (S)    | 8 Bytes
Header (Attributes) | Coordinate Count (N) | 8 Bytes
Header (Attributes) | Properties Count     | 8 Bytes
Header (Attributes) | Property Types       | N Bytes
Header (Attributes) | Property Names       | ((8 * (N + 3) + 3) - S) Bytes
Header (Offsets)    | Coordinate Offset    | 8 Bytes
Header (Offsets)    | Property 1 Offset    | 8 Bytes
Header (Offsets)    | Property 2 Offset    | 8 Bytes
Header (Offsets)    | ...                  | ...
Header (Offsets)    | Property N Offset    | 8 Bytes
Data                | Coordinate Data      |
Data                | Property 1 Data      |
Data                | Property 2 Data      |
Data                | ...                  |
Data                | Property N Data      |

## Braindumping

- Coordinate Encoding Codec: Geohash using Hilbert Curves or Hilbert Indexing (Allow for other encodings in later implementations)
- Integer Compression Codec: VTEnc OR LEB128 (Allow for other encodings in later implementations)
- Properties Compression: TBD

## References
- Giulio Ermanno Pibiri, Rossano Venturini (2019). "Techniques for Inverted Index Compression." [arXiv:1908.10598v2](https://arxiv.org/abs/1908.10598v2).
- Vicente Romera Calero (2022). "VTEnc". [GitHub Repository](https://github.com/vteromero/VTEnc).
- Vukovic, Tibor (2016). "Hilbert-Geohash - Hashing Geographical Point Data Using the Hilbert Space-Filling Curve."

## License

The reference implementation of flatpoints is licensed under APLv2.
The format specification for the flatpoints data format is public domain (or under a CC0 license as applicable).