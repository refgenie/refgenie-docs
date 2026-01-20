# Refget CLI Reference

The `refget` command-line interface provides tools for working with reference sequences following GA4GH standards. It includes commands for computing sequence collection digests, managing local sequence stores, and interacting with remote seqcol APIs.

## Installation

```bash
pip install refget
```

## Quick Start

```bash
# Compute seqcol digest from a FASTA file
refget fasta digest genome.fa

# Create all index files from a FASTA
refget fasta index genome.fa

# Initialize a local sequence store
refget store init

# Add a FASTA to the store
refget store add genome.fa

# Compare two sequence collections
refget seqcol compare genome1.fa genome2.fa
```

## Command Groups

The CLI is organized into five command groups:

| Group | Description |
|-------|-------------|
| `refget config` | Configuration management |
| `refget fasta` | FASTA file utilities |
| `refget store` | RefgetStore operations |
| `refget seqcol` | Sequence collection API |
| `refget admin` | Admin/database operations |

---

## Global Options

```
--version, -v    Show version and exit
--help           Show help message and exit
```

---

## Config Commands

Manage refget configuration stored in `~/.refget/config.toml`.

### config init

Interactive setup wizard for refget configuration.

```bash
refget config init [--force]
```

**Options:**

- `--force, -f`: Overwrite existing configuration

### config show

View all configuration or a specific section.

```bash
refget config show [SECTION]
```

**Arguments:**

- `SECTION`: Optional section to show (store, seqcol_servers, remote_stores, admin)

### config get

Get a specific configuration value.

```bash
refget config get KEY
```

**Examples:**
```bash
refget config get store.path
refget config get admin.postgres_host
```

### config set

Set a configuration value.

```bash
refget config set KEY VALUE
```

**Examples:**
```bash
refget config set store.path /path/to/store
refget config set admin.postgres_host localhost
```

### config path

Show the path to the configuration file.

```bash
refget config path
```

### config validate

Validate the configuration file.

```bash
refget config validate
```

---

## FASTA Commands

Utilities for processing FASTA files and computing seqcol data.

### fasta digest

Compute the seqcol digest (top-level) of a FASTA file.

```bash
refget fasta digest FILE
```

**Output:** JSON with digest and file path
```json
{"digest": "abc123...", "file": "genome.fa"}
```

### fasta seqcol

Compute the full seqcol JSON from a FASTA file.

```bash
refget fasta seqcol FILE [-o OUTPUT] [-l LEVEL]
```

**Options:**

- `--output, -o`: Output file path (default: stdout)
- `--level, -l`: Seqcol level: 1 (digests only) or 2 (full arrays). Default: 2

**Example:**
```bash
refget fasta seqcol genome.fa -o genome.seqcol.json
```

### fasta index

Generate ALL derived files from a FASTA file.

```bash
refget fasta index FILE [-o OUTPUT_DIR] [--json]
```

For `genome.fa`, creates:

- `genome.fa.fai` - FASTA index (samtools-compatible)
- `genome.seqcol.json` - Sequence collection JSON
- `genome.chrom.sizes` - Chromosome sizes

**Options:**

- `--output-dir, -o`: Output directory (default: same as input file)
- `--json, -j`: Output result as JSON

### fasta fai

Compute FAI index from a FASTA file.

```bash
refget fasta fai FILE [-o OUTPUT]
```

Outputs samtools-compatible .fai format (tab-separated).

### fasta chrom-sizes

Compute chrom.sizes from a FASTA file.

```bash
refget fasta chrom-sizes FILE [-o OUTPUT]
```

Outputs UCSC-compatible chrom.sizes format (tab-separated name/length).

### fasta stats

Display statistics for a FASTA file.

```bash
refget fasta stats FILE [--json]
```

Shows: sequence count, total length, N50, min/max/mean sequence length.

**Options:**

- `--json, -j`: Output as JSON instead of table

### fasta validate

Validate a FASTA file format.

```bash
refget fasta validate FILE
```

Returns exit code 0 if valid, non-zero if invalid.

---

## Store Commands

Manage a local RefgetStore for storing and retrieving sequences.

### store init

Initialize a local RefgetStore.

```bash
refget store init [--path PATH]
```

**Options:**

- `--path, -p`: Path for the store (default: from config or `~/.refget/store`)

### store add

Import a FASTA file to the local store.

```bash
refget store add FASTA [--path PATH]
```

**Output:** JSON with digest and sequence count
```json
{"digest": "abc123...", "fasta": "/path/to/file.fa", "sequences": 25}
```

### store list

List collections in the store.

```bash
refget store list [--path PATH]
```

**Output:**
```json
{"collections": [{"digest": "abc123..."}, {"digest": "def456..."}]}
```

### store get

Get a collection by digest.

```bash
refget store get DIGEST [--path PATH]
```

**Output:** Full seqcol with names, lengths, and sequences arrays.

### store export

Export a collection as a FASTA file.

```bash
refget store export DIGEST [-o OUTPUT] [--bed BED] [--name NAME] [--path PATH]
```

**Options:**

