# Refget Python API Documentation

## Package Overview

The `refget` package provides a Python implementation of the GA4GH refget protocol for accessing reference sequences and sequence collections. It enables standardized access to reference genome sequences using computed identifiers.

### Key Features

- **Sequence Retrieval**: Fetch reference sequences by computed digests
- **Sequence Collections**: Manage and query collections of sequences (seqcol)
- **Multiple Digest Types**: Support for MD5, SHA512, and other digest algorithms
- **Client/Server Architecture**: Both client libraries and server implementations
- **FastAPI Integration**: Easy integration with FastAPI applications
- **Compliance Testing**: Tools for testing refget API compliance

## Core Functions

### FASTA Processing

Functions for converting FASTA files to refget-compatible formats:

::: refget.fasta_to_seqcol_dict
    options:
      heading_level: 3

::: refget.fasta_to_digest
    options:
      heading_level: 3

### FastAPI Integration

::: refget.create_refget_router
    options:
      heading_level: 3

## Client Classes

The client module provides interfaces for interacting with refget-compliant servers.

### SequenceClient

Client for retrieving individual sequences from refget servers:

::: refget.clients.SequenceClient
    options:
      show_source: true
      show_signature: true
      heading_level: 3

### SequenceCollectionClient

Client for working with sequence collections (seqcol):

::: refget.clients.SequenceCollectionClient
    options:
      show_source: true
      show_signature: true
      heading_level: 3

## Agent Classes

Agents provide higher-level abstractions for working with refget data.

### RefgetDBAgent

Database agent for managing refget data storage:

::: refget.agents.RefgetDBAgent
    options:
      show_signature: true
      heading_level: 3

### SequenceCollectionAgent

Agent for sequence collection operations:

::: refget.agents.SequenceCollectionAgent
    options:
      heading_level: 3

### SequenceAgent

Agent for individual sequence operations:

::: refget.agents.SequenceAgent
    options:
      heading_level: 3

## GlobalRefgetStore (gtars)

High-performance sequence store for GA4GH refget sequences with lazy-loading support.

```python
from gtars.refget import GlobalRefgetStore
```

GlobalRefgetStore provides content-addressable storage for reference genome sequences following the GA4GH refget specification. Supports both local and remote stores with on-demand sequence loading.

### Creating a Store

```python
# In-memory store
store = GlobalRefgetStore.in_memory()
store.add_sequence_collection_from_fasta("genome.fa")

# Disk-backed store
store = GlobalRefgetStore.on_disk("/data/store")
store.add_sequence_collection_from_fasta("genome.fa")
```

### Loading Existing Stores

```python
# Load local store
store = GlobalRefgetStore.load_local("/data/hg38")

# Load remote store with caching
store = GlobalRefgetStore.load_remote(
    "/local/cache",
    "https://example.com/hg38"
)
```

### Retrieving Sequences

```python
# By digest
record = store.get_sequence_by_id("aKF498dAxcJAqme6QYQ7EZ07-fiw8Kw2")

# By collection and name
record = store.get_sequence_by_collection_and_name(
    "uC_UorBNf3YUu1YIDainBhI94CedlNeH",
    "chr1"
)

# Get substring
seq = store.get_substring("chr1_digest", 0, 1000)
```

### Exporting

```python
# Export collection to FASTA
store.export_fasta("collection_digest", "output.fa")

# Export specific sequences by digest
store.export_fasta_by_digests(["digest1", "digest2"], "output.fa")

# Export regions from BED file
store.export_fasta_from_regions("collection_digest", "regions.bed", "output.fa")
```

### Key Methods

| Method | Description |
|--------|-------------|
| `in_memory()` | Create in-memory store |
| `on_disk(path)` | Create disk-backed store |
| `load_local(path)` | Load existing local store |
| `load_remote(cache, url)` | Load remote store with caching |
| `add_sequence_collection_from_fasta(path)` | Import FASTA file |
| `get_sequence_by_id(digest)` | Get sequence by SHA-512/24u or MD5 |
| `get_sequence_by_collection_and_name(col, name)` | Get sequence by collection + name |
| `get_substring(digest, start, end)` | Extract subsequence |
| `export_fasta(col, path)` | Export collection to FASTA |
| `stats()` | Get store statistics |
| `len(store)` | Number of sequences |

For detailed method signatures and parameters, use `help(GlobalRefgetStore)` in Python.

