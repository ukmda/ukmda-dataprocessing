#!/bin/bash

# bash script to create monthly index page for orbit data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config/config.ini > /dev/null 2>&1

yr=$1
srcdir=${REPORTDIR}/${yr}/orbits
displstr=${yr}
msg="Click to explore each month."
targ=${WEBSITEBUCKET}/reports/${yr}/orbits/

if [ $# -gt 1 ] ; then
    mth=$2
    srcdir=${REPORTDIR}/${yr}/orbits/${yr}${mth}
    displstr=${yr}-${mth}
    msg="Click on an entry to see results of orbit analysis for the matched events"
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${yr}${mth}/
fi
idxfile=${srcdir}/index.html
echo $yr $mth

cp $TEMPLATES/header.html $idxfile
echo "<div class=\"container\">" >> $idxfile
echo "<h2>Orbit Reports for $displstr</h2>" >> $idxfile
echo "$msg<hr>" >> $idxfile
echo "<table class=\"table table-striped table-bordered table-hover table-condensed\"><tr>" >> $idxfile
j=0
ls -1d $srcdir/* | egrep -v "index|csv" | while read i
do
    indir=`basename $i`
    echo "<td><a href=$indir/index.html>$indir<a></td>" >> $idxfile
    ((j=j+1))
    if [ $j == 6 ] ; then
        j=0
        echo "</tr>" >> $idxfile
    fi 
done
echo "</tr></table>" >> $idxfile
echo "</div>" >> $idxfile

cat $TEMPLATES/footer.html >> $idxfile

source $WEBSITEKEY
aws s3 cp $idxfile $targ