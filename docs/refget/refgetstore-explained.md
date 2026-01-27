# What is RefgetStore?

RefgetStore is a content-addressable sequence database that stores both individual sequences and sequence collections (like genome assemblies). It provides a local, file-based alternative to traditional sequence storage formats while supporting remote access and automatic caching.

## Why use RefgetStore?

Existing sequence formats are optimized for different use cases:

| Format | Strengths | Gaps |
|--------|-----------|------|
| FASTA + .fai | Universal, indexed random access | No deduplication, no collection tracking |
| bgzip + index | Compressed with random access | No deduplication, no collection tracking |
| 2bit | Compact, fast access | DNA only, no collection tracking |
| seqrepo | Content-addressable, deduplication, namespaces | Requires SQLite, no collection tracking |

RefgetStore is most similar to [seqrepo](https://github.com/biocommons/biocommons.seqrepo). Both provide content-addressable storage with deduplication. RefgetStore differs in being purely file-based (no database), supporting static file hosting (S3, HTTP) without a server, native support for GA4GH sequence collections, and adaptive encoding that provides smaller files with faster random access.

## Key features

### Collection management

Unlike formats that only store sequences, RefgetStore tracks sequence collections (genome assemblies, transcriptomes, etc.). You can query by collection digest and retrieve sequences by their local names within that collection.

### Universal identifiers

Every sequence and collection has a GA4GH refget digest. This enables:

- Reproducible retrieval by content hash
- Lookup by digest alone, or by (collection digest + sequence name)
- Computing derived digests (name/length pairs) for coordinate system comparison

### Automatic deduplication

Identical sequences are stored once, even across different assemblies. For example, mitochondrial sequences are often identical between GRCh38 and GRCh37—RefgetStore stores them once and references them from both collections.

### Efficient encoding

RefgetStore automatically selects the optimal encoding for each sequence:

| Alphabet | Encoding |
|----------|----------|
| DNA (ACGT only) | 2-bit |
| DNA with N | 3-bit |
| DNA with ambiguity codes | 4-bit |
| RNA or extended | 5-bit |
| Protein/other | 8-bit |

This provides compression while maintaining fast random access—no decompression needed.

### Remote access with caching

Connect a local store to a remote URL (HTTP, S3, or any file server). Sequences are downloaded on-demand and cached locally. Subsequent requests are served from the local cache.

### Region extraction

Extract subsequences by coordinates. Batch extraction from BED files is optimized for high throughput.

### File-based simplicity

No database server required. A RefgetStore is just a directory structure that can be:

- Copied and backed up with standard tools
- Hosted on any static file server
- Inspected directly on disk

## Learn more

- [RefgetStore tutorial](using-services/refgetstore.py) - Hands-on guide to using RefgetStore
- [RefgetStore file format](reference/refgetstore-format.md) - Technical specification of the directory structure
- [CLI reference](reference/cli.md) - Command-line interface for RefgetStore operations
