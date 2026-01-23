# %% [markdown]
# # RefgetStore Tutorial
#
# ## Introduction 
#
# RefgetStore is a high-performance, content-addressable sequence database that solves
# common problems with managing reference genomes:
#
# - **Automatic deduplication**: Identical sequences are stored once, even across assemblies.
#   For example, chrM is often identical between GRCh38 and GRCh37 - RefgetStore stores it once.
#
# - **Collection management**: RefgetStore stores not only sequences, it also stores sequence collections, so you
#   can manage, query by, and retrieve collections in the same repository (e.g., genome assemblies).
#
# - **Universal identifiers**: Every sequence and sequence collection gets a GA4GH-compliant digest.
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
#
# <div class="admonition success">
#   <p class="admonition-title">Learning objectives</p>
#   <ul>
#     <li>How do I create and load a RefgetStore from FASTA files?</li>
#     <li>How do I connect to a remote RefgetStore and cache sequences locally?</li>
#     <li>How do I retrieve sequences by digest or by name?</li>
#     <li>How do I extract regions from a BED file?</li>
#     <li>How do I export sequences back to FASTA format?</li>
#   </ul>
# </div>

# %% [markdown]
# ## 1. Creating or loading a local RefgetStore from FASTA
#
# You can create a RefgetStore from one or more FASTA files. The store
# computes sequence digests and indexes everything for fast retrieval.
#
# RefgetStore offers two storage modes:
#
# - **`in_memory()`**: Loads all sequences into RAM. Best for maximum lookup speed
#   when you have sufficient memory.
#
# - **`on_disk(path)`**: Lazy-loads sequences from disk as they're accessed. Best for
#   large genomes or when you only need a subset of sequences.

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
# Created: /tmp/refget_tutorial_x4ugn1ot/genome1.fa
# Created: /tmp/refget_tutorial_x4ugn1ot/genome2.fa
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
# Processing /tmp/refget_tutorial_x4ugn1ot/genome1.fa...
# Added NikmJ6xnuvO741NgL-zszh5_p4DsD3nV (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Processing /tmp/refget_tutorial_x4ugn1ot/genome2.fa...
# Added zmVRc4oI2ny1UgSMdSdjj-FG-TkaUtvh (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Created in-memory store with 4 sequences
# ```

# %% [markdown]
# ### On-disk store (for larger datasets)

# %%
# Create a persistent store on disk
store_path = os.path.join(temp_dir, "my_refget_store")
disk_store = RefgetStore.on_disk(store_path)
disk_store.add_sequence_collection_from_fasta(fasta1_path)

print(f"Store saved to: {store_path}")


# %% [markdown] output
# ```
# Processing /tmp/refget_tutorial_x4ugn1ot/genome1.fa...
# Added NikmJ6xnuvO741NgL-zszh5_p4DsD3nV (2 seqs) in 0.0s [0.0s digest + 0.0s encode]
# Store saved to: /tmp/refget_tutorial_x4ugn1ot/my_refget_store
# ```

# %% [markdown]
# See [RefgetStore file format](../reference/refgetstore-format.md) for details on the directory structure.

# %% [markdown]
# ### Loading an existing store

# %%
# Load the store we just created
loaded_store = RefgetStore.load_local(store_path)
print(f"Loaded store: {loaded_store.stats()}")



# %% [markdown] output
# ```
# Loaded store: {'n_sequences_loaded': '0', 'n_sequences': '2', 'n_collections': '1', 'storage_mode': 'Encoded', 'n_collections_loaded': '0'}
# ```

# %% [markdown]
# ## 2. Connecting to a Remote RefgetStore
#
# RefgetStore can load from remote URLs (e.g., S3). Only metadata is fetched
# initially; sequences are downloaded on-demand and cached locally.

# %%
# Remote store URL (2023 Human Pangenome Reference - 47 haplotype-resolved assemblies)
REMOTE_URL = "https://refgenie.s3.us-east-1.amazonaws.com/pangenome_refget_store"
CACHE_DIR = f"{Path.home()}/.refget/pangenome_cache"

remote_store = RefgetStore.load_remote(
    cache_path=str(CACHE_DIR),
    remote_url=REMOTE_URL
)

print(f"Loaded {len(remote_store)} sequences from remote store")



# %% [markdown] output
# ```
# Loaded 37603 sequences from remote store
# ```

