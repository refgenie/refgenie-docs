# What is RefgetTranscripts (reftx)?

RefgetTranscripts (reftx) is a high-performance binary store for transcript annotations, designed as a companion to RefgetStore. Where RefgetStore holds sequences, reftx holds the transcript models that describe how those sequences are organized into genes -- exon boundaries, coding regions, strand orientation, and the mapping between transcript coordinates and genome coordinates.

## Why reftx?

HGVS nomenclature is the standard for describing genetic variants in clinical and research contexts. An HGVS expression like `NM_004333.6:c.1799T>A` (the BRAF V600E mutation) uses transcript coordinates (`c.` notation) rather than genome coordinates (`g.` notation). Converting between these coordinate systems requires transcript annotation data: which exons belong to transcript NM_004333.6, where they fall on the chromosome, and where the coding sequence begins.

Existing solutions have significant limitations:

| Solution | How it works | Problems |
|----------|--------------|----------|
| **UTA** (biocommons) | PostgreSQL database | Requires database server setup, complex infrastructure, network latency for every lookup |
| **cdot** | JSON files | 2-3 second cold start (JSON parsing), entire 500MB file loaded into memory, repeated field names waste space |

Both approaches work, but neither scales well to high-throughput variant annotation where millions of variants need coordinate mapping.

reftx takes a different approach: a binary format optimized for memory-mapped access with O(log n) lookups. The result is approximately 500-nanosecond single transcript lookups after a 1-millisecond cold start, with memory usage proportional to the data actually accessed rather than the entire file.

## How reftx relates to RefgetStore

reftx and RefgetStore are independent but linked stores:

- **RefgetStore** holds sequences, indexed by content digest (e.g., `SQ.abc123...` → `ACGT...`)
- **reftx** holds transcript models that reference those sequences by digest (e.g., `NM_004333.6` has `chrom: SQ.abc123...`)

Each transcript record in reftx stores a chromosome reference as a refget digest (the `SQ.xxx` identifier), not a chromosome name. This means:

- **No assembly ambiguity**: The transcript is explicitly tied to a specific sequence, not a name that might mean different things in different contexts
- **Cross-assembly lookup**: Given a transcript, you can retrieve its chromosome sequence from any RefgetStore that contains that digest
- **Deduplication**: If two assemblies share the same chromosome sequence (common for mitochondrial DNA), the same digest resolves to both

The stores are operationally independent. You can build and query an reftx store without a RefgetStore present, and vice versa. The linking happens at query time when you need both transcript structure and sequence content.

## The binary format

reftx uses a custom binary format (`.reftx` files) designed for memory-mapped random access. The file has three sections:

**Header (32 bytes):** Magic bytes (`RFTX`), version (u32), record count (u64), index offset (u64), and reserved space.

**Records (variable length):** Each transcript record contains:
- Accession (length-prefixed string, e.g., `NM_004333.6`)
- Gene symbol (length-prefixed string, e.g., `BRAF`)
- Chromosome digest (24 bytes, truncated refget SQ digest)
- Strand (+1 or -1)
- CDS start/end (u32, or sentinel value for non-coding)
- Exon count + exon coordinates (start/end pairs)

**Index (16 bytes per entry, sorted by hash):** Each entry contains an accession hash (u64, FNV-1a) and record offset (u64).

### Why this layout matters

**mmap-friendly**: The operating system's virtual memory system can page in only the portions of the file actually accessed. Looking up a single transcript touches perhaps 3-4 pages (the index entries visited during binary search, plus the record itself), not the entire file.

**O(log n) lookup**: The sorted index enables binary search. For a store with 200,000 transcripts, a lookup visits at most 18 index entries.

**No parsing overhead**: Unlike JSON, there is no parsing step. Reading a u32 from the mmap is a single memory access. The file is the in-memory representation.

**Compact**: No repeated field names (every JSON record repeats `"accession"`, `"gene"`, `"exons"`, etc.). Coordinates use u32 (4 bytes) rather than JSON numbers (variable, typically 6-10 bytes as text). The entire NCBI RefSeq transcript set fits in roughly 100MB.

## Key concepts

### TxStore vs ReadonlyTxStore

reftx provides two store types that reflect a common pattern for concurrent access:

1. **Build phase:** `TxStore` (mutable, single owner) — open the file, validate header, pre-cache
2. **Convert:** Call `.into_readonly()` to get `ReadonlyTxStore`
3. **Query phase:** `ReadonlyTxStore` (immutable) wrapped in `Arc<>` for multi-threaded access

**TxStore** is used during the setup phase: opening the file, validating the header, potentially pre-caching frequently accessed transcripts. It owns the mmap exclusively.

**ReadonlyTxStore** is the immutable form, safe for concurrent `&self` access. Wrap it in `Arc` to share across threads. All lookup methods take `&self`, never `&mut self`, so multiple threads can query simultaneously without locks.

This separation follows Rust's ownership model: mutation happens in a single-threaded setup phase, then the data becomes immutable and shareable.

### Zero-allocation lookups

For batch processing (annotating millions of variants), allocation overhead adds up. reftx provides lookup paths that reuse buffers and avoid allocating new strings:

- The transcript accession is compared in-place against the mmap bytes
- Exon coordinates are read directly as u32 pairs without intermediate allocations
- Gene symbols and other string fields can be returned as references into the mmap (`&str` slices)

The owned `Transcript` struct is available when you need it, but the hot path can operate on references.

### TranscriptProvider trait

reftx implements the `TranscriptProvider` trait, which abstracts over different transcript sources:

```rust
pub trait TranscriptProvider {
    fn get_transcript(&self, accession: &str) -> Option<TranscriptInfo>;
    fn get_transcripts_by_gene(&self, gene: &str) -> Vec<TranscriptInfo>;
}
```

This allows HGVS parsing code to work with reftx, cdot, UTA, or any other backend through a common interface. You can swap implementations without changing the coordinate mapping logic.

## MANE Select integration

MANE (Matched Annotation from NCBI and EBI) Select transcripts are the authoritative "default" transcripts for clinical reporting. For each protein-coding gene, MANE Select designates exactly one RefSeq transcript and one Ensembl transcript that:

- Are identical at the exon/CDS level
- Represent the most clinically relevant isoform
- Are stable identifiers for variant reporting

reftx tracks MANE Select status as a field on transcript records. This enables queries like "give me the MANE Select transcript for BRAF" without external lookups. For clinical variant annotation pipelines, this distinction matters: reporting a variant on the MANE Select transcript ensures consistency across labs and databases.

The MANE Plus Clinical set (additional transcripts for genes with clinically significant non-Select isoforms) is also tracked where applicable.

## See also

- [What is RefgetStore?](refgetstore-explained.md) -- The companion sequence store
- [Digests explained](digests-explained.md) -- How refget digests work
- [reftx reference](reference/reftx-reference.md) -- API and CLI details
- [Getting started with refget](using-services/getting-started.py) -- Tutorial for sequence operations
