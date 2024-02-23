
# <img src="../img/refget_logo.svg" class="img-header"> 
<h1 align="center" style="margin-bottom:0px">Python package</h1>

<p align="center">
<a href="https://img.shields.io/pypi/v/refget"><img src="https://img.shields.io/pypi/v/refget"></a>
<a href="https://github.com/refgenie/refget"><img src="https://img.shields.io/badge/source-github-354a75?logo=github"></a>
<iframe src="https://ghbtns.com/github-btn.html?user=refgenie&repo=refget&type=star&count=true" frameborder="0" scrolling="0" width="80" height="20" title="GitHub"></iframe>
</p>

## The refget Python package

The `refget` Python package aims to provide a Python interface for both remote and local use of the refget protocol.

### The refget protocol

Refget will consist of 3 standards for identifying and distributing reference genome data:

- **Refget sequences**: a GA4GH-approved standard for individual sequences
- **Refget sequence collections**: a standard for collections of sequences, under review 
- **Refget pangenomes**: a future standard for which development is just beginning

<p align="center">
<img src="img/refget-umbrella.svg" width="500">
</p>

### Refget Python package utilities:

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
