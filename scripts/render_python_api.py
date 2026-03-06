#!/usr/bin/env python3
"""Generate Python API documentation from mkdocstrings ::: directives.

Reads .md files that contain ::: module.Class directives,
uses griffe to extract documentation, and writes plain markdown.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / 'docs'
OUT_DIR = REPO_ROOT / 'src' / 'content' / 'docs'

API_FILES = [
    'refget/reference/reference_docs.md',
    'refget/reference/models.md',
]

DIRECTIVE_RE = re.compile(r'^::: (.+)$')
OPTION_RE = re.compile(r'^    (\w+):(.*)$')


def parse_directive(lines, start):
    """Parse a ::: directive block starting at line index `start`."""
    m = DIRECTIVE_RE.match(lines[start])
    module_path = m.group(1).strip()
    options = {}
    i = start + 1

    if i < len(lines) and lines[i].strip() == 'options:':
        i += 1
        while i < len(lines):
            om = OPTION_RE.match(lines[i])
            if om:
                options[om.group(1).strip()] = om.group(2).strip()
                i += 1
            elif lines[i].startswith('      '):
                i += 1
            else:
                break

    return module_path, options, i


def _resolve(obj):
    """Resolve a griffe Alias to its final target."""
    import griffe
    if isinstance(obj, griffe.Alias):
        try:
            return obj.final_target
        except Exception:
            return obj
    return obj


def _format_signature(obj):
    """Format a function/method signature string."""
    obj = _resolve(obj)
    if not hasattr(obj, 'parameters') or not obj.parameters:
        return obj.name

    params = []
    for p in obj.parameters:
        if p.name in ('self', 'cls'):
            continue
        s = p.name
        if p.annotation:
            ann = str(p.annotation)
            ann = ann.replace('typing.', '')
            s += f': {ann}'
        if p.default and str(p.default) != 'None':
            s += f' = {p.default}'
        elif p.default:
            s += ' = None'
        params.append(s)
    return f"{obj.name}({', '.join(params)})"


def _convert_docstring(text):
    """Convert Sphinx/rST docstring markup to markdown."""
    if not text:
        return ''

    lines = text.split('\n')
    result = []
    i = 0
    in_params = False

    while i < len(lines):
        line = lines[i]

        m = re.match(r'^:param\s+(.+?)\s+(\w+):\s*(.*)', line)
        if m:
            ptype_candidate, pname, desc = m.group(1), m.group(2), m.group(3)
            if not re.search(r'\.\s', ptype_candidate):
                if not in_params:
                    result.append('')
                    result.append('**Parameters:**')
                    result.append('')
                    in_params = True
                while i + 1 < len(lines) and lines[i + 1].startswith('    '):
                    i += 1
                    desc += ' ' + lines[i].strip()
                result.append(f'- **{pname}** (*{ptype_candidate}*) -- {desc}')
                i += 1
                continue

        m = re.match(r'^:param\s+(\w+):\s*(.*)', line)
        if m:
            if not in_params:
                result.append('')
                result.append('**Parameters:**')
                result.append('')
                in_params = True
            pname, desc = m.group(1), m.group(2)
            while i + 1 < len(lines) and lines[i + 1].startswith('    '):
                i += 1
                desc += ' ' + lines[i].strip()
            result.append(f'- **{pname}** -- {desc}')
            i += 1
            continue

        m = re.match(r'^:type\s+\w+:\s*(.*)', line)
        if m:
            i += 1
            continue

        m = re.match(r'^:returns?\s+(.+?):\s*(.*)', line)
        if m:
            in_params = False
            rtype, desc = m.group(1), m.group(2)
            while i + 1 < len(lines) and lines[i + 1].startswith('    '):
                i += 1
                desc += ' ' + lines[i].strip()
            result.append('')
            result.append(f'**Returns** (*{rtype}*): {desc}')
            i += 1
            continue

        m = re.match(r'^:returns?:\s*(.*)', line)
        if m:
            in_params = False
            desc = m.group(1)
            while i + 1 < len(lines) and lines[i + 1].startswith('    '):
                i += 1
                desc += ' ' + lines[i].strip()
            result.append('')
            result.append(f'**Returns:** {desc}')
            i += 1
            continue

        m = re.match(r'^:rtype:\s*(.*)', line)
        if m:
            result.append(f'**Return type:** *{m.group(1)}*')
            i += 1
            continue

        m = re.match(r'^:raises?\s+(\w+):\s*(.*)', line)
        if m:
            in_params = False
            desc = m.group(2)
            while i + 1 < len(lines) and lines[i + 1].startswith('    '):
                i += 1
                desc += ' ' + lines[i].strip()
            result.append('')
            result.append(f'**Raises** *{m.group(1)}*: {desc}')
            i += 1
            continue

        if line.strip() == ':Example:':
            in_params = False
            result.append('')
            result.append('**Example:**')
            i += 1
            continue

        m = re.match(r'^\.\. code-block::\s*(\w+)', line)
        if m:
            in_params = False
            lang = m.group(1)
            result.append(f'```{lang}')
            i += 1
            if i < len(lines) and lines[i].strip() == '':
                i += 1
            while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                if lines[i].strip() == '' and i + 1 < len(lines) and not lines[i + 1].startswith('    '):
                    break
                result.append(lines[i][4:] if lines[i].startswith('    ') else '')
                i += 1
            result.append('```')
            continue

        in_params = False
        result.append(line)
        i += 1

    return '\n'.join(result)


def render_object_doc(module_path, options):
    """Use griffe to extract and format documentation for a Python object."""
    try:
        import griffe
    except ImportError:
        return f"> API documentation for `{module_path}` (requires griffe: `pip install griffe`)\n"

    parts = module_path.rsplit('.', 1)
    if len(parts) == 2:
        module_name, obj_name = parts
    else:
        module_name = parts[0]
        obj_name = None

    try:
        mod = griffe.load(module_name)
    except Exception as e:
        return f"> API documentation for `{module_path}` (module not loadable: {e})\n"

    if obj_name:
        try:
            obj = mod.members[obj_name]
        except KeyError:
            return f"> API documentation for `{module_path}` (object not found)\n"
    else:
        obj = mod

    return _format_object(obj, options)


def _format_object(obj, options, heading_level=3):
    """Format a griffe object as markdown."""
    import griffe

    resolved = _resolve(obj)
    hl = int(options.get('heading_level', heading_level))
    lines = []
    prefix = '#' * hl

    is_class = isinstance(resolved, griffe.Class)
    is_func = isinstance(resolved, griffe.Function)
    is_attr = isinstance(resolved, griffe.Attribute)

    if is_class:
        sig = _format_signature(resolved)
        lines.append(f'{prefix} *class* `{sig}`')
        lines.append('')

        if resolved.docstring:
            lines.append(_convert_docstring(resolved.docstring.value))
            lines.append('')

        if options.get('merge_init_into_class', 'false').lower() == 'true':
            if '__init__' in resolved.members:
                init = _resolve(resolved.members['__init__'])
                if init.docstring:
                    lines.append(_convert_docstring(init.docstring.value))
                    lines.append('')

        methods = []
        properties = []
        classmethods = []

        for member_name, member in resolved.members.items():
            if member_name.startswith('_'):
                continue
            m = _resolve(member)
            if isinstance(m, griffe.Function):
                if any(d.value == 'property' or 'property' in str(d.value)
                       for d in (m.decorators or [])):
                    properties.append((member_name, m))
                elif any(d.value == 'classmethod' or 'classmethod' in str(d.value)
                         for d in (m.decorators or [])):
                    classmethods.append((member_name, m))
                else:
                    methods.append((member_name, m))
            elif isinstance(m, griffe.Attribute):
                properties.append((member_name, m))

        if properties:
            lines.append(f'{"#" * (hl + 1)} Properties')
            lines.append('')
            for pname, prop in sorted(properties, key=lambda x: x[0]):
                prop_resolved = _resolve(prop)
                ret = ''
                if isinstance(prop_resolved, griffe.Function) and prop_resolved.returns:
                    ret = f' -> *{prop_resolved.returns}*'
                elif isinstance(prop_resolved, griffe.Attribute) and prop_resolved.annotation:
                    ret = f': *{prop_resolved.annotation}*'
                lines.append(f'**`{pname}`**{ret}')
                if prop_resolved.docstring:
                    doc = prop_resolved.docstring.value.split('\n')[0]
                    lines.append(f': {doc}')
                lines.append('')

        if classmethods:
            lines.append(f'{"#" * (hl + 1)} Class Methods')
            lines.append('')
            for mname, method in sorted(classmethods, key=lambda x: x[0]):
                _render_method(lines, method, hl + 2)

        if methods:
            lines.append(f'{"#" * (hl + 1)} Methods')
            lines.append('')
            for mname, method in sorted(methods, key=lambda x: x[0]):
                _render_method(lines, method, hl + 2)

    elif is_func:
        sig = _format_signature(resolved)
        lines.append(f'{prefix} `{sig}`')
        lines.append('')
        if resolved.docstring:
            lines.append(_convert_docstring(resolved.docstring.value))
            lines.append('')

    elif is_attr:
        ann = f': *{resolved.annotation}*' if resolved.annotation else ''
        lines.append(f'{prefix} `{resolved.name}`{ann}')
        lines.append('')
        if resolved.docstring:
            lines.append(_convert_docstring(resolved.docstring.value))
            lines.append('')

    elif isinstance(resolved, griffe.Module):
        if resolved.docstring:
            lines.append(resolved.docstring.value)
            lines.append('')
        for member_name, member in resolved.members.items():
            if member_name.startswith('_'):
                continue
            m = _resolve(member)
            if isinstance(m, (griffe.Class, griffe.Function)):
                lines.append(_format_object(member, {}, hl))

    return '\n'.join(lines)


def _render_method(lines, method, hl):
    """Render a single method."""
    resolved = _resolve(method)
    sig = _format_signature(resolved)
    prefix = '#' * hl
    lines.append(f'{prefix} `{sig}`')
    lines.append('')
    if resolved.docstring:
        lines.append(_convert_docstring(resolved.docstring.value))
    lines.append('')


def process_api_file(rel_path):
    """Process a single API doc file, replacing ::: directives."""
    src = DOCS_DIR / rel_path
    dst = OUT_DIR / rel_path
    if not src.exists():
        print(f"  SKIP (not found): {src}")
        return False

    text = src.read_text()
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if DIRECTIVE_RE.match(lines[i]):
            module_path, options, end_i = parse_directive(lines, i)
            rendered = render_object_doc(module_path, options)
            result.append(rendered)
            i = end_i
        else:
            result.append(lines[i])
            i += 1

    output = '\n'.join(result)

    if not output.startswith('---'):
        title = rel_path.replace('/', ' - ').replace('.md', '').replace('code - ', '')
        for line in output.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                # Strip the H1 from body to avoid duplication with frontmatter title
                output = output.replace(line + '\n', '', 1)
                break
        output = f'---\ntitle: "{title}"\n---\n\n{output}'

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(output)
    print(f"  OK: {rel_path}")
    return True


def main():
    print("=== Rendering Python API docs ===")
    success = 0
    for rel_path in API_FILES:
        if process_api_file(rel_path):
            success += 1
    print(f"Processed {success}/{len(API_FILES)} API doc files.")


if __name__ == '__main__':
    main()
