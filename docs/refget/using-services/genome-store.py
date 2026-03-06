# %% [markdown]
# # Exploring the Brickyard Genome Store
#
# This tutorial shows how to connect to the brickyard genome store and browse
# its curated collection of ~1,952 reference genomes. You'll look up genomes by
# accession, compare assemblies from different sources, and export FASTA files.
#
# For background on what the brickyard genome collection is, see
# [The Brickyard Genome Collection](../../genome-collections-explained/).
# This tutorial assumes you can already [install the refget package](../../#install)
# and know the basics of [RefgetStore](refgetstore.py) and [aliases](aliases.py).
#
# <div class="admonition success">
#   <p class="admonition-title">Learning objectives</p>
#   <ul>
#     <li>Open the brickyard genome store (local path or remote URL)</li>
#     <li>List available genomes and alias namespaces</li>
#     <li>Look up a genome by NCBI accession</li>
#     <li>Compare two versions of the same genome from different sources</li>
#     <li>Export a FASTA from the store</li>
#   </ul>
# </div>

# %% [markdown]
# ## 1. Opening the store
#
# The brickyard genome store can be opened either from a remote URL or a local
# path. Here we connect to the remote store and use a temporary local cache.

# %%
import os
import tempfile
from refget.store import RefgetStore

# %%
# Remote URL for the brickyard genome store
# (Update this URL when the brickyard store is published to S3)
BRICKYARD_URL = "https://refgenie.s3.us-east-1.amazonaws.com/brickyard_genome_store"

# Open the remote store with a local cache directory
temp_dir = tempfile.mkdtemp(prefix="genome_store_tutorial_")
cache_path = os.path.join(temp_dir, "cache")

store = RefgetStore.open_remote(
    cache_path=cache_path,
    remote_url=BRICKYARD_URL
)

# Show store statistics
print(store.stats())

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# {'n_collections_loaded': '0', 'storage_mode': 'Encoded', 'n_sequences_loaded': '0', 'total_disk_size': '...', 'n_sequences': '...', 'n_collections': '1952'}
# ```

# %% [markdown]
# If you have a local copy of the store, you can open it directly:
#
# ```python
# # If you have a local copy:
# # store = RefgetStore.on_disk("/path/to/brickyard_genome_store")
# ```

# %% [markdown]
# ## 2. Browsing available genomes
#
# The store organizes genomes using alias namespaces. Let's see what's available.

