#!/bin/bash
# Local publish for refgenie.org.
#
# Why this exists: the site content under src/content/docs/ is generated at
# build time (it is gitignored), and the BiocRefgetStore R vignettes are rendered
# via `bulker` (scripts/render_r_vignettes.R). GitHub Actions does NOT have
# bulker, so the CI publish (.github/workflows/publish.yaml) SKIPs the R render
# and ships a site missing the BiocRefgetStore pages. Run THIS script locally,
# where bulker is available, to render everything, build the Astro site, and
# deploy dist/ to the gh-pages branch that serves refgenie.org.
#
# Usage:
#   bash scripts/publish.sh
#
# Prerequisites:
#   - node deps installed (npm ci)
#   - Python deps for the prebuild renders (pip install nbconvert griffe refget)
#   - bulker + the databio/nsheff crate (for the R vignettes)
#   - push access to the gh-pages branch
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

if ! command -v bulker >/dev/null 2>&1; then
  echo "ERROR: bulker not found. The BiocRefgetStore R vignettes are rendered via" >&2
  echo "       bulker; without it the R pages would be missing from the published" >&2
  echo "       site. Install bulker (and the databio/nsheff crate), then retry." >&2
  echo "       (This is exactly why we publish locally instead of from CI.)" >&2
  exit 1
fi

echo "=== Generate content + build the site ==="
# npm run build runs the prebuild (scripts/build_docs.sh -> renders notebooks,
# Python scripts, the Python API, and the R vignettes via bulker) and then
# `astro build`, emitting the finished site to dist/.
npm run build

# GitHub Pages runs Jekyll by default, which strips directories beginning with an
# underscore (Astro emits _astro/). .nojekyll disables that so assets are served.
touch dist/.nojekyll

echo ""
echo "=== Deploy dist/ to the gh-pages branch (serves refgenie.org) ==="
# --dotfiles ensures .nojekyll (and any other dotfiles) are published; the
# refgenie.org CNAME is a regular file copied from public/CNAME by Astro.
npx --yes gh-pages \
  --dotfiles \
  --dist dist \
  --branch gh-pages \
  --message "Publish docs ($(git rev-parse --short HEAD))"

echo ""
echo "=== Published. refgenie.org updates once GitHub Pages propagates. ==="
