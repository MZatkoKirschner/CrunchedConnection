#!/opt/anaconda3/bin/python3

import pandas as pd
import glob

#Create annual files and export raw files for EDA. Subset these files for ML in 03 script

#years = ['2015','2016','2017','2018','2019']
years = ['2019']

dfAnn = []

for year in years:
    obsdirs = glob.glob('rawMonthlyData/'+str(year)+'-*.csv')

    dfAnnTmp = []

    for obsdir in obsdirs:
        filename = obsdir.split("/")[1]
        year = filename.split("-")[0]
        #month = filename.split("-")[1].split(".")[0]

        #Read monthly data
        df = pd.read_csv(obsdir)

        #Append monthly data together
        dfAnnTmp.append(df)

    #Concatenate months together
    dfAnn = pd.concat(dfAnnTmp)

    #Sort by date
    dfAnn.sort_values(by='FL_DATE',inplace=True)

    #Save to csv
    dfAnn.to_csv(str(year)+'_allFlightData.csv',index=False)
