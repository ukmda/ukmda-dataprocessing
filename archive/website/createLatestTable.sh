#!/bin/bash
# Creates a report of camera status with images showing latest uploads
# 
# Parameters
#   none
# 
# Consumes
#   stacks and allsky maps from individual cameras, plus the timestamp of upload
#
# Produces
#   a webpage showing the latest stack and map from each camera
#

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

echo "StationID,DateTime" > $DATADIR/latest/uploadtimes.csv
source $WEBSITEKEY
aws s3 ls $WEBSITEBUCKET/latest/ | grep jpg | while read i
do
    fn=$(echo $i | awk '{print $4}')
    dt=$(echo $i | awk '{print $1}')
    tm=$(echo $i | awk '{print $2}')
    fname=$(basename $fn .jpg)
    echo $fname,${dt}T${tm}.000Z >> $DATADIR/latest/uploadtimes.csv
    loc=$(grep $fname $DATADIR/consolidated/camera-details.csv  | awk -F, '{printf("%s_%s\n",$1 , $4)}')
    echo "var row = table.insertRow(-1);" >> reportindex.js
    echo "var cell = row.insertCell(0);" >> reportindex.js
    cellstr="$fname<br>$loc<br>$dt<br>$tm"
    echo "cell.innerHTML = \"$cellstr\";" >> reportindex.js
    echo "var cell = row.insertCell(1);" >> reportindex.js
    echo "cell.innerHTML = \"<a href=./$fname.jpg><img src=./$fname.jpg width=100%></a>\";" >> reportindex.js
    echo "var cell = row.insertCell(2);" >> reportindex.js
    echo "cell.innerHTML = \"<a href=./$fname.png><img src=./$fname.png width=100%></a>\";" >> reportindex.js

done
echo "var outer_div = document.getElementById(\"summary\");" >> reportindex.js
echo "outer_div.appendChild(table);" >> reportindex.js
echo "})" >> reportindex.js

logger -s -t createLatestTable "done, sending to website"
source $WEBSITEKEY
aws s3 cp reportindex.js  $WEBSITEBUCKET/latest/ --quiet

logger -s -t createLatestTable "finished"