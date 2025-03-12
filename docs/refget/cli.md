# Refget CLI


!!! warning "CLI is beta and may change"
    The CLI is just a beta and may change at any time.
    
Refget also provides a command-line interface.


## Computing digests

You can also use the CLI to compute to digest locally from a fasta file. 

```
refget digest-fasta test_fasta/base.fa -level 0
INFO:refget.refget:Digesting fasta file: test_fasta/base.fa
XZlrcEGi6mlopZ2uD8ObHkQB1d0oDwKk
```

```
refget digest-fasta test_fasta/base.fa --level 1
INFO:refget.refget:Digesting fasta file: test_fasta/base.fa
{
  "names": "Fw1r9eRxfOZD98KKrhlYQNEdSRHoVxAG",
  "sequences": "0uDQVLuHaOZi1u76LjV__yrVUIz9Bwhr"
}
```

use `--level 2` to get the canonical representation of the sequence collection.





## Adding sequence collections

Use `refget add-fasta` to add fasta files to the database.
First you have to set the environment variables. You can run

```
source deployment/local_demo/local_demo.env
```

Or set them manually.

```
export POSTGRES_HOST=`pass databio/seqcol/postgres_host`
export POSTGRES_DB=`pass databio/seqcol/postgres_db`
export POSTGRES_USER=`pass databio/seqcol/postgres_user`
export POSTGRES_PASSWORD=`pass databio/seqcol/postgres_password`
export POSTGRES_TABLE="seqcol"
```

Then you just run

```
refget add-fasta -f path/to/fasta/file.fa.gz
```

### Adding a PEP

If you have a lot of fasta files, you can add them all at the same time like

```
refget add-fasta -p path/to/pep.csv
```

This CSV file should have these columns:

- `sample_name`: uniquee identifier for this fasta file
- `fasta`: path to fasta file

