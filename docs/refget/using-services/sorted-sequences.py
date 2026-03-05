# %% [markdown]
# # Finding Duplicate Genomes with Sorted Sequences
#
# The `sorted_sequences` ancillary digest identifies the set of sequences in a
# collection regardless of chromosome ordering or naming. Two FASTA files that
# contain identical sequences but use different chromosome names or a different
# order will share the same `sorted_sequences` digest.
#
# This guide shows how to use `sorted_sequences` to find genome collections
# that contain the same sequences.
#
# **Prerequisites:** You need the `refget` package installed with gtars support
# (`pip install refget[all]`). You should know how to create a RefgetStore and
# load FASTA files (see the [RefgetStore tutorial](refgetstore.py)).

# %% [markdown]
# ## Setup
#
# Create three FASTA files with identical sequences but different chromosome
# names and ordering, then load them into an in-memory store.

# %%
import os
import json
import tempfile

from refget.store import RefgetStore, digest_fasta

temp_dir = tempfile.mkdtemp(prefix="sorted_seq_howto_")

# Genome A: original names and order
fasta_a = os.path.join(temp_dir, "genome_a.fa")
with open(fasta_a, "w") as f:
    f.write(">chr1\nACGTACGTACGTACGT\n>chr2\nGGGGAAAATTTTCCCC\n")

# Genome B: same sequences, different chromosome names
fasta_b = os.path.join(temp_dir, "genome_b.fa")
with open(fasta_b, "w") as f:
    f.write(">seq_alpha\nACGTACGTACGTACGT\n>seq_beta\nGGGGAAAATTTTCCCC\n")

# Genome C: same sequences, reversed order
fasta_c = os.path.join(temp_dir, "genome_c.fa")
with open(fasta_c, "w") as f:
    f.write(">chr2\nGGGGAAAATTTTCCCC\n>chr1\nACGTACGTACGTACGT\n")

store = RefgetStore.in_memory()
store.set_quiet(True)

store.add_sequence_collection_from_fasta(fasta_a)
store.add_sequence_collection_from_fasta(fasta_b)
store.add_sequence_collection_from_fasta(fasta_c)

digest_a = digest_fasta(fasta_a).digest
digest_b = digest_fasta(fasta_b).digest
digest_c = digest_fasta(fasta_c).digest

print(f"Genome A: {digest_a}")
print(f"Genome B: {digest_b}")
print(f"Genome C: {digest_c}")

# %% [markdown] output
# ```
# Genome A: aBC123example_digestA_placeholder
# Genome B: xYZ789example_digestB_placeholder
# Genome C: qRS456example_digestC_placeholder
# ```

# %% [markdown]
# All three collections have different top-level digests because they differ
# in names or ordering.

# %% [markdown]
# ## Retrieve the sorted_sequences digest
#
# The level 1 representation includes a `sorted_sequences` key. This digest
# is computed from the sorted list of individual sequence digests, so it is
# invariant to both naming and ordering.

# %%
lvl1_a = store.get_collection_level1(digest_a)
lvl1_b = store.get_collection_level1(digest_b)
lvl1_c = store.get_collection_level1(digest_c)

print(f"Genome A sorted_sequences: {lvl1_a['sorted_sequences']}")
print(f"Genome B sorted_sequences: {lvl1_b['sorted_sequences']}")
print(f"Genome C sorted_sequences: {lvl1_c['sorted_sequences']}")
print(f"\nAll match: {lvl1_a['sorted_sequences'] == lvl1_b['sorted_sequences'] == lvl1_c['sorted_sequences']}")

# %% [markdown] output
# ```
# Genome A sorted_sequences: AbCdEfGh_sorted_seq_placeholder
# Genome B sorted_sequences: AbCdEfGh_sorted_seq_placeholder
# Genome C sorted_sequences: AbCdEfGh_sorted_seq_placeholder
#
# All match: True
# ```

# %% [markdown]
# ## Find all collections sharing the same sequences
#
# Use `find_collections_by_attribute` with the `sorted_sequences` digest to
# retrieve every collection in the store that contains the same set of sequences.

# %%
sorted_seq_digest = lvl1_a["sorted_sequences"]
matches = store.find_collections_by_attribute("sorted_sequences", sorted_seq_digest)

print(f"Collections with sorted_sequences = {sorted_seq_digest}:")
for m in matches:
    print(f"  {m}")
print(f"\nTotal: {len(matches)}")

# %% [markdown] output
# ```
# Collections with sorted_sequences = AbCdEfGh_sorted_seq_placeholder:
#   aBC123example_digestA_placeholder
#   xYZ789example_digestB_placeholder
#   qRS456example_digestC_placeholder
#
# Total: 3
# ```

# %% [markdown]
# ## Retrieve sequences by sorted_sequences digest
#
# The level 1 `sorted_sequences` value is a digest of the entire sorted array.
# Use `get_attribute` to expand it into the individual sequence digests, then
# retrieve each sequence.

# %%
# Level 1 digest -> array of individual sequence digests
sorted_seq_digest = lvl1_a["sorted_sequences"]
individual_seq_digests = store.get_attribute("sorted_sequences", sorted_seq_digest)
print(f"Individual sequence digests: {individual_seq_digests}")

# Each of those is a refget sequence digest -- use it to retrieve the sequence
for seq_digest in individual_seq_digests:
    record = store.get_sequence(seq_digest)
    if record:
        print(f"  {seq_digest} -> {record.metadata.name} ({record.metadata.length} bp)")

# %% [markdown] output
# ```
# Individual sequence digests: ['SQ.abc123...', 'SQ.def456...']
#   SQ.abc123... -> chr1 (16 bp)
#   SQ.def456... -> chr2 (16 bp)
# ```

# %% [markdown]
# ## Check an incoming FASTA against existing collections
#
# To test whether a new FASTA file duplicates sequences already in the store,
# compute its digest, load it, and query by `sorted_sequences`.

# %%
# A new FASTA arrives -- same sequences, yet another naming scheme
fasta_new = os.path.join(temp_dir, "genome_new.fa")
with open(fasta_new, "w") as f:
    f.write(">scaffold_1\nACGTACGTACGTACGT\n>scaffold_2\nGGGGAAAATTTTCCCC\n")

# Load it into the store
store.add_sequence_collection_from_fasta(fasta_new)
new_digest = digest_fasta(fasta_new).digest

# Get its sorted_sequences digest and search for duplicates
new_lvl1 = store.get_collection_level1(new_digest)
new_sorted = new_lvl1["sorted_sequences"]
duplicates = store.find_collections_by_attribute("sorted_sequences", new_sorted)

# Exclude the new collection itself to see pre-existing matches
existing = [d for d in duplicates if d != new_digest]

print(f"New collection: {new_digest}")
print(f"Existing collections with identical sequences: {len(existing)}")
for d in existing:
    print(f"  {d}")

# %% [markdown] output
# ```
# New collection: mNO012example_digestNew_placeholder
# Existing collections with identical sequences: 3
#   aBC123example_digestA_placeholder
#   xYZ789example_digestB_placeholder
#   qRS456example_digestC_placeholder
# ```

# %% [markdown]
# ## Related guides
#
# - [Coordinate system matching](coordinate-system-digests.py) -- Use
#   `sorted_name_length_pairs` to find collections sharing the same coordinate system
# - [Seqcol Operations](seqcol-operations.py) -- Compare collections and retrieve
#   attribute arrays

# %% [markdown]
# ## Cleanup

# %%
import shutil
shutil.rmtree(temp_dir)
