""" Simple example.
    Fetch list of eras
"""

from __future__ import print_function
from omsapi import OMSAPI

#note: use cert_verify = False in case certificate chain is not installed
omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=True)
omsapi.auth_krb()

# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
