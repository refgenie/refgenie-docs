# Refgenie from within Python

Third-party python tools can rely on our Python object for access to refgenie assets. `refgenie` CLI relies on `Refgenie` object that provides a Python API for accessing and managing genome assets.

## Installing

No additional installation is required if you have `refgenie` installed.

## Quick start

Create a `RefGenConf` object, which is the package's main data type. You just need to give it a refgenie genome configuration file (in YAML format). You can create a template using `refgenie init`.

As a general rule, the CLI functions are available from within Python under the same names, e.g. `refgenie list ...` is available as `Refgenie.list()` method.

```python
from refgenie import Refgenie
r = Refgenie()
```

Now, you can interact with it:

```python
print(r)
```

Use this to show all available remote assets:

```python
r.listr()
```

In a tool, you're probably most interested in using refgenie to locate reference genome assets, for which you want to use the `get_asset` function. For example:

```python
# identify genome (perhaps provided by user)
genome = "hg38"

# get the local path to bowtie2 indexes:
bt2idx = r.seek(genome, "bowtie2_index")

# run bowtie2...
```

This enables you to write python software that will work on any computing environment without having to worry about passing around brittle environment-specific file paths. See [this tutorial](../refgenie/notebooks/refgenconf_usage.ipynb) for more comprehensive example of how to work with `refgenconf` as a tool developer.

See the complete [refgenconf python API](../refgenie/code/refgenconf-api.md) for more details.
