# What is RefgetStore?

RefgetStore is a content-addressable sequence database that stores both individual sequences and sequence collections (like genome assemblies). It provides a local, file-based alternative to traditional sequence storage formats while supporting remote access and automatic caching.

At its core, **RefgetStore is a file format** — a directory layout for sequences and collections, addressed by their GA4GH refget digests. Around that format sits a stack of software (a Rust engine, language bindings, servers, and a web explorer) that all share the name "refget" or "RefgetStore." See [Components](#components) below for the full list with links.

## Local vs. remote RefgetStores

A RefgetStore is just a directory of files, so the same store can live in three places:

- **Local store** — a directory on your own disk. Fully self-contained; read and write it with no server and no network.
- **Remote store** — the identical directory layout hosted on static object storage (S3) or any HTTP file server. Because access is content-addressable and range-based, **no application server is required** — a plain bucket is enough to serve sequences.
- **Local cache of a remote store** — point a local store at a remote URL. Sequences are downloaded on demand and cached locally; subsequent requests are served from the cache. You get remote breadth with local speed.

This local/remote symmetry is the defining feature: the *same* store works on a laptop, on S3, or as a cache bridging the two.

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

## Components

The RefgetStore name spans the storage format *and* the layers of software built on top of it. Here are the pieces, from the bytes on disk up to the website you click on.

### The format

The RefgetStore format is the on-disk (or on-S3) directory layout itself — sequences and collections addressed by their digests. See the [format reference](reference/refgetstore-format.md).

### The engine (Rust)

[**`gtars`**](https://github.com/databio/gtars) is the Rust project at the heart of everything here. The RefgetStore implementation lives in its [`gtars-refget`](https://github.com/databio/gtars/tree/master/gtars-refget) crate ([crates.io](https://crates.io/crates/gtars-refget)), which reads and writes stores — local and remote/S3, with adaptive encoding and deduplication. Every component below is ultimately a wrapper around this engine.

### Bindings

The Rust engine is exposed to four other languages, all built from the same [`gtars`](https://github.com/databio/gtars) repo:

| Language | Package | Where |
|----------|---------|-------|
| Python | `gtars` | [GitHub](https://github.com/databio/gtars/tree/master/gtars-python) · [PyPI](https://pypi.org/project/gtars/) |
| Node.js | `@databio/gtars-node` | [GitHub](https://github.com/databio/gtars/tree/master/gtars-node) · [npm](https://www.npmjs.com/package/@databio/gtars-node) |
| WebAssembly | `@databio/gtars` | [GitHub](https://github.com/databio/gtars/tree/master/gtars-wasm) · [npm](https://www.npmjs.com/package/@databio/gtars) |
| R | `gtars` (R package) | [GitHub](https://github.com/databio/gtars/tree/master/gtars-r) |

The WebAssembly build exposes only the digest/encoding subset (the WASM-safe parts) for in-browser use; the others expose the full `RefgetStore` API.

### High-level library

[**`refget`**](https://github.com/refgenie/refget) ([PyPI](https://pypi.org/project/refget/)) is the friendly Python package most users start with. It wraps the store and adds clients, database agents, a FastAPI router, and a CLI.

### Servers

Two servers expose a backend over the GA4GH refget + seqcol HTTP APIs:

| Server | What it serves | Where |
|--------|----------------|-------|
| `seqcolapi` | Collection **metadata** + comparison (no sequence residues). Backed by PostgreSQL *or* a RefgetStore. | [GitHub](https://github.com/refgenie/refget/tree/master/seqcolapi) · live: [seqcolapi.databio.org](https://seqcolapi.databio.org) |
| `@databio/refgetstore-server` | Raw sequence **residues**, streamed or redirected from a (often S3-backed) RefgetStore. Node.js/Hono, no database. | [GitHub](https://github.com/databio/refgetstore-node-demo) |

These do different jobs — see [The two servers are not the same](#the-two-servers-are-not-the-same) below.

### Web explorer

The [**refget explorer**](https://refget.databio.org/explore) is a React app for browsing collections and stores in the browser ([source](https://github.com/refgenie/refget/tree/master/frontend)).

### The two servers are not the same

Both `seqcolapi` and `refgetstore-server` speak the GA4GH refget + seqcol APIs, and both can be backed by a RefgetStore — so people conflate them. The difference is **what they serve**, not where they store it:

- **`seqcolapi`** is a **collection metadata and comparison service**. It answers "what's in this collection?" (names, lengths, digests) and "how do these two collections compare?". It *deliberately does not hand out sequence bases.*
- **`refgetstore-server`** is a **raw sequence-residue delivery proxy**. Its whole job is to stream or redirect the actual bytes of a sequence out of a RefgetStore, with no database and no Python.

So a typical deployment stacks them: the **explorer** (web UI) talks to **seqcolapi** (collection metadata) for browsing, while sequence bytes come from a **RefgetStore** on S3 — served either directly (static, content-addressable) or through `refgetstore-server`.

## Learn more

- [Getting started tutorial](using-services/getting-started.py) - Quick introduction to computing digests
- [RefgetStore tutorial](using-services/refgetstore.py) - Hands-on guide to using RefgetStore
- [RefgetStore file format](reference/refgetstore-format.md) - Technical specification of the directory structure
- [CLI reference](reference/cli.md) - Command-line interface for RefgetStore operations
- [Names, aliases, and identifiers](names-and-aliases-explained.md) - How human-readable registry identifiers work alongside digests and sequence names
- [Understanding FHR metadata](fhr-metadata-explained.md) - How to attach structured assembly-level metadata to collections
- [The brickyard genome collection](genome-collections-explained.md) - A curated collection of ~1,952 reference genomes organized in a RefgetStore
- [Browse live collections](https://refget.databio.org/explore) - The public RefgetStore explorer
