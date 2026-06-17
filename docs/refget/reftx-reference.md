# RefgetTranscripts (reftx) Reference

RefgetTranscripts (reftx) is a high-performance binary transcript store for HGVS coordinate mapping. It provides O(log n) lookups via memory-mapped binary search, with sub-microsecond access times after initial load.

## Quick Example

```rust
use gtars_reftx::{TxStore, TxStoreBuilder};

// Build a store from cdot JSON
let mut builder = TxStoreBuilder::new();
builder.ingest_cdot("cdot.0.2.24.grch38.json.gz")?;
builder.build("transcripts.reftx")?;

// Open and query
let store = TxStore::open("transcripts.reftx")?;
let readonly = store.into_readonly();

if let Some(tx) = readonly.lookup("NM_004333.6") {
    println!("{}: {} exons on {:?}", tx.accession, tx.exons.len(), tx.strand);
}
```

---

## Rust API

### TxStore

Mutable transcript store for the setup/build phase. Convert to `ReadonlyTxStore` for concurrent access.

#### TxStore::open

```rust
pub fn open<P: AsRef<Path>>(path: P) -> Result<Self>
```

Open a transcript store from disk via mmap. Validates the header and returns an error if the magic number or version is invalid.

**Parameters:**

- `path` - Path to a `.reftx` file

**Returns:** `Result<TxStore>`

**Example:**

```rust
let store = TxStore::open("transcripts.reftx")?;
```

#### TxStore::in_memory

```rust
pub fn in_memory(data: Vec<u8>) -> Result<Self>
```

Create a store from an in-memory byte buffer. Useful for testing or when the store is embedded in another format.

**Parameters:**

- `data` - Raw bytes of a valid `.reftx` file

**Returns:** `Result<TxStore>`

#### TxStore::len

```rust
pub fn len(&self) -> u64
```

Returns the number of transcripts in the store.

#### TxStore::lookup

```rust
pub fn lookup(&self, accession: &str) -> Option<Transcript>
```

Look up a transcript by accession. Uses O(log n) binary search on the index.

**Parameters:**

- `accession` - Transcript accession with version (e.g., `"NM_004333.6"`)

**Returns:** `Option<Transcript>` - Returns owned `Transcript` if found

#### TxStore::ensure_decoded

```rust
pub fn ensure_decoded(&mut self, accession: &str) -> Result<()>
```

Pre-decode a specific transcript into the internal cache. Call during setup before `into_readonly()` to enable zero-allocation lookups for known transcripts.

#### TxStore::ensure_decoded_where

```rust
pub fn ensure_decoded_where<F>(&mut self, predicate: F) -> Result<usize>
where
    F: Fn(&Transcript) -> bool,
```

Pre-decode all transcripts matching a predicate. Returns the count of transcripts cached.

**Example:**

```rust
// Pre-load all BRAF transcripts
let count = store.ensure_decoded_where(|tx| tx.gene == "BRAF")?;
```

#### TxStore::into_readonly

```rust
pub fn into_readonly(self) -> ReadonlyTxStore
```

Convert to an immutable store for concurrent access. For stores with fewer than 500,000 transcripts, this pre-decodes all transcripts into memory.

#### TxStore::into_readonly_lazy

```rust
pub fn into_readonly_lazy(self) -> ReadonlyTxStore
```

Convert to an immutable store with lazy decoding. Transcripts are decoded on first access. Use when only a subset of transcripts will be queried.

---

### ReadonlyTxStore

Immutable transcript store for concurrent read access. Safe for multiple threads sharing `&ReadonlyTxStore` via `Arc<ReadonlyTxStore>`.

#### ReadonlyTxStore::len

```rust
pub fn len(&self) -> u64
```

Returns the number of transcripts in the store.

#### ReadonlyTxStore::lookup

```rust
pub fn lookup(&self, accession: &str) -> Option<TranscriptRef<'_>>
```

Look up a transcript by accession. Takes `&self`, so it is safe for concurrent access from multiple threads.

**Parameters:**

- `accession` - Transcript accession with version (e.g., `"NM_004333.6"`)

**Returns:** `Option<TranscriptRef<'_>>` - Zero-copy reference if cached, or freshly decoded

**Example:**

```rust
use std::sync::Arc;

let store = TxStore::open("transcripts.reftx")?.into_readonly();
let shared = Arc::new(store);

// Multiple threads can call lookup concurrently
let tx = shared.lookup("NM_004333.6");
```

#### ReadonlyTxStore::lookup_mane

```rust
pub fn lookup_mane(&self, gene_symbol: &str) -> Option<TranscriptRef<'_>>
```

