#!/opt/anaconda3/bin/python3

import pandas as pd
import csv
import urllib
from datetime import timedelta

#Notes about forecast weather data:
# 1. For now, only use forecasts from NAM because it has higher resolution than GFS
# 2. For now, download different forecast periods but only use 24-30 hour forecast in ML model

outdir = '../../data/raw/met/'

#Functions
def downloadMet(call,time):
    """Downloads forecast met data"""

    url = 'https://mesonet.agron.iastate.edu/mos/csv.php?station='+call+'&valid='+time

    try:
        data = pd.read_csv(url)
    except urllib.error.HTTPError as ex:
        print('Problem:', ex)

    return data

#Read in unique callsign list from flight data
callsignsFile = '../../data/raw/flights/callsigns_unique.txt'
callsigns = pd.read_csv(callsignsFile,header=None,names=['callsign'])

#Drop rows that are not callsigns
callsigns = callsigns[callsigns.callsign != 'DEST_CITY_NAME']
callsigns = callsigns[callsigns.callsign != 'ORIGIN']

#Add 'K' to callsign so it is consistent with the met airport callsigns
callsigns = 'K' + callsigns

#Manually deal with exceptions (in some cases, U.S callsign doesn't start with 'K')
callsigns.loc[callsigns['callsign']=='KANC'] = 'PANC' #Anchorage
callsigns.loc[callsigns['callsign']=='KHLN'] = 'PHLN' #Honolulu


#Loop over callsign and date to download met for each airport

#Reprocessed plane data, realized 18 sites were missing. Re-run scripts with these missing sites
#callsignsMore = ['KACK','KAKN','KATY','KBFM','KBKG','KDLG','KEFD','KENV','KFLO',

#years = [2019,2018,2017,2016,2015]
years = [2019]

for year in years:
    rawMet = []
    endyear = year+1
    date = pd.to_datetime(str(year)+'-01-01')
    enddate = pd.to_datetime(str(endyear)+'-01-15')

    while date <= enddate:

        dateFormat = str(date.year)+'-'+str(date.month).zfill(2)+'-'+str(date.day).zfill(2)

        #for i in range(0,len(callsignsMore)):
        for i in range(0,len(callsigns)):
            station = callsigns.iloc[i].values[0]
            #station = callsignsMore[i]

            rawMettmp = downloadMet(station,dateFormat)

            #Only use NAM model (this is not really station - columns are slightly mismatched)
            rawMettmp = rawMettmp[rawMettmp.station == 'NAM']

            #Append different sites together
            rawMet.append(rawMettmp)

        date += timedelta(9)
        print ('date =' + str(date))

    met = pd.concat(rawMet)
    met.to_hdf(outdir+str(year)+'_met.h5', key='met', mode='w')
    #met.to_hdf(str(year)+'_met_moreSites.h5', key='met', mode='w')
