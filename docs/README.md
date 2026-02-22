<p align="center"><img src="img/refgenie_reloaded.svg" alt="Refgenie: Reloaded"></p>

<h2 align="center">Reference genome management, rebuilt from the ground up</h2>

Refgenie has been completely rewritten with a modern architecture designed for reproducibility, scalability, and GA4GH compatibility.


## Refgenie legacy

<div id="refgenie-stats" style="display:flex; gap:1.5rem; margin:1.5rem 0;">
  <div style="flex:1; text-align:center; background:#f8f9fa; border:1px solid #dee2e6; border-radius:0.75rem; padding:1.5rem;">
    <div id="stat-bytes" style="font-size:2.5rem; font-weight:700; color:#1a73e8;">...</div>
    <div style="font-size:0.85rem; color:#666; margin-top:0.25rem;">TOTAL DATA SERVED</div>
  </div>
  <div style="flex:1; text-align:center; background:#f8f9fa; border:1px solid #dee2e6; border-radius:0.75rem; padding:1.5rem;">
    <div id="stat-requests" style="font-size:2.5rem; font-weight:700; color:#1a73e8;">...</div>
    <div style="font-size:0.85rem; color:#666; margin-top:0.25rem;">TOTAL REQUESTS SERVED</div>
  </div>
</div>

<script>
fetch('https://databio.org/stats/stats/aws/summary.json')
  .then(r => r.json())
  .then(d => {
    document.getElementById('stat-bytes').textContent = (d.BytesDownloaded / 1e12).toFixed(1) + ' TB';
    document.getElementById('stat-requests').textContent = (d.AllRequests / 1e6).toFixed(1) + ' million';
  });
</script>



## What's new

- **Database-backed storage** — SQLite by default, PostgreSQL for scale. No more flat YAML config files.
- **Built-in server** — Serve your assets over HTTP without a separate package.
- **Sequence-derived genome identifiers** — GA4GH-compatible digests replace arbitrary genome names.
- **Remote operation mode** — Use `seekr` to access assets on S3 or other cloud storage.
- **Improved CLI** — Rich terminal output with better feedback and discoverability.

## Quick start

```console
pip install refgenie

refgenie --help
```

## Documentation

Head to the [**Refgenie**](refgenie/README.md) tab for full documentation, including installation, tutorials, and how-to guides.

Looking for the refget Python package? See the [**Refget**](refget/README.md) tab.

!!! note "Upgrading from pre-1.0?"
    Documentation for the original refgenie and refgenie server is available in the [**Legacy**](legacy/README.md) tab.


                                                                                                                                                                                           
  ## Refgenie server usage                                                                                                                                                                       
                                                                                                 