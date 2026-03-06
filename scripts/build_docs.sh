#!/bin/bash
# Pre-build pipeline for refgenie documentation.
# Runs all content generation steps before Astro build.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo "=== Pre-build: Migrate content ==="
python scripts/migrate_content.py

echo ""
echo "=== Pre-build: Copy custom overrides ==="
cp -r src/overrides/* src/content/docs/ 2>/dev/null && echo "  Copied overrides" || echo "  No overrides"

echo ""
echo "=== Pre-build: Render Jupyter notebooks ==="
if python -c "import nbconvert" 2>/dev/null; then
    python scripts/render_notebooks.py
else
    echo "  SKIP: nbconvert not installed (pip install nbconvert)"
fi

echo ""
echo "=== Pre-build: Render percent-format Python scripts ==="
python scripts/render_py_scripts.py

echo ""
echo "=== Pre-build: Python API docs ==="
python scripts/render_python_api.py

echo ""
echo "=== Pre-build: Fix image paths ==="
python scripts/fix_image_paths.py

echo ""
echo "=== Pre-build complete ==="
