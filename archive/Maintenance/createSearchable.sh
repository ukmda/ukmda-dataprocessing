#!/bin/bash

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$RMS_ENV/bin/activate
if [ $# -lt 1 ] ; then
    yr=$(date +%Y)
else
    yr=$1
fi

mkdir -p $RCODEDIR/DATA/searchidx
cd $SRC/analysis
python ufoToSearchableFormat.py $CONFIG/config.ini $yr /tmp

mv /tmp/${yr}-singleevents.csv $RCODEDIR/DATA/searchidx/${yr}-allevents.csv
if [ -f /tmp/${yr}-matchedevents.csv ] ; then 
    sed '1d' /tmp/${yr}-matchedevents.csv >> $RCODEDIR/DATA/searchidx/${yr}-allevents.csv
fi 
sed '1d' /tmp/${yr}-liveevents.csv >> $RCODEDIR/DATA/searchidx/${yr}-allevents.csv

if [ -f /tmp/${yr}-matchedevents.csv ] ; then 
    rm -f /tmp/${yr}-matchedevents.csv
fi
rm -f /tmp/${yr}-liveevents.csv

grep -v "J8_TBC" $RCODEDIR/DATA/searchidx/${yr}-allevents.csv > /tmp/${yr}-allevents.csv

cp /tmp/${yr}-allevents.csv $RCODEDIR/DATA/searchidx/${yr}-allevents.csv
rm -f /tmp/${yr}-allevents.csv

source $WEBSITEKEY
aws s3 sync $RCODEDIR/DATA/searchidx/ $WEBSITEBUCKET/search/indexes/