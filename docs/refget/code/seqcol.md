```python
import seqcol, pymongo, mongodict
from henge import connect_mongo
from collections import OrderedDict
from platform import python_version 
python_version()
```




    '3.8.5'




```python
sqdb = seqcol.SeqColHenge({})
```

    ['/home/nsheff/.local/lib/python3.8/site-packages/seqcol/schemas/AnnotatedSequenceList.yaml']



```python
fa_file1 = "../demo_fasta/demo.fa.gz"
fa_file2 = "../demo_fasta/demo5.fa.gz"
```


```python
digest1, content1 = sqdb.load_fasta(fa_file1)
```


```python
digest1, content1
```




    ('0fa9bee27d61f92081c6063c922f9508352d940b8c53d53d',
     [{'name': 'chr1',
       'length': 4,
       'topology': 'linear',
       'sequence': {'sequence': 'ACGT'}},
      {'name': 'chr2',
       'length': 4,
       'topology': 'linear',
       'sequence': {'sequence': 'TCGA'}}])




```python
sqdb.retrieve(digest1)
```




    [{'length': '4',
      'name': 'chr1',
      'sequence': {'sequence': 'ACGT'},
      'topology': 'linear'},
     {'length': '4',
      'name': 'chr2',
      'sequence': {'sequence': 'TCGA'},
      'topology': 'linear'}]




```python
sqdb2 = seqcol.SeqColHenge({}, schemas=["../seqcol/schemas/RawSeqCol.yaml"])
```

    ['../seqcol/schemas/RawSeqCol.yaml']



```python
fa = seqcol.parse_fasta(fa_file1)
```


```python
str(fa[1])
```




    'TCGA'




```python
fa.keys()
```




    odict_keys(['chr1', 'chr2'])




```python
digest1, content1 = sqdb2.load_fasta2(fa_file1)
```


```python
digest1, content1
```




    ('4cf8e466ed0c750435042a86789d6b6f0c4c16f2098c6cb0',
     [{'name': 'chr1', 'length': 4, 'topology': 'linear', 'sequence': 'ACGT'},
      {'name': 'chr2', 'length': 4, 'topology': 'linear', 'sequence': 'TCGA'}])




```python
sqdb2.retrieve(digest1)
```




    [{'length': '4', 'name': 'chr1', 'sequence': 'ACGT'},
     {'length': '4', 'name': 'chr2', 'sequence': 'TCGA'}]




```python
sqdb2.show()
```

    d82912969973921cb8cffbfacc711e349363e61b1ad99f4a sequence,ACGT
    d82912969973921cb8cffbfacc711e349363e61b1ad99f4a_item_type sequence
    d82912969973921cb8cffbfacc711e349363e61b1ad99f4a_digest_version md5
    b3384914bd4120dcea6709943a467acc1b510102c9200446 length,4,name,chr1,sequence,d82912969973921cb8cffbfacc711e349363e61b1ad99f4a,topology,linear
    b3384914bd4120dcea6709943a467acc1b510102c9200446_item_type ASD
    b3384914bd4120dcea6709943a467acc1b510102c9200446_digest_version md5
    55b2baaa61e109b00bc94c631981e778d149683ff5b95d7a sequence,TCGA
    55b2baaa61e109b00bc94c631981e778d149683ff5b95d7a_item_type sequence
    55b2baaa61e109b00bc94c631981e778d149683ff5b95d7a_digest_version md5
    58ad19366004fc9e9f4ae94d499bec8b4ffdf41b7dbb4468 length,4,name,chr2,sequence,55b2baaa61e109b00bc94c631981e778d149683ff5b95d7a,topology,linear
    58ad19366004fc9e9f4ae94d499bec8b4ffdf41b7dbb4468_item_type ASD
    58ad19366004fc9e9f4ae94d499bec8b4ffdf41b7dbb4468_digest_version md5
    0fa9bee27d61f92081c6063c922f9508352d940b8c53d53d b3384914bd4120dcea6709943a467acc1b510102c9200446,58ad19366004fc9e9f4ae94d499bec8b4ffdf41b7dbb4468
    0fa9bee27d61f92081c6063c922f9508352d940b8c53d53d_item_type AnnotatedSequenceList
    0fa9bee27d61f92081c6063c922f9508352d940b8c53d53d_digest_version md5
    68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36 ACGT
    68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36_item_type sequence
    68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36_digest_version md5
    cc08127667cfd8b1807dcd8de9c41c61a5ac497a67318591 length,4,name,chr1,sequence,68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36
    cc08127667cfd8b1807dcd8de9c41c61a5ac497a67318591_item_type ASD
    cc08127667cfd8b1807dcd8de9c41c61a5ac497a67318591_digest_version md5
    3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce TCGA
    3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce_item_type sequence
    3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce_digest_version md5
    a97daae30ecae2e1b87f88f4275a8b9b2f8e02dbbb19e4b4 length,4,name,chr2,sequence,3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce
    a97daae30ecae2e1b87f88f4275a8b9b2f8e02dbbb19e4b4_item_type ASD
    a97daae30ecae2e1b87f88f4275a8b9b2f8e02dbbb19e4b4_digest_version md5
    4cf8e466ed0c750435042a86789d6b6f0c4c16f2098c6cb0 cc08127667cfd8b1807dcd8de9c41c61a5ac497a67318591,a97daae30ecae2e1b87f88f4275a8b9b2f8e02dbbb19e4b4
    4cf8e466ed0c750435042a86789d6b6f0c4c16f2098c6cb0_item_type RawSeqCol
    4cf8e466ed0c750435042a86789d6b6f0c4c16f2098c6cb0_digest_version md5



