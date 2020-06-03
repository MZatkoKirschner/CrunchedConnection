import pandas as pd
import glob

rawDataDir = '../../data/raw/flights/'

#years = [2015,2016,2017,2018,2019]
years = [2019]

for year in years:

    df = pd.read_csv(rawDataDir+str(year)+'_allFlightData.csv')

    #Drop features not needed for ML
    df.drop(['TAIL_NUM','OP_CARRIER_FL_NUM','ORIGIN_CITY_NAME','DEST_CITY_NAME',
        'DEP_TIME','DEP_DELAY','DEP_DELAY_GROUP','TAXI_OUT','WHEELS_OFF','WHEELS_ON',
        'TAXI_IN','ARR_TIME','ARR_DELAY','CANCELLED','DIVERTED','CRS_ELAPSED_TIME',
        'ACTUAL_ELAPSED_TIME','AIR_TIME','FLIGHTS','DISTANCE','CARRIER_DELAY',
        'WEATHER_DELAY','NAS_DELAY','SECURITY_DELAY','LATE_AIRCRAFT_DELAY'],inplace=True,axis=1)

    outpath = '../../data/processed/flights/'
    df.to_csv(outpath+str(year)+'_ProcessedFlightData.csv',index=False)
