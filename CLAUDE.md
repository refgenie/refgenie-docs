# Refgenie Documentation

This repository contains the MkDocs documentation for the refgenie ecosystem, hosted at refgenie.org.

## Notebooks vs Python Scripts for Tutorials

This project uses **percent-format `.py` files** instead of Jupyter notebooks (`.ipynb`) for executable tutorials.

### Comparison

|                          | `.ipynb`  | `.py`     |
|--------------------------|-----------|-----------|
| Inline output in editor  | Yes       | No        |
| Run as script            | Awkward   | Yes       |
| Clean git diffs          | No        | Yes       |
| mkdocs render speed      | Same      | Same      |
| AI editing               | Similar   | Similar   |

### Key Difference

In VS Code:
- **`.ipynb`**: Output renders inline, directly below the cell
- **`.py`**: Output renders in a separate Interactive Window panel

### Decision

We use `.py` files because:
1. **Runnable as scripts** - users can just `python tutorial.py`
2. **Clean version control** - plain text diffs, no JSON noise
3. **Still renders in mkdocs** - mkdocs-jupyter handles percent-format `.py` files

### Percent Format

The `.py` files use percent format with `# %%` cell markers:

```python
# %% [markdown]
# # Tutorial Title
#
# Introduction text here.

# %%
import refget
store = refget.load("path/to/store")
print(store.stats())

# %% [markdown]
# ## Next Section
```

This format is recognized by:
- **mkdocs-jupyter** - renders as notebook-style pages in docs
- **VS Code** - shows "Run Cell" buttons (output goes to Interactive Window)
- **Jupyter** - can open directly with jupytext installed

### Capturing Output for Docs

Since `.py` files don't store output, we use a capture script to insert output as markdown blocks:

```bash
cd repos/refget
python examples/capture_outputs.py examples/remote_store.py > ../refgenie-docs/docs/refget/notebooks/remote_store.py
```

This runs the script and inserts output blocks like:

```python
# %%
print("Hello")

# %% [markdown]
# ```
# Hello
# ```
```

The output appears in the rendered docs but the file remains a valid runnable script.

### Location

- Source scripts: `repos/refget/examples/`
- Docs versions (with captured output): `docs/refget/notebooks/`

### Adding to mkdocs.yml

Include `.py` files in the jupyter plugin config:

```yaml
plugins:
  - mkdocs-jupyter:
      include:
        - refget/notebooks/remote_store.py
```

And add to nav:

```yaml
nav:
  - Remote RefgetStore: refget/notebooks/remote_store.py
```
