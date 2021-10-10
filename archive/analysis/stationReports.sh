#!/bin/bash
#
# monthly reporting for UKMON stations
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -eq 0 ]; then
    yr=$(date +%Y)
else
    yr=$1
fi

logger -s -t stationReports "running Stations report for $yr"

cd $RCODEDIR
./STATION_SUMMARY_MASTER.r $yr
logger -s -t stationReports "shower report done creating index"

cd $DATADIR/reports/$yr/stations

echo "\$(function() {" > reportindex.js
echo "var table = document.createElement(\"table\");" >> reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $here/data/reportindex.js
echo "var header = table.createTHead();" >> reportindex.js
echo "header.className = \"h4\";" >> reportindex.js
echo "var row = table.insertRow(-1);" >> reportindex.js
echo "var cell = row.insertCell(0);" >> reportindex.js
echo "cell.innerHTML = \"Station Reports\";" >> reportindex.js
ls -1 *.html | grep -v index | while read i ; do
    echo "var row = table.insertRow(-1);">> reportindex.js
    echo "var cell = row.insertCell(0);" >> reportindex.js
    bn=$(basename $i .html)
    echo "cell.innerHTML = \"<a href="./$i">$bn</a>\";" >> reportindex.js
done
echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
echo "outer_div.appendChild(table);" >> reportindex.js
echo "})" >> reportindex.js
cp $TEMPLATES/statreportindex.html index.html

logger -s -t stationReports "create list of connected stations"
sudo grep publickey /var/log/secure | grep -v ec2-user | egrep "$(date "+%b %d")|$(date "+%b  %-d")" | awk '{printf("%s, %s\n", $3,$9)}' > $DATADIR/reports/stationlogins.txt

source $WEBSITEKEY
aws s3 sync $DATADIR/reports/$yr/stations/  $WEBSITEBUCKET/reports/$yr/stations/ --quiet
aws s3 cp $DATADIR/reports/stationlogins.txt $WEBSITEBUCKET/reports/stationlogins.txt

logger -s -t stationReports "finished"


