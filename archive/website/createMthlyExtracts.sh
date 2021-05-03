#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

if [ $# -gt 0 ] ; then
    ymd=$1
    yrs=${ymd:0:4}   
    mths=${ymd:4:2}
else
    yrs="2021 2020"
    mths="01 02 03 04 05 06 07 08 09 10 11 12"
fi 

logger -s -t createMthlyExtracts "starting"

cd $DATADIR/matched
logger -s -t createMthlyExtracts "creating matched extracts"

for yr in $yrs
do
    for mth in $mths
    do
        rc=$(grep _${yr}${mth} ./matches-${yr}.csv | egrep -v "_${yr}${mth}," | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UO_header.txt $SRC/website/browse/monthly/${yr}${mth}-matches.csv
            grep _${yr}${mth} ./matches-${yr}.csv >> $SRC/website/browse/monthly/${yr}${mth}-matches.csv
        fi
    done
done

cd $DATADIR/consolidated
logger -s -t createMthlyExtracts "creating UFO detections"
for yr in $yrs
do
    for mth in $mths
    do
        rc=$(grep ",${yr}${mth}" ./M_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UA_header.txt $SRC/website/browse/monthly/${yr}${mth}-detections-ufo.csv
            grep ",${yr}${mth}" ./M_${yr}-unified.csv >> $SRC/website/browse/monthly/${yr}${mth}-detections-ufo.csv
        fi
    done
done

logger -s -t createMthlyExtracts "creating RMS detections"
mths1="1 2 3 4 5 6 7 8 9"
mths2="10 11 12"
for yr in $yrs
do
    for mth in $mths1
    do
        rc=$(grep ",${yr}, ${mth}" ./P_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/RMS_header.txt $SRC/website/browse/monthly/${yr}0${mth}-detections-rms.csv
            grep ",${yr}, ${mth}" ./P_${yr}-unified.csv >> $SRC/website/browse/monthly/${yr}0${mth}-detections-rms.csv
        fi
    done
    for mth in $mths2
    do
        rc=$(grep ",${yr},${mth}" ./P_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/RMS_header.txt $SRC/website/browse/monthly/${yr}${mth}-detections-rms.csv
            grep ",${yr},${mth}" ./P_${yr}-unified.csv >> $SRC/website/browse/monthly/${yr}${mth}-detections-rms.csv
        fi
    done
done
logger -s -t createMthlyExtracts "done gathering data, creating table"

idxfile=$SRC/website/browse/monthly/browselist.js

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

cd $here/browse/monthly/
yr=$(date +%Y)

while [ $yr -gt 2012 ]
do
    for mth in {12,11,10,90,08,07,06,05,04,03,02,01}
    do
        ufobn=""
        rmsbn=""
        matbn=""
        if compgen -G "$SRC/website/browse/monthly/${yr}${mth}-detections-ufo.csv" > /dev/null ; then 
            ufodets=$(ls -1 $SRC/website/browse/monthly/${yr}${mth}-detections-ufo.csv)
            ufobn=$(basename $ufodets)
        fi
        if compgen -G "$SRC/website/browse/monthly/${yr}${mth}-detections-rms.csv" > /dev/null ; then 
            rmsdets=$(ls -1 $SRC/website/browse/monthly/${yr}${mth}-detections-rms.csv)
            rmsbn=$(basename $rmsdets)
        fi
        if compgen -G "$SRC/website/browse/monthly/${yr}${mth}-matches.csv" > /dev/null ; then 
            matches=$(ls -1 $here/browse/monthly/${yr}${mth}-matches.csv)
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
aws s3 sync $SRC/website/browse/monthly/  $WEBSITEBUCKET/browse/monthly/


logger -s -t createMthlyExtracts "gathering annual data"
cd $SRC/website/browse/annual/
yr=$(date +%Y)
cp -p ${DATADIR}/matched/pre2020/matches*.csv .
cp -p ${DATADIR}/matched/matches-202*.csv .
if compgen -G "${DATADIR}/matched/matches-203*.csv" ; then
    cp -p ${DATADIR}/matched/matches-203*.csv .
fi
if compgen -G "${DATADIR}/matched/matches-204*.csv" ; then
    cp -p ${DATADIR}/matched/matches-204*.csv .
fi
cp -p ${DATADIR}/consolidated/M*.csv .
cp -p ${DATADIR}/consolidated/P*.csv .

logger -s -t createMthlyExtracts "done gathering data, creating table"
idxfile=$SRC/website/browse/annual/browselist.js

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

while [ $yr -gt 2012 ]
do
    ufobn=""
    rmsbn=""
    matbn=""
    if compgen -G "$SRC/website/browse/annual/M_${yr}-unified.csv" > /dev/null ; then 
        ufodets=$(ls -1 $SRC/website/browse/annual/M_${yr}-unified.csv)
        ufobn=$(basename $ufodets)
    fi
    if compgen -G "$SRC/website/browse/annual/P_${yr}-unified.csv" > /dev/null ; then 
        rmsdets=$(ls -1 $SRC/website/browse/annual/P_${yr}-unified.csv)
        rmsbn=$(basename $rmsdets)
    fi
    if compgen -G "$SRC/website/browse/annual/matches-${yr}.csv" > /dev/null ; then 
        matches=$(ls -1 $SRC/website/browse/annual/matches-${yr}.csv)
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
aws s3 sync $SRC/website/browse/annual/  $WEBSITEBUCKET/browse/annual/

logger -s -t createMthlyExtracts "finished"