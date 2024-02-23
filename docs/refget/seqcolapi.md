# How to add a seqcolapi router

## Goal

You are writing a FastAPI application and want it to implement the refget sequence collections API. The `refget` package provides the ability to do that.


```python
# Import the seqcol_router from refget
from refget import seqcol_router

# Create your app in the usual way, then attach the imported router
app = FastAPI()
app.include_router(seqcol_router, prefix="/seqcol")

# Set up the databse connection for the seqcol henge that holds your collections
schenge = ...  

# Finally, attach the database object, to the app. This is how the router will
# get access to the database to serve the endpoints
app.state.schenge = schenge
```
