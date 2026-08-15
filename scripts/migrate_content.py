#!/usr/bin/env python3
"""Migrate markdown content from docs/ to src/content/docs/ for Starlight.

Handles:
- Copying .md files with frontmatter added
- Renaming README.md to index.md
- Converting admonitions
- Fixing code fences and image paths
- Skipping notebooks (.ipynb) and Python scripts (.py) handled by other scripts
"""
import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / 'docs'
OUT_DIR = REPO_ROOT / 'src' / 'content' / 'docs'

# Files/dirs to skip (handled by other scripts or not content)
SKIP_PATTERNS = {
    'stylesheets',
    'img',
    'CNAME',
    '.archive',
}

# Files with custom MDX replacements (don't overwrite)
CUSTOM_FILES = {
    'README.md',  # Root homepage is a custom index.mdx
}

# Files that contain ::: directives (handled by render_python_api.py)
API_FILES = {
    'refget/reference/reference_docs.md',
    'refget/reference/models.md',
}

# Files whose content comes from notebooks (handled by render_notebooks.py)
NOTEBOOK_OUTPUT_FILES = {
    'refget/using-services/digests.md',
    'refget/using-services/sequence-client.md',
    'refget/using-services/seqcol-client.md',
    'refget/hosting-services/agent.md',
    'refgenie/notebooks/refgenie.md',
    'legacy/refgenie/notebooks/tutorial.md',
    'legacy/refgenie/notebooks/aliases.md',
    'legacy/refgenie/notebooks/config_upgrade_03_to_04.md',
    'legacy/refgenie/notebooks/refgenconf_usage.md',
}

# Files whose content comes from .py scripts (handled by render_py_scripts.py)
PY_SCRIPT_OUTPUT_FILES = {
    'refget/using-services/getting-started.md',
    'refget/using-services/refgetstore.md',
    'refget/using-services/seqcol-operations.md',
    'refget/using-services/aliases.md',
    'refget/using-services/fhr-metadata.md',
    'refget/using-services/genome-store.md',
}

# MkDocs-specific frontmatter keys to remove
MKDOCS_FRONTMATTER_KEYS = {'hide', 'template', 'toc_depth'}

ADMONITION_START = re.compile(r'^(!{3}|[?]{3}\+?)\s+(\w+)\s*(?:"([^"]*)")?(.*)$', re.IGNORECASE)

TYPE_MAP = {
    'note': 'note',
    'tip': 'tip',
    'warning': 'caution',
    'caution': 'caution',
    'success': 'tip',
    'info': 'note',
    'important': 'caution',
    'danger': 'danger',
}


