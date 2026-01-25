# %% [markdown]
# # RefgetStore Tutorial
#
# ## Introduction
#
# RefgetStore is a high-performance, content-addressable sequence database that solves
# common problems with managing reference genomes, including a data structure that stores both sequences
# and collections of sequences, automatic deduplication of identical sequences, universal identifiers for
# both sequences and collections using GA4GH-approved standard refget digests, and efficient storage using adaptive
# encoding, optimized for remote and local access, and a file-based storage and retrieval system. Overall,
# RefgetStore provides substantial advantages over traditional FASTA/2bit/bgzip files and other sequence storage solutions.
# This tutorial will introduce you to the basic use of RefgetStore for managing and retrieving sequences.
#
# <div class="admonition success">
#   <p class="admonition-title">Learning objectives</p>
#   <ul>
#     <li>How do I create and load a RefgetStore from FASTA files?</li>
#     <li>How do I retrieve sequences by sequence digest or name from a RefgetStore for analysis in Python?</li>
#     <li>How do I extract specific subsequences, given coordinates of regions from a RefgetStore?</li>
#     <li>How do I export sequences from my RefgetStore into FASTA format?</li>
#     <li>How do I connect to a remote RefgetStore to download sequences or sequence collections into memory or into a local RefgetStore cache?</li>
#   </ul>
# </div>


# %% [markdown]
# ## Features of RefgetStore
#
# - **Automatic deduplication**: Identical sequences are stored once, even across assemblies.
#   For example, chrM is often identical between GRCh38 and GRCh37 - RefgetStore stores it once.
#
# - **Collection management**: RefgetStore stores not only sequences, it also stores sequence collections, so you
#   can manage, query by, and retrieve collections in the same repository (e.g., genome assemblies).
#
# - **Universal identifiers**: Every sequence and sequence collection gets a refget digest.
#   Collections can be retrieved by their digest, and sequences can be retrieved using either sequence digests, or sequence collection digests + local sequence names.
#   This facilitates reproducible research and federated data sharing.
#   RefgetStore also computes additional digests like name_length_pairs and sorted_name_length_pairs, providing
#   ability to quickly identify coordinate systems, collections of unnamed sequences, and more.
#
# - **Efficient storage**: RefgetStore automatically adapts to 2-bit, 3-bit, 4-bit, 5-bit, or 8-bit encoding
#   to compress each sequence based on its alphabet (DNA, RNA, protein, ambiguous). This provides fixed-width encoding,
#   retaining fast random access while achieving better compression than gzip-based compression.
#
# - **Lazy remote access**: A local client connects to remote stores and downloads only the sequences requested,
#   on the fly, with automatic local caching.
#
# - **Fast substring retrieval**: Extract regions without loading entire collections into memory.
#
# - **Batch BED extraction**: Pull sequences for thousands of regions in a single operation, faster than competing tools.
#
# - **File-system based**: No external database required. RefgetStore uses a simple directory structure, so a remote store
#   can be hosted on S3, HTTP, or any file server, and local stores are portable, backed up with regular file system tools,
#   and easy to inspect.


# %% [markdown]
# ## 1. Creating a local RefgetStore from FASTA
#
# Let's start by creating a RefgetStore from some FASTA files. The store computes
# sequence digests and indexes everything for fast retrieval.
#
# RefgetStore offers two storage modes:
#
# - **`in_memory()`**: Loads all sequences into RAM. Best for maximum lookup speed
#   when you have sufficient memory.
#
# - **`on_disk(path)`**: Lazy-loads sequences from disk as they're accessed. Best for
#   large genomes or when you only need a subset of sequences.
#
# We'll create both types so you can see how they work.

# %%
import os
import tempfile
from pathlib import Path

from refget.store import RefgetStore, digest_fasta

# %% [markdown]
# ### Create demo FASTA files (or use your own)

# %%
temp_dir = tempfile.mkdtemp(prefix="refget_tutorial_")

# First FASTA file
fasta1_path = os.path.join(temp_dir, "genome1.fa")
with open(fasta1_path, "w") as f:
    f.write(">chr1\nATGCATGCATGCAGTCGTAGCNNNATGCATGC\n>chr2\nGGGGAAAATTTTCCCC\n")

