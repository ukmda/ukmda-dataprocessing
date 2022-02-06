#!/bin/bash
# Creates an the reports page index.
#
# Parameters
#   year to create report index for - default is current year
# 
# Consumes
#   list of folders in the reports/ folder
#
# Produces
#   index.html for the reports page, synced to the website
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini >/dev/null 2>&1

logger -s -t createReportIndex "starting"
if [ $# -lt 1 ] ; then 
    curryr=$(date +%Y)
    fldr=.
    prefix=.
else
    curryr=$1
    fldr=$1
    prefix=/reports
fi

cd ${DATADIR}/reports

repidx=$fldr/reportindex.js
echo "\$(function() {" > $repidx
echo "var table = document.createElement(\"table\");" >> $repidx
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $repidx
echo "var header = table.createTHead();" >> $repidx
echo "header.className = \"h4\";" >> $repidx

echo "var row = table.insertRow(-1);" >> $repidx
echo "var cell = row.insertCell(0);" >> $repidx
echo "cell.innerHTML = \"<a href="$prefix/$curryr/ALL/index.html">$i Full Year</a>\";" >> $repidx
echo "var cell = row.insertCell(1);" >> $repidx
echo "cell.innerHTML = \"<a href="$prefix/$curryr/orbits/index.html">Trajectories and Orbits</a>\";" >> $repidx
echo "var cell = row.insertCell(2);" >> $repidx
echo "cell.innerHTML = \"<a href="$prefix/$curryr/fireballs/index.html">Fireballs</a>\";" >> $repidx
echo "var cell = row.insertCell(3);" >> $repidx
echo "cell.innerHTML = \"<a href="$prefix/$curryr/stations/index.html">Stations</a>\";" >> $repidx

if [ -f $curryr/tmp.txt ] ; then rm -f $curryr/tmp.txt ; fi

ls -1 $curryr | egrep -v "ALL|orbits|stations|fireballs|.js|.html" | while read j
do 
    python -m utils.getShowerDates $j >> $curryr/tmp.txt
done
sort -n $curryr/tmp.txt > $curryr/shwrs.txt
rm -f $curryr/tmp.txt
cat $curryr/shwrs.txt | while read j 
do
    dt=$(echo $j | awk -F, '{print $2}')
    nam=$(echo $j | awk -F, '{print $3}')
    abbrv=$(echo $j | awk -F, '{print $4}')
    echo "var row = table.insertRow(-1);">> $repidx
    echo "var cell = row.insertCell(0);" >> $repidx
    echo "var cell = row.insertCell(1);" >> $repidx
    echo "cell.innerHTML = \"<a href="$prefix/$curryr/$abbrv/index.html">$dt $nam</a>\";" >> $repidx
    #echo "var cell = row.insertCell(2);" >> $repidx
done
rm -f $curryr/shwrs.txt

echo "var outer_div = document.getElementById(\"summary\");" >> $repidx
echo "outer_div.appendChild(table);" >> $repidx
echo "})" >> $repidx

previdx=$fldr/prevyrs.js
echo "\$(function() {" > $previdx
echo "var table = document.createElement(\"table\");" >> $previdx
echo "table.className = \"table table-striped table-bordered table-hover table-condensed\";" >> $previdx
echo "var header = table.createTHead();" >> $previdx
echo "header.className = \"h4\";" >> $previdx

j=0
ls -1dr 2* | grep -v $curryr | while read i
do
    if [ $j == 0 ] ; then echo "var row = table.insertRow(-1);">> $previdx ; fi
    echo "var cell = row.insertCell(-1);" >> $previdx
    echo "cell.innerHTML = \"<a href="$prefix/$i/index.html">$i</a>\";" >> $previdx
    ((j=j+1))
    if [ $j == 5 ] ; then j=0 ; fi
done

echo "var outer_div = document.getElementById(\"prevyrs\");" >> $previdx
echo "outer_div.appendChild(table);" >> $previdx
echo "})" >> $previdx

logger -s -t createReportIndex "done, sending to website"
source $WEBSITEKEY
if [ "$prefix" == "." ] ; then 
    aws s3 cp $SRC/website/templates/reportindex.html $WEBSITEBUCKET/reports/index.html --quiet
    aws s3 cp $repidx  $WEBSITEBUCKET/reports/ --quiet
    aws s3 cp $previdx  $WEBSITEBUCKET/reports/ --quiet
else
    aws s3 cp $SRC/website/templates/reportindex.html $WEBSITEBUCKET/reports/$curryr/index.html --quiet
    aws s3 cp $repidx  $WEBSITEBUCKET/reports/$curryr/ --quiet
    aws s3 cp $previdx  $WEBSITEBUCKET/reports/$curryr/ --quiet
    realyr=$(date +%Y)
    if [ $curryr -eq $realyr ] ;  then
        aws s3 cp $SRC/website/templates/reportindex.html $WEBSITEBUCKET/reports/index.html --quiet
        aws s3 cp $repidx  $WEBSITEBUCKET/reports/ --quiet
        aws s3 cp $previdx  $WEBSITEBUCKET/reports/ --quiet
    fi 
fi
logger -s -t createReportIndex "finished"