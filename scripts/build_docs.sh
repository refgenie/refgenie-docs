#!/bin/bash
# Pre-build pipeline for refgenie documentation.
# Runs all content generation steps before Astro build.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo "=== Pre-build: Clear stale content + Astro cache ==="
# Everything below regenerates src/content/docs. Two kinds of staleness bite if
# we don't reset first:
#   1. Astro's content-layer cache (.astro/) keeps entries for restructured
#      pages -> "Duplicate id ... later items overwrite earlier".
#   2. migrate/render steps never delete a generated file whose source was moved
#      or removed -> "Failed to find the topic for ..." on the orphan.
# So clear the cache and wipe generated content before regenerating. Preserve
# the R vignette pages (refget/biocrefgetstore/), which only regenerate when
# bulker is available (it is skipped in CI); everything else is rebuilt below.
rm -rf .astro node_modules/.astro
mkdir -p src/content/docs
find src/content/docs -mindepth 1 \
  -path 'src/content/docs/refget/biocrefgetstore*' -prune -o \
  -type f -print0 | xargs -0 rm -f 2>/dev/null || true
find src/content/docs -mindepth 1 -type d -empty \
  -not -path 'src/content/docs/refget/biocrefgetstore*' -delete 2>/dev/null || true

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
echo "=== Pre-build: Render R vignettes (BiocRefgetStore) ==="
if command -v bulker >/dev/null 2>&1; then
    bulker exec databio/nsheff -- Rscript scripts/render_r_vignettes.R
else
    echo "  SKIP: bulker not available (committed .md outputs remain in place)"
fi

echo ""
echo "=== Pre-build: Fix image paths ==="
python scripts/fix_image_paths.py

echo ""
echo "=== Pre-build complete ==="
