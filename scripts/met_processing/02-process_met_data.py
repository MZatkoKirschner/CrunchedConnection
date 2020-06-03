#!/opt/anaconda3/bin/python3

import pandas as pd
import numpy as np
from datetime import timedelta

rawDataDir = '../../data/raw/met/'
outdir = '../../data/processed/met/'

#Functions
def convertTzone(df,tzone):
    """Convert utc to local"""
    df.index = df.index.tz_convert(tzone).tz_localize(None)
    df.index.rename('timeLocal',inplace=True)

    return df

#Read in timezone file
tzoneFile = pd.read_csv(rawDataDir+'airport_timezones_subset.csv',skiprows=1)
tzoneFile['iata_code'] = 'K' + tzoneFile['iata_code']
tzoneFile.rename(columns={'iata_code':'airport'},inplace=True)

#Manually deal with exceptions (in some cases, U.S callsign doesn't start with 'K')
tzoneFile['airport'].loc[tzoneFile['airport']=='KANC'] = 'PANC' #Anchorage
tzoneFile['airport'].loc[tzoneFile['airport']=='KHLN'] = 'PHLN' #Honolulu

#Add in missing timezones for airport
tzoneMissFile = pd.read_csv(rawDataDir+'MissingAirportTzones.csv')

#Merge airport timezone files together
tzonetmp = [tzoneFile,tzoneMissFile]
tzones = pd.concat(tzonetmp)

#Drop 'windows_tz' variable for now and just use 'iana_tz' for timezone shift
tzones.drop('windows_tz',inplace=True,axis=1)


years = ['2015','2016','2017','2018','2019']
#years = ['2019']

for year in years:
    print(year)

    #Contains majority of airports
    dfmost = pd.read_hdf(rawDataDir+str(year)+'_met.h5',key='met')

    #Contains 18 airports that were originally missed
    dfmore = pd.read_hdf(rawDataDir+str(year)+'_met_moreSites.h5',key='met')

    #Combine all airports into one dataframe
    dftmp = [dfmost,dfmore]
    df = pd.concat(dftmp)
    df.drop_duplicates(inplace=True)

    #Columns are wacky, for now 'model' is model runtime, 'runtime' is forecast times
    #Trim dataset down, then fix this
    df.model = pd.to_datetime(df.model)
    df.runtime = pd.to_datetime(df.runtime)
    df['ftime-rtime'] = df.runtime-df.model

    dfTrim = df[(df['ftime-rtime']>=pd.Timedelta('24 hours'))&(df['ftime-rtime']<=pd.Timedelta('30 hours'))]

    #Fix column issues
    dfTrim.drop(['station','model','ftime-rtime','ftime','t06','i06','sky','swh','lcb','pzr','slv',
        'typ','gst','pra'],axis=1,inplace=True)
    dfTrim.index.rename('airport',inplace=True)
    dfTrim.rename(columns={'runtime':'timeUTC','n_x':'tmpF','tmp':'dptF','dpt':'CC','cld':'dir','wdr':'spd',
        'wsp':'6hPrecPrb','p06':'12hPrecPrb','p12':'6hQntPrec','q06':'12hQntPrec','q12':'6hTsPrb',
        't12':'snow','snw':'ceil','cig':'visib','vis':'obstruc','obv':'fzRnPrb',
        'poz':'snowPrb','pos':'precTyp','s06':'prbRain','ppl':'prbSnow','psn':'prbFzRn',
        't03':'gust'},inplace=True)

    #Separate thunderstorm probabilities in separate columns
    dfTrim['6hTsPrb'].replace(np.NaN,'NaN/NaN',inplace=True)
    dfTrim[['6hrTsPrb_15mi','6hrSvrTsPrb_25mi']] = dfTrim['6hTsPrb'].str.split('/',expand=True)
    dfTrim.drop('6hTsPrb',inplace=True,axis=1)

    #Join time zone data into dfTrim
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

    #Save to csv file
    dfMrgTzone.to_csv(outdir+year+'_ProcessedMet.csv')