Look up the MANE Select transcript for a gene symbol. Requires that MANE summary data was loaded during build.

**Parameters:**

- `gene_symbol` - Gene symbol (e.g., `"BRAF"`)

**Returns:** `Option<TranscriptRef<'_>>` - The MANE Select transcript if found

---

### TxStoreBuilder

Builder for creating transcript stores from cdot JSON files.

#### TxStoreBuilder::new

```rust
pub fn new() -> Self
```

Create a new builder.

#### TxStoreBuilder::add_chrom_mapping

```rust
pub fn add_chrom_mapping(&mut self, name: &str, digest: [u8; 24])
```

Register a chromosome name to refget digest mapping. The digest is the 24-byte truncated SHA-512 of the sequence.

**Parameters:**

- `name` - Chromosome name (e.g., `"chr1"`, `"NC_000001.11"`)
- `digest` - 24-byte truncated refget digest

#### TxStoreBuilder::load_chrom_mappings_from_refget

```rust
pub fn load_chrom_mappings_from_refget(
    &mut self,
    store: &RefgetStore,
    collection_digest: &str,
) -> Result<usize>
```

Load chromosome mappings from a RefgetStore collection. Iterates the collection's sequences and builds a name-to-digest map.

**Parameters:**

- `store` - Reference to a RefgetStore
- `collection_digest` - Seqcol digest of the genome assembly

**Returns:** Count of chromosomes mapped

#### TxStoreBuilder::ingest_cdot

```rust
pub fn ingest_cdot<P: AsRef<Path>>(&mut self, path: P) -> Result<usize>
```

Ingest a cdot JSON file. Supports both plain JSON and gzip-compressed files (`.json.gz`). Skips transcripts on chromosomes not in the chrom_to_digest mapping.

**Parameters:**

- `path` - Path to cdot JSON file

**Returns:** Count of transcripts ingested

**Example:**

```rust
let mut builder = TxStoreBuilder::new();
builder.load_chrom_mappings_from_refget(&refget_store, "abc123...")?;
let count = builder.ingest_cdot("cdot.0.2.24.grch38.json.gz")?;
println!("Ingested {} transcripts", count);
```

#### TxStoreBuilder::load_mane_summary

```rust
pub fn load_mane_summary<P: AsRef<Path>>(&mut self, path: P) -> Result<usize>
```

Load MANE summary file to enable gene symbol lookups. The MANE summary file maps gene symbols to their MANE Select transcript accessions.

**Parameters:**

- `path` - Path to MANE summary TSV file

**Returns:** Count of MANE mappings loaded

#### TxStoreBuilder::build

```rust
pub fn build<P: AsRef<Path>>(&mut self, output: P) -> Result<()>
```

Build and write the binary store to disk. Sorts transcripts by accession hash and writes the index at the end of the file.

**Parameters:**

- `output` - Output path for the `.reftx` file

---

### Transcript

Transcript annotation record.

```rust
pub struct Transcript {
    /// Accession with version (e.g., "NM_004333.6")
    pub accession: String,
    /// Gene symbol (e.g., "BRAF")
    pub gene: String,
    /// Chromosome refget digest (24 bytes, truncated SHA-512)
    pub chrom_digest: [u8; 24],
    /// Strand orientation
    pub strand: Strand,
    /// CDS start in genomic coordinates (None if non-coding)
    pub cds_start: Option<u32>,
    /// CDS end in genomic coordinates (None if non-coding)
    pub cds_end: Option<u32>,
    /// Exons in genomic order (5' to 3' on chromosome)
    pub exons: Vec<Exon>,
}
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `transcript_length()` | `u32` | Total transcript length (sum of exon lengths) |
| `cds_length()` | `u32` | CDS length in bases (0 if non-coding) |
| `is_coding()` | `bool` | Returns true if transcript has CDS |
| `accession_base()` | `&str` | Accession without version (e.g., `"NM_004333"`) |

### Exon

A single exon with genomic coordinates.

```rust
pub struct Exon {
    /// Genomic start (0-based, inclusive)
    pub start: u32,
    /// Genomic end (0-based, exclusive)
    pub end: u32,
}
```

**Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `len()` | `u32` | Length in bases |
| `is_empty()` | `bool` | Returns true if zero-length |

### Strand

Strand orientation.

```rust
pub enum Strand {
    Forward = 1,
    Reverse = -1,
}
```

### TranscriptProvider Trait

Trait for types that can provide transcript data. Implemented by `ReadonlyTxStore`.

```rust
pub trait TranscriptProvider: Send + Sync {
    fn get_transcript(&self, accession: &str) -> Option<TranscriptRef<'_>>;
    fn get_mane_transcript(&self, gene_symbol: &str) -> Option<TranscriptRef<'_>>;
}
```

---

## Python API

### Installation

The reftx module is included in the gtars Python package:

```bash
pip install gtars
```

### TxStore

```python
from gtars.reftx import TxStore
```

#### Opening a store

```python
store = TxStore("transcripts.reftx")
```

#### Looking up transcripts

```python
tx = store.lookup("NM_004333.6")
if tx:
    print(f"{tx.accession}: {tx.gene}, {len(tx.exons)} exons")
    print(f"CDS: {tx.cds_start}-{tx.cds_end}")
    print(f"Strand: {tx.strand}")
