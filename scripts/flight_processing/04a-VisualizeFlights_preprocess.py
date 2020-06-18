#!/usr/bin/env python
import numpy as np
import pandas as pd

#This script pre-processes flight data so we can visualize the total number
# flight counts for each individual city pair.
# Map with lines creates, and lines are thicker for routes with higher counts

#Read file containing airport lat/lon values
latlonfile = '../../data/raw/flights/airport_latlon_subset.csv'
latlon = pd.read_csv(latlonfile)

#Read in annual flight data
flightfile = '../../data/raw/flights/2019_allFlightData.csv'
flight = pd.read_csv(flightfile)

#Process flight data to get it ready for lat/lon pairing
flight = flight[['ORIGIN','DEST']]
flightunique = flight.drop_duplicates(keep='first')

#Update airport code for future merging
flightunique['ORIGIN'] = 'K' + flightunique['ORIGIN']
flightunique['DEST'] = 'K' + flightunique['DEST']

#Merge flight data with origin airport lat/lon information
joinOrig = flightunique.merge(latlon, left_on='ORIGIN', right_on='airport')
joinOrig.rename(columns={'lat':'DepLat','lon':'DepLon'},inplace=True)
joinOrig.drop(['airport'],axis=1,inplace=True)

#Merge flight data with departure airport lat/lon information
joined = joinOrig.merge(latlon, left_on='DEST', right_on='airport')
joined.drop(['airport'],axis=1,inplace=True)
joined.rename(columns={'lat':'ArrLat','lon':'ArrLon'},inplace=True)

#Get unique counts of flights into dataframe
flightgrouped = flight.groupby(['ORIGIN','DEST']).size().reset_index()
flightgrouped.rename(columns={0:'NbFlights'},inplace=True)

#Minor fomatting for consistency
flightgrouped['ORIGIN'] = 'K' + flightgrouped['ORIGIN']
flightgrouped['DEST'] = 'K' + flightgrouped['DEST']
flightgrouped['ORIGIN'].loc[flightgrouped['ORIGIN']=='KANC'] = 'PANC' #Anchorage
flightgrouped['ORIGIN'].loc[flightgrouped['ORIGIN']=='KHLN'] = 'PHLN' #Honolulu
flightgrouped['DEST'].loc[flightgrouped['DEST']=='KANC'] = 'PANC' #Anchorage
flightgrouped['DEST'].loc[flightgrouped['DEST']=='KHLN'] = 'PHLN' #Honolulu

#Merge lat/lon data with flight count data
merged = pd.merge(joined, flightgrouped,  how='left', left_on=['ORIGIN','DEST'], right_on = ['ORIGIN','DEST'])
merged['NbFlights'] = merged['nb_Flights'].astype(int)
merged.drop(['ORIGIN','DEST'],axis=1,inplace=True)

#Save to csv
outpath = '../../data/raw/flights/'
merged.to_csv(outpath+'FlightRouteCounts.csv')