# %% [markdown]
# Note: `n_sequences_loaded: 0` means no sequence data has been fetched yet.
# Sequences are downloaded on first access and cached locally.

# %% [markdown]
# ## 3. Retrieving Sequences and Substrings
#
# Once you have a store, you can retrieve sequences by their refget sequence digest or
# by refget collection digest + sequence name.

# %% [markdown]
# ### List available sequences

# %%
# List sequences in our local store
records = list(store.sequence_records())
for rec in records:
    m = rec.metadata
    print(f"{m.name}: {m.length} bp, sha512t24u={m.sha512t24u}")



# %% [markdown] output
# ```
# chr1: 32 bp, sha512t24u=EjrJJS1FmLaytz_EHgNvVZ8owSU7kbNb
# chrY: 16 bp, sha512t24u=xNe1wHi4Bzi0uC62_W69LX1JLrPbLCDH
# chrX: 28 bp, sha512t24u=RCjXT2ppbKhHY6S2106R43I6-QpTqgwT
# chr2: 16 bp, sha512t24u=8zS0M3VBpV7-TNdB7RjfpMbC8hrz6SbH
# ```

# %% [markdown]
# ### Get sequence by digest

# %%
# Get the first sequence's digest
first_digest = records[0].metadata.sha512t24u

# Retrieve by digest
record = store.get_sequence_by_id(first_digest)
if record:
    print(f"Name: {record.metadata.name}")
    print(f"Length: {record.metadata.length}")



# %% [markdown] output
# ```
# Name: chr1
# Length: 32
# ```

# %% [markdown]
# ### Get substrings

# %%
# Get a substring (0-indexed, half-open interval)
substring = store.get_substring(first_digest, 0, 10)
print(f"First 10 bases: {substring}")

substring = store.get_substring(first_digest, 5, 15)
print(f"Bases 5-15: {substring}")



# %% [markdown] output
# ```
# First 10 bases: ATGCATGCAT
# Bases 5-15: TGCATGCAGT
# ```

# %% [markdown]
# ### Lookup by collection and name
#
# You can also look up by
# collection digest + sequence name.

# %%
# Example with the pangenome store
EXAMPLE_COLLECTION = "0aHV7I-94paL9Z1H4LNlqsW3WxJhlou5"
EXAMPLE_SEQ_NAME = "JAGYVX010000006.1 unmasked:primary_assembly HG03540.pri.mat.f1_v2:JAGYVX010000006.1:1:96320881:1"

record = remote_store.get_sequence_by_collection_and_name(EXAMPLE_COLLECTION, EXAMPLE_SEQ_NAME)
if record:
    print(f"Found: {record.metadata.name[:60]}...")
    print(f"Length: {record.metadata.length:,} bp")
    print(f"Digest: {record.metadata.sha512t24u}")



# %% [markdown] output
# ```
# Found: JAGYVX010000006.1 unmasked:primary_assembly HG03540.pri.mat....
# Length: 96,320,881 bp
# Digest: G8nBQLmLVRhsrIq31xku2dNu5dHExVkE
# ```

# %% [markdown]
# ## 4. Extracting Regions from BED Files
#
# RefgetStore can extract sequences for regions specified in a BED file.
# This is useful for pulling out specific genomic regions in bulk.

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

# Get the collection digest for our local store
collection = digest_fasta(fasta1_path)
collection_digest = collection.digest

# Extract regions
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

# %%
output_fasta = os.path.join(temp_dir, "regions.fa")
store.export_fasta_from_regions(collection_digest, bed_path, output_fasta)

print(f"Exported to: {output_fasta}")
with open(output_fasta) as f:
    print(f.read())



# %% [markdown] output
# ```
# Exported to: /tmp/refget_tutorial_x4ugn1ot/regions.fa
# >chr1 32 dna3bit EjrJJS1FmLaytz_EHgNvVZ8owSU7kbNb f64c9fb6ad2f6baad56e5a59ee07be63
# ATGCATGCATTGCATGCAGTCGTAG
# >chr2 16 dna2bit 8zS0M3VBpV7-TNdB7RjfpMbC8hrz6SbH 2640016f34792dc6302231ed4d027110
# GGGGAAAA
# ```

# %% [markdown]
# ## 5. Exporting to FASTA
#
# You can export sequences from a store back to FASTA format.