```

#### MANE lookups

```python
tx = store.lookup_mane("BRAF")
if tx:
    print(f"MANE Select for BRAF: {tx.accession}")
```

### TxStoreBuilder

```python
from gtars.reftx import TxStoreBuilder
```

#### Building a store from cdot

```python
builder = TxStoreBuilder()

# Add chromosome mappings (name -> 24-byte digest)
builder.add_chrom_mapping("chr1", digest_bytes)

# Or load from a RefgetStore
from gtars.refget import RefgetStore
refget = RefgetStore("/path/to/refget")
builder.load_chrom_mappings_from_refget(refget, "collection_digest")

# Ingest cdot JSON
count = builder.ingest_cdot("cdot.0.2.24.grch38.json.gz")
print(f"Ingested {count} transcripts")

# Optionally load MANE summary
builder.load_mane_summary("MANE.GRCh38.v1.3.summary.txt.gz")

# Build the store
builder.build("transcripts.reftx")
```

### Transcript object attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `accession` | `str` | Full accession with version |
| `gene` | `str` | Gene symbol |
| `strand` | `str` | `"+"` or `"-"` |
| `cds_start` | `int` or `None` | CDS start position (0-based) |
| `cds_end` | `int` or `None` | CDS end position (0-based) |
| `exons` | `list[tuple[int, int]]` | List of (start, end) tuples |
| `chrom_digest` | `bytes` | 24-byte chromosome digest |

---

## CLI Commands

All reftx commands are subcommands of `gtars`.

### gtars tx-build

Build a transcript store from cdot JSON.

```bash
gtars tx-build <CDOT_JSON> <OUTPUT> [OPTIONS]
```

**Arguments:**

- `CDOT_JSON` - Path to cdot JSON file (supports .gz)
- `OUTPUT` - Output path for .reftx file

**Options:**

| Option | Description |
|--------|-------------|
| `--refget <PATH>` | RefgetStore path for chromosome mappings |
| `--collection <DIGEST>` | Seqcol digest for chromosome mappings |
| `--mane <PATH>` | MANE summary file for gene symbol lookups |

**Example:**

```bash
gtars tx-build cdot.0.2.24.grch38.json.gz transcripts.reftx \
    --refget /data/refget \
    --collection XZlrcEGi6mlopZ2uD8ObHkQB1d0oDwKk \
    --mane MANE.GRCh38.v1.3.summary.txt.gz
```

**Output:**

```
Reading chromosome mappings from RefgetStore...
  Mapped 25 chromosomes
Ingesting cdot JSON...
  Ingested 234,567 transcripts
Loading MANE summary...
  Loaded 19,062 MANE mappings
Writing transcripts.reftx...
  Done. 45.2 MB