def convert_admonitions(text: str) -> str:
    """Convert MkDocs admonitions to Starlight format."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        m = ADMONITION_START.match(lines[i])
        if m:
            adm_type = m.group(2).lower()
            title = m.group(3) or ''
            starlight_type = TYPE_MAP.get(adm_type, 'note')

            if title:
                result.append(f':::{starlight_type}[{title}]')
            else:
                result.append(f':::{starlight_type}')

            i += 1
            while i < len(lines):
                line = lines[i]
                if line.strip() == '':
                    result.append('')
                    i += 1
                    if i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                        continue
                    break
                elif line.startswith('    ') or line.startswith('\t'):
                    if line.startswith('    '):
                        result.append(line[4:])
                    else:
                        result.append(line[1:])
                    i += 1
                else:
                    break
            result.append(':::')
            result.append('')
        else:
            result.append(lines[i])
            i += 1

    return '\n'.join(result)


def ensure_frontmatter(text: str, filepath: Path) -> str:
    """Ensure the file has YAML frontmatter with at least a title."""
    if text.startswith('---'):
        end_idx = text.index('---', 3)
        frontmatter = text[3:end_idx].strip()
        rest = text[end_idx + 3:]

        # Remove MkDocs-specific keys and their list values
        fm_lines = []
        skip_list = False
        for line in frontmatter.split('\n'):
            stripped = line.strip()
            if stripped.startswith('- '):
                if skip_list:
                    continue
                fm_lines.append(line)
                continue
            skip_list = False
            key = line.split(':')[0].strip()
            if key in MKDOCS_FRONTMATTER_KEYS:
                skip_list = True
                continue
            fm_lines.append(line)

        has_title = any(l.strip().startswith('title:') for l in fm_lines)
        if not has_title:
            title = _extract_title(rest, filepath)
            fm_lines.insert(0, f'title: "{title}"')

        # Always strip first H1 from body to avoid duplication with frontmatter title
        rest = _strip_first_h1(rest)

        return '---\n' + '\n'.join(fm_lines) + '\n---' + rest

    title = _extract_title(text, filepath)
    text = _strip_first_h1(text)
    return f'---\ntitle: "{title}"\n---\n\n{text}'


def _extract_title(text: str, filepath: Path) -> str:
    """Extract title from first H1 heading or derive from filename."""
    in_code_block = False
    for line in text.strip().split('\n'):
        if line.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if line.startswith('# '):
            title = line[2:].strip()
            title = re.sub(r'<img[^>]*?(?:alt="([^"]*)")?[^>]*/?>',
                          lambda m: m.group(1) or '', title).strip()
            if title:
                return title.replace('"', '\\"')
    name = filepath.stem
    if name in ('README', 'index'):
        name = filepath.parent.name
    return name.replace('-', ' ').replace('_', ' ').title()


def _strip_first_h1(text: str) -> str:
    """Remove the first H1 heading from text to avoid duplication with frontmatter title.

    Skips image-only H1s (logos) — those should remain in the body.
    """
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('# '):
            # Check if this H1 is image-only (a logo, not a real title)
            content = re.sub(r'<img[^>]*?(?:alt="[^"]*")?[^>]*/?>',
                             '', stripped[2:]).strip()
            if not content:
                # Image-only H1 — keep it (it's a logo)
                break
            # Remove the text H1 line and any immediately following blank line
            lines.pop(i)
            if i < len(lines) and lines[i].strip() == '':
                lines.pop(i)
            return '\n'.join(lines)
        # If the first non-empty line is not an H1, don't strip anything
        break
    return text


def fix_image_paths(text: str, filepath: Path) -> str:
    """Fix image paths for Starlight."""
    rel = filepath.relative_to(DOCS_DIR)
    tool = rel.parts[0] if rel.parts else ''

    def _fix_md(m):
        prefix = m.group(1)
        filename_part = m.group(3)
        return f'{prefix}/{tool}/img/{filename_part}'

    def _fix_html(m):
        prefix = m.group(1)
        filename_part = m.group(3)
        return f'{prefix}/{tool}/img/{filename_part}'

    text = re.sub(r'(\!\[.*?\]\()((?:\.\./)*)?img/(.+?\))', _fix_md, text)
    text = re.sub(r'(src=")((?:\.\./)*)?img/(.+?")', _fix_html, text)
    return text


def fix_code_fences(text: str) -> str:
    """Fix MkDocs code fence languages for Starlight/Shiki."""
    text = re.sub(r'```\{(\w+)\}', r'```\1', text)
    text = text.replace('```commandline', '```console')
    text = re.sub(r'```R$', '```r', text, flags=re.MULTILINE)
    text = re.sub(r'```(\w+)\s+title="[^"]*"', r'```\1', text)
    return text


def fix_internal_links(text: str) -> str:
    """Rewrite MkDocs internal links for Starlight."""
    # README.md -> index or / paths
    text = re.sub(r'\]\((\.\./)*README\.md\)', '](/)', text)
    text = re.sub(r'\]\(([^)]*)/README\.md\)', r'](/\1/)', text)
    # .md extensions in relative links -> drop extension
    text = re.sub(r'\]\(([^http][^)]*?)\.md\)', r'](\1/)', text)
    return text


def process_file(src: Path, dst: Path):
    """Process and copy a single markdown file."""
    text = src.read_text(errors='replace')

    text = convert_admonitions(text)
    text = fix_image_paths(text, src)
    text = fix_code_fences(text)
    text = fix_internal_links(text)
    text = ensure_frontmatter(text, src)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text)
    return dst


def main():
    print("=== Migrating content from docs/ to src/content/docs/ ===")
    copied = 0
    skipped = 0

    for src_file in sorted(DOCS_DIR.rglob('*')):
        if src_file.is_dir():
            continue

        rel = src_file.relative_to(DOCS_DIR)
        rel_str = str(rel)

        # Skip non-content files
        if any(rel_str.startswith(s) for s in SKIP_PATTERNS):
            continue
        if rel_str == 'CNAME':
            continue

        # Skip files with custom MDX replacements
        if rel_str in CUSTOM_FILES:
            skipped += 1
            continue

        # Skip notebooks (handled by render_notebooks.py)
        if src_file.suffix == '.ipynb':
            continue

        # Skip percent-format Python scripts (handled by render_py_scripts.py)
        if src_file.suffix == '.py':
            continue

        # Skip non-markdown
        if src_file.suffix not in ('.md',):
            dst = OUT_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst)
            copied += 1
            continue

        # Skip files that will be generated by render_notebooks.py
        if rel_str.replace('.md', '') + '.md' in NOTEBOOK_OUTPUT_FILES:
            skipped += 1
            continue

        # Skip files that will be generated by render_py_scripts.py
        if rel_str.replace('.md', '') + '.md' in PY_SCRIPT_OUTPUT_FILES:
            skipped += 1
            continue

        # Skip API files (handled by render_python_api.py)
        if rel_str in API_FILES:
            skipped += 1
            continue

        # Handle README.md -> index.md rename
        dst = OUT_DIR / rel
        if src_file.name == 'README.md':
            dst = dst.parent / 'index.md'

        dst = process_file(src_file, dst)
        print(f"  {rel_str} -> {dst.relative_to(REPO_ROOT)}")
        copied += 1

    print(f"\nMigrated {copied} files, skipped {skipped}.")


if __name__ == '__main__':
    main()
