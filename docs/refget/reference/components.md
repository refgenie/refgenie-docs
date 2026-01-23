# Package components

The `refget` package provides several components for working with GA4GH refget standards:

## 1. Local functions to compute digests

The `refget` package provides a Python interface to fast Rust-based implementations of GA4GH digests for both sequences and sequence collections. If you have a representation of your sequences, such as a FASTA file, you can use these standalone functions to compute the GA4GH digests from Python.

## 2. RefgetStore for local sequence storage

:material-database: **RefgetStore** provides high-performance local storage for sequences and collections. It supports in-memory and on-disk storage modes, sequence retrieval by digest, and FASTA export. RefgetStore is implemented in Rust for speed and can also connect to remote stores.

## 3. Clients for remote APIs

:material-api: **Clients** are for interacting with a remote Refget API. If you want to **use** a remote refget service in your application, you can use refget Clients:

- `SequenceClient` for retrieving sequences from a refget sequences API
- `SequenceCollectionClient` for interacting with a refget sequence collections API
- `FastaDrsClient` for accessing FASTA files via GA4GH DRS endpoints

## 4. Agents for database operations

:material-database-cog: **Agents** are for interacting with a database to produce an API. If you want to **create** a refget service, or otherwise host your own refget database, you can use refget Agents. The `RefgetDBAgent` is the primary interface for creating, updating, and interacting with a PostgreSQL-backed server.

## 5. FastAPI router

The package includes a router that implements the refget API endpoints. You can attach this router to an existing FastAPI service to deploy your own sequence collections API.

## 6. Compliance tests

The testing suite provides compliance tests to evaluate a remote API instance. Use this to confirm that you are implementing the sequence collections standard correctly.

## 7. Command-line interface

The `refget` CLI provides commands for:

- **fasta**: Computing digests and derived files from FASTA files
- **store**: Managing a local RefgetStore
- **seqcol**: Querying remote seqcol servers
- **config**: Managing configuration
- **admin**: Database administration (for server operators)
