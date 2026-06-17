#!/usr/bin/env Rscript
# Render BiocRefgetStore (R) package vignettes into the Starlight content tree.
#
# Adapted from mNexus clients/render_docs.R. Knits each vignettes/*.Rmd to a
# Starlight-friendly .md under src/content/docs/refget/biocrefgetstore/, writes
# plot PNGs into public/img/biocrefgetstore/, and post-processes the output so
# Starlight accepts the frontmatter and serves the images.
#
# Run from the refgenie-docs repo root, e.g. via bulker:
#   bulker exec databio/nsheff -- Rscript scripts/render_r_vignettes.R
#
# The package source location is a single variable (env override) so it is
# trivial to repoint once the package is extracted to databio/BiocRefgetStore.

suppressPackageStartupMessages({
  library("knitr")
})

# --- Configuration ----------------------------------------------------------

# Path to the BiocRefgetStore package source. Repoint after extraction to
# databio/BiocRefgetStore. Resolve via env var with a sensible default
# (relative to the refgenie-docs repo root, which must be the CWD).
pkg <- Sys.getenv("BIOCREFGETSTORE_SRC", "../BiocRefgetStore")

out_dir <- "src/content/docs/refget/biocrefgetstore"
# knitr fig.path -> served static assets. Trailing slash matters: knitr
# concatenates fig.path + chunk-label, so this yields
# public/img/biocrefgetstore/<chunk>-1.png
fig_dir <- "public/img/biocrefgetstore/"
# How those PNG paths must look in the final markdown (Starlight strips
# the leading public/ when serving).
served_prefix <- "/img/biocrefgetstore/"

dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(fig_dir, recursive = TRUE, showWarnings = FALSE)

if (!dir.exists(pkg)) {
  stop("Package source not found at '", pkg, "'. Set BIOCREFGETSTORE_SRC.")
}

cat("Rendering BiocRefgetStore vignettes\n")
cat("  package source: ", normalizePath(pkg), "\n", sep = "")
cat("  output dir:     ", out_dir, "\n", sep = "")
cat("  figure dir:     ", fig_dir, "\n", sep = "")

# Load the package from source (no install needed); falls back to library()
# if devtools is unavailable in the runtime.
if (requireNamespace("devtools", quietly = TRUE)) {
  suppressMessages(devtools::load_all(pkg, quiet = TRUE))
} else {
  library("BiocRefgetStore")
}

# --- knitr options ----------------------------------------------------------

knitr::opts_chunk$set(
  results = "hold",
  collapse = TRUE,
  comment = "#>",
  fig.path = fig_dir,    # PNGs land directly under public/img/biocrefgetstore/
  dev = "png"            # force static PNG output; no self-contained HTML widgets
)
knitr::opts_knit$set(base.dir = getwd())

# --- Frontmatter + image-path post-processing -------------------------------

# Build a clean Starlight frontmatter block from the knitted markdown:
#  - keep only `title:` (derive from the Rmd YAML title, or first `# ` heading)
#  - drop `output:` / `vignette:` and any other vignette YAML keys
#  - rewrite knitr image paths from public/img/... to the served /img/... path
postprocess <- function(md_path) {
  lines <- readLines(md_path, warn = FALSE)

  title <- NULL
  body_start <- 1L

  # Detect a leading YAML frontmatter block (--- ... ---).
  if (length(lines) >= 1L && grepl("^---\\s*$", lines[1])) {
    close_idx <- which(grepl("^---\\s*$", lines))[2]
    if (!is.na(close_idx)) {
      yaml_lines <- lines[2:(close_idx - 1L)]
      title_line <- grep("^title:\\s*", yaml_lines, value = TRUE)
      if (length(title_line) > 0) {
        title <- sub("^title:\\s*", "", title_line[1])
        title <- gsub('^"|"$', "", trimws(title))
      }
      body_start <- close_idx + 1L
    }
  }

  body <- lines[body_start:length(lines)]

  # Fall back to first `# ` heading if no title in YAML.
  if (is.null(title) || !nzchar(title)) {
    h <- grep("^#\\s+", body)
    if (length(h) > 0) {
      title <- sub("^#\\s+", "", body[h[1]])
      body <- body[-h[1]]
    } else {
      title <- tools::toTitleCase(gsub("[-_]", " ", tools::file_path_sans_ext(basename(md_path))))
    }
  }
  title <- trimws(title)

  text <- paste(body, collapse = "\n")

  # Rewrite knitr-emitted image paths (public/img/biocrefgetstore/...) to the
  # served URL (/img/biocrefgetstore/...). Handles both markdown ![](...) and
  # any HTML src="..." just in case.
  text <- gsub("public/img/biocrefgetstore/", served_prefix, text, fixed = TRUE)
  # Also handle a possible leading ./ form.
  text <- gsub("(\\./)?public/img/biocrefgetstore/", served_prefix, text)

  # Escape any stray double-quote in the derived title for YAML safety.
  title_yaml <- gsub('"', "'", title)

  out <- paste0("---\ntitle: \"", title_yaml, "\"\n---\n\n",
                sub("^\\n+", "", text), "\n")
  writeLines(out, md_path, useBytes = TRUE)
  invisible(title)
}

# --- Knit loop --------------------------------------------------------------

vig_dir <- file.path(pkg, "vignettes")
vigs <- list.files(vig_dir, pattern = "[.]Rmd$")
if (length(vigs) == 0L) stop("No vignettes found in ", vig_dir)

for (v in vigs) {
  src <- file.path(vig_dir, v)
  dst <- file.path(out_dir, sub("[.]Rmd$", ".md", v))
  cat("\n--- knitting ", v, " -> ", dst, "\n", sep = "")
  knitr::knit(src, dst, quiet = TRUE)
  title <- postprocess(dst)
  cat("    title: ", title, "\n", sep = "")
}

# List emitted figures for verification.
figs <- list.files(fig_dir, pattern = "[.]png$", full.names = FALSE)
cat("\nFigures emitted under ", fig_dir, ":\n", sep = "")
if (length(figs) == 0L) {
  cat("  (none)\n")
} else {
  for (f in figs) cat("  ", f, "\n", sep = "")
}

cat("\nDone rendering ", length(vigs), " vignette(s).\n", sep = "")
