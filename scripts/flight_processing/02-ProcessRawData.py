#!/opt/anaconda3/bin/python3

import pandas as pd
import glob

#Concatenate monthly files into annual files and export raw files for EDA.
#Subset these files for ML in following script

rawDataDir = '../../data/raw/flights/'

years = ['2015','2016','2017','2018','2019']

dfAnn = []

for year in years:
    obsdirs = glob.glob(rawDataDir+'rawMonthlyData/'+str(year)+'*.csv')

    dfAnnTmp = []

    for obsdir in obsdirs:
        filename = obsdir.split("/")[6]

        #Read monthly data
        df = pd.read_csv(obsdir)

        #Append monthly data together
        dfAnnTmp.append(df)

    #Concatenate months together
    dfAnn = pd.concat(dfAnnTmp)

    #Sort by date
    dfAnn.sort_values(by='FL_DATE',inplace=True)

    #Save to csv
    dfAnn.to_csv(rawDataDir+str(year)+'_allFlightData.csv',index=False)
