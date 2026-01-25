# RefgetStore vs seqrepo: Detailed Comparison

Both RefgetStore and [seqrepo](https://github.com/biocommons/biocommons.seqrepo) are content-addressable sequence stores with automatic deduplication. This document compares their architectures, use cases, and trade-offs.

## Overview

| Aspect | RefgetStore | seqrepo |
|--------|-------------|---------|
| **Primary use case** | Distributed sequence access | Local sequence management |
| **Storage backend** | Pure files (directory structure) | SQLite + bgzip files |
| **Remote access** | Static file hosting (S3, HTTP) | REST server ([seqrepo-rest-service](https://github.com/biocommons/seqrepo-rest-service)) |
| **Sequence encoding** | Adaptive 2-8 bit | bgzip compression |
| **Implementation** | Rust core (gtars) + Python bindings | Pure Python |
| **Collection management** | Native (GA4GH seqcol digests) | Namespaces |
| **Ecosystem** | refgenie/GA4GH | biocommons (hgvs, uta, etc.) |

## Architecture Differences

### Storage

**seqrepo** uses SQLite for indexing with sequences stored in bgzip-compressed files:
```
seqrepo/
├── aliases.sqlite3          # SQLite database for lookups
├── sequences/
│   ├── 2016/...            # Date-based organization
│   └── db.sqlite3          # Sequence metadata
```

**RefgetStore** is purely file-based with no database:
```
refgetstore/
├── sequences/              # Encoded sequence files
│   ├── ab/cd1234...       # Sharded by digest prefix
├── collections/            # Collection metadata
│   ├── xy/z789...
└── index.json             # Optional manifest
```

### Remote Access

**seqrepo** requires deploying the [seqrepo-rest-service](https://github.com/biocommons/seqrepo-rest-service):
- OpenAPI-based REST interface
- Implements GA4GH refget protocol
- Requires running server process
- Adds network overhead vs local access

**RefgetStore** works with static file hosting:
- Upload directory to S3, HTTP server, or any file host
- Client fetches files directly (no server logic)
- Built-in local caching of remote sequences
- No server process needed

### Encoding

**seqrepo** uses bgzip:
- Block-gzip compression
- Good compression ratios
- Requires decompression for access

**RefgetStore** uses adaptive bit encoding:
| Alphabet | Bits/base | Example |
|----------|-----------|---------|
| DNA (ACGT) | 2 | Most genomic sequences |
| DNA + N | 3 | Sequences with unknown bases |
| DNA + ambiguity | 4 | IUPAC codes |
| RNA/extended | 5 | RNA sequences |
| Protein/other | 8 | Amino acids |

Benefits:
- No decompression needed (direct bit extraction)
- Optimal encoding per sequence
- Fast random access

## Performance Considerations

### Local Access

From the [seqrepo paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239883):
> "A local SeqRepo sequence collection yields significant performance benefits of up to 1300-fold over remote sequence collections."

Both systems provide fast local access. RefgetStore's Rust implementation may offer advantages for bulk operations, but benchmarking would be needed for specific use cases.

### Remote Access

**seqrepo REST**:
- Adds HTTP overhead per request
- Server handles request parsing, routing
- Good for programmatic API access from any language

**RefgetStore remote**:
- Direct file fetches (simpler)
- Client-side caching reduces repeated fetches
- Better for batch operations (fetch once, use many times)

## Use Case Guidance

### Choose RefgetStore when:

- **Distributed deployment**: You want to host sequences on S3/CDN without running servers
- **No database dependencies**: You prefer pure file-based storage
- **GA4GH seqcol integration**: You're working with sequence collections standard
- **Batch remote access**: You'll fetch sequences once and reuse from local cache

### Choose seqrepo when:

- **biocommons ecosystem**: You're using hgvs, uta, or other biocommons tools
- **Mature tooling**: You need battle-tested, widely-deployed solution
- **Alias resolution**: You need rich identifier mapping (RefSeq, Ensembl, etc.)
- **REST API**: You need programmatic access from non-Python languages

## Migration Considerations

Both systems use GA4GH refget digests (sha512t24u), so sequences are identified consistently. However:

- Collection/namespace models differ
- Alias handling differs (seqrepo has richer alias support)
- Storage formats are incompatible (would need re-import)

## References

- [seqrepo GitHub](https://github.com/biocommons/biocommons.seqrepo)
- [seqrepo-rest-service](https://github.com/biocommons/seqrepo-rest-service)
- [seqrepo paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239883): Hart RK, Prlić A (2020) SeqRepo: A system for managing local collections of biological sequences. PLoS ONE 15(12): e0239883.
- [GA4GH refget specification](https://samtools.github.io/hts-specs/refget.html)
