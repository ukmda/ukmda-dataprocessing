#!/bin/bash

# bash script to create monthly index page for orbit data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/orbitsolver.ini > /dev/null 2>&1

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}

dtstr=`date -d "2020-$mth-01" '+%B %Y'`
idxfile=${results}/${yr}/orbits/${ym}/index.shtml

echo "<html><head><title>Orbit Reports for $dtstr</title>" > $idxfile
echo "<link rel=\"stylesheet\" href=\"/data/mjmm-data/analysis/ukmon.css\">" >> $idxfile
echo "</head>" >> $idxfile
echo "<body><h1>Orbit Reports for $dtstr</h1>" >> $idxfile
echo "<p>Click on an entry to see results of orbit analysis for the matched events.</p><hr>" >> $idxfile
echo "<br><table id=\"tablestyle\"><tr>" >> $idxfile
j=0
ls -1d ${results}/${yr}/orbits/${ym}/* | grep -v index | while read i
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
