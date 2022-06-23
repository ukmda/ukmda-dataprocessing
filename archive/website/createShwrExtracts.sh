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
    yrs=${ymd:0:4}   
    mths=${ymd:4:2}
else
    yrs="2021 2020"
fi 
shwrs=$(PYTHONPATH=$PYLIB python -c "from fileformats import imoWorkingShowerList as imo; sl = imo.IMOshowerList();print(sl.getMajorShowers(True, True));")


cd ${DATADIR}/matched
logger -s -t createShwrExtracts "creating matched extracts"

for yr in $yrs
do
    if compgen -G "$DATADIR/matched/matches-full-${yr}.csv" > /dev/null ; then 
        for shwr in $shwrs
        do
            logger -s -t createShwrExtracts "doing $yr $shwr"
            python -m reports.extractShowerCsv $yr $shwr 'M'
        done
    fi
done
cd ${DATADIR}/consolidated
logger -s -t createShwrExtracts "creating UFO detections"
for yr in $yrs
do
    if compgen -G "$DATADIR/consolidated/M_${yr}-unified.csv" > /dev/null ; then 
        for shwr in $shwrs
        do
            logger -s -t createShwrExtracts "doing $yr $shwr"
            python -m reports.extractShowerCsv $yr $shwr 'U'
        done
    fi
done
cd ${DATADIR}/consolidated
logger -s -t createShwrExtracts "creating RMS detections"
for yr in $yrs
do
    if compgen -G "$DATADIR/single/singles-${yr}.csv" > /dev/null ; then 
        for shwr in $shwrs
        do
            logger -s -t createShwrExtracts "doing $yr $shwr"
            python -m reports.extractShowerCsv $yr $shwr 'R'
        done
    fi
done

logger -s -t createShwrExtracts "done gathering data, creating tables"

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
    cd $DATADIR/browse/showers/
    yr=$(date +%Y)
    while [ $yr -gt 2012 ]
    do
        ufobn=""
        rmsbn=""
        matbn=""
        if compgen -G "$DATADIR/browse/showers/${yr}-${shwr}-detections-ufo.csv" > /dev/null ; then 
            ufodets=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-detections-ufo.csv)
            ufobn=$(basename $ufodets)
        fi
        if compgen -G "$DATADIR/browse/showers/${yr}-${shwr}-detections-rms.csv" > /dev/null ; then 
            rmsdets=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-detections-rms.csv)
            rmsbn=$(basename $rmsdets)
        fi
        if compgen -G "$DATADIR/browse/showers/${yr}-${shwr}-matches.csv" > /dev/null ; then 
            matches=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-matches.csv)
            matbn=$(basename $matches)
        fi
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

logger -s -t createShwrExtracts "sending to website"
aws s3 sync $DATADIR/browse/showers/  $WEBSITEBUCKET/browse/showers/ --quiet

logger -s -t createShwrExtracts "finished"