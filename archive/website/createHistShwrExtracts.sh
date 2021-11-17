#!/bin/bash
# 
# One-off script to create the historical shower extracts
#
# Parameters
#   none
# 
# Consumes
#   historical matched/matches-yyyy.csv files
#
# Produces
#   a webpage and javascript table of the historical shower data
#     synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

mkdir -p $DATADIR/browse/showers

cd ${DATADIR}/matched/
echo "creating matched extracts"
for yr in {2013,2014,2015,2016,2017,2018,2019}
do
    #for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA}
    for shwr in {ORI,URS}
    do
        rc=$(grep -i _$shwr ./matches-${yr}.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UO_header.txt $DATADIR/browse/showers/${yr}-${shwr}-matches.csv
            grep -i _$shwr ./matches-${yr}.csv >> $DATADIR/browse/showers/${yr}-${shwr}-matches.csv
        fi
    done
done
cd ${DATADIR}/consolidated
echo "creating UFO detections"
for yr in {2012,2013,2014,2015,2016,2017,2018,2019}
do
    #for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA}
    for shwr in {ORI,URS}
    do
        rc=$(grep "${shwr}" ./M_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp $SRC/analysis/templates/UA_header.txt $DATADIR/browse/showers/${yr}-${shwr}-detections-ufo.csv
            grep "${shwr}" ./M_${yr}-unified.csv >> $DATADIR/browse/showers/${yr}-${shwr}-detections-ufo.csv
        fi
    done
done

echo "done gathering data, creating tables"

#for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA,spo}
for shwr in {ORI,URS}
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
    for yr in {2019,2018,2017,2016,2015,2014,2013,2012}
    do
        ufodets=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-detections-ufo.csv)
        rmsdets=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-detections-rms.csv)
        matches=$(ls -1 $DATADIR/browse/showers/${yr}-${shwr}-matches.csv)
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
done
echo "js table created"

source $WEBSITEKEY
aws s3 sync $DATADIR/browse/showers/  $WEBSITEBUCKET/browse/showers/ --quiet
