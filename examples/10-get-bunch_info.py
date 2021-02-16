#!/usr/bin/env python

""" Get bunch info for a given fill
"""

from __future__ import print_function
import sys
import os
import argparse
import re
from omsapi import OMSAPI

parser = argparse.ArgumentParser( 
    description='python script using OMS API to get bunch info for a given fill', 
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

parser.add_argument( 'fill', type = int, help = 'fill for which bunch info should be retrieved' )
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument( '--all', action = 'store_true', help = 'print info for all bunches' )
group.add_argument( '--configured', action = 'store_true', help = 'print info for bunches where intensity in at least one of the beams is expected' )
group.add_argument( '--pilot', action = 'store_true', help = 'print info for all bunches with beam in only one the two beams' )

args = parser.parse_args()
if args.configured:
    args.pilot = True

omsapi = OMSAPI("https://vocms0183.cern.ch/agg/api", "v1") # this is the OMS development machine, don't use for production
omsapi.auth_krb()


# Create a query.
query = omsapi.query("bunches")
query.per_page = 4000  # to get all bunches in one go

# Filter fill
query.filter("fill_number", args.fill )

query.include('meta')

# Execute query and fetch data
resp = query.data()
oms = resp.json()   # all the data returned by OMS
data = oms['data']
print( 'bunch#      lumi     beam 1    beam 2')
colliding_bunches = 0
lumi = 0
filled_bunches = [0, 0, 0]
intensity = [0, 0, 0]
linePerBunch = '{bunch:4d}  {lumi:12.8f}  {beam_1:8.6f}  {beam_2}'
for row in data:
    bunch = row['attributes']
    if args.all:
        print( linePerBunch.format( bunch = bunch['bunch_number'],
                                    lumi = bunch['initial_lumi'],
                                    beam_1 = bunch['intensity_beam_1'],
                                    beam_2 = bunch['intensity_beam_2'] ) )
    if bunch['beam_1_configured'] and bunch['beam_2_configured']:
        colliding_bunches += 1
        intensity[1] += bunch['intensity_beam_1']
        intensity[2] += bunch['intensity_beam_2']
        lumi += bunch['initial_lumi']
        if args.configured:
            print( linePerBunch.format( bunch = bunch['bunch_number'],
                                            lumi = bunch['initial_lumi'],
                                            beam_1 = bunch['intensity_beam_1'],
                                            beam_2 = bunch['intensity_beam_2'] ) )
    elif bunch['beam_1_configured']:
        filled_bunches[1] += 1
        intensity[1] += bunch['intensity_beam_1']
        if args.pilot:
            print( linePerBunch.format( bunch = bunch['bunch_number'],
                                            lumi = bunch['initial_lumi'],
                                            beam_1 = bunch['intensity_beam_1'],
                                            beam_2 = bunch['intensity_beam_2'] ) )
    elif bunch['beam_2_configured']:
        filled_bunches[2] += 1
        intensity[2] += bunch['intensity_beam_2']
        if args.pilot:
            print( linePerBunch.format( bunch = bunch['bunch_number'],
                                            lumi = bunch['initial_lumi'],
                                            beam_1 = bunch['intensity_beam_1'],
                                            beam_2 = bunch['intensity_beam_2'] ) )

print()
print( 'beam 1: {} pilot bunches'.format( filled_bunches[1] ))
print( '  intensity: {:8.3f} {}'.format( intensity[1], oms['meta']['fields']['intensity_beam_1']['units'] ))
print()
print( 'beam 2: {} pilot bunches'.format( filled_bunches[2] ))
print( '  intensity: {:8.3f} {}'.format( intensity[2], oms['meta']['fields']['intensity_beam_2']['units'] ))
print()
print( '{} colliding bunches'.format( colliding_bunches ))
print( '  lumi: {:8.3f} {}'.format( lumi, oms['meta']['fields']['initial_lumi']['units'] ))
