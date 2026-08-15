# The Brickyard Genome Collection

The brickyard genome collection is a curated set of reference genome FASTA files from major public databases, organized into a RefgetStore for content-addressable access. It covers human, mouse, and hundreds of vertebrate genomes from sources including NCBI, Ensembl, UCSC, Gencode, the Broad Institute, and others.

## Collection at a glance

| Metric | Value |
|--------|-------|
| Input FASTA files | 1,147 |
| Sequence collections (genomes) | 810 |
| Individual sequences | 540,973 |
| Store size on disk | 446 GB |
| Input FASTAs (compressed) | 521 GB |

Some input files produce the same sequence collection (identical content from different sources), so the number of unique collections is smaller than the number of input files. A small number of files (38) could not be loaded due to missing files or corrupted gzip archives.

## What the collection contains

The collection is organized into four groups, each reflecting a different curatorial intent:

| Group | Description | Files | Sources |
|-------|-------------|-------|---------|
| `homo_sapiens` | Human reference genomes across builds and providers | 84 | ensembl, ncbi, ucsc, gencode, igenomes, broad, ddbj, ENA |
| `mus_musculus` | Mouse reference genomes | 349 | igenomes, ensembl, ncbi, ucsc, gencode, ENA |
| `mm_hg` | Curated human and mouse genomes from PEP metadata | 94 | Mixed (defined by PEP sample table) |
| `vertebrates` | Broad vertebrate assemblies from NCBI | 605 | NCBI accession-based |

### Human genomes

The human genome group includes assemblies across three major builds:

| Build | Files | Sources |
|-------|-------|---------|
| GRCh38 / hg38 | 57 | ncbi, ensembl, ucsc, gencode, igenomes, broad, ddbj, ENA |
| GRCh37 / hg19 | 20 | ncbi, ensembl, ucsc, gencode, igenomes, broad, ENA |
| hg18 | 3 | ucsc |

The same build appears from multiple providers because each formats the FASTA differently -- chromosome naming conventions, inclusion of alt contigs and patches, sequence ordering. These are distinct sequence collections with distinct digests, even when they represent the same biological assembly. The `sorted_name_length_pairs` digest can be used to identify collections that share the same coordinate system despite naming differences.

### Mouse genomes

The mouse group is dominated by iGenomes pre-built references (324 files), which include processed versions with various index formats. The remaining files span builds mm9 through mm39 from ensembl, ncbi, ucsc, and gencode.

### Vertebrate genomes

The largest group contains 605 assemblies from NCBI, covering a wide range of vertebrate species. These include genomes ranging from small assemblies with a few hundred sequences to large genomes with tens of thousands of contigs. Notable entries include the palmate newt (*Lissotriton helveticus*, GCA_964261635.1), one of the largest vertebrate genomes with a single chromosome containing approximately 2 billion bases.

## How genomes are identified

Every genome in the collection has a unique refget digest computed from its sequence content. In addition, three alias namespaces provide human-readable identifiers for looking up genomes by name rather than by digest. For background on how aliases work in general, see [Names, aliases, and identifiers](names-and-aliases-explained.md).

The three namespaces in the brickyard collection are:

- **`accession`** -- NCBI assembly accessions (GCF_\*/GCA_\*). These are the primary identifiers for most genomes. Every genome that has an NCBI accession is registered here. This is the most reliable namespace for cross-referencing with external databases.
- **`refgenie`** -- Sample names from the PEP project (`donaldcampbelljr/human_mouse_fasta_brickyard`). These are human-assigned descriptive names like `hg38_ensembl` or `mm10_ucsc`. Only the approximately 96 genomes in the PEP are registered here.
- **`common`** -- Short canonical names like `hg38`, `hg19`, `mm39`. These are convenience aliases that map to specific accessions. Only a handful of the most commonly referenced builds have common aliases.

The following table shows how the three namespaces relate for a few well-known builds:

| Common name | Accession | Refgenie name (example) |
|-------------|-----------|------------------------|
| hg38 | GCF_000001405.40 | hg38_ncbi |
| hg19 | GCF_000001405.25 | hg19_ncbi |
| mm39 | GCF_000001635.27 | mm39_ncbi |

Not every genome has aliases in all three namespaces. The `vertebrates` group has accession aliases only. The `mm_hg` group has refgenie aliases and, where applicable, accession and common aliases.

## How the collection is organized in a RefgetStore

When the FASTA files are loaded into a RefgetStore, several things happen:

- Each FASTA file becomes a sequence collection with a unique digest, computed from its sequence content.
- Identical sequences across assemblies are deduplicated. For example, mitochondrial DNA that is shared between builds is stored once and referenced from both collections.
- The alias TSV files in `aliases/collections/` provide the three namespace mappings described above.
- FHR sidecar files can attach species, taxonomy, masking, and version metadata to each collection. See [Understanding FHR metadata](fhr-metadata-explained.md) for details.

The resulting on-disk layout follows the standard [RefgetStore format](reference/refgetstore-format.md):

```
brickyard_store/
  rgstore.json
  sequences.rgsi          # 540,973 unique sequences across all genomes
  collections.rgci        # 810 collections
  sequences/              # Deduplicated sequence files (445 GB)
  collections/            # Per-collection .rgsi files + optional .fhr.json (196 MB)
  aliases/
    collections/
      accession.tsv       # GCF_*/GCA_* -> digest
      refgenie.tsv        # PEP sample names -> digest
      common.tsv          # hg38, mm39, etc. -> digest
```

The store can be hosted as static files on S3, HTTP, or any file server for remote access with local caching.

## Sources and builds

Each source directory represents a genome database provider. The major sources and what they contribute:

- **ncbi** -- RefSeq and GenBank assemblies with GCF/GCA accessions
- **ensembl** -- Ensembl-formatted assemblies (chromosome naming without "chr" prefix)
- **ucsc** -- UCSC-formatted assemblies (chromosome naming with "chr" prefix)
- **gencode** -- GENCODE releases (human and mouse)
- **igenomes** -- Illumina iGenomes pre-built references
- **broad** -- Broad Institute reference bundles

The same underlying assembly (for example, GRCh38) may appear from multiple sources with different formatting conventions -- chromosome naming, sequence ordering, inclusion of alt contigs or patches. These are distinct sequence collections with distinct digests, even when they represent the same biological assembly. The `sorted_name_length_pairs` digest can be used to identify collections that share the same coordinate system despite naming differences.

## The PEP sample table

A subset of the collection (96 genomes in the `mm_hg` group) has structured metadata in a PEP (Portable Encapsulated Project) hosted at `donaldcampbelljr/human_mouse_fasta_brickyard` on PEPhub. The PEP provides a sample table with columns for sample name, species, source, build, and FASTA path. These sample names become the `refgenie` namespace aliases.

The PEP predates the RefgetStore and was the original mechanism for tracking the curated subset. The RefgetStore alias system now supersedes this for discovery and lookup, but the PEP remains as the authoritative source for which genomes were curated and why.

## Learn more

- [Names, aliases, and identifiers](names-and-aliases-explained.md) -- How the alias system works in general
- [What is RefgetStore?](refgetstore-explained.md) -- The storage format underlying the collection
- [Understanding FHR metadata](fhr-metadata-explained.md) -- Attaching species and assembly metadata to collections
- [Working with aliases](using-services/aliases.py) -- Hands-on tutorial for alias operations
- [RefgetStore tutorial](using-services/refgetstore.py) -- Hands-on guide to loading and querying a store
