Crunched Connection Web App (http://bit.ly/crunchedconnectionwebsite)

Maria Zatko, Insight Data Science Fellow in Seattle

<br />
Motivation and Background:

Each year there are over 800 million airline passengers, and at least 20% of flights are delayed or cancelled. Missed flight connections are a huge hassle for both travelers and airlines. Some delays and cancellations are impossible to predict, such as mechanical plane issues. However, weather accounts for a significant portion (~30-50%) of total delay minutes each year and is something we can predict.  

Travelers can use the Crunched Connection web app several days before their flight to determine how likely they are to miss their flight connection because of several weather. The Crunched Connection tool is hosted on AWS and relies on flight itineraries, weather forecasts, and supervised machine learning to estimate the probability of a missed connection.

Domestic U.S. flight records from 2017 through 2019 are paired with archived weather forecast data at both departure and arrival airports. Twenty features from the merged dataset are incorporated into a random forest classifier model to estimate if a flight will be on-time or more than 15 minutes late. The Crunched Connection web app pairs a user's flight itinerary with corresponding weather forecast data and passes the data into the trained random forest model. Crunched Connection informs users how likely they are to miss their connecting flight because of severe weather.

<br />

Datasets:

Department of Transportation Statistics, Report Carrier On-Time Performance (https://www.transtats.bts.gov/Fields.asp).

National Weather Service Archived Model Output Statistics (https://mesonet.agron.iastate.edu/mos/).

<br />
<br />

Project Directory Structure:

data: Mimics structure of actual data directory but files not included because of filesize

demo: Slideshow presentation describing Crunched Connection tool

notebooks: Contains exploratory data analysis for flight and weather data. Also contains Crunched Connection machine learning algorithm.

scripts: Contains scripts used to download and process flight and weather data. Also contains script used to merge flight and weather data.

streamlit: Contains script used to create AWS-hosted streamlit web app.
