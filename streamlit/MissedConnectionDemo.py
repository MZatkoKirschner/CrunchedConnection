#!/opt/anaconda3/bin/python3

import streamlit as st
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier

st.title('Clean Connection')
st.write('Use this tool 2-3 days before your flight to determine if it is likely that your flight connection will be missed due to weather')

file = '../data/processed/merged/2019_FlightMetMerged.csv'
df = pd.read_csv(file)

#Gather User Inputs
UserDepartureYear = st.selectbox("Select Departure Year",(2018,2019,2020))
UserDepartureMonth = st.selectbox("Select Departure Month",list(range(1,13)))
UserDepartureDay = st.selectbox("Select Departure Day",list(range(1,32)))

UserOrigin = st.selectbox("Select Departure Airport", df['ORIGIN'].unique())
UserScheduledDepartureTimetmp = st.selectbox("Select Scheduled Depature Time (local time)",list(range(1,24)))
UserScheduledDepartureTime = str(UserScheduledDepartureTimetmp)+':00'

UserConnectingAirport = st.selectbox("Select Connecting Airport", df['ORIGIN'].unique())
UserScheduledArrivalTimetmp = st.selectbox("Select Scheduled Arrival Time at Connecting Airport (local time)",list(range(1,24)))
UserScheduledArrivalTime = str(UserScheduledArrivalTimetmp)+':00'

UserDestinationAirport = st.selectbox("Select Final Destination Airport", df['ORIGIN'].unique())
UserScheduledFinalTimetmp = st.selectbox("Select Scheduled Arrival Time at Final Destination (local time)",list(range(1,24)))
UserScheduledFinalTime = str(UserScheduledFinalTimetmp)+':00'

UserArrivalYear = UserDepartureYear
UserArrivalMonth = UserDepartureMonth
UserArrivalDay = UserDepartureDay

st.write("User input now being ingested into ML algorithm")

# --- behind the scenes ----

#Read met data
metfile = '../data/processed/met/2019_ProcessedMet.csv'
dfMet = pd.read_csv(metfile)

#Formatting met data to help with merge
dfMet['timeLocal'] = pd.to_datetime(dfMet['timeLocal'])
dfMet['ORIGIN'] = dfMet['airport']
dfMet['DEST'] = dfMet['airport']
dfMet.sort_values(by=['timeLocal'],inplace=True)

# Perform slight processing on merged flight+met data
file = '../data/processed/merged/2019_FlightMetMerged.csv'
df = pd.read_csv(file)
df.drop_duplicates(inplace=True)

#For now remove flights where arrival time before departure time
df['ARR_TIME'] = pd.to_datetime(df['ARR_TIME'])
df['DEP_TIME'] = pd.to_datetime(df['DEP_TIME'])

#Create a feature row with user-defined input to put into trained ML model
#Convert user-input into df-compatible format
depTime = str(UserDepartureYear)+'-'+str(UserDepartureMonth)+'-'+str(UserDepartureDay)+' '+UserScheduledDepartureTime
depTime = pd.to_datetime(depTime)

arrTime = str(UserArrivalYear)+'-'+str(UserArrivalMonth)+'-'+str(UserArrivalDay)+' '+UserScheduledArrivalTime
arrTime = pd.to_datetime(arrTime)

orgCode = df[df['ORIGIN']==UserOrigin]['ORIGIN_AIRPORT_ID'].iloc[0]
depCode = df[df['DEST']==UserConnectingAirport]['DEST_AIRPORT_ID'].iloc[0]

#Create a row of 'X' (called_dfUser) based upon given flight data, pair with appropriate meteorology
dftmp = df[['ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID','DEP_TIME','ARR_TIME']].iloc[0]
dfUser1 = pd.DataFrame(data=dftmp).transpose()
dfUser1['ORIGIN'] = UserOrigin
dfUser1['DEST'] = UserConnectingAirport
dfUser1['ORIGIN_AIRPORT_ID'] = orgCode
dfUser1['DEST_AIRPORT_ID'] = depCode
dfUser1['DEP_TIME'] = depTime
dfUser1['ARR_TIME'] = arrTime

#Link in meteorology at the departure airport
dfUser2 = pd.merge_asof(left=dfUser1,right=dfMet,left_on=['DEP_TIME'],right_on=['timeLocal'],by=['ORIGIN'])

