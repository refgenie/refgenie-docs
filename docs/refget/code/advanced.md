# Refget-py tutorial

## Introduction and prerequisites

This tutorial will introduce you to the `refget-py` python package. In addition to implementing the basic refget protocol, this tutorial will introduce the possibility of storing not just *sequences*, but *annotated sequence collections*, and other object types. This package is built on top of the `henge` package, which provides a generic ability to store and retrieve any data type.

This tutorial assumes you are familiar with the basic refget protocol, and have installed `refget-py` and dependencies.


To begin, let's import some required packages.  


```python
import refget, pymongo, mongodict
from henge import connect_mongo
from collections import OrderedDict
from platform import python_version 
python_version()
```




    '3.8.5'




```python
# Run this command to increase logging output
# import logmuse
# logmuse.init_logger("refget", "DEBUG", devmode=True)
```

## Initialize the back-end

We require some type of database to store the sequences and their digests. The `RefGetHenge` object just needs any object that extends a basic Python `dict`; so a simple `dict` is fine for testing. If you want data to persist, you can use a [MongoDB](https://www.mongodb.com/) instance and a `MongoDict` object on top of it. You can start a mongo database with docker like this:'

```
docker run -v /PATH/TO/PERSISTENT/DATABASE:/data/db mongo
```

Populate the USERID, GROUPID, and PATH variables with values for your setup. Now, we'll use a helper function `connect_mongo` to create a `MongoDict` object to use this back-end and use this to instantate a new refget database (`rgdb`) object:


```python
rgdb = refget.RefGetHenge(database=connect_mongo())
```


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-3-55a2cecd8904> in <module>
    ----> 1 rgdb = refget.RefGetHenge(database=connect_mongo())
    

    AttributeError: module 'refget' has no attribute 'RefGetHenge'


We can easily load and retrieve sequences with the `load_seq` and `refget` functions:


```python
rgdb.load_seq("TCGA")
```




    '45d0ff9f1a9504cf2039f89c1ffb4c32'



The returned digest is the md5 checksum of the sequence itself.


```python
refget.md5("TCGA")
```




    '45d0ff9f1a9504cf2039f89c1ffb4c32'




```python
rgdb.refget("45d0ff9f1a9504cf2039f89c1ffb4c32")
```




    {'sequence': 'TCGA'}




```python
rgdb.refget("45d0ff9f1a9504cf2039f89c1ffb4c32", postprocess="simplify")
```




    'TCGA'



## Loading sequence collections

The back-end can handle not just raw sequences, but another object type we call *Annotated Sequence Digest Lists* -- these are roughly equivalent to a `fasta` file. In fact, if you have a fasta file, you can load that directly into the database and then retrieve it using its own digest.

Let's demonstrate by loading and retreiving some fasta files. Define a few file paths here:


```python
fa_file1 = "demo_fasta/demo.fa.gz"
fa_file2 = "demo_fasta/demo2.fa.gz"
```

Load a fasta file directly into the database with the `load_fasta` function. The function will return 2 things: First, a *digest* that can be used to retrieve the entire contents of the fasta file, and also the contents (in `dict` form) that were loaded into the database.


```python
digest1, content1 = rgdb.load_fasta(fa_file1)
```


```python
digest1
```




    '2bcaa3eadf4fea03f55f0c584af05378'




```python
content1
```




    [{'name': 'chr1',
      'length': 4,
      'topology': 'linear',
      'sequence_digest': 'f1f8f4bf413b16ad135722aa4591043e'},
     {'name': 'chr2',
      'length': 4,
      'topology': 'linear',
      'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'}]



There are a few key concepts here. First, the digest returned here is not the same as the sequence digests we considered previously, because it maps to an *annotated sequence digest list*, rather than just to a sequence. Second, notice the content doesn't include actual sequences; rather, it includes *sequence digests*. These sequence digests can themselves be used with `refget` to retrieve the sequences themselves. In other words, these digests are *recursive*, and this is a critical feature of refget. Because these digests are recursive, we can either set a recursion limit to get the sequence-level digests, or we can set no limit and the `refget` function will recurse to retreive the sequences themselves.

Consider the difference between these two function calls:


```python
rgdb.refget(digest1, reclimit=0)
```




    [{'name': 'chr1',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': 'f1f8f4bf413b16ad135722aa4591043e'},
     {'name': 'chr2',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'}]




```python
rgdb.refget(digest1)
```




    [{'name': 'chr1',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'ACGT'}},
     {'name': 'chr2',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TCGA'}}]



By default, the `refget` function will automatically recurse to return the full sequences contained within. You can use the result like this or pass it through the `fasta_fmt` function to retrieve the original fasta file.


```python
print(rgdb.fasta_fmt(rgdb.refget(digest1)))
```

    >chr1
    ACGT
    >chr2
    TCGA


Here's an example of a second fasta file that includes 2 of the same sequences. The database is smart enough to only store these sequences a single time, but they can live in multiple collections without issue.


```python
digest2, content2 = rgdb.load_fasta(fa_file2)
```


```python
rgdb.refget(digest2)
```




    [{'name': 'chr1',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'ACGT'}},
     {'name': 'chr2',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TCGA'}},
     {'name': 'chrX',
      'length': '8',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TTCCGGAA'}}]




```python
print(rgdb.fasta_fmt(rgdb.refget(digest2)))
```

    >chr1
    ACGT
    >chr2
    TCGA
    >chrX
    TTCCGGAA


## Comparing sequence collections

We may be interested in if collections have the same sequences in different order, or with different names. The `compare` function can provide this information. Let's load some example fasta files with different sequences to demonstrate how the comparisons work.

Now we can compare the content in `digest1` versus `digest2`. Notice that the 2 sequences in the first example are found in the second example, which adds a third sequence.


```python
rgdb.compare(digest1, digest2)
```




    6165



The compare function returns a flag that provides information about the comparison. This allows us to use logical operators to test what features were shared among the sequence collections, similar to the way we use sam flags to identify features of sequence reads. 

We can see the explanation of the flags like this: 


```python
refget.FLAGS
```




    {1: 'CONTENT_ALL_A_IN_B',
     2: 'CONTENT_ALL_B_IN_A',
     4: 'LENGTHS_ALL_A_IN_B',
     8: 'LENGTHS_ALL_B_IN_A',
     16: 'NAMES_ALL_A_IN_B',
     32: 'NAMES_ALL_B_IN_A',
     64: 'TOPO_ALL_A_IN_B',
     128: 'TOPO_ALL_B_IN_A',
     256: 'CONTENT_ANY_SHARED',
     512: 'LENGTHS_ANY_SHARED',
     1024: 'NAMES_ANY_SHARED',
     2048: 'CONTENT_A_ORDER',
     4096: 'CONTENT_B_ORDER'}



So we can use this to ask questions, like, "Are all of the sequence in A contained in B?":


```python
rgdb.compare(digest1, digest2) & 1 == 1
```




    True



Now to ask the inverse question:


```python
rgdb.compare(digest1, digest2) & 2 == 2
```




    False



Or, to ask both at the same time:


```python
rgdb.compare(digest1, digest2) & 3 == 3
```




    False



As expected, we see that the all of A sequences are in B, but not the other way around. If the "&3" query yielded `True`, that would indicate that the sequence content was identical. We can demonstrate this by running a comparison to the same digest:


```python
rgdb.compare(digest1, digest1) & 3 == 3
```




    True



From this flag we can see that the all of the content (sequences) in A are in B, but not the other way around. Furthermore, the lengths in A all match with B (which *must* be true, since the content matches), and also the *names* match, which does not necessarily have to be true.

Let's load some additional fasta files to demonstrate a few more comparisons.


```python
fa_file3 = "demo_fasta/demo3.fa"
fa_file4 = "demo_fasta/demo4.fa"
```


```python
digest3, content3 = rgdb.load_fasta(fa_file3)
rgdb.refget(digest3)
```




    [{'name': '1',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'ACGT'}},
     {'name': '2',
      'length': '4',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TCGA'}},
     {'name': 'X',
      'length': '8',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TTCCGGAA'}}]



The `demo3` file has the exact same sequence content as demo2, but the names are different. The compare function shows that the content and lengths match and are in the same order, but the name match flag is not set:


```python
rgdb.compare(digest2, digest3, explain=True)
```

    Flag: 6159
    Binary: 0b1100000001111
    
    CONTENT_ALL_A_IN_B
    CONTENT_ALL_B_IN_A
    LENGTHS_ALL_A_IN_B
    LENGTHS_ALL_B_IN_A
    CONTENT_A_ORDER
    CONTENT_B_ORDER





    6159



The `demo4` example contains one of the sequences in `demo2`, but has no overlap with `demo1`:


```python
digest4, content4 = rgdb.load_fasta(fa_file4)
rgdb.refget(digest4)
```




    [{'name': 'chrX',
      'length': '8',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TTCCGGAA'}}]




```python
rgdb.compare(digest4, digest2, explain=True)
```

    Flag: 21
    Binary: 0b10101
    
    CONTENT_ALL_A_IN_B
    LENGTHS_ALL_A_IN_B
    NAMES_ALL_A_IN_B





    21




```python
rgdb.compare(digest4, digest1, explain=True)
```

    Flag: 0
    Binary: 0b0
    





    0



## Sequence reference compatibility

We may be interested in comparing the compatibilty of the assembly, rather than the sequences themselves. We can do this using the same comparison function, but this time testing against a version of the genome that lacks actual sequences. Here, we'll insert a 'lengths only' ASDList into the database, which has lengths and topologies but no actual sequences. This is analogous to a `chrom_sizes` file which doesn't care about underlying sequences.


```python
fa_file5 = "demo_fasta/demo5.fa"
digest5, content5 = rgdb.load_fasta(fa_file5, lengths_only=True)
rgdb.refget(digest5)
```




    [{'name': 'chr1', 'length': '4', 'topology': 'linear', 'sequence_digest': ''},
     {'name': 'chr2', 'length': '4', 'topology': 'linear', 'sequence_digest': ''},
     {'name': 'chrX', 'length': '8', 'topology': 'linear', 'sequence_digest': ''}]



These are compatible with the `demo2` file in length and name. You can ask that with "& 60".


```python
rgdb.compare(digest5, digest2, explain=True)
```

    Flag: 60
    Binary: 0b111100
    
    LENGTHS_ALL_A_IN_B
    LENGTHS_ALL_B_IN_A
    NAMES_ALL_A_IN_B
    NAMES_ALL_B_IN_A





    60




```python
rgdb.compare(digest5, digest2) & 60 == 60
```




    True



This is a very useful functionality that allows us to use this system not only to identify sequence matches, but also to establish reference assembly compatibility for questions that do not require strict sequence identity. For example, for a given genome reference, we can create a sequence-agnostic but length-enforced ASDList object and stick it into the database to get back a digest. Now, we can use the compare function to ensure that any future sequences are compatible with this reference assembly.

# 3-layer refget

It is also possible to continue this recursion to another layer. To demonstrate, let's make a sequence that consists of 2 fasta files checksums, and load that into the database.

This type of object is called an *Annotated Collection Digest List*, or *ACDList*, because it's a list of named collection digests. The RefGetHenge object will allow you to see what of its objects types would validate your given object. Here, we see that this henge would recognize this as validating the *ACDList* object type.


```python
ACDList = [{"name": "demo1", "collection_digest": digest1},
           {"name":" demo2", "collection_digest": digest2}]
```


```python
rgdb.select_item_type(ACDList)
```




    ['ACDList']




```python
acdl_digest = rgdb.insert(ACDList, "ACDList")
```

Can we retrieve it? You bet! At any recursion level:


```python
rgdb.refget(acdl_digest)
```




    [{'name': 'demo1',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'ACGT'}},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}}]},
     {'name': ' demo2',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'ACGT'}},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}},
       {'name': 'chrX',
        'length': '8',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TTCCGGAA'}}]}]




```python
rgdb.refget(acdl_digest, reclimit=0)
```




    [{'name': 'demo1', 'collection_digest': '2bcaa3eadf4fea03f55f0c584af05378'},
     {'name': ' demo2', 'collection_digest': '1cabbd10bf54f733718f0d3bc786dc3b'}]




```python
rgdb.refget(acdl_digest, reclimit=1)
```




    [{'name': 'demo1',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': 'f1f8f4bf413b16ad135722aa4591043e'},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'}]},
     {'name': ' demo2',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': 'f1f8f4bf413b16ad135722aa4591043e'},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'},
       {'name': 'chrX',
        'length': '8',
        'topology': 'linear',
        'sequence_digest': 'adbd2580b1cb145667c79baf9bfd391a'}]}]




```python
rgdb.refget(acdl_digest, reclimit=2)
```




    [{'name': 'demo1',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'ACGT'}},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}}]},
     {'name': ' demo2',
      'collection_digest': [{'name': 'chr1',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'ACGT'}},
       {'name': 'chr2',
        'length': '4',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}},
       {'name': 'chrX',
        'length': '8',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TTCCGGAA'}}]}]



## Under the hood: using the raw henge interface

Under the hood, the RefGetHenge is just a specialized class of `Henge` that provides convenience functions for dealing with sequences and sequence collections. Henge is a python package that builds back-ends for generic decomposable recursive unique identifiers (or, *druids*). It is intended to be used as a building block for refget 2.0 on collections, and also for other data types that need content-derived identifiers.

Henge provides 2 key advances:

- **decomposing**: identifiers in henge can retrieve tuples, not just sequences. These tuples can be tailored with a simple json schema document, so that henge can be used as a back-end for arbitrary data.

- **recursion**: individual elements retrieved by the henge object can be tagged as recursive, which means these attributes contain their own druids. Henge can recurse through these, providing arbitrary, multi-layer object retrieval.


To demonstrate how henge works as the back-end for the refget-py package, we'll now show  use the raw henge interface directly, if you want to wrap the metadata yourself.

The way a henge works is that we have to specify what item types it can hold using schemas written in JSON-schema. The RefGetHenge knows about 5 different item types:


```python
rgdb.item_types
```




    ['sequence', 'ASD', 'ASDList', 'ACDList', 'ACD']



We'll look more closely at these schemas in a moment. You can look through the actual schemas by looking at `rgdb.schemas`; for example, the `sequence` schema is quite simple:


```python
rgdb.schemas["sequence"]
```




    {'description': 'Schema for a single raw sequence',
     'type': 'object',
     'properties': {'sequence': {'type': 'string',
       'description': 'Actual sequence content'}},
     'required': ['sequence']}



The RefGetHenge class, handles all the object type control for you; it knows for example to insert a sequence as a 'sequence' object, and a fasta file as an 'ASDList' object. But, you can also use the base `Henge` interface to do this as well; all you have to do is insert the objects as `dicts` or `lists`, with the appropriate properties populated. Here's how we could insert some sequences directly:


```python
item_seq1 = {'sequence': "TCGA"}
item_seq2 = {'sequence': "TCGATCGATCGATCGA"}
item_seq3 = {'sequence': "GGAA"}
item_seq4 = {'sequence': "CGGCCCGGCGC"}

druid_seq1 = rgdb.insert(item_seq1, "sequence")
druid_seq2 = rgdb.insert(item_seq2, "sequence")
druid_seq3 = rgdb.insert(item_seq3, "sequence")
druid_seq4 = rgdb.insert(item_seq4, "sequence")

```

Now, we can also insert *Annotated Sequence Digests* (ASDs):


```python
asd1 = {'sequence_digest': druid_seq1,
        'name': "chr1",
        'length': 10, 
        'topology': "linear"}
asd2 = {'sequence_digest': druid_seq2,
        'name': "chr2",
        'length': 20, 
        'topology': "linear"}
asd3 = {'sequence_digest': druid_seq3,
        'name': "chr3",
        'length': 30, 
        'topology': "circular"}
asd4 = {'sequence_digest': druid_seq4,
        'name': "chr4::mod",
        'length': 40, 
        'topology': "linear"}                
```


```python
druid_asd1 = rgdb.insert(asd1, "ASD")
```

Take a look at the schema for an ASD object. Notice that the `sequence_digest` attribute is marked as `recursive` -- this means the henge will automatically know that upon retrieving one of these objects, that particular property could be recursively retrieved to get another object from the back-end.


```python
rgdb.schemas["ASD"]
```




    {'description': 'Schema for an Annotated Sequence Digest; a digested Sequence plus metadata',
     'type': 'object',
     'properties': {'name': {'type': 'string'},
      'length': {'type': 'integer'},
      'topology': {'type': 'string',
       'enum': ['circular', 'linear'],
       'default': 'linear'},
      'sequence_digest': {'type': 'string', 'description': 'The sequence digest'}},
     'required': ['length', 'name', 'topology'],
     'recursive': ['sequence_digest'],
     'not': {'required': ['sequence']}}




```python
rgdb.refget(druid_asd1)
```




    {'name': 'chr1',
     'length': '10',
     'topology': 'linear',
     'sequence_digest': {'sequence': 'TCGA'}}




```python
rgdb.refget(druid_asd1, reclimit=0)
```




    {'name': 'chr1',
     'length': '10',
     'topology': 'linear',
     'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'}




```python
rgdb.refget(druid_seq1)
```




    {'sequence': 'TCGA'}



And here we can insert ASDLists (which are, of course, simply lists of ASD objects):


```python
druid_asdlist1 = rgdb.insert([asd1, asd2], "ASDList")
druid_asdlist2 = rgdb.insert([asd3, asd4], "ASDList")
```


```python
rgdb.refget(druid_asdlist1)
```




    [{'name': 'chr1',
      'length': '10',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TCGA'}},
     {'name': 'chr2',
      'length': '20',
      'topology': 'linear',
      'sequence_digest': {'sequence': 'TCGATCGATCGATCGA'}}]




```python
acd1 = {'collection_digest': druid_asdlist1,
        'name': "fasta1"} 
acd2 = {'collection_digest': druid_asdlist2,
        'name': "fasta2"} 

druid_acdlist = rgdb.insert([acd1, acd2], "ACDList")    
```


```python
druid_acdlist
```




    '6eaefa29f5e59d6f93e723c02fb6d5fb'



### How items are stored

Refget stores the items as delimited strings. It uses the schemas to map the stored, delimited properties to the correct properties when the item is returned. It builds a string with two delimiters, a *property delimiter* that separates the individual properties, in the order listed in the schema, and it uses an *item delimiter* to delimit items in lists in the order given.

The `sequence` objects are really simple; they have only 1 property, named `sequence`:


```python
rgdb.schemas["sequence"]
```




    {'description': 'Schema for a single raw sequence',
     'type': 'object',
     'properties': {'sequence': {'type': 'string',
       'description': 'Actual sequence content'}},
     'required': ['sequence']}



They are thus stored in the database as is; no delimiters are required because there is only 1 property, and no possibility of listing more than one item.


```python
rgdb.database[druid_seq1]
```




    'TCGA'



The ASD objects have multiple properties, so they are stored as a delimited set of properties, ordered by the schema:


```python
rgdb.schemas["ASD"]
```




    {'description': 'Schema for an Annotated Sequence Digest; a digested Sequence plus metadata',
     'type': 'object',
     'properties': {'name': {'type': 'string'},
      'length': {'type': 'integer'},
      'topology': {'type': 'string',
       'enum': ['circular', 'linear'],
       'default': 'linear'},
      'sequence_digest': {'type': 'string', 'description': 'The sequence digest'}},
     'required': ['length', 'name', 'topology'],
     'recursive': ['sequence_digest'],
     'not': {'required': ['sequence']}}




```python
rgdb.database[druid_asd1]
```




    'chr1\x1e10\x1elinear\x1e45d0ff9f1a9504cf2039f89c1ffb4c32'



ASDList objects are defined as lists, so they can hold more than one item. The items themselves are simply ASD objects; ASDLists are therefore stored as item-delimited strings, with a property-delimited string for each item.


```python
rgdb.schemas["ASDList"]
```




    {'description': 'Schema for List of ASDs',
     'type': 'array',
     'items': {'type': 'object',
      'properties': {'name': {'type': 'string'},
       'length': {'type': 'integer'},
       'topology': {'type': 'string',
        'enum': ['circular', 'linear'],
        'default': 'linear'},
       'sequence_digest': {'type': 'string',
        'description': 'The sequence digest'}},
      'required': ['length', 'name', 'topology'],
      'recursive': ['sequence_digest'],
      'not': {'required': ['sequence']}}}




```python
rgdb.database[druid_asdlist1]
```




    'chr1\x1e10\x1elinear\x1e45d0ff9f1a9504cf2039f89c1ffb4c32\tchr2\x1e20\x1elinear\x1eb835d2c026aa66c52a05838dcc0b59d4'



Here we can see the schema for the ACDList, which is of type 'array', and each item will have 2 properties: `name` and `collection_digest`:


```python
rgdb.schemas["ACDList"]
```




    {'description': 'Schema for a list of ACDs; analogous to a collection of fasta files',
     'type': 'array',
     'items': {'type': 'object',
      'properties': {'name': {'type': 'string'},
       'collection_digest': {'type': 'string'}},
      'required': ['collection_digest'],
      'recursive': ['collection_digest']}}




```python
rgdb.database[druid_acdlist]
```




    'fasta1\x1ead6311ad38f593e9529dc9adf82f126a\tfasta2\x1e2e9262aac405c20d6cba33295b9ff72f'




```python
print(rgdb.database[druid_acdlist])
```

    fasta1ad6311ad38f593e9529dc9adf82f126a	fasta22e9262aac405c20d6cba33295b9ff72f


You can also use the `retrieve` interface (which comes from the parent Henge object) to retrieve items at different recursion levels:


```python
rgdb.retrieve(druid_acdlist)
```




    [{'name': 'fasta1',
      'collection_digest': [{'name': 'chr1',
        'length': '10',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}},
       {'name': 'chr2',
        'length': '20',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGATCGATCGATCGA'}}]},
     {'name': 'fasta2',
      'collection_digest': [{'name': 'chr3',
        'length': '30',
        'topology': 'circular',
        'sequence_digest': {'sequence': 'GGAA'}},
       {'name': 'chr4::mod',
        'length': '40',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'CGGCCCGGCGC'}}]}]




```python
rgdb.retrieve(druid_acdlist, reclimit=1)
```




    [{'name': 'fasta1',
      'collection_digest': [{'name': 'chr1',
        'length': '10',
        'topology': 'linear',
        'sequence_digest': '45d0ff9f1a9504cf2039f89c1ffb4c32'},
       {'name': 'chr2',
        'length': '20',
        'topology': 'linear',
        'sequence_digest': 'b835d2c026aa66c52a05838dcc0b59d4'}]},
     {'name': 'fasta2',
      'collection_digest': [{'name': 'chr3',
        'length': '30',
        'topology': 'circular',
        'sequence_digest': '31fc6ca291a32fb9df82b85e5f077e31'},
       {'name': 'chr4::mod',
        'length': '40',
        'topology': 'linear',
        'sequence_digest': 'c175211cccf95a0e3c43fc0c70a3226d'}]}]




```python
rgdb.retrieve(druid_acdlist, reclimit=2)
```




    [{'name': 'fasta1',
      'collection_digest': [{'name': 'chr1',
        'length': '10',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGA'}},
       {'name': 'chr2',
        'length': '20',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'TCGATCGATCGATCGA'}}]},
     {'name': 'fasta2',
      'collection_digest': [{'name': 'chr3',
        'length': '30',
        'topology': 'circular',
        'sequence_digest': {'sequence': 'GGAA'}},
       {'name': 'chr4::mod',
        'length': '40',
        'topology': 'linear',
        'sequence_digest': {'sequence': 'CGGCCCGGCGC'}}]}]



The jsonschema validation system will prevent you from inserting an item that doesn't match the schema you are trying to insert:


```python
rgdb.insert([{'sequence': "TCGA", "topology":"circular"}], "sequence")
```

    Not valid data
    Attempting to insert item: [{'sequence': 'TCGA', 'topology': 'circular'}]
    Item type: sequence


    [{'sequence': 'TCGA', 'topology': 'circular'}] is not of type 'object'
    
    Failed validating 'type' in schema:
        {'description': 'Schema for a single raw sequence',
         'properties': {'sequence': {'description': 'Actual sequence content',
                                     'type': 'string'}},
         'required': ['sequence'],
         'type': 'object'}
    
    On instance:
        [{'sequence': 'TCGA', 'topology': 'circular'}]





    False




```python
rgdb.insert([{'name': "chrX", 'sequence': "TCGA", "topology":"circular", "length":4}], "asd")
```

    I don't know about items of type 'asd'. I know of: '['sequence', 'ASD', 'ASDList', 'ACDList', 'ACD']'





    False



# Advanced bonus recipes

Here are some advanced things you can do:

List all the items in the database:


```python
for k,v in rgdb.database.items():
    print(k, v)
```

    45d0ff9f1a9504cf2039f89c1ffb4c32 TCGA
    45d0ff9f1a9504cf2039f89c1ffb4c32_item_type sequence
    45d0ff9f1a9504cf2039f89c1ffb4c32_digest_version md5
    f1f8f4bf413b16ad135722aa4591043e ACGT
    f1f8f4bf413b16ad135722aa4591043e_item_type sequence
    f1f8f4bf413b16ad135722aa4591043e_digest_version md5
    2bcaa3eadf4fea03f55f0c584af05378 chr14linearf1f8f4bf413b16ad135722aa4591043e	chr24linear45d0ff9f1a9504cf2039f89c1ffb4c32
    2bcaa3eadf4fea03f55f0c584af05378_item_type ASDList
    2bcaa3eadf4fea03f55f0c584af05378_digest_version md5
    adbd2580b1cb145667c79baf9bfd391a TTCCGGAA
    adbd2580b1cb145667c79baf9bfd391a_item_type sequence
    adbd2580b1cb145667c79baf9bfd391a_digest_version md5
    1cabbd10bf54f733718f0d3bc786dc3b chr14linearf1f8f4bf413b16ad135722aa4591043e	chr24linear45d0ff9f1a9504cf2039f89c1ffb4c32	chrX8linearadbd2580b1cb145667c79baf9bfd391a
    1cabbd10bf54f733718f0d3bc786dc3b_item_type ASDList
    1cabbd10bf54f733718f0d3bc786dc3b_digest_version md5
    2bcc40045a90366fdcc89feeed26ff3f 14linearf1f8f4bf413b16ad135722aa4591043e	24linear45d0ff9f1a9504cf2039f89c1ffb4c32	X8linearadbd2580b1cb145667c79baf9bfd391a
    2bcc40045a90366fdcc89feeed26ff3f_item_type ASDList
    2bcc40045a90366fdcc89feeed26ff3f_digest_version md5
    9fb8efcee89118d6035c4fd54fa41a3d chrX8linearadbd2580b1cb145667c79baf9bfd391a
    9fb8efcee89118d6035c4fd54fa41a3d_item_type ASDList
    9fb8efcee89118d6035c4fd54fa41a3d_digest_version md5
    e9974260ad53075f4021f96b0f7f64a0 chr14linear	chr24linear	chrX8linear
    e9974260ad53075f4021f96b0f7f64a0_item_type ASDList
    e9974260ad53075f4021f96b0f7f64a0_digest_version md5
    981f2447405240954ccef8031040d4c4 demo12bcaa3eadf4fea03f55f0c584af05378	 demo21cabbd10bf54f733718f0d3bc786dc3b
    981f2447405240954ccef8031040d4c4_item_type ACDList
    981f2447405240954ccef8031040d4c4_digest_version md5
    b835d2c026aa66c52a05838dcc0b59d4 TCGATCGATCGATCGA
    b835d2c026aa66c52a05838dcc0b59d4_item_type sequence
    b835d2c026aa66c52a05838dcc0b59d4_digest_version md5
    31fc6ca291a32fb9df82b85e5f077e31 GGAA
    31fc6ca291a32fb9df82b85e5f077e31_item_type sequence
    31fc6ca291a32fb9df82b85e5f077e31_digest_version md5
    c175211cccf95a0e3c43fc0c70a3226d CGGCCCGGCGC
    c175211cccf95a0e3c43fc0c70a3226d_item_type sequence
    c175211cccf95a0e3c43fc0c70a3226d_digest_version md5
    548acc8a98c34bbcdb17bdb7f8b7ea37 chr110linear45d0ff9f1a9504cf2039f89c1ffb4c32
    548acc8a98c34bbcdb17bdb7f8b7ea37_item_type ASD
    548acc8a98c34bbcdb17bdb7f8b7ea37_digest_version md5
    ad6311ad38f593e9529dc9adf82f126a chr110linear45d0ff9f1a9504cf2039f89c1ffb4c32	chr220linearb835d2c026aa66c52a05838dcc0b59d4
    ad6311ad38f593e9529dc9adf82f126a_item_type ASDList
    ad6311ad38f593e9529dc9adf82f126a_digest_version md5
    2e9262aac405c20d6cba33295b9ff72f chr330circular31fc6ca291a32fb9df82b85e5f077e31	chr4::mod40linearc175211cccf95a0e3c43fc0c70a3226d
    2e9262aac405c20d6cba33295b9ff72f_item_type ASDList
    2e9262aac405c20d6cba33295b9ff72f_digest_version md5
    6eaefa29f5e59d6f93e723c02fb6d5fb fasta1ad6311ad38f593e9529dc9adf82f126a	fasta22e9262aac405c20d6cba33295b9ff72f
    6eaefa29f5e59d6f93e723c02fb6d5fb_item_type ACDList
    6eaefa29f5e59d6f93e723c02fb6d5fb_digest_version md5


This is how you would clean out all items in the database:


```python
for k,v in rgdb.database.items():
    del rgdb.database[k]
```

Look at the actual delimiters used by `Henge`.


```python
import henge 
henge.DELIM_ATTR
```




    '\x1e'




```python
henge.DELIM_ITEM
```




    '\t'



## Linking henges

It may be that we want to split information among servers; for example, we want the sequences themselves to be hosted in one location, because that data is large; but we want the collection-level information, which is just sets of pointers to sequences, in another location.

We can do this by linking henges to one other. Here, we'll create two henges; one we call *heavy*, and it only knows how to store sequences. Another, we call *light* -- it stores everything else. Then, we'll tell the light henge that for sequences, it should interact with the heavy henge.


Here, I've started up 2 Mongo instances that both run locally but on different ports. These are effectively different databases and are simulating different servers. For development I do this with these commands: 

```
docker run -it --network "host" --user=854360:25014  -v /ext/qumulo/database/mongo_local:/data/db mongo --port 27018

docker run -it --network "host" --user=854360:25014  -v /ext/qumulo/database/mongo_remote:/data/db mongo --port 27019
```


```python
import henge
import os
```


```python
backend_light = refget.MongoDict(host='localhost', port=27018, database='my_dict',
                        collection='store')
```


```python
backend_heavy = refget.MongoDict(host='localhost', port=27019, database='my_dict',
                        collection='store')
```


```python
schemas_light= { 
                    "ASD": henge.load_yaml("http://schema.databio.org/refget/annotated_sequence_digest.yaml"),
                    "ASDList": henge.load_yaml("http://schema.databio.org/refget/ASDList.yaml"),
                    "ACDList": henge.load_yaml("http://schema.databio.org/refget/ACDList.yaml"),
                    "ACD": henge.load_yaml("http://schema.databio.org/refget/annotated_collection_digest.yaml")}

```


```python
schemas_heavy = {"sequence": henge.load_yaml("http://schema.databio.org/refget/sequence.yaml")}
```


```python
rgdb_heavy = refget.RefGetHenge(backend_heavy, schemas=schemas_heavy)
```


```python
rgdb_heavy.list_item_types()
```

Now when we create the light database, we'll need a dictionary that maps the item types to other henges, so this henge will know how to deal with these item types. We'll create a dict saying that `sequence` items should map to this heavy henge.


```python
heavy_henge_list = {"sequence": rgdb_heavy}
```


```python
rgdb_light = refget.RefGetHenge(backend_light, schemas=schemas_light, henges=heavy_henge_list)
```

But notice that the light database includes sequences in its list of known item types, even though this was included in the schemas. It's because it is populated via it's connection to the heavy henge, which *does* understand sequences.


```python
rgdb_light.list_item_types()
```


```python
rgdb_light.load_seq("TCGA")
```


```python
rgdb_light.refget("45d0ff9f1a9504cf2039f89c1ffb4c32")
```

We've just inserted and retrieved the sequence object through the light henge; however, this sequence is not actually stored in this henge, because it is not listed as one of its primary schemas; here we can show that the henge is actually inserting and retriving this object from the heavy henge"


```python
rgdb_light.show()
```


```python
rgdb_heavy.show()
```

Look at that; it put the heavy object in the heavy database (the 'storage henge') but can still retrieve it through the light database (the 'interface henge').
