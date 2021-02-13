#!/bin/bash
# bash script to create monthly index page for orbit data

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

if [[ "$here" == *"prod"* ]] ; then
    source $HOME/prod/config/config.ini >/dev/null 2>&1
else
    source $HOME/src/config/config.ini >/dev/null 2>&1
fi

source $WEBSITEKEY

ym=$1
yr=${ym:0:4}
mth=${ym:4:2}
echo $ym $yr $mth

if [ "$mth" != "" ] ; then
    displstr=${yr}-${mth}
    msg="Click on an entry to see results of analysis for the matched event."
    msg2="<a href=\"../index.html\">Back to annual index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits/${ym}
    orblist=$(aws s3 ls $targ/ | grep PRE | grep $mth | awk '{print $2}')
else
    displstr=${yr}
    msg="Click to explore each month."
    msg2="<a href=\"../../index.html\">Back to reports index</a>" 
    targ=${WEBSITEBUCKET}/reports/${yr}/orbits
    orblist=$(aws s3 ls $targ/ | grep PRE | grep $yr | awk '{print $2}')
fi

idxfile=/tmp/${ym}.html

cp $TEMPLATES/header.html $idxfile
echo "<div class=\"container\">" >> $idxfile
echo "<h2>Matched Event Orbit and Trajectory Reports for $displstr</h2>" >> $idxfile
echo "$msg2<hr>" >> $idxfile
echo "$msg<hr>" >> $idxfile
echo "<table class=\"table table-striped table-bordered table-hover table-condensed\"><tr>" >> $idxfile
j=0

if [ "$orblist" == "" ] ; then 
    echo "<td> No data available </td>" >> $idxfile
else
    for i in $orblist 
    do
        indir=$(basename $i)
        echo "<td><a href=$indir/index.html>$indir<a></td>" >> $idxfile
        ((j=j+1))
        if [ $j == 6 ] ; then
            j=0
            echo "</tr>" >> $idxfile
        fi 
    done
fi
echo "</tr></table>" >> $idxfile
echo "</div>" >> $idxfile

cat $TEMPLATES/footer.html >> $idxfile

source $WEBSITEKEY
aws s3 cp $idxfile $targ/index.html
#rm -f $idxfile