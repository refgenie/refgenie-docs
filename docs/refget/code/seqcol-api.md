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

## <a name="SeqColClient"></a> Class `SeqColClient`
A client for interacting with a sequence collection API.

Args:
    url (str, optional): The base URL of the sequence collection API. Defaults to "http://seqcolapi.databio.org".
Attributes:
    url (str): The base URL of the sequence collection API.
Methods:
    get_collection(accession, level=2): Retrieves a sequence collection for a given accession and level.


```python
def __init__(self, url='http://seqcolapi.databio.org')
```

Initialize self.  See help(type(self)) for accurate signature.



```python
def compare(self, accession1, accession2)
```

Compares two sequence collections.

Args:
    accession1 (str): The accession of the first sequence collection.
    accession2 (str): The accession of the second sequence collection.
Returns:
    dict: The JSON response containing the comparison of the two sequence collections.



```python
def get_collection(self, accession, level=2)
```

Retrieves a sequence collection for a given accession and detail level.

Args:
    accession (str): The accession of the sequence collection.
    level (int, optional): The level of detail for the sequence collection. Defaults to 2.
Returns:
    dict: The JSON response containing the sequence collection.






*Version Information: `refget` v0.2.0, generated by `lucidoc` v0.4.4*