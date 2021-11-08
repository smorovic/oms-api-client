#!/usr/bin/env python

""" Get maximum rate of L1 trigger algo bits
"""

from __future__ import print_function
import sys
import os
import argparse
import re

if not os.path.exists( os.getcwd() + 'omsapi.py' ):
    sys.path.append('..')  # if you run the script in the more-examples sub-folder 
from omsapi import OMSAPI

parser = argparse.ArgumentParser( 
    description='python script using OMS API to get maximum rate of L1 trigger algos', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument( 'run', type = int, help = 'run for which rates should be retrieved' )
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument( '--pattern', help = 'regexp pattern for algos for which max rate will be retrieved, example: ".*EG.*"' )
group.add_argument( '--algo', help = 'name of algorithm for which max rate will be retrieved' )
group.add_argument( '--bits', nargs='+', help = 'list of algo bits for which max rate will be retrieved')

args = parser.parse_args()

omsapi = OMSAPI('http://cmsoms.cms/agg/api/','v1')


triggerBits = []


if args.bits:
    for bit in args.bits:
        triggerBits.append( bit )
else:
    # Create a query.
    query = omsapi.query("l1algorithmtriggers")
    query.per_page = 1000  # to get all names in one go

    # Projection. Specify attributes you want to fetch
    query.attrs(["name","bit"])

    # Filter run
    query.filter("run_number", args.run )

    # Execute query and fetch data
    resp = query.data()
    oms = resp.json()   # all the data returned by OMS
    data = oms['data']
    for row in data:
        algo = row['attributes']
        if args.pattern:
            if re.match( args.pattern, algo['name'] ):
                triggerBits.append( algo['bit'] )
        elif args.algo:
            if algo['name'] == args.algo:
                triggerBits.append( algo['bit'] )
            
            



# Create a query.
query = omsapi.query("l1algorithmtriggers")
query.per_page = 10000  # to get all LS in one go

# Projection. Specify attributes you want to fetch
query.attrs(["name","bit","pre_dt_rate"])

for bit in triggerBits:
    query.clear_filter().filter("run_number", args.run ).filter("bit", bit)  # returns data per lumisection
    data = query.data().json()['data']
    query.verbose = False
    max = 0.0
    for ls in data:
        if ls['attributes']['pre_dt_rate'] > max:
            max = ls['attributes']['pre_dt_rate']
    print('max rate: {rate:8.1f} Hz    bit {bit:3d} {algo}'.format( rate = round(max), 
                                                                    bit = data[0]['attributes']['bit'],
                                                                    algo = data[0]['attributes']['name'] ) )

# let's check the mean rates
for bit in triggerBits:
    query.clear_filter().filter("run_number", args.run ).filter("bit", bit).custom('group[granularity]','run')  # returns mean value over run or lumisection range
    data = query.data().json()['data']
    print('mean rate: {rate:8.1f} Hz    bit {bit:3d} {algo}'.format( rate = data[0]['attributes']['pre_dt_rate'],
                                                                    bit = data[0]['attributes']['bit'],
                                                                    algo = data[0]['attributes']['name'] ) )


