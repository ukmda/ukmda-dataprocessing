#!/bin/bash
# Creates extracts of raw and matched data for each meteor shower in the selected year
#
# Note that the raw data is sourced from the consolidated raw UFO and RMS CSV files
#
# Parameters
#   date in yyyymm format
# 
# Consumes
#   IMO working shower list
#   matched/matches-yyyy.csv
#   consolidated/M_yyyy_unified.csv
#   single/singles-yyyy.csv
#
# Produces
#   csv extracts of detections and matches for each shower
#   an index page, all synced to the website
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate

mkdir -p $DATADIR/browse/showers

logger -s -t createShwrExtracts "starting"

if [ $# -gt 0 ] ; then
    ymd=$1
else
    ymd=$(date +%Y%m%d)
fi 

cd ${DATADIR}/matched
logger -s -t createShwrExtracts "creating annual shower extracts"
python -c "from reports import extractors as ex; ex.extractAllShowersData($ymd);"

logger -s -t createShwrExtracts "done gathering data, creating tables"
# sync data so its all there to get a list of 
aws s3 sync $DATADIR/browse/showers/  $WEBSITEBUCKET/browse/showers/ --quiet

cd $DATADIR/browse/showers/
# get a list of files on the website
aws s3 ls $WEBSITEBUCKET/browse/showers/ | awk '{ print $4 }' | grep csv > /tmp/browseshwr.txt

shwrs=$(python -c "from utils.getActiveShowers import getActiveShowersStr ; getActiveShowersStr('${ymd}')")
for shwr in $shwrs
do 
    now=$(date '+%Y-%m-%d %H:%M:%S')
    cat $TEMPLATES/shwrcsvindex.html  | sed "s/XXXXX/${shwr}/;s/DDDDDDDD/${now}/g" > $DATADIR/browse/showers/${shwr}index.html

    idxfile=$DATADIR/browse/showers/${shwr}index.js

    echo "\$(function() {" > $idxfile
    echo "var table = document.createElement(\"table\");" >> $idxfile
    echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
    echo "var header = table.createTHead();" >> $idxfile
    echo "header.className = \"h4\";" >> $idxfile

    yr=$(date +%Y)
    while [ $yr -gt 2012 ]
    do
        ufobn=$(grep ${yr}-${shwr}-detections-ufo.csv /tmp/browseshwr.txt)
        rmsbn=$(grep ${yr}-${shwr}-detections-rms.csv /tmp/browseshwr.txt)
        matbn=$(grep ${yr}-${shwr}-matches.csv /tmp/browseshwr.txt)
        echo "var row = table.insertRow(-1);" >> $idxfile
        echo "var cell = row.insertCell(0);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(1);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(2);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
        yr=$((yr-1))
    done
    echo "var row = header.insertRow(0);" >> $idxfile
    echo "var cell = row.insertCell(0);" >> $idxfile
    echo "cell.innerHTML = \"Detected UFO\";" >> $idxfile
    echo "cell.className = \"small\";" >> $idxfile
    echo "var cell = row.insertCell(1);" >> $idxfile
    echo "cell.innerHTML = \"Detected RMS\";" >> $idxfile
    echo "cell.className = \"small\";" >> $idxfile
    echo "var cell = row.insertCell(2);" >> $idxfile
    echo "cell.innerHTML = \"Matches\";" >> $idxfile
    echo "cell.className = \"small\";" >> $idxfile

    echo "var outer_div = document.getElementById(\"${shwr}table\");" >> $idxfile
    echo "outer_div.appendChild(table);" >> $idxfile
    echo "})" >> $idxfile
    echo "js table created for $shwr"
done
\rm -f /tmp/browseshwr.txt

logger -s -t createShwrExtracts "sending to website"
aws s3 sync $DATADIR/browse/showers/  $WEBSITEBUCKET/browse/showers/ --quiet

logger -s -t createShwrExtracts "finished"