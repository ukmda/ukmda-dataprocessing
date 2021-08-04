#!/bin/bash

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

source $WEBSITEKEY
aws s3 ls $WEBSITEBUCKET/img/single/$yr/ --recursive | awk '{print $4}' > /tmp/single.csv

export PYTHONPATH=$wmpl_loc:$PYLIB
export WEBSITEBUCKET
python $PYLIB/reports/createSearchableFormat.py $CONFIG/config.ini $yr /tmp

mv /tmp/${yr}-singleevents.csv $DATADIR/searchidx/${yr}-allevents.csv
if [ -f /tmp/${yr}-matchedevents.csv ] ; then 
    sed '1d' /tmp/${yr}-matchedevents.csv >> $DATADIR/searchidx/${yr}-allevents.csv
fi 
sed '1d' /tmp/${yr}-liveevents.csv >> $DATADIR/searchidx/${yr}-allevents.csv

if [ -f /tmp/${yr}-matchedevents.csv ] ; then 
    rm -f /tmp/${yr}-matchedevents.csv
fi
rm -f /tmp/${yr}-liveevents.csv

grep -v "J8_TBC" $DATADIR/searchidx/${yr}-allevents.csv > /tmp/${yr}-allevents.csv

cp /tmp/${yr}-allevents.csv $DATADIR/searchidx/${yr}-allevents.csv
rm -f /tmp/${yr}-allevents.csv

logger -s -t createSearchable "create list of all cameras"
cat $DATADIR/searchidx/*-allevents.csv | awk -F, '{print $5}' | sort | sed 's/^ *//g' | uniq > $DATADIR/camlist.txt

source $WEBSITEKEY
aws s3 sync $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --quiet