# %%
# List alias namespaces
namespaces = store.list_collection_alias_namespaces()
print(f"Collection alias namespaces: {namespaces}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Collection alias namespaces: ['accession', 'common', 'refgenie']
# ```

# %%
# List accession aliases (first 10)
accession_aliases = store.list_collection_aliases("accession")
print(f"Total accession aliases: {len(accession_aliases)}")
print(f"\nFirst 10 accessions:")
for alias in accession_aliases[:10]:
    print(f"  {alias}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Total accession aliases: 1952
#
# First 10 accessions:
#   GCA_000001215.4
#   GCA_000001405.15
#   GCA_000001405.28
#   GCA_000001405.29
#   GCA_000001635.8
#   GCA_000001635.9
#   GCA_000002985.3
#   GCA_000005005.6
#   GCA_000005425.2
#   GCA_000005575.1
# ```

# %%
# List common name aliases (should be a short list)
common_aliases = store.list_collection_aliases("common")
print(f"Common name aliases:")
for alias in common_aliases:
    print(f"  {alias}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Common name aliases:
#   hg38
#   hg19
#   mm39
#   mm10
# ```

# %% [markdown]
# ## 3. Looking up a genome by accession
#
# The most common way to find a genome is by its NCBI accession. Let's look up
# the GRCh38.p14 human reference genome.

# %%
# Look up hg38 by its NCBI RefSeq accession
hg38 = store.get_collection_by_alias("accession", "GCF_000001405.40")
if hg38:
    print(f"Digest: {hg38.digest}")
    print(f"Sequences: {hg38.n_sequences}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Digest: <sha512t24u digest>
# Sequences: <number of sequences>
# ```

# %%
# Reverse lookup: find all aliases that point to this collection
if hg38:
    aliases = store.get_aliases_for_collection(hg38.digest)
    print(f"All aliases for this collection:")
    for namespace, alias in aliases:
        print(f"  {namespace}/{alias}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# All aliases for this collection:
#   accession/GCF_000001405.40
#   common/hg38
#   refgenie/hg38
# ```

# %% [markdown]
# ## 4. Comparing two genome versions
#
# RefgetStore can compare two collections to show what they share and where
# they differ. This is useful for understanding the relationship between
# assemblies from different sources or different versions of the same genome.

# %%
# Look up two different assemblies to compare
hg38_ncbi = store.get_collection_by_alias("accession", "GCF_000001405.40")
hg19_ncbi = store.get_collection_by_alias("accession", "GCF_000001405.25")

if hg38_ncbi and hg19_ncbi:
    print(f"hg38 digest: {hg38_ncbi.digest}")
    print(f"hg19 digest: {hg19_ncbi.digest}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# hg38 digest: <sha512t24u digest>
# hg19 digest: <sha512t24u digest>
# ```

# %%
# Compare the two assemblies
if hg38_ncbi and hg19_ncbi:
    comparison = store.compare(hg38_ncbi.digest, hg19_ncbi.digest)
    print(f"Shared attributes: {comparison['attributes']['a_and_b']}")
    print(f"A-only attributes: {comparison['attributes']['a_only']}")
    print(f"B-only attributes: {comparison['attributes']['b_only']}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Shared attributes: ['lengths', 'name_length_pairs', 'names', 'sequences', 'sorted_name_length_pairs', 'sorted_sequences']
# A-only attributes: []
# B-only attributes: []
# ```

# %% [markdown]
# The comparison shows which seqcol attributes are shared between the two
# assemblies and which are unique to each. Since hg38 and hg19 are different
# genome builds, they will typically differ in their sequence content while
# sharing the same set of attribute types.

# %% [markdown]
# ## 5. Exporting a FASTA
#
# You can export any collection from the store as a FASTA file. This downloads
# the sequences (if remote) and writes them to disk.

# %%
# Export the hg38 collection to a FASTA file
if hg38:
    output_path = os.path.join(temp_dir, "hg38_export.fa")
    store.export_fasta(hg38.digest, output_path, None, None)
    print(f"Exported to: {output_path}")

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# Exported to: /tmp/genome_store_tutorial_.../hg38_export.fa
# ```

# %%
# Verify the export
if hg38:
    file_size = os.path.getsize(output_path)
    print(f"File size: {file_size:,} bytes")
    print(f"\nFirst 5 lines:")
    with open(output_path) as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(line.rstrip())

# %% [markdown] output
# ```
# TODO: capture output after store is built
# Expected format:
# File size: <size> bytes
#
# First 5 lines:
# >chr1
# NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
# NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
# NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
# NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
# ```

# %% [markdown]
# <div class="admonition success">
#   <p class="admonition-title">Summary</p>
#   <ul>
#     <li>The brickyard genome store provides <strong>~1,952 curated reference genomes</strong> accessible by accession, common name, or digest.</li>
#     <li>Use <strong><code>open_remote()</code></strong> to connect to the store with automatic local caching, or <strong><code>on_disk()</code></strong> for a local copy.</li>
#     <li><strong>Alias namespaces</strong> (accession, common, refgenie) let you look up genomes using familiar identifiers.</li>
#     <li><strong>Collection comparison</strong> reveals what two assemblies share, helping you understand the relationship between genome versions.</li>
#     <li><strong>FASTA export</strong> lets you extract any genome from the store for downstream analysis.</li>
#   </ul>
# </div>

# %% [markdown]
# ## What's next?
#
# - [RefgetStore tutorial](refgetstore.py) -- General store operations: creating stores, retrieving sequences, extracting regions
# - [Working with Aliases](aliases.py) -- Managing your own aliases: adding, resolving, bulk loading, and removing aliases
# - [FHR Metadata Headers](fhr-metadata.py) -- Attaching assembly metadata (species, version, masking) to collections

# %%
# Cleanup
import shutil
shutil.rmtree(temp_dir)
