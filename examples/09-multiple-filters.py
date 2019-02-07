""" Advanced Example. Apply multiple filters at once
    Fetch fills between 7485 and 7490
"""

from __future__ import print_function
from omsapi import OMSAPI

omsapi = OMSAPI("http://cmsomsapi.cern.ch:8080/api", "v1")

# Build a query
query = omsapi.query("fills")

# Create multiple filters
my_filters = [{
    "attribute_name": "fill_number",
    "value": 7485,
    "operator": "GE"
},
    {
    "attribute_name": "fill_number",
    "value": 7490,
    "operator": "LE"
}]

# Apply these filters at once. Basically same as calling .filter() multiple times
query.filters(my_filters)

# Execute query & fetch data
response = query.data()

# Display JSON data
print(response.json())
