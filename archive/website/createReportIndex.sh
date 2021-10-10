#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createReportIndex "starting"

cd ${DATADIR}/reports
echo "\$(function() {" > ./reportindex.js
echo "var table = document.createElement(\"table\");" >> ./reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> ./reportindex.js
echo "var header = table.createTHead();" >> ./reportindex.js
echo "header.className = \"h4\";" >> ./reportindex.js
ls -1dr 2* | while read i
do
    echo "var row = table.insertRow(-1);" >> ./reportindex.js
    echo "var cell = row.insertCell(0);" >> ./reportindex.js
    echo "cell.innerHTML = \"<a href="$i/ALL/index.html">$i Full Year</a>\";" >> ./reportindex.js
    echo "var cell = row.insertCell(1);" >> ./reportindex.js
    echo "cell.innerHTML = \"<a href="$i/orbits/index.html">Trajectories and Orbits</a>\";" >> ./reportindex.js
    echo "var cell = row.insertCell(2);" >> ./reportindex.js
    echo "cell.innerHTML = \"<a href="$i/stations/index.html">Stations</a>\";" >> ./reportindex.js

    if [ -f ./tmp.txt ] ; then rm -f ./tmp.txt ; fi
    ls -1 $i | egrep -v "ALL|orbits|stations" | while read j
    do 
        python $PYLIB/utils/getShowerDates.py $j >> ./tmp.txt
    done
    sort -n ./tmp.txt > ./shwrs.txt
    rm -f ./tmp.txt
    cat ./shwrs.txt | while read j 
    do
        dt=$(echo $j | awk -F, '{print $2}')
        nam=$(echo $j | awk -F, '{print $3}')
        abbrv=$(echo $j | awk -F, '{print $4}')
        echo "var row = table.insertRow(-1);">> ./reportindex.js
        echo "var cell = row.insertCell(0);" >> ./reportindex.js
        echo "var cell = row.insertCell(1);" >> ./reportindex.js
        echo "cell.innerHTML = \"<a href="$i/$abbrv/index.html">$dt $nam</a>\";" >> ./reportindex.js
        echo "var cell = row.insertCell(2);" >> ./reportindex.js
    done
    rm -f ./shwrs.txt
done
echo "var outer_div = document.getElementById(\"summary\");" >> ./reportindex.js
echo "outer_div.appendChild(table);" >> ./reportindex.js
echo "})" >> ./reportindex.js

logger -s -t createReportIndex "done, sending to website"
source $WEBSITEKEY
aws s3 cp ./reportindex.js  $WEBSITEBUCKET/data/ --quiet

logger -s -t createReportIndex "finished"