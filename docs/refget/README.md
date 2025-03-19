
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


### The `refget` Python package includes these capabilities:


| Standard | Local use<br>(computing digests locally)   | Client<br>(connecting to a remote API) | API<br>(implementing an http interface) | Agent<br>(managing a SQL database) |
|:--------:|:---------:|:------:|:----:|:----:|
| Sequences | :material-check: | :material-check: | :material-check: | :material-check: |
| Sequence Collections | :material-check: | :material-check: | :material-check: | :material-check: |
| Pangenomes | X | X | :material-check: | :material-check: |

## Install

The built package is hosted on PyPI.
Install with your flavor of:

```console
pip install refget
```
