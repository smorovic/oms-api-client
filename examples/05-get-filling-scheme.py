#!/usr/bin/env python

""" Get filling scheme (go to dip lhc database table if filling scheme is null in fill endpoint (no stable beams)
"""

from __future__ import print_function
import sys
import os
import argparse
import time

if not os.path.exists( os.getcwd() + 'omsapi.py' ):
    sys.path.append('..')  # if you run the script in the more-examples sub-folder 
from omsapi import OMSAPI

parser = argparse.ArgumentParser( 
    description='python script using OMS API to get filling scheme (from dip lhc database table if not in WBM table)', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument( '--fill', type = int, help = 'get filling scheme for fill# FILL' )
group.add_argument( '-n', help = 'get filling scheme for the last N fills' )
group.add_argument( '--currentFill', action = 'store_true', help = 'for the ongoing fill: check if the filling scheme in WBM table is still up-to-date' )

args = parser.parse_args()

omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
omsapi.auth_krb()

# Create a query.
wbm = omsapi.query("fills")
if args.n:
    wbm.per_page = int(args.n)

wbm.attrs(["fill_number","injection_scheme","end_time"])
wbm.sort("start_time", asc=False)

if args.n:
    
    fillingSchemes = {}

    # Execute query and fetch data
    resp = wbm.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']
    for row in data:
        attr = row['attributes']
        fillingSchemes[attr['fill_number']] = { 'injection_scheme' : attr['injection_scheme'] }

    for fill in fillingSchemes:
        if fillingSchemes[fill]['injection_scheme']: 
            fillingSchemes[fill]['inFillTable'] = True
        else:
            fillingSchemes[fill]['inFillTable'] = False
            lhc = omsapi.query("lhcrunconfigurations")
            lhc.filter( 'fill_number', fill ).sort('dip_time', asc=False)
            data = lhc.data().json()['data']
            for row in data:
                attr = row['attributes']
                if attr['active_injection_scheme']:
                    fillingSchemes[fill]['injection_scheme'] = attr['active_injection_scheme']
                    break
            
    for key in sorted(fillingSchemes.iterkeys()):
        print( '{}: {}'.format(key, fillingSchemes[key]['injection_scheme']) )
            
else: 
               
    wbm.per_page = 1
    wbm.verbose = False

    lhc = omsapi.query("lhcrunconfigurations")
    lhc.verbose = False
    lhc.sort('dip_time', asc=False)
    
    if args.fill:
        wbm.filter( 'fill_number', args.fill )
    
    data = wbm.data().json()['data']
    fill = data[0]['attributes']
    fillingSchemeInWbm = fill['injection_scheme']
    
    lhc.clear_filter().filter( 'fill_number', fill['fill_number'] )
    data = lhc.data().json()['data']
    for row in data:
        attr = row['attributes']
        if attr['active_injection_scheme']:
            actualFillingScheme = attr['active_injection_scheme']
            break

    print( 'fill: {}'.format( fill['fill_number'] ))
    if actualFillingScheme == fillingSchemeInWbm:
        print( 'filling scheme: {}'.format( actualFillingScheme ) )
    else:
        print( 'filling scheme has to be updated!!!')
        print( 'in wbm: {}'.format( fillingSchemeInWbm) )
        print( 'LHC: {}'.format(actualFillingScheme))
            
            
        

