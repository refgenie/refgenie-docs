# Explore a local store in your browser

The [RefgetStore Explorer](https://refgenie.org) is a web app for browsing a store's
sequences, collections, aliases, and [FHR metadata](../reference/refgetstore-format.md).
It runs entirely in the browser — it reads a store's static files directly over HTTP,
with no application server behind it.

The `refget store explore` command lets you point that Explorer at a store on your own
machine. It serves both the store's files and the Explorer web UI from a single local
web server and opens your browser to it:

```console
refget store explore /path/to/refget-store
```

This starts a server on `http://127.0.0.1:8080` and opens the Explorer pointed at your
store. Press `Ctrl-C` to stop it.

## When to use it

Because the Explorer only needs static files, it works against a store anywhere — an S3
bucket, an HTTP server, or a directory on disk. The hosted Explorer at
[refgenie.org](https://refgenie.org) already covers stores reachable from the public
internet. `refget store explore` covers the cases it can't:

- **A store on local disk.** Browsers can't `fetch()` `file://` URLs, so a store in a
  local directory needs a local web server to browse it.
- **A read-only mount**, such as a [CVMFS](https://cernvm.cern.ch/fs/) distribution of a
  reference store on a shared cluster.
- **An air-gapped or offline machine**, where the hosted Explorer is unreachable. The
  command bundles the Explorer web UI, so it needs no internet access.

## Options

| Option | Description |
|--------|-------------|
| `PATH` | Store directory to explore (falls back to your configured store path). |
| `--host` | Interface to bind (default `127.0.0.1`). |
| `--port`, `-P` | Port to serve on (default `8080`; auto-increments if busy). |
| `--no-browser` | Print the URLs instead of opening a browser. |
| `--store-only` | Serve only the store files, skipping the bundled UI — useful when hosting your own front end. |
| `--frontend-dir` | Serve a custom Explorer build from this directory. |

The command exposes read-only `GET`/`HEAD` access to the store's files. To modify a
store, use [`refget store add`, `pull`, and `alias`](../reference/cli.md).

## Serving on a shared server

To let others on your network reach a store hosted on a cluster login node, bind a
public interface and skip opening a local browser:

```console
refget store explore /cvmfs/data.example.org/refget-store --host 0.0.0.0 --no-browser
```

Then share the printed Explorer URL. See
[What is RefgetStore?](../refgetstore-explained.md) for background on the store format
and its local/remote symmetry.
