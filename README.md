# CMS OMS API python client

This client is a recommended way to access CMS OMS data from your scripts.

## Install

```
git clone ssh://git@gitlab.cern.ch:7999/cmsoms/oms-api-client.git
cd oms-api-client
python3 -m pip install -r requirements.txt
python3 setup.py install --user
```

## Update
```
cd oms-api-client
git pull
python3 setup.py install --user
```

## Build RPM
```
cd oms-api-client
python3 setup.py bdist_rpm
```

## Requirements

auth_oidc() requires registered CERN OpenID application. It can be created
by any user on the Application Portal: https://application-portal.web.cern.ch/
When doing the step of SSO Registration, select option allowing application to
request tokens itself. Copy client id and client secret and use them as parameters
of auth_oidc().

You will need to request rights for token exchange with the target application ID (audience parameter, see below for available IDs),
and/or ask cmsoms-developers to grant token access to your application from the Application Portal.

Audience parameter defaults to application ID 'cmsoms'. For testing, athese instance indentifier are available:
```
"cmsoms-dev-0183"
"cmsoms-dev-0184"
"cmsoms-int-0185"
```

Once production OMS moves to OpenID, it will have identifier:
```
"cmsoms-prod"
```

# Examples

### Fetch all eras
```
from omsapi import OMSAPI

#fill your values
my_app_id='omsapi_test_id'
my_app_secret='2398938-30389039-33'

omsapi = OMSAPI()
omsapi.auth_oidc(my_app_id,my_app_secret)

# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
```

### Fetch Last Run
```
from omsapi import OMSAPI

omsapi = OMSAPI()
omsapi.auth_oidc(my_app_id,my_app_secret)

# Create a query
q = omsapi.query("runs")

# Chain filters
q.paginate(page=1, per_page=1).sort("run_number", asc=False)

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
```

[More examples](examples/)

# Client API

## OMSAPI Class

### Create API client
constructor OMSAPI(*url*, *version="v1"*) - set API endpoint and version (recommended to keep default values)

Example:
```
from omsapi import OMSAPI

omsapi = OMSAPI()
```

### Create query
omsapi.query(*resource_name*) - set resource name (runs/fills/lumisections/...)

Returns query object

Example:
```
q = omsapi.query("eras")
```

## OMSAPIQuery class

### Projection
.attrs(*[attribute_names]*) - set only those attribute names you need in response

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
.sort(*attribute_name*, *asc=True*) - set attribute name and direction

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

presentation_timestamp - changes representation of datetime attribtutes

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

### Set verbose
.set_verbose(True/False) - print debug information or not

Example:
```
q.set_verbose(False)
```

### Set query attribute validation
.set_validation(True/False) - check or not for typos in filters/projection/sorting

Example:
```
.set_validation(False)
```

### Query is ready. Execute it!
.data() - execute query and fetch data.

Returns requests.Response object

Example:
```
resp = q.data()

print(resp.json())
```

### Interested how query (URL) looks like?
.data_query() - Contruct URL to be used to query data from API

Returns String

Example:
```
url = q.data_query()

print(url)
```

## Alternative Auth option

Instead of auth with OpenID you can use Kerberos authentication.

This works **ONLY** with CERN managed CC7 machines.

```
sudo yum install cern-get-sso-cookie
```

see example [07-sso-krb.py](examples/07-sso-krb.py)
