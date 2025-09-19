# Refget Python API Documentation

## Package Overview

The `refget` package provides a Python implementation of the GA4GH refget protocol for accessing reference sequences and sequence collections. It enables standardized access to reference genome sequences using computed identifiers.

### Key Features

- **Sequence Retrieval**: Fetch reference sequences by computed digests
- **Sequence Collections**: Manage and query collections of sequences (seqcol)
- **Multiple Digest Types**: Support for MD5, SHA512, and other digest algorithms
- **Client/Server Architecture**: Both client libraries and server implementations
- **FastAPI Integration**: Easy integration with FastAPI applications
- **Compliance Testing**: Tools for testing refget API compliance

## Core Functions

### FASTA Processing

Functions for converting FASTA files to refget-compatible formats:

::: refget.fasta_to_seqcol_dict
    options:
      heading_level: 3

::: refget.fasta_to_digest
    options:
      heading_level: 3

### FastAPI Integration

::: refget.create_refget_router
    options:
      heading_level: 3

## Client Classes

The client module provides interfaces for interacting with refget-compliant servers.

### SequenceClient

Client for retrieving individual sequences from refget servers:

::: refget.clients.SequenceClient
    options:
      show_source: true
      show_signature: true
      heading_level: 3

### SequenceCollectionClient

Client for working with sequence collections (seqcol):

::: refget.clients.SequenceCollectionClient
    options:
      show_source: true
      show_signature: true
      heading_level: 3

## Agent Classes

Agents provide higher-level abstractions for working with refget data.

### RefgetDBAgent

Database agent for managing refget data storage:

::: refget.agents.RefgetDBAgent
    options:
      show_signature: true
      heading_level: 3

### SequenceCollectionAgent

Agent for sequence collection operations:

::: refget.agents.SequenceCollectionAgent
    options:
      heading_level: 3

### SequenceAgent

Agent for individual sequence operations:

::: refget.agents.SequenceAgent
    options:
      heading_level: 3

