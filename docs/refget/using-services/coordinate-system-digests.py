# %% [markdown]
# # How to Find Collections Sharing a Coordinate System
#
# Use `name_length_pairs` and `sorted_name_length_pairs` digests to find
# genome collections that share the same coordinate system -- the same
# chromosome names paired with the same lengths. This determines whether
# BED files, BAM files, or other coordinate-based annotations from one
# collection are compatible with another.
#
# **Prerequisites:** You need the `refget` package installed with gtars
# support (`pip install refget[all]`). You should know how to create a
# RefgetStore and load FASTA files (see the [RefgetStore tutorial](refgetstore.py)).

# %% [markdown]
# ## Setup
#
# Create three FASTA files representing the same genome from different
# providers, then load them into an in-memory store.

# %%
import os
import tempfile

from refget.store import RefgetStore, digest_fasta

temp_dir = tempfile.mkdtemp(prefix="coord_system_howto_")

# Provider A: chr1, chr2, chrM
fasta_a = os.path.join(temp_dir, "provider_a.fa")
with open(fasta_a, "w") as f:
    f.write(">chr1\nACGTACGTACGTACGT\n>chr2\nGGGGAAAATTTTCCCC\n>chrM\nATATATAT\n")

# Provider B: same names and sequences, reversed order
fasta_b = os.path.join(temp_dir, "provider_b.fa")
with open(fasta_b, "w") as f:
    f.write(">chrM\nATATATAT\n>chr2\nGGGGAAAATTTTCCCC\n>chr1\nACGTACGTACGTACGT\n")

# Provider C: same sequences, different names (1, 2, MT)
fasta_c = os.path.join(temp_dir, "provider_c.fa")
with open(fasta_c, "w") as f:
    f.write(">1\nACGTACGTACGTACGT\n>2\nGGGGAAAATTTTCCCC\n>MT\nATATATAT\n")

store = RefgetStore.in_memory()
store.set_quiet(True)
store.add_sequence_collection_from_fasta(fasta_a)
store.add_sequence_collection_from_fasta(fasta_b)
store.add_sequence_collection_from_fasta(fasta_c)

digest_a = digest_fasta(fasta_a).digest
digest_b = digest_fasta(fasta_b).digest
digest_c = digest_fasta(fasta_c).digest

print(f"Provider A: {digest_a}")
print(f"Provider B: {digest_b}")
print(f"Provider C: {digest_c}")

# %% [markdown] output
# ```
# Provider A: aBC123...
# Provider B: dEF456...
# Provider C: gHI789...
# ```

# %% [markdown]
# ## Find collections with the same coordinate system (order-independent)
#
# `sorted_name_length_pairs` matches collections that have identical
# chromosome names and lengths, regardless of ordering. Use this to answer:
# "Can I use BED files from collection X with collection Y?"

# %%
lvl1_a = store.get_collection_level1(digest_a)
snlp_digest = lvl1_a["sorted_name_length_pairs"]
print(f"sorted_name_length_pairs digest: {snlp_digest}")

matches = store.find_collections_by_attribute("sorted_name_length_pairs", snlp_digest)
print(f"Collections sharing this coordinate system: {matches}")
print(f"Count: {len(matches)}")

# %% [markdown] output
# ```
# sorted_name_length_pairs digest: weuiIikf4uTSGp0BoHaoP3iNjofokg2c
# Collections sharing this coordinate system: ['aBC123...', 'dEF456...']
# Count: 2
# ```

# %% [markdown]
# Providers A and B match because they have the same chromosome names (chr1,
# chr2, chrM) with the same lengths. Provider C does not match -- it uses
# different names (1, 2, MT), even though the underlying sequences are identical.

# %% [markdown]
# ## Match on exact ordering with `name_length_pairs`
#
# BAM files encode the reference sequence dictionary in their header, and the
# ordering matters. Use `name_length_pairs` when you need collections whose
# chromosomes appear in the exact same order.

# %%
nlp_digest_a = lvl1_a["name_length_pairs"]
print(f"Provider A name_length_pairs: {nlp_digest_a}")

matches = store.find_collections_by_attribute("name_length_pairs", nlp_digest_a)
print(f"Collections with exact same ordering: {matches}")
print(f"Count: {len(matches)}")

# %% [markdown] output
# ```
# Provider A name_length_pairs: s8Bh4bruth2m-OAAJvMvHJtcg0IgFtbq
# Collections with exact same ordering: ['aBC123...']
# Count: 1
# ```

# %% [markdown]
# Only Provider A matches itself. Provider B has the same names and lengths
# but in reversed order, so its `name_length_pairs` digest differs.

# %%
# Confirm: Provider B has a different name_length_pairs digest
lvl1_b = store.get_collection_level1(digest_b)
print(f"A name_length_pairs: {lvl1_a['name_length_pairs']}")
print(f"B name_length_pairs: {lvl1_b['name_length_pairs']}")
print(f"Match: {lvl1_a['name_length_pairs'] == lvl1_b['name_length_pairs']}")

# %% [markdown] output
# ```
# A name_length_pairs: s8Bh4bruth2m-OAAJvMvHJtcg0IgFtbq
# B name_length_pairs: <different>
# Match: False
# ```

# %% [markdown]
# ## Which attribute to use
#
# Use `sorted_name_length_pairs` for coordinate-based formats where order
# does not matter (BED, GFF, VCF). Use `name_length_pairs` when the
# sequence dictionary order must match exactly (BAM/CRAM headers).
#
# For matching by sequence content rather than coordinate system, see
# [Matching by sequences](sorted-sequences.py). For a broader overview of
# collection operations, see [Seqcol Operations](seqcol-operations.py).

# %% [markdown]
# ## Cleanup

# %%
import shutil
shutil.rmtree(temp_dir)
