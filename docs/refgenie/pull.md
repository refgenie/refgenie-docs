# Download pre-built reference genome assets

## Introduction

Use the `refgenie` command-line interface to download and organize genome assets. You do this by simply running `refgenie` from the command line.

The `listr` command *lists remote assets* to see what's available:

```console
refgenie listr
```

The `pull` *downloads* the specific asset of your choice:

```console
refgenie pull GENOME/ASSET
```

Where `GENOME` refers to a genome key (*e.g.* hg38) and `ASSET` refers to one or more specific asset keys (*e.g.* bowtie2_index). For example:

```console
refgenie pull hg38/bowtie2_index
```

You can also pull many assets at once:

```console
refgenie pull --genome mm10 bowtie2_index hisat2_index
```

To see more details, consult the usage docs by running `refgenie pull --help`.

That's it! Easy.

## Downloading manually

You can also browse and download pre-built `refgenie` assemblies manually at [api.refgenie.org](http://api.refgenie.org).
