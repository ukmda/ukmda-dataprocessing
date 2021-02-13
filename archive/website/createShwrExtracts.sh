#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi
mkdir -p $here/browse/showers

if [ $# -gt 0 ] ; then
    ymd=$1
    yrs=${ymd:0:4}   
    mths=${ymd:4:2}
    shwrs="GEM LYR PER QUA LEO NTA STA ETA SDA"
else
    yrs="2021 2020"
    shwrs="GEM LYR PER QUA LEO NTA STA ETA SDA"
fi 


cd ${RCODEDIR}/DATA/matched
echo "creating matched extracts"
for yr in $yrs
do
    for shwr in $shwrs
    do
        rc=$(grep $shwr ./matches-${yr}.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UO_header.txt $here/browse/showers/${yr}-${shwr}-matches.csv
            grep $shwr ./matches-${yr}.csv >> $here/browse/showers/${yr}-${shwr}-matches.csv
        fi
    done
done
cd ${$CODEDIR}/DATA/consolidated
echo "creating UFO detections"
for yr in $yrs
do
    for shwr in $shwrs
    do
        rc=$(grep "_${shwr}" ./M_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UA_header.txt $here/browse/showers/${yr}-${shwr}-detections-ufo.csv
            grep "_${shwr}" ./M_${yr}-unified.csv >> $here/browse/showers/${yr}-${shwr}-detections-ufo.csv
        fi
    done
done

echo "done gathering data, creating tables"

for shwr in $shwrs
do 
    if [ ! -f $here/browse/showers/${shwr}index.html ] ; then 
        cat $TEMPLATES/shwrcsvindex.html  | sed "s/XXXXX/${shwr}/g" > $here/browse/showers/${shwr}index.html
    fi 
    idxfile=$here/browse/showers/${shwr}index.js

    echo "\$(function() {" > $idxfile
    echo "var table = document.createElement(\"table\");" >> $idxfile
    echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $idxfile
    echo "var header = table.createTHead();" >> $idxfile
    echo "header.className = \"h4\";" >> $idxfile
    cd $here/browse/showers/
    yr=$(date +%Y)
    while [ $yr -gt 2012 ]
    do
        ufodets=$(ls -1 $here/browse/showers/${yr}-${shwr}-detections-ufo.csv)
        #rmsdets=$(ls -1 $here/browse/showers/${yr}-${shwr}-detections-rms.csv)
        matches=$(ls -1 $here/browse/showers/${yr}-${shwr}-matches.csv)
        ufobn=$(basename $ufodets)
        #rmsbn=$(basename $rmsdets)
        matbn=$(basename $matches)
        echo "var row = table.insertRow(-1);" >> $idxfile
        echo "var cell = row.insertCell(0);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$ufobn">$ufobn</a>\";" >> $idxfile
        #echo "var cell = row.insertCell(1);" >> $idxfile
        #echo "cell.innerHTML = \"<a href="./$rmsbn">$rmsbn</a>\";" >> $idxfile
        echo "var cell = row.insertCell(1);" >> $idxfile
        echo "cell.innerHTML = \"<a href="./$matbn">$matbn</a>\";" >> $idxfile
        yr=$((yr-1))
    done
    echo "var row = header.insertRow(0);" >> $idxfile
    echo "var cell = row.insertCell(0);" >> $idxfile
    echo "cell.innerHTML = \"Detected UFO\";" >> $idxfile
    echo "cell.className = \"small\";" >> $idxfile
    #echo "var cell = row.insertCell(1);" >> $idxfile
    #echo "cell.innerHTML = \"Detected RMS\";" >> $idxfile
    #echo "cell.className = \"small\";" >> $idxfile
    echo "var cell = row.insertCell(1);" >> $idxfile
    echo "cell.innerHTML = \"Matches\";" >> $idxfile
    echo "cell.className = \"small\";" >> $idxfile

    echo "var outer_div = document.getElementById(\"${shwr}table\");" >> $idxfile
    echo "outer_div.appendChild(table);" >> $idxfile
    echo "})" >> $idxfile
done
echo "js table created"


source $WEBSITEKEY
aws s3 sync $here/browse/showers/  $WEBSITEBUCKET/browse/showers/
