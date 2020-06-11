import numpy as np
import pandas as pd

#Read airport data for 1 year
flightfile = '../../data/raw/flights/2019_allFlightData.csv'
flight = pd.read_csv(flightfile)

flightSub = flight[['ORIGIN_AIRPORT_ID','ORIGIN','DEST_AIRPORT_ID','DEST','DISTANCE',
    'DISTANCE_GROUP','OP_UNIQUE_CARRIER']]

#Create sorted list of individual airports, airport_ID, and region
flightSubAirports = flight[['ORIGIN_AIRPORT_ID','ORIGIN']].drop_duplicates(keep='first')
flightSubAirports.rename(columns={'ORIGIN_AIRPORT_ID':'airport_ID','ORIGIN':'airport'},inplace=True)
flightSubAirports.sort_values(by=['airport'],inplace=True)

#Read in airport region data (region by timezone)
regionFile = '../../data/raw/met/airport_regions.csv'
regions = pd.read_csv(regionFile,skiprows=1)
regions.drop(columns=['iana_tz','windows_tz'],axis=1,inplace=True)

#Merged datasets
result = pd.merge(flightSubAirports,regions,left_on=['airport'],right_on=['iata_code'])
result.drop('iata_code',axis=1,inplace=True)

#Save to csv
result.to_csv('Airports.csv',index=False)

#Now get unique list of city pairs and pair with distance and distance group
flightPairs = flightSub[['ORIGIN','DEST','DISTANCE','DISTANCE_GROUP']]
flightPairsunique = flightPairs.drop_duplicates(keep='first')
flightPairsunique.to_csv('AirportPairs_WithDistance.csv',index=False)
