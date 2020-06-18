#!/opt/anaconda3/bin/python3

import pandas as pd
import numpy as np
from datetime import timedelta

#This script processes annual met files so they are ready for pairing with flight dataset

#Define input and output directories
rawDataDir = '../../data/raw/met/'
outdir = '../../data/processed/met/'

#Function to convert from UTC to local time for each airport location
def convertTzone(df,tzone):
    """Convert utc to local"""
    df.index = df.index.tz_convert(tzone).tz_localize(None)
    df.index.rename('timeLocal',inplace=True)

    return df

#Read in file that contains timezones for each airport
tzoneFile = pd.read_csv(rawDataDir+'airport_timezones_subset.csv',skiprows=1)
tzoneFile['iata_code'] = 'K' + tzoneFile['iata_code']
tzoneFile.rename(columns={'iata_code':'airport'},inplace=True)

#Manually deal with exceptions (in some cases, U.S callsign doesn't start with 'K')
tzoneFile['airport'].loc[tzoneFile['airport']=='KANC'] = 'PANC' #Anchorage
tzoneFile['airport'].loc[tzoneFile['airport']=='KHLN'] = 'PHLN' #Honolulu

#Add in timezones for airports that were originally missing timezone
tzoneMissFile = pd.read_csv(rawDataDir+'MissingAirportTzones.csv')

#Merge airport timezone files together
tzonetmp = [tzoneFile,tzoneMissFile]
tzones = pd.concat(tzonetmp)

#Drop 'windows_tz' variable for now and just use 'iana_tz' for timezone shift
tzones.drop('windows_tz',inplace=True,axis=1)

years = ['2020','2019','2018','2017','2016','2015']

for year in years:
    print(year)

    #Read in annual met data files
    df = pd.read_hdf(rawDataDir+str(year)+'_met.h5',key='met')
    df.drop_duplicates(inplace=True)

    #Raw data columns are wacky, for now 'model' is model runtime, 'runtime' is forecast times
    #Trim dataset down, then fix this
    df.model = pd.to_datetime(df.model)
    df.runtime = pd.to_datetime(df.runtime)
    df['ftime-rtime'] = df.runtime-df.model

    #Only keep forecast times between 24 and 30 hours out
    dfTrim = df[(df['ftime-rtime']>=pd.Timedelta('24 hours'))&(df['ftime-rtime']<=pd.Timedelta('30 hours'))]

    #Fix wonky column issues now that we have a smaller file
    dfTrim.drop(['station','model','ftime-rtime','ftime','t06','i06','sky','swh','lcb','pzr','slv',
        'typ','gst','pra'],axis=1,inplace=True)
    dfTrim.index.rename('airport',inplace=True)
    dfTrim.rename(columns={'runtime':'timeUTC','n_x':'tmpF','tmp':'dptF','dpt':'CC','cld':'dir','wdr':'spd',
        'wsp':'6hPrecPrb','p06':'12hPrecPrb','p12':'6hQntPrec','q06':'12hQntPrec','q12':'6hTsPrb',
        't12':'snow','snw':'ceil','cig':'visib','vis':'obstruc','obv':'fzRnPrb',
        'poz':'snowPrb','pos':'precTyp','s06':'prbRain','ppl':'prbSnow','psn':'prbFzRn',
        't03':'gust'},inplace=True)

    #Separate thunderstorm probabilities into separate columns
    dfTrim['6hTsPrb'].replace(np.NaN,'NaN/NaN',inplace=True)
    dfTrim[['6hrTsPrb_15mi','6hrSvrTsPrb_25mi']] = dfTrim['6hTsPrb'].str.split('/',expand=True)
    dfTrim.drop('6hTsPrb',inplace=True,axis=1)

    #These columns appear to always be missing so just drop them
    dfTrim.drop(['prbRain','prbSnow','prbFzRn','gust','precTyp'],inplace=True,axis=1)

    #Join time zone data into met dataframe
    dfMrg = dfTrim.join(tzones.set_index('airport'),on='airport')

    #Convert from UTC to local time
    dfMrg.reset_index(inplace=True)
    dfMrg.set_index('timeUTC',inplace=True)

    uniqueTzones = dfMrg['iana_tz'].unique()

    dfAppTmp = []
    for uniqueTzone in uniqueTzones:
        dfsub = dfMrg[dfMrg['iana_tz']==uniqueTzone]
        dfTmp = convertTzone(dfsub,uniqueTzone)
        dfAppTmp.append(dfTmp)
    dfMrgTzone = pd.concat(dfAppTmp)

    #Drop UTC time from dataset
    dfMrgTzone.drop(['iana_tz'],axis=1,inplace=True)

    #Sort by airport and date and then save out to csv file for each year
    dfMrgTzone.reset_index(inplace=True)
    dfMrgTzone.sort_values(by=['airport','timeLocal'],inplace=True)
    dfMrgTzone.set_index('timeLocal',inplace=True)

    #Some met variables are reported once or twice a day. Use persistence to fill in these columns.
    #If first row of airport missing values, fill values with 0 so information from previous site not used
    uniqueAirports = dfMrgTzone.airport.unique()
    for uniqueAirport in uniqueAirports:
        dfMrgTzone[dfMrgTzone['airport']==uniqueAirport].iloc[0].fillna(0)

    #Convert t-storm columns to float so NaN is recognized
    dfMrgTzone['6hrTsPrb_15mi'] = dfMrgTzone['6hrTsPrb_15mi'].astype(float)
    dfMrgTzone['6hrSvrTsPrb_25mi'] = dfMrgTzone['6hrSvrTsPrb_25mi'].astype(float)

    #Replace NaN values with persistence values
    dfMrgTzone['6hPrecPrb'].fillna(method='ffill',inplace=True)
    dfMrgTzone['6hQntPrec'].fillna(method='ffill',inplace=True)
    dfMrgTzone['12hPrecPrb'].fillna(method='ffill',inplace=True)
    dfMrgTzone['12hQntPrec'].fillna(method='ffill',inplace=True)
    dfMrgTzone['snow'].fillna(method='ffill',inplace=True)
    dfMrgTzone['6hrTsPrb_15mi'].fillna(method='ffill',inplace=True)
    dfMrgTzone['6hrSvrTsPrb_25mi'].fillna(method='ffill',inplace=True)

    #Set snow, snowPrb, and freezing rain prob to 0 for summer months when not reported
    dfMrgTzone['fzRnPrb'].fillna(0,inplace=True)
    dfMrgTzone['snowPrb'].fillna(0,inplace=True)

    #Take care of missing value flags
    dfMrgTzone['dir'].loc[dfMrgTzone['dir']==990] = np.NaN
    dfMrgTzone['spd'].loc[dfMrgTzone['spd']==99] = np.NaN
    dfMrgTzone['tmpF'].loc[dfMrgTzone['tmpF']==999.0] = np.NaN
    dfMrgTzone['dptF'].loc[dfMrgTzone['dptF']==999.0] = np.NaN

    #Save to csv file
    dfMrgTzone.to_csv(outdir+year+'_ProcessedMet.csv')