# Second FASTA file
fasta2_path = os.path.join(temp_dir, "genome2.fa")
with open(fasta2_path, "w") as f:
    f.write(">chrX\nACGTACGTACGTACGTACGTACGTACGT\n>chrY\nTTTTAAAACCCCGGGG\n")

print(f"Created: {fasta1_path}")
print(f"Created: {fasta2_path}")









# %% [markdown] output
# ```
# Created: /tmp/refget_tutorial_2nl7t4d4/genome1.fa
# Created: /tmp/refget_tutorial_2nl7t4d4/genome2.fa
# ```

# %% [markdown]
# ### In-memory store

# %%
store = RefgetStore.in_memory()
store.add_sequence_collection_from_fasta(fasta1_path)
store.add_sequence_collection_from_fasta(fasta2_path)

print(f"Created in-memory store with {len(store)} sequences")










# %% [markdown] output
# ```
# Processing /tmp/refget_tutorial_2nl7t4d4/genome1.fa...
# Added NikmJ6xnuvO741NgL-zszh5_p4DsD3nV (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Processing /tmp/refget_tutorial_2nl7t4d4/genome2.fa...
# Added zmVRc4oI2ny1UgSMdSdjj-FG-TkaUtvh (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Created in-memory store with 4 sequences
# ```

# %% [markdown]
# ### On-disk store (for larger datasets)
#
# For larger datasets, you'll want to persist sequences to disk. This creates a
# directory structure that can be loaded later or even served remotely.
# See [RefgetStore file format](/refget/reference/refgetstore-format/) for details on the directory structure.

# %%
# Create a persistent store on disk
store_path = os.path.join(temp_dir, "my_refget_store")
disk_store = RefgetStore.on_disk(store_path)
disk_store.add_sequence_collection_from_fasta(fasta1_path)
disk_store.add_sequence_collection_from_fasta(fasta2_path)

print(f"Store saved to: {store_path}")









# %% [markdown] output
# ```
# Processing /tmp/refget_tutorial_2nl7t4d4/genome1.fa...
# Added NikmJ6xnuvO741NgL-zszh5_p4DsD3nV (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Processing /tmp/refget_tutorial_2nl7t4d4/genome2.fa...
# Added zmVRc4oI2ny1UgSMdSdjj-FG-TkaUtvh (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Store saved to: /tmp/refget_tutorial_2nl7t4d4/my_refget_store
# ```

# %% [markdown]
# ### Suppressing progress output (quiet mode)
#
# By default, RefgetStore prints progress messages when adding sequences.
# To suppress this output (useful in scripts), use `set_quiet()`:

# %%
quiet_store = RefgetStore.in_memory()
quiet_store.set_quiet(True)
resp = quiet_store.add_sequence_collection_from_fasta(fasta1_path)  # No output

print(f"Quiet mode enabled: {quiet_store.quiet}")
print(f"Store has {len(quiet_store)} sequences")









# %% [markdown] output
# ```
# Quiet mode enabled: True
# Store has 2 sequences
# ```

# %% [markdown]
# ### Loading an existing store
#
# Once you've created a store on disk, you can reload it later:

# %%
# Load the store we just created
loaded_store = RefgetStore.open_local(store_path)
print(f"Loaded store: {loaded_store.stats()}")










# %% [markdown] output
# ```
# Loaded store: {'n_collections_loaded': '0', 'n_sequences_loaded': '0', 'n_sequences': '4', 'storage_mode': 'Encoded', 'n_collections': '2', 'total_disk_size': '1848'}
# ```

# %% [markdown]
# Note: `n_sequences_loaded: 0` means no sequence data has been loaded into memory yet, while `n_sequences` shows the total number of sequences in the store.

# %% [markdown]
# ### Persistence control
#
# You can also control persistence dynamically. This is useful if you want to start
# in-memory for speed, then persist results when you're done:

# %%
# Start in-memory, then persist to disk
persist_store = RefgetStore.in_memory()
persist_store.set_quiet(True)
persist_store.add_sequence_collection_from_fasta(fasta1_path)

# Enable persistence - flushes existing data to disk
persist_path = os.path.join(temp_dir, "persisted_store")
persist_store.enable_persistence(persist_path)
print(f"Enabled persistence to: {persist_path}")

# Later you can also disable persistence (keep in memory only)
persist_store.disable_persistence()
print("Persistence disabled - new sequences stay in memory only")









