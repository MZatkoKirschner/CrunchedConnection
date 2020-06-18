Crunched Connection Web App (https://bit.ly/crunchedconnection)

Maria Zatko, Insight Data Science Fellow in Seattle


Motivation and Background:

Each year there are over 800 million airline passengers, and at least 20% of flights are delayed or cancelled. Missed flight connections are a huge hassle for both travelers and airlines. Some delays and cancellations are impossible to predict, such as mechanical plane issues. However, weather accounts for a signifcant portion (~30-50%) of total delay minutes each year and is something we can predict.  

Travelers can use the Crunched Connection web app several days before their flight to determine how likely they are to miss their flight connection because of several weather. The Crunched Connection tool is hosted on AWS and relies on flight itineraries, weather forecasts, and supervised machine learning to estimate the probability of a missed connection.

Domestic U.S. flight records from 2017 through 2019 are paired with archived weather forecast data at both departure and arrival airports. Twenty features from the merged dataset are incorporated into a random forest classifier model to estimate if a flight will be on-time or more than 15 minutes late. The Crunched Connection web app pairs a user's flight itinerary with corresponding weather forecast data and passes the data into the trained random forest model. Crunched Connection informs users how likely they are to miss their connecting flight because of severe weather.


Datasets:

Department of Transportation Statistics, Report Carrier On-Time Performance (https://www.transtats.bts.gov/Fields.asp)

Dataset contains detailed data for U.S. flights from 1987 to present. Data contains information such as departure and arrival city and delay information. Years 2017, 2018, and 2019 were used for this project.


National Weather Service achived forecast data (Model Output Statistics (https://mesonet.agron.iastate.edu/mos/)

Dataset contains archived forecast data for individual airports from 2000 to present. Python script used to download


Project Directory Structure:

data: Mimics structure of actual data directory but files not included because of filesize

demo: Slideshow presentation describing Crunched Connection tool

notebooks:

  01-EDA-FlightData: Flight data exploratory data analysis

  02-EDA-MetData: Weather forecast exploratory data analysis

  Demo_Final: Contains Crunched Connection machine learning algorithm

scripts:

  flight_processing directory: Contains scripts used to download and process flight dataset

  met_processing directory: Contains scripts used to download and process weather dataset

  01-mergeFlightsMet.py: Script used to merge flight and weeather data.

streamlit:

  01-MissedConnectionDemo.py: Script used to create AWS-hosted streamlit web app
