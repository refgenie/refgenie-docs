# Refgenie Archives

## Introduction

Refgenie archives are compressed packages of assets that can be transferred, backed up, or served via refgenieserver. When you build an asset locally, it exists as files on disk. Creating an archive packages these files into a distributable `.tgz` file along with metadata about the asset contents and build history.

!!! success "Learning objectives"
    - What are archives and why create them?
    - How to configure the genome archive folder
    - How to list, create, and remove archives
    - Connection to refgenieserver

## What is an archive?

An archive is a compressed tarball (`.tgz`) of an asset, along with metadata stored in the refgenie database. Archives contain:

- **The asset files**: All files from the asset directory, compressed into a single `.tgz` file
- **Directory contents**: A list of files included in the archive
- **Build commands**: The commands used to build the asset (for provenance)
- **Size information**: The archive file size
- **Download count**: Tracking for how many times the archive has been downloaded

Archives are stored in a separate folder from your regular genome assets, configured via the `genome_archive_folder` setting.

## Why create archives?

Archives serve several important purposes:

- **Distribution**: Archives are what refgenieserver serves to clients. When someone runs `refgenie pull`, they're downloading an archive.
- **Backup**: Archives provide a portable backup of built assets that can be stored separately from the working genome folder.
- **Transfer**: Archives can be moved between systems or shared with colleagues.
- **Reproducibility**: Archives include build command history, documenting how the asset was created.

## Configuring the archive folder

Before creating archives, you need to configure the `genome_archive_folder`. This is the directory where archive files will be stored. You can set this during initialization or via environment variables.

### During initialization

```bash
refgenie1 init --genome-archive-folder /path/to/archives
```

### Via environment variable

```bash
export REFGENIE_GENOME_ARCHIVE_FOLDER=/path/to/archives
```

### Verify configuration

Check your current configuration to see the archive folder:

```bash
refgenie1 config get
```

The output will show the `genome_archive_folder` setting:

```
                                                   Refgenie configuration
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ genome_folder                       ┃ version ┃ genome_archive_folder                ┃ servers                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ~/.refgenie/genomes                 │ 1       │ ~/.refgenie/archives                 │ ['http://refgenomes.databio.org'] │
└─────────────────────────────────────┴─────────┴──────────────────────────────────────┴───────────────────────────────────┘
```

!!! warning "Archive folder required"
    You must set the `genome_archive_folder` before creating archives. If not set, the `archive create` command will fail with an error.

## Archive CLI commands

The `refgenie archive` command provides three subcommands for managing archives.

### List archives

View all existing archives:

```bash
refgenie1 archive list
```

This displays a table showing:

- **Digest**: The unique identifier for the archive
- **Asset name**: The registry path of the archived asset (e.g., `genome_digest/asset_group:asset`)
- **Path**: The file path to the archive `.tgz` file
- **Size**: The size of the archive file

Example output:

```
                                     Asset Archives
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Digest                           ┃ Asset name                 ┃ Path           ┃ Size    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ a1b2c3d4e5f6...                  │ abc123.../fasta:default    │ /archives/...  │ 2.1 GB  │
└──────────────────────────────────┴────────────────────────────┴────────────────┴─────────┘
```

### Create an archive

Create an archive from a built asset using the [asset registry path](asset_registry_paths.md) syntax:

```bash
refgenie1 archive create GENOME/ASSET_GROUP:ASSET
```

For example, to archive the default fasta asset for hg38:

```bash
refgenie1 archive create hg38/fasta
```

Or to archive a specific asset tag:

```bash
refgenie1 archive create hg38/fasta:custom_tag
```

You can archive multiple assets at once:

```bash
refgenie1 archive create hg38/fasta mm10/fasta hg38/bowtie2_index
```

!!! tip "Archive during build"
    You can also create an archive automatically when building an asset by using the `--archive` flag with the build command:

    ```bash
    refgenie1 build hg38/fasta --archive
    ```

The archive file is created in a structured path within your archive folder:

```
{genome_archive_folder}/{genome_digest}/{asset_group}/{asset}/{asset_group}__{asset}.tgz
```

### Remove an archive

Remove an archive for a specific asset:

```bash
refgenie1 archive remove GENOME/ASSET_GROUP:ASSET
```

For example:

```bash
refgenie1 archive remove hg38/fasta:default
```

!!! note
    Removing an archive deletes the database record but does not automatically delete the archive file from disk.

## Connection to refgenieserver

Archives are the foundation of how refgenieserver distributes assets. The typical workflow for setting up a refgenie server is:

1. **Build assets locally** with `refgenie build`
2. **Create archives** with `refgenie archive create`
3. **Serve the archive folder** with refgenieserver

When you run refgenieserver, you point it to your archive folder. The server reads the archive metadata from the database and serves the `.tgz` files to clients who run `refgenie pull`.

```bash
# Example: Running refgenieserver with Docker
docker run --rm -d -p 80:80 \
    -v /path/to/archives:/genomes \
    refgenieserverim refgenieserver serve -c /genomes/genome_config.yaml
```

See [Set up your own refgenie server](refgenieserver.md) for detailed instructions on running refgenieserver.

## Archive folder structure

When you create archives, refgenie organizes them in a hierarchical folder structure:

```
genome_archive_folder/
├── {genome_digest_1}/
│   ├── fasta/
│   │   └── default/
│   │       └── fasta__default.tgz
│   └── bowtie2_index/
│       └── default/
│           └── bowtie2_index__default.tgz
└── {genome_digest_2}/
    └── fasta/
        └── default/
            └── fasta__default.tgz
```

This structure mirrors the organization of your genome folder, making it easy to locate specific archives.
