#!/opt/anaconda3/bin/python3

import streamlit as st
import numpy as np
import pandas as pd
import datetime
import pickle
import altair as alt
from vega_datasets import data
import sys, traceback, os

#Header info
st.title('Crunched Connection')
st.header('Use this tool several days before your domestic U.S. flight to see if you likely to miss your connection because of severe weather.')

#Read in unique list of airports, unique list of city pairs with distance, and airline carriers
file = 'Airports.csv'
df = pd.read_csv(file)

fileDist = 'AirportPairs_WithDistance.csv'
dfDist = pd.read_csv(fileDist)

fileCarrier = 'Carriers.csv'
dfCarrier = pd.read_csv(fileCarrier)

latlonFile = 'airport_latlon_subset.csv'
latlondf = pd.read_csv(latlonFile)


#Gather User Inputs though Streamlit App
st.sidebar.title('Flight Itinerary Details')
st.sidebar.markdown("---")

st.sidebar.markdown(' ')
st.sidebar.header('Select Main Carrier')
carrier = st.sidebar.selectbox("Carrier", dfCarrier['carrier'])
st.sidebar.markdown("---")

st.sidebar.header('Select Departing Flight Information')
depAirport = st.sidebar.selectbox("Departure Airport", df['airport'],302)
conAirport = st.sidebar.selectbox("Connecting Airport", df['airport'],335)
date = st.sidebar.date_input('Scheduled Departure Date', datetime.date(2019,12,31))

st.sidebar.markdown(' ')
st.sidebar.header('Scheduled Departure Time')
depHour = st.sidebar.slider('Hour (Local)', 0, 23, 9)
depMin = st.sidebar.slider('Minute', 0, 59, 30)

st.sidebar.markdown(' ')
st.sidebar.header('Scheduled Landing Time')
depLandHour = st.sidebar.slider('Hour (Local)', 0, 23, 13)
depLandMin = st.sidebar.slider('Minute', 0, 59, 24)

st.sidebar.markdown("---")
st.sidebar.markdown(' ')
st.sidebar.header('Select Connecting Flight Information')
conAirportDummy = st.sidebar.selectbox("Connecting Airport ", df['airport'],335)
arrAirport = st.sidebar.selectbox("Final Destination Airport", df['airport'],46)
st.sidebar.header('Scheduled Departure Time')
conHour = st.sidebar.slider('Hour (Local)', 0, 23, 14)
conMin = st.sidebar.slider('Minute', 0, 59, 13)
st.sidebar.header('Scheduled Landing Time')
conLandHour = st.sidebar.slider('Hour (Local)', 0, 23, 22)
conLandMin = st.sidebar.slider('Minute', 0, 59, 26)
st.sidebar.markdown("---")


#Interactive map information and code
depLat = latlondf.loc[latlondf['airport']=='K'+depAirport,'lat'].values[0]
depLon = latlondf.loc[latlondf['airport']=='K'+depAirport,'lon'].values[0]

conLat = latlondf.loc[latlondf['airport']=='K'+conAirport,'lat'].values[0]
conLon = latlondf.loc[latlondf['airport']=='K'+conAirport,'lon'].values[0]

arrLat = latlondf.loc[latlondf['airport']=='K'+arrAirport,'lat'].values[0]
arrLon = latlondf.loc[latlondf['airport']=='K'+arrAirport,'lon'].values[0]

states = alt.topo_feature(data.us_10m.url, feature='states')

line_source = pd.DataFrame({
    'longitude': [depLon, conLon, arrLon],
    'latitude': [depLat, conLat, arrLat],
    'order': [1,2,3]
})

background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    width=800,
    height=500
).project('albersUsa')
point_path = line_path = alt.Chart(line_source).mark_circle().encode(
    longitude="longitude:Q",
    latitude="latitude:Q",
    size=alt.value(60)
)
line_path = alt.Chart(line_source).mark_line().encode(
    longitude="longitude:Q",
    latitude="latitude:Q",
    order='order:O'
)

st.altair_chart((background + point_path + line_path))

#Find distance and distance group associated with distances between user-provided Airports
#Throw an error if there is not a known route between 2 cities.
try:
    depConDist = dfDist.loc[(dfDist['ORIGIN']==depAirport) & (dfDist['DEST']==conAirport),'DISTANCE'].values[0]
    depConDistGrp = dfDist.loc[(dfDist['ORIGIN']==depAirport) & (dfDist['DEST']==conAirport),'DISTANCE_GROUP'].values[0]
