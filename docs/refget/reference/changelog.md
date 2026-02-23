# Changelog

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.


## [0.11.0] - 2026-02-18

### Added
- New gtars features exposed in refget Python API: `compute_fai`, `digest_sequence`, and `SequenceCollection` now available via `import refget`
- FHR metadata support: `refget store metadata` and `refget store metadata-set` commands for managing collection metadata
- `refget store pull` command for fetching collections from remote servers into your local store
- Seqcol CLI commands (`show`, `compare`, `validate`) now look up collections in the local store before querying remote servers
- GA4GH compliance test suite with 65 checks covering all seqcol spec endpoints, runnable via pytest or the web UI
- Web UI compliance runner with real-time streaming results, stop button, and per-test descriptions
- Swagger/OpenAPI documentation for all API query parameters
- gtars version displayed in service-info and frontend footer badges
- Download collections in seqcol JSON format from the web UI

### Changed
- seqcolapi no longer has independent versioning; it now versions with refget
- Improved FASTA digest page UI
- Improved error messages and error handling across frontend fetch calls
- Frontend cleanup: removed dead code, simplified component structure

## [0.10.1] - 2026-01-27

- Fix CLI `store list` JSON serialization error (was returning non-serializable metadata objects)
- Fix CLI `store get`, `store remove`, and `store pull` commands that failed to find collections
- Update CLI to use `iter_collections()` API instead of removed `collections()` method

## [0.10.0] - 2026-01-26

- Major restructure of the package with new comprehensive CLI (`refget` command)
- New CLI subcommands: `admin`, `config`, `fasta`, `seqcol`, and `store`
- Implement FASTA DRS objects for serving FASTA files via GA4GH DRS endpoints
- Add RefgetStore integration for local sequence storage via gtars
- Refactor to isolate gtars dependency, improving import performance
- Add service-info capabilities for fasta_drs and refget_store features
- New integration test framework with ephemeral Docker PostgreSQL
- Comprehensive CLI test suite
- API compliance tests against GA4GH seqcol specification
- Fix endpoint path: `/list/collection` (was `/list/collections` in client)
- New browser-based `/digest` feature for computing seqcol digests from FASTA files entirely client-side using [@databio/gtars](https://www.npmjs.com/package/@databio/gtars) WASM module

## [0.9.0] - 2025-08-13

- performance fix for calculating jaccard similarties
- add human_readable_name list as an attribute to SequenceCollection for displaying similarity results
- adding SequenceCollections via PEP will now add associated sample_name as a human_readable_name
- add wrapper for gtars RefgetStore so it can be called directly from refget

## [0.8.3] - 2025-07-31

- adds API endpoints for jaccard similarity calculations
- some refactoring for newest gtars, v0.3.0
- add class method from_PySequenceCollection for creating SequenceCollection from a gtars-created SequenceCollection
- adds Similarity UI to frontend

## [0.8.2] - 2025-03-26

- updated add method to use boolean for updating SequenceCollection if already exists

## [0.8.1] - 2025-03-21

- addition of SCIM

## [0.8.0] - 2025-03-05

- Complete rewrite of the clients and agents.
- New SequenceAgent class allows using the RefgetDBAgent class to store sequences. This is meant for testing purposes.
- Completely refactored Clients work adds mature SequenceClient and SequenceCollectionClient classes.
- Fix issues with rust digest calculations to improve flexibilty, using latest update to gtars interface.
- Updates to latest ga4gh paging guidance
- Add a beta CLI with `digest-fasta` and `add-fasta` functionality.
- Remove some old stuff based on henge backend

## [0.7.0] - 2025-01-11

- Major revamp to RefGetClient object, which now works with either sequences or seqcol servers, and can handle any of the seqcol API endpoints.
- Better integration of rust digest calculations built on gtars
- switch back-end to use JSON instead of str
- implement name_length_pairs and sorted_sequences attrs
- improve some SeqCol object representations

## [0.6.0] - 2024-08-08

- Change paging style of list endpoints to match latest GA4GH pagination guide
- Implement new `/list/attribute` endpoint on back-end, and add to demo
- Update endpoint paths slightly after discussion for the `/list` and `/attribute` endpoints
- Remove some of the duplicate endpoints to solidify to one API

## [0.5.0] - 2024-07-06

- Work on deployment, container building, configuration
- Add some work toward pangenomes
- Various misc improvements

## [0.4.0] - 2024-06-26

- Implement new sqlmodel and agent for new database backend
- Add new React interface


## [0.3.0] - 2024-02-23

- Add seqcolapi router

## [0.2.0] - 2024-02-03

- Integrate seqcol into refget package.

## [0.1.0] - 2021-06-17

- First public version, backed by henge version 0.1.1.

## [0.0.1] - 2020-06-25

Beta version for testing
