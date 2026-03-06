#!/usr/bin/env python3
"""Convert Jupyter notebooks to Markdown for Starlight.

Reads .ipynb files from docs/ and writes .md files to src/content/docs/.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / 'docs'
OUT_DIR = REPO_ROOT / 'src' / 'content' / 'docs'

NOTEBOOK_MAP = {
    # Refget notebooks
    'refget/using-services/digests.ipynb': 'refget/using-services/digests.md',
    'refget/using-services/sequence-client.ipynb': 'refget/using-services/sequence-client.md',
    'refget/using-services/seqcol-client.ipynb': 'refget/using-services/seqcol-client.md',
    'refget/hosting-services/agent.ipynb': 'refget/hosting-services/agent.md',
    # Refgenie notebook
    'refgenie/notebooks/refgenie.ipynb': 'refgenie/notebooks/refgenie.md',
    # Legacy notebooks
    'legacy/refgenie/notebooks/tutorial.ipynb': 'legacy/refgenie/notebooks/tutorial.md',
    'legacy/refgenie/notebooks/aliases.ipynb': 'legacy/refgenie/notebooks/aliases.md',
    'legacy/refgenie/notebooks/config_upgrade_03_to_04.ipynb': 'legacy/refgenie/notebooks/config_upgrade_03_to_04.md',
    'legacy/refgenie/notebooks/refgenconf_usage.ipynb': 'legacy/refgenie/notebooks/refgenconf_usage.md',
}


def convert_notebook(nb_path: Path, out_path: Path) -> bool:
    """Convert a single notebook to markdown using nbconvert."""
    if not nb_path.exists():
        print(f"  SKIP (not found): {nb_path}")
        return False

    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                sys.executable, '-m', 'nbconvert',
                '--to', 'markdown',
                '--output-dir', str(out_path.parent),
                '--output', out_path.stem,
                str(nb_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ERROR: {nb_path}: {result.stderr}")
            return False
    except FileNotFoundError:
        print("ERROR: nbconvert not found. Install with: pip install nbconvert")
        sys.exit(1)

    # Post-process: add frontmatter if missing
    text = out_path.read_text()
    if not text.startswith('---'):
        title = out_path.stem.replace('-', ' ').replace('_', ' ').title()
        for line in text.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                text = text.replace(line + '\n', '', 1)
                break
        text = f'---\ntitle: "{title}"\n---\n\n{text}'
        out_path.write_text(text)

    print(f"  OK: {nb_path.name} -> {out_path.relative_to(REPO_ROOT)}")
    return True


def main():
    print("=== Rendering Jupyter notebooks ===")
    success = 0
    for nb_rel, out_rel in NOTEBOOK_MAP.items():
        nb_path = DOCS_DIR / nb_rel
        out_path = OUT_DIR / out_rel
        if convert_notebook(nb_path, out_path):
            success += 1
    print(f"Rendered {success}/{len(NOTEBOOK_MAP)} notebooks.")


if __name__ == '__main__':
    main()