except:
    sys.exit('Tool does not contain information about this flight route. Please choose another route')

#Format user-input times

#Original departure time
depTime = str(date)+ ' '+str(depHour).zfill(2)+':'+str(depMin).zfill(2)
depTime = pd.to_datetime(depTime)

#Scheduled landing time for first flight
depLandTime = str(date)+ ' '+str(depLandHour).zfill(2)+':'+str(depLandMin).zfill(2)
depLandTime = pd.to_datetime(depLandTime)

#Scheduled connection departure time
conTime = str(date)+ ' '+str(conHour).zfill(2)+':'+str(conMin).zfill(2)
conTime = pd.to_datetime(conTime)

#Scheduled landing time for second flight (at final destination)
conLandTime = str(date)+ ' '+str(conLandHour).zfill(2)+':'+str(conLandMin).zfill(2)
conLandTime = pd.to_datetime(conLandTime)

#Handle overnight flights appropriately
if (depLandTime - depTime) > pd.Timedelta('6 hours'):
    depLandTime = depLandTime + pd.Timedelta('1 day')

if (conLandTime - conTime) > pd.Timedelta('6 hours'):
    conLandTime = conLandTime + pd.Timedelta('1 day')

#Calculate connection time
ConnectionLength = conTime - depLandTime
ConnectionHours = ConnectionLength.components.hours
ConnectionMinutes = ConnectionLength.components.minutes

ConnectionLengthDelay = (ConnectionLength - pd.Timedelta('15 minutes'))
ConnectionHoursDelay = ConnectionLengthDelay.components.hours
ConnectionMinutesDelay = ConnectionLengthDelay.components.minutes

if (ConnectionHoursDelay==0):
    DelayImpact = str(ConnectionMinutesDelay)+' minutes'
else:
    DelayImpact = str(ConnectionHoursDelay)+' hours and '+str(ConnectionMinutesDelay)+' minutes'

#Print information to web app
st.write(" "); st.write(" ")
st.header("You have "+str(ConnectionHours)+" hours and "+str(ConnectionMinutes)+" minutes to make your connection in "+conAirport+'.')

st.write(" "); st.write(" ")
st.header("User input now being ingested into machine learning algorithm... ")

# Read met data
year = str(depTime.year)
metfile = year+'_ProcessedMet.csv'
dfMet = pd.read_csv(metfile)

#Format met data to help with merge
dfMet['timeLocal'] = pd.to_datetime(dfMet['timeLocal'])
dfMet['ORIGIN'] = dfMet['airport']
dfMet['DEST'] = dfMet['airport']
dfMet.sort_values(by=['timeLocal'],inplace=True)

#Create a feature row with user-defined input to put into trained ML model
#Format airport names for merging with met
depAirportK = 'K' + depAirport
conAirportK = 'K' + conAirport

#Find airport ID associated with user-provided airports
depAirportCode = df.loc[df['airport']==depAirport,'airport_ID'].values[0]
conAirportCode = df.loc[df['airport']==conAirport,'airport_ID'].values[0]

#Get airline carrier code
carrierCode = dfCarrier.loc[dfCarrier['carrier']==carrier,'carrier_number'].values[0]

#Create a row of 'X' (called_dfUser) based upon given flight data, then pair with appropriate meteorology
dfTmp = df.iloc[0]
dfUser = pd.DataFrame(data=dfTmp).transpose()
dfUser['ORIGIN'] = depAirportK
dfUser['DEST'] = conAirportK
dfUser['ORIGIN_AIRPORT_ID'] = depAirportCode
dfUser['DEST_AIRPORT_ID'] = conAirportCode
dfUser['DEP_TIME'] = depTime
dfUser['ARR_TIME'] = depLandTime
dfUser['DISTANCE'] = depConDist
dfUser['DISTANCE_GROUP'] = depConDistGrp
dfUser['OP_UNIQUE_CARRIER'] = carrierCode
dfUser['month'] = depTime.month
dfUser['hour'] = depTime.hour
dfUser['DOW'] = depTime.dayofweek
dfUser['DOY'] = depTime.dayofyear

#Drop unnecessary columns
dfUser.drop(columns=['airport','airport_ID','region'],axis=1,inplace=True)

