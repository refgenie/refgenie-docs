# How to add a seqcolapi router

## Goal

You are writing a FastAPI application and want it to implement the refget sequence collections API.
The `refget` package provides the ability to do that.


```python
# Import the seqcol_router from refget
from refget import seqcol_router
from refget.agents import RefgetDBAgent

# Create your app in the usual way, then attach the imported router
app = FastAPI()
app.include_router(seqcol_router, prefix="/seqcol")

# Set up the database connection
# You need a RefgetDBAgent, which will connect to your SQL database where the collections are stored
dbagent = RefgetDBAgent()  # Configured via env vars

# Finally, attach the database object, to the app. This is how the router will
# get access to the database to serve the endpoints
app.state.dbagent = dbagent
```

Practically, here's one way to do this:

```python
from refget import seqcol_router
app = FastAPI(...)
app.include_router(seqcol_router)

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