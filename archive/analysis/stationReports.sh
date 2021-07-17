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
aws s3 sync $SRC/data/reports/stations/  $WEBSITEBUCKET/reports/stations/ --quiet
logger -s -t stationReports "shower report done"

logger -s -t stationReports "list of connected stations"
sudo grep publickey /var/log/secure | grep -v ec2-user | grep "$(date "+%b %d")" | awk '{printf("%s, %s\n", $3,$9)}' > /tmp/stationlogins.txt
source $WEBSITEKEY
aws s3 cp /tmp/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt

logger -s -t stationReports "finished"


