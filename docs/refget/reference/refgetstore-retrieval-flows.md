# RefgetStore sequence retrieval flows

A RefgetStore can be read from three places: sequence bytes may be **resident in memory**, sitting in a **local `.seq` file** on disk, or available only from a **remote HTTP store**. Because moving whole chromosomes is expensive, the store offers three distinct retrieval *flows* so you can match the cost to your access pattern instead of always paying for a full download.

This page is a reference for those flows: what each one fetches, what it costs, and when to use it.

## The three flows

| Flow | What it moves | Peak memory | Persists locally? | Repeated remote reads | Best for |
|------|---------------|-------------|-------------------|-----------------------|----------|
| **1. Partial read** (`get_substring`, `get_substrings`) | Only the bytes covering `[start, end)`, returned as a string | O(region) | No | (resident/local only) | Sparse, random-access extraction from data that is already resident or on local disk |
| **2. Streaming** (`stream_sequence`) | Only the bytes covering `[start, end)`, as a byte/character stream — **local seek or remote HTTP `Range`** | O(1) in region length | No | Re-fetches each call | One-off or large region pulls from a **remote** store without downloading whole sequences |
| **3. Load &amp; cache** (`load_sequence`, `load_all_sequences`) | The **whole** sequence `.seq`, downloaded once | O(sequence) | Yes (under the local cache) | Served locally after first load | Repeated access to the same sequences; warm reuse across sessions |

The key trade-off is **flow 2 vs flow 3** for remote data:

- **Flow 2 (streaming / byte-range)** fetches only the bases you ask for. A 50 bp lookup transfers ~50 bytes. Nothing is stored, so a second read of the same region fetches again. Ideal for *sparse* extraction — a handful of loci scattered across a genome.
- **Flow 3 (load &amp; cache)** downloads the entire sequence (a whole chromosome can be tens of MB even encoded), persists it to the local cache, and holds it in memory. The first touch is expensive; every read afterward is local and fast. Ideal for *dense or repeated* access — e.g. converting an entire VCF against one assembly.

Flow 1 is the convenience layer over already-available data: once a sequence is resident (flow 3) or its `.seq` is on local disk, `get_substring` reads just the covering bytes with no full-sequence load.

## Source resolution

`get_substring` / `stream_sequence` resolve their byte source in order:

1. **Resident** — if the sequence is fully loaded (`Full`), read from the in-memory buffer.
2. **Local `.seq`** — if a local store path holds the file, do a positioned read of just the covering bytes (the whole sequence never enters RAM).
3. **Remote byte-range** — *streaming only*: if the file is remote, issue an HTTP `Range:` request for the covering bytes. This requires the build's `http` feature.

`get_substring` stops at step 2: against a **remote-only** sequence it raises an error rather than silently downloading. To read a remote region, use **flow 2** (stream the region) or **flow 3** (`load_sequence` to download and cache the whole sequence, after which flow 1 serves it from memory).

## Choosing a flow

```
Need bases for a region of a sequence?
│
├─ Is the sequence resident or on local disk?
│     └─ Yes → Flow 1: get_substring / get_substrings
│
└─ Is it remote-only?
      ├─ A few sparse regions, read once → Flow 2: stream_sequence (byte-range; no download)
      └─ Many regions / repeated reads    → Flow 3: load_sequence, then Flow 1
```

## Binding interface

The same three flows are exposed through a consistent interface across the bindings — Python, R, Node.js (native), and WebAssembly:

| Method | Flow | Notes |
|--------|------|-------|
| `get_substring(digest, start, end)` | 1 | Single region → string |
| `get_substrings(digest, ranges)` | 1 | Many regions of one sequence in a single call |
| `stream_sequence(digest, start, end)` | 2 | Region as a stream; the remote byte-range path |
| `load_sequence(digest)` | 3 | Download + cache + make resident |
| `load_all_sequences()` | 3 | Eagerly promote every sequence |

In the browser, WebAssembly has no synchronous disk or network access, so the fetch-and-cache machinery for flows 2 and 3 is driven from JavaScript (fetching `.seq` bytes, caching them in the Origin-Private File System) and handed to the in-memory wasm store. The method names mirror the native bindings so the mental model carries over.

!!! note
    On-demand remote retrieval through the byte-range path (flow 2) and uniform coverage of all three flows across every binding are being rolled out. The flow definitions and the trade-offs above are stable; consult your binding's release notes for the exact methods currently available.

## Related reference

- [RefgetStore file format](refgetstore-format.md) — the on-disk/remote directory layout, including the `sequences/<ab>/<digest>.seq` files these flows read.
- [RefgetStore encoding](encoding-comparison.md) — how `.seq` bytes map to bases, which determines the byte range a region read must fetch.
