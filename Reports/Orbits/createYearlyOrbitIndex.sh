#!/bin/bash

# bash script to create monthly index page for orbit data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/orbitsolver.ini > /dev/null 2>&1

yr=$1


idxfile=${results}/${yr}/orbits/index.shtml

echo "<html><head><title>Orbit Reports for $yr</title>" > $idxfile
echo "<link rel=\"stylesheet\" href=\"/data/mjmm-data/analysis/ukmon.css\">" >> $idxfile
echo "</head><body>" >> $idxfile
echo "</head><body>" >> $idxfile
echo "<a href=\"/data/mjmm-data/analysis/\"><img src=\"/data/mjmm-data/analysis/ukmon-logo.png\"></a>" >> $idxfile
echo "<h1>Orbit Reports for $yr</h1>" >> $idxfile
echo "<p>Click to explore each month.<hr>" >> $idxfile
echo "<a href=\"/data/mjmm-data/analysis/\">Up to report index</a></p>" >> $idxfile
echo "<br><table id=\"tablestyle\"><tr>" >> $idxfile
j=0
ls -1d ${results}/${yr}/orbits/* | egrep -v "index|csv" | while read i
do
    indir=`basename $i`
    echo "<td><a href=$indir>$indir<a></td>" >> $idxfile
    ((j=j+1))
    if [ $j == 6 ] ; then
        j=0
        echo "</tr>" >> $idxfile
    fi 
done

echo "</table>" >> $idxfile
echo "</body></html>" >> $idxfile