# %% [markdown]
# ### Export specific sequences by digest

# %%
# Get digests of sequences to export
digests = [rec.metadata.sha512t24u for rec in records[:2]]

output_path = os.path.join(temp_dir, "exported.fa")
store.export_fasta_by_digests(digests, output_path, line_width=60)

print("Exported FASTA:")
with open(output_path) as f:
    print(f.read())



# %% [markdown] output
# ```
# Exported FASTA:
# >chr1
# ATGCATGCATGCAGTCGTAGCNNNATGCATGC
# >chrY
# TTTTAAAACCCCGGGG
# ```

# %% [markdown]
# ### Export from remote store

# %%
# Export a few sequences from the pangenome store
remote_digests = [
    "du4GiRD_OcmdmCn_RmImyb71YZ4XoCdk",
    "cPD3x19YSSfB_TzCKAnp1tzjOKlQVu7l",
]

remote_output = os.path.join(temp_dir, "pangenome_export.fa")
remote_store.export_fasta_by_digests(remote_digests, remote_output, line_width=80)

# Show first few lines
with open(remote_output) as f:
    for i, line in enumerate(f):
        if i >= 8:
            print("...")
            break
        print(line.rstrip()[:70])



# %% [markdown] output
# ```
# >JAGYVI010000141.1 unmasked:primary_assembly HG02257.alt.pat.f1_v2:JAG
# ACATAAAATATCAAATAACACAAACTATATATTACATACTGTACTTAAAATATCAAACTACCCATACTAT
# CTGTACATAAAATATCAAACAACCCAAACTATATATTATATACTGCACAGAATATATCAAAGTACACATA
# TATACTGTATATAAAATATCAAAGTACCCAAAGTATATATTATATACTGTACATAAAATATCAAAGTACC
# ATTATATACCGTACATAAAATATCAAAGTACCCAAAGTATGTATTATATACTGTACATAAAATATCAAGG
# ATGTATTATATACTGTATATAAAATATGAAAGCACCCAAACATTTATAATAAACTGAACATTAAATATCA
# ACTATAAACTGTACATAAAATATCAAAGTAACAAAACTATTTATTTTATACTGGACATAAAATATCAAAA
# ATATATACGGTACTGCACATAAAATATCGAAGTACCCAATGTATGTATTATATACTGTACATAAAATATC
# ...
# ```

# %% [markdown]
# ## Store Directory Structure
#
# When you save a RefgetStore to disk (using `on_disk()` or `write_store_to_dir()`),
# it creates this structure:
#
# ```
# my_refget_store/
# ├── rgstore.json        # Store metadata
# ├── sequences.rgsi      # Sequence index
# ├── collections.rgci    # Collection metadata index
# ├── sequences/          # Encoded sequence data
# │   └── {prefix}/{digest}.seq
# └── collections/        # Collection files
#     └── {digest}.rgsi
# ```

# %% [markdown]
# ## Using the CLI
#
# You can also manage RefgetStores from the command line:
#
# ```bash
# # Initialize a store
# refget store init --path ~/.refget/store
#
# # Add a FASTA file
# refget store add genome.fa
#
# # List collections
# refget store list
#
# # Retrieve a sequence
# refget store seq <digest> --name chr1 --start 100 --end 200
#
# # Export to FASTA
# refget store export <digest> -o output.fa --bed regions.bed
# ```

# %% [markdown]
# <div class="admonition success">
#   <p class="admonition-title">Summary</p>
#   <ul>
#     <li><code>RefgetStore.in_memory()</code> / <code>RefgetStore.on_disk(path)</code> - create stores</li>
#     <li><code>RefgetStore.load_local(path)</code> / <code>RefgetStore.load_remote(cache, url)</code> - load stores</li>
#     <li><code>store.add_sequence_collection_from_fasta(path)</code> - add sequences from FASTA</li>
#     <li><code>store.get_sequence_by_id(digest)</code> - retrieve by digest</li>
#     <li><code>store.get_sequence_by_collection_and_name(collection, name)</code> - retrieve by name</li>
#     <li><code>store.substrings_from_regions(collection, bed_path)</code> - batch extract regions</li>
#   </ul>
# </div>

# %%
# Cleanup
import shutil
shutil.rmtree(temp_dir)
print("Tutorial complete!")


# %% [markdown] output
# ```
# Tutorial complete!
# ```

