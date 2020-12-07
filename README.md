# ActivebatchAdmin
Scripts and libraries I use for work to administer ActiveBatch

## Requirements
```
pip install pywin32
```

## Python Usage

Search example
```
from Handlers.connection_handler import ABConnectionManager

server = "SERVER_NAME"
version = 12  # int
with ABConnectionManager(server, version) as ab:
  items = ab.Search('some_plan')
  for item in items:
    # do something
    # most actions require a persistent connection hence the context
```
