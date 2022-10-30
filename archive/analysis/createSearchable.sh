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

source $here/../config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate
logger -s -t createSearchable "starting"
$SRC/utils/clearCaches.sh

if [ $# -lt 1 ] ; then
    yr=$(date +%Y)
else
    yr=$1
fi

mkdir -p $DATADIR/searchidx
cd $SRC/analysis

python -m reports.createSearchableFormat $yr /tmp
cp -f /tmp/${yr}-allevents.* $DATADIR/searchidx/
rm -f /tmp/${yr}-allevents.*

#logger -s -t createSearchable "create list of all cameras"
#cat $DATADIR/searchidx/*-allevents.csv | awk -F, '{print $5}' | sort | sed 's/^ *//g' | uniq > $DATADIR/camlist.txt

aws s3 sync $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --quiet

$SRC/utils/clearCaches.sh
logger -s -t createSearchable "finished"
