#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

cd $here/../analysis
echo "\$(function() {" > $here/data/summarytable.js
echo "var table = document.createElement(\"table\");" >> $here/data/summarytable.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $here/data/summarytable.js
echo "var header = table.createTHead();" >> $here/data/summarytable.js
echo "header.className = \"h4\";" >> $here/data/summarytable.js

yr=$(date +%Y)
until [ $yr -lt 2013 ]; do
    if [ $yr -gt 2019 ] ; then 
        detections=$(grep "OTHER Matched" logs/ALL$yr.log | awk '{print $4}')
    else
        detections=`cat DATA/consolidated/M_${yr}-unified.csv | wc -l`
    fi
    matches=`grep "UNIFIED Matched" logs/ALL${yr}.log  | awk '{print $4}'`
    fireballs=`tail -n +2 REPORTS/$yr/ALL/TABLE_Fireballs.csv |wc -l`
    echo "var row = table.insertRow(-1);" >> $here/data/summarytable.js
    echo "var cell = row.insertCell(0);" >> $here/data/summarytable.js
    echo "cell.innerHTML = \"<a href="/reports/$yr/ALL/index.html">$yr</a>\";" >> $here/data/summarytable.js
    echo "var cell = row.insertCell(1);" >> $here/data/summarytable.js
    echo "cell.innerHTML = \"$detections\";" >> $here/data/summarytable.js
    echo "var cell = row.insertCell(2);" >> $here/data/summarytable.js
    echo "cell.innerHTML = \"<a href="/reports/$yr/orbits/index.html">$matches</a>\";" >> $here/data/summarytable.js
    echo "var cell = row.insertCell(3);" >> $here/data/summarytable.js
    echo "cell.innerHTML = \"$fireballs\";" >> $here/data/summarytable.js
    ((yr=yr-1))
done
echo "var row = header.insertRow(0);" >> $here/data/summarytable.js
echo "var cell = row.insertCell(0);" >> $here/data/summarytable.js
echo "cell.innerHTML = \"Year\";" >> $here/data/summarytable.js
echo "cell.className = \"small\";" >> $here/data/summarytable.js
echo "var cell = row.insertCell(1);" >> $here/data/summarytable.js
echo "cell.innerHTML = \"Detections\";" >> $here/data/summarytable.js
echo "cell.className = \"small\";" >> $here/data/summarytable.js
echo "var cell = row.insertCell(2);" >> $here/data/summarytable.js
echo "cell.innerHTML = \"Matches\";" >> $here/data/summarytable.js
echo "cell.className = \"small\";" >> $here/data/summarytable.js
echo "var cell = row.insertCell(3);" >> $here/data/summarytable.js
echo "cell.innerHTML = \"Fireballs\";" >> $here/data/summarytable.js
echo "cell.className = \"small\";" >> $here/data/summarytable.js

echo "var outer_div = document.getElementById(\"summarytable\");" >> $here/data/summarytable.js
echo "outer_div.appendChild(table);" >> $here/data/summarytable.js
echo "})" >> $here/data/summarytable.js

source $WEBSITEKEY
aws s3 cp $here/data/summarytable.js  $WEBSITEBUCKET/data/