#Link in meteorology at the departure airport
dfUser = pd.merge_asof(left=dfUser,right=dfMet,left_on=['DEP_TIME'],right_on=['timeLocal'],by=['ORIGIN'])

#Drop columns no longer needed and rename met columns so we know those are tied to departure
dfUser.drop(['timeLocal','airport','DEST_y'],axis=1,inplace=True)
dfUser.rename(columns={'DEST_x':'DEST','tmpF':'tmpF_D','dptF':'dptF_D','CC':'CC_D','dir':'dir_D',
        'spd':'spd_D','6hPrecPrb':'6hPrecPrb_D','12hPrecPrb':'12hPrecPrb_D',
        '6hQntPrec':'6hQntPrec_D','12hQntPrec':'12hQntPrec_D','snow':'snow_D',
        'ceil':'ceil_D','visib':'visib_D','obstruc':'obstruc_D','fzRnPrb':'fzRnPrb_D',
        'snowPrb':'snowPrb_D','6hrTsPrb_15mi':'6hrTsPrb_15mi_D',
        '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_D'},inplace=True)

#Link in meteorology at the arrival airport
dfUser.sort_values(by=['ARR_TIME'],inplace=True)
dfUserML = pd.merge_asof(left=dfUser,right=dfMet,left_on=['ARR_TIME'],right_on=['timeLocal'],
            by=['DEST'])

dfUserML.drop(['timeLocal','airport','ORIGIN_y'],axis=1,inplace=True)
dfUserML.rename(columns={'ORIGIN_x':'ORIGIN','tmpF':'tmpF_A','dptF':'dptF_A','CC':'CC_A','dir':'dir_A',
            'spd':'spd_A','6hPrecPrb':'6hPrecPrb_A','12hPrecPrb':'12hPrecPrb_A',
            '6hQntPrec':'6hQntPrec_A','12hQntPrec':'12hQntPrec_A','snow':'snow_A',
            'ceil':'ceil_A','visib':'visib_A','obstruc':'obstruc_A','fzRnPrb':'fzRnPrb_A',
            'snowPrb':'snowPrb_A','6hrTsPrb_15mi':'6hrTsPrb_15mi_A',
            '6hrSvrTsPrb_25mi':'6hrSvrTsPrb_25mi_A'},inplace=True)


# Ingest data into trained ML model! Only include columns actually used in ML model

dfUserMLsub = dfUserML[['spd_D', 'fzRnPrb_D', 'snowPrb_D', '6hrTsPrb_15mi_D',
       '6hrSvrTsPrb_25mi_D', 'fzRnPrb_A', 'snowPrb_A', '6hrTsPrb_15mi_A',
       '6hrSvrTsPrb_25mi_A', '6hPrecPrb_D', '6hPrecPrb_A', '12hPrecPrb_D',
       '12hPrecPrb_A', 'snow_D', 'snow_A', 'spd_A', 'tmpF_D', 'dptF_D',
       'tmpF_A', 'dptF_A', 'ceil_D', 'ceil_A', 'visib_D', 'visib_A',
       '6hQntPrec_D', '6hQntPrec_A', '12hQntPrec_A', '12hQntPrec_D',
       'OP_UNIQUE_CARRIER', 'DISTANCE_GROUP', 'month', 'hour', 'DOY']]

#Load the trained ML model
pkl_filename = "pickle_model.pkl"
with open(pkl_filename, 'rb') as file:
    MLmodel = pickle.load(file)

#Ingest user input into trained ML model
forest_predicted = MLmodel.predict(dfUserMLsub)

#Calculate probability of being on-time and late
predictProba = MLmodel.predict_proba(dfUserMLsub)
dfProba = pd.DataFrame(predictProba,columns=['on-time','late'])
dfProbaOnTime = int ( (1 - dfProba['on-time'].values[0]) * 100 )
dfProbaLate = int( (dfProba['late'].values[0]) * 100 )

#Write ML results to web app
st.write(" "); st.write(" ")
if (forest_predicted==0):
     st.header ('Your departure flight is unlikely to be impacted by severe weather. There is a '+str(dfProbaOnTime)+'% chance that severe weather will impact your flight connection.')
else:
     st.header ('Your departure flight is '+str(dfProbaLate)+'% likely to be at least 15 minutes late, leaving you with no less than '+DelayImpact+' to spare. You are at risk of missing your flight connection!')
