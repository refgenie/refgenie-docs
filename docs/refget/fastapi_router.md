# How to add refget endpoints to an application

## Goal

You are writing a FastAPI application and want it to implement the refget sequence collections API.
The `refget` package provides a function to automatically add the necessary routes.
You can find a [working example of this](https://github.com/refgenie/refget/blob/master/seqcolapi/main.py) in the refget repository.

This is a minimal example of how it works:

```python
# Import the seqcol_router from refget
from refget import create_refget_router
from refget.agents import RefgetDBAgent

# Create your app in the usual way.
# Create a router with create_refget_router and attach it to your app.
# Parameterize it to choose routes.

app = FastAPI()
refget_router = create_refget_router(sequences=False, pangenomes=False)
app.include_router(refget_router, prefix="/seqcol")

# Set up the database connection
# A RefgetDBAgent connects to your SQL database of collections
dbagent = RefgetDBAgent()  # Configured via env vars

# Finally, attach the database object, to the app. This is how the router will
# get access to the database to serve the endpoints
app.state.dbagent = dbagent
```

Practically, here's one way to do this:

```python
from refget import seqcol_router
app = FastAPI(...)
refget_router = create_refget_router(sequences=False, pangenomes=False)
app.include_router(refget_router)

def create_global_dbagent():
    from refget.agents import RefgetDBAgent
    global dbagent
    dbagent = RefgetDBAgent()  # Configured via env vars
    return dbagent

def main(injected_args=None):
    ...
    create_global_dbagent()
    app.state.dbagent = dbagent
```