```

### gtars tx-lookup

Look up a transcript by accession.

```bash
gtars tx-lookup <STORE> <ACCESSION>
```

**Arguments:**

- `STORE` - Path to .reftx file
- `ACCESSION` - Transcript accession (e.g., NM_004333.6)

**Example:**

```bash
gtars tx-lookup transcripts.reftx NM_004333.6
```

**Output:**

```json
{
  "accession": "NM_004333.6",
  "gene": "BRAF",
  "strand": "+",
  "cds_start": 140719327,
  "cds_end": 140924929,
  "exons": [
    [140719327, 140719450],
    [140781513, 140781696],
    ...
  ]
}
```

### gtars tx-lookup-mane

Look up the MANE Select transcript for a gene symbol.

```bash
gtars tx-lookup-mane <STORE> <GENE>
```

**Arguments:**

- `STORE` - Path to .reftx file
- `GENE` - Gene symbol (e.g., BRAF)

**Example:**

```bash
gtars tx-lookup-mane transcripts.reftx BRAF
```

**Output:**

```json
{
  "accession": "NM_004333.6",
  "gene": "BRAF",
  "strand": "+",
  ...
}
```

---

## Binary Format Specification

The `.reftx` file format is a compact, mmap-friendly binary format optimized for O(log n) lookups.

### File Layout

```
+------------------------------------------------------------------------------+
| HEADER (32 bytes, fixed)                                                      |
+------------------------------------------------------------------------------+
| Offset | Size  | Type      | Name           | Description                    |
|   0    |  4    | [u8; 4]   | magic          | b"RFTX" (0x52, 0x46, 0x54, 0x58)|
|   4    |  4    | u32 LE    | version        | Format version (1)             |
|   8    |  8    | u64 LE    | record_count   | Number of transcript records   |
|  16    |  8    | u64 LE    | index_offset   | Byte offset to index section   |
|  24    |  8    | [u8; 8]   | reserved       | Zero-filled, future use        |
+------------------------------------------------------------------------------+
| RECORDS (variable length, starts at byte 32)                                  |
+------------------------------------------------------------------------------+
| INDEX (16 bytes per entry, starts at index_offset)                            |
+------------------------------------------------------------------------------+
```

### Header (32 bytes)

| Offset | Size | Type | Name | Description |
|--------|------|------|------|-------------|
| 0 | 4 | `[u8; 4]` | magic | `b"RFTX"` (0x52, 0x46, 0x54, 0x58) |
| 4 | 4 | `u32 LE` | version | Format version (currently 1) |
| 8 | 8 | `u64 LE` | record_count | Number of transcript records |
| 16 | 8 | `u64 LE` | index_offset | Byte offset to index section |
| 24 | 8 | `[u8; 8]` | reserved | Zero-filled for future use |

### Record Format (variable length)

Each transcript record has the following structure:

| Offset | Size | Type | Name | Description |
|--------|------|------|------|-------------|
| +0 | 1 | `u8` | accession_len | Length of accession string |
| +1 | N | `[u8; N]` | accession | UTF-8 accession string |
| +N | 1 | `u8` | gene_len | Length of gene symbol |
| +N+1 | M | `[u8; M]` | gene | UTF-8 gene symbol |
| ... | 24 | `[u8; 24]` | chrom_digest | Truncated refget digest |
| ... | 1 | `i8` | strand | +1 forward, -1 reverse |
| ... | 4 | `u32 LE` | cds_start | 0xFFFFFFFF if None |
| ... | 4 | `u32 LE` | cds_end | 0xFFFFFFFF if None |
| ... | 2 | `u16 LE` | exon_count | Number of exons |
| ... | 8*exons | `[(u32, u32)]` | exons | (start, end) pairs, LE |

### Index Format (16 bytes per entry)

The index is sorted by accession_hash in ascending order to enable binary search.

| Offset | Size | Type | Name | Description |
|--------|------|------|------|-------------|
| +0 | 8 | `u64 LE` | accession_hash | FNV-1a hash of accession bytes |
| +8 | 8 | `u64 LE` | record_offset | Byte offset of record in file |

### Hash Function

The index uses FNV-1a 64-bit hashing:

```rust
const FNV_OFFSET: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

fn fnv1a_64(data: &[u8]) -> u64 {
    let mut hash = FNV_OFFSET;
    for &byte in data {
        hash ^= byte as u64;
        hash = hash.wrapping_mul(FNV_PRIME);
    }
    hash
}
```

### Sentinel Values

- `0xFFFFFFFF` (u32 max) indicates None for `cds_start` and `cds_end`

### Version History

| Version | Changes |
|---------|---------|
| 1 | Initial format |

---

## Design Rationale

### Why binary instead of JSON?

cdot JSON files require full parsing (~2-3s cold start) and load the entire file into memory (~500MB). The binary format enables:

- **mmap-friendly layout**: OS pages in only accessed data
- **O(log n) lookup**: Binary search on sorted index
- **~500ns per lookup**: After ~1ms cold start
- **Zero-allocation hot paths**: For batch processing

### Why FNV-1a hashing?

FNV-1a is simple, fast, and deterministic. Hash collisions are handled by linear probing with full accession string comparison.

### Why 24-byte truncated digests?

Full SHA-512/24u digests are 32 bytes. Truncating to 24 bytes saves space while maintaining sufficient collision resistance for the ~25 chromosomes in a typical genome.

### Why exons inline?

Storing exons directly in each record avoids pointer chasing and keeps related data contiguous for better cache locality.

## See Also

- [cdot project](https://github.com/SACGF/cdot) - Source of transcript JSON data
- [MANE](https://www.ncbi.nlm.nih.gov/refseq/MANE/) - Matched Annotation from NCBI and EMBL-EBI
- [RefgetStore format](reference/refgetstore-format.md) - Sequence storage format
