# Compliance testing


In the repository under `/tests/api` are compliance tests for a service implementing the sequence collections API. This will test your collection and comparison endpoints to make sure the comparison function is working.

- `pytest tests/api` to test API compliance
- `pytest tests/api --api-root http://127.0.0.1:8100` to customize the API root URL to test

1. Load the fasta files from the `test_fasta` folder into your API database.
2. Run `pytest tests/api --api-root <API_URL>`, pointing to your URL to test

For example, this will test a remote server instance:

```
pytest tests/api --api-root https://seqcolapi.databio.org
```