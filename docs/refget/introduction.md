# Introduction to the refget Python package

This package provides several things.
In the following pages, you'll find tutorials that will walk you through:

## Package components: Functions, Clients, and Agents

In these docs, you will find how-to guides describing these components:

1. **Local functions to compute digests**. The `refget` package provides a Python interface to fast rust-based implementations of GA4GH digests for both sequences and sequence collections. If you have a representation of your sequences, such as a FASTA file or some other representation, you can use these standalone functions to compute the GA4GH digests for individual sequences or collections from Python.

2. :material-api: **Clients** are for interacting with a remote Refget API. If you want to **use** a remote refget service in your application, you can use refget Clients. There is a `refget.SequenceClient` object for operating with a refget sequences API, and a `refget.SequenceCollectionClient` for interacting with a refget sequence collections API.

3. :material-database-cog: **Agents**  are for interacting with a database to produce an API. If you want to **create** a refget service, or otherwise host your own refget database, then you can use refget Agents. The `refget.RefgetDBAgent` is the primary interface for creating, updating, and interacting with a SQL-backed server for storing refget sequences or collections.

4. **API router**. The package also includes a simple router that implements the refget sequences API. You can attach this router to an existing FastAPI service to deploy your own sequence collections API.

5. **Compliance tests.** The testing suite provides a compliance test to evaluate a remote API instance. Use this to confirm that you are implementing the sequence collections standard correctly.

6. **Command-line interface.** The `refget` command provides some convenient functions (beta).

