#!/bin/csh

#This script generates a list of unique callsigns in the flight dataset
#Unique list used to extract meteorology at each airport

#Get all the unique 3-letter callsigns for the flight dataset from each csv file
#Origin and destination callsigns both pulled

cd ../../data/raw/flights/rawMonthlyData

foreach file (*.csv)
  cat $file | cut -d ',' -f6,10 >> ../callsigns.txt
end

#Concatenate origin and destination 3-letter callsigns into one column
touch ../callsigns_concat.txt
cut -d ',' -f1 ../callsigns.txt >> ../callsigns_concat.txt
cut -d ',' -f2 ../callsigns.txt >> ../callsigns_concat.txt

#Check to make sure that callsigns_concat.txt is double the length of callsigns.txt
#wc -l ../callsigns.txt
#wc -l ../callsigns_concat.txt

#Get unique list of callsigns
sort -u ../callsigns_concat.txt > ../callsigns_unique.txt
