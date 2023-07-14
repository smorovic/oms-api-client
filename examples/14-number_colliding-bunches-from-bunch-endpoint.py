""" 
- check for invalid number of colliding bunches: null
- for fills with wrong data calculate colliding bunches from bunch endpoint
- print result 

"""

import time
from omsapi import OMSAPI

omsapi = OMSAPI("http://localhost:8080/api", "v1", cert_verify=False, verbose=False)

# Authenticate using kerberos
#omsapi.auth_krb()

# Create a query.
q = omsapi.query("fills")

q.attrs(["fill_number", "bunches_colliding"])

q.filter('bunches_colliding','null') 
q.filter('stable_beams',True)
q.sort("fill_number", asc=False).paginate(per_page = 200)  # get last 200 fills

# Execute query & fetch data
response = q.data()

# show run info
print('{fills} with bunches_colliding = null'.format(fills=len(response.json()['data'])))
fills_iterator = map(lambda fill : fill['attributes']['fill_number'], response.json()['data'])
for fill in fills_iterator:
    q = omsapi.query("bunches")
    q.filter('fill_number',fill) 
    q.paginate(per_page=10000)
    # Execute query & fetch data
    response = q.data()
    colliding_bunches = 0;
    for bunch in response.json()['data']:
        if bunch['attributes']['beam_1_configured'] and bunch['attributes']['beam_2_configured']:
            colliding_bunches += 1
    print('fill# {fill}: {colliding_bunches} colliding bunches'.format(fill=fill,colliding_bunches=colliding_bunches))
print()