# %% [markdown] output
# ```
# Enabled persistence to: /tmp/refget_tutorial_2nl7t4d4/persisted_store
# Persistence disabled - new sequences stay in memory only
# ```

# %% [markdown]
# ## 2. Exporting to FASTA
#
# A common task is exporting sequences from your store back to FASTA format.
# You can export full sequences by their digests or by collection.

# %% [markdown]
# ### List sequences and get collection digest
#
# First, let's get the sequence metadata and collection digest we'll use for exports:

# %%
# List sequences in our store
records = list(store.list_sequences())
for m in records:
    print(f"{m.name}: {m.length} bp, sha512t24u={m.sha512t24u}")

# Get the collection digest for genome1
collection = digest_fasta(fasta1_path)
collection_digest = collection.digest
print(f"\nCollection digest: {collection_digest}")










# %% [markdown] output
# ```
# chr2: 16 bp, sha512t24u=8zS0M3VBpV7-TNdB7RjfpMbC8hrz6SbH
# chr1: 32 bp, sha512t24u=EjrJJS1FmLaytz_EHgNvVZ8owSU7kbNb
# chrX: 28 bp, sha512t24u=RCjXT2ppbKhHY6S2106R43I6-QpTqgwT
# chrY: 16 bp, sha512t24u=xNe1wHi4Bzi0uC62_W69LX1JLrPbLCDH
# 
# Collection digest: NikmJ6xnuvO741NgL-zszh5_p4DsD3nV
# ```

# %% [markdown]
# ### Export specific sequences by digest

# %%
# Get digests of sequences to export (records is a list of SequenceMetadata)
digests = [m.sha512t24u for m in records[:2]]

output_path = os.path.join(temp_dir, "exported.fa")
store.export_fasta_by_digests(digests, output_path, line_width=60)

print("Exported FASTA:")
with open(output_path) as f:
    print(f.read())









# %% [markdown] output
# ```
# Exported FASTA:
# >chr2
# GGGGAAAATTTTCCCC
# >chr1
# ATGCATGCATGCAGTCGTAGCNNNATGCATGC
# ```

# %% [markdown]
# ### Export by collection (with optional name filtering)
#
# You can export all sequences from a collection, or filter to specific chromosomes:

# %%
# Export all sequences from a collection
all_output = os.path.join(temp_dir, "all_seqs.fa")
store.export_fasta(collection_digest, all_output, None, None)  # None = all sequences, default line width

# Export only specific sequences by name
subset_output = os.path.join(temp_dir, "subset.fa")
store.export_fasta(collection_digest, subset_output, ["chr1"], None)

print("All sequences:")
with open(all_output) as f:
    print(f.read())

print("Subset (chr1 only):")
with open(subset_output) as f:
    print(f.read())









# %% [markdown] output
# ```
# All sequences:
# >chr2
# GGGGAAAATTTTCCCC
# >chr1
# ATGCATGCATGCAGTCGTAGCNNNATGCATGC
# 
# Subset (chr1 only):
# >chr1
# ATGCATGCATGCAGTCGTAGCNNNATGCATGC
# ```

# %% [markdown]
# ## 3. Retrieving Sequences and Subsequences
#
# For interactive analysis in Python, you can retrieve sequences and subsequences
# directly into memory. RefgetStore treats sequences as the primary unit of storage -
# each unique sequence is stored once regardless of how many collections contain it.

# %% [markdown]
# ### Get sequence by digest
#
# If you know a sequence's refget digest, you can retrieve it directly:

# %%
# Get the first sequence's digest
first_digest = records[0].sha512t24u

# Retrieve by digest
record = store.get_sequence(first_digest)
if record:
    print(f"Name: {record.metadata.name}")
    print(f"Length: {record.metadata.length}")










# %% [markdown] output
# ```
# Name: chr2
# Length: 16
# ```

# %% [markdown]
# ### Get subsequences
#
# You don't need to load entire sequences to get a region of interest:

# %%
# Get a subsequence (0-indexed, half-open interval)
subsequence = store.get_substring(first_digest, 0, 10)
print(f"First 10 bases: {subsequence}")

subsequence = store.get_substring(first_digest, 5, 15)
print(f"Bases 5-15: {subsequence}")










# %% [markdown] output
# ```
# First 10 bases: GGGGAAAATT
# Bases 5-15: AAATTTTCCC
# ```

