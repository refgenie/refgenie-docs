# Using the RefGetClient to interact with a Sequence Collections API

## Introduction

The `refget` Python package contains an object called `RefGetClient` that provides a simple Python API for interacing with a remote refget server.
It is capable of interacting either with a Refget Sequences API, or a Refget Sequence Collections API.
Here, we will demonstrate how to use it to interact with a Sequence Collections API.

## Tutorial

Instantiate a `RefGetClient` object by giving it the base URL to the API.

```python
from refget import RefGetClient

rgc = RefGetClient()  # This will use default API URLs
rgc = RefGetClient(seqcol_api_urls=["https://seqcolapi.databio.org"], seq_api_urls=None)  # Use the demo seqcolapi instance
```

Now, you can interact with this object to run any of the API functions Check what's available

```python
rgc.list_collections(page_size=5)
```

Retrieve a collection:
```python
seqcol = rgc.get_collection("fLf5M0BOIPIqcfbE6R8oYwxsy-PnoV32")
seqcol
# {'lengths': [8, 4, 4],
#  'names': ['chrX', 'chr1', 'chr2'],
#  'sequences': ['SQ.iYtREV555dUFKg2_agSJW6suquUyPpMw',
#   'SQ.YBbVX0dLKG1ieEDCiMmkrTZFt_Z5Vdaj',
#   'SQ.AcLxtBuKEPk_7PGE_H4dGElwZHCujwH6'],
#  'sorted_name_length_pairs': ['IWFt7HQ4XoMk34U27BKO-4szSRifP6H5',
#   'chDD8A4S8YZKNNctCimHasAA2Dn596SZ',
#   'enZNOGccwFbN9yJ3YZVifFTFCVA9hIpH']}
```

Get a list of collections that have a certain digest for an attribute:

```
l = rgc.list_collections(page=1, page_size=2, attribute="lengths", attribute_digest="cGRMZIb3AVgkcAfNv39RN7hnT5Chk7RX")
```

List all available values of a specific attribute:
```
a = rgc.list_attributes("lengths", page_size=3)
```

Compare two sequence collections:

```
rgc.compare("fLf5M0BOIPIqcfbE6R8oYwxsy-PnoV32", "MFxJDHkVdTBlPvUFRbYWDZYxmycvHSRp")
```

Here are some other examples using a different server API:

```
scclient = RefGetClient(seqcol_api_urls=["http://45.88.81.158:8081/eva/webservices/seqcol"])
seqcol_1 = scclient.get_collection("3mTg0tAA3PS-R1TzelLVWJ2ilUzoWfVq", level=1)
seqcol_2 = scclient.get_collection("3mTg0tAA3PS-R1TzelLVWJ2ilUzoWfVq", level=2)
```

Now that you have the seqeuence digests, if you gave the client a sequences API URL, you could also retrieve the actual sequences like this (optional):

```python
rgc = refget.RefGetClient(seq_api_urls=["https://www.ebi.ac.uk/ena/cram/sequence/"])
rgc.get_sequence(seqcol['sequences'][0])
```

## Debugging

If you want, you can upgrade the logging level for debug code

```python
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel("DEBUG")
```