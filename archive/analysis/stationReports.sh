#!/bin/bash
#
# monthly reporting for UKMON stations
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

yr=$1

logger -s -t stationReports "running Stations report for $yr"

cd $RCODEDIR
./STATION_SUMMARY_MASTER.r $yr

source $WEBSITEKEY
aws s3 sync $SRC/data/reports/stations/  s3://ukmeteornetworkarchive/reports/stations/ --quiet
logger -s -t stationReports "shower report done"

