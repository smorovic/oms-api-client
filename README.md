# CMS OMS API python client

This client is a recommended way to access CMS OMS data from your scripts.

## Install

```
git clone ssh://git@gitlab.cern.ch:7999/cmsoms/oms-api-client.git
cd oms-api-client
python3 -m pip install -r requirements.txt
python3 setup.py install --user
```

## Update (CC7)
```
cd oms-api-client
git pull
python3 setup.py install --user
```

## Build RPM (CC7/python 3.6):
```
cd oms-api-client
python3.6 setup.py bdist_rpm --python python3.6 --release 0.cc7
```

## Build RPM (CC8/python 3.8):
```
cd oms-api-client
python3.8 setup.py bdist_rpm --python python3.8 --release 0.cc8
```

## Requirements

auth_oidc() requires registered CERN OpenID application. It can be created
by any user on the Application Portal: https://application-portal.web.cern.ch/
When doing the step of SSO Registration, select option allowing application to
request tokens itself. Copy client id and client secret and use them as parameters
of auth_oidc().

You will need to request rights for token exchange with the target application ID (audience parameter, see below for available IDs).
After creating the application, click on the new application -> `SSO Registration` -> `Token Exchange Permissions` button in the portal.
There you can request token exchange, by specifying target application ID (use same as audience parameter). We also advise to send a mail to
cmsoms-developers@cern.ch or cmsoms-operations@cern.ch to ask responsible maintainers to approve your application request.

Audience parameter defaults to application ID 'cmsoms-prod'. Corresponding IDs for OMS instances are:
```
cmsoms-int-0184 - for Development access
cmsoms-int-0185 - for Integration access
cmsoms-prod - for Production access
```

Production OMS is currently not using OpenID. Once all current clients are ready to migrate to OpenID, it wil be activated. For development
prior to this, other instances should be used for development.

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
constructor OMSAPI(*url*, *version="v1"*, cert_verify=True|False, retry_on_err_sec=0) - set API endpoint and version (recommended to keep default values, retry delay optional)

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

This depends on cern-get-sso-cookie RPM which works **ONLY** with CERN managed CC7 and CC8 machines (lxplus and OMS wbmportal hostgroup machines).

Installation, if available:
```
sudo yum install cern-get-sso-cookie
```

see example [07-sso-krb.py](examples/07-sso-krb.py)
