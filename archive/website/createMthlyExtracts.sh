#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
# Create extracts for sharing on the website.
#
# Parameters
#   yyyymm to run for
#
# Consumes
#   consolidated/* and matched/*
#
# Produces
#   annual and monthly CSV files of UFO, RMS and matched data
#   Website index pages for the above
#   synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

logger -s -t createMthlyExtracts "starting"

if [ $# -gt 0 ] ; then
    ymd=$1
    yr=${ymd:0:4}   
    mth=${ymd:4:2}
else
    yr=$(date +%Y)
    mth=$(date +%m)
fi 

logger -s -t createMthlyExtracts "gathering annual data"

cd $DATADIR/matched
logger -s -t createMthlyExtracts "creating extracts"

# sync the website with ukmon-shared so the annual data is all available
# Essential as we're using the content of the website to build the pages
aws s3 sync $UKMONSHAREDBUCKET/consolidated/ $WEBSITEBUCKET/browse/annual/ --exclude "*" --include "*unified.csv" --exclude "R*" --quiet
aws s3 sync $UKMONSHAREDBUCKET/matches/matched/ $WEBSITEBUCKET/browse/annual/ --exclude "*" --include "*.csv" --quiet

# this reads from the local copies, created by earlier steps in the batch and then synced to ukmon-shared
python -m reports.extractors $yr $mth

# sync the monthly extracts to the website so that it has the latest files - 
# Essential as we're using the content of the website to build the pages
aws s3 sync $DATADIR/browse/monthly/  $WEBSITEBUCKET/browse/monthly/ --quiet

logger -s -t createMthlyExtracts "done gathering data, creating monthly table"
idxfile=$DATADIR/browse/monthly/browselist.js

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

cd $DATADIR/browse/monthly/
# get a list of files on the website
aws s3 ls $WEBSITEBUCKET/browse/monthly/ | awk '{ print $4 }' | grep csv > /tmp/browsemth.txt
yr=$(date +%Y)

while [ $yr -gt 2012 ]
do
    for mth in {12,11,10,09,08,07,06,05,04,03,02,01}
    do
        ufobn=$(grep ${yr}${mth}-detections-ufo.csv /tmp/browsemth.txt)
        rmsbn=$(grep ${yr}${mth}-detections-rms.csv /tmp/browsemth.txt)
        rmshw=$(grep ${yr}${mth}-rms-shwr.csv /tmp/browsemth.txt)
        matbn=$(grep ${yr}${mth}-matches.csv /tmp/browsemth.txt)
        if [[ "$ufobn" != "" ]] || [[ "$rmsbn" != "" ]] || [[ "$matbn" != "" ]] || [[ "$rmsshw" != "" ]] ; then
            echo "var row = table.insertRow(-1);" >> $idxfile
            echo "var cell = row.insertCell(0);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
            echo "var cell = row.insertCell(1);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
            echo "var cell = row.insertCell(2);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$rmshw">$rmshw</a>\";" >> $idxfile
            echo "var cell = row.insertCell(3);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
        fi
    done
    yr=$((yr-1))
done
\rm /tmp/browsemth.txt

echo "var row = header.insertRow(0);" >> $idxfile
echo "var cell = row.insertCell(0);" >> $idxfile
echo "cell.innerHTML = \"Detected UFO\";" >> $idxfile
echo "cell.className = \"small\";" >> $idxfile
echo "var cell = row.insertCell(1);" >> $idxfile
echo "cell.innerHTML = \"Detected RMS\";" >> $idxfile
echo "cell.className = \"small\";" >> $idxfile
echo "var cell = row.insertCell(2);" >> $idxfile
echo "cell.innerHTML = \"Det RMS + Shwr\";" >> $idxfile
echo "cell.className = \"small\";" >> $idxfile
echo "var cell = row.insertCell(3);" >> $idxfile
echo "cell.innerHTML = \"Matches\";" >> $idxfile
echo "cell.className = \"small\";" >> $idxfile

echo "var outer_div = document.getElementById(\"browselist\");" >> $idxfile
echo "outer_div.appendChild(table);" >> $idxfile
echo "})" >> $idxfile

logger -s -t createMthlyExtracts "js table created, copying to website"
aws s3 sync $DATADIR/browse/monthly/  $WEBSITEBUCKET/browse/monthly/ --quiet

logger -s -t createMthlyExtracts "creating annual table"
idxfile=$DATADIR/browse/annual/browselist.js
yr=$(date +%Y)
# get a list of files on the website
aws s3 ls $WEBSITEBUCKET/browse/annual/ | awk '{ print $4 }' | grep csv > /tmp/browseann.txt

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

while [ $yr -gt 2012 ] ; do
    ufobn=$(grep M_${yr}-unified.csv /tmp/browseann.txt)
    rmsbn=$(grep P_${yr}-unified.csv /tmp/browseann.txt)
    matbn=$(grep matches-full-${yr}.csv /tmp/browseann.txt)
    if [ "$matbn" == "" ] ; then
        matbn=$(grep matches-${yr}.csv /tmp/browseann.txt)
    fi 

    if [[ "$ufobn" != "" ]] || [[ "$rmsbn" != "" ]] || [[ "$matbn" != "" ]] ; then
        echo "var row = table.insertRow(-1);" >> $idxfile
        echo "var cell = row.insertCell(0);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(1);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(2);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
    fi
    yr=$((yr-1))
done
\rm /tmp/browseann.txt

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

echo "var outer_div = document.getElementById(\"browselist\");" >> $idxfile
echo "outer_div.appendChild(table);" >> $idxfile
echo "})" >> $idxfile

logger -s -t createMthlyExtracts "annual js table created, copying to website"
aws s3 sync $DATADIR/browse/annual/  $WEBSITEBUCKET/browse/annual/ --quiet

logger -s -t createMthlyExtracts "finished"