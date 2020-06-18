#!/bin/csh

#Example template for easy way to unzip the downloads via command line for each year

for month in `seq -w 1 12`; do
unzip 2020$month.zip
mv *ONTIME*.csv 2020$month.csv
rm 2020$month.zip
done
