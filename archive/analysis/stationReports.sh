#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# monthly reporting for UKMON stations
#
# Parameters
#   year and month in yyyymm format
#
# Consumes
#   All single-station and matched data from $DATADIR/single and $DATADIR/matched
#
# Produces
#   A report for each station for each month in the year and for the whole year
#    in $DATADIR/reports/yyyy/stations which is then synced to the website
#   A list of stations that have uploaded and the last connection time. 

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}
$SRC/utils/clearCaches.sh

if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}
if [ "$2" != "" ] ; then
    loc=$2
    logger -s -t stationReports "running station reports for $ym for $loc"
else
    logger -s -t stationReports "running station reports for $ym for all stations"
fi
python -m analysis.stationAnalysis $ym $loc
python -m analysis.stationAnalysis $yr $loc

aws s3 sync $DATADIR/reports/$yr/stations/  $WEBSITEBUCKET/reports/$yr/stations/ --quiet

logger -s -t stationReports "station reports done creating index"

mkdir -p $DATADIR/reports/$yr/stations > /dev/null 2>&1
cd $DATADIR/reports/$yr/stations

echo "\$(function() {" > reportindex.js
echo "var table = document.createElement(\"table\");" >> reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> reportindex.js
echo "var header = table.createTHead();" >> reportindex.js
echo "header.className = \"h4\";" >> reportindex.js
echo "var row = table.insertRow(-1);" >> reportindex.js
echo "var cell = row.insertCell(0);" >> reportindex.js
echo "var cell = row.insertCell(1);" >> reportindex.js
echo "cell.innerHTML = \"Station Reports\";" >> reportindex.js
echo "var cell = row.insertCell(2);" >> reportindex.js
j=0
k=1
statlist=$(aws s3 ls $WEBSITEBUCKET/reports/$yr/stations/ | egrep -v "index.html|reportindex.js" | awk '{print $2}')
for i in $statlist ; do
    if [ $j -eq 0 ] ; then echo "var row = table.insertRow($k);">> reportindex.js ; fi
    echo "var cell = row.insertCell(-1);" >> reportindex.js
    j=$((j+1))
    if [ $j -eq 3 ] ; then j=0 ; k=$((k+1)); fi
    echo "cell.innerHTML = \"<a href="./${i}index.html">$(basename $i)</a>\";" >> reportindex.js
done
echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
echo "outer_div.appendChild(table);" >> reportindex.js
echo "})" >> reportindex.js
cp $TEMPLATES/statreportindex.html index.html

aws s3 cp $DATADIR/reports/$yr/stations/index.html  $WEBSITEBUCKET/reports/$yr/stations/ --quiet
aws s3 cp $DATADIR/reports/$yr/stations/reportindex.js  $WEBSITEBUCKET/reports/$yr/stations/ --quiet

logger -s -t stationReports "finished"
$SRC/utils/clearCaches.sh
