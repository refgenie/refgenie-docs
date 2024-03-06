# Sequence collections client

The `refget` repository includes a `SeqColClient` object that provides a simple Python API for interacing with a remote refget sequence collections server.

```python
from refget import SeqColClient

scclient = SeqColClient(url="https://seqcolapi.databio.org")
seqcol = scclient.get_collection("MFxJDHkVdTBlPvUFRbYWDZYxmycvHSRp")

scclient = SeqColClient(url="http://45.88.81.158:8081/eva/webservices/seqcol")
seqcol_1 = scclient.get_collection("3mTg0tAA3PS-R1TzelLVWJ2ilUzoWfVq", level=1)
seqcol_2 = scclient.get_collection("3mTg0tAA3PS-R1TzelLVWJ2ilUzoWfVq", level=2)
```

Now that you have the seqeuence digests, you could retrieve the sequences themselves using a refget client.

```python
import refget
rgc = refget.RefGetClient(api_url_base="https://www.ebi.ac.uk/ena/cram/sequence/")
rgc.refget("SQ.UN_b-wij0EtsgFqQ2xNsbXs_GYQQIbeQ")
```