#Drop columns no longer needed and rename met columns so we know those are tied to departure
dfUser2.drop(['timeLocal','airport','DEST_y'],axis=1,inplace=True)
dfUser2.rename(columns={'DEST_x':'DEST','tmpF':'tmpF_D','dptF':'dptF_D','CC':'CC_D','dir':'dir_D',
        'spd':'spd_D','6hPrecPrb':'6hPrecPrb_D','12hPrecPrb':'12hPrecPrb_D',
        '6hQntPrec':'6hQntPrec_D','12hQntPrec':'12hQntPrec_D','snow':'snow_D',
        'ceil':'ceil_D','visib':'visib_D','obstruc':'obstruc_D','fzRnPrb':'fzRnPrb_D',
        'snowPrb':'snowPrb_D','6hrTsPrb_15mi':'6hrTsPrb_15mi_D',
        '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_D'},inplace=True)

#Link in meteorology at the arrival airport
dfUser2.sort_values(by=['ARR_TIME'],inplace=True)
dfUser = pd.merge_asof(left=dfUser2,right=dfMet,left_on=['ARR_TIME'],right_on=['timeLocal'],
            by=['DEST'])

dfUser.drop(['timeLocal','airport','ORIGIN_y'],axis=1,inplace=True)
dfUser.rename(columns={'ORIGIN_x':'ORIGIN','tmpF':'tmpF_A','dptF':'dptF_A','CC':'CC_A','dir':'dir_A',
            'spd':'spd_A','6hPrecPrb':'6hPrecPrb_A','12hPrecPrb':'12hPrecPrb_A',
            '6hQntPrec':'6hQntPrec_A','12hQntPrec':'12hQntPrec_A','snow':'snow_A',
            'ceil':'ceil_A','visib':'visib_A','obstruc':'obstruc_A','fzRnPrb':'fzRnPrb_A',
            'snowPrb':'snowPrb_A','6hrTsPrb_15mi':'6hrTsPrb_15mi_A',
            '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_A'},inplace=True)


#For df used for ML modeling

#Drop any row from df with nans for ML model, drop columns columns that are not needed
dfML = df.dropna()

#Merged arrival bins for simplicity for now
dfML['ARR_DELAY_GROUP'].loc[(dfML['ARR_DELAY_GROUP']<=0)] = 0
dfML['ARR_DELAY_GROUP'].loc[(dfML['ARR_DELAY_GROUP']>0)] = 1

#Use subset of dfML for ML modeling
X = dfML[['tmpF_D', 'dptF_D','dir_D', 'spd_D', '6hPrecPrb_D',
          '6hQntPrec_D', 'ceil_D', 'visib_D','fzRnPrb_D', 'snowPrb_D', '6hrTsPrb_15mi_D',
          '6hrSvrTsPrb_25mi_D', 'tmpF_A', 'dptF_A', 'dir_A', 'spd_A','6hPrecPrb_A', '6hQntPrec_A', 'ceil_A',
          'visib_A','fzRnPrb_A', 'snowPrb_A', '6hrTsPrb_15mi_A','6hrSvrTsPrb_25mi_A','snow_D','snow_A',
          '12hPrecPrb_D','12hQntPrec_D','12hPrecPrb_A','12hQntPrec_A']]

y = dfML['ARR_DELAY_GROUP']

#Normalize dataset, make sure to include the user data row is in here so it gets scaled
dfUser = dfUser[['tmpF_D', 'dptF_D', 'dir_D', 'spd_D', '6hPrecPrb_D', '6hQntPrec_D','ceil_D', 'visib_D',
                 'fzRnPrb_D', 'snowPrb_D', '6hrTsPrb_15mi_D','6hrSvrTsPrb_25mi_D', 'tmpF_A', 'dptF_A',
                 'dir_A', 'spd_A','6hPrecPrb_A', '6hQntPrec_A', 'ceil_A', 'visib_A', 'fzRnPrb_A','snowPrb_A',
                 '6hrTsPrb_15mi_A', '6hrSvrTsPrb_25mi_A', 'snow_D','snow_A', '12hPrecPrb_D', '12hQntPrec_D',
                 '12hPrecPrb_A','12hQntPrec_A']]

#Make a dataframe with X plus user data
XwithUsertmp = [X,dfUser]
XwithUser = pd.concat(XwithUsertmp)

#Perform scaling
sc = MinMaxScaler()
data = sc.fit_transform(XwithUser)

#Separate X from user data
Xdata = data[:-1,:]

XUser = data[-1,:]

#Split conversion dataset into train and test groups
X_train, X_test, y_train, y_test = train_test_split(Xdata, y)

#Train random forest model
clf = RandomForestClassifier(n_estimators=10).fit(X_train, y_train)

#Ingest user input into trained ML model
XUserT = XUser.reshape(1, -1)
forest_predicted = clf.predict(XUserT)

if (forest_predicted==0):
     st.write ("You are going to make your connection!")
else:
     st.write ("You are likely going to miss your connection!")
