# RefGenConf Python API

## Package Overview

The `refgenconf` package provides a Python interface for managing reference genome resources. It offers a centralized configuration object (`RefGenConf`) that handles local and remote genome assets, enabling seamless integration with bioinformatics pipelines.

### Key Features

- **Asset Management**: Download, build, and organize reference genome assets
- **Path Resolution**: Retrieve paths to genome resources without hardcoding
- **Remote Servers**: Connect to refgenie servers to pull pre-built assets
- **Aliases**: Use human-readable genome names instead of digests
- **Seek Keys**: Access specific sub-assets within larger asset packages

### Installation

```bash
pip install refgenconf
```

### Quick Example

```python
import refgenconf

# Initialize with a genome configuration file
rgc = refgenconf.RefGenConf("genome_config.yaml")

# Get path to a genome asset
bowtie2_index = rgc.seek("hg38", "bowtie2_index")
```

## API Reference

### RefGenConf Class

The main class for interacting with refgenie-managed assets:

::: refgenconf.RefGenConf
    options:
      docstring_style: sphinx

### Exceptions

The package defines several custom exceptions for error handling:

::: refgenconf.MissingGenomeError
    options:
      docstring_style: sphinx

::: refgenconf.MissingAssetError
    options:
      docstring_style: sphinx

::: refgenconf.RefgenconfError
    options:
      docstring_style: sphinx

### Utility Functions

::: refgenconf.select_genome_config
    options:
      docstring_style: sphinx