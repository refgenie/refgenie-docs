
# <img src="img/refget_logo.svg" class="img-header" width="300"> 
<h1 align="center" style="margin-bottom:0px">Python package</h1>

<p align="center">
<a href="https://pypi.org/project/refget/"><img src="https://img.shields.io/pypi/v/refget"></a>
<a href="https://github.com/refgenie/refget"><img src="https://img.shields.io/badge/source-github-354a75?logo=github"></a>
<iframe src="https://ghbtns.com/github-btn.html?user=refgenie&repo=refget&type=star&count=true" frameborder="0" scrolling="0" width="80" height="20" title="GitHub"></iframe>
</p>

## The refget Python package

The `refget` Python package provides a Python implementation of the [GA4GH Refget Specifications](https://ga4gh.github.io/refget/), which define standards for identifying and distributing reference biological sequences, like reference genomes. It provides standards at 3 levels of data: sequences, sequence collections, and pangenomes (in progress).

<p align="center">
<img src="img/refget-umbrella.svg" width="500">
</p>


| Standard | Local use | Client | Agent |
|:--------:|:---------:|:------:|:----:|
| Sequences | :material-check: | :material-check: | :material-check: |
| Sequence Collections | :material-check: | :material-check: | :material-check: |


### The Python package `refget` includes these utilities:


!!! note "Refget Sequences"

    1. A lightweight Python client for a remote refget sequences server.
    2. Local caching of retrieved results, improving performance for applications that require repeated lookups.
    3. A fully functioning local implementation of the refget sequences protocol for local analysis backed by either memory, SQLite, or MongoDB.
    4. Convenience functions for computing refget sequence digests from Python and handling FASTA files directly.

!!! note "Refget Sequence Collections"

    1. A lightweight Python client that can retrieve data from a remote refget sequence collections server (`refget.SequenceCollectionClient`).
    2. A local implementation of the refget sequence collections protocol
    3. Convenience functions for computing refget sequence collection digests from Python.

!!! note "Refget Pangenomes"

    Implementation is still a work in progress.


## Install

The built package is hosted on PyPI.
Install with your flavor of:

```console
pip install refget
```
