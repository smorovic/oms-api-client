""" Full Example.

    Fetch only two attributes "run_number" and "start_time" from Run resource
    where run_number is between 300000 and 310000 in descending order.
    And paginate.
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
omsapi.auth_krb()


# Create a query.
runs_query = omsapi.query("runs")

# Projection. Specify attributes you want to fetch
runs_query.attrs(["run_number", "start_time"])

# Filter range
runs_query.filter("run_number", 300000, operator="GT") # Default operator is EQ (Equals)
runs_query.filter("run_number", 310000, operator="LT")

# Chain filters. Sort by run_runber in descending order. Include meta information into response
runs_query.sort("run_number", asc=False).include("meta")

# Execute query and fetch data
resp = runs_query.data()

# Pretty-print data
print(resp.json())

# Reuse previous query. Set second page. Fetch data
resp = runs_query.paginate(page=2).data()

# BAM! Second page
print(resp.json())
