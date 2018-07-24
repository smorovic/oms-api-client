""" Simple example.
    Fetch list of eras
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")

# Create a query.
q = omsapi.query("eras")

# Execute query & fetch data
response = q.data()

# Display JSON data
print(response.json())
