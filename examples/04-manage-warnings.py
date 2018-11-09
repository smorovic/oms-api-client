""" Simple example.
    Shows error handling
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")

# Create a query.
q = omsapi.query("eras")

q.attrs(["mistype", "name", "name"])    # Warning: Attribute [mistype] does not exist
q.filter("names", "2018")               # Warning: Attribute [names] does not exist

# Silent mode
q.set_verbose(False)

q.sort("nono")      # No warning

# Verbose mode
q.set_verbose(True)

q.sort("nono")      # Warning: Attribute [nono] does not exist

# Execute query & fetch data
response = q.data()

# Display JSON data
# print(response.json())
