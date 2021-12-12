#!/bin/bash
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

source $here/../config/config.ini >/dev/null 2>&1

if [ $# -gt 0 ] ; then
    ymd=$1
    yrs=${ymd:0:4}   
    mth=${ymd:4:2}
else
    yrs="2021 2020"
    mth=01
    endmths=12
fi 

logger -s -t createMthlyExtracts "gathering annual data"
cd $DATADIR/browse/annual/
yr=$(date +%Y)
rsync -avz ${DATADIR}/matched/matches*.csv .
rsync -avz ${DATADIR}/consolidated/M*.csv .
rsync -avz ${DATADIR}/consolidated/P*.csv .

cd $DATADIR/matched
logger -s -t createMthlyExtracts "creating extracts"

export DATADIR
for yr in $yrs
do
    python $PYLIB/reports/extractors.py $yr $mth $endmths
done

logger -s -t createMthlyExtracts "done gathering data, creating table"
idxfile=$DATADIR/browse/monthly/browselist.js

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

cd $DATADIR/browse/monthly/
yr=$(date +%Y)

while [ $yr -gt 2012 ]
do
    for mth in {12,11,10,09,08,07,06,05,04,03,02,01}
    do
        ufobn=""
        rmsbn=""
        matbn=""
        if compgen -G "$DATADIR/browse/monthly/${yr}${mth}-detections-ufo.csv" > /dev/null ; then 
            ufodets=$(ls -1 $DATADIR/browse/monthly/${yr}${mth}-detections-ufo.csv)
            ufobn=$(basename $ufodets)
        fi
        if compgen -G "$DATADIR/browse/monthly/${yr}${mth}-detections-rms.csv" > /dev/null ; then 
            rmsdets=$(ls -1 $DATADIR/browse/monthly/${yr}${mth}-detections-rms.csv)
            rmsbn=$(basename $rmsdets)
        fi
        if compgen -G "$DATADIR/browse/monthly/${yr}${mth}-matches.csv" > /dev/null ; then 
            matches=$(ls -1 $DATADIR/browse/monthly/${yr}${mth}-matches.csv)
            matbn=$(basename $matches)
        fi
        if [[ "$ufodets" != "" ]] || [[ "$rmsdets" != "" ]] || [[ "$matches" != "" ]] ; then
            echo "var row = table.insertRow(-1);" >> $idxfile
            echo "var cell = row.insertCell(0);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
            echo "var cell = row.insertCell(1);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
            echo "var cell = row.insertCell(2);" >> $idxfile
            echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
        fi
    done
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

echo "var outer_div = document.getElementById(\"browselist\");" >> $idxfile
echo "outer_div.appendChild(table);" >> $idxfile
echo "})" >> $idxfile

logger -s -t createMthlyExtracts "js table created, copying to website"
source $WEBSITEKEY
aws s3 sync $DATADIR/browse/monthly/  $WEBSITEBUCKET/browse/monthly/ --quiet

logger -s -t createMthlyExtracts "done gathering data, creating table"
idxfile=$DATADIR/browse/annual/browselist.js
yr=$(date +%Y)

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

while [ $yr -gt 2012 ] ; do
    ufobn=""
    rmsbn=""
    matbn=""
    if compgen -G "$DATADIR/browse/annual/M_${yr}-unified.csv" > /dev/null ; then 
        ufodets=$(ls -1 $DATADIR/browse/annual/M_${yr}-unified.csv)
        ufobn=$(basename $ufodets)
    fi
    if compgen -G "$DATADIR/browse/annual/P_${yr}-unified.csv" > /dev/null ; then 
        rmsdets=$(ls -1 $DATADIR/browse/annual/P_${yr}-unified.csv)
        rmsbn=$(basename $rmsdets)
    fi
    if compgen -G "$DATADIR/browse/annual/matches-${yr}.csv" > /dev/null ; then 
        matches=$(ls -1 $DATADIR/browse/annual/matches-${yr}.csv)
        matbn=$(basename $matches)
    fi
    if [[ "$ufodets" != "" ]] || [[ "$rmsdets" != "" ]] || [[ "$matches" != "" ]] ; then
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
source $WEBSITEKEY
aws s3 sync $DATADIR/browse/annual/  $WEBSITEBUCKET/browse/annual/ --quiet

logger -s -t createMthlyExtracts "finished"