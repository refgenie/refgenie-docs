# Compliance testing


In the repository under `/tests/api` are compliance tests for a service implementing the sequence collections API.
This will test your collection and comparison endpoints to make sure the comparison function is working. 

- `pytest tests/api` to tests API compliance.
- `pytest tests/api --api_root http://127.0.0.1:8100` to customize the API root URL to test
- By default, the tests will test the recommended `sorted_name_length_pairs`. Add `--no-snlp` to skip it.


So, if you want to test your implementation, you can do it like this:

1. Load the fasta files from the `test_fasta` folder into your API database.
2. Run `pytest tests/api --api_root <API_URL>`, pointing to your URL to test

For example, this will test a remote server instance, and skip tests for sorted name-length pairs:

```
pytest tests/api --api_root https://seqcolapi.databio.org --no-snlp
```