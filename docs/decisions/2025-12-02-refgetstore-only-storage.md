# ADR: RefgetStore-Only Storage Strategy

**Date:** 2025-12-02
**Status:** Accepted
**Deciders:** databio team

## Context

We need to decide how to store reference genome sequences for the seqcolapi service. There are three options:

1. **FASTA files only** - Traditional format
2. **RefgetStore only** - Content-addressed, deduplicated storage
3. **Both** - Maintain both formats

## Decision

**Store sequences only in RefgetStore format. Do not store duplicate FASTA files.**

Users who need FASTA files generate them locally using gtars tools.

## Rationale

### Storage Efficiency

RefgetStore provides significant storage savings through:

1. **2-bit encoding** - DNA sequences use 2 bits per base vs 8 bits in text FASTA
2. **Deduplication** - Identical sequences stored once, regardless of how many collections reference them

| Format | Human Genome | Compression vs Raw |
|--------|--------------|-------------------|
| Raw FASTA | ~3.1 GB | 1× (baseline) |
| Gzipped FASTA | ~900 MB | ~3.4× |
| RefgetStore (2-bit) | ~775 MB | ~4× |

### Deduplication Benefits

The key advantage emerges with multiple related genomes:

| Collections | Overlap | Raw FASTA | Gzipped | RefgetStore |
|-------------|---------|-----------|---------|-------------|
| 1 | - | 3.1 GB | 900 MB | 775 MB |
| 10 | 90% | 31 GB | 9 GB | **~1.5 GB** |
| 100 | 90% | 310 GB | 90 GB | **~8 GB** |
| 1000 | 95% | 3.1 TB | 900 GB | **~40 GB** |

For our dataset of ~2 TB raw FASTA with many related assemblies:
- Raw FASTA: ~2 TB
- Gzipped FASTA: ~600 GB
- RefgetStore: **~200-400 GB**

### Single Source of Truth

Maintaining only RefgetStore eliminates:
- Synchronization issues between formats
- Redundant storage costs
- Ambiguity about which format is authoritative

## Consequences

### Positive

- **~80% storage reduction** for our dataset
- **Deduplication scales** with collection count
- **Enables refget/seqcol APIs** - sequence-level random access, content-addressed lookups
- **Single source of truth** - no sync issues

### Negative

- **No direct FASTA download** - Users can't `curl` a FASTA file
- **Requires client tooling** - Users need gtars installed
- **Learning curve** - Different from traditional workflow

### Neutral

- **Future expansion possible** - Lambda-based on-demand generation can be added later if direct FASTA downloads become necessary (see `fasta_drs_lambda_plan.md`)

## User Workflow

Users generate FASTA locally from the remote RefgetStore:

```python
from gtars.refget import RefgetStore

# Load from remote with local cache
store = RefgetStore.load_remote("/tmp/cache", "https://refgetstore.example.com")

# Export FASTA
store.export_fasta(digest, "genome.fa")

# Or export specific chromosomes
store.export_fasta(digest, "genome.fa", ["chr1", "chr2"])
```

This shifts compute from server to client, which is appropriate - the user's machine generates the FASTA they need, in the format they need.

## Related Documents

- `fasta_drs_lambda_plan.md` - Optional Lambda-based on-demand FASTA generation (future enhancement)
