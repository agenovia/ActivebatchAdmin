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

Search a root key and gather details into a pandas dataframe
```
import pandas as pd
from Handlers.connection_manager import ABConnectionManager

def get_dicts(result_set):
    _d = []
    for result in result_set:
        _dict = {'ID': result.ID,
                 'Name': result.Name,
                 'FullPath': result.FullPath,
                 'ObjectType': result.ObjectType,
                 'Enabled': result.Enabled,
                 'Owner': result.Owner,
                 'LastRun': result.LastInstanceExecutionDateTime,
                 'NextRun': result.NextScheduledExecutionDateTime,
                 'CreationDateTime': result.CreationDateTime
                 }
        _d.append(_dict)
    return _d

df = pd.DataFrame()
key = 'PATH OR ID'
with ABConnectionManager(server='SC-AB-T01', version=12) as ab:
    results = ab.Search(key, GetFullObjects=True)
    details = get_dicts(results)
    df = df.append(details)
        
```
