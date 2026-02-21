# Use the dashboard

The refgenie dashboard is a local web interface for browsing your genomes, aliases, assets, and remote assets from subscribed servers. It is distinct from `refgenie serve`, which exposes an API for remote clients.

## Install

The dashboard requires the `dash` extras:

```bash
pip install refgenie1[dash]
```

## Launch the dashboard

```bash
refgenie dash
```

This starts the dashboard on port 8080 and automatically opens your browser. If the page doesn't load immediately, refresh after a moment.

### Custom port

```bash
refgenie dash -p 9090
```

## What the dashboard shows

The dashboard provides a web UI with the following pages:

- **Index page** -- Lists all genomes in your refgenie instance
- **Genome splash page** -- Shows details for a single genome, including its aliases and available assets
- **Asset detail page** -- Shows metadata and file paths for a specific asset
- **Manage page** (`/page/manage`) -- Administration interface for managing your refgenie instance, including remote assets from subscribed servers
