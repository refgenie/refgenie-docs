# Refgenie tutorial

The `Refgenie` class is a key component of the Refgenie package, which is used for managing and organizing reference genome files. It provides a set of methods and functionalities to interact with reference genome assets, and other related resources.

## Purpose of this file

This file serves as a tutorial for using the `Refgenie` Python API. It demonstrates how to set up a temporary directory for storing reference genome assets, configure the `Refgenie` instance, and perform various operations such as listing available assets, retrieving asset information, and managing data channels. 

In order to learn more about any of the contepts indicated in the code, please refer to a specific section of the documentation.

## Installation

Before the package gets released, clone the repository install, for example using `uv`:
  
```bash
git clone <repo_url>
cd refgenie1
uv pip install .
```

## Configuration

First, let's create a temporary directory that will be used to store the refgenie assets.



```python
from pathlib import Path
from rich import print
import os
```

Let's set a temporary directory to store the refgenie assets.


```python
from tempfile import TemporaryDirectory

REFGENIE_CODE_PATH = Path.cwd().parent / "refgenie" 

# set the environment variable
archive_tmp_dir = TemporaryDirectory(prefix="refgenie_archive_demo_").name
os.environ["REFGENIE_GENOME_ARCHIVE_FOLDER"] = archive_tmp_dir
tmp_dir = TemporaryDirectory(prefix="refgenie_demo_").name
os.environ["REFGENIE_GENOME_FOLDER"] = tmp_dir
# set the REFGENIE_DB_CONFIG_PATH to a sqlite config file in the refgenie package
# os.environ["REFGENIE_DB_CONFIG_PATH"] = (REFGENIE_CODE_PATH / "config" / "sqlite_config.yaml").as_posix()

```

Let's inspect the refgenie configuration object.


```python
from refgenie.config import config

print(config)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">RefgenieConfig</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">log_level</span>=<span style="font-weight: bold">&lt;</span><span style="color: #ff00ff; text-decoration-color: #ff00ff; font-weight: bold">LogLevel.INFO:</span><span style="color: #000000; text-decoration-color: #000000"> </span><span style="color: #008000; text-decoration-color: #008000">'INFO'</span><span style="font-weight: bold">&gt;</span>,
    <span style="color: #808000; text-decoration-color: #808000">genome_folder</span>=<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">PosixPath</span><span style="font-weight: bold">(</span><span style="color: #008000; text-decoration-color: #008000">'/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l'</span><span style="font-weight: bold">)</span>,
    <span style="color: #808000; text-decoration-color: #808000">genome_archive_folder</span>=<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">PosixPath</span><span style="font-weight: bold">(</span><span style="color: #008000; text-decoration-color: #008000">'/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_archive_demo_mthufo3</span>
<span style="color: #008000; text-decoration-color: #008000">u'</span><span style="font-weight: bold">)</span>,
    <span style="color: #808000; text-decoration-color: #808000">database_config_path</span>=<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">PosixPath</span><span style="font-weight: bold">(</span><span style="color: #008000; text-decoration-color: #008000">'/Users/stolarczyk/.refgenie/refgenie_db_config.yaml'</span><span style="font-weight: bold">)</span>
<span style="font-weight: bold">)</span>
</pre>



### Database backend

As you can see, refgenie configuration points to a database configuration file, as by default refgenie is backed by a SQLite database.

Let's inspect the refgenie database configuration file.


```python
%cat {config.database_config_path}
```

    type: sqlite
    path: /Users/stolarczyk/.refgenie/refgenie


Make sure the directory where the SQLite database file is stored exists, and create it if it doesn't.


```python
!refgenie1 purge --force
!rm -rf ~/refgenie_db
!mkdir -p ~/refgenie_db
```

In practice, you don't even need to create the configuration file manually, as refgenie ships with a default configuration file that is used if no configuration file is provided. Just as we've seen above.

For production deployments you may want to use a different database backend, such as MySQL or PostgreSQL. In this case, you can provide the database configuration file path by setting `REFGENIE_DB_CONFIG_PATH` environment variable, or even set/override the database engine using `database_engine` in the `Refgenie` constructor. The object must be a `sqlalchemy.engine.Engine` object.



### Refgenieserver client

Similarly, refgenie ships with a Refgenieserver client, which is used by default to retrieve remote genome assets and does not need to be replaced in majority of use cases. However, you can provide a custom URL-client mapping to `Refgenie` constructor, by setting the `server_client_mapping` argument. Please note that, the clients need to follow a specific interface, defined in `refgenie.server.ServerClient` protocol. More details below.


```python
from refgenie.server.models import ServerClient
from rich import inspect

