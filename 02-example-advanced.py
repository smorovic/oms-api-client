""" Advanced Example.
    Fetch last 100 lumisections of a run 320149
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")

ls_query = omsapi.query("lumisections")

# Build a query
ls_query.filter("run_number", 320149) # Default operator is EQ (Equals)

# Chain filters
ls_query.sort("lumisection_number", asc=False).paginate(page=1, per_page=100)

# Execute query & fetch data
response = ls_query.data()

# Display JSON data
print(response.json())
