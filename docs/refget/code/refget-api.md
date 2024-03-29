<script>
document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('h3 code').forEach((block) => {
    hljs.highlightBlock(block);
  });
});
</script>

<style>
h3 .content { 
    padding-left: 22px;
    text-indent: -15px;
 }
h3 .hljs .content {
    padding-left: 20px;
    margin-left: 0px;
    text-indent: -15px;
    martin-bottom: 0px;
}
h4 .content, table .content, p .content, li .content { margin-left: 30px; }
h4 .content { 
    font-style: italic;
    font-size: 1em;
    margin-bottom: 0px;
}

</style>


# Package `refget` Documentation

## <a name="RefGetClient"></a> Class `RefGetClient`
```python
def __init__(self, api_url_base=None, database={}, schemas=[], schemas_str=[], henges=None, checksum_function=<function md5 at 0x7f27a640c180>, suppress_connect=True)
```

A user interface to insert and retrieve decomposable recursive unique identifiers (DRUIDs).
#### Parameters:

- `database` (`dict`):  Dict-like lookup database with sequences and hashes.
- `schemas` (`dict`):  One or more jsonschema schemas describing thedata types stored by this Henge
- `checksum_function` (`function(str) -> str`):  Default function to handle the digest of theserialized items stored in this henge.




```python
def get_service_info(self)
```



```python
def item_types(self)
```

A list of item types handled by this Henge instance



```python
def load_fasta(self, fa_file, lengths_only=False)
```

Calculates checksums and loads each sequence in a fasta file into the database.



```python
def load_seq(self, seq)
```



```python
def load_sequence_dict(self, seqset)
```

Convert a 'seqset', which is a dict with names as sequence names and values as sequences, into the 'asdlist' required for henge insert.



```python
def meta(self, digest)
```



```python
def refget(self, digest, start=None, end=None)
```



```python
def refget_remote(self, digest, start=None, end=None)
```



```python
def service_info(self)
```






*Version Information: `refget` v0.2.0, generated by `lucidoc` v0.4.4*