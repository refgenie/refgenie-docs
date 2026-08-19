#!/usr/bin/env python3
"""Fix image paths in migrated Starlight content files.

Scans content files for image references and rewrites paths to match
the public/ directory structure.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / 'src' / 'content' / 'docs'
PUBLIC_DIR = REPO_ROOT / 'public'


def build_image_index():
    """Map filename -> list of paths relative to public/."""
    index = {}
    for f in PUBLIC_DIR.rglob('*'):
        if f.is_file() and f.suffix.lower() in ('.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp'):
            rel = '/' + str(f.relative_to(PUBLIC_DIR))
            name = f.name
            if name not in index:
                index[name] = []
            index[name].append(rel)
    return index


def determine_tool(filepath: Path) -> str:
    """Determine which section a content file belongs to."""
    rel = filepath.relative_to(CONTENT_DIR)
    parts = rel.parts
    if len(parts) > 0:
        return parts[0]
    return ''


def _resolve_path(path, tool, image_index):
    """Resolve an image path to the correct location in public/."""
    if re.match(r'^/\w+/img/', path) or path.startswith('/img/'):
        check = PUBLIC_DIR / path.lstrip('/')
        if check.exists():
            return path

    if path.startswith('./img/') or (path.startswith('img/') and not path.startswith('img.shields')):
        filename = path.split('/')[-1]
        return _find_image(filename, tool, image_index) or path

    if path.startswith('/') and path.count('/') == 1:
        filename = path.lstrip('/')
        check = PUBLIC_DIR / filename
        if check.exists():
            return path
        return _find_image(filename, tool, image_index) or path

    return path


def _find_image(filename, tool, image_index):
    """Find an image by filename, preferring the current tool's directory."""
    if filename not in image_index:
        return None

    candidates = image_index[filename]

    tool_path = f'/{tool}/img/{filename}'
    if tool_path in candidates:
        return tool_path

    shared_path = f'/img/{filename}'
    if shared_path in candidates:
        return shared_path

    return candidates[0]


def _fix_match(m, tool, image_index):
    """Fix a markdown image match ![alt](path)."""
    full = m.group(0)
    prefix = m.group(1)
    path = m.group(2)

    if path.startswith('http://') or path.startswith('https://'):
        return full

    new_path = _resolve_path(path, tool, image_index)
    if new_path != path:
        return prefix + new_path + ')'
    return full


def _fix_html_match(m, tool, image_index):
    """Fix an HTML src match src="path"."""
    full = m.group(0)
    prefix = m.group(1)
    path = m.group(2)
    suffix = m.group(3)

    if path.startswith('http://') or path.startswith('https://'):
        return full

    new_path = _resolve_path(path, tool, image_index)
    if new_path != path:
        return prefix + new_path + suffix
    return full


DOC_EXTS = ('.md', '.mdx', '.ipynb', '.py', '.html')


def _link_to_route(target: str, base_dir: str):
    """Resolve a relative doc-page link to an absolute Starlight route.

    Links in the source are relative to the file's own directory (MkDocs
    semantics). Starlight serves every page at an absolute directory URL that
    mirrors the content tree, so we resolve against `base_dir` (the file's
    directory relative to the content root) and drop the source extension,
    mapping README/index to the directory root. Returns None to leave a link
    unchanged (external, absolute, anchors, or non-doc targets).
    """
    import posixpath

    m = re.match(r'^([^#?]*)([#?].*)?$', target)
    path_part = m.group(1)
    suffix = m.group(2) or ''
    if not path_part:
        return None  # pure anchor
    if path_part.startswith('/') or '://' in path_part or path_part.startswith('mailto:'):
        return None
    low = path_part.lower()
    if not (low.endswith(DOC_EXTS) or path_part.endswith('README')):
        return None

    joined = posixpath.normpath(posixpath.join(base_dir, path_part))
    for ext in DOC_EXTS:
        if joined.lower().endswith(ext):
            joined = joined[:-len(ext)]
            break
    for tail in ('README', 'index'):
        if joined == tail or joined.endswith('/' + tail):
            joined = joined[:-len(tail)].rstrip('/')
            break
    route = '/' if joined in ('', '.') else '/' + joined + '/'
    return route + suffix


def fix_internal_links(text: str, filepath: Path) -> str:
    """Rewrite relative doc links in a content file to absolute Starlight routes."""
    base_dir = str(filepath.parent.relative_to(CONTENT_DIR)).replace('\\', '/')
    if base_dir == '.':
        base_dir = ''

    def _md(m):
        route = _link_to_route(m.group(2), base_dir)
        return f'{m.group(1)}{route}{m.group(3)}' if route is not None else m.group(0)

    def _html(m):
        route = _link_to_route(m.group(2), base_dir)
        return f'{m.group(1)}{route}{m.group(3)}' if route is not None else m.group(0)

    # Markdown links: ](target) but not image links ![](...) (those end in image exts)
    text = re.sub(r'(\]\()([^)\s]+)(\))', _md, text)
    # HTML anchors: <a href="target">
    text = re.sub(r'(href=["\'])([^"\']+)(["\'])', _html, text)
    return text


def fix_file(filepath: Path, image_index: dict) -> bool:
    """Fix image paths and internal links in a single file."""
    text = filepath.read_text(errors='replace')
    tool = determine_tool(filepath)

    new_text = re.sub(
        r'(\!\[[^\]]*\]\()([^)]+)\)',
        lambda m: _fix_match(m, tool, image_index),
        text
    )

    new_text = re.sub(
        r'(src=["\'])([^"\']+)(["\'])',
        lambda m: _fix_html_match(m, tool, image_index),
        new_text
    )

    new_text = fix_internal_links(new_text, filepath)

    if new_text != text:
        filepath.write_text(new_text)
        return True
    return False


def main():
    print("=== Fixing image paths in content files ===")
    image_index = build_image_index()
    print(f"Indexed {sum(len(v) for v in image_index.values())} images ({len(image_index)} unique filenames)")

    fixed_files = 0
    for filepath in sorted(CONTENT_DIR.rglob('*')):
        if filepath.is_file() and filepath.suffix in ('.md', '.mdx'):
            if fix_file(filepath, image_index):
                print(f"  Fixed: {filepath.relative_to(REPO_ROOT)}")
                fixed_files += 1

    print(f"\nFixed image paths in {fixed_files} files.")


if __name__ == '__main__':
    main()
