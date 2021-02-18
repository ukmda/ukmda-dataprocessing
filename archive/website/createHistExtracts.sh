#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

cd ${RCODEDIR}/DATA/matched/pre2020
echo "creating matched extracts"
for yr in {2013,2014,2015,2016,2017,2018,2019}
do
    for mth in {01,02,03,04,05,06,07,08,09,10,11,12}
    do
        rc=$(grep _${yr}${mth} ./matches-${yr}.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp ../../../templates/UO_header.txt $here/browse/monthly/${yr}${mth}-matches.csv
            grep _${yr}${mth} ./matches-${yr}.csv >> $here/browse/monthly/${yr}${mth}-matches.csv
        fi
    done
done
cd ${RCODEDIR}/DATA/consolidated
echo "creating UFO detections"
for yr in {2012,2013,2014,2015,2016,2017,2018,2019}
do
    for mth in {01,02,03,04,05,06,07,08,09,10,11,12}
    do
        rc=$(grep ",${yr}${mth}" ./M_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp ../../templates/UA_header.txt $here/browse/monthly/${yr}${mth}-detections-ufo.csv
            grep ",${yr}${mth}" ./M_${yr}-unified.csv >> $here/browse/monthly/${yr}${mth}-detections-ufo.csv
        fi
    done
done
echo "creating RMS detections"
for yr in {2018,2019}
do
    for mth in {1,2,3,4,5,6,7,8,9}
    do
        rc=$(grep ",${yr}, ${mth}" ./P_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/RMS_header.txt $here/browse/monthly/${yr}0${mth}-detections-rms.csv
            grep ",${yr}, ${mth}" ./P_${yr}-unified.csv >> $here/browse/monthly/${yr}0${mth}-detections-rms.csv
        fi
    done
    for mth in {10,11,12}
    do
        rc=$(grep ",${yr},${mth}" ./P_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/RMS_header.txt $here/browse/monthly/${yr}${mth}-detections-rms.csv
            grep ",${yr},${mth}" ./P_${yr}-unified.csv >> $here/browse/monthly/${yr}${mth}-detections-rms.csv
        fi
    done
done
echo "done gathering data, creating table"

idxfile=$here/browse/monthly/browselist.js

echo "\$(function() {" > $idxfile
echo "var table = document.createElement(\"table\");" >> $idxfile
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
echo "var header = table.createTHead();" >> $idxfile
echo "header.className = \"h4\";" >> $idxfile

cd $here/browse/monthly/
for yr in {2019,2018,2017,2016,2015,2014,2013,2012}
do
    for mth in {12,11,10,09,08,07,06,05,04,03,02,01}
    do
        ufodets=$(ls -1 $here/browse/monthly/${yr}${mth}-detections-ufo.csv)
        rmsdets=$(ls -1 $here/browse/monthly/${yr}${mth}-detections-rms.csv)
        matches=$(ls -1 $here/browse/monthly/${yr}${mth}-matches.csv)
        ufobn=$(basename $ufodets)
        rmsbn=$(basename $rmsdets)
        matbn=$(basename $matches)
        echo "var row = table.insertRow(-1);" >> $idxfile
        echo "var cell = row.insertCell(0);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(1);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(2);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
    done
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

echo "js table created"
source $WEBSITEKEY
aws s3 sync $here/browse/monthly/  $WEBSITEBUCKET/browse/monthly/
