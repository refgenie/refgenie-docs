
# <img src="img/refgenie_logo.svg" class="img-header"> 
<h1 align="center">reference genome manager</h1></p>

<p align="center">

<a href="https://pepkit.github.io/img/PEP-compatible-green.svg"><img src="https://pepkit.github.io/img/PEP-compatible-green.svg"></a>
</p>


## What is refgenie?

Refgenie manages storage, access, and transfer of reference genome resources. It provides command-line and Python interfaces to *download* pre-built reference genome "assets", like indexes used by bioinformatics tools. It can also *build* assets for custom genome assemblies. Refgenie provides programmatic access to a standard genome folder structure, so software can swap from one genome to another.

## What makes refgenie better?

1. **It provides a command-line interface to download individual resources**. Think of it as `GitHub` for reference genomes. You just type `refgenie pull hg38/bwa_index`.

2. **It's scripted**. In case you need resources *not* on the server, such as for a custom genome, you can `build` your own: `refgenie build custom_genome/bowtie2_index`.

3. **It simplifies finding local asset locations**. When you need a path to an asset, you can `seek` it, making your pipelines portable across computing environments: `refgenie seek hg38/salmon_index`.

4. **It provides remote operation mode**, useful for cloud applications. Get a path to an asset file hosted on AWS S3: `refgenie seekr hg38/fasta --remote-class s3`.

5. **It includes a Python API**. For tool developers, you use `rgc = refgenconf.RefGenConf("genomes.yaml")` to get a Python object with paths to any genome asset, *e.g.*, `rgc.seek("hg38", "kallisto_index")`.

6. **It strictly determines genomes compatibility**. Users refer to genomes with arbitrary aliases, like "hg38", but refgenie uses sequence-derived identifiers to verify genome identity with asset servers.

7. **It is scalable for large-scale operations**. Refgenie is backed by a database, enabling efficient, multi-user, management of genome assets. By default, it uses a local SQLite database, but it can be configured to use PostgreSQL, including setups on remote servers, to support high-performance and distributed workflows.

## Quick example

### Install

> Not released yet! Check the [README](https://github.com/refgenie/refgenie1?tab=readme-ov-file#installation) for the temporary installation instructions.

Refgenie is a Python package, install from [PyPi](https://pypi.org/project/refgenie/):

```console
pip install --user refgenie
```

Or [conda](https://anaconda.org/bioconda/refgenie):

```console
conda install refgenie
```

And that's it! If you wish to use refgenie in *remote mode*, see [further reading on remote mode in refgenie](remote.md).

If you're connected to the Internet, call a test command, e.g.:

```console
refgenie seekr hg38/fasta
```

### Initialize to use refgenie locally

By default, Refgenie keeps track of what's available using local configuration initialized by `refgenie init`:

```console
refgenie init
```

See [further reading on configuring refgenie](configuration.md).

### Download indexes and assets for a remote reference genome

Use `refgenie pull` to download pre-built assets from a remote server. View available remote assets with `listr`:

```console
refgenie listr
```

Response:
```console
                 Refgenie assets. Source: http://refgenomes.databio.org
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Genome digest                                    ┃ Asset group             ┃ Asset   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 047c6e1eda552b50c5add59ff0995a40bc4ce1732e3cc4ae │ bowtie2_index           │ default │
│ 047c6e1eda552b50c5add59ff0995a40bc4ce1732e3cc4ae │ bowtie2_index           │ default │
│ 047c6e1eda552b50c5add59ff0995a40bc4ce1732e3cc4ae │ bwa_index               │ default │
│ 047c6e1eda552b50c5add59ff0995a40bc4ce1732e3cc4ae │ bwa_index               │ default │
│ 047c6e1eda552b50c5add59ff0995a40bc4ce1732e3cc4ae │ fasta                   │ default │
....
```

Next, pull one:

```console
refgenie pull rCRSd/bowtie2_index
```

Response:
```console
refgenie1 pull hg38/fasta
WARNING  No local digest for genome alias: hg38. Setting genome identity with server: http://refgenomes.databio.org                                   refgenie.py:2980
INFO     HTTP Request: GET http://refgenomes.databio.org/openapi.json "HTTP/1.1 200 OK"                                                                _client.py:1027
INFO     Connected to server: title='refgenieserver' version='0.7.0' description='a web interface and RESTful API for reference genome assets'            client.py:32
INFO     Setting 'hg38' identity with server: http://refgenomes.databio.org                                                                           refgenie.py:1022
INFO     HTTP Request: GET http://refgenomes.databio.org/v3/genomes/genome_digest/hg38 "HTTP/1.1 200 OK"                                               _client.py:1027
INFO     HTTP Request: GET http://refgenomes.databio.org/v3/genomes/attrs/2230c535660fb4774114bfa966a62f823fdb6d21acf138d4 "HTTP/1.1 200 OK"           _client.py:1027
INFO     Determined digest for hg38: 2230c535660fb4774114bfa966a62f823fdb6d21acf138d4                                                                 refgenie.py:1096
INFO     Set genome alias: hg38                                                                                                                       refgenie.py:2990
INFO     HTTP Request: GET http://refgenomes.databio.org/v3/assets/default_tag/2230c535660fb4774114bfa966a62f823fdb6d21acf138d4/fasta "HTTP/1.1 200    _client.py:1027
         OK"
INFO     HTTP Request: GET http://refgenomes.databio.org/v3/assets/attrs/2230c535660fb4774114bfa966a62f823fdb6d21acf138d4/fasta?tag=default "HTTP/1.1  _client.py:1027
         200 OK"
INFO     HTTP Request: GET http://refgenomes.databio.org/v3/assets/archive/2230c535660fb4774114bfa966a62f823fdb6d21acf138d4/fasta?tag=default          _client.py:1027
         "HTTP/1.1 307 Temporary Redirect"
INFO     HTTP Request: GET                                                                                                                             _client.py:1027
         http://awspds.refgenie.databio.org/refgenomes.databio.org/2230c535660fb4774114bfa966a62f823fdb6d21acf138d4/fasta__default.tgz "HTTP/1.1 200
         OK"
hg38/fasta:default ━━━━━━━━━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 15.7% • 131.1/833.4 MB • 8.0 MB/s
...
```

See [further reading on downloading assets](pull.md).

### Build your own indexes and assets for a custom reference genome

Refgenie assets are scripted, so if what you need is not available remotely, you can use `build` it locally:


```console
refgenie build mygenome/bwa_index
```

See [further reading on building assets](build.md).

### Retrieve paths to *local* refgenie-managed assets

Once you've populated your refgenie with a few assets, use `seek` to retrieve their local file paths:

```console
refgenie seek mm10/bowtie2_index
```

This will return the path to the particular asset of interest, regardless of your computing environment. This gives you an ultra-portable asset manager! See [further reading on retrieving asset paths](seek.md).

### Retrieve paths to *remote* refgenie-managed assets

Use `seekr` (short for "seek remote") to retrieve remote `seek_key` targets:

```console
refgenie seekr mm10/fasta.fai
```

This will return the path to the particular remote file of interest, here: FASTA index file, which is a part of `mm10/fasta` asset.

See [further reading on using refgenie in remote mode](remote.md).

---
If you want to read more about the motivation behind refgenie and the software engineering that makes refgenie work, proceed next to the [overview](overview.md).