- `--output, -o`: Output FASTA file path (default: stdout)
- `--bed, -b`: BED file for region extraction
- `--name, -n`: Sequence names to include (can be repeated)
- `--line-width, -w`: FASTA line width (default: 80)

**Examples:**
```bash
# Export full collection
refget store export abc123 -o genome.fa

# Export specific chromosomes
refget store export abc123 -o subset.fa --name chr1 --name chr2

# Export regions from BED file
refget store export abc123 -o regions.fa --bed regions.bed
```

### store seq

Get a sequence or subsequence.

```bash
refget store seq DIGEST [--name NAME] [--start N] [--end M] [--path PATH]
```

**Examples:**
```bash
# Full sequence by digest
refget store seq <seq_digest>

# Subsequence
refget store seq <seq_digest> --start 100 --end 200

# By collection and name
refget store seq <coll_digest> --name chr1

# Subsequence by name
refget store seq <coll_digest> --name chr1 --start 100 --end 200
```

### store fai

Generate .fai index from a collection digest.

```bash
refget store fai DIGEST [-o OUTPUT] [--path PATH]
```

### store chrom-sizes

Generate chrom.sizes from a collection digest.

```bash
refget store chrom-sizes DIGEST [-o OUTPUT] [--path PATH]
```

### store stats

Display store statistics.

```bash
refget store stats [--path PATH]
```

**Output:**
```json
{"collections": 3, "sequences": 75, "storage_mode": "Encoded"}
```

### store remove

Remove a collection from the store.

```bash
refget store remove DIGEST [--path PATH]
```

---

## Seqcol Commands

Work with sequence collections and the seqcol API.

### seqcol compare

Compare two sequence collections.

```bash
refget seqcol compare A B [--server URL] [--quiet]
```

Accepts flexible inputs:

- `<digest>` - Fetches from local store or server
- `<file.fa>` - Computes seqcol on the fly
- `<file.seqcol.json>` - Uses local seqcol file

**Options:**

- `--server, -s`: Server URL override
- `--quiet, -q`: Suppress output; use exit code only (0=compatible, 1=incompatible)

**Example:**
```bash
refget seqcol compare genome1.fa genome2.fa
refget seqcol compare abc123 def456 --server https://seqcolapi.databio.org
```

### seqcol digest

Compute the seqcol digest of a file.

```bash
refget seqcol digest FILE
```

Accepts either a FASTA file or a `.seqcol.json` file.

### seqcol validate

Validate a seqcol JSON file.

```bash
refget seqcol validate FILE
```

Checks that the file is valid JSON and conforms to the seqcol schema.

### seqcol attributes

List attributes in a seqcol JSON file.

```bash
refget seqcol attributes FILE
```

Shows the attribute names and their array lengths.

### seqcol schema

Show the seqcol schema definition.

```bash
refget seqcol schema
```

### seqcol servers

List known seqcol servers from configuration.

```bash
refget seqcol servers
```

### seqcol lookup

Look up a sequence collection by digest from a remote server.

```bash
refget seqcol lookup DIGEST [--level LEVEL] [--server URL]
```

**Options:**

- `--level, -l`: Seqcol level: 1 (digests only) or 2 (full arrays). Default: 2
- `--server, -s`: Server URL override

---

## Admin Commands

Database administration and bulk loading operations.

### admin status

Show admin/database connection status.

```bash
refget admin status
```

Tests the database connection and displays connection info and table statistics.

### admin info

Show system info (version, dependencies, etc.).

```bash
refget admin info [--json]
```

### admin load

Load seqcol metadata from FASTA or JSON into PostgreSQL.

```bash
refget admin load [INPUT_FILE] [--pep PEP] [--pephub PROJECT] [--fa-root PATH] [--name NAME]
```

Can load from:

- Single FASTA file
- Single `.seqcol.json` file
- Batch from PEP project file (`--pep`)
- Batch from PEPhub project (`--pephub`)

**Options:**

- `--pep`: PEP project file for batch loading
- `--pephub`: PEPhub project (e.g., `nsheff/human_fasta_ref`)
- `--fa-root`: Root directory for FASTA files (used with `--pep`/`--pephub`)
- `--name, -n`: Human-readable name for the FASTA

**Examples:**
```bash
refget admin load genome.fa
refget admin load genome.fa --name "Human GRCh38"
refget admin load genome.seqcol.json
refget admin load --pep genomes.yaml --fa-root /data/fasta
refget admin load --pephub nsheff/human_fasta_ref --fa-root /data/fasta
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `REFGET_CONFIG` | Path to configuration file |
| `REFGET_STORE` | Path to local RefgetStore |
| `REFGET_STORE_PATH` | Alternative for store path |
| `REFGET_DATABASE_URL` | PostgreSQL connection URL |
| `POSTGRES_HOST` | Database host |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General failure |
| 2 | File not found |
| 3 | Network error |
| 4 | Configuration error |

---

## Configuration File

The configuration file is located at `~/.refget/config.toml`:

```toml
[store]
path = "~/.refget/store"

[seqcol_servers]
default = "https://seqcolapi.databio.org"

[admin]
postgres_host = "localhost"
postgres_db = "refget"
postgres_user = "postgres"
```
