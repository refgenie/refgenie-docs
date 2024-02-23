# Refget

## The refget protocol

Refget is a suite of standards for identifying and distributing reference genome sequence data. It consists of 3 standards: 

- **Refget sequences**: a GA4GH-approved standard for individual sequences
- **Refget sequence collections**: a standard for collections of sequences, currently under review by GA4GH 
- **Refget pangenomes**: a future standard for which development is just beginning

<p align="center">
<img src="img/refget-umbrella.svg" width="500">
</p>

## The refget Python package

The `refget` Python package aims to provide a Python interface for both remote and local use of the refget protocol. This package provides several utilities:

1. For refget sequences:
    1. A lightweight Python client for a remote refget sequences server.
    2. Local caching of retrieved results, improving performance for applications that require repeated lookups.
    3. A fully functioning local implementation of the refget sequences protocol for local analysis backed by either memory, SQLite, or MongoDB.
    4. Convenience functions for computing refget sequence digests from Python and handling FASTA files directly.

2. For refget sequence collections:
    1. A lightweight Python client for a remote refget sequence collections server.
    2. A local implementation of the refget sequence collections protocol
    3. Convenience functions for computing refget sequence collection digests from Python.

3. For pangenome sequences: implementation is still a work in progress.

## Install

```console
pip install refget
```

## Basic use

### Retrieve results from a RESTful API

```python
import refget

rgc = refget.RefGetClient("https://refget.herokuapp.com/sequence/")
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=10)

```

### Compute digests locally

```python
refget.trunc512_digest("TCGA")
```

### Insert and retrieve sequences with a local database

```python
checksum = rgc.load_seq("GGAA")
rgc.refget(checksum)
```

For more details, see the [tutorial](tutorial.md).