# %% [markdown]
# ### Browse collections
#
# Beyond individual sequences, RefgetStore tracks collections - groups of sequences
# that belong together (like a genome assembly). You can browse collection metadata
# without loading the full collection:

# %%
# List all collections in the store
collections = list(store.list_collections())
for meta in collections:
    print(f"Collection {meta.digest[:20]}...: {meta.n_sequences} sequences")

# Get the first collection's digest for subsequent examples
first_collection_digest = collections[0].digest

# Get metadata for a specific collection
collection_meta = store.get_collection_metadata(first_collection_digest)
if collection_meta:
    print(f"\nCollection details:")
    print(f"  Sequences: {collection_meta.n_sequences}")
    print(f"  Names digest: {collection_meta.names_digest}")

# Check if a collection is fully loaded in memory
print(f"\nCollection loaded: {store.is_collection_loaded(first_collection_digest)}")









# %% [markdown] output
# ```
# Collection NikmJ6xnuvO741NgL-zs...: 2 sequences
# Collection zmVRc4oI2ny1UgSMdSdj...: 2 sequences
# 
# Collection details:
#   Sequences: 2
#   Names digest: XEsH8IMZ09CBX17iXEWRagH50VGfARLo
# 
# Collection loaded: True
# ```

# %% [markdown]
# ### Iterate through sequences in a collection
#
# Once you have a collection digest, you can load the full collection and iterate
# through its sequences:

# %%
# Get the full collection (not just metadata)
collection = store.get_collection(first_collection_digest)
print(f"Collection digest: {collection.digest}")
print(f"Number of sequences: {len(collection.sequences)}")

# Iterate through sequences in this collection
print("\nSequences in collection:")
for seq in collection.sequences:
    print(f"  {seq.metadata.name}: {seq.metadata.length} bp (digest: {seq.metadata.sha512t24u[:12]}...)")









# %% [markdown] output
# ```
# Collection digest: NikmJ6xnuvO741NgL-zszh5_p4DsD3nV
# Number of sequences: 2
# 
# Sequences in collection:
#   chr2: 16 bp (digest: 8zS0M3VBpV7-...)
#   chr1: 32 bp (digest: EjrJJS1FmLay...)
# ```

# %% [markdown]
# ### Lookup by collection and name
#
# Often you'll want to look up a sequence by its name within a collection (like "chr1" in a genome assembly):

# %%
# Lookup chr1 in the first collection
record = store.get_sequence_by_name(first_collection_digest, "chr1")
if record:
    print(f"Found: {record.metadata.name}")
    print(f"Length: {record.metadata.length} bp")
    print(f"Digest: {record.metadata.sha512t24u}")









# %% [markdown] output
# ```
# Found: chr1
# Length: 32 bp
# Digest: EjrJJS1FmLaytz_EHgNvVZ8owSU7kbNb
# ```

# %% [markdown]
# ## 4. Extracting Regions from BED Files
#
# For bulk extraction of genomic regions, RefgetStore can read coordinates from a BED file.
# This is much faster than extracting regions one at a time.

# %% [markdown]
# ### Get regions as a list

# %%
# Create a BED file with regions
bed_path = os.path.join(temp_dir, "regions.bed")
bed_content = """chr1\t0\t10
chr1\t5\t20
chr2\t0\t8
"""
with open(bed_path, "w") as f:
    f.write(bed_content)

# Extract regions (using collection_digest from Section 2)
sequences = store.substrings_from_regions(collection_digest, bed_path)
for seq in sequences:
    print(f"{seq.start}-{seq.end}: {seq.sequence}")










# %% [markdown] output
# ```
# 0-10: ATGCATGCAT
# 5-20: TGCATGCAGTCGTAG
# 0-8: GGGGAAAA
# ```

# %% [markdown]
# ### Export regions to FASTA
#
# You can also write the extracted regions directly to a FASTA file:

# %%
output_fasta = os.path.join(temp_dir, "regions.fa")
store.export_fasta_from_regions(collection_digest, bed_path, output_fasta)

print(f"Exported to: {output_fasta}")
with open(output_fasta) as f:
    print(f.read())