inspect(
    ServerClient,
    methods=True,
    docs=True,
    help=True,
    title="ServerClient Protocol structure",
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">╭──────────────────────────────────────── ServerClient Protocol structure ────────────────────────────────────────╮</span>
<span style="color: #000080; text-decoration-color: #000080">│</span> <span style="color: #00ffff; text-decoration-color: #00ffff; font-style: italic">class </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">ServerClient</span><span style="font-weight: bold">(</span>*args, **kwargs<span style="font-weight: bold">)</span>:                                                                            <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                                                                                                                 <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span> <span style="color: #008080; text-decoration-color: #008080">Protocol for the server client.</span>                                                                                 <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                                                                                                                 <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>             <span style="color: #808000; text-decoration-color: #808000; font-style: italic">server_url</span> = <span style="font-weight: bold">&lt;</span><span style="color: #ff00ff; text-decoration-color: #ff00ff; font-weight: bold">property</span><span style="color: #000000; text-decoration-color: #000000"> object at </span><span style="color: #008080; text-decoration-color: #008080; font-weight: bold">0x111798e00</span><span style="font-weight: bold">&gt;</span>                                                       <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span> <span style="color: #808000; text-decoration-color: #808000; font-style: italic">download_with_progress</span> = <span style="color: #00ffff; text-decoration-color: #00ffff; font-style: italic">def </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">download_with_progress</span><span style="font-weight: bold">(</span>self, operation_id: str, output_path: pathlib.Path, params: <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                          Optional<span style="font-weight: bold">[</span>Dict<span style="font-weight: bold">]</span> = <span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>, url_format_params: Optional<span style="font-weight: bold">[</span>Dict<span style="font-weight: bold">[</span>str, str<span style="font-weight: bold">]]</span> = <span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>, name:       <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                          Optional<span style="font-weight: bold">[</span>str<span style="font-weight: bold">]</span> = <span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span><span style="font-weight: bold">)</span> -&gt; pathlib.Path: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Download asset at given URL to given filepath, </span> <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">show progress along the way.</span>                                                           <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                    <span style="color: #808000; text-decoration-color: #808000; font-style: italic">get</span> = <span style="color: #00ffff; text-decoration-color: #00ffff; font-style: italic">def </span><span style="color: #800000; text-decoration-color: #800000; font-weight: bold">get</span><span style="font-weight: bold">(</span>self, operation_id: str, params: Optional<span style="font-weight: bold">[</span>Dict<span style="font-weight: bold">]</span> = <span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>, url_format_params:     <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                          Optional<span style="font-weight: bold">[</span>Dict<span style="font-weight: bold">[</span>str, str<span style="font-weight: bold">]]</span> = <span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span><span style="font-weight: bold">)</span> -&gt; Dict: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">Send a GET request to the specified </span>         <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">│</span>                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">operation ID.</span>                                                                          <span style="color: #000080; text-decoration-color: #000080">│</span>
<span style="color: #000080; text-decoration-color: #000080">╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯</span>
</pre>



First, let's import the `Refgenie` class from the `refgenie` package.



```python
from refgenie import Refgenie

refgenie = Refgenie(suppress_migrations=True)
```

Let's ensure we start with a clean slate by removing any existing refgenie metadata and initializing a new refgenie instance.



```python
refgenie.init()  # initialize new refgenie instance
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Initialized refgenie backend: <span style="color: #008000; text-decoration-color: #008000">'sqlite:////Users/stolarczyk/.refgenie/refgenie'</span>             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#392" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">392</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'fasta'</span> asset class                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'fasta'</span> recipe                                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>



Let's subscribe to the default refgenie server. This method will reach out to the server at the provided URL and query the OpenAPI specification to determine whether ther server is refgenie-compatible. If it is, the server will be added to the list of subscribed servers.

Note: there's currently no public compatible refgenieserver instance deployed, so the following code snippets use a local refgenieserver instance serving the latest API.



```python
refgenie.configuration.subscribe("http://localhost:8000")
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Subscribed to servers: <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000</span>                                                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/configuration/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/configuration/manager.py#42" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">42</span></a>
</pre>



And that's it! We have now configured a refgenie instance and subscribed to a refgenie-compatible server. We can now start using the refgenie instance to manage reference genome assets.

### Pull an asset

Let's initialize a new genome by pulling an asset of fasta class. This will create a new directory in the `data` subdirectory of the `genome_folder` and mirror it in the `alias` directory with symbolic links, rather than copies of the files.



```python
refgenie.pull(alias_name="rCRSd-1", asset_group_name="fasta")
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/openapi.json</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>                     <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Connected to server: <span style="color: #808000; text-decoration-color: #808000">title</span>=<span style="color: #008000; text-decoration-color: #008000">'Refgenieserver REST API'</span> <span style="color: #808000; text-decoration-color: #808000">version</span>=<span style="color: #008000; text-decoration-color: #008000">'1.0.0'</span> <span style="color: #808000; text-decoration-color: #808000">description</span>=<span style="color: #008000; text-decoration-color: #008000">'a web </span>      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/server/client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/server/client.py#32" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">32</span></a>
         <span style="color: #008000; text-decoration-color: #008000">interface and RESTful API for reference genome assets'</span>                                        <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #808000; text-decoration-color: #808000">WARNING </span> No local digest for genome alias: rCRSd-<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>. Setting genome identity with server:           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3124" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3124</span></a>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000</span>                                                                     <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Setting <span style="color: #008000; text-decoration-color: #008000">'rCRSd-1'</span> identity with server: <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000</span>                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1070" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1070</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/aliases/rCRSd-1</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>               <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/genomes/ZtAkf32sCUjeSl0KxVA5DVevklHDazQM</span>        <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>                                                                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Determined digest for rCRSd-<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>: ZtAkf32sCUjeSl0KxVA5DVevklHDazQM                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1136" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1136</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span>                                                                          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/asset_groups?genome_digest=ZtAkf32sCUjeSl0KxVA5DVevklHDazQM&amp;asset</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">_group_name=fasta</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>                                                        <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/assets?asset_group_id=1&amp;name=</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span> <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span>                                                                          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/archives?asset_digest=8ccce3f01185ef75c8dabeb9e03f8822</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 </span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #008000; text-decoration-color: #008000">200 OK"</span>                                                                                    <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span>                                                                          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/relationships/8ccce3f01185ef75c8dabeb9e03f8822?expand=true</span>        <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>                                                                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/rich/live.py:231: UserWarning: install 
"ipywidgets" for Jupyter support
  warnings.warn('install "ipywidgets" for Jupyter support')
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span>                                                                          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/archives/a769250cd482fffc8bbabf8f00821d24/download</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 </span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #008000; text-decoration-color: #008000">OK"</span>                                                                                        <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Extracting asset tarball:                                                                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3293" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3293</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/ZtAkf32sCUje</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #800080; text-decoration-color: #800080">Sl0KxVA5DVevklHDazQM/fasta/samtools-1.21/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">fasta__samtools-1.21.tgz</span>                         <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">http://localhost:8000/v4/genomes/ZtAkf32sCUjeSl0KxVA5DVevklHDazQM</span>        <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
         <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>                                                                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Initializing genome from FASTA file:                                                      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1238" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1238</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/ZtAkf32sCUje</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #800080; text-decoration-color: #800080">Sl0KxVA5DVevklHDazQM/fasta/samtools-1.21/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">ZtAkf32sCUjeSl0KxVA5DVevklHDazQM.fa</span>              <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> SeqCol: <span style="color: #808000; text-decoration-color: #808000">digest</span>=<span style="color: #008000; text-decoration-color: #008000">'ZtAkf32sCUjeSl0KxVA5DVevklHDazQM'</span>                                            <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">agents.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py#242" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">242</span></a>
         <span style="color: #808000; text-decoration-color: #808000">sorted_name_length_pairs_digest</span>=<span style="color: #008000; text-decoration-color: #008000">'cqchGk0CDISu293ibJ6WhCZ4T4scXgZW'</span>                           <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Initialized genome: ZtAkf32sCUjeSl0KxVA5DVevklHDazQM <span style="font-weight: bold">(</span>Yeast genome <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span><span style="font-weight: bold">)</span>                     <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1272" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1272</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added: <span style="color: #008000; text-decoration-color: #008000">'rCRSd-1/fasta:samtools-1.21'</span>                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#773" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">773</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created alias directories:                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3515" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3515</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/rCRSd-1/fas</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #800080; text-decoration-color: #800080">ta/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">samtools-1.21</span>                                                                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Set default asset: <span style="color: #008000; text-decoration-color: #008000">'ZtAkf32sCUjeSl0KxVA5DVevklHDazQM/fasta:samtools-1.21'</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1640" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1640</span></a>
</pre>






    Asset(name='samtools-1.21', description=None, size=34082, updated_at=datetime.datetime(2025, 7, 6, 18, 28, 50, 885001), path='data/ZtAkf32sCUjeSl0KxVA5DVevklHDazQM/fasta/samtools-1.21', digest='8ccce3f01185ef75c8dabeb9e03f8822', recipe_id=None, asset_group_id=1, created_at=datetime.datetime(2025, 7, 6, 18, 28, 50, 885007))



As you can see above, the genome has been initialized and `fasta` asset was pulled. Let's inspect the initialized genome.



```python
print(refgenie.genomes_table())
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                       Genomes                       </span>
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Digest                           </span>┃<span style="font-weight: bold"> Description    </span>┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ ZtAkf32sCUjeSl0KxVA5DVevklHDazQM │ Yeast genome 1 │
└──────────────────────────────────┴────────────────┘
</pre>



Now, that a `fasta` asset has been built for the `dm6` genome, let's add some custom asset classes and recipes to build an asset based on that.

### Add `bowtie2_index` asset class and recipe

By supplying a URL (`str` object) rather than a local path (`pathlib.Path` object), refgenie will grab the remote file and register it as if it was a local file.



```python
refgenie.asset_class.add(
    "https://github.com/refgenie/recipes/raw/refgenie1/asset_classes/bowtie2_index_asset_class.yaml"
)
refgenie.recipe.add(
    "https://github.com/refgenie/recipes/raw/refgenie1/recipes/bowtie2_index_asset_recipe.yaml"
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bowtie2_index'</span> asset class                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bowtie2_index'</span> recipe                                                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>






    Recipe(id=2, name='bowtie2_index', version='0.0.1', description='Genome index for bowtie2, produced with bowtie2-build', output_asset_class_id=2, command_templates=['bowtie2-build --threads {{values.params["threads"]}} {{values.genome_folder}}/{{values.assets["fasta"].seek_keys_dict["fasta"]}} {{values.output_folder}}/{{values.genome_digest}}'], input_params={'threads': {'description': 'Number of threads to use', 'default': 1}}, input_files=None, input_assets={'fasta': {'asset_class': 'fasta', 'description': 'fasta asset for genome', 'default': 'fasta'}}, docker_image='docker.io/databio/refgenie', custom_properties={'version': "bowtie2-build --version | awk 'NR==1{print $3}'"}, default_asset='{{values.custom_properties.version}}', updated_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 196749), created_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 196751))



Let's verify that it worked by listing the available asset classes and recipes:



```python
from rich import print

print(refgenie.recipe.table())
print(refgenie.asset_class.table())
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                                      Recipes                                                      </span>
┏━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold">               </span>┃<span style="font-weight: bold">         </span>┃<span style="font-weight: bold"> Output asset    </span>┃<span style="font-weight: bold"> Input asset    </span>┃<span style="font-weight: bold">                 </span>┃<span style="font-weight: bold">                </span>┃<span style="font-weight: bold">                 </span>┃
┃<span style="font-weight: bold"> Name          </span>┃<span style="font-weight: bold"> Version </span>┃<span style="font-weight: bold"> class           </span>┃<span style="font-weight: bold"> classes        </span>┃<span style="font-weight: bold"> Input files     </span>┃<span style="font-weight: bold"> Input params   </span>┃<span style="font-weight: bold"> Docker image    </span>┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ fasta         │ 0.0.1   │ fasta           │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">None</span>           │ • fasta <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(DNA </span>   │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">None</span>           │ docker.io/data… │
│               │         │                 │                │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">sequences in </span>   │                │                 │
│               │         │                 │                │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">the FASTA </span>      │                │                 │
│               │         │                 │                │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">format) </span>        │                │                 │
│               │         │                 │                │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">default=None</span>    │                │                 │
├───────────────┼─────────┼─────────────────┼────────────────┼─────────────────┼────────────────┼─────────────────┤
│ bowtie2_index │ 0.0.1   │ bowtie2_index   │ • fasta <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(fasta</span> │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">None</span>            │ • threads      │ docker.io/data… │
│               │         │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">asset for </span>     │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">(Number of </span>    │                 │
│               │         │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">genome) </span>       │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">threads to </span>    │                 │
│               │         │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">default=fasta</span>  │                 │ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">use) default=1</span> │                 │
└───────────────┴─────────┴─────────────────┴────────────────┴─────────────────┴────────────────┴─────────────────┘
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                                   Asset Classes                                                   </span>
┏━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Name          </span>┃<span style="font-weight: bold"> Version </span>┃<span style="font-weight: bold"> Seek keys               </span>┃<span style="font-weight: bold"> Description                                                 </span>┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ fasta         │ 0.0.1   │ fasta, fai, chrom_sizes │ Sequences in the FASTA format, indexed FASTA (produced with │
│               │         │                         │ samtools index) and chromosome sizes file                   │
├───────────────┼─────────┼─────────────────────────┼─────────────────────────────────────────────────────────────┤
│ bowtie2_index │ 0.0.1   │ bowtie2_index           │ Genome index for bowtie2, produced with bowtie2-build       │
└───────────────┴─────────┴─────────────────────────┴─────────────────────────────────────────────────────────────┘
</pre>



## Build a `fasta` asset



```python
from refgenie import BuildParams

refgenie.build_asset(
    recipe_name="fasta",
    genome_name="t7",
    asset_group_name="fasta",
    params=BuildParams(
        files={"fasta": REFGENIE_CODE_PATH.parent / "tests/data/t7.fa"}
    ),
    genome_description="Genome of T7 phage",
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Initializing genome from FASTA file: <span style="color: #800080; text-decoration-color: #800080">/Users/stolarczyk/code/refgenie1/tests/data/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">t7.fa</span>    <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1238" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1238</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> SeqCol: <span style="color: #808000; text-decoration-color: #808000">digest</span>=<span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB'</span>                                            <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">agents.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py#242" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">242</span></a>
         <span style="color: #808000; text-decoration-color: #808000">sorted_name_length_pairs_digest</span>=<span style="color: #008000; text-decoration-color: #008000">'0R51wR5l44VrpWoLqmcfyYcrLLba--uY'</span>                           <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Initialized genome: kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB <span style="font-weight: bold">(</span>Genome of T7 phage<span style="font-weight: bold">)</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1272" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1272</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Building <span style="color: #008000; text-decoration-color: #008000">'t7/fasta'</span> using recipe <span style="color: #008000; text-decoration-color: #008000">'fasta (v0.0.1)'</span>                                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2499" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2499</span></a>
</pre>



    Using default schema: /Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/pipestat_output_schema.yaml



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Could not locate config file.                                                         <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/yacman/yacman_future.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">yacman_future.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/yacman/yacman_future.py#563" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">563</span></a>
</pre>



    No pipestat output schema was supplied to PipestatManager.
    Initializing results file '/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/stats.yaml'



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> File does not exist, but create_file is true. Creating<span style="color: #808000; text-decoration-color: #808000">...</span>                              <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ubiquerg/file_locking.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">file_locking.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ubiquerg/file_locking.py#251" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">251</span></a>
</pre>



    Warning: You're running an interactive python session. This works, but pypiper cannot tee the output, so results are only logged to screen.
    ### Pipeline run code and environment:
    
    *          Command: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ipykernel_launcher.py --f=/Users/stolarczyk/Library/Jupyter/runtime/kernel-v3b4e8f4927474eb39f1b6ad0ce5ad7909ee3e90d0.json`
    *     Compute host: `michals-macbook-pro-2.home`
    *      Working dir: `/Users/stolarczyk/code/refgenie1/docs`
    *        Outfolder: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/`
    *         Log file: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/refgenie_t7_fasta_samtools-1.21_log.md`
    *       Start time:  (07-06 20:28:51) elapsed: 0.0 _TIME_
    
    ### Version log:
    
    *   Python version: `3.12.7`
    *      Pypiper dir: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/pypiper`
    *  Pypiper version: `0.14.3`
    *     Pypiper hash: `f0996bac2e9d7f66d1378360de985188a24015f7`
    *   Pypiper branch: `* master`
    *     Pypiper date: `2025-07-06 13:49:47 +0200`
    *     Pypiper diff: `9 files changed, 2323 insertions(+), 1945 deletions(-)`
    *     Pipeline dir: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages`
    * Pipeline version: 
    *    Pipeline hash: `f0996bac2e9d7f66d1378360de985188a24015f7`
    *  Pipeline branch: `* master`
    *    Pipeline date: `2025-07-06 13:49:47 +0200`
    *    Pipeline diff: `9 files changed, 2323 insertions(+), 1945 deletions(-)`
    
    ### Arguments passed to pipeline:
    
    
    ### Initialized Pipestat Object:
    
    * PipestatManager (refgenie_t7_fasta_samtools-1.21)
    * Backend: File
    *  - results: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/stats.yaml
    *  - status: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build
    * Multiple Pipelines Allowed: False
    * Pipeline name: refgenie_t7_fasta_samtools-1.21
    * Pipeline type: sample
    * Status Schema key: None
    * Results formatter: default_formatter
    * Results schema source: None
    * Status schema source: None
    * Records count: 2
    * Sample name: DEFAULT_SAMPLE_NAME
    
    
    ----------------------------------------
    
    Target to produce: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/t7_fasta__samtools-1.21.flag`  
    
    > `cp /Users/stolarczyk/code/refgenie1/tests/data/t7.fa /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa.gz` (247)
    <pre>
    PID still exists but it's a zombie (pid=247)
    Warning: couldn't add memory use for process: 247
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0GB.  
      PID: 247;	Command: cp;	Return code: 0;	Memory used: 0GB
    
    
    > `if (file /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa.gz | grep -q compressed ) ; then gzip -df /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa.gz ; else mv /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa.gz /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa ; fi` (248)
    <pre>
    PID still exists but it's a zombie (pid=248)
    Warning: couldn't add memory use for process: 248
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.002GB.  
      PID: 248;	Command: if;	Return code: 0;	Memory used: 0.002GB
    
    
    > `samtools faidx /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa` (253)
    <pre>
    PID still exists but it's a zombie (pid=253)
    Warning: couldn't add memory use for process: 253
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.002GB.  
      PID: 253;	Command: samtools;	Return code: 0;	Memory used: 0GB
    
    
    > `cut -f 1,2 /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa.fai > /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.chrom.sizes` (254)
    <pre>
    PID still exists but it's a zombie (pid=254)
    Warning: couldn't add memory use for process: 254
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.002GB.  
      PID: 254;	Command: cut;	Return code: 0;	Memory used: 0GB
    
    
    > `touch /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/_refgenie_build/t7_fasta__samtools-1.21.flag` (256)
    <pre>
    PID still exists but it's a zombie (pid=256)
    Warning: couldn't add memory use for process: 256
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.002GB.  
      PID: 256;	Command: touch;	Return code: 0;	Memory used: 0GB
    
    
    ### Pipeline completed. Epilogue
    *        Elapsed time (this run):  0:00:00
    *  Total elapsed time (all runs):  0:00:00
    *         Peak memory (this run):  0.0017 GB
    *        Pipeline completed time: 2025-07-06 20:28:51



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Asset <span style="color: #008000; text-decoration-color: #008000">'t7/fasta:samtools-1.21'</span> build succeeded                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2602" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2602</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added: <span style="color: #008000; text-decoration-color: #008000">'t7/fasta:samtools-1.21'</span>                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#773" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">773</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created alias directories:                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3515" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3515</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/t7/fasta/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">sa</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #ff00ff; text-decoration-color: #ff00ff">mtools-1.21</span>                                                                               <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Set default asset: <span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta:samtools-1.21'</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1640" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1640</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added asset: kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta:samtools-<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1.21</span>                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2618" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2618</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Updated parents of <span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta:samtools-1.21'</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2856" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2856</span></a>
</pre>






    Asset(name='samtools-1.21', description='DNA sequences in the FASTA format, indexed FASTA (produced with samtools index), chromosome sizes file and FASTA dict (produced with samtools dict)', size=42981, updated_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 515997), path='data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21', digest='51a58ef25e4f1d7e76f226fd5655754f', recipe_id=1, asset_group_id=2, created_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 516002))



### Build a `bowtie2_index` asset

The `bowtie2_index` asset class and recipe have been added successfully. Let's build the `bowtie2_index` asset for the `dm6` genome.



```python
from refgenie.models import BuildParams

refgenie.build_asset(
    recipe_name="bowtie2_index",
    genome_name="t7",
    asset_group_name="bowtie2_index",
    params=BuildParams(params={"threads": 8}),
    archive=True,  # archive the asset right after building
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Building <span style="color: #008000; text-decoration-color: #008000">'t7/bowtie2_index'</span> using recipe <span style="color: #008000; text-decoration-color: #008000">'bowtie2_index (v0.0.1)'</span>                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2499" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2499</span></a>
</pre>



    Using default schema: /Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/pipestat_output_schema.yaml



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Could not locate config file.                                                         <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/yacman/yacman_future.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">yacman_future.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/yacman/yacman_future.py#563" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">563</span></a>
</pre>



    No pipestat output schema was supplied to PipestatManager.
    Initializing results file '/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/stats.yaml'



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> File does not exist, but create_file is true. Creating<span style="color: #808000; text-decoration-color: #808000">...</span>                              <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ubiquerg/file_locking.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">file_locking.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ubiquerg/file_locking.py#251" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">251</span></a>
</pre>



    Warning: You're running an interactive python session. This works, but pypiper cannot tee the output, so results are only logged to screen.
    ### Pipeline run code and environment:
    
    *          Command: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/ipykernel_launcher.py --f=/Users/stolarczyk/Library/Jupyter/runtime/kernel-v3b4e8f4927474eb39f1b6ad0ce5ad7909ee3e90d0.json`
    *     Compute host: `michals-macbook-pro-2.home`
    *      Working dir: `/Users/stolarczyk/code/refgenie1/docs`
    *        Outfolder: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/`
    *         Log file: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/refgenie_t7_bowtie2_index_2.5.3_log.md`
    *       Start time:  (07-06 20:28:51) elapsed: 0.0 _TIME_
    
    ### Version log:
    
    *   Python version: `3.12.7`
    *      Pypiper dir: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/pypiper`
    *  Pypiper version: `0.14.3`
    *     Pypiper hash: `f0996bac2e9d7f66d1378360de985188a24015f7`
    *   Pypiper branch: `* master`
    *     Pypiper date: `2025-07-06 13:49:47 +0200`
    *     Pypiper diff: `9 files changed, 2323 insertions(+), 1945 deletions(-)`
    *     Pipeline dir: `/Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages`
    * Pipeline version: 
    *    Pipeline hash: `f0996bac2e9d7f66d1378360de985188a24015f7`
    *  Pipeline branch: `* master`
    *    Pipeline date: `2025-07-06 13:49:47 +0200`
    *    Pipeline diff: `9 files changed, 2323 insertions(+), 1945 deletions(-)`
    
    ### Arguments passed to pipeline:
    
    
    ### Initialized Pipestat Object:
    
    * PipestatManager (refgenie_t7_bowtie2_index_2.5.3)
    * Backend: File
    *  - results: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/stats.yaml
    *  - status: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build
    * Multiple Pipelines Allowed: False
    * Pipeline name: refgenie_t7_bowtie2_index_2.5.3
    * Pipeline type: sample
    * Status Schema key: None
    * Results formatter: default_formatter
    * Results schema source: None
    * Status schema source: None
    * Records count: 2
    * Sample name: DEFAULT_SAMPLE_NAME
    
    
    ----------------------------------------
    
    Target to produce: `/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/t7_bowtie2_index__2.5.3.flag`  
    
    > `bowtie2-build --threads 8 /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB` (315)
    <pre>


    Settings:
      Output files: "/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.*.bt2"
      Line rate: 6 (line is 64 bytes)
      Lines per side: 1 (side is 64 bytes)
      Offset rate: 4 (one in 16)
      FTable chars: 10
      Strings: unpacked
      Max bucket size: default
      Max bucket size, sqrt multiplier: default
      Max bucket size, len divisor: 32
      Difference-cover sample period: 1024
      Endianness: little
      Actual local endianness: little
      Sanity checking: disabled
      Assertions: disabled
      Random seed: 0
      Sizeofs: void*:8, int:4, long:8, size_t:8
    Input files DNA, FASTA:
      /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta/samtools-1.21/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa
    Reading reference sizes
      Time reading reference sizes: 00:00:00
    Calculating joined length
    Writing header
    Reserving space for joined string
    Joining reference sequences
      Time to join reference sequences: 00:00:00
    bmax according to bmaxDivN setting: 1248
    Using parameters --bmax 936 --dcv 1024
      Doing ahead-of-time memory usage test
      Passed!  Constructing with these parameters: --bmax 936 --dcv 1024
    Constructing suffix-array element generator
    Building DifferenceCoverSample
      Building sPrime
      Building sPrimeOrder
      V-Sorting samples
      V-Sorting samples time: 00:00:00
      Allocating rank array
      Ranking v-sort output
      Ranking v-sort output time: 00:00:00
      Invoking Larsson-Sadakane on ranks
      Invoking Larsson-Sadakane on ranks time: 00:00:00
      Sanity-checking and returning
    Building samples
    Reserving space for 86 sample suffixes
    Generating random suffixes
    QSorting 86 sample offsets, eliminating duplicates
    QSorting sample offsets, eliminating duplicates time: 00:00:00
    Multikey QSorting 86 samples
      (Using difference cover)
      Multikey QSorting samples time: 00:00:00
    Calculating bucket sizes
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 13, merged 35; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 7, merged 7; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 2, merged 4; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Avg bucket size: 653.721 (target: 935)
    Converting suffix-array elements to index image
    Allocating ftab, absorbFtab
    Entering Ebwt loop
    Getting block 1 of 61
      Reserving size (936) for bucket 1
    Getting block 2 of 61
      Calculating Z arrays for bucket 1
      Reserving size (936) for bucket 2
    Getting block 3 of 61
      Entering block accumulator loop for bucket 1:
    Getting block 4 of 61
    Getting block 5 of 61
      Calculating Z arrays for bucket 2
      Reserving size (936) for bucket 3
    Getting block 6 of 61
    Getting block 7 of 61
      Reserving size (936) for bucket 4
      Reserving size (936) for bucket 5
      Calculating Z arrays for bucket 3
      Entering block accumulator loop for bucket 2:
      Reserving size (936) for bucket 6
      Reserving size (936) for bucket 7
      Calculating Z arrays for bucket 4
      bucket 1: 10%
      Calculating Z arrays for bucket 5
      Entering block accumulator loop for bucket 3:
      Calculating Z arrays for bucket 6
      Calculating Z arrays for bucket 7
      Entering block accumulator loop for bucket 4:
      Entering block accumulator loop for bucket 5:
      bucket 2: 10%
      bucket 1: 20%
      Entering block accumulator loop for bucket 6:
      Entering block accumulator loop for bucket 7:
      bucket 3: 10%
      bucket 2: 20%
      bucket 1: 30%
      bucket 4: 10%
      bucket 5: 10%
      bucket 3: 20%
      bucket 6: 10%
      bucket 2: 30%
      bucket 1: 40%
      bucket 7: 10%
      bucket 2: 40%
      bucket 1: 50%
      bucket 6: 20%
      bucket 4: 20%
      bucket 5: 20%
      bucket 2: 50%
      bucket 1: 60%
      bucket 3: 30%
      bucket 6: 30%
      bucket 2: 60%
      bucket 1: 70%
      bucket 6: 40%
      bucket 7: 20%
      bucket 2: 70%
      bucket 4: 30%
      bucket 1: 80%
      bucket 6: 50%
      bucket 5: 30%
      bucket 2: 80%
      bucket 3: 40%
      bucket 4: 40%
      bucket 7: 30%
      bucket 1: 90%
      bucket 6: 60%
      bucket 5: 40%
      bucket 2: 90%
      bucket 3: 50%
      bucket 4: 50%
      bucket 7: 40%
      bucket 6: 70%
      bucket 1: 100%
      bucket 5: 50%
      Sorting block of length 878 for bucket 1
      (Using difference cover)
      bucket 2: 100%
      bucket 3: 60%
      bucket 4: 60%
      bucket 7: 50%
      Sorting block of length 639 for bucket 2
      (Using difference cover)
      bucket 6: 80%
      bucket 5: 60%
      bucket 3: 70%
      bucket 4: 70%
      bucket 6: 90%
      bucket 7: 60%
      bucket 5: 70%
      bucket 3: 80%
      Sorting block time: 00:00:00
    Returning block of 879 for bucket 1
      bucket 4: 80%
      bucket 5: 80%
      Sorting block time: 00:00:00
      bucket 7: 70%
      bucket 6: 100%
    Returning block of 640 for bucket 2
      bucket 3: 90%
      Sorting block of length 596 for bucket 6
      (Using difference cover)
      bucket 4: 90%
      bucket 7: 80%
      bucket 5: 90%
      bucket 3: 100%
      bucket 4: 100%
      Sorting block of length 516 for bucket 3
      (Using difference cover)
      bucket 7: 90%
      Sorting block of length 552 for bucket 4
      (Using difference cover)
      bucket 5: 100%
      Sorting block of length 395 for bucket 5
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 597 for bucket 6
      Sorting block time: 00:00:00
    Returning block of 517 for bucket 3
      bucket 7: 100%
      Sorting block time: 00:00:00
      Sorting block of length 709 for bucket 7
      (Using difference cover)
    Returning block of 553 for bucket 4
    Getting block 8 of 61
      Reserving size (936) for bucket 8
      Calculating Z arrays for bucket 8
      Sorting block time: 00:00:00
    Returning block of 396 for bucket 5
      Entering block accumulator loop for bucket 8:
      bucket 8: 10%
      bucket 8: 20%
    Getting block 9 of 61
      Reserving size (936) for bucket 9
      Calculating Z arrays for bucket 9
      Sorting block time: 00:00:00
    Returning block of 710 for bucket 7
      bucket 8: 30%
      Entering block accumulator loop for bucket 9:
    Getting block 10 of 61
      Reserving size (936) for bucket 10
    Getting block 11 of 61
      bucket 8: 40%
      bucket 9: 10%
      Calculating Z arrays for bucket 10
    Getting block 12 of 61
      Reserving size (936) for bucket 11
    Getting block 13 of 61
      bucket 8: 50%
      bucket 9: 20%
      Reserving size (936) for bucket 12
      Entering block accumulator loop for bucket 10:
      Calculating Z arrays for bucket 11
    Getting block 14 of 61
      Reserving size (936) for bucket 13
      bucket 8: 60%
      Calculating Z arrays for bucket 12
      bucket 9: 30%
      Reserving size (936) for bucket 14
      Entering block accumulator loop for bucket 11:
      Calculating Z arrays for bucket 13
      Entering block accumulator loop for bucket 12:
      bucket 8: 70%
      bucket 10: 10%
      Calculating Z arrays for bucket 14
      bucket 9: 40%
      Entering block accumulator loop for bucket 13:
      Entering block accumulator loop for bucket 14:
      bucket 10: 20%
      bucket 8: 80%
      bucket 13: 10%
      bucket 11: 10%
      bucket 11: 20%
      bucket 13: 20%
      bucket 12: 10%
      bucket 8: 90%
      bucket 9: 50%
      bucket 10: 30%
      bucket 14: 10%
      bucket 11: 30%
      bucket 13: 30%
      bucket 11: 40%
      bucket 13: 40%
      bucket 8: 100%
      Sorting block of length 598 for bucket 8
      (Using difference cover)
      bucket 12: 20%
      bucket 14: 20%
      bucket 11: 50%
      bucket 9: 60%
      bucket 13: 50%
      bucket 12: 30%
      Sorting block time: 00:00:00
      bucket 10: 40%
      bucket 14: 30%
    Returning block of 599 for bucket 8
      bucket 12: 40%
      bucket 13: 60%
      bucket 11: 60%
      bucket 9: 70%
      bucket 14: 40%
      bucket 10: 50%
      bucket 9: 80%
    Getting block 15 of 61
      bucket 12: 50%
      Reserving size (936) for bucket 15
      bucket 9: 90%
      bucket 11: 70%
      Calculating Z arrays for bucket 15
      bucket 13: 70%
      bucket 10: 60%
      bucket 14: 50%
      Entering block accumulator loop for bucket 15:
      bucket 9: 100%
      Sorting block of length 581 for bucket 9
      (Using difference cover)
      bucket 14: 60%
      bucket 11: 80%
      bucket 13: 80%
      bucket 10: 70%
      bucket 12: 60%
      bucket 15: 10%
      Sorting block time: 00:00:00
    Returning block of 582 for bucket 9
      bucket 12: 70%
      bucket 13: 90%
      bucket 11: 90%
      bucket 12: 80%
      bucket 14: 70%
      bucket 10: 80%
      bucket 15: 20%
      bucket 12: 90%
    Getting block 16 of 61
      Reserving size (936) for bucket 16
      Calculating Z arrays for bucket 16
      bucket 13: 100%
      Entering block accumulator loop for bucket 16:
      bucket 12: 100%
      bucket 10: 90%
      Sorting block of length 595 for bucket 13
      (Using difference cover)
      bucket 11: 100%
      bucket 14: 80%
      Sorting block of length 686 for bucket 12
      (Using difference cover)
      bucket 15: 30%
      Sorting block of length 457 for bucket 11
      (Using difference cover)
      bucket 10: 100%
      bucket 16: 10%
      Sorting block time: 00:00:00
      Sorting block time: 00:00:00
      bucket 15: 40%
      bucket 14: 90%
      Sorting block of length 703 for bucket 10
      (Using difference cover)
    Returning block of 596 for bucket 13
      Sorting block time: 00:00:00
    Returning block of 687 for bucket 12
      bucket 14: 100%
      bucket 16: 20%
      Sorting block time: 00:00:00
    Returning block of 704 for bucket 10
      bucket 15: 50%
      Sorting block of length 402 for bucket 14
      (Using difference cover)
    Returning block of 458 for bucket 11
      Sorting block time: 00:00:00
      bucket 16: 30%
      bucket 15: 60%
    Returning block of 403 for bucket 14
    Getting block 17 of 61
      Reserving size (936) for bucket 17
      Calculating Z arrays for bucket 17
      Entering block accumulator loop for bucket 17:
      bucket 16: 40%
      bucket 15: 70%
      bucket 16: 50%
      bucket 17: 10%
      bucket 15: 80%
      bucket 16: 60%
    Getting block 18 of 61
      Reserving size (936) for bucket 18
      Calculating Z arrays for bucket 18
      Entering block accumulator loop for bucket 18:
    Getting block 19 of 61
      bucket 16: 70%
      Reserving size (936) for bucket 19
      Calculating Z arrays for bucket 19
      bucket 15: 90%
      Entering block accumulator loop for bucket 19:
      bucket 18: 10%
      bucket 17: 20%
    Getting block 20 of 61
      Reserving size (936) for bucket 20
      Calculating Z arrays for bucket 20
      bucket 15: 100%
      bucket 18: 20%
      bucket 19: 10%
      Sorting block of length 819 for bucket 15
      (Using difference cover)
    Getting block 21 of 61
      Entering block accumulator loop for bucket 20:
      Sorting block time: 00:00:00
      bucket 16: 80%
      bucket 17: 30%
      bucket 18: 30%
      bucket 19: 20%
      Reserving size (936) for bucket 21
    Returning block of 820 for bucket 15
      bucket 16: 90%
      bucket 17: 40%
      bucket 18: 40%
      Calculating Z arrays for bucket 21
      bucket 19: 30%
      bucket 20: 10%
      bucket 16: 100%
      bucket 17: 50%
      Entering block accumulator loop for bucket 21:
      bucket 18: 50%
      Sorting block of length 768 for bucket 16
      (Using difference cover)
    Getting block 22 of 61
      bucket 19: 40%
      bucket 17: 60%
      bucket 20: 20%
      Reserving size (936) for bucket 22
      Sorting block time: 00:00:00
      bucket 18: 60%
      Calculating Z arrays for bucket 22
    Returning block of 769 for bucket 16
      bucket 21: 10%
      bucket 17: 70%
      Entering block accumulator loop for bucket 22:
      bucket 18: 70%
      bucket 19: 50%
      bucket 20: 30%
      bucket 21: 20%
      bucket 17: 80%
      bucket 18: 80%
      bucket 19: 60%
      bucket 20: 40%
      bucket 21: 30%
      bucket 18: 90%
      bucket 17: 90%
      bucket 22: 10%
      bucket 21: 40%
      bucket 18: 100%
      Sorting block of length 693 for bucket 18
      (Using difference cover)
      bucket 19: 70%
      bucket 21: 50%
      bucket 20: 50%
      bucket 17: 100%
      Sorting block of length 736 for bucket 17
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 694 for bucket 18
    Getting block 23 of 61
      Reserving size (936) for bucket 23
      Calculating Z arrays for bucket 23
      Entering block accumulator loop for bucket 23:
      bucket 22: 20%
      Sorting block time: 00:00:00
      bucket 19: 80%
    Returning block of 737 for bucket 17
      bucket 20: 60%
      bucket 23: 10%
      bucket 21: 60%
      bucket 22: 30%
      bucket 19: 90%
    Getting block 24 of 61
      bucket 21: 70%
      Reserving size (936) for bucket 24
      bucket 20: 70%
      bucket 23: 20%
    Getting block 25 of 61
      bucket 19: 100%
      bucket 22: 40%
      Calculating Z arrays for bucket 24
      Reserving size (936) for bucket 25
      Sorting block of length 902 for bucket 19
      (Using difference cover)
      Entering block accumulator loop for bucket 24:
      bucket 21: 80%
      Calculating Z arrays for bucket 25
      bucket 23: 30%
      Sorting block time: 00:00:00
      bucket 20: 80%
      bucket 22: 50%
      Entering block accumulator loop for bucket 25:
    Returning block of 903 for bucket 19
      bucket 21: 90%
      bucket 23: 40%
      bucket 22: 60%
      bucket 24: 10%
      bucket 21: 100%
      Sorting block of length 599 for bucket 21
      (Using difference cover)
      bucket 20: 90%
      bucket 24: 20%
      bucket 23: 50%
      bucket 22: 70%
      Sorting block time: 00:00:00
    Returning block of 600 for bucket 21
      bucket 25: 10%
      bucket 24: 30%
      bucket 20: 100%
      Sorting block of length 578 for bucket 20
      (Using difference cover)
      bucket 25: 20%
      bucket 24: 40%
      bucket 22: 80%
      bucket 23: 60%
      bucket 25: 30%
      bucket 24: 50%
      bucket 22: 90%
      bucket 24: 60%
    Getting block 26 of 61
      Reserving size (936) for bucket 26
      Sorting block time: 00:00:00
      bucket 25: 40%
      Calculating Z arrays for bucket 26
    Returning block of 579 for bucket 20
      bucket 24: 70%
      bucket 23: 70%
      bucket 22: 100%
      bucket 25: 50%
      Entering block accumulator loop for bucket 26:
      Sorting block of length 895 for bucket 22
      (Using difference cover)
      bucket 24: 80%
      bucket 23: 80%
      bucket 25: 60%
    Getting block 27 of 61
    Getting block 28 of 61
      Reserving size (936) for bucket 27
      Sorting block time: 00:00:00
      bucket 24: 90%
      Reserving size (936) for bucket 28
      bucket 25: 70%
      Calculating Z arrays for bucket 27
      bucket 23: 90%
    Returning block of 896 for bucket 22
      bucket 26: 10%
      Calculating Z arrays for bucket 28
      Entering block accumulator loop for bucket 27:
      bucket 24: 100%
      bucket 25: 80%
      Entering block accumulator loop for bucket 28:
      bucket 26: 20%
      bucket 23: 100%
      Sorting block of length 583 for bucket 24
      (Using difference cover)
      bucket 25: 90%
      Sorting block time: 00:00:00
      bucket 27: 10%
      Sorting block of length 917 for bucket 23
      (Using difference cover)
      bucket 26: 30%
    Returning block of 584 for bucket 24
      bucket 25: 100%
      bucket 28: 10%
      bucket 27: 20%
    Getting block 29 of 61
      Sorting block time: 00:00:00
      Sorting block of length 490 for bucket 25
      (Using difference cover)
      bucket 26: 40%
      Reserving size (936) for bucket 29
    Returning block of 918 for bucket 23
      Sorting block time: 00:00:00
      bucket 27: 30%
      Calculating Z arrays for bucket 29
      bucket 28: 20%
    Returning block of 491 for bucket 25
      bucket 26: 50%
      Entering block accumulator loop for bucket 29:
      bucket 27: 40%
      bucket 28: 30%
    Getting block 30 of 61
      bucket 26: 60%
    Getting block 31 of 61
      Reserving size (936) for bucket 30
      bucket 28: 40%
      bucket 27: 50%
      Reserving size (936) for bucket 31
    Getting block 32 of 61
      bucket 29: 10%
      Calculating Z arrays for bucket 30
      bucket 26: 70%
      Calculating Z arrays for bucket 31
      bucket 28: 50%
      Reserving size (936) for bucket 32
      bucket 27: 60%
      Entering block accumulator loop for bucket 30:
      bucket 29: 20%
      Entering block accumulator loop for bucket 31:
      Calculating Z arrays for bucket 32
      bucket 26: 80%
      Entering block accumulator loop for bucket 32:
      bucket 29: 30%
      bucket 27: 70%
      bucket 28: 60%
      bucket 30: 10%
      bucket 27: 80%
      bucket 28: 70%
      bucket 31: 10%
      bucket 29: 40%
      bucket 26: 90%
      bucket 32: 10%
      bucket 30: 20%
      bucket 27: 90%
      bucket 28: 80%
      bucket 27: 100%
      Sorting block of length 532 for bucket 27
      (Using difference cover)
      bucket 29: 50%
      bucket 30: 30%
      bucket 31: 20%
      Sorting block time: 00:00:00
      bucket 26: 100%
      bucket 28: 90%
      bucket 32: 20%
    Returning block of 533 for bucket 27
      Sorting block of length 625 for bucket 26
      (Using difference cover)
      bucket 30: 40%
      bucket 29: 60%
      bucket 31: 30%
      bucket 28: 100%
      bucket 32: 30%
      Sorting block of length 775 for bucket 28
      (Using difference cover)
      Sorting block time: 00:00:00
      bucket 29: 70%
      bucket 30: 50%
    Returning block of 626 for bucket 26
      bucket 31: 40%
      Sorting block time: 00:00:00
      bucket 32: 40%
    Returning block of 776 for bucket 28
      bucket 29: 80%
      bucket 31: 50%
      bucket 30: 60%
    Getting block 33 of 61
      bucket 32: 50%
      Reserving size (936) for bucket 33
      Calculating Z arrays for bucket 33
      bucket 29: 90%
      Entering block accumulator loop for bucket 33:
      bucket 30: 70%
      bucket 32: 60%
      bucket 31: 60%
      bucket 30: 80%
      bucket 32: 70%
      bucket 33: 10%
      bucket 29: 100%
      Sorting block of length 397 for bucket 29
      (Using difference cover)
      bucket 30: 90%
      bucket 32: 80%
    Getting block 34 of 61
      Reserving size (936) for bucket 34
      Calculating Z arrays for bucket 34
    Getting block 35 of 61
      Reserving size (936) for bucket 35
      Calculating Z arrays for bucket 35
      Entering block accumulator loop for bucket 35:
      Entering block accumulator loop for bucket 34:
      bucket 31: 70%
      bucket 32: 90%
      bucket 33: 20%
      bucket 35: 10%
      bucket 34: 10%
      Sorting block time: 00:00:00
      bucket 30: 100%
    Returning block of 398 for bucket 29
      Sorting block of length 837 for bucket 30
      (Using difference cover)
      bucket 32: 100%
      bucket 35: 20%
      bucket 34: 20%
      Sorting block of length 542 for bucket 32
      (Using difference cover)
      bucket 33: 30%
      Sorting block time: 00:00:00
      bucket 31: 80%
    Returning block of 838 for bucket 30
      bucket 34: 30%
      bucket 35: 30%
      Sorting block time: 00:00:00
      bucket 34: 40%
      bucket 33: 40%
    Returning block of 543 for bucket 32
      bucket 31: 90%
      bucket 35: 40%
      bucket 33: 50%
      bucket 34: 50%
      bucket 31: 100%
      bucket 35: 50%
    Getting block 36 of 61
      Sorting block of length 852 for bucket 31
      (Using difference cover)
      bucket 34: 60%
      Reserving size (936) for bucket 36
    Getting block 37 of 61
    Getting block 38 of 61
      bucket 35: 60%
      bucket 33: 60%
      Calculating Z arrays for bucket 36
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 37
      Reserving size (936) for bucket 38
      bucket 34: 70%
    Returning block of 853 for bucket 31
      Calculating Z arrays for bucket 37
      Calculating Z arrays for bucket 38
      Entering block accumulator loop for bucket 36:
      bucket 33: 70%
      bucket 35: 70%
      Entering block accumulator loop for bucket 37:
      Entering block accumulator loop for bucket 38:
      bucket 34: 80%
      bucket 35: 80%
      bucket 33: 80%
      bucket 36: 10%
      bucket 37: 10%
      bucket 34: 90%
    Getting block 39 of 61
      bucket 38: 10%
      bucket 35: 90%
      Reserving size (936) for bucket 39
      bucket 36: 20%
      bucket 37: 20%
      Calculating Z arrays for bucket 39
      bucket 33: 90%
      bucket 34: 100%
      bucket 35: 100%
      Entering block accumulator loop for bucket 39:
      bucket 38: 20%
      Sorting block of length 581 for bucket 34
      (Using difference cover)
      bucket 37: 30%
      Sorting block of length 593 for bucket 35
      (Using difference cover)
      bucket 36: 30%
      bucket 33: 100%
      Sorting block time: 00:00:00
      Sorting block time: 00:00:00
      bucket 37: 40%
      bucket 38: 30%
      Sorting block of length 571 for bucket 33
      (Using difference cover)
    Returning block of 594 for bucket 35
    Returning block of 582 for bucket 34
      bucket 36: 40%
      bucket 39: 10%
      bucket 37: 50%
      bucket 37: 60%
    Getting block 40 of 61
      Reserving size (936) for bucket 40
      Calculating Z arrays for bucket 40
      bucket 38: 40%
      Entering block accumulator loop for bucket 40:
      bucket 37: 70%
      bucket 36: 50%
      bucket 39: 20%
      Sorting block time: 00:00:00
      bucket 38: 50%
    Returning block of 572 for bucket 33
      bucket 40: 10%
      bucket 37: 80%
      bucket 38: 60%
      bucket 39: 30%
      bucket 40: 20%
      bucket 36: 60%
      bucket 38: 70%
      bucket 39: 40%
    Getting block 41 of 61
      Reserving size (936) for bucket 41
      Calculating Z arrays for bucket 41
      Entering block accumulator loop for bucket 41:
      bucket 36: 70%
      bucket 37: 90%
      bucket 40: 30%
      bucket 39: 50%
      bucket 41: 10%
      bucket 36: 80%
      bucket 38: 80%
      bucket 37: 100%
      bucket 40: 40%
      Sorting block of length 600 for bucket 37
      (Using difference cover)
    Getting block 42 of 61
      Reserving size (936) for bucket 42
      Calculating Z arrays for bucket 42
      bucket 41: 20%
      bucket 36: 90%
      Entering block accumulator loop for bucket 42:
      bucket 39: 60%
      bucket 38: 90%
      bucket 41: 30%
      bucket 36: 100%
      Sorting block of length 379 for bucket 36
      (Using difference cover)
      bucket 40: 50%
      bucket 41: 40%
      Sorting block time: 00:00:00
    Returning block of 601 for bucket 37
      bucket 42: 10%
      Sorting block time: 00:00:00
      bucket 39: 70%
    Returning block of 380 for bucket 36
      bucket 38: 100%
      bucket 40: 60%
      bucket 41: 50%
      Sorting block of length 697 for bucket 38
      (Using difference cover)
      bucket 39: 80%
      bucket 42: 20%
      bucket 40: 70%
    Getting block 43 of 61
      Reserving size (936) for bucket 43
      bucket 40: 80%
      Calculating Z arrays for bucket 43
      bucket 42: 30%
      bucket 41: 60%
      Entering block accumulator loop for bucket 43:
      bucket 39: 90%
    Getting block 44 of 61
      Reserving size (936) for bucket 44
      Calculating Z arrays for bucket 44
      Entering block accumulator loop for bucket 44:
      bucket 41: 70%
      bucket 40: 90%
      bucket 39: 100%
      Sorting block of length 889 for bucket 39
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 698 for bucket 38
      bucket 41: 80%
      bucket 44: 10%
      bucket 42: 40%
      bucket 41: 90%
      bucket 44: 20%
      Sorting block time: 00:00:00
    Returning block of 890 for bucket 39
      bucket 40: 100%
      bucket 43: 10%
      Sorting block of length 619 for bucket 40
      (Using difference cover)
      bucket 41: 100%
      bucket 44: 30%
      Sorting block of length 892 for bucket 41
      (Using difference cover)
      Sorting block time: 00:00:00
      bucket 42: 50%
    Returning block of 620 for bucket 40
      bucket 44: 40%
      bucket 43: 20%
      bucket 44: 50%
      bucket 42: 60%
    Getting block 45 of 61
      Reserving size (936) for bucket 45
      Calculating Z arrays for bucket 45
      Entering block accumulator loop for bucket 45:
      bucket 44: 60%
      bucket 43: 30%
      bucket 45: 10%
    Getting block 46 of 61
      bucket 44: 70%
      Sorting block time: 00:00:00
      bucket 42: 70%
      Reserving size (936) for bucket 46
    Returning block of 893 for bucket 41
      bucket 45: 20%
      Calculating Z arrays for bucket 46
      bucket 44: 80%
      bucket 43: 40%
      bucket 42: 80%
      Entering block accumulator loop for bucket 46:
      bucket 44: 90%
      bucket 45: 30%
    Getting block 47 of 61
    Getting block 48 of 61
      bucket 43: 50%
      bucket 44: 100%
      Reserving size (936) for bucket 47
      Reserving size (936) for bucket 48
      bucket 42: 90%
      Sorting block of length 463 for bucket 44
      (Using difference cover)
      Calculating Z arrays for bucket 47
      bucket 46: 10%
      Calculating Z arrays for bucket 48
      bucket 45: 40%
      bucket 43: 60%
      Sorting block time: 00:00:00
      Entering block accumulator loop for bucket 47:
      bucket 42: 100%
      Entering block accumulator loop for bucket 48:
    Returning block of 464 for bucket 44
      bucket 46: 20%
      Sorting block of length 652 for bucket 42
      (Using difference cover)
      bucket 43: 70%
      bucket 45: 50%
      Sorting block time: 00:00:00
      bucket 46: 30%
    Returning block of 653 for bucket 42
      bucket 43: 80%
      bucket 47: 10%
      bucket 48: 10%
      bucket 46: 40%
      bucket 45: 60%
      bucket 43: 90%
      bucket 48: 20%
    Getting block 49 of 61
      bucket 47: 20%
      bucket 45: 70%
      bucket 43: 100%
    Getting block 50 of 61
      bucket 46: 50%
      Reserving size (936) for bucket 49
      Sorting block of length 811 for bucket 43
      (Using difference cover)
      bucket 48: 30%
      Reserving size (936) for bucket 50
      bucket 47: 30%
      Calculating Z arrays for bucket 49
      bucket 45: 80%
      Calculating Z arrays for bucket 50
      bucket 48: 40%
      Sorting block time: 00:00:00
      bucket 46: 60%
      Entering block accumulator loop for bucket 49:
      Entering block accumulator loop for bucket 50:
    Returning block of 812 for bucket 43
      bucket 47: 40%
      bucket 48: 50%
      bucket 46: 70%
      bucket 45: 90%
      bucket 48: 60%
      bucket 50: 10%
      bucket 49: 10%
      bucket 46: 80%
      bucket 48: 70%
    Getting block 51 of 61
      bucket 45: 100%
      Reserving size (936) for bucket 51
      bucket 47: 50%
      Sorting block of length 749 for bucket 45
      (Using difference cover)
      Calculating Z arrays for bucket 51
      bucket 48: 80%
      bucket 49: 20%
      Sorting block time: 00:00:00
      bucket 50: 20%
      bucket 46: 90%
      Entering block accumulator loop for bucket 51:
      bucket 47: 60%
    Returning block of 750 for bucket 45
      bucket 48: 90%
      bucket 50: 30%
      bucket 49: 30%
      bucket 46: 100%
      bucket 47: 70%
      Sorting block of length 368 for bucket 46
      (Using difference cover)
      bucket 49: 40%
      bucket 51: 10%
      bucket 50: 40%
      bucket 48: 100%
    Getting block 52 of 61
      Sorting block of length 419 for bucket 48
      (Using difference cover)
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 52
      bucket 49: 50%
      Sorting block time: 00:00:00
      bucket 50: 50%
      bucket 51: 20%
    Returning block of 369 for bucket 46
      Calculating Z arrays for bucket 52
      bucket 47: 80%
    Returning block of 420 for bucket 48
      bucket 49: 60%
      bucket 50: 60%
      Entering block accumulator loop for bucket 52:
      bucket 51: 30%
      bucket 47: 90%
      bucket 49: 70%
      bucket 50: 70%
    Getting block 53 of 61
      Reserving size (936) for bucket 53
      Calculating Z arrays for bucket 53
      bucket 51: 40%
      Entering block accumulator loop for bucket 53:
      bucket 50: 80%
      bucket 53: 10%
      bucket 51: 50%
      bucket 47: 100%
      bucket 49: 80%
      Sorting block of length 928 for bucket 47
      (Using difference cover)
      bucket 50: 90%
      bucket 52: 10%
      bucket 53: 20%
      Sorting block time: 00:00:00
      bucket 51: 60%
      bucket 49: 90%
    Returning block of 929 for bucket 47
      bucket 50: 100%
    Getting block 54 of 61
      Sorting block of length 218 for bucket 50
      (Using difference cover)
      bucket 51: 70%
      bucket 53: 30%
      Reserving size (936) for bucket 54
      bucket 52: 20%
      Calculating Z arrays for bucket 54
      bucket 49: 100%
      Entering block accumulator loop for bucket 54:
      Sorting block time: 00:00:00
      bucket 53: 40%
      Sorting block of length 893 for bucket 49
      (Using difference cover)
    Returning block of 219 for bucket 50
      bucket 51: 80%
      bucket 52: 30%
      bucket 53: 50%
      bucket 54: 10%
      Sorting block time: 00:00:00
    Returning block of 894 for bucket 49
      bucket 51: 90%
      bucket 53: 60%
      bucket 52: 40%
      bucket 54: 20%
      bucket 51: 100%
      bucket 53: 70%
      Sorting block of length 889 for bucket 51
      (Using difference cover)
    Getting block 55 of 61
      Reserving size (936) for bucket 55
      Calculating Z arrays for bucket 55
      Entering block accumulator loop for bucket 55:
      bucket 52: 50%
      bucket 54: 30%
    Getting block 56 of 61
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 56
    Returning block of 890 for bucket 51
    Getting block 57 of 61
      bucket 53: 80%
      Calculating Z arrays for bucket 56
      bucket 54: 40%
      bucket 55: 10%
      bucket 52: 60%
      Reserving size (936) for bucket 57
      Entering block accumulator loop for bucket 56:
      bucket 53: 90%
      Calculating Z arrays for bucket 57
    Getting block 58 of 61
      bucket 54: 50%
      bucket 52: 70%
      bucket 55: 20%
      Entering block accumulator loop for bucket 57:
      Reserving size (936) for bucket 58
      bucket 53: 100%
      bucket 54: 60%
      bucket 56: 10%
      Calculating Z arrays for bucket 58
      bucket 52: 80%
      Sorting block of length 934 for bucket 53
      (Using difference cover)
      bucket 55: 30%
      bucket 54: 70%
      Entering block accumulator loop for bucket 58:
      bucket 56: 20%
      bucket 57: 10%
      bucket 54: 80%
      bucket 58: 10%
      bucket 52: 90%
      Sorting block time: 00:00:00
      bucket 55: 40%
      bucket 56: 30%
      bucket 54: 90%
    Returning block of 935 for bucket 53
      bucket 57: 20%
      bucket 58: 20%
      bucket 52: 100%
      bucket 55: 50%
      bucket 56: 40%
      Sorting block of length 845 for bucket 52
      (Using difference cover)
      bucket 57: 30%
      bucket 54: 100%
      bucket 56: 50%
      Sorting block of length 62 for bucket 54
      (Using difference cover)
      bucket 57: 40%
      bucket 55: 60%
      bucket 58: 30%
      Sorting block time: 00:00:00
      Sorting block time: 00:00:00
      bucket 56: 60%
      bucket 57: 50%
    Returning block of 63 for bucket 54
    Returning block of 846 for bucket 52
      bucket 58: 40%
      bucket 55: 70%
      bucket 56: 70%
      bucket 57: 60%
    Getting block 59 of 61
      Reserving size (936) for bucket 59
      bucket 55: 80%
      Calculating Z arrays for bucket 59
      bucket 58: 50%
      Entering block accumulator loop for bucket 59:
      bucket 57: 70%
      bucket 56: 80%
      bucket 58: 60%
      bucket 55: 90%
    Getting block 60 of 61
      bucket 57: 80%
    Getting block 61 of 61
      Reserving size (936) for bucket 60
      bucket 58: 70%
      bucket 55: 100%
      bucket 59: 10%
      bucket 56: 90%
      Reserving size (936) for bucket 61
      Calculating Z arrays for bucket 60
      bucket 57: 90%
      Sorting block of length 897 for bucket 55
      (Using difference cover)
      bucket 58: 80%
      bucket 59: 20%
      Calculating Z arrays for bucket 61
      Entering block accumulator loop for bucket 60:
      Sorting block time: 00:00:00
      bucket 56: 100%
      bucket 57: 100%
      Entering block accumulator loop for bucket 61:
    Returning block of 898 for bucket 55
      bucket 58: 90%
      bucket 59: 30%
      Sorting block of length 606 for bucket 56
      (Using difference cover)
      Sorting block of length 493 for bucket 57
      (Using difference cover)
      bucket 60: 10%
      bucket 58: 100%
      bucket 59: 40%
      Sorting block time: 00:00:00
      Sorting block time: 00:00:00
      Sorting block of length 924 for bucket 58
      (Using difference cover)
      bucket 61: 10%
    Returning block of 607 for bucket 56
    Returning block of 494 for bucket 57
      bucket 60: 20%
      bucket 59: 50%
      bucket 61: 20%
      bucket 61: 30%
      bucket 60: 30%
      Sorting block time: 00:00:00
    Returning block of 925 for bucket 58
      bucket 61: 40%
      bucket 60: 40%
      bucket 61: 50%
      bucket 59: 60%
      bucket 61: 60%
      bucket 60: 50%
      bucket 61: 70%
      bucket 60: 60%
      bucket 61: 80%
      bucket 61: 90%
      bucket 60: 70%
      bucket 59: 70%
      bucket 60: 80%
      bucket 61: 100%
      Sorting block of length 693 for bucket 61
      (Using difference cover)
      bucket 60: 90%
      bucket 59: 80%
      Sorting block time: 00:00:00
    Returning block of 694 for bucket 61
      bucket 60: 100%
      Sorting block of length 727 for bucket 60
      (Using difference cover)
      bucket 59: 90%
      Sorting block time: 00:00:00
    Returning block of 728 for bucket 60
      bucket 59: 100%
      Sorting block of length 638 for bucket 59
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 639 for bucket 59
    Exited Ebwt loop
    fchr[A]: 0
    fchr[C]: 10842
    fchr[G]: 19880
    fchr[T]: 30171
    fchr[$]: 39937
    Exiting Ebwt::buildToDisk()
    Returning from initFromVector
    Wrote 4207850 bytes to primary EBWT file: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.1.bt2.tmp
    Wrote 9992 bytes to secondary EBWT file: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.2.bt2.tmp
    Re-opening _in1 and _in2 as input streams
    Returning from Ebwt constructor
    Headers:
        len: 39937
        bwtLen: 39938
        sz: 9985
        bwtSz: 9985
        lineRate: 6
        offRate: 4
        offMask: 0xfffffff0
        ftabChars: 10
        eftabLen: 20
        eftabSz: 80
        ftabLen: 1048577
        ftabSz: 4194308
        offsLen: 2497
        offsSz: 9988
        lineSz: 64
        sideSz: 64
        sideBwtSz: 48
        sideBwtLen: 192
        numSides: 209
        numLines: 209
        ebwtTotLen: 13376
        ebwtTotSz: 13376
        color: 0
        reverse: 0
    Total time for call to driver() for forward index: 00:00:00
    Reading reference sizes
      Time reading reference sizes: 00:00:00
    Calculating joined length
    Writing header
    Reserving space for joined string
    Joining reference sequences
      Time to join reference sequences: 00:00:00
      Time to reverse reference sequence: 00:00:00
    bmax according to bmaxDivN setting: 1248
    Using parameters --bmax 936 --dcv 1024
      Doing ahead-of-time memory usage test
      Passed!  Constructing with these parameters: --bmax 936 --dcv 1024
    Constructing suffix-array element generator
    Building DifferenceCoverSample
      Building sPrime
      Building sPrimeOrder
      V-Sorting samples
      V-Sorting samples time: 00:00:00
      Allocating rank array
      Ranking v-sort output
      Ranking v-sort output time: 00:00:00
      Invoking Larsson-Sadakane on ranks
      Invoking Larsson-Sadakane on ranks time: 00:00:00
      Sanity-checking and returning
    Building samples
    Reserving space for 86 sample suffixes
    Generating random suffixes
    QSorting 86 sample offsets, eliminating duplicates
    QSorting sample offsets, eliminating duplicates time: 00:00:00
    Multikey QSorting 86 samples
      (Using difference cover)
      Multikey QSorting samples time: 00:00:00
    Calculating bucket sizes
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 13, merged 40; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 7, merged 6; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 3, merged 4; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 2, merged 3; iterating...
    Splitting and merging
      Splitting and merging time: 00:00:00
    Split 2, merged 1; iterating...
    Avg bucket size: 664.633 (target: 935)
    Converting suffix-array elements to index image
    Allocating ftab, absorbFtab
    Entering Ebwt loop
    Getting block 1 of 60
      Reserving size (936) for bucket 1
    Getting block 2 of 60
      Calculating Z arrays for bucket 1
    Getting block 3 of 60
    Getting block 4 of 60
    Getting block 5 of 60
      Reserving size (936) for bucket 2
    Getting block 6 of 60
    Getting block 7 of 60
      Entering block accumulator loop for bucket 1:
      Reserving size (936) for bucket 3
      Reserving size (936) for bucket 4
      Reserving size (936) for bucket 5
      Calculating Z arrays for bucket 2
      Reserving size (936) for bucket 6
      Reserving size (936) for bucket 7
      Calculating Z arrays for bucket 3
      Calculating Z arrays for bucket 4
      Calculating Z arrays for bucket 5
      Entering block accumulator loop for bucket 2:
      Calculating Z arrays for bucket 6
      Calculating Z arrays for bucket 7
      bucket 1: 10%
      Entering block accumulator loop for bucket 3:
      Entering block accumulator loop for bucket 4:
      Entering block accumulator loop for bucket 5:
      Entering block accumulator loop for bucket 6:
      Entering block accumulator loop for bucket 7:
      bucket 1: 20%
      bucket 2: 10%
      bucket 3: 10%
      bucket 1: 30%
      bucket 4: 10%
      bucket 2: 20%
      bucket 5: 10%
      bucket 6: 10%
      bucket 1: 40%
      bucket 7: 10%
      bucket 4: 20%
      bucket 6: 20%
      bucket 1: 50%
      bucket 5: 20%
      bucket 2: 30%
      bucket 3: 20%
      bucket 4: 30%
      bucket 6: 30%
      bucket 1: 60%
      bucket 7: 20%
      bucket 5: 30%
      bucket 3: 30%
      bucket 2: 40%
      bucket 4: 40%
      bucket 6: 40%
      bucket 1: 70%
      bucket 7: 30%
      bucket 5: 40%
      bucket 3: 40%
      bucket 2: 50%
      bucket 4: 50%
      bucket 6: 50%
      bucket 1: 80%
      bucket 7: 40%
      bucket 5: 50%
      bucket 4: 60%
      bucket 3: 50%
      bucket 2: 60%
      bucket 1: 90%
      bucket 6: 60%
      bucket 7: 50%
      bucket 5: 60%
      bucket 4: 70%
      bucket 2: 70%
      bucket 1: 100%
      Sorting block of length 854 for bucket 1
      (Using difference cover)
      bucket 6: 70%
      bucket 3: 60%
      bucket 6: 80%
      bucket 3: 70%
      bucket 5: 70%
      bucket 7: 60%
      Sorting block time: 00:00:00
      bucket 6: 90%
      bucket 4: 80%
    Returning block of 855 for bucket 1
      bucket 2: 80%
      bucket 3: 80%
      bucket 6: 100%
      bucket 4: 90%
      Sorting block of length 214 for bucket 6
      (Using difference cover)
      bucket 7: 70%
      bucket 5: 80%
      bucket 2: 90%
      bucket 4: 100%
      Sorting block of length 602 for bucket 4
      (Using difference cover)
      bucket 7: 80%
      Sorting block time: 00:00:00
      bucket 3: 90%
    Returning block of 215 for bucket 6
      bucket 7: 90%
      bucket 2: 100%
      Sorting block time: 00:00:00
      bucket 7: 100%
      bucket 3: 100%
    Returning block of 603 for bucket 4
      bucket 5: 90%
      Sorting block of length 671 for bucket 2
      (Using difference cover)
      Sorting block of length 914 for bucket 7
      (Using difference cover)
      Sorting block of length 814 for bucket 3
      (Using difference cover)
      bucket 5: 100%
      Sorting block time: 00:00:00
    Getting block 8 of 60
      Sorting block of length 754 for bucket 5
      (Using difference cover)
    Returning block of 915 for bucket 7
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 8
    Getting block 9 of 60
    Returning block of 815 for bucket 3
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 8
      Reserving size (936) for bucket 9
    Returning block of 672 for bucket 2
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 9
      Entering block accumulator loop for bucket 8:
    Returning block of 755 for bucket 5
      Entering block accumulator loop for bucket 9:
    Getting block 10 of 60
      Reserving size (936) for bucket 10
      Calculating Z arrays for bucket 10
      Entering block accumulator loop for bucket 10:
    Getting block 11 of 60
      Reserving size (936) for bucket 11
      Calculating Z arrays for bucket 11
    Getting block 12 of 60
      Reserving size (936) for bucket 12
      Calculating Z arrays for bucket 12
    Getting block 13 of 60
      Reserving size (936) for bucket 13
      Calculating Z arrays for bucket 13
      Entering block accumulator loop for bucket 11:
      Entering block accumulator loop for bucket 12:
      Entering block accumulator loop for bucket 13:
      bucket 8: 10%
    Getting block 14 of 60
      Reserving size (936) for bucket 14
      Calculating Z arrays for bucket 14
      bucket 11: 10%
      Entering block accumulator loop for bucket 14:
      bucket 13: 10%
      bucket 8: 20%
      bucket 10: 10%
      bucket 9: 10%
      bucket 11: 20%
      bucket 14: 10%
      bucket 13: 20%
      bucket 8: 30%
      bucket 12: 10%
      bucket 10: 20%
      bucket 11: 30%
      bucket 9: 20%
      bucket 8: 40%
      bucket 13: 30%
      bucket 11: 40%
      bucket 9: 30%
      bucket 14: 20%
      bucket 12: 20%
      bucket 10: 30%
      bucket 11: 50%
      bucket 14: 30%
      bucket 9: 40%
      bucket 8: 50%
      bucket 13: 40%
      bucket 14: 40%
      bucket 11: 60%
      bucket 9: 50%
      bucket 12: 30%
      bucket 10: 40%
      bucket 14: 50%
      bucket 11: 70%
      bucket 8: 60%
      bucket 9: 60%
      bucket 14: 60%
      bucket 13: 50%
      bucket 11: 80%
      bucket 9: 70%
      bucket 12: 40%
      bucket 10: 50%
      bucket 14: 70%
      bucket 11: 90%
      bucket 9: 80%
      bucket 13: 60%
      bucket 12: 50%
      bucket 8: 70%
      bucket 10: 60%
      bucket 14: 80%
      bucket 11: 100%
      bucket 12: 60%
      bucket 9: 90%
      Sorting block of length 538 for bucket 11
      (Using difference cover)
      bucket 13: 70%
      bucket 10: 70%
      bucket 14: 90%
      bucket 8: 80%
      bucket 12: 70%
      bucket 9: 100%
      Sorting block of length 908 for bucket 9
      (Using difference cover)
      bucket 10: 80%
      Sorting block time: 00:00:00
    Returning block of 539 for bucket 11
      bucket 13: 80%
      bucket 12: 80%
      bucket 14: 100%
      Sorting block of length 759 for bucket 14
      (Using difference cover)
      bucket 8: 90%
      bucket 10: 90%
      bucket 12: 90%
      bucket 10: 100%
      Sorting block of length 806 for bucket 10
      (Using difference cover)
      bucket 13: 90%
      bucket 8: 100%
      Sorting block of length 902 for bucket 8
      Sorting block time: 00:00:00
      (Using difference cover)
      bucket 12: 100%
    Returning block of 909 for bucket 9
      Sorting block of length 684 for bucket 12
      (Using difference cover)
      Sorting block time: 00:00:00
      Sorting block time: 00:00:00
    Getting block 15 of 60
      bucket 13: 100%
    Returning block of 807 for bucket 10
    Returning block of 760 for bucket 14
      Reserving size (936) for bucket 15
      Sorting block of length 290 for bucket 13
      (Using difference cover)
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 15
      Sorting block time: 00:00:00
    Returning block of 903 for bucket 8
    Returning block of 685 for bucket 12
      Entering block accumulator loop for bucket 15:
      bucket 15: 10%
      bucket 15: 20%
      Sorting block time: 00:00:00
    Returning block of 291 for bucket 13
      bucket 15: 30%
      bucket 15: 40%
      bucket 15: 50%
      bucket 15: 60%
      bucket 15: 70%
      bucket 15: 80%
      bucket 15: 90%
      bucket 15: 100%
      Sorting block of length 715 for bucket 15
      (Using difference cover)
    Getting block 16 of 60
      Reserving size (936) for bucket 16
      Calculating Z arrays for bucket 16
      Entering block accumulator loop for bucket 16:
      bucket 16: 10%
    Getting block 17 of 60
      Reserving size (936) for bucket 17
      Calculating Z arrays for bucket 17
      Entering block accumulator loop for bucket 17:
      Sorting block time: 00:00:00
    Returning block of 716 for bucket 15
    Getting block 18 of 60
      Reserving size (936) for bucket 18
      Calculating Z arrays for bucket 18
      Entering block accumulator loop for bucket 18:
    Getting block 19 of 60
      bucket 17: 10%
      Reserving size (936) for bucket 19
      bucket 16: 20%
      Calculating Z arrays for bucket 19
    Getting block 20 of 60
      bucket 17: 20%
      Entering block accumulator loop for bucket 19:
      Reserving size (936) for bucket 20
      bucket 16: 30%
      Calculating Z arrays for bucket 20
    Getting block 21 of 60
      bucket 18: 10%
      bucket 19: 10%
      bucket 16: 40%
      bucket 17: 30%
      Reserving size (936) for bucket 21
      Entering block accumulator loop for bucket 20:
      bucket 19: 20%
      bucket 16: 50%
      Calculating Z arrays for bucket 21
      bucket 18: 20%
      bucket 17: 40%
      bucket 19: 30%
      bucket 16: 60%
      Entering block accumulator loop for bucket 21:
      bucket 20: 10%
      bucket 17: 50%
      bucket 19: 40%
    Getting block 22 of 60
      bucket 18: 30%
      bucket 16: 70%
      Reserving size (936) for bucket 22
      bucket 20: 20%
      bucket 19: 50%
      Calculating Z arrays for bucket 22
      bucket 21: 10%
      bucket 17: 60%
      bucket 20: 30%
      bucket 18: 40%
      bucket 19: 60%
      Entering block accumulator loop for bucket 22:
      bucket 16: 80%
      bucket 21: 20%
      bucket 20: 40%
      bucket 17: 70%
      bucket 18: 50%
      bucket 19: 70%
      bucket 21: 30%
      bucket 20: 50%
      bucket 16: 90%
      bucket 19: 80%
      bucket 22: 10%
      bucket 20: 60%
      bucket 18: 60%
      bucket 17: 80%
      bucket 19: 90%
      bucket 16: 100%
      Sorting block of length 865 for bucket 16
      (Using difference cover)
      bucket 20: 70%
      bucket 21: 40%
      bucket 19: 100%
      Sorting block of length 736 for bucket 19
      (Using difference cover)
      bucket 20: 80%
      bucket 18: 70%
      Sorting block time: 00:00:00
      bucket 22: 20%
      bucket 17: 90%
      Sorting block time: 00:00:00
    Returning block of 866 for bucket 16
      bucket 20: 90%
    Returning block of 737 for bucket 19
      bucket 21: 50%
      bucket 17: 100%
      bucket 18: 80%
      bucket 20: 100%
      Sorting block of length 817 for bucket 17
      (Using difference cover)
      bucket 22: 30%
      Sorting block of length 408 for bucket 20
      (Using difference cover)
      bucket 21: 60%
      bucket 18: 90%
    Getting block 23 of 60
      Sorting block time: 00:00:00
    Getting block 24 of 60
      bucket 22: 40%
      Reserving size (936) for bucket 23
    Returning block of 818 for bucket 17
      bucket 21: 70%
      Reserving size (936) for bucket 24
      bucket 18: 100%
      Calculating Z arrays for bucket 23
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 24
      Sorting block of length 604 for bucket 18
      (Using difference cover)
    Returning block of 409 for bucket 20
      Entering block accumulator loop for bucket 23:
      Entering block accumulator loop for bucket 24:
      bucket 22: 50%
      bucket 21: 80%
      Sorting block time: 00:00:00
    Returning block of 605 for bucket 18
      bucket 24: 10%
      bucket 23: 10%
      bucket 22: 60%
    Getting block 25 of 60
      Reserving size (936) for bucket 25
      Calculating Z arrays for bucket 25
      bucket 21: 90%
      bucket 24: 20%
      Entering block accumulator loop for bucket 25:
    Getting block 26 of 60
    Getting block 27 of 60
      bucket 21: 100%
      Reserving size (936) for bucket 26
      Reserving size (936) for bucket 27
      Sorting block of length 681 for bucket 21
      (Using difference cover)
      Calculating Z arrays for bucket 26
      bucket 23: 20%
      Calculating Z arrays for bucket 27
      bucket 22: 70%
      bucket 24: 30%
      Entering block accumulator loop for bucket 26:
      bucket 25: 10%
      Sorting block time: 00:00:00
      Entering block accumulator loop for bucket 27:
      bucket 22: 80%
    Returning block of 682 for bucket 21
      bucket 24: 40%
      bucket 23: 30%
      bucket 25: 20%
      bucket 22: 90%
      bucket 26: 10%
      bucket 27: 10%
      bucket 23: 40%
      bucket 25: 30%
      bucket 26: 20%
      bucket 22: 100%
      Sorting block of length 839 for bucket 22
      (Using difference cover)
      bucket 24: 50%
      bucket 25: 40%
      bucket 26: 30%
      bucket 23: 50%
      Sorting block time: 00:00:00
    Returning block of 840 for bucket 22
      bucket 25: 50%
      bucket 26: 40%
      bucket 24: 60%
      bucket 27: 20%
      bucket 25: 60%
      bucket 26: 50%
      bucket 25: 70%
      bucket 24: 70%
      bucket 26: 60%
      bucket 23: 60%
    Getting block 28 of 60
    Getting block 29 of 60
      Reserving size (936) for bucket 28
      Reserving size (936) for bucket 29
      Calculating Z arrays for bucket 28
      Calculating Z arrays for bucket 29
      bucket 25: 80%
      bucket 24: 80%
      Entering block accumulator loop for bucket 28:
      bucket 27: 30%
      Entering block accumulator loop for bucket 29:
      bucket 26: 70%
      bucket 24: 90%
      bucket 25: 90%
      bucket 23: 70%
      bucket 27: 40%
      bucket 28: 10%
      bucket 26: 80%
      bucket 29: 10%
      bucket 23: 80%
      bucket 24: 100%
      bucket 25: 100%
      bucket 26: 90%
      Sorting block of length 461 for bucket 24
      (Using difference cover)
      bucket 27: 50%
      Sorting block of length 879 for bucket 25
      (Using difference cover)
      bucket 29: 20%
      bucket 28: 20%
      bucket 26: 100%
      bucket 23: 90%
      Sorting block time: 00:00:00
      Sorting block of length 732 for bucket 26
      (Using difference cover)
    Returning block of 462 for bucket 24
      Sorting block time: 00:00:00
      bucket 29: 30%
      bucket 27: 60%
      bucket 28: 30%
    Returning block of 880 for bucket 25
      bucket 23: 100%
      Sorting block of length 601 for bucket 23
      Sorting block time: 00:00:00
      (Using difference cover)
      bucket 27: 70%
    Returning block of 733 for bucket 26
      bucket 28: 40%
      bucket 27: 80%
      Sorting block time: 00:00:00
    Returning block of 602 for bucket 23
      bucket 28: 50%
      bucket 29: 40%
      bucket 27: 90%
      bucket 28: 60%
      bucket 27: 100%
      Sorting block of length 827 for bucket 27
      (Using difference cover)
      bucket 29: 50%
      bucket 28: 70%
    Getting block 30 of 60
      Reserving size (936) for bucket 30
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 30
    Returning block of 828 for bucket 27
      Entering block accumulator loop for bucket 30:
    Getting block 31 of 60
      Reserving size (936) for bucket 31
      Calculating Z arrays for bucket 31
      Entering block accumulator loop for bucket 31:
      bucket 28: 80%
    Getting block 32 of 60
      Reserving size (936) for bucket 32
      Calculating Z arrays for bucket 32
      Entering block accumulator loop for bucket 32:
      bucket 31: 10%
      bucket 30: 10%
      bucket 29: 60%
      bucket 32: 10%
      bucket 31: 20%
      bucket 30: 20%
    Getting block 33 of 60
      Reserving size (936) for bucket 33
      Calculating Z arrays for bucket 33
      Entering block accumulator loop for bucket 33:
      bucket 32: 20%
      bucket 28: 90%
      bucket 31: 30%
      bucket 29: 70%
      bucket 30: 30%
      bucket 32: 30%
      bucket 33: 10%
      bucket 31: 40%
      bucket 28: 100%
    Getting block 34 of 60
      bucket 30: 40%
      bucket 32: 40%
      Sorting block of length 862 for bucket 28
      (Using difference cover)
      bucket 33: 20%
      bucket 29: 80%
      Reserving size (936) for bucket 34
      bucket 31: 50%
      bucket 30: 50%
      Sorting block time: 00:00:00
      bucket 32: 50%
      Calculating Z arrays for bucket 34
      bucket 33: 30%
      bucket 29: 90%
    Returning block of 863 for bucket 28
      bucket 31: 60%
      Entering block accumulator loop for bucket 34:
      bucket 32: 60%
      bucket 30: 60%
      bucket 33: 40%
      bucket 29: 100%
      bucket 31: 70%
      Sorting block of length 616 for bucket 29
      (Using difference cover)
      bucket 30: 70%
      bucket 32: 70%
      bucket 33: 50%
      bucket 31: 80%
    Getting block 35 of 60
      bucket 34: 10%
      bucket 30: 80%
      Reserving size (936) for bucket 35
      bucket 32: 80%
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 35
      bucket 33: 60%
    Returning block of 617 for bucket 29
      bucket 34: 20%
      bucket 31: 90%
      Entering block accumulator loop for bucket 35:
      bucket 33: 70%
      bucket 30: 90%
      bucket 32: 90%
      bucket 34: 30%
      bucket 31: 100%
      Sorting block of length 720 for bucket 31
      (Using difference cover)
      bucket 33: 80%
      bucket 30: 100%
      Sorting block of length 449 for bucket 30
      (Using difference cover)
      bucket 32: 100%
      Sorting block of length 607 for bucket 32
      (Using difference cover)
      bucket 33: 90%
      Sorting block time: 00:00:00
    Returning block of 450 for bucket 30
      bucket 35: 10%
      Sorting block time: 00:00:00
      bucket 34: 40%
      bucket 33: 100%
      Sorting block time: 00:00:00
    Returning block of 608 for bucket 32
      Sorting block of length 608 for bucket 33
      (Using difference cover)
      bucket 35: 20%
    Returning block of 721 for bucket 31
      bucket 34: 50%
    Getting block 36 of 60
    Getting block 37 of 60
      Reserving size (936) for bucket 36
      Reserving size (936) for bucket 37
      Sorting block time: 00:00:00
      Calculating Z arrays for bucket 36
      Calculating Z arrays for bucket 37
    Returning block of 609 for bucket 33
      bucket 35: 30%
    Getting block 38 of 60
      Entering block accumulator loop for bucket 37:
      Entering block accumulator loop for bucket 36:
      bucket 34: 60%
      Reserving size (936) for bucket 38
      Calculating Z arrays for bucket 38
    Getting block 39 of 60
      bucket 34: 70%
      bucket 35: 40%
      Reserving size (936) for bucket 39
    Getting block 40 of 60
      Entering block accumulator loop for bucket 38:
      Calculating Z arrays for bucket 39
      Reserving size (936) for bucket 40
      bucket 35: 50%
      bucket 34: 80%
      bucket 37: 10%
      Entering block accumulator loop for bucket 39:
      Calculating Z arrays for bucket 40
      bucket 36: 10%
      bucket 38: 10%
      bucket 35: 60%
      Entering block accumulator loop for bucket 40:
      bucket 34: 90%
      bucket 39: 10%
      bucket 37: 20%
      bucket 35: 70%
      bucket 36: 20%
      bucket 38: 20%
      bucket 34: 100%
      bucket 40: 10%
      Sorting block of length 631 for bucket 34
      (Using difference cover)
      bucket 37: 30%
      bucket 39: 20%
      bucket 36: 30%
      bucket 35: 80%
      Sorting block time: 00:00:00
      bucket 38: 30%
    Returning block of 632 for bucket 34
      bucket 40: 20%
      bucket 39: 30%
      bucket 37: 40%
      bucket 39: 40%
      bucket 35: 90%
      bucket 37: 50%
      bucket 40: 30%
    Getting block 41 of 60
      Reserving size (936) for bucket 41
      Calculating Z arrays for bucket 41
      bucket 36: 40%
      bucket 38: 40%
      Entering block accumulator loop for bucket 41:
      bucket 39: 50%
      bucket 35: 100%
      bucket 37: 60%
      bucket 38: 50%
      Sorting block of length 346 for bucket 35
      (Using difference cover)
      bucket 40: 40%
      bucket 36: 50%
      bucket 39: 60%
      Sorting block time: 00:00:00
      bucket 37: 70%
      bucket 38: 60%
    Returning block of 347 for bucket 35
      bucket 41: 10%
      bucket 36: 60%
      bucket 39: 70%
      bucket 37: 80%
      bucket 40: 50%
      bucket 39: 80%
      bucket 36: 70%
      bucket 37: 90%
      bucket 38: 70%
      bucket 40: 60%
      bucket 41: 20%
      bucket 39: 90%
    Getting block 42 of 60
      bucket 40: 70%
      bucket 37: 100%
      bucket 38: 80%
      Reserving size (936) for bucket 42
      bucket 36: 80%
      bucket 39: 100%
      bucket 41: 30%
      Sorting block of length 926 for bucket 37
      (Using difference cover)
      Calculating Z arrays for bucket 42
      bucket 40: 80%
      bucket 38: 90%
      Sorting block of length 988 for bucket 39
      (Using difference cover)
      bucket 36: 90%
      bucket 41: 40%
      Sorting block time: 00:00:00
      Entering block accumulator loop for bucket 42:
    Returning block of 927 for bucket 37
      bucket 40: 90%
      bucket 38: 100%
      Sorting block of length 774 for bucket 38
      (Using difference cover)
      bucket 41: 50%
      bucket 36: 100%
      bucket 40: 100%
      Sorting block time: 00:00:00
      Sorting block of length 446 for bucket 36
      (Using difference cover)
      bucket 42: 10%
      Sorting block of length 146 for bucket 40
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 989 for bucket 39
      Sorting block time: 00:00:00
      bucket 41: 60%
    Returning block of 775 for bucket 38
    Returning block of 447 for bucket 36
      bucket 42: 20%
      Sorting block time: 00:00:00
    Returning block of 147 for bucket 40
    Getting block 43 of 60
      Reserving size (936) for bucket 43
      Calculating Z arrays for bucket 43
      Entering block accumulator loop for bucket 43:
      bucket 42: 30%
      bucket 41: 70%
      bucket 42: 40%
      bucket 41: 80%
      bucket 42: 50%
      bucket 41: 90%
      bucket 43: 10%
      bucket 42: 60%
      bucket 41: 100%
      Sorting block of length 554 for bucket 41
      (Using difference cover)
      bucket 42: 70%
    Getting block 44 of 60
    Getting block 45 of 60
    Getting block 46 of 60
      Reserving size (936) for bucket 44
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 45
      Reserving size (936) for bucket 46
      Calculating Z arrays for bucket 44
    Returning block of 555 for bucket 41
      Calculating Z arrays for bucket 45
      bucket 43: 20%
      Calculating Z arrays for bucket 46
      bucket 42: 80%
    Getting block 47 of 60
      Entering block accumulator loop for bucket 44:
      Entering block accumulator loop for bucket 45:
      Entering block accumulator loop for bucket 46:
      bucket 43: 30%
      Reserving size (936) for bucket 47
      bucket 42: 90%
      Calculating Z arrays for bucket 47
      bucket 43: 40%
    Getting block 48 of 60
      bucket 44: 10%
      Entering block accumulator loop for bucket 47:
      bucket 45: 10%
      Reserving size (936) for bucket 48
      bucket 42: 100%
      bucket 46: 10%
      Calculating Z arrays for bucket 48
      Sorting block of length 478 for bucket 42
      (Using difference cover)
      bucket 43: 50%
      Entering block accumulator loop for bucket 48:
      bucket 44: 20%
      Sorting block time: 00:00:00
    Returning block of 479 for bucket 42
      bucket 47: 10%
      bucket 45: 20%
      bucket 46: 20%
      bucket 43: 60%
      bucket 44: 30%
      bucket 48: 10%
      bucket 47: 20%
      bucket 45: 30%
      bucket 46: 30%
      bucket 44: 40%
      bucket 43: 70%
    Getting block 49 of 60
      bucket 47: 30%
      Reserving size (936) for bucket 49
      bucket 48: 20%
      bucket 46: 40%
      Calculating Z arrays for bucket 49
      bucket 45: 40%
      bucket 47: 40%
      bucket 48: 30%
      bucket 44: 50%
      bucket 43: 80%
      bucket 46: 50%
      Entering block accumulator loop for bucket 49:
      bucket 45: 50%
      bucket 47: 50%
      bucket 48: 40%
      bucket 43: 90%
      bucket 44: 60%
      bucket 43: 100%
      Sorting block of length 734 for bucket 43
      (Using difference cover)
      bucket 47: 60%
      bucket 45: 60%
      bucket 48: 50%
      bucket 49: 10%
      bucket 47: 70%
      Sorting block time: 00:00:00
    Returning block of 735 for bucket 43
      bucket 46: 60%
      bucket 44: 70%
      bucket 45: 70%
      bucket 47: 80%
      bucket 49: 20%
      bucket 48: 60%
      bucket 46: 70%
      bucket 44: 80%
      bucket 47: 90%
    Getting block 50 of 60
      bucket 46: 80%
      Reserving size (936) for bucket 50
      bucket 45: 80%
      bucket 48: 70%
      Calculating Z arrays for bucket 50
      bucket 49: 30%
      Entering block accumulator loop for bucket 50:
      bucket 46: 90%
      bucket 45: 90%
      bucket 47: 100%
      bucket 44: 90%
      bucket 48: 80%
      Sorting block of length 434 for bucket 47
      bucket 48: 90%
      bucket 49: 40%
      (Using difference cover)
      bucket 44: 100%
      bucket 45: 100%
      bucket 46: 100%
      Sorting block of length 628 for bucket 44
      (Using difference cover)
      bucket 50: 10%
      Sorting block of length 883 for bucket 45
      (Using difference cover)
      Sorting block of length 683 for bucket 46
      (Using difference cover)
      bucket 48: 100%
      Sorting block time: 00:00:00
      bucket 49: 50%
      Sorting block of length 643 for bucket 48
      (Using difference cover)
    Returning block of 435 for bucket 47
      Sorting block time: 00:00:00
    Returning block of 684 for bucket 46
      bucket 50: 20%
      Sorting block time: 00:00:00
    Returning block of 884 for bucket 45
      bucket 49: 60%
      Sorting block time: 00:00:00
    Returning block of 629 for bucket 44
      bucket 50: 30%
      Sorting block time: 00:00:00
    Returning block of 644 for bucket 48
      bucket 49: 70%
      bucket 50: 40%
    Getting block 51 of 60
      Reserving size (936) for bucket 51
      Calculating Z arrays for bucket 51
      Entering block accumulator loop for bucket 51:
    Getting block 52 of 60
      Reserving size (936) for bucket 52
      Calculating Z arrays for bucket 52
      Entering block accumulator loop for bucket 52:
      bucket 50: 50%
      bucket 51: 10%
      bucket 49: 80%
      bucket 52: 10%
      bucket 50: 60%
      bucket 51: 20%
      bucket 52: 20%
      bucket 50: 70%
      bucket 51: 30%
    Getting block 53 of 60
      Reserving size (936) for bucket 53
      Calculating Z arrays for bucket 53
      bucket 52: 30%
      bucket 50: 80%
      Entering block accumulator loop for bucket 53:
      bucket 51: 40%
      bucket 49: 90%
      bucket 50: 90%
      bucket 52: 40%
    Getting block 54 of 60
    Getting block 55 of 60
      Reserving size (936) for bucket 54
      Reserving size (936) for bucket 55
      bucket 53: 10%
      bucket 50: 100%
      Calculating Z arrays for bucket 54
      bucket 52: 50%
      bucket 49: 100%
      bucket 51: 50%
      Calculating Z arrays for bucket 55
      Sorting block of length 302 for bucket 50
      (Using difference cover)
      Entering block accumulator loop for bucket 54:
      Sorting block time: 00:00:00
      Sorting block of length 757 for bucket 49
      (Using difference cover)
      bucket 53: 20%
      bucket 52: 60%
      Entering block accumulator loop for bucket 55:
      bucket 51: 60%
      Sorting block time: 00:00:00
    Returning block of 303 for bucket 50
      bucket 53: 30%
    Returning block of 758 for bucket 49
      bucket 52: 70%
      bucket 51: 70%
      bucket 54: 10%
      bucket 55: 10%
      bucket 53: 40%
      bucket 52: 80%
      bucket 55: 20%
      bucket 54: 20%
      bucket 51: 80%
    Getting block 56 of 60
      Reserving size (936) for bucket 56
      bucket 55: 30%
      Calculating Z arrays for bucket 56
      bucket 54: 30%
      bucket 53: 50%
      Entering block accumulator loop for bucket 56:
      bucket 55: 40%
      bucket 53: 60%
      bucket 54: 40%
      bucket 55: 50%
      bucket 52: 90%
      bucket 51: 90%
      bucket 53: 70%
      bucket 54: 50%
    Getting block 57 of 60
      Reserving size (936) for bucket 57
      Calculating Z arrays for bucket 57
      bucket 55: 60%
      Entering block accumulator loop for bucket 57:
      bucket 54: 60%
      bucket 56: 10%
      bucket 53: 80%
      bucket 55: 70%
      bucket 54: 70%
      bucket 53: 90%
      bucket 55: 80%
      bucket 52: 100%
      Sorting block of length 613 for bucket 52
      (Using difference cover)
      bucket 51: 100%
      Sorting block of length 653 for bucket 51
      (Using difference cover)
      bucket 53: 100%
      bucket 55: 90%
      bucket 54: 80%
      Sorting block of length 614 for bucket 53
      (Using difference cover)
      bucket 57: 10%
      bucket 56: 20%
      Sorting block time: 00:00:00
      bucket 55: 100%
      Sorting block time: 00:00:00
    Returning block of 614 for bucket 52
    Returning block of 654 for bucket 51
      Sorting block of length 812 for bucket 55
      (Using difference cover)
      Sorting block time: 00:00:00
      bucket 54: 90%
      bucket 57: 20%
      bucket 56: 30%
      Sorting block time: 00:00:00
    Returning block of 615 for bucket 53
      bucket 54: 100%
    Returning block of 813 for bucket 55
      bucket 56: 40%
      bucket 57: 30%
      Sorting block of length 507 for bucket 54
      (Using difference cover)
    Getting block 58 of 60
      Reserving size (936) for bucket 58
    Getting block 59 of 60
      bucket 56: 50%
      bucket 57: 40%
      Calculating Z arrays for bucket 58
      Sorting block time: 00:00:00
      Reserving size (936) for bucket 59
    Returning block of 508 for bucket 54
      Calculating Z arrays for bucket 59
      Entering block accumulator loop for bucket 58:
    Getting block 60 of 60
      bucket 56: 60%
      Entering block accumulator loop for bucket 59:
      Reserving size (936) for bucket 60
      bucket 57: 50%
      Calculating Z arrays for bucket 60
      bucket 56: 70%
      Entering block accumulator loop for bucket 60:
      bucket 57: 60%
      bucket 58: 10%
      bucket 56: 80%
      bucket 59: 10%
      bucket 57: 70%
      bucket 60: 10%
      bucket 56: 90%
      bucket 58: 20%
      bucket 57: 80%
      bucket 56: 100%
      Sorting block of length 721 for bucket 56
      (Using difference cover)
      bucket 59: 20%
      bucket 60: 20%
      bucket 58: 30%
      Sorting block time: 00:00:00
    Returning block of 722 for bucket 56
      bucket 58: 40%
      bucket 57: 90%
      bucket 60: 30%
      bucket 59: 30%
      bucket 58: 50%
      bucket 59: 40%
      bucket 60: 40%
      bucket 58: 60%
      bucket 57: 100%
      bucket 60: 50%
      Sorting block of length 633 for bucket 57
      (Using difference cover)
      bucket 59: 50%
      bucket 58: 70%
      bucket 60: 60%
      Sorting block time: 00:00:00
    Returning block of 634 for bucket 57
      bucket 59: 60%
      bucket 60: 70%
      bucket 59: 70%
      bucket 58: 80%
      bucket 59: 80%
      bucket 60: 80%
      bucket 59: 90%
      bucket 60: 90%
      bucket 60: 100%
      Sorting block of length 754 for bucket 60
      (Using difference cover)
      bucket 59: 100%
      Sorting block of length 878 for bucket 59
      (Using difference cover)
      bucket 58: 90%
      Sorting block time: 00:00:00
    Returning block of 755 for bucket 60
      Sorting block time: 00:00:00
    Returning block of 879 for bucket 59
      bucket 58: 100%
      Sorting block of length 603 for bucket 58
      (Using difference cover)
      Sorting block time: 00:00:00
    Returning block of 604 for bucket 58


    Building a SMALL index
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.3.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.3.bt2
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.4.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.4.bt2
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.1.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.1.bt2
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.2.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.2.bt2
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.1.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.1.bt2
    Renaming /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.2.bt2.tmp to /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.2.bt2
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.01GB.  
      PID: 315;	Command: bowtie2-build;	Return code: 0;	Memory used: 0.01GB
    
    
    > `touch /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/_refgenie_build/t7_bowtie2_index__2.5.3.flag` (318)
    <pre>
    PID still exists but it's a zombie (pid=318)
    Warning: couldn't add memory use for process: 318
    </pre>
    Command completed. Elapsed time: 0:00:00. Running peak memory: 0.01GB.  
      PID: 318;	Command: touch;	Return code: 0;	Memory used: 0GB
    
    
    ### Pipeline completed. Epilogue
    *        Elapsed time (this run):  0:00:00
    *  Total elapsed time (all runs):  0:00:00
    *         Peak memory (this run):  0.0103 GB
    *        Pipeline completed time: 2025-07-06 20:28:51


    Exited Ebwt loop
    fchr[A]: 0
    fchr[C]: 10842
    fchr[G]: 19880
    fchr[T]: 30171
    fchr[$]: 39937
    Exiting Ebwt::buildToDisk()
    Returning from initFromVector
    Wrote 4207850 bytes to primary EBWT file: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.1.bt2.tmp
    Wrote 9992 bytes to secondary EBWT file: /var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.2.bt2.tmp
    Re-opening _in1 and _in2 as input streams
    Returning from Ebwt constructor
    Headers:
        len: 39937
        bwtLen: 39938
        sz: 9985
        bwtSz: 9985
        lineRate: 6
        offRate: 4
        offMask: 0xfffffff0
        ftabChars: 10
        eftabLen: 20
        eftabSz: 80
        ftabLen: 1048577
        ftabSz: 4194308
        offsLen: 2497
        offsSz: 9988
        lineSz: 64
        sideSz: 64
        sideBwtSz: 48
        sideBwtLen: 192
        numSides: 209
        numLines: 209
        ebwtTotLen: 13376
        ebwtTotSz: 13376
        color: 0
        reverse: 1
    Total time for backward call to driver() for mirror index: 00:00:00



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Asset <span style="color: #008000; text-decoration-color: #008000">'t7/bowtie2_index:2.5.3'</span> build succeeded                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2602" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2602</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added: <span style="color: #008000; text-decoration-color: #008000">'t7/bowtie2_index:2.5.3'</span>                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#773" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">773</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created alias directories:                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3515" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3515</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/t7/bowtie2_</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #800080; text-decoration-color: #800080">index/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">2.5.3</span>                                                                               <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Set default asset: <span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index:2.5.3'</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1640" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1640</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added asset: kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index:<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2.5</span>.<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span>                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2618" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2618</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Updated parents of <span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index:2.5.3'</span>                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#2856" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">2856</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Archiving asset: kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index:<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2.5</span>.<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span>                        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/archive/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/archive/manager.py#49" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">49</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Running: rsync -rvL --exclude <span style="color: #008000; text-decoration-color: #008000">'_refgenie_build'</span>                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/utils/archiving.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">archiving.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/utils/archiving.py#64" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">64</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7e</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">i2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/</span>                                                   <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_archive_demo_mthufo3u/kN9XHLKLS_</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/</span>                                                <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>



    building file list ... done
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.1.bt2
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.2.bt2
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.3.bt2
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.4.bt2
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.1.bt2
    kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.2.bt2
    
    sent 8447138 bytes  received 152 bytes  16894580.00 bytes/sec
    total size is 8445686  speedup is 1.00



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Running: tar --exclude <span style="color: #008000; text-decoration-color: #008000">'_refgenie_build'</span> -C                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/utils/archiving.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">archiving.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/utils/archiving.py#19" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">19</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7e</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">i2GH87H-qpQrkz8moPB/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">bowtie2_index</span> -cvf - <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2.5</span>.<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span> | pigz &gt;                                    <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_archive_demo_mthufo3u/kN9XHLKLS_</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
         <span style="color: #800080; text-decoration-color: #800080">u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">bowtie2_index__2.5.3.tgz</span>                        <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">               </span>
</pre>



    a 2.5.3
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.4.bt2
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.2.bt2
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.2.bt2
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.3.bt2
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.1.bt2
    a 2.5.3/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.rev.1.bt2



<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"></pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created asset archive at:                                                                    <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/archive/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/archive/manager.py#85" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">85</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_archive_demo_mthufo3u/kN9XHLKLS_u7</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
         <span style="color: #800080; text-decoration-color: #800080">ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">bowtie2_index__2.5.3.tgz</span>                            <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
</pre>






    Asset(name='2.5.3', description='Genome index for bowtie2, produced with bowtie2-build', size=8446757, updated_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 871146), path='data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index/2.5.3', digest='40a7b72a358850f722b6734a836b0fa8', recipe_id=2, asset_group_id=3, created_at=datetime.datetime(2025, 7, 6, 18, 28, 51, 871153))



Let's list the assets for the genome `t7` to verify that the `bowtie2_index` asset has been built successfully.



```python
refgenie.assets_table(genome_names=["t7"])[0]
```




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                   Refgenie assets. Source: local                   </span>
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Genome digest                    </span>┃<span style="font-weight: bold"> Asset group   </span>┃<span style="font-weight: bold"> Asset         </span>┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB │ fasta         │ samtools-1.21 │
│ kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB │ bowtie2_index │ 2.5.3         │
└──────────────────────────────────┴───────────────┴───────────────┘
</pre>




One of the assets was also archived (a neccessary step to serve the assets via the refgenie server). Let's list the archived assets.


```python
print(refgenie.archive.table())
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                                  Asset Archives                                                   </span>
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Digest                          </span>┃<span style="font-weight: bold"> Asset name                      </span>┃<span style="font-weight: bold"> Path                            </span>┃<span style="font-weight: bold"> Size      </span>┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ ddf6f41d9d21d404fe5c7f07adb2f2… │ kN9XHLKLS_u7ei2GH87H-qpQrkz8mo… │ /var/folders/18/3fc3jyt50sv9kq… │ 230.38 KB │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴───────────┘
</pre>



Asset `bowtie2_index` has been built successfully for the `dm6` genome, and automatically tagged with `2.5.3`, indicating the version of Bowtie2 software used (this behavior is encoded in the recipe).


## Interact with aliases

Let's list the aliases:


```python
refgenie.aliases_table()
```




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                           Genome aliases                            </span>
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Alias(es) </span>┃<span style="font-weight: bold"> Genome digest                    </span>┃<span style="font-weight: bold"> Genome description </span>┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ rCRSd-1   │ ZtAkf32sCUjeSl0KxVA5DVevklHDazQM │ Yeast genome 1     │
│ t7        │ kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB │ Genome of T7 phage │
└───────────┴──────────────────────────────────┴────────────────────┘
</pre>




Let's assign another alias to the same genome digest, this way we can refer to the same genome in multiple ways.


```python
t7_alias = refgenie.set_genome_alias(
    alias_name="Bacteriophage-T7",
    genome_digest="kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB",
    genome_description="My favorite genome",
)
fav_alias = refgenie.set_genome_alias(
    alias_name="myFavGenome",
    genome_digest="kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB",
    genome_description="My favorite genome",
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added alias: Bacteriophage-T7                                                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1153" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1153</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created alias directories:                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3515" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3515</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">Bacteriopha</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
         <span style="color: #ff00ff; text-decoration-color: #ff00ff">ge-T7</span>                                                                                     <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Added alias: myFavGenome                                                                  <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1153" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1153</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Created alias directories:                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#3515" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">3515</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">myFavGenome</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                </span>
</pre>



The new alias should be listed in the aliases:


```python
refgenie.aliases_table()
```




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                       Genome aliases                                        </span>
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Alias(es)                         </span>┃<span style="font-weight: bold"> Genome digest                    </span>┃<span style="font-weight: bold"> Genome description </span>┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ rCRSd-1                           │ ZtAkf32sCUjeSl0KxVA5DVevklHDazQM │ Yeast genome 1     │
│ t7, Bacteriophage-T7, myFavGenome │ kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB │ Genome of T7 phage │
└───────────────────────────────────┴──────────────────────────────────┴────────────────────┘
</pre>




The command not only creates a new alias, but also creates a symbolic links to the files in the `data` directory for that genome.

Conversely, alias removal will remove the symbolic links, but not the files in the `data` directory.


```python
refgenie.remove_alias("myFavGenome")
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Deleting alias files:                                                                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">events.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py#49" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">49</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/alias/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">myFavGenome</span>     <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Removed alias: myFavGenome                                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#1401" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1401</span></a>
</pre>



## Retrieve paths to assets

Most importantly, we can retrieve paths to refgenie-managed files.

All below commands will return the same path to the fasta file managed by Refgenie:


```python
print(refgenie.seek("t7", "fasta"))
print(refgenie.seek("Bacteriophage-T7", "fasta", "samtools-1.21"))
print(refgenie.seek("t7", "fasta", "samtools-1.21", "fasta"))
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta</span>
<span style="color: #800080; text-decoration-color: #800080">/samtools-1.21/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta</span>
<span style="color: #800080; text-decoration-color: #800080">/samtools-1.21/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa</span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/fasta</span>
<span style="color: #800080; text-decoration-color: #800080">/samtools-1.21/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB.fa</span>
</pre>



## Remove an asset

Let's remove the `bowtie2_index` asset for the `dm6` genome.


```python
refgenie.remove_asset_group(
    genome_name="t7", asset_group_name="bowtie2_index", force=True
)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Deleting archive files:                                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">events.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py#59" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">59</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_archive_demo_mthufo3u/kN9XHLKLS_u7e</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
         <span style="color: #800080; text-decoration-color: #800080">i2GH87H-qpQrkz8moPB/bowtie2_index/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">2.5.3</span>                                                       <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Deleting asset files:                                                                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">events.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/db/events.py#32" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">32</span></a>
         <span style="color: #800080; text-decoration-color: #800080">/var/folders/18/3fc3jyt50sv9kqx6hdqg5b600000gn/T/refgenie_demo_ugm8n45l/data/kN9XHLKLS_u7ei2G</span> <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
         <span style="color: #800080; text-decoration-color: #800080">H87H-qpQrkz8moPB/bowtie2_index/</span><span style="color: #ff00ff; text-decoration-color: #ff00ff">2.5.3</span>                                                          <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Removed asset group and all assets <span style="color: #008000; text-decoration-color: #008000">'kN9XHLKLS_u7ei2GH87H-qpQrkz8moPB/bowtie2_index'</span>        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">refgenie.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/refgenie.py#919" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">919</span></a>
</pre>



## Data channels

Refgenie supports data channels, which are used to allow third-party tool developers to expose their recipes and asset classes to Refgenie ecosystem.
In the simplest case, data channels is just a github repository with an index file that lists available asset classes and recipes, like so:

```yaml
asset_class:
  dir: asset_classes # optional, needed only if the asset classes are stored in a subdirectory
  files: # list of asset class files, relative to the index file (or directory)
    - fasta.yaml 
    - bowtie2_index.yaml
recipe:
  dir: recipes # optional, needed only if the recipes are stored in a subdirectory
  files: # list of recipe files, relative to the index file (or directory)
    - fasta.yaml
    - bowtie2_index.yaml
```

One such example is the [refgenie/recipes](https://github.com/refgenie/recipes/blob/refgenie1/index.yaml) repository, which can be added as a data channel to refgenie in the following way:


```python
data_channel = refgenie.data_channel.add(
    name="refgenie-recipes",
    type="http",
    index_address="https://refgenie.github.io/recipes/index.yaml",
    description="Refgenie recipes channel",
)

print(refgenie.data_channel.table())
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-style: italic">                                                   Data Channels                                                   </span>
┏━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> Name             </span>┃<span style="font-weight: bold"> Type </span>┃<span style="font-weight: bold"> Index Address                            </span>┃<span style="font-weight: bold"> Description              </span>┃<span style="font-weight: bold"> Credentials set </span>┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│<span style="color: #008080; text-decoration-color: #008080"> refgenie-recipes </span>│ http │ https://refgenie.github.io/recipes/inde… │ Refgenie recipes channel │ False           │
└──────────────────┴──────┴──────────────────────────────────────────┴──────────────────────────┴─────────────────┘
</pre>



Subsequently, the asset classes and recipes from the data channel can be listed and added to the refgenie instance.


```python
for asset_class in refgenie.data_channel.iter_asset_classes("refgenie-recipes"):
    try:
        refgenie.asset_class.add(asset_class)
    except Exception as e:
        print(e)

for recipe in refgenie.data_channel.iter_recipes("refgenie-recipes"):
    try:
        refgenie.recipe.add(recipe)
    except Exception as e:
        print(e)
        

```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">https://refgenie.github.io/recipes/index.yaml</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'abundant_sequences'</span> asset class                                                  <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bed'</span> asset class                                                                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bismark_bt1_index'</span> asset class                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bismark_bt2_index'</span> asset class                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'blacklist'</span> asset class                                                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bowtie1_index'</span> asset class                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">Asset class <span style="color: #008000; text-decoration-color: #008000">'bowtie2_index'</span> version <span style="color: #008000; text-decoration-color: #008000">'0.0.1'</span> already exists.
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bwa_index'</span> asset class                                                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'cellranger_reference'</span> asset class                                                <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'dbnsfp'</span> asset class                                                              <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'dbsnp'</span> asset class                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'ensembl_rb'</span> asset class                                                          <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'epilog_index'</span> asset class                                                        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">Asset class <span style="color: #008000; text-decoration-color: #008000">'fasta'</span> version <span style="color: #008000; text-decoration-color: #008000">'0.0.1'</span> already exists.
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'feat_annotation'</span> asset class                                                     <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'gtf'</span> asset class                                                                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'hisat2_index'</span> asset class                                                        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'kallisto_index'</span> asset class                                                      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'refgene_anno'</span> asset class                                                        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_index'</span> asset class                                                        <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_partial_sa_index'</span> asset class                                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_sa_index'</span> asset class                                                     <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'small_rna'</span> asset class                                                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'star_index'</span> asset class                                                          <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'suffixerator_index'</span> asset class                                                  <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'tallymer_index'</span> asset class                                                      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'tgMap'</span> asset class                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/asset_class/manager.py#71" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">71</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> HTTP Request: <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">GET</span> <span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">https://refgenie.github.io/recipes/index.yaml</span> <span style="color: #008000; text-decoration-color: #008000">"HTTP/1.1 200 OK"</span>          <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">_client.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/httpx/_client.py#1027" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">1027</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'abundant_sequences'</span> recipe                                                      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bed12'</span> recipe                                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bismark_bt1_index'</span> recipe                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bismark_bt2_index'</span> recipe                                                       <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'blacklist'</span> recipe                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bowtie1_index'</span> recipe                                                           <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">Recipe <span style="color: #008000; text-decoration-color: #008000">'bowtie2_index'</span> version <span style="color: #008000; text-decoration-color: #008000">'0.0.1'</span> already exists.
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'bwa_index'</span> recipe                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'cellranger_reference'</span> recipe                                                    <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'dbnsfp'</span> recipe                                                                  <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'dbsnp'</span> recipe                                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'ensembl_gtf'</span> recipe                                                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'ensembl_rb'</span> recipe                                                              <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'epilog_index'</span> recipe                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">Recipe <span style="color: #008000; text-decoration-color: #008000">'fasta'</span> version <span style="color: #008000; text-decoration-color: #008000">'0.0.1'</span> already exists.
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'fasta_txome'</span> recipe                                                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'feat_annotation'</span> recipe                                                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'gencode_gtf'</span> recipe                                                             <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'hisat2_index'</span> recipe                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'kallisto_index'</span> recipe                                                          <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'refgene_anno'</span> recipe                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_index'</span> recipe                                                            <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_partial_sa_index'</span> recipe                                                 <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'salmon_sa_index'</span> recipe                                                         <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'small_rna'</span> recipe                                                               <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'star_index'</span> recipe                                                              <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'suffixerator_index'</span> recipe                                                      <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'tallymer_index'</span> recipe                                                          <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Registered <span style="color: #008000; text-decoration-color: #008000">'tgMap'</span> recipe                                                                   <a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">manager.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/refgenie/resource_manager/recipe/manager.py#113" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">113</span></a>
</pre>



Alternatively, the same can be achieved by running the following CLI command:

```bash
refgenie1 data_channel sync refgenie-recipes --exists-ok
```

## SeqCol interface

Refgenie also provides a `SeqCol` interface, which is standard for working with sequence collections. More details on this interface can be found on the [SeqCol project website](https://seqcol.readthedocs.io/en/latest/).
Under the hood, refgenie uses the `SeqCol` digests to uniquely identify genomes.


```python
d1 = refgenie.refget_db_agent.seqcol.add_from_fasta_file(
    "/Users/stolarczyk/code/refgenie1/tests/data/rCRSd.fa"
).digest
d2 = refgenie.refget_db_agent.seqcol.add_from_fasta_file(
    "/Users/stolarczyk/code/refgenie1/tests/data/rCRSd-extra.fa"
).digest
refgenie.refget_db_agent.compare_digests(d1, d2)
```


<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> SeqCol: <span style="color: #808000; text-decoration-color: #808000">digest</span>=<span style="color: #008000; text-decoration-color: #008000">'jthDpfNIgzM5AGJlOkRtfnky4rXMBIUP'</span>                                            <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">agents.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py#242" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">242</span></a>
         <span style="color: #808000; text-decoration-color: #808000">sorted_name_length_pairs_digest</span>=<span style="color: #008000; text-decoration-color: #008000">'AYk42eFmfBv_Q3GRVXWRKv2BWJ-2rWaN'</span>                           <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
</pre>




<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #000080; text-decoration-color: #000080">INFO    </span> SeqCol: <span style="color: #808000; text-decoration-color: #808000">digest</span>=<span style="color: #008000; text-decoration-color: #008000">'smiTbD3jP5EwF4DNWVm0c6DGKRlFHfas'</span>                                            <a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">agents.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///Users/stolarczyk/code/refgenie1/.venv/lib/python3.12/site-packages/refget/agents.py#242" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">242</span></a>
         <span style="color: #808000; text-decoration-color: #808000">sorted_name_length_pairs_digest</span>=<span style="color: #008000; text-decoration-color: #008000">'C4yiaCS1eR4cxiQCg4tInGAIiJ8rG6UG'</span>                           <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">             </span>
</pre>






    {'attributes': {'a_only': [],
      'b_only': [],
      'a_and_b': ['lengths',
       'name_length_pairs',
       'names',
       'sequences',
       'sorted_sequences']},
     'array_elements': {'a': {'lengths': 1,
       'name_length_pairs': 1,
       'names': 1,
       'sequences': 1,
       'sorted_sequences': 1},
      'b': {'lengths': 2,
       'name_length_pairs': 2,
       'names': 2,
       'sequences': 2,
       'sorted_sequences': 2},
      'a_and_b': {'lengths': 1,
       'name_length_pairs': 1,
       'names': 1,
       'sequences': 1,
       'sorted_sequences': 1},
      'a_and_b_same_order': {'lengths': True,
       'name_length_pairs': True,
       'names': True,
       'sequences': True,
       'sorted_sequences': True}}}


