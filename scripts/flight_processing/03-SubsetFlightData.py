import pandas as pd
import glob

#This script subsets annual flight data and generates output for merging with met data

#Define input directory
rawDataDir = '../../data/raw/flights/'

years = [2015,2016,2017,2018,2019]

for year in years:

    #Read annual flight data
    df = pd.read_csv(rawDataDir+str(year)+'_allFlightData.csv')

    #Remove rows that have carrier, NAS, security, late aircraft delays
    #This ensures that dataset contains 1) flights delayed by weather and 2) on-time flights
    df = df[~(df['CARRIER_DELAY']>0)]
    df = df[~(df['SECURITY_DELAY']>0)]

    #Drop features not needed for ML
    df.drop(['OP_CARRIER_FL_NUM','ORIGIN_CITY_NAME','DEST_CITY_NAME',
            'ARR_TIME','ARR_DELAY','AIR_TIME','FLIGHTS','CARRIER_DELAY',
            'SECURITY_DELAY'],inplace=True,axis=1)

    #Save subset of flight data to csv for merging with met data
    outpath = '../../data/processed/flights/'
    df.to_csv(outpath+str(year)+'_ProcessedFlightData_withNAS_lateAircraft_cancellations.csv',index=False)
