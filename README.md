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

## Requirements

Download certificate (*.p12) from https://ca.cern.ch/ca/ (New Grid User Certificate)

**Certificate must be passwordless**

```
mkdir -p ~/private

# Leave Import Password blank
# PEM passphrase is required to be set
openssl pkcs12 -clcerts -nokeys -in myCertificate.p12 -out ~/private/usercert.pem
openssl pkcs12 -nocerts -in myCertificate.p12 -out ~/private/userkey.tmp.pem
openssl rsa -in ~/private/userkey.tmp.pem -out ~/private/userkey.pem
```

# Examples

### Fetch all eras
```
from omsapi import OMSAPI

omsapi = OMSAPI()
omsapi.auth_cert()

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
omsapi.auth_cert()

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

### Authenticate using certificate
omsapi.auth_cert(*usercert*, *userkey*) - set user certificate path (recommended to keep default values)

* usercert - full path to certificate file
* userkey - full path to certificate key file

Example:
```
omsapi.auth_cert()
```

Set these values ONLY if:
* your user certificate is NOT in `~/private` or `~/.globus` folders
* certificate names ane NOT `usercert.pem` and `userkey.pem`

Example:
```
omsapi.auth_cert("/home/myuser/.cert/crt.pem", "/home/myuser/.cert/key.pem") 
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

## Alternative Auth option

Instead of auth with certificate you can use Kerberos authentication.

This works **ONLY** with CERN managed CC7 machines.

```
sudo yum install cern-get-sso-cookie
```

see example [07-sso-krb.py](examples/07-sso-krb.py)