# Refget python package tutorial

Record some versions:


```python
from platform import python_version 
python_version()
```




    '3.8.5'




```python
import refget
refget.__version__
```




    '0.1.0'



## Computing digests locally


```python
from refget import trunc512_digest
```

Show some results for sequence digests:


```python
trunc512_digest('ACGT')
```




    '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36'




```python
trunc512_digest('TCGA')
```




    '3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce'




```python
trunc512_digest('ACGT', 26)
```




    '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36cf70'



## Connecting to a remote API

The refget package provides a simple python wrapper around a remote hosted refget RESTful API. Provide the base url when construction a RefGetClient object and you can retrieve sequences from the remote server.


```python
rgc = refget.RefGetClient("https://refget.herokuapp.com/sequence/")
```


```python
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=10)
```




    'CCACACCACA'




```python
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=50)
```




    'CCACACCACACCCACACACCCACACACCACACCACACACCACACCACACC'



You can also hit the `{digest}/metadata` and `service_info` API endpoints described in the refget API specification:


```python
rgc.meta("6681ac2f62509cfc220d78751b8dc524")
```




    {'metadata': {'aliases': [{'alias': 'ga4gh:SQ.lZyxiD_ByprhOUzrR1o1bq0ezO_1gkrn',
        'naming_authority': 'ga4gh'},
       {'alias': 'I', 'naming_authority': 'unknown'}],
      'length': 230218,
      'md5': '6681ac2f62509cfc220d78751b8dc524',
      'trunc512': '959cb1883fc1ca9ae1394ceb475a356ead1ecceff5824ae7'}}




```python
rgc.service_info
```




    {'service': {'algorithms': ['ga4gh', 'md5', 'trunc512'],
      'circular_supported': True,
      'subsequence_limit': None,
      'supported_api_versions': ['1.0.0']}}



When requesting a sequence that is not found, the service responds appropriately:


```python
rgc.refget(trunc512_digest('TCGATCGA'))
```




    'Not Found'



## Use a local database for caching

By default, any full-sequences retrieved from an API are cached locally in memory (in a Python Dict). This data will not persist past a current session, but is useful if you have an application that requires repeated requests. here, we re-request the sequence requested above. It is much faster this time because it uses a local cache:



```python
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=10)
```




    'CCACACCACA'



We can also add new sequences into the database:


```python
rgc.refget(refget.md5('TCGATCGA'))  # This sequence is not found in our database yet
```




    'Not Found'




```python
checksum = rgc.load_seq("TCGATCGA")  # So, let's add it into database
```


```python
rgc.refget(checksum)  # This time it returns
```




    'TCGATCGA'



Keep in mind that sequences added in this way are added to your *local* database, not to the remote API, so when we restart, they will be gone:


```python
del rgc
```


```python
rgc = refget.RefGetClient("https://refget.herokuapp.com/sequence/")
rgc.refget(refget.md5('TCGA'))
```




    'Not Found'



## Making data persist

If you want to retain your local cache, you can use a Dict that is backed by some persistent storage, such as a database on disk or another running process. There are many ways to do this, for example, you can use an sqlite database, a Redis database, or a MongoDB database. Here we'll show you how to use the `sqlitedict` package to back your local database.

To start, you need to create a dict object and pass that to the RefGetClient constructor.


```python
import refget
from sqlitedict import SqliteDict
mydict = SqliteDict('./my_db.sqlite', autocommit=True)
```


```python
rgc = refget.RefGetClient("https://refget.herokuapp.com/sequence/", mydict)
```

Now when we retrieve a sequence it will be added to the local sqlite database automatically.


```python
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=50)
```




    'CCACACCACACCCACACACCCACACACCACACCACACACCACACCACACC'



Look, we can see that this object has been added to our sqlite database:


```python
mydict["6681ac2f62509cfc220d78751b8dc524"][1:50]
```




    'CACACCACACCCACACACCCACACACCACACCACACACCACACCACACC'



So now if we kill this object and start it up again *without the API connection*, but with the mydict local backend, we can still retrieve it:


```python
del rgc
```


```python
rgc = refget.RefGetClient(database=mydict)
```


```python
rgc.refget("6681ac2f62509cfc220d78751b8dc524", start=0, end=50)
```




    'CCACACCACACCCACACACCCACACACCACACCACACACCACACCACACC'



## Loading a fasta file

The package also comes with a helper function for computing checksums for an entire fasta file.


```python
fa_file = "../demo_fasta/demo.fa"
content = rgc.load_fasta(fa_file)
```


```python
content
```




    [{'name': 'chr1',
      'length': 4,
      'sequence_digest': 'f1f8f4bf413b16ad135722aa4591043e'},
     {'name': 'chr2',
      'length': 4,
      'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'}]




```python
rgc.refget(content[0]['sequence_digest'])
```




    'ACGT'




```python
rgc.refget("blah")
```

    No remote URL connected



```python
rgc.api_url_base = "https://refget.herokuapp.com/sequence/"
```


```python
rgc.refget("blah")
```




    'Not Found'




```python
# You can show the complete contents of the database like this:
# rgc.show()

```
