""" Simple example.
    Fetch list of eras
"""

from __future__ import print_function
from omsapi import OMSAPI

# Authenticate using OAuth token exchange of the user-owned application (needs to be authorized by OMS admins)

#integration OMS (retry in 2 seconds in case of ConnectionError)
omsapi = OMSAPI("http://vocms0185.cern.ch/agg/api", "v1", cert_verify=False, retry_on_err_sec=2)
omsapi.auth_oidc("your-client-app-identifier", "your-client-app-secret", audience="cmsoms-int-0185")

#production OMS:
#omsapi = OMSAPI("http://cmsoms.cern.ch/agg/api", "v1", cert_verify=True)
#omsapi.auth_oidc("your-client-app-identifier", "your-client-app-secret", audience="cmsoms-prod")

# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