# %% [markdown] output
# ```
# Exported to: /tmp/refget_tutorial_2nl7t4d4/regions.fa
# >chr1 32 dna3bit EjrJJS1FmLaytz_EHgNvVZ8owSU7kbNb f64c9fb6ad2f6baad56e5a59ee07be63
# ATGCATGCATTGCATGCAGTCGTAG
# >chr2 16 dna2bit 8zS0M3VBpV7-TNdB7RjfpMbC8hrz6SbH 2640016f34792dc6302231ed4d027110
# GGGGAAAA
# ```

# %% [markdown]
# ## 5. Connecting to a Remote RefgetStore
#
# So far we've been working with local data. But what if you want to access sequences
# from a public repository? RefgetStore can connect to remote stores hosted on S3, HTTP,
# or any file server.
#
# The key insight is that you can use a local store as a cache for remote data.
# Sequences are downloaded on-demand and cached locally for future access.
# Let's connect to a remote pangenome store:

# %%
# Remote store URL (Human Pangenome Reference - haplotype-resolved assemblies)
REMOTE_URL = "https://refgenie.s3.us-east-1.amazonaws.com/pangenome_refget_store"

# Create a fresh cache directory for the remote store
remote_cache_path = os.path.join(temp_dir, "remote_cache")
remote_store = RefgetStore.open_remote(
    cache_path=remote_cache_path,
    remote_url=REMOTE_URL
)

# The remote index is fetched automatically - stats show all remote collections!
print(f"Remote store stats: {remote_store.stats()}")

# List available collections from the remote store
remote_collections = list(remote_store.list_collections())
print(f"\nRemote collections available: {len(remote_collections)}")
for c in remote_collections[:3]:
    print(f"  {c.digest}: {c.n_sequences} sequences")









# %% [markdown] output
# ```
# Remote store stats: {'n_collections': '96', 'storage_mode': 'Encoded', 'n_sequences': '37603', 'total_disk_size': '6651362', 'n_sequences_loaded': '0', 'n_collections_loaded': '0'}
# 
# Remote collections available: 96
#   -Sfh5nx4f7dSrGDdfmz7xA0nsN5jh-mN: 566 sequences
#   -Z38q8izmrexleQATeOvcp0sZo6aSXMa: 436 sequences
#   0qveCdMlbF_kYn6XWb7YBy-FtRZ6gSAL: 481 sequences
# ```

# %% [markdown]
# The remote index is fetched automatically when opening the store, so `n_collections`
# and `n_sequences` show the full remote catalog. However, no sequence *data* has been
# downloaded yet (`n_sequences_loaded: 0`).
#
# Let's retrieve a sequence - this will download it and cache it locally:

# %%
# Pick a collection from the remote store
EXAMPLE_COLLECTION = remote_collections[0].digest

# Get the collection to see its sequences
example_coll = remote_store.get_collection(EXAMPLE_COLLECTION)
EXAMPLE_SEQ_NAME = example_coll.sequences[0].metadata.name

print(f"Collection: {EXAMPLE_COLLECTION}")
print(f"Sequence: {EXAMPLE_SEQ_NAME}")

# Retrieve the sequence (this downloads and caches it)
record = remote_store.get_sequence_by_name(EXAMPLE_COLLECTION, EXAMPLE_SEQ_NAME)
if record:
    print(f"\nDownloaded: {record.metadata.name}")
    print(f"Length: {record.metadata.length:,} bp")

# The sequence is now cached locally
print(f"\nRemote store stats: {remote_store.stats()}")









# %% [markdown] output
# ```
# Downloading collection -Sfh5nx4f7dSrGDdfmz7xA0nsN5jh-mN...
# Downloading sequence mqck23WRTrJRrmR-8bRb2IL4KJqP4AZf...
# Collection: -Sfh5nx4f7dSrGDdfmz7xA0nsN5jh-mN
# Sequence: JAHEOS010000235.1
# 
# Downloaded: JAHEOS010000235.1
# Length: 8,613,509 bp
# 
# Remote store stats: {'n_sequences': '37603', 'n_collections_loaded': '1', 'total_disk_size': '8904984', 'storage_mode': 'Encoded', 'n_collections': '96', 'n_sequences_loaded': '1'}
# ```

# %% [markdown]
# Notice how `n_sequences_loaded` increased - the sequence data is now cached locally.
# Subsequent requests for this sequence will be served from disk without network access.

