# Compliance testing


In the repository under `/test_api` are compliance tests for a service implementing the sequence collections API. This will test your collection and comparison endpoints to make sure the comparison function is working. 

- `pytest test_api` to tests API compliance
- `pytest test_api --api_root http://127.0.0.1:8100` to customize the API root URL to test

1. Load the fasta files from the `test_fasta` folder into your API database.
2. Run `pytest test_api --api_root <API_URL>`, pointing to your URL to test

For example, this will test a remote server instance:

```
pytest test_api --api_root https://seqcolapi.databio.org
```