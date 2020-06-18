#!/opt/anaconda3/bin/python3

import pandas as pd
import numpy as np
from datetime import timedelta

filepath = '../data/processed/'
filepathFlight = '../data/processed/flights/'
filepathMet = '../data/processed/met/'
outdir = '../data/processed/merged/'

#years = [2015, 2016, 2017, 2018, 2019]
years = [2017]

for year in years:

    #Read in met data
    fileMet = filepathMet+str(year)+'_ProcessedMet.csv'
    dfMet = pd.read_csv(fileMet)

    #Handle missing value flags
    dfMet['dir'].loc[dfMet['dir']==990] = np.NaN
    dfMet['spd'].loc[dfMet['spd']==99] = np.NaN
    dfMet['tmpF'].loc[dfMet['tmpF']==999.0] = np.NaN
    dfMet['dptF'].loc[dfMet['dptF']==999.0] = np.NaN

    #Updates to make merging more smooth
    dfMet['timeLocal'] = pd.to_datetime(dfMet['timeLocal'])
    dfMet['ORIGIN'] = dfMet['airport']
    dfMet['DEST'] = dfMet['airport']

    # #Read in flight data
    #fileFlight= filepathFlight+str(year)+'_ProcessedFlightData.csv'
    fileFlight= filepathFlight+str(year)+'_ProcessedFlightData_withNAS_lateAircraft_cancellations.csv'
    dfFlight = pd.read_csv(fileFlight)

    # #Update origin and deparature names for easier merging
    dfFlight['ORIGIN'] = 'K' + dfFlight['ORIGIN']
    dfFlight['ORIGIN'].loc[dfFlight['ORIGIN']=='KANC'] = 'PANC' #Anchorage
    dfFlight['ORIGIN'].loc[dfFlight['ORIGIN']=='KHNL'] = 'PHLN' #Honolulu

    dfFlight['DEST'] = 'K' + dfFlight['DEST']
    dfFlight['DEST'].loc[dfFlight['DEST']=='KANC'] = 'PANC' #Anchorage
    dfFlight['DEST'].loc[dfFlight['DEST']=='KHNL'] = 'PHLN' #Honolulu

    #Get origin and departure time in better time format
    #Perform string manipulations on schedule arrival and deparature time to pull hour and minute
    #Create valid departure and arrival timestamps
    dfFlight['FL_DATE'] = pd.to_datetime(dfFlight['FL_DATE'])

    dfFlight['CRS_DEP_TIME'] = dfFlight['CRS_DEP_TIME'].astype(str).str.zfill(4)
    dfFlight['DEP_HR'] = dfFlight['CRS_DEP_TIME'].str[:2]
    dfFlight['DEP_MIN'] = dfFlight['CRS_DEP_TIME'].str[-2:]
    dfFlight['DEP_TIME'] = pd.to_datetime({'year':dfFlight['FL_DATE'].dt.year,
        'month':dfFlight['FL_DATE'].dt.month,'day':dfFlight['FL_DATE'].dt.day,
        'hour':dfFlight['DEP_HR'],'minute':dfFlight['DEP_MIN']})

    dfFlight['CRS_ARR_TIME'] = dfFlight['CRS_ARR_TIME'].astype(str).str.zfill(4)
    dfFlight['ARR_HR'] = dfFlight['CRS_ARR_TIME'].str[:2]
    dfFlight['ARR_MIN'] = dfFlight['CRS_ARR_TIME'].str[-2:]

    dfFlight['ARR_TIME'] = pd.to_datetime({'year':dfFlight['FL_DATE'].dt.year,
        'month':dfFlight['FL_DATE'].dt.month,'day':dfFlight['FL_DATE'].dt.day,
        'hour':dfFlight['ARR_HR'],'minute':dfFlight['ARR_MIN']})

    dfFlight.drop(['CRS_DEP_TIME','CRS_ARR_TIME','Unnamed: 38','DEP_HR','DEP_MIN',
        'ARR_HR','ARR_MIN','FL_DATE'],inplace=True,axis=1)

    #Deal with overnight flights
    dfFlight.loc[(dfFlight['DEP_TIME'] - dfFlight['ARR_TIME']) > pd.Timedelta('6 hours'),'ARR_TIME'] = dfFlight['ARR_TIME'] + pd.Timedelta('1 day')

    # #Start the merging process

    #First, merge met and flights based on ORIGIN city and departure time
    dfMet.sort_values(by=['timeLocal'],inplace=True)
    dfFlight.sort_values(by=['DEP_TIME'],inplace=True)
    dfMergeD = pd.merge_asof(left=dfFlight,right=dfMet,left_on=['DEP_TIME'],right_on=['timeLocal'],
        by=['ORIGIN'])

    #Drop columns no longer needed and rename met columns so we know those are tied to departure
    dfMergeD.drop(['timeLocal','airport','DEST_y'],axis=1,inplace=True)
    dfMergeD.rename(columns={'DEST_x':'DEST','tmpF':'tmpF_D','dptF':'dptF_D','CC':'CC_D','dir':'dir_D',
        'spd':'spd_D','6hPrecPrb':'6hPrecPrb_D','12hPrecPrb':'12hPrecPrb_D',
        '6hQntPrec':'6hQntPrec_D','12hQntPrec':'12hQntPrec_D','snow':'snow_D',
        'ceil':'ceil_D','visib':'visib_D','obstruc':'obstruc_D','fzRnPrb':'fzRnPrb_D',
        'snowPrb':'snowPrb_D','6hrTsPrb_15mi':'6hrTsPrb_15mi_D',
        '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_D'},inplace=True)

    #Next merge met and flights based on destination city and arrival time
    dfMergeD.sort_values(by=['ARR_TIME'],inplace=True)
    dfMergeDA = pd.merge_asof(left=dfMergeD,right=dfMet,left_on=['ARR_TIME'],right_on=['timeLocal'],
            by=['DEST'])

    dfMergeDA.drop(['timeLocal','airport','ORIGIN_y'],axis=1,inplace=True)
    dfMergeDA.rename(columns={'ORIGIN_x':'ORIGIN','tmpF':'tmpF_A','dptF':'dptF_A','CC':'CC_A','dir':'dir_A',
            'spd':'spd_A','6hPrecPrb':'6hPrecPrb_A','12hPrecPrb':'12hPrecPrb_A',
            '6hQntPrec':'6hQntPrec_A','12hQntPrec':'12hQntPrec_A','snow':'snow_A',
            'ceil':'ceil_A','visib':'visib_A','obstruc':'obstruc_A','fzRnPrb':'fzRnPrb_A',
            'snowPrb':'snowPrb_A','6hrTsPrb_15mi':'6hrTsPrb_15mi_A',
            '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_A'},inplace=True)

    dfMergeDA.sort_values(by='DEP_TIME')

    dfMergeDA.drop_duplicates(inplace=True)

    dfMergeDA.to_csv(outdir+str(year)+'_FlightMetMerged.csv',index=False)