# %% [markdown]
# ### Extract regions from a remote collection
#
# Let's extract some regions from the remote pangenome using a BED file.
# This demonstrates how you can work with remote data just like local data:

# %%
# Create a BED file with regions from the remote collection
remote_bed_path = os.path.join(temp_dir, "remote_regions.bed")
with open(remote_bed_path, "w") as f:
    # Using the sequence we just downloaded
    f.write(f"{EXAMPLE_SEQ_NAME}\t1000\t1050\n")
    f.write(f"{EXAMPLE_SEQ_NAME}\t5000\t5100\n")

# Extract regions - this uses the cached sequence, no re-download needed
remote_regions = remote_store.substrings_from_regions(EXAMPLE_COLLECTION, remote_bed_path)
for seq in remote_regions:
    print(f"{seq.chrom_name} {seq.start}-{seq.end}: {seq.sequence[:40]}...")

# Export to FASTA
remote_regions_fasta = os.path.join(temp_dir, "remote_regions.fa")
remote_store.export_fasta_from_regions(EXAMPLE_COLLECTION, remote_bed_path, remote_regions_fasta)
print(f"\nExported to {remote_regions_fasta}")









# %% [markdown] output
# ```
# JAHEOS010000235.1 1000-1050: CTCCCCGTGGGATGGGCAAGCGGGCGAGGCTGGACAGGAC...
# JAHEOS010000235.1 5000-5100: GGAGTGGGGCTGTCTGAGGTTCCCCAGTGAACTTTGTGCT...
# 
# Exported to /tmp/refget_tutorial_2nl7t4d4/remote_regions.fa
# ```

# %% [markdown]
# ## 6. Using the CLI
#
# Everything we've done in Python can also be done from the command line.
# Here are the equivalent CLI commands for common operations.
#
# Check the store stats:
#
# ```bash
# refget store stats --path /path/to/store
# ```

# %%
import subprocess

def run_cli(args):
    """Run a CLI command and print the command + output."""
    cmd = " ".join(args)
    print(f"$ {cmd}")
    result = subprocess.run(args, capture_output=True, text=True)
    print(result.stdout)

run_cli(["refget", "store", "stats", "--path", store_path])









# %% [markdown] output
# ```
# $ refget store stats --path /tmp/refget_tutorial_2nl7t4d4/my_refget_store
# {
#   "n_sequences_loaded": "0",
#   "storage_mode": "Encoded",
#   "total_disk_size": "1848",
#   "n_sequences": "4",
#   "n_collections": "2",
#   "n_collections_loaded": "0",
#   "collections": 2
# }
# ```

# %% [markdown]
# Retrieve a subsequence by digest:
#
# ```bash
# refget store seq <digest> --path /path/to/store --start 0 --end 10
# ```

# %%
run_cli(["refget", "store", "seq", first_digest, "--path", store_path, "--start", "0", "--end", "10"])









# %% [markdown] output
# ```
# $ refget store seq 8zS0M3VBpV7-TNdB7RjfpMbC8hrz6SbH --path /tmp/refget_tutorial_2nl7t4d4/my_refget_store --start 0 --end 10
# GGGGAAAATT
# ```

# %% [markdown]
# For the full list of CLI commands and options, see the [CLI reference](../reference/cli.md).

# %% [markdown]
# <div class="admonition success">
#   <p class="admonition-title">Summary</p>
#   <ul>
#     <li>RefgetStore provides <strong>content-addressable storage</strong> for sequences - identical sequences are automatically deduplicated, even across different genome assemblies.</li>
#     <li>Choose <strong>in-memory mode</strong> for maximum speed, or <strong>on-disk mode</strong> for large datasets and persistence. You can switch between them dynamically.</li>
#     <li>Every sequence and collection gets a <strong>refget digest</strong>, enabling universal identification and retrieval by either digest or collection + name.</li>
#     <li><strong>Remote stores</strong> work transparently with local caching - sequences are downloaded on-demand and cached locally for future access.</li>
#     <li><strong>BED file extraction</strong> enables efficient batch retrieval of genomic regions, much faster than extracting regions one at a time.</li>
#     <li>The same operations are available via <strong>Python API</strong> or <strong>command-line interface</strong>.</li>
#   </ul>
# </div>

# %%
# Cleanup
import shutil
shutil.rmtree(temp_dir)

