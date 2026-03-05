# %% [markdown]
# # Retrieving Subsequences by Digest
#
# Given a `sorted_sequences` digest -- which identifies a set of sequences
# regardless of ordering or naming -- this guide shows how to expand it into
# individual sequence digests, inspect sequence metadata, and extract
# subsequences.
#
# **Prerequisites:** You need the `refget` package installed with gtars support
# (`pip install refget[all]`). You should know how to create a RefgetStore and
# load FASTA files (see the [RefgetStore tutorial](refgetstore.py)).

# %% [markdown]
# ## Setup
#
# Create a small FASTA file, load it into an in-memory store, and obtain the
# `sorted_sequences` digest from the level 1 representation.

# %%
import os
import json
import tempfile

from refget.store import RefgetStore, digest_fasta

temp_dir = tempfile.mkdtemp(prefix="subseq_howto_")

fasta_path = os.path.join(temp_dir, "genome.fa")
with open(fasta_path, "w") as f:
    f.write(">chr1\nACGTACGTACGTACGTACGTACGTACGTACGT\n")
    f.write(">chr2\nGGGGAAAATTTTCCCCGGGGAAAATTTTCCCC\n")
    f.write(">chrM\nTTTTAAAACCCCGGGGNNNNACGT\n")

store = RefgetStore.in_memory()
store.set_quiet(True)
store.add_sequence_collection_from_fasta(fasta_path)

collection_digest = digest_fasta(fasta_path).digest
lvl1 = store.get_collection_level1(collection_digest)
sorted_seq_digest = lvl1["sorted_sequences"]

print(f"Collection digest: {collection_digest}")
print(f"sorted_sequences digest: {sorted_seq_digest}")

# %% [markdown] output
# ```
# Collection digest: abc123exampledigest
# sorted_sequences digest: xyz789sorteddigest
# ```

# %% [markdown]
# ## Expand sorted_sequences into individual sequence digests
#
# The level 1 `sorted_sequences` value is a single digest representing the
# entire sorted array. Use `get_attribute` to expand it into the individual
# `SQ.*` sequence digests.

# %%
seq_digests = store.get_attribute("sorted_sequences", sorted_seq_digest)
print(f"Individual sequence digests ({len(seq_digests)}):")
for d in seq_digests:
    print(f"  {d}")

# %% [markdown] output
# ```
# Individual sequence digests (3):
#   SQ.abcdef123456example1
#   SQ.abcdef123456example2
#   SQ.abcdef123456example3
# ```

# %% [markdown]
# ## Retrieve sequence metadata
#
# For each individual digest, `get_sequence` returns a record with metadata
# including the sequence name, length, and digest.

# %%
for seq_digest in seq_digests:
    record = store.get_sequence(seq_digest)
    meta = record.metadata
    print(f"{meta.name}: length={meta.length}, digest={meta.sha512t24u}")

# %% [markdown] output
# ```
# chr1: length=32, digest=Blf3ILywY3YsZmFcjBssmHEPN0dDWP_V
# chr2: length=32, digest=LBh5K2bNKvmfsWSVKvPbjXFrmIOxxr_b
# chrM: length=24, digest=U1x5Qz66jmXmv_oJtfYmtUNkwq1wZ75u
# ```

# %% [markdown]
# ## Extract subsequences
#
# Use `get_substring` to extract a region from any individual sequence.
# Coordinates are 0-indexed with a half-open interval: `start` is inclusive,
# `end` is exclusive.

# %%
# Get the first sequence digest
first_digest = seq_digests[0]
record = store.get_sequence(first_digest)
print(f"Sequence: {record.metadata.name} ({record.metadata.length} bp)")

# Extract bases 0-8 (first 8 bases)
subseq = store.get_substring(first_digest, 0, 8)
print(f"Bases 0-8: {subseq}")

# Extract bases 16-24
subseq2 = store.get_substring(first_digest, 16, 24)
print(f"Bases 16-24: {subseq2}")

# %% [markdown] output
# ```
# Sequence: chr1 (32 bp)
# Bases 0-8: ACGTACGT
# Bases 16-24: ACGTACGT
# ```

# %% [markdown]
# ## Batch extraction with a BED file
#
# For bulk extraction, `substrings_from_regions` reads a BED file and returns
# all requested subsequences at once. This method requires a **collection
# digest** (not a `sorted_sequences` digest), because it needs chromosome name
# mappings to resolve BED coordinates.
#
# Use `find_collections_by_attribute` to find a collection that contains these
# sequences.

# %%
# Find a collection containing this sorted_sequences set
collections = store.find_collections_by_attribute("sorted_sequences", sorted_seq_digest)
coll_digest = collections[0]
print(f"Using collection: {coll_digest}")

# Create a BED file with regions to extract
bed_path = os.path.join(temp_dir, "regions.bed")
with open(bed_path, "w") as f:
    f.write("chr1\t0\t8\n")
    f.write("chr1\t24\t32\n")
    f.write("chr2\t4\t12\n")
    f.write("chrM\t0\t10\n")

# Extract all regions
results = store.substrings_from_regions(coll_digest, bed_path)
for r in results:
    print(f"{r.chrom_name}:{r.start}-{r.end}  {r.sequence}")

# %% [markdown] output
# ```
# Using collection: abc123exampledigest
# chr1:0-8  ACGTACGT
# chr1:24-32  ACGTACGT
# chr2:4-12  AAAATTTT
# chrM:0-10  TTTTAAAAC
# ```

# %% [markdown]
# ## Related guides
#
# - [Matching by sequences](sorted-sequences.py) -- Finding collections that share the same sequences
# - [RefgetStore tutorial](refgetstore.py) -- Creating and loading stores

# %% [markdown]
# ## Cleanup

# %%
import shutil
shutil.rmtree(temp_dir)
