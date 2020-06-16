#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

#This script pre-processes flight data so we can make a visualization

#Read raw flight data
latlonfile = '../../data/raw/flights/airport_latlon_subset.csv'
latlon = pd.read_csv(latlonfile)

#Read airport data for 1 year
flightfile = '../../data/raw/flights/2019_allFlightData.csv'
flight = pd.read_csv(flightfile)

#Process flight data to get it ready for lat/lon pairing
flight = flight[['ORIGIN','DEST']]
flightunique = flight.drop_duplicates(keep='first')

# flightunique['ORIGIN'] = 'K' + flightunique['ORIGIN']
# flightunique['DEST'] = 'K' + flightunique['DEST']
#
# joinOrig = flightunique.merge(latlon, left_on='ORIGIN', right_on='airport')
# joinOrig.rename(columns={'lat':'DepLat','lon':'DepLon'},inplace=True)
# joinOrig.drop(['airport'],axis=1,inplace=True)
#
# joined = joinOrig.merge(latlon, left_on='DEST', right_on='airport')
# joined.drop(['airport'],axis=1,inplace=True)
# joined.rename(columns={'lat':'ArrLat','lon':'ArrLon'},inplace=True)
#
# #Get unique counts of flights into dataframe
# flightgrouped = flight.groupby(['ORIGIN','DEST']).size().reset_index()
# flightgrouped.rename(columns={0:'NbFlights'},inplace=True)
#
# #Formatting
# flightgrouped['ORIGIN'] = 'K' + flightgrouped['ORIGIN']
# flightgrouped['DEST'] = 'K' + flightgrouped['DEST']
# flightgrouped['ORIGIN'].loc[flightgrouped['ORIGIN']=='KANC'] = 'PANC' #Anchorage
# flightgrouped['ORIGIN'].loc[flightgrouped['ORIGIN']=='KHLN'] = 'PHLN' #Honolulu
# flightgrouped['DEST'].loc[flightgrouped['DEST']=='KANC'] = 'PANC' #Anchorage
# flightgrouped['DEST'].loc[flightgrouped['DEST']=='KHLN'] = 'PHLN' #Honolulu
#
# #Merge lat/lon data with flight count data
# merged = pd.merge(joined, flightgrouped,  how='left', left_on=['ORIGIN','DEST'], right_on = ['ORIGIN','DEST'])
# merged['NbFlights'] = merged['nb_Flights'].astype(int)
# merged.drop(['ORIGIN','DEST'],axis=1,inplace=True)
#
# #Save to csv
# outpath = '../../data/raw/flights/'
# merged.to_csv(outpath+'FlightRouteCounts.csv')
