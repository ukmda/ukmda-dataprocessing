#!/bin/bash
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createLatestTable "starting"

mkdir ${DATADIR}/latest > /dev/null 2>&1
cd ${DATADIR}/latest

echo "\$(function() {" > reportindex.js
echo "var table = document.createElement(\"table\");" >> reportindex.js
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> reportindex.js
echo "var header = table.createTHead();" >> reportindex.js
echo "header.className = \"h4\";" >> reportindex.js 

source $WEBSITEKEY
aws s3 ls $WEBSITEBUCKET/latest/ | grep jpg | awk '{print $4}' | while read i
do
    fname=$(basename $i .jpg)
    echo "var row = table.insertRow(-1);" >> reportindex.js
    echo "var cell = row.insertCell(0);" >> reportindex.js
    echo "cell.innerHTML = \"$fname\";" >> reportindex.js
    echo "var cell = row.insertCell(1);" >> reportindex.js
    echo "cell.innerHTML = \"<img src=./$fname.jpg width=100%>\";" >> reportindex.js
    echo "var cell = row.insertCell(2);" >> reportindex.js
    echo "cell.innerHTML = \"<img src=./$fname.png width=100%>\";" >> reportindex.js

done
echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
echo "outer_div.appendChild(table);" >> reportindex.js
echo "})" >> reportindex.js

logger -s -t createLatestTable "done, sending to website"
source $WEBSITEKEY
aws s3 cp reportindex.js  $WEBSITEBUCKET/latest/ --quiet

logger -s -t createLatestTable "finished"