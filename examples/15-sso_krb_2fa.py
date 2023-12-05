#!/bin/env python3
""" Simple example.
    Fetch list of eras
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)

# Authenticate using kerberos
omsapi.auth_krb_2fa()

# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
