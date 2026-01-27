# Publishing a RefgetStore to S3

This guide explains how to publish a local RefgetStore to S3 for remote access.

## Prerequisites

- AWS CLI installed
- S3 bucket with public read policy (for public access)
- AWS credentials with write access to the bucket

## Creating the store

```python
from gtars.refget import RefgetStore

store = RefgetStore.on_disk("/path/to/my_store")
store.add_sequence_collection_from_fasta("genome.fa")
```

This creates a directory structure:

```
my_store/
├── rgstore.json        # Store metadata
├── sequences.rgsi      # Sequence index
├── collections.rgci    # Collection metadata index
├── sequences/          # Encoded sequence data
│   └── {prefix}/{digest}.seq
└── collections/        # Collection files
    └── {digest}.rgsi
```

## Uploading to S3

Set your AWS credentials and sync the store:

```bash
export AWS_ACCESS_KEY_ID=<your_key>
export AWS_SECRET_ACCESS_KEY=<your_secret>

aws s3 sync /path/to/my_store s3://bucket-name/my_store
```

## Verifying the upload

Check that files are publicly accessible:

```bash
curl -I "https://bucket-name.s3.us-east-1.amazonaws.com/my_store/rgstore.json"
# Should return HTTP 200
```

## Using the remote store

```python
from gtars.refget import RefgetStore

store = RefgetStore.load_remote(
    cache_path="~/.refget/cache",
    remote_url="https://bucket-name.s3.us-east-1.amazonaws.com/my_store"
)

# Sequences are fetched on-demand and cached locally
seq = store.get_substring("sequence_digest", 0, 100)
```

## S3 bucket policy for public read

If your bucket isn't already public, add this policy:

```json
{
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "AllowPublicRead",
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::bucket-name/*"
        }
    ]
}
```

## Example: Pangenome RefgetStore

The 2023 Human Pangenome Reference is available at:

```
https://refgenie.s3.us-east-1.amazonaws.com/pangenome_refget_store
```

```python
store = RefgetStore.load_remote(
    cache_path="~/.refget/pangenome_cache",
    remote_url="https://refgenie.s3.us-east-1.amazonaws.com/pangenome_refget_store"
)
```
