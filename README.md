CMS OMS API python client

Install
```
pip install -r requirements.txt
```

```
from omsapi import OMSAPI

omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")

```

Simple Query Example
```
# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
```

Fetch Last Run
```
# Create a query
q = omsapi.query("runs")

# Chain filters
q.paginate(page=1, per_page=1).sort("run_number", asc=False)

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
```

