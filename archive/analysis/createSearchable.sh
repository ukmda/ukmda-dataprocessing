#!/bin/bash

#
# Create a single searchable index file for matched, single and live data
#
# Parameters:
#   date to process in yyyy format
#
# Consumes:
#   The ukmon single-yyyy.csv, matches-full-yyyy.csv and live yyyyqq.csv files
#
# Produces:
#   searchidx/yyyy-allevents.txt - a searchable file 
#   camlist.txt - a list of cameras that provided data 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate
source $WEBSITEKEY
if [ $# -lt 1 ] ; then
    yr=$(date +%Y)
else
    yr=$1
fi

mkdir -p $DATADIR/searchidx
cd $SRC/analysis
logger -s -t createSearchable "creating searchable format files"

export PYTHONPATH=$wmpl_loc:$PYLIB
export WEBSITEBUCKET
python $PYLIB/reports/createSearchableFormat.py $yr /tmp

mv /tmp/${yr}-singleevents.csv $DATADIR/searchidx/${yr}-allevents.csv
if [ -f /tmp/${yr}-matchedevents.csv ] ; then 
    sed '1d' /tmp/${yr}-matchedevents.csv >> $DATADIR/searchidx/${yr}-allevents.csv
    rm -f /tmp/${yr}-matchedevents.csv
fi 
if [ -f /tmp/${yr}-liveevents.csv ] ; then 
    sed '1d' /tmp/${yr}-liveevents.csv >> $DATADIR/searchidx/${yr}-allevents.csv
    rm -f /tmp/${yr}-liveevents.csv
fi

if [ -f /tmp/matches-full-${yr}.csv ] ; then 
    mv -f /tmp/matches-full-${yr}.csv $DATADIR/matched/
fi

grep -v "J8_TBC" $DATADIR/searchidx/${yr}-allevents.csv > /tmp/${yr}-allevents.csv

cp /tmp/${yr}-allevents.csv $DATADIR/searchidx/${yr}-allevents.csv
rm -f /tmp/${yr}-allevents.csv

logger -s -t createSearchable "create list of all cameras"
cat $DATADIR/searchidx/*-allevents.csv | awk -F, '{print $5}' | sort | sed 's/^ *//g' | uniq > $DATADIR/camlist.txt

source $WEBSITEKEY
aws s3 sync $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --quiet
source $UKMONSHAREDKEY
aws s3 sync $DATADIR/matched $UKMONSHAREDBUCKET/matches/matched