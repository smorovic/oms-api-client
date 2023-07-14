""" Simple example.
    get last global run, get last lumisection
"""

from __future__ import print_function
import time
from omsapi import OMSAPI

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False, verbose=False)

# Authenticate using kerberos
omsapi.auth_krb()

# Create a query.
q = omsapi.query("runs")

q.attrs(["run_number", "fill_number", "start_time", "end_time", "last_lumisection_number"])
q.filter('sequence','GLOBAL-RUN') # get only global runs, no minidaq runs
q.sort("run_number", asc=False).paginate(per_page = 1)  # get last run only

# Execute query & fetch data
response = q.data()

# show run info
runInfo = response.json()['data'][0]['attributes']
print()
print('last global run:')
print('run# {0} (fill# {1})'.format(runInfo['run_number'], runInfo['fill_number']))
if runInfo['end_time'] == None:
    print('still ongoing')
else:
    print( 'last lumisection: {0}'.format(runInfo['last_lumisection_number']))
print()


# query lumisection data
q = omsapi.query("lumisections")
q.attrs(['lumisection_number','start_time','end_time'])
q.filter("run_number", runInfo['run_number'])
q.filter('cms_active', True)
q.sort("lumisection_number", asc=False).paginate(per_page = 1)  # get last ls only

while True:
    lsInfo = q.data().json()['data'][0]['attributes']
    print('\rlumisection# {0}'.format(lsInfo['lumisection_number']))
    print('from {0}'.format(lsInfo['start_time']))
    print('to {0}'.format(lsInfo['end_time']))
    print()
    print('sleeping for 25secs ...', end='', flush=True)
    time.sleep(25)