```python
sqdb3 = seqcol.SeqColHenge({}, schemas=["../seqcol/schemas/TASeqCol.yaml"])
```

    ['../seqcol/schemas/TASeqCol.yaml']



```python
tadat = {"topology": ["linear", "circular"], "rawseqcol": [{'name': 'chr1', 'length': 4, 'sequence': 'ACGT'},
 {'name': 'chr2', 'length': 4, 'sequence': 'TCGA'}]}
```


```python
digest_ta = sqdb3.insert(tadat, "TASeqCol")
```


```python
sqdb3.retrieve(digest_ta)
```




    {'rawseqcol': [{'length': '4', 'name': 'chr1', 'sequence': 'ACGT'},
      {'length': '4', 'name': 'chr2', 'sequence': 'TCGA'}],
     'topology': ['linear', 'circular']}




```python
sqdb3.retrieve(digest_ta, reclimit=1)
```




    {'rawseqcol': ['cc08127667cfd8b1807dcd8de9c41c61a5ac497a67318591',
      'a97daae30ecae2e1b87f88f4275a8b9b2f8e02dbbb19e4b4'],
     'topology': ['linear', 'circular']}




```python
sqdb3.retrieve(digest_ta, reclimit=0)
```




    {'rawseqcol': '4cf8e466ed0c750435042a86789d6b6f0c4c16f2098c6cb0',
     'topology': 'd6abc28a8e26eaededde8ccfc77251290fe523abf4292807'}




```python
sqdb3.retrieve("0e6a942e25005983bf54622997ec90cbf34b1c7dce597636")
```

    No remote URL connected



```python

digest1, content1 = sqdb3.load_fasta2(fa_file2)
```

    Whoa! A henge-classed primitive type!
    Whoa! A henge-classed primitive type!
    Whoa! A henge-classed primitive type!



```python

```


```python

```


```python
# If you want you can turn debug text on with this command:
import logmuse
logmuse.init_logger("henge", "DEBUG", devmode=True)
```

    DEBU 11:12:33 | henge:est:265 > Configured logger 'henge' using logmuse v0.2.6 





    <Logger henge (DEBUG)>




```python
sqdb4 = seqcol.SeqColHenge({}, schemas=["../seqcol/schemas/SeqColArraySet.yaml"])
```

    ['../seqcol/schemas/SeqColArraySet.yaml']



```python
sqdb4
```




    Henge object. Item types: SeqColArraySet,array,seqarray,seq




```python
item = {"topologies": ["linear", "circular"], "names": ['chr1', 'chr2'], 'sequences': ['ACGT', 'TCGA'], 
        'lengths': ['4', '4']}
```


```python
digest = sqdb4.insert(item, "SeqColArraySet")
```


```python
sqdb4.retrieve(digest)
```




    {'lengths': ['4', '4'],
     'names': ['chr1', 'chr2'],
     'sequences': ['ACGT', 'TCGA'],
     'topologies': ['linear', 'circular']}




```python
sqdb4.retrieve(digest, reclimit=1)
```




    {'lengths': ['4', '4'],
     'names': ['chr1', 'chr2'],
     'sequences': ['68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36',
      '3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce'],
     'topologies': ['linear', 'circular']}




```python
sqdb4.database
```




    {'d6abc28a8e26eaededde8ccfc77251290fe523abf4292807': 'linear,circular',
     'd6abc28a8e26eaededde8ccfc77251290fe523abf4292807_item_type': 'array',
     'd6abc28a8e26eaededde8ccfc77251290fe523abf4292807_digest_version': 'md5',
     'bccead699a3e2ba77c277494129c3e0c0e627f68f1d36ec6': 'chr1,chr2',
     'bccead699a3e2ba77c277494129c3e0c0e627f68f1d36ec6_item_type': 'array',
     'bccead699a3e2ba77c277494129c3e0c0e627f68f1d36ec6_digest_version': 'md5',
     '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36': 'ACGT',
     '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36_item_type': 'seq',
     '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36_digest_version': 'md5',
     '3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce': 'TCGA',
     '3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce_item_type': 'seq',
     '3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce_digest_version': 'md5',
     'ca82b053295b6f49923d0b2cedb83de49c6be59688c3dfd9': '68a178f7c740c5c240aa67ba41843b119d3bf9f8b0f0ac36,3912dddce432f3085c6b4f72a644c4c4c73f07215a9679ce',
     'ca82b053295b6f49923d0b2cedb83de49c6be59688c3dfd9_item_type': 'seqarray',
     'ca82b053295b6f49923d0b2cedb83de49c6be59688c3dfd9_digest_version': 'md5',
     '94f302915f7e6362d1c80bcf21287f8c54ff1a1f849d4bfd': '4,4',
     '94f302915f7e6362d1c80bcf21287f8c54ff1a1f849d4bfd_item_type': 'array',
     '94f302915f7e6362d1c80bcf21287f8c54ff1a1f849d4bfd_digest_version': 'md5',
     '4d89fcd5cd64a82356ca5ebd0ad90753fdeb8e7098717ade': 'lengths,94f302915f7e6362d1c80bcf21287f8c54ff1a1f849d4bfd,names,bccead699a3e2ba77c277494129c3e0c0e627f68f1d36ec6,sequences,ca82b053295b6f49923d0b2cedb83de49c6be59688c3dfd9,topologies,d6abc28a8e26eaededde8ccfc77251290fe523abf4292807',
     '4d89fcd5cd64a82356ca5ebd0ad90753fdeb8e7098717ade_item_type': 'SeqColArraySet',
     '4d89fcd5cd64a82356ca5ebd0ad90753fdeb8e7098717ade_digest_version': 'md5'}




```python

```
