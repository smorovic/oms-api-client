# CMS OMS API python client

## Install
```
sudo yum install cern-get-sso-cookie

git clone ssh://git@gitlab.cern.ch:7999/cmsoms/oms-api-client.git
cd oms-api-client
python setup.py install --user
```

## Update
```
cd oms-api-client
git pull
python setup.py install --force
```

# FAQ

### How to install cern-get-sso-cookie on Ubuntu?
Download latest script version: https://linuxsoft.cern.ch/cern/centos/7/cern/x86_64/repoview/cern-get-sso-cookie.html

Follow these steps to install rpm on Ubuntu: https://www.rosehosting.com/blog/how-to-install-rpm-packages-on-ubuntu/

# Usage

### Create API client
constructor OMSAPI(*url*, *version="v1"*) - set API endpoint and version

Example:
```
omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")
```
Note that "http://cmsomsapi.cern.ch:8080/api" is **NOT official** endpoint and must not be used in production.

### Create query
omsapi.query(*resource_name*) - set resource name (runs/fills/lumisections/...)

Returns query object

Example:
```
q = omsapi.query("eras")
```

### Projection
.attrs(*[attribute_names]*) - set only those attribute names you need in response.

Example:
```
q.attrs(["delivered_luminosity", "fill_number"])
```

### Filtering
.filter(*attribute_name*, *value*, *operator="EQ"*) - filters attribute againts value using operator

Supported operators: ["EQ", "NEQ", "LT", "GT", "LE", "GE", "LIKE"]

Examples:
```
q.filter("nun_number", 320149)
```
or
```
q.filter("fill_number", 5000, "GT").filter("fill_number", 5500, "LT")
```

.filters(*filters*) - apply multiple filters at once. Same as calling .filter() multiple times

Examples:

see `examples/09-multiple-filters.py`

### Sorting
.sort(*attribute_name*, *asc=True*) - set attribute name and direction.

Example:
```
q.sort("run_number").sort("lumisection_number", asc=False)
```
Note: order matters!

### Pagination
.paginate(*page=1*, *per_page=10*) - set page number and page size

Example:
```
q.paginate(2, per_page=10)
```

### Include
.include(*flag*) - include special flags to a query

Supported flags: ["meta", "presentation_timestamp"]

meta - includes meta information about resource into response object

presentation_timestamp - changes representation of datetime attribtutes.

Example:
```
q.include("meta")
```

### Custom Query parameters
.custom(*parameter_name*, *parameter_value*) - set custom parameter key:value pair

Example:
```
q.custom("group[size]", 100)
```

### Query is ready. Execute it!
.data() - execute query and fetch data.

Returns requests.Response object

Example
```
resp = q.data()

print(resp.json())
```


# Examples

### Fetch all eras
```
# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
```

### Fetch Last Run
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
