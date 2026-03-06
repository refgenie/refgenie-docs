#!/usr/bin/env python3
"""Convert percent-format Python scripts to Markdown for Starlight.

Reads .py files with # %% markers from docs/ and converts them to .md files
in src/content/docs/. These are percent-format Python scripts that mkdocs-jupyter
previously rendered as notebook-style pages.

The conversion:
- # %% [markdown] blocks -> markdown text
- # %% code cells -> fenced code blocks
- Output blocks (# %% [markdown] with ``` fences) -> output blocks
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / 'docs'
OUT_DIR = REPO_ROOT / 'src' / 'content' / 'docs'

PY_SCRIPT_MAP = {
    'refget/using-services/getting-started.py': 'refget/using-services/getting-started.md',
    'refget/using-services/refgetstore.py': 'refget/using-services/refgetstore.md',
    'refget/using-services/seqcol-operations.py': 'refget/using-services/seqcol-operations.md',
    'refget/using-services/aliases.py': 'refget/using-services/aliases.md',
    'refget/using-services/fhr-metadata.py': 'refget/using-services/fhr-metadata.md',
    'refget/using-services/genome-store.py': 'refget/using-services/genome-store.md',
}


def parse_percent_format(text: str) -> list:
    """Parse a percent-format Python script into cells.

    Returns list of (cell_type, content) tuples where cell_type is
    'markdown', 'code', or 'output'.
    """
    cells = []
    lines = text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Markdown cell: # %% [markdown]
        if re.match(r'^# %% \[markdown\]', line):
            is_output = 'output' in line.lower()
            i += 1
            content_lines = []
            while i < len(lines) and not re.match(r'^# %%', lines[i]):
                # Strip leading '# ' from markdown lines
                l = lines[i]
                if l.startswith('# '):
                    content_lines.append(l[2:])
                elif l == '#':
                    content_lines.append('')
                else:
                    content_lines.append(l)
                i += 1
            cell_type = 'output' if is_output else 'markdown'
            cells.append((cell_type, '\n'.join(content_lines)))

        # Code cell: # %%
        elif re.match(r'^# %%\s*$', line):
            i += 1
            content_lines = []
            while i < len(lines) and not re.match(r'^# %%', lines[i]):
                content_lines.append(lines[i])
                i += 1
            # Strip trailing empty lines
            while content_lines and content_lines[-1].strip() == '':
                content_lines.pop()
            cells.append(('code', '\n'.join(content_lines)))

        else:
            # Skip non-cell content (e.g., shebang, initial comments)
            i += 1

    return cells


def cells_to_markdown(cells: list, title: str) -> str:
    """Convert parsed cells to Starlight-compatible markdown."""
    parts = [f'---\ntitle: "{title}"\n---\n']

    first_markdown = True
    for cell_type, content in cells:
        if cell_type == 'markdown':
            if first_markdown:
                # Strip first H1 to avoid duplication with frontmatter title
                lines = content.split('\n')
                for idx, line in enumerate(lines):
                    if line.strip() == '':
                        continue
                    if line.startswith('# '):
                        lines.pop(idx)
                        if idx < len(lines) and lines[idx].strip() == '':
                            lines.pop(idx)
                        content = '\n'.join(lines)
                        break
                    break
                first_markdown = False
            parts.append(content)
            parts.append('')
        elif cell_type == 'code':
            parts.append('```python')
            parts.append(content)
            parts.append('```')
            parts.append('')
        elif cell_type == 'output':
            # Output blocks - render as-is (they contain ``` fences already)
            parts.append(content)
            parts.append('')

    return '\n'.join(parts)


def extract_title(text: str, filepath: Path) -> str:
    """Extract title from the first markdown cell's H1, or derive from filename."""
    cells = parse_percent_format(text)
    for cell_type, content in cells:
        if cell_type == 'markdown':
            for line in content.split('\n'):
                if line.startswith('# '):
                    return line[2:].strip().replace('"', '\\"')
    name = filepath.stem
    return name.replace('-', ' ').replace('_', ' ').title()


def convert_py_script(src_path: Path, out_path: Path) -> bool:
    """Convert a single percent-format Python script to markdown."""
    if not src_path.exists():
        print(f"  SKIP (not found): {src_path}")
        return False

    text = src_path.read_text(errors='replace')
    title = extract_title(text, src_path)
    cells = parse_percent_format(text)
    markdown = cells_to_markdown(cells, title)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown)
    print(f"  OK: {src_path.name} -> {out_path.relative_to(REPO_ROOT)}")
    return True


def main():
    print("=== Rendering percent-format Python scripts ===")
    success = 0
    for py_rel, out_rel in PY_SCRIPT_MAP.items():
        src_path = DOCS_DIR / py_rel
        out_path = OUT_DIR / out_rel
        if convert_py_script(src_path, out_path):
            success += 1
    print(f"Rendered {success}/{len(PY_SCRIPT_MAP)} Python scripts.")


if __name__ == '__main__':
    main()
