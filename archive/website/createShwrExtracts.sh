#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ "$here" == *"prod"* ]] ; then
    echo sourcing prod config
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    echo sourcing dev config
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi
mkdir -p $here/browse/showers

cd $SRC/analysis/DATA/matched
echo "creating matched extracts"
yr=$(date +%Y)
while [ $yr -gt 2019 ]
do
    for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA}
    do
        rc=$(grep $shwr ./matches-${yr}.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp ../../../templates/UO_header.txt $here/browse/showers/${yr}-${shwr}-matches.csv
            grep $shwr ./matches-${yr}.csv >> $here/browse/showers/${yr}-${shwr}-matches.csv
        fi
    done
    yr=$((yr-1))
done
cd $here/../analysis/DATA/consolidated
echo "creating UFO detections"
yr=$(date +%Y)
while [ $yr -gt 2019 ]
do
    for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA}
    do
        rc=$(grep "_${shwr}" ./M_${yr}-unified.csv | wc -l)
        if [ $rc -gt 0 ]; then
            cp ../../templates/UA_header.txt $here/browse/showers/${yr}-${shwr}-detections-ufo.csv
            grep "_${shwr}" ./M_${yr}-unified.csv >> $here/browse/showers/${yr}-${shwr}-detections-ufo.csv
        fi
    done
    yr=$((yr-1))
done

echo "done gathering data, creating tables"

for shwr in {GEM,LYR,PER,QUA,LEO,NTA,STA,ETA,SDA}
do 
    cat $TEMPLATES/shwrcsvindex.html  | sed "s/XXXXX/${shwr}/g" > $here/browse/showers/${shwr}index.html

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
