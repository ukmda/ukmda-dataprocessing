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

yr=$1
whichpass=$2
if [ "$yr"  == "" ] ; then yr=$(date +%Y) ; fi
if [ "$whichpass" == "" ] ; then whichpass=1 ; fi

mkdir -p $DATADIR/searchidx
cd $SRC/analysis

python -m reports.createSearchableFormat $yr $whichpass

aws s3 sync  $DATADIR/searchidx/ $WEBSITEBUCKET/search/indexes/ --exclude "*" --include "*.csv" --quiet 

logger -s -t createSearchable "finished"
