# What's new in refgenie 1.0

Refgenie 1.0 is a ground-up rewrite that replaces the three legacy packages (refgenie, refgenconf, refgenieserver) with a single unified package. It is a fresh install, not an upgrade from the legacy version.

## Unified package

The legacy ecosystem split functionality across three separate packages:

| Legacy package | Role |
|---|---|
| refgenie | CLI and asset management |
| refgenconf | Configuration library |
| refgenieserver | API server |

Refgenie 1.0 consolidates all of this into one installable package. Server functionality is available with `pip install refgenie[server]`.

## Database-backed configuration

The legacy YAML-based genome configuration file (`genome_config.yaml`) is replaced by a database. By default, refgenie uses a local SQLite database that requires zero configuration. For multi-user or server deployments, PostgreSQL is supported. See [Database backends](database.md) for setup details.

## RefgetStore for sequence data

When you initialize a genome with `refgenie genome init --fasta genome.fa`, refgenie loads all sequences into a local **RefgetStore** -- a content-addressable store where every sequence is identified by its GA4GH digest. This means:

- Identical sequences across genomes are stored only once
- You can retrieve subsequences directly with `refgenie getseq` without needing FASTA files on disk
- Chromosome sizes are derived from sequence collection metadata, not samtools

See [Genome initialization](genome_tutorial.md) for the full workflow.

## Serving modes

Asset classes now declare how they should be delivered to consumers via `serving_modes`:

| Mode | Description |
|---|---|
| `file` | Serve individual files at their own URLs (default) |
| `archive` | Serve a compressed `.tgz` tarball for bulk download |
| `none` | Metadata only -- no data hosting |

This replaces the legacy archive-only distribution model. See [Serving modes](serving_modes.md) for details.

## Data channels

Data channels are external sources that provide asset class and recipe definitions. They allow tool developers and the community to publish new asset types without modifying the core refgenie codebase. Channels are simple collections of YAML files hosted on GitHub Pages or any web server.

See [Use data channels](data_channels.md) and [Set up your own data channel](set_up_data_channel.md).

## Staging and remote storage

Assets are now **staged** before serving or pushing to cloud storage. Staging prepares assets according to their serving modes -- either as symlinks (file mode, no disk cost) or as `.tgz` tarballs (archive mode). Staged assets can then be pushed to remote storage like S3.

See [Stage assets for serving](staging.md) and [Configure remote storage](remotes.md).

## Built-in server

The `refgenie serve` command starts an API server directly -- no separate refgenieserver package needed. The server exposes REST API endpoints, GA4GH DRS endpoints, and data channel aggregation.

See [Run a server](server/README.md) for setup instructions.

## Alias system

Genomes are identified by sequence-derived digests, but you refer to them using human-readable aliases like `hg38`. The alias system supports both local (RefgetStore-based) and server-side (SQL) backends, so aliases resolve consistently across environments.

See [Manage aliases](alias.md).

## Migration from legacy

Refgenie 1.0 is a fresh install. There is no automated migration path from legacy refgenie. If you have existing assets managed by legacy refgenie, you will need to rebuild or re-pull them under the new system.
